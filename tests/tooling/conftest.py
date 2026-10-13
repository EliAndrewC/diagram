"""Fixtures the tests moved into this tree still take from their source module (feature 133 T29). A conftest is
where pytest looks for them, and here the name shadows nothing."""

import pytest

from tests.test_switches import fixture_skill  # noqa: F401


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
