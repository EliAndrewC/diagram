"""tier town tests split out of `tests.check_village.test_segments_08_town_and_flow` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    _kosatsuba,
    f,
    f_only,
)


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
