"""Split from tools/pack_audit.py by feature 173 - see this package's CLAUDE.md for the index."""

from dataclasses import dataclass

from .parse import ParsedPlan, Rect

FTPX: float = 3.0  # 3 px = 1 ft
# not a structure standing in the masonry. The pool's tightest LEGITIMATE clearance is 0.5 px
# (Hayakawa's south-wall stables/gatehouse row) and the smallest real defect found was 3 px, so
# this threshold has ~1 px of margin on the passing side and 6x on the failing side.

Grid = list[list[bool]]


@dataclass(frozen=True)
class VacantRect:
    """A maximal empty rectangle, sized in feet with its SVG-pixel top-left."""

    w_ft: float
    h_ft: float
    area_sqft: float
    x: float
    y: float
    zone: str = "central"  # "central" (courtyard) or "perimeter" (gap in the wall ring)

    @property
    def orient(self) -> str:
        return "horizontal" if self.w_ft >= self.h_ft else "vertical"


@dataclass(frozen=True)
class RegionTile:
    """Building coverage within one tile of the interior grid."""

    row: int
    col: int
    coverage_pct: float
    interior_sqft: float


def _blank(w: int, h: int) -> Grid:
    return [[False] * w for _ in range(h)]


def _paint(mask: Grid, r: Rect, cell: int, minx: float, miny: float, w: int, h: int) -> None:
    gy0 = max(0, int((r.y - miny) // cell))
    gy1 = min(h, int((r.y2 - miny) // cell) + 1)
    gx0 = max(0, int((r.x - minx) // cell))
    gx1 = min(w, int((r.x2 - minx) // cell) + 1)
    for gy in range(gy0, gy1):
        row = mask[gy]
        for gx in range(gx0, gx1):
            row[gx] = True


@dataclass(frozen=True)
class _Grids:
    inside: Grid
    building: Grid
    occ: Grid
    divider: Grid
    w: int
    h: int
    minx: float
    miny: float
    cell: int


def _grids(plan: ParsedPlan, cell: int) -> _Grids:
    minx, miny, maxx, maxy = plan.bounds
    w = max(1, int((maxx - minx) // cell) + 1)
    h = max(1, int((maxy - miny) // cell) + 1)
    inside = _blank(w, h)
    building = _blank(w, h)
    occ = _blank(w, h)
    for r in plan.interior:
        _paint(inside, r, cell, minx, miny, w, h)
    for r in plan.buildings:
        _paint(building, r, cell, minx, miny, w, h)
        _paint(occ, r, cell, minx, miny, w, h)
    for r in plan.open_features:
        _paint(occ, r, cell, minx, miny, w, h)
    for r in plan.glyphs:
        _paint(occ, r, cell, minx, miny, w, h)
    divider = _blank(w, h)
    for r in plan.dividers:
        _paint(divider, r, cell, minx, miny, w, h)
    return _Grids(inside, building, occ, divider, w, h, minx, miny, cell)


def coverage(plan: ParsedPlan, cell: int = 2) -> float:
    """Building footprint as a fraction (0..1) of the walled interior."""
    g = _grids(plan, cell)
    inside_cells = 0
    built_cells = 0
    for gy in range(g.h):
        for gx in range(g.w):
            if g.inside[gy][gx]:
                inside_cells += 1
                if g.building[gy][gx]:
                    built_cells += 1
    return built_cells / inside_cells


def _perimeter_band(g: _Grids, depth_cells: int) -> Grid:
    """Inside cells within depth_cells of the interior edge (a wall), by cardinal rays.

    A DISTANCE TRANSFORM, not a ray walk (GM 2026-08-26, the make quick profile): the first form
    walked up to `depth_cells` cells in four directions from EVERY cell - ~6M checks per call on a
    200 x 200 grid, 1.4 s for the four calls one report test makes. Two sweeps per axis give each
    cell its distance to the nearest blocking cell (outside the plan, a divider, or the grid edge)
    in each cardinal direction; a cell is in the band iff the least of the four is within
    `depth_cells`, which is exactly what the ray walk decided. Proven equal on random grids
    (tests/tools/test_pack_audit.py)."""
    w, h = g.w, g.h
    band = _blank(w, h)
    INF = w + h + 1

    def blocking(gy: int, gx: int) -> bool:
        return not g.inside[gy][gx] or bool(g.divider[gy][gx])

    dist = [[INF] * w for _ in range(h)]
    for gy in range(h):
        row = dist[gy]
        d = 1  # the grid edge is a blocking cell one step outside
        for gx in range(w):  # nearest blocker to the LEFT (or the edge) - a cell's OWN status never counts (the ray walk starts at d=1)
            row[gx] = min(row[gx], d)
            d = 1 if blocking(gy, gx) else d + 1
        d = 1
        for gx in range(w - 1, -1, -1):  # ...and to the RIGHT
            row[gx] = min(row[gx], d)
            d = 1 if blocking(gy, gx) else d + 1
    for gx in range(w):
        d = 1
        for gy in range(h):  # nearest blocker ABOVE
            dist[gy][gx] = min(dist[gy][gx], d)
            d = 1 if blocking(gy, gx) else d + 1
        d = 1
        for gy in range(h - 1, -1, -1):  # ...and BELOW
            dist[gy][gx] = min(dist[gy][gx], d)
            d = 1 if blocking(gy, gx) else d + 1
    for gy in range(h):
        for gx in range(w):
            band[gy][gx] = bool(g.inside[gy][gx]) and dist[gy][gx] <= depth_cells
    return band


def perimeter_hugging_pct(plan: ParsedPlan, depth_ft: float = 25.0, cell: int = 2) -> float:
    """Fraction of building footprint sitting within depth_ft of a wall (high = a good ring)."""
    g = _grids(plan, cell)
    band = _perimeter_band(g, max(1, int(depth_ft * FTPX / cell)))
    built = 0
    hugging = 0
    for gy in range(g.h):
        for gx in range(g.w):
            if g.building[gy][gx] and g.inside[gy][gx]:
                built += 1
                if band[gy][gx]:
                    hugging += 1
    return hugging / built if built else 0.0


def _max_rect(mask: Grid, w: int, h: int) -> tuple[int, int, int, int, int]:
    """Largest all-True axis-aligned rectangle: (area, left, top, width, height) in cells."""
    heights = [0] * w
    best = (0, 0, 0, 0, 0)
    for y in range(h):
        row = mask[y]
        for x in range(w):
            heights[x] = heights[x] + 1 if row[x] else 0
        stack: list[int] = []
        x = 0
        while x <= w:
            cur = heights[x] if x < w else 0
            if not stack or cur >= heights[stack[-1]]:
                stack.append(x)
                x += 1
            else:
                top = stack.pop()
                width = x if not stack else x - stack[-1] - 1
                area = heights[top] * width
                if area > best[0]:
                    left = stack[-1] + 1 if stack else 0
                    best = (area, left, y - heights[top] + 1, width, heights[top])
    return best


def top_vacant_rects(
    plan: ParsedPlan,
    n: int = 3,
    cell: int = 2,
    min_area_sqft: float = 150.0,
    perimeter_depth_ft: float = 25.0,
) -> list[VacantRect]:
    """The n largest non-overlapping empty rectangles, largest first (greedy).

    Each is tagged zone="central" (courtyard - good) or "perimeter" (a gap in the
    wall ring - slack) by whether its centroid sits in the perimeter band.
    """
    g = _grids(plan, cell)
    band = _perimeter_band(g, max(1, int(perimeter_depth_ft * FTPX / cell)))
    vacant: Grid = [[g.inside[gy][gx] and not g.occ[gy][gx] for gx in range(g.w)] for gy in range(g.h)]
    floor_px = min_area_sqft * FTPX * FTPX
    out: list[VacantRect] = []
    for _ in range(n):
        area_cells, gx0, gy0, wc, hc = _max_rect(vacant, g.w, g.h)
        if area_cells * cell * cell < floor_px:
            break
        cy, cx = gy0 + hc // 2, gx0 + wc // 2
        out.append(
            VacantRect(
                w_ft=wc * cell / FTPX,
                h_ft=hc * cell / FTPX,
                area_sqft=round(area_cells * cell * cell / (FTPX * FTPX)),
                x=gx0 * cell + g.minx,
                y=gy0 * cell + g.miny,
                zone="perimeter" if band[cy][cx] else "central",
            )
        )
        for yy in range(gy0, gy0 + hc):
            for xx in range(gx0, gx0 + wc):
                vacant[yy][xx] = False
    return out


def region_density(plan: ParsedPlan, rows: int = 3, cols: int = 3, cell: int = 2) -> list[RegionTile]:
    """Per-tile building coverage over the interior (exposes local sparsity)."""
    g = _grids(plan, cell)
    tiles: list[RegionTile] = []
    for row in range(rows):
        gy0, gy1 = row * g.h // rows, (row + 1) * g.h // rows
        for col in range(cols):
            gx0, gx1 = col * g.w // cols, (col + 1) * g.w // cols
            inside_cells = 0
            built_cells = 0
            for gy in range(gy0, gy1):
                for gx in range(gx0, gx1):
                    if g.inside[gy][gx]:
                        inside_cells += 1
                        if g.building[gy][gx]:
                            built_cells += 1
            pct = built_cells / inside_cells if inside_cells else 0.0
            tiles.append(RegionTile(row, col, pct, round(inside_cells * cell * cell / (FTPX * FTPX))))
    return tiles
