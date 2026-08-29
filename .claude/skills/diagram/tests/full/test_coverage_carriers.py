"""THE FULL TREE (feature 135, GM 2026-08-27): the coverage CARRIERS - fixtures and frozen pool maps replayed
through the whole gate so deep branches execute. They prove nothing at the merge check, which enforces no
coverage floor (the Makefile's `test` target defers the floors to FULL), and the largest costs 10.6 s; so they
run where the floors are enforced: `make done FULL=1` and the AWS check. Verdict-free as before."""

import json
import os

import pytest

from l7r.diagram import check_village
from tests.gate.test_regressions import HERE, _load

# Feature 022: the targeted replay no longer runs every check against every fixture, which
# uncovered 33 statements that only ever executed during fixtures' full-gate replays - deep
# branches needing frozen bad geometry (a capital deferral pass, a samurai-estate label pile-up,
# village fallow/shrine/pond forks). These four fixtures were selected EMPIRICALLY (greedy
# line-coverage search, specs/022-gate-check-registry/) to cover them; they also keep full-mode
# gate() integration-tested inside the suite. If coverage drops here again, re-run the greedy
# search rather than guessing fixtures.
_FULL_GATE_SENTINELS = ["settlement_wells_fire_on_a_village_with_no_wells.json"]


@pytest.mark.parametrize("name", _FULL_GATE_SENTINELS)
def test_full_gate_coverage_sentinel(name):
    path = os.path.join(HERE, "pool", "regressions", name)
    M, fires = _load(path)
    failed = set(check_village.gate(M, verbose=False))
    missing = [c for c in fires if c not in failed]
    assert not missing, f"{name} no longer trips under the FULL gate: {missing}"


# THE FROZEN-POOL CARRIERS ARE GONE (feature 158, GM 2026-08-29: *"there is no reason to see what would
# happen if we encountered a type of map, which is literally impossible to produce any longer"*). Five frozen
# hand-authored manifests - two towns, a provincial city and two hamlets - used to be replayed through the FULL
# gate purely to carry line coverage into `check_village`'s urban branches. They carried NOTHING enforced: since
# feature 145 the Makefile omits `check_village` from the global 100% floor (the GM ruled on 2026-08-28 that the
# other tiers owe no floor while nothing exercises them), and the derived hamlet-path floor judges only modules
# the scripted rolls execute, which these do not touch. So the carriers were paying ~3 s of every full sweep to
# hold up a floor that no longer exists, on maps no generator can produce. The synthetic sentinel above stays: it
# is a hand-built manifest, not a map from the hand-placement era, and it still holds full-mode `gate()` under test.
