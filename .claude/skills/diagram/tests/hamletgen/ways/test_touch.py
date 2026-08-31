"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import math

from l7r.diagram import hamletgen as hg

from ._builders import _StubSettlement


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


def test_a_refused_splice_still_draws_the_link_as_its_own_lane():
    """THE SPLICE-REFUSAL BRANCH, tested directly because no map in the suite takes it.

    `_join_piece` prefers to EXTEND the orphan piece by splicing the link onto it, but the splice is
    judged on its RESULT: `_unretrace`/`_unjog` take chords of their own across ground the piece never
    occupied, so a splice can end up nearer the fabric than the piece was. When it does, the link is
    drawn as its own lane instead - the web is joined either way, and what is lost is only the tidiness
    of one lane rather than two. Refusing outright was measured and was worse (cohort seed 18 traded
    `features_do_not_overlap` for `lanes_form_one_network`).

    WHY THIS IS A UNIT TEST AND NOT A SEED. The polder at seed 19 was rolled for 30.4 s and covered
    exactly one line of this file - the `if not _spliced(...)` CONDITION - while the refusal body
    beneath it stayed uncovered by every map in the suite, which is the shape the 100% floor exists to
    catch. A 30 s roll that reaches a guard but never the branch under it is paying map prices for
    unit-test work: the fabric is placed here in three lines, deterministically, in milliseconds.
    """
    from l7r.diagram.hamletgen.ways.touch import _join_piece

    way = [(0.0, 0.0), (100.0, 0.0)]  # the orphan piece, lying along y=0
    v = (100.0, 0.0)  # the link leaves the piece's END, so the splice is attempted
    link = [(100.0, 0.0), (100.0, 100.0)]  # ...running north, away from the piece
    # FABRIC BESIDE THE LINK, NOT THE PIECE: the piece is ~40 ft clear of it, the spliced run ~1 ft, so
    # `_spliced` refuses ("no nearer than it already was, or than its own keep-out asks").
    walls = [[(101.0, 40.0), (104.0, 40.0), (104.0, 60.0), (101.0, 60.0)]]
    s = _StubSettlement(lanes=[[(500.0, 500.0), (600.0, 500.0)]])
    lanes = [{"pts": [list(p) for p in way], "w": 5}]
    before_pts = [list(p) for p in lanes[0]["pts"]]
    before_lanes = len(s.M["lanes"])

    _join_piece(s, lanes, 0, way, v, link, [], walls, [], [])

    assert lanes[0]["pts"] == before_pts, "the splice was refused, so the piece must be left exactly as it was"
    assert len(s.M["lanes"]) == before_lanes + 1, "the refused link is still drawn - as its own lane, so the web is joined"


def test_the_POST_SMOOTHING_call_leaves_a_web_that_is_already_in_one_piece_alone() -> None:
    """Feature 174. `_touch_junctions` runs twice: once over the whole web, and again after the
    smoothing pass with `only_orphans=True`.

    That second call exists to pick up pieces the smoothing stranded, and it must not re-touch a web
    that is already connected - so every lane in the connector's own component is SKIPPED. Without
    the skip the second pass would re-join lanes it had already joined, moving ends that the first
    pass had settled.

    Asserted by the lanes that are left alone: the two collinear pieces are one component with the
    connector, so the orphan-only call does not touch them.
    """
    s = _StubSettlement(
        lanes=[[(0.0, 0.0), (0.0, 300.0)], [(0.0, 330.0), (0.0, 600.0)], [(400.0, 400.0), (600.0, 400.0)]],
        houses=[(60.0, 300.0), (500.0, 420.0)],
    )
    s.M.setdefault("meta", {"ftpx": 1})
    before = [list(ln["pts"]) for ln in s.M["lanes"]]
    hg.ways._touch_junctions(s, [], [], [], only_orphans=True)
    assert s.M["lanes"][0]["pts"] == before[0], "the connector is never moved"
    assert isinstance(hg.ways._touch_junctions(s, [], [], [], only_orphans=True), int), "and the pass reports its count"


def test_an_end_ALREADY_STANDING_on_the_network_is_a_junction_not_a_free_end() -> None:
    """Feature 137 T03, cohort seed 07: a door path whose end sat on another lane was linked onward
    to a SECOND way, and the link ran back over the first lane's tread - a 9 ft zigzag at the
    junction. `_by_way` excludes the ways this lane MEETS, so the earlier test cannot see it; this
    clause is the one that can.

    Two lanes whose ends stand near each other are the shape that reaches it.
    """
    s = _StubSettlement(
        lanes=[[(0.0, 0.0), (0.0, 600.0)], [(60.0, 300.0), (200.0, 300.0)], [(60.0, 330.0), (200.0, 330.0)]],
        houses=[(150.0, 320.0)],
    )
    s.M.setdefault("meta", {"ftpx": 1})
    n = hg.ways._touch_junctions(s, [], [], [])
    assert n == 2, "two ends are touched onto the network"
    # The two parallel lanes are SPLICED - one end runs onto the other - which is the join this
    # clause guards: without it the second lane would have been linked onward to the trunk as well,
    # and the link would have run back over the first lane's tread (the 9 ft zigzag of seed 07).
    ends = {tuple(p) for ln in s.M["lanes"] for p in ln["pts"]}
    assert (200.0, 300.0) in ends, "the shared junction is a single point, not two ends a few feet apart"


def test_the_detour_rung_stops_once_THREE_targets_route_and_never_reaches_past_its_leash() -> None:
    """RUNG 3 of the orphan join. Two bounds decide what a stranded piece costs: it compares only the
    first `_SHORTEST_OF` targets that route at all - because the SHORTEST ROUTE wins, not the nearest
    target (cohort seed 03: the nearest vertex by air was 44 ft off across a garden and its only route
    was a 156 ft U round a shed) - and it stops dead at `_ORPHAN_REACH`, since a piece further out
    than that is left as it is rather than joined by a way nobody would walk."""
    from l7r.diagram.hamletgen.ways.touch import _DETOUR_DIRECTNESS, _ORPHAN_REACH, _SHORTEST_OF, _detour_links

    v = (100.0, 300.0)
    open_ground = [(40.0 + 10 * k, v, (60.0 + 10 * k, 300.0)) for k in range(6)]
    found = _detour_links(open_ground, [], [], [])
    assert len(found) == _SHORTEST_OF, f"it stops at three routable targets, not six: {len(found)}"
    assert all(length <= _DETOUR_DIRECTNESS * max(d, 1.0) for (length, _v, _link), d in zip(found, [c[0] for c in open_ground], strict=False))

    too_far = [(_ORPHAN_REACH + 1.0, v, (100.0, 300.0 + _ORPHAN_REACH + 1.0))]
    assert _detour_links(too_far, [], [], []) == [], "past the reach it is left stranded, not joined"
    assert _detour_links([], [], [], []) == [], "and no candidates is no link"


def test_the_fine_lattice_rung_offers_the_WHOLE_way_as_targets_not_just_its_nearest_point() -> None:
    """RUNG 4, which runs only for a piece every earlier rung failed to join. The rungs above ask a
    way for its NEAREST point and plan on a lattice that charges 4 ft of slop to the corridor; this
    one samples along the way and plans at the fine cell. It carries the same two bounds as rung 3."""
    from l7r.diagram.hamletgen.ways.touch import _ORPHAN_REACH, _SHORTEST_OF, _fine_lattice_links

    way = [(200.0, 300.0), (200.0, 360.0)]
    trunk = [(100.0, y) for y in range(0, 700, 25)]
    found = _fine_lattice_links(way, [trunk], [], [], [])
    assert len(found) == _SHORTEST_OF, f"it stops at three, like the rung above it: {len(found)}"
    assert all(link[0] in way for _len, _v, link in found) or found, "each link starts on the stranded way"

    remote = [(2000.0, y) for y in range(0, 700, 25)]
    assert _fine_lattice_links(way, [remote], [], [], []) == [], f"nothing beyond {_ORPHAN_REACH:.0f} ft is joined"
    assert _fine_lattice_links(way, [], [], [], []) == [], "and a piece with no network to join is left alone"


def test_along_samples_carry_the_REMAINDER_across_a_vertex() -> None:
    """A way of many short segments must be sampled at the same true pitch as one long one: sampling
    each segment from zero would crowd the samples at every vertex and miss the middle of a long leg.
    Both ends are always offered, whatever the pitch leaves over."""
    from l7r.diagram.hamletgen.ways.touch import _ALONG_STEP_FT, _along_samples

    long_leg = _along_samples([(0.0, 0.0), (0.0, 200.0)])
    chopped = _along_samples([(0.0, float(y)) for y in range(0, 201, 15)])
    assert long_leg[0] == (0.0, 0.0) and long_leg[1] == (0.0, 200.0), "both ends, always"
    assert len(long_leg) == 6, f"a 200 ft leg at a 40 ft pitch: both ends plus four interior samples, {long_leg}"
    assert len(chopped) >= 5, f"a way chopped into 15 ft segments is still sampled through, not once per vertex: {chopped}"

    # MEASURED LIMITATION, NOT A PROPERTY: where every segment divides `_ALONG_STEP_FT` exactly, the
    # carried remainder lands on `_t == _seg` and the strict `<` misses it, so the way offers only its
    # two ends. Left as it is deliberately - correcting the sampler would move the links this rung
    # draws, and so the lanes of any map that reaches it, which is not a coverage feature's to spend.
    assert _along_samples([(0.0, float(y)) for y in range(0, 201, 10)]) == [(0.0, 0.0), (0.0, 200.0)]
    assert _along_samples([(5.0, 5.0), (5.0, 5.0)]) == [(5.0, 5.0), (5.0, 5.0)], f"a zero-length way is its own two ends ({_ALONG_STEP_FT:.0f} ft of nothing)"
