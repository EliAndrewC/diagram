"""The incremental gate's pure functions (feature 207) over synthetic data - the planner's arithmetic, apart from git and coverage.

The end-to-end proof on a fixture project is `tests/tooling/test_incremental_gate.py`; this file pins each rule the
plan and the merge apply, so a wrong selection is named by the rule that made it.
"""

from __future__ import annotations

import sqlite3
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
        def __init__(self, argnames: tuple[str, ...]) -> None:
            self.argnames = argnames

    class Info:
        name2fixturedefs = {"hamlet": [FD(("roll",))], "houses": [FD(("hamlet",))], "roll": [FD(())]}

    class Item:
        _fixtureinfo = Info()

    class Bare:
        pass

    assert selection.fixture_graph([Item(), Bare()]) == {"hamlet": ["houses"], "roll": ["hamlet"]}  # type: ignore[list-item]


def test_plan_dump_is_json_shaped() -> None:
    pl = incremental.Plan("full", "why")
    assert pl.dump()["mode"] == "full" and pl.dump()["full_fraction"] == incremental.FULL_FRACTION


@pytest.mark.parametrize("cmd", ["", "bogus"])
def test_main_usage(cmd: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert incremental.main([cmd] if cmd else [], tmp_path, tmp_path) == 2
    assert "usage" in capsys.readouterr().err
