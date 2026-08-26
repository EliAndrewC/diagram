"""tier town tests split out of `tests.check_village.test_segments_05_fields_and_ditches` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _supply_M,
    f,
)


@pytest.mark.tiers("town")
def test_field_supply_visibly_sourced_passes_on_a_cargo_canal():
    # a comb origin on a cargo-canal bank is sourced (a Lion-lands water-town form)
    M = _supply_M([450, 104])
    M["streams"] = []
    M["canals"] = [{"poly": [[100, 100], [800, 100]], "w": 12}]
    assert "field_supply_visibly_sourced[x]" not in f(M)
