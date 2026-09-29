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
from collections import deque
from collections.abc import Sequence

from l7r.diagram.settlement import edge_dist, point_in_poly, seg_dist

from ..consts import Poly, Pt

EXIT_CELL_FT = 20.0
"""The flood fill's grid - a map drawing convention: finer than any neck a track would use (a track is 6 ft; a neck under 20
ft between two marshes is no dry exit anyone would take), coarse enough that a canvas of a few thousand feet is tens of
thousands of cells."""

EXIT_OVERSHOOT_FT = 400.0
"""How far past the canvas edge the returned track runs on, so the crop trims it rather than it stopping short (the
connector's own rule: a track that overshoots is trimmed by the view, one that stops short reads as a dead end)."""


def _blocked_cells(walls: Sequence[tuple[Poly, float]], lines: Sequence[tuple[Pt, Pt]], x0: float, y0: float, nx: int, ny: int, cell: float) -> set[tuple[int, int]]:
    """The cells a point of which could stand inside a wall, within its margin of one, or on a water line: a cell whose
    CENTER stands within the margin plus half the cell's diagonal of a wall, or within one cell of a water line. So every
    point of a walkable cell keeps the margin, which is what makes the pulled path clear by construction."""
    out: set[tuple[int, int]] = set()
    pad = cell * math.sqrt(0.5)

    def span(lo: float, hi: float, n: int, org: float) -> range:
        return range(max(0, int((lo - org) // cell)), min(n, int((hi - org) // cell) + 2))

    for poly, margin in walls:
        if len(poly) < 3:
            continue
        bx0, by0 = min(p[0] for p in poly) - margin - pad, min(p[1] for p in poly) - margin - pad
        bx1, by1 = max(p[0] for p in poly) + margin + pad, max(p[1] for p in poly) + margin + pad
        for i in span(bx0, bx1, nx, x0):
            for j in span(by0, by1, ny, y0):
                cx, cy = x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell
                if point_in_poly(cx, cy, poly) or edge_dist(cx, cy, poly) < margin + pad:
                    out.add((i, j))
    for a, b in lines:
        for i in span(min(a[0], b[0]) - cell, max(a[0], b[0]) + cell, nx, x0):
            for j in span(min(a[1], b[1]) - cell, max(a[1], b[1]) + cell, ny, y0):
                if seg_dist(x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell, a, b) < cell:
                    out.add((i, j))
    return out


def dry_exit(start: Pt, walls: Sequence[tuple[Poly, float]], lines: Sequence[tuple[Pt, Pt]], W: float, H: float, cell: float = EXIT_CELL_FT) -> Poly | None:
    """A track from `start` off the canvas (0..W, 0..H) that stands clear of every wall - (polygon, margin) - and crosses no
    water line, or None when the start is walled in. The start's own cell is walkable whatever stands there (the gateway it
    leaves from is the caller's)."""
    x0, y0 = -2 * cell, -2 * cell
    nx, ny = int((W + 4 * cell) // cell) + 1, int((H + 4 * cell) // cell) + 1
    blocked = _blocked_cells(walls, lines, x0, y0, nx, ny, cell)
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


def _pull(pts: Poly, blocked: set[tuple[int, int]], x0: float, y0: float, cell: float, start: tuple[int, int]) -> Poly:
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
