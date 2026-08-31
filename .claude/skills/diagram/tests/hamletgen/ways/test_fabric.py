"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import math

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.ways import _crosses_fabric, _fabric_hits, _margin_frame, _pull_back_to_service
from l7r.diagram.settlement import Settlement, seg_dist

from .._builders import a_plan
from ._builders import _hamlet_for_ways, _StubSettlement


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


def test_margin_frame_without_a_house_cloud_falls_back_to_the_along_axis() -> None:
    """`near` is the placed houses, and callers inside the engine always have them. The fallback is
    for a caller that does not - it walks the outline by the seat band's own lateral reach instead,
    which is the same test `front_row` makes."""
    plan = a_plan()
    plan.seat = hg.seat_cluster(plan)
    frame = _margin_frame(plan, 150.0)
    assert frame.arc > 0.0
    assert len(frame.pts) >= 2


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


def test_homestead_polys_carries_the_per_house_groves() -> None:
    """A yashikirin belongs to its farmstead, so a lane may no more be drawn through one than
    through the house. It was missing from the fabric list while the lanes were laid first."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["groves"] = [{"poly": [[10.0, 10.0], [40.0, 10.0], [40.0, 40.0], [10.0, 40.0]]}]
    kinds = [kind for _poly, _owner, kind in hg.ways._homestead_polys(s)]
    assert "groves" in kinds


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
