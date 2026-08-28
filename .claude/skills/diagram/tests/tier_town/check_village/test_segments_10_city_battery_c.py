"""tier town tests split out of `tests.check_village.test_segments_10_city_battery_c` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    WALLSQ,
    f_only,
)


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
