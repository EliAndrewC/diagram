"""tier town tests split out of `tests.check_village.test_driver_and_fixtures` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _justice_town,
    f,
)


@pytest.mark.tiers("town")
def test_justice_town_fixture_passes_every_justice_check():
    # The control. Without it, a check that fires on EVERYTHING would look like a working check.
    bad = f(_justice_town())
    assert not {n for n in bad if n.startswith(("punishment_spot", "execution_ground", "town_has_punishment", "town_has_execution"))}
