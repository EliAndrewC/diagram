"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways.clearance import existing_walk
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


def test_a_way_round_the_field_crosses_it_nowhere_or_is_refused() -> None:
    """Feature 287, ways W24 (FR-005): six rounds and then the result as it stood let a leg across the field ship. The
    rounds run until no leg crosses (bounded by the ring's vertices), and a path that still crosses comes back None."""
    from l7r.diagram.settlement import segments_cross

    comb = [(0.0, 0.0), (400.0, 0.0), (400.0, 100.0)]  # a deeply lobed field: eight teeth hanging from a spine
    for k in range(8):
        x = 400.0 - k * 50.0
        comb += [(x, 300.0), (x - 25.0, 300.0), (x - 25.0, 100.0)]
    comb += [(0.0, 100.0)]
    path = [(-50.0, 200.0), (450.0, 200.0)]
    bent = hg.route_around(comb, path, 4.0)
    if bent is not None:
        assert not any(segments_cross(a, b, comb[k], comb[(k + 1) % len(comb)]) for a, b in zip(bent, bent[1:], strict=False) for k in range(len(comb)))
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    assert hg.route_around(square, [(-50.0, 50.0), (150.0, 50.0)], 8.0, rounds=0) is None, "still across the field: refused"


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
    assert hg.ways._clear_link((0.0, 0.0), (100.0, 0.0), [], [], []) is True, "nothing to foul: the link is whole"


class _Fouls:
    """A stand-in index whose `fouled` answers from a set of sample x-coordinates (links along the x axis)."""

    def __init__(self, xs: set[float]) -> None:
        self.xs = xs

    def fouled(self, q: tuple[float, float]) -> bool:
        return round(q[0], 6) in self.xs


def test_a_link_is_decided_as_soon_as_it_is_known_with_the_verdict_of_every_sample() -> None:
    """`link_survives` asks the same samples as `clear_runs` in order and stops once the answer is known (feature 287 perf):
    every pattern of fouled samples on links of 1 to 8 samples, and a range of asked lengths, give the verdict of the walk
    over every sample - `any(polyline_len(r) >= need for r in clear_runs(...))` - including a clear run exactly the length
    asked, which only its own `polyline_len` decides."""
    from l7r.diagram.hamletgen.ways.clearance import clear_runs, link_survives, polyline_len

    for n in range(1, 8):
        b = (3.0 * n, 0.0)
        samples = [round(3.0 * k, 6) for k in range(n + 1)]
        for mask in range(1 << (n + 1)):
            stub = _Fouls({x for k, x in enumerate(samples) if mask >> k & 1})
            for need in (-2.0, 0.4, 3.0, 4.5, 6.0, 3.0 * n - 3.0, 3.0 * n):
                runs = clear_runs([(0.0, 0.0), b], [[(0.0, 0.0)]], 1.0, step=3.0, floor=0.5, index=stub)  # type: ignore[arg-type]
                want = any(polyline_len(r) >= need for r in runs)
                assert link_survives((0.0, 0.0), b, stub.fouled, need) is want, (n, mask, need)


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


def test_existing_walk_is_zero_when_both_ends_snap_to_the_same_junction() -> None:
    """Feature 174: two points within `touch` of each other are the same node, so the walk is zero -
    not None, which would read as 'no route' and make a redundant bridge look necessary."""
    assert existing_walk([[(0.0, 0.0), (100.0, 0.0)]], (0.0, 0.0), (1.0, 0.0), 5.0) == 0.0
    assert existing_walk([[(0.0, 0.0), (100.0, 0.0)]], (0.0, 0.0), (100.0, 0.0), 5.0) == 100.0, "distinct ends still walk the way"


def test_existing_walk_ignores_a_heap_entry_a_better_route_has_already_beaten() -> None:
    """The stale-entry skip in the search. A triangle whose direct edge is longer than the two-hop
    route pushes the far end twice; the improved entry pops first and the stale one must be dropped
    rather than overwriting the answer with the worse distance."""
    a, b, c = (0.0, 0.0), (100.0, 0.0), (50.0, 1.0)
    ways = [[a, b], [a, c], [c, b]]  # direct 100.0 against about 50.0 + 50.0 through c
    got = existing_walk(ways, a, b, 2.0)
    assert got is not None and got <= 100.0 + 1e-9, "the shortest of the two routes, never the stale one"


def test_a_way_whose_first_stretch_has_no_length_carries_no_nub() -> None:
    """A repeated vertex at either end gives a zero-length stretch, and a turn cannot be measured over
    it: the nub test declines rather than divides by zero, and the way is left alone."""
    ways = [[(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)]]
    assert hg.ways.drop_end_nubs(ways) == []
    assert ways[0] == [(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)]


def test_a_rewrite_may_not_swing_the_drawn_tread_onto_fabric_it_cleared() -> None:
    """Feature 291, cohort seed 20: dropping a 6.9 ft nub left the lane's first leg starting where it did, 1.7 ft off a
    garden bed, but running along the bed - and the 5 ft stroke's square corner swung into it. The centerline distance
    was the same before and after, and the vertex-read clearance above the bar both times; the stroke is what moved."""
    from l7r.diagram.hamletgen.ways.clearance import may_write, stroke_hits

    bed = [(2214.1, 2592.3), (2223.5, 2586.2), (2240.8, 2611.0), (2232.1, 2617.1)]
    old = [(2233.0, 2596.0), (2238.0, 2592.0), (2258.0, 2612.0), (2178.0, 2682.0)]
    new = [(2233.0, 2596.0), (2258.0, 2612.0), (2178.0, 2682.0)]
    assert stroke_hits(old, 5.0, [bed]) == set() and stroke_hits(new, 5.0, [bed]) == {0}
    assert not may_write(old, new, 5.0, [bed])
    assert may_write(new, new, 5.0, [bed]), "no worse than it was: a lane already on it is not made to fix itself here"
    far = [(2400.0, 2400.0), (2410.0, 2400.0)]
    assert stroke_hits(new, 5.0, [far]) == set(), "a polygon nowhere near the stroke is not tested"
