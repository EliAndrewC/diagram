"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways import _route


def test_route_returns_nothing_when_the_way_is_genuinely_blocked() -> None:
    """[] is a real answer. The alternative - drawing something anyway - is what produced a 38 ft
    mark 71 ft from the house it served, touching nothing, to cure a one-foot violation."""
    wall = [(40.0, -400.0), (60.0, -400.0), (60.0, 400.0), (40.0, 400.0)]
    assert hg.ways._route((0.0, 0.0), (100.0, 0.0), [wall], [], [], cell=10.0) == []


def test_a_routed_path_never_passes_nearer_than_it_planned_for() -> None:
    """THE PROPERTY THE LATTICE HAS TO GUARANTEE, and did not.

    A cell was marked free by testing its CENTER, so the drawn line through a free cell could pass
    half a cell nearer an obstacle than its center did - seven feet, at a 14 ft cell. Three web lanes
    on a cohort map came within 4.0 ft of a farmhouse corner having been planned at 7, and a
    farmhouse ended up standing on the lane. This asserts the guarantee directly rather than the
    implementation: every point of the returned path clears the obstacle by the requested margin."""
    wall = [(200.0, 0.0), (240.0, 0.0), (240.0, 300.0), (200.0, 300.0)]
    gap = 7.0
    for cell in (10.0, 14.0):
        path = hg.ways._route((0.0, 400.0), (400.0, 400.0), [], [wall], [], cell=cell, gap=gap)
        assert path, f"a way round the wall exists at cell {cell}"
        worst = min(
            hg.ways.seg_dist(q[0], q[1], wall[k], wall[(k + 1) % len(wall)])
            for a, b in zip(path, path[1:], strict=False)
            for q in [(a[0] + (b[0] - a[0]) * i / 20, a[1] + (b[1] - a[1]) * i / 20) for i in range(21)]
            for k in range(len(wall))
        )
        assert worst >= gap - 0.5, f"at cell {cell} the path came within {worst:.1f} ft, planned for {gap}"


def test_route_pad_mult_is_what_lets_a_link_go_the_long_way_round() -> None:
    """A search box sized at 0.75x the gap has room for a path BETWEEN two steadings and nowhere near
    enough to find the way AROUND a field - it reported NO ROUTE for a journey that plainly exists,
    and that was a dozen houses counting as unreachable on one cohort seed."""
    barrier = [(180.0, -400.0), (220.0, -400.0), (220.0, 260.0), (180.0, 260.0)]
    a, b = (60.0, 0.0), (340.0, 0.0)
    assert hg.ways._route(a, b, [], [barrier], [], cell=12.0, pad_mult=0.75) == [], "the short box cannot see the way round"
    assert hg.ways._route(a, b, [], [barrier], [], cell=12.0, pad_mult=2.0), "the long box can"


def test_the_router_declines_a_span_too_wide_for_its_lattice() -> None:
    """A connector's span is the whole canvas, and the router says so by returning nothing.

    This is pinned rather than left to a `no cover` pragma because the OLD pragma asserted the
    opposite - that the pad was bounded so the grid could never overflow - and a reader who believed
    it would look for the reason a connector is not detoured in the wrong place entirely."""
    assert _route((0.0, 0.0), (4000.0, 0.0), [], [], []) == []


def test_unjog_takes_the_lattice_step_out_when_the_chord_is_clear() -> None:
    """Two turns past 50 degrees within 40 ft is the check's zigzag (seed 14: 7 ft up, 13 ft back)."""
    path = [(0.0, 0.0), (60.0, 0.0), (60.0, 7.0), (47.0, 7.0), (47.0, 60.0)]
    out = hg.ways._unjog(path, [], [], [])
    assert out == [(0.0, 0.0), (60.0, 0.0), (47.0, 60.0)] or out == [(0.0, 0.0), (47.0, 7.0), (47.0, 60.0)]
    assert all(hg.ways._turn_deg(out[k - 1], out[k], out[k + 1]) < 140.0 for k in range(1, len(out) - 1))


def test_unjog_keeps_the_jog_the_ground_forces() -> None:
    """A wall across the chord: the steps stay, because the chord would cross it."""
    wall = [(50.0, 2.0), (58.0, 2.0), (58.0, 5.0), (50.0, 5.0)]
    path = [(0.0, 0.0), (60.0, 0.0), (60.0, 7.0), (47.0, 7.0), (47.0, 60.0)]
    assert hg.ways._unjog(path, [wall], [], []) == path


def test_easing_a_corner_refuses_a_chord_too_short_to_have_a_normal() -> None:
    """The offset is measured along the chord's unit NORMAL, so a chord of no length has no normal to
    measure along - two coincident vertices would divide by ~zero. There is also nothing to ease: a
    jog whose two ends are the same point is not a corner. `None` puts the caller back on its other
    passes, which is the documented contract."""
    assert hg.ways._ease_corner((100.0, 100.0), (110.0, 108.0), (100.0, 100.0), [], [], []) is None
    assert hg.ways._ease_corner((100.0, 100.0), (110.0, 108.0), (100.4, 100.3), [], [], []) is None


def test_an_eased_corner_may_not_itself_be_a_hairpin() -> None:
    """The point of easing is to keep the way going ROUND what is there, the way a trodden path does.
    Sliding the corner far off a short chord replaces one hairpin with another - the two legs fold
    back on each other - so those candidates are skipped, and when every offset folds, the jog is left
    for the caller's other passes rather than swapped for an equally bad one.

    Ground is completely clear here, so nothing but the fold rule can be refusing them."""
    a, b = (0.0, 0.0), (2.0, 0.0)  # a 2 ft chord: every offset the search tries is wider than it
    apex = (1.0, 4.0)
    assert hg.ways._ease_corner(a, apex, b, [], [], []) is None
    for i in range(1, hg.ways._EASE_STEPS + 1):
        off = hg.ways._EASE_FT * i / hg.ways._EASE_STEPS
        assert hg.ways._turn_deg(a, (1.0, off), b) >= 140.0, "every candidate must fold, or this proves nothing"
    # ...and a chord long enough for the same offsets eases cleanly
    wide = hg.ways._ease_corner((0.0, 0.0), (60.0, 12.0), (120.0, 0.0), [], [], [])
    assert wide is not None and len(wide) == 1
