"""Feature 269 group E6: the homesteads' woods (B26), the commons' own stocking (B28) and the bamboo under the belt (B29)."""

import math
import random

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import CanopyArea, CrownIndex
from l7r.diagram.settlement.homestead_parts.groves import BAMBOO_CULM, GROVE_BAMBOO_SHARE, HOMESTEAD_WOOD_FT2, bamboo_mark
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
    n = sum(s._draw_grove(200.0 + 60 * (k % 12), 300.0 + 60 * (k // 12), 28.0, 28.0, face=(0, -1), mix="windbreak") for k in range(48))
    ink = "".join(str(o) for o in s.out)
    assert n > 0 and ink.count(f'stroke="{BAMBOO_CULM}"') == n, "every counted bamboo mark is inked, and nothing else in its color"
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
    """B26 (0036): seating stops once the clumps cover the goal, and a short first pass is topped up."""
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


def test_the_woodland_commons_seats_no_crown_in_a_plots_sun():
    """Feature 310 (GM 2026-10-02: "no canopy trees should be exempt"): a commons beside a yard throws no crown into the
    yard's sun ground, and stands elsewhere."""
    from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT, trees_shading_plots

    s = _hamlet()
    s.sun_corridor(39)
    s.M["threshing_yards"] = [{"x": 400.0, "y": 280.0, "w": 40.0, "h": 20.0}]  # its sun ground runs 270..340 deep into the wood
    s.commons([(300.0, 300.0), (500.0, 300.0), (500.0, 500.0), (300.0, 500.0)], role="woodland")
    assert s.M["tree_crowns"], "non-vacuity: the wood stands"
    assert trees_shading_plots(s.M, CANOPY_SHADE_FT) == []


def test_a_thin_dooryard_band_runs_its_trees_its_whole_length() -> None:
    """Feature 310 (the homestead grove's glyph-check): a band at least twice as long as wide in the dooryard mix spreads its
    few trees along its whole length - no stretch of it left bare - lying either way."""
    for w, h in ((17.0, 54.0), (54.0, 17.0)):
        s = _hamlet()
        s._draw_grove(400.0, 400.0, w, h, (1, 0), mix="dooryard", cls="homestead grove", bamboo=False)
        tc = s.M["tree_crowns"]
        along = sorted(tc[i + 1] if h > w else tc[i] for i in range(0, len(tc), 3))
        assert len(along) >= 3, "non-vacuity: the band drew its trees"
        lo, hi = 400.0 - max(w, h) / 2, 400.0 + max(w, h) / 2
        steps = [along[0] - lo, *(b - a for a, b in zip(along, along[1:], strict=False)), hi - along[-1]]
        assert max(steps) < max(w, h) / 2, (w, h, steps)
        discs = [(tc[i + 1] if h > w else tc[i], tc[i + 2]) for i in range(0, len(tc), 3)]
        bare = (min(c - r for c, r in discs) - lo, hi - max(c + r for c, r in discs))
        assert max(bare) <= 0.0, ("a crown reaches each end of the band, where it joins the belt", w, h, bare)


def test_a_clumps_bamboo_marks_keep_out_of_a_plots_sun_and_are_recorded() -> None:
    """Feature 315: a culm mark in a yard's sun ground at bamboo's reach is not inked, and every inked mark is recorded in
    `bamboo_marks` [x, y, r] - the record the map's check reads."""
    from l7r.diagram.settlement.homestead_parts.tree_shade import BAMBOO_SHADE_FT, bamboo_shading_plots

    def draw(yard: bool) -> tuple[int, Settlement]:
        s = _hamlet()
        s.sun_corridor(39)
        if yard:
            s.M["threshing_yards"] = [{"x": 400.0, "y": 380.0, "w": 200.0, "h": 30.0}]  # its sun ground covers the grove's south half
        n = s._draw_grove(400.0, 400.0, 320.0, 120.0, (0, -1), mix="windbreak", cls="homestead grove", bamboo=True)
        return n, s

    n_open, open_ = draw(False)
    n_sun, sunny = draw(True)
    assert n_open == len(open_.M["bamboo_marks"]) > 0, "non-vacuity: marks inked and recorded"
    assert n_sun == len(sunny.M.get("bamboo_marks") or []) < n_open, "the sun ground took some"
    assert bamboo_shading_plots(sunny.M, BAMBOO_SHADE_FT) == []


def test_no_crown_is_drawn_under_a_yard_persimmons_crown():
    """GM 2026-10-02: a yard persimmon is inked over every grove; 0046 (feature 328): "the grove's trees give way round it" -
    every crown, not the conifer alone (`_draw_grove`'s `_trees`), and wholly: no crown's edge under the persimmon's disc
    (batch 1's glyph checks: the 0.8 share let edges reach 3.7 and 4.1 ft under one)."""
    import math

    s = _hamlet()
    s.M["houses"] = [{"x": 2000.0, "y": 2000.0, "w": 40.0, "h": 30.0, "geom": {"fixtures": {"persimmon": (300.0, 300.0, 60.0)}}}]
    for k in range(9):
        s._draw_grove(270.0 + 30 * (k % 3), 270.0 + 30 * (k // 3), 28.0, 28.0, face=(0, -1), mix="windbreak")
    crowns = [(s.M["tree_crowns"][i], s.M["tree_crowns"][i + 1], s.M["tree_crowns"][i + 2]) for i in range(0, len(s.M["tree_crowns"]), 3)]
    assert crowns, "non-vacuity: the clumps drew crowns"
    assert all(math.hypot(c[0] - 300.0, c[1] - 300.0) >= 30.0 + c[2] for c in crowns), "no crown's edge under the persimmon's crown"


@pytest.mark.parametrize("mix", ["windbreak", "dooryard", "mixed_broadleaf"])
def test_every_grove_crown_is_drawn_in_the_woods_one_band(mix: str) -> None:
    """0080 (feature 328): each crown is drawn 0.75 to 1.4 times the mean radius - one band, a conifer no wider (it was
    0.72-1.05 or 1.25-1.7, and a conifer 15% wider)."""
    from l7r.diagram.settlement.homestead_parts.groves import CROWN_S

    s = _hamlet()
    sum(s._draw_grove(200.0 + 60 * (k % 4), 200.0 + 60 * (k // 4), 50.0, 50.0, face=(0, -1), mix=mix) for k in range(16))
    r0 = s.px(s.CANOPY_R_FT)
    radii = [s.M["tree_crowns"][i + 2] for i in range(0, len(s.M["tree_crowns"]), 3)]
    assert len(radii) > 20, "non-vacuity"
    assert all(CROWN_S[0] * r0 - 0.06 <= r <= CROWN_S[1] * r0 + 0.06 for r in radii), (min(radii) / r0, max(radii) / r0)


def test_a_windbreak_draws_about_half_its_crowns_conifer() -> None:
    """0072 (feature 328 wave 39, impl-drift): "735 of them, 48%, were cedar" - of the CROWNS; the bamboo items draw none,
    so the conifer's 0.48 is taken of the crowns, not of all the items (it drew about 52%)."""
    s = _hamlet()
    tally: dict[str, int] = {}
    for k in range(256):
        s._draw_grove(200.0 + 90 * (k % 16), 200.0 + 90 * (k // 16), 60.0, 60.0, face=(0, -1), mix="windbreak", tally=tally)
    crowns = tally.get("conifer", 0) + tally.get("broadleaf", 0)
    assert crowns > 300, "non-vacuity"
    # the kind is rolled where the crown is seated, against the clump's drawn deficit (wave 54): it was 0.508 drawn when it was
    # thrown with the crown, the cull being asymmetric (a lesser crown over a conifer is not drawn)
    assert abs(tally["conifer"] / crowns - 0.48) < 0.01, tally  # measured 0.479 (1,336 of 2,791)


def test_a_grove_throws_one_crown_to_about_180_sq_ft_at_every_grain() -> None:
    """0080 (feature 328 wave 53): 600 trees a hectare, one to about 180 sq ft - in real feet, so a hamlet at 1 ft/px
    throws no more than a clump's area over 180 sq ft (it threw one to ~71 sq ft: 48 sq px at the town grain, scaled
    by the building grain)."""
    from l7r.diagram.settlement.homestead_parts.groves import GROVE_CROWN_SQFT, grove_crown_px2

    assert abs(GROVE_CROWN_SQFT - 179.4) < 0.1
    assert grove_crown_px2(1.0) == GROVE_CROWN_SQFT and abs(grove_crown_px2(2.0) - GROVE_CROWN_SQFT / 4) < 1e-9
    s = _hamlet()
    tally: dict[str, int] = {}
    s._draw_grove(400.0, 400.0, 120.0, 120.0, face=(0, -1), mix="mixed_broadleaf", tally=tally)
    drawn = sum(tally.values())
    want = round(120.0 * 120.0 / GROVE_CROWN_SQFT)
    # ...AND DRAWN AT IT (wave 55, the homestead grove's glyph-check of Mizuguchi: the culls left ~400 sq ft a crown): an open
    # clump is topped up until its drawn crowns hold its ground at the page's density
    assert 0.9 * want <= drawn <= want, (drawn, want, tally)


def test_a_clumps_open_share_is_the_grid_left_by_what_covers_it() -> None:
    """`open_share` (feature 328 wave 55): the share of the clump's box a crown may stand on - a grid at the crown's radius,
    less every point a keep-out, an earlier stand or a persimmon covers."""
    from l7r.diagram.settlement.homestead_parts.groves import open_share

    assert open_share(0.0, 0.0, 40.0, 40.0, 10.0, lambda x, y: False) == 1.0
    assert open_share(0.0, 0.0, 40.0, 40.0, 10.0, lambda x, y: x < 0) == 0.5
    assert open_share(0.0, 0.0, 4.0, 4.0, 10.0, lambda x, y: False) == 1.0, "a box smaller than the step: one point"


def test_no_crown_is_topped_up_over_the_bamboo_patch() -> None:
    """Wave 55's top-up (impl-drift): the farm's bamboo patch is its culms' ground - no crown is thrown over it, the throw's or
    the top-up's."""
    s = _hamlet()
    box = (340.0, 340.0, 400.0, 460.0)  # the clump's west half
    s._draw_grove(400.0, 400.0, 120.0, 120.0, face=(0, -1), mix="windbreak", bamboo_box=box)
    xs = [s.M["tree_crowns"][i] for i in range(0, len(s.M["tree_crowns"]), 3)]
    assert len(xs) > 20, "non-vacuity: the east half drawn"
    assert all(x >= 400.0 - 1e-6 for x in xs), min(xs)


def test_no_coppice_crown_stands_in_a_marsh() -> None:
    """0074 (feature 328 wave 57): woody growth stops at the marsh's edge - the coppice's crowns thinned 46 ft into it over the
    grass's ramp; none is seated inside it now."""
    from shapely.geometry import Point, Polygon

    s = _hamlet()
    marsh = [(400.0, 300.0), (500.0, 300.0), (500.0, 500.0), (400.0, 500.0)]
    s.commons([(300.0, 300.0), (500.0, 300.0), (500.0, 500.0), (300.0, 500.0)], role="woodland", soft=[marsh])
    crowns = [(s.M["tree_crowns"][i], s.M["tree_crowns"][i + 1]) for i in range(0, len(s.M["tree_crowns"]), 3)]
    assert len(crowns) > 20, "non-vacuity: the dry half is stocked"
    assert not any(Polygon(marsh).contains(Point(c)) for c in crowns), "a crown in the marsh"
