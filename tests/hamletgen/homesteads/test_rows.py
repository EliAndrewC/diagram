"""Feature 291 amendment 3: the row village's geometry (`homesteads/rows.py`) and its rules (`homesteads/row_rules.py`)."""

from __future__ import annotations

from l7r.diagram.hamletgen.homesteads.row_rules import bamboo_mismatch, continuous, row_rules, water_rules
from l7r.diagram.hamletgen.homesteads.rows import (
    holding_quad,
    largest_ring,
)

FIELD = [(400.0, 400.0), (1000.0, 400.0), (1000.0, 1000.0), (400.0, 1000.0)]


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


def test_bamboo_mismatch() -> None:
    M = {"meta": {"household_bamboo_in_grove_farms": [[1.0, 2.0]]}, "groves": [{"of": [3.0, 4.0], "bamboo": True}, {"of": [1.0, 2.0], "bamboo": True}]}
    assert bamboo_mismatch(M) == [("draws_unrolled", (3.0, 4.0))]
    assert bamboo_mismatch({"meta": {"household_bamboo_in_grove_farms": [[1.0, 2.0]]}, "groves": []}) == [("rolled_undrawn", (1.0, 2.0))]


def test_a_holding_cell_on_a_lane_is_left_undrawn() -> None:
    from l7r.diagram.hamletgen.homesteads.rows import draw_holdings
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    quad = holding_quad((700.0, 700.0), (1.0, 0.0), (0.0, 1.0), 200.0, 450.0)
    s._row_holdings = [(quad, (1.0, 0.0), (0.0, 1.0), 450.0)]  # type: ignore[attr-defined]
    s.M["lanes"] = [{"pts": [[500.0, 700.0], [900.0, 700.0]], "w": 3}]  # across the middle cell
    n = draw_holdings(s)
    assert n == 2, "three cells of 150 ft, the middle one on the lane"


def test_row_rules_pass_over_a_farm_with_no_front_door() -> None:
    """A farm with no grove of its own has no front door (`front_door` None): the door rule has nothing to judge."""
    M = {"meta": {"settlement_form": "linear"}, "row_street_plans": [[[0.0, 0.0], [1000.0, 0.0]]], "houses": [{"x": 500.0, "y": 50.0}], "lanes": []}
    assert not [r for r, _s in row_rules(M) if r == "farm_not_on_its_street"]


def _hairpins(pts) -> int:  # type: ignore[no-untyped-def]
    import math

    n = 0
    for a, b, c in zip(pts, pts[1:], pts[2:], strict=False):
        v1, v2 = (b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        if n1 > 1e-6 and n2 > 1e-6 and (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2) < math.cos(math.radians(140)):
            n += 1
    return n
