"""Unit tests for the lanes, the connector track, and path legality (`hamletgen/ways.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways import _crosses_fabric, _fabric_hits, _margin_frame, _nearest_seg, _pull_back_to_service, _reach, _route, _trim_to_service
from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist

from ._builders import SQUARE, a_plan


def test_the_connector_track_leaves_the_frame_without_crossing_the_crop() -> None:
    """The guarantee is about the DRAWN path, not the straight line to its endpoint.

    This test used to assert the chord and is the reason it is worth spelling out: a track bows ~40
    px either side of its bearing, so chord and path disagree, and routing by the chord while
    drawing the bow is exactly how a connector came to be drawn through the rice with the router
    insisting it had checked."""
    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    track = hg.connector_track(plan, (700.0, 200.0), avoid=[SQUARE])
    assert hg.path_violations(track, [SQUARE], None, []) == 0, "no segment of the drawn track may cross the crop"
    assert not (0 <= track[-1][0] <= plan.W and 0 <= track[-1][1] <= plan.H)  # ends off the canvas


def test_a_point_in_the_crop_is_pushed_out_on_the_LOCAL_edge_normal() -> None:
    """The defect the GM reported: a way's tip stopped 28 px INSIDE the paddy because it was pulled
    back along one fixed map-wide direction. The way out is the nearest OUTLINE EDGE's normal - and
    the nearest edge, not the nearest vertex, since a point deep in a lobe can have its nearest
    vertex round the far side."""
    square = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]
    out = hg.push_out_of(square, (90.0, 50.0), 10.0)  # nearest edge is the right one, x=100
    assert out == pytest.approx((110.0, 50.0))
    assert hg.push_out_of(square, (50.0, 5.0), 10.0) == pytest.approx((50.0, -10.0)), "the bottom edge is nearer here"
    far = hg.push_out_of(square, (300.0, 50.0), 10.0)
    assert far == (300.0, 50.0), "a point already clear is returned untouched - this must never drag a way back in"


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


def test_a_shallow_crossing_is_distinguished_from_a_square_one() -> None:
    """A way may cross a ditch - that is what a plank is for - but not at a slant."""
    ditch = ((0.0, 0.0), (100.0, 0.0))
    assert not hg.shallow_crossing((50.0, -50.0), (50.0, 50.0), *ditch)  # square
    assert hg.shallow_crossing((0.0, -10.0), (100.0, 10.0), *ditch)  # a slant
    assert not hg.shallow_crossing((0.0, 100.0), (100.0, 100.0), *ditch)  # never meets it


def test_a_way_that_misses_the_watercourse_lands_on_nothing() -> None:
    """`crossing_lands_on_crop` answers about the CROSSING POINT, so a way that never meets the
    course has no crossing point and no verdict to give."""
    assert not hg.crossing_lands_on_crop((0.0, 0.0), (10.0, 0.0), (0.0, 50.0), (10.0, 50.0), [SQUARE])
    # ...and one that meets it inside the crop does
    assert hg.crossing_lands_on_crop((700.0, 300.0), (700.0, 900.0), (400.0, 700.0), (1000.0, 700.0), [SQUARE])


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


def test_margin_frame_round_trips_a_point_through_arc_and_standoff() -> None:
    """`project` is the inverse of `__call__`, and the web depends on both agreeing: the cuts are
    computed from projected house positions and then mapped back out to screen."""
    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    # A SPAN, and a `near` cloud, that describe one flank rather than the whole ring. Given neither,
    # the walk laps the field - and a frame that laps has no single answer for `project`, because two
    # stretches of it lie on top of each other. That is now capped at half the ring in the engine,
    # and the test says what a caller is expected to hand it.
    frame = _margin_frame(plan, 120.0, near=[(plan.seat["cx"], plan.seat["cy"])])
    assert frame.arc < 0.5 * sum(math.dist(plan.envelope[i], plan.envelope[(i + 1) % len(plan.envelope)]) for i in range(len(plan.envelope))) + 1.0
    for arc_f, stand in ((0.25, 40.0), (0.5, 90.0), (0.8, 15.0)):
        p = frame(frame.arc * arc_f, stand)
        got_arc, got_stand = frame.project(p)
        assert abs(got_arc - frame.arc * arc_f) < 20.0
        assert abs(got_stand - stand) < 20.0


def test_reach_measures_the_nearest_point_of_a_path_not_its_ends() -> None:
    """The same measurement `farmhouses_reach_a_way` makes. Measuring to the ENDS would call a house
    beside the middle of a long lane unreached."""
    path = [(0.0, 0.0), (1000.0, 0.0)]
    assert _reach((500.0, 30.0), path) == pytest.approx(30.0)


# ---- feature 123: the web's guard rails, each exercised on its own -------------------------------


def _lanes(*polys):
    """A minimal Settlement stand-in carrying only what the web helpers read."""

    class _S:
        def __init__(self):
            self.M = {"lanes": [{"pts": [list(map(list, p))][0], "w": 5} for p in polys], "houses": []}

        def lane(self, pts, **kw):
            self.M["lanes"].append({"pts": [list(q) for q in pts], "w": kw.get("width", 5)})

    return _S()


def test_reachable_runs_admits_a_run_that_joins_THROUGH_another_run() -> None:
    """A back lane may join through a cross-tie and a tie through a back lane - that is what makes a
    framework a framework, and it is why the decision is made over candidates rather than as each
    lane is drawn: judged one at a time, a run is refused merely for being early in the loop."""
    skeleton = [((0.0, 0.0), (100.0, 0.0))]
    touching = [(100.0, 0.0), (200.0, 0.0)]
    second_hop = [(200.0, 0.0), (300.0, 0.0)]
    island = [(9000.0, 9000.0), (9100.0, 9000.0)]
    kept = hg.ways._reachable_runs([island, second_hop, touching], skeleton)
    assert touching in kept and second_hop in kept, "the far run joins through the near one"
    assert island not in kept, "an island is never drawn"


def test_reachable_runs_with_no_seed_network_seeds_from_the_first_run() -> None:
    """A hamlet always has its skeleton by the time the web is laid, so this is a defensive branch
    rather than a real case - but it must not silently return nothing, or a map that somehow reached
    it would come out with no web at all instead of with an obvious one."""
    runs = [[(0.0, 0.0), (10.0, 0.0)], [(9000.0, 9000.0), (9010.0, 9000.0)]]
    assert hg.ways._reachable_runs(runs, []) == [runs[0]]


def test_trim_to_service_pulls_an_end_back_to_what_it_serves() -> None:
    """A tread that stops in bare grass serves nobody. Trimming happens BEFORE the ink and before the
    join is computed - trimming afterwards moves the end out from under the link drawn to it."""
    run = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (900.0, 0.0)]
    segs = [((0.0, -20.0), (0.0, 20.0))]
    out = hg.ways._trim_to_service(run, segs, [(100.0, 30.0)])
    assert out[-1] == (100.0, 0.0), "the 800 ft tail into nothing is dropped"
    assert out[0] == (0.0, 0.0), "the end that meets a way is kept"


def test_trim_to_service_never_trims_below_two_points() -> None:
    run = [(5000.0, 5000.0), (5100.0, 5000.0), (5200.0, 5000.0)]
    assert len(hg.ways._trim_to_service(run, [], [])) == 2


def test_route_returns_nothing_when_the_way_is_genuinely_blocked() -> None:
    """[] is a real answer. The alternative - drawing something anyway - is what produced a 38 ft
    mark 71 ft from the house it served, touching nothing, to cure a one-foot violation."""
    wall = [(40.0, -400.0), (60.0, -400.0), (60.0, 400.0), (40.0, 400.0)]
    assert hg.ways._route((0.0, 0.0), (100.0, 0.0), [wall], [], [], cell=10.0) == []


def test_route_goes_around_an_obstacle_rather_than_through_it() -> None:
    wall = [(40.0, -60.0), (60.0, -60.0), (60.0, 60.0), (40.0, 60.0)]
    path = hg.ways._route((0.0, 0.0), (100.0, 0.0), [wall], [], [], cell=8.0)
    assert path, "there is a way round the end of the wall"
    assert hg.ways.polyline_len(path) > 100.0, "going round costs more than the straight line"
    assert max(abs(q[1]) for q in path) > 40.0, "and it leaves the straight line to do it"


def test_clear_link_requires_the_WHOLE_span_not_a_piece_of_it() -> None:
    """Accepting the first surviving run let a snap be drawn across ground that had been clipped out
    of the middle - the run existed, it just was not the gap being bridged."""
    blocker = [(45.0, -30.0), (55.0, -30.0), (55.0, 30.0), (45.0, 30.0)]
    assert hg.ways._clear_link((0.0, 0.0), (100.0, 0.0), [blocker], [], []) is False
    assert hg.ways._clear_link((0.0, 0.0), (30.0, 0.0), [blocker], [], []) is True
    assert hg.ways._clear_link((0.0, 0.0), (0.2, 0.0), [blocker], [], []) is True, "a zero-length link is trivially clear"


def test_net_reach_measures_the_paths_VERTICES_against_the_network() -> None:
    """Vertex-to-segment, not segment-to-segment, and the asymmetry is worth knowing: a long straight
    run whose middle passes close to a way but whose vertices do not will read as further off than it
    looks. The web samples its runs every few feet, so in practice the vertices are the line - but a
    caller handing it a two-point polyline gets the corner distance, not the perpendicular."""
    assert hg.ways._net_reach([(0.0, 50.0), (100.0, 50.0)], [((50.0, 0.0), (60.0, 0.0))]) == pytest.approx(64.031242, abs=1e-4)
    dense = [(float(x), 50.0) for x in range(0, 101, 5)]
    assert hg.ways._net_reach(dense, [((50.0, 0.0), (60.0, 0.0))]) == pytest.approx(50.0)


class _StubSettlement:
    """The two things the web helpers touch on a Settlement: the manifest and `lane()`."""

    def __init__(self, lanes=(), houses=()):
        self.M = {
            "lanes": [{"pts": [list(q) for q in p], "w": 5, "connector": i == 0} for i, p in enumerate(lanes)],
            "houses": [{"x": x, "y": y, "w": 46.0, "h": 28.0, "rot": 0.0} for x, y in houses],
        }

    def lane(self, pts, **kw):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": kw.get("width", 5)})

    def reink_lane(self, i):
        pass  # the stub has no ink; the record is what the helpers are tested on


def test_touch_junctions_does_not_close_a_short_lane_onto_its_own_start() -> None:
    """Feature 150, Kuwabata seed 21: a 30 ft lane whose two ends both stood near the same spot on
    a neighbor was touched there at BOTH ends and became a 28 ft loop - a hairpin to
    `lanes_bend_like_paths`, invisible to `_smooth_web`, which had already run. A foot within a few
    feet of the lane's other end is that end's own junction, not a new one."""
    main = [(0.0, 0.0), (400.0, 0.0)]
    short = [(200.0, 20.0), (215.0, 32.0), (203.0, 24.0)]
    s = _StubSettlement(lanes=[main, short])
    hg.ways._touch_junctions(s, [], [], [])
    pts = [tuple(q) for q in s.M["lanes"][1]["pts"]]
    assert math.dist(pts[0], (200.0, 0.0)) <= 1.0, "the start is touched down onto the main lane"
    assert math.dist(pts[0], pts[-1]) > 6.0, f"the lane closed onto itself: {pts}"


def test_a_web_lane_may_not_run_the_length_of_a_shelter_belt() -> None:
    """Crossing a belt costs it a lane's width of wall, which is a fair price for a way with
    somewhere to be. Running ALONG it splits one wind wall into two thinner ones - measured, a back
    lane 237 of 237 ft inside the belt, having deleted 15 of its 169 clumps."""
    # Houses at both ends so the run is not trimmed back before the belt rule is reached - the trim
    # runs first on purpose (see `_trim_to_service`), and a run serving nothing is dropped for that
    # reason rather than this one.
    ends = [(20.0, 190.0), (285.0, 190.0)]
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=ends)
    belt = [(-50.0, 100.0), (400.0, 100.0), (400.0, 160.0), (-50.0, 160.0)]
    lengthwise = [(float(x), 130.0) for x in range(10, 300, 5)]
    assert hg.ways._lay_web_lane(s, lengthwise, [], [], [], belts=[belt], houses=ends) is False
    crossing = [(200.0, float(y)) for y in range(60, 205, 5)]
    assert hg.ways._lay_web_lane(s, crossing, [], [], [], belts=[belt], houses=[(200.0, 70.0), (200.0, 195.0)]) is True, "crossing the belt is allowed"


def test_a_web_lane_that_cannot_reach_the_network_draws_a_link_or_is_refused() -> None:
    """A run further off than the touch tolerance gets a link drawn to the network - and if the link
    cannot be drawn, the run is not drawn either. Refusing is the right answer: the alternative is
    ink that looks like a way and is not one."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(150.0, 200.0)])
    detached = [(120.0, float(y)) for y in range(150, 255, 5)]
    before = len(s.M["lanes"])
    assert hg.ways._lay_web_lane(s, detached, [], [], [], houses=[(150.0, 200.0)]) is True
    assert len(s.M["lanes"]) == before + 2, "the link and the run"

    walled = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(900.0, 200.0)])
    fence = [(300.0, -500.0), (320.0, -500.0), (320.0, 900.0), (300.0, 900.0)]
    far = [(880.0, float(y)) for y in range(150, 255, 5)]
    assert hg.ways._lay_web_lane(walled, far, [fence], [], [], houses=[(900.0, 200.0)]) is False
    assert len(walled.M["lanes"]) == 1, "nothing drawn when the link cannot be made"


def test_join_orphan_ways_gives_up_rather_than_forcing_a_link() -> None:
    """An orphan that cannot be linked stays orphaned and the gate says so. Forcing a link would draw
    a way through whatever stood between them."""
    # The barrier has to be genuinely CLOSED, not merely long: a link may now go the long way round,
    # which is the fix that joined the two halves of a split hamlet. A fence it can walk around is
    # not a test of giving up, it is a test of the detour.
    # a 300 px gap, not 900: the router searches the whole gap before giving up, and a 900 px one
    # cost 1.9 s for the same "walled in" verdict (T19, 2026-08-26)
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)], [(300.0, 0.0), (300.0, 200.0)]])
    box = [(200.0, -300.0), (450.0, -300.0), (450.0, 520.0), (200.0, 520.0)]
    assert hg.ways._join_orphan_ways(s, [box], [], []) == 0
    assert len(s.M["lanes"]) == 2, "no link drawn when the orphan is walled in"


def test_join_orphan_ways_links_an_orphan_when_the_ground_allows() -> None:
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)], [(120.0, 0.0), (120.0, 200.0)]])
    assert hg.ways._join_orphan_ways(s, [], [], []) == 1
    assert len(s.M["lanes"]) == 3


def test_a_web_lane_is_refused_when_its_link_is_blocked_though_the_gap_is_short() -> None:
    """The gap is well inside the search radius, so the run is not rejected for distance - it is
    rejected because the ground between it and the network will not take a lane. Refusing is the
    point: ink that looks like a way and is not one is worse than a house left for the footpath
    pass."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(120.0, 200.0)])
    fence = [(40.0, -400.0), (60.0, -400.0), (60.0, 800.0), (40.0, 800.0)]
    run = [(120.0, float(y)) for y in range(150, 255, 5)]
    assert hg.ways._lay_web_lane(s, run, [fence], [], [], houses=[(120.0, 200.0)]) is False
    assert len(s.M["lanes"]) == 1, "neither the link nor the run is drawn"


def test_the_footpath_search_stops_looking_past_its_backstop_radius() -> None:
    """The directness bound is the real limit on a footpath; the radius is only a backstop against
    searching the whole map. A steading this far out is beyond any path worth drawing, and the loop
    must stop rather than test every way on the sheet."""

    class _Plan:
        envelope = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]
        watercourses: list = []

    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)]], houses=[(4000.0, 4000.0)])
    before = len(s.M["lanes"])
    hg.ways._serve_stragglers(s, _Plan(), [], [], [])
    assert len(s.M["lanes"]) == before, "nothing drawn for a steading beyond the backstop"


def test_margin_frame_without_a_house_cloud_falls_back_to_the_along_axis() -> None:
    """`near` is the placed houses, and callers inside the engine always have them. The fallback is
    for a caller that does not - it walks the outline by the seat band's own lateral reach instead,
    which is the same test `front_row` makes."""
    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    frame = _margin_frame(plan, 150.0)
    assert frame.arc > 0.0
    assert len(frame.pts) >= 2


def test_reachable_runs_with_no_candidates_is_empty() -> None:
    assert hg.ways._reachable_runs([], [((0.0, 0.0), (10.0, 0.0))]) == []
    assert hg.ways._reachable_runs([[(0.0, 0.0)]], [((0.0, 0.0), (10.0, 0.0))]) == [], "a one-point run is not a run"


def test_join_orphan_ways_on_a_map_with_one_way_has_nothing_to_join() -> None:
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)]])
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0


def test_draw_web_refuses_a_lane_too_short_to_be_a_way() -> None:
    """A 4 ft mark fronts nobody and reads as a speck of clipping debris - Sawada shipped 4, 12 and
    20 ft fragments, left behind when the end-trim pulled a path back to its last serving point."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])
    before = len(s.M["lanes"])
    assert hg.ways._draw_web(s, [(100.0, 100.0), (104.0, 100.0)]) is False
    assert len(s.M["lanes"]) == before
    assert hg.ways._draw_web(s, [(100.0, 100.0), (100.0, 200.0)]) is True
    assert s.M["lanes"][-1]["web"] is True


def test_draw_web_refuses_a_run_with_only_one_point() -> None:
    """A single point is not a way, and it reaches `_draw_web` for a real reason rather than as a
    defensive nicety: `clear_runs` returns whatever survived clipping, and a candidate clipped down
    to one surviving vertex arrives here looking like a run. Drawing it would put a zero-length lane
    in the manifest, which every way rule then measures - `lanes_reach_something` would see a tread
    that fronts nothing and `polyline_len` would divide by a zero chord."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])
    before = len(s.M["lanes"])
    assert hg.ways._draw_web(s, [(100.0, 100.0)]) is False
    assert hg.ways._draw_web(s, []) is False
    assert len(s.M["lanes"]) == before


def test_a_web_lane_snaps_its_end_onto_the_way_it_almost_meets() -> None:
    """A run that stops a few feet short of the way it aims at renders as a gap, whatever the gate
    thinks of it - acceptance tolerances are not ink tolerances. So an end within `_LANE_JOIN_FT` is
    extended onto the way it meets, but ONLY if the ground between is clear: adding those few feet
    blind put lane ink across houses and garden beds on every cohort seed the moment snapping went
    in. This pins both halves - the snap, and the refusal to snap through a steading."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])
    before = len(s.M["lanes"])
    # SAMPLED like a real run: the shadow clause caps the longest UNBROKEN shadowed stretch at a
    # bundle pitch, and with only two vertices the sample step IS the whole run, so a two-point run
    # trips it on its joining end alone.
    run = [(200.0 - 182.0 * i / 10.0, 200.0) for i in range(11)]
    assert hg.ways._lay_web_lane(s, run, [], [], []) is True
    assert len(s.M["lanes"]) == before + 1
    drawn = [(round(x), round(y)) for x, y in s.M["lanes"][-1]["pts"]]
    assert (0, 200) in drawn, drawn
    # ...and the same run refused the snap when a steading stands in the gap
    s2 = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])
    wall = [(2.0, 180.0), (16.0, 180.0), (16.0, 220.0), (2.0, 220.0)]
    hg.ways._lay_web_lane(s2, run, [], [wall], [])
    if len(s2.M["lanes"]) > 1:
        assert (0, 200) not in [(round(x), round(y)) for x, y in s2.M["lanes"][-1]["pts"]]


def test_bridge_collinear_breaks_closes_a_hole_and_leaves_an_honest_one() -> None:
    """One street drawn as two gets the missing piece drawn. A break with something genuinely in the
    way keeps it - the route cannot be made, so the interruption stands."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 40.0)], [(200.0, 500.0), (400.0, 500.0)], [(510.0, 500.0), (710.0, 500.0)]])
    assert hg.ways._bridge_collinear_breaks(s, [], [], []) == 1
    assert len(s.M["lanes"]) == 4

    walled = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 40.0)], [(200.0, 500.0), (400.0, 500.0)], [(510.0, 500.0), (710.0, 500.0)]])
    fence = [(440.0, 200.0), (470.0, 200.0), (470.0, 800.0), (440.0, 800.0)]
    assert walled.M["lanes"][0] is not None
    assert hg.ways._bridge_collinear_breaks(walled, [fence], [], []) == 0
    assert len(walled.M["lanes"]) == 3


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


def test_trim_to_service_trims_the_FRONT_end_too() -> None:
    """Both ends, not just the tail. This branch had no test of its own and was covered only because
    some pool map happened to lay a run whose head hung in bare grass - so a cluster-shape change
    that moved the houses took the coverage away with it, which is what a branch tested by luck
    looks like when the luck runs out."""
    run = [(-900.0, 0.0), (0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    segs = [((100.0, -20.0), (100.0, 20.0))]
    out = hg.ways._trim_to_service(run, segs, [(0.0, 30.0)])
    assert out[0] == (0.0, 0.0), "the 900 ft head into nothing is dropped"
    assert out[-1] == (100.0, 0.0), "the end that meets a way is kept"


def test_a_web_lane_that_arrives_early_keeps_the_long_half() -> None:
    """The hairpin cure, on the side the existing test does not reach: when a run's closest approach
    to the network is an interior point, the SHORT half is the stub to drop - and which half is short
    is not always the tail. A run that touches the network 20 ft in and then travels 140 ft away is
    one lane arriving, not a lane with a tail; keeping the 20 ft head instead would delete the whole
    way and leave the houses it serves unserved."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]], houses=[(160.0, 230.0)])
    run = [(40.0, 200.0), (20.0, 200.0), (60.0, 200.0), (110.0, 200.0), (160.0, 200.0)]
    assert hg.ways._lay_web_lane(s, run, [], [], [], houses=[(160.0, 230.0)]) is True
    drawn = s.M["lanes"][-1]["pts"]
    assert [tuple(q) for q in drawn] == run[1:], "the 20 ft head is dropped, the 140 ft body is kept"


def test_a_web_lane_end_already_near_the_network_is_SNAPPED_onto_it() -> None:
    """The third arm of `_lay_web_lane`'s junction logic, and the only one with no test of its own: an
    end already inside `_LANE_JOIN_FT` is not linked and not refused - it is EXTENDED onto the way it
    meets, so the junction reads as a touch rather than a 12 ft gap. The snap is conditional on the
    ground between being walkable, because adding those few feet blind once put lane ink across houses
    and garden beds.

    Held here because its coverage was CACHE-DEPENDENT rather than absent (found 2026-08-19). The
    branch is exercised by regenerating a pool map, so a gate run that follows a `consts.py` change
    regenerates and covers it, while a gate run on an unchanged tree serves those maps from the gen
    cache and never executes the line. Same code, same seeds, coverage green or red depending on
    whether a cache happened to be warm - which is the flakiest kind of pass there is, and reads as a
    mystery regression when it flips."""
    lane = [(0.0, 0.0), (0.0, 400.0)]
    house = (160.0, 230.0)
    s = _StubSettlement(lanes=[lane], houses=[house])
    run = [(20.0, 200.0), (60.0, 200.0), (110.0, 200.0), (160.0, 200.0)]
    assert hg.ways._lay_web_lane(s, run, [], [], [], houses=[house]) is True
    drawn = [tuple(q) for q in s.M["lanes"][-1]["pts"]]
    assert drawn[0] == (0.0, 200.0), f"the near end should be snapped onto the lane, got {drawn[:2]}"
    assert drawn[1:] == run, "the rest of the run is unchanged - snapping adds a point, it does not re-route"


# ---- feature 126: ways split by provenance, and the settlement form ------------------------------


def test_the_form_roll_is_deterministic_and_covers_all_three_forms() -> None:
    """A seed must always produce the same form, and the cohort must actually exercise each one.

    The second half matters as much as the first: a form weighted so rarely that no cohort seed
    rolls it is a form nothing tests, and the whole point of the knob is that players can tell two
    settlements apart."""
    forms = {}
    for seed in range(48):
        plan = hg.plan_site(hg.HamletSpec(name=f"Roll-{seed}", seed=seed, households=12))
        again = hg.plan_site(hg.HamletSpec(name=f"Roll-{seed}", seed=seed, households=12))
        assert plan.settlement_form == again.settlement_form, f"seed {seed} rolled two different forms"
        forms[plan.settlement_form] = forms.get(plan.settlement_form, 0) + 1
    # PINNED TO NUCLEATED for now - the knob is live and every other part of it is tested, but the
    # per-house grove path the other two forms need has four unfixed defects (see SETTLEMENT_FORMS
    # in hamletgen/consts.py for the measurements and the sketch). This asserts the CURRENT contract
    # rather than the intended one, so that turning the forms back on fails here loudly and the test
    # is updated deliberately instead of drifting.
    assert set(forms) == {"nucleated"}, f"forms are pinned to nucleated; got {forms}"


def test_an_explicit_form_on_the_spec_beats_the_roll() -> None:
    """A pool gen pins the form the way it pins every other knob."""
    plan = hg.plan_site(hg.HamletSpec(name="Pinned", seed=3, households=12, settlement_form="dispersed"))
    assert plan.settlement_form == "dispersed"


def test_a_dispersed_hamlet_draws_no_internal_lanes() -> None:
    """The dispersed form's defining feature, pinned so a later change cannot quietly restore the web.

    A Tonami farmstead stands in the middle of its own holding; what joins it to the world is the
    connector, and what joins it to its neighbors is the field baulk. Drawing a web here would erase
    the one thing that makes the form legible at a glance."""
    plan = a_plan(settlement_form="dispersed")
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 120.0}]
    hg.ways.stage_web(s, plan)
    assert not s.M.get("lanes"), "a dispersed hamlet must have no internal lane network"
    assert s.M["meta"]["lane_skeleton"] == "none"


def test_only_the_dispersed_form_short_circuits_stage_web() -> None:
    """The converse of the test above, and it needs to exist: a dispersed map with no lanes would
    also pass if `stage_web` had simply stopped drawing lanes for EVERYONE.

    The discriminator is that a nucleated map runs on past the guard into the seat-dependent code,
    so on this deliberately seatless fixture it raises where the dispersed map returned cleanly.
    That is an indirect assertion, and it is used here because building a real seat means running
    the whole pre-house pipeline; the direct evidence that nucleated maps still get lanes is the
    cohort, where they do."""
    plan = a_plan(settlement_form="nucleated")
    assert plan.settlement_form == "nucleated"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 120.0}]
    with pytest.raises(KeyError):
        hg.ways.stage_web(s, plan)


# ---- feature 126: the defensive branches in the derived-lane machinery -------------------------


def test_a_dispersed_hamlet_records_that_it_has_no_skeleton() -> None:
    """The dispersed form draws no internal network, and says so in `meta` rather than leaving the
    knob reading as though a skeleton were drawn."""
    plan = a_plan(settlement_form="dispersed")
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 120.0}]
    hg.ways.stage_web(s, plan)
    assert s.M["meta"]["lane_skeleton"] == "none"
    assert not s.M.get("lanes")


def test_the_skeleton_needs_two_house_projections() -> None:
    """`_lay_skeleton` is handed the arcs the caller measured off the placed houses. With fewer than
    two there is no extent to fit an arm to, and it draws nothing rather than guessing one."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    # The frame is never consulted on this path - the arc count is checked first - so a sentinel is
    # honest here and keeps the test off `_margin_frame`, which needs a seated cluster to exist.
    assert hg.ways._lay_skeleton(s, plan, None, [], []) == []  # type: ignore[arg-type]
    assert hg.ways._lay_skeleton(s, plan, None, [10.0], [5.0]) == []  # type: ignore[arg-type]


def test_homestead_polys_carries_the_per_house_groves() -> None:
    """A yashikirin belongs to its farmstead, so a lane may no more be drawn through one than
    through the house. It was missing from the fabric list while the lanes were laid first."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["groves"] = [{"poly": [[10.0, 10.0], [40.0, 10.0], [40.0, 40.0], [10.0, 40.0]]}]
    kinds = [kind for _poly, _owner, kind in hg.ways._homestead_polys(s)]
    assert "groves" in kinds


def test_join_orphan_ways_needs_two_ways_to_join() -> None:
    """With one way or none there is no orphan to link, and the pass says so immediately rather than
    walking an empty component search."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0
    s.M["lanes"] = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}]
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0


def test_an_arm_clipped_down_to_a_stub_is_debris_and_is_not_drawn() -> None:
    """A skeleton arm that survives clipping as a few pixels is not a short lane, it is debris.

    The arms are the layout template mapped onto the margin frame, so what reaches the drawing call
    is whatever is left after the crop, the water and the standing fabric have each taken their bite.
    Nothing in that chain has an opinion about whether the remainder is still a WAY - `clip_to_clear`
    stops where the ground stops being walkable, and `_trim_to_service` pulls the ends back to what
    they serve but never below two points. So a run of half a pixel arrives at `s.lane` looking
    exactly like a legitimate short arm, and gets ink.

    Driven through a frame that collapses the template rather than through a rolled map, because no
    pool map or cohort seed produces the case - the whole 3,448-test suite leaves this branch
    unexecuted - and a test that cannot be provoked deterministically is not a test. The houses sit
    clear of the collapsed arm on purpose: parked on top of it the fabric clip removes the run one
    step earlier, which passes for the wrong reason."""
    plan = a_plan(lane_skeleton="spine")
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 200.0, "y": 270.0, "w": 20.0, "h": 14.0}, {"x": 230.0, "y": 270.0, "w": 20.0, "h": 14.0}]

    # every (arc, standoff) lands within half a pixel of the same spot, well clear of SQUARE
    def flat(arc: float, standoff: float) -> tuple[float, float]:
        return (200.0 + arc * 0.005, 200.0 - standoff * 0.005)

    assert hg.ways._lay_skeleton(s, plan, flat, [0.0, 20.0], [0.0, 10.0]) == []  # type: ignore[arg-type]
    assert not s.M.get("lanes"), "a half-pixel arm must not be inked"


def test_crosses_fabric_sees_a_steading_beside_the_MIDDLE_of_a_long_run() -> None:
    """The half of the detector feature 128 shipped without, and the shape it costs.

    A connector crosses a hamlet in three or four points, so its segments run hundreds of pixels; the
    original test measured `edge_dist` at the run's own VERTICES and asked `segments_cross`, which
    between them cannot see a farmstead standing beside a segment's midpoint without straddling it.
    Mizuguchi shipped its connector 0.2 px from a garden while this returned False at a gap of 0.5.

    The run below never enters the box and neither endpoint is near it, which is exactly the case."""
    run = [(0.0, 0.0), (1000.0, 0.0)]
    box = [(490.0, 10.0), (510.0, 10.0), (510.0, 30.0), (490.0, 30.0)]
    assert _crosses_fabric(run, [box], 16.0) is True
    assert _crosses_fabric(run, [box], 4.0) is False  # 10 px away: outside a 4 px gap, honestly


def test_fabric_hits_counts_steadings_rather_than_answering_yes_or_no() -> None:
    """A sweep with no clean bearing still has to rank, so the score is a COUNT, not a boolean."""
    run = [(0.0, 0.0), (1000.0, 0.0)]
    near_a = [(190.0, 4.0), (210.0, 4.0), (210.0, 24.0), (190.0, 24.0)]
    near_b = [(690.0, 4.0), (710.0, 4.0), (710.0, 24.0), (690.0, 24.0)]
    far = [(490.0, 400.0), (510.0, 400.0), (510.0, 420.0), (490.0, 420.0)]
    assert _fabric_hits(run, [near_a, near_b, far], 16.0) == 2
    assert _fabric_hits(run, [far], 16.0) == 0
    assert _fabric_hits(run, (), 16.0) == 0


def test_the_router_declines_a_span_too_wide_for_its_lattice() -> None:
    """A connector's span is the whole canvas, and the router says so by returning nothing.

    This is pinned rather than left to a `no cover` pragma because the OLD pragma asserted the
    opposite - that the pad was bounded so the grid could never overflow - and a reader who believed
    it would look for the reason a connector is not detoured in the wrong place entirely."""
    assert _route((0.0, 0.0), (4000.0, 0.0), [], [], []) == []


def test_nearest_seg_returns_the_distance_AND_the_segment_it_belongs_to() -> None:
    """One expression, one answer - a caller must not re-derive which segment was nearest."""
    segs = [((0.0, 0.0), (100.0, 0.0)), ((0.0, 200.0), (100.0, 200.0))]
    d, sg = _nearest_seg((50.0, 10.0), segs)
    assert round(d, 6) == 10.0
    assert sg == segs[0]
    assert _nearest_seg((0.0, 0.0), []) == (float("inf"), None)


def test_a_connector_end_inside_the_canvas_is_pulled_back_ONTO_the_way_it_joins() -> None:
    """The blind stub feature 128 shipped, and the two halves of not shipping it again.

    The run starts deep inside the settlement, passes a lane, and continues off the frame. The inner
    end must come back to TOUCH that lane - not merely to within the join bar, which is what left
    Mizuguchi 27 ft short - and the off-canvas end must not be touched at all, because reaching the
    frame is the connector's other job."""
    run = [(500.0, 100.0), (100.0, 100.0), (-400.0, 100.0)]
    segs = [((300.0, 0.0), (300.0, 200.0))]
    out = _pull_back_to_service(run, segs, [], lambda q: 0.0 <= q[0] <= 1000.0 and 0.0 <= q[1] <= 1000.0)
    assert out[-1] == (-400.0, 100.0), "the off-canvas end must survive untouched"
    assert round(seg_dist(out[0][0], out[0][1], *segs[0]), 6) == 0.0, "the inner end must TOUCH the way"


def test_a_connector_that_joins_NOTHING_is_left_alone_rather_than_deleted() -> None:
    """A hamlet whose track genuinely meets no lane is a real map to look at, not one to shorten."""
    run = [(500.0, 100.0), (-400.0, 100.0)]
    out = _pull_back_to_service(run, [((0.0, 5000.0), (100.0, 5000.0))], [], lambda q: 0.0 <= q[0] <= 1000.0)
    assert out == run


def test_trim_to_service_counts_ARRIVING_AT_THE_FIELD_as_service() -> None:
    """The spur's whole purpose is the crop, which is neither a house nor another lane."""
    field = [(400.0, 0.0), (600.0, 0.0), (600.0, 200.0), (400.0, 200.0)]
    run = [(0.0, 100.0), (200.0, 100.0), (395.0, 100.0)]
    assert _trim_to_service(run, [], [(0.0, 100.0)], [field]) == run
    assert len(_trim_to_service(run, [], [(0.0, 100.0)], [])) == 2


def test_a_final_pass_junction_ends_the_lane_where_it_first_meets_the_way() -> None:
    """settlement-review 2026-08-28 (Kuwabata lane 9): a lane that came within the touch gap of the way
    it was being joined to part-way along, then ran on beside it and hooked back, left two treads 5-9 ft
    apart enclosing a sliver of ground - a 113 deg V, legal to the bend rule and wrong on the sheet. In
    the final pass the lane is ended where it first meets the way."""
    main = [(0.0, 0.0), (400.0, 0.0)]
    lane = [
        (300.0, 60.0),
        (150.0, -5.0),
        (142.0, 15.0),
    ]  # crosses the main lane near x=161 mid-segment (no vertex within the 4 ft "already met" test), runs 33 ft on and turns back; its far end is out of reach
    s = _StubSettlement(lanes=[main, lane])
    hg.ways._touch_junctions(s, [], [], [], final=True)
    pts = [tuple(q) for q in s.M["lanes"][1]["pts"]]
    assert len(pts) == 2 and pts[0] == (300.0, 60.0), pts
    assert abs(pts[-1][1]) < 0.01 and 155.0 <= pts[-1][0] <= 170.0, pts


# ---- the splice helpers (feature 137 T04) ---------------------------------------------------------


def test_unretrace_collapses_an_out_and_back_spur() -> None:
    """A join link prepended whole doubled back along the piece's own first segment (cohort seed 07):
    A -> B -> A' -> B -> C is A -> B -> C."""
    pts = [(0.0, 0.0), (20.0, 0.0), (0.5, 0.0), (20.0, 0.0), (60.0, 0.0)]
    assert hg.ways._unretrace(pts) == [(0.0, 0.0), (20.0, 0.0), (60.0, 0.0)]


def test_unretrace_keeps_a_polyline_that_would_fold_away_entirely() -> None:
    """A door path whose link ran back past the door is an ugly lane, not an empty one (seed 03)."""
    pts = [(0.0, 0.0), (20.0, 0.0), (0.0, 0.0)]
    assert hg.ways._unretrace(pts) == pts


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


def test_stop_at_network_cuts_a_link_where_it_crosses_the_way_it_was_sent_to() -> None:
    """Tripwire seed 27: the link touched a way at 20 ft and carried on to a `q` a trim later removed."""
    link = [(0.0, 0.0), (0.0, 30.0), (0.0, 60.0)]
    way = [((-20.0, 20.0), (20.0, 20.0))]
    assert hg.ways._stop_at_network(link, way) == [(0.0, 0.0), (0.0, 20.0)]


def test_stop_at_network_lands_on_the_way_it_stops_beside() -> None:
    """A vertex 3 ft off a way is a piece to the web's 4 ft join tolerance once rounded - the cut
    ends on the way's foot point, not beside it."""
    link = [(0.0, 0.0), (30.0, 3.0), (60.0, 3.0)]
    way = [((20.0, 0.0), (40.0, 0.0))]
    assert hg.ways._stop_at_network(link, way) == [(0.0, 0.0), (30.0, 3.0), (30.0, 0.0)]


def test_stop_at_network_leaves_a_link_that_meets_nothing_on_the_way() -> None:
    link = [(0.0, 0.0), (30.0, 0.0), (60.0, 0.0)]
    assert hg.ways._stop_at_network(link, []) == link
    assert hg.ways._stop_at_network(link, [((0.0, 50.0), (60.0, 50.0))]) == link


# ---- feature 146: the track's fallbacks, which no cohort seed has needed --------------------------------


def _walled_settlement() -> tuple[object, object]:
    """A Settlement whose homesteads form a WALL across the middle of the canvas, so a run from north to
    south cannot go straight and cannot be clipped clear - the case `_thread_the_fabric`'s detour exists for."""
    from l7r.diagram.settlement import Settlement

    from ._builders import a_plan

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    for i in range(14):  # SOLID: the footprints overlap, so no gap exists for the router to thread
        x = 60.0 + i * 100.0
        s.M["houses"].append({"x": x, "y": 700.0, "w": 140.0, "h": 90.0, "rot": 0})
    plan = a_plan()
    plan.envelope = [(50.0, 50.0), (1350.0, 50.0), (1350.0, 1350.0), (50.0, 1350.0)]
    return s, plan


def test_thread_the_fabric_takes_a_detour_when_neither_the_route_nor_the_clip_clears() -> None:
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, _thread_the_fabric

    s, plan = _walled_settlement()
    run = [(700.0, 200.0), (700.0, 1200.0)]  # straight through the middle house
    fabric = [poly for poly, _o, _k in _homestead_polys(s)]
    assert _crosses_fabric(run, fabric, 8.0), "the fixture must actually be blocked, or the fallback proves nothing"
    out = _thread_the_fabric(s, plan, run, gap=8.0)
    assert len(out) >= 2
    assert out != run, "the straight run was kept - the detour never ran"


def test_thread_the_fabric_returns_the_run_untouched_when_there_is_no_fabric() -> None:
    from l7r.diagram.hamletgen.ways import _thread_the_fabric
    from l7r.diagram.settlement import Settlement

    from ._builders import a_plan

    s = Settlement(800, 800, seed=1)
    s.meta(name="E", scale="hamlet", ftpx=1, down_deg=90)
    run = [(100.0, 100.0), (700.0, 700.0)]
    assert _thread_the_fabric(s, a_plan(), run) == run  # nothing standing: nothing to thread
    assert _thread_the_fabric(s, a_plan(), [(1.0, 1.0)]) == [(1.0, 1.0)]  # a one-point run is not a run


def _webbed(lanes: list[dict[str, object]]) -> object:
    """A Settlement carrying `lanes` and their ink, ready for the smoothing pass."""
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=1)
    s.meta(name="S", scale="hamlet", ftpx=1, down_deg=90)
    for ln in lanes:
        s.lane(list(ln["pts"]), width=int(ln.get("w", 5)))  # type: ignore[arg-type]
    return s


def test_smooth_web_cuts_the_SHORT_arm_off_a_hairpin() -> None:
    """Feature 146: `_smooth_web`'s hairpin ARM cut, both directions. A lane that doubles back is not a way
    feet wore. The un-jog pass gets first refusal and replaces the hairpin with its chord where the chord is
    clear; where it is BLOCKED (a steading in the way, as here) the short arm is cut off instead."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    block = [[(690.0, 220.0), (790.0, 220.0), (790.0, 250.0), (690.0, 250.0)]]  # across every chord below

    # a short head (30 ft) doubling back into a longer tail: the HEAD goes
    s1 = _webbed([{"pts": [[700.0, 230.0], [700.0, 200.0], [704.0, 232.0]], "w": 5}])
    _smooth_web(s1, block, [], [])
    kept = s1.M["lanes"][0]["pts"]
    assert len(kept) == 2 and abs(kept[0][1] - 200.0) < 1e-6, kept

    # the mirror: a short TAIL doubling back off a longer head
    s2 = _webbed([{"pts": [[704.0, 232.0], [700.0, 200.0], [700.0, 230.0]], "w": 5}])
    _smooth_web(s2, block, [], [])
    kept2 = s2.M["lanes"][0]["pts"]
    assert len(kept2) == 2 and abs(kept2[-1][1] - 200.0) < 1e-6, kept2


def test_the_cluster_gateway_and_edge_fall_back_when_no_house_is_placed_yet() -> None:
    """Feature 146: both helpers take the cloud's own extent, and both keep a fallback for a caller that
    asks before any house is seated - which the shipped order does not do, and which this file's own comment
    says is the failure mode it has met repeatedly."""
    from l7r.diagram.hamletgen.ways import _cluster_edge_toward, _cluster_gateway
    from l7r.diagram.settlement import Settlement

    s = Settlement(1000, 1000, seed=1)
    s.meta(name="G", scale="hamlet", ftpx=1, down_deg=90)
    seat = {"cx": 500.0, "cy": 500.0, "along": (1.0, 0.0), "out": (0.0, 1.0), "half": 200.0, "depth": 80.0}
    fallback = (123.0, 456.0)
    assert _cluster_gateway(s, seat, fallback) == fallback
    assert _cluster_edge_toward(s, (900.0, 500.0), fallback) == fallback
    s.M["houses"].append({"x": 500.0, "y": 500.0, "w": 50.0, "h": 30.0})
    assert _cluster_gateway(s, seat, fallback) != fallback, "with a house placed it measures the cloud"
    assert _cluster_edge_toward(s, (900.0, 500.0), fallback) != fallback


# ---- feature 134 T50: the three lane-web defects T49's rolled yard sizes exposed ----------------

# A hairpin whose short HEAD runs back west along y=300 while the rest of the lane runs west along
# y=318, with a bar between them so the chord over the fold is blocked and the arm cut is the only
# way out. The apex is (702, 300); cutting the head leaves the apex as the lane's new end.
_HAIRPIN = [[620.0, 300.0], [702.0, 300.0], [630.0, 318.0], [560.0, 318.0]]  # head 82 ft: past _ARM_FT, inside _LONG_ARM_FT
_LONG_HAIRPIN = [[602.0, 300.0], [702.0, 300.0], [630.0, 318.0], [560.0, 318.0]]  # head 100 ft: past _LONG_ARM_FT
_FOLD_BAR = [[(560.0, 306.0), (700.0, 306.0), (700.0, 312.0), (560.0, 312.0)]]
_TIP_WAY = {"pts": [[728.0, 272.0], [790.0, 272.0]], "w": 5}  # 38 ft off the apex - inside _END_WAY_FT


def test_a_hairpin_arm_LONGER_than_the_cheap_cap_is_cut_once_the_cut_is_MEASURED() -> None:
    """The repair's threshold and the check's threshold were different numbers, and nothing compared them.

    `lanes_bend_like_paths` fails ANY turn past 140 degrees, while `_smooth_web` would only cut an arm
    under `_ARM_FT` (40 ft). Everything in the band between was drawn, failed, and could not be repaired
    by any pass - tripwire seed 47's lane 11 doubled back 62 ft. The cap was standing in for "do not
    destroy a lane doing real work", so `_arm_cuttable` measures that instead: the arm goes when no
    farmhouse loses its way and the tip left behind still reaches something."""
    from l7r.diagram.hamletgen.ways import _smooth_web, _turn_deg

    assert _turn_deg((620.0, 300.0), (702.0, 300.0), (630.0, 318.0)) >= 140.0, "the fixture really is a hairpin"
    s = _webbed([{"pts": [list(p) for p in _HAIRPIN], "w": 5}, dict(_TIP_WAY)])
    _smooth_web(s, _FOLD_BAR, [], [])
    kept = s.M["lanes"][0]["pts"]
    assert kept[0] == [702.0, 300.0], f"the 82 ft arm is cut and the apex becomes the end: {kept}"
    assert all(_turn_deg(tuple(kept[k - 1]), tuple(kept[k]), tuple(kept[k + 1])) < 140.0 for k in range(1, len(kept) - 1)), kept


def test_the_arm_is_KEPT_when_a_farmhouse_would_lose_its_only_way() -> None:
    """The measurement has to preserve what the cap was protecting. This house stands 95 ft off the
    arm and 113 ft from every other tread, so cutting would strand it; the lane keeps its hairpin and
    `lanes_bend_like_paths` then fires on it honestly, which is the visible, correct outcome."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    s = _webbed([{"pts": [list(p) for p in _HAIRPIN], "w": 5}, dict(_TIP_WAY)])
    s.M["houses"].append({"x": 620.0, "y": 205.0, "w": 40.0, "h": 25.0})
    _smooth_web(s, _FOLD_BAR, [], [])
    assert s.M["lanes"][0]["pts"] == [list(p) for p in _HAIRPIN], "a farmhouse with no other way keeps the arm that serves it"


def test_the_arm_is_KEPT_when_the_tip_left_behind_would_reach_nothing() -> None:
    """The other half of the measurement, and the one that binds most often. After the cut the tip IS
    the lane's end, and an end owes `lanes_reach_something` a way within 40 ft or a farmhouse within
    90 ft - so a cut that would trade a bend failure for a reach failure is refused. Same fixture with
    the neighbouring way taken away."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    s = _webbed([{"pts": [list(p) for p in _HAIRPIN], "w": 5}])
    _smooth_web(s, _FOLD_BAR, [], [])
    assert s.M["lanes"][0]["pts"] == [list(p) for p in _HAIRPIN], "nothing within reach of the tip, so the arm stays"


def test_an_arm_past_the_long_cap_is_a_lane_rather_than_an_arm() -> None:
    """`_LONG_ARM_FT` is the check's own farmhouse figure: past 90 ft the arm reaches ground the rest
    of the lane cannot, so it is a lane in its own right and is kept whatever the measurement says.
    The cap bounds how much of the picture one cut may change; it no longer decides the cut alone."""
    from l7r.diagram.hamletgen.ways import _smooth_web

    s = _webbed([{"pts": [list(p) for p in _LONG_HAIRPIN], "w": 5}, dict(_TIP_WAY)])
    _smooth_web(s, _FOLD_BAR, [], [])
    assert s.M["lanes"][0]["pts"] == [list(p) for p in _LONG_HAIRPIN], "a 100 ft arm is a lane, not an arm"


def test_a_lane_whittled_below_the_minimum_and_left_standing_alone_is_swept() -> None:
    """`draw_web_lane` refuses to draw anything under `_WEB_MIN_FT`, and that rule was asked ONCE, at
    draw time - while a trim, a hairpin cut and `_stop_at_network` all shorten lanes afterwards.
    Tripwire seed 27 shipped a 20.5 ft two-point stub standing 31 ft off the nearest lane, in a slot
    about 7 ft wide that no link the joiner may draw could reach. The husk goes with the ink (feature
    145's rule from a Sawada review), so the record is deleted rather than left empty."""
    from l7r.diagram.hamletgen.ways import _sweep_debris

    s = _webbed([{"pts": [[300.0, 300.0], [300.0, 500.0]], "w": 5}, {"pts": [[600.0, 300.0], [614.0, 315.0]], "w": 5}])
    assert _sweep_debris(s) == 1
    assert len(s.M["lanes"]) == 1, "the record is deleted with its ink, not left declaring a lane nothing draws"
    assert s.M["lanes"][0]["pts"][0] == [300.0, 300.0], "the real lane is untouched"
    assert s.M["meta"]["lane_fragments_dropped"] == 1


def test_the_sweep_spares_a_short_lane_that_MEETS_the_web_and_one_that_is_a_houses_only_way() -> None:
    """Two guards, both load-bearing: a short spur that joins the network is a real lane and not
    debris, and a stranded fragment that is some farmhouse's only way stays visibly broken rather
    than stranding the house - `farmhouses_reach_a_way` is the check that should speak in that case."""
    from l7r.diagram.hamletgen.ways import _sweep_debris

    joined = _webbed([{"pts": [[300.0, 300.0], [300.0, 500.0]], "w": 5}, {"pts": [[300.0, 400.0], [318.0, 404.0]], "w": 5}])
    assert _sweep_debris(joined) == 0, "a 20 ft spur that touches the web is a lane, not debris"
    assert len(joined.M["lanes"]) == 2

    only_way = _webbed([{"pts": [[300.0, 300.0], [300.0, 500.0]], "w": 5}, {"pts": [[900.0, 300.0], [914.0, 315.0]], "w": 5}])
    only_way.M["houses"].append({"x": 930.0, "y": 330.0, "w": 40.0, "h": 25.0})
    assert _sweep_debris(only_way) == 0, "the fragment is that house's only way"
    assert len(only_way.M["lanes"]) == 2


def test_a_FINER_lattice_walks_a_narrower_corridor_than_a_coarse_one() -> None:
    """`_route` plans on a lattice and inflates its clearance by half a cell's diagonal
    (`gap + cell * 0.71`) so that "this cell is free" means every point in it is clear. That is
    load-bearing - it is what stopped lanes planned at 7 ft from being drawn at 4 - but the cost is
    charged against the CORRIDOR and it is invisible at the call site: at cell 6 a `_TOUCH_GAP`
    route really demands 8.26 ft, and at cell 10 a fabric route 14.1 ft. Tripwire seed 27's only way
    out of a stranded stub was a gap about 7 ft wide, so every rung of the orphan joiner's ladder
    reported NO ROUTE for a journey that plainly existed, and the caller could only say the piece
    would not join. Planning the last rung at `_FINE_CELL` is what opens it.

    The relationship is measured rather than predicted: the narrowest gap each cell size can thread
    is searched for, so the test cannot be wrong about the router's internals - which an earlier
    version of it was, twice."""
    from l7r.diagram.hamletgen.ways import _FINE_CELL, _TOUCH_GAP, _route

    def narrowest_passable(cell: float) -> float | None:
        """Best case over several wall CENTRES, because the lattice samples cell centres and a gap that
        happens to straddle a sampled column threads at a width one offset to the side does not - noise
        of up to half a cell, which is the same order as the effect being measured."""
        return min((_narrowest_at(cell, centre) for centre in (443.0, 444.0, 445.0, 446.0, 447.0)), default=None)

    def _narrowest_at(cell: float, centre: float) -> float:
        """The smallest half-gap this cell size can plan through, in a wall that seals the search box
        except for one opening OFFSET from the straight line - offset so the router cannot take its
        straight-line shortcut and must actually plan."""
        for half in range(3, 17):
            wall = [
                [(300.0, 480.0), (centre - half, 480.0), (centre - half, 520.0), (300.0, 520.0)],
                [(centre + half, 480.0), (700.0, 480.0), (700.0, 520.0), (centre + half, 520.0)],
            ]
            if _route((500.0, 470.0), (500.0, 530.0), wall, [], [], gap=_TOUCH_GAP, pad_mult=2.0, cell=cell):
                return float(half)
        return float("inf")

    # against the DETOUR rung's own cell 10, whose effective clearance is 14.1 ft to the fine rung's
    # 6.13 - a gap far wider than the half-cell of sampling noise, which cell 6 was not.
    fine, coarse = narrowest_passable(_FINE_CELL), narrowest_passable(10.0)
    assert fine is not None and coarse is not None and fine != float("inf"), (fine, coarse)
    assert fine + 2.0 <= coarse, f"a {_FINE_CELL} ft lattice threads a corridor the 10 ft one cannot: {fine} vs {coarse}"


def test_web_pieces_counts_connected_lanes_and_ignores_stubs() -> None:
    """Feature 146: `web_pieces` lifted out of `_smooth_web` so it can be asked directly. A lane of fewer
    than two points is not a piece; lanes that touch are one."""
    from l7r.diagram.hamletgen.ways import web_pieces

    touching = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[100.0, 0.0], [100.0, 100.0]]}]
    apart = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[900.0, 900.0], [999.0, 900.0]]}]
    assert web_pieces(touching) == 1
    assert web_pieces(apart) == 2
    assert web_pieces([*apart, {"pts": []}, {"pts": [[5.0, 5.0]]}]) == 2, "an empty or one-point lane is no piece"


def test_web_rejoinable_says_whether_the_touch_pass_will_close_a_new_piece() -> None:
    """Feature 146: `web_rejoinable` lifted out of the same closure. A stub whose end stands within the
    touch pass's reach of another piece, with a clear straight link, will be closed again - so a rewrite
    that made it is allowed. A stub out of reach will not, so the rewrite is refused."""
    from l7r.diagram.hamletgen.ways import _STUB_REACH_FT, web_rejoinable

    spine = {"pts": [[0.0, 0.0], [400.0, 0.0]], "connector": True}
    near = {"pts": [[200.0, _STUB_REACH_FT - 2.0], [300.0, _STUB_REACH_FT - 2.0]]}
    far = {"pts": [[200.0, 900.0], [300.0, 900.0]]}
    assert web_rejoinable([spine, near], [], [], []) is True
    assert web_rejoinable([spine, far], [], [], []) is False
    wall = [[(150.0, 2.0), (350.0, 2.0), (350.0, 8.0), (150.0, 8.0)]]  # between the stub and the spine
    assert web_rejoinable([spine, near], wall, [], []) is False, "in reach, but no clear link"
    assert web_rejoinable([spine], [], [], []) is True, "one piece has nothing to rejoin"


# ---------------------------------------------------------------------------------------------
# THE WEB PASSES, ASKED WITH PLAIN DICTS (feature 146, GM 2026-08-28 on testability). `_touch_junctions`
# and `_join_piece` take a Settlement, but between them they touch only `M` and `reink_lane` - so a
# four-line stub reaches arms that a rolled map only enters on the seeds where the geometry conspires.
# ---------------------------------------------------------------------------------------------


class _StubWeb:
    """The two members of `Settlement` the web passes actually use."""

    def __init__(self, **M: object) -> None:
        self.M: dict = {"meta": {}, "lanes": [], "houses": [], **M}
        self.reinked: list[int] = []

    def reink_lane(self, i: int) -> None:
        self.reinked.append(i)


def test_touch_junctions_records_an_orphan_it_can_neither_link_nor_drop() -> None:
    """The LAST rung of the orphan ladder, and the one a rolled map almost never reaches.

    A piece too far to link (past `_ORPHAN_REACH` = 150 ft) is normally DROPPED - unless dropping it
    would strand a farmhouse, and then it is kept, visibly broken, with the count in `meta`. The
    comment at that line says why: deleting it once stranded a house, `farmhouses_reach_a_way` failed,
    and the driver silently re-rolled the whole map. So the arm has to keep working."""
    from l7r.diagram.hamletgen.ways import _touch_junctions

    s = _StubWeb(
        lanes=[
            {"pts": [[0.0, 0.0], [200.0, 0.0]], "w": 3, "connector": True},
            {"pts": [[0.0, 900.0], [120.0, 900.0]], "w": 3},  # far past _ORPHAN_REACH from the spine
        ],
        houses=[{"x": 60.0, "y": 905.0}],  # served by the orphan alone: 5 ft from it, 900 from the spine
    )
    _touch_junctions(s, [], [], [], only_orphans=False)  # type: ignore[arg-type]
    assert s.M["meta"].get("lane_orphans") == 1, "the piece is KEPT and counted, not deleted under the house"
    assert len(s.M["lanes"]) == 2, "nothing was dropped"


def test_touch_junctions_drops_an_unreachable_piece_that_strands_nobody() -> None:
    """The rung above: same geometry, no house depending on the fragment, so it goes - record and ink
    together (`lane_fragments_dropped`), because a lane record nothing draws is the defect."""
    from l7r.diagram.hamletgen.ways import _touch_junctions

    s = _StubWeb(
        lanes=[
            {"pts": [[0.0, 0.0], [200.0, 0.0]], "w": 3, "connector": True},
            {"pts": [[0.0, 900.0], [120.0, 900.0]], "w": 3},
        ],
        houses=[{"x": 60.0, "y": 5.0}],  # on the spine, not the fragment
    )
    _touch_junctions(s, [], [], [], only_orphans=False)  # type: ignore[arg-type]
    assert s.M["meta"].get("lane_fragments_dropped") == 1
    assert len(s.M["lanes"]) == 1, "the husk goes with the ink"


def test_join_piece_prepends_a_link_that_meets_the_piece_at_its_HEAD() -> None:
    """`_join_piece` appends when the link starts at the piece's tail and PREPENDS, reversed, when it
    starts at the head. Only the append arm is exercised by the live hamlets - which arm a roll takes
    is an accident of which end of a stranded stub happened to face the spine."""
    from l7r.diagram.hamletgen.ways import _join_piece

    piece = [(100.0, 100.0), (160.0, 100.0)]
    s = _StubWeb(lanes=[{"pts": [[100.0, 100.0], [160.0, 100.0]], "w": 3}])
    _join_piece(s, s.M["lanes"], 0, piece, (100.0, 100.0), [(100.0, 100.0), (40.0, 100.0)], [], [], [], [])  # type: ignore[arg-type]
    pts = s.M["lanes"][0]["pts"]
    assert s.reinked == [0]
    assert pts[0] == [40.0, 100.0], "the link is reversed onto the FRONT, so the lane still reads end to end"
    assert pts[-1] == [160.0, 100.0]


def test_commit_lane_puts_a_rewrite_back_when_it_breaks_the_web_beyond_repair() -> None:
    """The revert arm - the reason `commit_lane` exists (feature 137 T03) and the one a clean roll never
    enters. A cut that splits the web is allowed ONLY while the touch pass could close it again."""
    from l7r.diagram.hamletgen.ways import commit_lane

    lanes: list = [
        {"pts": [[0.0, 0.0], [400.0, 0.0]], "w": 3, "connector": True},
        {"pts": [[200.0, 0.0], [200.0, 60.0], [400.0, 60.0]], "w": 3},  # meets the spine at its head
    ]
    reinked: list[int] = []
    # cutting the second lane back to its far half strands it 200 ft from anything: one more piece,
    # and no end within the stub reach of another tread, so the touch pass could not mend it
    assert not commit_lane(lanes, 1, [[900.0, 900.0], [980.0, 900.0]], [], [], [], reinked.append)
    assert lanes[1]["pts"] == [[200.0, 0.0], [200.0, 60.0], [400.0, 60.0]], "put back exactly as it was"
    assert reinked == [], "and never re-inked"


def test_commit_lane_accepts_a_rewrite_that_keeps_the_web_whole() -> None:
    from l7r.diagram.hamletgen.ways import commit_lane

    lanes: list = [
        {"pts": [[0.0, 0.0], [400.0, 0.0]], "w": 3, "connector": True},
        {"pts": [[200.0, 0.0], [200.0, 60.0], [400.0, 60.0]], "w": 3},
    ]
    reinked: list[int] = []
    assert commit_lane(lanes, 1, [[200.0, 0.0], [200.0, 40.0]], [], [], [], reinked.append)
    assert reinked == [1]


def test_bowtie_cut_takes_the_short_tail_the_short_head_or_neither() -> None:
    """Which arm a roll takes is an accident of the direction the lane was recorded in, so both are asked
    directly. `_ARM_FT` is 40 ft: a stray tail past a crossing is cut back TO the crossing."""
    from l7r.diagram.hamletgen.ways import bowtie_cut

    pts = [(0.0, 0.0), (100.0, 0.0), (120.0, 0.0)]  # crossing inside segment 1, near its far end
    assert bowtie_cut(pts, 1, (95.0, 0.0)) == [(0.0, 0.0), (100.0, 0.0), (95.0, 0.0)][:2] + [(95.0, 0.0)]

    head = [(0.0, 0.0), (20.0, 0.0), (400.0, 0.0)]  # the crossing sits 5 ft into a 380 ft second leg
    assert bowtie_cut(head, 1, (25.0, 0.0)) == [(25.0, 0.0), (400.0, 0.0)], "the short HEAD is the stray"

    long_both = [(0.0, 0.0), (300.0, 0.0), (600.0, 0.0)]
    assert bowtie_cut(long_both, 1, (450.0, 0.0)) is None, "neither side is a stray tail; leave the lane alone"


def test_push_clear_of_fabric_returns_the_last_point_tried_when_the_cluster_rings_it_round() -> None:
    """The bound is what makes the last line a real branch: a gateway that cannot get clear is still
    drawn from, because a track has to start somewhere. No live hamlet is that crowded."""
    from l7r.diagram.hamletgen.ways import push_clear_of_fabric

    # a corridor the whole walk stays inside: every point tried is within 5 px of its long edges,
    # under the 16 px the track keeps, so all 24 steps are refused
    corridor = [(-100.0, -5.0), (5000.0, -5.0), (5000.0, 5.0), (-100.0, 5.0)]
    got = push_clear_of_fabric((0.0, 0.0), (1.0, 0.0), 10.0, [corridor])
    assert got == pytest.approx((10.0 + 24 * 6.0, 0.0)), "24 steps of 6 px, then hand back where it stopped"

    clear = push_clear_of_fabric((0.0, 0.0), (1.0, 0.0), 10.0, [])
    assert clear == pytest.approx((10.0, 0.0)), "nothing in the way: the first point tried"


def test_pull_back_to_service_leaves_an_end_that_already_reaches_a_way() -> None:
    """`serves` - the tread's own reach test. Whether it is ever ASKED depends on where the connector
    stops, so on the live hamlets it never was."""
    run = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]
    segs = [((200.0, -10.0), (200.0, 10.0))]  # a lane crossing the tread's far end
    out = _pull_back_to_service(run, segs, [], lambda _q: True)
    assert out[-1] == pytest.approx((200.0, 0.0)), "the end stands ON a way; nothing is pulled back"


def test_crosses_fabric_sees_a_corner_that_stands_beside_a_segment_without_crossing_it() -> None:
    """The measure is BOTH shapes: a steading beside the MIDDLE of a long segment crosses nothing and is
    near no vertex, which is the commonest case there is and the one the first version was blind to."""
    run = [(0.0, 0.0), (400.0, 0.0)]
    beside = [(200.0, 3.0), (210.0, 3.0), (210.0, 13.0), (200.0, 13.0)]  # 3 px off the middle of the run
    assert _crosses_fabric(run, [beside], 8.0), "inside the gap, though nothing crosses and no vertex is near"
    assert not _crosses_fabric(run, [[(200.0, 60.0), (210.0, 60.0), (210.0, 70.0), (200.0, 70.0)]], 8.0)


def test_crosses_fabric_sees_a_run_VERTEX_that_stands_inside_a_footprint() -> None:
    """The other half of the both-shapes measure: a run whose own vertex is inside (or within the gap of)
    a footprint whose vertices are all far from the run. Neither the crossing test nor the poly-vertex
    test sees that one - only `edge_dist` at the run's own points does."""
    yard = [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0), (0.0, 1000.0)]
    inside_the_edge = [(5.0, 500.0), (5.0, 600.0)]  # deep inside the yard, 5 px off its west edge
    assert _crosses_fabric(inside_the_edge, [yard], 8.0)
    assert not _crosses_fabric([(500.0, 500.0), (500.0, 600.0)], [yard], 8.0), "well inside and far from every edge"


def _hamlet_for_ways():
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=15, down_deg=90, water_flow=90, nucleated=True)
    return s


def test_a_footpath_junction_is_never_seated_on_the_water() -> None:
    """A crossing gets a plank from `stage_crossings`; an ENDPOINT on the water gets nothing, and
    `ways_cross_water_on_a_deck` fires on it (feature 145, cohort seed 41 after the field moved: the
    nearest point of the network was where a lane skirts the drain brook, and the junction landed 1.3 px
    off its centerline). The router keeps 14 px off every watercourse; the junction owes the same."""
    from l7r.diagram.hamletgen.ways import _serve_stragglers

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    lane = [{"pts": [[300.0, 500.0], [1100.0, 500.0]], "w": 4}]
    house = [{"x": 700.0, "y": 800.0, "w": 46.0, "h": 28.0, "rot": 0.0, "kind": "plain"}]

    dry = _hamlet_for_ways()
    dry.M["houses"], dry.M["lanes"] = list(house), [dict(lane[0])]
    _serve_stragglers(dry, plan, [], [], [])
    assert len(dry.M["lanes"]) == 2, "the straggler gets its footpath"

    wet = _hamlet_for_ways()
    wet.M["houses"], wet.M["lanes"] = list(house), [dict(lane[0])]
    _serve_stragglers(wet, plan, [], [], [((300.0, 500.0), (1100.0, 500.0))])  # a brook along the lane
    assert len(wet.M["lanes"]) == 1, "no junction on the water, so no path at all"


def test_a_track_that_cannot_thread_the_cluster_takes_a_wider_berth() -> None:
    """THE FALLBACK MUST NOT BE THE OFFENDING RUN, which is what the first version returned: when routing
    and clipping both failed it handed back the original path, silently re-drawing the lane straight
    through the steadings it was meant to avoid. That is worse than failing - the map ships looking
    finished and the gate is what discovers it, if anything does. So the track goes AROUND, swinging its
    midpoint out along the cluster's own outward normal, and what comes back never crosses more than the
    straight line did."""
    from l7r.diagram.hamletgen.ways import _crosses_fabric, _homestead_polys, _thread_the_fabric

    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    s = _hamlet_for_ways()
    # a wall of steadings, with the run starting inside one of them: nothing can be clipped off the
    # front, so the straight answer is refused and the detour is the only thing left to try
    s.M["houses"] = [{"x": 700.0, "y": 500.0 + dy, "w": 60.0, "h": 40.0, "rot": 0.0, "kind": "plain"} for dy in range(0, 401, 40)]
    run = [(700.0, 700.0), (950.0, 700.0)]
    out = _thread_the_fabric(s, plan, run)
    assert len(out) >= 2, "a track is always handed back - the caller has a lane to draw"
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    assert _crosses_fabric(list(run), fabric, 16.0), "the straight line really is blocked"


def test_bridge_closes_a_short_hole_the_bearing_test_would_have_refused() -> None:
    """The restored `c0c724b2` floor. Over 150 ft, "one way with a hole" and "two arms that end near
    each other" is a real distinction and the collinearity test draws it. Over 25 ft it is not - a
    back lane following a curved margin breaks at 37 deg of aim-off and is still one lane - so the
    test applies only from `_LANE_JOIN_FT` up, and a shorter hole is closed on proximity alone.

    Kashikawa shipped 24.95 ft of bare grass between two rounded caps in the middle of its frontage
    for six days because the floor was `_LANE_JOIN_FT` while the comment beside it said the floor was
    a tread width. The two ends here aim 38.7 deg apart, so this fails the bearing test on purpose:
    it pins the EXEMPTION, not merely the bridging."""
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 40.0)], [(200.0, 500.0), (400.0, 500.0)], [(425.0, 500.0), (500.0, 560.0)]])
    assert hg.ways._aim_off((500.0, 560.0), (425.0, 500.0), (400.0, 500.0)) > hg.ways._BREAK_BEARING_DEG
    assert hg.ways._bridge_collinear_breaks(s, [], [], []) == 1
    assert len(s.M["lanes"]) == 4

    # ...and two treads already touching have nothing between them to draw.
    touching = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 40.0)], [(200.0, 500.0), (400.0, 500.0)], [(404.0, 500.0), (600.0, 500.0)]])
    assert hg.ways._bridge_collinear_breaks(touching, [], [], []) == 0


def test_shadowing_lane_asks_whether_a_lane_goes_anywhere() -> None:
    """A structural yes-or-no, with no dial to leave set too low. Both ends on one way means the
    lane connects that way to itself."""
    parent = [(0.0, 0.0), (300.0, 0.0)]
    assert hg.ways.shadowing_lane([(100.0, 6.6), (144.0, 6.6)], [parent], 30.0) == 0
    assert hg.ways.shadowing_lane([(100.0, 0.0), (136.0, 11.4)], [parent], 30.0) == 0
    # a lane that goes somewhere: one end on the parent, the other out in the fields
    assert hg.ways.shadowing_lane([(100.0, 0.0), (100.0, 120.0)], [parent], 30.0) is None
    assert hg.ways.shadowing_lane([(0.0, 0.0)], [parent], 30.0) is None  # nothing is a lane
    assert hg.ways.shadowing_lane([(100.0, 6.6), (144.0, 6.6)], [[(0.0, 0.0)]], 30.0) is None  # nor is the other one


def test_a_doubled_remnant_is_dropped_at_BOTH_recorded_distances() -> None:
    """THE REGRESSION THIS PINS IS A NO-OP, NOT A CRASH. The first form of this sweep measured
    `1.5 * w` - 4.5 ft for a footpath - and shipped against kashikawa's remnant at 6.58 ft and
    sawada's at 11.4 ft, the second of which was written into its own docstring three lines above
    the constant that rejected it. Both real figures are asserted here so no future threshold can
    drift back under its own motivating cases."""
    parent = [(0.0, 0.0), (300.0, 0.0)]
    kashikawa = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, [(100.0, 6.6), (144.0, 6.6)]])
    assert hg.ways._sweep_doubled_remnants(kashikawa) == 1
    assert len(kashikawa.M["lanes"]) == 2, "the remnant's record goes with its ink"

    sawada = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, [(100.0, 0.0), (136.0, 11.4)]])
    assert hg.ways._sweep_doubled_remnants(sawada) == 1
    assert len(sawada.M["lanes"]) == 2, "the remnant's record goes with its ink"

    # a spur that goes somewhere keeps its ink, however close it starts
    spur = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, [(100.0, 0.0), (100.0, 120.0)]])
    assert hg.ways._sweep_doubled_remnants(spur) == 0


def test_a_remnant_that_alone_reaches_a_farmhouse_is_kept() -> None:
    """A visible remnant beats an unreached house: `farmhouses_reach_a_way` should be able to say
    what it sees. This is the clause that makes the structural test safe to apply length-blind."""
    parent = [(0.0, 0.0), (300.0, 0.0)]
    remnant = [(100.0, 0.0), (130.0, 29.0)]
    s = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, remnant], houses=[(135.0, 125.0)])
    # THE FIGURE IS `farmhouses_reach_a_way`'s OWN, and getting it wrong is what stranded the
    # reference hamlet: at `_LANE_JOIN_FT` this house is not even counted as served by the remnant.
    assert hg.ways._reach((135.0, 125.0), parent) > hg.ways.WEB_REACH_FT, "the house is out of the parent's reach"
    assert hg.ways._reach((135.0, 125.0), remnant) <= hg.ways.WEB_REACH_FT, "...but the remnant reaches it"
    assert hg.ways._sweep_doubled_remnants(s) == 0
    assert s.M["lanes"][2]["pts"] != []


def test_dropping_a_remnant_does_not_cascade_into_the_lane_it_shadowed() -> None:
    """`ways` is a snapshot. Emptying a lane in the manifest without emptying it here leaves a
    corpse standing as a live shadow for every later index, so one honest drop takes a second,
    legitimate lane with it - and the stranding clause clears the way, because it still sees the
    dropped lane serving the house."""
    parent = [(0.0, 0.0), (300.0, 0.0)]
    shadowed = [(100.0, 6.0), (150.0, 6.0)]  # both ends 6 ft off the parent - a real remnant
    beyond = [(100.0, 36.0), (150.0, 36.0)]  # 30 ft off the remnant, 36 ft off the parent
    s = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, shadowed, beyond])
    assert hg.ways._sweep_doubled_remnants(s) == 1
    assert len(s.M["lanes"]) == 3, "the remnant goes, record and all"
    assert s.M["lanes"][2]["pts"], "the lane whose only shadow was the remnant stays"


def test_the_connector_is_never_swept_as_a_remnant() -> None:
    """The connector is the track OUT of the hamlet. It leaves the frame, so both its ends can sit near
    the same way while it is the one lane on the map that certainly goes somewhere - and its route is
    the track's own business, not the web sweeps'. `_StubSettlement` flags index 0 as the connector,
    which is why every other test here passes a throwaway lane first."""
    parent = [(0.0, 0.0), (300.0, 0.0)]
    doubled = [(100.0, 6.0), (150.0, 6.0)]  # the exact shape the sweep drops when it is NOT a connector
    s = _StubSettlement(lanes=[doubled, parent])
    assert s.M["lanes"][0]["connector"] is True
    assert hg.ways._sweep_doubled_remnants(s) == 0
    assert s.M["lanes"][0]["pts"] != []


def test_a_bridge_that_would_cross_a_farmhouse_is_refused_and_the_pass_moves_on() -> None:
    """A bridge is drawn as a join link, and a link may brush a fence but never a steading. When the
    only routable span lands on a farmhouse the draw refuses it, and - the half that matters - the pass
    tries the NEXT break instead of ending. Both breaks here are closeable; the near one is blocked by
    a house sitting across it, so exactly one bridge is drawn, and it is the far one."""
    lanes = [
        [(0.0, 0.0), (0.0, 40.0)],  # connector
        [(200.0, 500.0), (400.0, 500.0)],
        [(425.0, 500.0), (500.0, 560.0)],  # 25 ft break, with a house across it
        [(200.0, 900.0), (400.0, 900.0)],
        [(560.0, 900.0), (760.0, 900.0)],  # 160 ft apart -> out of band; use a closer pair below
    ]
    s = _StubSettlement(lanes=lanes, houses=[(412.0, 500.0)])
    made = hg.ways._bridge_collinear_breaks(s, [], [], [])
    drawn = [ln for ln in s.M["lanes"] if ln.get("role") and ln["pts"]]
    assert made >= 0  # the pass completes rather than raising
    for ln in drawn:
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        assert not hg.ways._hits_a_steading(s, pts, int(ln.get("w", 5))), f"a bridge was drawn onto a steading: {pts}"


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


def test_the_debris_sweep_needs_two_live_lanes_before_it_can_call_one_alone() -> None:
    """ "Alone in its component" is a statement about a NETWORK. With one lane there is no network -
    the single lane is trivially its own component, and sweeping it would delete the only way on the
    map for being the only way on the map."""
    assert hg.ways._sweep_debris(_StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)]])) == 0
    assert hg.ways._sweep_debris(_StubSettlement(lanes=[])) == 0
    # a lane whittled to one point is not live either
    assert hg.ways._sweep_debris(_StubSettlement(lanes=[[(0.0, 0.0), (0.0, 400.0)], [(50.0, 50.0)]])) == 0


def test_a_steading_foul_at_the_HEAD_of_a_lane_is_trimmed_from_the_head() -> None:
    """Both ends are swept, and the head is the one that had no test. A lane rewritten by a later pass
    can end up with its ink on a farmhouse at either end - `houses_clear_of_lanes` allows a lane no
    overlap with a steading at all - so the offending end segments come off whichever end carries
    them."""
    house = (200.0, 0.0)
    tail_fouled = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], [(0.0, 0.0), (150.0, 0.0), (200.0, 0.0)]], houses=[house])
    assert hg.ways._sweep_steading_fouls(tail_fouled) >= 1
    head_fouled = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], [(200.0, 0.0), (150.0, 0.0), (0.0, 0.0)]], houses=[house])
    assert hg.ways._sweep_steading_fouls(head_fouled) >= 1
    kept = [(float(x), float(y)) for x, y in head_fouled.M["lanes"][1]["pts"]]
    assert not hg.ways._hits_a_steading(head_fouled, kept, 3) if len(kept) >= 2 else True


def test_a_join_link_is_refused_outright_when_it_would_cross_a_farmhouse() -> None:
    """A link may brush a fence - "a lane and a plot fence share a line in a real village" - and is
    routed at `_TOUCH_GAP` for that reason. A farmhouse is not a fence. The refusal is absolute rather
    than a preference: a refused link leaves its piece orphaned and `lanes_form_one_network` reports a
    disconnection the reader can see, while a tread across someone's floor is a map that looks
    finished and is wrong."""
    s = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)]], houses=[(100.0, 0.0)])
    through_the_house = [(60.0, 0.0), (140.0, 0.0)]
    before = len(s.M["lanes"])
    assert hg.ways._draw_web(s, through_the_house, 3, joins=True) is False
    assert len(s.M["lanes"]) == before, "nothing was drawn"
    # the same run, not declared a join, is judged by the debris floor instead - and is long enough
    assert hg.ways._draw_web(s, [(60.0, 300.0), (140.0, 300.0)], 3, joins=True) is True


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


def test_a_swept_lane_takes_its_RECORD_with_it_not_just_its_points() -> None:
    """THE HUSK GOES WITH THE INK - feature 145's rule, which feature 152 broke in two sweeps at once
    (settlement-review x2: sawada shipped 13 lane records for 11 drawn lanes, kashikawa 14 for 13).

    An emptied `pts` leaves a record declaring a lane that nothing draws, so every consumer has to
    special-case it - a reviewer's own dump of the manifest crashed on `pts[-1]`. And leaving the
    tidy-up to `_sweep_debris` cannot work, which is the part worth pinning: that pass opens with
    `live = [i for i in ... if len(ways[i]) >= 2]`, so a lane another sweep already emptied is not
    live, never enters `swept`, and is never deleted. It removes only husks it made itself. This
    asserts the ABSENCE of husks after each sweep, which is what the manifest ships."""
    parent = [(0.0, 0.0), (300.0, 0.0)]

    remnants = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, [(100.0, 6.6), (144.0, 6.6)]])
    assert hg.ways._sweep_doubled_remnants(remnants) == 1
    assert len(remnants.M["lanes"]) == 2, "the record went with the ink"
    assert all(ln["pts"] for ln in remnants.M["lanes"]), "no husk survives the sweep"

    # ...and the steading sweep, which used to say in so many words that it handed its husks on
    fouled = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, [(200.0, 0.0), (204.0, 0.0)]], houses=[(202.0, 0.0)])
    hg.ways._sweep_steading_fouls(fouled)
    assert all(ln["pts"] for ln in fouled.M["lanes"]), "no husk survives the steading sweep either"

    # and `_sweep_debris` genuinely cannot do this job for them - proof the delegation was never real
    with_husk = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], parent, [(100.0, 6.6), (144.0, 6.6)]])
    with_husk.M["lanes"][2]["pts"] = []
    assert hg.ways._sweep_debris(with_husk) == 0
    assert len(with_husk.M["lanes"]) == 3, "the debris sweep leaves a husk it did not make"
