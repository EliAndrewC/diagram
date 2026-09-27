"""The one caption placer (feature 266): the cartographic standard, case by case, on synthetic sheets (SC-002, SC-003)."""

from __future__ import annotations

import math

import pytest

from l7r.diagram.labels import CIVIC_GROUPS, Obstacle, ObstacleIndex, Subject, Way, cut, layouts, place, upright
from l7r.diagram.labels.geom import area_centroid, centroid, inside, nearest_points, poly_gap, poly_seg_gap, rect, segments_cross
from l7r.diagram.labels.placer import rings
from l7r.diagram.labels.standard import POSITIONS, PREFERRED_OFFSET_EM, REACH_EM, WEIGHT_OBSTACLE, WEIGHT_WAY, block_half

SIZE = 8.0
BOARD = Subject("point", tuple(rect(500.0, 500.0, 6.0, 2.5)))


def _gap(p, subject: Subject) -> float:
    return poly_gap(list(p.block), list(subject.poly))


def test_the_first_position_is_upper_right_at_the_preferred_offset() -> None:
    """Scenario 1: clear ground, so the caption takes the standard's first position, the preferred gap off the board's
    drawn edge, with no leader."""
    p = place("notice board", SIZE, BOARD, ObstacleIndex())
    assert (p.position, p.ring, p.lines, p.leader) == ("upper right", 0, ("notice board",), None)
    assert _gap(p, BOARD) == pytest.approx(PREFERRED_OFFSET_EM * SIZE, abs=1e-6)
    assert p.block[3][0] > 506.0 and max(q[1] for q in p.block) < 497.5, "right of the board and above it"


def test_a_blocked_position_falls_to_the_next_ranked_one() -> None:
    """Scenario 2: a house over the upper right sends the caption to the upper left, still at the preferred gap."""
    house = Obstacle(tuple(rect(560.0, 480.0, 40.0, 15.0)), WEIGHT_OBSTACLE)
    p = place("notice board", SIZE, BOARD, ObstacleIndex([house]))
    assert (p.position, p.ring, p.leader) == ("upper left", 0, None)


def test_every_adjacent_seat_is_tried_before_a_farther_one_and_the_farther_one_gets_a_leader() -> None:
    """Scenario 3: a ring of houses fills every seat at the preferred gap; the caption goes one ring out - a free seat
    beats any covered near one - and, no longer directly beside the board, is tied back by a leader."""
    ring0 = [rect(500.0, 500.0, 6.0 + 5.0, 2.5 + 5.0)]
    walls = [Obstacle(tuple(q), WEIGHT_OBSTACLE) for q in _collar(ring0[0], 4.5)]
    p = place("notice board", SIZE, BOARD, ObstacleIndex(walls))
    assert p.ring > 0 and p.cost == 0.0
    assert p.leader is not None
    a, b = p.leader
    assert poly_gap(list(p.block), [a, a, a]) < 1.5 and poly_gap(list(BOARD.poly), [b, b, b]) < 1.5, "block to board"


def _collar(poly, width):
    """Four thin rects hugging `poly`'s box out to `width` - obstacles that fill every seat at the preferred gap."""
    xs, ys = [q[0] for q in poly], [q[1] for q in poly]
    x0, y0, x1, y1 = min(xs) - 40, min(ys) - 20, max(xs) + 40, max(ys) + 20
    return [
        rect((x0 + x1) / 2, y0 - width / 2 + 16, (x1 - x0) / 2 + 60, width),
        rect((x0 + x1) / 2, y1 + width / 2 - 16, (x1 - x0) / 2 + 60, width),
        rect(x0 - width / 2 + 30, (y0 + y1) / 2, width, (y1 - y0) / 2 + 20),
        rect(x1 + width / 2 - 30, (y0 + y1) / 2, width, (y1 - y0) / 2 + 20),
    ]


def test_a_caption_is_never_dropped() -> None:
    """Scenario 4: a sheet with no free seat anywhere in reach - the caption still goes down, where it covers least."""
    everything = Obstacle(tuple(rect(500.0, 500.0, 900.0, 900.0)), WEIGHT_OBSTACLE)
    p = place("notice board", SIZE, BOARD, ObstacleIndex([everything]))
    assert p.cost == WEIGHT_OBSTACLE and p.lines
    assert (p.ring, p.rank) == (0, 0), "every seat costs the same, so the nearest, best-ranked one"


def test_crossing_one_way_costs_less_than_crossing_two() -> None:
    """Esri: a label that must cross roads crosses "one road instead of several". Each way crossed is 500."""
    idx = ObstacleIndex(ways=[Way(((0.0, 100.0), (300.0, 100.0)), 1.5), Way(((0.0, 110.0), (300.0, 110.0)), 1.5)])
    one = rect(150.0, 96.0, 20.0, 3.0)
    both = rect(150.0, 105.0, 20.0, 8.0)
    assert idx.cost(one, 4.0) == WEIGHT_WAY
    assert idx.cost(both, 4.0) == 2 * WEIGHT_WAY
    assert idx.cost(rect(150.0, 40.0, 20.0, 3.0), 4.0) == 0.0


class _Priced(ObstacleIndex):
    """An index whose every seat covers something: a way on the board's right, a house everywhere else."""

    def cost(self, block, clear, subject=None, text="", civic=False):
        return WEIGHT_WAY if centroid(list(block))[0] > 520.0 else WEIGHT_OBSTACLE


def test_when_nothing_is_free_the_least_weight_wins() -> None:
    """A sheet whose every seat covers something: a seat crossing one way beats every seat on a house, even at a lower
    rank - Esri's "a location with the lowest total feature weight is chosen"."""
    p = place("notice board", SIZE, BOARD, _Priced())
    assert p.cost == WEIGHT_WAY and p.position == "upper right" and p.ring == 0


def test_the_frame_is_never_left() -> None:
    """A clipped caption cannot be read: with the frame's right edge at the board, the right-hand seats are gone."""
    p = place("notice board", SIZE, BOARD, ObstacleIndex(), frame=(0.0, 0.0, 510.0, 1000.0))
    assert p.position == "upper left"
    squeezed = place("notice board", SIZE, BOARD, ObstacleIndex(), frame=(495.0, 495.0, 505.0, 505.0))
    assert squeezed.lines and squeezed.ring == 0, "no seat fits the frame at all: the caption still goes down"


def test_a_caption_wraps_at_a_seat_before_moving_off_it() -> None:
    """The GM's wrap rule: at a seat, one line first, then two - so a post that blocks the long one-liner's tail keeps
    the caption at upper right on two lines instead of sending it round the board."""
    post = Obstacle(tuple(rect(548.0, 490.0, 4.0, 4.0)), WEIGHT_OBSTACLE)
    p = place("notice board", SIZE, BOARD, ObstacleIndex([post]))
    assert (p.position, p.lines) == ("upper right", ("notice", "board"))


def test_a_rotated_subject_turns_its_caption_upright() -> None:
    """A board at 126 degrees carries its caption at -54: the same line, read the right way up; "upper right" is in
    the board's own turned frame."""
    tilted = Subject("point", tuple(rect(500.0, 500.0, 6.0, 2.5, 126.0)), angle=126.0)
    p = place("notice board", SIZE, tilted, ObstacleIndex())
    assert p.angle == pytest.approx(-54.0)
    assert _gap(p, tilted) == pytest.approx(PREFERRED_OFFSET_EM * SIZE, abs=1e-6)


def test_a_line_caption_runs_along_the_line_above_it() -> None:
    """A road's name follows the road, above it rather than below, near where it was asked for."""
    road = Subject("line", ((100.0, 300.0), (700.0, 300.0)), half_width=6.0, hint=(250.0, 320.0))
    p = place("Imperial Road", 12.0, road, ObstacleIndex())
    assert (p.position, p.angle, p.leader) == ("above", 0.0, None)
    assert max(q[1] for q in p.block) == pytest.approx(300.0 - 6.0 - 6.0)
    assert abs(centroid(list(p.block))[0] - 250.0) < 1.0
    blocked = ObstacleIndex([Obstacle(tuple(rect(400.0, 270.0, 400.0, 20.0)), WEIGHT_OBSTACLE)])
    assert place("Imperial Road", 12.0, road, blocked).position == "below"


def test_a_line_caption_without_a_hint_starts_at_the_middle_and_takes_a_leader_when_pushed_out() -> None:
    road = Subject("line", ((100.0, 300.0), (250.0, 300.0), (400.0, 300.0)), half_width=6.0)
    bands = [Obstacle(tuple(rect(250.0, 284.0, 400.0, 8.0)), WEIGHT_OBSTACLE), Obstacle(tuple(rect(250.0, 316.0, 400.0, 8.0)), WEIGHT_OBSTACLE)]
    near = ObstacleIndex(bands)
    p = place("Imperial Road", 12.0, road, near)
    assert p.ring > 0 and p.leader is not None


def test_an_area_caption_lies_inside_the_area_over_its_centroid() -> None:
    """A building's name on a plan lies inside the building, over its middle when that is free; the building's own
    outline is not an obstacle to its own name."""
    hall = tuple(rect(300.0, 300.0, 60.0, 25.0))
    idx = ObstacleIndex([Obstacle(hall, WEIGHT_OBSTACLE)])
    p = place("kitchen", 10.0, Subject("area", hall), idx)
    assert (p.position, p.rank, p.leader) == ("inside", 0, None)
    assert all(inside(q[0], q[1], list(hall)) for q in p.block)
    post = Obstacle(tuple(rect(300.0, 300.0, 6.0, 6.0)), WEIGHT_OBSTACLE, group=None)
    moved = place("kitchen", 10.0, Subject("area", hall), ObstacleIndex([post]))
    assert moved.rank > 0, "a post at the middle moves the name to the nearest free interior seat"
    tiny = tuple(rect(0.0, 0.0, 5.0, 5.0))
    spill = place("fire-water tubs", 10.0, Subject("area", tiny), ObstacleIndex())
    assert spill.cost >= WEIGHT_OBSTACLE, "a name that cannot fit inside still goes down, charged for spilling"


def test_a_caption_may_lie_on_its_own_group_but_a_civic_one_never_on_another_civic_building() -> None:
    """FR-014, the GM's 2026-07-21 rule: a temple's caption may lie on a temple; a ministry's name may not lie on the
    next ministry (research/presentation 070)."""
    temple = Obstacle(tuple(rect(560.0, 480.0, 40.0, 15.0)), WEIGHT_OBSTACLE, group="flophouse")
    assert place("flophouse", SIZE, BOARD, ObstacleIndex([temple])).position == "upper right"
    assert place("notice board", SIZE, BOARD, ObstacleIndex([temple])).position != "upper right"
    works = Obstacle(tuple(rect(560.0, 480.0, 40.0, 15.0)), WEIGHT_OBSTACLE, group="ministry", named=True)
    assert "ministry" in CIVIC_GROUPS
    justice = Subject("point", BOARD.poly, civic=True)  # the caption's SUBJECT is a named ministry
    assert place("Ministry of Justice", SIZE, justice, ObstacleIndex([works])).position != "upper right"
    shrine = Obstacle(tuple(rect(560.0, 480.0, 40.0, 15.0)), WEIGHT_OBSTACLE, group="temple")
    assert place("temple", SIZE, BOARD, ObstacleIndex([shrine])).position == "upper right", "an UNNAMED temple is waivable"
    named = Obstacle(tuple(rect(560.0, 480.0, 40.0, 15.0)), WEIGHT_OBSTACLE, group="temple", named=True)
    benten = Subject("point", BOARD.poly, civic=True)
    assert place("Temple of Benten", SIZE, benten, ObstacleIndex([named])).position != "upper right", "one named temple's name off another"
    assert place("temple neighborhood", SIZE, BOARD, ObstacleIndex([named])).position == "upper right", (
        "a district caption names no civic building, so it may lie on its district's named temple (answer 070)"
    )
    assert place("flophouse row", SIZE, BOARD, ObstacleIndex([Obstacle(named.poly, WEIGHT_OBSTACLE, "flophouse", named=True)])).position == "upper right", (
        "named but not civic: waived by its group like any other"
    )


def test_an_unknown_subject_kind_is_refused() -> None:
    with pytest.raises(ValueError, match="point, a line or an area"):
        place("x", SIZE, Subject("blob", BOARD.poly), ObstacleIndex())


def test_the_positions_rings_and_upright_rule() -> None:
    assert [n for n, _x, _y in POSITIONS][:4] == ["upper right", "upper left", "lower right", "lower left"]
    rs = rings(SIZE)
    assert rs[0] == PREFERRED_OFFSET_EM * SIZE and rs[-1] == pytest.approx(REACH_EM * SIZE)
    assert upright(126.0) == pytest.approx(-54.0) and upright(-100.0) == pytest.approx(80.0) and upright(90.0) == 90.0
    assert upright(270.0) == pytest.approx(90.0) and upright(-90.0) == pytest.approx(90.0)
    assert block_half(["notice board"], 8.0) == pytest.approx((26.4, 4.2))


def test_cut_and_layouts() -> None:
    assert cut(["Shrine", "of", "Benten"], 2) in (["Shrine of", "Benten"], ["Shrine", "of Benten"])
    assert cut(["a", "of", "b"], 2) is None, "every two-line cut would strand a short word"
    assert layouts("notice board") == [["notice board"], ["notice", "board"]]
    assert layouts("well") == [["well"]]
    assert len(layouts("Temple of the Moon")) == 3


def test_the_index_sees_what_is_added_to_it() -> None:
    """Built once, then each placed caption added, so the next caption sees it (FR-009)."""
    idx = ObstacleIndex()
    first = place("notice board", SIZE, BOARD, idx)
    idx.add(Obstacle(first.block, WEIGHT_OBSTACLE))
    second = place("notice board", SIZE, BOARD, idx)
    assert second.position != first.position
    assert idx.cost(list(first.block), 1.0) == WEIGHT_OBSTACLE
    assert idx.cost(list(first.block), 1.0, subject=list(first.block)) == 0.0, "a caption's own subject is waived"
    assert ObstacleIndex([Obstacle(first.block, 0.0)]).cost(list(first.block), 1.0) == 0.0, "weight 0 is free space"


def test_geometry_edges() -> None:
    sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert area_centroid(sq) == pytest.approx((5.0, 5.0))
    assert area_centroid([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]) == pytest.approx((1.0, 1.0)), "degenerate: the vertex mean"
    inner = [(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)]
    assert poly_gap(inner, sq) == 0.0 and poly_gap(sq, inner) == 0.0
    crossing = [(5.0, -5.0), (6.0, -5.0), (6.0, 5.0), (5.0, 5.0)]
    assert poly_gap(crossing, sq) == 0.0
    far = [(20.0, 0.0), (30.0, 0.0), (30.0, 10.0), (20.0, 10.0)]
    assert poly_gap(far, sq) == pytest.approx(10.0) and poly_gap(sq, far) == pytest.approx(10.0)
    a, b = nearest_points(far, [(0.0, 5.0), (15.0, 5.0)], closed=False)
    assert math.dist(a, b) == pytest.approx(5.0)
    assert poly_seg_gap(sq, (5.0, 5.0), (50.0, 50.0)) == 0.0
    assert poly_seg_gap(sq, (-5.0, 5.0), (15.0, 5.0)) == 0.0
    assert poly_seg_gap(sq, (20.0, 0.0), (20.0, 10.0)) == pytest.approx(10.0)
    assert segments_cross((0.0, 0.0), (10.0, 0.0), (5.0, 0.0), (5.0, 5.0)), "touching counts"
