"""`hamletgen/ways/law.py`: every lane rule as one predicate (feature 287, M1) - each asked of a constructed lane that keeps
the rule and of one that breaks it."""

import math

from l7r.diagram.hamletgen.ways import law


def _lane(*pts, **kw):
    return {"pts": [list(p) for p in pts], **kw}


def _house(x, y, w=40.0, h=30.0):
    return {"x": x, "y": y, "w": w, "h": h, "rot": 0.0}


BROOK = {"poly": [[100.0, -500.0], [100.0, 500.0]], "w": 6.0}


# ---- a lane's own shape --------------------------------------------------------------------------------------------


def test_a_straight_lane_bends_like_a_path() -> None:
    assert law.kinks([(0.0, 0.0), (100.0, 0.0), (200.0, 10.0)]) == []
    assert law.kinks([(0.0, 0.0), (100.0, 0.0)]) == [], "two points cannot bend"
    assert not law.bends_badly([(0.0, 0.0), (0.0, 0.0), (100.0, 0.0)]), "a zero-length leg is no turn"


def test_a_lane_that_doubles_back_or_kinks_does_not() -> None:
    assert law.kinks([(0.0, 0.0), (100.0, 0.0), (0.0, 5.0)]) == [("doubles back", 100, 0)]
    assert law.kinks([(0.0, 0.0), (100.0, 0.0), (100.0, 20.0), (200.0, 20.0)]) == [("kinks", 100, 0)], "two 90 degree turns 20 ft apart"
    assert law.bends_badly([(0.0, 0.0), (100.0, 0.0), (100.0, 20.0), (200.0, 20.0)])


def test_two_turns_a_run_apart_are_a_bend_not_a_kink() -> None:
    # the WHOLE run between the turns is summed: two 90 degree turns 100 ft apart bend, and two 30 ft legs do not make a
    # 60 ft run read as 30 (the one-segment reading `clearance._bends_badly` takes)
    assert law.kinks([(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (200.0, 100.0)]) == []
    assert law.kinks([(0.0, 0.0), (100.0, 0.0), (100.0, 20.0), (110.0, 20.0), (110.0, 40.0)]) != []


def test_the_bend_rule_skips_the_connector() -> None:
    kinked = [(0.0, 0.0), (100.0, 0.0), (0.0, 5.0)]
    assert law.lanes_that_kink({"lanes": [_lane(*kinked, connector=True)]}) == []
    assert law.lanes_that_kink({"lanes": [_lane(*kinked)]}) == [("doubles back", 100, 0)]


def test_a_hook_at_either_end_is_found_on_every_lane() -> None:
    hooked = [(0.0, 0.0), (100.0, 0.0), (95.0, 8.0)]
    assert law.hooks(hooked) == [(100, 0)]
    assert law.hooks(hooked[::-1]) == [(100, 0)], "the first leg is asked too"
    assert law.hooks([(0.0, 0.0), (100.0, 0.0), (80.0, 40.0)]) == [], "a long last leg is a turn, not a hook"
    assert law.hooks([(0.0, 0.0), (100.0, 0.0)]) == []
    assert law.hooked_ends({"lanes": [_lane(*hooked, connector=True)]}) == [(100, 0)], "the connector is asked too"


def test_a_husk_draws_nothing() -> None:
    M = {"lanes": [_lane((0.0, 0.0)), _lane((5.0, 5.0), (5.0, 5.0), (5.2, 5.0)), _lane((0.0, 0.0), (10.0, 0.0))]}
    assert law.husks(M) == [0, 1]


# ---- where lanes meet ----------------------------------------------------------------------------------------------


def test_two_lanes_meeting_end_to_end_in_a_fold() -> None:
    folded = [_lane((0.0, 0.0), (100.0, 0.0)), _lane((100.0, 0.0), (10.0, 5.0))]
    straight = [_lane((0.0, 0.0), (100.0, 0.0)), _lane((100.0, 0.0), (200.0, 10.0))]
    assert law.folded_joints(folded) == [(100, 0)]
    assert law.folded_joints(straight) == []


def test_a_lane_doubling_back_beside_the_connectors_start() -> None:
    conn = _lane((0.0, 0.0), (100.0, 0.0), connector=True)
    from_east = _lane((60.0, 15.0), (10.0, 15.0), (0.0, 0.0))  # runs west past the start and turns back onto it
    from_west = _lane((-60.0, 15.0), (-10.0, 15.0), (0.0, 0.0))  # arrives and carries on
    assert law.connector_hairpins([conn, from_east]) == [(0, 0)]
    assert law.connector_hairpins([conn, from_west, _lane((5.0, 5.0), (9.0, 9.0)), _lane((0.0, 0.0), connector=True)]) == []


def test_a_needle_join_runs_back_along_the_tread() -> None:
    tread = _lane((0.0, 0.0), (200.0, 0.0))
    needle = _lane((20.0, 60.0), (60.0, 8.0), (100.0, 0.0))  # the last 41 ft at 11 degrees to the tread
    tee = _lane((100.0, 60.0), (100.0, 0.0))
    carry_on = _lane((200.0, 0.0), (300.0, 0.0))  # starts at the tread's END and runs on: no tread beside it
    stub = _lane((90.0, 2.0), (100.0, 0.0))  # a leg this short is the approach to the junction
    assert law.needle_joins([tread, needle]) == [(100, 0)]
    assert law.needle_joins([tread, tee, carry_on, stub, _lane((5.0, 5.0)), _lane((0.0, 0.0), (0.0, 0.0), connector=True)]) == []


def test_a_zero_length_tread_runs_nowhere() -> None:
    assert law._tread_bearings((1.0, 1.0), (0.0, 0.0), (0.0, 0.0)) == []


def test_a_tail_run_on_beside_another_way_is_doubled() -> None:
    doubled = {"lanes": [_lane((0.0, 0.0), (100.0, 0.0), (140.0, 2.0)), _lane((100.0, 5.0), (300.0, 5.0), connector=True)]}
    clear = {"lanes": [_lane((0.0, 0.0), (100.0, 0.0), (100.0, 4.0)), _lane((0.0, 200.0), (300.0, 200.0)), _lane((5.0, 5.0))]}
    assert law.doubled_tails(doubled) == [0]
    assert law.doubled_tails(clear) == []


def test_the_lanes_are_one_network_at_the_ink_tolerance() -> None:
    joined = {"lanes": [_lane((0.0, 0.0), (100.0, 0.0)), _lane((50.0, 3.0), (50.0, 100.0)), _lane((1.0, 1.0))]}
    apart = {"lanes": [_lane((0.0, 0.0), (100.0, 0.0)), _lane((50.0, 6.0), (50.0, 100.0))]}
    assert law.lane_networks(joined) == 1
    assert law.lane_networks(apart) == 2


# ---- where lanes end -----------------------------------------------------------------------------------------------


def test_a_lane_end_in_open_ground_dangles() -> None:
    conn = _lane((0.0, 0.0), (100.0, 0.0), connector=True)
    M = {"lanes": [conn, _lane((50.0, 0.0), (50.0, 300.0))], "houses": []}
    assert law.dangling_ends(M) == [(50, 300)]
    M["houses"] = [_house(50.0, 330.0)]
    assert law.dangling_ends(M) == [], "the far end arrives at a farmhouse"


def test_an_end_served_only_by_the_way_it_left_dangles() -> None:
    # 40 ft off the connector, inside the 60 ft reach - but the connector is the way the lane's own far end stands on
    conn = _lane((0.0, 0.0), (100.0, 0.0), connector=True)
    M = {"lanes": [conn, _lane((50.0, 0.0), (50.0, 40.0)), _lane((5.0, 5.0))], "houses": []}
    assert law.dangling_ends(M) == [(50, 40)]


def test_a_farmhouse_discharges_two_lane_ends_not_three() -> None:
    three = [_lane((20.0, 0.0), (300.0, 0.0)), _lane((0.0, 20.0), (0.0, 300.0)), _lane((-20.0, 0.0), (-300.0, 0.0))]
    M = {"lanes": three, "houses": [_house(0.0, 0.0)]}
    assert law.fronted_ends(M) == {0: 3}
    assert law.doorstep_ends(M) == {0: 3}
    two = [*three[:2], _lane((-20.0, 0.0), (-300.0, 0.0), connector=True), _lane((1.0, 1.0)), _lane((300.0, 2.0), (400.0, 2.0))]
    assert law.doorstep_ends({"lanes": two, "houses": [_house(0.0, 0.0)]}) == {}, "a junction discharges an end, and the connector's ends are not counted"
    assert law.fronted_ends({"lanes": three, "houses": []}) == {}


def test_a_way_reaches_the_field_on_a_brook_map() -> None:
    field = {"outline": [[200.0, 0.0], [400.0, 0.0], [400.0, 200.0], [200.0, 200.0]]}
    near = {"streams": [BROOK], "fields": [field], "dry_plots": [{"poly": [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]}], "lanes": [_lane((150.0, 50.0), (170.0, 50.0))]}
    far = {**near, "dry_plots": [], "lanes": [_lane((0.0, 500.0), (10.0, 500.0)), _lane((150.0, 50.0), (170.0, 50.0), connector=True)]}
    assert math.isclose(law.field_reach_ft(near), 30.0)
    assert not law.field_unreached(near)
    assert law.field_unreached(far), "the connector is not the hamlet's own way"
    assert not law.field_unreached({**far, "streams": []}), "without a brook the rule does not apply"
    assert law.field_reach_ft({"lanes": []}) == math.inf


# ---- the fabric ----------------------------------------------------------------------------------------------------


def test_a_lane_segment_through_a_building_breaks_the_run() -> None:
    M = {"houses": [_house(100.0, 0.0)], "byres": [{"x": 0.0, "y": 0.0}], "lanes": [_lane((0.0, 0.0), (200.0, 0.0))]}
    assert law.solid_boxes(M) == [(80.0, -15.0, 120.0, 15.0)]
    assert law.breaks_mid_run(M) == [(100, 0)]
    M["lanes"] = [_lane((0.0, 0.0), (50.0, 0.0), (50.0, 100.0), (200.0, 100.0))]
    assert law.breaks_mid_run(M) == []


def test_a_lane_fouls_a_house_or_a_neighbors_plot_but_not_its_own() -> None:
    garden = [(0.0, 50.0), (40.0, 50.0), (40.0, 90.0), (0.0, 90.0)]
    fabric = [(garden, (20.0, 150.0), "gardens"), ([(0.0, 60.0), (100.0, 60.0), (100.0, 80.0)], None, "groves")]
    run = [(-50.0, 70.0), (100.0, 70.0)]
    assert law.fouls_fabric([(0.0, 0.0), (200.0, 0.0)], 3.0, [_house(100.0, 0.0)], []), "ink on a farmhouse"
    assert law.fouls_fabric(run, 3.0, [], fabric), "through a neighbor's garden"
    assert not law.fouls_fabric(run, 3.0, [], fabric, own=(20.0, 150.0)), "a door path leaves its own steading"
    assert not law.fouls_fabric([(-50.0, 200.0), (100.0, 200.0)], 3.0, [_house(100.0, 0.0)], fabric), "a grove is not fabric here"


# ---- water ---------------------------------------------------------------------------------------------------------


def test_a_lane_crossing_the_brook_out_and_back() -> None:
    M = {"streams": [BROOK], "lanes": [_lane((0.0, 0.0), (200.0, 0.0), (200.0, 50.0), (0.0, 50.0)), _lane((0.0, 300.0), (200.0, 300.0))]}
    assert law.over_and_back(M) == [(0, 2)]
    M["lanes"] = M["lanes"][1:]
    assert law.over_and_back(M) == []


def test_a_crossing_stands_at_a_ford_within_the_one_constant() -> None:
    M = {"streams": [BROOK], "meta": {"brook_fords": [[100.0, 0.0]]}, "lanes": [_lane((0.0, 0.0), (200.0, 0.0)), _lane((0.0, 50.0), (200.0, 50.0))]}
    assert law.off_ford_crossings(M) == [(100, 50)], "50 ft from the ford is off it at FORD_HALF (30 ft)"
    assert law.off_ford_crossings(M, reach=60.0) == []
    assert law.off_ford_crossings({**M, "meta": {}}) == [(100, 0), (100, 50)], "no ford recorded: every crossing is off one"


def test_a_lane_crosses_the_brook_and_a_channel_square() -> None:
    square = _lane((0.0, 0.0), (200.0, 0.0))
    skew = _lane((0.0, 100.0), (200.0, 300.0))
    M = {"streams": [BROOK], "drawn_channels": [{"pts": [[100.0, -500.0], [100.0, 500.0]]}], "lanes": [square, skew]}
    assert law.oblique_crossings(M) == [(100, 200, 45.0)]
    assert law.oblique_crossings(M, "channel") == [(100, 200, 45.0)]
    M["lanes"] = [square]
    assert law.oblique_crossings(M) == [] and law.oblique_crossings(M, "channel") == []


def test_every_brook_crossing_is_under_a_deck() -> None:
    M = {"streams": [BROOK], "lanes": [_lane((0.0, 0.0), (200.0, 0.0))], "bridges": [{"x": 100.0, "y": 10.0, "span": 20.0}]}
    assert law.deck_covers(M["bridges"][0], 100.0, 0.0)
    assert law.unbridged_crossings(M) == []
    M["bridges"] = [{"x": 100.0, "y": 25.0}]  # no span recorded: read at the 20 ft default
    assert law.unbridged_crossings(M) == [(100, 0)]


STRAIGHT = [(0.0, -100.0), (0.0, 100.0)]
# a course that crosses the way and then runs along it 2 ft off on both sides: every corner of every deck it could seat -
# grown to 2.56 times, skewed 7 degrees toward square - stands within its 8 ft need of the water
STEPPED = [(-1000.0, 2.0), (0.0, 2.0), (0.0, -2.0), (1000.0, -2.0)]


def test_a_deck_seats_where_the_placers_own_solve_seats_one() -> None:
    way = [(-100.0, 0.0), (100.0, 0.0)]
    assert law.deck_seats(way, 3.0, [(STRAIGHT, 4.0)]) == []
    assert law.deck_seats(way, 3.0, [(STEPPED, 4.0)]) == [(0, 0)]
    M = {"meta": {"ftpx": 1.0}, "lanes": [_lane(*way, w=3)], "streams": [{"poly": [list(p) for p in STEPPED], "w": 4.0}]}
    assert law.undeckable_crossings(M) == [(0, 0)]
    M["streams"] = [{"poly": [list(p) for p in STRAIGHT], "w": 4.0}]
    assert law.undeckable_crossings(M) == []


def test_a_deck_shorter_than_its_water() -> None:
    M = {
        "streams": [{"poly": [[0.0, -100.0], [0.0, 100.0]], "w": 10.0}],
        "field_ditches": [{"poly": [[500.0, 0.0], [600.0, 0.0]], "w": 3.0}, {"poly": [[0.0, 0.0]]}],
        "channels": [{"poly": [[900.0, 0.0], [900.0, 100.0]]}],
        "bridges": [{"x": 0.0, "y": 0.0, "span": 5.0}, {"x": 0.0, "y": 50.0, "span": 30.0}, {"x": 300.0, "y": 300.0, "span": 1.0}],
    }
    assert law.short_decks(M) == [(0, 0, 5.0, 10.0)]
    assert law.short_decks({"bridges": [{"x": 0.0, "y": 0.0, "span": 5.0}]}) == [], "no course: no deck is over one"


def test_a_plank_crosses_a_supply_ditch_and_never_the_drain() -> None:
    M = {
        "field_ditches": [{"poly": [[0.0, 0.0], [100.0, 0.0]], "role": "main"}, {"poly": [[0.0, 200.0], [100.0, 200.0]], "role": "drain"}, {"poly": [[0.0, 0.0]], "role": "branch"}],
        "bridges": [{"x": 50.0, "y": 1.0, "foot": True}, {"x": 50.0, "y": 201.0, "foot": True}, {"x": 50.0, "y": 100.0, "foot": True}, {"x": 50.0, "y": 100.0}],
    }
    assert law.plank_faults(M) == ([(50, 100)], [(50, 201, "drain")])
    assert law.plank_faults({"bridges": [{"x": 0.0, "y": 0.0, "foot": True}]}) == ([(0, 0)], [])


# ---- the ways out --------------------------------------------------------------------------------------------------


def test_a_way_out_crosses_the_brook_at_most_once() -> None:
    M = {"streams": [BROOK]}
    twice = [(0.0, 0.0), (200.0, 0.0), (200.0, 50.0), (0.0, 50.0)]
    once = [(0.0, 0.0), (200.0, 0.0)]
    assert law.way_outs_crossing(M, [twice, once]) == [(0, 0, 2)]
    assert law.way_outs_crossing(M, [once]) == []
    assert law.way_outs_crossing({**M, "lanes": [], "houses": []}) == [], "no handover: no way out to walk"


# ---- the registry --------------------------------------------------------------------------------------------------


def test_a_map_that_keeps_every_rule_has_no_violations() -> None:
    assert law.violations({"lanes": [_lane((0.0, 0.0), (100.0, 0.0), connector=True)], "houses": []}) == {}


def test_a_map_that_breaks_a_rule_names_it() -> None:
    v = law.violations({"lanes": [_lane((0.0, 0.0), (100.0, 0.0), (0.0, 5.0)), _lane((500.0, 500.0), (600.0, 500.0))], "houses": []})
    assert v["bends"] == [("doubles back", 100, 0)] and v["networks"] == 1
