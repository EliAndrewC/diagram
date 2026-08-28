"""The fabric index: clearance tests that measure only what is near (feature 138, GM 2026-08-28).

WHY. A profile of the seed-19 polder (110 s) put 57 s in `stage_web` and 22 s in `stage_track`, and
the GM asked the right question: *"are you doing some kind of NP complete problem?"*. No - the lane
router's clearance test (`ways.clear_runs`) was called once PER LATTICE CELL by `_route` (165,611
calls on that polder), each call re-deriving every polygon's bounding box from its vertices and then
measuring the sample against every segment of every polygon that survived: 36 million `seg_dist`
calls, 106 million `max`. Polynomial, with a brute-force constant. The connector's crossing check
compared every pair of water crossings (170 million `hypot`). This module is the index that scan
should have had.

WHAT IT GUARANTEES - byte identity. A verdict here is the SAME boolean the scan computed: a sample
is fouled when it lies inside a polygon or within the polygon's margin of one of its edges, or
within the line margin of a line. The index only decides WHICH entries are measured: each entry is
filed in every grid cell its margin-inflated bounds touch, so the entries a sample's cell holds are a
SUPERSET of the entries whose inflated bounds contain the sample - which is the set the old
per-call bounding-box prefilter measured. Measuring a superset with the same predicate cannot change
the answer; the early exit (`any` instead of `min(...) < m`) cannot either. Feature 138's
byte-identity sweep over every gate roll and every live pool map is the proof, and
`tests/hamletgen/test_clearance.py` pins the superset property on random fabric.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import point_in_poly, seg_dist

Pt = tuple[float, float]
Poly = list[Pt]
Line = tuple[Pt, Pt]


def bounds(poly: Sequence[Pt]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


# A BUILT INDEX IS REUSED WHILE ITS INPUTS ARE THE SAME OBJECTS (feature 138, second round of the profile):
# `_clear_link` and `_clear_touch` build one index per call, and the straggler and smoothing passes call
# them thousands of times with the SAME `hard` / `walls` / `water` lists - 4,969 builds, 26 s profiled, on
# the polder once the per-cell scan was gone. The key is every polygon's identity, length and end points
# plus the margins; a list rebuilt, extended, or a polygon replaced misses and rebuilds. A polygon mutated
# IN PLACE at an interior vertex with the same end points would be served stale - nothing in the engine
# does that (polygons are built, then read), and the byte-identity sweep over every roll is the check.
_MEMO: dict[tuple[object, ...], FabricIndex] = {}
_MEMO_MAX = 64
# AN ENTRY THAT WOULD SPAN MORE THAN THIS MANY CELLS IS NOT FILED IN THE GRID - the field envelope, a crop
# polygon, the marsh: each spans thousands of cells, so filing them cost 25 million dict inserts per polder.
# They go to `big` and are tested by bounds on every lookup, which is what the old prefilter did anyway.
_BIG_CELLS = 256


def _key(obstacles: Sequence[Sequence[Pt]], margin: float, tight: Sequence[Sequence[Pt]], tight_margin: float, lines: Sequence[Line], line_margin: float, cell: float | None) -> tuple[object, ...]:
    def polys(group: Sequence[Sequence[Pt]]) -> tuple[object, ...]:
        return tuple((id(o), len(o), o[0], o[-1]) if o else (0, 0, None, None) for o in group)

    return (polys(obstacles), margin, polys(tight), tight_margin, tuple((a, b) for a, b in lines), line_margin, cell)


def fabric_index(
    obstacles: Sequence[Sequence[Pt]], margin: float, tight: Sequence[Sequence[Pt]] = (), tight_margin: float = 0.0, lines: Sequence[Line] = (), line_margin: float = 0.0, cell: float | None = None
) -> FabricIndex:
    """`FabricIndex(...)`, memoized on the inputs' identity (see `_MEMO`)."""
    k = _key(obstacles, margin, tight, tight_margin, lines, line_margin, cell)
    hit = _MEMO.get(k)
    if hit is not None:
        return hit
    if len(_MEMO) >= _MEMO_MAX:
        _MEMO.pop(next(iter(_MEMO)))
    idx = _MEMO[k] = FabricIndex(obstacles, margin, tight, tight_margin, lines, line_margin, cell)
    return idx


class FabricIndex:
    """Obstacle polygons (each with its margin), tight polygons (theirs), and lines (theirs), filed by
    grid cell. Build once; ask `fouled(q)` many times."""

    __slots__ = ("big", "cell", "grid", "polys", "x0", "y0")

    def __init__(
        self,
        obstacles: Sequence[Sequence[Pt]],
        margin: float,
        tight: Sequence[Sequence[Pt]] = (),
        tight_margin: float = 0.0,
        lines: Sequence[Line] = (),
        line_margin: float = 0.0,
        cell: float | None = None,
    ) -> None:
        # each entry: (kind, points, margin, inflated bounds); kind 0 = polygon, 1 = line
        entries: list[tuple[int, list[Pt], float, tuple[float, float, float, float]]] = []
        for group, m in ((obstacles, margin), (tight, tight_margin)):
            for o in group:
                if not o:
                    continue
                pts = list(o)
                bx0, by0, bx1, by1 = bounds(pts)
                entries.append((0, pts, m, (bx0 - m, by0 - m, bx1 + m, by1 + m)))
        for a, b in lines:
            bx0, by0, bx1, by1 = min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
            entries.append((1, [a, b], line_margin, (bx0 - line_margin, by0 - line_margin, bx1 + line_margin, by1 + line_margin)))
        self.polys = entries
        self.big: list[int] = []
        if not entries:
            self.cell = 1.0
            self.x0 = self.y0 = 0.0
            self.grid: dict[tuple[int, int], list[int]] = {}
            return
        # THE CELL IS SIZED TO THE FABRIC, so a lookup holds a few entries: the median entry's extent,
        # floored at the largest margin. A cell far larger than the entries files each in one cell and
        # holds many; far smaller files each in many cells for no gain.
        extents = sorted(max(b[2] - b[0], b[3] - b[1]) for _k, _p, _m, b in entries)
        self.cell = cell if cell is not None else max(2.0 * max(margin, tight_margin, line_margin), extents[len(extents) // 2], 16.0)
        self.x0 = min(b[0] for _k, _p, _m, b in entries)
        self.y0 = min(b[1] for _k, _p, _m, b in entries)
        self.grid = {}
        c = self.cell
        for idx, (_k, _p, _m, (bx0, by0, bx1, by1)) in enumerate(entries):
            cx0, cx1 = int((bx0 - self.x0) // c), int((bx1 - self.x0) // c)
            cy0, cy1 = int((by0 - self.y0) // c), int((by1 - self.y0) // c)
            if (cx1 - cx0 + 1) * (cy1 - cy0 + 1) > _BIG_CELLS:
                self.big.append(idx)
                continue
            for cx in range(cx0, cx1 + 1):
                for cy in range(cy0, cy1 + 1):
                    self.grid.setdefault((cx, cy), []).append(idx)

    def candidates(self, q: Pt) -> list[int]:
        """Indices of every entry whose inflated bounds may contain `q` (a superset of those that do)."""
        if not self.polys:
            return []
        near = self.grid.get((int((q[0] - self.x0) // self.cell), int((q[1] - self.y0) // self.cell)))
        return self.big if near is None else (self.big + near if self.big else near)

    def fouled(self, q: Pt) -> bool:
        """Is `q` inside a polygon, within a polygon's margin of its edge, or within a line's margin?"""
        x, y = q
        for idx in self.candidates(q):
            kind, pts, m, (bx0, by0, bx1, by1) = self.polys[idx]
            if x < bx0 or x > bx1 or y < by0 or y > by1:
                continue
            if kind == 1:
                if seg_dist(x, y, pts[0], pts[1]) < m:
                    return True
                continue
            if point_in_poly(x, y, pts):
                return True
            n = len(pts)
            for j in range(n):
                if seg_dist(x, y, pts[j], pts[(j + 1) % n]) < m:
                    return True
        return False


def fouled_brute(q: Pt, obstacles: Sequence[Sequence[Pt]], margin: float, tight: Sequence[Sequence[Pt]] = (), tight_margin: float = 0.0, lines: Sequence[Line] = (), line_margin: float = 0.0) -> bool:
    """The scan the index replaces, kept as the ORACLE for the tests: every polygon, every edge."""
    if any(seg_dist(q[0], q[1], a, b) < line_margin for a, b in lines):
        return True

    def near(o: Sequence[Pt], m: float) -> bool:
        return point_in_poly(q[0], q[1], list(o)) or min(seg_dist(q[0], q[1], o[j], o[(j + 1) % len(o)]) for j in range(len(o))) < m

    return any(near(o, margin) for o in obstacles if o) or any(near(o, tight_margin) for o in tight if o)


def pairs_within(points: Sequence[Pt], reach: float) -> int:
    """How many unordered pairs of `points` lie within `reach` of each other - by a sweep, not by
    comparing every pair. Sorted by x, a pair with |dx| >= reach cannot be within reach, so each point
    compares only with the later points until the x-gap reaches `reach`: the same pairs the pairwise
    form counts (`ways.path_violations`, 170 million `hypot` on a polder before this), no other."""
    # BUCKETED, not an x-sweep: a polder's ditches run parallel, so its crossings share an x and a sweep on
    # x degenerates to the pairwise form (13 s profiled on the first cut). Cells of side `reach`: a pair
    # within `reach` is in the same or an adjacent cell, so each point compares with its own cell's later
    # points and with the four "forward" neighbor cells - every pair once, no pair twice.
    if reach <= 0.0 or len(points) < 2:
        return 0
    cells: dict[tuple[int, int], list[Pt]] = {}
    for p in points:
        cells.setdefault((int(p[0] // reach), int(p[1] // reach)), []).append(p)
    count = 0
    for (cx, cy), mine in cells.items():
        for i, u in enumerate(mine):
            for v in mine[i + 1 :]:
                if math.hypot(u[0] - v[0], u[1] - v[1]) < reach:
                    count += 1
        for dx, dy in ((1, -1), (1, 0), (1, 1), (0, 1)):
            for v in cells.get((cx + dx, cy + dy), ()):
                for u in mine:
                    if math.hypot(u[0] - v[0], u[1] - v[1]) < reach:
                        count += 1
    return count
