"""Feature 291: a grove farm is reached at its front door - `front_door`, `lay_door_paths`, `own_street`."""

from __future__ import annotations

import pytest

from l7r.diagram.hamletgen.consts import DOOR_STEP_FT, FOOTPATH_FABRIC_GAP
from l7r.diagram.hamletgen.ways.serve import front_door, lay_door_paths, street_arrives
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.homestead_parts.grove_sides import bundle_turn
from l7r.diagram.settlement.rolling.dispersed import dispersed_layout


def _farm(x: float, y: float, sides: int = 2) -> dict:
    geom = dispersed_layout(x, y, 46.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=sides, turn=bundle_turn("NW", -1), thin=17.0, sun_east=22.0, way_in=36.0)
    return {"x": x, "y": y, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain", "geom": geom}


def test_the_front_door_is_past_the_yard_on_the_open_side() -> None:
    h = _farm(500.0, 400.0)
    door = front_door(h, DOOR_STEP_FT)
    assert door is not None and door[1] > h["geom"]["yard"][1] + h["geom"]["yard"][3] / 2, "south of the yard, the lee front"
    assert front_door({"x": 0.0, "y": 0.0, "geom": {}}, 8.0) is None, "a farm with no grove of its own has no front door here"


def test_a_slanted_front_takes_its_door_just_past_the_yard_edge() -> None:
    """The door stands `clear` past where the house-to-yard ray leaves the yard box, not past its projected half-width,
    which overshot on a slant (Kashikawa, 12.4 ft past the yard at ten degrees)."""
    h = {"x": 2268.1, "y": 2143.9, "geom": {"groves": [[0.0, 0.0, 1.0, 1.0]], "yard": [2275.0, 2184.3, 64.8, 44.7]}}
    door = front_door(h, 8.0)
    assert door is not None
    ey = 2184.3 + 44.7 / 2
    assert abs(door[1] - ey - 8.0 * (door[1] - 2184.3) / ((door[0] - 2275.0) ** 2 + (door[1] - 2184.3) ** 2) ** 0.5) < 0.5, "clear past the bottom edge"
    assert door[1] - ey < 8.0 + 1e-6


def test_a_ring_s_door_lines_up_with_its_way_in() -> None:
    h = _farm(500.0, 400.0, sides=4)
    door = front_door(h, DOOR_STEP_FT)
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
    door = front_door(h, DOOR_STEP_FT)
    assert door is not None and not street_arrives(h, door, [((100.0, 700.0), (1300.0, 700.0))], None, [])
    assert lay_door_paths(s, [], [], []) == 1
    segs = [(a, b) for ln in s.M["lanes"] for a, b in zip(ln["pts"], ln["pts"][1:], strict=False)]
    assert street_arrives(h, door, segs, None, [])
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


def test_a_door_path_loses_the_hook_at_its_door() -> None:
    """`door_unhooked`: a first leg of 12 ft or less turned back from by 90 degrees or more goes - straight from the door
    where that is clear, else from the vertex after the door; a path with no hook is untouched."""
    from l7r.diagram.hamletgen.ways.geom import door_unhooked

    hooked = [(0.0, 0.0), (0.0, 6.0), (-110.0, 6.0), (-180.0, -100.0)]
    assert door_unhooked(hooked, lambda a, b: True) == [(0.0, 0.0), (-110.0, 6.0), (-180.0, -100.0)]
    assert door_unhooked(hooked, lambda a, b: False) == hooked[1:]
    straight = [(0.0, 0.0), (0.0, 30.0), (0.0, 60.0)]
    assert door_unhooked(straight, lambda a, b: True) == straight
    assert door_unhooked(hooked[:2], lambda a, b: True) == hooked[:2]


def test_a_ring_s_east_or_west_front_takes_its_gap_across_y_and_a_yard_on_the_house_has_no_door() -> None:
    """`front_door`: a ring whose front band is split top and bottom (an east or west front) puts the door in the gap
    along y; a yard centered on the house gives no direction out, so no door."""
    h = {"x": 0.0, "y": 0.0, "geom": {"yard": [60.0, 0.0, 40.0, 30.0], "groves": [[120.0, -60.0, 20.0, 80.0], [120.0, 60.0, 20.0, 80.0]], "grove_faces": [[1, 0], [1, 0]]}}
    door = front_door(h, 8.0)
    assert door is not None and door[1] == 0.0 and door[0] > 80.0, "between the two halves, past the yard"
    assert front_door({"x": 5.0, "y": 5.0, "geom": {"yard": [5.0, 5.0, 40.0, 30.0], "groves": [[0, 0, 1, 1]]}}, 8.0) is None


def test_a_household_reached_across_its_neighbor_s_yard_gets_no_door_path() -> None:
    """Feature 317, plan D2: a household reached by passage has no way of its own - the door pass leaves it, however far its
    door stands from the lanes."""
    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    h = {**_farm(700.0, 400.0), "reached_across": [500.0, 400.0], "passage_depth": 1}
    s.M["houses"] = [h]
    s.M["lanes"] = [{"pts": [[100.0, 700.0], [1300.0, 700.0]], "w": 6, "connector": True}]
    assert lay_door_paths(s, [], [], []) == 0 and len(s.M["lanes"]) == 1


def test_a_door_path_the_law_refuses_taut_is_routed_at_the_law_s_own_gap(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Cohort seed 33 (feature 328 wave 89): a row farm's straight step to its street ran 1 ft past its own garden bed, which
    the law keeps 7 ft off, and the door path tried nothing else. Where the law refuses the first path, a route at the law's
    own gap (`WEB_FABRIC_GAP`) is tried, pulled taut only as far as the law's ground half keeps each step."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.consts import WEB_FABRIC_GAP
    from l7r.diagram.hamletgen.ways import serve, settle

    gaps: list[float] = []
    detour = [(0.0, 0.0), (5.0, 20.0), (100.0, 20.0)]
    monkeypatch.setattr(serve, "route_from_door", lambda door, q, hard, walls, water, ok, gap=FOOTPATH_FABRIC_GAP: gaps.append(gap) or list(detour))
    monkeypatch.setattr(serve, "pulled", lambda p, ok: list(p))
    monkeypatch.setattr(serve, "door_unhooked", lambda p, ok: list(p))
    monkeypatch.setattr(serve, "to_first_arrival", lambda p, segs, gap, ok: list(p))
    monkeypatch.setattr(settle, "square_run", lambda M, p: list(p))
    asked: list[list] = []

    class _Law:
        def __call__(self, path, width):  # the taut step is refused, the routed one kept
            asked.append(list(path))
            return len(path) == 3

        def on_lawful_ground(self, run, width):
            return True

    s = SimpleNamespace(M={"lanes": []})
    got = serve.door_path(s, (0.0, 0.0), [((100.0, -50.0), (100.0, 50.0))], [], [], [], [], _Law())
    assert got == detour
    assert gaps == [WEB_FABRIC_GAP], "the straight step was clear, so only the law's-gap route was asked of the router"
    assert asked[0] == [(0.0, 0.0), (100.0, 0.0)], "the straight step first"


def test_closes_a_needle_refuses_a_door_path_that_makes_a_sliver() -> None:
    """Feature 374 wave 146 (dike-pond seed 3, polder seed 4): a door path is a tree lane no settle may cut, so one closing a
    sliver with the ways it meets is refused where it is laid."""
    from l7r.diagram.hamletgen.ways.serve import closes_a_needle

    lanes = [{"pts": [(0.0, 0.0), (100.0, 0.0)]}]
    assert closes_a_needle(lanes, [(0.0, 0.0), (50.0, 3.0), (100.0, 0.0)])
    assert not closes_a_needle(lanes, [(50.0, 0.0), (50.0, 80.0)]), "a T"


def test_the_room_off_a_grove_is_counted_once() -> None:
    """Feature 385 T98 (plan D119): the door path's band grown 11 ft a side and then routed at the footpath's gap stood its
    middle 18 ft off the trees, and cohort seed 22's two linear farms had no lawful door path; the connector kept 10 ft."""
    from l7r.diagram.hamletgen.consts import GROVE_WORKING_ROOM_FT
    from l7r.diagram.hamletgen.ways import serve, track

    assert serve.band_grow(FOOTPATH_FABRIC_GAP) / 2 + FOOTPATH_FABRIC_GAP == 1.5 + GROVE_WORKING_ROOM_FT == 11.0
    assert serve.band_grow(12.0) == 0.0, "a gap past 0036's room grows nothing"
    assert track.CONNECTOR_BAND_GAP_FT == GROVE_WORKING_ROOM_FT + track.CONNECTOR_WIDTH / 2 == 12.5
    assert 2 * track.CONNECTOR_BAND_GAP_FT <= 32.0, "dispersed farms' bands stand 32 ft apart"


def test_a_door_path_keeps_the_room_off_a_grove_however_it_was_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 385 T98's claims round: with the band grown less (`band_grow`), only the routed leg kept 0036's 11 ft - the
    straight step and the pull tested the bands at no gap, so a path's middle could pass 4 ft off the trees."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.ways import serve, settle

    detour = [(0.0, 0.0), (0.0, -40.0), (100.0, -40.0), (100.0, 0.0)]
    monkeypatch.setattr(serve, "route_from_door", lambda door, q, hard, walls, water, ok, gap=FOOTPATH_FABRIC_GAP: list(detour))
    monkeypatch.setattr(serve, "pulled", lambda p, ok: list(p))
    monkeypatch.setattr(serve, "door_unhooked", lambda p, ok: list(p))
    monkeypatch.setattr(serve, "to_first_arrival", lambda p, segs, gap, ok: list(p))
    monkeypatch.setattr(settle, "square_run", lambda M, p: list(p))

    class _Law:
        def __call__(self, path, width):
            return True

        def on_lawful_ground(self, run, width):
            return True

    band = [(40.0, 5.0), (60.0, 5.0), (60.0, 20.0), (40.0, 20.0)]  # 5 ft off the straight step: inside the footpath's gap
    s = SimpleNamespace(M={"lanes": []})
    args = (s, (0.0, 0.0), [((100.0, -50.0), (100.0, 50.0))], [], [band], [], [], _Law())
    assert serve.door_path(*args) == [(0.0, 0.0), (100.0, 0.0)], "the band only as a wall: crossing it is all that is asked"
    assert serve.door_path(*args, [band]) == detour, "held off the band by the footpath's gap, the step goes round"


def test_a_way_near_the_door_but_far_from_the_house_still_owes_a_footpath() -> None:
    """Feature 385 T97 (D125): off a row the door's distance alone was asked, so a way within 60 ft of the door point, 8 ft
    past the yard, counted the farm reached though it stood beyond 0246's 60 ft of the house and 12 ft of its built ground."""
    h = _farm(700.0, 400.0)
    door = front_door(h, DOOR_STEP_FT)
    assert door is not None
    c = (700.0, 400.0)
    ux, uy = (door[0] - c[0]) / ((door[0] - c[0]) ** 2 + (door[1] - c[1]) ** 2) ** 0.5, (door[1] - c[1]) / ((door[0] - c[0]) ** 2 + (door[1] - c[1]) ** 2) ** 0.5
    far = (door[0] + 55.0 * ux, door[1] + 55.0 * uy)  # 55 ft past the door, straight out from the house
    way = [((far[0] - 50.0 * uy, far[1] + 50.0 * ux), (far[0] + 50.0 * uy, far[1] - 50.0 * ux))]
    assert seg_dist(door[0], door[1], *way[0]) < 60.0 < seg_dist(c[0], c[1], *way[0])
    assert not street_arrives(h, door, way, None, []), "beyond 60 ft of the house: the farm owes its footpath"


def test_a_street_is_anchored_at_each_farm_it_serves_without_a_path() -> None:
    """Feature 385 T97 (D125): the trim anchored at a door within 12 ft of its street, while a farm took no door path wherever
    its street served it from its house - so a street could be cut back past a farm it served."""
    from l7r.diagram.hamletgen.ways.serve import street_anchors

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    h = _farm(700.0, 400.0)
    s.M["houses"] = [h]
    street = {"pts": [[100.0, 440.0], [1300.0, 440.0]], "w": 5, "street": True, "street_index": 0}  # 40 ft from the house
    s.M["lanes"] = [street]
    door = front_door(h, DOOR_STEP_FT)
    assert door is not None and street_arrives(h, door, [((100.0, 440.0), (1300.0, 440.0))], 0, [])
    assert [(round(x), round(y)) for x, y in street_anchors(s)] == [(700, 440)], "the street's point nearest the house"
    s.M["lanes"] = [{**street, "pts": [[100.0, 600.0], [1300.0, 600.0]]}]  # 200 ft off: not served, no anchor
    assert street_anchors(s) == []
