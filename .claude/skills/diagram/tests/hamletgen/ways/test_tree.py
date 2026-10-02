"""`hamletgen/ways/tree.py`: the access tree as lanes (feature 287 wave 6; ways W01, W03, homes H40) - judged whole at
seating (`admits`, the violating case of every clause among them), drawn where the web owes it (`settle_tree`), the
ordinary lanes deferring to it (`tree_faults`, `settle_defer`), and pruned where the map no longer needs it."""

import math
import types

from l7r.diagram.hamletgen.ways import law, settle, tree
from l7r.diagram.hamletgen.ways.corridors import ACCESS_ROLE, FIELD_ROLE, STRIP_ROLE

from ._builders import AdmitsAll

_GEN = {"ftpx": 1.0, "generated_by": "hamletgen"}


class _S(AdmitsAll):
    """What the tree touches on a Settlement: the manifest, `lane()`, `reink_lane()` and `drop_lanes()`."""

    def __init__(self, M):
        self.M = M

    def lane(self, pts, width=3, clearance=0, worn=True, connector=False, spur=False):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": width, "worn": worn, "connector": connector, "spur": spur})

    def reink_lane(self, i):
        pass

    def drop_lanes(self, idxs):
        for i in sorted(set(idxs), reverse=True):
            del self.M["lanes"][i]


def _house(x, y, rot=180.0):
    return {"x": x, "y": y, "w": 40.0, "h": 28.0, "rot": rot}


def _tree(**extra):
    """An exit strip from the cluster's center (400, 0) west to (0, 0), where the connector starts; house A's corridor runs
    from its door straight to the strip, house B's to A's corridor (its target stands on A's), house C has none."""
    M = {
        "meta": dict(_GEN),
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


def _law(M):
    return settle.Lawful(types.SimpleNamespace(M=M))


# ---- the tree's runs --------------------------------------------------------------------------------------------------


def test_the_records_are_read_as_runs_and_each_hangs_from_the_earliest_it_stands_on() -> None:
    M = _tree()
    M["access_corridors"] += [
        {"pts": [[500.0, 100.0], [480.0, 60.0]], "of": [520.0, 120.0]},
        {"pts": [[480.0, 60.0], [390.0, 0.0]]},  # its second leg, round a gable
        {"pts": [[50.0, 300.0], [50.0, 150.0]], "field": True},
        {"pts": [[50.0, 150.0], [50.0, 0.0]], "field": True},
        {"pts": [[900.0, 900.0], [950.0, 950.0]]},  # a leg after the field's is nobody's
        {"pts": [[1.0, 1.0]]},
    ]
    recs = tree.tree_records(M)
    assert [(r["role"], r["of"], r["pts"]) for r in recs] == [
        (ACCESS_ROLE, (300.0, 100.0), [(300.0, 80.0), (300.0, 0.0)]),
        (ACCESS_ROLE, (200.0, 200.0), [(200.0, 180.0), (300.0, 50.0)]),
        (ACCESS_ROLE, (520.0, 120.0), [(500.0, 100.0), (480.0, 60.0), (390.0, 0.0)]),
        (FIELD_ROLE, None, [(50.0, 300.0), (50.0, 150.0), (50.0, 0.0)]),
    ]
    assert tree.tree_records({"access_corridors": [{"pts": [[0.0, 0.0], [1.0, 1.0]]}]}) == [], "a leg with no first leg before it"
    host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
    assert host == [-1, 0, -1, -1] and tree.chain_of(recs, host, 1) == [1, 0]
    assert tree.hosts([{"pts": [(0.0, 900.0), (5.0, 900.0)]}], None) == [None], "on nothing: no host"


def test_the_strip_runs_from_its_innermost_attachment_to_the_connector_or_its_end() -> None:
    M = _tree()
    recs = tree.tree_records(M)
    host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
    assert tree.strip_run(M, recs, host, [0, 1]) == [(300.0, 0.0), (0.0, 0.0)], "to the connector's start"
    assert tree.strip_run(M, recs, host, [1]) is None, "no chosen run on the strip"
    assert tree.strip_run({**M, "access_exit": None}, recs, host, [0]) is None
    off = {**M, "lanes": [{"pts": [[-50.0, 40.0], [-1000.0, 40.0]], "w": 6, "connector": True}]}
    assert tree.strip_run(off, recs, host, [0]) == [(300.0, 0.0), (-50.0, 0.0), (-50.0, 40.0)], "to the start's foot, and on to it"
    near = {**M, "lanes": [{"pts": [[0.0, 3.0], [-1000.0, 3.0]], "w": 6, "connector": True}]}
    assert tree.strip_run(near, recs, host, [0]) == [(300.0, 0.0), (0.0, 3.0)], "a start a few feet off: the last leg turned onto it, no hook"
    assert tree.strip_run(M, recs, host, [0], drawn=False) == [(300.0, 0.0), (0.0, 0.0)], "as seated: to the strip's end"
    assert tree.connector_foot({"lanes": []}, (0.0, 0.0)) is None, "no connector drawn"
    lanes = tree.lanes_of(M, recs, host, [0, 1])
    assert [ln["role"] for ln in lanes] == [STRIP_ROLE, ACCESS_ROLE, ACCESS_ROLE] and lanes[1]["of"] == [300.0, 100.0]
    assert tree.lanes_chain(recs, host, lanes, 1) == [(200.0, 180.0), (300.0, 50.0), (300.0, 0.0), (0.0, 0.0)]


def test_the_strip_ends_on_the_connectors_tread_where_it_passes_the_foot_not_doubled_along_it_to_the_start() -> None:
    """Cohort seed 14 with the straggler footpaths off (feature 287): the web carried the connector's free start 41 ft off
    the strip onto a lane, its first leg running back through the strip's foot; the strip's leg on to the start then ran
    beside that leg - a doubled tail and a needle join between two TREE lanes, which no settle repair may cut. The strip
    ends on the connector's tread where it passes the foot."""
    M = _tree(lanes=[{"pts": [[1.0, -41.0], [0.0, 0.0], [-1000.0, 0.0]], "w": 6, "connector": True}])
    recs = tree.tree_records(M)
    host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
    old = [(300.0, 0.0), (1.0, 0.0), (1.0, -41.0)]  # the start's foot on the strip, and the leg on to it, as drawn before
    was = [M["lanes"][0], {"pts": [list(q) for q in old], "w": 3, "role": STRIP_ROLE}]
    assert 1 in law.doubled_tails({"lanes": was}) and law.needle_ends(was), "the violating case: the leg on to the start"
    run = tree.strip_run(M, recs, host, [0])
    assert run is not None and len(run) == 2 and run[0] == (300.0, 0.0), run
    assert math.dist(run[-1], (0.0, 0.0)) < 0.1, "on the connector's tread by the foot, not on to its start"
    now = [M["lanes"][0], {"pts": [list(q) for q in run], "w": 3, "role": STRIP_ROLE}]
    assert law.doubled_tails({"lanes": now}) == [] and law.needle_ends(now) == [] and law.lane_networks({"lanes": now}) == 1


# ---- the seating's question -------------------------------------------------------------------------------------------


def test_the_tree_admits_a_lawful_corridor_and_refuses_each_rule_it_would_break() -> None:
    """THE ONE PREDICATE (`admits`): a corridor square onto the strip is admitted, and one crossing another corridor (a
    crossroads); one that meets the strip at a needle or hangs from nothing is refused - and the strip itself is judged
    where the new corridor becomes its innermost attachment (here, folded back on it)."""
    M = _tree()
    ok = _law(M)
    house = _house(100.0, 100.0)
    assert tree.admits(ok, M, [(100.0, 80.0), (100.0, 0.0)], ACCESS_ROLE, house), "square onto the strip"
    assert not tree.admits(ok, M, [(100.0, 80.0), (20.0, 10.0), (100.0, 0.5)], ACCESS_ROLE, house), "a needle at the strip"
    assert not tree.admits(ok, M, [(100.0, 80.0), (100.0, 150.0)], ACCESS_ROLE, house), "on nothing"
    open_ = _tree(houses=[], access_corridors=[{"pts": [[300.0, 200.0], [300.0, 0.0]], "of": [300.0, 220.0]}])
    assert tree.admits(_law(open_), open_, [(240.0, 150.0), (340.0, 50.0), (340.0, 0.0)], ACCESS_ROLE, _house(240.0, 170.0)), "across a corridor: a crossroads"
    # the strip as the innermost attachment leaves it: from (400, 0) on, and a corridor arriving back along it folds
    assert not tree.admits(ok, M, [(330.0, 1.0), (400.0, 0.0)], ACCESS_ROLE, _house(330.0, 30.0)), "the strip folds on it"


def test_the_tree_refuses_a_way_out_over_the_brook_and_back_and_a_third_end_at_a_house() -> None:
    brook = {"poly": [[150.0, -500.0], [150.0, 500.0]], "w": 6.0}
    M = _tree(streams=[brook], meta={**_GEN, "brook_fords": [[150.0, 0.0], [150.0, 120.0]]})
    run = [(120.0, 140.0), (180.0, 120.0), (180.0, 60.0), (120.0, 60.0), (120.0, 0.0)]
    assert not tree.way_out_once(M, [run]) and tree.way_out_once(M, [[(120.0, 140.0), (120.0, 0.0)]])
    assert not tree.admits(_law(M), M, run, ACCESS_ROLE, _house(120.0, 160.0))
    crowded = _tree(access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}, {"pts": [[340.0, 90.0], [340.0, 0.0]], "of": [300.0, 100.0]}])
    assert not tree.admits(_law(crowded), crowded, [(260.0, 90.0), (260.0, 0.0)], ACCESS_ROLE, _house(300.0, 100.0)), "three ends at one house"


def test_a_tree_run_is_squared_where_it_crosses_water_and_rejoins_its_own_line_beyond() -> None:
    """Cohort seed 8: the exit strip crossed a channel off square, and `square_crossings` joins its square leg straight to the
    segment's far end - so the whole strip beyond moved under every corridor hanging from it. A tree run is given a vertex
    either side of the crossing first (`rejoined`), so squared it rejoins its own line; and a corridor that met its host on
    the stretch the squaring did move is carried on to the foot on it as drawn (`lanes_of`)."""
    channel = {"pts": [[0.0, -300.0], [400.0, 300.0]], "w0": 6.0}
    M = _tree(drawn_channels=[channel], access_corridors=[{"pts": [[350.0, 80.0], [350.0, 0.0]], "of": [350.0, 100.0]}, {"pts": [[195.0, -80.0], [199.0, 0.0]], "of": [195.0, -100.0]}])
    waters = settle.square_waters(M)
    run = [(400.0, 0.0), (0.0, 0.0)]
    split = tree.rejoined(run, waters)
    assert len(split) == 4 and split[0] == run[0] and split[-1] == run[-1] and all(abs(q[1]) < 1e-9 for q in split), "two vertices on its own line"
    squared = settle.square_run(M, split)
    assert squared != split and squared[0] == run[0] and squared[-1] == run[-1]
    assert tree._on((350.0, 0.0), squared) and tree._on((50.0, 0.0), squared), "away from the crossing, the strip where it was"
    assert tree.rejoined([], waters) == [] and tree.rejoined(run, []) == run
    recs = tree.tree_records(M)
    host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
    lanes = tree.lanes_of(M, recs, host, [0, 1])
    assert lanes[1]["pts"][-1] == [350.0, 0.0] or tuple(lanes[1]["pts"][-1]) == (350.0, 0.0), "met where the strip still runs"
    moved = [tuple(q) for q in lanes[2]["pts"]]
    assert len(moved) > 2 and tree._on(moved[-1], [tuple(q) for q in lanes[0]["pts"]]), "carried on to the squared strip"


def test_the_seating_asks_the_tree_of_a_bundle_as_it_will_be_drawn() -> None:
    """`records_of` reads a bundle's house at its turn and its yard as the matrix will (`access.yard_quad`); `seating_law`
    is built once per house seated; `seating_judge` asks `admits` with them."""
    geom = {"house": (100.0, 100.0, 40.0, 28.0), "yard": (100.0, 60.0, 30.0, 20.0), "turn": 180.0}  # the front faces the strip
    house, yard = tree.records_of(geom)
    assert house == {"x": 100.0, "y": 100.0, "w": 40.0, "h": 28.0, "rot": 180.0} and yard is not None
    assert [round(v, 6) for v in yard["poly"][0]] == [113.5, 69.0], "the rect shrunk by the jitter, turned with its house"
    assert tree.records_of({"house": (1.0, 2.0, 3.0, 4.0), "yard": None}) == ({"x": 1.0, "y": 2.0, "w": 3.0, "h": 4.0, "rot": 0.0}, None)
    s = types.SimpleNamespace(M=_tree())
    first = tree.seating_law(s)
    assert tree.seating_law(s) is first
    s.M["houses"].append(_house(700.0, 700.0))
    assert tree.seating_law(s) is not first, "a house seated: the law is read again"
    judge = tree.seating_judge(s)
    assert judge([(100.0, 48.0), (100.0, 0.0)], geom) and not judge([(100.0, 48.0), (100.0, -300.0)], geom)
    # ...over ONE view of the manifest, so the worked ground is built once for the seating, and the runs laid so far go on to
    # the next house's law (feature 287 perf: a fresh view per house rebuilt the union of the field's plots each time)
    second = tree.seating_law(s)
    laid = second.__dict__["_tree_laid"]
    s.M["houses"].append(_house(760.0, 760.0))
    third = tree.seating_law(s)
    assert third is not second and third.ground is second.ground is first.ground
    assert third.__dict__["_tree_laid"] is laid


# ---- the draw ----------------------------------------------------------------------------------------------------------


def test_the_web_draws_every_owed_chain_once_and_the_strip_again_for_a_new_innermost_attachment() -> None:
    M = _tree(houses=[_house(300.0, 100.0), _house(200.0, 200.0)])
    s = _S(M)
    assert tree.owed(M) == [0, 1], "B hangs from A: both owed"
    assert tree.settle_tree(s) == 3
    assert [ln.get("role") for ln in M["lanes"]] == [None, STRIP_ROLE, ACCESS_ROLE, ACCESS_ROLE]
    assert law.unreached_houses(M) == [] and tree.owed(M) == [] and tree.settle_tree(s) == 0
    M["houses"].append(_house(390.0, 250.0))
    M["access_corridors"].append({"pts": [[390.0, 230.0], [390.0, 0.0]], "of": [390.0, 250.0]})
    M["lanes"] = M["lanes"][:3]  # B's corridor gone: B and the new house are owed
    assert tree.settle_tree(s) == 3, "the strip re-laid from the new innermost attachment, and two corridors"
    assert M["lanes"][1]["pts"][0] == [390.0, 0.0]


def test_the_field_is_owed_its_corridor_where_no_way_reaches_it() -> None:
    field = [[200.0, 200.0], [500.0, 200.0], [500.0, 500.0], [200.0, 500.0]]
    brook = {"poly": [[900.0, -500.0], [900.0, 900.0]], "w": 6.0}
    M = _tree(houses=[], fields=[{"outline": field}], streams=[brook], access_corridors=[{"pts": [[250.0, 195.0], [250.0, 0.0]], "field": True}])
    assert law.field_unreached(M) and tree.owed(M) == [0]
    s = _S(M)
    tree.settle_tree(s)
    assert not law.field_unreached(M) and M["lanes"][-1]["role"] == FIELD_ROLE


def test_an_ordinary_lane_breaking_a_rule_against_a_tree_lane_is_cut_never_the_tree() -> None:
    """The ordinary lanes defer: a tree lane's end on an ordinary lane's tread at a needle, and a tree lane's tail run on beside
    an ordinary lane, are each repaired by cutting the ordinary lane there (`DEFER_GAP_FT` either side)."""
    M = _tree(houses=[], access_corridors=[])
    M["lanes"] += [
        {"pts": [[100.0, 100.0], [300.0, 100.0]], "w": 3, "role": ACCESS_ROLE, "of": [100.0, 130.0]},
        {"pts": [[150.0, 101.0], [500.0, 101.0], [500.0, 300.0]], "w": 3},  # its tread under the tree lane's end, at a needle
    ]
    assert tree.tree_faults(M) and all(i == 2 for i, _q in tree.tree_faults(M))
    s = _S(M)
    assert tree.settle_defer(s) == 1 and M["lanes"][1]["pts"] == [[100.0, 100.0], [300.0, 100.0]], "the tree stands"
    assert tree.tree_faults(M) == [] and tree.settle_defer(s) == 0
    doubled = _tree(houses=[], access_corridors=[])
    doubled["lanes"] += [{"pts": [[0.0, 100.0], [300.0, 100.0]], "w": 3, "role": ACCESS_ROLE}, {"pts": [[250.0, 106.0], [600.0, 106.0], [600.0, 400.0]], "w": 3}]
    assert [i for i, _q in tree.tree_faults(doubled)] == [2], "the tree lane's tail beside it: the ordinary lane defers"
    first = _tree(houses=[], access_corridors=[])  # the same tail at the tree lane's FIRST end (feature 306, perf seed 39)
    first["lanes"] += [{"pts": [[300.0, 100.0], [0.0, 100.0]], "w": 3, "role": ACCESS_ROLE}, {"pts": [[250.0, 106.0], [600.0, 106.0], [600.0, 400.0]], "w": 3}]
    assert 1 in law.doubled_tails(first) and [i for i, _q in tree.tree_faults(first)] == [2], "either end: the ordinary lane defers"
    crowded = _tree(houses=[_house(300.0, 100.0)], access_corridors=[])
    crowded["lanes"] += [{"pts": [[300.0, 80.0], [300.0, 0.0]], "w": 3, "role": ACCESS_ROLE}] + [{"pts": [[x, 85.0], [x, 20.0]], "w": 3} for x in (250.0, 350.0)]
    assert sorted(i for i, _q in tree.tree_faults(crowded)) == [2, 3], "three ends at a house: the ordinary ones"


def test_a_tree_lane_the_map_no_longer_needs_is_pruned_and_one_it_needs_is_kept() -> None:
    M = _tree(houses=[_house(300.0, 100.0)], access_corridors=[])
    M["lanes"] += [
        {"pts": [[300.0, 0.0], [0.0, 0.0]], "w": 3, "role": STRIP_ROLE},
        {"pts": [[300.0, 80.0], [300.0, 0.0]], "w": 3, "role": ACCESS_ROLE, "of": [300.0, 100.0]},
    ]
    s = _S(M)
    assert tree.prune_the_tree(s) == 0, "each is the house's way"
    M["lanes"].append({"pts": [[0.0, 0.0], [260.0, 60.0]], "w": 3})  # an ordinary lane now reaches the house
    assert tree.prune_the_tree(s) == 0, "no record of the corridor: it goes alone or not at all, and alone its strip dangles"
    M["access_corridors"] = [{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}]
    assert tree.prune_the_tree(s) == 1 and [ln.get("role") for ln in M["lanes"]] == [None, None], "the leaf, and the strip with it"
    assert tree.prune_the_tree(s) == 0 and tree.prune_the_tree(_S({"lanes": []})) == 0


def test_an_end_off_its_host_as_drawn_is_set_on_it_or_carried_on_to_it() -> None:
    """`lanes_of`: where a host is drawn off the line its corridor was reserved against (the squaring), the corridor's end is
    set on its foot there if a few feet off (a leg that short would hook) and carried on by a leg of its own if farther."""
    M = _tree()
    recs = tree.tree_records(M)
    host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
    for dy, n in ((5.0, 2), (40.0, 3)):

        def moved(run, dy=dy):
            return [(x, y + dy) for x, y in run] if tuple(run[0]) == (300.0, 0.0) else list(run)

        lanes = tree.lanes_of(M, recs, host, [0], square=moved)
        assert lanes[0]["pts"] == [(300.0, dy), (0.0, dy)] and len(lanes[1]["pts"]) == n and lanes[1]["pts"][-1] == (300.0, dy)


def test_the_tree_refuses_a_sliver_a_third_end_and_a_strip_folded_on_its_new_innermost_corridor() -> None:
    M = _tree(houses=[_house(300.0, 100.0)], access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}])
    ok = _law(M)
    assert not tree.admits(ok, M, [(330.0, 150.0), (300.0, 0.0)], ACCESS_ROLE, _house(330.0, 170.0)), "on the same host point: a sliver"
    crowded = _tree(houses=[_house(300.0, 100.0)], access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}, {"pts": [[250.0, 60.0], [250.0, 0.0]], "of": [250.0, 30.0]}])
    assert not tree.admits(_law(crowded), crowded, [(340.0, 60.0), (340.0, 0.0)], ACCESS_ROLE, _house(345.0, 30.0)), "a third free end at house A"
    # the strip's inner end, now the new corridor's: a corridor arriving from the connector's side folds back on the strip
    back = _tree(houses=[], access_corridors=[{"pts": [[100.0, 80.0], [100.0, 0.0]], "of": [100.0, 100.0]}])
    assert not tree.admits(_law(back), back, [(180.0, 60.0), (150.0, 5.0), (250.0, 0.0)], ACCESS_ROLE, _house(180.0, 80.0))


def test_an_ordinary_lane_closing_a_sliver_with_a_tree_lane_defers() -> None:
    M = _tree(houses=[], access_corridors=[])
    M["lanes"] += [{"pts": [[100.0, 0.0], [100.0, 200.0]], "w": 3, "role": ACCESS_ROLE}, {"pts": [[100.0, 0.0], [106.0, 100.0], [100.0, 200.0]], "w": 3}]
    assert law.needle_loops(M) and {i for i, _q in tree.tree_faults(M)} == {2}


def test_a_corridor_another_hangs_from_is_not_pruned_and_a_leaf_retracts_the_strip() -> None:
    M = _tree(
        houses=[_house(300.0, 100.0), _house(100.0, 100.0)],
        access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}, {"pts": [[100.0, 80.0], [100.0, 0.0]], "of": [100.0, 100.0]}],
    )
    s = _S(M)
    assert tree.settle_tree(s) >= 3 and M["lanes"][1]["pts"][0] == [300.0, 0.0]
    M["lanes"].append({"pts": [[0.0, 0.0], [240.0, 120.0]], "w": 3})  # an ordinary lane now reaches house A from the connector
    assert tree.prune_the_tree(s) == 1 and M["lanes"][1]["role"] == STRIP_ROLE and M["lanes"][1]["pts"][0] == [100.0, 0.0], "A's leaf gone, the strip retracted to B's"
    chain = _tree(houses=[_house(300.0, 100.0), _house(200.0, 200.0)])
    c = _S(chain)
    tree.settle_tree(c)
    chain["lanes"].append({"pts": [[0.0, 0.0], [240.0, 120.0]], "w": 3})
    before = [ln.get("role") for ln in chain["lanes"]]
    tree.prune_the_tree(c)
    assert [ln.get("role") for ln in chain["lanes"]].count(ACCESS_ROLE) >= 1 and before.count(ACCESS_ROLE) == 2, "A, which B hangs from, is no leaf"


def test_a_tree_that_hands_a_house_more_ends_than_its_doorstep_takes_is_refused(monkeypatch) -> None:
    """The doorstep clause of `admits`, reached on its own: a corridor every other clause admits (square onto the strip) is
    refused the moment the whole tree would leave any house discharging more than `law.DOORSTEP_MAX` free ends - here the
    count reported one past the limit, the way a third corridor on a crowded house's front reads to `law.fronting_ends`."""
    M = _tree()
    run, house = [(100.0, 80.0), (100.0, 0.0)], _house(100.0, 100.0)
    assert tree.admits(_law(M), M, run, ACCESS_ROLE, house), "lawful with the doorstep's ends at its limit"
    real = law.fronting_ends
    crowded = {(300.0, 100.0): [object()] * (law.DOORSTEP_MAX + 1)}

    def fronting(m):  # crowded only in the WHOLE tree's reading, the one that holds the new corridor's own lane
        mine = any(abs(q[0] - 100.0) < 1.0 and abs(q[1] - 80.0) < 1.0 for lane in m.get("lanes") or [] for q in lane["pts"][:1])
        return crowded if mine else real(m)

    monkeypatch.setattr(tree.law, "fronting_ends", fronting)
    assert not tree.admits(_law(M), M, run, ACCESS_ROLE, house), "one end past the doorstep: refused"


def test_a_tree_whose_new_way_out_would_cross_a_brook_twice_is_refused(monkeypatch) -> None:
    """The way-out clause of `admits`, reached on its own: a corridor every other clause admits is refused when the new
    house's way out along the tree fails `way_out_once` (a brook crossed and crossed back) - the case the lane law alone
    does not see, because each lane of the chain crosses the brook once."""
    M = _tree()
    run, house = [(100.0, 80.0), (100.0, 0.0)], _house(100.0, 100.0)
    assert tree.admits(_law(M), M, run, ACCESS_ROLE, house), "lawful with its way out crossing no brook twice"
    asked = []

    def twice(_m, chains):
        asked.append(chains)
        return False

    monkeypatch.setattr(tree, "way_out_once", twice)
    assert not tree.admits(_law(M), M, run, ACCESS_ROLE, house), "its way out over the brook and back: refused"
    assert asked and asked[0][0][0] == (100.0, 80.0), "the chain judged is the new house's, from its own door"


def test_an_end_on_the_connectors_tread_is_drawn_where_the_seating_judged_it() -> None:
    """`lanes_of` (feature 306, Inashiro): the web carried the connector's start a few feet inward along the strip, past
    the strip point a corridor hangs from; the strip is cut back to that start, and the corridor's end - already on the
    connector's tread - stays where the seating judged it rather than turning its long leg onto the start (which made a
    corridor hung from it a 19.9 degree needle). Off the tread it is set on the foot as before."""
    base = _tree(access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}, {"pts": [[40.0, 300.0], [1.0, 0.0]], "of": [40.0, 320.0]}])
    cases = (((3.0, 0.0), [[3.0, 0.0], [0.0, 0.0], [-1000.0, 0.0]], (1.0, 0.0)), ((10.0, 0.0), [[10.0, 0.0], [10.0, -1000.0]], (10.0, 0.0)))
    for start, tread, end in cases:
        M = {**base, "lanes": [{"pts": tread, "w": 6, "connector": True}]}
        recs = tree.tree_records(M)
        host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
        lanes = tree.lanes_of(M, recs, host, [0, 1])
        assert lanes[0]["pts"][-1] == start and lanes[2]["pts"][-1] == end, (start, lanes)


def test_an_ordinary_lane_whose_drop_leaves_only_reserved_houses_unreached_is_left_to_the_tree() -> None:
    """`left_to_the_tree` (feature 306, Sawada): the one way reaching houses A and B, both with reserved corridors, may go
    (the settle then draws their corridors); not one reaching house C, which has none, nor one another lane hangs from, nor
    one whose drop leaves nothing to the tree."""
    con = {"pts": [[0.0, 0.0], [-1000.0, 0.0]], "w": 6, "connector": True}
    x, y = {"pts": [[0.0, 0.0], [300.0, 80.0]], "w": 3}, {"pts": [[0.0, 0.0], [600.0, 580.0]], "w": 3}
    assert tree.left_to_the_tree(_tree(lanes=[con, x]), 1), "A and B are the tree's"
    assert not tree.left_to_the_tree(_tree(lanes=[con, y]), 1), "C has no reserved corridor"
    assert not tree.left_to_the_tree(_tree(lanes=[con, x, {"pts": [[300.0, 80.0], [310.0, 400.0]], "w": 3}]), 1), "it strands a lane"
    assert not tree.left_to_the_tree(_tree(lanes=[con, x, {"pts": [[0.0, -5.0], [-400.0, -5.0]], "w": 3}]), 2), "nothing left to the tree"
    apart = [con, {"pts": [[500.0, 900.0], [600.0, 900.0]], "w": 3}, {"pts": [[600.0, 900.0], [700.0, 900.0]], "w": 3}, {"pts": [[700.0, 900.0], [800.0, 900.0]], "w": 3}]
    assert not tree.left_to_the_tree(_tree(lanes=apart), 2), "it splits a piece off the connector's network in two"
