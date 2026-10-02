"""Feature 302's Phase 0 prototype: the comb field built by construction (plan D1-D5), importing the engine read-only.

    fit_by_construction(*fit_field_args, **fit_field_kwargs) -> (net, info)

The same signature as `hamletgen.water.fit.fit_field`, so the harness hands both the same captured call. Per trial size the
skeleton is laid exactly as `carve_comb` lays it (D1); the PLANTED REGION is the envelope less its water and the ground the
fan cannot command (D2), and its area is the trial's acreage - no plots are cut during the search. On the winning size the
region is cut by the row and column bunds in one partition (D3), each cell is judged by the engine's own ring rules and the
toe discipline and a failing cell is merged across a shared bund (D4), and the dry hem and the beans run after it (D5).

Nothing here is imported by the engine; it lives in the spec directory and runs only under `make spec-harness`.
"""

from __future__ import annotations

import math
import random
from typing import Any

from l7r.diagram.hamletgen.consts import FAN_ASPECTS
from l7r.diagram.hamletgen.water import fit as F_
from l7r.diagram.sitegen.geom import SQ_FT_PER_ACRE
from l7r.diagram.waterfields import comb as C
from l7r.diagram.waterfields.banks import _TOE_MIN_APEX, _TOE_MIN_AREA, _TOE_MIN_THICKNESS, cell_area, dedup_ring, is_chevron, pointed_ring
from l7r.diagram.waterfields.carve import _bnd, _root_f
from l7r.diagram.waterfields.frame import _Frame, _poly_area, _poly_perim
from l7r.diagram.waterfields.hem import _comb_dry_and_beans
from l7r.diagram.waterfields.palette import RICE_GREENS
from l7r.diagram.waterfields.ring_rules import fan_context, ring_violations
from l7r.diagram.waterfields.seams.pockets import _outside_command, _water
from l7r.diagram.waterfields.trunks import anchor_trunk_ends, drop_stub_pieces

STUBBED: list[str] = []  # SC-004: every part of the current finish the prototype does not build (none, so far)


# ---- D1 + D2: the skeleton and its region -------------------------------------------------------------------------------


class Trial:
    """One trial size: the skeleton `carve_comb` lays, and the planted region (D2)."""

    def __init__(self, W, H, sluice, seed, down_deg, canal_a_len, canal_b_len, offtakes_a, offtakes_b, plot_across, field_fall, grain, head_deg, head_len):  # type: ignore[no-untyped-def]
        from shapely.geometry import Polygon

        self.W, self.H, self.grain, self.down_deg, self.plot_across = W, H, grain, down_deg, plot_across
        R = self.R = random.Random(seed)
        Fm = self.F = _Frame(down_deg)
        DOWN = Fm.down
        channels: list[dict[str, Any]] = []
        self.fork, self.a_pts = C._comb_skeleton(R, Fm, DOWN, sluice, canal_a_len, canal_b_len, W, H, grain, channels, head_deg, head_len)
        self.threads, self.bc, spawns = C._comb_threads(R, Fm, DOWN, self.fork, self.a_pts, canal_b_len, offtakes_a, offtakes_b, plot_across)
        C._comb_march(R, Fm, DOWN, self.threads, spawns, W, H, field_fall)
        self.dpts = C._comb_drain(R, Fm, self.threads, W, H, grain, channels)
        self.brook = C._comb_brook(R, Fm, self.dpts, W, H)
        self.drain_bank = C._drain_bank(Fm, self.dpts, grain)
        C._comb_clip_and_cap(R, Fm, self.threads, self.dpts, self.drain_bank)
        n0 = len(channels)
        C._comb_canal_pieces(Fm, self.threads, self.bc, self.a_pts, offtakes_a, self.fork, grain, channels)
        kept = {id(c) for c in drop_stub_pieces([c for c in channels[n0:] if c["role"] == "main"])}
        channels[n0:] = [c for c in channels[n0:] if c["role"] != "main" or id(c) in kept]
        C.round_channel_joints(channels)
        self.channels = channels
        self.envelope = C._comb_floor_and_winding([], self.threads, self.a_pts, self.dpts, Fm)
        anchor_trunk_ends(channels, self.envelope, W, H)
        field = Polygon(self.envelope).buffer(0)
        self.region = field.difference(_water(channels, grain)).difference(_outside_command(Fm, self.a_pts, self.dpts, field, grain, self.drain_bank))

    def rings(self) -> list[list[tuple[float, float]]]:
        geoms = getattr(self.region, "geoms", [self.region])
        return [list(g.exterior.coords)[:-1] for g in geoms if not g.is_empty]

    def scoring_net(self) -> dict[str, Any]:
        """What the fit's legality reads (the plots' extent and the channels): the region's outline stands for the plots."""
        return {"plots": [{"poly": r} for r in self.rings()], "channels": self.channels}


# ---- D3: the partition --------------------------------------------------------------------------------------------------


def _extend(pts: list[tuple[float, float]], by: float) -> list[tuple[float, float]]:
    if len(pts) < 2:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[1]
    d = math.hypot(x0 - x1, y0 - y1) or 1.0
    head = (x0 + (x0 - x1) / d * by, y0 + (y0 - y1) / d * by)
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    d = math.hypot(xb - xa, yb - ya) or 1.0
    tail = (xb + (xb - xa) / d * by, yb + (yb - ya) / d * by)
    return [head, *pts, tail]


class Sectors:
    """The fan's sectors as the partition cuts them: each thread (continued straight down the fall past its own end, and
    stopped where that continuation meets another thread) divides the region into SECTOR PIECES, and each sector's rows and
    columns are clipped to its own pieces - so two sectors never cut the same ground (Sawada: a thread continued straight
    while its neighbor curved crossed it, and both sectors' rows cut the ground past the crossing into slivers)."""

    def __init__(self, t: Trial, row_step: tuple[float, float]) -> None:
        self.t, self.row_step = t, row_step
        Fm = t.F
        minx, miny, maxx, maxy = t.region.bounds
        corners = [Fm.to_uf(minx, miny), Fm.to_uf(maxx, miny), Fm.to_uf(maxx, maxy), Fm.to_uf(minx, maxy)]
        self.f_bottom = max(f for _, f in corners) + 20

    def bound(self, T: Any, fv: float) -> tuple[float, float]:
        """A thread's boundary at fall `fv`: `_bnd` down to its own end, then STRAIGHT DOWN THE FALL from where it stopped
        (along the drain, as `_bnd` follows it, a sector's columns converge on one point - the toe's sunburst)."""
        t, Fm = self.t, self.t.F
        end = T.pts[-1]
        f_end = Fm.to_uf(*end)[1]
        if fv <= f_end:
            return _bnd(T, fv, Fm, t.dpts, t.drain_bank)
        return (end[0] + Fm.d[0] * (fv - f_end), end[1] + Fm.d[1] * (fv - f_end))

    def thread_lines(self) -> list[Any]:
        import shapely
        from shapely.geometry import LineString, Point

        t, Fm = self.t, self.t.F
        own = [LineString(th.pts) for th in t.threads if len(th.pts) >= 2]
        out = list(own)
        for k, th in enumerate([th for th in t.threads if len(th.pts) >= 2]):
            end = th.pts[-1]
            reach = max(0.0, self.f_bottom - Fm.to_uf(*end)[1]) + 40.0
            ext = LineString([end, (end[0] + Fm.d[0] * reach, end[1] + Fm.d[1] * reach)])
            # STOPPED AT THE FIRST THING IT MEETS - another thread, or the region's edge past its own first few feet (a ditch
            # thread starts inside its own water): carried on along the drain's bank it would cut a hair-wide strip off the
            # region wherever the drain runs near the fall's line (Sawada: 347 slivers), and a thread stopping a little short of
            # the drain must still close its sector there, or two sectors' ground runs together through the gap
            others = shapely.union_all([g for m, g in enumerate(own) if m != k])
            hit = ext.intersection(others)
            if not hit.is_empty:
                d = min(ext.project(p) for p in shapely.get_parts(hit) if ext.project(p) > 0.5) if any(ext.project(p) > 0.5 for p in shapely.get_parts(hit)) else None
                if d is not None:
                    ext = LineString([end, ext.interpolate(d)])
            out.append(ext)
        return out

    def grid_lines(self, A: Any, B: Any) -> list[list[tuple[float, float]]]:
        """One sector's rows and columns, with the carve's contour wobble and row wander, drawn past its ground (clipped later)."""
        t, Fm, g, R = self.t, self.t.F, self.t.grain, self.t.R
        row_step = self.row_step
        f_lo = max(_root_f(A, Fm), _root_f(B, Fm)) + 6 * g
        f_hi0 = max(Fm.to_uf(*A.pts[-1])[1], Fm.to_uf(*B.pts[-1])[1])
        # THE SECTOR'S WIDTH IS ITS MEDIAN over its span, not one sample: at a single fall one thread may be riding its parent's
        # path, and a near-zero width there gave a narrow-sector stretch that spaced the rows hundreds of px apart
        span_fs = [f_lo + (f_hi0 - f_lo) * i / 12 for i in range(13)] if f_hi0 > f_lo else [f_lo]
        ws = sorted(math.dist(self.bound(A, fv), self.bound(B, fv)) for fv in span_fs)
        width_mid = ws[len(ws) // 2]
        nsub = max(1, round(width_mid / t.plot_across))  # a narrow sector still takes rows: its ground is in the region
        phase = [R.uniform(0, 6.28) for _ in range(nsub + 2)]
        rphase = [self.RW.uniform(0, 6.28) for _ in range(nsub + 2)]
        js = list(range(nsub + 1))
        rowamp = 0.13 * sum(row_step) / 2
        # A NARROW SECTOR TAKES FEWER ROWS: where the sector is narrower than a plot, rows at the fan's step would cut cells under
        # the area floor; spaced out so each cell is about a design cell (the whole-piece hug test would otherwise drop them)
        stretch = self.stretch = min(3.0, max(1.0, t.plot_across / max(width_mid, 1.0)))
        rows = [f_lo - 6 * g]
        while rows[-1] < self.f_bottom:
            rows.append(rows[-1] + R.uniform(*row_step) * stretch)
        span = (f_lo, rows[-1])

        def edge(fv: float, j: int) -> tuple[float, float]:
            a, b = self.bound(A, fv), self.bound(B, fv)
            tt = j / nsub
            x, y = a[0] + tt * (b[0] - a[0]), a[1] + tt * (b[1] - a[1])
            if j not in (0, nsub):
                wob = 5.0 * math.sin(fv / 70 + phase[j])
                x, y = x + Fm.c[0] * wob, y + Fm.c[1] * wob
                ft = max(0.0, min(1.0, (fv - span[0]) / (span[1] - span[0] or 1.0)))
                rw = rowamp * math.sin(fv / 47 + rphase[j]) * math.sin(math.pi * ft)
                x, y = x + Fm.d[0] * rw, y + Fm.d[1] * rw
            return (x, y)

        grid = [[edge(fv, j) for j in js] for fv in rows]
        # THE GRID THINS AS THE SECTOR NARROWS (where two threads converge, at a fork or on the drain): a column runs only
        # while the sector is wide enough for the columns it divides (`keep`, nested by halving so a dropped column ends in
        # a T on a row bund, as a real fan's wedge is terraced into fewer, wider basins), and a row only while the sector is
        # wider than `MIN_ROW` plot widths - past that the tip is one basin, not a stack of slivers cut and then merged

        widths = [math.dist(r[0], r[-1]) for r in grid]

        def keep(i: int, j: int) -> bool:
            n_here = max(1, round(widths[i] / t.plot_across))
            step = 1
            while nsub / step > n_here * 1.5 and step < nsub:
                step *= 2
            return j % step == 0

        MIN_ROW = 0.45
        lines = [_extend(row, 2.0) for i, row in enumerate(grid) if i == 0 or widths[i] >= MIN_ROW * t.plot_across]
        self.n_rows = len(lines)
        self.rows = rows
        for j in [j for j in js if j not in (0, nsub)]:
            run: list[tuple[float, float]] = []
            for i in range(len(rows)):
                if keep(i, j):
                    run.append(grid[i][j])
                else:
                    if len(run) >= 2:
                        lines.append(run)
                    run = []
            if len(run) >= 2:
                lines.append(_extend(run, 40.0) if len(run) == len(rows) else run)
        return lines

    def polygon(self, A: Any, B: Any) -> Any:
        """The sector's ground as the carve defines it: between `_bnd(A, f)` and `_bnd(B, f)` for every fall `f` - each
        thread's own course, its parent's above its takeoff, the drain's bank past its end - sampled every few px from above
        the sector's head to past the drain. Two neighbors share the thread between them exactly, so their pieces neither
        overlap nor leave a gap; the drain-bank tail where both bounds lie on the bank closes to nothing (`buffer(0)`)."""
        from shapely.geometry import Polygon

        t, Fm = self.t, self.t.F
        f0 = min(_root_f(A, Fm), _root_f(B, Fm)) - 2 * self.row_step[1]
        n = max(8, int((self.f_bottom - f0) / 4.0))
        fs = [f0 + (self.f_bottom - f0) * i / n for i in range(n + 1)]
        left = [_bnd(A, f, Fm, t.dpts, t.drain_bank) for f in fs]
        right = [_bnd(B, f, Fm, t.dpts, t.drain_bank) for f in fs]
        return Polygon(left + right[::-1]).buffer(0)

    def outer_lines(self, T: Any, other: Any) -> list[list[tuple[float, float]]]:
        """The lattice of the strip past an OUTERMOST thread `T` (the canal-side ground no sector brackets): column bunds are
        `T` itself shifted outward a plot width at a time, row bunds run outward from it along the contour at the sector's
        own row falls - so the strip is cut at the fan's grain and its rows meet the sector's. Clipped to the strip later."""
        Fm = self.t.F
        f_mid = sum(self.rows) / len(self.rows)
        away = 1.0 if Fm.to_uf(*self.bound(T, f_mid))[0] >= Fm.to_uf(*self.bound(other, f_mid))[0] else -1.0
        cx, cy = Fm.c[0] * away, Fm.c[1] * away
        base = [self.bound(T, fv) for fv in self.rows]
        reach = 14
        lines = [[(x + cx * m * self.t.plot_across, y + cy * m * self.t.plot_across) for x, y in base] for m in range(1, reach)]
        lines += [[(x, y), (x + cx * reach * self.t.plot_across, y + cy * reach * self.t.plot_across)] for x, y in base]
        return [_extend(ln, 40.0) for ln in lines]

    def sector_of(self, x: float, y: float) -> tuple[int, str] | None:
        """The sector whose two threads bracket (x, y) across the fall at its own fall, and "" - or, for ground past the
        OUTERMOST thread, the edge sector beside it and the side ("lo": past its thread A, "hi": past its B)."""
        Fm = self.t.F
        u, f = Fm.to_uf(x, y)
        us = [Fm.to_uf(*self.bound(T, f))[0] for T in self.t.threads]
        best = None
        for k in range(len(us) - 1):
            lo, hi = min(us[k], us[k + 1]), max(us[k], us[k + 1])
            if lo - 0.5 <= u <= hi + 0.5 and (best is None or hi - lo < best[0]):
                best = (hi - lo, k)
        if best is not None:
            return best[1], ""
        if len(us) < 2:
            return None
        e = min(range(len(us)), key=lambda m: us[m]) if u < min(us) else max(range(len(us)), key=lambda m: us[m])
        k = e if e < len(us) - 1 else e - 1
        return k, ("lo" if e == k else "hi")


def cut(t: Trial, row_step: tuple[float, float]) -> list[Any]:
    """D3: the region divided into sector pieces by the threads (each continued straight down the fall past its own end until
    it meets another thread); each sector's grid clipped to its own pieces and the strip past an outermost thread cut by the
    outer lattice; a bund piece lying wholly within `HUG_*` of its ground's edge not cut; then every bund noded at once and
    the cells `polygonize` makes inside the region kept - every edge shared by construction."""
    import shapely
    from shapely.geometry import MultiLineString

    sec = Sectors(t, row_step)
    sec.RW = random.Random(0x12005)
    threads = sec.thread_lines()
    region = t.region
    noded = shapely.union_all([region.boundary, *threads])
    pieces = _inside(region, list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(noded))))))
    PIECES.clear()
    by_sector: dict[int, list[Any]] = {}
    outer: dict[tuple[int, str], list[Any]] = {}
    for pc in pieces:
        p = pc.point_on_surface()
        got = sec.sector_of(p.x, p.y)
        PIECES.append((got, round(pc.area), (round(p.x), round(p.y))))
        if got is None:
            continue
        if got[1]:
            outer.setdefault(got, []).append(pc)
        else:
            by_sector.setdefault(got[0], []).append(pc)
    # A BUND LYING WHOLLY BESIDE ITS GROUND'S EDGE IS NOT CUT: a row piece every vertex of which is within `HUG_ROW` of a row
    # step of the edge (Sawada: rows across a hair-wide strip along the drain), or a column piece within `HUG_COL` of a plot
    # width (a column beside a thread or a ditch bank), would cut a strip no basin can be - so it stays with the cell beside it
    HUG_ROW, HUG_COL = 0.5, 0.3
    clipped = []
    TAGS.clear()

    def keep_far(parts: list[Any], ground: Any, lim: float) -> list[Any]:
        if not parts:
            return []
        edge = ground.boundary
        return [q for q in parts if shapely.distance(shapely.points(list(q.coords)), edge).max() >= lim]

    for k, pcs in sorted(by_sector.items()):
        lines = sec.grid_lines(t.threads[k], t.threads[k + 1])
        ground = shapely.union_all(pcs)
        for idx, group in ((0, lines[: sec.n_rows]), (1, lines[sec.n_rows :])):
            if not group:
                continue
            parts = [q for q in shapely.get_parts(ground.intersection(MultiLineString(group))) if q.geom_type == "LineString" and q.length > 0.5]
            # a narrow sector's rows are spaced for it (`stretch`): they run across ground near both its sides by nature
            lim = (0.0 if sec.stretch > 1.0 else HUG_ROW * row_step[0]) if idx == 0 else HUG_COL * t.plot_across
            got_ = keep_far(parts, ground, lim)
            TAGS.extend([("row" if idx == 0 else "col", k)] * len(got_))
            clipped += got_
    for (k, side), pcs in sorted(outer.items()):
        sec.grid_lines(t.threads[k], t.threads[k + 1])  # the sector's row falls, for the strip's rows to meet
        T, other = (t.threads[k], t.threads[k + 1]) if side == "lo" else (t.threads[k + 1], t.threads[k])
        ground = shapely.union_all(pcs)
        got = ground.intersection(MultiLineString(sec.outer_lines(T, other)))
        got_ = keep_far([q for q in shapely.get_parts(got) if q.geom_type == "LineString" and q.length > 0.5], ground, HUG_COL * t.plot_across)
        TAGS.extend([("outer", k)] * len(got_))
        clipped += got_
    global LAST_LINES
    LAST_LINES = [(TAGS[i], list(q.coords)) for i, q in enumerate(clipped)] + [(("thread", -1), list(q.coords)) for q in threads]
    noded = shapely.union_all([noded, *clipped])
    return _inside(region, list(shapely.get_parts(shapely.polygonize(list(shapely.get_parts(noded))))))


def _trim_hugs(parts: list[Any], edge: Any, lim: float) -> list[Any]:
    """Each bund piece with the stretch of it that runs within `lim` of its ground's `edge` cut away - but not the stubs at its
    own two ends, where it meets the sides it spans (a row across a narrow sector is near those by nature). A row that runs
    along the drain for part of its length, then rises from it, keeps the part that rose; the strip it would have cut off
    stays with the cell beside it."""
    import shapely
    from shapely.geometry import Point

    near = edge.buffer(lim)
    r = 1.5 * lim
    out = []
    for q in parts:
        kept = q.difference(near)
        ends = q.intersection(shapely.union(Point(q.coords[0]).buffer(r), Point(q.coords[-1]).buffer(r)))
        got = shapely.union(kept, ends) if not ends.is_empty else kept
        out += [s for s in shapely.get_parts(shapely.line_merge(got) if got.geom_type == "MultiLineString" else got) if s.geom_type == "LineString" and s.length > 0.5]
    return out


def _inside(region: Any, cells: list[Any]) -> list[Any]:
    import shapely

    if not cells:
        return []
    pts = shapely.point_on_surface(cells)
    inside = shapely.contains_xy(region, shapely.get_x(pts), shapely.get_y(pts))
    return [c for c, k in zip(cells, inside, strict=True) if k]


# ---- D4: the rules at construction --------------------------------------------------------------------------------------


def _ring(poly: Any) -> list[tuple[float, float]]:
    return [(round(x, 1), round(y, 1)) for x, y in list(poly.exterior.coords)[:-1]]


def breaks(ring: list[tuple[float, float]], ctx: Any, plot_across: float, cell: float, steps_ok: bool = False) -> bool:
    """`ring_violations`, and the toe discipline `_comb_toe_and_hem` drops by (thinness, area, apex, chevron)."""
    if len(ring) < 3:
        return True
    per = _poly_perim(ring)
    area = _poly_area(ring)
    if per <= 0 or 2 * area / per < _TOE_MIN_THICKNESS * plot_across or area < _TOE_MIN_AREA * cell:
        return True
    if pointed_ring(dedup_ring([(float(p[0]), float(p[1])) for p in ring], 1.0), _TOE_MIN_APEX) or is_chevron(ring):
        return True
    found = ring_violations(ring, ctx)
    return bool(found - {"steps"} if steps_ok else found)


def _verdict(c: Any, ctx: Any, plot_across: float, cell: float) -> set[str]:
    """Every rule a cell breaks: `ring_violations`, and "toe" for the toe discipline's drops."""
    ring = _ring(c)
    found = set(ring_violations(ring, ctx)) if len(ring) >= 3 else {"crossing"}
    if len(ring) >= 3:
        per, area = _poly_perim(ring), _poly_area(ring)
        if per <= 0 or 2 * area / per < _TOE_MIN_THICKNESS * plot_across or area < _TOE_MIN_AREA * cell:
            found.add("toe")
        elif pointed_ring(dedup_ring([(float(p[0]), float(p[1])) for p in ring], 1.0), _TOE_MIN_APEX) or is_chevron(ring):
            found.add("toe")
    return found


def _polys(g: Any) -> list[Any]:
    import shapely

    return [p for p in shapely.get_parts(g) if p.geom_type == "Polygon" and not p.is_empty and p.area > 0]


def settle(cells: list[Any], ctx: Any, plot_across: float, cell: float) -> tuple[list[Any], int]:
    """D4: the partition snapped to the recorded grid (0.1 px - the slivers thinner than a recorded coordinate collapse, every
    shared bund snapped the same on both sides); each cell judged ONCE; staircases split by the repair's own `_split_steps`;
    every other failing cell merged across its longest shared bund into the neighbor whose union holds the rules (a staircase
    the merge leaves is split after it). Returns (cells, the count neither could make lawful)."""
    import shapely

    from l7r.diagram.waterfields.seams.close import _split_steps

    snapped = [q for c in shapely.set_precision(cells, 0.1) for q in _polys(c)]
    alive: dict[int, Any] = {}
    verdict: dict[int, set[str]] = {}
    nxt = 0

    def add(c: Any) -> int:
        nonlocal nxt
        if not c.is_valid:
            parts = _polys(c.buffer(0))
            c = max(parts, key=lambda q: q.area) if parts else c
        alive[nxt], verdict[nxt] = c, _verdict(c, ctx, plot_across, cell)
        nxt += 1
        return nxt - 1

    def split(i: int) -> None:
        if not ctx.g or "steps" not in verdict[i]:
            return
        parts = _split_steps(alive[i], ctx)
        if len(parts) > 1:
            del alive[i], verdict[i]
            for q in parts:
                for r in _polys(q):
                    add(r)

    for c in snapped:
        add(c)
    for i in [k for k, v in verdict.items() if "steps" in v]:
        split(i)
    # THE MERGE: smallest failing cell first, into the neighbor across its longest shared bund whose union holds the rules
    ids = list(alive)
    tree = shapely.STRtree([alive[k] for k in ids])
    owner = {k: k for k in ids}

    def find(k: int) -> int:
        while owner.get(k, k) != k:
            k = owner[k]
        return k

    # A CLUSTER OF SMALL CELLS GROWS (the scraps a ditch junction leaves are several cells, each too small, neighbors to each
    # other): two failing cells may merge when the union's only fault is its size, and the pass repeats until nothing merges.
    # A lawful neighbor is only ever handed a union that is itself lawful.
    SIZE_ONLY = {"area", "toe", "steps"}
    for _round in range(6):
        merged = 0
        for i in sorted((k for k in list(alive) if verdict.get(k)), key=lambda k: alive[k].area):
            if i not in alive or not verdict[i]:
                continue
            me = alive[i]
            scored = []
            for jj in tree.query(me.buffer(0.2)):
                j = find(ids[int(jj)]) if int(jj) < len(ids) else None
                if j is None or j == i or j not in alive or (j, ) in scored:
                    continue
                try:
                    shared = me.boundary.intersection(alive[j].buffer(0.2)).length
                except shapely.errors.GEOSException:
                    continue
                if shared > 0.0:
                    scored.append((shared, j))
            why = []
            for _shared, j in sorted(set(scored), reverse=True):
                # the union OPENED by 0.3 px (mitred, so corners stay corners): a sliver's hair-width spike - thinner than three
                # recorded coordinates - does not survive into its neighbor's outline
                try:
                    u = shapely.simplify(shapely.union(me, alive[j]).buffer(-0.3, join_style="mitre").buffer(0.3, join_style="mitre"), 0.25)
                except shapely.errors.GEOSException:
                    continue
                if u.geom_type != "Polygon" or len(u.interiors):
                    why.append((u.geom_type, len(getattr(u, "interiors", []))))
                    continue
                v = _verdict(u, ctx, plot_across, cell)
                lawful = not (v - {"steps"})
                growing = bool(verdict[j]) and not (v - SIZE_ONLY) and u.area > max(me.area, alive[j].area)
                if not (lawful or growing):
                    why.append((sorted(v), sorted(verdict[j]), round(alive[j].area)))
                    continue
                alive[j], verdict[j] = u, v
                del alive[i], verdict[i]
                owner[i] = j
                split(j)
                merged += 1
                break
            else:
                WHY[i] = why
        if not merged:
            break
    # WHAT NEITHER CAN MAKE LAWFUL IS LEFT BARE, as the repair leaves it today (`seams/close.py` `hold_ring_rules`: "split,
    # welded, or left bare"): counted, with whether the scrap had any neighbor to merge into
    global LAST_SCRAPS
    LAST_SCRAPS = []
    for k, v in list(verdict.items()):
        if not v:
            continue
        c = alive[k]
        nb = sum(1 for jj in tree.query(c.buffer(0.2)) if find(ids[int(jj)]) in alive and find(ids[int(jj)]) != k and c.boundary.intersection(alive[find(ids[int(jj)])].buffer(0.2)).length > 0)
        LAST_SCRAPS.append((sorted(v), round(c.area, 1), nb, WHY.get(k, [])[:4], c))
        del alive[k], verdict[k]
    return list(alive.values()), len(LAST_SCRAPS)


LAST_SCRAPS: list[Any] = []
LAST_LINES: list[Any] = []
TAGS: list[Any] = []
PIECES: list[Any] = []
WHY: dict[int, Any] = {}


# ---- the low ground and its tint (what the carve marks and `close_seams`' last stretch judges) -----------------------------


def tint(plots: list[dict[str, Any]], dpts: Any, plot_across: float, row_step: tuple[float, float], g: float, R: random.Random) -> None:
    """The carve's `low` (the bottom two levels: here, the plots within two rows of the collector) and its FLOODED sample
    (45% of the bottom level: the plots on the collector), then `close_seams`' tint judgment verbatim - every sampled plot
    that would read as water rather than a basin demoted, and the most basin-like low plot promoted if none survives."""
    import shapely
    from shapely.geometry import LineString, Polygon

    from l7r.diagram.waterfields.banks import (
        _TINT_END_FT,
        _TINT_MAX_AREA_RATIO,
        _TINT_MAX_ASPECT,
        _TINT_MIN_APEX,
        _TINT_MIN_RECTANGULARITY,
        _TINT_MIN_SOLIDITY,
        tapers_to_a_point,
    )
    from l7r.diagram.waterfields.palette import FLOODED
    from l7r.diagram.waterfields.seams.close import _basin_rank, _needle
    from l7r.diagram.waterfields.seams.geoms import ring_polygons

    _pgs = ring_polygons([_q["poly"] for _q in plots])
    _collector = LineString(dpts) if len(dpts) >= 2 else None
    _to_collector = shapely.distance(_pgs, _collector).tolist() if _collector is not None and _pgs else [1e9] * len(plots)
    two_rows = 2 * sum(row_step) / 2
    for p, d in zip(plots, _to_collector, strict=True):
        p["low"] = d <= two_rows
        if d <= 0.25 * plot_across and R.random() < 0.45:
            p["fill"] = FLOODED
    _hull_areas = shapely.area(shapely.convex_hull(_pgs)).tolist() if _pgs else []
    _mrrs = list(shapely.minimum_rotated_rectangle(_pgs)) if _pgs else []
    _areas = sorted(_pg.area for _q, _pg in zip(plots, _pgs, strict=True) if len(_q.get("poly") or []) >= 3)
    _median_plot = _areas[len(_areas) // 2] if _areas else 0.0
    _keeps: list[Any] = []
    for _k, p in enumerate(plots):
        _t_end = _TINT_END_FT * g / 2
        _pg = _pgs[_k]
        _psol = (_pg.area / (_hull_areas[_k] or 1.0)) if isinstance(_pg, Polygon) and not _pg.is_empty else 1.0
        _pcx = sum(_q[0] for _q in p["poly"]) / len(p["poly"])
        _pcy = sum(_q[1] for _q in p["poly"]) / len(p["poly"])
        _at_outfall = bool(dpts) and min(math.hypot(_q[0] - dpts[-1][0], _q[1] - dpts[-1][1]) for _q in [*p["poly"], (_pcx, _pcy)]) < 1.5 * plot_across
        _mrr = _mrrs[_k] if isinstance(_pg, Polygon) and not _pg.is_empty else None
        _asp = 1.0
        _fill = (_pg.area / _mrr.area) if isinstance(_mrr, Polygon) and _mrr.area > 0.0 else 1.0
        if isinstance(_mrr, Polygon):
            _sides = [math.dist(_q, _r) for _q, _r in zip(list(_mrr.exterior.coords)[:-1], list(_mrr.exterior.coords)[1:], strict=True)]
            if len(_sides) >= 2 and min(_sides[0], _sides[1]) > 0.0:
                _asp = max(_sides[0], _sides[1]) / min(_sides[0], _sides[1])
        _wrong = (
            _needle(p["poly"])
            or pointed_ring(dedup_ring(p["poly"], 1.0), _TINT_MIN_APEX)
            or tapers_to_a_point(p["poly"], _t_end, _TINT_MIN_APEX, 4 * _t_end)
            or _psol < _TINT_MIN_SOLIDITY
            or _at_outfall
            or _asp > _TINT_MAX_ASPECT
            or _fill < _TINT_MIN_RECTANGULARITY
            or (_median_plot > 0.0 and _pg.area > _TINT_MAX_AREA_RATIO * _median_plot)
        )
        if p.get("fill") == FLOODED and _wrong:
            p["fill"] = RICE_GREENS[(int(abs(p["poly"][0][0]) * 7) + int(abs(p["poly"][0][1]) * 3)) % len(RICE_GREENS)]
        elif not _wrong and _pg.area > 0.0 and (p.get("low") or (_collector is not None and _to_collector[_k] <= 0.25 * plot_across)):
            _keeps.append((_basin_rank(_pg, _fill, _median_plot, _collector, plot_across), p))
    if _keeps and not any(_p.get("fill") == FLOODED for _p in plots):
        _keeps.sort(key=lambda _a: (_a[0], round(_a[1]["poly"][0][0], 1), round(_a[1]["poly"][0][1], 1)))
        _keeps[0][1]["fill"] = FLOODED


# ---- the fit (D2's search, D3-D5 on the winner) -------------------------------------------------------------------------


def _trial(plan: Any, sluice: Any, seed: int, plot_across: float, k: float, aspect: float) -> Trial:
    _trim_a = F_.BROOK_FAN_TRIM if plan.brook_side < 0 else 1.0
    _trim_b = F_.BROOK_FAN_TRIM if plan.brook_side > 0 else 1.0
    return Trial(
        plan.W,
        plan.H,
        sluice,
        seed,
        plan.down_deg,
        (F_.REF_CANAL_A[0] * k * aspect * _trim_a, F_.REF_CANAL_A[1] * k * aspect * _trim_a),
        (F_.REF_CANAL_B[0] * k * aspect * _trim_b, F_.REF_CANAL_B[1] * k * aspect * _trim_b),
        plan.offtakes_a,
        plan.offtakes_b,
        plot_across,
        F_.REF_FIELD_FALL * k / aspect,
        F_.GRAIN,
        plan.head_deg,
        plan.head_lead,
    )


def _search_aspect(plan: Any, sluice: Any, seed: int, plot_across: float, aspect: float, tolerance: float, rounds: int, probe: bool, counter: list[int]) -> tuple[tuple[bool, float], Trial]:
    """`_fit_at_aspect`'s search, each trial scored on its region (D2) instead of a carve and its prediction."""
    lo, hi = 0.35, 2.2
    lever = math.sqrt(2.0 / (1.0 + F_.BROOK_FAN_TRIM)) if plan.brook_side != 0 else 1.0
    lo, hi, k = lo * lever, hi * lever, 1.0 * lever
    best: tuple[tuple[bool, float], Trial] | None = None
    pts: list[tuple[float, float]] = []
    for _ in range(rounds):
        k = min(max(k, lo + 1e-3), hi - 1e-3)
        t = _trial(plan, sluice, seed, plot_across, k, aspect)
        counter[0] += 1
        acres = t.region.area * plan.ftpx * plan.ftpx / SQ_FT_PER_ACRE
        err = abs(acres - plan.target_acres) / plan.target_acres
        score = (not F_.fan_legal(t.scoring_net(), plan.down_deg, plan.ftpx), err)
        if best is None or score < best[0]:
            best = (score, t)
        if err <= tolerance and not score[0]:
            break
        if acres < plan.target_acres:
            lo = k
        else:
            hi = k
        pts.append((k, acres))
        if hi - lo < 0.03:
            break
        if probe and len(pts) == 1 and acres < plan.target_acres:
            k = hi - 1e-3
            continue
        k = F_._predict_k(pts, plan.target_acres, lo, hi)
    assert best is not None
    return best


def build(t: Trial, plan: Any, plot_across: float, row_step: tuple[float, float], fan_middle: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """D3-D5 on one trial: the partition, the rules, the dry hem and beans; the net and what the harness reports."""
    import time

    tm: dict[str, float] = {}
    t0 = time.perf_counter()
    cell = cell_area(plot_across, row_step)
    ctx = fan_context(t.channels, t.grain, cell)
    cells = cut(t, row_step)
    tm["partition"] = time.perf_counter() - t0
    raw_cells = len(cells)
    t0 = time.perf_counter()
    cells, stuck = settle(cells, ctx, plot_across, cell)
    tm["settle"] = time.perf_counter() - t0
    scraps = list(LAST_SCRAPS)
    plots = [{"poly": _ring(c), "fill": t.R.choice(RICE_GREENS)} for c in cells]
    t0 = time.perf_counter()
    tint(plots, t.dpts, plot_across, row_step, t.grain, t.R)
    tm["tint"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    dry_plots, dry_acres, beans, reserve = _comb_dry_and_beans(
        t.R, t.F, t.a_pts, t.bc, plots, t.channels, t.W, t.H, (), (70, 132), 0.28, t.grain, 1.1, plan.grain_drift, fan_middle=fan_middle, fork=t.fork
    )
    net = {
        "down_deg": t.down_deg,
        "fork": t.fork,
        "cell": cell,
        "channels": t.channels,
        "plots": plots,
        "threads": t.threads,
        "drain": t.dpts,
        "brook": t.brook,
        "envelope": t.envelope,
        "dry_plots": dry_plots,
        "dry_acres": dry_acres,
        "dry_reserve": reserve,
        "bund_bean_runs": beans,
        "bund_beans": [q for run in beans for q in run],
        "supply_banks": True,
        "acres": sum(_poly_area(p["poly"]) for p in plots) * 4 / 43560,
        "furrows_vary": True,
        "fan_middle": fan_middle,
    }
    tm["dry_and_beans"] = time.perf_counter() - t0
    return net, {"cells": len(cells), "raw_cells": raw_cells, "stuck": stuck, "region": t.region, "ctx": ctx, "cell": cell, "plot_across": plot_across, "times": tm, "scraps": scraps}


def fit_by_construction(plan: Any, sluice: Any, seed: int, plot_across: float, row_step: tuple[float, float], tolerance: float = 0.06, rounds: int = 9, fan_middle: str = "cleared") -> tuple[dict[str, Any], dict[str, Any]]:
    """`fit_field`, by construction: the same aspect order, bracket, probe and widening; each trial scored on its region."""
    counter = [0]
    order = [plan.fan_aspect] + [a for a in FAN_ASPECTS if a != plan.fan_aspect]
    best = None
    best_aspect = plan.fan_aspect
    import time

    t_search = time.perf_counter()
    for aspect in order:
        found = _search_aspect(plan, sluice, seed, plot_across, aspect, tolerance, rounds, True, counter)
        if best is None or found[0] < best[0]:
            best, best_aspect = found, aspect
        if not found[0][0] and found[0][1] <= tolerance:
            break
    assert best is not None
    if best[0][0] or best[0][1] > tolerance:
        again = _search_aspect(plan, sluice, seed, plot_across, best_aspect, tolerance, rounds, False, counter)
        if again[0] < best[0]:
            best = again
    search_s = time.perf_counter() - t_search
    net, info = build(best[1], plan, plot_across, row_step, fan_middle)
    info["admissible"] = F_.fan_admissible(net, plan.down_deg, plan.ftpx, plan.target_acres)  # the built net judged, as today
    info["trials"] = counter[0]
    info["times"]["search"] = search_s
    return net, info
