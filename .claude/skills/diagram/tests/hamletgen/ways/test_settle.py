"""`hamletgen/ways/settle.py`: the web settles itself (feature 287, M4) - each rule of the lane law, provoked on constructed
lanes, is repaired by `settle_the_web` and asked again of the same predicate the finished-map tests read."""

import math

import pytest

from l7r.diagram.hamletgen.ways import law, settle


class _S:
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


def test_a_cut_that_strands_a_house_or_the_field_redraws_the_reach_once() -> None:
    """Until the access corridor (M3) serves them, a farmhouse or the field left without a way by a settling cut is served
    by drawing the stragglers and the field path again, and the web settled once more."""
    calls = []
    kept = _S([CONN, [(0.0, 2.0), (0.0, 100.0)]], houses=[(40.0, 110.0)])
    assert "redrawn" not in settle.settle_and_redraw(kept, lambda: calls.append(1)) and calls == []
    # a house served only past a lattice step: the settle cuts the kink out, the far piece falls off the network and the
    # house is stranded, so the reach is redrawn
    lost = _S([CONN, [(0.0, 2.0), (0.0, 200.0), (100.0, 200.0), (100.0, 220.0), (200.0, 220.0)]], houses=[(120.0, 170.0), (230.0, 240.0)], meta={"ftpx": 1.0, "generated_by": "hamletgen"})

    def redraw() -> None:
        calls.append(1)
        lost.lane([(100.0, 200.0), (215.0, 200.0)], width=3)

    got = settle.settle_and_redraw(lost, redraw)
    assert calls == [1] and got["redrawn"] and got["unreached_after"] == 0 and got["unreached_before"] == 0


def test_the_web_stage_redraws_the_reach_through_the_straggler_and_field_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.hamletgen.ways import web

    seen = []
    monkeypatch.setattr(web, "_serve_stragglers", lambda *a: seen.append("stragglers"))
    monkeypatch.setattr(web, "a_way_onto_the_bund", lambda s: "run_on")
    s = _S([CONN])
    web.redraw_the_reach(s, None, [], [], [])
    assert seen == ["stragglers"] and s.M["meta"]["field_path"] == "run_on"
