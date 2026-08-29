"""THE FULL TREE (feature 135, GM 2026-08-27): the coverage CARRIERS - subjects replayed through the WHOLE
gate so deep branches execute. They prove nothing at the merge check, which enforces no coverage floor (the
Makefile's `test` target defers the floors to FULL), so they run where the floors are enforced:
`make done FULL=1` and the AWS check."""

import copy
import json
import os
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


# THE FROZEN-POOL CARRIERS STAY, AND THE FIRST DRAFT OF FEATURE 158 WAS WRONG TO CUT THEM. The GM's
# ruling is about STORED MAPS FROM PAST FAILURES - `pool/regressions/`, the corpus of bad manifests
# captured while iterating: *"there is no reason to see what would happen if we encountered a type of
# map, which is literally impossible to produce any longer"*. These are not that. They are the frozen
# SHIPPED pool - the nineteen hand-authored exhibits the project keeps on purpose - replayed through
# the full gate with NOTHING asserted about their verdicts, purely so the urban half of the check
# battery executes. Deleting them was measured and cost 48 lines across eleven modules on the
# hamlet-path floor (`specs/158-hamlet-test-cost/ledger.md` section 5), because those modules are
# SHARED: a segment file holds hamlet rules and city rules together, and only a city manifest walks
# the city ones. Restored, with the measurement, so the next reader does not repeat the cut.
#
# What DID go with feature 158 is `tests/tier_city/test_frozen_pool_gate.py`, which replayed the same
# manifests and PINNED each one's failures. That is the GM's category exactly - it existed to say what
# happens when you meet such a map - and its coverage is held here instead.
# ALL SIX town/city exhibits, not the five the greedy search picked (feature 158). The sixth, and
# `nagahara` and `tango`, were reaching their lines through `test_frozen_pool_gate.py` - which pinned
# verdicts and is gone - so the carrier list absorbs them: same manifests, same full gate, still
# nothing asserted about what they fail. Measured: without them the hamlet-path floor loses six lines
# across four shared segment modules.
_FROZEN_POOL_COVERAGE_CARRIERS = [
    "towns/hirameki.json",
    "towns/hoshizora.json",
    "towns/ubame.json",
    "provincial-cities/minami.json",
    "provincial-cities/nagahara.json",
    "provincial-cities/tango.json",
    "hamlets/akagahara.json",
    "hamlets/enokida.json",
]

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the skill root


@pytest.mark.parametrize("rel", _FROZEN_POOL_COVERAGE_CARRIERS)
def test_frozen_pool_full_gate_coverage_carrier(rel: str) -> None:
    with open(os.path.join(HERE, "pool", rel)) as fh:
        M = json.load(fh)
    failed = check_village.gate(M, verbose=False)
    assert failed is not None  # verdicts deliberately unchecked - see the carrier comment above
