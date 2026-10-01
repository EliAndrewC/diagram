"""Feature 269 group E6: the homesteads' woods (B26), the commons' own stocking (B28) and the bamboo under the belt (B29)."""

import math
import random

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import CanopyArea, CrownIndex
from l7r.diagram.settlement.homestead_parts.groves import GROVE_BAMBOO_SHARE, HOMESTEAD_WOOD_FT2, bamboo_mark
from l7r.diagram.settlement.homestead_parts.wood_goal import rolled_wood
from tests.settlement._builders import _nuc_village


def _hamlet() -> Settlement:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1)
    return s


def test_crown_index_gives_the_linear_seat_test_s_verdict():
    """The grid must never change a verdict: every candidate is judged as `_crown_seat_clear` judges it over the list."""
    rng = random.Random(7)
    seated = [(rng.uniform(0, 200), rng.uniform(0, 200), rng.uniform(3, 14)) for _ in range(120)]
    idx = CrownIndex(seated)
    for _ in range(600):
        x, y, r = rng.uniform(-20, 220), rng.uniform(-20, 220), rng.uniform(3, 14)
        assert idx.clear(x, y, r) == Settlement._crown_seat_clear(x, y, r, seated)
    idx.add(500.0, 500.0, 4.0)
    assert not idx.clear(502.0, 500.0, 4.0) and idx.clear(505.0, 500.0, 4.0)


def test_canopy_area_counts_the_union_of_its_discs():
    a = CanopyArea(0.5)
    a.add(0.0, 0.0, 10.0)
    assert abs(a.area - math.pi * 100) < 0.03 * math.pi * 100
    a.add(0.0, 0.0, 10.0)  # the same disc again adds nothing
    assert abs(a.area - math.pi * 100) < 0.03 * math.pi * 100
    a.add(100.0, 0.0, 10.0)
    assert abs(a.area - 2 * math.pi * 100) < 0.03 * 2 * math.pi * 100


def test_a_homestead_wood_rolls_inside_the_register_s_range():
    lo, hi = HOMESTEAD_WOOD_FT2
    assert rolled_wood(0.0, HOMESTEAD_WOOD_FT2) == lo and abs(rolled_wood(1.0, HOMESTEAD_WOOD_FT2) - hi) < 1e-6
    assert lo < rolled_wood(0.5, HOMESTEAD_WOOD_FT2) < 14000.0  # log-uniform: the middle of the roll near the register's middle wood


def test_the_woodland_commons_is_stocked_as_a_coppice_thicket():
    """B28 (vegetation/230): about one crown to 63 sq ft, each 8-9 ft across - not the hill wood's 540 sq ft and 13-23 ft."""
    s = _hamlet()
    poly = [(300.0, 300.0), (500.0, 300.0), (500.0, 500.0), (300.0, 500.0)]
    s.commons(poly, role="woodland")
    rec = s.M["commons"][-1]
    assert rec["crowns"] >= 0.8 * (200 * 200) / 64, rec["crowns"]  # the stated stocking, less the thinned edge
    radii = s.M["tree_crowns"][2::3]
    assert radii and all(4.0 <= r <= 4.5 for r in radii)


def test_a_windbreak_clump_inks_bamboo_only_in_the_open():
    """B29 (vegetation/260): the windbreak mix carries bamboo items, inked as the culm mark where no crown covers them."""
    s = _hamlet()
    n = sum(s._draw_grove(200.0 + 60 * k, 300.0, 28.0, 28.0, face=(0, -1), mix="windbreak") for k in range(12))
    ink = "".join(str(o) for o in s.out)
    assert n > 0 and ink.count('stroke="#9AAE3C"') == n, "every counted bamboo mark is inked, and nothing else in its color"
    crowns = [(s.M["tree_crowns"][i], s.M["tree_crowns"][i + 1], s.M["tree_crowns"][i + 2]) for i in range(0, len(s.M["tree_crowns"]), 3)]
    assert crowns, "non-vacuity: the clumps drew crowns too"
    assert 0 < GROVE_BAMBOO_SHARE < 0.2
    assert s._draw_grove(900.0, 900.0, 28.0, 28.0, face=(0, -1), mix="dooryard") == 0, "the dooryard mix carries no bamboo"


def test_bamboo_under_a_crown_or_on_a_roof_is_not_inked():
    """A bamboo item under an earlier crown is hidden from above; one on a building is refused like a crown."""
    s = _hamlet()
    s.M["tree_crowns"] = [300.0, 297.0, 40.0]  # one wide earlier crown over the whole clump
    assert s._draw_grove(300.0, 300.0, 28.0, 28.0, face=(0, -1), mix="windbreak") == 0
    s2 = _hamlet()
    s2.M["houses"] = [{"x": 300.0, "y": 300.0, "w": 60.0, "h": 60.0}]
    assert s2._draw_grove(300.0, 300.0, 28.0, 28.0, face=(0, -1), mix="windbreak") == 0


def test_bamboo_mark_is_two_culms_and_a_fork():
    mark = bamboo_mark(10.0, 20.0, 1.0, 0.0, 0.5)
    assert mark.count("<path") == 2 and 'M8.8,20.0 l0.0,-5.0' in mark


def test_a_copse_with_an_area_goal_stops_at_it_and_fills_toward_it():
    """B26 (rendering/homesteads/010): seating stops once the clumps cover the goal, and a short first pass is topped up."""
    poly = [(150, 300), (560, 300), (560, 700), (150, 700)]
    s = _nuc_village()
    free = s.village_grove(poly, role="copse", dense=False)
    s_small = _nuc_village()
    small = s_small.village_grove(poly, role="copse", dense=False, area=2000.0)
    assert 0 < small < free
    s_big = _nuc_village()
    big = s_big.village_grove(poly, role="copse", dense=False, area=1e9)
    assert big > free, "the offset passes seat more than the one grid did"
    cl = s_big.M["village_groves"][0]["clumps"]
    step = 32 * s_big.bscale
    assert all(math.dist(cl[k], cl[j]) >= step * 0.55 - 0.2 for k in range(free, len(cl)) for j in range(k)), "a topped-up clump never stacks on another"
    s_none = _nuc_village()
    assert s_none.village_grove(poly, role="copse", dense=False, area=0.0) == 0


def test_a_lone_yashikirin_is_held_inside_the_register_s_range():
    """B26: the ~6:1 target is clamped to 6,000-28,000 sq ft. A 10 x 10 ft house asks 600 sq ft at 6:1, which its base
    arms (14 ft deep) already cover; held to 6,000, the open arms deepen to their cap (36 ft) and still fall short."""
    s = _hamlet()
    arms = s._find_grove_arms(500.0, 500.0, 10.0, 10.0)
    assert arms, "an open site grows its arms"
    assert max(min(w, h) for _cx, _cy, w, h, _face, _depth in arms) >= 35.0


def test_the_roll_is_taken_within_what_the_ground_can_hold() -> None:
    """Feature 294 B9: the attainable band - no less than the belt and the groves give, no more than the ground holds, inside
    the register's range; a ground giving more than the register's largest wood is one value."""
    from l7r.diagram.settlement.homestead_parts.wood_goal import attainable_band, copse_goal

    lo, hi = HOMESTEAD_WOOD_FT2
    assert attainable_band(0.0, 1e9) == (lo, hi)
    assert attainable_band(9000.0, 12000.0) == (9000.0, 12000.0)
    assert attainable_band(30000.0, 31000.0) == (30000.0, 30000.0)
    assert attainable_band(1000.0, 2000.0) == (lo, lo), "the floor stands even where the ground cannot hold it"
    goal, mean = copse_goal([0.0, 1.0], given_px2=2 * 9000.0, kept_px2=0.0, capacity_px2=2 * 3000.0, px2_per_ft2=1.0)
    assert (goal, mean) == (3000.0, 10500.0)
    goal, mean = copse_goal([0.0, 0.0], given_px2=2 * 9000.0, kept_px2=2 * 2000.0, capacity_px2=2 * 3000.0, px2_per_ft2=1.0)
    assert (goal, mean) == (4000.0, 11000.0), "the reserved seats always stand, so the floor counts them"
    assert copse_goal([], 1.0, 1.0, 1.0, 1.0) == (0.0, 0.0)


def test_the_copse_is_trimmed_back_to_its_goal_and_never_below_its_reserved_seats() -> None:
    from l7r.diagram.settlement.homestead_parts.wood_goal import canopy_of, trim_to_goal

    seats = [(float(i * 30), 0.0) for i in range(10)]  # ten crowns of radius 10, apart: each ~314 px^2
    one = canopy_of(seats[:1], 10.0, 1.0)
    kept = frozenset({seats[9]})
    out = trim_to_goal(seats, kept, 10.0, 1.0, 3.4 * one)
    assert seats[9] in out and len(out) == 3, "the reserved seat, then the shortest run nearest the goal"
    assert trim_to_goal(seats, kept, 10.0, 1.0, 0.0) == [seats[9]]
    assert len(trim_to_goal(seats, kept, 10.0, 1.0, 3.6 * one)) == 4
