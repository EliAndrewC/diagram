"""`hamletgen/ways/knots.py`: lane ends that nearly meet are joined (research/questions/0081-village-lanes.drawing.html, "Ends
within 25 ft of one another are joined at a single point") - the knot found on plain lanes and gathered by the settle's step
(feature 328 wave 4, glyph-check of Inashiro)."""

import math

from l7r.diagram.hamletgen.ways import knots as kn
from l7r.diagram.hamletgen.ways.smooth import _KNOT_FT

from ._settle_builders import _S, CONN


def _ln(*pts, **kw):
    return {"pts": [list(q) for q in pts], "w": 3, **kw}


def test_ends_within_the_joint_tolerance_are_one_node_standing_at_a_fixed_end() -> None:
    lanes = [_ln((0.0, 0.0), (100.0, 0.0)), _ln((100.4, 0.0), (100.0, 80.0), connector=True), _ln((5.0, 5.0))]
    nodes = kn.end_nodes(lanes)
    at = [q for q, ends in nodes if (0, -1) in ends]
    assert at == [(100.4, 0.0)], "the connector's end is the node's point"
    assert len(nodes) == 3, "a one-point lane has no ends"


def test_a_knot_is_two_nodes_within_the_reach_no_one_lane_runs_between() -> None:
    lanes = [
        _ln((0.0, 0.0), (-500.0, 0.0), connector=True),
        _ln((10.0, 100.0), (10.0, 0.0)),  # a T on the connector 10 ft from its head
        _ln((0.0, -15.0), (0.0, 0.0)),  # a 15 ft lane from the head: its own two ends are its join
        _ln((300.0, 100.0), (300.0, 0.0)),  # far off
    ]
    got = kn.knots(lanes)
    pairs = [{q for q in (kn.end_nodes(lanes)[a][0], kn.end_nodes(lanes)[b][0])} for a, b, _d in got]
    assert {(10.0, 0.0), (0.0, 0.0)} in pairs
    assert {(0.0, -15.0), (0.0, 0.0)} not in pairs, "spanned by one lane"
    assert all(d <= _KNOT_FT for _a, _b, d in got) and [d for *_x, d in got] == sorted(d for *_x, d in got)


def test_an_end_is_moved_onto_the_node_with_its_corner_in_the_knot_taken_out_as_a_second_form() -> None:
    p = [(0.0, 100.0), (0.0, 10.0), (3.0, 0.0)]
    first, second = kn.moved_onto(p, -1, (20.0, 0.0))
    assert first == [(0.0, 100.0), (0.0, 10.0), (20.0, 0.0)] and second == [(0.0, 100.0), (20.0, 0.0)]
    assert kn.moved_onto(p[::-1], 0, (20.0, 0.0))[0] == [(20.0, 0.0), (0.0, 10.0), (0.0, 100.0)], "the start end"
    assert kn.moved_onto([(0.0, 100.0), (20.0, 0.0), (3.0, 0.0)], -1, (20.0, 0.0)) == [[(0.0, 100.0), (20.0, 0.0)]], "no point repeated, no form twice"


def test_the_smaller_node_moves_a_fixed_end_never_and_a_refusal_turns_it_round() -> None:
    lanes = [_ln((0.0, 0.0), (-500.0, 0.0), connector=True), _ln((60.0, 100.0), (10.0, 0.0))]
    assert kn.next_gather(lanes, lambda edits: True) == {1: [(60.0, 100.0), (0.0, 0.0)]}, "onto the connector's head"
    assert kn.next_gather(lanes, lambda edits: False) is None, "never the connector onto the lane"
    two = [_ln((0.0, 100.0), (0.0, 0.0)), _ln((0.0, 0.0), (0.0, -100.0)), _ln((60.0, 100.0), (10.0, 0.0))]
    asked: list[dict] = []
    assert kn.next_gather(two, lambda e: asked.append(e) or 2 not in e) == {0: [(0.0, 100.0), (10.0, 0.0)], 1: [(10.0, 0.0), (0.0, -100.0)]}
    assert 2 in asked[0], "the one-end node asked first"
    loop = [_ln((0.0, 0.0), (50.0, 50.0), (0.5, 0.0)), _ln((60.0, 100.0), (10.0, 0.0))]
    assert kn.next_gather(loop, lambda e: 0 not in e) == {1: [(60.0, 100.0), (0.0, 0.0)]}, "a loop's node is not moved, only gathered onto"


def test_the_settle_gathers_two_lanes_tied_onto_the_connector_a_few_feet_apart() -> None:
    """Inashiro's knot in small: two lanes meet the connector 6 ft apart, each from its own farmhouse - one point after."""
    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])
    assert kn.knots(s.M["lanes"])
    assert kn.settle_knots(s) == 1
    assert kn.knots(s.M["lanes"]) == []
    assert s.M["lanes"][0]["pts"] == [[0.0, 0.0], [-1000.0, 0.0]], "the connector is not moved"
    assert math.dist(s.M["lanes"][1]["pts"][-1], s.M["lanes"][2]["pts"][-1]) < 1e-6


def test_a_gather_the_matrix_refuses_is_left_and_not_asked_again() -> None:
    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])
    s.reshape_lane = lambda ln, pts: False
    assert kn.settle_knots(s) == 0
    assert kn.knots(s.M["lanes"]), "left as it was"


def test_a_gather_that_would_split_the_web_is_refused() -> None:
    """A lane that joins its farmhouse to the connector is not carried off onto an island's end beside it: the island's two
    ends make the bigger node, so the lane's end is asked to move first - and refused, the house left unreached otherwise."""
    lane = [(-100.0, 150.0), (-100.0, 0.0)]
    island = [[(-60.0, 200.0), (-88.0, 15.0)], [(-30.0, 100.0), (-88.0, 15.0)]]  # off the connector, east of the lane
    s = _S([CONN, lane, *island], houses=[(-100.0, 180.0)])
    kn.settle_knots(s)
    assert s.M["lanes"][1]["pts"][-1] == [-100.0, 0.0], "still on the connector"


def test_a_gather_that_closes_a_needle_loop_is_refused(monkeypatch) -> None:
    """A gather that closes a sliver the lane law refuses (`law.needle_loops`) is not made (feature 328 wave 4: the
    20-household seed 4 of the reference spec was refused `needle_loops` with the gather in) - Inashiro's knot in small, its
    two ends gathered closing a loop."""
    from l7r.diagram.hamletgen.ways import tree_base

    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])

    def loops(self, lanes, changed):  # the trial's needle count (feature 387: the faces an edit meets, `tree_base.Faces`)
        return 1 if math.dist(lanes[1]["pts"][-1], lanes[2]["pts"][-1]) < 1e-6 else 0

    monkeypatch.setattr(tree_base.Faces, "needles_with", loops)
    assert kn.settle_knots(s) == 0
    assert kn.knots(s.M["lanes"]), "left as it was"


def test_a_households_foot_may_move_its_door_end_never() -> None:
    assert kn._fixed({"connector": True}, -1) and kn._fixed({"street": True}, 0)
    assert kn._fixed({"role": "access", "of": [0.0, 0.0]}, 0), "where it leaves its dooryard"
    assert not kn._fixed({"role": "access", "of": [0.0, 0.0]}, -1), "its foot on the tree"
    assert kn._fixed({"role": "field way"}, -1) and kn._fixed({"role": "way target"}, 0) and not kn._fixed({}, 0)


def test_two_junctions_on_one_lane_within_the_reach_are_a_knot() -> None:
    """Two T's on one lane within the page's 25 ft reach are a knot; past it they are two T's - `KNOT_MARGIN` is the page's
    own reach (feature 328: a 1.5 margin went past the page)."""
    lanes = [_ln((0.0, 0.0), (-500.0, 0.0), connector=True), _ln((-100.0, 200.0), (-100.0, 0.0)), _ln((-200.0, 200.0), (-120.0, 0.0))]
    assert [round(d) for _a, _b, d in kn.knots(lanes)] == [20], "two T's on the connector 20 ft apart"
    assert kn.knots([lanes[0], lanes[1], _ln((-200.0, 200.0), (-130.0, 0.0))]) == [], "30 ft apart: two T's"


def test_a_knots_corner_is_taken_out_of_the_lane_joining_its_two_junctions() -> None:
    """A way's foot on another's last corner, 21 ft from where that one meets the connector (Inashiro's lanes 11 and 13): the
    corner is taken out of the joining lane, and a T on the stretch it no longer runs along is carried onto it."""
    x = _ln((-300.0, 100.0), (-115.0, 15.0), (-100.0, 0.0))
    w = _ln((-207.5, 157.5), (-207.5, 57.5))  # its foot on x's long leg
    lanes = [_ln((0.0, 0.0), (-500.0, 0.0), connector=True), x, _ln((-150.0, 200.0), (-115.0, 15.0)), w]
    got = kn.contracted(lanes, (-115.0, 15.0), (-100.0, 0.0), {2})
    assert got[1] == [(-300.0, 100.0), (-100.0, 0.0)]
    foot = got[3][-1]
    assert abs((foot[1] - 0.0) * 200.0 + (foot[0] + 100.0) * 100.0) < 1e-6, "carried onto the new leg"
    assert kn.contracted(lanes, (-115.0, 15.0), (-100.0, 0.0), {1, 2}) == {}, "skipped"
    assert kn.carried(lanes, [(-300.0, 100.0), (-100.0, 0.0)], [(-300.0, 100.0), (-100.0, 0.0)], set()) == {}, "nothing left the line"
    edits = kn.next_gather(lanes, lambda e: 1 in e)
    assert edits is not None and edits[2][-1] == (-100.0, 0.0) and edits[1] == [(-300.0, 100.0), (-100.0, 0.0)], "gathered with the corner out"


def test_a_households_gathered_foot_is_written_into_its_corridor() -> None:
    """The settle draws a household's way from its reserved corridor every round (`tree.settle_tree`), so a gathered foot is
    written there too (`tree.set_corridor`) or the next round undoes it."""
    from l7r.diagram.hamletgen.ways.tree import set_corridor

    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])
    s.M["lanes"][1].update(role="access", of=[-100.0, 180.0])
    s.M["lanes"][2].update(role="access", of=[-106.0, -180.0])
    s.M["access_corridors"] = [
        {"pts": [[-100.0, 150.0], [-100.0, 0.0]], "of": [-100.0, 180.0]},
        {"pts": [[-106.0, -150.0], [-106.0, -50.0]], "of": [-106.0, -180.0]},
        {"pts": [[-106.0, -50.0], [-106.0, 0.0]]},
    ]
    assert kn.settle_knots(s) == 1
    moved = next(ln for ln in s.M["lanes"][1:] if ln["pts"][-1] != [-106.0, 0.0] or ln["of"] == [-106.0, -180.0])
    legs = [c for c in s.M["access_corridors"]]
    assert [q for c in legs for q in c["pts"]].count(moved["pts"][-1]) >= 1 and math.dist(s.M["lanes"][1]["pts"][-1], s.M["lanes"][2]["pts"][-1]) < 1e-6
    assert sum(1 for c in legs if c.get("of")) == 2, "each household's record keeps its house"
    assert not set_corridor(s.M, {"pts": [[0.0, 0.0], [1.0, 0.0]]}) and not set_corridor(s.M, {"role": "access", "of": [5.0, 5.0], "pts": [[0.0, 0.0], [1.0, 0.0]]})
    assert not set_corridor(s.M, {"role": "access", "of": [-100.0, 180.0], "pts": [[0.0, 0.0]]}), "a lane of one point"


# ---- the perf-audit of feature 328 wave 4: a trial's whole-web questions asked pair by pair, the answers kept ----------


def _web(*lanes, houses=((-100.0, 180.0), (3000.0, 3000.0))):
    return {"lanes": [dict(ln) for ln in lanes], "houses": [{"x": x, "y": y, "w": 40.0, "h": 28.0, "rot": 0.0} for x, y in houses], "meta": {"generated_by": "test", "ftpx": 1.0}}


_LANES = (
    _ln((0.0, 0.0), (-1000.0, 0.0), connector=True),
    _ln((-100.0, 150.0), (-100.0, 0.0)),  # a T on the connector
    _ln((-300.0, 100.0), (-300.0, 8.0), (-450.0, 8.0)),  # its end run on beside the connector: a doubled tail, a shadow
    _ln((-120.0, 150.0), (-120.0, 30.0)),  # beside lane 1 its whole length, joined to nothing
    _ln((2000.0, 2000.0), (2100.0, 2000.0)),  # an island far off
    _ln((5.0, 5.0)),  # a lane of one point
)


def _asked_whole(M):
    from l7r.diagram.hamletgen.ways import law
    from l7r.diagram.hamletgen.ways.checks import unreached_houses
    from l7r.diagram.hamletgen.ways.serve import shadowed_by
    from l7r.diagram.hamletgen.ways.settle import connector_component

    ways = [kn._pts(ln) for ln in M["lanes"]]
    shadows = [i for i, ln in enumerate(M["lanes"]) if not ln.get("connector") and len(ways[i]) >= 2 and shadowed_by(ways, i) is not None]
    rules = {
        "needle_loops": len(law.needle_loops(M)),
        "doorstep_ends": len(law.doorstep_ends(M)),
        "doubled_tails": len(law.doubled_tails(M)),
        "way_outs": len(law.way_outs_crossing(M)),
        "shadows": len(shadows),
    }
    return (law.lane_networks(M), connector_component(M["lanes"]), len(unreached_houses(M))), rules


def _asked_pairwise(memo, M):
    ways = [kn._pts(ln) for ln in M["lanes"]]
    ids = memo.ids(ways)
    return memo.web(M, ways, ids), {name: memo.count(name, M, ways, ids) for name in kn._WHOLE_RULES}


def test_the_web_asked_pair_by_pair_answers_as_the_whole_web_does() -> None:
    """`WebMemo`: the networks, the connector's component, the unreached farmhouses and every whole-web rule's count are the
    whole web's own answers - on the web, on it with a lane moved (the kept pairs reused), with no connector (the longest
    lane the served network's seed), with a connector of one point (no network served) and with no lanes at all."""
    memo = kn.WebMemo()
    M = _web(*_LANES)
    web, rules = _asked_whole(M)
    assert web == (4, {0, 1}, 1) and rules["doubled_tails"] >= 1 and rules["shadows"] >= 1, f"non-vacuous: lanes apart, an unreached house, a tail, a shadow: {web} {rules}"
    assert _asked_pairwise(memo, M) == (web, rules)
    kept = len(memo._pairs)
    moved = _web(*_LANES[:3], _ln((-120.0, 150.0), (-120.0, 0.0)), *_LANES[4:])  # lane 3 now meets the connector
    assert _asked_pairwise(memo, moved) == _asked_whole(moved)
    assert len(memo._pairs) < 2 * kept, "only the moved lane's pairs asked again"
    for M2 in (
        _web(*(dict(ln, connector=False) for ln in _LANES)),
        _web(_ln((0.0, 0.0), connector=True), *_LANES[1:]),
        _web(),
    ):
        assert _asked_pairwise(kn.WebMemo(), M2) == _asked_whole(M2)


def test_a_ways_box_is_its_points_and_none_for_no_points() -> None:
    memo = kn.WebMemo()
    a, b = memo.ids([[(0.0, 0.0), (10.0, 5.0)], []])
    assert memo._boxes[a] == (0.0, 0.0, 10.0, 5.0) and memo._apart(a, b, 1e9), "no points: apart from everything"
    assert memo.ids([[(0.0, 0.0), (10.0, 5.0)]]) == [a], "one number per run of points"


def test_an_end_is_teed_onto_the_other_lane_from_the_vertex_before_it() -> None:
    """`teed_onto`: the end re-aimed from the vertex before it at the nearest point of the other lane, either end; nothing where
    the other lane is a point or the vertex already stands on it."""
    other = [(-50.0, 0.0), (50.0, 0.0)]
    assert kn.teed_onto([(0.0, 100.0), (0.0, 10.0)], -1, other) == [[(0.0, 100.0), (0.0, 0.0)]]
    assert kn.teed_onto([(0.0, 10.0), (0.0, 100.0)], 0, other) == [[(0.0, 0.0), (0.0, 100.0)]]
    assert kn.teed_onto([(0.0, 100.0), (0.0, 10.0)], -1, [(0.0, 0.0)]) == []
    assert kn.teed_onto([(0.0, 0.0), (5.0, 9.0)], -1, other) == []


def test_a_knot_neither_node_can_move_onto_is_teed_onto_the_other_lane() -> None:
    """Feature 328 wave 28 (Kuwabata): two lanes converging at a sharp angle - the end onto the connector's head refused, the
    connector never moved - the lone movable end is teed onto the connector's side."""
    lanes = [_ln((0.0, 0.0), (100.0, 0.0), connector=True), _ln((40.0, 60.0), (10.0, 10.0))]
    tee = {1: [(40.0, 60.0), (40.0, 0.0)]}
    assert kn.next_gather(lanes, lambda e: e == tee) == tee


def test_a_lone_end_beside_a_way_is_teed_from_an_earlier_vertex_clear_of_the_knot() -> None:
    """405 T134 (D125), fresh cohort seed 717220 with T26's sheds: a way ran 20 ft beside another and teed onto it 24 ft from
    that way's end - its tee from the vertex before its end is where it already stands. It is teed from an earlier vertex,
    the legs beside the way dropped, its tee past the knot's reach; never a form the judge refuses or one that adds a knot."""
    lanes = [_ln((0.0, 0.0), (0.0, -500.0), connector=True), _ln((80.0, 0.0), (0.0, 0.0)), _ln((150.0, 30.0), (60.0, 20.0), (24.0, 20.0), (24.0, 0.0))]
    assert kn.knots(lanes) == [(0, 4, 24.0)]
    tee = {2: [(150.0, 30.0), (60.0, 20.0), (60.0, 0.0)]}
    assert kn.next_gather(lanes, lambda e: e == tee) == tee
    assert kn.next_gather(lanes, lambda e: False) is None


def test_an_end_is_teed_back_from_each_earlier_vertex_never_longer() -> None:
    """`teed_back`: each earlier vertex nearest the end first, either end, every form shorter than the lane it replaces."""
    way = [(80.0, 0.0), (0.0, 0.0)]
    run = [(150.0, 30.0), (60.0, 20.0), (24.0, 20.0), (24.0, 0.0)]
    assert kn.teed_back(run, -1, way) == [[(150.0, 30.0), (60.0, 20.0), (60.0, 0.0)], [(150.0, 30.0), (80.0, 0.0)]]
    assert kn.teed_back(run[::-1], 0, way) == [[(60.0, 0.0), (60.0, 20.0), (150.0, 30.0)], [(80.0, 0.0), (150.0, 30.0)]]
    assert kn.teed_back([(0.0, 0.0), (10.0, 30.0), (0.0, 20.0)], -1, [(-5.0, 0.0), (5.0, 0.0)]) == [], "a vertex already on the way is no tee"


def test_two_ends_a_house_parts_are_no_knot() -> None:
    """Feature 385 T01 (plan D4b): ends within the knot reach with a building between them are two paths either side of it,
    not a knot - on the manifest's ground; with no manifest the rule reads as before (cohort seed 24 under the wave 155
    re-deal suggested it, but proved a staggered junction with clear ground between its ends)."""
    lanes = [_ln((0.0, -100.0), (0.0, 0.0)), _ln((0.0, 24.0), (0.0, 124.0))]
    open_M = {"lanes": lanes, "houses": [], "meta": {"ftpx": 1.0}}
    parted_M = {**open_M, "houses": [{"x": 0.0, "y": 12.0, "w": 40.0, "h": 8.0, "rot": 0.0}]}
    assert kn.lane_knots(lanes) and kn.lane_knots(lanes, open_M), "on open ground the two ends are a knot"
    assert kn.lane_knots(lanes, parted_M) == [], "a house between them parts them"
    apart = kn.ground_apart(parted_M)
    assert apart((0.0, 0.0), (0.0, 24.0)) and not kn.ground_apart(open_M)((0.0, 0.0), (0.0, 24.0))
    assert kn.knots(lanes) and kn.knots(lanes, apart) == []


def test_a_manifests_view_reads_its_own_scale() -> None:
    """`ground_apart` on a manifest alone reads a well's verge at the map's scale (`_View.px`, from `meta.ftpx`)."""
    from l7r.diagram.hamletgen.ways import forced

    assert forced._View({"meta": {"ftpx": 2.0}}).px(10.0) == 5.0 and forced._View({}).px(10.0) == 10.0


def test_a_knot_the_fence_gap_leaves_is_gathered_at_the_crop_clearance(monkeypatch) -> None:  # noqa: ANN001
    """405 T107 (D83): the gather asks every knot first at the fence gap (0246's 7 ft, a convention), and only the knots it
    leaves again at 0081's crop clearance (3 ft) - a gather at 3 ft on every knot reshaped seed 7's web into a new knot."""
    from l7r.diagram.hamletgen.consts import WEB_CROP_GAP, WEB_FABRIC_GAP
    from l7r.diagram.hamletgen.ways.settle import lawful

    asked: list[float] = []

    def fault(self, run, width, skip=None):  # noqa: ANN001, ANN202 - the fence a join passes, refused at the convention's gap
        asked.append(self.fence_gap)
        return "fabric" if self.fence_gap > WEB_CROP_GAP else None

    monkeypatch.setattr(lawful.Lawful, "fault", fault)
    s = _S([CONN, [(-100.0, 150.0), (-100.0, 0.0)], [(-106.0, -150.0), (-106.0, 0.0)]], houses=[(-100.0, 180.0), (-106.0, -180.0)])
    assert kn.settle_knots(s) == 1
    assert kn.knots(s.M["lanes"]) == []
    assert asked[0] == WEB_FABRIC_GAP and asked[-1] == WEB_CROP_GAP, "the convention first, the crop clearance after"
