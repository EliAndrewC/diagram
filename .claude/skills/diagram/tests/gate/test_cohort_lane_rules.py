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

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

COHORT = tuple(hg.cohort_specs(4, first_seed=41))
DOUBLE_BACK_DEG = 140.0
BEND_RUN_FT = 40.0


def _kinks(M) -> list[tuple[str, int, int]]:
    """The `lanes_bend_like_paths` predicate: a turn past 140 deg doubles back, and two real turns inside
    40 ft is a kink rather than a bend. Stated here rather than imported from the reference module so this
    test reads on its own; the two are held together by both asserting the reference roll is clean."""
    bad: list[tuple[str, int, int]] = []
    for ln in M.get("lanes") or []:
        if ln.get("connector"):
            continue
        p = [(float(a), float(b)) for a, b in (ln.get("pts") or [])]
        if len(p) < 3:
            continue
        turns: list[tuple[int, float]] = []
        for k in range(1, len(p) - 1):
            v1 = (p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1])
            v2 = (p[k + 1][0] - p[k][0], p[k + 1][1] - p[k][1])
            n1, n2 = math.hypot(*v1), math.hypot(*v2)
            if n1 < 1e-6 or n2 < 1e-6:
                continue
            deg = math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
            if deg >= DOUBLE_BACK_DEG:
                bad.append(("doubles back", round(p[k][0]), round(p[k][1])))
            elif deg >= 50.0:
                turns.append((k, deg))
        for (ka, _da), (kb, _db) in zip(turns, turns[1:], strict=False):
            if sum(math.dist(p[j], p[j + 1]) for j in range(ka, kb)) <= BEND_RUN_FT:
                bad.append(("kinks", round(p[ka][0]), round(p[ka][1])))
    return bad


@pytest.mark.rolls_map
@pytest.mark.parametrize("spec", [s for s in COHORT if s.seed != 43], ids=lambda s: f"seed{s.seed}")
def test_the_clean_cohort_seeds_bend_like_paths(spec) -> None:
    """Seeds 41, 42 and 44. These are the ones the pin said were clean, and holding them is what makes
    the seed-43 xfail below mean something: without them, "seed 43 fails" is indistinguishable from "the
    predicate fails on everything"."""
    _plan, M = rollcache.hamlet(spec)
    assert M.get("lanes"), f"seed {spec.seed} drew no lane, so this rule would judge nothing"
    assert not _kinks(M), f"seed {spec.seed}: {_kinks(M)}"


@pytest.mark.rolls_map
@pytest.mark.xfail(strict=True, reason="known-open: seed 43's routed footpath keeps a 36 px lattice step round a house corner (research R2b)")
def test_seed_43_still_kinks_round_a_house_corner() -> None:
    """The pin `GATE_COHORT_EXPECTED` used to hold, moved somewhere that can still read it.

    STRICT, so it fails the day the router stops making this - which is the half of the old
    `baseline_verdict` that mattered most: a pin that only ever loosens hides the next regression on the
    seed it covers."""
    _plan, M = rollcache.hamlet([s for s in COHORT if s.seed == 43][0])
    assert not _kinks(M), f"seed 43: {_kinks(M)}"
