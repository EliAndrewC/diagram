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
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.work_counts import OPS

from .._geom import Pt

if TYPE_CHECKING:
    from ..core import Settlement

#: The grid a route is searched on, in px: MEASURED on the reference at 40 households (research R5) - 10 px took 59.6 s on seed 25
#: (26 margins), 12 px 7.2 s (6 margins); finer than a corridor's width (2 x `ACCESS_HALF_FT`), so a gap a corridor fits holds a
#: grid line. A search breadth, never a rule: every leg is judged exactly (`leg_ok`).
#: How far from its door a route is sought, in px: a guess, the reach of a neighborhood (about three homesteads); a door with
#: no tree within it has no routed path, and the seat is refused as before.
#: The search's weight on its aim (weighted A*): 1.5 finds a near-shortest route in a fraction of the plain search's grid
#: points; the route is pulled taut after, so its length beyond the shortest costs nothing drawn.
#: The most legs a routed path takes: a guess - a path round two or three homesteads; the web's bend law judges each joint.

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
                if __debug__:
                    OPS["candidate@search"] += 1
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


def own_parts(s: Settlement, geom: Any, own: Any, hgap: float, half: float) -> list[tuple[Any, float]]:
    """What a household's own parts keep a WALK off of (`passage.walk_of`, feature 317), each with the gap its leg test keeps:
    the house (`house_clear`'s gap), the shed, byre, well and garden beds (`parts_clear`'s), the fixtures by a corridor's
    half-width (`fixtures_clear`'s). The corridor's own route keeps off the house alone (`routed_corridors`: searched per
    layout round these parts, it was withdrawn - research R8).

    Research: a walk crosses nothing of either household - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no house, garden bed, shed or fixture, each kept at its leg test's gap; the persimmon left out of the grid's walls, its trunk held off by every leg's own test (`passage.walk_clear`, `fixtures_clear`)
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
