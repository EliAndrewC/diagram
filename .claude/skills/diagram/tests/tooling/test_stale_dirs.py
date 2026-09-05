"""`check-stale-dirs.py`: a directory left with only `__pycache__` is an importable namespace package.

The hazard, stated once: such a directory has no source and no `__init__.py`, but `import` against it
SUCCEEDS under PEP 420 and yields an empty module. So a long-lived clone behaves differently from a
fresh one, and it is the LOCAL run that passes - the direction that hides the bug. Feature 175 paid a
remote build to discover this from the other side; four instances were live in this tree when the
guard landed, all left by feature 166's deletion of the check battery.

These pin the two properties that make the guard trustworthy: it FIRES on the real shape, and it stays
quiet on everything that merely resembles it. The second matters more - a guard that fires on correct
work teaches a session to bypass every guard.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]  # <repo>/.claude/skills/diagram/tests/tooling -> repo root
GUARD = ROOT / "scripts" / "check-stale-dirs.py"
SKILL_REL = Path(".claude/skills/diagram")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(GUARD), *args], capture_output=True, text=True, timeout=300)


def test_the_selftest_passes() -> None:
    """It plants a stale dir and proves the scan fires - a checker that cannot fail is worth nothing."""
    r = _run("--selftest")
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_tree_is_clean() -> None:
    r = _run(str(ROOT))
    assert r.returncode == 0, f"stale directories in the tree:\n{r.stdout}"


def _plant(tmp_path: Path) -> Path:
    (tmp_path / SKILL_REL / "l7r" / "diagram").mkdir(parents=True)
    (tmp_path / SKILL_REL / "tests").mkdir(parents=True)
    return tmp_path


def test_it_FIRES_on_a_directory_holding_only_bytecode(tmp_path: Path) -> None:
    root = _plant(tmp_path)
    dead = root / SKILL_REL / "l7r" / "diagram" / "gone" / "__pycache__"
    dead.mkdir(parents=True)
    (dead / "m.cpython-314.pyc").write_bytes(b"\x00")
    r = _run(str(root))
    assert r.returncode == 1, "a stale directory must fail the check"
    assert "gone" in r.stdout and "rm -rf" in r.stdout, "the refusal must name it and print the command"
    assert "namespace package" in r.stdout.lower(), "and say WHY it matters, not just that it is untidy"


def test_it_does_NOT_delete_anything(tmp_path: Path) -> None:
    """Removing a directory is irreversible for anything untracked inside it, so a person runs it."""
    root = _plant(tmp_path)
    dead = root / SKILL_REL / "l7r" / "diagram" / "gone" / "__pycache__"
    dead.mkdir(parents=True)
    (dead / "m.pyc").write_bytes(b"\x00")
    _run(str(root))
    assert dead.exists(), "the guard REFUSES; it must never delete"


def test_a_real_package_is_left_alone(tmp_path: Path) -> None:
    root = _plant(tmp_path)
    live = root / SKILL_REL / "l7r" / "diagram" / "alive"
    (live / "__pycache__").mkdir(parents=True)
    (live / "mod.py").write_text("x = 1\n", encoding="utf-8")
    assert _run(str(root)).returncode == 0, "a package with source is not stale"


def test_a_directory_of_real_files_is_left_alone(tmp_path: Path) -> None:
    root = _plant(tmp_path)
    d = root / SKILL_REL / "tests" / "fixtures"
    d.mkdir(parents=True)
    (d / "f.json").write_text("{}", encoding="utf-8")
    assert _run(str(root)).returncode == 0, "a data directory holds files of its own"


def test_a_fresh_clone_shape_finds_nothing(tmp_path: Path) -> None:
    """No __pycache__ anywhere is what a fresh clone looks like - the guard must be silent there."""
    root = _plant(tmp_path)
    (root / SKILL_REL / "l7r" / "diagram" / "pkg").mkdir(parents=True)
    (root / SKILL_REL / "l7r" / "diagram" / "pkg" / "m.py").write_text("y = 2\n", encoding="utf-8")
    assert _run(str(root)).returncode == 0


def test_outside_the_importable_trees_is_not_its_business(tmp_path: Path) -> None:
    """Scoped to l7r/ and tests/ on the GM's ruling: elsewhere a leftover cannot be imported."""
    root = _plant(tmp_path)
    (root / SKILL_REL / "pool" / "leftover" / "__pycache__").mkdir(parents=True)
    assert _run(str(root)).returncode == 0, "an unimportable leftover is untidy, not dangerous"
