"""tier city tests split out of `tests.check_village.test_segments_10_city_battery_a` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    WALLSQ,
    _road_city,
    _samurai_varied_city,
    _unwalled_road_city,
    _warren,
    _well_city,
    bldg,
    f_only,
)


@pytest.mark.tiers("city")
def test_city_samurai_housing_varied_fires_when_uniform():
    # a samurai quarter of nothing but small uniform houses - no large senior houses to vary it
    M = _samurai_varied_city([bldg(300 + i * 30, 300, kind="samurai") for i in range(10)])
    assert "city_samurai_housing_varied" in f_only(M, "city_samurai_housing_varied")


@pytest.mark.tiers("city")
def test_city_samurai_housing_varied_fires_when_estate_inside_the_wall():
    # a proper small/large mix, but a samurai walled ESTATE sits INSIDE the city wall - those belong
    # outside the rampart (only the governor's mansion is walled within)
    blds = [bldg(300 + i * 30, 300, kind="samurai_large") for i in range(4)] + [bldg(300 + i * 30, 400, kind="samurai") for i in range(8)]
    M = _samurai_varied_city(blds, manors=[{"x": 500, "y": 500, "w": 80, "h": 60}])  # inside WALLSQ
    assert "city_samurai_housing_varied" in f_only(M, "city_samurai_housing_varied")


@pytest.mark.tiers("city")
def test_city_samurai_housing_varied_passes_with_a_mix_and_estates_outside():
    blds = [bldg(300 + i * 30, 300, kind="samurai_large") for i in range(4)] + [bldg(300 + i * 30, 400, kind="samurai") for i in range(8)]
    M = _samurai_varied_city(blds, manors=[{"x": 900, "y": 500, "w": 80, "h": 60}])  # outside WALLSQ
    assert "city_samurai_housing_varied" not in f_only(M, "city_samurai_housing_varied")


@pytest.mark.tiers("city")
def test_city_imperial_road_has_commerce_fires_when_road_frontage_is_bare():
    # the Imperial road runs through, but only housing lines it - no shops on the prime road frontage
    M = _road_city([bldg(300, 400, kind="laborer")])
    assert "city_imperial_road_has_commerce" in f_only(M, "city_imperial_road_has_commerce")


@pytest.mark.tiers("city")
def test_city_imperial_road_has_commerce_passes_when_road_is_lined():
    shops = [bldg(540, y, kind="shop") for y in range(300, 760, 70)]  # a commercial ribbon along the road
    M = _road_city(shops)
    assert "city_imperial_road_has_commerce" not in f_only(M, "city_imperial_road_has_commerce")


@pytest.mark.tiers("city")
def test_city_imperial_road_has_commerce_skipped_without_a_road():
    # a city with no Imperial road has no road-ribbon rule (its commerce stays in the market district)
    M = _road_city([bldg(540, y, kind="shop") for y in range(300, 760, 70)], road=False)
    assert "city_imperial_road_has_commerce" not in f_only(M, "city_imperial_road_has_commerce")


@pytest.mark.tiers("city")
def test_city_imperial_road_has_commerce_generic_for_an_unwalled_city_fires_when_bare():
    # the rule applies to ANY city with an Imperial road, walled or not - here an unwalled one runs bare
    assert "city_imperial_road_has_commerce" in f_only(_unwalled_road_city([]), "city_imperial_road_has_commerce")


@pytest.mark.tiers("city")
def test_city_imperial_road_has_commerce_generic_for_an_unwalled_city_passes_when_lined():
    shops = [bldg(540, y, kind="shop") for y in range(260, 760, 60)]  # a commercial ribbon along the road
    assert "city_imperial_road_has_commerce" not in f_only(_unwalled_road_city(shops), "city_imperial_road_has_commerce")


@pytest.mark.tiers("city")
def test_city_neighborhoods_have_wells_fires_when_a_dwelling_is_dry():
    # a laborer dwelling 990px from the only well - the water network forgot its neighborhood
    M = _well_city(buildings=[{"kind": "laborer", "x": 1200, "y": 1200, "w": 28, "h": 18, "rot": 0}])
    assert "city_neighborhoods_have_wells" in f_only(M, "city_neighborhoods_have_wells")


@pytest.mark.tiers("city")
def test_city_neighborhoods_have_wells_passes_when_in_reach():
    M = _well_city(buildings=[{"kind": "laborer", "x": 560, "y": 540, "w": 28, "h": 18, "rot": 0}])
    assert "city_neighborhoods_have_wells" not in f_only(M, "city_neighborhoods_have_wells")


@pytest.mark.tiers("city")
def test_city_neighborhoods_have_wells_ignores_samurai_and_outside_dwellings():
    # samurai have private wells; a dwelling OUTSIDE the wall (a gate market) is not a residential
    # neighborhood - neither demands a public well even when far from one
    M = _well_city(wall=WALLSQ, buildings=[{"kind": "samurai", "x": 500, "y": 500, "w": 56, "h": 40, "rot": 0}, {"kind": "merchant", "x": 980, "y": 980, "w": 40, "h": 30, "rot": 0}])
    assert "city_neighborhoods_have_wells" not in f_only(M, "city_neighborhoods_have_wells")


@pytest.mark.tiers("city")
def test_city_wells_in_block_interiors_fires_on_a_building():
    M = _well_city(buildings=[{"kind": "laborer", "x": 505, "y": 505, "w": 40, "h": 30, "rot": 0}])
    assert "city_wells_in_block_interiors" in f_only(M, "city_wells_in_block_interiors")


@pytest.mark.tiers("city")
def test_city_wells_in_block_interiors_passes_when_clear():
    assert "city_wells_in_block_interiors" not in f_only(_well_city(), "city_wells_in_block_interiors")


@pytest.mark.tiers("city")
def test_city_well_density_sufficient_fires_when_a_well_is_overburdened():
    # 30 households all nearest a single well -> it is the nearest for far more than 26
    assert "city_well_density_sufficient" in f_only(_warren(1), "city_well_density_sufficient")


@pytest.mark.tiers("city")
def test_city_well_density_sufficient_passes_with_enough_wells():
    # three wells split the 30 households -> ~10 each, none over-burdened
    assert "city_well_density_sufficient" not in f_only(_warren(3), "city_well_density_sufficient")


@pytest.mark.tiers("city")
def test_city_samurai_quarter_has_no_public_wells_fires_among_samurai():
    # a wellhead embedded among samurai dwellings - the samurai quarter has no communal wells
    M = _well_city(
        buildings=[
            {"kind": "samurai", "x": 510, "y": 505, "w": 24, "h": 17, "rot": 0},
            {"kind": "samurai", "x": 480, "y": 520, "w": 24, "h": 17, "rot": 0},
            {"kind": "laborer", "x": 900, "y": 900, "w": 14, "h": 10, "rot": 0},
        ]
    )
    assert "city_samurai_quarter_has_no_public_wells" in f_only(M, "city_samurai_quarter_has_no_public_wells")


@pytest.mark.tiers("city")
def test_city_samurai_quarter_has_no_public_wells_passes_among_commoners():
    # the same well, but it sits among commoner dwellings (a samurai house is a block away) - fine
    M = _well_city(
        buildings=[
            {"kind": "laborer", "x": 510, "y": 505, "w": 14, "h": 10, "rot": 0},
            {"kind": "laborer", "x": 480, "y": 520, "w": 14, "h": 10, "rot": 0},
            {"kind": "samurai", "x": 900, "y": 900, "w": 24, "h": 17, "rot": 0},
        ]
    )
    assert "city_samurai_quarter_has_no_public_wells" not in f_only(M, "city_samurai_quarter_has_no_public_wells")


@pytest.mark.tiers("city")
def test_well_density_uses_a_higher_ceiling_for_outcast_rows():
    """GM 2026-08-10: a burakumin quarter at ~2x machi density cannot reach 1-per-20 without
    knotting 5-7 wellheads in one 150 ft radius. Historically those quarters were the last
    served by communal water, so they carry their own ceiling - but the REACH rule still binds."""
    base = {"meta": {"scale": "city", "walled": True, "W": 2000, "H": 2000, "ftpx": 3}, "wall": WALLSQ, "gates": [[500, 200], [500, 800]]}
    well = [{"x": 500, "y": 500, "kind": None}]
    outcast = {**base, "wells": well, "buildings": [{"x": 480 + (i % 8) * 6, "y": 480 + (i // 8) * 6, "w": 8, "h": 6, "rot": 0, "kind": "burakumin"} for i in range(40)]}
    assert "city_well_density_sufficient" not in f_only(outcast, "city_well_density_sufficient")
    machi = {**base, "wells": well, "buildings": [{"x": 480 + (i % 8) * 6, "y": 480 + (i // 8) * 6, "w": 8, "h": 6, "rot": 0, "kind": "laborer"} for i in range(40)]}
    assert "city_well_density_sufficient" in f_only(machi, "city_well_density_sufficient")
    far = {
        **base,
        "wells": well,
        "buildings": [{"x": 740 + (i % 8) * 6, "y": 740 + (i // 8) * 6, "w": 8, "h": 6, "rot": 0, "kind": "burakumin"} for i in range(40)],
    }  # inside the wall, 340px+ from the only well
    assert "city_neighborhoods_have_wells" in f_only(far, "city_neighborhoods_have_wells")  # the reach rule still binds on outcast rows
