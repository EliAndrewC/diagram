"""`tools/phase_calls.py` (feature 434): a hamlet's calls by stage and by step - each stage's total cProfile's own count, its
steps and its own work adding up to it, a call counted by the innermost listed step running; the record keeps the newest
measurement per map type."""

import cProfile
import json
import pstats
import types
from pathlib import Path
from typing import Any

import pytest

from l7r.diagram.tools import phase_calls as pc

_LEAF = types.ModuleType("leaf")


def _inner(n: int) -> int:
    return sum(abs(i) for i in range(n))


def _outer(n: int) -> int:
    return _LEAF.inner(n) + len([max(i, 1) for i in range(n)])  # type: ignore[attr-defined]


_LEAF.inner = _inner  # type: ignore[attr-defined]
_LEAF.outer = _outer  # type: ignore[attr-defined]


def _bind(path: str) -> tuple[list[tuple[Any, str]], Any]:
    leaf = path.rsplit(".", 1)[-1]
    if leaf == "missing":
        raise AttributeError(leaf)
    return [(_LEAF, leaf)], getattr(_LEAF, leaf)


def _stage() -> int:
    return _LEAF.outer(30) + _LEAF.inner(5) + len(str(list(range(7))))  # type: ignore[attr-defined]


def _plain_count() -> int:
    """The fanout's measure of the stage: one profiler on around it, as `perf_profile.profile_stage` takes it."""
    prof = cProfile.Profile()
    prof.enable()
    _stage()
    prof.disable()
    return sum(v[1] for v in pstats.Stats(prof).stats.values())  # type: ignore[attr-defined]


def test_a_stages_tally_equals_the_fanouts_count_and_its_parts_add_up() -> None:
    got = pc.Tally().stage(_stage, ["leaf.outer", "leaf.inner", "leaf.missing"], _bind)
    assert got["calls"] == _plain_count(), "the stage total is cProfile's own count of the stage (SC-003)"
    assert got["own"] + sum(got["steps"].values()) == got["calls"], "steps and own work add up to the stage (SC-002)"
    assert got["steps"]["leaf.missing"] == 0, "a step that does not bind is shown at 0"
    assert got["steps"]["leaf.inner"] > 0 and got["steps"]["leaf.outer"] > 0
    assert _LEAF.outer is _outer and _LEAF.inner is _inner, "every binding restored"  # type: ignore[attr-defined]


def test_a_call_counts_for_the_innermost_step_only() -> None:
    nested = pc.Tally().stage(lambda: _LEAF.outer(30), ["leaf.outer", "leaf.inner"], _bind)  # type: ignore[attr-defined]
    alone = pc.Tally().stage(lambda: _LEAF.outer(30), ["leaf.outer"], _bind)  # type: ignore[attr-defined]
    assert nested["steps"]["leaf.outer"] + nested["steps"]["leaf.inner"] == alone["steps"]["leaf.outer"], "inner's calls leave outer's tally"
    assert nested["calls"] == alone["calls"], "the stage's total does not depend on which steps are listed"


def test_the_map_type_and_the_record_keep_the_newest_per_type(tmp_path: Path) -> None:
    assert pc.type_key({"settlement_form": "nucleated", "water_sink": "pond"}) == "nucleated/rolled/pond"
    path = str(tmp_path / "rec.json")
    a = {"type": "t1", "seed": 39, "households": 40, "total": 10, "stages": {"x": {"calls": 10, "own": 10, "steps": {}}}}
    pc.record(a, path, commit="abc", today="2026-10-27")
    pc.record({**a, "type": "t2"}, path, commit="abc", today="2026-10-27")
    rec = pc.record({**a, "total": 12}, path, commit="def", today="2026-10-28")
    assert set(rec) == {"t1", "t2"} and rec["t1"]["total"] == 12 and rec["t1"]["commit"] == "def" and rec["t1"]["date"] == "2026-10-28"
    assert json.loads(Path(path).read_text()) == rec
    assert pc.report(rec["t2"]).splitlines()[1].split() == ["x", "10", "100.0%"]
    assert pc._commit()


def test_measure_rolls_every_stage_once_under_the_tally(monkeypatch: pytest.MonkeyPatch) -> None:
    """On stand-in stages (`test_perf_profile`'s): each stage measured, its steps from its docstring's `Steps:`."""
    from l7r.diagram.hamletgen import driver

    ran: list[str] = []

    def stage_water_frame(s, plan):  # noqa: ANN001, ARG001
        """Stand-in."""
        ran.append("water_frame")

    def stage_sink(s, plan):  # noqa: ANN001, ARG001
        """Stand-in.

        Steps:
            l7r.diagram.tools.phase_calls.type_key
        """
        ran.append("sink")
        pc.type_key({})

    monkeypatch.setattr(driver, "STAGES", (stage_water_frame, stage_sink))
    from concurrent.futures import ThreadPoolExecutor

    m = pc.measure(7, 12, {"water_sink": "offmap"}, jobs=2, pool_cls=ThreadPoolExecutor)
    assert ran.count("water_frame") == 2 and ran.count("sink") == 1, "each stage its own roll: the stages before it run first"
    assert m["type"] == "nucleated/rolled/offmap" and m["households"] == 12
    assert set(m["stages"]) == {"water_frame", "sink"} and m["total"] == sum(v["calls"] for v in m["stages"].values())
    assert m["stages"]["sink"]["steps"]["l7r.diagram.tools.phase_calls.type_key"] > 0


def test_main_measures_records_and_prints(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    got: dict[str, Any] = {}
    m = {"type": "t", "seed": 1, "households": 40, "total": 4, "stages": {"x": {"calls": 4, "own": 4, "steps": {}}}}
    monkeypatch.setattr(pc, "measure", lambda seed, households, over, jobs: got.update(seed=seed, households=households, over=over) or m)
    monkeypatch.setattr(pc, "RECORD", str(tmp_path / "rec.json"))
    monkeypatch.setattr(pc, "record", lambda mm: got.update(recorded=mm))
    assert pc.main(["--seed", "5", "--form", "linear", "--sink", "pond"]) == 0
    assert got == {"seed": 5, "households": 40, "over": {"settlement_form": "linear", "water_sink": "pond"}, "recorded": m}
    assert "4 calls" in capsys.readouterr().out
