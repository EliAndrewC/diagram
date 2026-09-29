"""`hamletgen/ways/settle.py`: the web settles itself (feature 287, M4) - each rule of the lane law, provoked on constructed
lanes, is repaired by `settle_the_web` and asked again of the same predicate the finished-map tests read."""

import math

import pytest

from l7r.diagram.hamletgen.ways import corridors as co
from l7r.diagram.hamletgen.ways import law, settle
from l7r.diagram.settlement import segments_cross

from ._builders import AdmitsAll


class _S(AdmitsAll):
    """The four things `settle_the_web` touches on a Settlement: the manifest, `lane()`, `reink_lane()`, `drop_lanes()`."""

    def __init__(self, lanes=(), houses=(), **extra):
        self.M = {"lanes": [], "houses": [{"x": x, "y": y, "w": 40.0, "h": 28.0, "rot": 0.0} for x, y in houses], "meta": {"ftpx": 1.0}, **extra}
        for ln in lanes:
            pts, kw = (ln, {}) if isinstance(ln, list) else ln
            self.M["lanes"].append({"pts": [list(q) for q in pts], "w": kw.get("w", 3), "worn": True, "connector": kw.get("connector", False), **({"spur": True} if kw.get("spur") else {})})

    def lane(self, pts, width=3, clearance=0, worn=True, connector=False, spur=False):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": width, "worn": worn, "connector": connector, "spur": spur})

    def reink_lane(self, i):
        pass

    def drop_lanes(self, idxs):
        for i in sorted(set(idxs), reverse=True):
            del self.M["lanes"][i]


def _c(*pts):
    return ([*pts], {"connector": True, "w": 6})


def _pts(s, i):
    return [(float(x), float(y)) for x, y in s.M["lanes"][i]["pts"]]


BROOK = {"poly": [[100.0, -500.0], [100.0, 500.0]], "w": 6.0}
CONN = _c((0.0, 0.0), (-1000.0, 0.0))


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


def test_a_lane_that_doubles_back_keeps_its_longer_arm_and_a_kink_loses_its_middle() -> None:
    s = _S([CONN, [(0.0, 50.0), (200.0, 50.0), (150.0, 55.0)], [(0.0, 300.0), (100.0, 300.0), (100.0, 320.0), (200.0, 320.0)]])
    settle.settle_shapes(s)
    assert law.lanes_that_kink(s.M) == []
    assert any(len(ln["pts"]) == 2 and ln["pts"][0] == [0.0, 50.0] for ln in s.M["lanes"]), "the 200 ft arm is kept"


def test_seed_43s_lattice_step_is_a_kink_the_old_bend_test_passed() -> None:
    """Ways W18 (FR-003): two 50 degree turns separated by two short legs - summed 30 ft - kink; the one-segment reading the
    web's passes used to ask let it through."""
    from l7r.diagram.hamletgen.ways.clearance import _bends_badly

    step = [(0.0, 0.0), (100.0, 0.0), (110.0, 12.0), (115.0, 25.0), (215.0, 25.0)]
    assert _bends_badly(step) and law.bends_badly(step)
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
    out = ([(150.0, 300.0), (50.0, 300.0)], {"role": "field way"})
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
    assert settle.lane_violators(s) == [1, 2], "the last resort names the tree lanes when no ordinary lane carries it"
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


def test_a_way_out_left_over_the_brook_after_the_last_resort_loses_its_lanes(monkeypatch: pytest.MonkeyPatch) -> None:
    """The last resort's tail: a way out over the brook and back that is still there after the final steps loses every
    lane carrying it, tree or not - never kept as the least bad (FR-005)."""
    s = _over_and_back_on_the_tree()
    monkeypatch.setattr(settle, "lane_violators", lambda s: [])
    got = settle.settle_the_web(s, rounds=0)
    assert law.way_outs_crossing(s.M) == [] and got["dropped"] >= 1


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
    s = _S([CONN, [(0.0, 2.0), (0.0, 100.0)]], houses=[(40.0, 110.0)])
    before = [dict(ln) for ln in s.M["lanes"]]
    got = settle.settle_the_web(s)
    assert got["rounds"] == 1 and got["changed"] == 0 and got["dropped"] == 0
    assert s.M["lanes"] == before


def test_the_settled_web_breaks_no_rule_of_the_law() -> None:
    lanes = [
        CONN,
        [(0.0, 2.0), (0.0, 200.0), (5.0, 150.0)],  # doubles back
        [(0.0, 100.0), (300.0, 100.0)],  # crosses the brook off its ford
        [(0.0, 150.0), (60.0, 150.0), (60.0, 170.0), (0.0, 170.0), (0.0, 171.0)],  # a lattice step and a hook
    ]
    s = _S(lanes, houses=[(20.0, 60.0)], streams=[BROOK], meta={"ftpx": 1.0, "brook_fords": [[100.0, 400.0]]})
    got = settle.settle_the_web(s)
    assert got["rounds"] >= 2
    left = {k: v for k, v in law.violations(s.M).items() if k not in ("unreached_houses", "field_unreached")}
    assert left == {}, left


def test_the_last_resort_drops_what_the_rounds_could_not_mend(monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-005: when the rounds run out, a lane still breaking a rule goes whole - never kept as the least bad."""
    s = _S([CONN, [(0.0, 2.0), (0.0, 200.0), (5.0, 150.0)]])
    got = settle.settle_the_web(s, rounds=0)
    assert got["dropped"] == 1 and len(s.M["lanes"]) == 1
    assert settle.lane_violators(s) == []


def test_every_per_lane_rule_names_its_violator() -> None:
    lanes = [CONN, [(0.0, 2.0), (0.0, 200.0), (5.0, 150.0)], [(900.0, 0.0), (900.0, 100.0), (1000.0, 100.0), (1000.0, 0.0)], [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)], [(0.0, 0.0), (160.0, 0.0)]]
    s = _S(lanes, houses=[(40.0, 320.0)], streams=[{"poly": [[950.0, -500.0], [950.0, 500.0]], "w": 6.0}], meta={"ftpx": 1.0, "brook_fords": [[950.0, 0.0], [950.0, 100.0]]})
    bad = settle.lane_violators(s)
    assert 1 in bad and 2 in bad and 0 not in bad
    # ...and a way out over the brook and back names every lane that crosses it
    out = _S(
        [_c((50.0, 0.0), (-1000.0, 0.0)), [(50.0, 0.0), (50.0, 100.0)], [(50.0, 100.0), (150.0, 100.0), (150.0, 300.0), (50.0, 300.0)]],
        houses=[(40.0, 320.0)],
        streams=[BROOK],
        meta={"ftpx": 1.0, "brook_fords": [[100.0, 100.0], [100.0, 300.0]]},
    )
    assert 2 in settle.lane_violators(out)


# ---- joins, fragments, widths (homes H37-H40, H42) -------------------------------------------------------------------


def test_a_join_that_stopped_short_is_carried_onto_its_way() -> None:
    s = _S([CONN, [(0.0, 0.0), (0.0, 400.0)], [(200.0, 100.0), (28.0, 100.0)]])
    assert settle.settle_joins(s) == 1
    assert _pts(s, 2)[-1] == (0.0, 100.0) and law.near_misses(s.M) == []
    assert settle.settle_joins(s) == 0
    both = _S([CONN, [(0.0, 0.0), (0.0, 400.0)], [(300.0, 0.0), (300.0, 400.0)], [(28.0, 100.0), (272.0, 100.0)]])
    assert settle.settle_joins(both) == 1 and settle.settle_joins(both) == 1, "one end a round"
    assert law.near_misses(both.M) == []


def test_a_piece_the_ink_would_drop_is_joined_first() -> None:
    """Cohort seed 40: two pieces within the web's 30 ft join reach but not touching; the network rule at the ink tolerance
    dropped them and stranded two farmhouses. Settled, they are joined and kept."""
    s = _S([CONN, [(0.0, 0.0), (0.0, 400.0)], [(200.0, 200.0), (25.0, 200.0)], [(200.0, 200.0), (200.0, 350.0)]])
    assert settle.STEPS.index(settle.settle_joins) < settle.STEPS.index(settle.settle_network)
    settle.settle_joins(s)
    assert settle.settle_network(s) == 0
    assert len(s.M["lanes"]) == 4 and law.lane_networks(s.M) == 1


def test_a_fragment_is_dropped_and_a_chain_takes_one_width() -> None:
    s = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 150.0), (10.0, 150.0)]], meta={"ftpx": 1.0, "generated_by": "hamletgen"})
    assert settle.settle_fragments(s) == 1 and len(s.M["lanes"]) == 2
    assert settle.settle_fragments(s) == 0
    # HOMES H40 ON THE TREE (R9: Kashikawa's lane 17, Mizuguchi's lane 11): a short access corridor to a house another lane
    # already reaches earns nothing and goes like any lane; one that is the house's only way stays
    tree = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 150.0), (10.0, 150.0)]], houses=[(40.0, 150.0)], meta={"ftpx": 1.0, "generated_by": "hamletgen"})
    tree.M["lanes"][2].update(role=co.ACCESS_ROLE, of=[40.0, 150.0])
    assert law.short_fragments(tree.M) == [2] and settle.settle_fragments(tree) == 1 and len(tree.M["lanes"]) == 2
    only = _S([CONN, [(0.0, 0.0), (0.0, 300.0)], [(0.0, 150.0), (20.0, 150.0)]], houses=[(115.0, 150.0)], meta={"ftpx": 1.0, "generated_by": "hamletgen"})
    only.M["lanes"][2].update(role=co.ACCESS_ROLE, of=[115.0, 150.0])
    assert law.unreached_houses(only.M) == [] and settle.settle_fragments(only) == 0, "the house's only way earns its place"
    w = _S([CONN, ([(0.0, 5.0), (100.0, 5.0)], {"w": 6}), ([(100.0, 5.0), (200.0, 15.0)], {"w": 3})])
    assert settle.settle_widths(w) == 1 and law.width_steps(w.M["lanes"]) == []
    assert {ln["w"] for ln in w.M["lanes"][1:]} == {6}, "the way takes its widest member's width"
    tight = _S([CONN, ([(0.0, 5.0), (100.0, 5.0)], {"w": 6}), ([(100.0, 5.0), (200.0, 5.0)], {"w": 3})], houses=[(150.0, 23.0)])  # its wall 4 ft off
    settle.settle_widths(tight)
    assert {ln["w"] for ln in tight.M["lanes"][1:]} == {3}, "widened, it would foul the farmhouse beside it: the narrowest"
    assert settle.settle_widths(_S([CONN])) == 0


def test_a_width_change_redraws_the_ink() -> None:
    from l7r.diagram.settlement import Settlement

    s = Settlement(600, 600, seed=1)
    s.meta(name="W", scale="hamlet", ftpx=1, down_deg=90)
    s.lane([(0.0, 5.0), (100.0, 5.0)], width=6, worn=True)
    old = list(s._lane_ink[0])
    settle.rewidth(s, 0, 3.0)
    assert s.M["lanes"][0]["w"] == 3.0 and s._lane_ink[0] != old
    assert all(not s.ground[z].get(part) for z in old for part in ("edge", "bed", "top")), "the old ink is blanked"


# ---- step 4: the reach the web owes, drawn as tree lanes (ways W01, W03, homes H36) ----------------------------------------


_GEN = {"ftpx": 1.0, "generated_by": "hamletgen"}


def test_a_stranded_house_is_reached_along_its_corridor_and_the_tree_is_never_cut() -> None:
    """Ways W01: the house the web left 360 ft off is served by the tree lanes the seating judged - its corridor from its
    door to the exit strip, and the strip from there to the connector's start (`tree.settle_tree`) - and a settle round
    after cuts nothing of them (`corridors.is_tree`)."""
    s = _S([CONN], houses=[(300.0, 200.0)], meta=dict(_GEN), access_exit=[[400.0, 0.0], [0.0, 0.0]], access_corridors=[{"pts": [[300.0, 180.0], [300.0, 0.0]], "of": [300.0, 200.0]}])
    s.M["houses"][0]["rot"] = 180.0  # the front faces the strip: the door is in the dooryard
    assert law.unreached_houses(s.M)
    got = settle.settle_the_web(s)
    assert got["unreached_before"] == 1 and got["unreached_after"] == 0 and law.unreached_houses(s.M) == []
    assert [(ln.get("role"), ln.get("of")) for ln in s.M["lanes"][1:]] == [("exit strip", None), ("access", [300.0, 200.0])]
    assert _pts(s, 1) == [(300.0, 0.0), (0.0, 0.0)], "the strip from the corridor's end to the connector's start"
    assert not law.violations(s.M)
    assert settle.settle_the_web(s)["changed"] == 0, "the tree lanes keep the law, so nothing is left to repair"
    assert settle.settle_reach(s) == 0, "nothing owed, nothing drawn"


def test_a_way_target_gets_its_spur() -> None:
    """Homes H36 (a path runs to the graves): the connector alone does not reach the burial ground's edge, so the settle lays
    the shortest lawful spur to it - a tree lane, drawn once."""
    meta = {**_GEN, "way_targets": [{"kind": "burial ground", "at": [-300.0, 80.0]}]}
    s = _S([CONN], meta=meta)
    assert law.unreached_targets(s.M) == [(-300.0, 80.0)]
    settle.settle_the_web(s)
    assert law.unreached_targets(s.M) == [] and [ln.get("role") for ln in s.M["lanes"]].count("way target") == 1
    assert settle.settle_targets(s, settle.Lawful(s)) == 0, "drawn once"


def test_the_field_corridor_the_seating_reserved_is_the_field_way() -> None:
    """Ways W03: the field's corridor the seating reserved (`access_corridors` legs marked `field`, from the bund toward the
    tree) is drawn as the field way where no way reaches the field - over the brook at its ford, on to the bund - with the
    strip it hangs from; the field is reached by construction. Without a reservation nothing is drawn: the seating refuses
    a margin with no lawful field corridor (`homesteads.stages.reserve_field_corridor`)."""
    field = [[200.0, -300.0], [500.0, -300.0], [500.0, 300.0], [200.0, 300.0]]
    legs = [[[195.0, 150.0], [112.0, 150.0]], [[112.0, 150.0], [88.0, 150.0]], [[88.0, 150.0], [0.0, 150.0]]]
    meta = {**_GEN, "brook_fords": [[100.0, 150.0]]}
    for reserved in (True, False):
        s = _S([_c((0.0, 300.0), (0.0, 1000.0))], meta=dict(meta), streams=[BROOK], fields=[{"outline": field}])
        s.M["access_exit"] = [[0.0, 0.0], [0.0, 300.0]]
        s.M["access_corridors"] = [{"pts": p, "field": True} for p in legs] if reserved else []
        assert law.field_unreached(s.M)
        settle.settle_the_web(s)
        assert law.field_unreached(s.M) is not reserved
        if reserved:
            roles = {ln.get("role"): _pts(s, i) for i, ln in enumerate(s.M["lanes"])}
            assert [round(v) for v in roles["field way"][0]] == [195, 150] and roles["exit strip"] == [(0.0, 150.0), (0.0, 300.0)]


def test_a_target_no_lawful_run_reaches_is_left_unreached_not_drawn_least_bad(monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-005: with no spur to a way target keeping the law, nothing is drawn - the report says what is still owed."""
    meta = {**_GEN, "way_targets": [{"kind": "burial ground", "at": [-300.0, 80.0]}]}
    s = _S([CONN], meta=meta)
    monkeypatch.setattr(settle.Lawful, "__call__", lambda self, run, width, skip=None: False)
    got = settle.settle_the_web(s)
    assert got["targets_unreached"] == 1
    assert not any(ln.get("role") == "way target" for ln in s.M["lanes"])


def test_an_end_behind_a_house_is_carried_round_the_gable_or_cut() -> None:
    """Water W57: a lane ending 26 ft behind a farmhouse's back wall has not reached it. Carried round the nearer gable into
    the dooryard band where that keeps the law; where it would not (another house on the gable), its last leg goes."""
    from l7r.diagram.settlement.water_ways.lanes import reaches_dooryard

    lane = [(-100.0, 0.0), (-100.0, 100.0), (-100.0, 160.0)]
    s = _S([CONN, lane], houses=[(-100.0, 200.0)])
    assert law.ends_behind(s.M) == [(1, -1, 0)]
    settle.settle_ends(s)
    assert law.ends_behind(s.M) == [] and reaches_dooryard(s.M["houses"][0], _pts(s, 1)[-1])
    walled = [(-100.0, 200.0), (-60.0, 200.0), (-140.0, 200.0)]  # a house on either gable: no carry keeps the law
    blocked = _S([CONN, lane], houses=walled)
    settle.settle_ends(blocked)
    cut = _pts(blocked, 1)
    assert law.ends_behind(blocked.M) == [] and cut[:2] == lane[:2] and math.dist(cut[-1], (-100.0, 200.0)) > 60.0, "taken back only off the back"
    junction = _S([CONN, lane, [(-130.0, 150.0), (-100.0, 150.0)]], houses=walled)
    settle.settle_ends(junction)
    assert math.dist(_pts(junction, 1)[-1], (-100.0, 150.0)) <= law.JOIN_TOL, "no further than its last junction: the way that joins it keeps it"
    behind = _S([CONN, [(-100.0, 170.0), (-100.0, 180.0)]], houses=walled)
    settle.settle_ends(behind)
    assert len(behind.M["lanes"]) == 1, "a lane standing wholly behind the house goes"


def test_a_needle_of_grass_is_opened_on_its_shorter_lane() -> None:
    """Homes H39 (future-work 2c): two ways forking and rejoining round a sliver of ground - the shorter lane loses its
    stretch along the needle, and no loop that thin is left."""
    s = _S([CONN, [(-300.0, 0.0), (-250.0, 110.0), (-250.0, 200.0)], [(-280.0, 0.0), (-250.0, 110.0)]])
    assert law.needle_loops(s.M)
    assert settle.settle_needles(s) == 1
    assert law.needle_loops(s.M) == [] and polyline(_pts(s, 1)) > 200.0, "the longer way stands"
    tree = _S([CONN, ([(-300.0, 0.0), (-250.0, 110.0)], {}), ([(-280.0, 0.0), (-250.0, 110.0)], {})])
    for ln in tree.M["lanes"][1:]:
        ln["role"] = "access"
    assert settle.settle_needles(tree) == 0, "a needle bounded by the tree alone is the tree's"


def polyline(p):
    return sum(math.dist(a, b) for a, b in zip(p, p[1:], strict=False))


def test_lawful_refuses_each_rule_a_new_tree_lane_would_break() -> None:
    """`Lawful`: the one question asked before a tree lane is laid, since it is never cut afterwards."""
    s = _S(
        [CONN, [(-500.0, 0.0), (-500.0, 300.0)]], houses=[(-300.0, 300.0), (-460.0, 300.0)], streams=[BROOK], fields=[{"outline": [[-800.0, 400.0], [-700.0, 400.0], [-700.0, 500.0], [-800.0, 500.0]]}]
    )
    s.M["threshing_yards"] = [{"poly": [[-320.0, 100.0], [-280.0, 100.0], [-280.0, 120.0], [-320.0, 120.0]], "of": [-300.0, 300.0]}]
    ok = settle.Lawful(s)
    assert ok([(-240.0, 0.0), (-250.0, 290.0)], 3.0), "a clean spur off the connector, to a house"
    assert not ok([(-100.0, 0.0), (-100.0, 150.0)], 3.0), "a spur to nothing: its end dangles"
    assert not ok([(-100.0, 0.0)], 3.0) and not ok([(-100.0, 0.0), (-100.0, 150.0), (-90.0, 20.0)], 3.0), "too short; doubled back"
    assert not ok([(0.0, 50.0), (200.0, 50.0)], 3.0), "over the brook off any ford"
    assert not ok([(-300.0, 0.0), (-300.0, 160.0)], 3.0), "through a neighbor's threshing yard"
    assert not ok([(-750.0, 0.0), (-750.0, 450.0)], 3.0), "into the field"
    assert not ok([(-490.0, 0.0), (-490.0, 290.0)], 3.0), "doubling a way along its whole run"
    assert ok([(-500.0, 0.0), (-500.0, 300.0)], 3.0, skip=1), "the lane it would replace is not asked to meet it"
    assert not ok([(-340.0, 100.0), (-340.0, 250.0), (-300.0, 295.0)], 3.0), "into a house"
    quad = [(0.0, 0.0), (40.0, 0.0), (40.0, 28.0), (0.0, 28.0)]
    assert co.through_a_building([(20.0, -10.0), (20.0, 40.0)], [quad]), "clean through between the corners"
    assert co.through_a_building([(20.0, -10.0), (20.0, 10.0)], [quad]) and not co.through_a_building([(50.0, -10.0), (50.0, 40.0)], [quad])


def test_the_tree_is_left_alone_at_a_fold_and_behind_a_house_and_a_target_is_drawn_to_once() -> None:
    """The tree lanes (`corridors.is_tree`) are never the lane a repair edits: two folded on each other are left, a tree
    lane ending behind a house is the corridor pass's to carry, and a target whose spur is drawn is not drawn to again."""
    folded = _S([CONN, [(-100.0, 0.0), (-100.0, 100.0)], [(-100.0, 100.0), (-95.0, 20.0)]])
    for ln in folded.M["lanes"][1:]:
        ln["role"] = "access"
    assert law.folded_joint_pairs(folded.M["lanes"]) and settle.settle_ends(folded) == 0
    behind = _S([CONN, [(-100.0, 0.0), (-100.0, 100.0), (-100.0, 160.0)]], houses=[(-100.0, 200.0)])
    behind.M["lanes"][1]["role"] = "access"
    assert law.ends_behind(behind.M) and settle.settle_ends(behind) == 0
    drawn = _S([CONN, ([(-600.0, 0.0), (-600.0, 50.0)], {})], meta={**_GEN, "way_targets": [{"at": [-300.0, 80.0]}]})
    drawn.M["lanes"][1].update({"role": "way target", "to": [-300.0, 80.0]})
    assert settle.settle_targets(drawn, settle.Lawful(drawn)) == 0


def test_lawful_refuses_a_needle_or_a_hairpin_at_the_connectors_start() -> None:
    s = _S([CONN])
    ok = settle.Lawful(s)
    assert not ok([(-200.0, 30.0), (-100.0, 0.5)], 3.0), "meets the connector at a needle's angle"
    assert not ok([(-60.0, 10.0), (-5.0, 10.0), (0.0, 0.0)], 3.0), "doubles back over a short leg at the connector's start"


def test_a_field_way_no_straight_run_keeps_is_threaded_round_the_steadings() -> None:
    """Ways W03, cohort seed 13: every straight run from the network to the bund passed through a steading, so the field's
    corridor the seating reserves is threaded by the web's router (`field_router`, `routed_field_runs`) round it."""
    from l7r.diagram.hamletgen.ways.bund import BRANCH_WIDTH
    from l7r.diagram.hamletgen.ways.geom import WorkedGround

    field = [[300.0, -300.0], [500.0, -300.0], [500.0, 300.0], [300.0, 300.0]]
    far_brook = {"poly": [[1000.0, -500.0], [1000.0, 500.0]], "w": 6.0}
    s = _S([_c((0.0, 0.0), (-1000.0, 0.0))], houses=[(150.0, 0.0)], meta=dict(_GEN), streams=[far_brook], fields=[{"outline": field}])
    s.M["houses"][0].update({"w": 60.0, "h": 200.0})
    ground = WorkedGround([[(float(a), float(b)) for a, b in field]])
    runs = co.routed_field_runs([((0.0, 0.0), (-100.0, 0.0))], ground, BRANCH_WIDTH / 2.0, co.field_router(s, [(1000.0, -500.0), (1000.0, 500.0)]))
    assert runs and len(runs[0]) > 2 and not co.through_a_building(runs[0], co.building_quads(s.M)), "threaded round the house"


def test_a_repair_that_would_split_the_web_is_known_before_it_is_made() -> None:
    """`keeps_the_network` (cohort seed 31: a backbone's end carried round a gable took the tread three lanes stood on and
    nine fell off the network), asked of the web as this round's earlier repairs leave it (`with_edits`)."""
    s = _S([CONN, [(0.0, 0.0), (0.0, 200.0)], [(-100.0, 200.0), (100.0, 200.0)]])
    assert settle.keeps_the_network(s.M, 1, [[(0.0, 0.0), (10.0, 100.0), (0.0, 200.0)]]), "the junction kept: nothing hangs"
    assert not settle.keeps_the_network(s.M, 1, [[(0.0, 0.0), (0.0, 150.0)]]), "cut short of it: the cross lane falls off"
    work = settle.with_edits(s.M, {1: [[(0.0, 0.0), (0.0, 150.0)], [(5.0, 5.0), (5.0, 9.0)]], 2: []})
    assert [ln["pts"] for ln in work["lanes"]][1:] == [[[0.0, 0.0], [0.0, 150.0]], [], [[5.0, 5.0], [5.0, 9.0]]]


def test_a_lane_over_a_fixture_is_cut_and_no_tree_lane_is_laid_over_one() -> None:
    s = _S([CONN, [(-100.0, 0.0), (-100.0, 200.0)]], farm_fixtures=[{"kind": "manure", "x": -100.0, "y": 100.0, "w": 8.0, "h": 6.0, "rot": 0.0}])
    assert law.lanes_over_fixtures(s.M) == [(1, 0)]
    settle.settle_shapes(s)
    assert law.lanes_over_fixtures(s.M) == [], "the leg over the heap is cut"
    assert not settle.Lawful(s)([(-200.0, 0.0), (-100.0, 100.0)], 3.0)


def test_a_lane_through_a_yard_persimmons_trunk_is_cut_and_no_tree_lane_is_laid_through_one() -> None:
    """Feature 287, homes H43 (`test_no_tree_is_planted_in_a_path`; cohort seed 42 laid a straggler through a neighbor's
    persimmon, seated with its household before the web): the trunk is a fixture quad, so the leg through it is cut and a
    tree lane through it refused - a lane under the crown, clear of the trunk, is let stand."""
    from l7r.diagram.settlement.homestead_parts.stands import trunk_on_tread

    s = _S([CONN, [(-100.0, 0.0), (-100.0, 200.0)], [(-140.0, 0.0), (-140.0, 200.0)]], persimmons=[{"x": -100.0, "y": 100.0, "r": 11.5}, {"x": -150.0, "y": 100.0, "r": 11.5}])
    assert law.lanes_over_fixtures(s.M) == [(1, 0)] and trunk_on_tread(-100.0, 100.0, s.M["lanes"][1:2])
    settle.settle_shapes(s)
    assert law.lanes_over_fixtures(s.M) == [] and not any(trunk_on_tread(-100.0, 100.0, [ln]) for ln in s.M["lanes"])
    assert [(-140.0, 0.0), (-140.0, 200.0)] in [_pts(s, i) for i in range(len(s.M["lanes"]))], "under the other crown, 10 ft off its trunk: kept"
    assert not settle.Lawful(s)([(-200.0, 100.0), (-50.0, 100.0)], 3.0)


def test_seed_8_a_corridor_over_the_brook_at_its_ford_is_squared_and_drawn() -> None:
    """Cohort seed 8 (the coarse-grain knob reseated the cluster): the exit strip ran from the houses over the brook to the
    connector's start 38 degrees off square at a ford, the corridor was judged unsquared, refused, and three houses were
    stranded. The web squares a tree lane at its crossings (`square_run`) before it asks the law, as it squares every lane."""
    brook = {"poly": [[100.0, -500.0], [100.0, 500.0]], "w": 7.0}
    s = _S(
        [_c((0.0, -150.0), (-1000.0, -150.0))],
        houses=[(300.0, 200.0)],
        meta={**_GEN, "brook_fords": [[100.0, -73.3]]},
        streams=[brook],
        access_exit=[[300.0, 80.0], [0.0, -150.0]],
        access_corridors=[{"pts": [[300.0, 180.0], [300.0, 80.0]], "of": [300.0, 200.0]}],
    )
    s.M["houses"][0]["rot"] = 180.0
    assert not settle.Lawful(s).on_lawful_ground([(300.0, 80.0), (0.0, -150.0)], 3.0), "unsquared, the strip crosses 38 degrees off"
    assert settle.corridor_on_lawful_ground(s.M, [(300.0, 80.0), (0.0, -150.0)]), "squared, the seating's own question admits it"
    settle.settle_the_web(s)
    assert law.unreached_houses(s.M) == [] and law.oblique_crossings(s.M) == [] and law.off_ford_crossings(s.M) == []
    assert [ln["role"] for ln in s.M["lanes"] if ln.get("role")] == ["exit strip", "access"]


def _reference_lawful_ground(ok: settle.Lawful, run, width) -> bool:
    """`Lawful.on_lawful_ground` as it read before the ground was indexed: every registry walked whole."""
    if len(run) < 2 or law.hooked(run) or settle.kink_spans(run):
        return False
    if settle._crossing_fault({**ok.M, "lanes": [{"pts": settle._rounded(run), "w": width}]}, 0, run, ok.wet) is not None:
        return False
    rings = settle.open_ground_rings(ok.M)
    crossed = any(segments_cross(p, q, r[k], r[(k + 1) % len(r)]) for p, q in zip(run, run[1:], strict=False) for r in rings for k in range(len(r)))
    return settle.fouled_segment(run, width, ok.houses, ok.yards, ok.solid, ok.fixtures) is None and not crossed and not co.through_a_building(run, ok.buildings)


def test_the_indexed_lawful_ground_answers_as_the_whole_registries_do() -> None:
    """The ground half of the law reads an index built once (`corridors.GroundIndex`, dev/performance.md): it only prunes, so
    over runs that cross the brook, a channel, a field, a dry plot and a marsh, pass a house, a yard, a byre and a fixture,
    each near and far, it gives the verdict every registry walked whole gives - and some of each."""
    import random

    s = _S(
        [CONN],
        houses=[(-300.0, 300.0), (-460.0, 300.0), (400.0, 200.0)],
        streams=[BROOK],
        drawn_channels=[{"pts": [[-900.0, 600.0], [900.0, 650.0]], "w0": 4.0}],
        fields=[{"outline": [[-800.0, 400.0], [-700.0, 400.0], [-700.0, 500.0], [-800.0, 500.0]]}],
        dry_plots=[{"poly": [[300.0, -300.0], [360.0, -300.0], [360.0, -240.0], [300.0, -240.0]]}],
        marshes=[{"poly": [[-200.0, -400.0], [-100.0, -400.0], [-150.0, -300.0]]}, {"poly": [[500.0, 500.0], [560.0, 500.0], [530.0, 560.0]], "role": "defense"}],
        byres=[{"x": 200.0, "y": 300.0, "w": 30.0, "h": 20.0}],
        farm_fixtures=[{"x": -250.0, "y": 200.0, "w": 8.0, "h": 8.0}],
    )
    s.M["meta"]["brook_fords"] = [[100.0, 100.0]]
    s.M["threshing_yards"] = [{"poly": [[-320.0, 100.0], [-280.0, 100.0], [-280.0, 120.0], [-320.0, 120.0]], "of": [-300.0, 300.0]}]
    ok = settle.Lawful(s)
    rng = random.Random(7)
    verdicts = []
    for _ in range(400):
        run = [(rng.uniform(-900.0, 900.0), rng.uniform(-600.0, 700.0))]
        for _leg in range(rng.choice((1, 1, 2))):
            run.append((run[-1][0] + rng.uniform(-300.0, 300.0), run[-1][1] + rng.uniform(-300.0, 300.0)))
        want = _reference_lawful_ground(ok, run, 3.0)
        assert ok.on_lawful_ground(run, 3.0) == want, run
        verdicts.append(want)
    assert 40 < sum(verdicts) < 360, "the runs drawn are admitted and refused both"
    assert ok.index is ok.index, "built once"


def test_a_run_is_squared_only_where_water_comes_within_the_squaring_reach() -> None:
    """`Lawful.squared` is `square_run` where water comes near the run, and the run itself where none does - where the
    squaring would change nothing."""
    s = _S([CONN], streams=[BROOK])
    ok = settle.Lawful(s)
    across = [(40.0, 100.0), (160.0, 160.0)]
    assert ok.squared(across) == settle.square_run(s.M, across) != across, "an oblique crossing is squared"
    far = [(300.0, 100.0), (320.0, 160.0), (400.0, 170.0)]
    assert ok.squared(far) == settle.square_run(s.M, far) == far


def test_an_ordinary_join_that_would_break_a_rule_against_the_tree_is_taken_back_instead(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287 wave 6 (cohort seed 25 under the probes): a join closed onto the tree that the deference then cut again took
    turns with it until the rounds ran out - so an ordinary lane whose join would break a rule against a tree lane
    (`tree.tree_faults`) is taken back out of the join's reach instead; a tree lane's own join is made."""
    s = _S([CONN, [(-100.0, 0.0), (-100.0, 170.0)], [(-200.0, 200.0), (0.0, 200.0)]])
    assert [i for i, _e, _f in law.near_misses(s.M)] == [1]
    monkeypatch.setattr(settle, "tree_faults", lambda M: [(1, (-100.0, 200.0))] if len(M["lanes"][1]["pts"]) > 2 else [])
    assert settle.settle_joins(s) == 1
    got = _pts(s, 1)
    assert got[0] == (-100.0, 0.0) and got[-1][1] == pytest.approx(170.0 - law.JOIN_REACH_FT - settle.JOIN_BACK_PAD_FT), "taken back"
    t = _S([CONN, ([(-100.0, 0.0), (-100.0, 170.0)], {}), [(-200.0, 200.0), (0.0, 200.0)]])
    t.M["lanes"][1]["role"] = co.ACCESS_ROLE
    assert settle.settle_joins(t) == 1 and _pts(t, 1)[-1] == (-100.0, 200.0), "a tree lane joins"


def test_a_house_crowded_with_ends_keeps_the_trees_and_loses_an_ordinary_one() -> None:
    """Homes H41 under the tree (feature 287 wave 6): a house discharging three free ends keeps the tree lane's - never cut -
    and the settle cuts the ordinary end that is farther than the nearer ordinary one; a violator the tree names is an
    ordinary lane (`lane_violators` reads `tree.tree_faults`)."""
    s = _S([CONN, [(-300.0, 40.0), (-300.0, 170.0)], [(-200.0, 60.0), (-240.0, 180.0)], [(-400.0, 60.0), (-360.0, 190.0)]], houses=[(-300.0, 200.0)])
    s.M["lanes"][3]["role"] = co.ACCESS_ROLE
    assert len(law.fronting_ends(s.M)[0]) == 3
    settle.settle_ends(s)
    tree = [[tuple(q) for q in ln["pts"]] for ln in s.M["lanes"] if ln.get("role") == co.ACCESS_ROLE]
    assert tree == [[(-400.0, 60.0), (-360.0, 190.0)]], "the tree lane stands"
    assert len(s.M["lanes"]) < 4 or _pts(s, 1) != [(-300.0, 40.0), (-300.0, 170.0)] or _pts(s, 2) != [(-200.0, 60.0), (-240.0, 180.0)], "an ordinary end cut"
    assert len(law.fronting_ends(s.M).get(0, [])) <= law.DOORSTEP_MAX


def test_the_last_resort_names_an_ordinary_lane_the_tree_faults(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _S([CONN, [(-100.0, 0.0), (-100.0, 170.0)]])
    s.M["lanes"].append({"pts": [[-50.0, 0.0], [-50.0, 100.0]], "w": 3, "role": co.ACCESS_ROLE})
    monkeypatch.setattr(settle, "tree_faults", lambda M: [(1, (0.0, 0.0)), (2, (0.0, 0.0))])
    assert settle.lane_violators(s) == [1], "the ordinary lane, never the tree's"
