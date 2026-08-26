"""tier town tests split out of `tests.settlement.test_city` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _inwall_settlement


@pytest.mark.tiers("town")
def test_inwall_drain_outfall_normalizes_orientation_and_degenerate_cases():
    # outfall-FIRST input comes back outfall-first (the caller's orientation is preserved)
    s = _inwall_settlement()
    out = s.inwall_drain_outfall([(150, 110), (300, 150), (500, 300)])
    assert out[-1] == (500.0, 300.0)  # far end untouched, so the cut landed at index 0
    # no ring road: nothing to trim - the gate still marks the outfall
    s2 = Settlement(1000, 1000, seed=1)
    s2.meta(name="C2", scale="town", ftpx=1)
    s2.M["moat"] = [[60, 60], [940, 60], [940, 940], [60, 940]]
    out2 = s2.inwall_drain_outfall([(500, 300), (150, 110)])
    assert out2 == [(500.0, 300.0), (150.0, 110.0)] and s2.M["sluice_gates"]
    # no moat: gate only - no conduit record, no orientation flip
    s3 = Settlement(1000, 1000, seed=1)
    s3.meta(name="C3", scale="town", ftpx=1)
    s3.M["ring_road"] = [[100, 100], [900, 100], [900, 900], [100, 900], [100, 100]]
    s3.M["ring_road_width"] = 8
    n3 = len(s3.M["channels"])
    s3.inwall_drain_outfall([(500, 300), (150, 110)])
    assert len(s3.M["channels"]) == n3 and s3.M["sluice_gates"]
    # the whole polyline hugs the road: left untrimmed (the check flags it), gate at the raw end
    s4 = _inwall_settlement()
    out4 = s4.inwall_drain_outfall([(300, 104), (200, 104)])
    assert out4[-1] == (200.0, 104.0)
