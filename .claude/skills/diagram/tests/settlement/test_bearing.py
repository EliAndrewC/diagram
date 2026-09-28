"""269 E3 (B18, B17): which way a farmhouse faces, the homestead turning as one piece, and where a lane end stops at a house.

research/homesteads/240 and 310. `settlement/rolling/bearing.py`, the turned boxes of `_bundle_geom`, and the dooryard clause
of `trim_lane_stubs`.
"""

import math

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.rolling import bearing as B
from l7r.diagram.settlement.rolling.fit import house_box, part_box
from l7r.diagram.settlement.water_ways._helpers import DOORYARD_REACH_FT, HOUSE_SERVE_FT, dooryard_dist, vertex_behind, walked_past
from tests.settlement._builders import _nuc_village


def test_a_line_has_no_front_or_back() -> None:
    assert B.wrap_line_deg(170.0) == pytest.approx(-10.0)
    assert B.wrap_line_deg(-100.0) == pytest.approx(80.0)
    assert B.wrap_line_deg(0.0) == 0.0


def test_the_margin_bearing_reads_the_lane_line_a_house_stands_on() -> None:
    """A house beside a margin running along the settlement's axis follows no turn; one beside a stretch at a right angle
    to it reads the full quarter (the house turn clamps it later); out of reach, and on a ring too small to have a
    direction, nothing is followed."""
    square = [(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)]
    mb = B.MarginBearing(square, 0.0)
    assert mb(200.0, -30.0) == pytest.approx(0.0, abs=1e-6), "beside the bottom edge, which runs along the axis"
    assert abs(mb(430.0, 200.0)) == pytest.approx(90.0, abs=1e-6), "beside the right edge, square to the axis"
    assert mb(5000.0, 5000.0) == 0.0 and mb.nearest(5000.0, 5000.0) is None, "past the reach: no lane to follow"
    assert mb.nearest(200.0, -30.0) is not None
    assert B.MarginBearing([(0.0, 0.0), (1.0, 0.0)], 0.0)(0.0, 0.0) == 0.0, "two samples are no direction"
    # a point further than the first 64 px pad but inside the reach: the pad doubles until it finds the ring
    assert B.MarginBearing(square, 0.0).nearest(200.0, -150.0) is not None


def test_the_house_turn_is_common_bearing_lane_and_spread_within_thirty_and_a_quarter_on_the_tenth() -> None:
    mid = lambda x, y, salt: 0.5  # noqa: E731 - a draw at the middle: no spread, no quarter turn
    low = lambda x, y, salt: 0.0  # noqa: E731 - the bottom of every draw: the widest spread, and a quarter turn
    assert B.house_rot(mid, 10.0, 10.0, 5.0, None, B.QUARTER_TURN_SHARE) == pytest.approx(5.0)
    assert B.house_rot(mid, 10.0, 10.0, 5.0, lambda x, y: 12.0, B.QUARTER_TURN_SHARE) == pytest.approx(17.0), "the lane's turn"
    assert B.house_rot(mid, 10.0, 10.0, 0.0, lambda x, y: 80.0, B.QUARTER_TURN_SHARE) == pytest.approx(B.BEARING_SPREAD_DEG), "clamped to the spread"
    assert B.house_rot(low, 10.0, 10.0, 0.0, None, B.QUARTER_TURN_SHARE) == pytest.approx(B.QUARTER_TURN_DEG - B.BEARING_JITTER_DEG)
    assert B.house_rot(low, 10.0, 10.0, 0.0, None, 0.0) == pytest.approx(-B.BEARING_JITTER_DEG), "no share, no quarter turn"
    # the draw keys on the seat's 4 ft cell: a seat moved a pixel keeps its turn
    seen = []
    B.house_rot(lambda x, y, salt: seen.append((x, y)) or 0.5, 101.3, 58.9, 0.0, None, 0.1)
    assert all(x % B.KEY_CELL_PX == 0 and y % B.KEY_CELL_PX == 0 for x, y in seen)


def test_a_turned_part_clears_the_box_it_is_drawn_in() -> None:
    assert B.turned_box((0.0, 0.0, 10.0, 4.0), 0.0) == pytest.approx((0.0, 0.0, 10.0, 4.0))
    assert B.turned_box((0.0, 0.0, 10.0, 4.0), 90.0) == pytest.approx((0.0, 0.0, 4.0, 10.0))
    w30 = B.turned_box((0.0, 0.0, 10.0, 4.0), 30.0)
    assert w30[2] > 10.0 and w30[3] > 4.0, "a raked part needs more ground on both axes"
    assert B.turned_reach((-5.0, -2.0, 5.0, 2.0), 0.0, (0.0, 1.0)) == pytest.approx(2.0)
    assert B.turned_reach((-5.0, -2.0, 5.0, 2.0), 90.0, (0.0, 1.0)) == pytest.approx(5.0), "a quarter turn reaches with its length"


def test_a_hamlet_house_takes_the_bearing_rule_and_every_other_map_keeps_the_old_rake() -> None:
    s = _nuc_village()
    assert s._house_bearing is None and -5.0 <= s._house_rot(123.0, 456.0) < 5.0
    s._house_bearing = 4.0
    assert s._house_rot(123.0, 456.0) == pytest.approx(B.house_rot(s._hjit, 123.0, 456.0, 4.0, None, B.QUARTER_TURN_SHARE))


def test_the_bundle_boxes_are_the_drawn_parts_turned_and_the_parts_keep_their_true_size() -> None:
    s = _nuc_village()
    s._household_seat = (400.0, 400.0)
    flat = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "SE", shed=True, rot=0.0)
    assert flat["boxes"]["house"] == pytest.approx(flat["house"]) and flat["boxes"]["yard"] == pytest.approx(flat["yard"])
    turned = s._bundle_geom(400.0, 400.0, 46.0, 28.0, "SE", shed=True, rot=90.0)
    assert turned["house"][2:] == pytest.approx((46.0, 28.0)), "the part keeps its true size, in its house's frame"
    assert turned["boxes"]["house"][2:] == pytest.approx((28.0, 46.0)), "...and clears the ground it is drawn on"
    assert turned["yard"][0] < 400.0 and abs(turned["yard"][1] - 400.0) < 1.0, "the yard turned with the house: to the west"
    bb = turned["bbox"]
    for key in ("house", "yard", "shed"):
        bx = turned["boxes"][key]
        assert bb[0] - bb[2] / 2 <= bx[0] - bx[2] / 2 + 1e-6 and bx[0] + bx[2] / 2 <= bb[0] + bb[2] / 2 + 1e-6
    assert part_box({"yard": (1.0, 2.0, 3.0, 4.0)}, "yard") == (1.0, 2.0, 3.0, 4.0), "a hand-built geometry carries no boxes"
    assert house_box({"x": 1.0, "y": 2.0, "w": 3.0, "h": 4.0}) == (1.0, 2.0, 3.0, 4.0)
    assert house_box({"x": 1.0, "y": 2.0, "w": 3.0, "h": 4.0, "geom": turned}) == tuple(turned["boxes"]["house"])


def test_a_quarter_turned_homestead_draws_its_yard_beside_the_house_with_the_edge_toward_it_level(monkeypatch) -> None:
    """The GM's ruling of 2026-09-26 (homesteads/240): a yard and its beds always line up with their house. A quarter turn
    carries the yard from the south front round to the west, and its edge toward the house stays straight - the level
    edge is chosen in the house's frame, not the map's."""
    from l7r.diagram.settlement import houses as H

    monkeypatch.setattr(H, "QUARTER_TURN_SHARE", 1.0)
    s = _nuc_village()
    s._house_bearing = 0.0
    n = 0
    for gx in range(380, 640, 100):
        for gy in range(200, 720, 90):
            if n < 4 and s.try_place(gx, gy, "plain"):
                n += 1
    assert n, "a quarter-turned homestead was seated"
    s.farmsteads()
    for h in s.M["houses"]:
        assert abs(B.wrap_line_deg(h["rot"])) > 45.0, "every house took the quarter turn"
    for y in s.M["threshing_yards"]:
        hx, hy = y["of"]
        assert y["x"] < hx and abs(y["x"] - hx) > abs(y["y"] - hy), "the yard stands west of its house"
        th = math.radians(next(h["rot"] for h in s.M["houses"] if (h["x"], h["y"]) == (hx, hy)))
        local = [((px - y["x"]) * math.cos(th) + (py - y["y"]) * math.sin(th), -(px - y["x"]) * math.sin(th) + (py - y["y"]) * math.cos(th)) for px, py in y["poly"]]
        assert local[0][1] == pytest.approx(local[1][1], abs=0.2), "the yard's edge toward the house is level in the house's frame"


def test_an_end_serves_a_house_at_its_dooryard_or_beside_it_and_never_past_it() -> None:
    house = {"x": 0.0, "y": 0.0, "w": 46.0, "h": 28.0, "rot": 0.0}
    assert dooryard_dist(house, (0.0, 0.0)) == 0.0
    assert dooryard_dist(house, (0.0, 24.0)) == pytest.approx(10.0)
    turned = {**house, "geom": {"yard": (0.0, 30.0, 30.0, 20.0), "gardens": [(40.0, 0.0, 10.0, 10.0)]}}
    assert dooryard_dist(turned, (0.0, 45.0)) == pytest.approx(5.0), "the yard is the dooryard too"
    assert not walked_past((-50.0, 30.0), (0.0, 30.0), (0.0, 0.0)), "level with the house"
    assert walked_past((-50.0, 30.0), (40.0, 30.0), (0.0, 0.0)), "40 ft on past it"
    assert not walked_past((0.0, 0.0), (0.0, 0.0), (5.0, 5.0)), "a leg of no length walks nowhere"
    assert vertex_behind((150.0, 0.0), [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]) == (100.0, 0.0)
    assert vertex_behind((50.0, 0.0), [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]) == (0.0, 0.0)
    assert DOORYARD_REACH_FT < HOUSE_SERVE_FT


def test_the_dooryard_figures_are_the_scripted_tiers_own() -> None:
    """The settlement engine cannot import the scripted tier, so the figures are restated - and held equal here."""
    from l7r.diagram.hamletgen.consts import STEADING_ARRIVAL_FT, WAY_END_REACH_FT

    assert DOORYARD_REACH_FT == STEADING_ARRIVAL_FT and HOUSE_SERVE_FT == WAY_END_REACH_FT


def _lanes_past_a_house(end_x: float) -> Settlement:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    s.M["houses"] = [{"x": 500.0, "y": 540.0, "w": 46.0, "h": 28.0, "rot": 0.0}]
    s.lane([(100.0, 100.0), (100.0, 900.0)], width=4)
    s.lane([(100.0, 500.0), (end_x, 500.0)], width=4)  # an arm off the first, running east past the house 40 ft south of it
    return s


def test_trim_lane_stubs_pulls_an_arm_back_to_the_last_house_it_serves() -> None:
    """269 B17 (research/homesteads/310: "a lane end that reaches nothing is pulled back to the last house it serves"). The
    arm ran 90 ft past the house's center - inside the old 90 ft reach, so it stayed; now it walks back to the house."""
    s = _lanes_past_a_house(590.0)
    s.trim_lane_stubs()
    end = s.M["lanes"][1]["pts"][-1]
    assert end[0] <= 500.0 + 8.0, f"the arm stops beside the house, not {end[0] - 500.0:.0f} ft past it"
    assert end[0] >= 440.0, "...and not short of it"


def test_trim_lane_stubs_counts_an_end_on_the_bund() -> None:
    s = _lanes_past_a_house(700.0)
    s.M["fields"] = [{"outline": [(704.0, 400.0), (900.0, 400.0), (900.0, 600.0), (704.0, 600.0)]}]
    s.trim_lane_stubs()
    assert s.M["lanes"][1]["pts"][-1] == [700.0, 500.0], "an end 4 ft off the field's edge has arrived on the bund"
