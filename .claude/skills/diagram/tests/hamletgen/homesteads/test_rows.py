"""Feature 291 amendment 3: the row village's geometry (`homesteads/rows.py`) and its rules (`homesteads/row_rules.py`)."""

from __future__ import annotations

import pytest
from shapely.geometry import Point

from l7r.diagram.hamletgen.homesteads.row_rules import bamboo_mismatch, continuous, doors_unreached, row_rules, water_rules
from l7r.diagram.hamletgen.homesteads.rows import (
    door_clear,
    frame_extent,
    frame_on_holdings,
    hard_ground,
    holding_clear,
    holding_quad,
    largest_ring,
    row_offsets,
    row_seats,
    street_line,
)

FIELD = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]


def test_hard_ground_unions_the_field_the_outline_and_the_water() -> None:
    hard = hard_ground(FIELD, [[(0.0, 0.0), (50.0, 0.0), (50.0, 50.0)]], [((1100.0, 0.0), (1100.0, 900.0), 10.0)])
    assert hard.contains(Point(700.0, 700.0)) and hard.contains(Point(30.0, 10.0)) and hard.distance(Point(1108.0, 500.0)) == 0.0
    assert hard_ground([], (), ()) is None


def test_the_edge_line_follows_the_ground_and_the_street_is_straight() -> None:
    hard = hard_ground(FIELD)
    edge = street_line(hard, (700.0, 300.0), 40.0, 400.0, "edge")
    assert edge and all(abs(Point(p).distance(hard) - 40.0) < 1.5 for p, _n in edge), "on the ring grown 40 ft"
    assert all(n[1] < 0 for _p, n in edge), "the normal points away from the field (north)"
    street = street_line(hard, (700.0, 300.0), 40.0, 400.0, "street", slack=100.0)
    ys = [p[1] for p, _n in street]
    assert max(ys) - min(ys) < 1e-6 and abs(street[-1][0][0] - street[0][0][0]) == pytest.approx(500.0, abs=1.0), "straight, the slack added"
    assert all(Point(p).distance(hard) >= 39.0 for p, _n in street), "set out so the stretch lies behind it"
    assert street_line(None, (0.0, 0.0), 10.0, 100.0, "edge") == []
    corner = street_line(hard, (380.0, 380.0), 40.0, 600.0, "edge")
    assert len(corner) > 2


def test_row_seats_step_one_frame_along_on_one_side_or_both() -> None:
    line = [((float(x), 0.0), (0.0, -1.0)) for x in range(0, 1001, 8)]
    frame = (0.0, 0.0, 200.0, 150.0)
    one = row_seats(line, frame, "one", 20.0)
    assert one[0][0] == pytest.approx((500.0, -95.0), abs=5.0) and all(side == 1 for _c, side, _t, _n in one)
    xs = sorted(c[0] for c, *_r in one)
    assert all(b - a == pytest.approx(200.0, abs=9.0) for a, b in zip(xs, xs[1:], strict=False)), "one frame (its longer side) apart"
    both = row_seats(line, frame, "both", 20.0)
    assert len(both) == 2 * len(one) and {side for _c, side, *_r in both} == {1, -1}
    assert row_seats(line[:1], frame, "one", 20.0) == []


def test_frame_extent_offsets_and_door_room() -> None:
    assert frame_extent((0.0, 0.0, 200.0, 100.0), (1.0, 0.0)) == 200.0 and frame_extent((0.0, 0.0, 200.0, 100.0), (0.0, 1.0)) == 100.0
    assert row_offsets(100.0, "one", 2, 24.0, 15.0) == [24.0, 24.0 + 100.0 + 30.0 + 24.0]
    assert row_offsets(100.0, "both", 2, 24.0, 15.0, 300.0) == [139.0, 139.0 + 200.0 + 30.0 + 24.0 + 300.0]
    hard = hard_ground(FIELD)
    assert door_clear((700.0, 200.0, 200.0, 150.0), (0, -1), 16.0, hard, 16.0), "the front faces away from the field"
    assert not door_clear((700.0, 330.0, 200.0, 150.0), (0, 1), 16.0, hard, 16.0), "the door on the field itself"
    assert door_clear((0.0, 0.0, 10.0, 10.0), (0, 1), 0.0, None, 16.0)


def test_a_holding_is_clipped_to_the_sheet_and_refused_on_hard_ground_or_a_box() -> None:
    quad = holding_quad((100.0, 100.0), (1.0, 0.0), (0.0, 1.0), 80.0, 200.0)
    assert quad[0] == (60.0, 0.0) and quad[2] == (140.0, 200.0)
    clipped = holding_clear(quad, None, [], (0.0, 30.0, 1000.0, 1000.0))
    assert clipped is not None and min(p[1] for p in clipped) == 30.0, "a sheet shows only the near end"
    assert holding_clear(quad, None, [], (500.0, 500.0, 900.0, 900.0)) is None, "nothing of it on the sheet"
    assert holding_clear(quad, hard_ground([(90.0, 90.0), (110.0, 90.0), (110.0, 110.0)]), [], (0.0, 0.0, 1000.0, 1000.0)) is None
    assert holding_clear(quad, None, [(100.0, 150.0, 10.0, 10.0)], (0.0, 0.0, 1000.0, 1000.0)) is None
    assert frame_on_holdings((100.0, 100.0, 20.0, 20.0), [quad]) and not frame_on_holdings((500.0, 500.0, 20.0, 20.0), [quad])


def test_largest_ring_takes_a_multipolygon_s_biggest_part() -> None:
    from shapely.geometry import MultiPolygon, Polygon

    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1)]), Polygon([(10, 10), (20, 10), (20, 20), (10, 20)])])
    assert len(largest_ring(mp)) == 4


def _row_map(**over) -> dict:  # type: ignore[no-untyped-def]
    house = {
        "x": 100.0,
        "y": 60.0,
        "w": 46.0,
        "h": 28.0,
        "geom": {"bbox": (100.0, 60.0, 200.0, 120.0), "groves": [(0, 0, 1, 1)], "grove_faces": [((0, -1), "deep")], "yard": (100.0, 90.0, 40.0, 20.0)},
    }
    M = {
        "meta": {"settlement_form": "linear", "row_water": "own"},
        "row_street_plans": [[[0.0, 0.0], [1000.0, 0.0]]],
        "houses": [house],
        "lanes": [{"pts": [[0.0, 0.0], [1000.0, 0.0]], "street": True, "street_index": 0, "w": 6}, {"pts": [[100.0, 108.0], [100.0, 0.0]], "serves": [100.0, 60.0], "w": 3}],
        "wells": [{"x": 150.0, "y": 60.0, "private": True}],
        "dry_plots": [],
        "row_holdings": [],
        "groves": [],
    }
    M.update(over)
    return M


def test_row_rules_hold_on_a_good_row_and_name_each_break() -> None:
    assert row_rules(_row_map()) == []
    assert row_rules({"meta": {"settlement_form": "nucleated"}}) == []
    assert row_rules({"meta": {"settlement_form": "linear"}, "houses": [{}]}) == [("no_row_street", 1)], "a linear map in no row fails"
    far = _row_map(houses=[{**_row_map()["houses"][0], "y": 400.0}])
    assert ("farm_off_its_street", (100.0, 400.0)) in row_rules(far)
    assert ("street_not_drawn", 0) in row_rules(_row_map(lanes=[]))
    broken = _row_map(lanes=[{"pts": [[0.0, 0.0], [300.0, 0.0]], "street": True, "street_index": 0}, {"pts": [[500.0, 0.0], [1000.0, 0.0]], "street": True, "street_index": 0}])
    assert ("street_broken", 0) in row_rules(broken)
    assert ("holding_not_drawn", (5.0, 6.0)) in row_rules(_row_map(row_holdings=[{"id": 0, "of": [5.0, 6.0]}]))
    two = _row_map(houses=[_row_map()["houses"][0], {**_row_map()["houses"][0], "x": 120.0, "y": 190.0}])
    assert any(r == "farm_behind_another" for r, _s in row_rules(two))
    lost = _row_map(lanes=[{"pts": [[0.0, 0.0], [1000.0, 0.0]], "street": True, "street_index": 0}], houses=[{**_row_map()["houses"][0], "y": 100.0}])
    assert ("farm_not_on_its_street", (100.0, 100.0)) in row_rules(lost)


def test_continuous_joins_pieces_end_to_end() -> None:
    assert continuous([]) and continuous([[[0, 0], [1, 0]]])
    assert continuous([[[0, 0], [10, 0]], [[10, 0], [20, 0]]]) and not continuous([[[0, 0], [10, 0]], [[15, 0], [20, 0]]])


def test_water_rules_own_and_shared() -> None:
    assert water_rules(_row_map()) == []
    assert water_rules({"meta": {"settlement_form": "nucleated"}}) == []
    assert ("farm_without_its_well", (100.0, 60.0)) in water_rules(_row_map(wells=[]))
    assert ("well_in_the_way_in", (100.0, 60.0)) in water_rules(_row_map(wells=[{"x": 100.0, "y": 95.0, "private": True}]))
    shared = _row_map(meta={"settlement_form": "linear", "row_water": "shared"})
    assert water_rules({**shared, "wells": [{"x": 100.0, "y": 700.0}]}) == []
    assert ("farm_beyond_a_shared_well", (100.0, 60.0)) in water_rules({**shared, "wells": [{"x": 100.0, "y": 2000.0}]})
    no_grove = _row_map(houses=[{**_row_map()["houses"][0], "geom": {}}], wells=[])
    assert water_rules(no_grove) == []


def test_doors_and_bamboo() -> None:
    assert doors_unreached(_row_map()) == []
    assert doors_unreached(_row_map(lanes=[{"pts": [[0.0, -500.0], [1000.0, -500.0]]}])) == [(100.0, 60.0)]
    assert doors_unreached({"meta": {"settlement_form": "linear"}, "lanes": []}) == []
    assert doors_unreached({**_row_map(lanes=[{"pts": [[0.0, -500.0], [1000.0, -500.0]]}]), "meta": {"settlement_form": "dispersed"}}) == [], "no network to reach"
    M = {"meta": {"household_bamboo_in_grove_farms": [[1.0, 2.0]]}, "groves": [{"of": [3.0, 4.0], "bamboo": True}, {"of": [1.0, 2.0], "bamboo": True}]}
    assert bamboo_mismatch(M) == [("draws_unrolled", (3.0, 4.0))]
    assert bamboo_mismatch({"meta": {"household_bamboo_in_grove_farms": [[1.0, 2.0]]}, "groves": []}) == [("rolled_undrawn", (1.0, 2.0))]
