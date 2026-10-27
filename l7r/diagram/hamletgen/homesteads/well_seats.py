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
from dataclasses import dataclass
from typing import Any

from l7r.diagram.settlement._geom.overlap import rot_rect
from l7r.diagram.settlement._geom.primitives import seg_dists

from ..consts import Pt

#: THE CELL A SEAT TEST IS ASKED BY (feature 435 T06): the lattice's seats are asked in groups that share a 64 px cell, so each
#: group meets only the lane legs and reserved seats near it - a block of whole lattice rows spans the map and meets them all
CELL_PX = 64.0
"""Research: plumbing - NONE: how many seats one array asks at once, deciding nothing about the place"""


@dataclass(frozen=True)
class SeatTest:
    """A seat test asked of one seat (`one`, the reference) or of many as an array (`many`, rows of x and y) - its verdicts kept
    on the sweep under `key` (feature 435 T06)."""

    key: str
    one: Callable[[float, float], bool]
    many: Callable[[Any], Any]

    def __call__(self, x: float, y: float) -> bool:
        return self.one(x, y)


def cells(P: Any, size: float = CELL_PX) -> list[Any]:
    """The row indices of `P` grouped by the `size` px cell each point stands in."""
    import numpy as np

    if not len(P):
        return []
    k = np.floor(P / size).astype(np.int64)
    key = k[:, 0] * 1_000_003 + k[:, 1]
    order = np.argsort(key, kind="stable")
    return list(np.split(order, np.nonzero(np.diff(key[order]))[0] + 1))


def discs_cover(P: Any, centers: Any, r: float) -> Any:
    """For each point of `P`, does a disc of radius `r` there stand over any of `centers` - `ReservedSeats.disc_covers` for
    every point at once, the same strict test, asked cell by cell of the centers near each."""
    import numpy as np

    out = np.zeros(len(P), dtype=bool)
    if not len(centers) or r <= 0.0:
        return out
    for rows in cells(P):
        B = P[rows]
        lo, hi = B.min(axis=0) - r, B.max(axis=0) + r
        C = centers[((centers >= lo) & (centers <= hi)).all(axis=1)]
        if len(C):
            out[rows] = (((B[:, None, :] - C[None, :, :]) ** 2).sum(axis=2) < r * r).any(axis=1)
    return out


class SeatSweep:
    """Every lattice seat's distance to every house, one array (seats x houses), read by each rung of the ladder."""

    __slots__ = ("dist", "houses", "ok", "pts", "wall", "xy")

    def __init__(self, pts: Sequence[Pt], houses: Sequence[Mapping[str, Any]]) -> None:
        import numpy as np  # loaded when a well is seated, never at import (feature 237: no heavy library at import time)

        self.pts = [(float(x), float(y)) for x, y in pts]
        self.houses = houses
        p = np.asarray(self.pts, dtype=float).reshape(-1, 2)
        h = np.asarray([(float(o["x"]), float(o["y"])) for o in houses], dtype=float).reshape(-1, 2)
        self.dist = np.hypot(p[:, None, 0] - h[None, :, 0], p[:, None, 1] - h[None, :, 1])
        self.wall = np.full(len(self.pts), np.nan)
        self.xy = p
        self.ok: dict[Any, Any] = {}

    def walls(self, idx: Any, reach: float) -> Any:
        """The gap from each seat of `idx` (lattice rows) to the nearest dwelling's drawn wall, measured once a seat and kept for
        every later rung (feature 427 T05): `well_gap_to_dwellings`' reading - each dwelling's turned quad, 0 inside it, the seat
        at its tenth-of-a-pixel rounding, abandoned houses no dwelling - asked of the seats as arrays, dwelling by dwelling, where
        each seat had walked its near houses' edges one call at a time (965k segment distances on a 40-household roll, the T05
        fan-out). A dwelling whose center is farther than `reach` (the rung's gap plus the widest half-diagonal, the same for
        every rung of a sweep) is not measured: its wall is farther than the gap, and a seat with none nearer reads infinity.

        Research: plumbing - NONE: `well_gap_to_dwellings`' gap, computed for the lattice at once"""
        import numpy as np

        todo = idx[np.isnan(self.wall[idx])]
        self.wall[todo] = np.inf
        if not len(todo):
            return self.wall[idx]
        P = np.asarray([(round(self.pts[int(k)][0], 1), round(self.pts[int(k)][1], 1)) for k in todo], dtype=float).reshape(-1, 2)
        for j, o in enumerate(self.houses):
            near = self.dist[todo, j] <= reach
            if o.get("kind") == "abandoned" or not near.any():
                continue
            q = np.asarray(rot_rect(o["x"], o["y"], o["w"], o["h"], o.get("rot", 0.0)), dtype=float)
            r = np.roll(q, -1, axis=0)  # each corner's next: the quad's edges
            pts = P[near]
            gap = seg_dists([(float(x), float(y)) for x, y in pts], [((float(a[0]), float(a[1])), (float(c[0]), float(c[1]))) for a, c in zip(q, r, strict=True)]).min(axis=1)
            # inside the quad: `point_in_poly`'s crossing test, each corner against the one before it
            px, py = pts[:, 0:1], pts[:, 1:2]
            xi, yi, xj, yj = q[None, :, 0], q[None, :, 1], np.roll(q, 1, axis=0)[None, :, 0], np.roll(q, 1, axis=0)[None, :, 1]
            cross = ((yi > py) != (yj > py)) & (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi)
            gap[cross.sum(axis=1) % 2 == 1] = 0.0
            rows = todo[near]
            self.wall[rows] = np.minimum(self.wall[rows], gap)
        return self.wall[idx]

    def passing(self, rows: Any, key: Any, many: Callable[[Any], Any]) -> Any:
        """The rows of `rows` whose seat passes the static test `many`, asked of the seats not yet asked as one array and each
        verdict kept under `key` for every later rung and call that reads this sweep (feature 435 T06) - the verge and the wood
        floor, which no well landing changes.

        Research: plumbing - NONE: the caller's own seat test, asked of the lattice at once and kept"""
        import numpy as np

        got = self.ok.get(key)
        if got is None:
            got = self.ok[key] = np.full(len(self.pts), np.nan)
        todo = rows[np.isnan(got[rows])]
        if len(todo):
            got[todo] = np.asarray(many(self.xy[todo]), dtype=float)
        return rows[got[rows] == 1.0]

    def seats(
        self,
        third: float,
        want_near: int,
        gap: float,
        reach_r: float,
        seat_ok: Callable[[float, float], bool],
        center: Pt,
        many: tuple[Any, Callable[[Any], Any]] | None = None,
    ) -> tuple[list[tuple[float, float, float]], dict[tuple[float, float, float], float]]:
        """The rung's seats, `(distance to center, x, y)` in the lattice's order, and each seat's `want_near`-th nearest house
        (the ranking's neighborhood tie-break): a seat with `want_near` houses within `third`, its nearest house's center within
        `gap` plus the widest house's half-diagonal (the prefilter), a dwelling's wall within `gap` (`walls`, each seat measured
        once for every rung), and `seat_ok` - or, given `many` (its key and array form), the kept verdicts of `passing`.

        Research: the rung's test - NONE: `seat_wells`' own neighborhood and seat gap, computed for the lattice at once"""
        import numpy as np

        out: list[tuple[float, float, float]] = []
        kth: dict[tuple[float, float, float], float] = {}
        if len(self.houses) < want_near or not self.pts:
            return out, kth
        d = self.dist
        nth = np.partition(d, want_near - 1, axis=1)[:, want_near - 1]
        nearest = d.min(axis=1)
        reach = gap + reach_r
        idx = np.nonzero((nth <= third) & (nearest <= reach))[0]
        rows = idx[self.walls(idx, reach) <= gap]
        if many is not None:
            rows = self.passing(rows, *many)
        for k in rows:
            x, y = self.pts[int(k)]
            if many is None and not seat_ok(x, y):
                continue
            c = (float(np.hypot(x - center[0], y - center[1])), x, y)
            out.append(c)
            kth[c] = float(nth[int(k)])
        return out, kth


class PairAhead:
    """The look ahead of the first of two wells, for every second seat at once (feature 374 wave 155's `pair_keeps_ten`,
    vectorized by feature 387)."""

    __slots__ = ("hx", "hy", "sx", "sy")

    def __init__(self, seats: Sequence[tuple[float, float, float]], houses: Sequence[Mapping[str, Any]]) -> None:
        import numpy as np  # loaded when a well is seated, never at import (feature 237: no heavy library at import time)

        self.sx = np.asarray([c[1] for c in seats], dtype=float)
        self.sy = np.asarray([c[2] for c in seats], dtype=float)
        self.hx = np.asarray([float(h["x"]) for h in houses], dtype=float)
        self.hy = np.asarray([float(h["y"]) for h in houses], dtype=float)

    def keeps_ten(self, c: tuple[float, float, float], spacing: float = 170.0, most: int = 10) -> bool:
        """Would a first well at `c` leave a second seat, `spacing` px off it, with both wells nearest to no more than `most`
        households? Each household goes to its nearer well, the first on a tie (`wells.most_served_after`'s `min`).

        Research:
            no well serving more than ten - research/questions/0196-communal-wells-ido.drawing.html: the five to ten houses each dug well served at Karihama
            the second well held 170 px off the first - GUESS: searched, the record silent (feature 417 T29 pass C, 2026-10-25); the pair's spacing, `seat_wells`' own "wells apart"; no page gives a hamlet's wells' spacing"""
        import numpy as np

        if not len(self.sx):
            return False
        apart = np.hypot(self.sx - c[1], self.sy - c[2]) >= spacing
        to_c = np.hypot(self.hx - c[1], self.hy - c[2])[:, None]
        to_d = np.hypot(self.hx[:, None] - self.sx[None, :], self.hy[:, None] - self.sy[None, :])
        first = (to_c <= to_d).sum(axis=0)
        busiest = np.maximum(first, len(self.hx) - first)
        return bool(np.any(apart & (busiest <= most)))


class PoolScore:
    """`seat_wells`' sort key for a whole pool at once (feature 427 T05, D5): the key the pool is sorted by after each landed
    well - (serves more than ten, the minimax bucket of the worst walk plus the crop overreach, in the belt, the overreach, the
    worst walk, the neighborhood) - computed for every seat in one pass of array operations, where each seat used to walk every
    household against every standing well (`wells.most_served_after`, `wells.worst_after`): 2.19M inner calls of the wells'
    stage at 40 households (the feature's T01 survey). The seats-by-households distances are taken once per rung; per sort only
    each household's nearest standing well is.

    Research: plumbing - NONE: how `seat_wells`' own ranking (its claims) is computed"""

    __slots__ = ("hx", "hy", "nx", "ny", "row", "to_n", "to_s")

    def __init__(self, pool: Sequence[tuple[float, float, float]], served: Sequence[Mapping[str, Any]], needy: Sequence[Mapping[str, Any]]) -> None:
        import numpy as np  # loaded when a well is seated, never at import (feature 237: no heavy library at import time)

        self.row = {c: i for i, c in enumerate(pool)}
        sx = np.asarray([c[1] for c in pool], dtype=float)
        sy = np.asarray([c[2] for c in pool], dtype=float)
        self.hx = np.asarray([float(h["x"]) for h in served], dtype=float)
        self.hy = np.asarray([float(h["y"]) for h in served], dtype=float)
        self.nx = np.asarray([float(h["x"]) for h in needy], dtype=float)
        self.ny = np.asarray([float(h["y"]) for h in needy], dtype=float)
        self.to_s = np.hypot(sx[:, None] - self.hx[None, :], sy[:, None] - self.hy[None, :])  # seats x served households
        self.to_n = np.hypot(sx[:, None] - self.nx[None, :], sy[:, None] - self.ny[None, :])  # seats x needy households

    def keys(
        self,
        pool: Sequence[tuple[float, float, float]],
        placed: Sequence[Pt],
        standing: Sequence[float],
        box: tuple[float, float, float, float],
        r: float,
        in_belt: Callable[[tuple[float, float, float]], int],
        near_of: Mapping[tuple[float, float, float], float],
        most: int,
        bucket: float,
    ) -> list[tuple[int, float, int, float, float, float]]:
        """Each seat's key, in `pool`'s order. A household goes to a well at the seat only when strictly nearer than its nearest
        standing well, as `most_served_after`'s `min` over the wells in order keeps a tie with the standing one; the worst walk
        is `worst_after`'s, from `standing` (each needy household's walk to its nearest standing well); `most` and `bucket` are
        `seat_wells`' ceiling and walk bucket, its claims, handed in."""
        import numpy as np

        rows = np.asarray([self.row[c] for c in pool], dtype=np.int64)
        wx = np.asarray([p[0] for p in placed], dtype=float)
        wy = np.asarray([p[1] for p in placed], dtype=float)
        to_w = np.hypot(self.hx[:, None] - wx[None, :], self.hy[:, None] - wy[None, :])  # served households x standing wells
        nearest = to_w.argmin(axis=1)  # the first nearest, as `min(range(...))` takes it
        held = to_w[np.arange(len(self.hx)), nearest]
        base = np.bincount(nearest, minlength=len(placed))
        takes = self.to_s[rows] < held[None, :]  # seats x served: the households a well at the seat would take
        onehot = np.zeros((len(self.hx), len(placed)))
        onehot[np.arange(len(self.hx)), nearest] = 1.0
        left = base[None, :] - takes.astype(float) @ onehot  # each standing well's count once the seat's well has taken its own
        busiest = np.maximum(left.max(axis=1), takes.sum(axis=1)) if len(placed) else takes.sum(axis=1)
        worst = np.minimum(self.to_n[rows], np.asarray(standing, dtype=float)[None, :]).max(axis=1)
        sx = np.asarray([c[1] for c in pool], dtype=float)
        sy = np.asarray([c[2] for c in pool], dtype=float)
        bx0, bx1, by0, by1 = box
        over = np.maximum.reduce([np.zeros(len(pool)), bx0 - (sx - r), (sx + r) - bx1, by0 - (sy - r), (sy + r) - by1])
        return [(int(b > most), (w + e) // bucket, in_belt(c), e, w, near_of[c]) for c, b, w, e in zip(pool, busiest.tolist(), worst.tolist(), over.tolist(), strict=True)]
