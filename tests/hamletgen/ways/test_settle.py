"""`hamletgen/ways/settle/`: the web settles itself (feature 287, M4) - each rule of the lane law, provoked on constructed
lanes, is repaired by `settle_the_web` and asked again of the same predicate the finished-map tests read. Steps 1-3 here; the
reach the web owes (step 4) and the law asked of a new lane are `test_settle_reach.py` (split at the 1,000-line bar, 405 T107)."""

import pytest

from l7r.diagram.hamletgen.ways import corridors as co
from l7r.diagram.hamletgen.ways import law, settle

from ._settle_builders import _GEN, _S, BROOK, CONN, _c, _pts

# ---- the arc-length helpers ----------------------------------------------------------------------------------------


def test_a_run_is_sliced_and_cut_by_arc_length() -> None:
    p = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
    assert settle.sub_run(p, 50.0, 150.0) == [(50.0, 0.0), (100.0, 0.0), (100.0, 50.0)]
    assert settle.sub_run(p, 80.0, 80.0) == [] and settle.sub_run([(0.0, 0.0)], 0.0, 1.0) == []
    assert settle.sub_run([(0.0, 0.0), (0.0, 0.0), (10.0, 0.0)], 0.0, 10.0) == [(0.0, 0.0), (10.0, 0.0)], "a zero-length leg is skipped"
    assert settle.arc_at(p, 1, (100.0, 30.0)) == 130.0
    head, tail = settle.cut_around(p, 100.0, 10.0)
    assert head[-1] == (90.0, 0.0) and tail[0] == (100.0, 10.0)
    assert settle.cut_around(p, 0.0, 10.0) == [[(10.0, 0.0), (100.0, 0.0), (100.0, 100.0)]]


def test_pieces_replace_a_lane_and_a_lane_with_none_goes() -> None:
    s = _S([CONN, [(0.0, 0.0), (0.0, 100.0)], [(5.0, 0.0), (5.0, 50.0)]])
    s.M["lanes"][1]["role"] = "web"
    assert settle.apply_pieces(s, {1: [[(0.0, 0.0), (0.0, 40.0)], [(0.0, 60.0), (0.0, 100.0)], [(0.0, 0.0), (0.0, 0.5)]], 2: []}) == 2
    assert [len(ln["pts"]) for ln in s.M["lanes"]] == [2, 2, 2] and s.M["lanes"][-1]["role"] == "web", "the second piece keeps its kind"


# ---- step 1: every crossing square (ways W11) --------------------------------------------------------------------


# ---- step 2: shapes and crossings --------------------------------------------------------------------------------


def test_seed_43s_lattice_step_is_a_kink_the_old_bend_test_passed() -> None:
    """Ways W18 (FR-003): two 50 degree turns separated by two short legs - summed 30 ft - kink; the one-segment reading the
    web's passes used to ask let it through."""
    step = [(0.0, 0.0), (100.0, 0.0), (110.0, 12.0), (115.0, 25.0), (215.0, 25.0)]
    assert law.bends_badly(step)
    s = _S([CONN, step])
    settle.settle_the_web(s)
    assert law.lanes_that_kink(s.M) == []


def test_a_re_laid_end_meets_its_way_clean_or_not_at_all() -> None:
    tread = [(0.0, 0.0), (300.0, 0.0)]
    assert settle.meets_clean([(100.0, 100.0), (100.0, 0.0)], tread)
    assert not settle.meets_clean([(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)], tread), "a needle"
    assert not settle.meets_clean([(60.0, 15.0), (10.0, 15.0), (0.0, 0.0)], [(0.0, 0.0), (100.0, 0.0)], connector=True), "a hairpin at the connector's start"
    assert not settle.meets_clean([(0.0, 50.0), (300.0, 0.0)], [(300.0, 0.0), (0.0, 40.0)]), "a fold at a joint"
    assert settle.reaimed([(0.0, 1.0), (50.0, 0.0)], tread) == [(0.0, 1.0)], "no vertex to re-lay from: the last leg goes"


def test_an_end_that_crossed_its_way_is_teed_where_it_first_reaches_it() -> None:
    """405 T134 (D124), cohort seed 10 with T26's sheds: a link crossed the track 30 ft from its head and hooked back to the
    head; the re-aim teed it from its last vertex 12 ft from the head, beside the junction there - a knot. It is cut where it
    first crosses the way (0081: a tail under 40 ft beyond a crossing is cut; a lane laid only to join two others, however long),
    on a way long enough that a margin taken as a share of it would miss the crossing."""
    tread = [(0.0, 0.0), (0.0, -3000.0)]
    seq = [(100.0, -60.0), (20.0, -40.0), (-20.0, -20.0), (0.0, 0.0)]  # its tail beyond the crossing is 51 ft
    assert settle.reaimed(seq, tread, connector=True, joiner=True) == [(100.0, -60.0), (20.0, -40.0), (0.0, -30.0)], "a lane laid only to join: any tail"
    assert settle.reaimed(seq, tread, connector=True) != [(100.0, -60.0), (20.0, -40.0), (0.0, -30.0)], "40 ft or more: re-laid as before"
    short = [(100.0, -60.0), (20.0, -40.0), (-10.0, -25.0), (0.0, -15.0)]  # a 26 ft tail
    assert settle.reaimed(short, tread) == [(100.0, -60.0), (20.0, -40.0), (0.0, -30.0)], "a tail under 40 ft is cut at the crossing"


# ---- step 3: the ways out (ways W08) -----------------------------------------------------------------------------


def _over_and_back_on_the_tree():
    """A household on the west bank whose only way out is two TREE lanes - its field way east over the brook, and a spur
    back west over it to the connector's start: every crossing of its way out is on a lane no repair cuts."""
    back = ([(50.0, 0.0), (50.0, 100.0), (150.0, 100.0), (150.0, 300.0)], {"role": "way target"})
    out = ([(150.0, 300.0), (50.0, 300.0)], {"role": "way target"})
    s = _S([_c((50.0, 0.0), (-1000.0, 0.0))], houses=[(40.0, 340.0)], streams=[BROOK], meta={**_GEN, "brook_fords": [[100.0, 100.0], [100.0, 300.0]]})
    for pts, kw in (back, out):
        s.M["lanes"].append({"pts": [list(q) for q in pts], "w": 3, "worn": True, **kw})
    s.M["houses"][0]["rot"] = 180.0  # its front faces the field way's end
    return s


def test_lawful_refuses_a_tree_lane_that_hands_a_household_a_way_out_over_the_brook_and_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """`Lawful` asks the ROUTE, not only the lane (`law.adds_a_way_out_crossing`): the field way east over the brook is a
    clean lane, crossing once at a ford, but it makes the household's way out cross twice - refused; a run on its own bank
    is not."""
    s = _over_and_back_on_the_tree()
    field_way = settle._pts(s.M["lanes"][2])
    del s.M["lanes"][2]
    assert law.way_outs_crossing(s.M) == [] and law.adds_a_way_out_crossing(s.M, field_way, 3.0), "the violating case"
    assert not law.adds_a_way_out_crossing(s.M, [(50.0, 300.0), (50.0, 150.0)], 3.0), "a run on the household's own bank"
    assert not law.adds_a_way_out_crossing({**s.M, "streams": []}, field_way, 3.0), "no brook, no way out to cross it"
    assert not settle.Lawful(s, tree=True)(field_way, 3.0)
    assert settle.Lawful(s)(field_way, 3.0), "...and it is the way out that refuses it: an ordinary lane keeps every other rule"
    monkeypatch.setattr(law, "adds_a_way_out_crossing", lambda *a, **k: False)
    assert settle.Lawful(s, tree=True)(field_way, 3.0)


# ---- step 4: joints and ends -------------------------------------------------------------------------------------


def test_kuwabatas_lane_and_connector_doubling_back_meet_as_a_tee() -> None:
    """Ways W22, the pool finding T03 recorded: Kuwabata's lane runs 126 ft east beside the connector and turns back onto its
    start over a 15 ft leg (the geometry as shipped). Settled, it meets the connector as a T and the web stays one."""
    conn = _c((2055.3, 25.3), (1408.0, -20.4), (366.5, 35.3), (-1871.9, -62.9))
    lane = [(2158.0, 457.2), (1957.1, 462.4), (1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]
    s = _S([conn, lane])
    assert law.connector_hairpins(s.M["lanes"])
    settle.settle_ends(s)
    assert law.connector_hairpins(s.M["lanes"]) == [] and law.lane_networks(s.M) == 1


def test_mizuguchis_needle_join_is_relaid_square() -> None:
    """Ways W21, the pool finding: a join whose last 35 ft runs back along the lane it meets at 16 degrees."""
    tread = [(0.0, 0.0), (300.0, 0.0)]
    needle = [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)]
    s = _S([CONN, tread, needle])
    assert law.needle_joins(s.M["lanes"])
    settle.settle_ends(s)
    assert law.needle_joins(s.M["lanes"]) == [] and law.lane_networks(s.M) == 1


def test_a_fold_at_a_joint_becomes_a_tee_and_two_bare_legs_lose_the_shorter() -> None:
    s = _S([CONN, [(0.0, 0.0), (100.0, 0.0)], [(-50.0, 30.0), (50.0, 8.0), (100.0, 0.0)]])
    # lanes 1 and 2 meet end to end at (100, 0) and the second doubles back beside the first
    settle.settle_ends(s)
    assert law.folded_joints(s.M["lanes"]) == [] and law.lane_networks(s.M) == 1
    bare = _S([CONN, [(0.0, 150.0), (100.0, 150.0)], [(100.0, 150.0), (20.0, 170.0)]])  # two bare legs folded 166 degrees
    settle.settle_ends(bare)
    assert law.folded_joints(bare.M["lanes"]) == []


def test_a_tail_run_on_beside_another_way_is_cut_where_it_came_alongside() -> None:
    s = _S([_c((100.0, 5.0), (300.0, 5.0), (1300.0, 5.0)), [(0.0, 60.0), (100.0, 0.0), (140.0, 2.0)]])
    assert law.doubled_tails(s.M) == [1]
    settle.settle_the_web(s)
    assert law.doubled_tails(s.M) == []


def test_a_lane_whose_first_end_runs_on_beside_a_way_is_cut_there_too() -> None:
    """Feature 293 on 291 (Mizuguchi's field spur): `doubled_tails` asks both ends, and the repair cuts the first end as the
    lane reversed, turned back."""
    s = _S([_c((100.0, 5.0), (300.0, 5.0), (1300.0, 5.0)), [(140.0, 2.0), (100.0, 0.0), (0.0, 60.0)]])
    assert law.doubled_tails(s.M) == [1]
    settle.settle_the_web(s)
    assert law.doubled_tails(s.M) == []


def _a_link_beside_a_door_path() -> _S:
    s = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 0.0), (15.0, 20.0), (15.0, 250.0)], [(15.0, 250.0), (200.0, 250.0)]])
    s.M["lanes"][1]["serves"] = [0.0, 320.0]  # a door path: a tree lane, never the one that goes
    return s


def test_a_farmhouse_discharges_two_lane_ends_not_three() -> None:
    ends = [[(x, 300.0), (x, 80.0)] for x in (-40.0, 0.0, 40.0)]
    s = _S([CONN, *ends], houses=[(0.0, 50.0)])
    assert law.doorstep_ends(s.M)
    settle.settle_ends(s)
    assert law.doorstep_ends(s.M) == {}
    near = _S([CONN, *[[(x, 60.0), (x, 70.0)] for x in (-40.0, 0.0, 40.0)]], houses=[(0.0, 50.0)])
    settle.settle_ends(near)
    assert law.doorstep_ends(near.M) == {}, "an end with no vertex beyond the doorstep takes its lane with it"


def test_a_lane_end_in_open_ground_is_trimmed_and_a_lane_serving_nothing_goes() -> None:
    s = _S([CONN, [(-50.0, 0.0), (-50.0, 300.0)], [(-500.0, 2.0), (-500.0, 3.0)]], houses=[(-50.0, 120.0)])
    settle.settle_ends(s)
    assert law.dangling_ends(s.M) == []
    assert settle.settle_dangling(_S([CONN])) == 0


# ---- step 5: one network (ways W17) and the husks (W04) ----------------------------------------------------------


# ---- the loop ----------------------------------------------------------------------------------------------------


def test_a_web_that_keeps_every_rule_is_left_as_it_was() -> None:
    # the lane starts ON the connector's head: 2 ft off it, as it stood before feature 328 wave 4, the two ends are a knot the
    # settle gathers (`knots.settle_knots`, research/questions/0081-village-lanes.drawing.html: joined at a single point)
    s = _S([CONN, [(0.0, 0.0), (0.0, 100.0)]], houses=[(40.0, 110.0)])
    before = [dict(ln) for ln in s.M["lanes"]]
    got = settle.settle_the_web(s)
    assert got["rounds"] == 1 and got["changed"] == 0 and got["dropped"] == 0
    assert s.M["lanes"] == before


def test_the_settled_web_breaks_no_rule_of_the_law(monkeypatch: pytest.MonkeyPatch) -> None:
    lanes = [
        CONN,
        [(0.0, 2.0), (0.0, 200.0), (5.0, 150.0)],  # doubles back
        [(0.0, 100.0), (300.0, 100.0)],  # crosses the brook off its ford
        [(0.0, 150.0), (60.0, 150.0), (60.0, 170.0), (0.0, 170.0), (0.0, 171.0)],  # a lattice step and a hook
    ]
    s = _S(lanes, houses=[(20.0, 60.0)], streams=[BROOK], meta={"ftpx": 1.0, "brook_fords": [[100.0, 400.0]]})
    # every lane here breaks a rule and goes, the house and the field left unreached - the reach is not this test's subject, and
    # since feature 320 a brook map's field no way reaches is refused whatever was reserved (`last_resort.refuse_unreached`)
    monkeypatch.setattr(law, "field_unreached", lambda M: False)
    got = settle.settle_the_web(s)
    assert got["rounds"] >= 2
    left = {k: v for k, v in law.violations(s.M).items() if k not in ("unreached_houses", "field_unreached")}
    assert left == {}, left


# ---- joins, fragments, widths (homes H37-H40, H42) -------------------------------------------------------------------


def test_a_crossing_no_deck_seats_is_squared_and_else_cut() -> None:
    """Ways W12/W13: `law.undeckable_at` is the placer's own deck solve, asked of a lane by `_crossing_fault`. A shallow crossing
    of a field ditch is squared where a square deck seats; one that cannot seat even square - its landing on flooded rice - is
    cut (asked of one lane: the settle's own shapes step went in feature 417 T31, and `Lawful` and the last resort ask it)."""
    ditch = {"poly": [[0.0, 100.0], [400.0, 110.0]], "w": 4.0, "role": "main"}
    shallow = [(0.0, 95.0), (400.0, 118.0)]  # two degrees off the ditch's own line
    s = _S([CONN, shallow], field_ditches=[ditch])
    fixed = settle._crossing_fault(s.M, 1, _pts(s, 1), [])
    assert fixed is not None and len(fixed) == 1 and not law.undeckable_crossings({**s.M, "lanes": [s.M["lanes"][0], {**s.M["lanes"][1], "pts": [list(q) for q in fixed[0]]}]}), "squared"
    ring = [[-50.0, 101.75], [450.0, 114.25], [450.0, 400.0], [-50.0, 400.0]]  # the rice 3 ft past the ditch's line
    wet = _S([CONN, [(200.0, 0.0), (200.0, 300.0)]], field_ditches=[ditch], fields=[{"outline": ring, "plot_rings": [ring]}])
    cut = settle._crossing_fault(wet.M, 1, _pts(wet, 1), [[(float(x), float(y)) for x, y in ring]])
    assert cut is not None and len(cut) == 2 and cut[0][-1][1] < 105.0 < cut[1][0][1], "cut either side of the ditch's line (y 105 at x 200)"


def test_with_no_connector_the_longest_network_is_kept() -> None:
    """`settle_network` keeps the connector's network; where no lane is the connector, the longest network is kept."""
    s = _S([[(0.0, 0.0), (400.0, 0.0)], [(0.0, 500.0), (100.0, 500.0)]])
    assert settle.settle_network(s) == 1 and _pts(s, 0) == [(0.0, 0.0), (400.0, 0.0)]


def test_a_fragment_is_dropped_but_never_a_household_s_own_way() -> None:
    s = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 150.0), (10.0, 150.0)]], meta={"ftpx": 1.0, "generated_by": "hamletgen"})
    assert settle.settle_fragments(s) == 1 and len(s.M["lanes"]) == 2
    assert settle.settle_fragments(s) == 0
    # A HOUSEHOLD'S OWN WAY IS NEVER DEBRIS (feature 318, FR-014): a short access corridor to a house another lane already
    # reaches is still the lane that household is served by - it stays (homes H40 dropped it, R9; owed again, it looped)
    tree = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 150.0), (10.0, 150.0)]], houses=[(40.0, 150.0)], meta={"ftpx": 1.0, "generated_by": "hamletgen"})
    tree.M["lanes"][2].update(role=co.ACCESS_ROLE, of=[40.0, 150.0])
    assert law.short_fragments(tree.M) == [] and settle.settle_fragments(tree) == 0 and len(tree.M["lanes"]) == 3
    only = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 150.0), (20.0, 150.0)]], houses=[(115.0, 150.0)], meta={"ftpx": 1.0, "generated_by": "hamletgen"})
    only.M["lanes"][2].update(role=co.ACCESS_ROLE, of=[115.0, 150.0])
    assert law.unreached_houses(only.M) == [] and settle.settle_fragments(only) == 0, "the house's only way earns its place"
