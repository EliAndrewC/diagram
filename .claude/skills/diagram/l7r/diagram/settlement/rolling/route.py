"""A house's path ROUTED round what stands, where no straight one clears (feature 308, plan D3; FR-005).

The GM, 2026-10-02: *"once you've placed the first house, you should notionally be able to compute the minimum distance needed to
seat a second house, then place it in a direction, then repeat"* - and the path out is part of what a homestead holds. A grown
house stands behind another, and its dooryard has no straight run to the access tree: the house in front and its woodlot stand
across every run (specs/308-grow-the-cluster/research.md R1). So the path is laid as the house is placed, back to the tree,
round what stands:

- SEARCHED on a grid of the open ground (`ROUTE_STEP_PX`) within `ROUTE_REACH_PX` of the door: weighted A* (`ROUTE_WEIGHT`)
  aimed at the tree's nearest points. A grid point is open off the site's taken ground (`FreeGround`), off every placed
  homestead box by the corridor's half-width, off the reserved wood seats and off the household's own house, beds, sheds and
  fixtures (`own_parts`; the placed index, the site raster and the wood grid, each asked per point - never a registry walk).
  So it is searched for each LAYOUT of a seat (its garden side, its fixtures), not once for the seat's house and yard.
- PULLED TAUT through the engine's OWN leg tests (`leg_ok`): each leg runs to the farthest grid point the house, its fixtures,
  its beds, the standing ground and the ways' ground test admit - the tests a straight corridor passes - and none turns back on
  itself (`doubles_back`). At most `ROUTE_LEGS` legs.
- ADMITTED as any corridor is (`access_corridor`: its fixtures, the lane law over the whole tree), and recorded leg by leg.

A MAP DRAWING CONVENTION (spec Decisions; plan D3): the routing is how a seat's path is FOUND; the web draws it under the
unchanged lane law. The paths it draws bend between the homesteads, as the record's accretion form of village lanes has them -
each household cutting its own way (research/contents.json#ways). Only a tree that asks for it routes (`AccessTree.routed`,
the nucleated seating's): the other forms keep their straight corridors (spec, the round-1 rulings).

Research: grid search plumbing - NONE
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Callable, Iterator, Sequence
from typing import TYPE_CHECKING, Any

from .._geom import Pt, seg_closest, seg_dist

if TYPE_CHECKING:
    from ..core import Settlement
    from .access import AccessTree

#: The grid a route is searched on, in px: MEASURED on the reference at 40 households (research R5) - 10 px took 59.6 s on seed 25
#: (26 margins), 12 px 7.2 s (6 margins); finer than a corridor's width (2 x `ACCESS_HALF_FT`), so a gap a corridor fits holds a
#: grid line. A search breadth, never a rule: every leg is judged exactly (`leg_ok`).
ROUTE_STEP_PX = 12.0
#: How far from its door a route is sought, in px: a guess, the reach of a neighborhood (about three homesteads); a door with
#: no tree within it has no routed path, and the seat is refused as before.
ROUTE_REACH_PX = 320.0
"""Research: how far a routed path is sought - GUESS: 320 px from the door, about three homesteads; a door with no tree within it is refused"""
#: The search's weight on its aim (weighted A*): 1.5 finds a near-shortest route in a fraction of the plain search's grid
#: points; the route is pulled taut after, so its length beyond the shortest costs nothing drawn.
ROUTE_WEIGHT = 1.5
#: The most legs a routed path takes: a guess - a path round two or three homesteads; the web's bend law judges each joint.
ROUTE_LEGS = 5
"""Research: most legs of a routed path - GUESS: 5, a path round two or three homesteads"""

Cell = tuple[int, int]


def search(
    is_open: Callable[[Cell], bool],
    goal_of: Callable[[Cell], Pt | None],
    aims: Sequence[tuple[float, float]],
    n: int,
    weight: float,
    start: Cell = (0, 0),
    first_ok: Callable[[Cell], bool] | None = None,
) -> tuple[list[Cell], Pt] | None:
    """Weighted A* from cell `start` over the cells within `n` of it on each axis, eight neighbors: the first cell `goal_of`
    answers (other than the start), as the path of cells from the start and the goal's point; None where none is reached.
    `aims` are the goal's likely cells (the heuristic's targets, in cell units). A cell's heuristic is computed once
    (feature 314: it was asked again at every push and pop, a third of the search). `first_ok` judges each step off the
    start (a step there may span two cells)."""
    aims = list(aims) or [(float(start[0]), float(start[1]))]
    hypot = math.hypot
    hs: dict[Cell, float] = {}

    def h(c: Cell) -> float:
        v = hs.get(c)
        if v is None:
            v = hs[c] = weight * min([hypot(c[0] - a[0], c[1] - a[1]) for a in aims])
        return v

    si, sj = start
    dist: dict[Cell, float] = {start: 0.0}
    prev: dict[Cell, Cell] = {}
    opened: dict[Cell, bool] = {}
    heap = [(h(start), start)]
    while heap:
        f, c = heapq.heappop(heap)
        if f > dist[c] + h(c) + 1e-9:
            continue
        if c != start:
            q = goal_of(c)
            if q is not None:
                cells = [c]
                while cells[-1] != start:
                    cells.append(prev[cells[-1]])
                return cells[::-1], q
        # ...THE FIRST STEP REACHES TWO CELLS (feature 314): the start is the door on a grid that is the map's, and the grid points
        # beside its nearest one can all stand within the house's own clearance - the search then never left the door
        reach = (-2, -1, 0, 1, 2) if c == start else (-1, 0, 1)
        for di in reach:
            for dj in reach:
                nc = (c[0] + di, c[1] + dj)
                if nc == c or abs(nc[0] - si) > n or abs(nc[1] - sj) > n:
                    continue
                if nc not in opened:
                    opened[nc] = is_open(nc)
                if not opened[nc] or (c == start and first_ok is not None and not first_ok(nc)):
                    continue
                nd = dist[c] + math.hypot(di, dj)
                if nd < dist.get(nc, math.inf):
                    dist[nc] = nd
                    prev[nc] = c
                    heapq.heappush(heap, (nd + h(nc), nc))
    return None


def taut(pts: Sequence[Pt], leg_ok: Callable[[Pt, Pt], bool], turns_back: Callable[[Pt, Pt, Pt], bool], most: int) -> tuple[Pt, ...] | None:
    """The polyline through `pts` pulled taut: from each point, the farthest later point a leg to it is admitted (`leg_ok`)
    without turning back on the leg before (`turns_back`). None where a point admits no leg onward or more than `most` legs
    are needed.

    Research: path pulled taut - research/questions/0081-village-lanes.drawing.html: straight from point to point where it can, never doubling back
    """
    out = [pts[0]]
    k = 0
    while k < len(pts) - 1:
        if len(out) > most:
            return None
        far = next((m for m in range(len(pts) - 1, k, -1) if leg_ok(pts[k], pts[m]) and (len(out) < 2 or not turns_back(out[-2], out[-1], pts[m]))), None)
        if far is None:
            return None
        out.append(pts[far])
        k = far
    return tuple(out) if len(out) - 1 <= most else None


def routed_corridors(s: Settlement, tree: AccessTree, geom: Any) -> Iterator[tuple[Pt, ...]]:
    """The routed paths from the homestead's two dooryard doors (`doors_of`: the forecourt, the yard's far edge), each searched
    once while nothing standing changes (`_standing_memo`).

    Research: path routed round what stands - research/questions/0081-village-lanes.html, research/questions/0081-village-lanes.drawing.html: a house no straight path reaches gets one bending between the homesteads, from its dooryard
    """
    from . import access as A

    half = float(tree.half)
    hgap = A.house_gap(s)
    memo = A._standing_memo(s)[1]
    fg = getattr(s, "_free_ground", None)
    wood = getattr(s, "_wood", None)
    own = (geom.get("boxes") or {}).get("house") or geom["house"]
    placed = s._reach_index(s.placed, "placed_reach")
    step = ROUTE_STEP_PX

    def leg_ok(a: Pt, b: Pt) -> bool:
        return A.house_clear(a, b, geom, hgap) and A.fixtures_clear(s, a, b, geom) and A.parts_clear(s, a, b, geom) and A.standing_ground(s, a, b, memo) and A.lawful_leg(s, a, b, memo)

    # ...OFF THE HOUSE'S OWN BOX ONLY, and once for the seat's house and yard - its layouts share it, each taking it only where
    # its own beds and fixtures leave it clear (the taut pull's and `access_corridor`'s leg tests). A FIX THAT FAILED (feature
    # 317, task T06, research R8): searched for each garden layout round its own beds and fixtures (`own_parts`), it seated more
    # households with a path before feature 315 merged (seats lost to the path alone 77 -> 21 at 15 households), and after it cost
    # the homesteads stage 3-43% more than this search on the bookend's seeds (calls, passage off), the layouts no longer seated
    # better and each searched again. Withdrawn: do not retry it without measuring it against main's layouts first.
    mine = [(own, hgap)]
    for door in A.doors_of(geom, half)[:2]:
        key = ("routed", door, tuple(own), tuple((geom.get("boxes") or {}).get("yard") or ()))
        if key not in memo:
            memo[key] = _route_from(s, tree, door, mine, (geom.get("boxes") or {}).get("yard"), half, hgap, fg, wood, placed, step, leg_ok, geom)
        if memo[key] is not None:
            yield memo[key]


def own_parts(s: Settlement, geom: Any, own: Any, hgap: float, half: float) -> list[tuple[Any, float]]:
    """What a household's own parts keep a WALK off of (`passage.walk_of`, feature 317), each with the gap its leg test keeps:
    the house (`house_clear`'s gap), the shed, byre, well and garden beds (`parts_clear`'s), the fixtures by a corridor's
    half-width (`fixtures_clear`'s). The corridor's own route keeps off the house alone (`routed_corridors`: searched per
    layout round these parts, it was withdrawn - research R8).

    Research: a walk crosses nothing of either household - research/questions/0081-village-lanes.drawing.html: no house, garden bed, shed or fixture, each kept at its leg test's gap; the persimmon left out of the grid's walls, its trunk held off by every leg's own test (`passage.walk_clear`, `fixtures_clear`)
    """
    from .access import PART_MARGIN_FT, TREAD_HALF_FT

    boxes = geom.get("boxes") or {}
    pgap = s.px(TREAD_HALF_FT + PART_MARGIN_FT)
    mine: list[tuple[Any, float]] = [(own, hgap)]
    mine += [(b, pgap) for b in [*(boxes.get(k) for k in ("shed", "byre", "well")), *(boxes.get("gardens") or ())] if b is not None]
    # ...BUT NOT THE PERSIMMON (feature 317, research R8): feature 315 holds it in the dooryard, by the door, and its trunk's keep
    # (a corridor's half-width) left the grid no cell between it and the house - seed 39 at 40 households searched 456 routes,
    # 112 of them finding nothing, and tried 1,084 seats where the search without it tried 295. The taut pull still keeps every
    # leg off its trunk (`fixtures_clear`), as it did before the route kept off its own parts.
    mine += [(b, half) for kind, b in sorted((boxes.get("fixtures") or {}).items()) if kind != "persimmon"]
    return mine


def _route_from(
    s: Settlement,
    tree: AccessTree,
    door: Pt,
    mine: Sequence[tuple[Any, float]],
    yard: Any,
    half: float,
    hgap: float,
    fg: Any,
    wood: Any,
    placed: Any,
    step: float,
    leg_ok: Callable[[Pt, Pt], bool],
    geom: Any,
) -> tuple[Pt, ...] | None:
    """One door's routed path (`routed_corridors`), or None.

    Research: path leaves its own yard once - UNRESEARCHED: kept off the house, its parts and the neighbors' homesteads, leaving its threshing yard and never crossing it again
    """
    from .access import PART_MARGIN_FT, TREAD_HALF_FT, doubles_back, leaves_its_yard

    found = _cells_to_tree(s, tree, door, mine, half, hgap, fg, wood, placed, step, geom)
    if found is None:
        return None
    cells, q = found
    pts = [door, *((door[0] + c[0] * step, door[1] + c[1] * step) for c in cells[1:]), q]
    run = taut(pts, leg_ok, doubles_back, ROUTE_LEGS)
    # ...AND IT LEAVES ITS OWN YARD, as every straight and round-the-gable corridor must (`_house_candidates`, feature 287 M8)
    return run if run is not None and leaves_its_yard(run, yard, s.px(TREAD_HALF_FT + PART_MARGIN_FT)) else None


def _cells_to_tree(
    s: Settlement, tree: AccessTree, door: Pt, mine: Sequence[tuple[Any, float]], half: float, hgap: float, fg: Any, wood: Any, placed: Any, step: float, geom: Any
) -> tuple[list[Cell], Pt] | None:
    """The search of one door's route (`search`): the path of grid cells to the tree and the goal's point, or None.

    Research: path kept off what stands - research/questions/0081-village-lanes.drawing.html: nothing built on a lane - off the household's own house and the parts given it, the neighbors' homesteads and the refused ground, on a grid laid from the door
    """
    from . import access as A
    from .access import seg_box_within

    memo = A._standing_memo(s)[1]

    # THE GRID IS THE DOOR'S (feature 314, research R4): laid on the map's own multiples of the step, so that what a point's
    # standing ground answers could be shared between searches, the narrow ways between homesteads held no grid point and seed 6
    # at 40 households threw two margins away (16.4 s against the base's 5.9); laid from the door, it seated on one in 2.2 s.
    # What made the search cheap was not the sharing but the tests below, which refuse a path where it is searched and not
    # after it is found.
    x0, y0 = door

    def at(c: Cell) -> Pt:
        return (x0 + c[0] * step, y0 + c[1] * step)

    # ...OFF THE HOUSEHOLD'S OWN HOUSE AND PARTS (`own_parts`): the first step and the last leg keep their tests (below)
    def is_open(c: Cell) -> bool:
        p = at(c)
        if fg is not None and fg.point_taken(p[0], p[1]):
            return False
        if any(seg_box_within(p, p, b, g) for b, g in mine):
            return False
        if any(seg_box_within(p, p, (it[0], it[1], it[2], it[3]), half) for it in placed.near(p[0], p[1], half)):
            return False
        return not (wood is not None and wood.corridor_bars(p, p))

    def goal_of(c: Cell) -> Pt | None:
        p = at(c)
        got = None
        for a, b, *_ in tree.grid.near(p[0], p[1], step + half):
            if seg_dist(p[0], p[1], a, b) <= step:
                got = seg_closest(p[0], p[1], a, b)
                break
        # ...and the last leg onto the tree standing on ground the standing tests admit (`standing_ground`), as the taut pull
        # will ask it: a goal whose last leg grazed a placed homestead was found and then refused (research R2)
        if got is not None and math.dist(p, got) > 1e-6 and not A.standing_ground(s, p, got, memo):
            got = None
        return got

    aims = [((q[0] - x0) / step, (q[1] - y0) / step) for q in tree.targets(door)]

    # ...ITS FIRST STEP OFF ITS OWN PARTS, by the leg tests that read only the household (`house_clear`, `fixtures_clear`,
    # `parts_clear`) - the refusals a first leg met (research R2); the standing ground's tests, the dearest, are the taut pull's
    def first_ok(c: Cell) -> bool:
        p = at(c)
        return A.house_clear(door, p, geom, hgap) and A.fixtures_clear(s, door, p, geom) and A.parts_clear(s, door, p, geom)

    return search(is_open, goal_of, aims, int(ROUTE_REACH_PX / step), ROUTE_WEIGHT, (0, 0), first_ok)
