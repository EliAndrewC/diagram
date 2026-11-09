"""Fixtures for the dispatcher tests: a throwaway repository with a `main`, a fake AWS client driven
by the RECORDED responses in fixtures/ (Principle X: saved fixtures at the boundary, never a
transport mock), and a scripted `sh` so lint / reference / git outcomes are chosen per test."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parents[3]  # tests/tooling/ci/ is one level deeper than tests/ci/ was (T29)  # the real repository, for rust/gate/src/stamp.rs


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repo shaped like this one: rust/gate/src/stamp.rs present, the skill dir, one commit on main
    and an `origin/main` ref pointing at it (so merge-base and merge-tree work)."""
    root = tmp_path / "clone"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    (root / "scripts/gates").mkdir(parents=True)
    (root / "scripts/gates/codeid.py").write_text((REPO_ROOT / "scripts/gates/codeid.py").read_text(encoding="utf-8"), encoding="utf-8")  # gate-stamp loads its code id beside it (feature 426 D2)
    skill = root
    (skill / "l7r" / "diagram").mkdir(parents=True, exist_ok=True)
    (skill / "l7r" / "diagram" / "m.py").write_text("x = 1\n", encoding="utf-8")
    (skill / "dev" / "run-log").mkdir(parents=True)
    (skill / "dev" / "bypass-log").mkdir(parents=True)
    (root / "buildspec").mkdir()
    for m in ("check", "merge", "measure", "image"):  # feature 177 adds the measurement buildspec
        (root / "buildspec" / f"{m}.yml").write_text(f"version: 0.2\n# {m}\n", encoding="utf-8")
    (root / "README.md").write_text("base\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    return root


def commit(root: Path, rel: str, text: str, msg: str = "work") -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", msg)
    return git(root, "rev-parse", "HEAD")
