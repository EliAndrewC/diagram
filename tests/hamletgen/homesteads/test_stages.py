"""`hamletgen/homesteads/stages.py` helpers on stub settlements - no roll (269 E3, B18)."""

from __future__ import annotations

import math

import pytest

from l7r.diagram.hamletgen.homesteads.stages import face_the_houses, turn_the_seat
from l7r.diagram.settlement.rolling.bearing import COMMON_BEARING_DEG, MarginBearing
from tests.settlement._builders import _nuc_village


class _Plan:
    seat = {"along": (1.0, 0.0)}
    envelope = [(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)]


def test_the_hamlet_rolls_its_common_bearing_near_south_and_follows_its_margin() -> None:
    s = _nuc_village()
    face_the_houses(s, _Plan())  # type: ignore[arg-type]
    assert abs(s._house_bearing) <= COMMON_BEARING_DEG and s.M["meta"]["house_bearing_deg"] == s._house_bearing
    assert isinstance(s._bearing_follow, MarginBearing) and s._bearing_follow.along == 0.0
    again = _nuc_village()
    face_the_houses(again, _Plan())  # type: ignore[arg-type]
    assert again._house_bearing == s._house_bearing, "rolled from the map's seed"

    class _NoField(_Plan):
        envelope = [(0.0, 0.0), (1.0, 1.0)]

    face_the_houses(s, _NoField())  # type: ignore[arg-type]
    assert s._bearing_follow is None


def test_a_front_row_seat_stands_off_by_its_turned_reach() -> None:
    """The seat moves out along the chord's normal by how much further the turned core reaches toward the chord; an
    unturned house does not move, and a quarter-turned long house moves by the difference of its half-length and depth."""
    s = _nuc_village()
    s._house_bearing = 0.0
    core = (-30.0, -15.0, 30.0, 15.0)
    s._house_rot = lambda x, y: 0.0  # type: ignore[method-assign]
    assert turn_the_seat(s, (100.0, 100.0), (0.0, -1.0), core) == pytest.approx((100.0, 100.0))
    s._house_rot = lambda x, y: 90.0  # type: ignore[method-assign]
    moved = turn_the_seat(s, (100.0, 100.0), (0.0, -1.0), core)
    assert moved == pytest.approx((100.0, 100.0 - 15.0)), "30 ft of half-length against 15 of depth"
    assert math.dist(moved, (100.0, 100.0)) > 0.0


def test_the_seating_admits_a_corridor_by_the_ways_own_ground_test_built_once_per_seating() -> None:
    """Feature 287, ways: `corridor_ground` is `settle.corridor_on_lawful_ground`'s question over one `Lawful` per standing
    seating - into the paddy refused, open ground admitted, and the law rebuilt only when a house has been seated."""
    from l7r.diagram.hamletgen.homesteads.stages import corridor_ground
    from l7r.diagram.hamletgen.ways.settle import corridor_on_lawful_ground
    from tests.hamletgen.test_homesteads import _toy_hamlet

    s, plan = _toy_hamlet(10)
    ground = corridor_ground(s)
    cx, cy = float(plan.seat["cx"]), float(plan.seat["cy"])
    open_run = [(cx - 100.0, cy - 60.0), (cx - 100.0, cy - 160.0)]
    assert ground(open_run) is corridor_on_lawful_ground(s.M, open_run) is True, "the ways' own verdict"
    s.M["houses"].append({"x": cx - 100.0, "y": cy - 110.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain"})
    assert not ground(open_run), "a house seated since: the law is rebuilt and the run now fouls it"
    assert ground(open_run) is corridor_on_lawful_ground(s.M, open_run)


def test_a_margin_with_no_lawful_way_out_seats_no_one(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.hamletgen.homesteads import stages as st
    from tests.hamletgen.test_homesteads import _toy_hamlet

    s, plan = _toy_hamlet(10)
    monkeypatch.setattr(st, "exit_bearing", lambda *a: None)
    assert st._seat_households(s, plan) == (0, 0) and not s.M["houses"]
