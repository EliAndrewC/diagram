"""The marker census runs in `make quick` when tests change (the round arbiter's tooling fix on red-gate@2026-10-12T16:26:46Z,
feature 374 batch 10: new soak tests that roll a map lacked `rolls_map`, and only the gate's full run found it)."""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _quick_recipe() -> str:
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("quick:"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i] and not lines[i].startswith(("\t", "##")))
    return "\n".join(lines[start:end])


def test_quick_runs_the_marker_census_when_tests_change() -> None:
    """...ON A TEST FILE CHANGED SINCE THE LAST QUICK (feature 444 T36, measured 2026-11-07: keyed on the branch's delta against main,
    the 2 s whole-tree census ran on every quick of every working branch): a test file - a new soak test among them, the case the
    arbiter's fix was for - newer than `.testmondata`, or no record, or ALL=1."""
    recipe = _quick_recipe()
    line = next(ln for ln in recipe.splitlines() if "tests/test_markers.py" in ln and "-newer .testmondata" in ln)
    assert "find tests -name '*.py'" in line and "[ ! -f .testmondata ]" in line and "exit 1" in line, "the census refuses quick, on a test changed since the last"
