"""Washing places at the water's edge (feature 374 wave 150, `hamletgen/washing.py`, 0065): a knob between shared footings on the
bank and a step at each house's channel, seated where the overlap matrix admits them."""

from __future__ import annotations

import math
import types

import pytest

from l7r.diagram.hamletgen import washing as wa
from l7r.diagram.settlement import Settlement


def _plan(seed: int = 1) -> types.SimpleNamespace:
    return types.SimpleNamespace(spec=types.SimpleNamespace(seed=seed))


def _s() -> Settlement:
    s = Settlement(W=800, H=800, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    return s


def test_the_form_is_rolled_and_a_house_step_needs_a_farm_channel() -> None:
    forms = {wa.washing_form(_plan(sd), {"farm_channels": [{}]}) for sd in range(40)}
    assert forms == {"shared", "each_house"}, "both forms roll where channels run to the houses"
    assert {wa.washing_form(_plan(sd), {}) for sd in range(40)} == {"shared"}, "no channel, only the shared form"


def test_the_courses_are_the_brook_the_race_and_every_ditch_the_drain_too() -> None:
    M = {
        "streams": [{"poly": [[0, 0], [10, 0]], "w": 8.0}, {"poly": [[0, 0]]}],
        "channels": [{"poly": [[0, 2], [10, 2]], "w": 6.0}, {"poly": [[1, 1]]}],
        "field_ditches": [{"poly": [[0, 5], [10, 5]], "role": "main", "w": 2.0}, {"poly": [[0, 9], [10, 9]], "role": "drain"}],
        "farm_channels": [{"pts": [[0, 20], [10, 20]]}, {"poly": [[3, 3]]}],
    }
    got = wa.passing_courses(M)
    assert [hw for _c, hw in got] == [4.0, 3.0, 1.0, 0.75, 1.25], "the brook, the head race, the main, the drain at 1.5 ft, a farm channel at 2.5 ft"


def test_the_nearest_point_on_a_course_and_its_segment() -> None:
    q, d, seg = wa.nearest_on([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], (12.0, 6.0))
    assert q == (10.0, 6.0) and d == pytest.approx(2.0) and seg == 1


def test_a_footing_stands_on_the_houses_side_its_foot_at_the_water() -> None:
    rec = wa.footing([(0.0, 0.0), (100.0, 0.0)], (50.0, 0.0), 0, 4.0, (50.0, 80.0), 0.0, lambda v: v)
    assert rec["x"] == 50.0 and rec["y"] == pytest.approx(4.0 + 3.0) and (rec["w"], rec["h"]) == (4.0, 6.0) and rec["rot"] == 0.0
    other = wa.footing([(0.0, 0.0), (100.0, 0.0)], (50.0, 0.0), 0, 4.0, (50.0, -80.0), 8.0, lambda v: v)
    assert other["y"] == pytest.approx(-7.0) and other["x"] == 58.0, "the far side's households, slid 8 along the bank"


def test_shared_places_one_for_every_few_households_on_a_bank() -> None:
    s = _s()
    s.M["streams"] = [{"poly": [[50.0, 400.0], [750.0, 400.0]], "w": 8.0}]
    s.M["houses"] = [{"x": 100.0 + 60.0 * k, "y": 330.0} for k in range(9)] + [{"x": 400.0, "y": 50.0}]  # the last far off
    got = wa.shared_places(s, s.M)
    assert len(got) == math.ceil(9 / wa.HOUSEHOLDS_PER_WASHING), "one for every four of the nine on the bank"
    assert all(r["y"] < 400.0 for r in got), "on their side of the water"
    assert s.M["washing_places"] == got


def test_a_shared_place_with_no_seat_is_left_out(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _s()
    s.M["streams"] = [{"poly": [[50.0, 400.0], [750.0, 400.0]], "w": 8.0}]
    s.M["houses"] = [{"x": 300.0, "y": 330.0}]
    monkeypatch.setattr(s, "admits", lambda *a, **k: False)
    assert wa.shared_places(s, s.M) == [] and s.M["meta"]["washing_no_seat"] == 1, "left out, and counted"


def test_each_house_places_a_step_at_its_channels_end() -> None:
    s = _s()
    s.M["farm_channels"] = [{"poly": [[100.0, 100.0], [100.0, 200.0]], "of": [100.0, 230.0], "w": 2.5}, {"poly": [[5.0, 5.0]]}]
    got = wa.each_house_places(s, s.M)
    assert len(got) == 1 and got[0]["y"] == pytest.approx(200.0) and abs(got[0]["x"] - 100.0) > 3.0, "at the channel's end, off its bank"


def test_each_house_with_no_seat_keeps_none(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _s()
    s.M["farm_channels"] = [{"pts": [[100.0, 100.0], [100.0, 200.0]]}]
    monkeypatch.setattr(s, "admits", lambda *a, **k: False)
    assert wa.each_house_places(s, s.M) == [] and s.M["meta"]["washing_no_seat"] == 1


def test_the_stage_draws_each_place_and_records_the_form(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _s()
    s.M["streams"] = [{"poly": [[50.0, 400.0], [750.0, 400.0]], "w": 8.0}]
    s.M["houses"] = [{"x": 300.0, "y": 330.0}]
    n = len(s.out)
    wa.stage_washing(s, _plan(1))
    assert s.M["meta"]["washing_form"] == "shared" and s.M["meta"]["washing_places"] == 1
    assert len(s.out) == n + 1 and s.out_cls[-1] == "washing place" and wa.STEP_STONE in s.out[-1]
    s2 = _s()
    s2.M["farm_channels"] = [{"poly": [[100.0, 100.0], [100.0, 200.0]], "of": [100.0, 230.0]}]
    monkeypatch.setattr(wa, "washing_form", lambda plan, M: "each_house")
    wa.stage_washing(s2, _plan(1))
    assert s2.M["meta"]["washing_form"] == "each_house" and s2.M["meta"]["washing_places"] == 1


def test_a_bank_is_one_side_of_the_water_and_a_house_takes_its_nearest_water() -> None:
    assert wa.bank_of([(0.0, 0.0), (10.0, 0.0)], 0, (5.0, 3.0)) == 1 and wa.bank_of([(0.0, 0.0), (10.0, 0.0)], 0, (5.0, -3.0)) == -1
    s = _s()
    s.M["streams"] = [{"poly": [[50.0, 400.0], [750.0, 400.0]], "w": 8.0}]
    s.M["field_ditches"] = [{"poly": [[50.0, 300.0], [750.0, 300.0]], "role": "main", "w": 2.0}]
    s.M["houses"] = [{"x": 200.0, "y": 380.0}, {"x": 400.0, "y": 420.0}, {"x": 600.0, "y": 310.0}]
    got = wa.shared_places(s, s.M)
    assert len(got) == 3, "the two banks of the brook apart, and the house by the ditch at the ditch"
    assert sorted(round(r["y"]) for r in got) == [304, 393, 407], "the ditch's 1 ft half-width plus the footing's 3, the brook's 4 plus 3 either side"


def test_no_water_no_washing_place() -> None:
    s = _s()
    s.M["houses"] = [{"x": 300.0, "y": 330.0}]
    assert wa.shared_places(s, s.M) == [] and "washing_places" not in s.M
