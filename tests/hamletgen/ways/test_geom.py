"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways import _crosses_fabric, _reach, _trim_to_service

from ._builders import _walled_settlement


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


def test_reach_measures_the_nearest_point_of_a_path_not_its_ends() -> None:
    """The same measurement `farmhouses_reach_a_way` makes. Measuring to the ENDS would call a house
    beside the middle of a long lane unreached."""
    path = [(0.0, 0.0), (1000.0, 0.0)]
    assert _reach((500.0, 30.0), path) == pytest.approx(30.0)


def test_trim_to_service_pulls_an_end_back_to_what_it_serves() -> None:
    """A tread that stops in bare grass serves nobody. Trimming happens BEFORE the ink and before the
    join is computed - trimming afterwards moves the end out from under the link drawn to it."""
    run = [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (900.0, 0.0)]
    segs = [((0.0, -20.0), (0.0, 20.0))]
    out = hg.ways._trim_to_service(run, segs, [(100.0, 30.0)])
    assert out[-1] == (100.0, 0.0), "the 800 ft tail into nothing is dropped"
    assert out[0] == (0.0, 0.0), "the end that meets a way is kept"


def test_trim_to_service_walks_a_long_last_segment_in_and_never_drops_it_whole() -> None:
    """Pulled back to the last house it serves (0246's drawing page, "Lane ends"), 4 ft at a time - never a whole segment at
    once (feature 405 T12, D1). The house stands beside the long last segment: popping that segment left the end at (450, 0),
    50 ft short of the house; the walk stops where the segment still reaches it and the cut takes it to the house's foot."""
    run = [(0.0, 0.0), (450.0, 0.0), (1000.0, 0.0)]
    segs = [((0.0, -20.0), (0.0, 20.0))]
    out = _trim_to_service(run, segs, [(500.0, 30.0)])
    assert out[0] == (0.0, 0.0), "the end that meets a way is kept"
    assert out[-1] == pytest.approx((500.0, 0.0), abs=4.0), "the end stops beside the house it serves, not a segment short"


def test_a_run_that_serves_NOTHING_comes_back_too_short_to_draw() -> None:
    """The honest answer for a way with nothing at either end: it is handed back under two points, for the
    caller to drop, rather than rounded off to a two-point stub in the middle of a field.

    This test used to assert the opposite - "never trims below two points" - and it was right about the
    code path it reached, which was the looser private triple a caller got by passing no `end_reach`. Every
    engine caller already asked the gate's bar and so already got this behavior; feature 227 deleted the
    triple once nothing but this file could reach it, which made the walk unconditional and turned the old
    assertion into a statement about dead code. Nothing that ships changed."""
    run = [(5000.0, 5000.0), (5100.0, 5000.0), (5200.0, 5000.0)]
    assert len(hg.ways._trim_to_service(run, [], [])) < 2, "nothing is at either end, so there is no way to draw"
    way = [((5200.0, 4990.0), (5200.0, 5010.0))]
    assert len(hg.ways._trim_to_service(run, way, [])) < 2, "a run from a way to nothing is a road to nowhere (feature 261)"
    served = hg.ways._trim_to_service(run, way, [(4990.0, 5000.0)])
    assert len(served) >= 2, "...but a run from a way to a house keeps a drawable tread"


def test_route_goes_around_an_obstacle_rather_than_through_it() -> None:
    wall = [(40.0, -60.0), (60.0, -60.0), (60.0, 60.0), (40.0, 60.0)]
    path = hg.ways._route((0.0, 0.0), (100.0, 0.0), [wall], [], [], cell=8.0)
    assert path, "there is a way round the end of the wall"
    assert hg.ways.polyline_len(path) > 100.0, "going round costs more than the straight line"
    assert max(abs(q[1]) for q in path) > 40.0, "and it leaves the straight line to do it"


def test_net_reach_measures_the_paths_VERTICES_against_the_network() -> None:
    """Vertex-to-segment, not segment-to-segment, and the asymmetry is worth knowing: a long straight
    run whose middle passes close to a way but whose vertices do not will read as further off than it
    looks. The web samples its runs every few feet, so in practice the vertices are the line - but a
    caller handing it a two-point polyline gets the corner distance, not the perpendicular."""
    assert hg.ways._net_reach([(0.0, 50.0), (100.0, 50.0)], [((50.0, 0.0), (60.0, 0.0))]) == pytest.approx(64.031242, abs=1e-4)
    dense = [(float(x), 50.0) for x in range(0, 101, 5)]
    assert hg.ways._net_reach(dense, [((50.0, 0.0), (60.0, 0.0))]) == pytest.approx(50.0)


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


def test_an_end_served_by_a_house_stops_BESIDE_it_not_past_it() -> None:
    """THE ROAD TO NOWHERE (GM 2026-09-27): Inashiro's spine passed its last farmhouse and ran on 45 ft into the
    windbreak, every point of the tail still inside the 60 ft bar of the house's center. The tail is cut at the
    foot of the perpendicular from the house; an end that meets a way is left where it is."""
    segs = [((-120.0, -20.0), (-120.0, 20.0))]
    run = [(-120.0, 0.0), (-40.0, 0.0), (0.0, 0.0), (30.0, 0.0), (45.0, 0.0)]
    out = _trim_to_service(run, segs, [(0.0, 35.0)])
    assert out[-1] == (0.0, 0.0), "the two segments walking away from the house are taken off"
    assert out[0] == (-120.0, 0.0), "the end at the way has arrived, and stays"
    out = _trim_to_service([(-120.0, 0.0), (45.0, 0.0)], segs, [(0.0, 35.0)])
    assert out[-1] == pytest.approx((0.0, 0.0)), "a two-point tread is cut mid-segment, at the house"
    assert _trim_to_service([(-120.0, 0.0), (2.0, 0.0)], segs, [(0.0, 35.0)])[-1] == (2.0, 0.0), "a 2 ft overshoot is below the grain"
    toward = [(-120.0, 0.0), (0.0, 0.0), (45.0, 0.0)]
    assert _trim_to_service(toward, segs, [(0.0, 35.0), (70.0, 30.0)]) == toward, "still walking TO a second house: arriving there"
    assert _trim_to_service(run, [*segs, ((45.0, -20.0), (45.0, 20.0))], [(0.0, 35.0)]) == run, "an end at a way has arrived, however it walks"
    beside = [(-40.0, 0.0), (0.0, 0.0), (40.0, 0.0)]
    assert _trim_to_service(beside, [], [(0.0, 35.0)]) == beside, "both ends serve only the one house: a way beside it, not past it"
    assert _trim_to_service(run, [], [(0.0, 35.0), (-120.0, 30.0)])[-1] == (0.0, 0.0), "from ANOTHER house to this one, it stops here"


def test_closest_approach_keeps_a_tread_that_walks_away_from_its_ONLY_house() -> None:
    """A two-point tread whose every point moves away from the house: its other end is the arrival, and cutting
    this one to the start would leave a lane of no length."""
    from l7r.diagram.hamletgen.ways.geom import _stop_at_closest_approach

    assert _stop_at_closest_approach([(0.0, 0.0), (50.0, 0.0)], [(-10.0, 30.0)]) == [(0.0, 0.0), (50.0, 0.0)]
    assert _stop_at_closest_approach([(0.0, 0.0), (0.0, 0.0)], [(-10.0, 30.0)]) == [(0.0, 0.0), (0.0, 0.0)]


# ---- the dooryard a tread arrives at (feature 227 D11) --------------------------------------------

_GARDEN = [(70.0, -30.0), (130.0, -30.0), (130.0, 30.0), (70.0, 30.0)]
"""A steading's kitchen garden, 60 ft square, with its west fence at x=70."""


def test_end_serves_counts_ARRIVING_AT_A_STEADING() -> None:
    """A TREAD THAT STOPS AT THE DOORYARD HAS ARRIVED (feature 227 D11). Both pool maps that failed
    `lanes_reach_something` were this: a straggler footpath clipped at the garden fence of the one
    steading it was drawn for - 7.8 and 6.9 ft off it - and then measured 63 and 76 ft to a house
    CENTER, which is inside the house and not where anybody walks to."""
    end = (62.0, 0.0)
    assert not hg.ways.end_serves(end, (), [(160.0, 0.0)]), "the house center is 98 ft away: not served by the center rule"
    assert hg.ways.end_serves(end, (), [(160.0, 0.0)], steadings=[_GARDEN]), "...but it stands 8 ft from that steading's garden"


def test_arrival_is_a_TIGHT_distance_not_the_reach_bar() -> None:
    """And the reason it is its own constant. Measuring the footprint at `WAY_END_REACH_FT` instead would
    have passed three of Inashiro's skeleton arms with ends 56-60 ft from the nearest wall, which is a
    tread stopping in open ground - measured the same afternoon the two stragglers were fixed."""
    from l7r.diagram.hamletgen.consts import STEADING_ARRIVAL_FT, WAY_END_REACH_FT

    assert STEADING_ARRIVAL_FT < WAY_END_REACH_FT
    off = (70.0 - STEADING_ARRIVAL_FT - 8.0, 0.0)
    assert not hg.ways.end_serves(off, (), [(400.0, 400.0)], steadings=[_GARDEN])


def test_trim_keeps_a_straggler_end_standing_at_the_dooryard() -> None:
    """The placer and the check read the SAME body (`end_serves`), which is the whole of this fix: the
    trim used to measure houses by their centers at its own 90 ft bar while the gate measured centers at
    60, and neither could see the garden the tread had actually reached."""

    run = [(62.0, 0.0), (-40.0, 0.0), (-120.0, 0.0)]
    segs = [((-120.0, -20.0), (-120.0, 20.0))]
    assert _trim_to_service(run, segs, [(160.0, 0.0)]) != run, "with no steading it is trimmed"
    assert _trim_to_service(run, segs, [(160.0, 0.0)], steadings=[_GARDEN]) == run


def test_steading_footprints_reads_the_built_ground_and_not_the_ground_cover() -> None:
    """The commons and the homestead groves are what the ground IS, not something built on it - a lane
    crosses them, so a tread that stops 29 ft into the commons has stopped in a field."""
    M = {
        "houses": [{"x": 0.0, "y": 0.0, "w": 46.0, "h": 28.0}],
        "byres": [{"x": 200.0, "y": 0.0, "w": 20.0, "h": 14.0}],
        "farm_sheds": [{"x": 300.0, "y": 0.0, "w": 16.0, "h": 12.0}],
        "threshing_yards": [{"poly": [[0.0, 40.0], [40.0, 40.0], [40.0, 80.0]]}],
        "gardens": [{"poly": [[0.0, 100.0], [40.0, 100.0], [40.0, 140.0]]}],
        "commons": [{"poly": [[500.0, 500.0], [900.0, 500.0], [900.0, 900.0]]}],
        "village_groves": [{"poly": [[50.0, 500.0], [90.0, 500.0], [90.0, 540.0]]}],
        "wells": [{"x": 10.0, "y": 10.0}],  # no footprint recorded: it contributes nothing rather than raising
    }
    rings = hg.ways.steading_footprints(M)
    assert len(rings) == 5, f"house, byre, shed, yard, garden - and nothing else; got {len(rings)}"
    assert hg.ways.steading_footprints({}) == []


def test_trim_to_service_counts_ARRIVING_AT_THE_BUND_as_service() -> None:
    """The spur's whole purpose is the crop, which is neither a house nor another lane - and it arrives ON the bund
    (269 B04, research/fields/290: the path "never ends in open ground short of the bund"), no longer anywhere within
    the gate's 60 ft of the field."""
    field = [(400.0, 0.0), (600.0, 0.0), (600.0, 200.0), (400.0, 200.0)]
    run = [(0.0, 100.0), (200.0, 100.0), (395.0, 100.0)]
    assert _trim_to_service(run, [], [(0.0, 100.0)], hg.ways.WorkedGround([field])) == run, "5 ft off the bund is on it"
    assert len(_trim_to_service(run, [], [(0.0, 100.0)], None)) == 2
    short = [(0.0, 100.0), (200.0, 100.0), (360.0, 100.0)]
    assert _trim_to_service(short, [], [(0.0, 100.0)], hg.ways.WorkedGround([field])) != short, "40 ft short of the bund is open ground"


# ---- the splice helpers (feature 137 T04) ---------------------------------------------------------


def test_thread_the_fabric_takes_a_detour_when_neither_the_route_nor_the_clip_clears() -> None:
    from l7r.diagram.hamletgen.ways import _homestead_polys, _thread_the_fabric

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

    from .._builders import a_plan

    s = Settlement(800, 800, seed=1)
    s.meta(name="E", scale="hamlet", ftpx=1, down_deg=90)
    run = [(100.0, 100.0), (700.0, 700.0)]
    assert _thread_the_fabric(s, a_plan(), run) == run  # nothing standing: nothing to thread
    assert _thread_the_fabric(s, a_plan(), [(1.0, 1.0)]) == [(1.0, 1.0)]  # a one-point run is not a run


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


def test_web_pieces_counts_connected_lanes_and_ignores_stubs() -> None:
    """Feature 146: `web_pieces` lifted out of `_smooth_web` so it can be asked directly. A lane of fewer
    than two points is not a piece; lanes that touch are one."""
    from l7r.diagram.hamletgen.ways import web_pieces

    touching = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[100.0, 0.0], [100.0, 100.0]]}]
    apart = [{"pts": [[0.0, 0.0], [100.0, 0.0]]}, {"pts": [[900.0, 900.0], [999.0, 900.0]]}]
    assert web_pieces(touching) == 1
    assert web_pieces(apart) == 2
    assert web_pieces([*apart, {"pts": []}, {"pts": [[5.0, 5.0]]}]) == 2, "an empty or one-point lane is no piece"


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


def test_trim_to_service_cuts_an_end_that_reaches_nothing() -> None:
    """Feature 227 D11: no pass may leave a lane's end in open ground - the bar is the gate's own
    `WAY_END_REACH_FT`, and a run whose tail runs 300 ft past the last house it serves is cut back to it."""
    from l7r.diagram.hamletgen.consts import WAY_END_REACH_FT

    run = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (500.0, 0.0)]
    houses = [(0.0, 20.0), (100.0, 20.0)]
    out = hg.ways._trim_to_service(run, [], houses)
    assert out[-1][0] <= 200.0, "the tail past the last house it serves is gone"
    assert min(math.dist(out[-1], h) for h in houses) <= WAY_END_REACH_FT


def test_trim_to_service_keeps_the_tail_that_is_a_houses_ONLY_way() -> None:
    """...but not at the price of stranding somebody. A house no other way reaches is passed as `keep`, and the
    run is then cut no further back than the point that still serves it - a dangling end is a blemish, an
    unreached farmhouse is a map that fails its own rule (cohort seed 39, when both were tightened together)."""
    from l7r.diagram.hamletgen.consts import WAY_END_REACH_FT

    run = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0), (500.0, 0.0)]
    houses = [(0.0, 20.0), (100.0, 20.0)]
    outlier = (230.0, 40.0)  # 50 ft from the run's (200, 0) vertex: inside the page's 60 ft reach of a farmhouse
    out = hg.ways._trim_to_service(run, [], houses, keep=[outlier])
    assert math.dist(out[-1], outlier) <= WAY_END_REACH_FT, "the point that serves the outlier survived the cut"
    farther = (260.0, 80.0)  # 100 ft off: past the reach, so it keeps nothing (the 100 ft WEB_REACH_FT until feature 328)
    assert math.dist(hg.ways._trim_to_service(run, [], houses, keep=[farther])[-1], farther) > WAY_END_REACH_FT


def test_a_turn_at_a_repeated_vertex_is_no_turn() -> None:
    """`_turn_deg` on a run with a zero-length leg has no heading to change, so it reads straight on (0) rather than
    dividing by nothing - once reached through the straggler footpaths' repeated junction points, dropped by feature 287."""
    from l7r.diagram.hamletgen.ways import _turn_deg

    assert _turn_deg((0.0, 0.0), (0.0, 0.0), (10.0, 0.0)) == 0.0
    assert _turn_deg((0.0, 0.0), (10.0, 0.0), (10.0, 0.0)) == 0.0
    assert _turn_deg((0.0, 0.0), (10.0, 0.0), (0.0, 0.0)) == pytest.approx(180.0), "control: a real reversal reads 180"


def test_a_lane_is_owed_to_every_farmhouse_but_one_reached_across_a_yard() -> None:
    """`lane_houses` (feature 317): the houses a pass may keep a lane for or carry one to - never a household reached across
    its neighbor's yard, whose neighbor's way is its way in."""
    from l7r.diagram.hamletgen.ways.geom import lane_houses

    M = {"houses": [{"x": 1.0, "y": 2.0}, {"x": 3.0, "y": 4.0, "reached_across": [1.0, 2.0]}]}
    assert lane_houses(M) == [(1.0, 2.0)]
    assert lane_houses({}) == []
