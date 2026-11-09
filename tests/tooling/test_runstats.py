"""The gate's run stats (GM 2026-10-03): first and last failure times and the host's figures, read from
fake /proc and /sys trees so every field and every absence is pinned without depending on this machine.

No `tooling` marker: it calls functions over temporary files, it runs no make, git or subprocess.
"""

from __future__ import annotations

import importlib.util
import pathlib
import types

import pytest

from tests import _gate_failures

REPO = pathlib.Path(__file__).resolve().parents[2]
SKILL = pathlib.Path(__file__).resolve().parents[2]


def test_a_failed_report_is_marked_and_a_pass_is_not(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    path = str(tmp_path / "gate-failures")
    assert _gate_failures.mark(types.SimpleNamespace(failed=True), path)
    assert not _gate_failures.mark(types.SimpleNamespace(failed=False), path)
    assert not _gate_failures.mark(types.SimpleNamespace(failed=True), None)
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw0")
    assert not _gate_failures.mark(types.SimpleNamespace(failed=True), path)
    assert pathlib.Path(path).read_text().count(" test\n") == 1


def test_the_hooks_mark_into_the_file_the_gate_named(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    monkeypatch.setattr(_gate_failures, "_PATH", str(tmp_path / "gate-failures"))
    _gate_failures.pytest_runtest_logreport(types.SimpleNamespace(failed=True))
    _gate_failures.pytest_collectreport(types.SimpleNamespace(failed=True))
    assert (tmp_path / "gate-failures").read_text().count(" test\n") == 2


def test_the_gate_variable_is_not_left_for_child_processes() -> None:
    """A fixture repository's own pytest, failing on purpose, must not mark into this gate."""
    import os

    assert "L7R_GATE_FAILURES" not in os.environ


def test_the_gate_wires_the_stats_into_every_entry_it_writes() -> None:
    """The start snapshot, the export pytest reads, a mark per failed phase, and the stats on each entry."""
    recipe = (SKILL / "Makefile").read_text().split("\ndone:", 1)[1].split("\ntest-full:", 1)[0]
    makefile = (SKILL / "Makefile").read_text()
    assert "**json.loads(os.environ.get('RUN_STATS') or '{}')" in makefile.split("LOGRUN = ", 1)[1].split("\n\n", 1)[0]
    assert '$(RUNSTATS) start "$$G"' in recipe and 'export L7R_GATE_FAILURES="$$G/gate-failures"' in recipe
    # Two phase loops and the reference step mark their failures.
    assert recipe.count('$(RUNSTATS) fail "$$G"') == 3
    # Each LOGRUN that follows a run (two failure paths, the reference failure, the moved tree, green) carries the stats.
    assert recipe.count('RUN_STATS="$$($(RUNSTATS) end "$$G" 2>/dev/null)" ') == 5


def test_a_mark_carries_its_tests_id(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385: the mark names the failed test (`report.nodeid`), so the run record can."""
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    path = tmp_path / "gate-failures"
    assert _gate_failures.mark(types.SimpleNamespace(failed=True, nodeid="tests/test_a.py::test_b"), str(path))
    assert path.read_text().endswith(" test tests/test_a.py::test_b\n")


def test_a_coverage_report_that_errors_is_named_in_the_run_record() -> None:
    """The round arbiter's tooling fix on red-gate@2026-10-18T21:00:44Z (feature 388): `coverage report` stopped at "No source
    for code" on a deleted module, listed no row, and the red gate's record named nothing. The error is a mark of its own."""
    _um = importlib.util.spec_from_file_location("uncovered_marks", REPO / "scripts/measure/uncovered_marks.py")
    assert _um is not None and _um.loader is not None
    um = importlib.util.module_from_spec(_um)
    _um.loader.exec_module(um)
    out = "Name  Stmts\nNo source for code: '/x/l7r/gone.py'; see https://coverage.readthedocs.io/x\n"
    assert um.errors(out) == ["coverage-error No source for code: '/x/l7r/gone.py'; see https://coverage.readthedocs.io/x"]
    assert um.errors("Name   Stmts   Miss\nTOTAL  1  0\n") == []
