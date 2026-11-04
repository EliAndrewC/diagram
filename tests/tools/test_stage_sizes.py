"""`tools/stage_sizes.py` (feature 444 T27): what a stage is handed, counted - records and points of each manifest and plan part."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.hamletgen import driver
from l7r.diagram.tools import stage_sizes as ss


def test_points_are_counted_in_rings_and_in_records() -> None:
    assert ss._points([(0.0, 0.0), (1.0, 2.0), (3, 4)]) == 3
    assert ss._points([{"poly": [(0, 0), (1, 1)]}, {"outline": [(0, 0), (1, 1), (2, 2)]}]) == 5
    assert ss._points([[(0, 0), (1, 1)], [(2, 2), (3, 3)]]) == 4, "a list of rings"
    assert ss._points([]) is None and ss._points("ab") is None and ss._points([{"x": 1}]) is None
    assert ss._points([{"pts": [(0, 0)]}, 7]) is None, "a member that holds no points spoils the part"


def test_the_input_is_measured_where_the_stage_would_run_and_a_refusal_named(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def lay(s: Any, plan: Any) -> None:
        s.M["lines"] = [{"pts": [(0.0, 0.0), (5.0, 5.0)]}]
        plan.envelope = [(0.0, 0.0), (9.0, 0.0), (9.0, 9.0)]

    def boom(_s: Any, _plan: Any) -> None:
        raise ValueError("no seat")

    lay.__name__, boom.__name__ = "stage_lay", "stage_boom"
    after = driver.STAGES[0]
    name = after.__name__.removeprefix("stage_")
    monkeypatch.setattr(driver, "STAGES", (lay, after))
    got = ss.sizes(25, 12, name, ("toe_band",), str(tmp_path / "in.json"), {"down_deg": 90})
    dumped = json.loads((tmp_path / "in.json").read_text())
    assert dumped["M"]["lines"][0]["pts"] == [[0.0, 0.0], [5.0, 5.0]] and "toe_band" in dumped["calls"] and dumped["plan"]["envelope"]
    assert got["M.lines"] == [1, 2] and len(got["canvas"]) == 2 and "s.toe_band()" in got
    assert got["plan.envelope"] == [3, 3]
    monkeypatch.setattr(driver, "STAGES", (boom, after))
    assert ss.sizes(25, 12, name) == {"refused": "stage_boom: ValueError"}
    with pytest.raises(ValueError, match="no stage"):
        ss.sizes(25, 12, "nowhere")


def test_the_table_and_the_command(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    rows = {20: [{"seed": 4, "canvas": [10.0, 20.0], "M.a": [2, 10]}, {"seed": 25, "refused": "stage_x: ValueError"}], 40: []}
    out = ss.table(rows)
    assert "| M.a | 2.0 / 10 | - |" in out and "| canvas (first seed) | 10 x 20 | - |" in out and "seed 25 at 20" in out
    seen: list[str] = []
    monkeypatch.setattr(ss, "sizes", lambda seed, h, stage, calls, dump, spec=None: seen.append(dump) or {"canvas": [1.0, 1.0], "M.b": [1, h]})
    monkeypatch.setattr(ss, "SEEDS", (4,))
    assert ss.main(["seat", "--sizes", "20", "--calls", "toe_band"]) == 0
    assert ss.main(["seat", "--sizes", "20", "--dump", "/x"]) == 0 and seen == ["", "/x/4-20.json"]
    assert "| M.b | 1.0 / 20 |" in capsys.readouterr().out
    assert ss.main(["seat", "--sizes", "19", "--seeds", "24", "--spec", '{"down_deg": 225}']) == 0 and "given spec" in capsys.readouterr().out
