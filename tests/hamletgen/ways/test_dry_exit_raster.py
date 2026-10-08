"""`dry_exit._blocked_cells` rasterized (feature 306): the same blocked cells the scan of every cell against every ring
found, held to that scan - kept here as the ORACLE - on rolled walls and water lines, and shown to notice a dropped
candidate."""

import math
import random

import pytest

from l7r.diagram.hamletgen.ways import dry_exit as DE
from l7r.diagram.settlement import edge_dist, point_in_poly, seg_dist


def _blocked_scan(walls, lines, x0, y0, nx, ny, cell):  # type: ignore[no-untyped-def]
    """The scan `_blocked_cells` was before feature 306, verbatim: every cell of a wall's box asked `point_in_poly` and
    `edge_dist`, every cell of a line's box asked `seg_dist`."""
    out = set()
    pad = cell * math.sqrt(0.5)

    def span(lo, hi, n, org):  # type: ignore[no-untyped-def]
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


def _rolled(seed: int, W: float = 900.0):  # type: ignore[no-untyped-def]
    """Walls of every kind the callers hand in - a ragged many-vertex envelope (concave, so the ray test's parity is
    exercised), buildings with a margin, a 16-gon at a wide berth, a degenerate two-point wall - and water lines with a
    horizontal, a vertical and long diagonals, some off the canvas."""
    rng = random.Random(seed)
    cx, cy = rng.uniform(250, 650), rng.uniform(250, 650)
    env = [(cx + math.cos(t) * r, cy + math.sin(t) * r) for t, r in ((math.tau * k / 71, rng.uniform(80, 300)) for k in range(71))]
    walls = [(env, 0.0)]
    for _ in range(12):
        x, y, w, h = rng.uniform(-50, W), rng.uniform(-50, W), rng.uniform(20, 60), rng.uniform(20, 60)
        walls.append(([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], 16.0))
    px, py, r = rng.uniform(0, W), rng.uniform(0, W), rng.uniform(30, 90)
    walls.append(([(px + r * math.cos(k * math.pi / 8), py + r * math.sin(k * math.pi / 8)) for k in range(16)], 80.0))
    walls.append(([(0.0, 0.0), (10.0, 10.0)], 5.0))
    lines = [((rng.uniform(-100, W + 100), rng.uniform(-100, W + 100)), (rng.uniform(-100, W + 100), rng.uniform(-100, W + 100))) for _ in range(25)]
    y = rng.uniform(0, W)
    lines += [((10.0, y), (W - 10.0, y)), ((y, 10.0), (y, W - 10.0))]
    return walls, lines


@pytest.mark.parametrize("cell", [DE.EXIT_CELL_FT, DE.GROVE_EXIT_CELL_FT])
@pytest.mark.parametrize("seed", range(6))
def test_the_raster_blocks_exactly_the_cells_the_scan_blocked(seed: int, cell: float) -> None:
    walls, lines = _rolled(seed)
    x0 = y0 = -2 * cell
    nx = ny = int((900.0 + 4 * cell) // cell) + 1
    want = _blocked_scan(walls, lines, x0, y0, nx, ny, cell)
    assert len(want) > 100, "non-vacuous: the fixture blocks ground"
    assert DE._blocked_cells(walls, lines, x0, y0, nx, ny, cell) == want


def test_the_oracle_notices_a_dropped_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    """The comparison above would fail if the row slice dropped a cell the scan blocks: the slice is cut short by one
    cell at each end, and the answers differ."""
    walls, lines = _rolled(0)
    cell = DE.EXIT_CELL_FT
    x0 = y0 = -2 * cell
    nx = ny = int((900.0 + 4 * cell) // cell) + 1
    keep = DE._near_cells

    def short(a, b, r, *rest):  # type: ignore[no-untyped-def]
        cells = list(keep(a, b, r, *rest))
        rows: dict[int, list[int]] = {}
        for i, j in cells:
            rows.setdefault(j, []).append(i)
        return [(i, j) for j, row in rows.items() for i in row[1:-1]]

    monkeypatch.setattr(DE, "_near_cells", short)
    assert DE._blocked_cells(walls, lines, x0, y0, nx, ny, cell) != _blocked_scan(walls, lines, x0, y0, nx, ny, cell)
