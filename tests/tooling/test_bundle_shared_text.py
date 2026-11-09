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


LINE_MIN = 40
cb = _load("_check_bundle", script("_check_bundle"))
mb = _load("modal_bundle", REPO / "scripts/record/modal_bundle.py")


def _lines(text: str) -> set[str]:
    """A text's lines of LINE_MIN characters or more, the Read tool's line-number prefix dropped."""
    out = set()
    for raw in text.splitlines():
        line = raw.split("\t", 1)[-1].strip() if "\t" in raw[:12] else raw.strip()
        if len(line) >= LINE_MIN:
            out.add(line)
    return out


def shared_text(a: str, b: str) -> int:
    """Characters of the lines (LINE_MIN or longer) both texts hold - what two bundles of one check repeat."""
    return sum(len(line) for line in _lines(a) & _lines(b))


#: a bundle section built from the UNIT's own inputs - its research pages and entries, the claims and candidates derived from
#: them - may coincide between two units that read the same pages; it is not text the check repeats (plan D38)
UNIT_ORIGINS = ("research/questions/", "research/sources/", "dev/claims-index.json")
UNIT_SECTIONS = ("claims.md", "candidates.md", "entry/", "drawing/", "record/", "cand/", "sources/")


def contract_part(manifest: str) -> str:
    """A MANIFEST without its sections copied from the unit's own inputs: what the builder writes and the files it copies
    from outside the record - where a check's standing text would be."""
    keep, out = True, []
    for line in manifest.splitlines():
        if line.startswith("## "):
            head = line[3:]
            keep = not (any(f"origin `{o}" in head for o in UNIT_ORIGINS) or any(head.startswith(f"`{s}") for s in UNIT_SECTIONS))
        if keep:
            out.append(line)
    return "\n".join(out)


def contract_shared(a: str, b: str) -> int:
    """`shared_text` over two manifests' `contract_part`s."""
    return shared_text(contract_part(a), contract_part(b))


def _shared(a: pathlib.Path, b: pathlib.Path) -> int:
    """What two manifests share outside the sections built from each unit's own inputs (two crops cite the same drawing pages;
    that is the units coinciding, not the check repeating itself)."""
    return contract_shared(_manifest(a), _manifest(b))


def _manifest(d: pathlib.Path) -> str:
    """The bundle's MANIFEST, or its first batch's where the check splits a large page into batches (quote-check)."""
    top = d / "MANIFEST.md"
    return (top if top.is_file() else sorted(d.glob("batch-*/MANIFEST.md"))[0]).read_text(encoding="utf-8")


def test_the_measure_fails_on_a_block_both_bundles_repeat(tmp_path: pathlib.Path) -> None:
    """The seeded case: a 3,000-character block added to two bundles that otherwise differ is over the limit."""
    block = "\n".join(f"Standing rule {i}: what every bundle of this check repeats, in so many words." for i in range(40))
    for name, unit in (("a", "the byre"), ("b", "the well")):
        (tmp_path / name).mkdir()
        (tmp_path / name / "MANIFEST.md").write_text(f"# Bundle for {unit}\n\n{block}\n\nThe unit: {unit}, its own text.\n", encoding="utf-8")
    assert len(block) >= 3000 and _shared(tmp_path / "a", tmp_path / "b") >= LIMIT
