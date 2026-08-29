"""tier city tests split out of `tests.check_village.test_segments_09_justice_and_tanning` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import _fall_map, f_only


@pytest.mark.tiers("city")
def test_settlement_declares_a_land_fall_fires_when_nothing_declares_a_slope():
    # the hole that let both provincial cities skip every drainage-slope rule behind a green gate
    assert "settlement_declares_a_land_fall" in f_only(_fall_map(), "settlement_declares_a_land_fall")
