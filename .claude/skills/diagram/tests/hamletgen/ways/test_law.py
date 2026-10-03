"""`hamletgen/ways/law.py`: every lane rule as one predicate (feature 287, M1) - each asked of a constructed lane that keeps
the rule and of one that breaks it."""

import math

import pytest

from l7r.diagram.hamletgen.ways import law
from l7r.diagram.settlement.homestead_parts.stands import trunk_on_tread


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


def test_an_end_that_walked_away_from_its_junction_dangles() -> None:
    """Feature 293 (settlement-review of Inashiro): a stub leaves the connector at a junction and ends 58 ft from another
    way's end at that SAME junction - inside the 60 ft reach, but the lane walked away from it. A way the end came toward
    still serves it."""
    conn = _lane((2289.5, 1649.0), (2011.5, 1476.7), connector=True)
    strip = _lane((2704.8, 1906.5), (2289.5, 1649.0))
    stub = _lane((2264.8, 1596.6), (2248.2, 1623.4))
    M = {"lanes": [conn, stub, strip], "houses": []}
    assert (2265, 1597) in law.dangling_ends(M), "the stub walked away from the junction it left"
    toward = _lane((2240.0, 1560.0), (2400.0, 1560.0))  # a way 37 ft on past the stub's end, across its line
    assert (2265, 1597) not in law.dangling_ends({**M, "lanes": [conn, stub, strip, toward]}), "a way the end came toward serves it"


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
    # feature 287: a LATERAL is a supply ditch - a polder's ring canal and its field ditches record that role (Kuwabata's
    # six planks, which the comb-only reading named as laid on a drain; research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html, archetypes/110)
    polder = {"field_ditches": [{"poly": [[0.0, 0.0], [100.0, 0.0]], "role": "lateral", "seg": "e_toe"}], "bridges": [{"x": 50.0, "y": 1.0, "foot": True}]}
    assert law.plank_faults(polder) == ([], [])


def test_a_deck_landing_on_the_rice_does_not_seat() -> None:
    """Ways W13: `deck_seats` asks the placer's own solve with the flooded rice (`flooded_ground`), so a crossing whose
    deck can land only in the paddy is named - `settle_the_web` then cuts it."""
    ditch = [(0.0, 100.0), (400.0, 100.0)]
    drowned = [[(-50.0, 101.0), (450.0, 101.0), (450.0, 400.0), (-50.0, 400.0)]]
    assert law.deck_seats([(200.0, 0.0), (200.0, 300.0)], 3.0, [(ditch, 4.0)]) == []
    assert law.deck_seats([(200.0, 0.0), (200.0, 300.0)], 3.0, [(ditch, 4.0)], 1.0, drowned) == [(200, 100)]


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


# ---- joins, fragments, widths (feature 287, homes H37-H40, H42) -------------------------------------------------------


def test_a_join_that_stops_short_of_the_way_it_makes_for() -> None:
    """Homes H37/H38: a free end making for a way within `JOIN_REACH_FT`, over walkable ground, is a join that stopped short
    (future-work: Inashiro's four lanes 28.1-28.5 ft shy of the lane they join)."""
    way = _lane((0.0, 0.0), (0.0, 400.0))
    short = _lane((200.0, 100.0), (28.0, 100.0))  # heading west, 28 ft shy of the way
    away = _lane((200.0, 300.0), (28.0, 300.0), (60.0, 330.0))  # its end turns away from the way
    far = _lane((200.0, 200.0), (50.0, 200.0))  # 50 ft off: not a join
    M = {"lanes": [way, short, away, far]}
    assert law.near_misses(M) == [(1, -1, (0.0, 100.0))]
    assert law.near_misses({"lanes": [way, short], "streams": [{"poly": [[14.0, -50.0], [14.0, 450.0]]}]}) == [], "over water: blocked"
    assert law.near_misses({"lanes": [way, short], "houses": [_house(14.0, 100.0, 10.0, 10.0)]}) == [], "through a farmhouse: blocked"
    assert law.near_misses({"lanes": [way, short], "gardens": [{"poly": [[10.0, 95.0], [18.0, 95.0], [18.0, 105.0], [10.0, 105.0]]}]}) == []
    assert law.near_misses({"lanes": [way, short], "fields": [{"outline": [[10.0, 50.0], [18.0, 50.0], [18.0, 150.0], [10.0, 150.0]]}]}) == []
    assert law.near_misses({"lanes": [way, _lane((5.0, 5.0)), _lane((1.0, 1.0), (1.0, 1.0)), _lane((50.0, 0.0), (50.0, 0.0), (80.0, 0.0), connector=True)]}) == []


def test_a_span_that_would_hook_or_run_along_a_tread_is_no_join() -> None:
    way = _lane((0.0, 0.0), (0.0, 400.0))
    hooky = _lane((-100.0, 90.0), (10.0, 100.0))  # already past the way: the span back to it is a hook
    assert law.near_misses({"lanes": [way, hooky]}) == []
    assert not law.span_walkable({"lanes": [way, _lane((10.0, 0.0), (10.0, 400.0))]}, (12.0, 100.0), (8.0, 180.0), (0,)), "down the length of a way"
    assert law.span_walkable({"lanes": [way, _lane((10.0, 0.0), (10.0, 400.0))]}, (12.0, 100.0), (8.0, 180.0), (0, 1)), "...unless it is a way the span meets"


def test_a_fragment_that_earns_nothing() -> None:
    conn = _lane((0.0, 0.0), (-500.0, 0.0), connector=True)
    main = _lane((0.0, 0.0), (0.0, 300.0))
    stub = _lane((0.0, 150.0), (10.0, 150.0))  # 10 ft off the main, serving nothing the main does not
    link = _lane((0.0, 300.0), (20.0, 300.0))
    island = _lane((20.0, 300.0), (20.0, 500.0))
    M = {"lanes": [conn, main, stub, link, island], "houses": [_house(40.0, 480.0)], "meta": {"generated_by": "hamletgen"}}
    assert law.short_fragments(M) == [2], "the link earns its place (it joins the island), the stub does not"
    assert law.short_fragments({"lanes": [conn, main]}) == []


def test_one_way_keeps_one_width() -> None:
    lanes = [_lane((0.0, 0.0), (100.0, 0.0), w=6), _lane((100.0, 0.0), (200.0, 10.0), w=3), _lane((200.0, 10.0), (300.0, 10.0), w=3)]
    assert law.width_steps(lanes) == [(0, 1)]


# ---- feature 287 wave 3: the ends at a house, the needles, the way targets, every water decked ---------------------------


def test_a_lane_end_behind_a_house_has_not_reached_it() -> None:
    """Water W57: behind the back wall and abreast of it, at no dooryard, off the bund and at no junction."""
    house = _house(0.0, 200.0)  # the front faces +y: the back wall is at y = 185
    M = {"lanes": [_lane((0.0, 0.0), (0.0, 160.0))], "houses": [house]}
    assert law.ends_behind(M) == [(0, -1, 0)]
    assert law.ends_behind({**M, "houses": []}) == [] and law.ends_behind({**M, "lanes": [_lane((0.0, 0.0), (0.0, 100.0))]}) == [], "no house near"
    front = {**M, "lanes": [_lane((0.0, 400.0), (0.0, 220.0))]}
    assert law.ends_behind(front) == [], "at the front, the dooryard"
    joined = {**M, "lanes": [*M["lanes"], _lane((-50.0, 160.0), (50.0, 160.0))]}
    assert law.ends_behind(joined) == [], "an end on another way is a junction"
    field = {**M, "fields": [{"outline": [[-20.0, 162.0], [20.0, 162.0], [20.0, 170.0], [-20.0, 170.0]]}]}
    assert law.ends_behind(field) == [], "an end on the bund reaches the field"
    assert law.ends_behind({**M, "lanes": [_lane((0.0, 0.0), (0.0, 160.0), connector=True)]}) == [], "the connector leaves the map"


def test_a_way_forked_round_a_needle_of_grass_is_named_and_a_block_is_not() -> None:
    """Homes H39: a face of the web thinner than `NEEDLE_LOOP_FT` is the same way drawn twice."""
    needle = {"lanes": [_lane((0.0, 0.0), (200.0, 0.0)), _lane((0.0, 0.0), (100.0, 12.0), (200.0, 0.0))]}
    ((face, bounding),) = law.needle_loops(needle)
    assert bounding == [0, 1] and 2.0 * face.area / face.length < law.NEEDLE_LOOP_FT
    block = {"lanes": [_lane((0.0, 0.0), (200.0, 0.0), (200.0, 150.0)), _lane((0.0, 0.0), (0.0, 150.0), (200.0, 150.0))]}
    assert law.needle_loops(block) == [], "a block wide enough to hold a steading"
    assert law.needle_loops({"lanes": [_lane((0.0, 0.0), (200.0, 0.0))]}) == []


def test_a_way_target_is_reached_by_the_served_network_and_counts_as_served() -> None:
    """Homes H36: the burial ground's near edge is a point a way must reach, and an end there serves something."""
    meta = {"way_targets": [{"kind": "burial ground", "at": [100.0, 60.0]}]}
    M = {"meta": meta, "lanes": [_lane((0.0, 0.0), (-500.0, 0.0), connector=True)]}
    assert law.way_targets(M) == [(100.0, 60.0)] and law.unreached_targets(M) == [(100.0, 60.0)]
    assert law.unreached_targets({"lanes": M["lanes"]}) == []
    spur = {**M, "lanes": [*M["lanes"], _lane((0.0, 0.0), (100.0, 55.0))]}
    assert law.unreached_targets(spur) == [] and law.dangling_lane_ends(spur) == [], "the spur's end serves the graves"
    near = {"meta": {"way_targets": [{"at": [0.0, 20.0]}]}, "lanes": [M["lanes"][0], _lane((0.0, 0.0), (0.0, 18.0))]}
    assert law.short_fragments(near) == [], "a short spur that reaches the graves earns its place"


def test_every_water_a_way_crosses_is_under_a_deck_not_the_brook_alone() -> None:
    """The drain takes no footplank (`plank_on_supply`), so a way over it is carried on a deck or not drawn at all."""
    drain = {"poly": [[0.0, 100.0], [400.0, 100.0]], "w": 4.0, "role": "drain"}
    M = {"field_ditches": [drain], "lanes": [_lane((200.0, 0.0), (200.0, 200.0))], "bridges": []}
    assert law.unbridged_crossings(M) == [(200, 100)]
    M["bridges"] = [{"x": 200.0, "y": 100.0, "span": 12.0, "rot": 90.0}]
    assert law.unbridged_crossings(M) == []


def test_a_lane_over_a_farmstead_fixture_is_named() -> None:
    """Feature 287 (the fixtures laid in each bundle): a tread over a privy, a heap or a hokora - its own household's too."""
    privy = {"kind": "privy", "x": 100.0, "y": 0.0, "w": 6.0, "h": 6.0, "rot": 0.0}
    M = {"farm_fixtures": [privy, {"kind": "coop", "x": 1.0}], "lanes": [_lane((0.0, 0.0), (200.0, 0.0)), _lane((0.0, 50.0), (200.0, 50.0))]}
    assert len(law.fixture_quads(M)) == 1
    assert law.lanes_over_fixtures(M) == [(0, 0)]
    assert law.over_a_fixture([(0.0, 4.9), (200.0, 4.9)], 3.0, law.fixture_quads(M)) == 0, "the tread's half-width reaches it"
    assert law.over_a_fixture([(0.0, 6.5), (200.0, 6.5)], 3.0, law.fixture_quads(M)) is None
    assert law.over_a_fixture([(0.0, 50.0), (100.0, 1.0)], 3.0, law.fixture_quads(M)) == 0, "an end standing in it"
    assert law.lanes_over_fixtures({"lanes": M["lanes"]}) == []


def test_a_lane_through_a_yard_persimmons_trunk_is_named_and_one_under_its_crown_is_not() -> None:
    """Feature 287, homes H43 (cohort seed 42: a straggler through a neighbor's persimmon): the trunk's box, the seating's
    own (`TRUNK_FT`), is a fixture quad the web keeps its tread off; the crown's reach is not - a lane may pass under it."""
    tree = {"x": 100.0, "y": 0.0, "r": 11.5}
    M = {"persimmons": [tree, {"r": 3.0}], "meta": {"ftpx": 2.0}, "lanes": [_lane((0.0, 1.0), (200.0, 1.0), w=3.0), _lane((0.0, 9.0), (200.0, 9.0), w=3.0)]}
    (quad,) = law.fixture_quads(M)
    assert max(abs(q[0] - 100.0) for q in quad) == pytest.approx(law.TRUNK_FT / 2.0 / 2.0), "the box read in px at the map's scale"
    assert law.lanes_over_fixtures(M) == [(0, 0)], "the trunk on the tread"
    assert trunk_on_tread(100.0, 0.0, M["lanes"][:1]) and not trunk_on_tread(100.0, 0.0, M["lanes"][1:])
    assert law.over_a_fixture([(0.0, 9.0), (200.0, 9.0)], 3.0, law.fixture_quads(M)) is None, "under the crown, clear of the trunk"


def test_a_short_lane_that_holds_another_lanes_end_earns_its_place() -> None:
    """Feature 291 on 287: a short door path whose removal would leave its street's end reaching nothing is no fragment -
    the street's end stands 70 ft from its house, served only by the path meeting it there."""
    conn = _lane((0.0, 0.0), (-500.0, 0.0), connector=True)
    street = _lane((0.0, 0.0), (400.0, 0.0), w=6)
    path = _lane((400.0, 0.0), (400.0, 20.0))  # 20 ft, to a door; the house stands 70 ft off the street's end
    M = {"lanes": [conn, street, path], "houses": [_house(400.0, 70.0)], "meta": {"generated_by": "hamletgen"}}
    assert law.short_fragments(M) == [], "dropped, the street's end would dangle"
    beside = _lane((200.0, 0.0), (200.0, 20.0))  # the same, mid-street: holds no end
    M2 = {"lanes": [conn, street, path, beside], "houses": [_house(400.0, 70.0), _house(200.0, 70.0)], "meta": {"generated_by": "hamletgen"}}
    assert law.short_fragments(M2) == [3]


def test_two_boxes_meet_within_their_pad_and_an_empty_line_meets_nothing() -> None:
    """Feature 314: `boxes_meet` and `_bbox`, read by the squaring and the oblique test to skip a course out of reach - and an
    empty lane's box is none, so `oblique_at` passes it."""
    from l7r.diagram.hamletgen.ways import law as L

    a, b = [(0.0, 0.0), (10.0, 0.0)], [(15.0, 0.0), (20.0, 5.0)]
    assert L.boxes_meet(a, b, 5.0) and not L.boxes_meet(a, b, 4.9), "five apart: within a pad of five, not of 4.9"
    assert not L.boxes_meet([], b, 100.0) and L._bbox([]) is None
    M = {"streams": [{"poly": [[50.0, -10.0], [50.0, 10.0]]}], "lanes": [{"pts": []}, {"pts": [[0.0, 0.0], [100.0, 2.0]]}]}
    assert [i for i, _k, _x, _off in L.oblique_at(M)] == [] or all(i == 1 for i, _k, _x, _off in L.oblique_at(M)), "the empty lane passed"


def test_a_point_lies_from_a_box_no_farther_than_from_what_it_holds_and_a_free_end_reads_the_boxes_the_same() -> None:
    """Feature 317: `box_gap`, read by `free_end` and `near_misses` to pass over a way whose box is beyond reach - zero inside the
    box, the corner distance off it, infinite from no box; and `free_end` answers alike with the boxes and without them."""
    from l7r.diagram.hamletgen.ways import law as L

    box = (0.0, 0.0, 10.0, 10.0)
    assert L.box_gap((5.0, 5.0), box) == 0.0 and L.box_gap((13.0, 14.0), box) == 5.0 and L.box_gap((5.0, -2.0), box) == 2.0
    assert L.box_gap((0.0, 0.0), None) == math.inf
    ways = [[(0.0, 0.0), (50.0, 0.0)], [(50.0, 0.5), (50.0, 40.0)], [(200.0, 0.0), (250.0, 0.0)]]
    boxes = [L._bbox(w) for w in ways]
    for q, free in (((50.0, 0.0), False), ((0.0, 0.0), True)):
        assert L.free_end(ways, 0, q) is free and L.free_end(ways, 0, q, boxes) is free, f"{q}: the boxes change no answer"
