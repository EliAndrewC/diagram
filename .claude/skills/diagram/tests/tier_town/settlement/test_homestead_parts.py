"""tier town tests split out of `tests.settlement.test_homestead_parts` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement


@pytest.mark.tiers("town")
def test_grove_fits_rejects_wall_overlap():
    # a belt arm is footprint-checked against the town wall: the corridor test is center-only,
    # so a wide arm centered clear of the rampart could still lap the stroke (Hirameki, 2026-07)
    s = Settlement(W=1000, H=1000, seed=1)
    s.meta(name="Gw", scale="town", ftpx=1)
    assert s._grove_fits(500, 500, 90, 40, [(470, 470)])  # no wall: fits
    s.M["wall"] = [(540, 300), (540, 700)]
    assert not s._grove_fits(500, 500, 90, 40, [(470, 470)])  # east corner laps the wall stroke
