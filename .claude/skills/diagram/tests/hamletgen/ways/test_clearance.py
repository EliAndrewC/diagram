"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import point_in_poly

from .._builders import SQUARE


def test_a_way_cutting_the_field_is_bent_ROUND_it_not_nibbled_at() -> None:
    """`route_around` walks the outline between where a leg enters and where it leaves.

    The first version inserted one waypoint at the mean of the crossings and re-ran; it converged a
    few px per round and ran out of rounds still crossing, because a point pushed off the middle of
    a lobe lands right beside the leg it came from. Both the detour and the odd-hit case (a leg that
    enters and does not leave) are asserted, and so is the do-nothing case."""
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    bent = hg.route_around(square, [(-50.0, 50.0), (150.0, 50.0)], 8.0)
    assert len(bent) > 2, "a leg straight through the square must gain waypoints"
    for q in bent:
        assert not point_in_poly(q[0], q[1], square), f"{q} is still inside the crop"
    clear = [(-50.0, 200.0), (150.0, 200.0)]
    assert hg.route_around(square, clear, 8.0) == clear, "a way that never touches the field is left alone"
    stub = hg.route_around(square, [(50.0, 50.0), (150.0, 50.0)], 8.0)  # STARTS inside: one crossing, not two
    assert not point_in_poly(stub[0][0], stub[0][1], square)


def test_a_way_is_clipped_where_the_crop_begins() -> None:
    """`clip_to_clear` truncates rather than dragging a vertex, and returns NOTHING when the
    surviving run is too short to be a lane - the arm is simply not drawn."""
    assert hg.clip_to_clear([(0.0, 0.0), (100.0, 0.0)], [], 10.0) == [(0.0, 0.0), (100.0, 0.0)]
    clipped = hg.clip_to_clear([(0.0, 700.0), (900.0, 700.0)], [SQUARE], 10.0)
    assert clipped and max(p[0] for p in clipped) < 400.0
    assert hg.clip_to_clear([(395.0, 700.0), (900.0, 700.0)], [SQUARE], 10.0) == []


def test_a_way_is_clipped_at_a_watercourse_as_well_as_at_a_crop() -> None:
    """A cluster's lane arms stop at the bank: they serve the houses, and a lane that crosses a ditch
    gets a deck sized for whatever angle it happens to meet the water at."""
    ditch = [((500.0, 0.0), (500.0, 400.0))]
    clipped = hg.clip_to_clear([(100.0, 200.0), (900.0, 200.0)], [], 10.0, lines=ditch)
    assert clipped and max(p[0] for p in clipped) < 500.0, "the arm must stop short of the water"
    assert hg.clip_to_clear([(100.0, 200.0), (300.0, 200.0)], [], 10.0, lines=ditch) == [(100.0, 200.0), (300.0, 200.0)], "a run that never reaches the water is untouched"


# ---- feature 123: the lane web -------------------------------------------------------------------


def test_clear_runs_returns_every_run_not_just_the_first_or_longest() -> None:
    """A back lane interrupted by a steading is two lanes, not one shortened one.

    This is the whole difference from `clip_to_clear`, which stops at the first blockage - right for
    an arm radiating out of the cluster, wrong for a way that runs the length of the settlement and
    whose two ends are just its two ends. Measured when it was wrong: Inashiro's back lanes came back
    as 250 ft of an intended 1,400 because the sampling happened to start in the crop."""
    line = [(0.0, 0.0), (1000.0, 0.0)]
    blocker = [(400.0, -50.0), (500.0, -50.0), (500.0, 50.0), (400.0, 50.0)]
    runs = hg.clear_runs(line, [blocker], 10.0)
    assert len(runs) == 2, "the run before the blocker and the run after it"
    assert all(len(r) >= 2 for r in runs)
    assert runs[0][0][0] < 400.0 < runs[1][-1][0]


def test_clear_runs_holds_the_settlement_fabric_at_a_closer_margin_than_the_crop() -> None:
    """Two obstacle families on purpose: a web lane may not go near the crop at all, but it threads
    BETWEEN the steadings - it IS the leftover room between two plots. Held 20 ft off every wall
    there would be nowhere for it to be."""
    line = [(0.0, 0.0), (400.0, 0.0)]
    wall = [(190.0, 12.0), (210.0, 12.0), (210.0, 40.0), (190.0, 40.0)]  # 12 ft off the line
    assert len(hg.clear_runs(line, [wall], 20.0)) == 2, "as HARD ground, 20 ft, it severs the line in two"
    assert len(hg.clear_runs(line, [], 20.0, tight=[wall], tight_margin=6.0)) == 1, "as fabric, 6 ft, the lane passes unbroken"


def test_clear_runs_floor_admits_a_short_footpath_to_a_door() -> None:
    """The 70 ft floor is right for a through-lane and wrong for the path from an outlying
    steading's door to the nearest way, which is 60-odd feet by construction. Refusing those as
    stubs left eight houses unreachable while a path to each was drawn and thrown away."""
    short = [(0.0, 0.0), (60.0, 0.0)]
    assert hg.clear_runs(short, [[(500.0, 500.0), (510.0, 500.0), (510.0, 510.0)]], 20.0) == []
    assert hg.clear_runs(short, [[(500.0, 500.0), (510.0, 500.0), (510.0, 510.0)]], 20.0, floor=20.0)


def test_clear_link_requires_the_WHOLE_span_not_a_piece_of_it() -> None:
    """Accepting the first surviving run let a snap be drawn across ground that had been clipped out
    of the middle - the run existed, it just was not the gap being bridged."""
    blocker = [(45.0, -30.0), (55.0, -30.0), (55.0, 30.0), (45.0, 30.0)]
    assert hg.ways._clear_link((0.0, 0.0), (100.0, 0.0), [blocker], [], []) is False
    assert hg.ways._clear_link((0.0, 0.0), (30.0, 0.0), [blocker], [], []) is True
    assert hg.ways._clear_link((0.0, 0.0), (0.2, 0.0), [blocker], [], []) is True, "a zero-length link is trivially clear"


def test_a_rewrite_may_leave_a_lane_no_worse_than_it_found_it() -> None:
    """Lifted out of `_touch_junctions` so it can be asked with plain lists (GM 2026-08-28). Both of
    its rules are NO WORSE THAN IT WAS, not GOOD, and that asymmetry is the whole design: the pass
    moving a lane is not the pass that owns it, so it must not make things worse and is not asked to
    make them better.

    The motivating measurements are in the docstring - footpaths drawn 5.2 ft clear of a garden that
    came out of this pass at 1.21 ft, and one accepted with no bend that came out turning 90 degrees
    and then 60 within 34 ft. Neither is reachable from a rolled map without reproducing the cohort
    seed that produced it."""
    garden = [(100.0, 100.0), (140.0, 100.0), (140.0, 140.0), (100.0, 140.0)]
    clear = [(0.0, 200.0), (300.0, 200.0)]  # 60 ft off the garden
    # 2 ft off it - inside the `bar`, which caps the requirement at `_TOUCH_GAP`: the rule asks a
    # rewrite to be no worse than the lane was OR no worse than its own keep-out, whichever forgives
    # more, so a move that merely closes 60 ft to 5 is allowed and one that closes it to 2 is not.
    nearer = [(0.0, 142.0), (300.0, 142.0)]

    assert hg.ways.fabric_clearance(clear, [garden]) > hg.ways.fabric_clearance(nearer, [garden])
    assert hg.ways.fabric_clearance(clear, []) == float("inf"), "no fabric, nothing to be near"
    assert hg.ways.fabric_clearance([(0.0, 200.0)], [garden]) == float("inf"), "a point is not a run"

    # a rewrite that walks a clear lane INTO the fabric is refused...
    assert hg.ways.may_write(clear, nearer, 3.0, [garden]) is False
    # ...and the same rewrite in reverse - a lane already inside the bar, moving away - is allowed
    assert hg.ways.may_write(nearer, clear, 3.0, [garden]) is True
    # ...as is leaving a lane exactly where it was
    assert hg.ways.may_write(nearer, list(nearer), 3.0, [garden]) is True

    # THE BEND HALF: a rewrite may not fold a lane that had no fold in it...
    straight = [(0.0, 500.0), (100.0, 500.0), (200.0, 500.0)]
    folded = [(0.0, 500.0), (100.0, 500.0), (20.0, 505.0)]  # a hairpin: the run doubles back on itself
    assert hg.ways._bends_badly(folded) and not hg.ways._bends_badly(straight)
    assert hg.ways.may_write(straight, folded, 3.0, []) is False
    # ...but a lane that was already folded is not required to unfold itself
    assert hg.ways.may_write(folded, list(folded), 3.0, []) is True


def test_a_nub_at_the_TAIL_of_a_way_is_dropped_too() -> None:
    """`drop_end_nubs` checks BOTH ends, by reversing between the two checks - and the second check
    needs its own test, because only one map in the suite ever presented a trailing nub.

    The shape: a long straight run whose LAST point doubles back a few feet. The head is clean (its
    first stretch is 100 ft, far over `_NUB_FT` = 9), so a test that only ever fed a leading nub would
    pass identically with the second check deleted. Here the tail turns 90 degrees over 3 ft, which is
    inside both bands, so the nub goes and the way comes back in its DRAWN orientation - the reverse
    after the second check is unconditional for exactly that reason.
    """
    ways = [[(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (200.0, 3.0)]]
    hit = hg.ways.drop_end_nubs(ways)
    assert hit == [0], "the way carries a trailing nub, so its index is reported as changed"
    assert ways[0] == [(0.0, 0.0), (100.0, 0.0), (200.0, 3.0)], "the nub vertex goes and the orientation is preserved"
    # ...and a way clean at both ends is left exactly alone (the non-vacuity half: prove the rule can decline)
    clean = [[(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]]
    assert hg.ways.drop_end_nubs(clean) == []
    assert clean[0] == [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]
