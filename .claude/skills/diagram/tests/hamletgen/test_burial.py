"""The hamlet's own burial ground (feature 273, research/religion-and-death.html "Where do a hamlet's dead lie?").

Asked of the stage with hand-built hamlets - a cluster of houses on an open canvas - so each rule is proved by the
geometry it is about: the size band, down the fall line first, turning aside where the fall line is taken, the
set-backs from houses, a stream and a paddy edge, and a recorded "no seat" when nothing clears."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.burial import BURIAL_FORMS, FIELD_SETBACK_PX, GROUND_SQFT, STREAM_SETBACK_PX, ground_size, stage_burial
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement._knobs import BOUNDARY_STONE_CLEAR_FT
from l7r.diagram.settlement.civic_grounds.edge_seat import rect_gap as _rect_gap
from tests.hamletgen._builders import a_plan


def _hamlet(scale: str = "hamlet", form: str | None = "own_ground") -> Settlement:
    s = Settlement(W=1400, H=1400, seed=1)
    s.meta(name="X", scale=scale, ftpx=1.0)
    if form:
        s.knob_pins["hamlet_burial"] = form
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x, y in ((650, 650), (720, 650), (650, 700), (720, 700))]
    return s


def _ground(s: Settlement) -> dict:
    (g,) = s.M["cemeteries"]
    return g


def test_the_ground_is_sized_inside_the_records_band() -> None:
    for households, want in ((3, GROUND_SQFT[0]), (5, GROUND_SQFT[0]), (30, GROUND_SQFT[1]), (80, GROUND_SQFT[1])):
        w, h = ground_size(households, 1.0)
        assert math.isclose(w * h, want, rel_tol=1e-9)
        assert math.isclose(w / h, 1.4, rel_tol=1e-9)
    w, h = ground_size(15, 2.0)  # at 2 ft per px the same ground is drawn half as many px each way
    assert math.isclose(w * h * 4, GROUND_SQFT[0] + 0.4 * (GROUND_SQFT[1] - GROUND_SQFT[0]), rel_tol=1e-9)


def test_rect_gap() -> None:
    assert _rect_gap((0, 0, 10, 10), (20, 0, 10, 10)) == 10
    assert _rect_gap((0, 0, 10, 10), (5, 5, 10, 10)) == 0
    assert math.isclose(_rect_gap((0, 0, 10, 10), (20, 20, 10, 10)), math.hypot(10, 10))


def test_a_hamlet_draws_its_own_ground_down_the_fall_line_clear_of_the_houses() -> None:
    s = _hamlet()
    stage_burial(s, a_plan())  # the fall runs south (+y)
    g = _ground(s)
    assert s.M["meta"]["burial_ground"] == "own"
    assert g["y"] > 700 and abs(g["x"] - 685) < 1  # straight down the fall line from the middle of the houses
    assert min(_rect_gap((g["x"], g["y"], g["w"], g["h"]), (h["x"], h["y"], h["w"], h["h"])) for h in s.M["houses"]) >= BOUNDARY_STONE_CLEAR_FT
    assert "burial ground" in s.out_cls, "the ground is its own kind on the page"


def test_it_turns_aside_where_the_fall_line_is_a_paddy() -> None:
    s = _hamlet()
    s.M["fields"] = [{"outline": [(500, 760), (900, 760), (900, 1300), (500, 1300)]}]  # the paddy fills the ground below
    stage_burial(s, a_plan())
    g = _ground(s)
    assert not (500 - FIELD_SETBACK_PX < g["x"] < 900 + FIELD_SETBACK_PX and g["y"] + g["h"] / 2 > 760 - FIELD_SETBACK_PX)
    assert math.dist((g["x"], g["y"]), (685, 675)) < 300, "beside the houses, not across the paddy from them"


def test_it_keeps_the_stream_set_back() -> None:
    s = _hamlet()
    s.M["streams"] = [{"poly": [(400.0, 820.0), (1000.0, 820.0)], "w": 7}]
    stage_burial(s, a_plan())
    g = _ground(s)
    corners = [(g["x"] + fx * g["w"] / 2, g["y"] + fy * g["h"] / 2) for fx in (-1, 1) for fy in (-1, 1)]
    assert min(seg_dist(px, py, (400.0, 820.0), (1000.0, 820.0)) for px, py in corners) >= STREAM_SETBACK_PX


def test_no_seat_is_recorded_and_nothing_drawn() -> None:
    s = _hamlet()
    s.M["fields"] = [{"outline": [(0, 0), (1400, 0), (1400, 1400), (0, 1400)]}]  # paddy everywhere
    stage_burial(s, a_plan())
    assert s.M["meta"]["burial_ground"] == "no seat" and not s.M["cemeteries"]


def test_only_a_hamlet_draws_one() -> None:
    s = _hamlet(scale="village")
    stage_burial(s, a_plan())
    assert not s.M["cemeteries"] and "burial_ground" not in s.M["meta"]
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="X", scale="hamlet", ftpx=1.0)
    stage_burial(s, a_plan())
    assert not s.M["cemeteries"]


def test_the_knob_rolls_both_forms_and_a_village_ground_draws_nothing() -> None:
    seen = set()
    for seed in range(1, 40):
        s = Settlement(W=1400, H=1400, seed=seed)
        s.meta(name="X", scale="hamlet", ftpx=1.0)
        s.M["houses"] = [{"x": 650.0, "y": 650.0, "w": 46.0, "h": 28.0}]
        stage_burial(s, a_plan())
        seen.add(s.M["meta"]["hamlet_burial"])
        assert bool(s.M["cemeteries"]) == (s.M["meta"]["hamlet_burial"] == "own_ground")
    assert seen == set(BURIAL_FORMS), "both forms occur across seeds"


def test_a_nonsense_pin_is_refused() -> None:
    import pytest

    s = _hamlet(form="in_the_river")
    with pytest.raises(ValueError, match="hamlet_burial"):
        stage_burial(s, a_plan())


def test_the_edge_seat_has_nothing_to_measure_from_without_houses() -> None:
    from l7r.diagram.settlement.civic_grounds.edge_seat import EdgeGround, edge_seat

    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="X", scale="hamlet", ftpx=1.0)
    assert edge_seat(s, 90.0, 30.0, 20.0, EdgeGround(s, 60.0, 75.0, 6.0, 50.0), reach_px=300.0, step_px=10.0) is None
