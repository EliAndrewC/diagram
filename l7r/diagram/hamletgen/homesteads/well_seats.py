"""The well seating's per-seat questions, answered for the whole lattice at once (feature 387, amendment 1, plan D9).

`wells.seat_wells` asks every lattice seat for its nearest houses (the rung's neighborhood test and the ranking's
tie-break), its gap to a dwelling's wall, and - for the first of two wells - whether the best second seat would leave both
wells serving ten or fewer households. Asked seat by seat, house by house, that was 6.8 million house distances on one
40-household roll and 10-43 s of its wells (profile 2026-10-18, seed 25). Here the distances are one array per call and
every rung reads it; the wall gap is measured only against the houses whose centers stand near enough to matter; the
look ahead counts each household's nearest well for every second seat in one array operation.

The rules are the ones `seat_wells` claims (0196, 0072); only how they are computed changes. Where a float rounding in
numpy's distance differs from `math.hypot`'s in the last place, a seat exactly on a rung's threshold can fall either way -
the GM's amendment 1 lets maps change so long as the research holds, and every seat still passes the same predicates.

Research: plumbing - NONE: how `seat_wells`' own questions (its claims) are computed
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

import numpy as np

from l7r.diagram.settlement.shrines_wells.wells import well_gap_to_dwellings

from ..consts import Pt


class SeatSweep:
    """Every lattice seat's distance to every house, one array (seats x houses), read by each rung of the ladder."""

    __slots__ = ("dist", "houses", "pts")

    def __init__(self, pts: Sequence[Pt], houses: Sequence[Mapping[str, Any]]) -> None:
        self.pts = [(float(x), float(y)) for x, y in pts]
        self.houses = houses
        p = np.asarray(self.pts, dtype=float).reshape(-1, 2)
        h = np.asarray([(float(o["x"]), float(o["y"])) for o in houses], dtype=float).reshape(-1, 2)
        self.dist = np.hypot(p[:, None, 0] - h[None, :, 0], p[:, None, 1] - h[None, :, 1])

    def seats(
        self, third: float, want_near: int, gap: float, reach_r: float, seat_ok: Callable[[float, float], bool], center: Pt
    ) -> tuple[list[tuple[float, float, float]], dict[tuple[float, float, float], float]]:
        """The rung's seats, `(distance to center, x, y)` in the lattice's order, and each seat's `want_near`-th nearest house
        (the ranking's neighborhood tie-break): a seat with `want_near` houses within `third`, its nearest house's center within
        `gap` plus the widest house's half-diagonal (the prefilter), a dwelling's wall within `gap` (`well_gap_to_dwellings`,
        asked of the houses near enough to matter: a house whose center is farther than `gap` plus the half-diagonal has its
        wall farther than `gap`), and `seat_ok`.

        Research: the rung's test - NONE: `seat_wells`' own neighborhood and seat gap, computed for the lattice at once"""
        out: list[tuple[float, float, float]] = []
        kth: dict[tuple[float, float, float], float] = {}
        if len(self.houses) < want_near or not self.pts:
            return out, kth
        d = self.dist
        nth = np.partition(d, want_near - 1, axis=1)[:, want_near - 1]
        nearest = d.min(axis=1)
        reach = gap + reach_r
        for k in np.nonzero((nth <= third) & (nearest <= reach))[0]:
            x, y = self.pts[int(k)]
            near = [self.houses[int(j)] for j in np.nonzero(d[int(k)] <= reach)[0]]
            if well_gap_to_dwellings(near, round(x, 1), round(y, 1)) <= gap and seat_ok(x, y):
                c = (float(np.hypot(x - center[0], y - center[1])), x, y)
                out.append(c)
                kth[c] = float(nth[int(k)])
        return out, kth


class PairAhead:
    """The look ahead of the first of two wells, for every second seat at once (feature 374 wave 155's `pair_keeps_ten`,
    vectorized by feature 387)."""

    __slots__ = ("hx", "hy", "sx", "sy")

    def __init__(self, seats: Sequence[tuple[float, float, float]], houses: Sequence[Mapping[str, Any]]) -> None:
        self.sx = np.asarray([c[1] for c in seats], dtype=float)
        self.sy = np.asarray([c[2] for c in seats], dtype=float)
        self.hx = np.asarray([float(h["x"]) for h in houses], dtype=float)
        self.hy = np.asarray([float(h["y"]) for h in houses], dtype=float)

    def keeps_ten(self, c: tuple[float, float, float], spacing: float = 170.0, most: int = 10) -> bool:
        """Would a first well at `c` leave a second seat, `spacing` px off it, with both wells nearest to no more than `most`
        households? Each household goes to its nearer well, the first on a tie (`wells.most_served_after`'s `min`).

        Research:
            no well serving more than ten - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses each dug well served at Karihama
            the second well held 170 px off the first - UNRESEARCHED: the pair's spacing, `seat_wells`' own "wells apart"; no page gives a hamlet's wells' spacing"""
        if not len(self.sx):
            return False
        apart = np.hypot(self.sx - c[1], self.sy - c[2]) >= spacing
        to_c = np.hypot(self.hx - c[1], self.hy - c[2])[:, None]
        to_d = np.hypot(self.hx[:, None] - self.sx[None, :], self.hy[:, None] - self.sy[None, :])
        first = (to_c <= to_d).sum(axis=0)
        busiest = np.maximum(first, len(self.hx) - first)
        return bool(np.any(apart & (busiest <= most)))
