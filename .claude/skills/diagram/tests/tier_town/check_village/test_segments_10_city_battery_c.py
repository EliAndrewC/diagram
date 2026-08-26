"""tier town tests split out of `tests.check_village.test_segments_10_city_battery_c` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    WALLSQ,
    _capital_manifest,
    bldg,
    f,
    f_only,
)


@pytest.mark.tiers("city", "town")
def test_city_streets_have_buildings_fires_on_an_empty_city_street():
    M = {"meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000}, "wall": WALLSQ, "gates": [[500, 200], [500, 800]], "town_streets": [{"pts": [[300, 300], [700, 300]], "w": 20}]}
    assert "city_streets_have_buildings" in f_only(M, "city_streets_have_buildings")


@pytest.mark.tiers("city", "town")
def test_city_streets_have_buildings_ignores_frontage_across_a_ward_fence():
    # the buildings hug the street (60px away) but a ward fence runs BETWEEN them and it: they front
    # whatever lies on their own side, not this street, so the street still reads as empty and fires.
    # (This is the Tango government-avenue bug: gap-band housing across the ward fence papered over a
    # bare avenue. A building walled off from a street cannot count as fronting it.)
    blds = [bldg(320 + i * 40, 440, kind="laborer") for i in range(9)]  # y440: 60px N of the street, N of the fence
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[300, 500], [700, 500]], "w": 20}],
        "wards": [{"name": "x", "boundary": [[280, 470], [720, 470]]}],  # fence between the houses and the street
        "buildings": blds,
    }
    assert "city_streets_have_buildings" in f_only(M, "city_streets_have_buildings")


@pytest.mark.tiers("city", "town")
def test_city_streets_connected_and_empty_space_fire():
    # two town streets far apart with no road -> two disconnected groups; the interior is almost
    # all empty (no buildings/fields), and a pond sits on a grid point (the pond-as-occupancy path)
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": [[100, 100], [900, 100], [900, 900], [100, 900]],
        "gates": [[500, 100], [500, 900]],
        "town_streets": [{"pts": [[200, 200], [200, 400]], "w": 18}, {"pts": [[700, 600], [700, 800]], "w": 18}],
        "pond": [400, 400, 80, 60],
    }
    fails = f(M)
    assert "city_streets_connected" in fails
    assert "city_no_large_empty_space" in fails


@pytest.mark.tiers("city", "town")
def test_city_has_dye_works_fires_when_the_yard_is_far_from_water():
    # a dyer's yard needs rinsing/vat water ON site - a yard in the dry middle of town fails even
    # though one exists (settlements.md "TRADE WORKS"; the presence branch is covered by the pinned
    # pre-trades city fixtures)
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000, "ftpx": 3, "walled": True},
        "wall": [[100, 100], [900, 100], [900, 900], [100, 900]],
        "gates": [[500, 100]],
        "streams": [{"poly": [[0, 950], [1000, 950]], "w": 12}],  # far south, ~400px away
        "dye_yards": [{"x": 500, "y": 500, "w": 27, "h": 17, "rot": 0, "label": "dye works"}],
    }
    assert "city_has_dye_works" in f_only(M, "city_has_dye_works")


@pytest.mark.tiers("city", "town")
def test_city_streets_connected_fires_on_a_gap_wider_than_45px():
    # two parallel streets 60px apart: the old 95px tolerance bridged them, the tightened 45px
    # does not - a grid that stops short of the road reads as a separated network, not connected
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[400, 300], [400, 700]], "w": 18}, {"pts": [[460, 300], [460, 700]], "w": 18}],
    }  # 60px apart, no road bridge
    assert "city_streets_connected" in f_only(M, "city_streets_connected")


@pytest.mark.tiers("city", "town")
def test_city_streets_connected_requires_beds_to_actually_overlap():
    # a cross-street whose end stops 30px short of the through-street: under the old flat 45px
    # tolerance this "connected", but the two paved beds (half-widths 9+9) do not touch, so you
    # cannot walk between them - it is a separate network. This is the Tango laborer-grid bug.
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [
            {"pts": [[300, 400], [700, 400]], "w": 18},  # the through-street
            {"pts": [[400, 430], [400, 700]], "w": 18},
        ],
    }  # ends 30px below it: beds 18px apart
    assert "city_streets_connected" in f_only(M, "city_streets_connected")


@pytest.mark.tiers("city", "town")
def test_city_streets_no_near_miss_fires_on_a_sliver_gap():
    # two street segments ~18px apart that do NOT cross - they almost touch but never meet
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [
            {"pts": [[300, 400], [500, 400]], "w": 18},  # ends at (500, 400)
            {"pts": [[515, 410], [515, 700]], "w": 18},
        ],
    }  # top at (515, 410): an ~18px gap
    assert "city_streets_no_near_miss" in f_only(M, "city_streets_no_near_miss")


@pytest.mark.tiers("city", "town")
def test_city_streets_no_intersection_stub_fires_on_a_short_overshoot():
    # a vertical street crosses a horizontal one and then stops 25px past it - a dangling stub
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [
            {"pts": [[300, 500], [700, 500]], "w": 18},  # horizontal cross-street
            {"pts": [[450, 300], [450, 525]], "w": 18},
        ],
    }  # crosses at y500, stops at 525 (25px past)
    assert "city_streets_no_intersection_stub" in f_only(M, "city_streets_no_intersection_stub")


@pytest.mark.tiers("city", "town")
def test_city_streets_no_intersection_stub_passes_when_streets_run_well_past():
    # the same crossing, but the vertical street continues well past (to 700) - a real grid line
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "town_streets": [{"pts": [[300, 500], [700, 500]], "w": 18}, {"pts": [[450, 300], [450, 700]], "w": 18}],
    }
    assert "city_streets_no_intersection_stub" not in f_only(M, "city_streets_no_intersection_stub")


@pytest.mark.tiers("city", "town")
def test_city_torii_over_streets_fires_when_torii_under_street():
    # a torii on the street but with a LOWER draw-z than the street -> the street paints over it
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "torii": [[500, 500, 50]],  # z = 50
        "town_streets": [{"pts": [[300, 500], [700, 500]], "w": 18, "z": 100}],
    }  # z = 100 > torii -> torii underneath
    assert "city_torii_over_streets" in f_only(M, "city_torii_over_streets")


@pytest.mark.tiers("city", "town")
def test_city_temple_approach_has_torii_fires_when_street_runs_up_without_one():
    # a street terminates right at the temple front but there is no torii arch on it
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "religious": [{"kind": "temple", "label": "T", "x": 500, "y": 500, "w": 100, "h": 80}],
        "town_streets": [{"pts": [[500, 700], [500, 545]], "w": 18}],
    }  # runs up to the south edge (540)
    assert "city_temple_approach_has_torii" in f_only(M, "city_temple_approach_has_torii")


@pytest.mark.tiers("city", "town")
def test_city_civic_clear_of_streets_fires():
    M = {
        "meta": {"scale": "city", "walled": True, "W": 1000, "H": 1000},
        "wall": WALLSQ,
        "gates": [[500, 200], [500, 800]],
        "ministries": [{"x": 500, "y": 500, "w": 90, "h": 60, "name": "Ministry of War"}],
        "town_streets": [{"pts": [[300, 500], [700, 500]], "w": 20}],
    }  # the street runs through the ministry
    assert "city_civic_clear_of_streets" in f_only(M, "city_civic_clear_of_streets")


@pytest.mark.tiers("city", "town")
def test_streets_may_front_open_ground():
    """021: a street along a commons (the castle's cleared ring, a festival ground) serves that
    ground - it is not a bare stretch. Without the commons the same street fires."""
    M = _capital_manifest(scale="city")
    M["meta"]["walled"] = True  # the urban battery (where both street checks live) binds walled cities
    M["buildings"] = [b for b in M.get("buildings", []) if not 700 < b["y"] < 1100]  # bare band for the test street
    M["town_streets"] = (M.get("town_streets") or []) + [{"pts": [[300, 900], [900, 900]], "w": 15}]
    r = f(M)
    fired = "city_streets_have_buildings" in r or "city_larger_streets_lined" in r
    assert fired  # a long street with nothing fronting it
    M["commons"] = [{"poly": [[300, 820], [900, 820], [900, 880], [300, 880]], "role": "pasture", "x": 600, "y": 850, "w": 600, "h": 60}]
    r = f(M)
    assert "city_streets_have_buildings" not in r and "city_larger_streets_lined" not in r
