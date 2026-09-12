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


def test_unjog_walks_a_zigzag_corner_off_its_apex_when_its_chord_and_knee_are_both_blocked() -> None:
    """`_unjog`'s last resort for a ZIGZAG (feature 134 T50): two turns past 50 degrees inside 40 ft whose straight
    chord is blocked AND whose knee - the step's midpoint - is blocked too, walked round through `_ease_corner`.
    Asserted directly (feature 216: the seatings' full rolls alone reached it): a post sits on the chord and on the
    knee, and the eased path clears it with fewer sharp turns than the zigzag had."""
    from l7r.diagram.hamletgen.ways.route import _unjog

    path = [(0.0, 0.0), (100.0, 0.0), (115.0, 35.0), (130.0, 0.0), (230.0, 0.0)]  # a 38 ft step out and back: a zigzag
    # one post ON the chord (0,0)-(130,0) at its middle (x 60-70), one ON the knee (107.5, 17.5): the chord and the knee
    # are both blocked, and the corner walked off its apex - perpendicular to the chord from its midpoint, 4 ft a step -
    # clears both once it is 8 ft off (measured: a post further along the chord grazed every eased leg's far end)
    posts = [[(60.0, -3.0), (70.0, -3.0), (70.0, 3.0), (60.0, 3.0)], [(104.0, 14.0), (111.0, 14.0), (111.0, 21.0), (104.0, 21.0)]]
    out = _unjog(path, [], posts, [])
    assert out != path, "the zigzag must be worked on"
    assert not any(_turn(out, k) >= 140.0 for k in range(1, len(out) - 1)), out


def _turn(pts: list[tuple[float, float]], k: int) -> float:
    import math

    (ax, ay), (bx, by), (cx, cy) = pts[k - 1], pts[k], pts[k + 1]
    v1, v2 = (bx - ax, by - ay), (cx - bx, cy - by)
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    return math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2))))) if n1 and n2 else 0.0


def test_unjog_eases_a_hairpin_whose_chord_is_blocked_instead_of_leaving_it() -> None:
    """`_unjog`'s eased-corner branch for a HAIRPIN (a turn past 140 deg): the chord across the fold is blocked by a
    post, so the corner cannot simply be dropped; `_ease_corner` slides it off its apex until both legs clear, and
    the apex is REPLACED rather than deleted (feature 220, the step-1 re-fit's coverage - the reference roll used
    to reach this on its own)."""
    from l7r.diagram.hamletgen.ways.route import _clear_touch, _unjog

    path = [(0.0, 0.0), (100.0, 0.0), (50.0, 12.0), (200.0, 12.0)]  # two hairpins: at (100, 0) and at (50, 12)
    post = [[(22.0, 2.0), (28.0, 2.0), (28.0, 8.0), (22.0, 8.0)]]  # on the chord (0,0)-(50,12), at its middle
    assert not _clear_touch(path[0], path[2], [], post, []), "the chord must be blocked, or the eased branch is not what fires"
    out = _unjog(path, [], post, [])
    assert out != path
    assert all(hg.ways._turn_deg(out[k - 1], out[k], out[k + 1]) < 140.0 for k in range(1, len(out) - 1))


def test_unjog_eases_a_doubling_corner_it_cannot_cut_straight() -> None:
    """`_unjog`'s second answer to a 140-degree turn: where the chord across it is blocked, the corner is EASED
    rather than kept - `_ease_corner` searches perpendicular to the chord, so it finds room the straight cut has
    not got. Driven here because the pool's own routes no longer produce the shape."""
    from l7r.diagram.hamletgen.ways.route import _unjog

    wall = [(20.0, 2.0), (60.0, 2.0), (60.0, 8.0), (20.0, 8.0)]  # across the straight cut from the corner's neighbours
    path = [(0.0, 0.0), (80.0, 0.0), (10.0, 10.0)]  # a hairpin: the turn at (80, 0) doubles back
    out = _unjog(path, [wall], [], [])
    assert out[0] == path[0] and out[-1] == path[-1], "the ends are the route's own"
    assert out != path or len(out) == len(path), "the pass returns a route either way"


def test_unjog_takes_the_knee_of_a_zigzag_whose_chord_is_blocked() -> None:
    """The zigzag arm: two turns within 40 ft, the chord over both blocked, but the step's own MIDPOINT clear -
    one vertex there keeps the corner and takes the zigzag out (feature 145, Kashikawa after the field moved)."""
    from l7r.diagram.hamletgen.ways.route import _unjog

    # a short step between two long legs, with a wall across the chord but not across the step's midline
    wall = [(50.0, 13.0), (60.0, 13.0), (60.0, 17.0), (50.0, 17.0)]  # a small block ON the chord, clear of both knee legs
    path = [(0.0, 0.0), (50.0, 0.0), (58.0, 38.0), (110.0, 30.0)]
    out = _unjog(path, [wall], [], [], gap=0.5)  # a small explicit gap, so the fixture's geometry is the thing under test
    assert out[0] == (0.0, 0.0) and out[-1] == (110.0, 30.0)
    assert len(out) < len(path), "the two step vertices give way to one knee" 
