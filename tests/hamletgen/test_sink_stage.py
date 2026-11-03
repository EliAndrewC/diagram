"""The sink's thin seam (`hamletgen/sink_stage.py`, feature 444 T26 D1): what it gathers, what it refuses by name, and what it
writes from the Rust stage's records. The rules themselves are the crate's tests (`rust/phases/src/sink/tests.rs`)."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram.hamletgen import sink_stage
from l7r.diagram.settlement import Settlement

from ._builders import a_plan


def _settled(plan: Any) -> Settlement:
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M.setdefault("field_ditches", []).append({"field": "test-paddies", "role": "drain", "poly": [[500.0, 990.0], [700.0, 990.0]]})
    return s


def test_a_field_with_no_collector_lays_no_sink_and_records_the_sink_as_rolled() -> None:
    plan = a_plan(10)
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    sink_stage.stage_sink(s, plan)
    assert s.M["meta"]["water_sink"] == plan.water_sink
    assert not s.M.get("pond")


def test_a_collector_beside_a_dike_is_refused_by_name() -> None:
    plan = a_plan(10)
    s = _settled(plan)
    s.M["dikes"] = [{"crest": [[0.0, 0.0], [10.0, 0.0]]}]
    with pytest.raises(sink_stage.SinkRefused, match="beside a dike"):
        sink_stage.stage_sink(s, plan)


def test_a_route_the_rust_stage_refuses_is_refused_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = a_plan(10)
    s = _settled(plan)

    class Refusing:
        def stage_sink(self, *_a: Any) -> None:
            raise ValueError("the drain's constructed route crosses a resting basin")

    monkeypatch.setattr(sink_stage, "phases", lambda: Refusing())
    with pytest.raises(sink_stage.SinkRefused, match="Test: the drain's constructed route crosses a resting basin"):
        sink_stage.stage_sink(s, plan)


def test_the_records_rust_returns_are_written_a_pond_its_ditch_and_reeds_or_a_confluence(monkeypatch: pytest.MonkeyPatch) -> None:
    plan = a_plan(10)
    s = _settled(plan)
    pond = {
        "form": "pond",
        "run": [(700.0, 990.0), (705.0, 1050.0), (700.0, 1110.0)],
        "to": "pond",
        "pond": ((700.0, 1110.0), 80.0, 50.0),
        "reeds": [(700.0 + 124.0 * c, 1110.0 + 94.0 * d) for c, d in ((1, 0), (0, 1), (-1, 0), (0, -1))],
        "confluence": None,
        "counts": {"test@pond_seat": 3},
    }

    class Laying:
        def __init__(self, out: dict[str, Any]) -> None:
            self.out = out

        def stage_sink(self, *_a: Any) -> dict[str, Any]:
            return self.out

    monkeypatch.setattr(sink_stage, "phases", lambda: Laying(pond))
    sink_stage.stage_sink(s, plan)
    assert plan.sink_pond == (700.0, 1110.0, 80.0, 50.0) and s.M["meta"]["pond_role"] == "drainage"
    run = s.M["channels"][-1]
    assert run["to"] == {"kind": "pond"} and run["field"] == "test-paddies" and run["w"] == sink_stage.RUN_RECORD_W
    assert s.block_polys[-1][0] == (700.0 - 80.0 - sink_stage.NO_BUILD_FT, 1110.0 - 50.0 - sink_stage.NO_BUILD_FT)
    s = _settled(plan)
    joined = {**pond, "form": "offmap", "to": "stream", "pond": None, "reeds": [], "confluence": (705.0, 1200.0)}
    monkeypatch.setattr(sink_stage, "phases", lambda: Laying(joined))
    sink_stage.stage_sink(s, plan)
    assert plan.confluence == (705.0, 1200.0) and plan.water_sink == "offmap" and s.M["meta"]["water_sink"] == "offmap"
