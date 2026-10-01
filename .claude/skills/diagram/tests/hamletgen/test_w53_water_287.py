"""Feature 287, water W53 at the hamlet's water stages: the sink's drain run and its tameike, and the intake's weir, each ask
the registry of what stands (the overlap matrix) before they are recorded - a route or a seat the matrix forbids is refused and
the next taken, and where none is left the refusal is by name. On constructed input including the violating case."""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.sink import SinkRefused
from l7r.diagram.overlap.registry import OverlapRefused
from l7r.diagram.settlement import Settlement

from ._builders import a_plan
from .test_sink import _u_field_stage


def _square(x0: float, y0: float, x1: float, y1: float) -> list[list[float]]:
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _strict(plan: hg.SitePlan) -> Settlement:
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.standing.strict = True
    return s


def test_a_drain_run_across_a_resting_basin_is_not_admitted_and_is_never_recorded() -> None:
    plan = a_plan()
    s = _strict(plan)
    s.M["fallow_patches"].append({"outline": _square(680.0, 1100.0, 720.0, 1140.0), "form": "rested_basin"})
    across, clear = [(700.0, 1010.0), (700.0, 1300.0)], [(800.0, 1010.0), (800.0, 1300.0)]
    assert not hg.sink.drain_admitted(s, across, "offmap") and hg.sink.drain_admitted(s, clear, "offmap")
    drawn = len(s.late_water) + len(s.water) + len(s.out)
    with pytest.raises(OverlapRefused):
        hg.sink.drain_run(s, across, "offmap")
    assert not s.M["channels"] and len(s.late_water) + len(s.water) + len(s.out) == drawn, "refused before its ink"
    hg.sink.drain_run(s, clear, "offmap")
    assert s.M["channels"][0] == hg.sink.drain_record(clear, "offmap")


def test_a_confluence_the_registry_refuses_sends_the_drain_off_the_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    """The drain joins the passing brook where one is in reach - unless its run to the brook lies on a resting basin; then the
    searched run off the frame is taken instead."""

    def roll(basin: bool) -> hg.SitePlan:
        plan = a_plan()
        plan.water_sink = "offmap"
        plan.brook = [(760.0, 900.0), (760.0, 1000.0), (760.0, 1100.0), (760.0, 1400.0), (760.0, 1700.0)]
        monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 1010.0))
        monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (0.0, 1.0))
        s = _strict(plan)
        if basin:
            s.M["fallow_patches"].append({"outline": _square(725.0, 1000.0, 755.0, 1300.0), "form": "rested_basin"})
        hg.sink.lay_sink(s, plan)
        assert all(s.admits("channels", c, ignore=c) for c in s.M["channels"])
        return plan

    assert roll(False).confluence is not None, "with nothing in the way the drain meets the brook"
    refused = roll(True)
    assert refused.confluence is None and refused.sink_brook, "the basin refuses the confluence: the drain leaves the frame"


def test_the_constructed_route_the_registry_refuses_is_refused_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    plan, drawn, _out = _u_field_stage(monkeypatch)
    monkeypatch.setattr(hg.sink, "drain_admitted", lambda s_, pts, to: False)
    with pytest.raises(SinkRefused, match="overlap matrix"):
        hg.sink.stage_sink(Settlement(W=plan.W, H=plan.H, seed=1), plan)
    assert drawn == [], "no searched route and no constructed one is drawn"


def test_a_tameike_or_its_run_the_registry_refuses_sends_the_drain_off_the_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = a_plan()
    plan.water_sink = "pond"
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 1010.0))
    monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (0.0, 1.0))
    monkeypatch.setattr(hg.sink, "drain_admitted", lambda s_, pts, to: to != "pond")
    real = hg.sink.lay_sink
    reentered: list[str] = []
    monkeypatch.setattr(hg.sink, "lay_sink", lambda s_, plan_: reentered.append(plan_.water_sink))
    s = _strict(plan)
    real(s, plan)
    assert reentered == ["offmap"] and not s.M.get("pond"), "no pond, and the stage re-enters as an off-map sink"


def test_the_weir_walks_past_a_seat_on_dry_ground_and_is_refused_by_name_where_its_leg_holds_none() -> None:
    """A bar is mounted on water alone. Its first seat below the mouth is put under a dry plot: the bar steps on down the brook
    to the first seat the registry admits. With the whole leg under dry crop no seat is left, and the weir is refused."""

    def intake(plots: list[list[list[float]]]) -> Settlement:
        plan = a_plan()
        plan.intake = "weir"
        plan.brook = [(700.0, 100.0), (700.0, 300.0), (700.0, 600.0)]
        s = _strict(plan)
        for p in plots:
            s.M["dry_plots"].append({"poly": p})
        hg.draw_intake(s, plan, (700.0, 300.0))
        return s

    first = intake([]).M["weirs"][0]
    xs, ys = [q[0] for q in first["poly"]], [q[1] for q in first["poly"]]
    s = intake([_square(max(xs) - 2.0, min(ys) - 4.0, max(xs) + 20.0, max(ys) + 4.0)])
    moved = s.M["weirs"][0]
    assert moved["y"] > first["y"] and s.admits("weirs", moved, ignore=moved), "stepped down past the dry plot"
    with pytest.raises(OverlapRefused):
        intake([_square(600.0, 300.0, 800.0, 700.0)])
