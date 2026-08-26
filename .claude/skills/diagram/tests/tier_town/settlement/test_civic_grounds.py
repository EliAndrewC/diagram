"""tier town tests split out of `tests.settlement.test_civic_grounds` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _town


@pytest.mark.tiers("town")
def test_granary_draws_a_storehouse_row():
    # opt-in rice-transit granary: a row of n fireproof kura, recorded for town_has_granary
    s = _town()
    stores = s.granary(500, 500, n=3)
    assert len(stores) == 3 and s.M["granary"]["n"] == 3 and s.M["granary"]["label"] == "granary"


@pytest.mark.tiers("town")
def test_merchant_residences_stop_at_the_requested_count():
    # the placed >= count early-break: with more storefronts than requested homes, the loop
    # must stop at the cap (previously covered by the towns' legacy gens)
    s = Settlement(W=1600, H=1600, seed=4)
    s.meta(name="Mr", scale="town", ftpx=1)
    rd = [(300, 1100), (1300, 1100)]
    s.road(rd, label="post road")  # merchant_residences derives its band from the ROAD, not a street
    s.frontage(rd, ["shop"] * 8, width=24, spacing=64, skip=rd)
    n0 = sum(1 for b in s.M["buildings"] if b["kind"] == "merchant_large")
    s.merchant_residences(0)  # count already satisfied -> the cap break fires on the first storefront
    assert sum(1 for b in s.M["buildings"] if b["kind"] == "merchant_large") == n0
    s.merchant_residences(1)
    assert sum(1 for b in s.M["buildings"] if b["kind"] == "merchant_large") <= n0 + 1


@pytest.mark.tiers("town")
def test_punishment_spot_records_true_size_and_reserves_ground():
    s = _town()
    s.punishment_spot(400, 400, rot=30)
    p = s.M["punishment_spots"][0]
    assert (p["w"], p["h"]) == (30.0, 12.0)  # ~30x12 real ft, true size at town grain (1 ft/px)
    assert p["rot"] == 30.0
    assert (400, 400, 30.0, 12.0) in s.placed  # reserved against the urban pack
    assert s.block_polys  # and against footprint-blocking placers


@pytest.mark.tiers("town")
def test_boundary_marker_floor_never_shrinks_a_stone():
    # The marker floor lifts a sub-glyph stone; it must not shrink one that already draws larger.
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="B", scale="town", ftpx=0.25)  # 4 px per foot - the true stone is already 12 px
    s.boundary_marker(300, 300)
    b = s.M["boundary_markers"][0]
    assert b["vw"] == b["w"] == 12.0
