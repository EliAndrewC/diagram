"""The fabric index (feature 138) is allowed to replace the brute-force clearance scan only because it is
DEMONSTRABLY the same verdict: on random fabric every sample's `fouled` agrees with the scan it replaces,
and the index's candidates are a superset of the entries whose inflated bounds contain the sample."""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.clearance import FabricIndex, fouled_brute, pairs_within


def _fabric(rng: random.Random, n: int) -> tuple[list[list[tuple[float, float]]], list[list[tuple[float, float]]], list[tuple[tuple[float, float], tuple[float, float]]]]:
    def poly() -> list[tuple[float, float]]:
        cx, cy = rng.uniform(0, 1000), rng.uniform(0, 1000)
        w, h = rng.uniform(5, 120), rng.uniform(5, 120)
        a = rng.uniform(0, math.pi)
        c, s = math.cos(a), math.sin(a)
        return [(cx + c * dx - s * dy, cy + s * dx + c * dy) for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]

    obstacles = [poly() for _ in range(n)]
    tight = [poly() for _ in range(n)]
    lines = [((rng.uniform(0, 1000), rng.uniform(0, 1000)), (rng.uniform(0, 1000), rng.uniform(0, 1000))) for _ in range(n)]
    return obstacles, tight, lines


def test_the_index_agrees_with_the_brute_force_scan_on_random_fabric() -> None:
    rng = random.Random(138)
    for trial in range(40):
        obstacles, tight, lines = _fabric(rng, rng.randint(0, 25))
        margin, tm, lm = rng.choice((0.0, 4.0, 8.0, 20.0)), rng.choice((0.0, 4.0, 7.0)), rng.choice((0.0, 14.0))
        idx = FabricIndex(obstacles, margin, tight, tm, lines, lm)
        for _ in range(200):
            q = (rng.uniform(-50, 1050), rng.uniform(-50, 1050))
            assert idx.fouled(q) == fouled_brute(q, obstacles, margin, tight, tm, lines, lm), (trial, q)
            # the superset property: every entry whose inflated bounds contain q is among the candidates
            cands = set(idx.candidates(q))
            for i, (_k, _p, _m, (bx0, by0, bx1, by1)) in enumerate(idx.polys):
                if bx0 <= q[0] <= bx1 and by0 <= q[1] <= by1:
                    assert i in cands, (trial, q, i)


def test_empty_fabric_fouls_nothing_and_a_degenerate_polygon_is_skipped() -> None:
    idx = FabricIndex([], 8.0, [[]], 4.0, [], 14.0)
    assert not idx.fouled((3.0, 3.0)) and idx.candidates((3.0, 3.0)) == []
    assert not fouled_brute((3.0, 3.0), [], 8.0, [[]], 4.0)


def test_a_fixed_cell_size_is_honored_and_lines_are_filed() -> None:
    idx = FabricIndex([], 0.0, (), 0.0, [((0.0, 0.0), (100.0, 0.0))], 5.0, cell=10.0)
    assert idx.cell == 10.0
    assert idx.fouled((50.0, 4.0)) and not idx.fouled((50.0, 6.0)) and not idx.fouled((50.0, -6.0))


def test_pairs_within_counts_exactly_what_the_pairwise_form_counts() -> None:
    rng = random.Random(7)
    for _ in range(60):
        pts = [(rng.uniform(0, 300), rng.uniform(0, 300)) for _ in range(rng.randint(0, 40))]
        reach = rng.choice((10.0, 46.0, 120.0))
        pairwise = sum(1 for i, u in enumerate(pts) for v in pts[i + 1 :] if math.hypot(u[0] - v[0], u[1] - v[1]) < reach)
        assert pairs_within(pts, reach) == pairwise
    assert pairs_within([(0.0, 0.0), (45.0, 0.0), (46.0, 0.0)], 46.0) == 2  # strict: 46 is not within 46 of 0, 45 is of both... 45-46 is 1 apart
