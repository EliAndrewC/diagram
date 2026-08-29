"""tier city tests split out of `tests.check_village.test_segments_07_water` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _water_map,
    f_only,
)


@pytest.mark.tiers("capital")
def test_aqueduct_taps_water_lands_dry():
    """The intake must touch its river; the terminus (settling basin) must land clear of the
    moat - the capital's ended IN the moat (GM 2026-08-10)."""
    ok = _water_map(aqueducts=[{"poly": [[500, 512], [700, 300]], "w": 3}])
    assert "aqueduct_taps_water_lands_dry" not in f_only(ok, "aqueduct_taps_water_lands_dry")
    dry_intake = _water_map(aqueducts=[{"poly": [[500, 460], [700, 300]], "w": 3}])
    assert "aqueduct_taps_water_lands_dry" in f_only(dry_intake, "aqueduct_taps_water_lands_dry")
    in_moat = _water_map(aqueducts=[{"poly": [[500, 512], [700, 255]], "w": 3}], moat=[[600, 250], [800, 250], [800, 350], [600, 350]], moat_width=22)  # terminus lands in the moat channel itself
    assert "aqueduct_taps_water_lands_dry" in f_only(in_moat, "aqueduct_taps_water_lands_dry")
