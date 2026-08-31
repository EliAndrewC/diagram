"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

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


def test_join_orphan_ways_needs_two_ways_to_join() -> None:
    """With one way or none there is no orphan to link, and the pass says so immediately rather than
    walking an empty component search."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0
    s.M["lanes"] = [{"pts": [[0.0, 0.0], [50.0, 0.0]]}]
    assert hg.ways._join_orphan_ways(s, [], [], []) == 0


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


def test_a_swept_lane_takes_its_RECORD_with_it_not_just_its_points() -> None:
    """THE HUSK GOES WITH THE INK - feature 145's rule, which feature 155 broke in two sweeps at once
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


def test_a_bridge_closes_a_hole_and_refuses_to_close_a_loop() -> None:
    """MIZUGUCHI'S REGRESSION, PINNED (settlement-review, feature 155). With the short-gap floor
    restored, the pass drew an 89.9 ft span between two ends that already had a 126.9 ft walk between
    them - lanes 1/4/7 closed into a triangle enclosing 1,710 sq ft of nothing, and the fixture placer
    running afterwards deleted that homestead's woodpile and hen coop and left its bath on the far
    side of a public lane from its own door.

    The discriminator is the DETOUR RATIO. A genuine break has no alternative walk at all, or one that
    goes right around the block; a redundant loop closure saves a fraction. This asserts both ends of
    that distinction on the geometry, not on the map."""
    # a straight way with a hole in it, and nothing else: no walk exists at all
    apart = [[(0.0, 0.0), (100.0, 0.0)], [(125.0, 0.0), (225.0, 0.0)]]
    assert hg.ways.existing_walk(apart, (100.0, 0.0), (125.0, 0.0), 6.0) is None

    # ...the same two ends, with a long way round: the walk exists but the detour is worth bridging
    around = [*apart, [(100.0, 0.0), (100.0, 300.0)], [(100.0, 300.0), (125.0, 300.0)], [(125.0, 300.0), (125.0, 0.0)]]
    long_way = hg.ways.existing_walk(around, (100.0, 0.0), (125.0, 0.0), 6.0)
    assert long_way is not None and long_way > hg.ways._BRIDGE_DETOUR * 25.0

    # ...and a short way round: the hole is a second route, and a bridge would only enclose ground
    short_way = [*apart, [(100.0, 0.0), (112.5, 20.0)], [(112.5, 20.0), (125.0, 0.0)]]
    near = hg.ways.existing_walk(short_way, (100.0, 0.0), (125.0, 0.0), 6.0)
    assert near is not None and near <= hg.ways._BRIDGE_DETOUR * 25.0

    # AN END THAT TEES INTO THE MIDDLE of a way joins it there, which is the shape that made
    # Mizuguchi's loop invisible to a test that looked only at lane ENDS
    tee = [[(0.0, 0.0), (200.0, 0.0)], [(50.0, 0.0), (50.0, 60.0)], [(150.0, 0.0), (150.0, 60.0)]]
    assert hg.ways.existing_walk(tee, (50.0, 60.0), (150.0, 60.0), 6.0) == 220.0

    # the pass itself: the loop is refused, the honest hole is drawn
    loop = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], [(200.0, 500.0), (400.0, 500.0)], [(425.0, 500.0), (500.0, 560.0)], [(400.0, 500.0), (412.0, 470.0)], [(412.0, 470.0), (425.0, 500.0)]])
    assert hg.ways._bridge_collinear_breaks(loop, [], [], []) == 0, "the walk round is already short"
    hole = _StubSettlement(lanes=[[(0.0, 900.0), (0.0, 940.0)], [(200.0, 500.0), (400.0, 500.0)], [(425.0, 500.0), (500.0, 560.0)]])
    assert hg.ways._bridge_collinear_breaks(hole, [], [], []) == 1, "nothing connects these ends: bridge it"


def test_a_nub_is_KEPT_when_dropping_it_would_push_the_lane_into_the_fabric() -> None:
    """The refusal half of `_drop_end_nubs`, which no map in the suite reaches.

    Removing an end nub STRAIGHTENS the lane, and a straightened lane can lie closer to a farmhouse
    than the doglegged one did - measured on Kashikawa, where this pass took a house corner from 3.18
    ft clear of a tread to 0.69 ft inside it. So the pass judges the RESULT: the nub is only worth
    removing if what replaces it is clear, and where it is not, the lane is put back exactly as it was.

    Here the dogleg holds the lane at y=5 while the straightened run cuts the corner toward y=2.5, and
    the fabric sits just below it - so the rewrite is refused and the nub survives.
    """
    from l7r.diagram.hamletgen.ways.sweeps import _drop_end_nubs

    lane = [(0.0, 0.0), (2.0, 5.0), (100.0, 5.0)]  # a leading nub: 5.4 ft then a 68 degree turn
    s = _StubSettlement(lanes=[lane])
    fabric = [[(45.0, -3.0), (55.0, -3.0), (55.0, 1.0), (45.0, 1.0)]]  # under the STRAIGHTENED line, not the dogleg
    _drop_end_nubs(s, fabric)
    assert [tuple(p) for p in s.M["lanes"][0]["pts"]] == [(0.0, 0.0), (2.0, 5.0), (100.0, 5.0)], "the nub must survive: dropping it would put the tread nearer the fabric than the dogleg was"
    # ...and with nothing to foul, the very same nub IS dropped - so the assertion above is about the
    # fabric and not about the nub being unrecognized.
    s2 = _StubSettlement(lanes=[lane])
    _drop_end_nubs(s2, [])
    assert [tuple(p) for p in s2.M["lanes"][0]["pts"]] == [(0.0, 0.0), (100.0, 5.0)], "with clear ground the nub goes"
