"""tier city tests split out of `tests.check_village.test_segments_02_capital_and_walls` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village


@pytest.mark.tiers("capital", "city")
def test_capital_wall_matches_budget_reuses_the_provincial_tolerances():
    """Inherited deliberately - they are pinned by the shipped-Tango / rejected-Nagahara pair, and
    nothing about a capital argues for different slack."""
    assert check_village.BUDGET_TOL_OVER == 0.08
    assert check_village.BUDGET_TOL_UNDER == 0.05
