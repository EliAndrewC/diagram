"""`scripts/gates/cover_changed.py` (feature 430 T03, D3): every line of each changed module, with the floor's tests and its
carried coverage - not only the lines a change added."""

import importlib.util
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "gates" / "cover_changed.py"
_spec = importlib.util.spec_from_file_location("cover_changed", SCRIPT)
assert _spec and _spec.loader
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args], capture_output=True, text=True, check=True).stdout


MOD = "def f(x):\n    return x + 1\n\n\ndef g(x):\n    y = x * 2\n    return y\n"
TESTS = "from l7r.m import f, g\n\n\ndef test_f():\n    assert f(1) == 2\n\n\ndef test_g():\n    assert g(1) == 2\n"


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, str]:
    """A tree with one engine module and its mirrored tests, committed as the base."""
    _git(tmp_path, "init", "-q")
    (tmp_path / "l7r").mkdir()
    (tmp_path / "l7r" / "m.py").write_text(MOD)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_m.py").write_text(TESTS)
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "base")
    return tmp_path, _git(tmp_path, "rev-parse", "HEAD").strip()


def test_an_existing_line_that_lost_its_test_is_named(repo: tuple[Path, str]) -> None:
    """Research R1: every line 2026-10-26's coverage reds named was an EXISTING line of a changed module whose test went with its
    pass - the first form, which asked only ADDED lines, named none. Here `f` changes, `g`'s test is deleted: `g`'s lines are
    named though the change added none of them."""
    root, base = repo
    (root / "l7r" / "m.py").write_text(MOD.replace("x + 1", "x + 1  # changed"))
    (root / "tests" / "test_m.py").write_text(TESTS.split("\n\n\ndef test_g")[0] + "\n")
    assert cc.changed_modules(root, base) == ["l7r/m.py"]
    assert cc.uncovered(root, ["l7r/m.py"], None) == {"l7r/m.py": [6, 7]}


def test_an_unchanged_module_is_not_asked(repo: tuple[Path, str]) -> None:
    """The narrowing the spec states (FR-009): a line lost in a module the change did not touch is the gate's to name."""
    root, base = repo
    (root / "tests" / "test_m.py").write_text(TESTS.split("\n\n\ndef test_g")[0] + "\n")
    assert cc.changed_modules(root, base) == []


def _baseline_db(path: Path, rows: dict[str, dict[str, list[int]]]) -> Path:
    from coverage.numbits import nums_to_numbits

    con = sqlite3.connect(str(path))
    con.executescript(
        "create table file (id integer primary key, path text unique); create table context (id integer primary key, context text unique);"
        "create table line_bits (file_id integer, context_id integer, numbits blob, unique (file_id, context_id));"
    )
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


def test_the_floors_carried_coverage_is_honored_only_for_unrun_contexts_and_unchanged_lines(repo: tuple[Path, str]) -> None:
    """A line the baseline shows a roll reaching (a context this run did not run) is the floor's carried coverage - unless the
    line changed, or the context is one this run ran (then its loss is real)."""
    root, _base = repo
    blob = _git(root, "rev-parse", "HEAD:l7r/m.py").strip()
    now = "# a new first line\n" + MOD.replace("y = x * 2", "y = x * 3")
    (root / "l7r" / "m.py").write_text(now)
    db = _baseline_db(root / "c.db", {"tests/gate/test_roll.py::test_r|run": {str(root / "l7r/m.py"): [5, 6, 7]}, "tests/test_m.py::test_g|run": {str(root / "l7r/m.py"): [7]}})
    (root / "tests" / "gate").mkdir()
    (root / "tests" / "gate" / "test_roll.py").write_text("x = 1\n")
    tests = {m: _git(root, "hash-object", m).strip() for m in ("tests/gate/test_roll.py", "tests/test_m.py")}
    base = (db, {"engine": {"l7r/m.py": blob}, "tests": tests})
    # old 5 (def g) -> new 6; old 6 changed (x * 3) -> not carried; old 7 -> new 8
    assert cc.carried(root, "l7r/m.py", base, ran=set()) == {6, 8}
    assert cc.carried(root, "l7r/m.py", base, ran={"tests/gate/test_roll.py::test_r"}) == {8}, "test_g's context still carries 7"
    assert cc.carried(root, "l7r/m.py", base, ran={"tests/gate/test_roll.py::test_r", "tests/test_m.py::test_g"}) == set()
    (root / "tests" / "test_m.py").write_text(TESTS.split("\n\n\ndef test_g")[0] + "\n")
    assert cc.carried(root, "l7r/m.py", base, ran={"tests/gate/test_roll.py::test_r"}) == set(), "test_g was deleted: it carries nothing"


def test_the_floors_tests_include_every_baseline_context_that_touched_the_module(repo: tuple[Path, str]) -> None:
    root, _base = repo
    (root / "tests" / "gate").mkdir()
    (root / "tests" / "gate" / "test_far.py").write_text("x = 1\n")
    db = _baseline_db(root / "c.db", {"tests/gate/test_far.py::test_x|run": {str(root / "l7r/m.py"): [1]}, "fixture:built|setup": {str(root / "l7r/m.py"): [1]}})
    assert cc.selected_tests(root, ["l7r/m.py"], (db, {})) == ["tests", "tests/gate/test_far.py"]


def test_the_tooling_tests_are_counted_exactly_when_the_floor_counts_them(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The sixth red (9a157cc4b): on a FULL plan with the tooling unchanged the floor deselects the tooling-marked tests
    (`tests/conftest.py`), and the first form of the check forced them in. An incremental plan keeps them."""
    sys.path.insert(0, str(SCRIPT.parents[2]))
    from l7r.diagram.ci import incremental

    base = (tmp_path / "c.db", {})
    monkeypatch.setattr(cc, "tooling_unchanged", lambda root: True)
    monkeypatch.setattr(incremental, "plan", lambda root: incremental.Plan("full", "x"))
    assert cc.floor_markers(tmp_path, base) == cc.WITHOUT_TOOLING
    assert cc.floor_markers(tmp_path, None) == cc.WITHOUT_TOOLING, "no baseline: the gate plans full"
    monkeypatch.setattr(incremental, "plan", lambda root: incremental.Plan("incremental", "x"))
    assert cc.floor_markers(tmp_path, base) == cc.WITH_TOOLING
    monkeypatch.setattr(cc, "tooling_unchanged", lambda root: False)
    monkeypatch.setattr(incremental, "plan", lambda root: incremental.Plan("full", "x"))
    assert cc.floor_markers(tmp_path, base) == cc.WITH_TOOLING, "tooling changed: the full gate runs them"
