"""`scripts/reviews/moves.py`: a file the delta only moved is told apart from one it edited (feature 329)."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _mod():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_moves", ROOT / "scripts/reviews/moves.py")
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


@pytest.mark.tooling
def test_a_moved_file_is_moved_and_an_edited_or_new_one_is_not(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / "old").mkdir()
    (tmp_path / "old" / "a.md").write_text("same words\n")
    (tmp_path / "old" / "b.md").write_text("before\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    base = _git(tmp_path, "rev-parse", "HEAD").strip()
    _git(tmp_path, "mv", "old", "new")
    (tmp_path / "new" / "b.md").write_text("after\n")
    (tmp_path / "new" / "c.md").write_text("brand new\n")
    m = _mod()
    assert m.moved_only(tmp_path, base, ["new/a.md", "new/b.md", "new/c.md", "new/missing.md"]) == {"new/a.md"}
    assert m.moved_only(tmp_path, "", ["new/a.md"]) == set() and m.moved_only(tmp_path, base, []) == set()
