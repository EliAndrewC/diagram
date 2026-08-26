"""tier city tests split out of `tests.check_village.test_segments_10_city_battery_a` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from tests.check_village._builders import (
    _DIAMOND,
    WALLSQ,
    _caste_city,
    _fort_city,
    _gate_furn,
    _lanes,
    _martial_city,
    _merchant_city,
    _road_city,
    _samurai_varied_city,
    _tower,
    _unwalled_road_city,
    _ward_lane,
    _warren,
    _well_city,
    bldg,
    f,
    f_only,
)


@pytest.mark.tiers("city")
def test_city_required_structures_all_fire_on_an_empty_city():
    fails = f({"meta": {"scale": "city"}})
    for name in (
        "city_has_governor_mansion",
        "city_has_six_ministries",
        "city_has_ministry_of_rites",
        "city_has_samurai_neighborhood",
        "city_has_merchant_district",
        "city_has_laborer_neighborhoods",
        "city_has_outside_farmland",
    ):
        assert name in fails


@pytest.mark.tiers("city")
def test_city_ministry_of_rites_fires_when_six_but_none_are_rites():
    mins = [{"x": i * 30, "y": 50, "w": 80, "h": 50, "name": f"Ministry {i}"} for i in range(6)]
    assert "city_has_ministry_of_rites" in f_only({"meta": {"scale": "city"}, "ministries": mins}, "city_has_ministry_of_rites")


@pytest.mark.tiers("city")
def test_city_samurai_housing_sufficient_fires_when_too_few():
    # a 3,000-pop city is ~300 samurai (~60 households); ~10 token houses is far too few - it must
    # depict the bulk of the samurai cohort, not a handful (this was Tango's 22).
    sam = [bldg(300 + i * 12, 300, kind="samurai") for i in range(10)]
    M = {"meta": {"scale": "city", "walled": True, "population": 3000, "W": 1000, "H": 1000}, "wall": WALLSQ, "gates": [[500, 200], [500, 800]], "buildings": sam}
    assert "city_samurai_housing_sufficient" in f_only(M, "city_samurai_housing_sufficient")


@pytest.mark.tiers("city")
def test_city_merchant_housing_varied_fires_when_uniform():
    # a merchant quarter of nothing but small uniform houses - no large houses, no walled estates
    M = _merchant_city([bldg(300 + i * 30, 300, kind="merchant_house") for i in range(10)])
    assert "city_merchant_housing_varied" in f_only(M, "city_merchant_housing_varied")


@pytest.mark.tiers("city")
def test_city_merchant_housing_varied_passes_with_a_mix():
    blds = [bldg(300 + i * 30, 300, kind="merchant_large") for i in range(4)] + [bldg(300 + i * 30, 400, kind="merchant_house") for i in range(6)]
    M = _merchant_city(blds, estates=[{"x": 500, "y": 600, "w": 78, "h": 58}])
    assert "city_merchant_housing_varied" not in f_only(M, "city_merchant_housing_varied")


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
def test_city_lanes_meet_when_aligned_fires_through_the_gate():
    M = _lanes(streets=[[[500, 300], [500, 480]]], alleys=[[[500, 510], [500, 700]]], meta={"scale": "city"})
    assert "city_lanes_meet_when_aligned" in f_only(M, "city_lanes_meet_when_aligned")


@pytest.mark.tiers("city")
def test_city_lanes_reach_ward_gates_fires_through_the_gate():
    M = _ward_lane(alleys=[[[500, 300], [500, 460]]], meta={"scale": "city"})
    assert "city_lanes_reach_ward_gates" in f_only(M, "city_lanes_reach_ward_gates")


@pytest.mark.tiers("city")
def test_city_caste_counts_in_band_fires_when_a_caste_is_off():
    # ~50 laborers is far over the ~24 target for a 60-household city (and the other castes are absent)
    assert "city_caste_counts_in_band" in f_only(_caste_city(laborer=50), "city_caste_counts_in_band")


@pytest.mark.tiers("city")
def test_city_caste_counts_in_band_passes_with_a_balanced_mix():
    # ~40% laborer / 20% servant / 25% merchant / 10% samurai / 5% burakumin of ~60 households
    M = _caste_city(laborer=24, servant=12, merchant_house=15, samurai=6, burakumin=3)
    assert "city_caste_counts_in_band" not in f_only(M, "city_caste_counts_in_band")


@pytest.mark.tiers("city")
def test_city_laborer_housing_varied_fires_when_uniform():
    # every laborer identical - no wealthy 'master' tier (0 large homes)
    assert "city_laborer_housing_varied" in f_only(_caste_city(laborer=30), "city_laborer_housing_varied")


@pytest.mark.tiers("city")
def test_city_laborer_housing_varied_passes_with_a_minority_of_large():
    # ~12.5% of the laborers are larger 'master/rich' homes, the rest standard (budgets.md)
    assert "city_laborer_housing_varied" not in f_only(_caste_city(laborer=28, laborer_large=4), "city_laborer_housing_varied")


@pytest.mark.tiers("city")
def test_city_laborer_housing_varied_fires_when_too_many_large():
    # half the laborers large - not "a clear minority"
    assert "city_laborer_housing_varied" in f_only(_caste_city(laborer=15, laborer_large=15), "city_laborer_housing_varied")


@pytest.mark.tiers("city")
def test_city_caste_shift_must_be_declared_documented_and_live():
    """GM 2026-08-05, on Minami: Fox temples hold much of the commerce that merchant houses conduct
    in other clans' cities, so its merchant households run about a third under the budgets.md share
    while the population is unchanged. The generic +/-30% band cannot tell that from drift - Minami
    was passing at a ratio of exactly 0.700, one household from a failure whose message would have
    said "mix is off" and taught the reader nothing. So the shift is DECLARED, with the same three
    obligations a waiver carries: it widens the band, it must give a real reason, and it must
    describe something that is actually happening.
    """

    def city(merchants, **extra):
        buildings = [
            {"x": 300 + 3 * i, "y": 300 + 3 * j, "w": 10, "h": 8, "rot": 0, "kind": kind}
            for j, (kind, n) in enumerate((("laborer", 40), ("servant", 20), ("merchant_house", merchants), ("samurai", 10), ("burakumin", 5)))
            for i in range(n)
        ]
        M = _fort_city(buildings=buildings)
        M["meta"].update({"population": 500, **extra})  # 100 households -> merchant target 25
        return M

    why = (
        "Fox temples hold much of the commerce that merchant houses conduct in other clans' cities, so merchant "
        "households run under the budgets.md share and hereditary temple families stand in their place."
    )
    assert "city_caste_counts_in_band" in f_only(city(15), "city_caste_counts_in_band")  # 0.60 of target, undeclared - ordinary drift, fails
    assert "city_caste_counts_in_band" not in f_only(city(15, caste_shifts={"merchant": why}), "city_caste_counts_in_band")  # ... declared, allowed
    assert "city_caste_counts_in_band" in f_only(city(9, caste_shifts={"merchant": why}), "city_caste_counts_in_band")  # 0.36 - past even the declared band
    assert "city_caste_shifts_are_live" in f_only(city(25, caste_shifts={"merchant": why}), "city_caste_shifts_are_live")  # on target: the declaration is stale
    assert "city_caste_shifts_are_documented" in f_only(city(15, caste_shifts={"merchant": "by design"}), "city_caste_shifts_are_documented")


@pytest.mark.tiers("city")
def test_city_wall_furniture_clear_of_moat_fires_when_a_tower_stands_in_the_bed():
    # a tower centered on the wall line pokes its outer face into a close-set moat's bed (GM 2026-07:
    # every Tango tower did - the gap=24 moat leaves a 13px berm vs a 19-20px tower half-width)
    moat = [[176, 176], [824, 176], [824, 824], [176, 824], [176, 176]]
    M = _fort_city(moat=moat, moat_width=22, wall_towers=[{"x": 200, "y": 500, "w": 38, "h": 38, "rot": 0}])
    assert "city_wall_furniture_clear_of_moat" in f_only(M, "city_wall_furniture_clear_of_moat")


@pytest.mark.tiers("city")
def test_city_wall_furniture_clear_of_moat_passes_when_nudged_onto_the_berm():
    # the placement fix: the tower nudged inward so only ~8px of its face projects past the wall line
    moat = [[176, 176], [824, 176], [824, 824], [176, 824], [176, 176]]
    M = _fort_city(moat=moat, moat_width=22, wall_towers=[{"x": 212, "y": 500, "w": 38, "h": 38, "rot": 0}])
    assert "city_wall_furniture_clear_of_moat" not in f_only(M, "city_wall_furniture_clear_of_moat")


@pytest.mark.tiers("city")
def test_city_wall_towers_spaced_fires_with_only_gate_towers():
    M = _fort_city(wall_towers=[{"x": 500, "y": 200}, {"x": 500, "y": 800}])  # only the 2 gate towers
    assert "city_wall_towers_spaced" in f_only(M, "city_wall_towers_spaced")


@pytest.mark.tiers("city")
def test_city_wall_towers_spaced_passes_when_ringed():

    towers = [{"x": 500 + 300 * math.cos(i * math.pi / 5), "y": 500 + 300 * math.sin(i * math.pi / 5)} for i in range(10)]
    assert "city_wall_towers_spaced" not in f_only(_fort_city(wall_towers=towers), "city_wall_towers_spaced")


@pytest.mark.tiers("city")
def test_city_wall_towers_aligned_fires_when_axis_aligned_on_a_slanted_wall():
    M = _fort_city(wall=_DIAMOND, wall_towers=[{"x": 650, "y": 350, "rot": 0}, {"x": 350, "y": 650, "rot": 0}])
    assert "city_wall_towers_aligned" in f_only(M, "city_wall_towers_aligned")


@pytest.mark.tiers("city")
def test_city_wall_towers_aligned_passes_when_square_to_the_wall():
    # both towers sit on a 45 deg wall edge and are rotated 45 deg to match it
    M = _fort_city(wall=_DIAMOND, wall_towers=[{"x": 650, "y": 350, "rot": 45}, {"x": 350, "y": 650, "rot": 45}])
    assert "city_wall_towers_aligned" not in f_only(M, "city_wall_towers_aligned")


@pytest.mark.tiers("city")
def test_city_gate_furniture_aligned_fires_when_axis_aligned_on_a_slanted_wall():
    # guard house + inspection station left axis-aligned (rot 0) on a 45 deg wall edge
    M = _gate_furn(0, wall=_DIAMOND, gates=[[650, 350], [350, 650]])
    M["gate_structs"] = [{"x": 640, "y": 360, "w": 66, "h": 44, "rot": 0, "kind": "guardhouse", "z": 1}, {"x": 610, "y": 390, "w": 60, "h": 44, "rot": 0, "kind": "inspection", "z": 1}]
    assert "city_gate_furniture_aligned" in f_only(M, "city_gate_furniture_aligned")


@pytest.mark.tiers("city")
def test_city_gate_furniture_aligned_passes_when_square_to_the_wall():
    M = _gate_furn(45, wall=_DIAMOND, gates=[[650, 350], [350, 650]])
    M["gate_structs"] = [{"x": 640, "y": 360, "w": 66, "h": 44, "rot": 45, "kind": "guardhouse", "z": 1}, {"x": 610, "y": 390, "w": 60, "h": 44, "rot": 45, "kind": "inspection", "z": 1}]
    assert "city_gate_furniture_aligned" not in f_only(M, "city_gate_furniture_aligned")


@pytest.mark.tiers("city")
def test_city_gate_furniture_aligned_fires_on_a_90_degree_turn():
    # on the horizontal top wall a guard house turned 90 deg stands across the road the wrong way
    assert "city_gate_furniture_aligned" in f_only(_gate_furn(90), "city_gate_furniture_aligned")


@pytest.mark.tiers("city")
def test_city_gate_furniture_aligned_passes_when_along_the_wall():
    assert "city_gate_furniture_aligned" not in f_only(_gate_furn(0), "city_gate_furniture_aligned")


@pytest.mark.tiers("city")
def test_city_gate_furniture_at_throat_passes_when_hard_by_the_gate():
    # guard house + inspection station flanking the road right at each gate opening (~45px in)
    M = _fort_city(
        gate_structs=[
            {"x": 480, "y": 240, "w": 11, "h": 7, "kind": "guardhouse"},
            {"x": 520, "y": 240, "w": 15, "h": 7, "kind": "inspection"},
            {"x": 480, "y": 760, "w": 11, "h": 7, "kind": "guardhouse"},
            {"x": 520, "y": 760, "w": 15, "h": 7, "kind": "inspection"},
        ],
        inspection_stations=[{"x": 520, "y": 240, "w": 15, "h": 7}, {"x": 520, "y": 760, "w": 15, "h": 7}],
    )
    assert "city_gate_furniture_at_throat" not in f_only(M, "city_gate_furniture_at_throat")


@pytest.mark.tiers("city")
def test_city_gate_furniture_at_throat_fires_when_walked_back_along_the_wall():
    # the north-gate guard house (~85px) and inspection (~146px) walked back along the wall: the looser
    # 160/180px gate radii still PASS (no teeth), but the ~70px throat check catches the far placement
    M = _fort_city(
        gate_structs=[
            {"x": 440, "y": 260, "w": 11, "h": 7, "kind": "guardhouse"},
            {"x": 360, "y": 240, "w": 15, "h": 7, "kind": "inspection"},
            {"x": 480, "y": 760, "w": 11, "h": 7, "kind": "guardhouse"},
            {"x": 520, "y": 760, "w": 15, "h": 7, "kind": "inspection"},
        ],
        inspection_stations=[{"x": 360, "y": 240, "w": 15, "h": 7}, {"x": 520, "y": 760, "w": 15, "h": 7}],
    )
    fails = f(M)
    assert "city_gate_furniture_at_throat" in fails
    assert "city_inspection_station_at_each_gate" not in fails  # the loose radii wave the far placement through...
    assert "city_gate_has_guardhouse" not in fails  # ...which is exactly why the throat check exists


@pytest.mark.tiers("city")
def test_city_gate_tower_at_its_gate_passes_when_the_tower_is_closest():
    # each gate's own tower (a gate_structs "tower") is the CLOSEST tower to its opening; mural bastions sit further
    M = _fort_city(
        gate_structs=[{"x": 500, "y": 280, "w": 17, "h": 10, "kind": "tower"}, {"x": 500, "y": 720, "w": 17, "h": 10, "kind": "tower"}],
        wall_towers=[{"x": 500, "y": 280, "w": 17, "h": 10}, {"x": 420, "y": 250, "w": 21, "h": 13}, {"x": 500, "y": 720, "w": 17, "h": 10}, {"x": 420, "y": 750, "w": 21, "h": 13}],
    )
    assert "city_gate_tower_at_its_gate" not in f_only(M, "city_gate_tower_at_its_gate")


@pytest.mark.tiers("city")
def test_city_gate_tower_at_its_gate_fires_when_a_mural_is_closer():
    # the N gate's own tower is marooned out (dist 140) while a mural bastion sits closer (dist 90)
    M = _fort_city(
        gate_structs=[{"x": 500, "y": 340, "w": 17, "h": 10, "kind": "tower"}, {"x": 500, "y": 720, "w": 17, "h": 10, "kind": "tower"}],
        wall_towers=[{"x": 500, "y": 340, "w": 17, "h": 10}, {"x": 500, "y": 290, "w": 21, "h": 13}, {"x": 500, "y": 720, "w": 17, "h": 10}, {"x": 420, "y": 750, "w": 21, "h": 13}],
    )
    assert "city_gate_tower_at_its_gate" in f_only(M, "city_gate_tower_at_its_gate")


@pytest.mark.tiers("city")
def test_city_merchant_housing_spread_fires_when_jammed():
    # merchant homes jammed as tight as the laborers (same ~16px spacing) - not more spread out
    homes = [bldg(300 + i * 16, 300, kind="merchant_house") for i in range(8)]
    labor = [bldg(300 + i * 16, 500, kind="laborer") for i in range(8)]
    assert "city_merchant_housing_spread" in f_only(_merchant_city(homes + labor), "city_merchant_housing_spread")


@pytest.mark.tiers("city")
def test_city_merchant_housing_spread_passes_when_roomier():
    homes = [bldg(300 + i * 44, 300, kind="merchant_house") for i in range(8)]  # 44px apart
    labor = [bldg(300 + i * 16, 500, kind="laborer") for i in range(8)]  # 16px apart (dense)
    assert "city_merchant_housing_spread" not in f_only(_merchant_city(homes + labor), "city_merchant_housing_spread")


@pytest.mark.tiers("city")
def test_walled_city_structural_checks_fire():
    M = {"meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000}, "wall": WALLSQ, "gates": [[500, 200]]}  # only ONE gate, no stations / burakumin / estates / road
    fails = f(M)
    assert "walled_city_has_wall_and_gates" in fails
    assert "city_inspection_station_at_each_gate" in fails
    assert "walled_city_has_burakumin_inside" in fails
    assert "city_samurai_estates_outside" in fails  # 0 estates, want 1-3
    assert "city_imperial_road_through" in fails


@pytest.mark.tiers("city")
def test_city_civic_amenity_checks_fire_on_an_empty_city():
    fails = f({"meta": {"scale": "city"}})
    for name in ("city_has_merchant_storehouses", "city_has_flophouse", "city_has_theater_stage"):
        assert name in fails


@pytest.mark.tiers("city")
def test_city_civic_label_on_its_own_building_fires_over_a_sibling_ministry():
    # the "Ministry of Justice" label drifts onto the "Ministry of Works" office - same group, so
    # labels_clear_of_other_buildings misses it, but this finer check catches it
    M = {
        "meta": {"scale": "city"},
        "ministries": [{"name": "Ministry of Works", "x": 500, "y": 500, "w": 88, "h": 58}, {"name": "Ministry of Justice", "x": 500, "y": 640, "w": 88, "h": 58}],
        "labels": [[470, 490, 560, 510, 1, "Ministry of Justice"]],
    }
    assert "city_civic_label_on_its_own_building" in f_only(M, "city_civic_label_on_its_own_building")
    assert "labels_clear_of_other_buildings" not in f_only(M, "labels_clear_of_other_buildings")  # the coarse check is fooled by the shared group


@pytest.mark.tiers("city")
def test_city_civic_label_on_its_own_building_passes_over_its_own():
    M = {"meta": {"scale": "city"}, "ministries": [{"name": "Ministry of Works", "x": 500, "y": 500, "w": 88, "h": 58}], "labels": [[470, 490, 560, 510, 1, "Ministry of Works"]]}
    assert "city_civic_label_on_its_own_building" not in f_only(M, "city_civic_label_on_its_own_building")


@pytest.mark.tiers("city")
def test_city_government_offices_dont_abut_fires_when_two_ministries_touch():
    M = {
        "meta": {"scale": "city"},
        "ministries": [{"name": "Ministry of Works", "x": 500, "y": 500, "w": 88, "h": 58}, {"name": "Ministry of Justice", "x": 500, "y": 560, "w": 88, "h": 58}],
    }  # 2px gap
    assert "city_government_offices_dont_abut" in f_only(M, "city_government_offices_dont_abut")


@pytest.mark.tiers("city")
def test_city_government_offices_dont_abut_passes_when_clear():
    M = {
        "meta": {"scale": "city"},
        "ministries": [{"name": "Ministry of Works", "x": 500, "y": 500, "w": 88, "h": 58}, {"name": "Ministry of Justice", "x": 500, "y": 640, "w": 88, "h": 58}],
    }  # 82px gap
    assert "city_government_offices_dont_abut" not in f_only(M, "city_government_offices_dont_abut")


@pytest.mark.tiers("city")
def test_city_government_offices_dont_abut_ignores_ordinary_houses():
    # ordinary city houses MAY touch - only government offices must stand clear
    M = {"meta": {"scale": "city"}, "buildings": [{"kind": "laborer", "x": 500, "y": 500, "w": 14, "h": 10, "rot": 0}, {"kind": "laborer", "x": 512, "y": 500, "w": 14, "h": 10, "rot": 0}]}
    assert "city_government_offices_dont_abut" not in f_only(M, "city_government_offices_dont_abut")


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
def test_city_has_fire_towers_fires_with_one():
    assert "city_has_fire_towers" in f_only({"meta": {"scale": "city"}, "fire_towers": [_tower(500, 500)]}, "city_has_fire_towers")


@pytest.mark.tiers("city")
def test_city_has_fire_towers_passes_with_two():
    assert "city_has_fire_towers" not in f_only({"meta": {"scale": "city"}, "fire_towers": [_tower(500, 500), _tower(700, 700)]}, "city_has_fire_towers")


@pytest.mark.tiers("city")
def test_city_has_fire_towers_opt_out():
    assert "city_has_fire_towers" not in f_only({"meta": {"scale": "city", "fire_tower": False}}, "city_has_fire_towers")


@pytest.mark.tiers("city")
def test_city_martial_hall_keeps_a_full_length_archery_lane():
    # the lane covers the kyudo standard 28 m / 92 ft shot (floored at the ~90 ft clear lane the
    # Mode A azuchi uses); a lane shorter than that is not a shooting ground
    assert "city_martial_hall_has_archery_range" not in f_only(_martial_city(range_ft=100.0), "city_martial_hall_has_archery_range")
    assert "city_martial_hall_has_archery_range" not in f_only(_martial_city(range_ft=90.0), "city_martial_hall_has_archery_range")
    assert "city_martial_hall_has_archery_range" in f_only(_martial_city(range_ft=60.0), "city_martial_hall_has_archery_range")


@pytest.mark.tiers("city")
def test_city_dojo_count_follows_the_samurai_cohort_formula():
    # GM formula 2026-07-25: 1 private dojo per full 200 samurai (a city's ~10% share) + a
    # remainder-fraction chance of one extra, floored at 1; a recorded roll must match the drawn
    # count. 2,000 -> 200 samurai -> exactly 1; 3,000 -> 300 -> 1 or 2; 4,000 -> 400 -> exactly 2.
    assert "city_dojo_count_follows_samurai" not in f_only(_martial_city(pop=2000, dojos=1), "city_dojo_count_follows_samurai")
    assert "city_dojo_count_follows_samurai" in f_only(_martial_city(pop=2000, dojos=2), "city_dojo_count_follows_samurai")
    assert "city_dojo_count_follows_samurai" not in f_only(_martial_city(pop=3000, dojos=1), "city_dojo_count_follows_samurai")
    assert "city_dojo_count_follows_samurai" not in f_only(_martial_city(pop=3000, dojos=2), "city_dojo_count_follows_samurai")
    assert "city_dojo_count_follows_samurai" in f_only(_martial_city(pop=3000, dojos=3), "city_dojo_count_follows_samurai")
    assert "city_dojo_count_follows_samurai" in f_only(_martial_city(pop=4000, dojos=1), "city_dojo_count_follows_samurai")
    assert "city_dojo_count_follows_samurai" in f_only(_martial_city(pop=3000, dojos=1, roll=2), "city_dojo_count_follows_samurai")  # stale hand count
    assert "city_dojo_count_follows_samurai" not in f_only(_martial_city(pop=3000, dojos=1, roll=1), "city_dojo_count_follows_samurai")


@pytest.mark.tiers("city")
def test_city_dojos_stand_among_the_samurai_they_serve():
    # a dojo serves samurai and nobody else, so both the state hall and the private halls sit in
    # or against the samurai neighborhood - not out among the merchant rows or laborer warrens
    assert "city_dojos_among_samurai" not in f_only(_martial_city(), "city_dojos_among_samurai")
    assert "city_dojos_among_samurai" in f_only(_martial_city(dojo_xy=(830, 850)), "city_dojos_among_samurai")  # a private hall adrift
    assert "city_dojos_among_samurai" in f_only(_martial_city(hall_xy=(830, 180)), "city_dojos_among_samurai")  # the state hall adrift


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
