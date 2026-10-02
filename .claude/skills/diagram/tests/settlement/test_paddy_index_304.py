"""The shared sheds' pockets ask only the paddies near them (feature 304, plan D6) and answer EXACTLY as the scan of every
outline they replaced - which was 16.7% of seed 47's homesteads stage at 40 households (specs/304-homesteads-at-scale/
research.md R2). Every map must stay byte-identical (spec SC-005), so the index is held here to the scan, kept as the oracle,
on random outlines and candidates built to reach what an index can get wrong: a candidate on an outline, inside one, and one
beside it only. (Plan D5, a ring query for the access tree's targets, was withdrawn - research R10.)"""

from __future__ import annotations

import math
import random

import pytest

from l7r.diagram.settlement._geom import edge_dist, point_in_poly
from l7r.diagram.settlement.shrines_wells.byres import beside_a_paddy, paddy_index


def _outline(rng: random.Random) -> list[tuple[float, float]]:
    cx, cy, r = rng.uniform(0, 2000), rng.uniform(0, 2000), rng.uniform(20, 200)
    n = rng.randint(3, 9)
    return [(cx + r * rng.uniform(0.5, 1.0) * math.cos(k * 6.283 / n), cy + r * rng.uniform(0.5, 1.0) * math.sin(k * 6.283 / n)) for k in range(n)]


@pytest.mark.parametrize("seed", range(30))
def test_a_pocket_beside_a_paddy_answers_as_the_scan_of_every_outline(seed: int) -> None:
    rng = random.Random(1000 + seed)
    polys = [_outline(rng) for _ in range(rng.choice((0, 1, 10, 60)))]
    index = paddy_index(polys)
    pts = [(rng.uniform(-300, 2300), rng.uniform(-300, 2300)) for _ in range(200)]
    pts += [p for ff in polys[:5] for p in ff]  # on an outline's corner
    for gap in (5.0, 11.0, 40.0):
        for x, y in pts:
            scan = any(point_in_poly(x, y, ff) or edge_dist(x, y, ff) < gap for ff in polys)
            assert beside_a_paddy(x, y, gap, polys, index) == scan == beside_a_paddy(x, y, gap, polys), (seed, x, y, gap)


def test_a_pocket_inside_a_paddy_and_one_only_beside_it_are_both_refused_through_the_index() -> None:
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    index = paddy_index([square])
    assert beside_a_paddy(50.0, 50.0, 11.0, [square], index), "inside the outline"
    assert beside_a_paddy(108.0, 50.0, 11.0, [square], index), "8 px off the east edge, inside the 11 px gap"
    assert not beside_a_paddy(112.0, 50.0, 11.0, [square], index), "12 px off it"
