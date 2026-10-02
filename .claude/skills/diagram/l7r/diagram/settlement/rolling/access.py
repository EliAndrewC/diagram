"""The access-corridor tree reserved at seating (feature 287, plan M3's seat half; homes H16, ways W01).

A farmhouse the lane web cannot reach was found only on the finished map, and the map was re-rolled with that ground
forbidden (`hamletgen/driver.py`). Eighteen seat-time reach tests failed before this because they ran while the
neighbors' fabric was still to be laid. The corridor is reserved AGAINST that fabric instead: the first corridor is an
EXIT STRIP from the cluster's center outward, and each house is admitted only with a clear corridor from its door to
the tree - a straight strip a footpath wide, clear of every other homestead's box and of the ground the boundary
refuses. Every later envelope refuses to cover a corridor, so no household seated after can hem a house in.

The corridor is a RESERVATION, not a way: the web draws a way along it where its lanes do not reach the house
(WAYS' `settle_the_web`). The tree is recorded on the manifest (`access_corridors`) for the stages that follow.
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any

from .._geom import PointGrid, Pt, seg_closest, seg_dist, segments_cross
from .._geom.primitives import chain_violated

if TYPE_CHECKING:
    from ..core import Settlement

#: Half the corridor's width, in feet: `WEB_FABRIC_GAP` (7 ft) either side of the tread's line - a footpath's room between
#: two steadings, the gap the web's own fabric keeps (homes H16: "a footpath-width strip (WEB_FABRIC_GAP x 2)").
ACCESS_HALF_FT = 7.0

#: How far along a corridor its ground is sampled against the site boundary, in px: finer than the thinnest member the
#: boundary holds a corridor off (a ditch's half-width plus its clearance).
SAMPLE_PX = 8.0

#: How many of the tree's points a door tries before its seat is refused, nearest first: each corridor's nearest point and
#: its points every `TARGET_STEP_PX` along it. A straight corridor to the nearest point is the common case; a point further
#: along the same corridor is the way round a neighbor standing square across the direct run.
TARGETS_TRIED = 12

#: The spacing of the points along a corridor a door may aim at, in px: half a bundle pitch (`BUNDLE_PITCH`, 100 ft), so a
#: neighbor's homestead standing across the direct run leaves an aim point on either side of it.
TARGET_STEP_PX = 50.0


def _seg_box_gap(a: Pt, b: Pt, box: Any) -> float:
    """The least distance from the segment a-b to the axis-aligned box `(cx, cy, w, h)`; 0 where they meet."""
    cx, cy, w, h = box
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in (a, b)):
        return 0.0
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if any(segments_cross(a, b, corners[k], corners[(k + 1) % 4]) for k in range(4)):
        return 0.0
    return min(
        min(seg_dist(c[0], c[1], a, b) for c in corners),
        min(seg_dist(p[0], p[1], corners[k], corners[(k + 1) % 4]) for p in (a, b) for k in range(4)),
    )


def seg_box_within(a: Pt, b: Pt, box: Any, t: float) -> bool:
    """Is the segment a-b nearer than `t` to the box `(cx, cy, w, h)` - `_seg_box_gap(a, b, box) < t`, the same verdict,
    decided by one distance wherever it can be (seed 17: 1.4 million exact gaps, a third of the seating): the gap is at
    most the center's distance from the line (the center is in the box) and at least that less the half-diagonal, and a
    box beyond the segment's own box widened by `t` is farther than `t`. Only a box between those bounds takes the exact
    gap."""
    cx, cy, w, h = box
    if min(a[0], b[0]) - t > cx + w / 2 or max(a[0], b[0]) + t < cx - w / 2 or min(a[1], b[1]) - t > cy + h / 2 or max(a[1], b[1]) + t < cy - h / 2:
        return False
    d = seg_dist(cx, cy, a, b)
    if d < t:
        return True
    if d - math.hypot(w, h) / 2 >= t:
        return False
    return _seg_box_gap(a, b, box) < t


class AccessTree:
    """The reserved corridors: segments `(a, b)` a footpath wide (`half` either side), indexed by their widened boxes."""

    __slots__ = ("_along", "_targets", "grid", "half", "routed", "segs", "tried")

    def __init__(self, half: float) -> None:
        self.half = half
        self.segs: list[tuple[Pt, Pt]] = []
        self.grid = PointGrid(128.0)
        self._targets: dict[Pt, list[Pt]] = {}  # `targets`, remembered while no corridor is added
        self._along: list[list[Pt]] = []  # each corridor's points every `TARGET_STEP_PX`
        # how many of the tree's nearest points a door's corridor is tried to: `TARGETS_TRIED`, widened for a near miss's rescue
        # (`capacity.seat_the_rest`, feature 306) and set back after it
        self.tried = TARGETS_TRIED
        # ...and whether a door no straight corridor clears is routed round what stands (`route.py`, feature 308 plan D3): the
        # nucleated seating's tree only
        self.routed = False

    def add(self, a: Pt, b: Pt) -> None:
        self.segs.append((a, b))
        self._targets = {}
        n = int(math.dist(a, b) // TARGET_STEP_PX)
        self._along.append([(a[0] + (b[0] - a[0]) * k / max(1, n), a[1] + (b[1] - a[1]) * k / max(1, n)) for k in range(n + 1)])
        h = self.half
        self.grid.extend([(a, b, min(a[0], b[0]) - h, min(a[1], b[1]) - h, max(a[0], b[0]) + h, max(a[1], b[1]) + h)])

    def covers_box(self, box: Any) -> bool:
        """Does any corridor's strip meet the box `(cx, cy, w, h)`? The ONE test an envelope asks (plan M3: every later
        placement refuses to cover a corridor)."""
        cx, cy, w, h = box
        for a, b, x0, y0, x1, y1 in self.grid.near(cx, cy, max(w, h) / 2 + self.half):
            if x1 < cx - w / 2 or x0 > cx + w / 2 or y1 < cy - h / 2 or y0 > cy + h / 2:
                continue
            if seg_box_within(a, b, box, self.half):
                return True
        return False

    def targets(self, p: Pt) -> list[Pt]:
        """The nearest point of each corridor and its points every `TARGET_STEP_PX`, nearest first, at most
        `TARGETS_TRIED`. REMEMBERED per door until a corridor is added: the four garden sides of one seat ask from the same
        doors (seed 17: 24,466 calls, each measuring and sorting every point of the tree)."""
        got = self._targets.get(p)
        if got is not None:
            return got
        # each corridor's points along are the tree's, not the door's: laid out once per corridor (`_along`); the nearest
        # `TARGETS_TRIED` taken as a stable sort's first ones would be (`heapq.nsmallest`, whose ties keep list order)
        # A RING QUERY WAS TRIED AND WITHDRAWN (feature 304, plan D5; specs/304 research R10): the targets from a `PointGrid` ring
        # doubled until it held `TARGETS_TRIED`, exactly this answer, was 1-4% SLOWER on the stage at 40 households on all four
        # reference seeds - the exhaustive pass's doors stand far from the tree, so the ring grew across many empty cells, and
        # the scan's list is a few hundred points even then. Do not retry it without a measurement that says the tree outgrew it.
        pts: list[Pt] = []
        for (a, b), along in zip(self.segs, self._along, strict=True):
            pts.append(seg_closest(p[0], p[1], a, b))
            pts += along
        dist = math.dist
        got = self._targets[p] = heapq.nsmallest(self.tried, pts, key=lambda q: dist(p, q))
        return got


def doors_of(geom: Any, half: float = 0.0) -> list[Pt]:
    """Where a homestead's corridor may start, in preference order - IN ITS DOORYARD, never at a back wall (feature 287,
    ways W57: the path serves the house at its dooryard, and the web drew a back-wall door round the gable after the
    fact): the forecourt (the yard's center, before the door), then the yard's far edge, then the dooryard's two flanks -
    at the yard's depth, beside it, carried out past the house's gable by a corridor's half-width (`half`) and a foot, so a
    corridor to a tree behind the house leaves its dooryard and passes the gable rather than crossing the house. A bundle
    with no yard leaves by a step off its front wall."""
    boxes = geom.get("boxes") or {}
    yard = boxes.get("yard") or geom.get("yard")
    hx, hy, hw, hh = boxes.get("house") or geom["house"]
    if yard is None:
        return [(float(hx), float(hy + hh / 2 + 2.0))]
    yx, yy, yw, yh = (float(v) for v in yard)
    d = math.hypot(yx - hx, yy - hy) or 1.0
    ux, uy = (yx - hx) / d, (yy - hy) / d
    along = yw / 2 * abs(ux) + yh / 2 * abs(uy)  # the yard's half extent away from the house
    if geom.get("turn") is not None and geom.get("yard") is not None:
        # ...AS DRAWN, where the bundle says how its parts are turned (`BundleGeomMixin._bundle_geom`): its axis-aligned box
        # overstates a turned yard's extent, and a far-edge door set by it stood past the yard (merge of features 280 and 287,
        # cohort seed 32: a 25-tsubo yard turned 12 degrees put the door 16 ft beyond it, a lane end the law reads as reaching
        # nothing, `end_serves`, so the reserved corridor could not be drawn). The true rect's half extent along the bearing.
        tw, th_ = float(geom["yard"][2]), float(geom["yard"][3])
        c, sn = math.cos(math.radians(float(geom["turn"]))), math.sin(math.radians(float(geom["turn"])))
        along = tw / 2 * abs(ux * c + uy * sn) + th_ / 2 * abs(-ux * sn + uy * c)
    across = max(yw / 2 * abs(uy) + yh / 2 * abs(ux), hw / 2 * abs(uy) + hh / 2 * abs(ux) + half + 1.0)  # ...and across, past the gable
    return [(yx, yy), (yx + ux * along, yy + uy * along), (yx - uy * across, yy + ux * across), (yx + uy * across, yy - ux * across)]


#: The turns off the seat's outward bearing an exit strip is tried at, in degrees, nearest first, where the strip straight
#: out is refused by the ground: a quarter turn either way at most, so the strip still leaves the cluster away from its field.
EXIT_TURNS_DEG = (0.0, 15.0, -15.0, 30.0, -30.0, 45.0, -45.0, 60.0, -60.0, 75.0, -75.0, 90.0, -90.0)


def exit_bearing(s: Settlement, center: Pt, out: Pt, length: float) -> Pt | None:
    """The bearing the exit strip leaves the cluster's center along: `out`, or the nearest turn off it (`EXIT_TURNS_DEG`)
    whose strip stands on lawful ground (`lawful_ground`, the corridors' own test). None where no turn does - the margin
    has no way out and is refused."""
    for deg in EXIT_TURNS_DEG:
        c, sn = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        u = (out[0] * c - out[1] * sn, out[0] * sn + out[1] * c)
        if lawful_ground(s, center, (center[0] + u[0] * length, center[1] + u[1] * length)):
            return u
    return None


def start_tree(s: Settlement, center: Pt, out: Pt, length: float) -> AccessTree:
    """The tree's first corridor, the EXIT STRIP: from the cluster's center outward along `out` for `length` px (the
    connector starts at its outer end). Installed on the settlement for the seat pass and recorded on the manifest. The
    caller asks `exit_bearing` for an `out` whose strip stands on lawful ground."""
    tree = AccessTree(s.px(ACCESS_HALF_FT))
    s.__dict__.pop("_corridor_memo", None)  # a new tree is a new seating: nothing remembered of the last one's ground
    end = (center[0] + out[0] * length, center[1] + out[1] * length)
    tree.add(center, end)
    s._access = tree
    s.M["access_corridors"] = []
    s.M["access_exit"] = [[round(center[0], 1), round(center[1], 1)], [round(end[0], 1), round(end[1], 1)]]
    return tree


def corridor_clear(s: Settlement, a: Pt, b: Pt, own: Any) -> bool:
    """May a corridor run a-b? Its strip clears every placed homestead box but its own (`own`, the candidate's bbox, whose
    house it may not cross either), and its line stands on ground the site boundary admits - not on the field's side of a
    chord, not within a water course's clearance, not inside the outline of the other ground."""
    return house_clear(a, b, own, house_gap(s)) and fixtures_clear(s, a, b, own) and parts_clear(s, a, b, own) and standing_clear(s, a, b)


#: How far a way's tread edge stands from a farmhouse wall, in feet (feature 294 B7): GUESS, anchored on the research's three-shaku
#: (~3 ft) eaves strip before a townhouse (research/contents.json#compounds) with a margin for the eaves themselves; the recorded defect was a
#: tread 3.85 ft from a wall, and every pool map measured 4.9 ft or more when the rule was written (rules-recon.md item 8). The
#: house seating holds a house off every tread by it (`houses._on_a_tread`, which imports it from here) and a corridor holds its
#: tread off its own house by it (`house_gap`).
TREAD_WALL_FT = 4.0


def house_clear(a: Pt, b: Pt, own: Any, gap: float = 0.5) -> bool:
    """Does a corridor a-b keep `gap` off its own house (`own`'s)? The seating asks it at `house_gap`: a corridor grazing its
    house's corner by less than the tread and `house_hit`'s pad was reserved and then refused by the web when it came to draw
    it (cohort seed 44, feature 287 M8), leaving the house with no way."""
    return not seg_box_within(a, b, own.get("boxes", {}).get("house") or own["house"], gap)


def house_gap(s: Settlement) -> float:
    """The gap a corridor's line keeps off its own house: the tread's half-width, the tread-to-wall rule (`TREAD_WALL_FT`) and
    the margin. It kept the web's `house_hit` pad (2 ft) until feature 302 found a corridor 3.80 ft from its own house's wall
    (Inashiro, B7): feature 294 raised the house seating's clearance to 4 ft and not this one. The 4 ft rule is the stricter,
    so a corridor it admits the web's pad admits too."""
    return s.px(TREAD_HALF_FT + TREAD_WALL_FT + PART_MARGIN_FT)


def fixtures_clear(s: Settlement, a: Pt, b: Pt, own: Any) -> bool:
    """...NOR ITS OWN FARMSTEAD FIXTURES (feature 287, homes H32): they are parts of the homestead now, laid before the web,
    and the web draws its way along this corridor - a privy on its own path would be a lane on the privy. A persimmon is
    held off by its trunk; the path may pass under the crown."""
    half, trunk = s._access.half, s.px(4.0)
    return not any(seg_box_within(a, b, box if kind != "persimmon" else (box[0], box[1], trunk, trunk), half) for kind, box in ((own.get("boxes") or {}).get("fixtures") or {}).items())


#: Half the tread the web draws along a corridor, in feet: the ways' `ACCESS_WIDTH` (3 ft) halved - this package cannot
#: import the hamlet generator; `tests/settlement/test_access.py` holds the two equal.
TREAD_HALF_FT = 1.5

#: How much farther than the tread's half-width a corridor's line keeps off its own homestead's parts, in feet: the lane law
#: asks a tread of the overlap matrix `PLACER_MARGIN_PX` wider than it is drawn, and a leg is judged here before its ends
#: are rounded to the record's 0.1 px.
PART_MARGIN_FT = 0.5


def parts_clear(s: Settlement, a: Pt, b: Pt, own: Any) -> bool:
    """...NOR ITS OWN GARDEN BEDS, SHED, BYRE OR WELL POCKET (feature 287 M8): the overlap matrix holds a path off every
    homestead's parts but the dooryard it arrives at, its own household's too - the web draws its way along this line, so
    a corridor across its own bed would be a lane across the bed (Inashiro's flank door ran north through its second bed).
    The tread, not the corridor's reserved strip, keeps off them: the strip is the web's room to draw in, and the line is
    what it draws. The yard is the door's own ground; the web leaves it at its edge (`corridors.door_ends`)."""
    boxes = own.get("boxes") or {}
    gap = s.px(TREAD_HALF_FT + PART_MARGIN_FT)
    parts = [boxes.get(k) for k in ("shed", "byre", "well")] + list(boxes.get("gardens") or ())
    return not any(seg_box_within(a, b, box, gap) for box in parts if box is not None)


def standing_clear(s: Settlement, a: Pt, b: Pt, memo: dict[Any, Any] | None = None) -> bool:
    """The half of `corridor_clear` that reads only what already stands - the reserved seats, the placed boxes, the site's
    ground and the ways' ground test - REMEMBERED while nothing of it changes (the placed boxes, the tree, the seats and
    the houses the ground test reads): the four garden sides of one seat ask the same doors of the same targets, and seed 14
    spent 136 of its 215 s asking them again (361,575 calls)."""
    memo = _standing_memo(s)[1] if memo is None else memo  # a caller asking many lines at one state hands its memo in
    return standing_ground(s, a, b, memo) and lawful_leg(s, a, b, memo)


def standing_ground(s: Settlement, a: Pt, b: Pt, memo: dict[Any, Any]) -> bool:
    """`standing_clear` but for its last conjunct, the ways' ground test (`lawful_leg`), remembered the same way. The corridor
    search asks this of every line it tries and the ways' test only of a line whose corridor its own fixtures and beds leave
    clear (`access_corridor`): the ways' test is the dearest conjunct and refuses almost nothing the others pass (reference
    seed 4, feature 287 perf: 1 of 1,317 lines), while the fixtures and beds refuse most of what it was asked of."""
    key = (round(a[0], 3), round(a[1], 3), round(b[0], 3), round(b[1], 3))
    hit = memo.get(key)
    if hit is None:
        hit = memo[key] = _standing_clear(s, a, b)
    return hit


def lawful_leg(s: Settlement, a: Pt, b: Pt, memo: dict[Any, Any]) -> bool:
    """`lawful_ground` of the line a-b, remembered with the rest of what stands (`_standing_memo`)."""
    key = ("lawful", round(a[0], 3), round(a[1], 3), round(b[0], 3), round(b[1], 3))
    hit = memo.get(key)
    if hit is None:
        hit = memo[key] = lawful_ground(s, a, b)
    return bool(hit)


def _standing_memo(s: Settlement) -> tuple[Any, dict[Any, Any]]:
    """The memo of what is asked of the standing ground, kept while none of it changes (the placed boxes, the tree, the
    seats and the houses the ground test reads) and emptied when any does."""
    wood = getattr(s, "_wood", None)
    houses = s.M.get("houses") or []
    state = (len(s.placed), len(s._access.segs), wood.seats.n if wood is not None else 0, len(houses), id(houses[-1]) if houses else None)
    memo = s.__dict__.get("_corridor_memo")
    if memo is None or memo[0] != state:
        memo = s.__dict__["_corridor_memo"] = (state, {})
    return memo


def _standing_clear(s: Settlement, a: Pt, b: Pt) -> bool:
    half = s._access.half
    # THE SITE'S RASTER FIRST: the site ground is what refuses most corridors (seed 44: 82,801 of the 106,061 refused), and
    # a sample in a surely taken cell refuses one with a lookup (`site_edge_samples`)
    edge = site_edge_samples(s, a, b)
    if edge is None:
        return False
    # ...NOR OVER A HOUSEHOLD'S SHARE OF THE WOOD FLOOR (feature 287, woods W25): the way drawn along it would take the
    # reserved seats' clumps
    wood = getattr(s, "_wood", None)
    if wood is not None and wood.corridor_bars(a, b):
        return False
    x0, y0, x1, y1 = min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
    seen: set[int] = set()
    for it in s._reach_index(s.placed, "placed_reach").near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + half):
        if id(it) in seen:
            continue
        seen.add(id(it))
        # pruned with one distance before the eight the exact gap takes (`seg_box_within`; seed 44: 4 million gaps asked,
        # most of boxes in the long corridor's bounding box but nowhere near its line)
        if seg_box_within(a, b, (it[0], it[1], it[2], it[3]), half):
            return False
    return site_samples_clear(s, edge)  # ...and the ways' ground test last, apart (`lawful_leg`)


def site_edge_samples(s: Settlement, a: Pt, b: Pt) -> Iterable[Pt] | None:
    """The corridor a-b's samples, every `SAMPLE_PX`, that the site's raster (`FreeGround`, built with the boundary from the
    same ground) leaves to be asked: None where one stands in a surely taken cell (the tests refuse it), and the samples
    in a surely clear cell left out (the tests pass them). Every sample where no raster is installed. Read from the lines
    `prime_site` asked together, where it asked this one."""
    n = max(1, int(math.dist(a, b) / SAMPLE_PX))
    fg = getattr(s, "_free_ground", None)
    if fg is None:
        return [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
    if getattr(s, "_access", None) is None:  # no seating under way: nothing primed, nothing to remember
        alone: Iterable[Pt] | None = fg.lines_edge_points([(a, b, n)])[0]
        return alone
    memo = _standing_memo(s)[1]
    key = ("site", a, b)
    if key not in memo:
        memo[key] = fg.lines_edge_points([(a, b, n)])[0]
    edge: Iterable[Pt] | None = memo[key]
    return edge


def prime_site(s: Settlement, segs: list[tuple[Pt, Pt]]) -> None:
    """Ask the site's raster of all these corridors at once (`FreeGround.lines_edge_points`), for `site_edge_samples` to
    read: a homestead's corridor search is some seventy lines, and asked one by one each paid the array's setup."""
    fg = getattr(s, "_free_ground", None)
    if fg is None:
        return
    memo = _standing_memo(s)[1]
    todo = [(a, b) for a, b in dict.fromkeys(segs) if ("site", a, b) not in memo]
    for (a, b), edge in zip(todo, fg.lines_edge_points([(a, b, max(1, int(math.dist(a, b) / SAMPLE_PX))) for a, b in todo]), strict=True):
        memo[("site", a, b)] = edge


def site_samples_clear(s: Settlement, pts: Iterable[Pt]) -> bool:
    """Do these points stand on ground the site boundary admits - not on the field's side of a chord, not within a water
    course's clearance, not inside the outline of the other ground?"""
    chains, corr = getattr(s, "_site_chains", None), getattr(s, "_site_corridors", None)
    if chains and any(chain_violated(px, py, chains, 0.0) for px, py in pts):
        return False
    return not (corr is not None and any(corr.hit_points([p]) for p in pts))


def on_site_ground(s: Settlement, a: Pt, b: Pt) -> bool:
    """Does a corridor's line a-b stand on ground the site boundary admits, at every sample (`site_edge_samples`, then
    `site_samples_clear`)? The raster answers first: seed 44's 6.7 million samples each asked every test, three quarters
    of the seating."""
    edge = site_edge_samples(s, a, b)
    return edge is not None and site_samples_clear(s, edge)


def lawful_ground(s: Settlement, a: Pt, b: Pt) -> bool:
    """Would the web's way along a-b stand on lawful ground? THE WAYS' OWN PREDICATE (`settle.corridor_on_lawful_ground`:
    the run squared at its water crossings, then judged by the ground half of the law the web draws by), installed on the
    settlement by the hamlet's seating as `_corridor_ground` - the settlement package cannot import the hamlet generator.
    With none installed (a village roll) the site boundary's test above is the whole test."""
    ground = getattr(s, "_corridor_ground", None)
    return ground is None or bool(ground([a, b]))


def round_the_gable(geom: Any, door: Pt, half: float) -> Pt:
    """Where a corridor from a dooryard flank door (`doors_of`) turns once it has passed its house: carried back along the
    gable, parallel to the house's front-to-yard axis, past the back wall by a corridor's half-width and a foot - so the
    leg beside the house clears it and the turn stands behind its corner, not behind its wall."""
    boxes = geom.get("boxes") or {}
    yard = boxes.get("yard") or geom.get("yard")
    hx, hy, hw, hh = boxes.get("house") or geom["house"]
    d = math.hypot(float(yard[0]) - hx, float(yard[1]) - hy) or 1.0
    ux, uy = (float(yard[0]) - hx) / d, (float(yard[1]) - hy) / d
    back = hw / 2 * abs(ux) + hh / 2 * abs(uy) + half + 1.0  # the back wall's reach behind the center, and the strip past it
    t = (door[0] - hx) * ux + (door[1] - hy) * uy + back
    return (door[0] - ux * t, door[1] - uy * t)


def access_corridor(s: Settlement, geom: Any) -> tuple[Pt, ...] | None:
    """The corridor this homestead would be admitted with: from a dooryard door to the first of the tree's nearest points
    that a clear strip reaches (`corridor_clear`) - straight, or, where the tree lies behind the house, from a flank door
    carried past the gable first (`round_the_gable`), two legs, or - on a tree that routes (`AccessTree.routed`, the
    nucleated seating's) - routed round what stands (`route.routed_corridors`), at most `ROUTE_LEGS` legs. None when none
    of these is admitted - the seat is refused (the ONE predicate the placer reads and its test reads).

    THE SEARCH IS SHARED BY THE HOMESTEADS THAT SHARE ITS HOUSE AND YARD, while nothing standing changes (`_standing_memo`):
    the four garden sides of one seat have the same doors, the same gable and the same house, and differ only in their
    fixtures. So the candidates that clear the house and the standing ground are found once, in the search's order and
    only as far as asked (`_house_candidates`), and each homestead takes the first of them its own fixtures leave clear -
    the corridor the search would have returned (seed 44: 610,000 strips asked for 12,215 searches, nearly all refused)."""
    tree = getattr(s, "_access", None)
    if tree is None:
        return None
    boxes = geom.get("boxes") or {}
    key = ("corridor", tuple(boxes.get("house") or geom["house"]), tuple(boxes.get("yard") or geom.get("yard") or ()))
    memo = _standing_memo(s)[1]
    found = memo.get(key)
    if found is None:
        found = memo[key] = ([], _house_candidates(s, tree, geom))
    seen: list[tuple[Pt, ...]] = found[0]
    more: Iterator[tuple[Pt, ...]] = found[1]
    k = 0
    while True:
        if k == len(seen):
            nxt = next(more, None)
            if nxt is None:
                return None
            seen.append(nxt)
        corridor = seen[k]
        if corridor is ROUTE_LATER:
            k += 1
            continue
        # the leg onto the tree passes unasked where it has no length, as the search passed it; every other leg is asked
        last = len(corridor) - 2
        # ...and the ways' ground test of each leg the search asked, after its own fixtures and beds (`standing_ground`)
        if all((n == last and math.dist(a, b) < 1e-6) or (fixtures_clear(s, a, b, geom) and parts_clear(s, a, b, geom)) for n, (a, b) in enumerate(legs(corridor))) and all(
            (n == last and math.dist(a, b) < 1e-6) or lawful_leg(s, a, b, memo) for n, (a, b) in enumerate(legs(corridor))
        ):
            # ...AS IT WILL BE DRAWN - from where it leaves its own threshing yard (`drawn_corridor`) - AND ONLY WHERE THE WHOLE
            # TREE STAYS LAWFUL WITH IT (feature 287 wave 6, ways W01): every joint among the tree's lanes is known here, so a
            # corridor the tree cannot take lawfully is refused now and the next tried, never found at the web's draw
            drawn = drawn_corridor(s, corridor, geom)
            if tree_admits(s, drawn, geom):
                return drawn
        k += 1


def seat_reaches_tree(s: Settlement, core: Any) -> bool:
    """Has this house and yard ANY corridor candidate to the access tree - a door whose strip clears the house and the standing
    ground (`_house_candidates`)? The seat's own question (feature 297, FR-002), asked of the house-and-yard core before any
    layout is built: the memo entry `access_corridor` keys on the same house and yard is the one created and peeked here, so a
    layout's corridor search continues from it rather than starting again. True where no tree is installed."""
    tree = getattr(s, "_access", None)
    if tree is None:
        return True
    boxes = core.get("boxes") or {}
    key = ("corridor", tuple(boxes.get("house") or core["house"]), tuple(boxes.get("yard") or core.get("yard") or ()))
    memo = _standing_memo(s)[1]
    found = memo.get(key)
    if found is None:
        found = memo[key] = ([], _house_candidates(s, tree, core))
    if found[0]:
        return True
    nxt = next(found[1], None)
    if nxt is None:
        return False
    found[0].append(nxt)
    return True


def yard_quad(geom: Any) -> list[Pt] | None:
    """A homestead's threshing yard as the overlap matrix will read it: its rect turned with its house (`_attach_yard` draws
    it at the house's rake about its own center, `registry.element_extents` reads the record's turned rect), or None for a
    bundle with no yard."""
    yard = geom.get("yard")
    if yard is None:
        return None
    x, y, w, h = (float(v) for v in yard)
    th = math.radians(float(geom.get("turn") or 0.0))
    c, sn = math.cos(th), math.sin(th)
    return [(x + dx * c - dy * sn, y + dx * sn + dy * c) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]


#: How far past its own threshing yard's edge, beyond the tread's half-width, a corridor's drawn door end stands
#: (`past_the_yard`): the overlap matrix asks a tread `PLACER_MARGIN_PX` (0.2) wider than drawn and the record rounds to 0.1,
#: so a foot is room for both. A map drawing convention.
YARD_EXIT_PAD_FT = 1.0


def past_the_yard(run: Any, yard: Any, half: float) -> list[Pt] | None:
    """`run` from where its tread (`half` wide either side) leaves the threshing yard `yard` (its quad) for good: the arc past
    the last point within `half` and `YARD_EXIT_PAD_FT` of the yard. The overlap matrix forbids a way on a yard, its own
    household's too (a path arrives at its dooryard and does not cross it), and the door stands in the yard's middle
    (`doors_of`) - an 81-mat yard 76 x 53 ft left every door end the web once trimmed to 40 ft still on it (cohort seed 39
    under feature 284's probes). The corridor leaves its yard once (`leaves_its_yard`), so the run past it is the reserved
    ground. None where the run never comes that near the yard or ends on it."""
    from shapely.geometry import LineString, Point, Polygon

    pts = [(float(q[0]), float(q[1])) for q in run]
    line = LineString(pts)
    inside = line.intersection(Polygon([(float(q[0]), float(q[1])) for q in yard]).buffer(half + YARD_EXIT_PAD_FT))
    if inside.is_empty:
        return None
    s0 = max(line.project(Point(c)) for g in getattr(inside, "geoms", [inside]) for c in g.coords)
    if s0 >= line.length - 1.0:
        return None
    out: list[Pt] = []
    acc = 0.0
    for a, b in zip(pts, pts[1:], strict=False):
        d = math.dist(a, b)
        if acc + d > s0 and d > 0:
            if not out:
                t = max(0.0, (s0 - acc) / d)
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            out.append(b)
        acc += d
    return out


def drawn_corridor(s: Settlement, corridor: tuple[Pt, ...], geom: Any) -> tuple[Pt, ...]:
    """The corridor as the web will draw it: from where it leaves the homestead's own threshing yard (`past_the_yard`, at
    the tread's half-width), else as found. What the seating reserves and records, so the tree the web draws is the tree the
    seating judged."""
    yard = yard_quad(geom)
    past = past_the_yard(corridor, yard, s.px(TREAD_HALF_FT)) if yard is not None else None
    return tuple(past) if past is not None and len(past) >= 2 else corridor


def tree_admits(s: Settlement, corridor: tuple[Pt, ...], geom: Any) -> bool:
    """Would the access tree, drawn as lanes with this corridor added, keep the whole lane law among its lanes? THE WAYS' OWN
    PREDICATE (`hamletgen/ways/tree.py:tree_admits`), installed on the settlement by the hamlet's seating as `_corridor_tree`
    - the settlement package cannot import the hamlet generator. Remembered per corridor while nothing standing changes.
    With none installed (a village roll) every corridor is admitted, as the ground test is."""
    judge = getattr(s, "_corridor_tree", None)
    if judge is None:
        return True
    memo = _standing_memo(s)[1]
    key = ("tree", corridor, tuple(geom["house"]))
    if key not in memo:
        memo[key] = bool(judge(corridor, geom))
    return bool(memo[key])


def _house_candidates(s: Settlement, tree: AccessTree, geom: Any) -> Iterator[tuple[Pt, ...]]:
    """The corridors `access_corridor` would try, in its order, that clear the house and the standing ground - a leg onto
    the tree of no length (a door on the tree) passes unasked, as the search passed it."""
    doors = doors_of(geom, tree.half)
    turns = {door: round_the_gable(geom, door, tree.half) for door in doors[2:]}
    prime_site(s, [(door, q) for door in doors for q in tree.targets(door)] + [seg for door, turn in turns.items() for seg in [(door, turn), *((turn, q) for q in tree.targets(turn))]])
    memo = _standing_memo(s)[1]
    hgap = house_gap(s)

    def clear(a: Pt, b: Pt) -> bool:
        # a strip the site's raster refused (`prime_site`) is refused by the standing ground before anything is asked
        # ...the ways' ground test left to `access_corridor`, which asks it after the fixtures and beds (`standing_ground`)
        return memo.get(("site", a, b), ()) is not None and house_clear(a, b, geom, hgap) and standing_ground(s, a, b, memo)

    yard = (geom.get("boxes") or {}).get("yard")
    gap = s.px(TREAD_HALF_FT + PART_MARGIN_FT)
    for door in doors:
        for q in tree.targets(door):
            if math.dist(door, q) < 1e-6 or (clear(door, q) and leaves_its_yard((door, q), yard, gap)):
                yield (door, q)
    for door in doors[2:]:  # the flank doors: round the gable (none on a bundle with no yard)
        turn = turns[door]
        if not clear(door, turn):
            continue
        for q in tree.targets(turn):
            # ...never back past the house it went round (`doubles_back`): the web could not draw it (cohort seed 32)
            if math.dist(turn, q) < 1e-6 or (not doubles_back(door, turn, q) and clear(turn, q) and leaves_its_yard((door, turn, q), yard, gap)):
                yield (door, turn, q)
    if tree.routed:  # ...then the path routed round what stands (feature 308, plan D3; FR-005)
        from .route import routed_corridors

        yield ROUTE_LATER  # the seat MAY be reached by a route: `seat_reaches_tree` says so without searching for one
        yield from routed_corridors(s, tree, geom)


#: The marker `_house_candidates` yields between its straight corridors and its routed ones (feature 308): the seat's own
#: question (`seat_reaches_tree`) takes it as a YES - a route may be found - so the route's search, the dearest of the seat's
#: questions, is asked only by `access_corridor`, after the parts' cheap refusals (the wood's seats, the sun). The verdict is
#: the same, asked later: a seat no route reaches is refused there. `access_corridor` passes over it.
ROUTE_LATER: tuple[Pt, ...] = ((math.inf, math.inf),)  # one object, asked by identity; no corridor is it


def leaves_its_yard(corridor: tuple[Pt, ...], yard: Any, gap: float, step: float = 2.0) -> bool:
    """Does a corridor leave its own threshing yard (`(cx, cy, w, h)`, grown by `gap`) at most once, never to cross it again
    (feature 287 M8)? The door stands in or beside the dooryard and the web draws the way from where the corridor leaves it
    (`corridors.door_ends`); a corridor from a flank door back across the yard (cohort seed 48) was a way the matrix refuses
    anywhere along the yard, so the house was left with none."""
    if yard is None:
        return True
    cx, cy, w, h = (float(v) for v in yard)

    def inside(p: Pt) -> bool:
        return abs(p[0] - cx) < w / 2 + gap and abs(p[1] - cy) < h / 2 + gap

    left = False
    for a, b in legs(corridor):
        n = max(1, int(math.dist(a, b) // step))
        for k in range(n + 1):
            p = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            if inside(p):
                if left:
                    return False
            else:
                left = True
    return True


#: A turn a path cannot take, in degrees off straight on: the web's own bend law (`hamletgen/ways/clearance._HAIRPIN_DEG`,
#: "doubles back"), which this package cannot import; `tests/settlement/test_access.py` holds the two equal.
HAIRPIN_DEG = 140.0


def doubles_back(a: Pt, b: Pt, c: Pt) -> bool:
    """THE ONE PREDICATE of a corridor's turn (feature 287, homes wave 5): does the run a-b-c turn at b by `HAIRPIN_DEG` or
    more? A corridor carried round the gable to a tree point back in front of the house doubles back on itself, and the web
    - which draws a way along a corridor only where its bend law admits it - left the house with no way at all."""
    u, v = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
    nu, nv = math.hypot(*u), math.hypot(*v)
    if nu < 1e-9 or nv < 1e-9:
        return False
    cos = max(-1.0, min(1.0, (u[0] * v[0] + u[1] * v[1]) / (nu * nv)))
    return math.degrees(math.acos(cos)) >= HAIRPIN_DEG


def legs(corridor: tuple[Pt, ...]) -> list[tuple[Pt, Pt]]:
    """A corridor's straight legs, door first."""
    return list(zip(corridor, corridor[1:], strict=False))


def reserve(s: Settlement, corridor: tuple[Pt, ...], of: Pt | None = None) -> None:
    """Add an admitted house's corridor to the tree and to the manifest's record, a record per leg, the first naming the
    house it serves (`of`, its center) - the records the web reads to draw a way along the corridor of a house its lanes do
    not reach, following the chain from the door's leg to the next."""
    for k, (a, b) in enumerate(legs(corridor)):
        s._access.add(a, b)
        rec: dict[str, Any] = {"pts": [[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)]]}
        if of is not None and k == 0:
            rec["of"] = [round(of[0], 1), round(of[1], 1)]
        s.M.setdefault("access_corridors", []).append(rec)
