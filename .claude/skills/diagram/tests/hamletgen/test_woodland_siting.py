"""Feature 269 group E6, B27: where a village keeps its fuel wood (research/vegetation/220) - beyond the fields, on ground
higher than the fields it adjoins, never downslope of the houses."""

import math

from l7r.diagram.hamletgen.hinterland.parcels import crop_edge_points, field_height_near, woodland_tier

DOWN_SOUTH = (0.0, 1.0)  # the land falls toward +y: height is -y


def test_the_tiers_follow_the_record_s_ranking():
    # the lowest house at height -500 (y = 500), the field beside the seat at height -300 (y = 300)
    assert woodland_tier((0.0, 200.0), DOWN_SOUTH, -500.0, -300.0) == 0  # above the field it adjoins, above the houses
    assert woodland_tier((0.0, 400.0), DOWN_SOUTH, -500.0, -300.0) == 1  # below that field but not below the houses: the level
    assert woodland_tier((0.0, 600.0), DOWN_SOUTH, -500.0, -300.0) == 2  # downslope of every house: never the wood
    assert woodland_tier((0.0, 600.0), DOWN_SOUTH, -math.inf, -math.inf) == 0  # no houses, no fields: any ground


def test_the_field_height_is_read_off_the_nearest_stretch_of_edge():
    """A long edge is sampled along its length, so a seat beside its middle reads the middle, not a far vertex."""
    field = [(0.0, 1000.0), (2000.0, 0.0), (2000.0, 1000.0)]  # a sloping top edge from (0, 1000) up to (2000, 0)
    grid = crop_edge_points([field])
    h = field_height_near((1000.0, 400.0), DOWN_SOUTH, grid)
    assert -520.0 <= h <= -480.0, h  # the edge at x = 1000 stands at y = 500
    assert field_height_near((9000.0, 9000.0), DOWN_SOUTH, grid) < -900.0  # far off, the widening pad still answers
    assert field_height_near((50000.0, 50000.0), DOWN_SOUTH, grid) == -math.inf  # past the widest pad: no field at all
    assert field_height_near((0.0, 0.0), DOWN_SOUTH, crop_edge_points([])) == -math.inf


def test_the_windward_bamboo_strip_stands_clear_of_its_house():
    """B29: the wind side's strip seats on the windward corner for a diagonal wind and on the windward face for a
    cardinal one, the gap clear of the walls - it used to lap the house's own corner under a NW wind and never seat."""
    from l7r.diagram.hamletgen.homesteads.bamboo import wind_seat

    hw, hh, gap, sw, sh = 40.0, 30.0, 6.0, 22.0, 16.0
    for wind in ((-math.sqrt(0.5), -math.sqrt(0.5)), (0.0, -1.0), (1.0, 0.0), (0.2, 0.98)):
        cx, cy, w, h = wind_seat(wind[0], wind[1], hw, hh, gap, sw, sh)
        clear_x = abs(cx) - w / 2 >= hw / 2 + gap - 1e-9
        clear_y = abs(cy) - h / 2 >= hh / 2 + gap - 1e-9
        assert clear_x or clear_y, (wind, cx, cy)
        assert cx * wind[0] >= 0 and cy * wind[1] >= 0, "on the windward side"
    assert wind_seat(-0.7, -0.7, hw, hh, gap, sw, sh)[:2] == (-(hw / 2 + gap + sw / 2), -(hh / 2 + gap + sh / 2))
    assert wind_seat(1.0, 0.0, hw, hh, gap, sw, sh) == (hw / 2 + gap + sh / 2, 0.0, sh, sw)
