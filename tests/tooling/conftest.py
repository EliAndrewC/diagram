"""Fixtures the tests moved into this tree still take from their source module (feature 133 T29). A conftest is
where pytest looks for them, and here the name shadows nothing."""

import subprocess
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _sources_home(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every tooling test's sources-consulted ledger and page cache are its own (feature 288, `_sources.home`): a
    test that saves a page or reserves an entry never writes the host's `.specify/`, and never reads its cache."""
    monkeypatch.setenv("L7R_SOURCES_HOME", str(tmp_path_factory.mktemp("sources-home")))
    monkeypatch.setenv("L7R_ATTEMPTS_ROOT", str(tmp_path_factory.mktemp("attempts-root")))  # the attempts log (feature 312)
    monkeypatch.setenv("L7R_ARCHIVE_READS", "0")  # a page read in a test is never archived to the real archive (feature 309)
    monkeypatch.delenv("REFRESH", raising=False)
    # a page session's own feature (set by its runner) overrides a fixture's `.specify/feature.json`: two arbiter tests
    # failed only under a page session (368's check session, 2026-10-10)
    monkeypatch.delenv("L7R_FEATURE_DIRECTORY", raising=False)
    # the clone's own active feature (`.specify/feature.json`, which git ignores) is no input of any tooling test: one fixed
    # feature, so a test's result is the same in every clone and a landing's worktree can reuse its pass (383 amendment 2)
    monkeypatch.setenv("SPECIFY_FEATURE", "000-tooling-tests")


@pytest.fixture
def fixture_skill(tmp_path: Path) -> Path:
    """A tree shaped like a clone's skill dir: the real Makefile, `l7r` symlinked, no `.clones/`
    (so `guard` passes), and the switch file under our control."""
    root = tmp_path / "repo"
    skill = root
    skill.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (skill / "Makefile").write_bytes((SKILL / "Makefile").read_bytes())
    (skill / "pyproject.toml").write_bytes((SKILL / "pyproject.toml").read_bytes())
    (skill / "l7r").symlink_to(SKILL / "l7r", target_is_directory=True)
    (skill / "dev").mkdir()
    gate = skill / "scripts/gates/l7r-gate.sh"  # the fixture has no rust/: the real gate, reached from the fixture's own path
    gate.parent.mkdir(parents=True)
    gate.write_text(f'#!/usr/bin/env bash\nexec "{SKILL}/scripts/gates/l7r-gate.sh" "$@"\n', encoding="utf-8")
    gate.chmod(0o755)
    return skill
