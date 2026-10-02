"""`seat_cluster` with the dry plots' edges and the brook indexed once (feature 306): the hem and the brook's share are
asked of `seg_reach_index` grids, held to the scan of every segment - kept here as the ORACLE - point by point, and the
whole seat held to the seat the unpruned scan picks."""

import math
import random

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen import cluster as CL
from l7r.diagram.settlement import seg_dist
from l7r.diagram.settlement._geom import seg_reach_index

from ._builders import a_plan


def _segments(seed: int) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    rng = random.Random(seed)
    out = []
    for _ in range(40):
        x, y = rng.uniform(0, 1000), rng.uniform(0, 1000)
        out.append(((x, y), (x + rng.uniform(-200, 200), y + rng.uniform(-200, 200))))
    return out


@pytest.mark.parametrize("seed", range(4))
def test_the_nearest_under_the_reach_is_the_scans_minimum(seed: int) -> None:
    segs = _segments(seed)
    rng = random.Random(100 + seed)
    for reach in (30.0, 180.0):
        index = seg_reach_index([([a, b], 0.0) for a, b in segs], reach)
        under = 0
        for _ in range(300):
            px, py = rng.uniform(-100, 1100), rng.uniform(-100, 1100)
            scan = min(seg_dist(px, py, a, b) for a, b in segs)
            got = CL.nearest_within(index, px, py, reach)
            if scan < reach:
                under += 1
                assert got == scan
            else:
                assert got >= reach
        assert under > 20, "non-vacuous: points fall within the reach"


def test_the_oracle_notices_a_dropped_segment() -> None:
    """The comparison above would fail if the grid omitted the nearest segment: a grid that loses it answers a farther
    one (or the reach)."""
    segs = _segments(0)
    index = seg_reach_index([([a, b], 0.0) for a, b in segs], 180.0)
    px, py = segs[0][0]

    class Short:
        def near(self, x, y, pad=0.0):  # type: ignore[no-untyped-def]
            return [e for e in index.near(x, y, pad) if e[0] != segs[0][0]]

    assert CL.nearest_within(index, px, py, 180.0) == 0.0
    assert CL.nearest_within(Short(), px, py, 180.0) != min(seg_dist(px, py, a, b) for a, b in segs)


class _Unpruned:
    """A `seg_reach_index` stand-in that prunes nothing: every segment, its box the whole plane - the scan."""

    def __init__(self, lines, extra):  # type: ignore[no-untyped-def]
        self.items = [(pl[k], pl[k + 1], hw + extra, -math.inf, -math.inf, math.inf, math.inf) for pl, hw in lines for k in range(len(pl) - 1)]

    def near(self, px, py, pad=0.0):  # type: ignore[no-untyped-def]
        return self.items


def test_the_seat_is_the_one_the_unpruned_scan_picks(monkeypatch: pytest.MonkeyPatch) -> None:
    """A ragged field with dry plots near its northern margins and a brook across it: the indexed seat and its ladder
    are the scan's, to the last digit."""
    plan = a_plan()
    c = plan.W / 2.0
    rng = random.Random(7)
    plan.envelope = [(c + math.cos(t) * r, c + math.sin(t) * r) for t, r in ((math.tau * k / 40, rng.uniform(280, 340)) for k in range(40))]
    dry = [[(x, c - 420.0), (x + 90.0, c - 420.0), (x + 90.0, c - 350.0), (x, c - 350.0)] for x in (c - 300, c + 150)]
    brook = [(0.0, c - 380.0), (c - 100, c - 420.0), (c + 200, c - 360.0), (plan.W, c - 400.0)]
    asked: list[bool] = []
    keep = CL.nearest_within

    def counted(index, px, py, reach):  # type: ignore[no-untyped-def]
        d = keep(index, px, py, reach)
        asked.append(d < reach)
        return d

    monkeypatch.setattr(CL, "nearest_within", counted)
    seat = hg.seat_cluster(plan, dry_plots=dry, brook=brook)
    assert sum(asked) > 10 and not all(asked), "non-vacuous: the hem and the brook score some margins and not others"
    monkeypatch.setattr(CL, "seg_reach_index", _Unpruned)
    assert hg.seat_cluster(plan, dry_plots=dry, brook=brook) == seat
    assert seat["ladder"], "non-vacuous: more than one margin was scored"
