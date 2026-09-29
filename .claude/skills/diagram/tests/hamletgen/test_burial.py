"""Where a hamlet's dead lie (feature 273; feature 280 M68, research/religion-and-death/155), and the shared EDGE SEAT the
village's cremation ground stands on (`settlement/civic_grounds/edge_seat.py`).

The edge seat is asked with hand-built settlements - a cluster of houses on an open canvas - so each rule is proved by the
geometry it is about: down the fall line first, turning aside where the fall line is taken, clear of the houses' hull, a
bank margin from water, and None when nothing clears."""

from __future__ import annotations

import math

import pytest

from l7r.diagram.hamletgen.burial import BURIAL_FORMS, stage_burial
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.civic_grounds.edge_seat import EdgeGround, convex_hull, edge_seat
from l7r.diagram.settlement.civic_grounds.edge_seat import rect_gap as _rect_gap
from tests.hamletgen._builders import a_plan

W, H = 60.0, 42.0  # a ground's box, px


def _hamlet(scale: str = "hamlet") -> Settlement:
    s = Settlement(W=1400, H=1400, seed=1)
    s.meta(name="X", scale=scale, ftpx=1.0)
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x, y in ((650, 650), (720, 650), (650, 700), (720, 700))]
    return s


def _seat(s: Settlement, field_px: float = 0.0) -> tuple[float, float] | None:
    return edge_seat(s, 90.0, W, H, EdgeGround(s, clear_px=60.0, stream_px=6.0, ditch_px=6.0, field_px=field_px), reach_px=700.0, step_px=10.0)


def test_a_hamlet_draws_no_ground_of_its_own_and_records_where_its_dead_lie() -> None:
    """Feature 280 M68: a hamlet's own ground rests only on twentieth-century records, so its dead lie in the village's."""
    assert BURIAL_FORMS == ("village_ground",)
    s = _hamlet()
    stage_burial(s, a_plan())
    assert s.M["meta"]["hamlet_burial"] == "village_ground" and not s.M["cemeteries"]
    s.knob_pins["hamlet_burial"] = "own_ground"
    with pytest.raises(ValueError, match="hamlet_burial"):
        stage_burial(s, a_plan())
    v = _hamlet(scale="village")
    stage_burial(v, a_plan())
    assert "hamlet_burial" not in v.M["meta"]
    e = Settlement(W=600, H=600, seed=1)
    e.meta(name="X", scale="hamlet", ftpx=1.0)
    stage_burial(e, a_plan())
    assert "hamlet_burial" not in e.M["meta"], "no houses, nothing to say"


def test_rect_gap() -> None:
    assert _rect_gap((0, 0, 10, 10), (20, 0, 10, 10)) == 10
    assert _rect_gap((0, 0, 10, 10), (5, 5, 10, 10)) == 0
    assert math.isclose(_rect_gap((0, 0, 10, 10), (20, 20, 10, 10)), math.hypot(10, 10))


def test_the_edge_seat_runs_down_the_fall_line_clear_of_the_houses() -> None:
    s = _hamlet()
    x, y = _seat(s)  # the fall runs south (+y)
    assert y > 700 and abs(x - 685) < 1, "straight down the fall line from the middle of the houses"
    assert min(_rect_gap((x, y, W, H), (h["x"], h["y"], h["w"], h["h"])) for h in s.M["houses"]) >= 60.0


def test_the_edge_seat_turns_aside_where_the_fall_line_is_a_paddy() -> None:
    s = _hamlet()
    s.M["fields"] = [{"outline": [(500, 760), (900, 760), (900, 1300), (500, 1300)]}]  # the paddy fills the ground below
    x, y = _seat(s, field_px=10.0)
    assert not (490 < x < 910 and y + H / 2 > 750)
    assert math.dist((x, y), (685, 675)) < 300, "beside the houses, not across the paddy from them"


def test_the_edge_seat_keeps_off_the_water_by_its_bank_margin_only() -> None:
    """Feature 280 M75 (research/religion-and-death/180): no set-back that scales with a watercourse is attested; a ground
    only keeps out of the water, by the bank margin - 20 px off a stream's bank is clear, a ground over the bank is not."""
    s = _hamlet()
    s.M["streams"] = [{"poly": [(100.0, 1100.0), (1300.0, 1100.0)], "w": 7}]
    ground = EdgeGround(s, clear_px=60.0, stream_px=6.0, ditch_px=6.0, field_px=0.0)
    assert ground.clear(s, 685.0, 1100.0 - 3.5 - 20.0 - H / 2, W, H), "20 px off the bank: clear - there is no 75 px band"
    assert not ground.clear(s, 685.0, 1100.0 - 3.5 - 2.0 - H / 2, W, H), "inside the bank margin"
    assert seg_dist(685.0, 1100.0 - 3.5 - 20.0, (100.0, 1100.0), (1300.0, 1100.0)) < 75.0


def test_the_edge_seat_is_none_where_nothing_clears() -> None:
    s = _hamlet()
    s.M["fields"] = [{"outline": [(0, 0), (1400, 0), (1400, 1400), (0, 1400)]}]  # paddy everywhere
    assert _seat(s) is None
    e = Settlement(W=600, H=600, seed=1)
    e.meta(name="X", scale="hamlet", ftpx=1.0)
    assert edge_seat(e, 90.0, 30.0, 20.0, EdgeGround(e, 60.0, 75.0, 6.0, 50.0), reach_px=300.0, step_px=10.0) is None, "no houses to measure from"


def test_the_ground_stands_beyond_the_last_house_not_in_a_gap_among_them() -> None:
    """Settlement-review on Kuwabata (feature 273): a dispersed cluster's inner gap is 60 ft clear of every house, and the
    seat took it. The ground may not enter the houses' hull."""
    from l7r.diagram.settlement._geom import point_in_poly

    s = Settlement(W=1600, H=1600, seed=1)
    s.meta(name="X", scale="hamlet", ftpx=1.0)
    corners = ((500, 500), (1000, 500), (500, 1000), (1000, 1000))
    s.M["houses"] = [{"x": x, "y": y, "w": 46.0, "h": 28.0} for x, y in corners]
    s.M["dry_plots"] = [{"poly": [(1300, 700), (1400, 700), (1400, 800), (1300, 800)]}]
    x, y = _seat(s)
    hull = convex_hull([(cx + fx * 23, cy + fy * 14) for cx, cy in corners for fx in (-1, 1) for fy in (-1, 1)])
    assert not point_in_poly(x, y, hull), "outside the houses, not in the square they enclose"


def test_convex_hull_of_few_points() -> None:
    assert convex_hull([(0.0, 0.0), (1.0, 1.0)]) == [(0.0, 0.0), (1.0, 1.0)]
    assert set(convex_hull([(0.0, 0.0), (2.0, 0.0), (1.0, 1.0), (1.0, 0.5), (0.0, 2.0), (2.0, 2.0)])) == {(0.0, 0.0), (2.0, 0.0), (0.0, 2.0), (2.0, 2.0)}
