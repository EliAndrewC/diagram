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
_SKILL = os.path.normpath(os.path.join(_HERE, ".."))


def _with_blocks() -> list[str]:
    """Every map's notes file that carries a census block, in BOTH trees (feature 161).

    A frozen exhibit's census block is as much a shipped claim as a live map's - it states counts
    a reader can check against the manifest beside it - so the legacy tree is walked here too.
    """
    out = []
    for tree in ("pool", "legacy-hand-authored-pool"):
        for notes in sorted(glob.glob(os.path.join(_SKILL, tree, "*", "*", "*.notes.md"))):
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


def test_a_count_typed_in_the_current_prose_must_be_the_manifest_s_and_history_is_left_alone() -> None:
    """Feature 294 B14: seeded - the recorded case, a notes file stating last roll's count as the map's (paddy counts and
    typed totals stale ~25 times in features 269 and 293)."""
    from l7r.diagram.tools.notes_census import block, stale_counts

    M = {"houses": [{"x": 0, "y": 0}] * 16, "wells": [{}] * 2, "farm_fixtures": [{"kind": "privy"}] * 3}
    notes = (
        "# Design notes\n\nThe hamlet has 15 farmhouses and two wells; three privies.\n\n"
        "## 2026-08-29 - feature 152\n\n15 farmhouses then.\n\n"
        "## Map notes\n\nAs first rolled (2026-08-11) it seated 14 farmhouses.\n\n- 2026-08-28 the review: nine wells\n"
        f"\n{block(M)}\n"
    )
    assert stale_counts(notes, M) == ["'15 farmhouses' - the map ships 16 farmhouses"]
    assert stale_counts(notes.replace("15 farmhouses and", "sixteen farmhouses and"), M) == []


def test_the_pool_notes_state_no_stale_count_in_their_current_prose() -> None:
    from l7r.diagram.tools.notes_census import stale_counts

    checked = 0
    for notes in sorted(glob.glob(os.path.join(_SKILL, "pool", "*", "*", "*.notes.md"))):
        manifest = notes[: -len(".notes.md")] + ".json"
        if not os.path.isfile(manifest):
            continue  # a Mode A sheet: its notes are held to its data-kind census (B15b)
        with open(notes, encoding="utf-8") as fh, open(manifest, encoding="utf-8") as mf:
            assert stale_counts(fh.read(), json.load(mf)) == [], notes
        checked += 1
    assert checked >= 5, "non-vacuity: the hamlets' notes were read"
