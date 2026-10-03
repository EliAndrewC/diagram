"""The comb fan's plots BY CONSTRUCTION (feature 302): its planted region cut by its bunds in one partition.

The carve used to cut each sector into rows of quads, drop the quads a guard refused, and leave the ground between them - the
dropped quads, the fork wedges, the toe below the last rows - to a repair pass (`close_seams`) that found every scrap and planted
or absorbed it. Here the ground the fan plants is computed FIRST (`planted_region`: the envelope less its water and the ground
it cannot command - the very three geometries the repair took as the ground to be planted), and then cut by every bund at once:
the threads, each sector's rows and columns, the strip past an outermost thread. `polygonize` of the noded bunds tiles the
region, so every bund is shared by the two cells it divides as it is laid, and no pass looks for bare ground after it.

TWO ADJACENT BASINS SHARE ONE BUND (GM 2026-08-17, on Inashiro: *"a tiny little standalone rectangle of earthen walls is just
smack dab in the middle of where the field should be ... it should basically always be the case that two adjacent rice paddies
share a single earthen wall rather than two different earthen walls"*). THE RESEARCH BEHIND THE RULE
(`research/questions/0014-bunds-between-the-paddies-aze.html`): an *aze* is a puddled-mud ridge 1-2 ft wide, re-plastered every
spring (*azenuri*) so each basin holds its shallow sheet of standing water. It is the WALL BETWEEN two basins, and it is built
once: a second parallel ridge would double the annual azenuri, drain neither basin, and strand the strip between them - inside
an irrigated command area, the most valuable land there is. Real paddy fabric is one CONNECTED bund network whose lines meet at
T-junctions; a free-standing four-sided ring floating inside it is not a paddy at all. A partition holds that by construction:
every cell's every edge is a bund it shares with the cell across it, or the region's own edge (water, or ground the fan cannot
command). The rule's test is `paddy_plot_seams_shared`.

The lattice keeps the carve's own character - rows along the contour with the wander between them (`rphase`), columns across the
sector with the contour wobble (`phase`), a sector's own row steps - and adds what a partition needs that a quad carve did not
(specs/302 research R2, each a measured dead end walked first):

- Past a thread's own end its boundary runs STRAIGHT DOWN THE FALL (`Sectors.bound`): along the drain, as `carve._bnd` follows
  it, a sector's columns converge on one point - the toe's sunburst.
- Each thread, so continued until it meets another thread, divides the region into SECTOR PIECES, and each sector's lattice is
  clipped to its own pieces: two sectors never cut the same ground (Sawada's crossed sectors made 30,000 slivers).
- The lattice thins where a sector narrows: a column runs only while the sector is wide enough for the columns it divides
  (ending in a T on a row bund as the width halves), a row only while it is wider than `MIN_ROW` plot widths.
- A bund piece lying wholly beside its ground's edge - within `HUG_ROW` of a row step (a row) or `HUG_COL` of a plot width (a
  column) - is not cut: it would cut a strip no basin can be (Sawada: rows across a hair-wide strip along the drain).
- A row is kept where the cell it closes reaches `ROW_CELL_SHARE` of a design cell at the sector's LOCAL width (`_rows_kept`), and
  the columns are counted at the sector's widest and thinned where it narrows - never one spacing or one count for a whole sector,
  whose width can halve where a thread rides its parent's path. A sector narrower than a plot is exempt from the row hug test.

Research: partition plumbing - NONE: line extension, clipping, polygonize and point-on-surface tests
"""

from __future__ import annotations

import math
import random
from typing import Any

from .carve import _bnd, _root_f
from .frame import Poly, Pt, _Frame, _Thread

MIN_ROW = 0.45
"""A row is cut only where its sector is wider than this many plot widths (or, in a sector narrower than a plot, this share of its
own median width): past that the tip is one basin, not a stack of slivers cut and then merged (specs/302 research R2, a map
drawing convention).

Research: narrow tip left one basin - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: no row cut where the sector is under 0.45 plot widths
"""

HUG_ROW = 0.5
"""A row piece lying wholly within this many row steps of its ground's edge is not cut (research R2: Sawada's rows across a strip
along the drain). Half the lower row step: the strip it would cut is under half a basin deep.

Research: no strip too thin for a paddy - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a row within half a row step of the edge is not cut
"""

HUG_COL = 0.3
"""A column piece lying wholly within this many plot widths of its ground's edge is not cut (a column beside a thread or a ditch
bank would cut a strip under a third of a basin wide).

Research: no strip too thin for a paddy - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a column within 0.3 plot widths of the edge is not cut
"""

ROW_CELL_SHARE = 0.6
"""A row is cut where the cell it closes reaches this share of a design cell at the sector's local width (`_rows_kept`): every row
on ground a plot wide or wider, fewer where it narrows - a map drawing convention, so a strip's cells are basins, not slivers.

Research: basin size where the sector narrows - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a row cut once its cell reaches 0.6 of the design cell
"""

CROSS = 0.5
"""A sector's bunds are clipped to its ground GROWN by this many px, so each piece crosses the ground's edge rather than ending on
it: clipped exactly, a row's end lay on the edge only to within floating error, and a row a hair short of the edge is a dangle
`polygonize` ignores - the edge column's cells came out three to five basins tall (measured, Inashiro's brief at 10 households: 12
cells over three design cells). The overshoot is a dangle outside the cell, which `polygonize` ignores in turn."""

RECUT_OVER = 2.5
"""A cell over this many design cells is cut again on a plain lattice (`recut`): the backstop under every lattice rule above, so
no gap in a sector's lattice ships a basin several plots big (the old carve's largest: about 3.7 design cells, specs/302 R2).

Research: largest basin - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a cell over 2.5 design cells is cut again
"""

OUTER_REACH = 14
"""The outer strip's lattice reaches this many plot widths past its thread - more than any strip a pool or cohort fan carries."""


def planted_region(F: _Frame, envelope: Poly, channels: list[dict[str, Any]], a_pts: Poly, dpts: Poly, g: float, bank: Any) -> Any:
    """The ground a fan plants: its envelope less its water and its banks (`seams.pockets._water`) and less the ground it cannot
    command - below the collector's bank, above the supply canal (`_outside_command`). Its area IS the fan's planted acreage.

    Research:
        planted ground - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: the envelope within the command area
        water and banks left out - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: no paddy on a course or its bank
    """
    from shapely.geometry import Polygon

    from .seams.pockets import _outside_command, _water

    field = Polygon(envelope).buffer(0)
    return field.difference(_water(channels, g)).difference(_outside_command(F, a_pts, dpts, field, g, bank))


def region_rings(region: Any) -> list[Poly]:
    """The region's outer rings - what stands for the plots' extent where the fit's legality reads it before any plot is cut.
    Its POLYGONS only: the difference that makes it can leave a sliver LINE where the water's edge runs along the envelope's
    (feature 304's scaling leg, seed 7 at 40 households: `'LineString' object has no attribute 'exterior'`), and a line
    plants nothing."""
    return [list(p.exterior.coords)[:-1] for p in getattr(region, "geoms", [region]) if p.geom_type == "Polygon" and not p.is_empty]


def _extend(pts: list[Pt], by: float) -> list[Pt]:
    """`pts` with both ends pushed out by `by` along their own terminal directions."""
    if len(pts) < 2:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[1]
    d = math.hypot(x0 - x1, y0 - y1) or 1.0
    head = (x0 + (x0 - x1) / d * by, y0 + (y0 - y1) / d * by)
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    d = math.hypot(xb - xa, yb - ya) or 1.0
    return [head, *pts, (xb + (xb - xa) / d * by, yb + (yb - ya) / d * by)]


class Sectors:
    """The fan's sectors - the ground between adjacent threads - as the partition cuts them (see the module docstring).

    Research: sectors between the ditch threads - research/questions/0053-irrigation-canals-and-how-they-are-laid-out-yosuiro.drawing.html: paddies cut between the lines of the water network
    """

    def __init__(self, F: _Frame, threads: list[_Thread], region: Any, R: random.Random, RW: random.Random, plot_across: float, row_step: tuple[float, float], g: float) -> None:
        self.F, self.threads, self.region = F, threads, region
        self.R, self.RW, self.plot_across, self.row_step, self.g = R, RW, plot_across, row_step, g
        minx, miny, maxx, maxy = region.bounds
        self.f_bottom = max(F.to_uf(x, y)[1] for x, y in ((minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy))) + 20
        self.rows: list[float] = []
        self.n_rows = 0
        self.narrow = False

    def bound(self, T: _Thread, fv: float) -> Pt:
        """A thread's boundary at fall `fv`: `carve._bnd` down to its own end, then straight down the fall from where it stopped.

        Research: past a thread's end - UNRESEARCHED: the column bund runs straight down the fall rather than converging along the drain
        """
        end = T.pts[-1]
        f_end = self.F.to_uf(*end)[1]
        if fv <= f_end:
            return _bnd(T, fv, self.F)
        return (end[0] + self.F.d[0] * (fv - f_end), end[1] + self.F.d[1] * (fv - f_end))

    def thread_lines(self) -> list[Any]:
        """Every thread, and each continued straight down the fall past its own end until it meets another thread.

        Research: sector pieces - UNRESEARCHED: each thread continued straight down the fall until it meets another
        """
        import shapely
        from shapely.geometry import LineString

        own = [LineString(th.pts) for th in self.threads if len(th.pts) >= 2]
        out = list(own)
        for k, th in enumerate([th for th in self.threads if len(th.pts) >= 2]):
            end = th.pts[-1]
            reach = max(0.0, self.f_bottom - self.F.to_uf(*end)[1]) + 40.0
            ext = LineString([end, (end[0] + self.F.d[0] * reach, end[1] + self.F.d[1] * reach)])
            hit = ext.intersection(shapely.union_all([g for m, g in enumerate(own) if m != k]))
            stops = [ext.project(p) for p in shapely.get_parts(hit)] if not hit.is_empty else []
            stops = [s for s in stops if s > 0.5]
            out.append(LineString([end, ext.interpolate(min(stops))]) if stops else ext)
        return out

    def grid_lines(self, A: _Thread, B: _Thread, f_top: float | None = None) -> list[list[Pt]]:
        """One sector's rows (the first `n_rows`) and columns, drawn past its ground - the caller clips them to it. `f_top`: the
        fall of the sector's ground's top, where its rows begin when that lies above its threads' takeoff (the head wedge along
        the canal - the ground the carve's canal closers cut - which rows begun at the takeoff never crossed: measured, a 34 x 526
        px wedge on Inashiro's brief at 20 households came out one cell).

        Research:
            row spacing - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: rows a random `row_step` apart down the fall, the design cell's depth
            column count - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: one column a plot width at the sector's widest
            row wander - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: each row bund drifts downhill by up to 0.13 of a row step, fading to nothing at the first and last rows
            column wobble - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: each column line bows along the contour by up to 5 px on its own phase
        """
        F, g, R, row_step, across = self.F, self.g, self.R, self.row_step, self.plot_across
        f_lo = max(_root_f(A, F), _root_f(B, F)) + 6 * g
        f_hi0 = max(F.to_uf(*A.pts[-1])[1], F.to_uf(*B.pts[-1])[1])
        span_fs = [f_lo + (f_hi0 - f_lo) * i / 12 for i in range(13)] if f_hi0 > f_lo else [f_lo]
        ws = sorted(math.dist(self.bound(A, fv), self.bound(B, fv)) for fv in span_fs)
        width_mid = ws[len(ws) // 2]
        # THE COLUMNS ARE COUNTED AT THE SECTOR'S WIDEST, and thinned where it narrows (`_column_kept`): counted at its median, a
        # sector whose thread rides its parent's path for half its span was given one column where it was four plots wide
        nsub = max(1, round(ws[-1] / across))
        phase = [R.uniform(0, 6.28) for _ in range(nsub + 2)]
        rphase = [self.RW.uniform(0, 6.28) for _ in range(nsub + 2)]
        rowamp = 0.13 * sum(row_step) / 2
        self.narrow = width_mid < across
        rows = [(f_lo if f_top is None else min(f_lo, f_top)) - 6 * g]
        while rows[-1] < self.f_bottom:
            rows.append(rows[-1] + R.uniform(*row_step))
        lo, hi = f_lo, rows[-1]

        def edge(fv: float, j: int) -> Pt:
            a, b = self.bound(A, fv), self.bound(B, fv)
            x, y = a[0] + j / nsub * (b[0] - a[0]), a[1] + j / nsub * (b[1] - a[1])
            if j in (0, nsub):
                return (x, y)
            wob = 5.0 * math.sin(fv / 70 + phase[j])
            ft = max(0.0, min(1.0, (fv - lo) / (hi - lo)))
            rw = rowamp * math.sin(fv / 47 + rphase[j]) * math.sin(math.pi * ft)
            return (x + F.c[0] * wob + F.d[0] * rw, y + F.c[1] * wob + F.d[1] * rw)

        grid = [[edge(fv, j) for j in range(nsub + 1)] for fv in rows]
        widths = [math.dist(r[0], r[-1]) for r in grid]
        # the tip is judged against the sector's OWN width where that is under a plot's: a sector narrow along its whole length
        # is not a tip, and a plot-width threshold cut none of its rows
        tip = MIN_ROW * min(across, width_mid)
        # A ROW'S VERTICES ARE WHERE IT MEETS A COLUMN THAT RUNS THERE (and its two ends): through every column's point, the thinned
        # ones too, a row narrowing to a few px between its columns carried each point's own wobble and wander - a sawtooth of
        # 1-2 px teeth, and where the wobble passed a neighbor a fold, whose cells failed the toe rule and were left bare or merged
        # past the recut bound (the glyph check on Inashiro's east sector head; every scrap over 700 sq ft in the pool and the
        # 10/20-household briefs carried the teeth)
        kept = _rows_kept(rows, widths, nsub, across, row_step, tip)
        lines = [_extend([q for j, q in enumerate(row) if j in (0, nsub) or _column_kept(widths[i], nsub, j, across)], 2.0) for i, row in enumerate(grid) if i in kept]
        self.n_rows, self.rows = len(lines), rows
        for j in range(1, nsub):
            run: list[Pt] = []
            for i in range(len(rows)):
                if _column_kept(widths[i], nsub, j, across):
                    run.append(grid[i][j])
                    continue
                if len(run) >= 2:
                    lines.append(run)
                run = []
            if len(run) >= 2:
                lines.append(_extend(run, 40.0) if len(run) == len(rows) else run)
        return lines

    def outer_lines(self, T: _Thread, other: _Thread) -> list[list[Pt]]:
        """The strip past an OUTERMOST thread `T`: columns are `T` shifted outward a plot width at a time, rows run outward from
        it along the contour at the sector's own row falls (call `grid_lines` for the sector first).

        Research: strip past the outer thread - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: columns a plot width apart parallel to the thread, rows at the sector's falls
        """
        F, across = self.F, self.plot_across
        f_mid = sum(self.rows) / len(self.rows)
        away = 1.0 if F.to_uf(*self.bound(T, f_mid))[0] >= F.to_uf(*self.bound(other, f_mid))[0] else -1.0
        cx, cy = F.c[0] * away, F.c[1] * away
        base = [self.bound(T, fv) for fv in self.rows]
        lines = [[(x + cx * m * across, y + cy * m * across) for x, y in base] for m in range(1, OUTER_REACH)]
        lines += [[(x, y), (x + cx * OUTER_REACH * across, y + cy * OUTER_REACH * across)] for x, y in base]
        return [_extend(ln, 40.0) for ln in lines]

    def sector_of(self, x: float, y: float) -> tuple[int, str] | None:
        """The sector whose threads bracket (x, y) across the fall at its own fall, with "" - or, for ground past the OUTERMOST
        thread, the edge sector beside it and its side ("lo": past its thread A, "hi": past its B). None with under two threads."""
        u, f = self.F.to_uf(x, y)
        us = [self.F.to_uf(*self.bound(T, f))[0] for T in self.threads]
        if len(us) < 2:
            return None
        best = None
        for k in range(len(us) - 1):
            lo, hi = min(us[k], us[k + 1]), max(us[k], us[k + 1])
            if lo - 0.5 <= u <= hi + 0.5 and (best is None or hi - lo < best[0]):
                best = (hi - lo, k)
        if best is not None:
            return best[1], ""
        e = min(range(len(us)), key=lambda m: us[m]) if u < min(us) else max(range(len(us)), key=lambda m: us[m])
        k = e if e < len(us) - 1 else e - 1
        return k, ("lo" if e == k else "hi")


def _rows_kept(rows: list[float], widths: list[float], nsub: int, across: float, row_step: tuple[float, float], tip: float) -> set[int]:
    """The rows a sector cuts: the first, then each where the cell it closes - its column's width THERE (the sector's width over
    the columns kept there) times the fall since the last row kept - reaches `ROW_CELL_SHARE` of a design cell, and the sector is
    still wider than `tip`. Wide ground keeps every row; a strip half a plot wide keeps every other one. (A spacing set once per
    sector, from its median width, spaced the rows three steps apart down a sector that was narrow for only half its span.)

    Research: rows where the sector narrows - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a row kept once its cell reaches ROW_CELL_SHARE of a design cell
    """
    design = across * sum(row_step) / 2
    kept = {0}
    last = rows[0]
    for i in range(1, len(rows)):
        n_here = min(nsub, max(1, round(widths[i] / across)))
        if widths[i] >= tip and widths[i] / n_here * (rows[i] - last) >= ROW_CELL_SHARE * design:
            kept.add(i)
            last = rows[i]
    return kept


def _column_kept(width: float, nsub: int, j: int, across: float) -> bool:
    """Does column `j` of `nsub` run where its sector is `width` wide? Halved (every other column, then every fourth) while the
    sector holds fewer than two thirds of the columns it divides - nested, so a dropped column ends in a T on a row bund.

    Research: columns thin to a T - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a dropped column ends at a T-junction on a row bund
    """
    n_here = max(1, round(width / across))
    step = 1
    while nsub / step > n_here * 1.5 and step < nsub:
        step *= 2
    return j % step == 0


def keep_rows(parts: list[Any], ground: Any, lim: float, across: float) -> list[Any]:
    """The row pieces a sector cuts: a SHORT piece (under a plot's width) crosses a strip of its ground, and is kept where the strip
    is at least `MIN_ROW` plot widths across - a ditch-side strip, whose rows are basins - and dropped where it is narrower (a
    hair-wide strip along the drain, whose rows would be slivers); a longer piece takes the whole-piece hug test (`keep_far`).
    (Measured on Inashiro's brief at 10 households: the strips beside its ditches lost every row to the hug test and came out
    3-4 basins long - the sector's width is measured between thread centerlines, inside the ditches, so it reads wider than the
    strip of land and the narrow-sector exemption never applied.)

    Research: ditch-side strips keep their rows - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a short row kept where its strip is at least MIN_ROW plot widths across
    """
    short = [q for q in parts if q.length < across]
    return [q for q in short if q.length >= MIN_ROW * across] + keep_far([q for q in parts if q.length >= across], ground, lim)


def keep_far(parts: list[Any], ground: Any, lim: float) -> list[Any]:
    """The bund pieces NOT lying wholly within `lim` of `ground`'s edge - every point along the piece, sampled at half the
    limit, nearer than `lim` drops it. SAMPLED, not its vertices: a straight row across a one-column sector has vertices only at
    its two ends, which lie on the sector's sides, so a vertex test dropped every row of such a sector.

    Research: no strip too thin for a paddy - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a bund lying wholly within `lim` of its ground's edge is not cut
    """
    import shapely

    if not parts or lim <= 0.0:
        return parts
    edge = ground.boundary
    return [q for q in parts if shapely.distance(shapely.points(shapely.get_coordinates(shapely.segmentize(q, lim / 2))), edge).max() >= lim]


def inside(region: Any, cells: list[Any]) -> list[Any]:
    """The cells whose point on surface lies in `region`."""
    import shapely

    if not cells:
        return []
    pts = shapely.point_on_surface(cells)
    return [c for c, k in zip(cells, shapely.contains_xy(region, shapely.get_x(pts), shapely.get_y(pts)), strict=True) if k]


def recut(cell: Any, F: _Frame, across: float, step: float) -> list[Any]:
    """A cell the lattice left over `RECUT_OVER` design cells, cut again on a plain lattice at the fan's grain - rows along the
    contour every `step`, columns every `across`, spaced evenly over the cell's own extent in the frame - as the old seam pass
    planted a large pocket (`_plant`). The pieces tile the cell; what is too small is the settle's to merge.

    Research: oversized cell recut - research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html: a plain lattice at the fan's design cell
    """
    import shapely
    from shapely.geometry import LineString

    uf = [F.to_uf(x, y) for x, y in cell.exterior.coords]
    u0, u1 = min(u for u, _ in uf), max(u for u, _ in uf)
    f0, f1 = min(f for _, f in uf), max(f for _, f in uf)
    n_c, n_r = max(1, round((u1 - u0) / across)), max(1, round((f1 - f0) / step))
    lines = [LineString([F.to_xy(u0 + (u1 - u0) * k / n_c, f0 - 1), F.to_xy(u0 + (u1 - u0) * k / n_c, f1 + 1)]) for k in range(1, n_c)]
    lines += [LineString([F.to_xy(u0 - 1, f0 + (f1 - f0) * k / n_r), F.to_xy(u1 + 1, f0 + (f1 - f0) * k / n_r)]) for k in range(1, n_r)]
    if not lines:
        return [cell]
    noded = shapely.union_all([cell.boundary, *(ln.intersection(cell.buffer(CROSS)) for ln in lines)])
    return inside(cell, list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(noded)))))) or [cell]


def _f_top(F: _Frame, ground: Any) -> float:
    """The least fall over `ground`'s outline - where its top lies down the slope."""
    return min(F.to_uf(x, y)[1] for p in getattr(ground, "geoms", [ground]) for x, y in p.exterior.coords)


def _lines_in(ground: Any, lines: list[list[Pt]]) -> list[Any]:
    import shapely
    from shapely.geometry import MultiLineString

    if not lines:
        return []
    return [q for q in shapely.get_parts(ground.intersection(MultiLineString(lines))) if q.geom_type == "LineString" and q.length > 0.5]


def cut(sec: Sectors) -> list[Any]:
    """The region tiled: divided into sector pieces by the threads, each sector's lattice clipped to its own pieces (the strip
    past an outermost thread by the outer lattice), the pieces of bund hugging their ground's edge left out, then every bund
    noded at once and the cells `polygonize` makes inside the region kept - every bund shared by construction.

    Research: one shared bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: two paddies side by side share one bund, no bare strip between them
    """
    import shapely

    region = sec.region
    noded = shapely.union_all([region.boundary, *sec.thread_lines()])
    by_sector: dict[int, list[Any]] = {}
    outer: dict[tuple[int, str], list[Any]] = {}
    for pc in inside(region, list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(noded)))))):
        p = pc.point_on_surface()
        got = sec.sector_of(p.x, p.y)
        if got is None:
            continue
        (outer.setdefault(got, []) if got[1] else by_sector.setdefault(got[0], [])).append(pc)
    bunds: list[Any] = []
    for k, pcs in sorted(by_sector.items()):
        ground = shapely.union_all(pcs)
        lines = sec.grid_lines(sec.threads[k], sec.threads[k + 1], _f_top(sec.F, ground))
        reach = ground.buffer(CROSS)
        # a narrow sector's rows are spaced for it (`_rows_kept`): they cross ground near both its sides by nature
        bunds += keep_rows(_lines_in(reach, lines[: sec.n_rows]), ground, 0.0 if sec.narrow else HUG_ROW * sec.row_step[0], sec.plot_across)
        bunds += keep_far(_lines_in(reach, lines[sec.n_rows :]), ground, HUG_COL * sec.plot_across)
    for (k, side), pcs in sorted(outer.items()):
        sec.grid_lines(sec.threads[k], sec.threads[k + 1])  # the sector's own row falls, for the strip's rows to meet
        T, other = (sec.threads[k], sec.threads[k + 1]) if side == "lo" else (sec.threads[k + 1], sec.threads[k])
        ground = shapely.union_all(pcs)
        bunds += keep_far(_lines_in(ground.buffer(CROSS), sec.outer_lines(T, other)), ground, HUG_COL * sec.plot_across)
    noded = shapely.union_all([noded, *bunds])
    cells = inside(region, list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(noded))))))
    design = sec.plot_across * sum(sec.row_step) / 2
    return [q for c in cells for q in (recut(c, sec.F, sec.plot_across, sum(sec.row_step) / 2) if c.area > RECUT_OVER * design else [c])]
