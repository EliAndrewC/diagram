"""The function-length cap: 100 statements, ruff's count, held at the gate and the push (feature 370).

The GM, 2026-10-10: *"Please go with 100. And we can document why 100 is the number that we went with, like that it
is the second most common value on GitHub from our initial survey"* (`specs/370-function-length-gate/research.md`
R1), and *"I do like the idea of just doing that in our linter"*. These run the project's own ruff configuration and
`scripts/gates/check-function-cap.py` on fixture trees, so they prove the SETTING and the check, not a copy of either.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from tests._scripts import script

REPO = Path(__file__).resolve().parents[2]
CAP = 100
CHECK = script("check-function-cap.py")

_spec = importlib.util.spec_from_file_location("check_function_cap", CHECK)
assert _spec is not None and _spec.loader is not None
cfc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cfc)


def _function(n: int, suppress: str = "") -> str:
    """A module holding one function of exactly `n` statements (ruff counts the body's statements)."""
    return f"def f() -> None:{suppress}\n" + "".join(f"    x{i} = {i}\n" for i in range(n))


def _check(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECK), str(root)], capture_output=True, text=True, check=False)


@pytest.mark.parametrize(("n", "fails"), [(CAP, False), (CAP + 1, True)])
def test_the_project_config_fails_a_function_past_100_statements(tmp_path: Path, n: int, fails: bool) -> None:
    """SC-001 / FR-001: 101 statements fails, 100 passes, under the configuration `ruff check .` reads."""
    f = tmp_path / "one.py"
    f.write_text(_function(n))
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--no-cache", "--config", str(REPO / "pyproject.toml"), str(f)],
        capture_output=True,
        text=True,
        check=False,
        cwd=REPO,
    )
    assert ("PLR0915" in r.stdout) is fails, r.stdout
    if fails:
        assert f"({CAP + 1} > {CAP})" in r.stdout


@pytest.mark.parametrize("tree", ["l7r", "tests", "scripts", "pool", "tests/hooks"])
def test_the_check_names_a_long_function_with_both_ways_out_in_every_held_tree(tmp_path: Path, tree: str) -> None:
    """FR-002 / FR-008: every held tree, the fenced-out ones included, and the message carries the two ways out."""
    d = tmp_path / tree
    d.mkdir(parents=True)
    (d / "long.py").write_text(_function(CAP + 1))
    r = _check(tmp_path)
    assert r.returncode == 1
    assert f"{tree}/long.py:1" in r.stderr and f"(101 > {CAP})" in r.stderr
    assert "split it into parts at module or class level" in r.stderr
    assert "# noqa: PLR0915 <why the body must remain one>" in r.stderr


def test_a_tree_the_cap_does_not_hold_is_not_checked(tmp_path: Path) -> None:
    """The legacy pool and specs/ are write-once history (spec edge cases)."""
    for tree in ("legacy-hand-authored-pool", "specs"):
        (tmp_path / tree).mkdir()
        (tmp_path / tree / "long.py").write_text(_function(CAP + 1))
    (tmp_path / "l7r").mkdir()
    (tmp_path / "l7r" / "short.py").write_text(_function(CAP))
    r = _check(tmp_path)
    assert (r.returncode, r.stderr) == (0, ""), r.stderr


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        (_function(CAP + 1, "  # noqa: PLR0915 - one ordered pass whose steps share every local"), None),
        (_function(3, "  # noqa: PLR0915 - long"), "say why the body must remain one"),
        (_function(3, "  # noqa: PLR0915"), "say why the body must remain one"),
        ("x = 1  # noqa: PLR0915 - a reason given in enough words\n", "only on the `def` line"),
        (_function(3, "  # noqa"), "a bare `# noqa` on a `def` line"),
        ("import os  # noqa\n", None),
        ("# ruff: noqa\n" + _function(3), "a file-level `# ruff: noqa`"),
        ("# ruff: noqa: PLR0915 - the whole file is one long table\n" + _function(3), "a file-level `# ruff: noqa`"),
        ("# ruff: noqa: E501\n" + _function(3), None),
        (_function(3, "  # noqa: E501, PLR0915 - kept whole because every step reads the same cursor"), None),
    ],
)
def test_a_suppression_is_one_body_with_its_reason(tmp_path: Path, text: str, problem: str | None) -> None:
    """FR-004 / SC-004: the escape is clause 12's - on the `def` line, saying why the body must remain one."""
    (tmp_path / "l7r").mkdir()
    (tmp_path / "l7r" / "m.py").write_text(text)
    r = _check(tmp_path)
    if problem is None:
        assert (r.returncode, r.stderr) == (0, ""), r.stderr
    else:
        assert r.returncode == 1 and "l7r/m.py:1" in r.stderr and problem in r.stderr, r.stderr


@pytest.mark.parametrize(
    ("toml", "refused"),
    [
        ('[tool.ruff.lint]\nignore = ["E501", "PLR0915"]\n', True),
        ('[tool.ruff.lint.per-file-ignores]\n"l7r/x.py" = ["PLR0915"]\n', True),
        ('[tool.ruff.lint]\nextend-ignore = ["PLR09"]\n', True),
        ('[tool.ruff.lint]\nignore = ["E501"]\n', False),
    ],
)
def test_the_config_may_not_switch_the_cap_off(toml: str, refused: bool) -> None:
    """FR-004: an ignore in pyproject.toml would exempt every function at once."""
    assert bool(cfc.config_ignores(toml)) is refused


def test_the_repository_config_holds_the_cap_and_says_why_100() -> None:
    """FR-001 / FR-005 / SC-005: the rule selected at 100, nothing ignoring it, the GM's reason beside the number."""
    text = (REPO / "pyproject.toml").read_text()
    assert '"PLR0915"' in text and "max-statements = 100" in text
    assert cfc.config_ignores(text) == []
    assert "131 of 1,209" in text and "second most common" in text


def test_the_check_runs_first_in_static_and_before_every_push() -> None:
    """D2: a session reads the check's message, not ruff's; a tests- or scripts-only push runs no gate."""
    static = (REPO / "Makefile").read_text().split("\nstatic:", 1)[1].split("\n\n", 1)[0]
    lines = [ln.strip() for ln in static.splitlines() if ln.startswith("\t")]
    assert "check-function-cap.py" in lines[0], lines[:2]
    assert "check-function-cap.py" in (REPO / "scripts/sync-with-main.sh").read_text()


def test_the_selftest_passes() -> None:
    r = subprocess.run([sys.executable, str(CHECK), "--selftest"], capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
