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


def test_the_wall_gap_is_measured_once_a_seat_and_reads_the_dwellings() -> None:
    """Feature 427 T05: `walls` is `well_gap_to_dwellings` for the lattice - 0 inside a dwelling, an abandoned house no dwelling,
    a seat measured once for every rung."""
    import numpy as np

    houses = [{"x": 100.0, "y": 100.0, "w": 40.0, "h": 20.0, "rot": 30.0}, {"x": 400.0, "y": 100.0, "w": 40.0, "h": 20.0, "kind": "abandoned"}]
    pts = [(100.0, 100.0), (160.0, 100.0), (400.0, 100.0)]
    sweep = SeatSweep(pts, houses)
    got = sweep.walls(np.arange(3), 1e9)
    for k, (x, y) in enumerate(pts):
        assert math.isclose(got[k], well_gap_to_dwellings(houses, x, y), abs_tol=1e-9)
    sweep.wall[0] = -1.0  # a seat measured is never measured again
    assert sweep.walls(np.arange(1), 1e9)[0] == -1.0
    assert np.isinf(SeatSweep(pts, houses).walls(np.arange(3), 1.0)[1:]).all()  # no dwelling within reach: infinity
    gone = SeatSweep(pts, [houses[1]])
    assert np.isinf(gone.walls(np.arange(3), 1e9)).all()
    assert len(gone.walls(np.arange(3), 1e9)) == 3  # measured once: nothing left to do


def test_the_seat_tests_asked_as_arrays_are_the_one_seat_tests_and_kept_on_the_sweep() -> None:
    """Feature 435 T06: `discs_cover` is `ReservedSeats.disc_covers` for every seat, `SeatTest.many` the seat test asked of many,
    and `SeatSweep.seats` with `many` keeps the seats the one-seat test keeps, each verdict asked once."""
    import numpy as np

    from l7r.diagram.hamletgen.homesteads.well_seats import SeatTest, cells, discs_cover
    from l7r.diagram.settlement.homestead_parts.wood_share import ReservedSeats

    assert cells(np.zeros((0, 2))) == [] and not discs_cover(np.zeros((2, 2)), np.zeros((0, 2)), 5.0).any()
    for seed in seeds(20):
        rng = random.Random(200 + seed)
        reserved = ReservedSeats([{"wood_share": {"seats": [(rng.uniform(0, 900), rng.uniform(0, 900)) for _ in range(rng.randint(0, 30))]}}])
        P = np.asarray([(rng.uniform(-50, 950), rng.uniform(-50, 950)) for _ in range(300)])
        r = rng.uniform(5.0, 60.0)
        got = discs_cover(P, np.asarray(reserved.pts, dtype=float).reshape(-1, 2), r)
        assert [bool(g) for g in got] == [reserved.disc_covers(float(x), float(y), r) for x, y in P], seed
        houses = _hamlet(rng)
        pts = [(rng.uniform(-100, 1000) + 0.37, rng.uniform(-100, 1000) + 0.37) for _ in range(400)]
        reach_r = max(math.hypot(h["w"], h["h"]) / 2 for h in houses)
        asked: list[int] = []

        def many(Q: Any, asked: list[int] = asked) -> Any:
            asked.append(len(Q))
            return np.asarray([_ok(float(x), float(y)) for x, y in Q])

        test = SeatTest("odd", _ok, many)
        assert test(7.0, 0.0) is False
        sweep = SeatSweep(pts, houses)
        for third, want_near in ((190.0, 3), (300.0, 5), (1e9, 2)):
            got_seats, _ = sweep.seats(third, want_near, 80.0, reach_r, test, (450.0, 450.0), (test.key, test.many))
            old, _ = SeatSweep(pts, houses).seats(third, want_near, 80.0, reach_r, _ok, (450.0, 450.0))
            assert got_seats == old, (seed, third)
        assert sum(asked) == int((~np.isnan(sweep.ok["odd"])).sum())  # each seat asked once across the rungs
