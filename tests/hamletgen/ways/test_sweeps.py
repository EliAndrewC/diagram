"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import math

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from .._builders import a_plan
from ._builders import _StubSettlement


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


def test_join_orphan_ways_on_a_map_with_one_way_has_nothing_to_join() -> None:
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)]])
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0


def test_join_orphan_ways_needs_two_ways_to_join() -> None:
    """With one way or none there is no orphan to link, and the pass says so immediately rather than
    walking an empty component search."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0
    s.M["lanes"] = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}]
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0


def test_a_lane_end_in_open_ground_is_pulled_back_to_something_or_dropped() -> None:
    """`_sweep_dangling_ends`, settlement-review feature 230 passes 10 and 11. Every pass above it rewrites ends, so a link
    laid to reach a piece another pass then drops is left stopping in open ground - which is what `lanes_reach_something`
    fails on, one map at a time. The end is walked in, 4 ft at a time, until it reaches a way, a house or the field (feature
    405 T14, D8) - never a whole segment at a time, which landed it on the vertex before, past the last point that served."""
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(
        lanes=[
            [(0.0, 0.0), (400.0, 0.0)],  # the connector, and what the others must reach
            [(100.0, 10.0), (100.0, 50.0), (100.0, 400.0)],  # its far end is 400 ft from anything: walked in to the last point that reaches
            [(300.0, 2.0), (900.0, 900.0)],  # it stands on the connector and reaches nothing else: emptied and dropped (D9)
        ],
        houses=[(60.0, 40.0)],
    )
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    assert sweeps._sweep_dangling_ends(s) == 2
    kept = [ln["pts"] for ln in s.M["lanes"]]
    assert kept[0] == [[0.0, 0.0], [400.0, 0.0]], "the connector is exempt - it leaves the map by design"
    # the far end's last serving point is 60 ft from the house at (60, 40): y = 40 + sqrt(60^2 - 40^2) = 84.7, reached 4 ft at a
    # time from 400 - so y 84.0; the pop landed it on (100, 50), 34 ft short (red at HEAD). Then on toward the house it serves
    # (405 T74), held at y 64 - one step on it would come within 60 ft of the connector, a way, and a junction end stays put
    assert kept[1] == [[100.0, 10.0], [100.0, 50.0], [100.0, 64.0]], "the end walks in to the house it serves, not a segment short"
    assert len(s.M["lanes"]) == 2, "and a lane that cannot be saved is dropped whole"


def test_a_pull_back_stops_where_another_lanes_end_rests_on_it() -> None:
    """269 E4: an unserving end is pulled back no further than the outermost junction another lane's end rests on, at
    either end of the lane - taking that stretch away left Sawada's straggler 27 ft from the web it had met. Walked in 4 ft
    at a time (feature 405 T14), an end comes within reach of the straggler's own way before it gets to the junction, so it
    stops short of it; the hold itself bites where that way does not count - it also stands on the lane's other end (D9)."""
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(
        lanes=[
            [(0.0, 0.0), (400.0, 0.0)],  # the connector
            [(100.0, 10.0), (100.0, 700.0)],  # its far end reaches nothing - but a straggler's end rests on it at y 300
            [(100.0, 300.0), (600.0, 300.0)],  # ...the straggler, which serves a house at its far end
            [(900.0, 1200.0), (900.0, 700.0), (600.0, 700.0), (600.0, 310.0)],  # its HEAD reaches nothing; a lane ends on it
            [(900.0, 800.0), (1300.0, 800.0)],  # ...there, and serves a house at its far end
        ],
        houses=[(640.0, 300.0), (1340.0, 800.0)],
    )
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    sweeps._sweep_dangling_ends(s)
    assert s.M["lanes"][1]["pts"] == [[100.0, 10.0], [100.0, 360.0]], "walked in to the straggler's reach, never past its junction"
    assert s.M["lanes"][3]["pts"][0] == [900.0, 860.0], "the head too"
    # ...and where the straggler also stands on the lane's start, its way does not serve the end (D9): the hold stops it
    u = _StubSettlement(lanes=[[(0.0, 0.0), (400.0, 0.0)], [(100.0, 2.0), (100.0, 700.0)], [(102.0, 3.0), (100.0, 300.0)]], houses=[])
    u.M["fields"] = []
    u.M.setdefault("meta", {})
    sweeps._sweep_dangling_ends(u)
    assert u.M["lanes"][1]["pts"] == [[100.0, 2.0], [100.0, 300.0]], "held at the junction, not past it"
    assert sweeps.held_at((0.0, 0.0), (10.0, 0.0), [(50.0, 0.0), (5.0, 30.0)]) is None, "nothing rests on the segment"
    # ...and a lane the hold leaves under the web minimum is still the link another lane ends on: kept, not emptied as
    # debris (Sawada's 28 ft link, which took its straggler with it when it was dropped)
    t = _StubSettlement(
        lanes=[[(0.0, 0.0), (400.0, 0.0)], [(200.0, 2.0), (200.0, 600.0)], [(202.0, 3.0), (200.0, 22.0)]],
        houses=[],
    )
    t.M["fields"] = []
    t.M.setdefault("meta", {})
    sweeps._sweep_dangling_ends(t)
    assert [ln["pts"] for ln in t.M["lanes"]][1] == [[200.0, 2.0], [200.0, 22.0]], "a 20 ft link, kept"
    assert sweeps.held_at((0.0, 0.0), (0.0, 0.0), [(0.0, 0.0)]) is None, "a segment of no length holds nothing"


def test_a_lane_whose_ends_already_reach_something_is_left_alone() -> None:
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(lanes=[[(0.0, 0.0), (400.0, 0.0)], [(100.0, 10.0), (100.0, 90.0)]], houses=[(120.0, 120.0)])
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    before = [list(ln["pts"]) for ln in s.M["lanes"]]
    assert sweeps._sweep_dangling_ends(s) == 0
    assert [ln["pts"] for ln in s.M["lanes"]] == before


def test_a_one_point_lane_record_is_not_a_lane_to_sweep() -> None:
    """`_sweep_dangling_ends` reads every record on the map, and a pass above it can leave one with a single
    point. There is no end to judge, so it is passed over rather than measured."""
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(lanes=[[(0.0, 0.0), (400.0, 0.0)], [(50.0, 50.0)]], houses=[(60.0, 40.0)])
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    assert sweeps._sweep_dangling_ends(s) == 0
    assert s.M["lanes"][1]["pts"] == [[50.0, 50.0]], "left exactly as it was found"


def test_a_lane_that_dangles_at_its_HEAD_is_pulled_back_from_that_end() -> None:
    """Both ends are judged, not just the last one: the passes above rewrite whichever end their own work
    touched, so the vertex left in open ground is as often the first as the last."""
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(
        lanes=[
            [(0.0, 0.0), (400.0, 0.0)],  # the connector, exempt
            [(100.0, -400.0), (100.0, -200.0), (100.0, -10.0)],  # its HEAD is 400 ft from anything
        ],
        houses=[(100.0, -150.0)],  # ...while its middle passes a farmhouse, which is what the head is pulled back to
    )
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    assert sweeps._sweep_dangling_ends(s) == 1
    # the head first reaches at the last point within 60 ft of the house at y -150, -208.0 walked from -400 in 4 ft steps (the
    # pop landed it on the vertex at -200), then walks on to the house it serves (405 T74): -152, the step nearest -150
    assert s.M["lanes"][1]["pts"] == [[100.0, -152.0], [100.0, -10.0]], "the head walks in to the house it serves"


def test_a_lane_a_farmhouse_needs_keeps_an_end_that_nothing_lies_near() -> None:
    """The stranding guard restores a lane whose loss would leave a farmhouse unserved, and then tries to
    carry its dangling end to the nearest house. Where there is no house within reach of that end either,
    there is nothing to carry it to - the lane stands as it was drawn rather than being pulled somewhere
    arbitrary, and the record is left untouched (feature 230 pass 11)."""
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(
        lanes=[
            [(0.0, 0.0), (400.0, 0.0)],  # the connector, 400 ft from the house below
            [(180.0, -200.0), (180.0, -600.0)],  # the only way that serves it (80 ft off, inside `_SERVE_FT`), no point within 60
        ],
        houses=[(100.0, -400.0)],  # ...and both its ends 215 ft off, past the dooryard carry's 120
    )
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    before = [list(ln["pts"]) for ln in s.M["lanes"]]
    assert sweeps._sweep_dangling_ends(s) == 0, "nothing was changed, so nothing is counted as fixed"
    assert [ln["pts"] for ln in s.M["lanes"]] == before, "the farmhouse keeps its way, ragged end and all"


def test_an_end_that_reaches_nothing_is_carried_on_to_the_dooryard_of_the_house_it_serves() -> None:
    """`_sweep_dangling_ends`' rescue arm: the lane must stay because a farmhouse would lose its way, so its end is carried
    to the house instead of left in grass - and stops AT THE DOORYARD (269 B17, research/questions/0081-village-lanes.drawing.html: a lane that serves a
    farmhouse ends at its dooryard), inside the arrival bar of the house's footprint and clear of its wall. It used to stop
    at nine tenths of the 60 ft reach of the house's center, 40 ft off the wall.

    A unit test because the pool stopped reaching it: the 227/230 merge re-packed the clusters and no shipped
    map now leaves an end between one and two reaches of its house (feature 174 - bring it up BY TESTS).
    """
    from l7r.diagram.hamletgen.consts import STEADING_ARRIVAL_FT
    from l7r.diagram.hamletgen.ways import sweeps as _sw
    from l7r.diagram.settlement import edge_dist, point_in_poly, rot_rect

    from ._builders import _StubSettlement

    # lane 0 is the connector (exempt, and far away); lane 1 runs past the one house it serves 70 ft off, no point of it
    # within the 60 ft reach (so the walk-in leaves nothing), both of its ends 99 ft off - inside twice the reach - so each
    # end is carried on to the house's dooryard.
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 100.0)], [(570.0, 570.0), (570.0, 430.0)]], houses=[(500.0, 500.0)])
    assert _sw._sweep_dangling_ends(s) == 1, "the lane was fixed rather than dropped"
    pts = s.M["lanes"][1]["pts"]
    assert len(pts) == 4, "a vertex was added at each end"
    wall = rot_rect(500.0, 500.0, 46.0, 28.0, 0.0)
    for q in (pts[0], pts[-1]):
        assert not point_in_poly(q[0], q[1], wall), "the end stops short of the wall"
        assert edge_dist(q[0], q[1], wall) <= STEADING_ARRIVAL_FT, f"an end stands {edge_dist(q[0], q[1], wall):.1f} ft off the house, not at its dooryard"
    # ...and only the end that reaches nothing is carried: a lane off the connector whose walk-in empties it (the connector its
    # own head stands on does not serve its tail, D9) is restored for the house 80 ft off it, its head left on the connector
    u = _StubSettlement(lanes=[[(0.0, 0.0), (400.0, 0.0)], [(100.0, 2.0), (100.0, 400.0)]], houses=[(180.0, 330.0)])
    assert _sw._sweep_dangling_ends(u) == 1
    kept = u.M["lanes"][1]["pts"]
    assert kept[:2] == [[100.0, 2.0], [100.0, 400.0]] and len(kept) == 3, "the head stays; the tail is carried on to the dooryard"
    assert _sw.carry_to_dooryard((0.0, 0.0), [(500.0, 500.0)], [wall], 120.0) is None, "no house within the reach: nothing to carry to"
    assert _sw.carry_to_dooryard((500.0, 590.0), [(500.0, 500.0)], [], 120.0) is None, "a house with no built ground to arrive at"
    band = [(480.0, 540.0), (520.0, 540.0), (520.0, 560.0), (480.0, 560.0)]
    assert _sw.carry_to_dooryard((500.0, 590.0), [(500.0, 500.0)], [wall], 120.0, groves=[band]) is None, "a farm's grove band is in the way (feature 291)"


def test_a_tail_run_alongside_another_way_is_cut_where_it_came_alongside() -> None:
    """Feature 261: `along_tail` finds where a lane's end starts running beside another way (within 14 ft, nearly parallel,
    30 ft or more); `cut_at_tail` ends it there, on its snap onto that way. A short approach or a crossing is no tail."""
    from l7r.diagram.hamletgen.ways.sweeps import along_tail, cut_at_tail

    way = [(0.0, 0.0), (300.0, 0.0)]
    lane = [(100.0, 200.0), (100.0, 10.0), (220.0, 10.0)]  # comes down to the way, then runs 120 ft beside it
    k = along_tail(lane, way)
    assert k is not None
    cut = cut_at_tail(lane, k, way)
    assert cut[0] == lane[0] and abs(cut[-1][1]) < 1e-9 and cut[-1][0] <= 112.0, "ends on the way where it came alongside"
    assert along_tail([(100.0, 200.0), (100.0, 10.0)], way) is None, "an approach that meets the way square is no tail"
    assert along_tail([(0.0, 50.0), (300.0, 50.0)], way) is None, "a lane 50 ft off is not alongside"
    assert along_tail(lane, [(5.0, 5.0)]) is None
    # feature 293 (Inashiro in the earlier 293 pass): a tail that runs back along a way to that way's own VERTEX is nearest
    # there to the other reach meeting at it; judged against that reach alone it was no tail, and a 95 ft retrace shipped
    bent = [(0.0, 100.0), (100.0, 0.0), (300.0, 0.0)]  # the way turns at (100, 0)
    retrace = [(300.0, 150.0), (300.0, 6.0), (100.0, 0.0)]  # comes down to it, then runs back along it to the vertex
    assert along_tail(retrace, bent) is not None
    # feature 293 on 291 (Mizuguchi's field spur): a tail that meets its way at an angle for its last few feet - inside
    # `_ALONG_FT` - and runs beside it before that is walked through the approach; a square T past it is still none
    spur = [(420.0, 100.0), (400.0, 10.0), (160.0, 10.0), (153.0, 0.0)]  # 10 ft off the way, then 12 ft at 55 degrees onto it
    assert along_tail(spur, way) is not None
    assert along_tail([(150.0, 200.0), (150.0, 0.0)], way) is None, "a square T is no tail past its approach either"


def test_brook_crossings_counts_a_polyline_over_the_drawn_course() -> None:
    from l7r.diagram.hamletgen.ways.sweeps import brook_crossings
    from l7r.diagram.settlement import Settlement

    s = Settlement(400, 400, seed=1)
    s.M["streams"] = [{"poly": [[200.0, 0.0], [200.0, 400.0]]}]
    assert brook_crossings([(100.0, 100.0), (300.0, 100.0), (100.0, 150.0)], s) == 2
    assert brook_crossings([(100.0, 100.0), (150.0, 300.0)], s) == 0


def test_join_orphan_ways_never_draws_an_over_and_back_link(monkeypatch) -> None:
    """Feature 261 refused a link that crosses the brook out and home again while another candidate would do, and drew it
    as the last resort when none would. Feature 287 (ways W06, FR-005): that fallback emitted the violation, so the link is
    refused outright and the orphan is left to the web's last pass."""
    from l7r.diagram.hamletgen.ways import sweeps

    monkeypatch.setattr(sweeps, "brook_crossings", lambda pts, s: 2)
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 200.0)], [(120.0, 0.0), (120.0, 200.0)]])
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0
    assert len(s.M["lanes"]) == 2, "no link drawn"


def test_a_doubled_tail_that_overran_the_way_ends_at_the_crossing() -> None:
    """Feature 261 (settlement-review of Sawada): a tail that crossed the way and ran on beside it is ended AT the
    crossing, not snapped back onto the way behind it - the snap drew a hook."""
    from l7r.diagram.hamletgen.ways.sweeps import along_tail, cut_at_tail

    other = [(0.0, 0.0), (200.0, 0.0)]
    lane = [(100.0, -60.0), (100.0, 6.0), (60.0, 6.0)]  # crosses at (100, 0), then runs back 40 ft beside it
    k = along_tail(lane, other)
    assert k is not None
    assert cut_at_tail(lane, k, other)[-1] == (100.0, 0.0)


def test_a_wider_lane_is_never_cut_back_along_a_narrower() -> None:
    """Feature 261 (settlement-review of Sawada): of two tails doubled into one junction the narrower is cut, so a cart
    track keeps its run and the route out does not neck to a footpath."""
    from l7r.diagram.hamletgen.ways.sweeps import _sweep_doubled_tails

    s = _StubSettlement(lanes=[[(0.0, -300.0), (0.0, 300.0)], [(-100.0, 200.0), (-6.0, 150.0), (-6.0, 60.0)], [(100.0, 200.0), (6.0, 150.0), (6.0, 60.0)]])
    s.M["lanes"][0]["connector"] = False
    s.M["lanes"][1]["w"] = 6
    s.M["lanes"][0]["w"] = 3
    s.M["lanes"][2]["w"] = 3
    wide = [list(q) for q in s.M["lanes"][1]["pts"]]
    assert _sweep_doubled_tails(s) >= 1
    assert s.M["lanes"][1]["pts"] == wide, "the 6 ft lane keeps its run"
    assert s.M["lanes"][2]["pts"] != [[100.0, 200.0], [6.0, 150.0], [6.0, 60.0]], "the 3 ft lane beside a 3 ft way is cut"


def test_a_cut_on_a_later_leg_keeps_the_vertices_before_it() -> None:
    """`cut_at_tail` on a lane whose cut sample lies on its THIRD leg: the vertices before the cut are kept, in order, and
    the one past it goes with the tail."""
    from l7r.diagram.hamletgen.ways.sweeps import cut_at_tail

    got = cut_at_tail([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (30.0, 0.0)], 5, [(0.0, 6.0), (60.0, 6.0)])
    assert got[:3] == [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)] and (30.0, 0.0) not in got


def test_a_cut_that_strands_a_lane_does_not_keep_the_network() -> None:
    """Sawada (feature 280): a doubled tail that a third lane joined is not cut back past that junction."""
    from l7r.diagram.hamletgen.ways.sweeps import cut_keeps_network

    tail = [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]
    lanes = [{"pts": [list(p) for p in tail]}, {"pts": [[150.0, 0.0], [150.0, 80.0]]}, {"pts": [[0.0, 0.0], [0.0, -90.0]]}]
    assert cut_keeps_network(lanes, 0, tail, [(0.0, 0.0), (100.0, 0.0)]) is False, "the lane joining at x=150 is stranded"
    assert cut_keeps_network(lanes, 0, tail, [(0.0, 0.0), (160.0, 0.0)]) is True, "the junction is kept"
    assert cut_keeps_network([{"pts": [list(p) for p in tail]}], 0, tail, [(0.0, 0.0), (10.0, 0.0)]) is True, "one lane is one piece"
    from l7r.diagram.hamletgen.ways.sweeps import _sweep_doubled_tails

    far = [(0.0, -300.0), (0.0, 300.0)], [(100.0, 200.0), (6.0, 150.0), (6.0, 60.0)], [(80.0, 90.0), (9.5, 90.0)], [(100.0, 200.0), (100.0, 300.0), (0.0, 300.0)]
    s = _StubSettlement(lanes=list(far))
    for ln in s.M["lanes"]:
        ln["connector"], ln["w"] = False, 3
    n = _sweep_doubled_tails(s)  # the fourth lane joins the straggler to the way, so the web is one piece
    assert n == 0
    assert s.M["lanes"][1]["pts"] == [[100.0, 200.0], [6.0, 150.0], [6.0, 60.0]], "a third lane 9.5 ft off the way keeps the tail"
    # Sawada (feature 280): the third lane's end 8 ft off the way is carried onto it, and the tail is cut
    s = _StubSettlement(lanes=[far[0], far[1], [(80.0, 90.0), (8.0, 90.0)], far[3]])
    for ln in s.M["lanes"]:
        ln["connector"], ln["w"] = False, 3
    assert _sweep_doubled_tails(s) == 1
    assert s.M["lanes"][2]["pts"][-1] == [0.0, 90.0], "the straggler meets the way"
    assert s.M["lanes"][1]["pts"] != [[100.0, 200.0], [6.0, 150.0], [6.0, 60.0]], "and the doubled tail is cut"
    # ...BUT ONLY WHERE THE OVERLAP MATRIX ADMITS THE CARRIED END (feature 287 M8, merged with feature 280's carry): a carried
    # end the matrix refuses would stay on the cut tail, stranded, so the tail is not cut and no lane is rewritten
    s = _StubSettlement(lanes=[far[0], far[1], [(80.0, 90.0), (8.0, 90.0)], far[3]])
    for ln in s.M["lanes"]:
        ln["connector"], ln["w"] = False, 3
    s.admits = lambda *a, **k: False  # type: ignore[method-assign]
    assert _sweep_doubled_tails(s) == 0
    assert s.M["lanes"][2]["pts"][-1] == [8.0, 90.0] and s.M["lanes"][1]["pts"] == [[100.0, 200.0], [6.0, 150.0], [6.0, 60.0]]


def test_an_end_walked_in_is_held_nearest_the_house_it_serves() -> None:
    """405 T74 (D52, 0246: a lane ends at the dooryard): the first point walking in that reaches stood on the far edge of the
    house's 60 ft reach; given `near`, the end walks on to the point nearest the house while it still reaches."""
    from l7r.diagram.hamletgen.ways.sweeps import _walk_in

    house = (500.0, 20.0)
    reaches = lambda q, far: math.dist(q, house) <= 60.0  # noqa: E731
    edge = [(0.0, 0.0), (1000.0, 0.0)]
    _walk_in(edge, reaches, [])
    assert 550.0 <= edge[-1][0] <= 560.0, "without `near`: the zone's far edge"
    held = [(0.0, 0.0), (1000.0, 0.0)]
    _walk_in(held, reaches, [], lambda q, far: math.dist(q, house))
    assert 496.0 <= held[-1][0] <= 504.0, "with it: beside the house"


def test_an_end_at_a_junction_is_not_walked_off_it() -> None:
    """Batch 6's round 4 (405 T74): an end within reach of a way scores `near` infinite; a step just past that reach scored
    lower and the walk carried the end off its junction toward a house. It stays."""
    from l7r.diagram.hamletgen.ways.sweeps import _walk_in

    way_y, house = 0.0, (100.0, 300.0)
    reaches = lambda q, far: True  # noqa: E731 - it reaches (the way) wherever it stands
    near = lambda q, far: float("inf") if abs(q[1] - way_y) <= 60.0 else math.dist(q, house)  # noqa: E731
    pts = [(100.0, 400.0), (100.0, 58.0)]
    _walk_in(pts, reaches, [], near)
    assert pts[-1] == (100.0, 58.0), "held at its junction"


def test_a_link_off_a_way_walks_on_to_its_house() -> None:
    """405 T82 (D58): the way a lane's far end stands on is no other way (as `_reaches`), so `_near` does not hold a short link
    off a way 60 ft past the house it serves; a way it did not leave still holds it."""
    from l7r.diagram.hamletgen.ways import sweeps

    s = _StubSettlement(lanes=[[(0.0, 0.0), (400.0, 0.0)], [(100.0, 0.0), (100.0, 150.0)]], houses=[(130.0, 40.0)])
    s.M["fields"] = []
    s.M.setdefault("meta", {})
    sweeps._sweep_dangling_ends(s)
    end = s.M["lanes"][1]["pts"][-1]
    assert end[1] <= 44.0, "walked on to its closest approach to the house (y 40), not held at the 60 ft edge of the way it left"


def test_the_sweep_reads_a_farm_band_rotated_as_the_door_path_does() -> None:
    """405 T83: the sweep built each band's box unrotated while `lay_door_paths` reads it at its `rot`, so the two disagreed on
    where a turned farm's wood stood. A band 40 by 10 turned 90 degrees stands 10 wide and 40 deep; a copse with no width is
    no farm's band."""
    import pytest

    from l7r.diagram.hamletgen.ways import sweeps as _sw

    (band,) = _sw.farm_bands({"groves": [{"x": 100.0, "y": 100.0, "w": 40.0, "h": 10.0, "rot": 90.0}, {"x": 0.0, "y": 0.0}]})
    xs, ys = [p[0] for p in band], [p[1] for p in band]
    assert max(xs) - min(xs) == pytest.approx(10.0) and max(ys) - min(ys) == pytest.approx(40.0)
    # ...and a farm's share of the dooryard copse is its wood too (0036: one wood), a windbreak's clumps are not
    M = {"village_groves": [{"role": "copse", "r": 10.0, "clumps": [[50.0, 50.0]]}, {"role": "windbreak", "r": 10.0, "clumps": [[0.0, 0.0]]}]}
    (clump,) = _sw.farm_bands(M)
    assert max(math.dist(p, (50.0, 50.0)) for p in clump) == pytest.approx(10.0)
