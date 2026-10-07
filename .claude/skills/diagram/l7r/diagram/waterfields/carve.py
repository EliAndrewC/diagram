"""The comb's sector bounds and its dry hem: `_bnd` and `_root_f` - where a sector's two threads run at a given fall, which the
partition's lattice is drawn between (`partition.py`, feature 302) - then `_dry_fields`, the dry-crop hem tiling, and
`_bund_beans`, the azemame bead accents.

Feature 302 retired the plot carve that lived here (`_carve`, one `_carve_sector` per thread pair and its supply-bank and drain
guards, `sector_rows.py`, the `_hem_pass`): the plots are laid as a partition of the planted region, so nothing cuts quads and
leaves ground for a repair.

Research: sector bounds - NONE: where a thread runs at a given fall, and its root fall
"""

import math
import random
from collections.abc import Callable, Sequence
from typing import Any

from .banks import StrokeIndex, polyline_cum
from .frame import CANAL_BERM_FT, Poly, Pt, _at_f, _Frame, _miter_normals, _pip, _seg_d, _Thread, taper_w
from .furrows import TRACT_PLOT_TURN_RAD, tract_ways
from .palette import DRY_CROPS


def _bnd(t: _Thread, f: float, F: _Frame) -> Pt:
    """Where thread `t` runs at fall `f`, down to its own end: its parent's path above its takeoff, else its own course (the
    sector a partition's lattice is drawn between). Past its end the partition runs the bound straight down the fall itself
    (`partition.Sectors.bound`); the carve's bound along the collector's bank went with the carve (feature 302)."""
    if f < t.f0 and t.fallback is not None:
        fb = t.fallback
        return _at_f(F, fb if isinstance(fb, list) else fb.pts, f)
    return _at_f(F, t.pts, f)


def _root_f(t: _Thread, F: _Frame) -> float:
    while isinstance(t.fallback, _Thread):
        t = t.fallback
    if isinstance(t.fallback, list):
        return min(t.f0, F.to_uf(*t.fallback[0])[1])
    return t.f0


def _dry_fields(
    R: random.Random,
    F: _Frame,
    a_pts: Poly,
    W: float,
    H: float,
    keepout: Sequence[tuple[float, float, float]],
    plot: float = 46,
    band: tuple[float, float] = (70, 132),
    g: float = 1.0,
    furrow_spread: float = 1.1,
    grain_drift: float = 0.0,
    supply: Sequence[dict[str, Any]] = (),
    tract0: int = 0,
) -> list[dict[str, Any]]:
    """DRY FIELDS (hatake) on the UPSLOPE margin the irrigation cannot command - the band just ABOVE the
    supply canal. Grain and pulses (barley/wheat, millet, buckwheat, field soy) in an irregular PATCHWORK of
    ridge-cultivated plots. Crop is assigned per-PLOT (not per-column) with spatial coherence - historical
    holdings were fragmented, so adjacent small plots carry different crops. To scale (1px=2ft): plot outlines
    are real, furrows stylised.

    The plots are RECTANGLES laid out AGAINST THE CANAL THEY BORDER - one edge runs ALONG the supply canal,
    the other PERPENDICULAR to it, extending upslope. They are NOT oriented to the paddy's fall grid (that gave
    a pronounced ~43deg shear, since the canal runs diagonally to the fall). The base edge rides the canal
    itself, and each shared boundary point is offset along ONE mitred normal (`_miter_normals`), so adjacent
    columns share every seam as a single straight line - no gap wedge or lap where the canal bends. Only the
    UPSLOPE (outer) edge is ragged - a per-column depth, stepping along the shared seam lines. The base dips
    slightly BELOW the canal so it tucks under the paddy (drawn after). `band` = (min, max) upslope depth in
    px: a THIN fringe (default) for a water-rich valley floor.

    FURROWS run along the CONTOUR (perpendicular to the fall), the traditional ridge-along-contour that dams
    rain and checks runoff - or down to the outfall, set TRACT BY TRACT (`tract_ways`); `theta` per plot, and `tract`
    numbered from `tract0`, so a caller laying a second band keeps its tracts apart from the first.

    Research:
        dry plot size - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: 46 grain px along the canal (x0.9-1.25) by 36 grain px a row, about 92 by 72 ft on a village map
        squared to the canal - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: each plot a rectangle square to the canal, neighbors sharing every seam
        behind a bare bank - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html, research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html: the hem starts CANAL_BERM_FT past the stroke's local bank
        hem depth - UNRESEARCHED: a ragged outer edge, each column `band` px deep from the canal line
        crop per plot - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: one of four crops
        neighbor keeps the crop - UNRESEARCHED: a plot keeps the last plot's crop with a 55% chance, about 0.66 once a re-roll lands on the same crop
        row direction - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: each column's tract heading, each plot turned up to TRACT_PLOT_TURN_RAD
        off the water and the frame - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.drawing.html, research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: held at 0.5 px of a supply stroke's painted edge, short of the page's bank (its half-width plus `CANAL_BERM_FT`) - at the bank the freed ground re-lays Inashiro's toe marsh with a sharp corner on open ground; the found row waterfields/carve.py::_dry_fields#a hem that keeps its ground inside the berm
        keep-out and frame margin - NONE: a cell in a keep-out or within 12 px of the frame is dropped
    """
    plots = []
    plot = plot * g  # the along-canal parcel width and the 36px row depth below are REAL-FEET
    # quantities tuned at the village grain (1px = 2ft; ~1 mu strips per Buck) - unscaled at a
    # coarser grain every hem parcel doubled in area, dry cells dwarfing the rice plots beside
    # them ("a number of pixels, not a number of feet" - the GM's catch, 2026-07-21; gated by
    # dry_plots_to_scale)
    theta0 = math.atan2(F.c[1], F.c[0]) + math.radians(grain_drift)  # contour heading (ridges follow it), drifted off the fall-line by the grain_drift knob (feature 005)

    def blocked(x: float, y: float) -> bool:
        return any((x - cx) ** 2 + (y - cy) ** 2 < rr * rr for (cx, cy, rr) in keepout)

    # tile the plots ALONG the canal by ARC-LENGTH (shared boundaries -> a contiguous margin), jittered widths
    seglen = [math.dist(a_pts[i], a_pts[i + 1]) for i in range(len(a_pts) - 1)]
    total = sum(seglen)

    def at(s: float) -> Pt:  # point on the canal polyline at arc-length s
        acc = 0.0
        for i, sl in enumerate(seglen):
            if acc + sl >= s or i == len(seglen) - 1:
                t = (s - acc) / sl if sl else 0.0
                ax, ay = a_pts[i]
                bx, by = a_pts[i + 1]
                return (ax + (bx - ax) * t, ay + (by - ay) * t)
            acc += sl
        # UNREACHABLE for a real (non-empty) canal, and kept to satisfy the type: the loop above returns
        # on `i == len(seglen) - 1` whatever arc-length is asked for, so the only way past it is a canal
        # with no segments at all - and a fan with no supply canal never carves (feature 146).
        return a_pts[-1]

    bounds = [0.0]
    while bounds[-1] < total - plot * 0.6:
        bounds.append(bounds[-1] + plot * R.uniform(0.9, 1.25))
    bounds[-1] = total
    if g != 1.0 and len(bounds) >= 2 and bounds[-1] - bounds[-2] > 1.35 * plot:
        # the snap-to-total stretch can hand the END cell up to ~1.85 plot widths (a ~0.38-acre
        # slab at city grain - the largest-parcel outlier, 2026-07-21); split it. Coarse grains
        # only: the vetted village maps carry the same (milder, in-band) artifact byte-stably.
        bounds.insert(-1, (bounds[-1] + bounds[-2]) / 2)

    # THE ROW DIRECTION IS SET TRACT BY TRACT (269 B06; research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html, 0006). The land set the direction: a run of neighboring plots on one lie of ground
    # shares one row direction, turned a few degrees from plot to plot, and the direction changes at the seam between
    # tracts, by as much as a right angle - along the contour or down to the outfall, never straight down a steep slope.
    # The seams, not every plot boundary, are what read the family strips apart. This replaced a per-plot rule that
    # seated each plot's angle in the widest gap between its neighbors': it forbade the neighbors that share a
    # direction, which the record makes the common case. `tract_ways` rolls each tract's heading.
    tracts = tract_ways(R, len(bounds) - 1, theta0, furrow_spread)
    prev_crop = R.choice(list(DRY_CROPS))
    # THE BERM IS MEASURED FROM THE CANAL'S BANK, NOT ITS CENTERLINE (settlement-review 2026-08-17).
    # This used to be a flat `8 * g` from the centerline, which silently bundled the canal's own
    # half-width into the stand-off - so when the net went to TRUE SIZE the water shrank threefold and
    # the bare stripe GREW, leaving a canal running hard against the paddy on one side with a ~15 ft
    # empty verge on the other. `CANAL_BERM_FT` is now the berm itself (spoil bank + room to stand for
    # the annual dredging), added to the stroke's LOCAL half-width where each boundary point sits, via
    # the same `supply_bank_clearance` the carve and the gate already share. Derive, never pin.
    berm_px = CANAL_BERM_FT * g / 2.0  # grain is 2 / ftpx, so ft * g / 2 is ft in pixels
    _hem_reach = 8 * g  # where `band` is measured OUTWARD from - the legacy offset off the canal line, deliberately unchanged so the hem's outer edge stays put (see the o_near/o_far note below)
    _sup = []
    for _c in supply:
        _sp = [(float(p[0]), float(p[1])) for p in _c.get("pts") or ()]
        if len(_sp) < 2:
            continue
        _w0, _w1 = float(_c["w"]), float(_c.get("w_tail", _c["w"]))  # pyrefly: ignore[bad-argument-type]  # dict.get(k, Any-default) typed Any|None by pyrefly, Any by mypy - research 142 R5
        _reach = max(_w0, _w1) / 2 + berm_px + 2.0  # bbox prefilter: prunes only, never decides
        _scum = polyline_cum(_sp)
        _sup.append(
            (
                _sp,
                _w0,
                _w1,
                _scum,
                (min(p[0] for p in _sp) - _reach, min(p[1] for p in _sp) - _reach, max(p[0] for p in _sp) + _reach, max(p[1] for p in _sp) + _reach),
                StrokeIndex(_sp, _w0, _w1, _scum, _reach),
            )
        )

    def _bank(q: Pt) -> tuple[float, float]:
        """`(gap, halfw)` against the NEAREST supply stroke at `q` - distance to its centerline and
        half its drawn width there. `(1e9, 0.0)` where no stroke governs the point."""
        best: tuple[float, float] | None = None
        past_best: tuple[float, float] | None = None
        for _pts, _w0, _w1, _cum, _bb, _sidx in _sup:
            if not (_bb[0] <= q[0] <= _bb[2] and _bb[1] <= q[1] <= _bb[3]):
                continue
            gap, halfw, past, _foot, _nrm = _sidx.clearance(q)  # the indexed walk (feature 220): the same tuple `supply_bank_clearance` returns
            if past:
                if past_best is None or gap < past_best[0]:
                    past_best = (gap, halfw)
                continue
            if best is None or gap < best[0]:
                best = (gap, halfw)
        # `past` means "this ground is beyond MY ends, so some other stroke governs it" - an
        # assumption that holds along a run and FAILS AT A JUNCTION, where the pieces meet end to end
        # and every one of them reports past. Returning nothing there gave the hem no berm at all at
        # the bunsuiguchi, which is precisely where the defect this berm exists to fix lives: a hem
        # corner shipped 0.70 ft off the head-race's painted bank against an intended 5.0
        # (settlement-review 2026-08-17, which replayed this predicate on the shipped geometry to
        # prove the guard should have caught it). So when NOTHING governs the point, fall back to the
        # nearest stroke that merely ends near it rather than pretending there is no water.
        return best or past_best or (1e9, 0.0)

    bpts = [at(b) for b in bounds]

    # ONE berm per BOUNDARY POINT, so adjacent columns still share each seam as a single straight
    # line (the invariant `_miter_normals` exists for) even though the stand-off now varies along the
    # canal as the canal tapers.
    def _in_berm(q: Pt) -> bool:
        """Is `q` ON a supply canal's bank - i.e. effectively in the water?

        0.5 px, the same margin `_quad_in_supply` uses, and deliberately NOT a fraction of
        `CANAL_BERM_FT`. The berm above is a stand-off measured at a BOUNDARY POINT, against THAT
        point's own canal, along that point's normal. This re-measures anywhere on the cell, against
        whichever stroke happens to be NEAREST, by true perpendicular distance. Those are different
        questions, so this is a FLOOR under the berm rule and never a restatement of it - and a floor
        has to be sized to the defect it catches, not inherited from the rule it backstops.

        THREE SETTINGS WERE TRIED, ALL MEASURED, because each one that was too generous cost
        something real - and every cost arrived by the same route, FREED GROUND:

          - the FULL berm collapsed the hem, 23 cells -> 8 on Inashiro;
          - HALF wiped 347 px off the fork triangle's west reach, and the ground it freed re-packed
            the wells until one stood 84 px out holding the map's frame open (cohort seed 4);
          - a QUARTER still dropped four cells on cohort seed 41, whose wells moved the same way and
            broke the 4-of-4 ratchet in `tests/hamletgen/test_driver.py`.

        At 0.5 px it drops only ground genuinely in the water - which is all that was ever wrong (two
        corners at the bunsuiguchi stood 0.2 ft off the head-race's bank against an intended 5.0) -
        while still clearing the `dry_plots`/`field_ditches` overlaps that testing CORNERS ALONE let
        through on three cohort seeds. **A guard that DELETES a map feature hands its footprint to
        the next placer, so its blast radius is never confined to the thing it deletes.**"""
        gap, halfw = _bank(q)
        return gap - halfw < 0.5  # HELD (feature 328 wave 10): at the page's berm Inashiro's toe marsh took a sharp corner on open ground

    def _quad_in_berm(quad: Poly) -> bool:
        """Corners AND every edge, at a 3 px step. A cell can keep four dry corners while an EDGE
        crosses a stroke between them - the same trap `_quad_in_supply` documents for the paddy
        carve, and testing corners alone shipped `dry_plots`/`field_ditches` overlaps on three of
        twenty-four cohort seeds before this was widened (2026-08-17)."""
        for i in range(len(quad)):
            a, b = quad[i], quad[(i + 1) % len(quad)]
            n = max(1, int(math.dist(a, b) / 3.0))
            for k in range(n + 1):
                t = k / n
                if _in_berm((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))):
                    return True
        return False

    berms = [_bank(p)[1] + berm_px for p in bpts]
    bnorm = _miter_normals(bpts, F)  # ONE shared upslope normal per boundary point - see its WHY
    for i in range(len(bounds) - 1):
        pL, pR = bpts[i], bpts[i + 1]
        (nLx, nLy), (nRx, nRy) = bnorm[i], bnorm[i + 1]
        depth = R.uniform(*band)  # ragged outer edge (per-column depth)
        outer = _hem_reach + depth  # the band's OUTER edge, measured from the canal line as always
        # Rows keep their ~36g depth, so a hem that starts nearer the water gains a ROW rather than
        # stretching its parcels - `dry_plots_to_scale` judges parcel size, not band depth.
        nrow = max(1, round((outer - (berms[i] + berms[i + 1]) / 2) / (36 * g)))
        for k in range(nrow):
            # per-plot crop with coherence: usually keep the last crop (holdings cluster), sometimes switch
            if R.random() < 0.45:
                prev_crop = R.choice(list(DRY_CROPS))
            crop = prev_crop
            fill, furrow = DRY_CROPS[crop]
            # PERPENDICULAR offset from the canal (both edges UPSLOPE of it): near = canal side, far = upslope.
            # The whole plot stays on the DRY side - it never dips across the canal onto the wet paddy.
            # THE BERM MOVES THE HEM'S INNER EDGE ONLY - its OUTER reach is unchanged. `band` has
            # always measured outward from the canal LINE, and it still does (`_hem_reach`); the berm
            # decides where the hem STARTS. So narrowing the verge gives the HEM the recovered ground
            # rather than giving the MAP an empty strip - which matters because a strip of newly-open
            # ground is something the placers downstream will wander into: an earlier draft that let
            # the outer edge move in with the inner one re-packed the wells on two cohort maps and
            # left one of them (Cohort-41) with a well 66 px out, holding the whole frame open.
            bL, bR = berms[i], berms[i + 1]
            o_nL, o_fL = bL + (outer - bL) * k / nrow, bL + (outer - bL) * (k + 1) / nrow
            o_nR, o_fR = bR + (outer - bR) * k / nrow, bR + (outer - bR) * (k + 1) / nrow
            quad = [(pL[0] + nLx * o_fL, pL[1] + nLy * o_fL), (pR[0] + nRx * o_fR, pR[1] + nRy * o_fR), (pR[0] + nRx * o_nR, pR[1] + nRy * o_nR), (pL[0] + nLx * o_nL, pL[1] + nLy * o_nL)]
            cx = sum(p[0] for p in quad) / 4
            cy = sum(p[1] for p in quad) / 4
            if any(p[0] < 12 or p[0] > W - 12 or p[1] < 12 or p[1] > H - 12 for p in quad):
                continue
            if blocked(cx, cy):
                continue
            # ...AND NO CORNER SITS IN A CANAL'S BERM. The stand-off above is applied along THIS
            # canal's normal, which does not clear a stroke running at a different angle - at the
            # bunsuiguchi the hem's first cells are offset from canal A while the wider head-race
            # passes beside them, and two corners came out 0.2 ft off its bank (measured on Inashiro,
            # 2026-08-17). Dropping the cell keeps the shared-seam invariant that pulling the vertex
            # back would break, and the hem is a patchwork of family strips where a missing cell at
            # the fork reads as ordinary.
            if _quad_in_berm(quad):
                continue
            tract, heading = tracts[i]
            theta = heading + R.uniform(-TRACT_PLOT_TURN_RAD, TRACT_PLOT_TURN_RAD)  # the few degrees a plot turns within its tract
            plots.append({"poly": [(round(p[0], 1), round(p[1], 1)) for p in quad], "crop": crop, "fill": fill, "furrow": furrow, "theta": round(theta, 3), "tract": tract0 + tract})
    return plots


MIN_BEADS_PER_RUN = 2
"""Research: two beads at least - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a stretch of bund that carries beans shows at least two beads"""
# A BEADED BUND SEGMENT SHOWS AT LEAST TWO BEADS (GM 2026-09-14, feature 247: "On any segment of earthen
# bunds which has bund beans, I would like at least 2 glyphs. I currently see some segments with only 1
# glyph."). A rendering convention only - the beans are sub-pixel and the beads stand for them - so the
# number claims nothing physical; one bead does not read as a row of anything. The forms priced, and the
# one taken, are in specs/247-two-beads-per-bund/research.md R2.


def bead_runs(line: Poly, alive: Callable[[Pt], bool]) -> list[Poly]:
    """Split one edge's line of beads at every bead `alive` rejects and keep each contiguous part of
    MIN_BEADS_PER_RUN or more - the one place the two-bead rule lives, used by `_bund_beans` for the
    plot-burial and ditch-net drops and by the draw site (settlement/fields/comb.py) for the pond and
    recorded-ditch drops. A part left with a single bead loses it: nothing can be laid where the drop was
    (that ground is painted over or under water), so on that segment the rule is met only by removal.
    SPLIT rather than counted, because a dropped MIDDLE bead leaves one bead each side of a painted-over
    stretch - two segments of one glyph each, which is exactly what the GM saw.

    Research: bead runs - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a run left with one bead loses it
    """
    runs: list[Poly] = []
    part: Poly = []
    for q in line:
        if alive(q):
            part.append(q)
        elif part:
            runs.append(part)
            part = []
    if part:
        runs.append(part)
    return [r for r in runs if len(r) >= MIN_BEADS_PER_RUN]


def _bund_beans(R: random.Random, plots: list[dict[str, Any]], frac: float, spacing: float = 9.5, tol: float = 1.0, channels: list[dict[str, Any]] | None = None) -> list[Poly]:
    """AZEMAME (bund soybeans): sub-pixel at 1px=2ft, so drawn symbolically as a green BEAD
    line along a fraction of the paddy bunds. Returns bead RUNS - each a contiguous line of two or
    more bead center points along one plot edge (`bead_runs`, feature 247); the caller draws small
    BEAN_GREEN dots. ~`frac` of plots carry beaded bunds (not every bund had beans).

    A bead is DROPPED when a plot drawn LATER than its host buries it deeper than `tol` px
    (GM 2026-08-15, on Inashiro: green dots scattered mid-paddy). `_fill_wedges`' fillers
    deliberately lap up to ~12 real ft onto a neighbor and paint last - the lapped stretch of
    the neighbor's bund stroke is not visible ground on the finished map, so a bead line laid
    along it surfaces as dots floating in the filler's water. Beads must land on the bunds the
    finished paint actually shows, so each bead is tested against the plots that paint after
    its host and dropped when buried. `tol` is bead-scale rather than bund-scale: a bead
    within ~its own 1.4px drawn radius of the burying plot's edge still reads as sitting on
    that plot's seam. The gate mirrors this at double the tolerance (bund_beans_on_bunds), so
    a bead this filter allows cannot false-fire there through manifest rounding. The filter
    runs after all draws from R, so dropping beads never ripples the RNG stream.

    `channels` extends the same honesty to the ditch net (GM 2026-08-15, second pass): the net's
    strokes draw LATE - over every plot and bead - so a bead within a stroke's local half-width
    (tapering w -> w_tail along the run) + tol is buried under water paint and dropped. Pond
    burial is filtered at the draw site (draw_comb_field), where the pond geometry lives.

    Research:
        beaded bunds - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a single row of beads along one or two edges of about `frac` of the plots
        bead spacing - CONVENTION: a symbolic bead every 9.5 px
        two beads at least - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: an edge of two to three spacings carrying two beads at its thirds
        buried beads dropped - CONVENTION: a bead under a later plot's paint or a ditch's stroke is not drawn
    """
    runs: list[Poly] = []
    boxes = [(min(q[0] for q in p["poly"]), min(q[1] for q in p["poly"]), max(q[0] for q in p["poly"]), max(q[1] for q in p["poly"])) for p in plots]

    def buried(x: float, y: float, host: int) -> bool:
        for j in range(host + 1, len(plots)):
            bx0, by0, bx1, by1 = boxes[j]
            if not (bx0 - tol <= x <= bx1 + tol and by0 - tol <= y <= by1 + tol):
                continue
            poly = plots[j]["poly"]
            if _pip(x, y, poly) and min(_seg_d(x, y, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))) > tol:
                return True
        return False

    chans = []
    for c in channels or []:
        cpts = c["pts"]
        if len(cpts) < 2:
            continue
        cum = polyline_cum(cpts)
        pad = max(c["w"], c.get("w_tail", c["w"])) / 2 + tol  # pyrefly: ignore[unsupported-operation, bad-specialization]  # dict.get(k, Any-default) typed Any|None by pyrefly, Any by mypy - research 142 R5
        cbox = (min(q[0] for q in cpts) - pad, min(q[1] for q in cpts) - pad, max(q[0] for q in cpts) + pad, max(q[1] for q in cpts) + pad)
        chans.append((cpts, cum, cum[-1] or 1.0, c["w"], c.get("w_tail", c["w"]), cbox))

    def wet(x: float, y: float) -> bool:
        for cpts, cum, tot, w0, w1, (bx0, by0, bx1, by1) in chans:
            if not (bx0 <= x <= bx1 and by0 <= y <= by1):
                continue
            for i in range(len(cpts) - 1):
                # taper measured at the segment head - within one segment it moves less than tol
                if _seg_d(x, y, cpts[i], cpts[i + 1]) < taper_w(w0, w1, cum[i] / tot) / 2 + tol:  # pyrefly: ignore[bad-argument-type]  # dict.get(k, Any-default) typed Any|None by pyrefly, Any by mypy - research 142 R5
                    return True
        return False

    for pi, p in enumerate(plots):
        if R.random() > frac:
            continue
        poly = p["poly"]
        order = list(range(len(poly)))
        R.shuffle(order)
        for ei in order[: R.randint(1, 2)]:
            a = poly[ei]
            b = poly[(ei + 1) % len(poly)]
            nd = int(math.dist(a, b) / spacing)
            # AN EDGE OF TWO TO THREE SPACINGS CARRIES TWO BEADS AT ITS THIRDS (feature 247). Laid at the
            # spacing with the corners empty it carried exactly one - the single glyph the GM saw; under
            # two spacings it carries none, as before, and at three or more the spacing is untouched. The
            # other forms - lay nothing on a short edge (a visible loss of beaned bunds the GM did not ask
            # for), or pass it over for a longer edge of the plot (beans on bunds that carry none) - are
            # declined in research R2. The count is fixed AFTER the draws above and the drops below run
            # after all draws, so the random stream is the same as before the rule (R3).
            if nd == 2:
                nd = 3
            line = [(round(a[0] + t / nd * (b[0] - a[0]), 1), round(a[1] + t / nd * (b[1] - a[1]), 1)) for t in range(1, nd)]
            runs += bead_runs(line, lambda q, pi=pi: not buried(q[0], q[1], pi) and not wet(q[0], q[1]))
    return runs
