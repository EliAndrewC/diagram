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


def test_the_first_position_is_directly_above_at_the_preferred_offset() -> None:
    """Scenario 1: clear ground, so the caption takes the first position - directly above the board (the GM's deviation
    from the standard's corners-first order, feature 289) - the preferred gap off the board's drawn edge, no leader."""
    p = place("notice board", SIZE, BOARD, ObstacleIndex())
    assert (p.position, p.ring, p.lines, p.leader) == ("above", 0, ("notice board",), None)
    assert _gap(p, BOARD) == pytest.approx(PREFERRED_OFFSET_EM * SIZE, abs=1e-6)
    assert centroid(list(p.block))[0] == pytest.approx(500.0) and max(q[1] for q in p.block) < 497.5, "centered, above"


# A post in the seat directly above the board at the preferred gap, clear of every other seat
ABOVE = rect(500.0, 489.0, 4.0, 2.0)


def test_a_blocked_position_falls_to_the_next_ranked_one() -> None:
    """Scenario 2 and feature 290's SC-001: the user-tested order (PerceptPPO) - above, below, right, upper right, lower
    right, left, upper left, lower left - each seat, once taken by a post, sending the caption to the next, every one
    at the preferred gap with no leader."""
    order = ["above", "below", "right", "upper right", "lower right", "left", "upper left", "lower left"]
    posts: list[Obstacle] = []
    for want in order:
        p = place("notice board", SIZE, BOARD, ObstacleIndex(posts))
        assert (p.position, p.ring, p.leader) == (want, 0, None), want
        cx, cy = centroid(list(p.block))
        posts.append(Obstacle(tuple(rect(cx, cy, 1.0, 1.0)), WEIGHT_OBSTACLE))


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


def test_a_leader_given_what_it_may_not_cross_goes_around_it() -> None:
    """Feature 283: a hand sheet hands the placer the captions and small glyphs a leader may not pass over or end
    against; the seat whose leader would cross one is passed over for a seat whose leader is clear. The engine passes
    none, and places as before."""
    ring0 = [rect(500.0, 500.0, 6.0 + 5.0, 2.5 + 5.0)]
    walls = ObstacleIndex([Obstacle(tuple(q), WEIGHT_OBSTACLE) for q in _collar(ring0[0], 4.5)])
    first = place("notice board", SIZE, BOARD, walls)
    a, b = first.leader
    across = rect((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 3.0, 3.0)  # a caption lying on that leader
    again = place("notice board", SIZE, BOARD, walls, leader_index=ObstacleIndex([Obstacle(tuple(across), WEIGHT_OBSTACLE)]))
    assert again.leader is not None and again.block != first.block and again.cost == 0.0
    assert not any(segments_cross(again.leader[0], again.leader[1], p, q) for p, q in zip(across, across[1:] + across[:1], strict=False))
    assert place("notice board", SIZE, BOARD, walls, leader_index=ObstacleIndex()) == first, "nothing to avoid, nothing moves"


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
    assert p.cost == WEIGHT_WAY and p.position == "right" and p.ring == 0


def test_the_frame_is_never_left() -> None:
    """A clipped caption cannot be read: with the frame's right edge at the board, the right-hand seats are gone."""
    p = place("notice board", SIZE, BOARD, ObstacleIndex(), frame=(0.0, 0.0, 510.0, 1000.0))
    assert p.position == "left", "above and below run past the frame's edge too"
    squeezed = place("notice board", SIZE, BOARD, ObstacleIndex(), frame=(495.0, 495.0, 505.0, 505.0))
    assert squeezed.lines and squeezed.ring == 0, "no seat fits the frame at all: the caption still goes down"


def test_a_caption_wraps_at_a_seat_before_moving_off_it() -> None:
    """The GM's wrap rule: at a seat, one line first, then two - so a post that blocks the long one-liner's tail keeps
    the caption above the board on two lines instead of sending it round the board."""
    post = Obstacle(tuple(rect(522.0, 490.0, 2.0, 2.0)), WEIGHT_OBSTACLE)
    p = place("notice board", SIZE, BOARD, ObstacleIndex([post]))
    assert (p.position, p.lines) == ("above", ("notice", "board"))


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
    temple = Obstacle(tuple(ABOVE), WEIGHT_OBSTACLE, group="flophouse")
    assert place("flophouse", SIZE, BOARD, ObstacleIndex([temple])).position == "above"
    assert place("notice board", SIZE, BOARD, ObstacleIndex([temple])).position != "above"
    works = Obstacle(tuple(ABOVE), WEIGHT_OBSTACLE, group="ministry", named=True)
    assert "ministry" in CIVIC_GROUPS
    justice = Subject("point", BOARD.poly, civic=True)  # the caption's SUBJECT is a named ministry
    assert place("Ministry of Justice", SIZE, justice, ObstacleIndex([works])).position != "above"
    shrine = Obstacle(tuple(ABOVE), WEIGHT_OBSTACLE, group="temple")
    assert place("temple", SIZE, BOARD, ObstacleIndex([shrine])).position == "above", "an UNNAMED temple is waivable"
    named = Obstacle(tuple(ABOVE), WEIGHT_OBSTACLE, group="temple", named=True)
    benten = Subject("point", BOARD.poly, civic=True)
    assert place("Temple of Benten", SIZE, benten, ObstacleIndex([named])).position != "above", "one named temple's name off another"
    assert place("temple neighborhood", SIZE, BOARD, ObstacleIndex([named])).position == "above", (
        "a district caption names no civic building, so it may lie on its district's named temple (answer 070)"
    )
    assert place("flophouse row", SIZE, BOARD, ObstacleIndex([Obstacle(named.poly, WEIGHT_OBSTACLE, "flophouse", named=True)])).position == "above", (
        "named but not civic: waived by its group like any other"
    )


def test_an_unknown_subject_kind_is_refused() -> None:
    with pytest.raises(ValueError, match="point, a line or an area"):
        place("x", SIZE, Subject("blob", BOARD.poly), ObstacleIndex())


def test_the_positions_rings_and_upright_rule() -> None:
    assert [n for n, _x, _y in POSITIONS] == [  # PerceptPPO, Bobák, Čmolík and Čadík 2024 (feature 290)
        "above",
        "below",
        "right",
        "upper right",
        "lower right",
        "left",
        "upper left",
        "lower left",
    ]
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


def test_a_name_over_a_smaller_gloss_is_measured_line_by_line() -> None:
    """Feature 286: measured at the head's size, a 12 px name over two 7 px lines was too tall for any seat."""
    from l7r.diagram.labels.placer import sized_half

    head_only = sized_half(["bath", "xxxxx", "xxxxx"], 12.0)
    sized = sized_half(["bath", "xxxxx", "xxxxx"], 12.0, line_sizes=[12.0, 7.0, 7.0])
    assert sized[0] == head_only[0] and sized[1] < head_only[1]
    assert sized_half(["bath"], 12.0, line_sizes=None) == sized_half(["bath"], 12.0)


def test_the_fallback_finds_a_free_seat_the_standard_misses() -> None:
    """Feature 286: when no ranked seat is free the fallback searches on - round a point, sliding along its sides; inside
    an area, over its whole extent - before it settles for the least cost."""
    board = Subject("point", tuple(rect(500.0, 500.0, 11.0, 7.5)))
    # every ranked seat covered, one gap left along the top edge, off the ranked positions
    walls = [Obstacle(tuple(q), WEIGHT_OBSTACLE) for q in _collar(rect(500.0, 500.0, 11.0, 7.5), 4.5)]
    cover = [rect(500.0, 470.0, 200.0, 12.0)]  # the band above, but a notch cut out left of center
    notch = ObstacleIndex(walls + [Obstacle(tuple(rect(440.0, 485.0, 30.0, 6.0)), WEIGHT_OBSTACLE), Obstacle(tuple(rect(560.0, 485.0, 30.0, 6.0)), WEIGHT_OBSTACLE)])
    p = place("notice board", SIZE, board, notch)
    assert p.cost == 0.0 or p.cost <= min(Obstacle(tuple(cover[0]), WEIGHT_OBSTACLE).weight, WEIGHT_OBSTACLE)
    # a large area whose only free ground lies far from its centroid, beyond the standard's nearest 400 seats
    court = Subject("area", tuple(rect(1000.0, 1000.0, 800.0, 200.0)))  # x 200-1800
    busy = ObstacleIndex([Obstacle(tuple(rect(880.0, 1000.0, 720.0, 260.0)), WEIGHT_OBSTACLE)])  # x 160-1600, past the court's edges
    q = place("forecourt", SIZE, court, busy)
    assert q.cost == 0.0 and q.x > 1600.0, "found at the court's free east end"


def test_the_least_cost_seat_is_nudged_into_a_band_between_grid_points() -> None:
    """Feature 286: a free band exactly as tall as the caption lies between any grid's points; the nudge finds it."""
    from l7r.diagram.labels.placer import _Cand, nudge

    sub = Subject("area", tuple(rect(0.0, 0.0, 100.0, 100.0)))
    index = ObstacleIndex([Obstacle(tuple(rect(0.0, -20.0, 120.0, 10.0)), WEIGHT_OBSTACLE)])  # y -30 to -10, past the area's sides
    c = _Cand(0, 0, "inside", (0.0, -8.0), 0.0, ("x",), (4.0, 3.0), 9.0)
    block = rect(0.0, -8.0, 4.0, 3.0)
    cost, moved, _ = nudge(1000.0, c, block, sub, index, 0.5, list(sub.poly), "x", None, None)  # a real clearance: an overlap reads a gap of 0
    assert cost == 0.0 and moved.center[1] > -8.0


def test_the_index_skips_by_boxes_and_measures_level_rectangles_by_them() -> None:
    """Feature 286: the outline test was nine tenths of placing a hand sheet's captions. An obstacle whose box is clear
    of the block's is clear; two level rectangles are their boxes. Both agree with the outline test they stand for."""
    from l7r.diagram.labels.geom import poly_gap
    from l7r.diagram.labels.obstacles import level_rect

    wall = Obstacle(tuple(rect(100.0, 0.0, 5.0, 50.0)), 1000.0)
    turned = Obstacle(tuple(rect(0.0, 100.0, 20.0, 5.0, 30.0)), 1000.0)
    index = ObstacleIndex([wall, turned])
    for x in (80.0, 90.0, 92.5, 93.0, 96.0, 140.0):
        block = rect(x, 0.0, 4.0, 3.0)
        want = sum(o.weight for o in (wall, turned) if poly_gap(block, list(o.poly)) < 3.0 - 1e-6)
        assert index.cost(block, 3.0) == want, x
    near_turned = rect(0.0, 90.0, 4.0, 3.0)
    assert index.cost(near_turned, 3.0) == (1000.0 if poly_gap(near_turned, list(turned.poly)) < 3.0 else 0.0)
    assert level_rect(rect(0.0, 0.0, 4.0, 3.0)) and not level_rect(turned.poly) and not level_rect(((0.0, 0.0), (1.0, 1.0), (2.0, 0.0)))


def test_an_obstacle_keeps_its_own_gap_when_larger() -> None:
    """Feature 286: a placed caption keeps its own clearance from the next one - a small name 4 px from a large one was
    clear by its own 3 px gap and inside the large one's 5.5."""
    far = rect(200.0, 0.0, 10.0, 5.0)
    big = Obstacle(tuple(rect(0.0, 0.0, 20.0, 5.0)), 1000.0, keep=5.5)
    block = rect(28.0, 0.0, 4.0, 3.0)  # 4 px from the big one's right edge
    assert ObstacleIndex([big]).cost(block, 3.0) == 1000.0, "inside its keep"
    assert ObstacleIndex([Obstacle(big.poly, 1000.0)]).cost(block, 3.0) == 0.0, "clear by the caption's own gap"
    assert ObstacleIndex([big, Obstacle(tuple(far), 1000.0)]).cost(rect(31.0, 0.0, 4.0, 3.0), 3.0) == 0.0, "past both"


def test_the_nudge_stays_in_the_frame_and_a_line_has_no_fallback() -> None:
    """Feature 286: a nudge never moves a caption off the picture; a line subject's stations already walk its length, so
    the fallback adds no seat for it."""
    from l7r.diagram.labels.placer import _Cand, _extended_cands, nudge

    sub = Subject("point", tuple(rect(0.0, 0.0, 5.0, 5.0)))
    index = ObstacleIndex([Obstacle(tuple(rect(20.0, 0.0, 6.0, 6.0)), WEIGHT_OBSTACLE)])
    c = _Cand(0, 0, "right", (20.0, 0.0), 0.0, ("x",), (4.0, 3.0), 9.0)
    frame = (16.0, -3.0, 24.0, 3.0)  # exactly the block: every move leaves the picture
    cost, moved, _ = nudge(1000.0, c, rect(20.0, 0.0, 4.0, 3.0), sub, index, 0.5, list(sub.poly), "x", frame, None)
    assert cost == 1000.0 and moved.center == (20.0, 0.0)
    line = Subject("line", ((0.0, 0.0), (100.0, 0.0)), half_width=2.0)
    assert list(_extended_cands("lane", 9.0, line)) == []
