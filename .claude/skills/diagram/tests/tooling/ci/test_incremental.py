"""The incremental gate's pure functions (feature 207) over synthetic data - the planner's arithmetic, apart from git and coverage.

The end-to-end proof on a fixture project is `tests/tooling/test_incremental_gate.py`; this file pins each rule the
plan and the merge apply, so a wrong selection is named by the rule that made it.
"""

from __future__ import annotations

import json
import os
import sqlite3
import types
from pathlib import Path

import pytest

from l7r.diagram.ci import incremental, selection


def test_changed_classifies_engine_tests_and_tooling() -> None:
    before = {"engine": {"e/a.py": "1", "e/b.py": "2", "pool/x.json": "9"}, "tests": {"t/test_a.py": "1", "t/conftest.py": "5", "t/_helper.py": "7"}, "tooling": "T"}
    now = {"engine": {"e/a.py": "1", "e/b.py": "3", "e/c.py": "4"}, "tests": {"t/test_a.py": "2", "t/test_new.py": "8", "t/conftest.py": "5", "t/_helper.py": "6"}, "tooling": "T"}
    ch = incremental.changed(before, now)
    assert ch.engine == ("e/b.py", "e/c.py", "pool/x.json") and ch.removed == ("pool/x.json",)
    assert ch.test_modules == ("t/test_a.py", "t/test_new.py") and ch.other_tests == ("t/_helper.py",) and not ch.tooling_moved
    assert incremental.changed(before, {**now, "tooling": "U"}).tooling_moved


def test_old_lines_changed_names_the_old_side_only() -> None:
    old = "a\nb\nc\nd\n"
    assert incremental.old_lines_changed(old, "a\nB\nc\nd\n") == {2}  # replaced
    assert incremental.old_lines_changed(old, "a\nc\nd\n") == {2}  # deleted
    assert incremental.old_lines_changed(old, "a\nb\nx\ny\nc\nd\n") == set()  # a pure insertion changes no old line
    assert incremental.old_lines_changed(old, old) == set()


def test_stale_tests_drops_changed_modules_and_vanished_ids_but_keeps_an_uncollected_module() -> None:
    baseline = ["t/test_a.py::x", "t/test_a.py::y", "t/test_b.py::p[1]", "t/test_b.py::p[2]", "t/test_c.py::z"]
    collected = ["t/test_a.py::x", "t/test_a.py::y", "t/test_b.py::p[1]"]  # p[2] vanished; test_c not collected at all
    gone = incremental.stale_tests(baseline, collected, ["t/test_a.py"])
    assert gone == {"t/test_a.py::x", "t/test_a.py::y", "t/test_b.py::p[2]"}


def test_fixture_closure_walks_dependents_transitively() -> None:
    dependents = {"roll": ["hamlet", "polder"], "hamlet": ["houses"], "houses": ["yards"], "other": ["x"]}
    assert incremental.fixture_closure(["roll"], dependents) == {"roll", "hamlet", "polder", "houses", "yards"}
    assert incremental.fixture_closure([], dependents) == set()


def test_keep_set_applies_the_four_rules() -> None:
    pl = {
        "affected_tests": ["t/test_a.py::hit"],
        "affected_fixtures": ["roll"],
        "changed_test_modules": ["t/test_m.py"],
        "baseline_tests": ["t/test_a.py::hit", "t/test_a.py::cold", "t/test_a.py::viaroll", "t/test_m.py::old"],
    }
    closures = {"t/test_a.py::viaroll": ["roll", "tmp_path"], "t/test_a.py::cold": ["tmp_path"]}
    collected = ["t/test_a.py::hit", "t/test_a.py::cold", "t/test_a.py::viaroll", "t/test_m.py::old", "t/test_m.py::new", "t/test_z.py::brand_new"]
    keep = selection.keep_set(pl, collected, closures)
    assert keep == {"t/test_a.py::hit", "t/test_a.py::viaroll", "t/test_m.py::old", "t/test_m.py::new", "t/test_z.py::brand_new"}


def _db(path: Path, rows: dict[str, dict[str, list[int]]]) -> Path:
    """A coverage-shaped sqlite file: {context: {abs file path: [lines]}}."""
    from coverage.numbits import nums_to_numbits

    con = sqlite3.connect(str(path))
    con.executescript(
        "create table file (id integer primary key, path text unique); create table context (id integer primary key, context text unique);"
        "create table line_bits (file_id integer, context_id integer, numbits blob, unique (file_id, context_id));"
        "create table arc (file_id integer, context_id integer, fromno integer, tono integer); create table tracer (file_id integer primary key, tracer text);"
        "create table meta (key text, value text, unique (key)); create table coverage_schema (version integer);"
    )
    con.execute("insert into coverage_schema values (7)")
    con.execute("insert into meta values ('has_arcs', '0')")
    for ctx, files in rows.items():
        con.execute("insert or ignore into context (context) values (?)", (ctx,))
        cid = con.execute("select id from context where context = ?", (ctx,)).fetchone()[0]
        for f, lines in files.items():
            con.execute("insert or ignore into file (path) values (?)", (f,))
            fid = con.execute("select id from file where path = ?", (f,)).fetchone()[0]
            con.execute("insert into line_bits values (?, ?, ?)", (fid, cid, nums_to_numbits(lines)))
    con.commit()
    con.close()
    return path


def test_contexts_touching_and_import_time_lines_read_the_db(tmp_path: Path) -> None:
    root = tmp_path
    db = _db(tmp_path / "c.db", {"": {str(root / "e/a.py"): [1, 2]}, "t::x|run": {str(root / "e/a.py"): [3]}, "fixture:f": {str(root / "e/b.py"): [1]}, "t::y|run": {str(root / "e/b.py"): [2]}})
    assert incremental.contexts_touching(db, root, ("e/a.py",)) == {"", "t::x|run"}
    assert incremental.contexts_touching(db, root, ("e/b.py",)) == {"fixture:f", "t::y|run"}
    assert incremental.contexts_touching(db, root, ()) == set()
    assert incremental.import_time_lines(db, root, "e/a.py") == {1, 2} and incremental.import_time_lines(db, root, "e/b.py") == set()


def test_prune_drops_files_and_contexts_in_place(tmp_path: Path) -> None:
    root = tmp_path
    db = _db(tmp_path / "c.db", {"": {str(root / "e/a.py"): [1]}, "t::x|run": {str(root / "e/a.py"): [3], str(root / "e/b.py"): [4]}, "t::y|run": {str(root / "e/b.py"): [2]}})
    incremental.prune(db, root, ("e/a.py",), {"t::y|run"})
    con = sqlite3.connect(str(db))
    files = {r[0] for r in con.execute("select path from file")}
    rows = con.execute("select f.path, c.context from line_bits l join file f on f.id = l.file_id join context c on c.id = l.context_id").fetchall()
    assert files == {str(root / "e/b.py")} and rows == [(str(root / "e/b.py"), "t::x|run")]
    assert set(incremental.all_contexts(db)) == {"", "t::x|run", "t::y|run"}  # the context rows stay; only their data goes


def test_fixture_graph_reads_the_reverse_edges() -> None:
    class FD:
        def __init__(self, argname: str, argnames: tuple[str, ...], baseid: str = "") -> None:
            self.argname, self.argnames, self.baseid = argname, argnames, baseid

    class Info:
        name2fixturedefs = {"hamlet": [FD("hamlet", ("roll",))], "houses": [FD("houses", ("hamlet",))], "roll": [FD("roll", ())]}

    class Item:
        _fixtureinfo = Info()

    class Bare:
        pass

    assert selection.fixture_graph([Item(), Bare()]) == {"hamlet": ["houses"], "roll": ["hamlet"]}  # type: ignore[list-item]


def test_a_fixture_is_identified_by_where_it_is_defined_so_two_modules_rolled_fixtures_stay_apart() -> None:
    """Feature 213 (the polder-only run of 2026-09-08): ten gate modules each define a `rolled` fixture, and keying the
    context by argument name alone gave them ONE context - a change one of their rolls touched selected every test
    behind any of them (18 specs re-rolled for a polder-only edit). The id is the definition site plus the name; a
    root-conftest fixture (no baseid) keeps its bare name, so the context-switch test above still reads `fixture:built`."""

    class FD:
        def __init__(self, argname: str, argnames: tuple[str, ...], baseid: str = "") -> None:
            self.argname, self.argnames, self.baseid = argname, argnames, baseid

    polder = FD("rolled", ("spec",), "tests/gate/test_water.py")
    inashiro = FD("rolled", (), "tests/gate/test_paddy_fabric.py")
    assert selection.fixture_id(polder) == "tests/gate/test_water.py::rolled"
    assert selection.fixture_id(FD("built", ())) == "built"

    class InfoA:
        name2fixturedefs = {"rolled": [polder], "spec": [FD("spec", (), "tests/gate")]}

    class InfoB:
        name2fixturedefs = {"rolled": [inashiro]}

    class ItemA:
        nodeid, fixturenames, _fixtureinfo = "tests/gate/test_water.py::t", ["rolled", "request"], InfoA()

    class ItemB:
        nodeid, fixturenames, _fixtureinfo = "tests/gate/test_paddy_fabric.py::t", ["rolled"], InfoB()

    assert selection.fixture_ids(ItemA()) == ["request", "tests/gate/test_water.py::rolled"], "a name with no definition (request) stays bare"
    assert selection.fixture_ids(ItemB()) == ["tests/gate/test_paddy_fabric.py::rolled"]
    assert selection.fixture_ids(types.SimpleNamespace(fixturenames=["b", "a"])) == ["a", "b"], "no fixture info: the names, as before"
    graph = selection.fixture_graph([ItemA(), ItemB()])  # type: ignore[list-item]
    assert graph == {"tests/gate::spec": ["tests/gate/test_water.py::rolled"]}, "edges are between ids, so the two rolled fixtures never meet"
    # and keep_set sees the two apart: an affected polder fixture selects A and not B
    pl = {"affected_tests": [], "affected_fixtures": ["tests/gate/test_water.py::rolled"], "changed_test_modules": [], "baseline_tests": [ItemA.nodeid, ItemB.nodeid]}
    closures = {ItemA.nodeid: selection.fixture_ids(ItemA()), ItemB.nodeid: selection.fixture_ids(ItemB())}
    assert selection.keep_set(pl, [ItemA.nodeid, ItemB.nodeid], closures) == {ItemA.nodeid}


def test_plan_dump_is_json_shaped() -> None:
    pl = incremental.Plan("full", "why")
    assert pl.dump()["mode"] == "full" and pl.dump()["full_fraction"] == incremental.FULL_FRACTION


@pytest.mark.parametrize("cmd", ["", "bogus"])
def test_main_usage(cmd: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert incremental.main([cmd] if cmd else [], tmp_path, tmp_path) == 2
    assert "usage" in capsys.readouterr().err


# ---- the plugin's hooks, driven in-process with plain fakes (the fixture-project run exercises them in a SUBPROCESS,
# which coverage does not see; these are the same lines, called directly) --------------------------------------------


class _Cov:
    def __init__(self) -> None:
        self.contexts: list[str] = []

    def switch_context(self, name: str) -> None:
        self.contexts.append(name)


class _Config:
    def __init__(self, cov: _Cov | None, worker: str | None = None) -> None:
        self._cov = cov
        self.deselected: list[list[str]] = []
        self.registered: list[tuple[object, str]] = []
        if worker is not None:
            self.workerinput = {"workerid": worker}

        class Hook:
            def pytest_deselected(_h, items: list) -> None:  # noqa: N805
                self.deselected.append([it.nodeid for it in items])

        self.hook = Hook()

        class PM:
            def get_plugin(_p, name: str):  # noqa: N805
                if name != "_cov" or cov is None:
                    return None

                class Ctl:
                    started = True

                class Plugin:
                    cov_controller = Ctl()

                Plugin.cov_controller.cov = cov  # type: ignore[attr-defined]
                return Plugin()

            def register(_p, plugin: object, name: str) -> None:  # noqa: N805
                self.registered.append((plugin, name))

        self.pluginmanager = PM()


class _Item:
    def __init__(self, nodeid: str, fixtures: tuple[str, ...] = (), config: _Config | None = None) -> None:
        self.nodeid = nodeid
        self.fixturenames = list(fixtures)
        self.config = config or _Config(None)


class _Session:
    pass


def _drive(gen) -> None:  # a hookwrapper generator: enter, then finish
    next(gen)
    with pytest.raises(StopIteration):
        next(gen)


def test_the_hooks_switch_the_coverage_context_around_a_fixture_and_back_to_the_phase() -> None:
    cov = _Cov()
    cfg = _Config(cov)
    plugin = selection.GateSelection(Path("/nowhere"), {"mode": "full", "reason": "r"}, {})
    item = _Item("t/test_a.py::x", config=cfg)
    _drive(plugin.pytest_runtest_setup(item))

    class FD:
        argname = "built"

    class Req:
        config = cfg

    _drive(plugin.pytest_fixture_setup(FD(), Req()))
    _drive(plugin.pytest_runtest_call(item))
    _drive(plugin.pytest_runtest_teardown(item))
    assert cov.contexts == ["t/test_a.py::x|setup", "fixture:built", "t/test_a.py::x|setup", "t/test_a.py::x|run", "t/test_a.py::x|teardown"]
    # with no coverage plugin running the fixture hook is a no-op
    _drive(selection.GateSelection(Path("/nowhere"), {"mode": "full", "reason": "r"}, {}).pytest_fixture_setup(FD(), type("R", (), {"config": _Config(None)})()))


def test_modifyitems_deselects_per_the_plan_and_writes_the_result_from_the_writer(tmp_path: Path) -> None:
    pl = {
        "mode": "incremental",
        "reason": "one file",
        "affected_tests": ["t/test_a.py::hit"],
        "affected_fixtures": [],
        "changed_test_modules": [],
        "baseline_tests": ["t/test_a.py::hit", "t/test_a.py::cold"],
        "full_fraction": 0.6,
    }
    plugin = selection.GateSelection(tmp_path, pl, {})
    items = [_Item("t/test_a.py::hit", ("tmp_path",)), _Item("t/test_a.py::cold")]
    session = _Session()
    selection.remember_all(session, items)  # type: ignore[arg-type]
    cfg = _Config(None)
    plugin.pytest_collection_modifyitems(session, cfg, items)  # type: ignore[arg-type]
    assert [it.nodeid for it in items] == ["t/test_a.py::hit"] and cfg.deselected == [["t/test_a.py::cold"]]
    result = json.loads((tmp_path / incremental.RESULT).read_text(encoding="utf-8"))
    assert result["mode"] == "incremental" and result["selected"] == ["t/test_a.py::hit"] and result["collected"] == ["t/test_a.py::hit", "t/test_a.py::cold"]
    nxt = json.loads((tmp_path / (incremental.TESTS + ".next")).read_text(encoding="utf-8"))
    assert nxt == {"t/test_a.py::hit": ["tmp_path"], "t/test_a.py::cold": []}, "the deselected item is remembered too"


def test_modifyitems_over_the_fraction_runs_everything_and_a_worker_other_than_gw0_writes_nothing(tmp_path: Path) -> None:
    pl = {
        "mode": "incremental",
        "reason": "many",
        "affected_tests": ["t::a", "t::b"],
        "affected_fixtures": [],
        "changed_test_modules": [],
        "baseline_tests": ["t::a", "t::b", "t::c"],
        "full_fraction": 0.5,
    }
    items = [_Item("t::a"), _Item("t::b"), _Item("t::c")]
    plugin = selection.GateSelection(tmp_path, pl, {})
    plugin.pytest_collection_modifyitems(_Session(), _Config(None, worker="gw3"), items)  # type: ignore[arg-type]
    assert len(items) == 3 and not (tmp_path / incremental.RESULT).exists(), "gw3 is not the writer"
    plugin.pytest_collection_modifyitems(_Session(), _Config(None, worker="gw0"), items)  # type: ignore[arg-type]
    result = json.loads((tmp_path / incremental.RESULT).read_text(encoding="utf-8"))
    assert result["mode"] == "full" and "fraction" in result["reason"] and len(result["selected"]) == 3


def test_an_empty_selection_turns_no_tests_ran_into_a_green_run(tmp_path: Path) -> None:
    plugin = selection.GateSelection(tmp_path, {"mode": "incremental", "reason": "nothing changed"}, {})

    class Sess:
        exitstatus = 5

    s = Sess()
    plugin.pytest_sessionfinish(s, 5)  # type: ignore[arg-type]
    assert s.exitstatus == 5, "no result file: not ours to overrule"
    (tmp_path / incremental.RESULT).write_text(json.dumps({"mode": "incremental", "selected": [], "collected": ["t::a"]}), encoding="utf-8")
    plugin.pytest_sessionfinish(s, 5)  # type: ignore[arg-type]
    assert s.exitstatus == 0
    s2 = Sess()
    (tmp_path / incremental.RESULT).write_text(json.dumps({"mode": "incremental", "selected": ["t::a"], "collected": ["t::a"]}), encoding="utf-8")
    plugin.pytest_sessionfinish(s2, 5)  # type: ignore[arg-type]
    assert s2.exitstatus == 5, "a selection that ran and reported 5 is a real 'no tests ran'"
    full = selection.GateSelection(tmp_path, {"mode": "full", "reason": "r"}, {})
    s3 = Sess()
    full.pytest_sessionfinish(s3, 5)  # type: ignore[arg-type]
    assert s3.exitstatus == 5


def test_configure_registers_the_plugin_with_the_plan_and_closures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / incremental.PLAN).write_text(
        json.dumps({"mode": "incremental", "reason": "r", "affected_tests": [], "affected_fixtures": [], "changed_test_modules": [], "baseline_tests": []}), encoding="utf-8"
    )
    (tmp_path / incremental.TESTS).write_text(json.dumps({"t::a": ["f"]}), encoding="utf-8")
    monkeypatch.setenv(selection.ENV, str(tmp_path))
    cfg = _Config(None)
    selection.configure(cfg)  # type: ignore[arg-type]
    ((plugin, name),) = cfg.registered
    assert name == "_l7r_gate_selection" and isinstance(plugin, selection.GateSelection) and plugin.closures == {"t::a": ["f"]}
    monkeypatch.setenv(selection.ENV, str(tmp_path / "empty"))
    (tmp_path / "empty").mkdir()
    cfg2 = _Config(None)
    selection.configure(cfg2)  # type: ignore[arg-type]
    assert cfg2.registered[0][0].plan["mode"] == "full"  # type: ignore[attr-defined]


def test_the_shim_delegates_only_under_the_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import importlib

    from l7r.diagram.ci import gate_plugin

    # At the gate this module was imported by `-p` BEFORE coverage started, so its five import-time lines
    # were never recorded; a reload re-runs them under coverage. pluggy keeps the hook objects it registered.
    importlib.reload(gate_plugin)
    monkeypatch.delenv(selection.ENV, raising=False)
    cfg = _Config(None)
    gate_plugin.pytest_configure(cfg)
    gate_plugin.pytest_collection_modifyitems(_Session(), cfg, [])
    assert cfg.registered == []
    monkeypatch.setenv(selection.ENV, str(tmp_path))
    gate_plugin.pytest_configure(cfg)
    s = _Session()
    gate_plugin.pytest_collection_modifyitems(s, cfg, [_Item("t::a")])
    assert len(cfg.registered) == 1 and [it.nodeid for it in s._l7r_all_items] == ["t::a"]  # type: ignore[attr-defined]


# ---- the planner's remaining branches ------------------------------------------------------------------------------


def test_blob_ids_of_nothing_is_empty(tmp_path: Path) -> None:
    assert incremental._blob_ids(tmp_path, []) == {}


def test_plan_forced_full_and_the_nothing_changed_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pl = incremental.plan(tmp_path, "because")
    assert pl.mode == "full" and pl.reason == "because"
    bdir = tmp_path / "gb"
    bdir.mkdir()
    monkeypatch.setattr(incremental, "baseline_dir", lambda root: bdir)
    man = {"engine": {"e/a.py": "1"}, "tests": {"t/test_a.py": "1"}, "tooling": "T"}
    (bdir / incremental.MANIFEST).write_text(json.dumps(man), encoding="utf-8")
    (bdir / incremental.COVERAGE_DB).write_bytes(b"")
    (bdir / incremental.TESTS).write_text(json.dumps({"t/test_a.py::x": []}), encoding="utf-8")
    monkeypatch.setattr(incremental, "manifest", lambda root: man)
    pl = incremental.plan(tmp_path)
    assert pl.mode == "incremental" and "nothing" in pl.reason and pl.baseline_tests == ["t/test_a.py::x"]


def test_import_time_change_skips_removed_new_and_never_imported_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path
    db = _db(tmp_path / "c.db", {"": {str(root / "e/a.py"): [1]}})
    before = {"engine": {"e/a.py": "sha", "e/b.py": "sha2"}}
    # b.py is not in the import-time context; a.py is removed; c.py is new; nothing reaches `git cat-file`
    ch = incremental.Changed(engine=("e/a.py", "e/b.py", "e/c.py"), removed=("e/a.py",), test_modules=(), other_tests=(), tooling_moved=False)
    assert incremental.import_time_change(root, db, before, ch) is None


def test_main_where_mode_and_selected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    bdir = tmp_path / "gb"
    monkeypatch.setattr(incremental, "baseline_dir", lambda root: bdir)
    assert incremental.main(["where"], tmp_path, tmp_path) == 0 and capsys.readouterr().out.strip() == str(bdir)
    assert incremental.main(["selected"], tmp_path, tmp_path) == 0 and capsys.readouterr().out.strip() == ""
    bdir.mkdir()
    (bdir / incremental.RESULT).write_text(json.dumps({"mode": "incremental", "selected": ["a", "b"], "collected": ["a", "b", "c"]}), encoding="utf-8")
    assert incremental.main(["mode"], tmp_path, tmp_path) == 0 and capsys.readouterr().out.strip() == "incremental"
    assert incremental.main(["selected"], tmp_path, tmp_path) == 0 and capsys.readouterr().out.strip() == "2/3"
    assert incremental.main(["save-baseline"], tmp_path, tmp_path) == 0 and "stays" in capsys.readouterr().out


def test_switch_exports_the_context_so_a_coverage_child_can_label_its_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 213: a roll made in a child recorded the engine's lines under NO context, so the polder-only
    incremental run selected 46 unit tests and not one polder gate test (the floor then re-rolled both polder
    subjects). `switch` now exports the context it set; `rollcache._in_child` and `gencache.gate_obtain` pass it
    to `coverage run --context=`, and the baseline sees the roll under its requester."""
    from l7r.diagram import _census

    monkeypatch.delenv(_census.CONTEXT_ENV, raising=False)
    cov = _Cov()
    selection.switch(cov, "fixture:built")
    assert os.environ[_census.CONTEXT_ENV] == "fixture:built"
    selection.switch(cov, "t/test_a.py::x|run")
    assert os.environ[_census.CONTEXT_ENV] == "t/test_a.py::x|run"
