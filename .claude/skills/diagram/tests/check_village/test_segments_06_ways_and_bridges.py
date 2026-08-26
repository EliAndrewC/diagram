"""Split from test_checks.py by feature 025 - see tests/check_village/CLAUDE.md for the index."""

from tests.check_village._builders import _bridge_map, _capital_manifest, _skew_bridge_map, f, f_only


def test_roads_bridge_water_fires_when_unbridged():
    # the road runs straight through the stream with no bridge
    assert "roads_bridge_water" in f_only(_bridge_map([]), "roads_bridge_water")


def test_roads_bridge_water_passes_when_bridged():
    assert "roads_bridge_water" not in f_only(_bridge_map([{"x": 500, "y": 500, "rot": 0, "span": 37, "w": 26}]), "roads_bridge_water")


def test_roads_bridge_water_passes_when_road_runs_alongside_water():
    # a road parallel to a stream, never intersecting it, needs no bridge
    M = {"meta": {"scale": "village", "W": 1000, "H": 1000}, "road": [[100, 480], [900, 480]], "streams": [{"poly": [[100, 520], [900, 520]], "frm": None, "to": None, "w": 9}], "bridges": []}
    assert "roads_bridge_water" not in f_only(M, "roads_bridge_water")


def test_roads_bridge_water_fires_on_an_unbridged_lane_over_a_canal():
    # a village LANE crossing an irrigation ditch must be bridged too (not only roads/streets)
    M = {
        "meta": {"scale": "village", "W": 1000, "H": 1000},
        "lanes": [{"pts": [[100, 500], [900, 500]], "w": 6}],
        "field_ditches": [{"poly": [[500, 100], [500, 900]], "w": 5, "role": "main", "field": "p"}],
        "bridges": [],
    }
    assert "roads_bridge_water" in f_only(M, "roads_bridge_water")
    M["bridges"] = [{"x": 500, "y": 500, "rot": 0, "span": 32, "w": 6}]
    assert "roads_bridge_water" not in f_only(M, "roads_bridge_water")


def test_bridges_align_with_their_way_passes_a_solved_deck():
    # a deck seated on the crossing and bearing with the road - what s.bridges() produces
    assert "bridges_align_with_their_way" not in f_only(_skew_bridge_map(), "bridges_align_with_their_way")
    # ...and a deck may point either way along the road: a plank has no forward direction
    assert "bridges_align_with_their_way" not in f_only(_skew_bridge_map(rot=180), "bridges_align_with_their_way")


def test_bridges_align_with_their_way_fires_on_a_skewed_deck():
    # GM 2026-07-27, Minami's cargo basin: the deck was 39 deg off the way it carried, so the road
    # read as running straight through the water past a crooked plank
    fails = f(_skew_bridge_map(rot=39))
    assert "bridges_align_with_their_way" in fails
    assert "roads_bridge_water" not in fails  # the older rule is satisfied by ANY deck within 40px - that is the gap


def test_bridges_align_with_their_way_fires_on_a_deck_beside_its_crossing():
    # seated 17px east of where the way actually meets the water (Minami's offset), correctly angled
    fails = f(_skew_bridge_map(x=517))
    assert "bridges_align_with_their_way" in fails
    assert "roads_bridge_water" not in fails


def test_bridges_align_with_their_way_fires_on_a_deck_that_carries_nothing():
    # a deck over water with no way on it at all: either the way or the watercourse is unrecorded
    M = _bridge_map([{"x": 500, "y": 500, "rot": 0, "span": 37, "w": 26}])
    del M["road"]
    assert "bridges_align_with_their_way" in f_only(M, "bridges_align_with_their_way")


def test_bridges_align_with_their_way_exempts_standalone_footplanks():
    """A `foot` plank is carried by no way and crosses its ditch PERPENDICULAR by construction, so
    the alignment rule would fire on every correct one. Its own rules are long_ditches_have_a_
    footbridge and footbridges_reach_useful_ground."""
    M = _skew_bridge_map(rot=90, foot=True)  # square across the road it is nowhere near carrying
    assert "bridges_align_with_their_way" not in f_only(M, "bridges_align_with_their_way")


# ---- feature 021: the capital housing layer ---------------------------------------------------


def test_terraces_are_ranges_fires_on_a_single_unit():
    """A one-unit terrace is a detached house miscoded (T005) - the range record models one
    roof over several household cells."""
    M = _capital_manifest()
    M["terraces"] = [{"x": 500, "y": 500, "w": 6, "h": 7, "rot": 0, "units": 1, "z": 1}]
    assert "terraces_are_ranges" in f_only(M, "terraces_are_ranges")
    M["terraces"][0]["units"] = 6
    assert "terraces_are_ranges" not in f_only(M, "terraces_are_ranges")


def test_precinct_interiors_within_reservation():
    """T017 red-green: a declared precinct must draw >= 5 halls inside its reserved rect; a
    dormitory overhanging the reservation fires."""
    M = _capital_manifest()
    M["precincts"] = [{"x": 500, "y": 500, "w": 130, "h": 100, "rear": "north", "graveyard": False}]
    assert "precinct_interiors_within_reservation" in f_only(M, "precinct_interiors_within_reservation")  # declared, nothing drawn
    halls = [
        {"x": 456, "y": 462, "w": 16, "h": 10, "kind": "residence", "precinct": [500, 500]},
        {"x": 455, "y": 480, "w": 12, "h": 8, "kind": "kitchen", "precinct": [500, 500]},
        {"x": 492, "y": 460, "w": 19, "h": 7, "kind": "dormitory", "precinct": [500, 500]},
        {"x": 514, "y": 472, "w": 19, "h": 7, "kind": "dormitory", "precinct": [500, 500]},
        {"x": 552, "y": 498, "w": 11, "h": 8, "kind": "library", "precinct": [500, 500]},
        {"x": 446, "y": 502, "w": 14, "h": 9, "kind": "administration", "precinct": [500, 500]},
    ]
    M["precinct_halls"] = halls
    assert "precinct_interiors_within_reservation" not in f_only(M, "precinct_interiors_within_reservation")
    M["precinct_halls"] = halls[:-1] + [{"x": 570, "y": 502, "w": 14, "h": 9, "kind": "administration", "precinct": [500, 500]}]
    assert "precinct_interiors_within_reservation" in f_only(M, "precinct_interiors_within_reservation")  # administration overhangs east edge


def test_monzen_fronts_the_approach():
    """T018 red-green: a monzen district on the temple's blind side (no torii inside) fires; on
    the approach with its commercial rows it passes."""
    M = _capital_manifest()
    M["precincts"] = [{"x": 500, "y": 500, "w": 130, "h": 100, "rear": "north", "graveyard": False}]
    M["precinct_halls"] = [{"x": 456 + i, "y": 462, "w": 4, "h": 4, "kind": k, "precinct": [500, 500]} for i, k in enumerate(("residence", "kitchen", "dormitory", "dormitory", "library"))]
    M["torii"] = [(500, 580), (500, 620)]  # the sando marches SOUTH
    shops = [{"kind": "shop", "x": 460 + 12 * i, "y": 600, "w": 8, "h": 6} for i in range(7)]
    M["buildings"] = M.get("buildings", []) + shops
    M["districts"] = (M.get("districts") or []) + [{"name": "blind monzen", "kind": "monzen", "poly": [[430, 380], [570, 380], [570, 445], [430, 445]]}]
    assert "monzen_fronts_the_approach" in f_only(M, "monzen_fronts_the_approach")  # north of the temple, torii face south
    M["districts"][-1] = {"name": "monzen", "kind": "monzen", "poly": [[430, 560], [570, 560], [570, 640], [430, 640]]}
    assert "monzen_fronts_the_approach" not in f_only(M, "monzen_fronts_the_approach")


def test_teramachi_backstrip_lean():
    """T019 red-green: a packed dwelling between a rim temple and the rampart fires; a
    monk_house there is the temple's own and passes."""
    M = _capital_manifest()
    wallx = max(p9[0] for p9 in M["wall"])
    ty = sum(p9[1] for p9 in M["wall"]) / len(M["wall"])
    M["religious"] = (M.get("religious") or []) + [{"kind": "temple", "x": wallx - 130, "y": ty, "w": 32, "h": 21, "label": "Temple of Ebisu"}]
    M["buildings"] = M.get("buildings", []) + [{"kind": "laborer", "x": wallx - 60, "y": ty, "w": 10, "h": 7}]
    assert "teramachi_backstrip_lean" in f_only(M, "teramachi_backstrip_lean")
    M["buildings"][-1]["kind"] = "monk_house"
    assert "teramachi_backstrip_lean" not in f_only(M, "teramachi_backstrip_lean")


def test_monzen_floor_fires_on_too_few_commercial_buildings():
    """A monzen with its torii but a bare handful of shops is not doing a monzen's job - the
    elif branch of monzen_fronts_the_approach (coverage: the no-torii branch had a test, the
    too-few-commerce branch did not)."""
    M = _capital_manifest()
    M["precincts"] = [{"x": 500, "y": 500, "w": 130, "h": 100, "rear": "north", "graveyard": False}]
    M["precinct_halls"] = [{"x": 456 + i, "y": 462, "w": 4, "h": 4, "kind": k, "precinct": [500, 500]} for i, k in enumerate(("residence", "kitchen", "dormitory", "dormitory", "library"))]
    M["torii"] = [(500, 580), (500, 620)]
    M["districts"] = (M.get("districts") or []) + [{"name": "thin monzen", "kind": "monzen", "poly": [[430, 560], [570, 560], [570, 650], [430, 650]]}]
    M["buildings"] = M.get("buildings", []) + [{"x": 460, "y": 600, "w": 8, "h": 6, "kind": "shop", "rot": 0}]  # torii inside, but ONE shop
    assert "monzen_fronts_the_approach" in f_only(M, "monzen_fronts_the_approach")
