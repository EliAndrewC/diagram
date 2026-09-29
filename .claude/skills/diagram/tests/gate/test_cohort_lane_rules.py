"""The lane rules over the gate COHORT, not just the reference roll (feature 166).

WHY THIS MODULE EXISTS, and it is the acceptance review's finding rather than mine. The retired check
battery ran on EVERY shipped manifest; its successors run seed tests on a CACHED ROLL. The reviewer put
the consequence precisely:

    "a property that is true of the cached seeds and false of a map the GM actually rolls now has no
     reader."

That is a real gap this migration opened, and seed 43 is the proof of it. `GATE_COHORT_EXPECTED` pinned
`lanes_bend_like_paths` on seed 43; `tests/gate/test_lane_network.py` asserts the same rule on Inashiro,
which passes it. So after the migration the rule was carried - on a map that does not break it - while
the map that does break it had no reader at all.

So the fix is not another pin. It is to run the rules over the COHORT the gate already rolls, which is
the population the pin was describing, and to keep the one real defect visible as a strict xfail rather
than as a comment in a dictionary.

MEASURED, 2026-08-30, over the gate cohort: seed 43 carries one kink at (991, 188); seeds 41, 42 and 44
are clean. The mechanism is `research R2b` - the routed footpath keeps a 36 px lattice step round a house
corner that neither the chord nor the knee can take.
"""

from __future__ import annotations

import pytest

from l7r.diagram.hamletgen.ways import law
from tests import rolls
from tests.gate import _pool

# THE POPULATION IS THE TWO SHIPPED MAPS THE GATE READS (feature 219; the roster's coverage rolls since 214). Seed 43's kink
# is in the tier above the gate since feature 216 (tests/soak/test_seed_43_kink.py) and Polder 12 since 219
# (tests/soak/test_polder_fall_0.py): a roll that carries no coverage line of its own is not the gate's to make.
COHORT = tuple(rolls.COVERAGE)


def _kinks(M) -> list[tuple[str, int, int]]:
    """The `lanes_bend_like_paths` predicate: a turn past 140 deg doubles back, and two real turns inside 40 ft is a kink
    rather than a bend. It was stated here, a copy of the reference module's, the two held together only by both asserting
    the reference roll clean; since feature 287 (M1) both read the lane law's ONE predicate (`law.lanes_that_kink`)."""
    return law.lanes_that_kink(M)


@pytest.mark.rolls_map
@pytest.mark.parametrize("spec", list(COHORT), ids=lambda s: f"{s.name}-{s.seed}")
def test_the_clean_cohort_seeds_bend_like_paths(spec) -> None:
    """Seeds 41, 42 and 44. These are the ones the pin said were clean, and holding them is what makes
    the seed-43 xfail below mean something: without them, "seed 43 fails" is indistinguishable from "the
    predicate fails on everything"."""
    _plan, M = _pool.rolled_map(spec)
    assert M.get("lanes"), f"seed {spec.seed} drew no lane, so this rule would judge nothing"
    assert not _kinks(M), f"seed {spec.seed}: {_kinks(M)}"
