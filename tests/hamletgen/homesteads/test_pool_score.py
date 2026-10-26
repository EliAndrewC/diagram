"""`well_seats.PoolScore` (feature 427 T05, D5): `seat_wells`' sort key for a whole pool at once, held seat for seat to the
one-seat forms it replaced - `most_served_after`, `worst_after`, the crop overreach and the rung's neighborhood."""

from __future__ import annotations

import math
import random

import pytest

from l7r.diagram.hamletgen.homesteads.well_seats import PoolScore
from l7r.diagram.hamletgen.homesteads.wells import most_served_after, worst_after


def _reference(c, served, needy, placed, standing, box, r, belt, near, most):  # noqa: ANN001, ANN202
    """The key as `seat_wells` built it seat by seat before feature 427."""
    bx0, bx1, by0, by1 = box
    w = worst_after(c, needy, standing)
    e = max(0.0, bx0 - (c[1] - r), (c[1] + r) - bx1, by0 - (c[2] - r), (c[2] + r) - by1)
    return (int(most_served_after(c, served, placed) > most), (w + e) // 66.0, belt(c), e, w, near[c])


@pytest.mark.parametrize("seed", [1, 7, 23])
def test_the_pool_s_keys_are_the_one_seat_keys(seed: int) -> None:
    rng = random.Random(seed)
    served = [{"x": rng.uniform(0, 900), "y": rng.uniform(0, 700)} for _ in range(30)]
    needy = served[:22]
    pool = [(rng.uniform(0, 400), rng.uniform(0, 900), rng.uniform(0, 700)) for _ in range(60)]
    placed = [(rng.uniform(0, 900), rng.uniform(0, 700)) for _ in range(2)]
    standing = [min(math.hypot(h["x"] - wx, h["y"] - wy) for wx, wy in placed) for h in needy]
    box = (100.0, 800.0, 80.0, 620.0)
    near = {c: rng.uniform(10, 300) for c in pool}

    def belt(c):  # noqa: ANN001, ANN202
        return int(c[1] < 150.0)

    got = PoolScore(pool, served, needy).keys(pool, placed, standing, box, 8.0, belt, near, 10, 66.0)
    want = [_reference(c, served, needy, placed, standing, box, 8.0, belt, near, 10) for c in pool]
    for g, w in zip(got, want, strict=True):
        assert g[0] == w[0] and g[1] == w[1] and g[2] == w[2], (g, w)
        assert g[3] == pytest.approx(w[3]) and g[4] == pytest.approx(w[4]) and g[5] == w[5]


def test_a_tie_with_a_standing_well_stays_with_it_and_a_subset_of_the_pool_is_scored() -> None:
    """A household equidistant from a standing well and the seat stays with the standing well, as `min` over the wells in order
    keeps it; and the pool the sort sees shrinks as seats are popped - the rows are read by seat, not by position."""
    served = [{"x": 0.0, "y": 0.0}, {"x": 10.0, "y": 0.0}, {"x": 20.0, "y": 0.0}]
    pool = [(0.0, 20.0, 0.0), (0.0, 0.0, 0.0), (0.0, 5.0, 0.0)]
    placed = [(0.0, 0.0)]
    score = PoolScore(pool, served, served)
    standing = [0.0, 10.0, 20.0]
    keys = score.keys(pool[1:], placed, standing, (-50.0, 50.0, -50.0, 50.0), 1.0, lambda c: 0, {c: 0.0 for c in pool}, 1, 66.0)
    assert [k[0] for k in keys] == [int(most_served_after(c, served, placed) > 1) for c in pool[1:]]
    assert keys[0][0] == 1, "a seat ON the standing well takes no one: the standing well keeps all three"
