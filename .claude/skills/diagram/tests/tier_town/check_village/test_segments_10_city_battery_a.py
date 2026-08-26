"""tier town tests split out of `tests.check_village.test_segments_10_city_battery_a` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _STAGE,
    WALLSQ,
    _block,
    _field,
    _fort_city,
    _martial_city,
    _tower,
    _well_city,
    bldg,
    f,
    f_only,
)


@pytest.mark.tiers("town")
def test_kido_aligned_squares_to_the_lane_it_bars_not_the_oblique_fence_it_hangs_in():
    # GM 2026-07-26: a kido shuts a WAY, so where a lane runs through the seat the bar stands
    # SQUARE ACROSS THE LANE, and the fence meets it at whatever angle the fence runs. Tango's SW
    # ring-road gate followed its ~44deg fence jog while the road it barred ran at ~172deg - 38deg
    # off square to its own roadbed. Here: a 45deg fence, a HORIZONTAL street through the gate, so
    # the bar wants 90deg (vertical, across the street), NOT the fence's 45.
    ward = [{"name": "w", "boundary": [[300, 300], [600, 600]], "z": 1, "wall_caps": []}]
    street = [{"pts": [[300, 450], [600, 450]], "w": 18}]
    fenced = _fort_city(wards=ward, town_streets=street, kido=[{"x": 450, "y": 450, "rot": 45.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" in f_only(fenced, "kido_aligned_with_ward_fence")  # square to the FENCE is now the defect, because a lane runs through
    squared = _fort_city(wards=ward, town_streets=street, kido=[{"x": 450, "y": 450, "rot": 90.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" not in f_only(squared, "kido_aligned_with_ward_fence")
    # a street laid ALONGSIDE the fence is not something the gate bars, so it must not be what the
    # gate squares to - the fence tangent still rules there
    along = _fort_city(wards=ward, town_streets=[{"pts": [[300, 290], [600, 590]], "w": 18}], kido=[{"x": 450, "y": 450, "rot": 45.0, "bbox": [430, 430, 470, 470]}])
    assert "kido_aligned_with_ward_fence" not in f_only(along, "kido_aligned_with_ward_fence")


@pytest.mark.tiers("city", "town")
def test_city_samurai_partly_front_streets_fires_when_all_set_back():
    # plenty of samurai houses but every one buried far from the street: a samurai quarter LINES its
    # streets, so an all-interior cluster (none within 90px of a lane) trips the check.
    sam = [bldg(300 + (i % 8) * 30, 300 + (i // 8) * 30, kind="samurai") for i in range(40)]  # all up in the NW corner
    M = {
        "meta": {"scale": "city", "walled": True, "population": 3000, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[600, 600], [800, 600]], "w": 18}],  # the only street is far from the cluster
        "buildings": sam,
    }
    assert "city_samurai_partly_front_streets" in f_only(M, "city_samurai_partly_front_streets")


@pytest.mark.tiers("city", "town")
def test_city_theater_stage_larger_than_town_fires_when_small():
    # a town-sized theater stage (viewing ground 150 wide) in a city - a city's is larger (>= 185)
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "theater_stage": {"x": 500, "y": 500, "w": 150, "h": 105, "rot": 0},
        "religious": [{"x": 540, "y": 540, "w": 120, "h": 80, "rot": 0, "kind": "temple"}],
    }
    assert "city_theater_stage_larger_than_town" in f_only(M, "city_theater_stage_larger_than_town")


@pytest.mark.tiers("town")
def test_theater_stage_by_temple_fires_when_far_from_any_hall():
    # a town theater stage sited off on its own, far from any temple/monastery - it was a temple/shrine
    # performance stage, so it must sit ADJACENT to a religious hall
    M = {"meta": {"scale": "town"}, "theater_stage": {"x": 500, "y": 500, "w": 150, "h": 105, "rot": 0}, "religious": [{"x": 1200, "y": 1200, "w": 132, "h": 86, "rot": 0, "kind": "monastery"}]}
    assert "theater_stage_by_temple" in f_only(M, "theater_stage_by_temple")


@pytest.mark.tiers("town")
def test_theater_stage_by_temple_passes_when_adjacent():
    M = {"meta": {"scale": "town"}, "theater_stage": {"x": 500, "y": 500, "w": 150, "h": 105, "rot": 0}, "religious": [{"x": 540, "y": 620, "w": 132, "h": 86, "rot": 0, "kind": "monastery"}]}
    assert "theater_stage_by_temple" not in f_only(M, "theater_stage_by_temple")


@pytest.mark.tiers("town")
def test_theater_stage_faces_temple_fires_when_back_to_the_hall():
    # adjacent to the monastery (NORTH) but the stage's viewing ground opens SOUTH (rot=0) - its BACK is to
    # the hall, the audience facing away. This is the Hoshizora bug the check is meant to catch.
    M = {"meta": {"scale": "town"}, "theater_stage": {"x": 500, "y": 500, "w": 150, "h": 105, "rot": 0}, "religious": [{"x": 510, "y": 380, "w": 132, "h": 86, "rot": 0, "kind": "monastery"}]}
    assert "theater_stage_faces_temple" in f_only(M, "theater_stage_faces_temple")


@pytest.mark.tiers("town")
def test_theater_stage_faces_temple_passes_when_open_toward_hall():
    # the hall is SOUTH and the ground opens SOUTH (rot=0) - the stage faces the hall, audience between
    M = {"meta": {"scale": "town"}, "theater_stage": {"x": 500, "y": 500, "w": 150, "h": 105, "rot": 0}, "religious": [{"x": 510, "y": 640, "w": 132, "h": 86, "rot": 0, "kind": "monastery"}]}
    assert "theater_stage_faces_temple" not in f_only(M, "theater_stage_faces_temple")


@pytest.mark.tiers("town")
def test_theater_stage_clear_fires_on_a_wall():
    M = {"meta": {"scale": "town"}, "theater_stage": dict(_STAGE), "wall": [[500, 380], [500, 620]]}
    assert "theater_stage_clear" in f_only(M, "theater_stage_clear")


@pytest.mark.tiers("town")
def test_theater_stage_clear_fires_on_a_building():
    M = {"meta": {"scale": "town"}, "theater_stage": dict(_STAGE), "buildings": [bldg(500, 500, "merchant")]}
    assert "theater_stage_clear" in f_only(M, "theater_stage_clear")


@pytest.mark.tiers("town")
def test_theater_stage_clear_fires_on_a_field():
    M = {"meta": {"scale": "town"}, "theater_stage": dict(_STAGE), "fields": [_field("f", 400, 400, 600, 600)]}
    assert "theater_stage_clear" in f_only(M, "theater_stage_clear")


@pytest.mark.tiers("town")
def test_theater_stage_clear_fires_on_the_pond():
    M = {"meta": {"scale": "town"}, "theater_stage": dict(_STAGE), "pond": [500, 500, 80, 60]}
    assert "theater_stage_clear" in f_only(M, "theater_stage_clear")


@pytest.mark.tiers("town")
def test_theater_stage_clear_passes_in_open_ground():
    M = {"meta": {"scale": "town"}, "theater_stage": dict(_STAGE), "religious": [{"x": 510, "y": 640, "w": 132, "h": 86, "rot": 0, "kind": "monastery"}]}
    assert "theater_stage_clear" not in f_only(M, "theater_stage_clear")


@pytest.mark.tiers("city", "town")
def test_city_wells_in_block_interiors_fires_on_a_lane():
    M = _well_city(town_streets=[{"pts": [[400, 500], [600, 500]], "w": 18}])
    assert "city_wells_in_block_interiors" in f_only(M, "city_wells_in_block_interiors")


@pytest.mark.tiers("town")
def test_fire_tower_in_commoner_quarter_fires_in_samurai_quarter():
    # a tower whose nearest neighbors are all samurai sits in the samurai quarter, not the warren
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "buildings": [bldg(520, 510, "samurai"), bldg(480, 515, "samurai"), bldg(510, 480, "samurai_large")]}
    assert "fire_tower_in_commoner_quarter" in f_only(M, "fire_tower_in_commoner_quarter")


@pytest.mark.tiers("town")
def test_fire_tower_in_commoner_quarter_fires_when_isolated():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "buildings": [bldg(900, 900, "laborer")]}  # nearest dwelling > 230px away
    assert "fire_tower_in_commoner_quarter" in f_only(M, "fire_tower_in_commoner_quarter")


@pytest.mark.tiers("town")
def test_fire_tower_in_commoner_quarter_passes_among_commoners():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "buildings": [bldg(520, 510, "laborer"), bldg(480, 515, "servant"), bldg(510, 480, "merchant")]}
    assert "fire_tower_in_commoner_quarter" not in f_only(M, "fire_tower_in_commoner_quarter")


@pytest.mark.tiers("town")
def test_fire_towers_dispersed_fires_when_bunched():
    # two towers 100 px apart (< one 230 px watch radius) watch the same rooftops twice
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500), _tower(600, 500)]}
    assert "fire_towers_dispersed" in f_only(M, "fire_towers_dispersed")


@pytest.mark.tiers("town")
def test_fire_towers_dispersed_passes_when_spread():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(400, 500), _tower(900, 500)]}
    assert "fire_towers_dispersed" not in f_only(M, "fire_towers_dispersed")


@pytest.mark.tiers("town")
def test_fire_towers_dispersed_ignores_a_single_tower():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)]}
    assert "fire_towers_dispersed" not in f_only(M, "fire_towers_dispersed")


@pytest.mark.tiers("town")
def test_fire_tower_amid_its_district_fires_when_towers_share_a_quarter():
    # both towers by the west block (though > one watch radius apart, so dispersal passes): the
    # second tower inherits the whole east block as its "district" and stands far off its centroid
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(470, 545), _tower(775, 545)], "buildings": _block(400, 500) + _block(1400, 500)}
    fails = f(M)
    assert "fire_tower_amid_its_district" in fails
    assert "fire_towers_dispersed" not in fails  # 305px apart - the old check alone misses this


@pytest.mark.tiers("town")
def test_fire_tower_amid_its_district_passes_with_one_tower_per_quarter():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(445, 545), _tower(1445, 545)], "buildings": _block(400, 500) + _block(1400, 500)}
    assert "fire_tower_amid_its_district" not in f_only(M, "fire_tower_amid_its_district")


@pytest.mark.tiers("town")
def test_fire_tower_amid_its_district_ignores_extramural_rows():
    # with a wall drawn, the gate-market rows OUTSIDE it are not part of any tower's district -
    # counting them would drag the east tower's centroid out and false-fire
    M = {
        "meta": {"scale": "town", "walled": True},
        "wall": [[100, 100], [1900, 100], [1900, 1000], [100, 1000]],
        "fire_towers": [_tower(445, 545), _tower(1445, 545)],
        "buildings": _block(400, 500) + _block(1400, 500) + _block(1400, 1200),
    }
    assert "fire_tower_amid_its_district" not in f_only(M, "fire_tower_amid_its_district")


@pytest.mark.tiers("town")
def test_fire_tower_standoff_fires_on_true_overlap_too():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "buildings": [bldg(510, 500, "laborer", w=40, h=28)]}
    assert "fire_tower_standoff" in f_only(M, "fire_tower_standoff")


@pytest.mark.tiers("town")
def test_fire_tower_standoff_passes_with_daylight():
    # 6px gap (centers 539 apart) clears the 5px rule
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "buildings": [bldg(539, 500, "laborer", w=40, h=28)]}
    assert "fire_tower_standoff" not in f_only(M, "fire_tower_standoff")


@pytest.mark.tiers("town")
def test_fire_tower_amid_its_district_skips_a_district_less_tower():
    # two coincident towers: all dwellings assign to the first, the second has no district to be
    # off-center of (dispersal is what catches the stacking)
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500), _tower(500, 500)], "buildings": _block(455, 455)}
    fails = f(M)
    assert "fire_tower_amid_its_district" not in fails
    assert "fire_towers_dispersed" in fails


@pytest.mark.tiers("town")
def test_fire_tower_clear_of_fields_fires_on_a_field():
    # a hinomi-yagura standing ON cultivated ground (e.g. an in-wall agricultural district) is nonsense
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(250, 250)], "fields": [_field("paddy", 100, 100, 400, 400)]}
    assert "fire_tower_clear_of_fields" in f_only(M, "fire_tower_clear_of_fields")


@pytest.mark.tiers("town")
def test_fire_tower_clear_of_fields_fires_on_flower_field():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(250, 250)], "flower_fields": [{"outline": [[100, 100], [400, 100], [400, 400], [100, 400]]}]}
    assert "fire_tower_clear_of_fields" in f_only(M, "fire_tower_clear_of_fields")


@pytest.mark.tiers("town")
def test_fire_tower_clear_of_fields_passes_when_clear():
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(800, 800)], "fields": [_field("paddy", 100, 100, 400, 400)]}
    assert "fire_tower_clear_of_fields" not in f_only(M, "fire_tower_clear_of_fields")


@pytest.mark.tiers("town")
def test_fire_tower_clear_of_wells_fires_on_a_wellhead():
    # wells are overlap-EXEMPT, so only the dedicated check catches a tower footing on the well court
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "wells": [{"x": 505, "y": 500, "r": 8}]}
    fails = f(M)
    assert "fire_tower_clear_of_wells" in fails
    assert "no_structure_overlaps" not in fails  # the exemption means the blanket pass misses this


@pytest.mark.tiers("town")
def test_fire_tower_clear_of_wells_fires_within_the_standoff():
    # tower half-width 13 + well r 8 + 5px daylight rule -> a well center 25px away is still too close
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "wells": [{"x": 525, "y": 500, "r": 8}]}
    assert "fire_tower_clear_of_wells" in f_only(M, "fire_tower_clear_of_wells")


@pytest.mark.tiers("town")
def test_fire_tower_clear_of_wells_passes_with_daylight():
    # 26px of clearance (center 500 -> well 539: 13 + 8 + 18) is comfortably clear of the 5px rule
    M = {"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)], "wells": [{"x": 539, "y": 500, "r": 8}]}
    assert "fire_tower_clear_of_wells" not in f_only(M, "fire_tower_clear_of_wells")


@pytest.mark.tiers("city", "town")
def test_city_martial_hall_is_required_exactly_once_and_inside_the_walls():
    # a provincial city is the first tier that supports a dojo at all, and the STATE hall is a
    # program item rather than a roll - exactly one, inside the rampart, in its own compound
    assert "city_has_martial_hall" not in f_only(_martial_city(), "city_has_martial_hall")
    assert "city_has_martial_hall" in f_only(_martial_city(halls=0), "city_has_martial_hall")  # a county town has none; a city must
    assert "city_has_martial_hall" in f_only(_martial_city(halls=2), "city_has_martial_hall")  # the state institution is singular
    assert "city_has_martial_hall" in f_only(_martial_city(hall_xy=(50, 500), sam_xy=(60, 520)), "city_has_martial_hall")  # outside the wall


@pytest.mark.tiers("capital", "town")
def test_theater_stage_checks_run_per_stage_and_kind_gates_the_temple_rules():
    """List-shaped theater_stage (the post-clobber-fix record): every stage gets the clear
    check, but only a MONZEN (temple) stage owes temple adjacency - a machi-kind stage is the
    entertainment quarter's commercial theater and sits in the fabric, not at a hall."""
    far_machi = {"x": 500, "y": 500, "w": 190, "h": 120, "rot": 0, "kind": "machi"}
    hall = [{"x": 1200, "y": 1200, "w": 132, "h": 86, "rot": 0, "kind": "monastery"}]
    # EVERY stage owes its temple: the `machi` kind was briefly exempted on the research finding
    # that a capital's entertainment district is commercial, and the GM (2026-08-10) ruled the
    # older setting rule governs - a stage belongs to a hall whoever pays for the troupe.
    assert "theater_stage_by_temple" in f_only({"meta": {"scale": "town"}, "theater_stage": [far_machi], "religious": hall}, "theater_stage_by_temple")
    far_monzen = dict(far_machi, kind="monzen")
    assert "theater_stage_by_temple" in f_only({"meta": {"scale": "town"}, "theater_stage": [far_monzen], "religious": hall}, "theater_stage_by_temple")
    near = {"x": 1160, "y": 1080, "w": 190, "h": 120, "rot": 0, "kind": "machi"}
    assert "theater_stage_by_temple" not in f_only({"meta": {"scale": "town"}, "theater_stage": [near], "religious": hall}, "theater_stage_by_temple")
