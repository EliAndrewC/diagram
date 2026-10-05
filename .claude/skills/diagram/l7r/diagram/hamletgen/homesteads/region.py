"""THE SEAT REGION: where a homestead can stand and a door can reach the access tree, computed once per change to what stands,
and the seats every round offers drawn only from it (feature 297, FR-001, plan B1).

The GM, 2026-09-30: *">1s is a lot to place 15 farmhouses ... hard to believe that's actually necessary"*. Inashiro's seating
offered 734 seats for 15 houses, and 464 of them were refused by ground occupancy alone - the house's box and every garden
side's envelope - each after the placer had built the homestead's four layouts (research R6). The region asks that question
of the whole candidate list at once, from two rasters kept current as houses are seated:

- **buildable** - FreeGround's surely-taken ground, the access tree's corridors at their half-width and the reserved wood-floor
  seats, painted into one `Region` over the seat band's window. The seated homesteads are NOT painted: measured painted, every
  household still seated but the stage ran 9% slower (repainting and re-tabling the raster per house costs more than the placer
  calls it saves - specs/297 research R15), and the placer's own box test refuses a seat on a neighbor;
- **reachable** - LANE GROUND connected to the way out (feature 318, FR-012): FreeGround's surely-taken ground grown by a cell
  (about a corridor's half-width, so a pocket against the paddy or the water narrower than a lane is closed) and the reserved
  wood-floor seats, flooded from the exit strip and the field's corridor. The seated homesteads are not painted here either:
  the growth parts every two by a lane's threading gap (`growth.grow_gap`), which this grid's cell cannot resolve, so the gap
  is what guarantees a lane's room between them and this raster answers where the field, the water and the map's edge close
  ground off. A yard that opens onto it is a household with a way of its own (`SeatRegion.opens`): the seat's one cheap check,
  in place of a path search while houses are seated (FR-012, FR-013); the ways are laid once every house stands
  (`settlement/rolling/gap_ways.py`), and a pocket this raster misses is reached there by a neighbor's yard.

A seat is OFFERED only where at least one garden side's envelope - the side's box at the smallest house the size ladder
rolls, from a layout with no household's parts, unturned - is clear in the buildable raster, and its yard's box touches the
reachable raster. The placer still decides every seat it is offered, by all of its rules; the region only stops it being
offered what free ground already rules out. Painting is conservative (`Region`), so a seat the region offers may still be
refused, and one it does not offer is one whose smallest homestead would stand on painted ground - the map moves where the
margin bites (the GM, 2026-09-30: maps "do NOT need to remain identical in output"; the spec's Decisions).

Research: seat region - NONE: rasters that prune the seats offered, kept current as houses stand
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.settlement._geom.region import GROW, Region
from l7r.diagram.settlement.rolling.lot import DEPTH_FACTORS, LENGTH_FACTORS

from ..consts import Pt

if TYPE_CHECKING:
    from l7r.diagram.settlement import Settlement

#: The seat region's cell, FreeGround's own (`boundary.FreeGround`): its taken cells paint whole.
SEAT_REGION_CELL = 8.0


class SeatRegion:
    """The buildable and reachable rasters over one seat band (see the module docstring)."""

    def __init__(self, s: Settlement, window: tuple[float, float, float, float], cell: float = SEAT_REGION_CELL) -> None:
        """The two rasters over `window` (the module's account).

        Research:
            no way of its own across a water course within its clearance - UNRESEARCHED: the courses painted onto lane ground at the corridor test's own clearance
            a way of its own decided on lane ground - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a dooryard that opens onto the ground the lanes are laid in, connected to the track out
        """
        self.s, self.window, self.cell = s, window, cell
        fg = getattr(s, "_free_ground", None)
        if fg is not None:  # ON FREEGROUND'S OWN GRID, so each of its surely-taken cells is one cell here, painted exactly
            cell = float(fg.cell)
            x0, y0 = fg.x0 + math.floor((window[0] - fg.x0) / cell) * cell, fg.y0 + math.floor((window[1] - fg.y0) / cell) * cell
            window = (x0, y0, window[2], window[3])
            self.window, self.cell = window, cell
        self.buildable = Region(window, cell)
        self.lane = Region(window, cell)  # the lane ground (the module's account): no corridor painted, the site grown at the flood
        if fg is not None:
            self.buildable.cells(fg.taken, fg.cell, fg.x0, fg.y0)
            self.lane.cells(fg.taken, fg.cell, fg.x0, fg.y0)
        # ...AND THE WATER COURSES AT THEIR CLEARANCE, as the corridor's own ground test holds them (`access.site_samples_clear`:
        # no way runs within a course's clearance), so a cluster is never grown across a brook no way can then cross (cohort
        # seed 13: four households seated beyond one, reached by none - the courses lie in FreeGround's uncertain cells, which
        # the raster counts free). Painted short of the clearance by the raster's own over-paint (`Region.line`: `GROW` cells)
        corr = getattr(s, "_site_corridors", None)
        for a, b, clr in getattr(corr, "water", None) or ():
            self.lane.line([a, b], max(0.0, float(clr) - GROW * cell))
        self._tree_n = self._placed_n = self._houses_n = 0
        self._reach: Any = None
        self.sides, self.yard = smallest_sides(s)
        self.sync()

    def sync(self) -> None:
        """Paint what has come to stand since the last call - the tree's new corridors, newly seated homesteads and the wood
        seats their households reserved - and drop the reachable raster, recomputed on its next read.

        Research: reserved wood seats bar lane ground - UNRESEARCHED: a household's reserved wood seats are no ground its way runs on
        """
        s = self.s
        tree = getattr(s, "_access", None)
        nseg, nhouse = (len(tree.segs) if tree is not None else 0), len(s.M.get("houses") or ())
        if (nseg, nhouse) == (self._tree_n, self._houses_n):
            return  # nothing has come to stand since the last call
        segs = list(tree.segs) if tree is not None else []
        half = float(tree.half) if tree is not None else 0.0
        for a, b in segs[self._tree_n :]:
            self.buildable.line([a, b], half)
        # THE SEATED HOMESTEADS ARE NOT PAINTED: the placer's one computed move shifts a seat off the single neighbor it overlaps
        # (`_place_bundle_nucleated`), so a seat lapping one neighbor is still a seat; the placer's own box test refuses the rest
        placed = list(getattr(s, "placed", None) or [])
        houses = list(s.M.get("houses") or [])
        for h in houses[self._houses_n :]:
            for p in (h.get("wood_share") or {}).get("seats") or ():
                self.buildable.circle(float(p[0]), float(p[1]), 1.0)
                self.lane.circle(float(p[0]), float(p[1]), 1.0)
        if (len(segs), len(placed), len(houses)) != (self._tree_n, self._placed_n, self._houses_n):
            self._reach = None
        self._tree_n, self._placed_n, self._houses_n = len(segs), len(placed), len(houses)

    def _reached(self) -> tuple[Any, Any]:
        """The reachable cells and their summed-area table, built together once per change to what stands.

        Research: a way of its own decided on lane ground - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: reached ground flooded from the open ground on the track out's side
        """
        if self._reach is None:
            import numpy as np

            tree = getattr(self.s, "_access", None)
            # ...FROM THE WAY OUT'S SIDE (feature 320 D1): the tree has no legs while houses are seated, so the open ground past
            # the seat band on the bearing out (`_way_out_anchor`) is where reachable ground starts - a seed, nothing reserved
            anchor = getattr(self.s, "_way_out_anchor", None)
            seed = anchor_in_window(anchor, self.window, self.cell) if anchor is not None else None
            segs = list(tree.segs) if tree is not None and tree.segs else ([seed] if seed is not None else [])
            # ...AND NOT FROM THE WINDOW'S EDGE (feature 318): seeded there, ground that might reach the tree round the outside of
            # the window was counted reached - an over-count the seat's corridor search once settled. With no search while houses
            # are seated, it admitted a group of households beyond a brook that no way then reached (cohort seed 13: four of
            # thirteen reached across a neighbor's yard; without the edge, none - research R5)
            reach = flood_from(LaneGround(self.lane), segs, float(tree.half) if tree is not None else 0.0)
            sat = np.zeros((reach.shape[0] + 1, reach.shape[1] + 1), dtype=np.int32)
            sat[1:, 1:] = reach.astype(np.int32).cumsum(0).cumsum(1)
            self._reach = (reach, sat)
        return self._reach

    def opens(self, geom: Any) -> bool:
        """Does the homestead laid as `geom` open onto lane ground connected to the way out - its yard (its house where it has
        none), grown by the corridor's half-width and a cell, touching a reachable cell? THE ONE PREDICATE of a way of its
        own while houses are seated (feature 318, FR-012, FR-013): an ordinary seat is admitted only where it holds
        (`fit._parts_fit`, `place._place_bundle_nucleated`), a tight seat only where it does not (`passage.landlocked`). A yard
        past the window's edge is counted open (the window bounds the rasters' cost, never an answer).

        Research: a way of its own - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a household whose yard opens onto the ground the lanes are laid in, connected to the way out; one with none is the custom's land reached across a neighbor's
        """
        self.sync()
        boxes = geom.get("boxes") or {}
        box = boxes.get("yard") or geom.get("yard") or boxes.get("house") or geom["house"]
        tree = getattr(self.s, "_access", None)
        g = (float(tree.half) if tree is not None else 0.0) + self.cell
        x0, y0, x1, y1 = box[0] - box[2] / 2 - g, box[1] - box[3] / 2 - g, box[0] + box[2] / 2 + g, box[1] + box[3] / 2 + g
        w = self.window
        if x0 < w[0] or y0 < w[1] or x1 > w[2] or y1 > w[3]:
            return True
        return bool(touches_many(self._reached()[1], self.buildable, [x0], [y0], [x1], [y1])[0])

    def offer(self, pts: Sequence[Pt]) -> list[bool]:
        """For each candidate seat (a house center), whether it is offered: a side's envelope clear, and - where an access tree is
        installed - its yard's box touching the reachable ground. A seat outside the region's window is offered unjudged (feature
        318: the window bounds the rasters' cost, never where a house may stand; the placer's own tests decide).

        Research: a way of its own - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a seat is offered only where its yard opens onto the ground the lanes are laid in, connected to the track out
        """
        import numpy as np

        self.sync()
        if not pts:
            return []
        xs = np.asarray([float(p[0]) for p in pts])
        ys = np.asarray([float(p[1]) for p in pts])
        ok = np.zeros(len(pts), dtype=bool)
        m = self.cell  # each box shrunk by a cell: the placer judges the static ground at a box's nine points, not its every cell
        for x0, y0, x1, y1 in self.sides:
            ok |= self.buildable.box_clear_many(xs + x0 + m, ys + y0 + m, xs + x1 - m, ys + y1 - m)
        if self.yard is not None and getattr(self.s, "_access", None) is not None:
            y0_, y1_ = self.yard[1], self.yard[3]
            ok &= touches_many(self._reached()[1], self.buildable, xs + self.yard[0], ys + y0_, xs + self.yard[2], ys + y1_)
        # ...where every box it asks lies inside the window; one that crosses its edge is judged by no raster cell of its own
        x0w, y0w, x1w, y1w = self.window[0], self.window[1], self.window[2], self.window[3]
        boxes = [*self.sides, *([self.yard] if self.yard is not None else [])]
        bx0, by0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
        bx1, by1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
        ok |= (xs + bx0 < x0w) | (xs + bx1 > x1w) | (ys + by0 < y0w) | (ys + by1 > y1w)
        return [bool(v) for v in ok]


class LaneGround:
    """The lane raster (`SeatRegion.lane`) as the flood reads it (`flood_from`): its taken cells grown by one cell on every side -
    about a corridor's half-width at the free-ground grid's cell - so ground a lane cannot pass at its width is not free.

    Research: lane ground - NONE: the lane raster grown one cell for the flood to read; the clearance itself is painted in `SeatRegion.__init__` (its own claim)
    """

    def __init__(self, region: Region) -> None:
        self.x0, self.y0, self.nx, self.ny, self.cell = region.x0, region.y0, region.nx, region.ny, region.cell
        self._region = region

    def array(self) -> Any:
        """The taken cells grown by one cell (8-neighbor), rows = y: 1 where taken."""
        import numpy as np

        a = self._region.array() > 0
        out = a.copy()
        out[1:, :] |= a[:-1, :]
        out[:-1, :] |= a[1:, :]
        out[:, 1:] |= a[:, :-1]
        out[:, :-1] |= a[:, 1:]
        out[1:, 1:] |= a[:-1, :-1]
        out[:-1, :-1] |= a[1:, 1:]
        out[1:, :-1] |= a[:-1, 1:]
        out[:-1, 1:] |= a[1:, :-1]
        return out.astype(np.uint8)


def smallest_sides(s: Settlement) -> tuple[list[tuple[float, float, float, float]], tuple[float, float, float, float] | None]:
    """Each garden side's envelope at the smallest house the size ladder rolls, from a layout carrying no household's parts,
    unturned, relative to the house's center, as (x0, y0, x1, y1) - and the yard's box the same way (None for a bundle with no
    yard)."""
    hw, hh = s.px(46) * LENGTH_FACTORS[0], s.px(28) * DEPTH_FACTORS[0]
    saved = {k: s.__dict__.pop(k) for k in ("_household_seat", "_household_byre", "_household_well", "_household_fixtures") if k in s.__dict__}
    try:
        sides: list[tuple[float, float, float, float]] = []
        yard: tuple[float, float, float, float] | None = None
        for side in s._NUC_SIDES:
            g = s._bundle_geom(0.0, 0.0, hw, hh, side, False, rot=0.0)
            x, y, w, h = g["bbox"]
            sides.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
            yb = (g.get("boxes") or {}).get("yard")
            if yard is None and yb is not None:
                yard = (yb[0] - yb[2] / 2, yb[1] - yb[3] / 2, yb[0] + yb[2] / 2, yb[1] + yb[3] / 2)
        return sides, yard
    finally:
        s.__dict__.update(saved)


def _clip(a: Pt, b: Pt, box: tuple[float, float, float, float]) -> tuple[float, float] | None:
    """The span (t0, t1) of the segment a-b, as fractions of it, inside `box` (Liang-Barsky); None where it misses."""
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    for p, q in ((-dx, a[0] - box[0]), (dx, box[2] - a[0]), (-dy, a[1] - box[1]), (dy, box[3] - a[1])):
        if p == 0.0:
            if q < 0.0:
                return None
            continue
        r = q / p
        if p < 0.0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
    return (t0, t1) if t0 <= t1 else None


def anchor_in_window(anchor: Any, window: tuple[float, float, float, float], cell: float) -> tuple[Pt, Pt] | None:
    """The seating's reach seed (`_way_out_anchor`: the seat's center, the band's bound and the far end, on the bearing out)
    as it lies in the region's `window`, inset a cell: the stretch past the band's bound where it is inside; where none of it
    is (a seat by the canvas's edge, the window clipped there), the last two cells of the bearing out inside the window -
    the open ground on the way out's side at its edge (feature 320: an anchor wholly off the canvas seeded nothing, and no
    seat counted open). None where the bearing out never enters the window.

    Research: a way of its own decided on lane ground - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a dooryard that opens onto the ground the lanes are laid in, on the way out's side"""
    c, near, far = ((float(q[0]), float(q[1])) for q in anchor)
    box = (window[0] + cell, window[1] + cell, window[2] - cell, window[3] - cell)
    span = _clip(near, far, box)
    if span is not None and span[1] > span[0]:
        return (near[0] + (far[0] - near[0]) * span[0], near[1] + (far[1] - near[1]) * span[0]), (near[0] + (far[0] - near[0]) * span[1], near[1] + (far[1] - near[1]) * span[1])
    span = _clip(c, far, box)
    if span is None or span[1] <= span[0]:
        return None
    d = math.dist(c, far) or 1.0
    t1 = span[1]
    t0 = max(span[0], t1 - 2.0 * cell / d)
    return (c[0] + (far[0] - c[0]) * t0, c[1] + (far[1] - c[1]) * t0), (c[0] + (far[0] - c[0]) * t1, c[1] + (far[1] - c[1]) * t1)


def flood_from(region: Region | LaneGround, segs: Sequence[tuple[Pt, Pt]], half: float) -> Any:
    """The free cells of `region` connected to the segments `segs` (painted into it at half-width `half`): the free cells'
    4-connected components (`free_components`) that meet the ring of cells just beyond each segment's painted strip. A boolean
    array, rows = y."""
    import numpy as np

    from l7r.diagram.settlement._geom.region import GROW

    free = region.array() == 0
    if not segs or not free.any():
        return np.zeros(free.shape, dtype=bool)
    labels = free_components(free)
    seeds = Region((region.x0, region.y0, region.x0 + region.nx * region.cell, region.y0 + region.ny * region.cell), region.cell)
    for a, b in segs:  # the strip grown by a cell more than it was painted: its first unpainted cells on either side
        seeds.line([a, b], half + region.cell)
    seed = np.zeros(free.shape, dtype=bool)  # the seeds' raster can round to one more row or column than the region's
    sa = seeds.array() > 0
    h, w = min(seed.shape[0], sa.shape[0]), min(seed.shape[1], sa.shape[1])
    seed[:h, :w] = sa[:h, :w]
    hit = np.unique(labels[seed & free])
    hit = hit[hit > 0]
    _ = GROW
    return np.isin(labels, hit)


def free_components(free: Any) -> Any:
    """Label the 4-connected components of the True cells of `free` (rows = y): an int array, 0 off the free cells. Run-length
    union-find: each row's runs of free cells are unioned with the runs of the row above that they overlap - a few thousand runs
    on a seat band, where a cell-by-cell flood was most of the seating's time (PIL's fill is Python)."""
    import numpy as np

    ny, nx = free.shape
    starts: list[Any] = []
    ends: list[Any] = []
    for j in range(ny):
        row = np.concatenate(([False], free[j], [False])).astype(np.int8)
        d = np.diff(row)
        starts.append(np.flatnonzero(d == 1))
        ends.append(np.flatnonzero(d == -1))
    parent: list[int] = []
    run_of: list[list[int]] = []

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for j in range(ny):
        ids = []
        for s0, e0 in zip(starts[j].tolist(), ends[j].tolist(), strict=True):
            k = len(parent)
            parent.append(k)
            ids.append(k)
            if j > 0:
                for m, (s1, e1) in enumerate(zip(starts[j - 1].tolist(), ends[j - 1].tolist(), strict=True)):
                    if s1 < e0 and s0 < e1:  # the runs share a column: 4-connected
                        ra, rb = find(k), find(run_of[j - 1][m])
                        if ra != rb:
                            parent[ra] = rb
        run_of.append(ids)
    labels = np.zeros((ny, nx), dtype=np.int64)
    for j in range(ny):
        for (s0, e0), k in zip(zip(starts[j].tolist(), ends[j].tolist(), strict=True), run_of[j], strict=True):
            labels[j, s0:e0] = find(k) + 1
    return labels


def touches_many(sat: Any, region: Region, x0s: Any, y0s: Any, x1s: Any, y1s: Any) -> Any:
    """Does each box touch a reachable cell? `sat` is the reachable cells' summed-area table (`SeatRegion._reached`)."""
    import numpy as np

    i0 = np.clip(np.floor((np.asarray(x0s) - region.x0) / region.cell).astype(np.int64), 0, region.nx)
    j0 = np.clip(np.floor((np.asarray(y0s) - region.y0) / region.cell).astype(np.int64), 0, region.ny)
    i1 = np.clip(np.floor((np.asarray(x1s) - region.x0) / region.cell).astype(np.int64) + 1, 0, region.nx)
    j1 = np.clip(np.floor((np.asarray(y1s) - region.y0) / region.cell).astype(np.int64) + 1, 0, region.ny)
    return (sat[j1, i1] - sat[j0, i1] - sat[j1, i0] + sat[j0, i0]) > 0
