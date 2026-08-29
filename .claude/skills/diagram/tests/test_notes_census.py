"""Every count a notes file STATES inside its census block must be the shipped manifest's own.

The guard exists because the same defect landed three times: a settlement-review reading a
`.notes.md` against the artifacts found counts describing a roll that no longer ships, twice in the
paragraph written to correct the previous stale one (2026-08-29). Typed numbers go stale silently -
the prose still reads as a measurement, and the next session quotes it precisely BECAUSE it is
labeled as the corrected one. So the counts are derived and this test is what keeps them honest.

It binds what a notes file CLAIMS, not what it omits: a file with no census block is not required to
grow one, and the prose around a block stays the author's."""

from __future__ import annotations

import glob
import json
import os

import pytest

from l7r.diagram.tools.notes_census import BEGIN, END, block

_HERE = os.path.dirname(os.path.abspath(__file__))
_POOL = os.path.normpath(os.path.join(_HERE, "..", "pool"))


def _with_blocks() -> list[str]:
    out = []
    for notes in sorted(glob.glob(os.path.join(_POOL, "*", "*.notes.md"))):
        with open(notes, encoding="utf-8") as fh:
            if BEGIN in fh.read():
                out.append(notes)
    return out


@pytest.mark.parametrize("notes", _with_blocks(), ids=lambda p: os.path.basename(p))
def test_a_notes_census_block_states_the_shipped_manifests_own_counts(notes: str) -> None:
    manifest = notes[: -len(".notes.md")] + ".json"
    assert os.path.exists(manifest), f"{os.path.basename(notes)} carries a census block but has no manifest beside it"
    with open(manifest, encoding="utf-8") as fh:
        M = json.load(fh)
    with open(notes, encoding="utf-8") as fh:
        text = fh.read()
    i, j = text.find(BEGIN), text.find(END)
    got = text[i : j + len(END)]
    want = block(M)
    assert got == want, f"{os.path.basename(notes)}'s census block is stale - run `make notes-census`.\n--- recorded\n{got}\n--- shipped\n{want}"


def test_the_pool_hamlets_all_carry_a_census_block() -> None:
    """The five scripted hamlets are the maps whose counts the reviews keep catching, so for THOSE the
    block is required rather than optional - a stale paragraph and no block would pass the test above."""
    want = {"inashiro", "kashikawa", "kuwabata", "mizuguchi", "sawada"}
    have = {os.path.basename(p)[: -len(".notes.md")] for p in _with_blocks()}
    assert want <= have, f"missing a census block: {sorted(want - have)}"
