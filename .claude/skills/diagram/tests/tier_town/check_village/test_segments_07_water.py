"""tier town tests split out of `tests.check_village.test_segments_07_water` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _field,
    _paddy_f,
    bldg,
    f_only,
)


@pytest.mark.tiers("town")
def test_fields_clear_of_wall_fires():
    M = {"meta": {"scale": "town", "walled": True}, "wall": [[250, 50], [250, 500], [260, 500]], "fields": [_field("f", 100, 100, 400, 400)], "gate": [250, 500]}
    assert "fields_clear_of_wall" in f_only(M, "fields_clear_of_wall")


@pytest.mark.tiers("town")
def test_town_margins_clothed_fires_on_a_bare_sheet():
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}}
    assert "town_margins_clothed" in f_only(M, "town_margins_clothed")


@pytest.mark.tiers("town")
def test_town_margins_clothed_passes_when_the_ground_is_worked():
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "commons": [{"x": 500, "y": 500, "w": 1000, "h": 1000, "role": "grazing", "poly": [[-10, -10], [1010, -10], [1010, 1010], [-10, 1010]]}]}
    assert "town_margins_clothed" not in f_only(M, "town_margins_clothed")


@pytest.mark.tiers("town")
def test_near_ring_cultivated_fraction_fires_on_a_sparse_town():
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}}  # bare sheet, 0% cultivated
    assert "near_ring_cultivated_fraction" in f_only(M, "near_ring_cultivated_fraction")


@pytest.mark.tiers("town")
def test_near_ring_cultivated_fraction_passes_when_the_near_ring_is_cropped():
    # dry cropland over ~62% of the flat frame clears the dense town floor (0.28, combs-only doctrine)
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "dry_plots": [{"poly": [[0, 0], [1000, 0], [1000, 620], [0, 620]], "crop": "soy", "theta": 0.0}]}
    assert "near_ring_cultivated_fraction" not in f_only(M, "near_ring_cultivated_fraction")


@pytest.mark.tiers("town")
def test_near_ring_cultivated_fraction_thin_tier_tolerates_a_scrubbier_ring():
    # ~26% cultivated: fires when declared 'dense' (floor 0.28), passes when declared 'thin' (floor 0.12)
    cover = [{"poly": [[0, 0], [1000, 0], [1000, 260], [0, 260]], "crop": "soy", "theta": 0.0}]
    dense = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "dry_plots": cover}
    thin = {"meta": {"scale": "town", "W": 1000, "H": 1000, "near_ring_density": "thin"}, "dry_plots": cover}
    assert "near_ring_cultivated_fraction" in f_only(dense, "near_ring_cultivated_fraction")
    assert "near_ring_cultivated_fraction" not in f_only(thin, "near_ring_cultivated_fraction")


@pytest.mark.tiers("town")
def test_near_ring_paddy_dominant_fires_when_dry_grain_dominates():
    # a big dry-grain field, only a sliver of paddy -> dry dominates -> fires
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "fields": [_paddy_f(0, 0, 120, 120)], "dry_plots": [{"poly": [[0, 300], [1000, 300], [1000, 900], [0, 900]], "crop": "soy", "theta": 0.0}]}
    assert "near_ring_paddy_dominant" in f_only(M, "near_ring_paddy_dominant")


@pytest.mark.tiers("town")
def test_near_ring_paddy_dominant_passes_when_paddy_dominates():
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "fields": [_paddy_f(0, 0, 1000, 700)], "dry_plots": [{"poly": [[0, 800], [200, 800], [200, 900], [0, 900]], "crop": "soy", "theta": 0.0}]}
    assert "near_ring_paddy_dominant" not in f_only(M, "near_ring_paddy_dominant")


@pytest.mark.tiers("town")
def test_near_ring_paddy_dominant_ignores_gardens_as_dry_grain():
    # a large GARDEN dry area is NOT dry-grain; a modest paddy still dominates the grain (there is none)
    M = {"meta": {"scale": "town", "W": 1000, "H": 1000}, "fields": [_paddy_f(0, 0, 300, 300)], "dry_plots": [{"poly": [[0, 400], [1000, 400], [1000, 900], [0, 900]], "crop": "garden", "theta": 0.0}]}
    assert "near_ring_paddy_dominant" not in f_only(M, "near_ring_paddy_dominant")


@pytest.mark.tiers("town")
def test_near_ring_paddy_dominant_excludes_a_paddy_combs_own_dry_hem():
    # a paddy field's dry HEM (a dry plot within the paddy field's envelope) is part of the paddy system,
    # not competing dry grain: a big paddy field whose only dry plot sits inside it stays paddy-dominant
    M = {
        "meta": {"scale": "town", "W": 1000, "H": 1000},
        "fields": [{"name": "comb", "kind": "paddy", "outline": [[0, 0], [900, 0], [900, 700], [0, 700]], "bbox": [0, 0, 900, 700]}],
        "dry_plots": [{"poly": [[100, 100], [800, 100], [800, 300], [100, 300]], "crop": "barley", "theta": 0.0}],  # a hem INSIDE the paddy bbox
    }
    assert "near_ring_paddy_dominant" not in f_only(M, "near_ring_paddy_dominant")


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
