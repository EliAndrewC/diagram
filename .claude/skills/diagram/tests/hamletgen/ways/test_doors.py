"""Feature 291: a grove farm is reached at its front door - `front_door`, `lay_door_paths`, `own_street`."""

from __future__ import annotations

from l7r.diagram.hamletgen.consts import FOOTPATH_FABRIC_GAP
from l7r.diagram.hamletgen.ways.serve import DOOR_REACH_FT, front_door, lay_door_paths
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.homestead_parts.grove_sides import bundle_turn
from l7r.diagram.settlement.rolling.dispersed import dispersed_layout


def _farm(x: float, y: float, sides: int = 2) -> dict:
    geom = dispersed_layout(x, y, 46.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=sides, turn=bundle_turn("NW", -1), thin=17.0, sun_east=22.0, way_in=36.0)
    return {"x": x, "y": y, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain", "geom": geom}


def test_the_front_door_is_past_the_yard_on_the_open_side() -> None:
    h = _farm(500.0, 400.0)
    door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
    assert door is not None and door[1] > h["geom"]["yard"][1] + h["geom"]["yard"][3] / 2, "south of the yard, the lee front"
    assert front_door({"x": 0.0, "y": 0.0, "geom": {}}, 8.0) is None, "a farm with no grove of its own has no front door here"


def test_a_ring_s_door_lines_up_with_its_way_in() -> None:
    h = _farm(500.0, 400.0, sides=4)
    door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
    halves = [r for r, (f, _d) in zip(h["geom"]["groves"], h["geom"]["grove_faces"], strict=True) if tuple(f) == (0, 1)]
    assert door is not None and len(halves) == 2
    lo, hi = sorted(halves)
    assert lo[0] + lo[2] / 2 < door[0] < hi[0] - hi[2] / 2, "between the two halves of the front band"


def test_a_door_far_from_the_lanes_gets_a_footpath_to_them() -> None:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    h = _farm(700.0, 400.0)
    s.M["houses"] = [h]
    s.M["lanes"] = [{"pts": [[100.0, 700.0], [1300.0, 700.0]], "w": 6, "connector": True}]
    door = front_door(h, FOOTPATH_FABRIC_GAP + 4.0)
    assert door is not None and seg_dist(door[0], door[1], (100.0, 700.0), (1300.0, 700.0)) > DOOR_REACH_FT
    assert lay_door_paths(s, [], [], []) == 1
    segs = [(a, b) for ln in s.M["lanes"] for a, b in zip(ln["pts"], ln["pts"][1:], strict=False)]
    assert min(seg_dist(door[0], door[1], a, b) for a, b in segs) <= DOOR_REACH_FT
    assert lay_door_paths(s, [], [], []) == 0, "a door already reached gets nothing"


def test_a_door_no_route_reaches_is_left_to_the_roll_s_report() -> None:
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    h = _farm(700.0, 400.0)
    s.M["houses"] = [h]
    s.M["lanes"] = [{"pts": [[100.0, 700.0], [1300.0, 700.0]], "w": 6, "connector": True}]
    wall = [(0.0, 560.0), (1400.0, 560.0), (1400.0, 600.0), (0.0, 600.0)]  # hard ground right across the way
    assert lay_door_paths(s, [wall], [], []) == 0
    assert len(s.M["lanes"]) == 1, "nothing drawn"
