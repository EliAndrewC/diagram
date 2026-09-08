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


def _roster(*keys: tuple[str, int], duplicates: tuple[Any, ...] = (), in_process: tuple[Any, ...] = (), pool_gens: tuple[Any, ...] = ()) -> Any:
    class Row:
        def __init__(self, key: tuple[str, int]) -> None:
            self.key, self.rolled_by = key, "a child roll"

    rows = {k: Row(k) for k in keys}
    return types.SimpleNamespace(by_key=lambda: rows, DUPLICATES=duplicates, IN_PROCESS=in_process, POOL_GENS=pool_gens)


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


def test_two_children_of_one_test_are_two_rolls_while_re_rolls_in_one_process_are_attempts() -> None:
    """The first census grouped by request alone and reported the fan-out's serial and pool children as one
    roll with two attempts - hiding the very duplicate the roster states. A roll is (spec, request, PROCESS)."""
    two_children = [_roll("Cohort-41", 41, "tests/full/x.py::t", "r1", pid="500"), _roll("Cohort-41", 41, "tests/full/x.py::t", "r1", pid="501")]
    failures, lines = rollverdict.judge(two_children, _roster(("Cohort-41", 41)), full=False, renders_ok=set())
    assert len(failures) == 1 and "rolled 2 times" in failures[0]
    assert any("2 roll(s), attempts 1, 1" in ln for ln in lines)
    dup = types.SimpleNamespace(key=("Cohort-41", 41), test="tests/full/x.py::t", mechanism="pool child", reason="the path under test")
    assert rollverdict.judge(two_children, _roster(("Cohort-41", 41), duplicates=(dup,)), full=False, renders_ok=set())[0] == []


def test_a_pool_gen_may_roll_once_when_its_key_moved_and_is_never_stale() -> None:
    pool = types.SimpleNamespace(key=("Sawada", 6), gen="pool/hamlets/sawada/sawada.gen.py", note="pool-only", test="tests/full/test_villages.py::test_village_passes_gate")
    cold = [_roll("Sawada", 6, "tests/full/test_villages.py::test_village_passes_gate[sawada.gen.py]", "r1", pid="600")]
    failures, lines = rollverdict.judge(cold, _roster(("Inashiro", 4), pool_gens=(pool,)), full=False, renders_ok=set())
    assert failures == [], failures
    assert any("Sawada seed=6: 1 roll(s)" in ln and "pool gen" in ln for ln in lines)
    assert any("pool gen: Sawada seed=6" in ln and "ROLLED this run" in ln for ln in lines)
    warm = rollverdict.judge([_roll("Inashiro", 4, "tests/gate/a.py::t", "r1")], _roster(("Inashiro", 4), pool_gens=(pool,)), full=True, renders_ok=set())
    assert warm[0] == [], "a pool gen served from the gen cache is not a stale row"
    assert any("served from the gen cache" in ln for ln in warm[1])
    twice = cold + [_roll("Sawada", 6, "tests/full/test_villages.py::test_village_passes_gate[sawada.gen.py]", "r2", pid="601")]
    assert any("rolled 2 times" in f for f in rollverdict.judge(twice, _roster(pool_gens=(pool,)), full=False, renders_ok=set())[0])
    # the same key as a rostered roll: the gate's roll plus the cold pool gen is the passing state, and the line says so
    both = [_roll("Inashiro", 4, "tests/gate/a.py::t", "r1"), _roll("Inashiro", 4, "tests/full/test_villages.py::test_village_passes_gate[inashiro.gen.py]", "r2", pid="602")]
    ref = types.SimpleNamespace(key=("Inashiro", 4), gen="pool/hamlets/inashiro/inashiro.gen.py", note="", test="tests/full/test_villages.py::test_village_passes_gate")
    failures, lines = rollverdict.judge(both, _roster(("Inashiro", 4), pool_gens=(ref,)), full=True, renders_ok=set())
    assert failures == [] and any("rostered (+ the pool gen: its key moved)" in ln for ln in lines)
    # ...and the pool gen's one cold roll may be requested by ANY reader (feature 215: a gate module reading the pool's
    # map through gate_obtain rolls it when it comes first); a second roll of it in the same run still fails
    stray = [_roll("Sawada", 6, "tests/gate/s.py::t", "r1", pid="700")]
    assert rollverdict.judge(stray, _roster(pool_gens=(pool,)), full=False, renders_ok=set())[0] == []
    twice_by_readers = stray + [_roll("Sawada", 6, "tests/gate/u.py::t", "r2", pid="701")]
    assert any("rolled 2 times" in f for f in rollverdict.judge(twice_by_readers, _roster(pool_gens=(pool,)), full=False, renders_ok=set())[0])
    # a key that is BOTH a roll (the immune experiment's perturbed reference) and a pool gen allows one of each
    both_kinds = [_roll("Inashiro", 4, "tests/full/test_villages.py::immune", "r1", pid="800"), _roll("Inashiro", 4, "tests/gate/a.py::t", "r2", pid="801")]
    assert rollverdict.judge(both_kinds, _roster(("Inashiro", 4), pool_gens=(ref,)), full=True, renders_ok=set())[0] == []
    assert any(
        "rolled 3 times" in f
        for f in rollverdict.judge(both_kinds + [_roll("Inashiro", 4, "tests/gate/b.py::t", "r3", pid="802")], _roster(("Inashiro", 4), pool_gens=(ref,)), full=False, renders_ok=set())[0]
    )


def test_a_stub_module_s_rolls_are_reported_and_bounded_never_counted() -> None:
    stub = types.SimpleNamespace(module="tests/hamletgen/test_driver.py", reason="stand-in stages", stub=True)
    fast = [_roll("Probe", 4, "tests/hamletgen/test_driver.py::t1", "r1", pid=W, dt=0.01), _roll("Probe", 4, "tests/hamletgen/test_driver.py::t2", "r2", pid=W, dt=0.02)]
    failures, lines = rollverdict.judge(fast, _roster(in_process=(stub,)), full=True, renders_ok=set())
    assert failures == [], "two in-worker stub rolls of an unrostered spec: reported, not judged"
    assert any("stand-in stage rolls" in ln and "2," in ln for ln in lines)
    slow = [_roll("Probe", 4, "tests/hamletgen/test_driver.py::t1", "r1", pid=W, dt=rollverdict.STUB_MAX_S + 1)]
    failures, _ = rollverdict.judge(slow, _roster(in_process=(stub,)), full=False, renders_ok=set())
    assert len(failures) == 1 and "excepted as a stub-stage module" in failures[0]
    plain = types.SimpleNamespace(module="tests/hamletgen/test_driver.py", reason="in the worker")  # no stub attribute: a real in-process exception
    assert any("not in the roster" in f for f in rollverdict.judge(fast[:1], _roster(in_process=(plain,)), full=False, renders_ok=set())[0])


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


def test_engine_changed_reads_the_plan_and_defaults_to_the_strict_side(tmp_path: pathlib.Path) -> None:
    from l7r.diagram.ci import incremental

    assert rollverdict.engine_changed(None) is True
    assert rollverdict.engine_changed(tmp_path) is True, "no plan: strict"
    bdir = incremental.baseline_dir(tmp_path)
    bdir.mkdir(parents=True)
    (bdir / incremental.PLAN).write_text(json.dumps({"changed_engine": []}))
    assert rollverdict.engine_changed(tmp_path) is False
    (bdir / incremental.PLAN).write_text(json.dumps({"changed_engine": ["x.py"]}))
    assert rollverdict.engine_changed(tmp_path) is True


def test_main_reads_the_census_and_the_renders_file_and_judges_against_the_real_roster(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv(_census.ENV, raising=False)
    assert rollverdict.main(["verdict"]) == 2
    assert rollverdict.main([]) == 2
    census = tmp_path / "census.jsonl"
    monkeypatch.setenv(_census.ENV, str(census))
    census.write_text(
        json.dumps(_roll("Inashiro", 4, "tests/gate/a.py::t", "r1"))
        + "\n"
        + json.dumps({"kind": "render", "what": "png", "test": "tests/settlement/test_finish.py::t", "pid": "99", "worker": W})
        + "\n"
    )
    pathlib.Path(rollverdict.renders_file(str(census))).write_text("tests/settlement/test_finish.py::t\n")
    assert rollverdict.main(["verdict"]) == 0, capsys.readouterr().out
    assert "roll census: green" in capsys.readouterr().out
    # since feature 219 the real roster holds no Roll row, so a full run has nothing stale to report; the stale-row rule is
    # proved on the synthetic roster in test_a_stale_roster_row_fails_a_full_run_only
    assert rollverdict.main(["verdict", "full"]) == 0
    assert "roll census: green" in capsys.readouterr().out


def test_the_shim_delegates_and_its_import_lines_are_measured(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """As `tests/tooling/ci/test_incremental.py` does for gate_plugin: a `-p` module's import runs before coverage
    starts, so it is reloaded here; each hook delegates only when a census is open."""
    from l7r.diagram.ci import rollcensus

    importlib.reload(rollcensus)
    # under the gate this very test runs with the plugin live, so the attribution variables are SET around it;
    # clear them (monkeypatch restores them for the plugin afterward) so the no-census half can be judged
    monkeypatch.delenv(_census.ENV, raising=False)
    monkeypatch.delenv(_census.TEST_ENV, raising=False)
    monkeypatch.delenv(_census.REQUEST_ENV, raising=False)
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


def test_a_roll_no_test_requested_is_the_floor_s_and_fails() -> None:
    """The hamlet-floor phase runs after pytest under the same census (feature 213, the polder-only run of
    2026-09-08: it re-rolled both polder subjects unseen). A roll with no requesting test is its; the tests'
    roll must be its record, so any such roll fails and the message says where to look."""
    floor = {"kind": "roll", "spec": _spec("Polder", 12), "test": None, "request": None, "pid": "4242", "worker": None, "dt": 64.0, "ok": True}
    failures, lines = rollverdict.judge([floor], _roster(("Polder", 12)), full=False, renders_ok=set(), engine_changed=True)
    assert len(failures) == 1 and "hamlet-floor phase ROLLED Polder seed=12" in failures[0] and "CONTEXT_ENV" in failures[0]
    assert any("hamlet-floor rolls (no test requested them): 1" in ln for ln in lines)
    assert rollverdict.judge([floor], _roster(("Polder", 12)), full=True, renders_ok=set(), engine_changed=False)[0], "on a full run every spec was just rolled: a floor roll is always wrong"
    # NO engine change against the baseline (an edit reverted: the cache holds the edited roll, the baseline says nothing
    # moved, no test could be selected) - the floor's roll is the record's only refresh: reported, allowed
    failures, lines = rollverdict.judge([floor], _roster(("Polder", 12)), full=False, renders_ok=set(), engine_changed=False)
    assert failures == [] and any("allowed: no engine file changed" in ln for ln in lines)
    assert rollverdict.judge([_roll("Polder", 12, "tests/gate/p.py::t", "r1")], _roster(("Polder", 12)), full=True, renders_ok=set())[0] == []


def test_a_roster_row_whose_only_rolls_are_stand_ins_is_stale_on_a_full_run() -> None:
    """Feature 215 moved the re-roll loop onto stand-in stages and left its two roster rows behind for one gate; the
    stand-in records are excused from the count, so on a full run the rows had no real roll and must read as stale."""
    stub = types.SimpleNamespace(module="tests/gate/hamletgen/test_driver.py", reason="stand-in stages", stub=True)
    rows = [_roll("Retry", 4, "tests/gate/hamletgen/test_driver.py::t", "r1", pid=W, dt=0.01)]
    failures, _ = rollverdict.judge(rows, _roster(("Retry", 4), in_process=(stub,)), full=True, renders_ok=set())
    assert any("stale" in f and "Retry seed=4" in f for f in failures), failures


def test_a_child_roll_requested_from_a_stub_module_is_a_real_roll_judged_by_the_roster() -> None:
    """Feature 216: the stub exception is about rolls made IN THE WORKER. A child roll a stub-excepted module
    merely REQUESTS is the shared roll every other module reads, and is judged against the roster - the first
    census after 216 bucketed the fan-out's request for Polder 12 as a 62 s "stub" and then reported the
    Polder row as never rolled by the run."""
    stub = types.SimpleNamespace(module="tests/gate/hamletgen/test_driver.py", reason="stand-in stages", stub=True)
    child = [_roll("Polder", 12, "tests/gate/hamletgen/test_driver.py::test_fanout", "r1", pid="4242", dt=62.0)]
    failures, lines = rollverdict.judge(child, _roster(("Polder", 12), in_process=(stub,)), full=True, renders_ok=set())
    assert failures == [], failures
    assert any("Polder seed=12: 1 roll(s)" in ln and "rostered" in ln for ln in lines), lines
    assert not any("stand-in stage rolls" in ln for ln in lines), "a child roll is not a stub"
    in_worker = [_roll("Polder", 12, "tests/gate/hamletgen/test_driver.py::test_fanout", "r1", pid=W, dt=62.0)]
    failures, _ = rollverdict.judge(in_worker, _roster(("Polder", 12), in_process=(stub,)), full=False, renders_ok=set())
    assert len(failures) == 1 and "excepted as a stub-stage module" in failures[0], "...and the in-worker one still is, and is still too slow"


# ---- feature 217: a roll earns its lines ----------------------------------------------------------


def _rolled_with_context(name: str, seed: int, test: str, ctx: str, pid: str = "99") -> dict[str, Any]:
    return {**_roll(name, seed, test, "r1", pid=pid), "context": ctx}


def test_a_rostered_roll_with_no_unique_line_fails_and_one_with_lines_is_printed() -> None:
    """FR-001: zero unique lines means the roll can go with 100% kept, so it must; a roll with lines passes and its
    count and lines are printed on the green run too."""
    roster = _roster(("Polder", 12))
    row = _rolled_with_context("Polder", 12, "tests/gate/a.py::t", "fixture:tests/gate/a.py::polder")
    failures, lines = rollverdict.judge([row], roster, full=True, renders_ok=set(), unique={"fixture:tests/gate/a.py::polder": []})
    assert len(failures) == 1 and "reaches NO engine line" in failures[0] and "tests/soak/" in failures[0] and "tests/rolls.py" in failures[0], failures
    assert any("lines only this roll reaches: 0" in ln for ln in lines)
    uniq = [("hamletgen/water.py", 12), ("hamletgen/water.py", 13), ("hamletgen/water.py", 14), ("hamletgen/water.py", 20), ("ways/route.py", 7)]
    failures, lines = rollverdict.judge([row], roster, full=True, renders_ok=set(), unique={"fixture:tests/gate/a.py::polder": uniq})
    assert failures == [], failures
    assert any("lines only this roll reaches: 5 - hamletgen/water.py:12-14,20; ways/route.py:7" in ln for ln in lines), lines


def test_a_roll_without_a_context_is_judged_under_its_test_s_run_context_and_an_unseen_context_is_not_judged() -> None:
    roster = _roster(("Polder", 12))
    plain = _roll("Polder", 12, "tests/gate/a.py::t", "r1")  # no context field: a census written before 217
    failures, lines = rollverdict.judge([plain], roster, full=True, renders_ok=set(), unique={"tests/gate/a.py::t|run": []})
    assert len(failures) == 1, "the test's own run context stands in"
    failures, lines = rollverdict.judge([plain], roster, full=True, renders_ok=set(), unique={"tests/other.py::t|run": []})
    assert failures == [] and not any("lines only this roll" in ln for ln in lines), "a context the database never saw is not judged"
    failures, lines = rollverdict.judge([plain], roster, full=True, renders_ok=set(), unique=None)
    assert failures == [] and not any("lines only this roll" in ln for ln in lines), "no database (make quick): not judged"


def test_the_pool_sweep_s_roll_of_a_shipped_generator_is_printed_and_never_judged() -> None:
    ref = types.SimpleNamespace(key=("Inashiro", 4), gen="pool/hamlets/inashiro/inashiro.gen.py", test="tests/full/test_villages.py::test_village_passes_gate")
    sweep = _rolled_with_context(
        "Inashiro", 4, "tests/full/test_villages.py::test_village_passes_gate[inashiro.gen.py]", "tests/full/test_villages.py::test_village_passes_gate[inashiro.gen.py]|run", pid="801"
    )
    failures, lines = rollverdict.judge([sweep], _roster(pool_gens=(ref,)), full=False, renders_ok=set(), unique={sweep["context"]: []})
    assert failures == [], failures
    assert any("lines only this roll reaches: 0 (the shipped generator's roll: printed, never judged)" in ln for ln in lines), lines
    # ...while the SAME spec's rostered roll (the immune test's perturbed reference) is judged
    immune = _rolled_with_context("Inashiro", 4, "tests/full/test_villages.py::test_a_map_is_immune", "tests/full/test_villages.py::test_a_map_is_immune|run", pid="802")
    failures, _ = rollverdict.judge([sweep, immune], _roster(("Inashiro", 4), pool_gens=(ref,)), full=False, renders_ok=set(), unique={sweep["context"]: [], immune["context"]: []})
    assert len(failures) == 1 and "test_a_map_is_immune" in failures[0]


def test_unique_by_context_reads_the_run_s_database_and_main_judges_with_it(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The arithmetic on a real coverage database, then `main` wiring it in: the roll's context reaches one engine
    line nothing else does -> green with the line printed; the same line reached by another context too -> red."""
    import coverage

    engine = "/repo/.claude/skills/diagram/l7r/diagram"
    census = tmp_path / "census.jsonl"
    monkeypatch.setenv(_census.ENV, str(census))
    census.write_text(json.dumps(_rolled_with_context("Inashiro", 4, "tests/gate/a.py::t", "tests/gate/a.py::t|run")) + "\n")
    monkeypatch.setattr(rollverdict, "run_db", lambda root: tmp_path / ".coverage")
    monkeypatch.setattr(rollverdict, "engine_changed", lambda root: True)
    assert rollverdict.unique_by_context(tmp_path / ".coverage") is None, "no database: not judged"

    def build(shared: bool) -> None:
        (tmp_path / ".coverage").unlink(missing_ok=True)
        data = coverage.CoverageData(basename=str(tmp_path / ".coverage"))
        data.set_context("tests/gate/a.py::t|run")
        data.add_lines({f"{engine}/hamletgen/sink.py": [10, 11, 12], f"{engine}/../../tests/x.py": [1]})
        data.set_context("tests/unit/test_w.py::t|run")
        data.add_lines({f"{engine}/hamletgen/sink.py": [10, 11] + ([12] if shared else [])})
        data.write()

    build(shared=False)
    assert rollverdict.unique_by_context(tmp_path / ".coverage") == {"tests/gate/a.py::t|run": [("hamletgen/sink.py", 12)], "tests/unit/test_w.py::t|run": []}
    assert rollverdict.main(["verdict"], root=tmp_path) == 0
    out = capsys.readouterr().out
    assert "lines only this roll reaches: 1 - hamletgen/sink.py:12" in out, out
    build(shared=True)
    assert rollverdict.main(["verdict"], root=tmp_path) == 1
    assert "reaches NO engine line" in capsys.readouterr().out


def test_a_gen_marked_roll_is_the_shipped_generator_s_whoever_requested_it() -> None:
    """Feature 217, found on its own first gate: a shipped generator's cold roll is requested by WHICHEVER reader of
    the pool's map comes first under worksteal - a gate module, not the sweep - and by requester alone it looked like
    the rostered roll and was judged. The gen child marks its record; the mark decides."""
    ref = types.SimpleNamespace(key=("Inashiro", 4), gen="pool/hamlets/inashiro/inashiro.gen.py", test="tests/full/test_villages.py::test_village_passes_gate")
    cold = {**_rolled_with_context("Inashiro", 4, "tests/full/hamletgen/test_driver.py::test_the_cli", "tests/full/hamletgen/test_driver.py::test_the_cli|run", pid="801"), "gen": ref.gen}
    immune = _rolled_with_context("Inashiro", 4, "tests/full/test_villages.py::test_a_map_is_immune", "tests/full/test_villages.py::test_a_map_is_immune|run", pid="802")
    unique = {cold["context"]: [], immune["context"]: [("pipeline/rollcache.py", 393)]}
    failures, lines = rollverdict.judge([cold, immune], _roster(("Inashiro", 4), pool_gens=(ref,)), full=False, renders_ok=set(), unique=unique)
    assert failures == [], failures
    assert any("printed, never judged" in ln for ln in lines) and any("lines only this roll reaches: 1 - pipeline/rollcache.py:393" in ln for ln in lines), lines
