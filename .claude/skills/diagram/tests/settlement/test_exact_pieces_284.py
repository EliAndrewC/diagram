"""Feature 284's exact pieces, each against a copy of the form it replaced: the board's lazy caption choice (A3), the bamboo
search walked outward (A4), the fabric crossing's box prefilters and the ring test (A5), and the grove draw's crown grid
(A6). Each index or ordering PRUNES; the old test DECIDES (`dev/performance.md`)."""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.hinterland.bamboo import nearest_fitting
from l7r.diagram.hamletgen.ways.fabric import _crosses_fabric
from l7r.diagram.hamletgen.ways.geom import ring_within
from l7r.diagram.settlement._geom import edge_dist, seg_dist, segments_cross
from l7r.diagram.settlement.shrines_wells.woods import CrownIndex, TreeStandsMixin
from l7r.diagram.settlement.structures.fixtures.siting import BOARD_CAPTION_TOP, board_choice


def _old_choice(seats, level):
    fits = {id(c): level(c) for c in seats}
    fitting = [c for c in seats if fits[id(c)] == max(fits.values())]
    in_the_open = [c for c in fitting if not c[7]] or fitting
    return max(in_the_open, key=lambda c: (fits[id(c)], c[5] is not None, c[1]))


def test_the_lazy_board_choice_is_the_full_choice() -> None:
    """A3: over random candidate sets - ties on score, shaded and open seats, caption levels 0 to the top - the lazy walk
    picks the very seat (the same object) the full evaluation picks, and asks fewer levels when a top seat is open."""
    rng = random.Random(2843)
    asked_less = 0
    for _ in range(400):
        seats = [(0, rng.choice((1.0, 2.0, 3.0, rng.uniform(0, 5))), 0.0, 0.0, 0.0, rng.choice((None, 0, 1)), 0.0, rng.random() < 0.4) for _ in range(rng.randint(1, 14))]
        levels = {id(c): rng.choice((0, 1, 1, BOARD_CAPTION_TOP, BOARD_CAPTION_TOP)) for c in seats}
        calls: list[int] = []

        def level(c, calls=calls, levels=levels):
            calls.append(1)
            return levels[id(c)]

        assert board_choice(seats, level) is _old_choice(seats, lambda c, levels=levels: levels[id(c)])
        asked_less += len(calls) < len(seats)
    assert asked_less, "non-vacuity: the walk stopped early somewhere"


def test_the_bamboo_walk_outward_finds_the_scans_seat() -> None:
    """A4: the nearest fitting position, ties in row order, exactly as the whole-square scan kept it - obstacles of every
    kind, no fit at all, and a fit exactly on a tie."""
    rng = random.Random(2844)
    for _ in range(60):
        target, reach, step = (rng.uniform(100, 300), rng.uniform(100, 300)), rng.uniform(40, 90), rng.choice((4.0, 8.0))
        holes = [(rng.uniform(0, 400), rng.uniform(0, 400), rng.uniform(5, 70)) for _ in range(rng.randint(0, 8))]

        def fits(x, y, holes=holes):
            return all(math.hypot(x - hx, y - hy) > hr for hx, hy, hr in holes)

        best = None
        y = target[1] - reach
        while y <= target[1] + reach:
            x = target[0] - reach
            while x <= target[0] + reach:
                if fits(x, y):
                    d = math.hypot(x - target[0], y - target[1])
                    if best is None or d < best[0]:
                        best = (d, x, y)
                x += step
            y += step
        assert nearest_fitting(target, reach, step, fits) == best
    assert nearest_fitting((0.0, 0.0), 10.0, 5.0, lambda x, y: False) is None


def _old_crosses(run, fabric, gap):
    for poly in fabric:
        for k in range(len(run) - 1):
            a, b = run[k], run[k + 1]
            for j in range(len(poly)):
                c, d = poly[j], poly[(j + 1) % len(poly)]
                if segments_cross(a, b, c, d) or seg_dist(c[0], c[1], a, b) < gap:
                    return True
            if edge_dist(a[0], a[1], poly) < gap or edge_dist(b[0], b[1], poly) < gap:
                return True
    return False


def _box(rng):
    cx, cy, w, h = rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(8, 60), rng.uniform(8, 60)
    return [(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h)]


def test_the_fabric_crossing_with_box_prefilters_is_the_old_scan() -> None:
    """A5: `_crosses_fabric` answers as the full scan did - runs through, beside and exactly `gap` off a steading."""
    rng = random.Random(2845)
    for _ in range(500):
        fabric = [_box(rng) for _ in range(rng.randint(0, 9))]
        run = [(rng.uniform(0, 600), rng.uniform(0, 600)) for _ in range(rng.randint(2, 5))]
        gap = rng.choice((3.0, 7.0, 12.0))
        assert _crosses_fabric(run, fabric, gap) == _old_crosses(run, fabric, gap)
    square = [(100.0, 100.0), (200.0, 100.0), (200.0, 200.0), (100.0, 200.0)]
    at = [(0.0, 93.0), (300.0, 93.0)]  # exactly 7 off the square's edge: not under a 7 gap, under an 8
    assert _crosses_fabric(at, [square], 7.0) is _old_crosses(at, [square], 7.0) is False
    assert _crosses_fabric(at, [square], 8.0) is _old_crosses(at, [square], 8.0) is True


def test_the_ring_test_from_the_shared_index_is_edge_dist() -> None:
    """A5: `ring_within` is `edge_dist <= limit` (closed) and `< limit` (open) - points inside, outside, and exactly at the
    limit."""
    rng = random.Random(2846)
    for _ in range(300):
        poly = _box(rng)
        limit = rng.choice((4.0, 10.0, 25.0))
        for _k in range(20):
            x, y = rng.uniform(-50, 650), rng.uniform(-50, 650)
            d = edge_dist(x, y, poly)
            assert ring_within(x, y, poly, limit) == (d <= limit)
            assert ring_within(x, y, poly, limit, closed=False) == (d < limit)
    sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert ring_within(5.0, -4.0, sq, 4.0) is True and ring_within(5.0, -4.0, sq, 4.0, closed=False) is False


def test_the_crown_grid_is_the_crown_scan() -> None:
    """A6: a crown seat is clear by the grid exactly when the scan over every crown says so - crowns of every size, a seat
    inside a bigger crown, a crown center inside a bigger seat, and crowns added as they land."""
    rng = random.Random(2847)
    for _ in range(100):
        crowns = [(rng.uniform(0, 300), rng.uniform(0, 300), rng.uniform(3, 20)) for _ in range(rng.randint(0, 40))]
        index = CrownIndex(crowns[: len(crowns) // 2])
        index.add(crowns[len(crowns) // 2 :])
        for _k in range(60):
            x, y, r = rng.uniform(-20, 320), rng.uniform(-20, 320), rng.uniform(3, 20)
            assert index.clear(x, y, r) == TreeStandsMixin._crown_seat_clear(x, y, r, crowns)
    assert CrownIndex().clear(1.0, 1.0, 5.0) is True
