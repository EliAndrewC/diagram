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


# The 2026-08-16 legacy freeze (migration-plan.md "The accepted trade") removed the hand-authored
# maps from the test_villages sweep, which uncovered the handful of check_village branches only
# those maps' full-gate runs reached (a town's fire/justice variants, minami's no-Imperial-road
# walled-city branch, the odd water fork). These FROZEN pool manifests - committed, permanent,
# never regenerated - are replayed through the FULL gate purely as coverage carriers, selected by
# the same greedy line-coverage search as the sentinels above (if coverage drops here again,
# re-run the search rather than guessing). NOTHING is asserted about their verdicts: a frozen map
# is allowed to fail rules added after the freeze, so the only claim held is that the gate still
# RUNS on old manifests - the claim the whole corpus already makes.
_FROZEN_POOL_COVERAGE_CARRIERS = [
    "towns/hirameki.json",
    "towns/hoshizora.json",
    "provincial-cities/minami.json",
    "hamlets/akagahara.json",
    "hamlets/enokida.json",
]


@pytest.mark.parametrize("rel", _FROZEN_POOL_COVERAGE_CARRIERS)
def test_frozen_pool_full_gate_coverage_carrier(rel):
    with open(os.path.join(HERE, "pool", rel)) as fh:
        M = json.load(fh)
    failed = check_village.gate(M, verbose=False)
    assert failed is not None  # verdicts deliberately unchecked - see the carrier comment above
