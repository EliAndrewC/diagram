"""tier town tests split out of `tests.check_village.test_segments_08_town_and_flow` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _kosatsuba,
    _monastery,
    _tower,
    _town_behind,
    _town_caravan,
    _town_housing,
    _town_manor,
    f,
    f_only,
)


@pytest.mark.tiers("town")
def test_town_has_granary_off_by_default():
    # a standard county seat keeps grain in the yamen - no granary declared, no check
    assert "town_has_granary" not in f_only({"meta": {"scale": "town"}}, "town_has_granary")


@pytest.mark.tiers("town")
def test_town_has_granary_fires_when_declared_but_not_drawn():
    assert "town_has_granary" in f_only({"meta": {"scale": "town", "granary": True}}, "town_has_granary")


@pytest.mark.tiers("town")
def test_town_has_granary_passes_when_drawn():
    M = {"meta": {"scale": "town", "granary": True}, "granary": {"x": 500, "y": 500, "n": 3, "stores": [], "label": "granary"}}
    assert "town_has_granary" not in f_only(M, "town_has_granary")


@pytest.mark.tiers("town")
def test_town_has_merchant_storehouses_fires_when_too_few():
    assert "town_has_merchant_storehouses" in f_only({"meta": {"scale": "town"}}, "town_has_merchant_storehouses")  # 0 < 3


@pytest.mark.tiers("town")
def test_town_has_merchant_storehouses_passes_with_several():
    M = {"meta": {"scale": "town"}, "storehouses": [{"x": i, "y": 0} for i in range(4)]}
    assert "town_has_merchant_storehouses" not in f_only(M, "town_has_merchant_storehouses")


@pytest.mark.tiers("town")
def test_town_has_flophouse_fires_when_absent_by_default():
    assert "town_has_flophouse" in f_only({"meta": {"scale": "town"}}, "town_has_flophouse")  # 0 < default 1


@pytest.mark.tiers("town")
def test_town_has_flophouse_requires_more_when_declared():
    M = {"meta": {"scale": "town", "flophouses": 2}, "flophouses": [{"x": 500, "y": 500, "w": 104, "h": 46, "rot": 0}]}
    assert "town_has_flophouse" in f_only(M, "town_has_flophouse")  # 1 < 2


@pytest.mark.tiers("town")
def test_town_has_flophouse_opt_out_with_zero():
    assert "town_has_flophouse" not in f_only({"meta": {"scale": "town", "flophouses": 0}}, "town_has_flophouse")


@pytest.mark.tiers("town")
def test_town_monasteries_dedicated_fires_on_wrong_fortune():
    # Lion's patrons are Bishamon + Daikoku; a Benten monastery is wrong (no override declared)
    M = {"meta": {"scale": "town", "clan": "Lion"}, "religious": [_monastery("Bishamon"), _monastery("Benten")]}
    assert "town_monasteries_dedicated" in f_only(M, "town_monasteries_dedicated")


@pytest.mark.tiers("town")
def test_town_monasteries_dedicated_passes_with_correct_fortunes():
    M = {"meta": {"scale": "town", "clan": "Lion"}, "religious": [_monastery("Bishamon"), _monastery("Daikoku")]}
    assert "town_monasteries_dedicated" not in f_only(M, "town_monasteries_dedicated")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_passes_with_inn_stables_open_ground():
    assert "town_has_caravan_inn" not in f_only(_town_caravan(), "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_fires_without_stables():
    assert "town_has_caravan_inn" in f_only(_town_caravan(stables=False), "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_fires_when_outside_the_walls():
    assert "town_has_caravan_inn" in f_only(_town_caravan(walled=True, inn_xy=(40, 40), st_xy=(40, 100)), "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_fires_when_stables_hemmed_in():
    # the stables needs open ground (a pasture) - >4 dwellings crowding it fails
    M = _town_caravan()
    M["buildings"] += [{"x": 500 + i * 8, "y": 560, "w": 20, "h": 16, "kind": "laborer", "rot": 0} for i in range(5)]
    assert "town_has_caravan_inn" in f_only(M, "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_passes_when_inn_fronts_road():
    M = _town_caravan(inn_xy=(500, 560), st_xy=(500, 640))
    M["road"] = [[100, 500], [900, 500]]  # the inn (y560) fronts the road (y500), nothing between
    assert "town_has_caravan_inn" not in f_only(M, "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_fires_when_inn_behind_shops():
    M = _town_caravan(inn_xy=(500, 560), st_xy=(500, 640))
    M["road"] = [[100, 500], [900, 500]]
    M["buildings"].append({"x": 500, "y": 525, "w": 60, "h": 30, "kind": "merchant", "rot": 0})  # a shop between inn and road
    assert "town_has_caravan_inn" in f_only(M, "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_has_caravan_inn_fires_when_inn_far_from_any_road():
    M = _town_caravan(inn_xy=(500, 560), st_xy=(500, 640))
    M["road"] = [[100, 200], [900, 200]]  # the road is far away - the inn is not along it
    assert "town_has_caravan_inn" in f_only(M, "town_has_caravan_inn")


@pytest.mark.tiers("town")
def test_town_merchant_housing_varied_fires_when_uniform():
    assert "town_merchant_housing_varied" in f_only(_town_housing(m_large=0, l_large=3), "town_merchant_housing_varied")


@pytest.mark.tiers("town")
def test_town_merchant_housing_varied_passes_when_mixed():
    assert "town_merchant_housing_varied" not in f_only(_town_housing(m_large=4, l_large=3), "town_merchant_housing_varied")


@pytest.mark.tiers("town")
def test_town_laborer_housing_varied_fires_when_uniform():
    assert "town_laborer_housing_varied" in f_only(_town_housing(m_large=4, l_large=0), "town_laborer_housing_varied")


@pytest.mark.tiers("town")
def test_town_laborer_housing_varied_passes_when_mixed():
    assert "town_laborer_housing_varied" not in f_only(_town_housing(m_large=4, l_large=3), "town_laborer_housing_varied")


@pytest.mark.tiers("town")
def test_merchant_residences_behind_businesses_skipped_without_a_road():
    # a walled town has no trunk M["road"]; the single-axis test must not run
    M = _town_behind(res_x=140, lab_x=240)
    del M["road"]
    assert "merchant_residences_behind_businesses" not in f_only(M, "merchant_residences_behind_businesses")


@pytest.mark.tiers("town")
def test_manor_gate_faces_town_passes_facing_the_road():
    # town centroid is SE, but a north gate faces an Imperial road to the manor's north -> ok
    assert "manor_gate_faces_town" not in f_only(_town_manor("north", road=[[100, 150], [600, 150]]), "manor_gate_faces_town")


@pytest.mark.tiers("town")
def test_walled_town_has_fire_tower_fires_when_absent():
    # WALLED towns only (GM 2026-07-24, reverting the 2026-07 audit widening): an unwalled seat
    # keeps fire bells and kura, not a tower - see settlements.md "Fire towers"
    assert "walled_town_has_fire_tower" in f_only({"meta": {"scale": "town", "walled": True}}, "walled_town_has_fire_tower")


@pytest.mark.tiers("town")
def test_walled_town_has_fire_tower_passes_with_one():
    assert "walled_town_has_fire_tower" not in f_only({"meta": {"scale": "town", "walled": True}, "fire_towers": [_tower(500, 500)]}, "walled_town_has_fire_tower")


@pytest.mark.tiers("town")
def test_walled_town_has_fire_tower_opt_out():
    assert "walled_town_has_fire_tower" not in f_only({"meta": {"scale": "town", "walled": True, "fire_tower": False}}, "walled_town_has_fire_tower")


@pytest.mark.tiers("town")
def test_unwalled_town_needs_no_fire_tower():
    # an OPEN town's detached fabric has its own natural breaks; the presence check is walled-only
    # (and the widened town_has_fire_tower name must stay gone)
    fails = f({"meta": {"scale": "town", "walled": False}})
    assert "walled_town_has_fire_tower" not in fails
    assert "town_has_fire_tower" not in fails


@pytest.mark.tiers("town")
def test_town_kosatsuba_passes_by_a_main_street():
    # sited on the traffic artery: within ~60 ft of a road or main street (town_streets branch)
    M = {"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 530)], "town_streets": [{"pts": [[0, 500], [1000, 500]], "w": 28}]}
    fails = f(M)
    assert "town_has_kosatsuba" not in fails and "kosatsuba_by_the_road" not in fails


@pytest.mark.tiers("town")
def test_kosatsuba_by_the_road_fires_when_marooned():
    # a board deep in the back blocks defeats the institution (road branch of the routes)
    M = {"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 900)], "road": [[0, 500], [1000, 500]]}
    assert "kosatsuba_by_the_road" in f_only(M, "kosatsuba_by_the_road")


@pytest.mark.tiers("town")
def test_kosatsuba_on_a_main_way_fires_on_a_side_lane_board():
    # GM 2026-08-02 (Ubame): the board sat a legal 49 ft off a side lane while the high street
    # ran 200 ft away. Where the map declares a way hierarchy, only a MAIN way seats the board -
    # the side lane satisfies the old distance check, which is exactly why this check exists.
    M = {
        "meta": {"scale": "town"},
        "kosatsuba": [_kosatsuba(500, 830)],
        "road": [[0, 500], [1000, 500]],
        "lanes": [{"pts": [[0, 800], [1000, 800]], "w": 5}],
    }
    fails = f(M)
    assert "kosatsuba_by_the_road" not in fails
    assert "kosatsuba_on_a_main_way" in fails
    on_road = f({**M, "kosatsuba": [_kosatsuba(500, 530)]})
    assert "kosatsuba_on_a_main_way" not in on_road


@pytest.mark.tiers("town")
def test_kosatsuba_on_a_main_way_reads_the_main_street_flag():
    # a main: True town street is a main way; an unflagged one is a side street
    main_st = {"pts": [[0, 500], [1000, 500]], "w": 28, "main": True}
    side_st = {"pts": [[0, 800], [1000, 800]], "w": 22, "main": False}
    on_side = f({"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 830)], "town_streets": [main_st, side_st]})
    assert "kosatsuba_on_a_main_way" in on_side
    on_main = f({"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 530)], "town_streets": [main_st, side_st]})
    assert "kosatsuba_on_a_main_way" not in on_main


@pytest.mark.tiers("town")
def test_town_kosatsuba_opt_out():
    # a suppressed or backwater seat may omit it
    assert "town_has_kosatsuba" not in f_only({"meta": {"scale": "town", "kosatsuba": False}}, "town_has_kosatsuba")


@pytest.mark.tiers("town")
def test_kosatsuba_routeless_map_skips_the_siting_check():
    # no road/street recorded: presence still gates, the siting check stays quiet
    fails = f({"meta": {"scale": "town"}, "kosatsuba": [_kosatsuba(500, 900)]})
    assert "kosatsuba_by_the_road" not in fails
    # ... and so does the ORIENTATION check: with no route in the band there is nothing to face
    assert "kosatsuba_faces_the_road" not in fails
    marooned = f({"meta": {"scale": "town"}, "kosatsuba": [dict(_kosatsuba(500, 900), rot=90)], "road": [[0, 500], [1000, 500]]})
    assert "kosatsuba_by_the_road" in marooned and "kosatsuba_faces_the_road" not in marooned


@pytest.mark.tiers("town")
def test_kosatsuba_faces_the_road_fires_when_edge_on():
    # GM 2026-07-27: a kosatsu is a BROADSIDE signboard - stood across the road it fronts, its
    # face goes edge-on to the traffic the siting check fought for, and both the presence and
    # distance checks stay green. The glyph's long axis IS the face, so rot = the road's bearing.
    road = [[0, 500], [1000, 500]]
    across = f({"meta": {"scale": "town"}, "kosatsuba": [dict(_kosatsuba(500, 530), rot=90)], "road": road})
    assert "kosatsuba_by_the_road" not in across and "kosatsuba_faces_the_road" in across
    along = f({"meta": {"scale": "town"}, "kosatsuba": [dict(_kosatsuba(500, 530), rot=0)], "road": road})
    assert "kosatsuba_faces_the_road" not in along
    # a board on a BEND takes the bend's bearing, so a few degrees off its nearest segment is fine
    assert "kosatsuba_faces_the_road" not in f_only({"meta": {"scale": "town"}, "kosatsuba": [dict(_kosatsuba(500, 530), rot=18)], "road": road}, "kosatsuba_faces_the_road")
