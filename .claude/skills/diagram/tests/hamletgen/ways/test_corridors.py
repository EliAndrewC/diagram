"""`hamletgen/ways/corridors.py`: the reserved corridors drawn (feature 287, plan M3's web half; ways W01, W03, homes H36,
water W57) - each helper on constructed records, the violating case among them."""

import math

import pytest

from l7r.diagram.hamletgen.ways import corridors as co
from l7r.diagram.hamletgen.ways import law
from l7r.diagram.hamletgen.ways.geom import WorkedGround

from ._builders import AdmitsAll


class _S(AdmitsAll):
    """What `draw_corridors` touches on a Settlement: the manifest and `lane()`."""

    def __init__(self, M):
        self.M = M

    def lane(self, pts, width=3, clearance=0, worn=True, connector=False, spur=False):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": width, "worn": worn, "connector": connector, "spur": spur})


def _house(x, y, rot=180.0, w=40.0, h=28.0):
    return {"x": x, "y": y, "w": w, "h": h, "rot": rot}


def _tree_map(**extra):
    """An exit strip from the cluster's center (400, 0) west to the connector's start (0, 0); house A's corridor runs from
    its door straight to the strip, house B's to A's corridor (its target stands on A's), house C has none."""
    M = {
        "meta": {"ftpx": 1.0, "generated_by": "hamletgen"},
        "houses": [_house(300.0, 100.0), _house(200.0, 200.0), _house(600.0, 600.0)],
        "lanes": [{"pts": [[0.0, 0.0], [-1000.0, 0.0]], "w": 6, "connector": True}],
        "access_exit": [[400.0, 0.0], [0.0, 0.0]],
        "access_corridors": [
            {"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]},
            {"pts": [[200.0, 180.0], [300.0, 50.0]], "of": [200.0, 200.0]},
        ],
    }
    M.update(extra)
    return M


def test_the_tree_is_the_connector_and_the_lanes_the_web_draws_for_what_it_owes() -> None:
    assert co.is_tree({"connector": True}) and co.is_tree({"role": co.ACCESS_ROLE}) and co.is_tree({"role": co.FIELD_ROLE})
    assert co.is_tree({"role": co.TARGET_ROLE}) and not co.is_tree({"role": "straggler"}) and not co.is_tree({})


def test_a_chain_runs_from_the_door_along_the_corridors_to_the_strip_and_the_connector() -> None:
    M = _tree_map()
    assert co.corridor_of(M, (300.0, 100.0))["pts"][0] == [300.0, 80.0] and co.corridor_of(M, (600.0, 600.0)) is None
    assert co.connector_start(M) == (0.0, 0.0) and co.connector_start({"lanes": [{"pts": [[1, 1]], "connector": True}]}) is None
    assert co.corridor_chain(M, (300.0, 100.0)) == [(300.0, 80.0), (300.0, 0.0), (0.0, 0.0)]
    assert co.corridor_chain(M, (200.0, 200.0)) == [(200.0, 180.0), (300.0, 50.0), (300.0, 0.0), (0.0, 0.0)], "on along the host corridor to ITS target"
    assert co.corridor_chain(M, (600.0, 600.0)) is None, "a house with no corridor has no chain"
    stray = _tree_map(access_corridors=[{"pts": [[500.0, 300.0], [500.0, 200.0]], "of": [500.0, 320.0]}])
    assert co.corridor_chain(stray, (500.0, 320.0)) == [(500.0, 300.0), (500.0, 200.0)], "a target on nothing ends the chain there"
    bare = _tree_map(lanes=[])
    assert co.corridor_chain(bare, (300.0, 100.0)) == [(300.0, 80.0), (300.0, 0.0)], "no connector: the chain ends on the strip"


def test_the_run_stops_at_its_first_contact_with_the_network_and_meets_it_clean() -> None:
    tread = [((50.0, 0.0), (150.0, 0.0))]
    assert co.first_contact([(0.0, 100.0), (60.0, 10.0)], []) is None
    assert co.first_contact([(0.0, 100.0), (0.0, 300.0)], tread) is None, "a run that never comes near meets nothing"
    run = co.first_contact([(0.0, 100.0), (60.0, 10.0), (60.0, -100.0)], tread)
    assert run is not None and run[0] == (0.0, 100.0) and abs(run[-1][1]) < 1e-9 and 50.0 <= run[-1][0] <= 150.0
    assert not law.bends_badly(run) and law.meets_clean(run, [(50.0, 0.0), (150.0, 0.0)])
    # a run sliding onto the tread along its line would meet it at a needle; it runs on to where it can meet it square
    slide = co.first_contact([(-100.0, 10.0), (100.0, 10.0), (100.0, -100.0)], [((-50.0, 0.0), (300.0, 0.0))])
    assert slide is not None and law.meets_clean(slide, [(-50.0, 0.0), (300.0, 0.0)])
    q, foot = (5.0, 5.0), (5.0, 0.0)
    assert co.contact_endings([(0.0, 50.0), (0.0, 10.0), (10.0, 10.0)], 1, q, foot) == [[(0.0, 50.0), (0.0, 10.0), q, foot], [(0.0, 50.0), (0.0, 10.0), foot]]


def test_a_door_is_stepped_off_its_own_wall_until_the_path_clears_the_house() -> None:
    """Kashikawa's west-wall door stood 2 ft off the wall and its path grazed the corner (`house_hit`)."""
    from l7r.diagram.hamletgen.ways.fabric import house_hit

    h = _house(0.0, 0.0, rot=0.0)
    chain = [(-22.0, 0.0), (-22.0, -200.0)]  # a west-wall door, the path running north along the wall
    out = co.off_the_wall(chain, h)
    assert not house_hit(out[:2], co.ACCESS_WIDTH, [h]) and out[0][0] < -22.0 and out[1:] == chain[1:]
    assert co.off_the_wall([(-22.0, 0.0)], h) == [(-22.0, 0.0)] and co.off_the_wall([(0.0, 0.0), (0.0, 5.0)], h) == [(0.0, 0.0), (0.0, 5.0)]
    through = [(-22.0, 0.0), (22.0, 0.0)]  # straight through the house: no step clears it, the chain comes back as it was
    assert co.off_the_wall(through, h) == through


def test_an_end_behind_a_house_is_carried_round_the_nearer_gable_into_the_dooryard() -> None:
    """Water W57: Kuwabata's lane 5 ended 11 ft behind house 1 and counted as its dooryard."""
    from l7r.diagram.settlement.water_ways.lanes import behind_house, reaches_dooryard

    h = _house(0.0, 0.0, rot=0.0)  # the front faces +y
    for end, side in (((10.0, -25.0), 1.0), ((-10.0, -25.0), -1.0)):
        run = co.round_the_gable([(end[0], -200.0), end], h)
        assert behind_house(h, end) and reaches_dooryard(h, run[-1]) and not behind_house(h, run[-1])
        assert math.copysign(1.0, run[-1][0]) == side, "round the gable on the side the end stands"
    tie = co.round_the_gable([(-50.0, -200.0), (0.0, -25.0)], h)
    assert tie[-1][0] < 0, "on a tie, the side the lane came from"
    assert co.round_the_gable([(0.0, -25.0)], h)[-1][0] > 0


def test_spurs_leave_the_network_nearest_first() -> None:
    segs = [((0.0, 0.0), (100.0, 0.0))]
    assert co.samples_along(segs, step=50.0) == [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0)]
    runs = co.spur_runs(segs, (50.0, 60.0), limit=3)
    assert runs[0] == [(50.0, 0.0), (50.0, 60.0)] and len(runs) == 3
    assert co.spur_runs(segs, (50.0, 0.5)) == [r for r in co.spur_runs(segs, (50.0, 0.5)) if math.dist(r[0], r[1]) > 1.0], "no spur of no length"


def test_a_field_run_goes_straight_to_the_bund_or_over_the_brook_at_a_ford() -> None:
    paddy = WorkedGround([[(200.0, -100.0), (400.0, -100.0), (400.0, 100.0), (200.0, 100.0)]])
    segs = [((0.0, 0.0), (0.0, 50.0))]
    straight = co.field_runs(segs, [paddy], 2.5)
    assert straight and straight[0][0] == (0.0, 0.0) and 190.0 < straight[0][-1][0] < 200.0, "stops on the bund, the half-tread off it"
    brook, fords = [(100.0, -500.0), (100.0, 500.0)], [(100.0, 25.0)]
    over = co.field_runs(segs, [paddy], 2.5, brook, fords)
    assert all(len(r) == 4 for r in over), "every run crosses the brook, so every one crosses it at the ford"
    assert any(abs(r[1][0] - 78.0) < 1e-6 and abs(r[2][0] - 122.0) < 1e-6 for r in over), "square over the ford, landing to landing"
    landed = co.field_runs([((78.0, 25.0), (78.0, 26.0))], [paddy], 2.5, brook, fords)
    assert landed[0][0] == (78.0, 25.0) and len(landed[0]) == 3, "a network point on the near landing starts the crossing itself"
    inside = WorkedGround([[(-10.0, -10.0), (10.0, -10.0), (10.0, 60.0), (-10.0, 60.0)]])
    assert co.field_runs(segs, [inside], 2.5) == [], "a network inside the ground has no run to it"


def test_a_stranded_house_gets_its_corridor_once_and_a_refused_one_is_recorded() -> None:
    s = _S(_tree_map())
    assert law.unreached_houses(s.M), "the constructed web strands the houses"
    assert co.draw_corridors(s, lambda run: True) >= 2
    assert [(x, y) for x, y, _d in law.unreached_houses(s.M)] == [(600, 600)], "the house with no corridor alone is left"
    drawn = [ln for ln in s.M["lanes"] if ln.get("role") == co.ACCESS_ROLE]
    assert {tuple(ln["of"]) for ln in drawn} == {(300.0, 100.0), (200.0, 200.0)} and all(len(ln["pts"]) >= 2 for ln in drawn)
    assert co.draw_corridors(s) == 0, "drawn once: the house its corridor serves is reached"
    refused = _S(_tree_map())
    assert co.draw_corridors(refused, lambda run: False) == 0
    assert [300.0, 100.0] in refused.M["meta"]["access_refused"] and not any(ln.get("role") == co.ACCESS_ROLE for ln in refused.M["lanes"])
    co.draw_corridors(refused, lambda run: False)
    assert refused.M["meta"]["access_refused"].count([300.0, 100.0]) == 1, "a refusal is recorded once"
    reached = _S(_tree_map(houses=[_house(10.0, 30.0)]))
    assert co.draw_corridors(reached) == 0, "nothing is owed where every house is reached"


def test_a_back_wall_door_is_left_round_the_gable() -> None:
    """Water W57 on the tree itself: `access.doors_of` offers every wall, and a corridor from the back wall is drawn from
    the front, round the gable - never ending behind its own house."""
    from l7r.diagram.settlement.water_ways.lanes import behind_house

    M = _tree_map(houses=[_house(300.0, 100.0, rot=0.0)])  # the front faces +y, away from the strip: the door is behind
    s = _S(M)
    assert co.draw_corridors(s) == 1
    run = [tuple(q) for q in s.M["lanes"][-1]["pts"]]
    assert not behind_house(M["houses"][0], run[0]) and not behind_house(M["houses"][0], run[-1])


def test_a_corridor_is_bowed_round_a_building_seated_on_it_or_its_turn_moved_off_one() -> None:
    """A byre, kura or shed seated after the corridor was reserved can stand on it (cohort seeds 10 and 17, Kashikawa's kura
    on a corridor junction): the drawn way bows round it - one apex beside it, either side - or its turn moves off it."""
    shed = [(90.0, -8.0), (110.0, -8.0), (110.0, 8.0), (90.0, 8.0)]
    bows = co.bowed_round([(0.0, 0.0), (200.0, 0.0)], [shed])
    assert len(bows) == 2 * len(co.BOW_OFFSETS_FT) and all(len(b) == 3 for b in bows)
    assert not co.through_a_building(bows[0], [shed]) and not co.through_a_building(bows[1], [shed]), "each side clears it"
    assert bows[0][1][1] * bows[1][1][1] < 0, "one either side"
    moved = co.bowed_round([(0.0, 0.0), (100.0, 0.0), (100.0, 200.0)], [shed])
    assert all(not co.through_a_building([m[1]], [shed]) for m in moved) and moved[0][0] == (0.0, 0.0)
    assert co.bowed_round([(0.0, 50.0), (200.0, 50.0)], [shed]) == [] and co.bowed_round([(5.0, 5.0), (5.0, 5.0)], [shed]) == []
    clear = lambda run: not co.through_a_building(run, [shed])  # noqa: E731 - a vet in one line
    assert co.lawful_run([(0.0, 50.0), (200.0, 50.0)], [shed], clear) == [(0.0, 50.0), (200.0, 50.0)], "a clear run as it came"
    assert co.lawful_run([(0.0, 0.0), (200.0, 0.0)], [shed], clear) == bows[0]
    assert co.lawful_run([(0.0, 0.0), (200.0, 0.0)], [shed], lambda run: False) is None
    assert co.building_quads({"houses": [_house(0.0, 0.0, rot=0.0)], "byres": [{"x": 1.0}]}) == [[(-20.0, -14.0), (20.0, -14.0), (20.0, 14.0), (-20.0, 14.0)]]


def test_a_door_end_is_left_round_either_gable_or_taken_back_off_an_outbuilding() -> None:
    from l7r.diagram.settlement.water_ways.lanes import behind_house

    h = _house(0.0, 0.0, rot=0.0)
    back = [(5.0, -25.0), (5.0, -200.0)]
    near, far = co.door_ends(back, h)
    assert near[0][0] > 0 > far[0][0] and not behind_house(h, near[0]) and not behind_house(h, far[0])
    front = [(0.0, 30.0), (0.0, 130.0)]
    ends = co.door_ends(front, h)
    assert ends[0] == front and [e[0] for e in ends[1:3]] == [(0.0, 34.0), (0.0, 38.0)] and len(ends) == 1 + int(co.DOOR_TRIM_FT // co.DOOR_TRIM_STEP_FT)
    assert co.door_ends([(0.0, 30.0), (0.0, 36.0)], None) == [[(0.0, 30.0), (0.0, 36.0)], [(0.0, 34.0), (0.0, 36.0)]], "no trim past the run's end"
    assert co.sub_run_from([(0.0, 0.0), (0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], 12.0) == [(10.0, 2.0), (10.0, 10.0)]


def test_a_routed_field_way_threads_to_a_ford_and_on_to_the_bund() -> None:
    paddy = WorkedGround([[(200.0, -100.0), (400.0, -100.0), (400.0, 100.0), (200.0, 100.0)]])
    segs = [((0.0, 0.0), (0.0, 50.0))]
    straight = lambda a, b: [a, b]  # noqa: E731 - the router stood in for by a ruler
    alone = co.routed_field_runs(segs, paddy, 2.5, straight)
    assert len(alone) == 1 and alone[0][0] == (0.0, 0.0) and 190.0 < alone[0][-1][0] < 200.0
    brook, fords = [(100.0, -500.0), (100.0, 500.0)], [(100.0, 25.0), (100.0, 400.0)]
    over = co.routed_field_runs(segs, paddy, 2.5, straight, brook, fords)
    assert over and over[0][1] == (78.0, 25.0) and over[0][2] == (122.0, 25.0), "to the near landing, over, from the far"
    assert co.routed_field_runs(segs, paddy, 2.5, lambda a, b: [], brook, fords) == [], "a leg the router finds no way for"
    assert co.routed_field_runs([], paddy, 2.5, straight) == []
    inside = WorkedGround([[(-10.0, -10.0), (500.0, -10.0), (500.0, 600.0), (-10.0, 600.0)]])
    assert co.routed_field_runs(segs, inside, 2.5, straight) == [] and co.routed_field_runs(segs, inside, 2.5, straight, brook, fords) == []


def test_a_stranded_house_behind_a_shed_on_its_corridor_is_reached_round_it() -> None:
    M = _tree_map(houses=[_house(300.0, 100.0)], byres=[{"x": 300.0, "y": 40.0, "w": 16.0, "h": 12.0}])
    s = _S(M)
    assert co.draw_corridors(s, lambda run: not co.through_a_building(run, co.building_quads(M))) == 1
    run = [tuple(q) for q in s.M["lanes"][-1]["pts"]]
    assert not co.through_a_building(run, co.building_quads(M)) and law.unreached_houses(s.M) == []


def test_a_corridor_that_meets_the_network_nowhere_is_routed_on_from_the_strip() -> None:
    """Cohort seeds 15 and 41: the connector started 72 ft off the exit strip and the reserved run turned back on itself
    to reach it, so no contact kept the law - the web's router carries the run on from where it reached the strip."""
    M = _tree_map(houses=[_house(300.0, 100.0)])
    M["lanes"] = [{"pts": [[0.0, -72.0], [0.0, -1000.0]], "w": 6, "connector": True}]
    assert co.corridor_chain(M, (300.0, 100.0), to_connector=False) == [(300.0, 80.0), (300.0, 0.0)]
    calls = []

    def route(a, b):
        calls.append((a, b))
        return [a, b]

    s = _S(M)
    assert co.draw_corridors(s, lambda run: (0.0, 0.0) not in run, route) == 1 and calls, "the reserved run turns back; the routed one is drawn"
    assert law.unreached_houses(s.M) == []
    refused = _S(_tree_map(houses=[_house(300.0, 100.0)], lanes=M["lanes"]))
    assert co.draw_corridors(refused, lambda run: (0.0, 0.0) not in run, lambda a, b: []) == 0, "no route: refused"
    assert co._lawful_contact(None, None, [], lambda r: True) is None


def test_a_house_whose_corridor_is_drawn_is_not_drawn_to_again() -> None:
    M = _tree_map(houses=[_house(300.0, 100.0)])
    M["lanes"].append({"pts": [[900.0, 900.0], [950.0, 900.0]], "w": 3, "role": co.ACCESS_ROLE, "of": [300.0, 100.0]})
    assert co.draw_corridors(_S(M)) == 0


def test_the_ground_index_hands_back_only_what_comes_within_the_pad_in_filing_order() -> None:
    """`GroundIndex` prunes: a part whose box comes within the pad of the run is handed back, in the order filed; water near
    a run is found by its box; an outline edge the run crosses is found."""
    ix = co.GroundIndex(
        [[(100.0, -500.0), (100.0, 500.0)], [(0.0, 0.0)]],
        [[(200.0, 200.0), (300.0, 200.0), (300.0, 300.0)]],
        {"houses": [("b", (50.0, 50.0, 60.0, 60.0)), ("a", (0.0, 0.0, 10.0, 10.0)), ("far", (900.0, 900.0, 910.0, 910.0))]},
    )
    run = [(0.0, 20.0), (40.0, 20.0)]
    assert ix.near("houses", run, 31.0) == ["b", "a"], "within 31: both near ones, filing order kept"
    assert ix.near("houses", run, 12.0) == ["a"] and ix.near("houses", run, 5.0) == []
    assert ix.water_near([(60.0, 0.0), (90.0, 0.0)], 12.0) and not ix.water_near([(60.0, 0.0), (90.0, 0.0)], 5.0)
    assert not ix.open_ground([(250.0, 150.0), (250.0, 250.0)]), "into the outline"
    assert ix.open_ground([(250.0, 150.0), (250.0, 190.0)]) and ix.open_ground([(400.0, 150.0), (400.0, 400.0)])


def test_every_later_contact_is_offered_in_order_and_spaced() -> None:
    """`contacts`: the first is `first_contact`'s; the later ones follow along the run, none nearer than `spacing` to the
    last, each meeting its tread clean - what the draw offers once the first is refused (ways W01, cohort seed 8)."""
    tread = [((0.0, 0.0), (400.0, 0.0))]
    path = [(-20.0, 60.0), (-20.0, 10.0), (380.0, 10.0)]
    every = list(co.contacts(path, tread, spacing=co.CONTACT_FT))
    assert every[0] == co.first_contact(path, tread) and len(every) > 5
    feet = [e[-1][0] for e in every[1:]]  # past the corner each meets the tread square below where it stops
    assert all(b - a >= co.CONTACT_FT - 1e-6 for a, b in zip(feet, feet[1:], strict=False)), "in order along the run, spaced"
    assert all(law.meets_clean(e, [(0.0, 0.0), (400.0, 0.0)]) and not law.bends_badly(e) for e in every)
    assert list(co.contacts(path, [])) == [] and len(list(co.contacts(path, tread))) > len(every), "unspaced, one per sample"


def _yard_house():
    """A house at (300, 100) fronting the strip, its 81-mat threshing yard 80 x 50 ft centered on its door (300, 60) - wider
    along the corridor than `DOOR_TRIM_FT` reaches, as cohort seed 39's under the probes."""
    h = _house(300.0, 100.0)
    yard = {"x": 300.0, "y": 60.0, "w": 50.0, "h": 80.0, "rot": 0.0, "of": [300.0, 100.0], "poly": [[276.0, 21.0], [324.0, 21.0], [324.0, 99.0], [276.0, 99.0]]}
    return h, yard


def test_a_door_end_is_taken_past_its_own_yard_where_the_yard_is_wider_than_the_trims_reach() -> None:
    """Ways W01 (R9: cohort seed 39 under the probes): the door stands in the middle of its threshing yard, the matrix
    forbids a way on the yard, and a yard wider along the run than `DOOR_TRIM_FT` left every trimmed end on it. The last
    door end starts where the tread leaves the yard - as the matrix reads the yard (`own_yard`: its turned rect, not the
    smaller drawn poly)."""
    h, yard = _yard_house()
    M = {"meta": {"ftpx": 1.0}, "threshing_yards": [yard]}
    quad = co.own_yard(M, (300.0, 100.0))
    assert quad is not None and sorted(round(q[1]) for q in quad) == [20, 20, 100, 100], "the matrix's rect, 80 deep"
    assert co.own_yard(M, (0.0, 0.0)) is None and co.own_yard({}, (300.0, 100.0)) is None
    run = [(300.0, 60.0), (300.0, -100.0)]
    past = co.past_the_yard(run, quad)
    assert past is not None and past[0] == (300.0, pytest.approx(20.0 - co.ACCESS_WIDTH / 2 - co.YARD_EXIT_PAD_FT))
    ends = co.door_ends(run, h, quad)
    assert ends[-1] == past and all(e[0][1] > 20.0 - co.ACCESS_WIDTH / 2 for e in ends[:-1]), "every trim stood on the yard"
    assert co.past_the_yard([(0.0, 0.0), (0.0, -50.0)], quad) is None, "a run that never comes near the yard"
    assert co.past_the_yard([(300.0, -100.0), (300.0, 60.0)], quad) is None, "a run that ends on it"
    assert co.door_ends(run, h) == ends[:-1], "no yard, no such end"


def test_a_stranded_house_whose_yard_the_trims_cannot_leave_is_reached_past_it() -> None:
    """The violating case, constructed: every door end within `DOOR_TRIM_FT` stands on the yard, which the vet refuses (as
    the matrix does); before the fix the house was recorded refused and left unreached."""
    h, yard = _yard_house()
    M = _tree_map(houses=[h], threshing_yards=[yard], access_corridors=[{"pts": [[300.0, 60.0], [300.0, 0.0]], "of": [300.0, 100.0]}])
    quad = co.own_yard(M, (300.0, 100.0))

    def off_the_yard(run):
        return not any(20.0 - co.ACCESS_WIDTH / 2 < q[1] < 100.0 and 250.0 < q[0] < 350.0 for q in run)

    s = _S(M)
    assert co.draw_corridors(s, off_the_yard) == 1 and law.unreached_houses(s.M) == []
    assert "access_refused" not in s.M["meta"] and off_the_yard([tuple(q) for q in s.M["lanes"][-1]["pts"]])
    assert quad is not None


def test_a_corridor_whose_first_contact_is_refused_meets_the_network_farther_on() -> None:
    """Ways W01 (R9: cohort seed 8 under the probes): the reserved run's first contact is refused (there, squared at the
    channel it had just crossed, the run kinked) - a later contact along the run, squared as drawn, meets the network clean
    and the house is reached."""
    M = _tree_map(houses=[_house(300.0, 100.0)])
    M["lanes"].append({"pts": [[0.0, 0.0], [20.0, -12.0], [400.0, -12.0]], "w": 3})  # a lane beside the strip, off the connector
    first = co.first_contact(co.corridor_chain(M, (300.0, 100.0)), co.served_network(M["lanes"]))
    assert first is not None

    def not_there(run):
        return math.dist(run[-1], first[-1]) > 1.0

    s = _S(M)
    assert co.draw_corridors(s, not_there) == 1, "a later contact is drawn"
    assert law.unreached_houses(s.M) == [] and "access_refused" not in s.M["meta"]
    assert not_there([tuple(q) for q in s.M["lanes"][-1]["pts"]])
