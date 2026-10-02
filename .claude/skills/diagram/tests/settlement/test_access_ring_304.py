"""The indexed scans of feature 304 (plan D5, D6) answer EXACTLY as the scans they replace.

The access tree's nearest targets were the whole tree measured for every door, and the shared sheds' pockets every paddy
outline for every candidate - both growing with the households (specs/304-homesteads-at-scale/research.md R2, R3). Each lever
must leave every map byte-identical (spec SC-005), so each is held here to its scan, kept as the oracle, on random inputs
built to reach the cases an index can get wrong: ties, a tree with fewer points than are asked for, an asker far outside the
tree, a candidate on an outline and one beside it only."""

from __future__ import annotations

import random

import pytest

from l7r.diagram.settlement._geom import edge_dist, point_in_poly
from l7r.diagram.settlement.rolling.access import TARGETS_TRIED, AccessTree, ring_targets, scan_targets
from l7r.diagram.settlement.shrines_wells.byres import beside_a_paddy, paddy_index


def _tree(rng: random.Random, n: int, span: float, grid: bool = False) -> AccessTree:
    """`n` corridors chained and branched over a `span`-wide square; on `grid`, their ends snapped to a 50 px lattice so
    equal distances (ties) are common."""
    t = AccessTree(7.0)
    ends = [(rng.uniform(0, span), rng.uniform(0, span))]
    for _ in range(n):
        a = rng.choice(ends)
        b = (a[0] + rng.uniform(-400, 400), a[1] + rng.uniform(-400, 400))
        if grid:
            a, b = (round(a[0] / 50) * 50.0, round(a[1] / 50) * 50.0), (round(b[0] / 50) * 50.0, round(b[1] / 50) * 50.0)
        t.add(a, b)
        ends.append(b)
    return t


@pytest.mark.parametrize("seed", range(40))
def test_the_ring_answers_as_the_scan_on_random_trees_and_doors(seed: int) -> None:
    rng = random.Random(seed)
    t = _tree(rng, rng.choice((1, 2, 5, 20, 80)), rng.choice((300.0, 3000.0, 9000.0)), grid=seed % 2 == 0)
    doors = [(rng.uniform(-2000, 11000), rng.uniform(-2000, 11000)) for _ in range(15)]
    doors += [q for along in t._along for q in along][:10]  # doors standing on the tree: distance 0, the tie of every corridor through it
    for door in doors:
        assert ring_targets(t, door) == scan_targets(t, door), (seed, door)


def test_a_tree_with_fewer_points_than_asked_gives_them_all_in_the_scans_order() -> None:
    t = AccessTree(7.0)
    t.add((0.0, 0.0), (60.0, 0.0))  # two points along and one nearest point: three targets, fewer than `TARGETS_TRIED`
    door = (5000.0, 5000.0)
    assert len(scan_targets(t, door)) == 3 < TARGETS_TRIED
    assert ring_targets(t, door) == scan_targets(t, door)


def test_an_empty_tree_has_no_targets() -> None:
    assert ring_targets(AccessTree(7.0), (0.0, 0.0)) == [] == scan_targets(AccessTree(7.0), (0.0, 0.0))


def test_the_tree_remembers_a_doors_targets_until_a_corridor_is_added() -> None:
    t = AccessTree(7.0)
    t.add((0.0, 0.0), (1000.0, 0.0))
    first = t.targets((500.0, 300.0))
    assert t.targets((500.0, 300.0)) is first
    t.add((500.0, 0.0), (500.0, 290.0))
    assert t.targets((500.0, 300.0)) == scan_targets(t, (500.0, 300.0)) != first


def _outline(rng: random.Random) -> list[tuple[float, float]]:
    cx, cy, r = rng.uniform(0, 2000), rng.uniform(0, 2000), rng.uniform(20, 200)
    n = rng.randint(3, 9)
    return [(cx + r * rng.uniform(0.5, 1.0) * __import__("math").cos(k * 6.283 / n), cy + r * rng.uniform(0.5, 1.0) * __import__("math").sin(k * 6.283 / n)) for k in range(n)]


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
