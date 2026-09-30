"""Feature 291 amendment 5: a dispersed farm's own water as a channel into its grounds - `homesteads/farm_water.py`."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.homesteads import farm_water as fw
from l7r.diagram.hamletgen.homesteads.row_rules import water_rules
from l7r.diagram.settlement import Settlement


def test_the_supply_courses_are_the_ditches_but_the_drain_and_the_brook() -> None:
    M = {
        "field_ditches": [{"poly": [[0, 0], [100, 0]], "role": "main"}, {"poly": [[0, 50], [100, 50]], "role": "drain"}, {"poly": [[5, 5]], "role": "branch"}],
        "streams": [{"poly": [[0, 200], [100, 200]]}],
    }
    assert fw.supply_courses(M) == [[(0.0, 0.0), (100.0, 0.0)], [(0.0, 200.0), (100.0, 200.0)]]


def test_source_points_are_nearest_first_and_include_each_course_s_nearest_point() -> None:
    pts = fw.source_points([[(0.0, 0.0), (100.0, 0.0)]], (37.0, 30.0), 20.0, 3)
    assert pts[0] == (37.0, 0.0), "the course's own nearest point comes first"
    assert len(pts) == 3 and all(math.dist(pts[i], (37.0, 30.0)) <= math.dist(pts[i + 1], (37.0, 30.0)) for i in range(2))


def test_the_dooryard_end_is_a_step_off_the_yard_toward_the_water() -> None:
    yard = [[0.0, 0.0], [40.0, 0.0], [40.0, 30.0], [0.0, 30.0]]
    end = fw.dooryard_end(yard, (20.0, 200.0), 6.0)
    assert end[1] > 30.0 and abs(end[1] - 30.0 - 6.0) < 1.0 and abs(end[0] - 20.0) < 1.0, end


def test_a_channel_crosses_no_water_but_at_its_own_mouth() -> None:
    water = [((-10.0, 0.0), (10.0, 0.0))]
    assert not fw.crosses_other_water([(0.0, -2.0), (0.0, 100.0)], water, 6.0), "the crossing 2 ft from the start is its mouth"
    assert fw.crosses_other_water([(0.0, -50.0), (0.0, 100.0)], water, 6.0), "50 ft along is another water"
    assert fw.cross_t((0.0, 0.0), (1.0, 0.0), (0.5, -1.0), (0.5, 1.0)) == 0.5
    assert fw.cross_t((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)) == 0.0, "parallel lines meet nowhere"


def _farm_settlement(with_yard: bool = True) -> tuple[Settlement, dict]:
    s = Settlement(800, 800, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    h = {"x": 400.0, "y": 300.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain", "geom": {"groves": [[400.0, 240.0, 200.0, 40.0]], "bbox": [400.0, 330.0, 240.0, 200.0]}}
    s.M["houses"] = [h]
    s.M["threshing_yards"] = [{"of": [400.0, 300.0], "x": 400.0, "y": 350.0, "poly": [[380.0, 340.0], [420.0, 340.0], [420.0, 360.0], [380.0, 360.0]]}] if with_yard else []
    s.M["field_ditches"] = [{"poly": [[100.0, 500.0], [700.0, 500.0]], "role": "main"}]
    s.M["meta"] = {**s.M.get("meta", {}), "settlement_form": "dispersed", "farm_water": "channel"}
    return s, h


def test_a_farm_takes_a_channel_from_the_nearest_ditch_into_its_dooryard() -> None:
    s, h = _farm_settlement()
    dry = fw.farm_channels(s, [h])
    assert dry == []
    rec = s.M["farm_channels"][0]
    assert rec["of"] == [400.0, 300.0] and abs(rec["pts"][0][1] - 500.0) < 1.0, "led off the main"
    assert 360.0 < rec["pts"][-1][1] < 375.0, "ending a step off the threshing yard"
    assert s.M["drawn_channels"][-1]["farm"] == [400.0, 300.0]
    assert water_rules(s.M) == []


def test_a_farm_with_no_yard_or_no_water_is_left_to_its_well_and_reported() -> None:
    s, h = _farm_settlement(with_yard=False)
    assert fw.farm_channels(s, [h]) == [h], "no dooryard to lead it into"
    assert water_rules(s.M) == [("farm_without_its_channel", (400.0, 300.0))]
    s2, h2 = _farm_settlement()
    s2.M["field_ditches"] = []
    assert fw.farm_channels(s2, [h2]) == [h2], "no water to lead it off"


def test_a_channel_goes_round_another_farm_s_grove_and_frame() -> None:
    s, h = _farm_settlement()
    other = {"x": 400.0, "y": 440.0, "w": 46.0, "h": 28.0, "geom": {"bbox": [400.0, 440.0, 500.0, 60.0]}}
    s.M["houses"].append(other)
    s.M["groves"] = [{"of": [400.0, 440.0], "x": 400.0, "y": 440.0, "w": 500.0, "h": 40.0}, {"of": [400.0, 300.0], "x": 400.0, "y": 240.0, "w": 200.0, "h": 40.0}]
    walls = fw._obstacles(s, h)[1]
    assert any(min(p[0] for p in w) < 160.0 for w in walls), "the other farm's grove is a wall"
    assert not any(min(p[1] for p in w) >= 219.0 and max(p[1] for p in w) <= 261.0 for w in walls), "its own grove is not"
