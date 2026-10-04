"""A nucleated cluster GROWN from its first house (feature 308, plan D1 and D2; FR-003, FR-004, FR-007).

The GM, 2026-10-02: *"once you've placed the first house, you should notionally be able to compute the minimum distance needed to
seat a second house, then place it in a direction, then repeat, with a little randomized jitter to the distance and direction so
that it's not jhusgt [just] an unrealistic grid"* - and *"keep in mind the sunlight / shade requirements when computing minimum
distance, since 'contents of the homestead' is not the only thing which determines minimum distance, i.e. casting shade on a
threshing yard also contributes."*

- THE FIRST HOUSE is offered the margin's free ground nearest the seat, in order (`capacity.free_seats` through the seat region),
  so the cluster starts against its field, where the front row started.
- EACH NEXT HOUSE is offered from a house already standing, in a ring of directions round it, at the distance in that direction
  where the two homesteads' FOOTPRINTS part (`seat_toward`), plus a path's room (`grow_gap`). Direction and distance are jittered
  by a hash of the standing house's position (`_hjit`, no random draw), so a map grows the same way every roll. A standing
  homestead's footprint (`footprint`) is its envelope, its reserved woodlot seats, and to the SOUTH the sun its threshing yard
  and its beds are owed (`SUN_CORRIDOR_FT` and the placer's 2 ft, the reach of `_sun_corridor_ok` and `_gardens_sun_ok`). The new household's own reach is its envelope rolled AT THE SEAT
  offered, exactly as the placer will lay it there - its own house, kura, fixtures, byre and well pocket from its lot
  (`household_reach`, `settled_seat`): its yard and beds are rolled from where it stands, so
  the seat is moved out until its own envelope there clears - no seat is offered closer than its own footprint allows.
- A SEAT THE GROUND REFUSES IS NEVER LAID OUT (feature 314): before the household's envelope is rolled at a seat, the questions
  that need no layout are asked of the house there (`seat_refused`) - its own box against the canvas, the
  reserved corridors, the placed homesteads and the refused-ground grid, exactly as the placer asks them - and a seat they refuse
  is dropped. Laying out the household was 11% of the stage on seats the placer then refused for one of these in a lookup.
- Seats are offered nearest the seat first, in rings, the nearer the field first within a ring (`grow_key`, feature 318, the GM:
  "all else being equal, try this first"), and each is judged by the placer's full rules (`try_place`), a lane's threading gap
  from every standing homestead (`keeps_every_gap`). No radius and no distance from the field refuses one. No path is searched
  while it is seated: its yard must open onto lane ground (`SeatRegion.opens`), and every way is laid in the gaps once the last
  house stands (`settlement/rolling/gap_ways.py`).
- WHEN THE SEATS RUN DRY with households left, every standing house offers again one ring further (`grow_level`, past
  `GROW_LEVELS`), until a level queues no new seat on the canvas.
  No seated house is ever taken back (feature 318): a margin that cannot seat everyone is refused.

What it replaced on the nucleated form (FR-007): the front row along the field, the lattice ranks behind it and the exhaustive pass
over every free grid point with its rescue - 383 to 5,927 offers for 40 houses, a margin seated whole and thrown away where it fell
short (specs/308-grow-the-cluster/research.md R4, R6). The dispersed form keeps them, and the linear form seats its rows
(`rows.seat_rows`) - the spec's round-1 rulings.

Research: growth search - NONE: reaches, settling, search breadth and the placer's own questions; the units that decide carry their own claims
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement._geom.primitives import chain_distance, convex_hull
from l7r.diagram.settlement.rolling.lot import household_parts, seat_parts_done
from l7r.diagram.settlement.rolling.passage import crossable
from l7r.diagram.sitegen.geom import poly_area

from ..consts import MIN_WEB_GAP, SUN_CORRIDOR_FT, Pt
from .capacity import DRY_SPELL, _near_a_house, free_seats, offer_seats

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

#: The jitter on a seat's direction, in degrees either way AT EIGHT DIRECTIONS: a GUESS for the GM's "a little randomized jitter
#: ... so that it's not just an unrealistic grid" - 12 of the eight-direction ring's 45-degree step either way, and scaled with the
#: step at any other count (`grow_jitter`: 6 at sixteen), so neighboring directions never cross (at sixteen, 12 either way of a
#: 22.5-degree step did). The record gives no spacing variance for a nucleated hamlet.
GROW_JITTER_DEG = 12.0
"""Research: direction jitter - GUESS: 12 degrees either way at eight directions, scaled with the step"""
#: ...and on its distance, as a share added to the least distance (never subtracted - the least is the rule): a GUESS, as above.
GROW_JITTER_FRAC = 0.12
"""Research: distance jitter - GUESS: up to 0.12 of the least distance added"""
#: The growth's widening, (directions, rings) - each ring a multiple of the least distance - offered in turn while households are
#: left and the seats run dry, and past the table one ring further each level (`grow_level`): MEASURED on the reference at 40
#: households (feature 308, research R5): at eight directions and one ring a margin seated 29-36 of 40 and was thrown away; with the
#: three levels all sixteen seeds seat on the first or second margin. MAIN'S BREADTH (feature 318, Amendment 3, the GM: "the
#: tie-break thing for the real speedup"): one level of sixteen directions at three rings offered at once, nearest the field first,
#: tried and refused the near-field seats the field hemmed in (seed 4: 281 seats offered against 80) - withdrawn (research R1, R4).
GROW_LEVELS: tuple[tuple[int, tuple[float, ...]], ...] = ((8, (1.0,)), (12, (1.0, 1.5)), (16, (1.25, 1.75, 2.0)))
"""Research: the growth's widening - UNRESEARCHED: 8, then 12, then 16 directions at rings 1.0 to 2.0 times the least distance, a search breadth (measured: feature 308 R5)"""
#: The width of the rings of distance from the margin's seat center inside which the growth counts two seats EQUAL (feature 318,
#: FR-003a, the GM: "all else being equal, try this first"), and tries the one nearer the field first: a GUESS - about the parting
#: between two neighbors' houses, so a ring holds the seats one growth step offers and no more. A distance on a continuous scale
#: is never exactly equal (an exact tie would never fire); a ring wide enough to hold several steps would make the field the
#: primary order again, which the GM ruled out.
TIE_RING_FT = 20.0
"""Research: seats counted equal - GUESS: within one 20 ft ring of distance from the seat center, about the parting between neighbors"""
#: Half a woodlot clump's width about a reserved wood seat, in px: the copse's clump (`COPSE_CLUMP_BS` at hamlet scale is 24)
WOOD_CLUMP_PX = 12.0
#: How many times a seat is moved out to clear its own envelope rolled where it stands (`settled_seat`) before it is dropped:
#: each move only grows the reach it clears, and a roll that keeps outgrowing it is a seat not offered (a search breadth).
SETTLE_TRIES = 4
#: The position-hash salts of a seat's direction and distance jitter (`Settlement._hjit`), one per direction index
_SALT_DIRECTION, _SALT_DISTANCE = 300.0, 400.0

Reach = tuple[float, float, float, float]  # (west, east, north, south) from the house's center


def grows(plan: SitePlan) -> bool:
    """Is this hamlet's cluster grown (FR-007)? The nucleated form's; the dispersed form keeps the front row, the ranks and
    the exhaustive pass, and the linear form seats its rows (the spec's round-1 rulings)."""
    return plan.settlement_form == "nucleated"


def box_reach(center: Pt, box: Sequence[float]) -> Reach:
    """How far the box `(cx, cy, w, h)` reaches from `center` to the west, east, north and south."""
    bx, by, bw, bh = (float(v) for v in box[:4])
    return center[0] - (bx - bw / 2), (bx + bw / 2) - center[0], center[1] - (by - bh / 2), (by + bh / 2) - center[1]


def footprint(s: Settlement, rec: dict[str, Any]) -> Reach:
    """A standing homestead's footprint (FR-003): its envelope, its reserved wood seats, and to the south the sun its yard and
    beds are owed - no house's north wall within `SUN_CORRIDOR_FT` and the placer's 2 ft of a yard's or a bed's south edge.

    Research:
        sun owed to the south - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: `SUN_CORRIDOR_FT` and 2 ft south of the yard and each bed
        the household's wood - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: its reserved copse seats inside its footprint
    """
    g = rec.get("geom") or {}
    hx, hy = float(rec["x"]), float(rec["y"])
    w, e, n, so = box_reach((hx, hy), g.get("bbox") or (hx, hy, float(rec.get("w") or 0.0), float(rec.get("h") or 0.0)))  # a bare record: its house
    for p in (rec.get("wood_share") or {}).get("seats") or ():
        w, e = max(w, hx - p[0] + WOOD_CLUMP_PX), max(e, p[0] - hx + WOOD_CLUMP_PX)
        n, so = max(n, hy - p[1] + WOOD_CLUMP_PX), max(so, p[1] - hy + WOOD_CLUMP_PX)
    boxes = g.get("boxes") or {}
    sun = s.px(SUN_CORRIDOR_FT + 2.0)
    for r in (boxes.get("yard"), *(boxes.get("gardens") or ())):
        if r is not None:
            so = max(so, (r[1] + r[3] / 2) - hy + sun)
    return w, e, n, so


def seat_toward(center: Pt, standing: Reach, new: Reach, angle: float, gap: float) -> Pt:
    """The seat along `angle` (radians, screen axes) from `center` where a homestead reaching `new` from its house clears one
    reaching `standing` from `center` by `gap`: the boxes part when EITHER axis parts by `gap`, so the least of the two axes'
    needs."""
    dx, dy = math.cos(angle), math.sin(angle)
    need_x = (standing[1] + new[0]) if dx > 0 else (standing[0] + new[1])
    need_y = (standing[3] + new[2]) if dy > 0 else (standing[2] + new[3])
    # the gap on the axis that parts them, not along the bearing: added along a slant it would part them by gap x cos only
    t = min((need_x + gap) / abs(dx) if abs(dx) > 1e-9 else math.inf, (need_y + gap) / abs(dy) if abs(dy) > 1e-9 else math.inf)
    return center[0] + dx * t, center[1] + dy * t


def union(a: Reach, b: Reach) -> Reach:
    """The reach of both: the larger on each side."""
    return max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])


def settled_seat(center: Pt, standing: Reach, guess: Reach, angle: float, gap: float, scale: float, reach_at: Any, refused: Any = None, allotted: list[Reach] | None = None) -> Pt | None:
    """The seat along `angle` from `center`, `scale` times its least distance, where the new homestead - its reach rolled AT
    THE SEAT (`reach_at`) - clears the standing one (FR-004's "never closer"): from `guess`, moved out while the reach rolled
    there exceeds the reach it was placed for, each move to the union of the two; None after `SETTLE_TRIES` moves, or as soon
    as a seat it would roll at is one `refused` refuses (feature 314: the ground is asked before the layout). `allotted`, where
    given, is set to the reach the seat was parted by - the household's land as the growth allots it (feature 317)."""
    new = guess
    for _ in range(SETTLE_TRIES):
        base = seat_toward(center, standing, new, angle, gap)
        q = (center[0] + (base[0] - center[0]) * scale, center[1] + (base[1] - center[1]) * scale)
        if refused is not None and refused(q):
            return None
        got = reach_at(q)
        if all(g <= n + 1e-9 for g, n in zip(got, new, strict=True)):
            if allotted is not None:
                allotted[:] = [new]
            return q
        new = union(got, new)
    return None


def keeps_its_distance(box: Sequence[float], center: Pt, standing: Reach, gap: float) -> bool:
    """Does the homestead box `(cx, cy, w, h)` clear the footprint reaching `standing` from `center` by `gap` on one axis -
    the distance the growth seated it at (FR-004), asked of a box the placer moved (`_place_bundle_nucleated`)?"""
    bx, by, bw, bh = (float(v) for v in box[:4])
    apart_x = max((bx - bw / 2) - (center[0] + standing[1]), (center[0] - standing[0]) - (bx + bw / 2))
    apart_y = max((by - bh / 2) - (center[1] + standing[3]), (center[1] - standing[2]) - (by + bh / 2))
    return max(apart_x, apart_y) >= gap - 1e-9


def household_reach(s: Settlement, q: Pt, largest: tuple[float, float]) -> Reach:
    """The next household's envelope rolled at `q` EXACTLY as the placer will lay it there (plan review rounds 2-3): its own
    parts set as the seat search sets them (`household_parts`: the k-th plain household's lot - its fixtures, its byre, its
    well pocket), its own house from the lot's size ladder and its own kura (`_try_place_bundle`'s reading of the lot), the
    rolls keyed on `q` as the seat search keys them; taken down after (`seat_parts_done`). A household with no lot (no lots
    installed) is taken at the largest house the roll can take, the kura reserved. The fixtures are sought round the
    household's OWN walls, so no larger house bounds them (measured, research R9) - the household's own envelope does."""
    lot = household_parts(s, q[0], q[1], "plain", None)[0]
    try:
        hw, hh, shed = (s.px(46) * lot[0], s.px(28) * lot[1], bool(lot[2])) if lot is not None else (largest[0], largest[1], True)
        return box_reach(q, s._bundle_envelope(q[0], q[1], hw, hh, shed=shed))
    finally:
        seat_parts_done(s)


def seat_refused(s: Settlement, q: Pt, house: tuple[float, float]) -> bool:
    """Would the placer refuse a house of `house` (w, h) seated at `q` before laying out any part of its homestead (feature 314)?
    Its own questions, asked as it asks them (`_place_bundle_nucleated`): the house's own box as drawn
    there against the canvas, the reserved corridors and the placed homesteads (`_house_box_refused`) and the refused-ground grid
    (`FreeGround.rect_refused`: every garden side's box holds the house's, so a refused cell under it refuses them all). The
    water is not asked: a household seated where it is sought carries a pocket wherever none is in reach (`watered`)."""
    box = s._house_box(q[0], q[1], house[0], house[1])
    if s._house_box_refused(box):
        return True
    fg = getattr(s, "_free_ground", None)
    return bool(fg is not None and fg.rect_refused(box))


def next_house(s: Settlement, largest: tuple[float, float]) -> tuple[float, float]:
    """The house (w, h) the next plain household will build: its lot's rung of the size ladder (`household_parts` reads the
    same lot), or the largest the roll can take where no lots are installed."""
    lots = getattr(s, "_lots", None)
    k = sum(1 for h in s.M["houses"] if h.get("kind") == "plain")
    lot = lots.lot(k) if lots is not None else None
    return (s.px(46) * lot[0], s.px(28) * lot[1]) if lot is not None else largest


def grow_gap(s: Settlement) -> float:
    """The room left between two footprints: a lane's THREADING GAP (`MIN_WEB_GAP`: the web's own figure for two steadings a
    lane threads - `WEB_FABRIC_GAP` off each garden fence and the tread between) and the parting (`TIGHT_GAP_PX`), so a way can
    always be laid between two neighbors (feature 318, FR-011, the GM: "what if we just added a slightly higher minimum distance
    from your neighbors? Wouldn't that guarantee space for an access path?"). A corridor's line keeps `ACCESS_HALF_FT` off each
    homestead, so the gap leaves its line a band of `MIN_WEB_GAP` + the parting - 2 x `ACCESS_HALF_FT` to run in.

    Research: a lane's room between homesteads - research/questions/0081-village-lanes.drawing.html: a lane 7 ft clear of a garden fence on each side and its tread, the web's threading gap, and the 2 ft the growth leaves between neighbors
    """
    return s.px(MIN_WEB_GAP) + TIGHT_GAP_PX


def keeps_every_gap(box: Sequence[float], standing: Sequence[tuple[Pt, Reach, Any]], gap: float, tight: Any = None) -> bool:
    """Does the homestead box `(cx, cy, w, h)` clear EVERY standing footprint (`(center, reach, record)`) by `gap` - the one it
    is a tight seat against (`tight`, its record) by `TIGHT_GAP_PX` alone (feature 318, FR-011: the exemption is pairwise)?

    Research: every two homesteads a lane's gap apart - research/questions/0081-village-lanes.drawing.html: the threading gap between any two steadings; a household reached across its neighbor's yard stands against that one neighbor
    """
    bx, by, bw, bh = (float(v) for v in box[:4])
    for center, reach, rec in standing:
        g = TIGHT_GAP_PX if tight is not None and rec is tight else gap
        if (bx - bw / 2) - (center[0] + reach[1]) >= g or (center[0] - reach[0]) - (bx + bw / 2) >= g:
            continue
        if (by - bh / 2) - (center[1] + reach[3]) >= g or (center[1] - reach[2]) - (by + bh / 2) >= g:
            continue
        return False
    return True


#: The parting a TIGHT seat leaves between two footprints, in px: the 2 px the growth parts every two homesteads by, with no path's
#: strip - a household seated there stands against its neighbor's land, and is taken only by passage across the neighbor's yard
#: (feature 317, plan D2; `settlement/rolling/passage.py`).
TIGHT_GAP_PX = 2.0
"""Research:
    household against its neighbor's land - research/questions/0081-village-lanes.html: land with no way of its own to the road, reached by passage over a neighbor's
    the parting - GUESS research/questions/0081-village-lanes.drawing.html: the 2 ft the growth leaves between neighbors, with no path's strip
"""


#: How far off the bearing from a standing house to its threshing yard a TIGHT seat may stand, in degrees (feature 317): the side of
#: the house its yard lies on, as the drawing page places such a household. MEASURED (research R7): behind the house - 135 and 180
#: degrees off - a walk had to go round it and seated 1 household in 194 tight tries on 13 settlements at 15 households, the yard's
#: side 15 in 304. It was 112.5, past the perpendicular, until the impl-drift check held it to the page (research R9): at 15
#: households on seeds 1-16, 23 households were reached by passage at either value. A search breadth, not a rule of the custom: a
#: household behind its neighbor is still seated, by the growth's ordinary seats and a way of its own.
TIGHT_BEARING_DEG = 90.0
"""Research: a passage household on its neighbor's yard side - research/questions/0081-village-lanes.drawing.html: offered within 90 degrees of the bearing to the neighbor's threshing yard, the side its yard lies on"""


#: How near the access tree a TIGHT seat may stand and still be offered, in feet (feature 317): a household that close to a way has
#: a way of its own, the custom's condition failing. MEASURED (research R8): at 15 households on 13 settlements, no passage came
#: from a tight seat nearer the tree than 87 ft, and of the 135 of 343 tight tries nearer than 80 every one whose walk was found had
#: a corridor of its own; the tries the cut spares are a search breadth, never a rule - each is refused unasked as it would have been.
TIGHT_TREE_FT = 80.0
"""Research: a passage household away from a way - research/questions/0081-village-lanes.drawing.html: no tight seat offered within 80 ft of the access tree, a household near a way having one"""


def near_the_tree(s: Settlement, seat: Pt) -> bool:
    """Does a tight seat stand within `TIGHT_TREE_FT` of the access tree's nearest point (`AccessTree.targets`)?

    Research: a passage household away from a way - research/questions/0081-village-lanes.drawing.html: the distance to the access tree's nearest point
    """
    tree = getattr(s, "_access", None)
    near = tree.targets(seat)[:1] if tree is not None else []
    return bool(near) and math.dist(seat, near[0]) < s.px(TIGHT_TREE_FT)


def yard_side(center: Pt, yard: Pt, angle: float) -> bool:
    """Does the bearing `angle` (radians) from a standing house at `center` stand within `TIGHT_BEARING_DEG` of the bearing to
    its threshing yard at `yard`?

    Research: a passage household on its neighbor's yard side - research/questions/0081-village-lanes.drawing.html: the bearing off the bearing to the yard
    """
    to_yard = math.atan2(yard[1] - center[1], yard[0] - center[0])
    off = abs((math.degrees(angle - to_yard) + 180.0) % 360.0 - 180.0)
    return off < TIGHT_BEARING_DEG


def land_box(center: Pt, reach: Reach) -> tuple[float, float, float, float]:
    """The box `(cx, cy, w, h)` a footprint reaching `reach` (west, east, north, south) from `center` covers - a standing
    household's land as the growth parts it, which a passage's walk may cross (feature 317).

    Research: a household's land - NONE: the box its footprint covers
    """
    w, e, n, so = reach
    return (center[0] + (e - w) / 2.0, center[1] + (so - n) / 2.0, w + e, n + so)


def built_share(houses: Sequence[dict[str, Any]]) -> float:
    """The share of a nucleated cluster's outline its homesteads cover (feature 318, FR-007): the homesteads' boxes (house,
    yard, gardens and the homestead grove, `geom.bbox`) over the convex hull of their corners. REPORTED, never enforced - page
    0032's quarter-built floor binds a village, and "a hamlet is rightly loose and is not held to it". 0.0 under three
    homesteads (no outline).

    Research: the built share reported - research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html: the quarter-built figure measured on every nucleated map, refusing nothing
    """
    boxes = [(rec.get("geom") or {}).get("bbox") for rec in houses]
    boxes = [b for b in boxes if b]
    if len(boxes) < 3:
        return 0.0
    corners = [(float(x) + sx * float(w) / 2.0, float(y) + sy * float(h) / 2.0) for x, y, w, h in boxes for sx in (-1, 1) for sy in (-1, 1)]
    hull = convex_hull(corners)
    area = poly_area(hull) if len(hull) >= 3 else 0.0
    return round(min(1.0, sum(float(b[2]) * float(b[3]) for b in boxes) / area), 3) if area > 0.0 else 0.0


def grow_jitter(ndir: int) -> float:
    """The direction jitter, degrees either way, at `ndir` directions: `GROW_JITTER_DEG` at eight, scaled with the step.

    Research: direction jitter - GUESS: scaled with the step, so neighboring directions never cross
    """
    return GROW_JITTER_DEG * 8.0 / ndir


def grow_level(level: int) -> tuple[int, tuple[float, ...]]:
    """The growth's `level`-th widening: `GROW_LEVELS`' (directions, rings), and past the table 16 directions on one ring half
    the least distance further out each level (feature 318: the cluster grows at its edge until every household stands; no
    radius stops it).

    Research: the growth's widening past the table - UNRESEARCHED: a ring half the least distance further each level, a search breadth
    """
    if level < len(GROW_LEVELS):
        return GROW_LEVELS[level]
    return 16, (GROW_LEVELS[-1][1][-1] + 0.5 * (level - len(GROW_LEVELS) + 1),)


def on_the_canvas(s: Settlement, q: Pt) -> bool:
    """Does the seat `q` stand on the map's canvas - the growth's only bound on where it queues a seat (feature 318)?

    Research: plumbing - NONE: the canvas's extent
    """
    x0, y0, x1, y1 = getattr(s, "_canvas_box", None) or (0.0, 0.0, float(s.W), float(s.H))
    return x0 <= q[0] <= x1 and y0 <= q[1] <= y1


def field_distance(s: Settlement, q: Pt) -> float:
    """How far the seat `q` stands from the field's facing chains (`s._site_chains`) - the growth's TIE-BREAK: of two seats in
    one ring of distance from the seat center, the nearer the field is tried first (feature 318, FR-003a, the GM: "all else
    being equal, try this first"). 0 where no chains are installed.

    Research: nearer the field, all else being equal - CANON: the GM's rulings of 2026-10-03, people did not want to walk far to their fields; never a limit, never ahead of the ring
    """
    chains = getattr(s, "_site_chains", None)
    return float(chain_distance(q[0], q[1], chains)) if chains else 0.0


def grow_key(s: Settlement, q: Pt, center: Pt) -> tuple[int, float, float]:
    """The growth's order for the seat `q`: its ring of distance from the margin's seat `center` (`TIE_RING_FT` wide), then its
    distance from the field (`field_distance`), then its exact distance - nearest the seat first, the field breaking ties
    within a ring (feature 318, FR-003a).

    Research: nearest the seat first, the field a tie-break - CANON: the GM's ruling of 2026-10-03, all else being equal; the ring a GUESS (`TIE_RING_FT`)
    """
    d = math.hypot(q[0] - center[0], q[1] - center[1])
    return int(d // s.px(TIE_RING_FT)), field_distance(s, q), d


def tie_reordered(heap: Sequence[tuple[Any, ...]], popped: tuple[Any, ...]) -> bool:
    """Did the tie-break pop `popped` ahead of a seat in its own ring nearer the seat center - a seat the distance alone would
    have tried first (`seat_search.tie_reordered`, SC-002a: the count shows the tie-break fires)?

    Research: plumbing - NONE: a count of the order's effect
    """
    return any(e[0] == popped[0] and e[2] < popped[2] for e in heap)


def grow_the_margin(s: Settlement, plan: SitePlan, placed: int, largest: tuple[float, float]) -> int:
    """Seat `plan.spec.households` on this margin by growth (the module's account); returns the count seated. `largest` is the
    largest house `(w, h)` the roll can take. Records `seat_search.grow_offered`,
    `grow_took` and `grow_level` (the widening levels it needed).

    Research:
        cluster grown house by house - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.html, research/questions/0032-how-our-maps-pack-a-clustered-villages-houses.drawing.html: each next house where two footprints part by a lane's threading gap, jittered, nearest the seat first, nearer the field breaking ties (`grow_key`)
        first house against the field - UNRESEARCHED: the free ground nearest the seat's center
        tight seats for a passage household - research/questions/0081-village-lanes.drawing.html: offered round each house a passage may cross while the settlement's share has room, beside the ordinary seats
        a neighbor's land - research/questions/0081-village-lanes.drawing.html: its footprint as the growth parts it (`land_box`), which the household's land must adjoin
        the growth's widening - UNRESEARCHED: 8, then 12, then 16 directions (`GROW_LEVELS`), then one ring further each level, while households are left and the canvas offers seats (`grow_level`)
    """
    want = plan.spec.households
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    offered = took = 0
    if not s.M.get("houses") and placed < want:
        seats = free_seats(s, (cx, cy))
        region = getattr(s, "_seat_region", None)
        if region is not None:
            seats = [q for q, ok in zip(seats, region.offer(seats), strict=True) if ok]
        placed, offered, took = offer_seats(s, seats, placed, placed + 1, DRY_SPELL)
    houses = s.M.get("houses") or []
    level = reordered = 0
    if houses and placed < want:
        h0 = houses[0]

        last: list[Reach] = []

        def reach_at(q: Pt) -> Reach:
            got = household_reach(s, q, largest)
            last[:] = [got]
            return got

        guess = reach_at((float(h0["x"]), float(h0["y"])))
        gap = grow_gap(s)
        start = guess
        heap: list[tuple[Any, ...]] = []  # (ring, field distance, distance, n, seat, how it was offered) - `grow_key`
        tight: set[tuple[int, int]] = set()  # the standing houses whose tight seats are queued (feature 317)
        seen: set[tuple[Any, ...]] = set()
        done = 0
        while placed < want:
            ndir, rings = grow_level(level)
            queued = 0
            for rec in houses[done:]:
                hx, hy = float(rec["x"]), float(rec["y"])
                reach = footprint(s, rec)
                for k in range(ndir):
                    ang = math.radians(360.0 / ndir * k + (s._hjit(hx, hy, _SALT_DIRECTION + k) - 0.5) * 2.0 * grow_jitter(ndir))
                    far = 1.0 + s._hjit(hx, hy, _SALT_DISTANCE + k) * GROW_JITTER_FRAC
                    base = seat_toward((hx, hy), reach, guess, ang, gap)
                    for ring in rings:
                        # queued at the GUESS's seat and SETTLED only when offered (`settled_seat`): the household it is
                        # settled for is the one seated next, and most queued seats are never offered (seed 8 at 15
                        # households: 448 queued, 194 offered - settling each as queued was 1.27 s of a 2.6 s seating)
                        q = (hx + (base[0] - hx) * far * ring, hy + (base[1] - hy) * far * ring)
                        key = (round(q[0] / 10.0), round(q[1] / 10.0))
                        if key not in seen and on_the_canvas(s, q):
                            seen.add(key)
                            queued += 1
                            heapq.heappush(heap, (*grow_key(s, q, (cx, cy)), len(seen), q, ((hx, hy), reach, ang, far * ring, None)))
                # ...AND, WHILE THE SHARE HAS ROOM, ITS TIGHT SEATS (feature 317, plan D2): at the parting with no path's strip,
                # in the same directions, unjittered in distance - a household there stands against this one's land, and is
                # taken only by passage across its yard (`fit._parts_fit`, `passage.passage_of`); queued once a house, only round
                # one a passage may cross to (`passage.crossable`), and only on its yard's side (`yard_side`)
                hkey = (round(hx), round(hy))
                if getattr(s, "_passage_left", 0) > 0 and hkey not in tight and crossable(rec):
                    tight.add(hkey)
                    yard = rec["geom"]["boxes"]["yard"]
                    for k in range(ndir):
                        ang = math.radians(360.0 / ndir * k + (s._hjit(hx, hy, _SALT_DIRECTION + k) - 0.5) * 2.0 * grow_jitter(ndir))
                        if not yard_side((hx, hy), (float(yard[0]), float(yard[1])), ang):
                            continue
                        q = seat_toward((hx, hy), reach, guess, ang, TIGHT_GAP_PX)
                        if on_the_canvas(s, q):
                            seen.add(("tight", round(q[0] / 10.0), round(q[1] / 10.0)))
                            queued += 1
                            heapq.heappush(heap, (*grow_key(s, q, (cx, cy)), len(seen), q, ((hx, hy), reach, ang, 1.0, rec)))
            done = len(houses)
            if not heap:
                if level >= len(GROW_LEVELS) and not queued:
                    break  # ...widened past the table until a level queues no new seat on the canvas: the ground is full
                level, done = level + 1, 0  # DRY: every standing house offers again, wider
                continue
            top = heapq.heappop(heap)
            reordered += tie_reordered(heap, top)
            seat, (center, reach, ang, scale, nb) = top[4:]
            if nb is not None and (getattr(s, "_passage_left", 0) <= 0 or near_the_tree(s, seat)):
                continue  # the share is spent, or the seat stands by a way (`TIGHT_TREE_FT`): a tight seat is no seat
            parting = TIGHT_GAP_PX if nb is not None else gap
            house = next_house(s, largest)
            lot: list[Reach] = []
            got = settled_seat(center, reach, start, ang, parting, scale, reach_at, lambda q, h=house: seat_refused(s, q, h), lot)
            if got is not None:  # the next settle starts from the reach this one settled on (fewer rolls a seat)
                start = union(guess, last[0])
            if got is None or _near_a_house(s, got):
                continue
            q = got
            offered += 1
            s._seat_search["candidates"] += 1
            # the placer's one computed move off a third homestead may not carry it nearer its source than the growth's distance
            # ...NOR NEARER ANY OTHER STANDING HOMESTEAD THAN THE THREADING GAP (FR-011), a tight seat's own neighbor by the parting
            standing = [((float(h["x"]), float(h["y"])), footprint(s, h), h) for h in houses]
            s._grown_keep = lambda box, c=center, r=reach, g=parting, st=standing, nb_=nb: keeps_its_distance(box, c, r, g) and keeps_every_gap(box, st, gap, nb_)  # type: ignore[attr-defined]
            # ...a tight seat's household told its neighbor, the two lands as the growth parted them (its own: the reach the seat
            # was parted by, `lot`, carried with its house), and the parting
            s._tight_of = {"rec": nb, "land": land_box(center, reach), "own": lot[0], "gap": TIGHT_GAP_PX} if nb is not None else None  # type: ignore[attr-defined]
            try:
                seated = s.try_place(q[0], q[1], "plain")
            finally:
                s._grown_keep = None  # type: ignore[attr-defined]
                s._tight_of = None  # type: ignore[attr-defined]
            if seated:
                placed += 1
                took += 1
    s._seat_search["grow_offered"], s._seat_search["grow_took"], s._seat_search["grow_level"] = offered, took, level
    s._seat_search["tie_reordered"] = s._seat_search.get("tie_reordered", 0) + reordered
    return placed
