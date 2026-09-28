"""The threshing yard as the harvest leaves it (feature 282): a floor of straw mats, thinned so each reads, and a rack by
the house only where the harvest weather is changeable - never in the yard's map-south half.

research/homesteads.html 'What lay in the work yard at harvest?' and 'Did a village put its drying racks by the houses
by custom, or because of its weather?'.
"""

from __future__ import annotations

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement.homestead_parts.yards import MAT_SQ_FT, RACK_MIN_FT, _quad_gap, mat_cells, rack_segment, thin_evenly
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
    # FR-004 as amended (2026-09-28): a third where the yard holds one at a 1 ft gap, else as many as fit there, never under 4
    assert (lo if tsubo >= 18 else 4) <= len(mats) <= hi, f"{tsubo} tsubo at {ftpx} ft/px: {len(mats)} mats, band {lo}-{hi}"
    quarters = {(mx + mw / 2 > 0, my + mh / 2 > 0) for mx, my, mw, mh, _a in mats}
    assert len(quarters) == 4, f"{tsubo} tsubo: mats in only {sorted(quarters)} - the floor must read covered, every quarter"
    assert all(mw * ftpx == 6.0 and mh * ftpx == 3.0 for _x, _y, mw, mh, _a in mats), "a mat is 3 x 6 ft, drawn at its real size"


def test_a_mat_stays_inside_the_yards_quad_and_off_the_rack() -> None:
    w, h = 40.0, 28.0
    quad = [(-18.0, -14.0), (20.0, -14.0), (17.0, 12.0), (-20.0, 14.0)]  # corners pulled in, as `_quad` pulls them
    keep = (12.0, -13.0, 18.0, 0.0)
    for mx, my, mw, mh, _a in mat_cells(w, h, quad, 1.0, keep):
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


def test_two_mats_that_overlap_have_no_gap_and_two_apart_have_theirs() -> None:
    a = [(0.0, 0.0), (6.0, 0.0), (6.0, 3.0), (0.0, 3.0)]
    assert _quad_gap(a, [(5.0, 1.0), (11.0, 1.0), (11.0, 4.0), (5.0, 4.0)]) == 0.0, "a corner inside the other: they touch"
    assert abs(_quad_gap(a, [(7.0, 0.0), (13.0, 0.0), (13.0, 3.0), (7.0, 3.0)]) - 1.0) < 1e-9, "side by side, a foot apart"


def _brute_fit(w: float, h: float, poly: list[tuple[float, float]], keep: tuple[float, float, float, float] | None, clear: float = 1.0) -> int:
    """The most unturned 6 x 3 ft mats any lattice at a 1 ft gap seats in the yard - every column and row count and every
    offset on a quarter-foot grid - with each corner 1 ft inside `poly` and clear of `keep`. The independent oracle for
    FR-004's "cannot hold a third": it shares no search with `mat_cells`."""
    from l7r.diagram.settlement._geom import edge_dist, point_in_poly

    def ok(x: float, y: float) -> bool:
        cs = ((x, y), (x + 6, y), (x + 6, y + 3), (x, y + 3))
        if not all(point_in_poly(px, py, poly) and edge_dist(px, py, poly) >= clear for px, py in cs):
            return False
        return keep is None or not (x < keep[2] and x + 6 > keep[0] and y < keep[3] and y + 3 > keep[1])

    best = 0
    for nc in range(1, int(w // 7) + 2):
        for nr in range(1, int(h // 4) + 2):
            sx, sy = nc * 7 - 1, nr * 4 - 1
            for i in range(int((w - sx) * 4) + 1):
                for j in range(int((h - sy) * 4) + 1):
                    x0, y0 = -w / 2 + i / 4, -h / 2 + j / 4
                    best = max(best, sum(ok(x0 + c * 7, y0 + r * 4) for r in range(nr) for c in range(nc)))
    return best


@pytest.mark.parametrize(
    ("w", "h", "poly", "keep"),
    [
        # the pool's short yards as drawn (2026-09-28): Sawada's 20 x 14 ft with its rack on the west, Kashikawa's 22 x 15 ft
        (20.32, 14.01, [(-9.58, -6.78), (10.04, -6.72), (9.7, 6.28), (-9.85, 6.93)], (-9.44, -5.27, -6.44, -0.46)),
        (22.1, 15.2, [(-10.5, -7.6), (11.05, -7.6), (10.2, 7.1), (-10.9, 7.3)], None),
        (27.0, 19.0, [(-13.1, -9.5), (13.5, -9.5), (12.7, 9.0), (-13.4, 8.8)], None),
    ],
)
def test_a_yard_short_of_a_third_draws_as_many_as_any_1_ft_lattice_would_fit(w: float, h: float, poly: list[tuple[float, float]], keep: tuple[float, float, float, float] | None) -> None:
    third = math.ceil(w * h / MAT_SQ_FT / 3)
    drawn = len(mat_cells(w, h, poly, 1.0, keep))
    assert drawn >= min(third, _brute_fit(w, h, poly, keep)), "a lattice the layout never tried seats more"
    assert drawn >= 4


def test_a_lattice_that_fits_only_in_a_band_thinner_than_any_grid_is_found() -> None:
    # a 25.4 x 17.5 ft yard with its rack on the east (spec-fidelity, amendment round 8, 2026-09-28): a 1 ft lattice seats 8
    # only with its top row in a band under 0.02 ft tall just below the rack's end; the y grid of 0.02 ft drew it 7
    poly = [(-10.916545273005731, -8.000801383130378), (12.539506545824656, -8.56225445403871), (12.554600478710167, 8.22205926909465), (-11.471217965375882, 8.56225445403871)]
    keep = (8.952654744209827, -7.010451547730915, 11.952654744209827, 0.25)
    assert len(mat_cells(25.405309488419654, 17.52090309546183, poly, 1.0, keep)) >= 8
