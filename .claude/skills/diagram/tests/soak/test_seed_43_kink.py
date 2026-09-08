"""THE ONE OPEN DEFECT, kept visible in the tier ABOVE the gate (feature 216, GM 2026-09-08).

Cohort seed 43's routed footpath keeps a 36 px lattice step round a house corner at (991, 188) - research R2b of
feature 166 - and this strict xfail is its only reader: it fails the day the router stops making the kink. It
rolled in every gate from feature 166 to 215. Feature 215's audit found its eight unique engine lines and made
them unit tests (`tests/hamletgen/ways/test_touch.py`, `tests/waterfields/test_seams.py`), which left this roll
carrying no coverage line at all - and the GM's rule for the gate is *"doing only what is strictly necessary in
order to reach one hundred percent code coverage ... the correct place for the kind of test in which we make more
map rolls than are strictly necessary is in the AWS tests. or the CI tests"*. This tree is that place: nothing
ordinary collects it (`norecursedirs`), `make soak` names it. The kink's own geometry, for whoever fixes the
router: `specs/215-the-floor-itself/census/kink-seed-43.json`.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from tests.gate.test_cohort_lane_rules import _kinks

KINK = hg.cohort_specs(1, first_seed=43)[0]


@pytest.mark.rolls_map
@pytest.mark.xfail(strict=True, reason="known-open: seed 43's routed footpath keeps a 36 px lattice step round a house corner (research R2b)")
def test_seed_43_still_kinks_round_a_house_corner() -> None:
    _plan, M = rollcache.hamlet(KINK)
    assert not _kinks(M), f"seed 43: {_kinks(M)}"
