"""Fixtures the tests moved into this tree still take from their source module (feature 133 T29). A conftest is
where pytest looks for them, and here the name shadows nothing."""

import pytest

from tests.test_switches import fixture_skill  # noqa: F401


@pytest.fixture(autouse=True)
def _sources_home(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every tooling test's sources-consulted ledger and page cache are its own (feature 288, `_sources.home`): a
    test that saves a page or reserves an entry never writes the host's `.specify/`, and never reads its cache."""
    monkeypatch.setenv("L7R_SOURCES_HOME", str(tmp_path_factory.mktemp("sources-home")))
    monkeypatch.setenv("L7R_ARCHIVE_READS", "0")  # a page read in a test is never archived to the real archive (feature 309)
    monkeypatch.delenv("REFRESH", raising=False)
