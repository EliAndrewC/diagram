"""tier city tests split out of `tests.check_village.test_segments_08_town_and_flow` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _FIELD_400,
    f_only,
)


@pytest.mark.tiers("city")
def test_pond_clear_of_field_exempts_a_decorative_pond_not_wired_to_a_field():
    # a city garden pond overlapping a farmland sample, with NO channel wiring it to the field, is exempt
    M = {"pond": [400, 400, 120, 80], "fields": [_FIELD_400]}  # no pond channel -> not an irrigation pond
    assert "pond_clear_of_field" not in f_only(M, "pond_clear_of_field")
