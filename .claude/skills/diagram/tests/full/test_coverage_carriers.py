"""THE FULL TREE (feature 135, GM 2026-08-27): the coverage CARRIERS - subjects replayed through the WHOLE
gate so deep branches execute. They prove nothing at the merge check, which enforces no coverage floor (the
Makefile's `test` target defers the floors to FULL), so they run where the floors are enforced:
`make done FULL=1` and the AWS check."""

import copy
from typing import Any

import pytest

from l7r.diagram import check_village
from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

REFERENCE = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")


# THE SENTINEL IS A ROLL NOW, NOT A STORED BAD MAP (feature 158, 2026-08-29). It used to be
# `settlement_wells_fire_on_a_village_with_no_wells.json` - a hand-authored Kikuta village with its wells
# taken out, picked by feature 022's greedy line-coverage search. That fixture went with the rest of the
# hand-era corpus on the GM's ruling (*"there is no reason to see what would happen if we encountered a type
# of map, which is literally impossible to produce any longer"*), and what it was actually still earning its
# place for - keeping full-mode `gate()` (no `only=`, every segment, the shared derivations end to end) under
# test inside the suite - a real roll does better, because the manifest is one the engine can still produce.
#
# The deliberate break is what stops this going vacuous: a gate that returned `[]` for every input would pass
# the "it runs" half and fail here.
@pytest.mark.rolls_map
def test_the_whole_gate_runs_end_to_end_on_a_real_roll_and_still_names_a_break() -> None:
    _plan, rolled = rollcache.hamlet(REFERENCE)

    clean: list[str] = check_village.gate(copy.deepcopy(rolled), verbose=False)
    assert clean == [], f"the reference roll must be clean under the FULL gate, or the break below proves nothing: {clean}"

    broken: dict[str, Any] = copy.deepcopy(rolled)
    broken["wells"] = []
    named = check_village.gate(broken, verbose=False)
    assert "settlement_has_wells" in named and "settlement_dwellings_watered" in named, f"the full gate no longer names a settlement with no wells: {named}"
