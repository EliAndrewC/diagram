"""`StrokeIndex.clearance` is `supply_bank_clearance` to the bit (feature 220).

The carve asks the nearest-segment question 86,000 times per roll; the index answers it from the cells
within the caller's reach and falls back to the full walk beyond it. Random strokes, random points,
tuple equality - including points inside the stroke's box but far from its line (the fallback) and
points past either end (the `past` reading)."""

from __future__ import annotations

import random

from l7r.diagram.waterfields.banks import StrokeIndex, polyline_cum, supply_bank_clearance


def _stroke(rng: random.Random, n: int) -> list[tuple[float, float]]:
    x, y = rng.uniform(100, 300), rng.uniform(100, 300)
    pts = [(x, y)]
    for _ in range(n):
        x += rng.uniform(20, 140)
        y += rng.uniform(-90, 90)
        pts.append((x, y))
    return pts


def test_the_indexed_walk_equals_the_full_walk_on_random_strokes_and_points() -> None:
    rng = random.Random(220)
    fallbacks = nears = 0
    for _ in range(12):
        pts = _stroke(rng, rng.randint(2, 14))
        w0, w1 = rng.uniform(4, 16), rng.uniform(2, 8)
        cum = polyline_cum(pts)
        reach = max(w0, w1) / 2 + 12.0
        idx = StrokeIndex(pts, w0, w1, cum, reach)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for _ in range(400):
            q = (rng.uniform(min(xs) - 60, max(xs) + 60), rng.uniform(min(ys) - 60, max(ys) + 60))
            full = supply_bank_clearance(q, pts, w0, w1, cum)
            assert idx.clearance(q) == full, (q, pts)
            if full[0] > reach:
                fallbacks += 1
            else:
                nears += 1
    assert fallbacks > 0 and nears > 0  # both branches exercised, or the equality proved half of nothing


def test_a_point_past_the_stroke_end_reads_past_through_the_index() -> None:
    pts = [(0.0, 0.0), (100.0, 0.0), (200.0, 10.0)]
    cum = polyline_cum(pts)
    idx = StrokeIndex(pts, 8.0, 4.0, cum, 10.0)
    assert idx.clearance((-5.0, 1.0)) == supply_bank_clearance((-5.0, 1.0), pts, 8.0, 4.0, cum)
    assert idx.clearance((-5.0, 1.0))[2] is True and idx.clearance((100.0, 3.0))[2] is False


def test_the_inexact_walk_answers_beyond_for_a_far_point_and_exactly_within_reach() -> None:
    rng = random.Random(221)
    pts = _stroke(rng, 6)
    w0, w1 = 10.0, 4.0
    cum = polyline_cum(pts)
    reach = 17.0
    idx = StrokeIndex(pts, w0, w1, cum, reach)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    beyond = within = 0
    for _ in range(600):
        q = (rng.uniform(min(xs) - 60, max(xs) + 60), rng.uniform(min(ys) - 60, max(ys) + 60))
        full = supply_bank_clearance(q, pts, w0, w1, cum)
        got = idx.clearance(q, exact=False)
        if full[0] > reach:
            assert got == StrokeIndex.BEYOND and got[0] >= full[0]  # a caller deciding under the reach reads "clear" either way
            beyond += 1
        else:
            assert got == full
            within += 1
    assert beyond > 0 and within > 0
