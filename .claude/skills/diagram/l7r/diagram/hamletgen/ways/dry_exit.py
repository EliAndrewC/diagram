"""The dry exit: a track out of the frame over ground it may stand on, found by a flood fill (feature 287, ways W23-W25).

WHY IT EXISTS. `connector_track` sweeps forty-one bearings and, when none is clean, kept the LEAST BAD one - a track through
the toe marsh or across a steading, drawn anyway. The GM's rule is that a path does not pass through marshland (2026-08-12),
and a track across a farmstead is a lane on somebody's floor, so the least-bad bearing emitted the violation (FR-005). A
bearing is a straight-ish line; where the dry ground out of the cluster is a neck between two marshes, no bearing finds it.
A flood fill over a coarse grid does: from the start, every cell whose center stands clear of the walls, until a cell off
the canvas is reached - then the chain of cells is string-pulled back to a few legs. It runs at most a few times a map, only
where the sweep found nothing clean, so a 20 ft grid over the canvas is cheap.

THE GRID IS THE DECISION. A cell is walkable when its center stands farther than its wall's margin (plus half its diagonal) from every wall and off
every water line; a leg of the pulled path is kept only if every sample along it falls in a walkable cell. So the path the
fill finds and the path it returns answer the same question, and the result is clear of every wall by construction.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from collections import deque
from collections.abc import Iterator, Sequence, Set
from functools import lru_cache

from l7r.diagram.settlement import edge_dist, point_in_poly, seg_dist

from ..consts import Poly, Pt
from .geom import push_out_of

EXIT_CELL_FT = 20.0
"""The flood fill's grid - a map drawing convention: finer than any neck a track would use (a track is 6 ft; a neck under 20
ft between two marshes is no dry exit anyone would take), coarse enough that a canvas of a few thousand feet is tens of
thousands of cells."""

EXIT_OVERSHOOT_FT = 400.0
"""How far past the canvas edge the returned track runs on, so the crop trims it rather than it stopping short (the
connector's own rule: a track that overshoots is trimmed by the view, one that stops short reads as a dead end)."""


def _span(lo: float, hi: float, n: int, org: float, cell: float) -> range:
    """The grid's indices whose cell centers can lie in [lo, hi], with a cell to spare above (the scan's own range)."""
    return range(max(0, int((lo - org) // cell)), min(n, int((hi - org) // cell) + 2))


def _near_cells(a: Pt, b: Pt, r: float, x0: float, y0: float, nx: int, ny: int, cell: float) -> Iterator[tuple[int, int]]:
    """Every cell whose center COULD stand within `r` of the segment ab, a row at a time (feature 306): a point within r of
    the segment has its nearest point on the segment within r of it in y AND in x, so a row's cells are those within r in
    x of the part of the segment within r of the row's center line in y. A millionth of a foot is added to r, so rounding
    in the slice never drops a cell the exact `seg_dist` test would keep - the test still decides."""
    rr = r + 1e-6
    for j in _span(min(a[1], b[1]) - r, max(a[1], b[1]) + r, ny, y0, cell):
        cy = y0 + (j + 0.5) * cell
        if a[1] == b[1]:
            lo, hi = min(a[0], b[0]), max(a[0], b[0])
        else:
            t0, t1 = (cy - rr - a[1]) / (b[1] - a[1]), (cy + rr - a[1]) / (b[1] - a[1])
            t0, t1 = max(0.0, min(t0, t1)), min(1.0, max(t0, t1))
            if t0 > t1:
                continue
            lo, hi = sorted((a[0] + (b[0] - a[0]) * t0, a[0] + (b[0] - a[0]) * t1))
        for i in _span(lo - rr, hi + rr, nx, x0, cell):
            yield i, j


def _blocked_cells(walls: Sequence[tuple[Poly, float]], lines: Sequence[tuple[Pt, Pt]], x0: float, y0: float, nx: int, ny: int, cell: float) -> set[tuple[int, int]]:
    """The cells a point of which could stand inside a wall, within its margin of one, or on a water line: a cell whose
    CENTER stands within the margin plus half the cell's diagonal of a wall, or within one cell of a water line. So every
    point of a walkable cell keeps the margin, which is what makes the pulled path clear by construction.

    RASTERIZED, NOT SCANNED (feature 306, the GM's rule that an overlap check against more than a few things means the
    box or the line to stay on the right side of was never drawn). This asked every cell of a wall's box `point_in_poly`
    and `edge_dist` - each a walk of the WHOLE ring - so a 71-vertex field envelope over a 322-cell canvas was ~100,000
    ring walks a call (1.5 s of Kuwabata's track stage). The same two questions are asked of the same numbers in two
    cheaper orders: INSIDE a row at a time - the ray test's crossings of that row, each the very expression
    `point_in_poly` evaluates, sorted once, and a cell is inside when an odd number of them lie past its center (the ray
    test counts exactly the crossings with `cx < x`); WITHIN THE MARGIN an edge at a time - `edge_dist < r` is "some edge's
    `seg_dist` is under r", and only the cells of that edge's own box grown by r can be. Identical cells, by construction;
    `tests/hamletgen/ways/test_dry_exit_raster.py` holds the old scan as the oracle. An edge's or a water line's cells are
    asked a row at a time (`_near_cells`), so a long diagonal asks the strip beside it and not its whole box."""
    out: set[tuple[int, int]] = set()
    pad = cell * math.sqrt(0.5)
    for poly, margin in walls:
        if len(poly) < 3:
            continue
        reach = margin + pad
        n = len(poly)
        bx0, by0 = min(p[0] for p in poly) - margin - pad, min(p[1] for p in poly) - margin - pad
        bx1, by1 = max(p[0] for p in poly) + margin + pad, max(p[1] for p in poly) + margin + pad
        cols = _span(bx0, bx1, nx, x0, cell)
        # `point_in_poly`'s edges as it pairs them - vertex i with the one before it - so each crossing is its own number
        ray = [(poly[k][0], poly[k][1], poly[k - 1][0], poly[k - 1][1]) for k in range(n)]
        for j in _span(by0, by1, ny, y0, cell):
            cy = y0 + (j + 0.5) * cell
            xs = sorted((xj - xi) * (cy - yi) / (yj - yi + 1e-9) + xi for xi, yi, xj, yj in ray if (yi > cy) != (yj > cy))
            if xs:
                for i in cols:
                    if (len(xs) - bisect_right(xs, x0 + (i + 0.5) * cell)) & 1:
                        out.add((i, j))
        for k in range(n):
            a, b = poly[k], poly[(k + 1) % n]  # `edge_dist`'s own pairing, so `seg_dist` reads the same endpoints in the same order
            for i, j in _near_cells(a, b, reach, x0, y0, nx, ny, cell):
                if (i, j) not in out and seg_dist(x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell, a, b) < reach:
                    out.add((i, j))
    for a, b in lines:
        for i, j in _near_cells(a, b, cell, x0, y0, nx, ny, cell):
            if (i, j) not in out and seg_dist(x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell, a, b) < cell:
                out.add((i, j))
    return out


@lru_cache(maxsize=8)
def _blocked_memo(walls: tuple[tuple[tuple[Pt, ...], float], ...], lines: tuple[tuple[Pt, Pt], ...], x0: float, y0: float, nx: int, ny: int, cell: float) -> frozenset[tuple[int, int]]:
    """`_blocked_cells`, REMEMBERED by what it reads: the seat search asks every margin of a site with the same walls and
    water lines (cohort seed 44: 0.8 s rebuilding the one raster per margin), and only the start differs."""
    return frozenset(_blocked_cells([(list(p), m) for p, m in walls], list(lines), x0, y0, nx, ny, cell))


def dry_exit(start: Pt, walls: Sequence[tuple[Poly, float]], lines: Sequence[tuple[Pt, Pt]], W: float, H: float, cell: float = EXIT_CELL_FT) -> Poly | None:
    """A track from `start` off the canvas (0..W, 0..H) that stands clear of every wall - (polygon, margin) - and crosses no
    water line, or None when the start is walled in. The start's own cell is walkable whatever stands there (the gateway it
    leaves from is the caller's)."""
    x0, y0 = -2 * cell, -2 * cell
    nx, ny = int((W + 4 * cell) // cell) + 1, int((H + 4 * cell) // cell) + 1
    blocked = _blocked_memo(
        tuple((tuple((float(q[0]), float(q[1])) for q in poly), float(m)) for poly, m in walls), tuple(((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in lines), x0, y0, nx, ny, cell
    )
    si, sj = int((start[0] - x0) // cell), int((start[1] - y0) // cell)
    back: dict[tuple[int, int], tuple[int, int] | None] = {(si, sj): None}
    queue = deque([(si, sj)])
    goal: tuple[int, int] | None = None
    while queue:
        i, j = queue.popleft()
        cx, cy = x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell
        if not (0.0 <= cx <= W and 0.0 <= cy <= H):
            goal = (i, j)
            break
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nb = (i + di, j + dj)
            if 0 <= nb[0] < nx and 0 <= nb[1] < ny and nb not in back and nb not in blocked:
                back[nb] = (i, j)
                queue.append(nb)
    if goal is None:
        return None
    chain: list[tuple[int, int]] = []
    at: tuple[int, int] | None = goal
    while at is not None:
        chain.append(at)
        at = back[at]
    chain.reverse()
    pts: Poly = [start, *((x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell) for i, j in chain[1:])]
    pulled = _pull(pts, blocked, x0, y0, cell, (si, sj))
    a, b = pulled[-2], pulled[-1]
    d = math.dist(a, b) or 1.0
    return [*pulled[:-1], (b[0] + (b[0] - a[0]) / d * EXIT_OVERSHOOT_FT, b[1] + (b[1] - a[1]) / d * EXIT_OVERSHOOT_FT)]


def _pull(pts: Poly, blocked: Set[tuple[int, int]], x0: float, y0: float, cell: float, start: tuple[int, int]) -> Poly:
    """String-pull the chain of cell centers: from each point, the farthest later point whose straight leg samples only
    walkable cells (the start's own cell included)."""

    def clear(a: Pt, b: Pt) -> bool:
        n = max(1, int(math.dist(a, b) / (cell / 4)))
        for k in range(n + 1):
            q = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
            c = (int((q[0] - x0) // cell), int((q[1] - y0) // cell))
            if c in blocked and c != start:
                return False
        return True

    out = [pts[0]]
    k = 0
    while k < len(pts) - 1:
        m = len(pts) - 1
        while m > k + 1 and not clear(pts[k], pts[m]):
            m -= 1
        out.append(pts[m])
        k = m
    return out


def clear_of_bands(p: Pt, bands: Sequence[Poly], clear: float, tries: int = 4) -> Pt:
    """`p` pushed out past `clear` of every grove band it stands in or within `clear` of (`push_out_of`, a few rounds, since a
    push off one band can land near another)."""
    for _ in range(tries):
        near = next((b for b in bands if point_in_poly(p[0], p[1], b) or edge_dist(p[0], p[1], b) < clear), None)
        if near is None:
            break
        p = push_out_of(near, p, clear)
    return p


GROVE_EXIT_CELL_FT = 7.0
"""The dry exit's grid where farms carry their own groves (feature 291): a cell center stands clear when it is a band's
footpath gap and the track's half-width (7 ft) plus 0.71 of a cell from each band, so a gap G between two bands is sure to
hold one when G >= 14 + 2.41 x cell - for the 32 ft lane's room (`dispersed.LANE_ROOM_FT`), a cell of at most 7.4 ft. Only a
connector no bearing clears is found so, so the finer grid is paid where it is needed."""
