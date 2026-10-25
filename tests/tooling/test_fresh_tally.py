"""`make fresh-tally` - fresh seeds pooled by form and cause (feature 417 T01, plan D2, D8)."""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

MEASURE = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "measure"
pytestmark = pytest.mark.tooling

_spec = importlib.util.spec_from_file_location("fresh_tally", MEASURE / "fresh_tally.py")
assert _spec and _spec.loader
ft = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ft)


def _seed(n: int, form: str, failures: list[str] | None = None) -> dict:
    return {"seed": n, "form": form, "verdict": "fail" if failures else "pass", "failures": failures or []}


def _write(log: pathlib.Path, name: str, rec: dict) -> None:
    log.mkdir(exist_ok=True)
    (log / name).write_text(json.dumps(rec), encoding="utf-8")


def test_fresh_seeds_are_pooled_by_form_and_cause_and_fixed_and_pinned_seeds_are_left_out(tmp_path, capsys):
    log = tmp_path / "log"
    _write(
        log,
        "a.json",
        {
            "utc": "20261024T01Z",
            "commit": "abc",
            "first_seed": 1,
            "seeds": [
                _seed(1, "linear", ["lane_knots 2"]),
                _seed(901, "linear", ["row_rules 1"]),
                {**_seed(20001, "linear", ["lane_knots 1", "row_rules 1"]), "fresh": True},
                {**_seed(20002, "dispersed"), "fresh": True},
            ],
        },
    )
    _write(
        log,
        "b.json",
        {"utc": "20261024T02Z", "commit": "abc", "first_seed": 3000001, "seeds": [_seed(3000001, "nucleated", ["refused:WebRefused"]), _seed(3000002, "nucleated"), _seed(902, "linear", ["x"])]},
    )
    assert ft.main(["--log", str(log)]) == 0
    out = capsys.readouterr().out
    assert "fresh seeds: 2 of 4 failed (50%)" in out
    assert "linear      1 of 1 (100%)" in out and "nucleated   1 of 2 (50%)" in out
    assert "      1  lane_knots" in out and "      1  refused:WebRefused" in out and "      1  row_rules" in out


def test_a_seed_rolled_twice_on_one_engine_counts_once_from_its_latest_record_and_commit_filters(tmp_path, capsys):
    log = tmp_path / "log"
    _write(log, "a.json", {"utc": "20261024T01Z", "commit": "abc", "first_seed": 3000001, "seeds": [_seed(3000001, "linear", ["lane_knots 1"])]})
    _write(log, "b.json", {"utc": "20261024T02Z", "commit": "abc", "first_seed": 3000001, "seeds": [_seed(3000001, "linear")]})
    _write(log, "c.json", {"utc": "20261024T03Z", "commit": "def", "first_seed": 3000001, "seeds": [_seed(3000001, "linear", ["lane_knots 1"])]})
    ft.main(["--log", str(log), "--commit", "abc"])
    assert "fresh seeds: 0 of 1 failed (0%)" in capsys.readouterr().out
    ft.main(["--log", str(log), "--since", "20261024T03Z"])
    assert "fresh seeds: 1 of 1 failed (100%)" in capsys.readouterr().out
