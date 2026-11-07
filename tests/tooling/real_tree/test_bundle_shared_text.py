"""THE REAL TREE's half of `tests/tooling/test_bundle_shared_text.py`: two real check bundles of one kind share less than the limit.

Moved here by feature 444 T36 (the GM 2026-11-07: "any single test which takes even 100 milliseconds is fairly suspect"; then "please
proceed with all 3 of those things"): it checks a TOOL's behavior over the whole repository, and a scan of the whole repository reads
every file, so the gate's recorded reads selected it for every edit, a Rust one included. It is the tool's property, not the edited
file's: `tests/tooling/real_tree/` runs when the gate plans full (any `scripts/`, gate-configuration or tooling change - the tool's
own) and on `FULL=1`, never for an engine or a Rust increment (`pool_readers.rust_readers`, `tests/CLAUDE.md`).
"""

from __future__ import annotations

import pathlib

import pytest

from tests.tooling.test_bundle_shared_text import LIMIT, REPO, _shared, cb, mb


@pytest.mark.parametrize("for_", ["record-format", "quote-check"])
def test_two_record_bundles_of_one_check_share_less_than_the_limit(for_: str, tmp_path: pathlib.Path) -> None:
    for q in ("0086", "0087"):
        assert cb.main([q, "--for", for_, "--no-quotes", "--not-owed-ok", "a test of the shared text", "--out", str(tmp_path / q), "--root", str(REPO)]) == 0
    assert _shared(tmp_path / "0086", tmp_path / "0087") < LIMIT


@pytest.mark.parametrize("for_", ["modal-form", "modal-research", "modal-depiction"])
def test_two_modal_bundles_of_one_check_share_less_than_the_limit(for_: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHECK_ORDER_OK", "a test of the bundle's shared text, not of the check order")
    for kind in ("Alder", "Barley"):
        assert mb.bundle(REPO, kind, for_, str(tmp_path / kind), "a test of the shared text") == 0
    assert _shared(tmp_path / "Alder", tmp_path / "Barley") < LIMIT, "a modal bundle repeats a contract's text - move it to the agent file"
