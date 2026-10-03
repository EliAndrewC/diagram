"""A comb fan's low ground and its water tint (feature 302): which plots are `low`, which are painted FLOODED.

`low` is the TOPOGRAPHY; `fill` is only the PICTURE (feature 010). The carve used to set both as it cut the closing rank - `low`
on the bottom two levels, FLOODED on a random 45% of the level whose bottom edge lies on the collector - and `close_seams`
re-judged the tint at its end against every plot's final ring. With the plots laid as a partition (`partition.py`) there is no
closing rank to cut, so both are set here from where each plot lies, and the re-judgment - moved here verbatim from
`seams/close.py`, its six clauses and its promotion - runs on the finished plots as it always did.

Research: tint plumbing - NONE: ring rounding for the needle test
"""

from __future__ import annotations

import math
import random
from typing import Any

from .banks import (
    _TINT_END_FT,
    _TINT_MAX_AREA_RATIO,
    _TINT_MAX_ASPECT,
    _TINT_MIN_APEX,
    _TINT_MIN_RECTANGULARITY,
    _TINT_MIN_SOLIDITY,
    dedup_ring,
    pointed_ring,
    tapers_to_a_point,
)
from .frame import Poly
from .palette import FLOODED, RICE_GREENS
from .ring_rules import needle

FLOOD_SAMPLE = 0.45
"""The share of the plots ON the collector drawn FLOODED, for texture - the carve's own figure (`_sector_closing_rank`).

Research: wet-paddy sample - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: each plot on the collector a 45% chance of the tint
"""

LOW_ROWS = 2
"""How many row steps from the collector count as low ground: the carve marked the bottom TWO levels (a wet backswamp with width,
not a one-plot hem - a calibrated liberty, see `apply_land_use`).

Research: low ground depth - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: plots within two row steps of the collector are low ground
"""


def _needle(poly: Poly) -> bool:
    """The flooded tint's needle rule on the ring AS RECORDED - `ring_rules.needle`, the test's own call, asked of the
    plot rounded to the manifest's 0.1 px (feature 287, T04), so the tint pass and the test judge one ring."""
    return needle([(round(float(q[0]), 1), round(float(q[1]), 1)) for q in poly])


def basin_rank(basin: Any, fill: float, median: float, collector: Any, plot_across: float) -> tuple[bool, float, float]:
    """How a compliant low plot ranks as THE flooded basin a map must exhibit - lower is better.

    First, whether it lies ON the collector (within a quarter of a plot's width): blue means the closing rank pooling before the
    outfall, and a promoted plot owes the same reading. Then how far it falls short of filling its own rectangle, which is what a
    leveled basin looks like. Then how far its size is from the median basin's, so the one blue plot on the sheet is not also
    its biggest. (Moved from `seams/close.py` `_basin_rank`.)

    Research: which plot is promoted - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: fronting the collector first, then the most rectangular, then nearest the median size
    """
    # ON the collector means FRONTING it, not touching it at a corner (settlement-review, feature 230 pass 11): Kashikawa's
    # promoted basin met the drain at one corner with a sliver and a wedge between it and the drain-side edge. A basin fronts
    # the drain when a real length of its boundary runs along it - a quarter of a plot's width.
    on = collector is not None and basin.buffer(0.25 * plot_across).intersection(collector).length >= 0.25 * plot_across
    size = abs(math.log(basin.area / median)) if median > 0.0 and basin.area > 0.0 else 0.0
    return (not on, round(1.0 - fill, 4), round(size, 4))


def mark_low(plots: list[dict[str, Any]], dpts: Poly, plot_across: float, row_step: tuple[float, float], R: random.Random) -> None:
    """`low` on every plot within `LOW_ROWS` row steps of the collector, and FLOODED on `FLOOD_SAMPLE` of those ON it (within a
    quarter of a plot's width) - the carve's two marks, set from where each plot lies rather than from the level it was cut in.

    Research:
        low ground - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: within LOW_ROWS row steps of the collector
        wet plots on the drain - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: FLOOD_SAMPLE of the plots within a quarter plot of the collector tinted
    """
    import shapely
    from shapely.geometry import LineString, Polygon

    if len(dpts) < 2 or not plots:
        return
    near = shapely.distance([Polygon(p["poly"]) for p in plots], LineString(dpts)).tolist()
    for p, d in zip(plots, near, strict=True):
        p["low"] = d <= LOW_ROWS * sum(row_step) / 2
        if d <= 0.25 * plot_across and R.random() < FLOOD_SAMPLE:
            p["fill"] = FLOODED


def judge_tint(plots: list[dict[str, Any]], dpts: Poly, plot_across: float, g: float) -> None:
    """Every FLOODED plot that would not read as a basin goes back to rice green; if none survives, the most basin-like compliant
    low plot is tinted. Moved verbatim from the end of `seams/close.py` `close_seams` - its comments carry the research and the
    defects each clause answers.

    Research:
        pointed plot left green - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a needle, a truncated point or an apex under 25 deg loses the tint
        tint reads as a basin - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: a lobed, channel-shaped, triangular, outsized or outfall plot loses the tint
        one wet plot at least - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: when none survives, the most basin-like low plot is tinted
    """
    import shapely
    from shapely.geometry import LineString, Polygon

    from .seams.geoms import ring_polygons

    # A POINTED SLIVER MUST NOT WEAR THE WATER TINT: a blue plot tapering to a needle reads as a tiny triangular pond at fit zoom,
    # not as a leveled basin. The replacement green is indexed by POSITION rather than drawn from R - the point is the ABSENT
    # DRAW (the stream stays put, so demoting one plot cannot re-roll the rest), not variety: `RICE_GREENS` holds one color
    # three times today. `low` is untouched, because it is the topography and the tint is only the picture (feature 010).
    # BOTH the raw ring and the deduped one, because the two carry different apexes and the gate judges the RAW one
    # (`flooded_plots_read_as_basins`, cohort seed 8). Testing both at the generous 25 deg keeps the placer strictly
    # stricter than the gate's 15.
    # THE FOURTH BLIND SPOT: EVERY PREDICATE MEASURES SHAPE, NONE MEASURES SIZE (feature 152 T10, settlement-review
    # 2026-08-29). Sawada's surviving flooded plot was 6,706 sq ft - 4.9x the median basin and the largest of 776 - on the one
    # map whose whole brief is that it has no pond. A basin far larger than its neighbors does not read as a basin whatever its
    # outline, so size joins the other four. Measured on the FINAL ring, which is the only place the size exists.
    # EACH PLOT'S SHAPE ONCE, AND ITS HULL AND MINIMUM RECTANGLE IN ONE ARRAY CALL EACH (feature 276, FR-004, plan D11/D12).
    _pgs = ring_polygons([_q["poly"] for _q in plots])
    _hull_areas = shapely.area(shapely.convex_hull(_pgs)).tolist() if _pgs else []
    _mrrs = list(shapely.minimum_rotated_rectangle(_pgs)) if _pgs else []
    _areas = sorted(_pg.area for _q, _pg in zip(plots, _pgs, strict=True) if len(_q.get("poly") or []) >= 3)
    _median_plot = _areas[len(_areas) // 2] if _areas else 0.0
    _keeps: list[tuple[tuple[bool, float, float], dict[str, Any]]] = []
    _collector = LineString(dpts) if len(dpts) >= 2 else None
    _to_collector = shapely.distance(_pgs, _collector).tolist() if _collector is not None and _pgs else []  # every plot's, in one call
    for _k, p in enumerate(plots):
        # THE RULE ITSELF FIRST, AS THE TEST READS IT (feature 287, FR-003, water W20): `ring_rules.needle` on the RAW ring as
        # the manifest records it (rounded to 0.1 px). THEN TWO MORE RINGS: the deduplicated ring at 25 deg is the placer's
        # margin over the rule (cohort seed 8), and the end-collapsed clause catches a needle truncated a few feet short of its
        # point, which no interior angle on the 1.0 ring reports.
        # A THIRD CLAUSE MEASURES SHAPE RATHER THAN TAPER: a blunt-cornered LOBE (Sawada's 0.731-solidity flooded plot read as an
        # arrowhead pond; see `_TINT_MIN_SOLIDITY`). Blue has to mean "a leveled basin pooling on the collector".
        # A FOURTH MEASURES SITING: THE OUTFALL, NOT THE WHOLE DRAIN. Blue lying ALONG the collector is the rule working; only
        # the terminus is ambiguous (Sawada's blue basin fused with the brook's head, settlement-review 2026-08-18), and the
        # keep-out is one and a half plot widths of it, measured TO THE PLOT'S NEAREST CORNER, NOT ITS CENTROID (feature 145).
        # A FIFTH MEASURES PROPORTION: a long parallel-sided wedge in blue reads as a channel (see `_TINT_MAX_ASPECT`).
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
            _keeps.append((basin_rank(_pg, _fill, _median_plot, _collector, plot_across), p))
    # THE MAP MUST STILL EXHIBIT THE CLASS IT DECLARES (feature 230). The tint is a SAMPLE, and every draw can be taken back by
    # the clauses above - which is how the reference hamlet once came to paint no blue plot at all; `flooded_plots` is the
    # record the interactive page's wet-paddy class reads. So when the sample comes back empty, the most BASIN-LIKE compliant
    # plot on the low ground is tinted (not the largest: settlement-review pass 10 - see `basin_rank`). It takes NO draw from R,
    # so promoting one plot cannot re-roll another, and on a roll whose sample survived this does nothing at all.
    if _keeps and not any(_p.get("fill") == FLOODED for _p in plots):
        _keeps.sort(key=lambda _a: (_a[0], round(_a[1]["poly"][0][0], 1), round(_a[1]["poly"][0][1], 1)))
        _keeps[0][1]["fill"] = FLOODED
