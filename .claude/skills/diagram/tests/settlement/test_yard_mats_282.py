"""The threshing yard as the harvest leaves it (feature 282): a floor of straw mats, thinned so each reads, and a rack by
the house only where the harvest weather is changeable - never in the yard's map-south half.

research/homesteads.html 'What lay in the work yard at harvest?' and 'Did a village put its drying racks by the houses
by custom, or because of its weather?'.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement.homestead_parts.yards import MAT_SQ_FT, RACK_MIN_FT, mat_cells, rack_segment, thin_evenly
from tests.settlement._builders import _nuc_village

TSUBO_FT2 = 35.583


def _rect(w: float, h: float) -> list[tuple[float, float]]:
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]


def _band(w: float, h: float, ftpx: float) -> tuple[int, int]:
    full = (w * ftpx) * (h * ftpx) / MAT_SQ_FT
    return math.ceil(full / 3), math.floor(2 * full / 3)


@pytest.mark.parametrize("ftpx", [1.0, 2.0])
@pytest.mark.parametrize("tsubo", [8, 12, 18, 25, 40, 60, 90])
def test_the_mats_cover_the_whole_yard_at_between_a_third_and_two_thirds_of_a_full_cover(tsubo: int, ftpx: float) -> None:
    # the yard sizes the roll makes (a floor of 8 tsubo up past the large farms), at the 1.45 aspect `_yard_dims` draws
    depth_ft = math.sqrt(tsubo * TSUBO_FT2 / 1.45)
    w, h = depth_ft * 1.45 / ftpx, depth_ft / ftpx
    mats = mat_cells(w, h, _rect(w, h), ftpx)
    lo, hi = _band(w, h, ftpx)
    assert lo <= len(mats) <= hi, f"{tsubo} tsubo at {ftpx} ft/px: {len(mats)} mats, band {lo}-{hi}"
    quarters = {(mx + mw / 2 > 0, my + mh / 2 > 0) for mx, my, mw, mh in mats}
    assert len(quarters) == 4, f"{tsubo} tsubo: mats in only {sorted(quarters)} - the floor must read covered, every quarter"
    assert all(mw * ftpx == 6.0 and mh * ftpx == 3.0 for _x, _y, mw, mh in mats), "a mat is 3 x 6 ft, drawn at its real size"


def test_a_mat_stays_inside_the_yards_quad_and_off_the_rack() -> None:
    w, h = 40.0, 28.0
    quad = [(-18.0, -14.0), (20.0, -14.0), (17.0, 12.0), (-20.0, 14.0)]  # corners pulled in, as `_quad` pulls them
    keep = (12.0, -13.0, 18.0, 0.0)
    for mx, my, mw, mh in mat_cells(w, h, quad, 1.0, keep):
        assert not (mx < keep[2] and mx + mw > keep[0] and my < keep[3] and my + mh > keep[1]), "a mat under the rack"
        for px, py in ((mx, my), (mx + mw, my), (mx + mw, my + mh), (mx, my + mh)):
            assert -20.0 <= px <= 20.0 and -14.0 <= py <= 14.0


def test_an_overshoot_is_thinned_evenly_not_from_one_end() -> None:
    assert thin_evenly(list(range(11)), 10) == [0, 1, 2, 3, 4, 6, 7, 8, 9, 10], "the drop falls mid-list"
    assert thin_evenly(list(range(4)), 10) == [0, 1, 2, 3], "under the cap, untouched"


def test_a_yard_with_room_for_no_mat_draws_none() -> None:
    assert mat_cells(5.0, 2.0, _rect(5.0, 2.0), 1.0) == []


def _map_south(x: float, y: float, rot: float) -> float:
    th = math.radians(rot)
    return x * math.sin(th) + y * math.cos(th)


@pytest.mark.parametrize("rot", [0.0, 4.5, -4.5, 30.0, 89.0, 90.0, -90.0, 180.0])
@pytest.mark.parametrize("side", [1, -1])
def test_the_rack_never_stands_in_the_yards_map_south_half(rot: float, side: int) -> None:
    w, h = 36.0, 25.0
    seg = rack_segment(w, h, rot, 1.0, side)
    assert seg is not None, f"no rack at rot {rot} - every yard on a changeable-weather map takes one"
    x, y0, y1, hw = seg
    assert y1 - y0 >= RACK_MIN_FT
    for px, py in ((x - hw, y0), (x + hw, y0), (x + hw, y1), (x - hw, y1)):
        assert _map_south(px, py, rot) <= 1e-6, f"rot {rot}: a rack corner {_map_south(px, py, rot):.2f} ft map-south of the center"
    assert abs(x) < w / 2 and -h / 2 < y0 < y1 <= h / 2


def test_the_rack_prefers_the_half_nearest_the_house_and_its_preferred_side() -> None:
    x, y0, y1, _hw = rack_segment(36.0, 25.0, 0.0, 1.0, 1) or (0.0, 0.0, 0.0, 0.0)
    assert x > 0 and y1 <= 0.0 and y0 < -10.0, "on an unturned yard: the east side, from the house's edge to the middle"


def test_the_rack_takes_the_whole_side_where_no_near_half_has_room() -> None:
    # a yard turned about so its house-facing half lies map-south: the far half, now map-north, takes it
    seg = rack_segment(36.0, 25.0, 180.0, 1.0, 1)
    assert seg is not None and seg[1] >= 0.0 and seg[2] > 0.0
    assert rack_segment(36.0, 3.0, 0.0, 1.0, 1) is None, "a yard with no depth has no side to take a rack"


def test_the_drawn_yard_records_its_mats_and_its_rack_in_map_coordinates() -> None:
    s = _nuc_village()
    s._attach_yard(500.0, 500.0, (500.0, 530.0, 30.0, 20.0), 4.0)
    rec = s.M["threshing_yards"][-1]
    assert rec["mats"] > 0 and "rack" not in rec, "settled weather: mats, no rack"
    s._house_racks = True
    s._attach_yard(700.0, 500.0, (700.0, 530.0, 30.0, 20.0), 4.0)
    rec = s.M["threshing_yards"][-1]
    assert len(rec["rack"]) == 4 and all(py <= rec["y"] + 1e-6 for _px, py in rec["rack"]), "the rack is map-north of the yard's center"
    s._work_yards = False
    s._attach_yard(900.0, 500.0, (900.0, 530.0, 30.0, 20.0), 0.0)
    assert "mats" not in s.M["threshing_yards"][-1], "a forecourt draws no floor and no mats"


def test_harvest_weather_is_declared_never_rolled() -> None:
    plans = {hg.plan_site(hg.HamletSpec(name="X", seed=s, households=15)).harvest_weather for s in range(1, 12)}
    assert plans == {"settled"}, "the regional default on every seed: the weather is a fact of the country, not a roll"
    assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, harvest_weather="changeable")).harvest_weather == "changeable"
    with pytest.raises(ValueError, match="harvest_weather"):
        hg.HamletSpec(name="X", seed=1, harvest_weather="monsoon")
