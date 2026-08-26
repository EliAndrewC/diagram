"""Unit tests for where the runoff goes - the drain, the brook, the tameike (`hamletgen/sink.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math
from typing import Any, cast

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from ._builders import a_plan


def _with_drain(poly: list[tuple[float, float]]) -> Settlement:
    """The only thing `drain_heading` reads is the manifest, so the manifest is the whole fixture."""
    stub: Any = type("_S", (), {})()
    stub.M = {"field_ditches": [{"role": "drain", "field": "test-paddies", "poly": [list(p) for p in poly]}]}
    return cast(Settlement, stub)


def _bearing(v: tuple[float, float] | None) -> float:
    assert v is not None
    return math.degrees(math.atan2(v[1], v[0]))


def test_the_run_to_the_map_edge_is_measured_along_the_fall() -> None:
    plan = a_plan()  # falls due south
    assert hg.edge_run(plan, (500.0, plan.H - 300.0)) == pytest.approx(300.0)


def test_the_drain_heading_is_read_over_the_gates_span_not_the_final_vertex_pair() -> None:
    """A collector's LAST SEGMENT is noise, and reading the heading off it is what let cohort seed 2
    draw a brook 1,100 px uphill.

    `drainage_junction_smooth` measures the corner with `_flow_dir(..., span=40.0)` - it walks back
    up the collector until the chord is at least 40 px long. Here the collector runs due east and
    then hooks 2 px east, 4 px north at its outfall: the final pair reads -63.4 deg, the gate's span
    reads -5.4 deg. The placer must agree with the gate, or it optimizes a corner nobody measures."""
    heading = hg.drain_heading(_with_drain([(0.0, 0.0), (100.0, 0.0), (140.0, 0.0), (142.0, -4.0)]), "test-paddies")
    assert _bearing(heading) == pytest.approx(-5.44, abs=0.1), "the span bearing, over the last 40+ px"
    assert _bearing(heading) != pytest.approx(-63.4, abs=1.0), "NOT the final vertex pair's hook"


def test_a_collector_shorter_than_the_span_is_read_end_to_end() -> None:
    """The walk-back can run out of collector before it runs out of span, and then the whole ditch IS
    the chord - there is no shorter honest answer, and no reason to fall back to the noisy last pair."""
    heading = hg.drain_heading(_with_drain([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)]), "test-paddies")
    assert heading == pytest.approx((1.0, 0.0)), "due east, measured over the entire 20 px ditch"


def test_pond_setback_walks_past_blocked_probes() -> None:
    """An outfall INSIDE the field envelope blocks the first probes (every near rim point lands in
    the crop), so the walk must step outward (`d += step`) until the ellipse clears, and the
    returned distance carries the 12 px cushion past that first clear seat."""
    plan = a_plan()
    d = hg.pond_setback(plan, (700.0, 700.0), 60.0, 40.0)
    assert d > 40.0 + 46.0 + 14.0  # further than the first probe: the walk really stepped
    cx, cy = 700.0 + plan.fall[0] * d, 700.0 + plan.fall[1] * d
    assert hg.pond_clear_of_crop(plan, (cx, cy), 60.0, 40.0)


def test_a_pond_laid_over_the_crop_is_recognized() -> None:
    """The predicate `stage_sink` uses to check its own clamp: `pond_clear_of_field`'s two tests, on
    the same envelope, so the siting and the check cannot disagree."""
    plan = a_plan()
    assert hg.pond_clear_of_crop(plan, (700.0, 1400.0), 100.0, 60.0), "well below the field: clear"
    assert not hg.pond_clear_of_crop(plan, (700.0, 700.0), 100.0, 60.0), "sitting in the middle of it: not clear"
    assert not hg.pond_clear_of_crop(plan, (700.0, 1040.0), 100.0, 60.0), "rim overlapping the low edge: not clear"


@pytest.mark.parametrize(("down_deg", "start", "expect"), [(0.0, (500.0, 500.0), None), (180.0, (500.0, 500.0), 500.0), (90.0, (500.0, 500.0), None)])
def test_the_run_to_the_frame_is_measured_on_every_axis(down_deg, start, expect) -> None:  # type: ignore[no-untyped-def]
    """`edge_run` walks whichever axis the fall actually points along - east and west included, which
    the south-falling fixtures elsewhere in this file never exercise."""
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, down_deg=down_deg))
    run = hg.edge_run(plan, start)
    assert run > 0
    if expect is not None:
        assert run == pytest.approx(expect)


# ---- end to end ---------------------------------------------------------------------------------
