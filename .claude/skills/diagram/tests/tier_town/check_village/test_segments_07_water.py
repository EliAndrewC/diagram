"""tier town tests split out of `tests.check_village.test_segments_07_water` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    bldg,
    f_only,
)


@pytest.mark.tiers("town")
def test_scrub_clear_of_urban_fabric_fires_when_scrub_claims_the_town():
    M = {
        "meta": {"scale": "town"},
        "commons": [{"x": 500, "y": 500, "w": 400, "h": 400, "rot": 0, "role": "grazing", "seq": 1, "poly": [[300, 300], [700, 300], [700, 700], [300, 700]]}],
        "buildings": [bldg(500, 500)],  # a merchant house deep inside the claimed scrub
        "wells": [{"x": 400, "y": 400, "r": 8, "vr": 12}],  # a wellhead inside it too
    }
    assert "scrub_clear_of_urban_fabric" in f_only(M, "scrub_clear_of_urban_fabric")


@pytest.mark.tiers("town")
def test_scrub_clear_of_urban_fabric_passes_when_scrub_hugs_the_outskirts():
    M = {
        "meta": {"scale": "town"},
        "commons": [
            {"x": 500, "y": 500, "w": 400, "h": 400, "rot": 0, "role": "grazing", "seq": 1, "poly": [[300, 300], [700, 300], [700, 700], [300, 700]]},
            {"x": 0, "y": 0, "w": 0, "h": 0, "rot": 0, "role": "grazing", "seq": 2, "poly": [[0, 0], [1, 0]]},  # degenerate record - skipped, never a crash
        ],
        "buildings": [bldg(500, 500, kind="barn"), bldg(900, 900)],  # the hay barn IN the grazing is legal; the merchant stands outside
        "wells": [{"x": 800, "y": 300, "r": 8, "vr": 12}],  # outside the poly
    }
    assert "scrub_clear_of_urban_fabric" not in f_only(M, "scrub_clear_of_urban_fabric")


@pytest.mark.tiers("town")
def test_channels_join_water_not_cross_fires_on_a_channel_through_the_moat():
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "moat": [[50, 100], [450, 100], [450, 110]],
        "channels": [{"poly": [[100, 30], [100, 180]], "frm": {"kind": "offmap"}, "to": {"kind": "offmap"}, "w": 2.5}],
    }
    assert "channels_join_water_not_cross" in f_only(M, "channels_join_water_not_cross")


@pytest.mark.tiers("town")
def test_channels_join_water_not_cross_fires_on_a_ditch_through_the_river():
    M = {
        "meta": {"scale": "town", "W": 500, "H": 500},
        "river": {"pts": [[200, 20], [200, 480]], "w": 40},
        "field_ditches": [{"poly": [[80, 300], [350, 300]], "role": "main", "field": "f1", "w": 4, "w_tail": 4}],
    }
    assert "channels_join_water_not_cross" in f_only(M, "channels_join_water_not_cross")
