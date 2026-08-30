"""The firing census guards that GATE FROZEN FIXTURES (feature 163).

Split from `tests/tools/test_firing_census.py` because the tree decides when a test runs
(`tests/CLAUDE.md`): these two drive the real gate over frozen manifests - 10.4 s in the quick
suite against its ~0.5 s bar and its 60 s budget - and what they buy is merge-time assurance that
the census cannot classify quietly. The pure classifiers stay in the quick tree beside the tool.

Both are the FR-005 instrument proof: `dev/gate.md`'s *"a census that silently returns nothing is
indistinguishable from a clean bill of health"*, applied to a census whose output deletes code.
"""

from __future__ import annotations

import glob
import json

from l7r.diagram.tools import firing_census as fc

KNOWN_FIRING = "all_ink_is_ruled_on"


def test_the_census_names_a_check_that_is_known_to_fire(tmp_path, monkeypatch):
    """Guard 1, and the one that would catch the census silently classifying nothing: a check with a
    frozen fixture named after it must come back FIRES, from that fixture."""
    from l7r.diagram.check_village import driver

    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    ev = fc.evidence_from_paths([f"{fc.HERE}/pool/regressions/{KNOWN_FIRING}_fires_on_an_unruled_element.json"], frozen=True)
    assert KNOWN_FIRING in ev, "the census saw no verdict on a fixture frozen because it fires"
    assert fc.verdict_for(ev[KNOWN_FIRING]) == fc.FIRES


def test_no_check_a_frozen_fixture_pins_is_ever_reported_never_fires(tmp_path, monkeypatch):
    """Guard 3. Every `_regression.fires` name is a check this repository has SEEN fire; if the
    census calls one of them NEVER-FIRES, the census is broken, not the check."""

    from l7r.diagram.check_village import driver

    monkeypatch.setenv(driver.VERDICT_JOURNAL_ENV, str(tmp_path))
    paths = sorted(glob.glob(f"{fc.HERE}/pool/regressions/*.json"))[:12]  # a sample: the full sweep is the census's own job
    pinned = set()
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            pinned |= set((json.load(fh).get("_regression") or {}).get("fires") or [])
    ev = fc.evidence_from_paths(paths, frozen=True)
    live = set(fc.live_check_names())
    missed = sorted(n for n in pinned & live if fc.verdict_for(ev.get(n, set())) == fc.NEVER_FIRES)
    assert not missed, f"the census saw no verdict for pinned check(s) {missed}"
