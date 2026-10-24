"""`scripts/measure/gate_costs.py` - what a gate run costs, from the run records (feature 415 T04, D7)."""

from __future__ import annotations

import importlib.util
import json
import pathlib

from tests._scripts import script

_spec = importlib.util.spec_from_file_location("gate_costs", script("gate_costs.py"))
assert _spec and _spec.loader
gc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gc)


def test_the_fit_the_growth_and_the_records_read(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    """The records with T01's fields are read (one without phases is not); the fit is the least squares line through the test
    phase's seconds on the selection; the growth counts incremental runs since the last full one."""
    runs = tmp_path / "dev" / "run-log" / "2026-10"
    runs.mkdir(parents=True)
    rows = [
        {"utc": "2026-10-24T01:00:00Z", "target": "done", "result": "green", "plan_mode": "full", "selected": 1000, "phases": {"pytest": 110.0}, "seconds": 120},
        {"utc": "2026-10-24T02:00:00Z", "target": "done", "result": "green", "plan_mode": "incremental", "selected": 100, "phases": {"pytest": 20.0}, "seconds": 30},
        {"utc": "2026-10-24T03:00:00Z", "target": "done", "result": "green", "plan_mode": "incremental", "selected": 200, "phases": {"pytest": 30.0}, "seconds": 40},
        {"utc": "2026-10-24T04:00:00Z", "target": "done", "result": "green", "seconds": 50},
    ]
    for n, r in enumerate(rows):
        (runs / f"{n}.json").write_text(json.dumps(r), encoding="utf-8")
    recs = gc.records(tmp_path)
    assert len(recs) == 3, "a record without phases predates T01"
    fixed, per = gc.fit([(1000.0, 110.0), (100.0, 20.0), (200.0, 30.0)])
    assert round(fixed, 6) == 10.0 and round(per, 6) == 0.1
    assert gc.fit([(5.0, 1.0), (5.0, 2.0)]) is None, "one distinct selection fits nothing"
    assert gc.growth(recs) == [("2026-10-24T02:00:00Z", 1, 100), ("2026-10-24T03:00:00Z", 2, 200)]
    import os  # noqa: PLC0415

    os.environ["L7R_ROOT"] = str(tmp_path)
    try:
        assert gc.main(["--since", "2026-10-24"]) == 0
    finally:
        del os.environ["L7R_ROOT"]
    assert "10.0 s fixed + 100.00 ms per selected test" in capsys.readouterr().out
