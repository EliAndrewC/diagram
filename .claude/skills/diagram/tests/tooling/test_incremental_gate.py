"""THE INCREMENTAL GATE, PROVED ON A FIXTURE PROJECT (feature 207, spec FR-014).

A tiny engine (`eng/`) and suite under a git repo shaped like this one, run through the REAL planner
(`l7r.diagram.ci.incremental`), the REAL plugin (`-p l7r.diagram.ci.gate_plugin`, under xdist) and the real
merge, then judged by `coverage report --fail-under=100` exactly as the Makefile does. Five shapes:

  (a) a changed function with a new uncovered line FAILS;
  (b) deleting the only test that covered a line FAILS;
  (c) a change that makes a line of an UNCHANGED module unreachable FAILS - the test that reached it re-runs;
  (d) an unrelated edit selects only the tests that executed it, and the merged report is 100%;
  (e) each fallback rule fires on its shape (no baseline, a conftest edit, a non-Python engine file, the
      tooling hash, an import-time line, the 60% fraction);
  and the coverage-core proof: the fast core with re-armed events records the same per-context lines as the C tracer.

The fixture engine's session fixture `built` is what makes (a) and (c) honest: it executes `core.py` once,
under the first test that asks, and two test modules read what it built. Eight tests, so that the four polder
tests (d) and the four `built` readers (a) each sit at 50%, under the 60% fraction the plugin falls back at.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from l7r.diagram.ci import incremental

pytestmark = pytest.mark.tooling

HERE = Path(__file__).resolve()
SKILL = HERE.parents[2]
REPO_ROOT = SKILL.parents[2]
S = ".claude/skills/diagram"

CORE = '''from eng import tool


def add(a, b):
    return a + b


def build():
    return {"n": add(1, 2), "deep": tool.deep(3)}
'''
POLDER = '''def dike(n):
    if n > 2:
        return "long"
    return "short"
'''
TOOL = '''def deep(x):
    return x * 2


def shallow(x):
    return x + 1
'''
CONFTEST = '''import pytest
from eng import core


@pytest.fixture(scope="session")
def built():
    return core.build()
'''
TEST_CORE = '''from eng import core


def test_add(built):
    assert built["n"] == 3 and core.add(2, 2) == 4
'''
TEST_TOOL = '''from eng import tool


def test_shallow(built):
    assert tool.shallow(1) == 2 and built["deep"] == 6


def test_shallow_again(built):
    assert tool.shallow(2) == 3 and built["n"] == 3


def test_shallow_thrice(built):
    assert tool.shallow(3) == 4 and "deep" in built
'''
TEST_POLDER = '''import pytest
from eng import polder


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_dike(n):
    assert polder.dike(n) in ("long", "short")
'''
PYPROJECT = '''[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ""

[tool.coverage.run]
source = ["eng"]
omit = ["*/tests/*"]

[tool.coverage.report]
show_missing = true
'''


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def project(tmp_path: Path) -> tuple[Path, Path]:
    """A repo shaped like this one - scripts/gate-stamp.py, the skill dir - with a tiny engine and suite."""
    root = tmp_path / "clone"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    (root / "scripts").mkdir()
    shutil.copyfile(REPO_ROOT / "scripts" / "gate-stamp.py", root / "scripts" / "gate-stamp.py")
    skill = root / S
    (skill / "eng").mkdir(parents=True)
    (skill / "eng" / "__init__.py").write_text("", encoding="utf-8")
    (skill / "eng" / "core.py").write_text(CORE, encoding="utf-8")
    (skill / "eng" / "polder.py").write_text(POLDER, encoding="utf-8")
    (skill / "eng" / "tool.py").write_text(TOOL, encoding="utf-8")
    (skill / "tests").mkdir()
    (skill / "tests" / "conftest.py").write_text(CONFTEST, encoding="utf-8")
    (skill / "tests" / "test_core.py").write_text(TEST_CORE, encoding="utf-8")
    (skill / "tests" / "test_tool.py").write_text(TEST_TOOL, encoding="utf-8")
    (skill / "tests" / "test_polder.py").write_text(TEST_POLDER, encoding="utf-8")
    (skill / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")
    (skill / "Makefile").write_text("all:\n\t@true\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    return root, skill


PYTEST = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "l7r.diagram.ci.gate_plugin", "--cov", "--cov-context=test", "tests"]


def gate_env(bdir: Path, core: str | None = None) -> dict[str, str]:
    """The environment the Makefile's floored run sets: the baseline directory. `core` pins a coverage core for
    the comparison test; the gate itself runs the default (fast) core, whose events the plugin re-arms."""
    env = {**os.environ, "L7R_GATE_SELECT": str(bdir), "PYTHONPATH": str(SKILL)}
    env.pop("L7R_VIA_MAKE", None)
    env.pop("COVERAGE_CORE", None)
    if core:
        env["COVERAGE_CORE"] = core
    return env


def run_gate(root: Path, skill: Path, force_full: str | None = None) -> tuple[str, dict, int, str]:
    """One gate test phase as the Makefile runs it: plan -> pytest (traced, contexts, the plugin, xdist) -> merge -> report.
    Returns (the plan's mode, the result the plugin wrote, the `coverage report --fail-under=100` exit code, its output)."""
    bdir = incremental.baseline_dir(root)
    argv = ["plan"] + (["full", force_full] if force_full else [])
    assert incremental.main(argv, root, skill) == 0
    proc = subprocess.run(PYTEST + ["-n", "2"], cwd=skill, env=gate_env(bdir), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads((bdir / incremental.RESULT).read_text(encoding="utf-8"))
    assert incremental.main(["merge"], root, skill) == 0
    report = subprocess.run([sys.executable, "-m", "coverage", "report", "--fail-under=100"], cwd=skill, capture_output=True, text=True)
    plan = json.loads((bdir / incremental.PLAN).read_text(encoding="utf-8"))
    return plan["mode"], result, report.returncode, report.stdout


def baseline(root: Path, skill: Path) -> None:
    mode, result, rc, out = run_gate(root, skill)
    assert mode == "full" and result["mode"] == "full" and rc == 0, out
    assert incremental.main(["save-baseline"], root, skill) == 0
    bdir = incremental.baseline_dir(root)
    assert (bdir / incremental.COVERAGE_DB).is_file() and (bdir / incremental.MANIFEST).is_file() and (bdir / incremental.TESTS).is_file()


def write(skill: Path, rel: str, text: str) -> None:
    (skill / rel).write_text(text, encoding="utf-8")


# ---- the coverage core --------------------------------------------------------------------------------------


def _context_lines(db: Path) -> dict[tuple[str, str], frozenset[int]]:
    import sqlite3

    from coverage.numbits import numbits_to_nums

    con = sqlite3.connect(str(db))
    try:
        rows = con.execute("select c.context, f.path, l.numbits from line_bits l join file f on f.id = l.file_id join context c on c.id = l.context_id").fetchall()
    finally:
        con.close()
    return {(c, os.path.basename(f)): frozenset(numbits_to_nums(n)) for c, f, n in rows}


def test_the_fast_core_keeps_every_context_once_its_events_are_re_armed(project: tuple[Path, Path]) -> None:
    """THE FINDING BEHIND `selection.switch` (measured 2026-09-07, spec D8). Python 3.14's default sys.monitoring
    core disables a line's event after its first hit - correct for plain line coverage, fatal for dynamic contexts:
    the second test to execute a line records nothing under its own context. With the plugin re-arming the events
    at every switch, the per-(context, file) line sets under sysmon EQUAL the C tracer's - here, 12 of 12 rows,
    `test_add|run` (whose only engine lines the `built` fixture hit first) included - at a fraction of the
    tracer's cost. If this ever fails, the fast core's behavior changed and the planner's selection is unsound."""
    root, skill = project
    bdir = incremental.baseline_dir(root)
    assert incremental.main(["plan"], root, skill) == 0
    got = {}
    for core in ("sysmon", "ctrace"):
        proc = subprocess.run(PYTEST + ["-n", "2"], cwd=skill, env=gate_env(bdir, core), capture_output=True, text=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        got[core] = _context_lines(skill / ".coverage")
    assert ("tests/test_core.py::test_add|run", "core.py") in got["sysmon"], sorted(got["sysmon"])
    assert got["sysmon"] == got["ctrace"], "the fast core with re-armed events records exactly what the C tracer records"


# ---- the baseline itself --------------------------------------------------------------------------------


def test_a_full_run_records_per_test_and_per_fixture_contexts_and_the_manifest(project: tuple[Path, Path]) -> None:
    root, skill = project
    baseline(root, skill)
    bdir = incremental.baseline_dir(root)
    contexts = set(incremental.all_contexts(bdir / incremental.COVERAGE_DB))
    assert "tests/test_core.py::test_add|run" in contexts and "fixture:tests::built" in contexts, sorted(
        contexts
    )  # the fixture is keyed by its definition site since feature 213 (tests/conftest.py -> baseid "tests")
    # the session fixture's execution of core.py is recorded under the FIXTURE, not under whichever test asked first
    touched = incremental.contexts_touching(bdir / incremental.COVERAGE_DB, root, (f"{S}/eng/core.py",))
    assert "fixture:tests::built" in touched
    tests = json.loads((bdir / incremental.TESTS).read_text(encoding="utf-8"))
    assert "tests::built" in tests["tests/test_tool.py::test_shallow"] and "tests::built" not in tests["tests/test_polder.py::test_dike[1]"]
    man = json.loads((bdir / incremental.MANIFEST).read_text(encoding="utf-8"))
    assert f"{S}/eng/core.py" in man["engine"] and f"{S}/tests/conftest.py" in man["tests"] and man["tooling"]


# ---- (d) an unrelated edit selects only what executed it --------------------------------------------------


def test_d_a_polder_only_edit_runs_only_the_polder_tests_and_the_merged_report_is_100(project: tuple[Path, Path]) -> None:
    root, skill = project
    baseline(root, skill)
    write(skill, "eng/polder.py", POLDER.replace('return "short"', 'return "short"  # a comment inside the body'))
    mode, result, rc, out = run_gate(root, skill)
    assert mode == "incremental" and result["mode"] == "incremental"
    assert set(result["selected"]) == {f"tests/test_polder.py::test_dike[{n}]" for n in (1, 2, 3, 4)}, result["selected"]
    assert rc == 0, out


# ---- (a) a changed function with a new uncovered line fails ------------------------------------------------


def test_a_an_uncovered_line_in_a_changed_function_fails_the_merged_floor(project: tuple[Path, Path]) -> None:
    root, skill = project
    baseline(root, skill)
    write(skill, "eng/core.py", CORE.replace("    return a + b\n", "    if a > 100:\n        return 100\n    return a + b\n"))
    mode, result, rc, out = run_gate(root, skill)
    assert mode == "incremental"
    # its own test, AND the test that only reads what the `built` fixture made from core.py
    assert set(result["selected"]) == {"tests/test_core.py::test_add", "tests/test_tool.py::test_shallow", "tests/test_tool.py::test_shallow_again", "tests/test_tool.py::test_shallow_thrice"}, result[
        "selected"
    ]
    assert rc != 0 and "core.py" in out, out


# ---- (b) deleting the only test that covered a line fails ------------------------------------------------


def test_b_deleting_the_only_covering_test_fails(project: tuple[Path, Path]) -> None:
    root, skill = project
    baseline(root, skill)
    write(skill, "tests/test_polder.py", TEST_POLDER.replace("[1, 2, 3, 4]", "[3, 4]"))  # `dike` never returns "short" now
    mode, result, rc, out = run_gate(root, skill)
    assert mode == "incremental" and set(result["selected"]) == {"tests/test_polder.py::test_dike[3]", "tests/test_polder.py::test_dike[4]"}
    assert rc != 0 and "polder.py" in out, out


# ---- (c) an unchanged module's line made unreachable fails --------------------------------------------------


def test_c_a_line_of_an_unchanged_module_made_unreachable_fails(project: tuple[Path, Path]) -> None:
    root, skill = project
    baseline(root, skill)
    # core no longer calls tool.deep(); tool.py is untouched, and nothing else reaches deep()
    write(skill, "eng/core.py", CORE.replace('"deep": tool.deep(3)', '"deep": 6'))
    write(skill, "tests/test_tool.py", TEST_TOOL)  # unchanged bytes - rewritten to prove that does not select it
    mode, result, rc, out = run_gate(root, skill)
    assert mode == "incremental"
    assert rc != 0 and "tool.py" in out, out


# ---- (e) the fallbacks ---------------------------------------------------------------------------------------


def test_e_no_baseline_is_a_full_run(project: tuple[Path, Path]) -> None:
    root, skill = project
    pl = incremental.plan(root)
    assert pl.mode == "full" and "no baseline" in pl.reason


@pytest.mark.parametrize(
    ("rel", "text", "why"),
    [
        ("tests/conftest.py", CONFTEST + "\n# edited\n", "non-module file under tests/"),
        ("pool/hamlets/x/x.json", "{}", "not Python"),
        ("Makefile", "all:\n\t@echo changed\n", "tooling changed"),
        ("eng/core.py", CORE.replace("def add(a, b):", "def add(a, b, c=0):"), "import time"),
    ],
    ids=["conftest", "manifest", "tooling", "import-time-def-line"],
)
def test_e_each_fallback_shape_forces_a_full_run(project: tuple[Path, Path], rel: str, text: str, why: str) -> None:
    root, skill = project
    baseline(root, skill)
    (skill / rel).parent.mkdir(parents=True, exist_ok=True)
    write(skill, rel, text)
    pl = incremental.plan(root)
    assert pl.mode == "full" and why in pl.reason, pl


def test_e_over_the_fraction_the_plugin_runs_everything_and_marks_the_run_full(project: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    root, skill = project
    baseline(root, skill)
    write(skill, "eng/polder.py", POLDER.replace('return "short"', 'return "short"  # edited'))
    monkeypatch.setattr(incremental, "FULL_FRACTION", 0.1)  # the knob travels in the plan, which is how the plugin (a subprocess) sees it
    bdir = incremental.baseline_dir(root)
    assert incremental.main(["plan"], root, skill) == 0
    pl = json.loads((bdir / incremental.PLAN).read_text(encoding="utf-8"))
    assert pl["mode"] == "incremental" and pl["full_fraction"] == 0.1
    proc = subprocess.run(PYTEST, cwd=skill, env=gate_env(bdir), capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads((bdir / incremental.RESULT).read_text(encoding="utf-8"))
    assert result["mode"] == "full" and "fraction" in result["reason"] and len(result["selected"]) == 8, result
    assert "8 passed" in proc.stdout


def test_nothing_changed_selects_nothing_and_the_run_is_green_on_the_untouched_baseline(project: tuple[Path, Path]) -> None:
    """The gate's cheapest shape after the short-circuit: the tree equals the baseline, so nothing is selected,
    pytest would say "no tests ran" (exit 5), the plugin turns that into a green run, and the merged floors judge
    the baseline as it stands."""
    root, skill = project
    baseline(root, skill)
    mode, result, rc, out = run_gate(root, skill)
    assert mode == "incremental" and result["selected"] == [] and rc == 0, out


def test_an_incremental_run_never_writes_the_baseline(project: tuple[Path, Path]) -> None:
    root, skill = project
    baseline(root, skill)
    bdir = incremental.baseline_dir(root)
    before = (bdir / incremental.COVERAGE_DB).read_bytes()
    write(skill, "eng/polder.py", POLDER.replace('return "short"', 'return "short"  # edited'))
    mode, _result, rc, _out = run_gate(root, skill)
    assert mode == "incremental" and rc == 0
    assert incremental.main(["save-baseline"], root, skill) == 0
    assert (bdir / incremental.COVERAGE_DB).read_bytes() == before, "spec D1: the baseline is the last FULL run"


def test_mode_reports_the_run_that_happened(project: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    root, skill = project
    assert incremental.main(["mode"], root, skill) == 0 and capsys.readouterr().out.strip() == "full"
    baseline(root, skill)
    capsys.readouterr()
    assert incremental.main(["mode"], root, skill) == 0 and capsys.readouterr().out.strip() == "full"
    assert incremental.main(["nonsense"], root, skill) == 2
