"""The roll census's verdict and attribution (`ci/rollverdict.py`, `ci/rollcensus.py`, feature 213).

Every refusal the spec names is PROVED to fire on a synthetic census against a synthetic roster, and the passing
state - many requests served by one roll - is proved to pass. The shim is reloaded under coverage as 207's is.
"""

from __future__ import annotations

import importlib
import json
import os
import pathlib
import types
from typing import Any

import pytest

from l7r.diagram import _census
from l7r.diagram.ci import rollverdict

pytestmark = pytest.mark.tooling

W = "7"  # the worker's pid in the synthetic census


def _spec(name: str, seed: int) -> dict[str, Any]:
    return {"name": name, "seed": seed, "households": 12, "field_archetype": None, "down_deg": None, "water_sink": None, "settlement_form": None}


def _roll(name: str, seed: int, test: str, request: str, pid: str = "99", dt: float = 10.0) -> dict[str, Any]:
    return {"kind": "roll", "spec": _spec(name, seed), "test": test, "request": request, "pid": pid, "worker": W, "dt": dt, "ok": True}


def _roster(*keys: tuple[str, int], duplicates: tuple[Any, ...] = (), in_process: tuple[Any, ...] = ()) -> Any:
    class Row:
        def __init__(self, key: tuple[str, int]) -> None:
            self.key, self.rolled_by = key, "a child roll"

    rows = {k: Row(k) for k in keys}
    return types.SimpleNamespace(by_key=lambda: rows, DUPLICATES=duplicates, IN_PROCESS=in_process)


def test_one_roll_served_to_many_tests_is_the_passing_state() -> None:
    rows = [_roll("Inashiro", 4, "tests/gate/a.py::t1", "r1")] + [{"kind": "served", "subject": "roll:Inashiro", "test": f"tests/gate/b.py::t{i}"} for i in range(5)]
    failures, lines = rollverdict.judge(rows, _roster(("Inashiro", 4)), full=True, renders_ok=set())
    assert failures == []
    assert "1 roll(s) of 1 spec(s); 5 request(s) served" in lines[0]


def test_a_second_roll_of_a_spec_fails_and_names_both_tests() -> None:
    rows = [_roll("Inashiro", 4, "tests/gate/a.py::t1", "r1"), _roll("Inashiro", 4, "tests/gate/b.py::t2", "r2")]
    failures, _ = rollverdict.judge(rows, _roster(("Inashiro", 4)), full=False, renders_ok=set())
    assert len(failures) == 1 and "rolled 2 times" in failures[0] and "a.py::t1" in failures[0] and "b.py::t2" in failures[0]


def test_re_roll_attempts_inside_one_request_are_one_roll() -> None:
    rows = [_roll("Cohort-42", 42, "tests/gate/c.py::t", "r1") for _ in range(3)]
    failures, lines = rollverdict.judge(rows, _roster(("Cohort-42", 42)), full=True, renders_ok=set())
    assert failures == []
    assert any("1 roll(s), attempts 3" in ln for ln in lines)


def test_a_stated_duplicate_is_allowed_once_and_listed() -> None:
    dup = types.SimpleNamespace(key=("Cohort-41", 41), test="tests/full/hamletgen/test_driver.py::test_the_fan_out", mechanism="pool child", reason="the path under test")
    rows = [_roll("Cohort-41", 41, "tests/gate/a.py::t", "r1"), _roll("Cohort-41", 41, "tests/full/hamletgen/test_driver.py::test_the_fan_out_agrees", "r2")]
    failures, lines = rollverdict.judge(rows, _roster(("Cohort-41", 41), duplicates=(dup,)), full=True, renders_ok=set())
    assert failures == [] and any("stated duplicate" in ln for ln in lines)
    rows.append(_roll("Cohort-41", 41, "tests/gate/z.py::t3", "r3"))
    failures, _ = rollverdict.judge(rows, _roster(("Cohort-41", 41), duplicates=(dup,)), full=True, renders_ok=set())
    assert len(failures) == 1 and "rolled 3 times" in failures[0], "a third roll is not covered by the one stated duplicate"


def test_an_unrostered_roll_fails_with_the_instruction_to_add_the_row() -> None:
    failures, _ = rollverdict.judge([_roll("Newcomer", 9, "tests/gate/n.py::t", "r1")], _roster(("Inashiro", 4)), full=False, renders_ok=set())
    assert any("not in the roster" in f and "tests/rolls.py" in f for f in failures)


def test_a_stale_roster_row_fails_a_full_run_only() -> None:
    rows = [_roll("Inashiro", 4, "tests/gate/a.py::t", "r1")]
    roster = _roster(("Inashiro", 4), ("Gone", 1))
    assert rollverdict.judge(rows, roster, full=False, renders_ok=set())[0] == [], "an incremental run rolls a subset"
    failures, _ = rollverdict.judge(rows, roster, full=True, renders_ok=set())
    assert len(failures) == 1 and "Gone seed=1" in failures[0] and "stale" in failures[0]


def test_an_in_process_roll_fails_unless_its_module_is_excepted() -> None:
    inproc = _roll("Inashiro", 6, "tests/tools/test_perf_snapshot.py::t", "r1", pid=W)
    failures, _ = rollverdict.judge([inproc], _roster(("Inashiro", 6)), full=False, renders_ok=set())
    assert len(failures) == 1 and "IN THE TEST WORKER" in failures[0]
    exc = types.SimpleNamespace(module="tests/tools/test_perf_snapshot.py", reason="times the stages")
    assert rollverdict.judge([inproc], _roster(("Inashiro", 6), in_process=(exc,)), full=False, renders_ok=set())[0] == []
    nameless = {"kind": "roll", "spec": None, "test": "tests/x.py::t", "request": "r", "pid": W, "worker": W, "dt": 0.0}
    assert any("no spec" in f for f in rollverdict.judge([nameless], _roster(), full=False, renders_ok=set())[0])


def test_a_render_fails_unless_the_test_is_marked() -> None:
    render = {"kind": "render", "what": "png", "test": "tests/settlement/test_finish.py::t", "pid": W, "worker": W}
    failures, _ = rollverdict.judge([render], _roster(), full=False, renders_ok=set())
    assert len(failures) == 1 and "rendered a png" in failures[0] and "`renders` marker" in failures[0]
    assert rollverdict.judge([render], _roster(), full=False, renders_ok={"tests/settlement/test_finish.py::t"})[0] == []


def test_read_skips_a_half_written_line(tmp_path: pathlib.Path) -> None:
    p = tmp_path / "c.jsonl"
    p.write_text(json.dumps({"kind": "served"}) + "\n{\"kind\": \"roll\", \n\n")
    assert [r["kind"] for r in rollverdict.read(p)] == ["served"]
    assert rollverdict.read(tmp_path / "absent.jsonl") == []


class _Item:
    def __init__(self, nodeid: str, *marks: str) -> None:
        self.nodeid, self._marks = nodeid, set(marks)

    def get_closest_marker(self, name: str) -> object:
        return object() if name in self._marks else None


def test_rolls_first_moves_the_rolling_tests_to_the_front_and_writes_the_renders_file(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    census = tmp_path / "census.jsonl"
    monkeypatch.setenv(_census.ENV, str(census))
    items: list[Any] = [_Item("a::t1"), _Item("b::t2", "rolls_map"), _Item("c::t3", "renders"), _Item("d::t4", "rolls_map")]
    rollverdict.rolls_first(items)
    assert [it.nodeid for it in items] == ["b::t2", "d::t4", "a::t1", "c::t3"], "rollers first, each group in its collected order"
    assert pathlib.Path(rollverdict.renders_file(str(census))).read_text().split() == ["c::t3"]


def test_begin_and_end_set_and_clear_the_attribution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_census.TEST_ENV, raising=False)
    monkeypatch.delenv(_census.REQUEST_ENV, raising=False)
    rollverdict.configure()
    assert os.environ[_census.WORKER_ENV] == str(os.getpid())
    rollverdict.begin("tests/x.py::t")
    assert os.environ[_census.TEST_ENV] == "tests/x.py::t" and len(os.environ[_census.REQUEST_ENV]) == 12
    first = os.environ[_census.REQUEST_ENV]
    rollverdict.begin("tests/x.py::u")
    assert os.environ[_census.REQUEST_ENV] != first, "a fresh request id per test"
    rollverdict.end()
    assert _census.TEST_ENV not in os.environ and _census.REQUEST_ENV not in os.environ


def test_main_reads_the_census_and_the_renders_file_and_judges_against_the_real_roster(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv(_census.ENV, raising=False)
    assert rollverdict.main(["verdict"]) == 2
    assert rollverdict.main([]) == 2
    census = tmp_path / "census.jsonl"
    monkeypatch.setenv(_census.ENV, str(census))
    census.write_text(json.dumps(_roll("Inashiro", 4, "tests/gate/a.py::t", "r1")) + "\n" + json.dumps({"kind": "render", "what": "png", "test": "tests/settlement/test_finish.py::t", "pid": "99", "worker": W}) + "\n")
    pathlib.Path(rollverdict.renders_file(str(census))).write_text("tests/settlement/test_finish.py::t\n")
    assert rollverdict.main(["verdict"]) == 0, capsys.readouterr().out
    assert "roll census: green" in capsys.readouterr().out
    assert rollverdict.main(["verdict", "--full"]) == 1, "the real roster has more rows than this one roll: stale on a full run"
    assert "ROLL CENSUS FAILED" in capsys.readouterr().out


def test_the_shim_delegates_and_its_import_lines_are_measured(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """As `tests/tooling/ci/test_incremental.py` does for gate_plugin: a `-p` module's import runs before coverage
    starts, so it is reloaded here; each hook delegates only when a census is open."""
    from l7r.diagram.ci import rollcensus

    importlib.reload(rollcensus)
    monkeypatch.delenv(_census.ENV, raising=False)
    rollcensus.pytest_configure(None)
    rollcensus.pytest_collection_modifyitems(None, None, [])
    rollcensus.pytest_runtest_protocol(types.SimpleNamespace(nodeid="x::t"), None)
    rollcensus.pytest_runtest_logfinish("x::t", None)
    assert _census.TEST_ENV not in os.environ, "no census open: the hooks do nothing"
    monkeypatch.setenv(_census.ENV, str(tmp_path / "c.jsonl"))
    items: list[Any] = [_Item("a::t1"), _Item("b::t2", "rolls_map")]
    rollcensus.pytest_configure(None)
    rollcensus.pytest_collection_modifyitems(None, None, items)
    assert items[0].nodeid == "b::t2"
    rollcensus.pytest_runtest_protocol(types.SimpleNamespace(nodeid="x::t"), None)
    assert os.environ[_census.TEST_ENV] == "x::t"
    rollcensus.pytest_runtest_logfinish("x::t", None)
    assert _census.TEST_ENV not in os.environ
