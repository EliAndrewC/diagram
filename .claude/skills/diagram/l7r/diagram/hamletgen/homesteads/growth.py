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
  that need no layout are asked of the house there (`seat_refused`) - the field's reach, and its own box against the canvas, the
  reserved corridors, the placed homesteads and the refused-ground grid, exactly as the placer asks them - and a seat they refuse
  is dropped. Laying out the household was 11% of the stage on seats the placer then refused for one of these in a lookup.
- Seats are offered nearest the seat first, within the form's bound, and each is judged by the placer's full rules
  (`try_place`). Its path is laid as it is placed - straight, or routed round what stands (`settlement/rolling/route.py`).
- WHEN THE SEATS RUN DRY with households left, every standing house offers again at the next of `GROW_LEVELS`: more directions,
  farther rings. Past the last the margin is short, and `seat_every_household` offers the next margin.

What it replaced on the nucleated form (FR-007): the front row along the field, the lattice ranks behind it and the exhaustive pass
over every free grid point with its rescue - 383 to 5,927 offers for 40 houses, a margin seated whole and thrown away where it fell
short (specs/308-grow-the-cluster/research.md R4, R6). The dispersed form keeps them, and the linear form seats its rows
(`rows.seat_rows`) - the spec's round-1 rulings.
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement.rolling.access import ACCESS_HALF_FT
from l7r.diagram.settlement.rolling.fit import within_field_reach
from l7r.diagram.settlement.rolling.lot import household_parts, seat_parts_done
from l7r.diagram.settlement.rolling.passage import PASSAGE_CHAIN, depth_of

from ..consts import SUN_CORRIDOR_FT, Pt
from .capacity import DRY_SPELL, _near_a_house, free_seats, offer_seats

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

    from ..plan import SitePlan

#: The jitter on a seat's direction, in degrees either way: a GUESS for the GM's "a little randomized jitter ... so that it's not
#: just an unrealistic grid" - a twelfth of the eight-direction ring's 45-degree step either way, so neighboring directions never
#: cross. The record gives no spacing variance for a nucleated hamlet.
GROW_JITTER_DEG = 12.0
#: ...and on its distance, as a share added to the least distance (never subtracted - the least is the rule): a GUESS, as above.
GROW_JITTER_FRAC = 0.12
#: The growth's widening, (directions, rings) - each ring a multiple of the least distance - offered in turn while households are
#: left and the seats run dry: MEASURED on the reference at 40 households (research R5): at eight directions and one ring a margin
#: seated 29-36 of 40 and was thrown away; with the three levels all sixteen seeds seat on the first or second margin. A search
#: breadth, never a rule - every seat is still asked every rule.
GROW_LEVELS: tuple[tuple[int, tuple[float, ...]], ...] = ((8, (1.0,)), (12, (1.0, 1.5)), (16, (1.25, 1.75, 2.0)))
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
    beds are owed - no house's north wall within `SUN_CORRIDOR_FT` and the placer's 2 ft of a yard's or a bed's south edge."""
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
    Its own questions, asked as it asks them (`_place_bundle_nucleated`): the field's reach, then the house's own box as drawn
    there against the canvas, the reserved corridors and the placed homesteads (`_house_box_refused`) and the refused-ground grid
    (`FreeGround.rect_refused`: every garden side's box holds the house's, so a refused cell under it refuses them all). The
    water is not asked: a household seated where it is sought carries a pocket wherever none is in reach (`watered`)."""
    if not within_field_reach(s, q[0], q[1]):
        return True
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
    """The room left between two footprints: a path's whole reserved strip (2 x `ACCESS_HALF_FT`) and the parting
    (`TIGHT_GAP_PX`) - the PATH OUT the GM's footprint includes (plan review round 1)."""
    return 2.0 * s.px(ACCESS_HALF_FT) + TIGHT_GAP_PX


#: The parting a TIGHT seat leaves between two footprints, in px: the 2 px the growth parts every two homesteads by, with no path's
#: strip - a household seated there stands against its neighbor's land, and is taken only by passage across the neighbor's yard
#: (feature 317, plan D2; `settlement/rolling/passage.py`).
TIGHT_GAP_PX = 2.0


def land_box(center: Pt, reach: Reach) -> tuple[float, float, float, float]:
    """The box `(cx, cy, w, h)` a footprint reaching `reach` (west, east, north, south) from `center` covers - a standing
    household's land as the growth parts it, which a passage's walk may cross (feature 317)."""
    w, e, n, so = reach
    return (center[0] + (e - w) / 2.0, center[1] + (so - n) / 2.0, w + e, n + so)


def grow_the_margin(s: Settlement, plan: SitePlan, placed: int, bound: float, largest: tuple[float, float]) -> int:
    """Seat `plan.spec.households` on this margin by growth (the module's account); returns the count seated. `bound` is the
    form's reach from the seat, `largest` the largest house `(w, h)` the roll can take. Records `seat_search.grow_offered`,
    `grow_took` and `grow_level` (the widening levels it needed)."""
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
    level = 0
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
        heap: list[tuple[float, int, Pt, Any]] = []
        tight: set[tuple[int, int]] = set()  # the standing houses whose tight seats are queued (feature 317)
        seen: set[tuple[Any, ...]] = set()
        done = 0
        while placed < want:
            ndir, rings = GROW_LEVELS[level]
            for rec in houses[done:]:
                hx, hy = float(rec["x"]), float(rec["y"])
                reach = footprint(s, rec)
                for k in range(ndir):
                    ang = math.radians(360.0 / ndir * k + (s._hjit(hx, hy, _SALT_DIRECTION + k) - 0.5) * 2.0 * GROW_JITTER_DEG)
                    far = 1.0 + s._hjit(hx, hy, _SALT_DISTANCE + k) * GROW_JITTER_FRAC
                    base = seat_toward((hx, hy), reach, guess, ang, gap)
                    for ring in rings:
                        # queued at the GUESS's seat and SETTLED only when offered (`settled_seat`): the household it is
                        # settled for is the one seated next, and most queued seats are never offered (seed 8 at 15
                        # households: 448 queued, 194 offered - settling each as queued was 1.27 s of a 2.6 s seating)
                        q = (hx + (base[0] - hx) * far * ring, hy + (base[1] - hy) * far * ring)
                        key = (round(q[0] / 10.0), round(q[1] / 10.0))
                        d = math.hypot(q[0] - cx, q[1] - cy)
                        if key not in seen and d <= bound:
                            seen.add(key)
                            heapq.heappush(heap, (d, len(seen), q, ((hx, hy), reach, ang, far * ring, None)))
                # ...AND, WHILE THE SHARE HAS ROOM, ITS TIGHT SEATS (feature 317, plan D2): at the parting with no path's strip,
                # in the same directions, unjittered in distance - a household there stands against this one's land, and is
                # taken only by passage across its yard (`fit._parts_fit`, `passage.passage_of`); queued once a house, and only
                # round one a passage may cross to - itself reached within the chain, with a yard (`passage.depth_of`)
                hkey = (round(hx), round(hy))
                depth = depth_of(rec)
                crossable = depth is not None and depth < PASSAGE_CHAIN and ((rec.get("geom") or {}).get("boxes") or {}).get("yard") is not None
                if getattr(s, "_passage_left", 0) > 0 and hkey not in tight and crossable:
                    tight.add(hkey)
                    for k in range(ndir):
                        ang = math.radians(360.0 / ndir * k + (s._hjit(hx, hy, _SALT_DIRECTION + k) - 0.5) * 2.0 * GROW_JITTER_DEG)
                        q = seat_toward((hx, hy), reach, guess, ang, TIGHT_GAP_PX)
                        d = math.hypot(q[0] - cx, q[1] - cy)
                        if d <= bound:
                            seen.add(("tight", round(q[0] / 10.0), round(q[1] / 10.0)))
                            heapq.heappush(heap, (d, len(seen), q, ((hx, hy), reach, ang, 1.0, rec)))
            done = len(houses)
            if not heap:
                if level + 1 >= len(GROW_LEVELS):
                    break
                level, done = level + 1, 0  # DRY: every standing house offers again, wider
                continue
            center, reach, ang, scale, nb = heapq.heappop(heap)[3]
            if nb is not None and getattr(s, "_passage_left", 0) <= 0:
                continue  # the share is spent: a tight seat is no seat
            parting = TIGHT_GAP_PX if nb is not None else gap
            house = next_house(s, largest)
            lot: list[Reach] = []
            got = settled_seat(center, reach, start, ang, parting, scale, reach_at, lambda q, h=house: seat_refused(s, q, h), lot)
            if got is not None:  # the next settle starts from the reach this one settled on (fewer rolls a seat)
                start = union(guess, last[0])
            if got is None or _near_a_house(s, got) or math.hypot(got[0] - cx, got[1] - cy) > bound:
                continue
            q = got
            offered += 1
            s._seat_search["candidates"] += 1
            # the placer's one computed move off a third homestead may not carry it nearer its source than the growth's distance
            s._grown_keep = lambda box, c=center, r=reach, g=parting: keeps_its_distance(box, c, r, g)  # type: ignore[attr-defined]
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
    return placed
