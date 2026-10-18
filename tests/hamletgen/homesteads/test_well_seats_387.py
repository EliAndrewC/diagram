"""Feature 387 amendment 1 (plan D9): the well seating's per-seat questions answered for the lattice at once.

`SeatSweep.seats` keeps the seats the seat-by-seat loop kept, and `PairAhead.keeps_ten` answers as `pair_keeps_ten` did, on
random hamlets; the old forms are kept here as the oracles. (A distance on a rung's threshold may round differently in numpy -
amendment 1 lets that move a seat; the random cases here keep off the exact thresholds.)"""

from __future__ import annotations

import math
import random
from typing import Any

from l7r.diagram.hamletgen.homesteads.well_seats import PairAhead, SeatSweep
from l7r.diagram.settlement.shrines_wells.wells import well_gap_to_dwellings
from tests._sweep import seeds


def _old_seats(pts: Any, houses: Any, third: float, want_near: int, gap: float, reach_r: float, ok: Any, center: Any) -> list[tuple[float, float, float]]:
    out = []
    for x, y in pts:
        near = sorted(math.hypot(x - h["x"], y - h["y"]) for h in houses)
        if len(near) >= want_near and near[want_near - 1] <= third and near[0] <= gap + reach_r and well_gap_to_dwellings(houses, round(x, 1), round(y, 1)) <= gap and ok(x, y):
            out.append((math.hypot(x - center[0], y - center[1]), x, y))
    return out


def _old_most_served_after(c: Any, houses: Any, wells: Any) -> int:
    pts = [*wells, (c[1], c[2])]
    count = [0] * len(pts)
    for h in houses:
        count[min(range(len(pts)), key=lambda i: math.hypot(h["x"] - pts[i][0], h["y"] - pts[i][1]))] += 1
    return max(count)


def _old_pair_keeps_ten(c: Any, seats: Any, houses: Any) -> bool:
    return any(math.hypot(c[1] - d[1], c[2] - d[2]) >= 170.0 and _old_most_served_after(d, houses, [(c[1], c[2])]) <= 10 for d in seats)


def _hamlet(rng: random.Random) -> list[dict[str, Any]]:
    return [
        {"x": round(rng.uniform(0, 900), 3), "y": round(rng.uniform(0, 900), 3), "w": rng.uniform(30, 50), "h": rng.uniform(20, 30), "rot": rng.uniform(-30, 30)} for _ in range(rng.randint(3, 40))
    ]


def _ok(x: float, y: float) -> bool:
    return (int(x) + int(y)) % 7 != 0  # a seat test that refuses some


def test_the_sweep_keeps_the_seats_the_loop_kept() -> None:
    for seed in seeds(30):
        rng = random.Random(seed)
        houses = _hamlet(rng)
        pts = [(rng.uniform(-100, 1000) + 0.37, rng.uniform(-100, 1000) + 0.37) for _ in range(400)]
        sweep = SeatSweep(pts, houses)
        reach_r = max(math.hypot(h["w"], h["h"]) / 2 for h in houses)
        for third, want_near in ((190.0, 3), (300.0, 5), (1e9, 2)):
            got, kth = sweep.seats(third, want_near, 80.0, reach_r, _ok, (450.0, 450.0))
            old = _old_seats(pts, houses, third, want_near, 80.0, reach_r, _ok, (450.0, 450.0))
            assert [(round(a, 6), b, c) for a, b, c in got] == [(round(a, 6), b, c) for a, b, c in old], (seed, third)
            for c in got:
                assert math.isclose(kth[c], sorted(math.hypot(c[1] - h["x"], c[2] - h["y"]) for h in houses)[want_near - 1], abs_tol=1e-9)
    assert SeatSweep([(0.0, 0.0)], [{"x": 1.0, "y": 1.0, "w": 10, "h": 10}]).seats(100.0, 3, 80.0, 10.0, lambda x, y: True, (0.0, 0.0)) == ([], {})


def test_the_look_ahead_is_the_pair_rule_for_every_second_seat() -> None:
    for seed in seeds(60):
        rng = random.Random(100 + seed)
        houses = _hamlet(rng)
        seats = [(0.0, rng.uniform(0, 900), rng.uniform(0, 900)) for _ in range(rng.randint(1, 60))]
        ahead = PairAhead(seats, houses)
        for c in seats[:10]:
            assert ahead.keeps_ten(c) == _old_pair_keeps_ten(c, seats, houses), seed
