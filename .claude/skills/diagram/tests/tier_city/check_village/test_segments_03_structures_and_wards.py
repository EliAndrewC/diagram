"""tier city tests split out of `tests.check_village.test_segments_03_structures_and_wards` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _CHAN,
    _MOAT,
    WALL,
    WALLSQ,
    _capital_manifest,
    _fort_city,
    _maus_ward,
    _walled,
    _ward_wall,
    bldg,
    f_only,
)


@pytest.mark.tiers("city")
def test_irrigation_channels_hairline_allows_a_drain_outfall_culvert_at_four():
    # a drain-outfall culvert carries the fan's whole runoff and matches the drain's outfall width
    # (4.0 at the city grain) - it is not a field ditch, so its ceiling is 4.5 (GM 2026-07-23)
    M = {"channels": [{"poly": _CHAN, "frm": {"kind": "drain"}, "to": {"kind": "moat"}, "w": 4.0}]}
    assert "irrigation_channels_hairline" not in f_only(M, "irrigation_channels_hairline")


@pytest.mark.tiers("city")
def test_city_lane_under_wall_fires_when_a_street_touches_the_wall():
    # a street whose end reaches the wall (z above the rampart's) renders OVER it - away from any gate
    M = _walled(streets=[{"pts": [[300, 300], [300, 205]], "w": 18, "z": 100}])
    assert "city_lane_under_wall" in f_only(M, "city_lane_under_wall")


@pytest.mark.tiers("city")
def test_city_lane_under_wall_fires_when_a_street_crosses_the_wall():
    M = _walled(streets=[{"pts": [[300, 150], [300, 300]], "w": 18, "z": 100}])  # crosses the top edge off-gate
    assert "city_lane_under_wall" in f_only(M, "city_lane_under_wall")


@pytest.mark.tiers("city")
def test_city_lane_under_wall_passes_at_a_gate_opening():
    # a road through the gate crosses the wall ring there, but the gate is a genuine opening - exempt
    M = _walled(streets=[{"pts": [[500, 400], [500, 150]], "w": 18, "z": 100}])  # crosses at the gate (500,200)
    assert "city_lane_under_wall" not in f_only(M, "city_lane_under_wall")


@pytest.mark.tiers("city")
def test_city_lane_under_wall_passes_when_lane_already_under():
    M = _walled(streets=[{"pts": [[300, 300], [300, 205]], "w": 18, "z": 5}])  # z below wall_z (10)
    assert "city_lane_under_wall" not in f_only(M, "city_lane_under_wall")


@pytest.mark.tiers("city")
def test_city_lanes_under_ward_fences_fires_when_a_lane_renders_over_a_fence():
    M = {"meta": {"scale": "city"}, "wards": [{"name": "samurai", "boundary": [[300, 500], [700, 500]], "z": 10}], "alleys": [{"pts": [[400, 300], [400, 505]], "w": 10, "z": 100}]}
    assert "city_lanes_under_ward_fences" in f_only(M, "city_lanes_under_ward_fences")


@pytest.mark.tiers("city")
def test_city_lanes_under_ward_fences_passes_when_crossing_at_a_kido():
    M = {
        "meta": {"scale": "city"},
        "wards": [{"name": "samurai", "boundary": [[300, 500], [700, 500]], "z": 10}],
        "kido": [{"x": 400, "y": 500}],
        "alleys": [{"pts": [[400, 300], [400, 505]], "w": 10, "z": 100}],
    }
    assert "city_lanes_under_ward_fences" not in f_only(M, "city_lanes_under_ward_fences")


@pytest.mark.tiers("city")
def test_label_hugs_its_referent_skips_a_caption_with_no_subject():
    # a district caption names an AREA, not a feature, so it records no referent and is exempt
    # (city_labels_placed_with_subject governs those instead)
    M = {"meta": {}, "labels": [[400, 500, 560, 512.6, 1, "samurai neighborhood"]]}
    assert "label_hugs_its_referent" not in f_only(M, "label_hugs_its_referent")


@pytest.mark.tiers("city")
def test_no_structure_on_canal_fires_and_passes():
    # GM 2026-07 (Nagahara, first city with a cargo canal): a merchant house in the canal water
    canal = [{"poly": [[300, 500], [700, 500]], "w": 14}]
    fire = {"canals": canal, "buildings": [{"x": 500, "y": 500, "w": 24, "h": 18, "rot": 0, "kind": "merchant_house"}]}
    assert "no_structure_on_canal" in f_only(fire, "no_structure_on_canal")
    ok = {"canals": canal, "buildings": [{"x": 500, "y": 440, "w": 24, "h": 18, "rot": 0, "kind": "merchant_house"}]}
    assert "no_structure_on_canal" not in f_only(ok, "no_structure_on_canal")


@pytest.mark.tiers("city")
def test_city_ward_cap_flush_to_wall_fires_when_a_cap_juts():
    # a straight cap whose far vertex juts 30px off the wall face (the corner-stub artifact)
    ward = {"name": "samurai", "boundary": [[200, 500], [500, 500]], "wall_caps": [{"x": 200, "y": 500, "pts": [[200, 500], [230, 500]]}]}
    assert "city_ward_cap_flush_to_wall" in f_only(_fort_city(wards=[ward]), "city_ward_cap_flush_to_wall")


@pytest.mark.tiers("city")
def test_city_ward_cap_flush_to_wall_passes_when_flush():
    # a cap that lies ALONG the west wall face (x=200): both vertices sit on the wall
    ward = {"name": "samurai", "boundary": [[200, 500], [500, 500]], "wall_caps": [{"x": 200, "y": 500, "pts": [[200, 484], [200, 516]]}]}
    assert "city_ward_cap_flush_to_wall" not in f_only(_fort_city(wards=[ward]), "city_ward_cap_flush_to_wall")


@pytest.mark.tiers("city")
def test_alleys_serve_buildings_fires_on_a_lane_to_nowhere():
    # a 400px alley serving only two dwellings - a lane running off into empty space
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "alleys": [{"pts": [[500, 300], [500, 700]], "w": 10}],
        "buildings": [bldg(530, 320, kind="laborer"), bldg(530, 360, kind="laborer")],
    }
    assert "alleys_serve_buildings" in f_only(M, "alleys_serve_buildings")


@pytest.mark.tiers("city")
def test_walled_structure_yields_to_ward_wall_fires_on_a_vertical_fence():
    # the mausoleum's EAST wall (x = cx+27 = 1535) runs along a VERTICAL ward fence at x=1535
    M = {
        "meta": {"scale": "city", "walled": True},
        "wall": [[100, 100], [3000, 100], [3000, 2500], [100, 2500]],
        "wards": [{"name": "samurai", "boundary": [[1535, 1200], [1535, 1900]], "z": 5}],
        "mausoleums": [{"x": 1508, "y": 1556, "w": 54, "h": 40, "rot": 0, "gate_dir": "west", "ward_walls": []}],
    }
    assert "walled_structure_yields_to_ward_wall" in f_only(M, "walled_structure_yields_to_ward_wall")


@pytest.mark.tiers("city")
def test_walled_structure_yields_to_ward_wall_skips_compounds_outside_the_wall():
    # a compound OUTSIDE the city wall is not held to the rule (wards are an intramural feature)
    M = _maus_ward([])
    M["mausoleums"][0]["x"], M["mausoleums"][0]["y"] = 50, 50  # west of the wall (x >= 100): outside
    assert "walled_structure_yields_to_ward_wall" not in f_only(M, "walled_structure_yields_to_ward_wall")


@pytest.mark.tiers("city")
def test_no_structure_on_moat_fires_when_a_structure_sits_on_it():
    M = {
        "meta": {"scale": "city"},
        "wall": [[200, 200], [800, 200], [800, 800], [200, 800]],
        "moat": _MOAT,
        "moat_width": 22,
        "buildings": [
            {"x": 168, "y": 500, "w": 44, "h": 30, "rot": 0, "kind": "laborer"},  # a corner within the moat band
            {"x": 160, "y": 160, "w": 70, "h": 70, "rot": 0, "kind": "laborer"},
        ],
    }  # a moat vertex inside the footprint
    assert "no_structure_on_moat" in f_only(M, "no_structure_on_moat")


@pytest.mark.tiers("city")
def test_torii_and_religious_clear_of_works_and_ring():
    # GM placement rules (2026-07-21, caught on Tango): torii keep clear of halls/towers/the ring
    # road; religious footprints keep clear of towers/the ring road. An ordinary street through a
    # torii stays legal (only the RING corridor counts), so no street data appears here.
    base = {"meta": {"scale": "city", "ftpx": 3}, "ring_road": [[100, 900], [900, 900]], "ring_road_width": 8, "wall_towers": [{"x": 500, "y": 500, "w": 38, "h": 38}]}
    hall = {"kind": "temple", "x": 300, "y": 300, "w": 43, "h": 28, "label": "Temple of Ebisu"}
    # torii: on the hall / on the tower / on the ring -> fire; standing clear -> pass
    assert "torii_clear_of_halls_towers_ring" in f_only({**base, "religious": [hall], "torii": [[305, 310, 9]]}, "torii_clear_of_halls_towers_ring")
    assert "torii_clear_of_halls_towers_ring" in f_only({**base, "religious": [hall], "torii": [[505, 512, 9]]}, "torii_clear_of_halls_towers_ring")
    assert "torii_clear_of_halls_towers_ring" in f_only({**base, "religious": [hall], "torii": [[400, 902, 9]]}, "torii_clear_of_halls_towers_ring")
    assert "torii_clear_of_halls_towers_ring" not in f_only({**base, "religious": [hall], "torii": [[300, 380, 9]]}, "torii_clear_of_halls_towers_ring")
    # religious: the Tango defect (shrine on a wall tower) and a hall on the ring -> fire; clear -> pass
    shrine_on_tower = {"kind": "small_shrine", "x": 521, "y": 509, "w": 11, "h": 8}
    assert "religious_clear_of_ring_and_towers" in f_only({**base, "religious": [shrine_on_tower]}, "religious_clear_of_ring_and_towers")
    assert "religious_clear_of_ring_and_towers" in f_only({**base, "religious": [{**hall, "y": 890}]}, "religious_clear_of_ring_and_towers")
    # ...and a hall standing ON THE EDGE of the roadbed without crossing its centerline: entirely
    # south of y=900 but lapping the bed's 896-904 span. Crossing and proximity are separate
    # branches of the corridor test and this is the one only proximity catches.
    assert "religious_clear_of_ring_and_towers" in f_only({**base, "religious": [{**hall, "y": 916}]}, "religious_clear_of_ring_and_towers")
    assert "religious_clear_of_ring_and_towers" not in f_only({**base, "religious": [hall]}, "religious_clear_of_ring_and_towers")


@pytest.mark.tiers("city")
def test_torii_clear_of_walls():
    # GM 2026-07-25, caught on Nagahara: the 7th arch of the Ebisu sando stood IN the samurai ward
    # fence. A torii is a FREESTANDING gateway and a wall is a continuous barrier, so an arch never
    # stands in one - a way through a wall is a GATE. Every wall counts: the city rampart, a ward
    # fence (and its wall-cap), and the perimeter of a walled compound.
    base = {"meta": {"scale": "city", "ftpx": 3}}
    fence = {"name": "samurai", "boundary": [[300, 700], [900, 700]], "z": 10, "wall_caps": []}
    manor = {"x": 400, "y": 400, "w": 60, "h": 40, "rot": 0, "wall_w": 2}
    assert "torii_clear_of_walls" in f_only({**base, "wards": [fence], "torii": [[600, 699, 9]]}, "torii_clear_of_walls")  # the Nagahara defect
    assert "torii_clear_of_walls" not in f_only({**base, "wards": [fence], "torii": [[600, 680, 9]]}, "torii_clear_of_walls")  # the sando stops short
    assert "torii_clear_of_walls" in f_only({**base, "wall": WALL, "torii": [[500, 52, 9]]}, "torii_clear_of_walls")  # standing in the rampart
    assert "torii_clear_of_walls" in f_only(
        {**base, "wards": [{**fence, "wall_caps": [{"x": 300, "y": 700, "z": 3, "pts": [[290, 690], [290, 760]]}]}], "torii": [[290, 730, 9]]}, "torii_clear_of_walls"
    )
    assert "torii_clear_of_walls" in f_only({**base, "manors": [manor], "torii": [[400, 420, 9]]}, "torii_clear_of_walls")  # in a compound wall
    assert "torii_clear_of_walls" not in f_only({**base, "manors": [manor], "torii": [[400, 460, 9]]}, "torii_clear_of_walls")
    assert "torii_clear_of_walls" in f_only({**base, "governor_mansion": {**manor, "x": 700}, "torii": [[700, 420, 9]]}, "torii_clear_of_walls")
    assert "torii_clear_of_walls" in f_only({**base, "merchant_estates": [{**manor, "y": 200}], "torii": [[430, 200, 9]]}, "torii_clear_of_walls")
    assert "torii_clear_of_walls" in f_only({**base, "mausoleums": [{**manor, "y": 900}], "torii": [[370, 900, 9]]}, "torii_clear_of_walls")
    # a run that ENDS inside the arch box, crossing none of its edges, still counts as standing in it
    assert "torii_clear_of_walls" in f_only({**base, "wards": [{**fence, "boundary": [[599, 700], [601, 701]]}], "torii": [[600, 700, 9]]}, "torii_clear_of_walls")


@pytest.mark.tiers("city")
def test_city_ward_fence_joins_wall_not_crosses_fires_on_an_end_poking_through():
    # the fence runs up to the north rampart (y50) and out the far side by 10px
    M = _ward_wall([[500, 400], [500, 40]])
    assert "city_ward_fence_joins_wall_not_crosses" in f_only(M, "city_ward_fence_joins_wall_not_crosses")


@pytest.mark.tiers("city")
def test_city_ward_fence_joins_wall_not_crosses_clear_when_the_end_lands_on_the_centerline():
    # ending ON the wall line is the JOIN: the 2.5px linecap tip stays inside the 5.5px rampart band
    M = _ward_wall([[500, 400], [500, 50]])
    assert "city_ward_fence_joins_wall_not_crosses" not in f_only(M, "city_ward_fence_joins_wall_not_crosses")


@pytest.mark.tiers("city")
def test_city_ward_fence_joins_wall_not_crosses_reads_the_INK_not_the_vertex():
    # the Minami shape, and the reason the defect shipped green: the end vertex sits only 4px
    # outside the wall - well inside city_ward_fence_meets_wall's 10px tolerance, so THAT check
    # passes - but the fence's round linecap inks 2.5px further, putting 1px of palisade past the
    # rampart's 5.5px half-width. Testing the recorded coordinate alone would see nothing here.
    M = _ward_wall([[500, 400], [500, 46]])
    assert "city_ward_fence_meets_wall" not in f_only(M, "city_ward_fence_meets_wall")
    assert "city_ward_fence_joins_wall_not_crosses" in f_only(M, "city_ward_fence_joins_wall_not_crosses")


@pytest.mark.tiers("city")
def test_city_ward_fence_joins_wall_not_crosses_fires_on_a_crossing_mid_run():
    # both ENDS are inside; the fence dives out through the north rampart and back mid-run
    M = _ward_wall([[400, 400], [500, 20], [600, 400]])
    assert "city_ward_fence_joins_wall_not_crosses" in f_only(M, "city_ward_fence_joins_wall_not_crosses")


@pytest.mark.tiers("city")
def test_city_ward_fence_joins_wall_not_crosses_ignores_a_degenerate_boundary():
    M = _ward_wall([[500, 400]])
    assert "city_ward_fence_joins_wall_not_crosses" not in f_only(M, "city_ward_fence_joins_wall_not_crosses")


@pytest.mark.tiers("capital", "city")
def test_religious_matches_scale_capital_takes_temples():
    """A capital is the city tier at 4x - temples, same as a provincial city. The scale map did
    not know 'capital' and demanded NO religious building at all (feature 020)."""
    M = _capital_manifest()
    M["religious"] = [{"kind": "temple", "label": "Temple of Benten", "x": 500, "y": 500, "w": 50, "h": 33, "torii_count": 1}]
    M["torii"] = [[500, 560, 1]]
    assert "religious_matches_scale" not in f_only(M, "religious_matches_scale")


@pytest.mark.tiers("city")
def test_businesses_on_street_measured_from_bed_edge():
    """021: the on-street reach is bed half-width + 85 real ft - a shop hugging a wide trunk
    road's paving edge is ON the street; one two blocks out is not."""
    M = _capital_manifest(scale="city")
    M["road"] = [[500, 0], [500, 1000]]
    M["road_width"] = 26
    M["buildings"] = [{"kind": "shop", "x": 530, "y": 400, "w": 8, "h": 6}]  # 30px out: edge-hugging
    assert "businesses_front_streets" not in f_only(M, "businesses_front_streets")
    M["buildings"] = [{"kind": "shop", "x": 620, "y": 400, "w": 8, "h": 6}]  # 120px out: interior
    assert "businesses_front_streets" in f_only(M, "businesses_front_streets")
