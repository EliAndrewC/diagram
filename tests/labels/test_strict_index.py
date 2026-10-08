"""Feature 287 wave 5: the strict search indexed, exact (the notice board's 216 s siting under one wide canopy).

`ObstacleIndex.blocked` refuses a strict seat without measuring it where something holds it past a nudge's reach; the
way term measures each segment once and clears a segment by the boxes first; `nearest_points` skips its crossing tests
for outlines whose boxes stand apart. Each is exact: these tests hold the indexed answer to the scan's on constructed
scenes that include the seats the index refuses."""

from __future__ import annotations

import math
import random

from l7r.diagram.labels import Obstacle, ObstacleIndex, Subject, Way, circle_obstacle, place
from l7r.diagram.labels.geom import nearest_points, poly_gap, poly_seg_gap, rect, seg_closest
from l7r.diagram.labels.placer import NUDGE_PX, NUDGE_REACH
from l7r.diagram.labels.standard import WAY_NOTCH, WEIGHT_OBSTACLE, WEIGHT_WAY

SIZE = 8.0


class _Unindexed(ObstacleIndex):
    """The scan: an index that refuses no seat unmeasured, so a strict search measures and nudges as it did before."""

    def blocked(self, block, clear, slack, subject=None, text="", civic=False):  # noqa: ANN001, ANN201
        return False


def _scene(rng: random.Random, cls: type[ObstacleIndex] = ObstacleIndex) -> ObstacleIndex:
    obs: list[Obstacle] = []
    for _ in range(rng.randint(0, 14)):
        if rng.random() < 0.5:
            obs.append(circle_obstacle(rng.uniform(0, 200), rng.uniform(0, 200), rng.uniform(2, 70), WEIGHT_OBSTACLE, rng.choice([None, "grove"])))
        else:
            box = rect(rng.uniform(0, 200), rng.uniform(0, 200), rng.uniform(1, 40), rng.uniform(1, 40), rng.choice([0.0, 17.0, 45.0]))
            obs.append(Obstacle(tuple(box), WEIGHT_OBSTACLE, keep=rng.choice([0.0, 6.0]), soft=rng.random() < 0.2))
    ways = [Way(tuple((rng.uniform(0, 200), rng.uniform(0, 200)) for _ in range(rng.randint(2, 4))), rng.choice([1.5, 4.0, 13.0])) for _ in range(rng.randint(0, 3))]
    return cls(obs, ways)


def test_a_strict_search_answers_as_if_it_measured_every_seat() -> None:
    """The indexed strict search returns exactly the scan's seat - or None - over scenes of crowns, roofs and ways, the
    board beside them, deep under them and in the open (the canopy scene among them, `blocked` refusing every seat)."""
    rng = random.Random(287)
    refused = 0
    for k in range(60):
        seed = rng.random()
        board = Subject("point", tuple(rect(100 + rng.uniform(-30, 30), 100 + rng.uniform(-30, 30), 6.0, 2.5, rng.choice([0.0, 30.0]))), angle=rng.choice([0.0, 30.0]))
        frame = (0.0, 0.0, 200.0, 200.0) if k % 2 else None
        for ring in (0, None):
            fast = place("notice board", SIZE, board, _scene(random.Random(seed)), frame, strict=True, max_ring=ring)
            scan = place("notice board", SIZE, board, _scene(random.Random(seed), _Unindexed), frame, strict=True, max_ring=ring)
            assert fast == scan, (k, ring)
            refused += fast is None
    assert 0 < refused < 120, "the scenes hold both answers"
    canopy = ObstacleIndex([circle_obstacle(100.0, 100.0, 600.0, WEIGHT_OBSTACLE)], [Way(((0.0, 110.0), (200.0, 110.0)), 13.0)])
    board = Subject("point", tuple(rect(100.0, 100.0, 6.0, 2.5)))
    assert place("notice board", SIZE, board, canopy, strict=True, max_ring=0) is None


def test_a_blocked_seat_stays_covered_however_a_nudge_moves_it() -> None:
    """`blocked` is a promise about every seat within a nudge: wherever it says so, every block moved by up to
    `NUDGE_PX` each way is scored above zero - by a gap closer than the clearance less the nudge, a disc or roof the
    block's center stands deep in, or a way through the block's middle."""
    rng = random.Random(7)
    said = 0
    for _ in range(400):
        idx = _scene(rng)
        cx, cy, ang = rng.uniform(0, 200), rng.uniform(0, 200), rng.choice([0.0, 30.0])
        hw, hh, clear = rng.uniform(4, 30), rng.uniform(2, 8), rng.choice([2.0, 4.0, 8.0])
        if not idx.blocked(rect(cx, cy, hw, hh, ang), clear, NUDGE_REACH, text="notice board"):
            continue
        said += 1
        for dx in range(-NUDGE_PX, NUDGE_PX + 1):
            for dy in range(-NUDGE_PX, NUDGE_PX + 1):
                assert idx.cost(rect(cx + dx, cy + dy, hw, hh, ang), clear, text="notice board") > 0.0
    assert said > 100, "the scenes refuse seats by every route"
    thin = ObstacleIndex(ways=[Way(((0.0, 50.0), (100.0, 50.0)), 1.5)])
    assert thin.blocked(rect(50.0, 50.0, 20.0, 8.0), 4.0, NUDGE_REACH), "a lane through the block's middle, thinner than a nudge"
    assert not thin.blocked(rect(50.0, 56.0, 20.0, 8.0), 4.0, NUDGE_REACH), "a lane near the block's edge a nudge may clear"
    grove = ObstacleIndex([circle_obstacle(50.0, 50.0, 300.0, WEIGHT_OBSTACLE, "grove")])
    assert grove.blocked(rect(50.0, 50.0, 20.0, 8.0), 4.0, NUDGE_REACH, text="notice board")
    assert not grove.blocked(rect(50.0, 50.0, 20.0, 8.0), 4.0, NUDGE_REACH, text="village grove"), "a caption naming its group"
    roof = ObstacleIndex([Obstacle(tuple(rect(50.0, 50.0, 40.0, 40.0, 10.0)), WEIGHT_OBSTACLE)])
    assert roof.blocked(rect(50.0, 50.0, 5.0, 3.0), 2.0, NUDGE_REACH), "deep inside a turned roof"
    assert not roof.blocked(rect(50.0, 50.0, 5.0, 3.0), 2.0, NUDGE_REACH, text="x", subject=list(rect(50.0, 50.0, 40.0, 40.0, 10.0))), "its own subject"


def test_the_way_term_measures_each_segment_once_and_answers_as_the_scan() -> None:
    """A long way is filed in every cell it crosses; the score measures a segment once and clears it by the boxes first,
    and still counts `WEIGHT_WAY` per way crossed exactly as measuring every segment in every cell did."""
    rng = random.Random(11)
    for _ in range(300):
        ways = [Way(tuple((rng.uniform(0, 300), rng.uniform(0, 300)) for _ in range(rng.randint(2, 5))), rng.choice([1.5, 13.0])) for _ in range(3)]
        block = rect(rng.uniform(0, 300), rng.uniform(0, 300), rng.uniform(3, 60), rng.uniform(2, 10), rng.choice([0.0, 25.0]))
        crossed = sum(any(poly_seg_gap(block, a, b) < w.half_width + WAY_NOTCH for a, b in zip(w.pts, w.pts[1:], strict=False)) for w in ways)
        assert ObstacleIndex(ways=ways).cost(block, 4.0) == WEIGHT_WAY * crossed


def test_outlines_whose_boxes_stand_apart_are_measured_vertex_to_edge() -> None:
    """`nearest_points` skips its crossing and containment tests for outlines whose boxes stand apart; the gap is the least
    vertex-to-edge distance either way, as before - and outlines whose boxes meet still take every test."""
    rng = random.Random(5)
    for _ in range(300):
        p = rect(rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(1, 20), rng.uniform(1, 20), rng.uniform(0, 90))
        q = rect(rng.uniform(0, 100), rng.uniform(0, 100), rng.uniform(1, 20), rng.uniform(1, 20), rng.uniform(0, 90))
        edges = lambda poly: list(zip(poly, [*poly[1:], poly[0]], strict=True))  # noqa: E731
        brute = min([math.dist(v, seg_closest(v, a, b)) for v in p for a, b in edges(q)] + [math.dist(v, seg_closest(v, a, b)) for v in q for a, b in edges(p)])
        gap = poly_gap(p, q)
        assert gap == brute or gap == 0.0
    far = nearest_points(rect(0.0, 0.0, 1.0, 1.0), rect(10.0, 0.0, 1.0, 1.0))
    assert far == ((1.0, -1.0), (9.0, -1.0))
    assert poly_gap(rect(0.0, 0.0, 5.0, 5.0), rect(0.0, 0.0, 1.0, 1.0)) == 0.0, "one holds the other: boxes meet, tested"
