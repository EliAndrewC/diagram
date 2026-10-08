"""Feature 287: the one placer's guarantees, each on constructed inputs that include the violating case - the free seat
or none (`strict`), the association term (labels L6), the subject's own angle (L8), the hug (L10), the ways a caption
clears (L5), the crowns (L7) and the key a caption with no seat goes in (D10)."""

from __future__ import annotations

import math

import pytest

from l7r.diagram.labels import Obstacle, ObstacleIndex, Subject, Way, caption_clears_ways, circle_obstacle, hug_gap, place, referent_box, upright
from l7r.diagram.labels.geom import poly_gap, rect
from l7r.diagram.labels.obstacles import circle_gap
from l7r.diagram.labels.placer import HUG_RING, _Cand, leader_cost, outer_rings, record_box, rings
from l7r.diagram.labels.standard import CLEAR_EM, HUG_PX, PREFERRED_OFFSET_EM, REACH_EM, WEIGHT_OBSTACLE

SIZE = 8.0
BOARD = Subject("point", tuple(rect(500.0, 500.0, 6.0, 2.5)))


def test_strict_takes_a_free_seat_or_none() -> None:
    """`place(strict=True)` returns the free seat the lax placer would take, and None where the lax placer would settle
    for a covered one - the board's siter and the generated sheets choose the subject or the program instead."""
    assert place("notice board", SIZE, BOARD, ObstacleIndex(), strict=True) == place("notice board", SIZE, BOARD, ObstacleIndex())
    boxed = ObstacleIndex([Obstacle(tuple(rect(500.0, 500.0, 900.0, 900.0)), WEIGHT_OBSTACLE)])
    assert place("notice board", SIZE, BOARD, boxed, strict=True) is None
    assert place("notice board", SIZE, BOARD, boxed).cost > 0.0, "lax: the seat covering the least (0242), never None"


def test_max_ring_keeps_only_the_seats_beside_the_subject() -> None:
    """`max_ring=0`: only seats at the preferred offset, with no leader - the board's caption (labels L4)."""
    collar = [Obstacle(tuple(q), WEIGHT_OBSTACLE) for q in (rect(500.0, 488.0, 60.0, 4.0), rect(500.0, 512.0, 60.0, 4.0), rect(470.0, 500.0, 4.0, 20.0), rect(530.0, 500.0, 4.0, 20.0))]
    index = ObstacleIndex(collar)
    free = place("notice board", SIZE, BOARD, index, strict=True)
    assert free is not None and free.ring > 0 and free.leader is not None, "a leader seat past the collar is free"
    assert place("notice board", SIZE, BOARD, index, strict=True, max_ring=0) is None


def test_a_neighbor_one_offset_off_is_counted_by_the_association() -> None:
    """Labels L6: a caption standing as near a neighbor as its own subject is not plainly its subject's. An obstacle
    exactly the preferred offset off the ring-0 block - the tie `>` forbids - is counted, where without the association
    term it was clear (a seat exactly one offset off is clear, feature 266 plan P6)."""
    first = place("notice board", SIZE, BOARD, ObstacleIndex())
    assert first.position == "above" and first.ring == 0
    x0 = max(q[0] for q in first.block)
    gap = CLEAR_EM * SIZE
    post = Obstacle(tuple(rect(x0 + gap + 3.0, sum(q[1] for q in first.block) / 4, 3.0, 3.0)), WEIGHT_OBSTACLE)
    index = ObstacleIndex([post])
    own = poly_gap(list(first.block), list(BOARD.poly))
    assert index.cost(list(first.block), gap) == 0.0, "clear by the offset alone"
    assert index.cost(list(first.block), gap, list(BOARD.poly), own_gap=own) == WEIGHT_OBSTACLE, "as near as its own board: counted"
    p = place("notice board", SIZE, BOARD, index, strict=True)
    assert p is not None and p.block != first.block, "the tied seat is refused"
    others = [poly_gap(list(p.block), list(o.poly)) for o in index.obstacles]
    assert poly_gap(list(p.block), list(BOARD.poly)) < min(others), "nearer its own board than any neighbor"


def test_stands_nearest_is_strict_and_asks_every_neighbor_but_the_subject() -> None:
    """Labels L6, the association as measured (`stands_nearest`, the one predicate the board's siter and the pool test
    share): a yard just nearer than the board claims the caption, and so does one at a tie; one just farther does not. A
    crown is measured as its disc, a neighbor of a group the caption names still counts, and ink inside the subject is
    the subject's."""
    from l7r.diagram.labels.obstacles import stands_nearest

    first = place("notice board", SIZE, BOARD, ObstacleIndex())
    block = list(first.block)
    own = poly_gap(block, list(BOARD.poly))
    top = min(q[1] for q in block)

    def yard(gap: float) -> ObstacleIndex:
        return ObstacleIndex([Obstacle(tuple(rect(500.0, top - gap - 10.0, 20.0, 10.0)), WEIGHT_OBSTACLE)])

    assert not stands_nearest(block, list(BOARD.poly), yard(own - 0.048)), "a yard just nearer than the board claims it"
    assert not stands_nearest(block, list(BOARD.poly), yard(own)), "a tie is the neighbor's"
    assert stands_nearest(block, list(BOARD.poly), yard(own + 0.01))
    assert stands_nearest(block, list(BOARD.poly), yard(own + 0.01 + 50.0)) and stands_nearest(block, list(BOARD.poly), ObstacleIndex())
    crown = ObstacleIndex([circle_obstacle(500.0, top - own - 20.0 + 0.5, 20.0, WEIGHT_OBSTACLE, "board")])
    assert not stands_nearest(block, list(BOARD.poly), crown), "a disc, as a disc; a group the caption names still counts"
    inner = ObstacleIndex([Obstacle(tuple(rect(500.0, 500.0, 1.0, 1.0)), WEIGHT_OBSTACLE), Obstacle(BOARD.poly, WEIGHT_OBSTACLE)])
    assert stands_nearest(block, list(BOARD.poly), inner), "ink inside the subject, and its own record, are the subject"


def test_a_free_seat_accept_refuses_is_passed_over() -> None:
    """`accept` is asked of every free seat, and a refused one is passed over for the next; where it refuses every seat,
    a strict search has no answer (feature 287: the board's siter proves the association on the record this way)."""
    first = place("notice board", SIZE, BOARD, ObstacleIndex(), strict=True, max_ring=0)
    assert first is not None
    other = place("notice board", SIZE, BOARD, ObstacleIndex(), strict=True, max_ring=0, accept=lambda p: p.position != first.position)
    assert other is not None and other.position != first.position and other.cost == 0.0 and other.ring == 0
    assert place("notice board", SIZE, BOARD, ObstacleIndex(), strict=True, max_ring=0, accept=lambda p: False) is None


def test_the_association_waives_ink_inside_the_subject() -> None:
    """The association is about OTHER features: ink inside the subject (a partition drawn along its edge) stands no
    nearer than the subject itself and is not what the rule counts."""
    inside = Obstacle(tuple(rect(505.0, 498.0, 0.5, 0.5)), WEIGHT_OBSTACLE, inner=True)
    first = place("notice board", SIZE, BOARD, ObstacleIndex())
    own = poly_gap(list(first.block), list(BOARD.poly))
    assert ObstacleIndex([inside]).cost(list(first.block), CLEAR_EM * SIZE, list(BOARD.poly), own_gap=own) == 0.0


def test_a_caption_is_drawn_at_its_subjects_own_angle_through_every_fallback() -> None:
    """Labels L8: a 126-degree board whose preferred seats are all taken - the fallback slides and the nudge run - is
    still captioned at upright(126), the one angle every candidate carries."""
    board = Subject("point", tuple(rect(500.0, 500.0, 6.0, 2.5, 126.0)), angle=126.0)
    near = [Obstacle(tuple(rect(500.0 + 16.0 * math.cos(math.radians(a)), 500.0 + 16.0 * math.sin(math.radians(a)), 7.0, 7.0)), WEIGHT_OBSTACLE) for a in range(0, 360, 30)]
    p = place("notice board", SIZE, board, ObstacleIndex(near))
    assert p.angle == pytest.approx(upright(126.0))
    far = place("notice board", SIZE, board, ObstacleIndex([Obstacle(tuple(rect(500.0, 500.0, 900.0, 900.0)), WEIGHT_OBSTACLE, soft=True)]))
    assert far.cost > 0 and far.angle == pytest.approx(upright(126.0)), "the least-cost seat, nudged, keeps it too"


@pytest.mark.parametrize("size", [7.0, 8.0, 9.0, 15.0, 30.0])
def test_no_seat_stands_past_the_hug(size: float) -> None:
    """Labels L10: a point subject boxed in so that only its farthest seats are free - at every caption size, the seat
    taken stands within `HUG_PX` of what it names, box to box (`hug_gap`, the gate's own measure)."""
    board = Subject("point", tuple(rect(500.0, 500.0, 6.0, 2.5)))
    reach = min((PREFERRED_OFFSET_EM + 0.5 * 30) * size, HUG_RING) - size
    walls = ObstacleIndex([Obstacle(tuple(rect(500.0, 500.0, 6.0 + reach, 2.5 + reach)), WEIGHT_OBSTACLE)])
    p = place("notice board", size, board, walls)
    assert hug_gap(p.block, referent_box(board, p.block)) <= HUG_PX
    assert max(rings(size)) <= HUG_RING and all(g <= HUG_RING for _k, g in outer_rings(size))
    assert rings(300.0) == [HUG_RING], "a caption too large for any ring past the first keeps the first, capped"


def test_the_leader_rings_reach_past_the_standard_to_the_hug() -> None:
    """Feature 287, D10: with every seat in the standard's reach covered, a free seat past it - out to the hug - is taken
    with a leader before the key."""
    reach = REACH_EM * SIZE
    inner = Obstacle(tuple(rect(500.0, 500.0, 6.0 + reach + 2.0, 2.5 + reach + 2.0)), WEIGHT_OBSTACLE)
    p = place("notice board", SIZE, BOARD, ObstacleIndex([inner]))
    assert p.cost == 0.0 and p.ring >= len(rings(SIZE)) and p.leader is not None
    assert hug_gap(p.block, referent_box(BOARD, p.block)) <= HUG_PX
    assert list(outer_rings(SIZE)) and outer_rings(SIZE)[0][0] == len(rings(SIZE))


def test_a_line_caption_takes_the_leader_rings_too_and_an_area_does_not() -> None:
    lane = Subject("line", ((0.0, 0.0), (400.0, 0.0)), half_width=2.0, hint=(200.0, 0.0))
    band = SIZE * (PREFERRED_OFFSET_EM + 0.5 * 20)
    cover = ObstacleIndex([Obstacle(tuple(rect(200.0, 0.0, 300.0, band)), WEIGHT_OBSTACLE)])
    p = place("lane", SIZE, lane, cover)
    assert p.leader is not None and p.ring >= len(rings(SIZE))
    court = Subject("area", tuple(rect(0.0, 0.0, 30.0, 10.0)))
    q = place("a court far too long for its ground", SIZE, court, ObstacleIndex([Obstacle(tuple(rect(0.0, 0.0, 5.0, 5.0)), WEIGHT_OBSTACLE)]))
    assert q.leader is None and q.position != "key", "an area's name lies in it, where it covers the least - no leader, no key"


def test_a_way_crossed_between_the_blocks_corners_is_seen() -> None:
    """Labels L5: the way term measures segment against polygon, so a curved tread whose arc crosses a caption's long
    edge between its corners - every corner and the center clear - is a crossing, and a strict seat refuses it."""
    block = rect(100.0, 100.0, 30.0, 5.0)
    arc = Way(tuple((100.0 + 40.0 * math.cos(math.radians(a)), 145.0 - 40.0 * math.sin(math.radians(a))) for a in range(30, 151, 10)), 1.5)
    corners_clear = all(min(math.dist(c, q) for q in arc.pts) > 3.5 for c in block)
    assert corners_clear, "the arc stays clear of every corner"
    assert not caption_clears_ways(block, [arc])
    assert ObstacleIndex(ways=[arc]).cost(block, 4.0) > 0.0
    assert caption_clears_ways(rect(100.0, 30.0, 30.0, 5.0), [arc])
    lane = Subject("point", tuple(rect(100.0, 100.0, 2.0, 2.0)))
    p = place("x" * 12, SIZE, lane, ObstacleIndex(ways=[arc]), strict=True, max_ring=0)
    assert p is None or caption_clears_ways(p.block, [arc])


def test_a_crown_is_a_disc_and_a_grove_caption_may_lie_on_it() -> None:
    """Labels L7: a tree crown is measured as a disc, not its box - a block by the box's corner is clear of it - and a
    caption naming trees may lie on its own kind."""
    crown = circle_obstacle(0.0, 0.0, 10.0, WEIGHT_OBSTACLE, "grove")
    corner = rect(10.0, 10.0, 2.0, 2.0)  # inside the crown's box, outside its disc
    assert circle_gap(corner, crown.circle) > 0.0
    assert ObstacleIndex([crown]).cost(corner, 0.5) == 0.0
    on = rect(0.0, 0.0, 3.0, 3.0)
    assert circle_gap(on, crown.circle) == 0.0 and ObstacleIndex([crown]).cost(on, 0.5) == WEIGHT_OBSTACLE
    assert ObstacleIndex([crown]).cost(on, 0.5, text="village grove") == 0.0
    edge = rect(0.0, 13.0, 3.0, 2.0)
    assert circle_gap(edge, crown.circle) == pytest.approx(1.0)


def test_a_leader_through_hard_ink_is_an_overlap_and_through_soft_ink_is_not() -> None:
    board = BOARD
    c = _Cand(3, 0, "upper right", (540.0, 470.0), 0.0, ("x",), (4.0, 3.0), SIZE)
    block = rect(540.0, 470.0, 4.0, 3.0)
    mid = rect(522.0, 486.0, 3.0, 3.0)
    hard = ObstacleIndex([Obstacle(tuple(mid), WEIGHT_OBSTACLE)])
    soft = ObstacleIndex([Obstacle(tuple(mid), WEIGHT_OBSTACLE, soft=True)])
    assert leader_cost(c, block, board, hard, 0.5, None, "x") == WEIGHT_OBSTACLE
    assert hard.score(rect(522.0, 486.0, 1.0, 1.0), 0.5) == (WEIGHT_OBSTACLE, True)
    assert soft.score(rect(522.0, 486.0, 1.0, 1.0), 0.5) == (WEIGHT_OBSTACLE, False)
    assert ObstacleIndex(ways=[Way(((0.0, 0.0), (10.0, 0.0)), 1.0, soft=True)]).score(rect(5.0, 0.0, 1.0, 1.0), 0.5) == (500.0, False)


def test_the_record_box_is_the_block_unturned() -> None:
    block = rect(10.0, 20.0, 5.0, 2.0, 30.0)
    x0, y0, x1, y1 = record_box(block)
    assert (x1 - x0, y1 - y0) == (pytest.approx(10.0), pytest.approx(4.0)) and (x0 + x1) / 2 == pytest.approx(10.0)


def test_the_fallbacks_run_out_to_the_least_cover_or_to_none() -> None:
    """Every seat off the picture: strict has nothing to offer; a line with every seat covered takes its leader rings to
    the end and goes down where it covers the least (0242; the key retired, 0241); an area's referent is its own box."""
    assert place("notice board", SIZE, BOARD, ObstacleIndex(), frame=(495.0, 495.0, 505.0, 505.0), strict=True) is None
    lane = Subject("line", ((0.0, 0.0), (400.0, 0.0)), half_width=2.0)
    assert place("lane", SIZE, lane, ObstacleIndex([Obstacle(tuple(rect(200.0, 0.0, 900.0, 900.0)), WEIGHT_OBSTACLE)])).cost > 0.0
    court = Subject("area", tuple(rect(50.0, 60.0, 10.0, 20.0)))
    assert referent_box(court, court.poly) == (40.0, 40.0, 60.0, 80.0)
