"""The type checker is pyrefly, one-shot (feature 142, GM 2026-08-28). Two facts the gate must keep true:
the checker can actually fail a target (a tool that silently passes everything is worse than none), and
its file list is the SAME list `[tool.mypy]` checks - mypy stays installed as the cross-check until the
GM rules on removing it (spec FR-007b), and two lists that drift would check two different engines.
The spec asks for exactly one planted-error test, not a per-rule harness: the report records what each
rule enforces (research 142 R3)."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2]


def _pyproject() -> dict[str, object]:
    return tomllib.loads((SKILL / "pyproject.toml").read_text())["tool"]  # type: ignore[no-any-return]


@pytest.mark.tooling
def test_pyrefly_checks_the_same_files_mypy_does() -> None:
    tool = _pyproject()
    assert tool["pyrefly"]["project-includes"] == tool["mypy"]["files"]  # type: ignore[index]


@pytest.mark.tooling
def test_pyrefly_fails_a_planted_type_error_under_the_projects_rules(tmp_path: Path) -> None:
    """One planted error - a wrong argument type - through the project's own `[tool.pyrefly.errors]`,
    so the rules the gate runs are the rules under test, not pyrefly's defaults."""
    errors = _pyproject()["pyrefly"]["errors"]  # type: ignore[index]
    rules = "\n".join(f"{k} = {str(v).lower()}" for k, v in errors.items())  # type: ignore[union-attr]
    (tmp_path / "pyproject.toml").write_text(f'[tool.pyrefly]\nproject-includes = ["bad.py", "good.py"]\n[tool.pyrefly.errors]\n{rules}\n')
    (tmp_path / "good.py").write_text("def f(x: int) -> int:\n    return x + 1\n")
    (tmp_path / "bad.py").write_text('def f(x: int) -> int:\n    return x + 1\n\nf("not an int")\n')
    run = subprocess.run(["pyrefly", "check"], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode != 0, run.stdout + run.stderr
    assert "bad-argument-type" in run.stdout + run.stderr
    assert "good.py" not in run.stdout, "the clean file must not be blamed"
