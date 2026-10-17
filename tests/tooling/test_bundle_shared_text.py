"""Two bundles of one check share almost nothing: what every dispatch of a check shares belongs in its agent file (feature 383
amendment 6, FR-035, plan D38).

A bundle is read AFTER the prompt, which differs per unit, so any text two bundles of a check both carry is written to the prompt
cache fresh at every dispatch; the agent file is the system prompt, first in every dispatch, and read from the cache. The modal
checks' bundles each carried the guidelines - 15-17k characters - until this amendment (research R13). The bundles here are built
from the real record, two units of each kind, because the repetition is in what real units produce.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]
#: characters two manifests of one kind may share: headings, an origin line, the owed-checks line - nothing a contract holds
LIMIT = 2000


def _load(name: str, path: pathlib.Path):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sc = _load("subagent_cache", REPO / "scripts/measure/subagent_cache.py")
cb = _load("_check_bundle", script("_check_bundle"))
mb = _load("modal_bundle", REPO / "scripts/record/modal_bundle.py")


def _shared(a: pathlib.Path, b: pathlib.Path) -> int:
    """What two manifests share outside the sections built from each unit's own inputs (two crops cite the same drawing pages;
    that is the units coinciding, not the check repeating itself)."""
    return sc.contract_shared(_manifest(a), _manifest(b))


def _manifest(d: pathlib.Path) -> str:
    """The bundle's MANIFEST, or its first batch's where the check splits a large page into batches (quote-check)."""
    top = d / "MANIFEST.md"
    return (top if top.is_file() else sorted(d.glob("batch-*/MANIFEST.md"))[0]).read_text(encoding="utf-8")


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


def test_the_measure_fails_on_a_block_both_bundles_repeat(tmp_path: pathlib.Path) -> None:
    """The seeded case: a 3,000-character block added to two bundles that otherwise differ is over the limit."""
    block = "\n".join(f"Standing rule {i}: what every bundle of this check repeats, in so many words." for i in range(40))
    for name, unit in (("a", "the byre"), ("b", "the well")):
        (tmp_path / name).mkdir()
        (tmp_path / name / "MANIFEST.md").write_text(f"# Bundle for {unit}\n\n{block}\n\nThe unit: {unit}, its own text.\n", encoding="utf-8")
    assert len(block) >= 3000 and _shared(tmp_path / "a", tmp_path / "b") >= LIMIT
