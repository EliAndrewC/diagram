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

import math
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


class AccessTree:
    """The reserved corridors: segments `(a, b)` a footpath wide (`half` either side), indexed by their widened boxes."""

    __slots__ = ("grid", "half", "segs")

    def __init__(self, half: float) -> None:
        self.half = half
        self.segs: list[tuple[Pt, Pt]] = []
        self.grid = PointGrid(128.0)

    def add(self, a: Pt, b: Pt) -> None:
        self.segs.append((a, b))
        h = self.half
        self.grid.extend([(a, b, min(a[0], b[0]) - h, min(a[1], b[1]) - h, max(a[0], b[0]) + h, max(a[1], b[1]) + h)])

    def covers_box(self, box: Any) -> bool:
        """Does any corridor's strip meet the box `(cx, cy, w, h)`? The ONE test an envelope asks (plan M3: every later
        placement refuses to cover a corridor)."""
        cx, cy, w, h = box
        for a, b, x0, y0, x1, y1 in self.grid.near(cx, cy, max(w, h) / 2 + self.half):
            if x1 < cx - w / 2 or x0 > cx + w / 2 or y1 < cy - h / 2 or y0 > cy + h / 2:
                continue
            if _seg_box_gap(a, b, box) < self.half:
                return True
        return False

    def targets(self, p: Pt) -> list[Pt]:
        """The nearest point of each corridor and its points every `TARGET_STEP_PX`, nearest first, at most
        `TARGETS_TRIED`."""
        pts: list[Pt] = []
        for a, b in self.segs:
            pts.append(seg_closest(p[0], p[1], a, b))
            n = int(math.dist(a, b) // TARGET_STEP_PX)
            pts += [(a[0] + (b[0] - a[0]) * k / max(1, n), a[1] + (b[1] - a[1]) * k / max(1, n)) for k in range(n + 1)]
        pts.sort(key=lambda q: math.dist(p, q))
        return pts[:TARGETS_TRIED]


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
    tree = s._access
    half = tree.half
    house = own.get("boxes", {}).get("house") or own["house"]
    if _seg_box_gap(a, b, house) < 0.5:
        return False
    # ...NOR ITS OWN FARMSTEAD FIXTURES (feature 287, homes H32): they are parts of the homestead now, laid before the web,
    # and the web draws its way along this corridor - a privy on its own path would be a lane on the privy. A persimmon
    # is held off by its trunk; the path may pass under the crown.
    for kind, box in ((own.get("boxes") or {}).get("fixtures") or {}).items():
        if _seg_box_gap(a, b, box if kind != "persimmon" else (box[0], box[1], s.px(4.0), s.px(4.0))) < half:
            return False
    return standing_clear(s, a, b)


def standing_clear(s: Settlement, a: Pt, b: Pt) -> bool:
    """The half of `corridor_clear` that reads only what already stands - the reserved seats, the placed boxes, the site's
    ground and the ways' ground test - REMEMBERED while nothing of it changes (the placed boxes, the tree, the seats and
    the houses the ground test reads): the four garden sides of one seat ask the same doors of the same targets, and seed 14
    spent 136 of its 215 s asking them again (361,575 calls)."""
    wood = getattr(s, "_wood", None)
    houses = s.M.get("houses") or []
    state = (len(s.placed), len(s._access.segs), wood.seats.n if wood is not None else 0, len(houses), id(houses[-1]) if houses else None)
    memo = s.__dict__.get("_corridor_memo")
    if memo is None or memo[0] != state:
        memo = s.__dict__["_corridor_memo"] = (state, {})
    key = (round(a[0], 3), round(a[1], 3), round(b[0], 3), round(b[1], 3))
    hit = memo[1].get(key)
    if hit is None:
        hit = memo[1][key] = _standing_clear(s, a, b)
    return hit


def _standing_clear(s: Settlement, a: Pt, b: Pt) -> bool:
    half = s._access.half
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
        # a box whose center stands its half-diagonal and the strip's half clear of the line cannot meet the strip: pruned
        # with one distance before the eight the exact gap takes (seed 44: 4 million gaps asked, most of boxes in the
        # long corridor's bounding box but nowhere near its line)
        if seg_dist(it[0], it[1], a, b) - math.hypot(it[2], it[3]) / 2 >= half:
            continue
        if _seg_box_gap(a, b, (it[0], it[1], it[2], it[3])) < half:
            return False
    if not on_site_ground(s, a, b):
        return False
    return lawful_ground(s, a, b)


def on_site_ground(s: Settlement, a: Pt, b: Pt) -> bool:
    """Does a corridor's line a-b stand on ground the site boundary admits - not on the field's side of a chord, not within
    a water course's clearance?"""
    n = max(1, int(math.dist(a, b) / SAMPLE_PX))
    pts = [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
    chains, corr = getattr(s, "_site_chains", None), getattr(s, "_site_corridors", None)
    if chains and any(chain_violated(px, py, chains, 0.0) for px, py in pts):
        return False
    return not (corr is not None and any(corr.hit_points([p]) for p in pts))


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
    carried past the gable first (`round_the_gable`), two legs. None when no target is clear - the seat is refused (the ONE
    predicate the placer reads and its test reads)."""
    tree = getattr(s, "_access", None)
    if tree is None:
        return None
    doors = doors_of(geom, tree.half)
    for door in doors:
        for q in tree.targets(door):
            if math.dist(door, q) < 1e-6 or corridor_clear(s, door, q, geom):
                return (door, q)
    for door in doors[2:]:  # the flank doors: round the gable (none on a bundle with no yard)
        turn = round_the_gable(geom, door, tree.half)
        if not corridor_clear(s, door, turn, geom):
            continue
        for q in tree.targets(turn):
            if math.dist(turn, q) < 1e-6 or corridor_clear(s, turn, q, geom):
                return (door, turn, q)
    return None


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
