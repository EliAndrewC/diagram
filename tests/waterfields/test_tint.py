"""`waterfields/tint.py` (feature 302): the low ground and the water tint - moved from the end of `close_seams`, its tests with it.

The collector runs along y = 1300 throughout (`_D`), as it did in the seam pass's own tests of the tint.
"""

from __future__ import annotations

import random

from l7r.diagram.waterfields import tint
from l7r.diagram.waterfields.banks import dedup_ring
from l7r.diagram.waterfields.palette import FLOODED

_D = [(100.0, 1300.0), (1300.0, 1300.0)]
GREEN = "#A6C398"


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def test_a_map_whose_blue_sample_is_all_demoted_still_exhibits_one_flooded_basin() -> None:
    """The flooded tint is a random sample that the tint clauses can take back entirely - the reference hamlet once shipped no
    blue plot at all. When nothing survives, the most BASIN-LIKE compliant low plot is tinted, preferring one on the collector,
    taking no draw from R; when something survives, nothing is promoted."""
    far, on = _rect(300, 300, 346, 330), _rect(600, 1266, 640, 1292)
    plots = [{"poly": far, "fill": GREEN, "low": True}, {"poly": on, "fill": GREEN, "low": True}, {"poly": _rect(300, 700, 346, 730), "fill": GREEN}]
    tint.judge_tint(plots, _D, 46.0, 2.0)
    flooded = [p for p in plots if p["fill"] == FLOODED]
    assert len(flooded) == 1, "exactly one basin is promoted when the sample left none"
    assert min(q[1] for q in flooded[0]["poly"]) > 1200, "and it is the one on the collector, as the carve's own blue always was"

    kept = [{"poly": far, "fill": GREEN, "low": True}, {"poly": on, "fill": FLOODED, "low": True}]
    tint.judge_tint(kept, _D, 46.0, 2.0)
    assert [min(q[1] for q in p["poly"]) > 1200 for p in kept if p["fill"] == FLOODED] == [True], "a surviving draw is left alone"


def test_the_tint_judges_the_flooded_needle_on_the_ring_the_test_reads() -> None:
    """Feature 287 T04 (water W20): the tint and the test read ONE predicate, `ring_rules.needle` on the ring as recorded: a
    basin with a hairline spur - blunt on the deduplicated ring at 25 deg, a needle under 15 deg raw - is a needle to both."""
    from l7r.diagram.waterfields.banks import _TINT_MIN_APEX, pointed_ring
    from l7r.diagram.waterfields.ring_rules import needle

    spur = [(600.0, 1266.0), (620.0, 1266.0), (620.05, 1265.1), (620.2, 1266.0), (640.0, 1266.0), (640.0, 1292.0), (600.0, 1292.0)]
    assert needle(spur) and not pointed_ring(dedup_ring(spur, 1.0), _TINT_MIN_APEX), "the disagreement: a needle raw, blunt deduplicated"
    assert tint._needle(spur), "the tint sees the needle the test sees"
    assert not tint._needle(_rect(600, 1266, 640, 1292))
    flat = [(600.0, 1266.0), (620.0, 1266.0), (620.004, 1265.96), (620.008, 1266.0), (640.0, 1266.0), (640.0, 1292.0), (600.0, 1292.0)]
    assert needle(flat) and not tint._needle(flat), "judged AS RECORDED: a spur the 0.1 px rounding flattens is no needle"


def test_only_a_pointed_shape_loses_the_water_tint() -> None:
    """0007 drawing (feature 328 wave 40): "Only the random draw, or a plot's pointed shape, left them untinted." A triangle whose
    sharpest corner is about 35 degrees keeps its tint (the fill clause that demoted it was on no page); one tapering to a
    15 degree point, under `_TINT_MIN_APEX`, loses it."""
    blunt = [{"poly": [(600.0, 1292.0), (660.0, 1292.0), (600.0, 1250.0)], "fill": FLOODED, "low": True}]
    tint.judge_tint(blunt, _D, 46.0, 2.0)
    assert blunt[0]["fill"] == FLOODED
    sharp = [{"poly": [(600.0, 1292.0), (700.0, 1292.0), (600.0, 1265.0)], "fill": FLOODED, "low": True}]
    tint.judge_tint(sharp, _D, 46.0, 2.0)
    assert sharp[0]["fill"] != FLOODED


def test_basin_rank_orders_on_the_collector_then_fill_then_size() -> None:
    from shapely.geometry import LineString, Polygon

    drain = LineString([(0.0, 100.0), (1000.0, 100.0)])
    sq = Polygon(_rect(0, 60, 40, 98))
    assert tint.basin_rank(sq, 1.0, 1520.0, drain, 48.0)[0] is False, "within a quarter plot of the drain is ON it"
    assert tint.basin_rank(Polygon(_rect(0, 0, 40, 38)), 1.0, 1520.0, drain, 48.0)[0] is True
    assert tint.basin_rank(sq, 0.9, 1520.0, drain, 48.0) > tint.basin_rank(sq, 1.0, 1520.0, drain, 48.0), "a fuller rectangle ranks first"
    assert tint.basin_rank(sq, 1.0, 1520.0, None, 48.0)[0] is True, "no collector to be on"
    assert tint.basin_rank(sq, 1.0, 0.0, drain, 48.0)[2] == 0.0, "no median, no size term"


def test_mark_low_flags_the_bottom_two_rows_and_samples_the_plots_on_the_collector() -> None:
    plots = [{"poly": _rect(600, 1266, 640, 1296), "fill": GREEN} for _ in range(40)]
    plots += [{"poly": _rect(600, 1230, 640, 1260), "fill": GREEN}, {"poly": _rect(600, 600, 640, 630), "fill": GREEN}]
    tint.mark_low(plots, _D, 48.0, (26.0, 36.0), random.Random(3))
    on, near, far = plots[:40], plots[40], plots[41]
    assert all(p["low"] for p in on) and near["low"] and not far["low"], "within two row steps of the collector is low ground"
    blue = sum(1 for p in on if p["fill"] == FLOODED)
    assert 0 < blue < 40, "a SAMPLE of the plots on the collector is drawn flooded"
    assert near["fill"] == GREEN and far["fill"] == GREEN, "only plots ON the collector are sampled"


def test_mark_low_and_judge_tint_do_nothing_without_a_collector_or_plots() -> None:
    plots = [{"poly": _rect(0, 0, 10, 10), "fill": GREEN}]
    tint.mark_low(plots, [(0.0, 0.0)], 48.0, (26.0, 36.0), random.Random(1))
    tint.mark_low([], _D, 48.0, (26.0, 36.0), random.Random(1))
    assert "low" not in plots[0]
    tint.judge_tint(plots, [], 48.0, 1.0)
    tint.judge_tint([], _D, 48.0, 1.0)
    assert plots[0]["fill"] == GREEN


def test_a_plot_at_the_drains_end_keeps_its_tint() -> None:
    """0007 drawing (feature 328 wave 40): only the draw or a pointed shape leaves a low plot green - the outfall's keep-out (no
    plot within one and a half plot widths of the drain's end) is on no page, and went."""
    plots = [{"poly": _rect(1260, 1262, 1300, 1298), "fill": FLOODED, "low": True}]
    tint.judge_tint(plots, _D, 46.0, 2.0)
    assert plots[0]["fill"] == FLOODED
