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


def test_a_touch_chord_shorter_than_a_foot_is_clear() -> None:
    """`_clear_touch` of two points under a foot apart is clear without a scan: there is no chord to foul anything (its
    callers in the deleted touch pass reached this before feature 417 T26)."""
    from l7r.diagram.hamletgen.ways.clearance import _clear_touch

    wall = [(0.0, -50.0), (50.0, -50.0), (50.0, 50.0), (0.0, 50.0)]
    assert _clear_touch((10.0, 0.0), (10.5, 0.0), [wall], [wall], [])
