"""`hamletgen/ways/settle/`: the web settles itself (feature 287, M4) - each rule of the lane law, provoked on constructed
lanes, is repaired by `settle_the_web` and asked again of the same predicate the finished-map tests read. Steps 1-3 here; the
reach the web owes (step 4) and the law asked of a new lane are `test_settle_reach.py` (split at the 1,000-line bar, 405 T107)."""

import math

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


def test_every_crossing_is_squared_and_a_joint_at_a_moved_end_moves_with_it() -> None:
    # the lane starts 4 ft short of the brook and crosses it 39 degrees off square - the "left as drawn" case of old
    s = _S([CONN, [(96.0, 20.0), (300.0, 180.0)], [(96.0, 20.0), (0.0, 0.0)]], streams=[BROOK], drawn_channels=[{"pts": [[400.0, -500.0], [400.0, 500.0]], "w0": 4.0}, {"pts": [[0.0, 0.0]]}])
    s.M["lanes"].append({"pts": [[1.0, 1.0]]})
    assert settle.square_every_crossing(s) == 1
    assert law.oblique_crossings(s.M) == []
    assert _pts(s, 2)[0] == _pts(s, 1)[0], "the lane that ended where the squared lane began still meets it"
    assert settle.square_every_crossing(s) == 0, "squaring a squared web changes nothing"


# ---- step 2: shapes and crossings --------------------------------------------------------------------------------


def test_a_hook_is_relaid_as_a_tee_and_a_free_hook_loses_its_leg() -> None:
    way = [(0.0, 100.0), (0.0, -100.0)]
    hooked_on = [(-100.0, 0.0), (8.0, 0.0), (0.0, 6.0)]  # overshoots the way by 8 ft and bends back onto it
    free = [(-100.0, 300.0), (100.0, 300.0), (95.0, 308.0)]
    s = _S([_c(*way), hooked_on, free, _c((0.0, 500.0), (100.0, 500.0), (95.0, 508.0))])
    settle.settle_shapes(s)
    assert law.hooked_ends(s.M) == []
    assert min(math.dist(_pts(s, 1)[-1], q) for q in [(0.0, y) for y in range(-100, 101)]) <= law.JOIN_TOL, "still on the way it joined"


def test_a_returning_leg_under_40_ft_is_cut_and_a_zigzag_pulled_straight() -> None:
    """0081 (feature 328): "a returning leg under 40 ft is cut" - a 30 ft one goes, and a 50 ft one too (a lane never doubles
    back; the page gives no other remedy, a GUESS); "Two turns of more than
    50 degrees within 40 ft of path ... are pulled straight" - one lane, its two turns dropped (it was cut into two)."""
    s = _S([CONN, [(0.0, 50.0), (200.0, 50.0), (170.0, 54.0)], [(0.0, 300.0), (100.0, 300.0), (100.0, 320.0), (200.0, 320.0)]])
    settle.settle_shapes(s)
    assert law.lanes_that_kink(s.M) == []
    assert any(ln["pts"] == [[0.0, 50.0], [200.0, 50.0]] for ln in s.M["lanes"]), "the 30 ft returning leg is cut"
    assert any(ln["pts"] == [[0.0, 300.0], [200.0, 320.0]] for ln in s.M["lanes"]), "the zigzag pulled straight, one lane"
    from l7r.diagram.hamletgen.ways.settle import _unkinked

    long_back = [(0.0, 50.0), (200.0, 50.0), (150.0, 55.0)]  # a 50 ft returning leg: a lane never doubles back, so it goes too (GUESS)
    assert _unkinked(long_back, ("doubles back", 1, 1)) == [long_back[:2]]


def test_seed_43s_lattice_step_is_a_kink_the_old_bend_test_passed() -> None:
    """Ways W18 (FR-003): two 50 degree turns separated by two short legs - summed 30 ft - kink; the one-segment reading the
    web's passes used to ask let it through."""
    step = [(0.0, 0.0), (100.0, 0.0), (110.0, 12.0), (115.0, 25.0), (215.0, 25.0)]
    assert law.bends_badly(step)
    s = _S([CONN, step])
    settle.settle_the_web(s)
    assert law.lanes_that_kink(s.M) == []


def test_a_brook_crossed_out_and_back_loses_the_far_bank_stretch() -> None:
    husk = [(1.0, 1.0)]  # which the shape step passes over
    s = _S([CONN, [(0.0, 0.0), (200.0, 0.0), (200.0, 80.0), (0.0, 80.0)], husk], streams=[BROOK], meta={"ftpx": 1.0, "brook_fords": [[100.0, 0.0], [100.0, 80.0]]})
    assert law.over_and_back(s.M)
    settle.settle_shapes(s)
    assert law.over_and_back(s.M) == []
    assert all(ln["pts"][0][0] < 100.0 or ln["pts"][-1][0] < 100.0 for ln in s.M["lanes"][1:] if len(ln["pts"]) >= 2), "what is left is on the home bank"


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


def test_a_crossing_off_a_ford_is_cut_and_one_at_a_ford_stands() -> None:
    s = _S([CONN, [(0.0, 0.0), (200.0, 0.0)], [(0.0, 200.0), (200.0, 200.0)]], streams=[BROOK], meta={"ftpx": 1.0, "brook_fords": [[100.0, 5.0]]})
    settle.settle_shapes(s)
    assert law.off_ford_crossings(s.M) == []
    assert any(ln["pts"] == [[0.0, 0.0], [200.0, 0.0]] for ln in s.M["lanes"]), "the lane at the ford is untouched"


def test_a_crossing_left_oblique_is_cut() -> None:
    lanes = [CONN, [(0.0, 0.0), (200.0, 150.0)]]
    s = _S(lanes, streams=[BROOK], meta={"ftpx": 1.0, "brook_fords": [[100.0, 75.0]]})
    settle.settle_shapes(s)
    assert law.oblique_crossings(s.M) == []
    ch = _S(lanes, drawn_channels=[{"pts": [[100.0, -500.0], [100.0, 500.0]], "w0": 4.0}])
    settle.settle_shapes(ch)
    assert law.oblique_crossings(ch.M, "channel") == []


def test_a_crossing_no_deck_seats_is_squared_and_else_cut() -> None:
    """Ways W12/W13: `law.undeckable_at` is the placer's own deck solve. A shallow crossing of a field ditch is squared
    where a square deck seats; one that cannot seat even square - its landing on flooded rice - is cut."""
    ditch = {"poly": [[0.0, 100.0], [400.0, 110.0]], "w": 4.0, "role": "main"}
    shallow = [(0.0, 95.0), (400.0, 118.0)]  # two degrees off the ditch's own line
    s = _S([CONN, shallow], field_ditches=[ditch])
    assert law.undeckable_crossings(s.M), "the fixture provokes the violation"
    settle.settle_shapes(s)
    assert law.undeckable_crossings(s.M) == []
    ring = [[-50.0, 101.75], [450.0, 114.25], [450.0, 400.0], [-50.0, 400.0]]  # the rice 3 ft past the ditch's line
    rice = {"outline": ring, "plot_rings": [ring]}
    wet = _S([CONN, [(200.0, 0.0), (200.0, 300.0)]], field_ditches=[ditch], fields=[rice])
    assert law.undeckable_crossings(wet.M), "the deck's far landing stands in the rice"
    settle.settle_shapes(wet)
    assert law.undeckable_crossings(wet.M) == []


def test_a_lane_through_a_neighbors_plot_or_a_building_is_cut_but_not_through_its_own() -> None:
    yard = {"poly": [[90.0, -10.0], [110.0, -10.0], [110.0, 10.0], [90.0, 10.0]], "of": [300.0, 300.0]}
    own = {"poly": [[390.0, 190.0], [410.0, 190.0], [410.0, 210.0], [390.0, 210.0]], "of": [400.0, 240.0]}
    s = _S(
        [CONN, [(0.0, 0.0), (200.0, 0.0)], [(300.0, 200.0), (400.0, 200.0)], [(0.0, 600.0), (200.0, 600.0)]],
        houses=[(300.0, 300.0), (400.0, 240.0)],
        threshing_yards=[yard, own],
        byres=[{"x": 100.0, "y": 600.0, "w": 10.0, "h": 10.0}],
    )
    s.M["lanes"][2]["serves"] = [400.0, 240.0]  # a door path names its household (405 T18)
    settle.settle_shapes(s)
    assert [ln["pts"] for ln in s.M["lanes"] if ln["pts"][0] == [300.0, 200.0]] == [[[300.0, 200.0], [400.0, 200.0]]], "a door path crosses its own yard"
    assert not any(ln["pts"] == [[0.0, 0.0], [200.0, 0.0]] for ln in s.M["lanes"]), "the neighbor's yard is not crossed"
    assert law.breaks_mid_run(s.M) == []


# ---- step 3: the ways out (ways W08) -----------------------------------------------------------------------------


def test_no_way_out_crosses_the_brook_twice() -> None:
    # the connector on the west bank; a house on the west bank whose lanes leave over the brook and come back
    lanes = [_c((50.0, 0.0), (-1000.0, 0.0)), [(50.0, 0.0), (50.0, 100.0)], [(50.0, 100.0), (150.0, 100.0), (150.0, 300.0), (50.0, 300.0)]]
    s = _S(lanes, houses=[(40.0, 320.0)], streams=[BROOK], meta={"ftpx": 1.0, "brook_fords": [[100.0, 100.0], [100.0, 300.0]]})
    assert law.way_outs_crossing(s.M), "the fixture provokes the violation"
    assert settle.settle_way_outs(s) == 1
    assert law.way_outs_crossing(s.M) == []
    assert settle.settle_way_outs(s) == 0


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


def test_a_way_out_only_tree_lanes_carry_over_and_back_loses_the_tree_lane_nearest_the_house() -> None:
    """Ways W08, the tree half: `settle_way_outs` cut only ordinary lanes, so a way out carried over the brook and back on
    tree lanes alone was left (the kept test's reason). The first tree lane carrying it goes whole; the reach is the next
    step's to lay again, under `Lawful`."""
    s = _over_and_back_on_the_tree()
    assert law.way_outs_crossing(s.M) and all(co.is_tree(s.M["lanes"][i]) for i, _k, _y in law.way_out_carriers(s.M)), "the fixture provokes it on the tree"
    assert settle.settle_way_outs(s) == 1
    assert [ln.get("role") for ln in s.M["lanes"]] == [None, "way target"] and law.way_outs_crossing(s.M) == []
    assert law.way_out_carriers(s.M) == [] and settle.settle_way_outs(s) == 0


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


def test_a_street_s_dangling_end_is_cut_back_to_its_last_joint() -> None:
    """`settle_street_ends` (feature 293 on 291, cohort seed 903): a row's street, a tree lane, has the end the law calls
    dangling cut back to its last joint - the door path's; a map with no street, or a street no end dangles on, is left."""
    street = ([(0.0, 0.0), (0.0, 200.0), (0.0, 600.0)], {"w": 6})
    s = _S([CONN, street, [(0.0, 200.0), (80.0, 200.0)], [(-300.0, 0.0), (-300.0, 200.0)], ([(-500.0, -500.0), (-500.0, -400.0)], {"w": 6})], houses=[(100.0, 200.0)])
    s.M["lanes"][1].update({"street": True, "street_index": 1})
    s.M["lanes"][-1].update({"street": True, "street_index": 0})  # the row's first street, which the settle passes by
    assert {(1, -1), (3, -1)} <= set(law.dangling_lane_ends(s.M)), "the street's end, and an ordinary lane's"
    assert settle.settle_street_ends(s) == 1
    assert _pts(s, 3)[-1] == (-300.0, 200.0), "an ordinary lane is the other repairs' to trim"
    assert _pts(s, 1)[-1] == (0.0, 200.0)
    assert settle.settle_street_ends(s) == 0, "cut already"
    assert settle.settle_street_ends(_S([CONN, [(0.0, 0.0), (0.0, 600.0)]])) == 0, "no street"
    lone = _S([CONN, ([(500.0, 300.0), (500.0, 600.0)], {"w": 6})])
    lone.M["lanes"][1].update({"street": True, "street_index": 0})
    assert settle.settle_street_ends(lone) == 0, "no joint on it: as it is"


def test_a_street_s_dangling_end_keeps_the_last_farm_it_serves(monkeypatch: pytest.MonkeyPatch) -> None:
    """385 T127 (405 T13, D22): a farm the street serves without a door path stands past its last lane joint - the end is cut
    back to that farm's point (`street_anchors`, as the web's trim reads it), not to the joint before it."""
    street = ([(0.0, 0.0), (0.0, 200.0), (0.0, 600.0)], {"w": 6})
    s = _S([CONN, street, [(0.0, 200.0), (80.0, 200.0)], ([(-500.0, -500.0), (-500.0, -400.0)], {"w": 6})], houses=[(100.0, 200.0)])
    s.M["lanes"][1].update({"street": True, "street_index": 1})
    s.M["lanes"][-1].update({"street": True, "street_index": 0})  # the row's first street, which the settle passes by
    monkeypatch.setattr(settle.ends, "street_anchors", lambda s: [(0.0, 400.0)])
    assert settle.settle_street_ends(s) == 1
    assert _pts(s, 1)[-1] == pytest.approx((0.0, 400.0)), "kept to the farm it serves"


def test_a_street_s_dangling_end_stops_where_it_crosses_a_way(monkeypatch: pytest.MonkeyPatch) -> None:
    """405 T49 (D26, T13's round): a street crossing a way mid-run and dangling past it ends at the crossing, on the way
    (0246 section 6), not back at the joint before it."""
    street = ([(0.0, 0.0), (0.0, 200.0), (0.0, 600.0)], {"w": 6})
    s = _S([CONN, street, [(0.0, 200.0), (80.0, 200.0)], [(-100.0, 450.0), (100.0, 450.0)], ([(-500.0, -500.0), (-500.0, -400.0)], {"w": 6})], houses=[(100.0, 200.0)])
    s.M["lanes"][1].update({"street": True, "street_index": 1})
    s.M["lanes"][-1].update({"street": True, "street_index": 0})  # the row's first street, which the settle passes by
    monkeypatch.setattr(settle.ends, "street_anchors", lambda s: [])
    monkeypatch.setattr(settle.law, "dangling_lane_ends", lambda M, ground: [(1, -1)])
    assert settle.settle_street_ends(s) == 1
    assert _pts(s, 1)[-1] == pytest.approx((0.0, 450.0)), "ended on the way it crosses"


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


def test_a_piece_off_the_network_goes_and_so_does_a_husk() -> None:
    s = _S([CONN, [(0.0, 2.0), (0.0, 100.0)], [(0.0, 300.0), (0.0, 400.0)], [(5.0, 5.0)]])
    assert settle.settle_husks(s) == 1
    assert settle.settle_network(s) == 1
    assert law.lane_networks(s.M) == 1 and settle.settle_network(s) == 0
    headless = _S([[(0.0, 0.0), (0.0, 500.0)], [(300.0, 0.0), (300.0, 50.0)]])
    settle.settle_network(headless)
    assert len(headless.M["lanes"]) == 1 and headless.M["lanes"][0]["pts"][1] == [0.0, 500.0], "no connector: the longest network stands"


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


def test_a_join_that_stopped_short_is_carried_onto_its_way() -> None:
    shy = law.JOIN_REACH_FT - 3.0  # inside the page's 25 ft join reach (0081)
    s = _S([CONN, [(0.0, 0.0), (0.0, 400.0)], [(200.0, 100.0), (shy, 100.0)]])
    assert settle.settle_joins(s) == 1
    assert _pts(s, 2)[-1] == (0.0, 100.0) and law.near_misses(s.M) == []
    assert settle.settle_joins(s) == 0
    both = _S([CONN, [(0.0, 0.0), (0.0, 400.0)], [(300.0, 0.0), (300.0, 400.0)], [(shy, 100.0), (300.0 - shy, 100.0)]])
    assert settle.settle_joins(both) == 1 and settle.settle_joins(both) == 1, "one end a round"
    assert law.near_misses(both.M) == []


def test_a_piece_the_ink_would_drop_is_joined_first() -> None:
    """Cohort seed 40: two pieces within the web's 30 ft join reach but not touching; the network rule at the ink tolerance
    dropped them and stranded two farmhouses. Settled, they are joined and kept."""
    s = _S([CONN, [(0.0, 0.0), (0.0, 400.0)], [(200.0, 200.0), (25.0, 200.0)], [(200.0, 200.0), (200.0, 350.0)]])
    settle.settle_joins(s)
    assert settle.settle_network(s) == 0
    assert len(s.M["lanes"]) == 4 and law.lane_networks(s.M) == 1


def test_a_fragment_is_dropped_and_a_chain_takes_one_width() -> None:
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
    w = _S([CONN, ([(0.0, 5.0), (100.0, 5.0)], {"w": 6}), ([(100.0, 5.0), (200.0, 15.0)], {"w": 3})])
    assert settle.settle_widths(w) == 1 and law.width_steps(w.M["lanes"]) == []
    assert {ln["w"] for ln in w.M["lanes"][1:]} == {6}, "the way takes its widest member's width"
    tight = _S([CONN, ([(0.0, 5.0), (100.0, 5.0)], {"w": 6}), ([(100.0, 5.0), (200.0, 5.0)], {"w": 3})], houses=[(150.0, 21.5)])  # its wall 2.5 ft off: past a 3 ft tread's half, inside a 6 ft one's
    settle.settle_widths(tight)
    assert {ln["w"] for ln in tight.M["lanes"][1:]} == {3}, "widened, it would foul the farmhouse beside it: the narrowest"
    assert settle.settle_widths(_S([CONN])) == 0
    # EACH WAY AT ITS RANK (feature 328 wave 4, glyph-check round 2 of Inashiro: the field route - a household's way, a 6 ft
    # link, the spur - all drawn 6 ft): the ranked lanes back to their rank, the link between them at the widest rank
    route = _S([CONN, ([(0.0, 5.0), (100.0, 5.0)], {"w": 6.0}), ([(100.0, 5.0), (200.0, 15.0)], {"w": 6}), ([(200.0, 15.0), (300.0, 15.0)], {"w": 6.0})])
    route.M["lanes"][1]["role"], route.M["lanes"][3]["spur"] = co.ACCESS_ROLE, True
    assert settle.settle_widths(route) == 3
    assert [ln["w"] for ln in route.M["lanes"][1:]] == [3.0, 5.0, 5.0] and law.width_steps(route.M["lanes"]) == []
    assert settle.settle_widths(route) == 0


def test_a_width_change_redraws_the_ink() -> None:
    from l7r.diagram.settlement import Settlement

    s = Settlement(600, 600, seed=1)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    s.lane([(0.0, 5.0), (100.0, 5.0)], width=6, worn=True)
    old = list(s._lane_ink[0])
    settle.rewidth(s, 0, 3.0)
    assert s.M["lanes"][0]["w"] == 3.0 and s._lane_ink[0] != old
    assert all(not s.ground[z].get(part) for z in old for part in ("edge", "bed", "top")), "the old ink is blanked"
