"""`hamletgen/ways/tree.py`: the access tree as lanes (feature 287 wave 6; ways W01, W03, homes H40) - judged whole at
seating (`admits`, the violating case of every clause among them), drawn where the web owes it (`settle_tree`), the
ordinary lanes deferring to it (`tree_faults`, `settle_defer`), and pruned where the map no longer needs it."""

import types

from l7r.diagram.hamletgen.ways import law, settle, tree
from l7r.diagram.hamletgen.ways.corridors import ACCESS_ROLE, TARGET_ROLE

from ._builders import AdmitsAll

_GEN = {"ftpx": 1.0, "generated_by": "hamletgen"}


class _S(AdmitsAll):
    """What the tree touches on a Settlement: the manifest, `lane()`, `reshape_lane()`, `reink_lane()` and `drop_lanes()`."""

    def __init__(self, M, refuse=False):
        self.M = M
        self.refuse = refuse  # `reshape_lane` refuses every rewrite, as the overlap matrix may
        self.reinked: list[int] = []

    def reshape_lane(self, ln, pts):
        if self.refuse:
            return False
        ln["pts"] = [[float(x), float(y)] for x, y in pts]
        return True

    def lane(self, pts, width=3, clearance=0, worn=True, connector=False, spur=False):
        self.M["lanes"].append({"pts": [list(q) for q in pts], "w": width, "worn": worn, "connector": connector, "spur": spur})

    def reink_lane(self, i):
        self.reinked.append(i)

    def drop_lanes(self, idxs):
        for i in sorted(set(idxs), reverse=True):
            del self.M["lanes"][i]


def _house(x, y, rot=180.0):
    return {"x": x, "y": y, "w": 40.0, "h": 28.0, "rot": rot}


def _tree(**extra):
    """The track out from the way out's gate (400, 0) west (feature 320: the tree's root, `tree._root`); house A's corridor runs
    from its door straight to it, house B's to A's corridor (its target stands on A's), house C has none."""
    M = {
        "meta": dict(_GEN),
        "houses": [_house(300.0, 100.0), _house(200.0, 200.0), _house(600.0, 600.0)],
        "lanes": [{"pts": [[400.0, 0.0], [0.0, 0.0], [-1000.0, 0.0]], "w": 6, "connector": True}],
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
        {"pts": [[1.0, 1.0]]},
    ]
    recs = tree.tree_records(M)
    assert [(r["role"], r["of"], r["pts"]) for r in recs] == [
        (ACCESS_ROLE, (300.0, 100.0), [(300.0, 80.0), (300.0, 0.0)]),
        (ACCESS_ROLE, (200.0, 200.0), [(200.0, 180.0), (300.0, 50.0)]),
        (ACCESS_ROLE, (520.0, 120.0), [(500.0, 100.0), (480.0, 60.0), (390.0, 0.0)]),
    ]
    assert tree.tree_records({"access_corridors": [{"pts": [[0.0, 0.0], [1.0, 1.0]]}]}) == [], "a leg with no first leg before it"
    host = tree.hosts(recs, ((400.0, 0.0), (0.0, 0.0)))
    assert host == [-1, 0, -1] and tree.chain_of(recs, host, 1) == [1, 0]
    assert tree.hosts([{"pts": [(0.0, 900.0), (5.0, 900.0)]}], None) == [None], "on nothing: no host"


def test_the_root_is_the_track_out_as_drawn_else_the_track_as_chosen() -> None:
    """`_root` (feature 320): the connector's points where it is drawn; before that, the track out as chosen once the last
    house stood, which the households' ways are laid to (`way_out_track`); neither, none. `lanes_of` draws no lane of its own for the root."""
    M = _tree()
    assert tree._root(M) == [(400.0, 0.0), (0.0, 0.0), (-1000.0, 0.0)]
    assert tree._root({"lanes": [], "way_out_track": [[5.0, 5.0], [6.0, 5.0]]}) == [(5.0, 5.0), (6.0, 5.0)]
    assert tree._root({"lanes": []}) is None
    recs = tree.tree_records(M)
    host = tree.hosts(recs, tree._root(M))
    lanes = tree.lanes_of(M, recs, host, [0, 1])
    assert [ln["role"] for ln in lanes] == [ACCESS_ROLE, ACCESS_ROLE] and lanes[0]["of"] == [300.0, 100.0]
    assert tree.lanes_chain(recs, host, lanes, 1) == [(200.0, 180.0), (300.0, 50.0), (300.0, 0.0)]


# ---- the seating's question -------------------------------------------------------------------------------------------


def test_the_tree_admits_a_lawful_corridor_and_refuses_each_rule_it_would_break() -> None:
    """THE ONE PREDICATE (`admits`): a corridor square onto the track out is admitted, and one crossing another corridor (a
    crossroads); one that meets the track out at a needle, folds back along it or hangs from nothing is refused."""
    M = _tree()
    ok = _law(M)
    house = _house(100.0, 100.0)
    assert tree.admits(ok, M, [(100.0, 80.0), (100.0, 0.0)], ACCESS_ROLE, house), "square onto the track out"
    assert not tree.admits(ok, M, [(100.0, 80.0), (20.0, 10.0), (100.0, 0.5)], ACCESS_ROLE, house), "a needle at the track out"
    assert not tree.admits(ok, M, [(100.0, 80.0), (100.0, 150.0)], ACCESS_ROLE, house), "on nothing"
    open_ = _tree(houses=[], access_corridors=[{"pts": [[300.0, 200.0], [300.0, 0.0]], "of": [300.0, 220.0]}])
    assert tree.admits(_law(open_), open_, [(240.0, 150.0), (340.0, 50.0), (340.0, 0.0)], ACCESS_ROLE, _house(240.0, 170.0)), "across a corridor: a crossroads"
    # a corridor arriving back along the track out to its start folds on it
    assert not tree.admits(ok, M, [(330.0, 1.0), (400.0, 0.0)], ACCESS_ROLE, _house(330.0, 30.0)), "folded along the track out"


def test_a_corridor_closing_a_sliver_with_another_and_the_track_out_is_refused() -> None:
    open_ = _tree(houses=[], access_corridors=[{"pts": [[300.0, 200.0], [300.0, 0.0]], "of": [300.0, 220.0]}])
    assert not tree.admits(_law(open_), open_, [(240.0, 100.0), (312.0, 0.0)], ACCESS_ROLE, _house(240.0, 120.0)), "a sliver"


def test_the_tree_refuses_a_way_out_over_the_brook_and_back_and_a_third_end_at_a_house() -> None:
    brook = {"poly": [[150.0, -500.0], [150.0, 500.0]], "w": 6.0}
    M = _tree(streams=[brook], meta={**_GEN, "brook_fords": [[150.0, 0.0], [150.0, 120.0]]})
    run = [(120.0, 140.0), (180.0, 120.0), (180.0, 60.0), (120.0, 60.0), (120.0, 0.0)]
    assert not tree.way_out_once(M, [run]) and tree.way_out_once(M, [[(120.0, 140.0), (120.0, 0.0)]])
    assert not tree.admits(_law(M), M, run, ACCESS_ROLE, _house(120.0, 160.0))
    crowded = _tree(access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}, {"pts": [[340.0, 90.0], [340.0, 0.0]], "of": [300.0, 100.0]}])
    assert not tree.admits(_law(crowded), crowded, [(260.0, 90.0), (260.0, 0.0)], ACCESS_ROLE, _house(300.0, 100.0)), "three ends at one house"


def test_a_tree_run_is_squared_where_it_crosses_water_and_rejoins_its_own_line_beyond() -> None:
    """Cohort seed 8: a tree run crossed a channel off square, and `square_crossings` joins its square leg straight to the
    segment's far end - so the whole run beyond moved under every corridor hanging from it. A tree run is given a vertex
    either side of the crossing first (`rejoined`), so squared it rejoins its own line; a corridor meeting the track out as
    drawn stays where it meets it (`lanes_of`)."""
    channel = {"pts": [[0.0, -300.0], [400.0, 300.0]], "w0": 6.0}
    M = _tree(drawn_channels=[channel], access_corridors=[{"pts": [[350.0, 80.0], [350.0, 0.0]], "of": [350.0, 100.0]}, {"pts": [[195.0, -80.0], [199.0, 0.0]], "of": [195.0, -100.0]}])
    waters = settle.square_waters(M)
    run = [(400.0, 0.0), (0.0, 0.0)]
    split = tree.rejoined(run, waters)
    assert len(split) == 4 and split[0] == run[0] and split[-1] == run[-1] and all(abs(q[1]) < 1e-9 for q in split), "two vertices on its own line"
    squared = settle.square_run(M, split)
    assert squared != split and squared[0] == run[0] and squared[-1] == run[-1]
    assert tree._on((350.0, 0.0), squared) and tree._on((50.0, 0.0), squared), "away from the crossing, the run where it was"
    assert tree.rejoined([], waters) == [] and tree.rejoined(run, []) == run
    recs = tree.tree_records(M)
    host = tree.hosts(recs, tree._root(M))
    lanes = tree.lanes_of(M, recs, host, [0, 1])
    assert tuple(lanes[0]["pts"][-1]) == (350.0, 0.0), "met where the track out runs"
    assert tree._on(tuple(lanes[1]["pts"][-1]), tree._root(M)), "on the track out as drawn"


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


def test_the_web_draws_every_owed_chain_once() -> None:
    M = _tree(houses=[_house(300.0, 100.0), _house(200.0, 200.0)])
    s = _S(M)
    assert tree.owed(M) == [0, 1], "B hangs from A: both owed"
    assert tree.settle_tree(s) == 2
    assert [ln.get("role") for ln in M["lanes"]] == [None, ACCESS_ROLE, ACCESS_ROLE]
    assert law.unreached_houses(M) == [] and tree.owed(M) == [0, 1] and tree.settle_tree(s) == 0, "every household's way owed (feature 318), each drawn once"
    M["houses"].append(_house(390.0, 250.0))
    M["access_corridors"].append({"pts": [[390.0, 230.0], [390.0, 0.0]], "of": [390.0, 250.0]})
    M["lanes"] = M["lanes"][:2]  # B's corridor gone: B and the new house are owed
    assert tree.settle_tree(s) == 2, "two corridors, hung from the track out and from A's"
    assert M["lanes"][-1]["pts"][-1] == [390.0, 0.0]


def test_a_drawn_way_off_its_judged_form_is_reshaped_and_reinked_unless_the_rewrite_is_refused() -> None:
    """`settle_tree` (feature 320): a household's way already drawn whose points differ from the form the gap pass judged is
    rewritten to it in place (`reshape_lane`) and re-inked, and counted; a refused rewrite leaves it as drawn, uncounted."""
    for refuse, want in ((False, 1), (True, 0)):
        M = _tree(houses=[_house(300.0, 100.0)], access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}])
        s = _S(M, refuse=refuse)
        assert tree.settle_tree(s) == 1 and len(M["lanes"]) == 2
        judged = [list(q) for q in M["lanes"][1]["pts"]]
        M["lanes"][1]["pts"] = [[310.0, 80.0], [310.0, 0.0]]  # moved off its judged form
        assert tree.settle_tree(s) == want and len(M["lanes"]) == 2, "rewritten in place, never drawn twice"
        assert M["lanes"][1]["pts"] == (judged if not refuse else [[310.0, 80.0], [310.0, 0.0]])
        assert s.reinked == ([1] if not refuse else [])


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
    for _ in range(5):  # ...and the stretch the cut left 1 ft beside the tree lane is a doubled band, cut in turn (feature 318)
        if not tree.settle_defer(s):
            break
    assert tree.tree_faults(M) == [] and tree.settle_defer(s) == 0 and M["lanes"][1]["pts"] == [[100.0, 100.0], [300.0, 100.0]]
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
        {"pts": [[300.0, 80.0], [300.0, 0.0]], "w": 3, "role": ACCESS_ROLE, "of": [300.0, 100.0]},
    ]
    s = _S(M)
    assert tree.prune_the_tree(s) == 0, "the house's way"
    M["lanes"].append({"pts": [[0.0, 0.0], [260.0, 60.0]], "w": 3})  # an ordinary lane now reaches the house
    M["access_corridors"] = [{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}]
    assert tree.prune_the_tree(s) == 0, "a household's own way is never pruned, an ordinary lane reaching its house or not (feature 318)"
    # ...a tree lane that is no household's way (a way target's spur) goes when the map no longer needs it
    M["access_corridors"] = []
    M["lanes"][-2] = {"pts": [[300.0, 80.0], [300.0, 0.0]], "w": 3, "role": TARGET_ROLE}
    assert tree.prune_the_tree(s) == 1
    assert tree.prune_the_tree(_S({"lanes": []})) == 0


def test_an_end_off_its_host_as_drawn_is_set_on_it_or_carried_on_to_it() -> None:
    """`lanes_of`: where the track out is drawn off the line a corridor was laid against, the corridor's end is set on its foot
    there if a few feet off (a leg that short would hook) and carried on by a leg of its own if farther."""
    for dy, n in ((5.0, 2), (40.0, 3)):
        M = _tree(lanes=[{"pts": [[400.0, dy], [0.0, dy], [-1000.0, dy]], "w": 6, "connector": True}])
        recs = tree.tree_records(M)
        host = tree.hosts(recs, [(400.0, 0.0), (0.0, 0.0)])  # laid against the line before it moved
        lanes = tree.lanes_of(M, recs, host, [0])
        assert len(lanes[0]["pts"]) == n and lanes[0]["pts"][-1] == (300.0, dy), (dy, lanes)


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


def test_a_corridor_another_hangs_from_is_not_pruned() -> None:
    M = _tree(
        houses=[_house(300.0, 100.0), _house(100.0, 100.0)],
        access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}, {"pts": [[100.0, 80.0], [100.0, 0.0]], "of": [100.0, 100.0]}],
    )
    s = _S(M)
    assert tree.settle_tree(s) == 2 and M["lanes"][1]["pts"][-1] == [300.0, 0.0]
    M["lanes"].append({"pts": [[0.0, 0.0], [240.0, 120.0]], "w": 3})  # an ordinary lane now reaches house A from the connector
    assert tree.prune_the_tree(s) == 0 and M["lanes"][1]["pts"][-1] == [300.0, 0.0], "A's way stays though a lane reaches A (feature 318)"
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
    """`lanes_of` (feature 306, Inashiro): a corridor's end already on the track out's tread stays where the seating judged it
    rather than being turned onto the track's start (which made a corridor hung from it a 19.9 degree needle); off the tread
    it is set on its foot there."""
    base = _tree(access_corridors=[{"pts": [[40.0, 300.0], [1.0, 0.0]], "of": [40.0, 320.0]}])
    for tread, end in (([[3.0, 0.0], [0.0, 0.0], [-1000.0, 0.0]], (1.0, 0.0)), ([[10.0, 0.0], [10.0, -1000.0]], (10.0, 0.0))):
        M = {**base, "lanes": [{"pts": tread, "w": 6, "connector": True}]}
        recs = tree.tree_records(M)
        host = tree.hosts(recs, [(400.0, 0.0), (0.0, 0.0)])
        lanes = tree.lanes_of(M, recs, host, [0])
        assert lanes[0]["pts"][-1] == end, (tread, lanes)


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


def test_the_tree_is_asked_again_with_its_ends_joined_as_the_web_joins_them() -> None:
    """Feature 317, plan D6: a free end that stops short of a way it makes for is carried onto it (`law.near_misses`, as the
    settle's `settle_joins` carries it) - feature 314 R12's corridor start, 15 ft from another's end, closed a sliver once
    joined - so `admits` asks the needle of the joined tree too."""
    lanes = [{"pts": [[0.0, 0.0], [300.0, 0.0]], "w": 3.0}, {"pts": [[150.0, 60.0], [110.0, 12.0]], "w": 3.0}]
    trial = {"meta": dict(_GEN), "lanes": lanes, "houses": []}
    joined = tree.as_joined(trial, lanes)
    assert [list(q) for q in joined[0]["pts"]] == lanes[0]["pts"], "a lane whose ends make for no way is left as it was"
    assert len(joined[1]["pts"]) == 3 and abs(joined[1]["pts"][-1][1]) < 1e-6, "the end carried onto the way it made for"
    assert lanes[1]["pts"] == [[150.0, 60.0], [110.0, 12.0]], "the trial's own lanes untouched"


def test_a_corridor_whose_joined_tree_closes_a_sliver_is_refused(monkeypatch) -> None:  # noqa: ANN001
    """Feature 317, plan D6: lawful as laid, but a sliver once the web joins the ends - refused at seating."""
    M = _tree()
    ok = _law(M)
    house = _house(100.0, 100.0)
    assert tree.admits(ok, M, [(100.0, 80.0), (100.0, 0.0)], ACCESS_ROLE, house), "lawful as laid and as joined"
    real = law.needle_loops
    monkeypatch.setattr(tree, "as_joined", lambda trial, lanes: [{**ln, "joined": True} for ln in lanes])
    monkeypatch.setattr(law, "needle_loops", lambda M_: ["sliver"] if any(ln.get("joined") for ln in M_["lanes"]) else real(M_))
    assert not tree.admits(_law(M), M, [(100.0, 80.0), (100.0, 0.0)], ACCESS_ROLE, house), "a sliver only once joined: refused"


def test_a_corridor_whose_drawn_form_crosses_its_own_fixture_is_refused(monkeypatch) -> None:  # noqa: ANN001
    """Feature 317 (cohort seed 18 at 15 households): squaring a water crossing re-lays a run's approach (`laid_run`), and a
    routed path's bend taken out ran the lane across the household's own privy. The seating judge asks the household's own
    house, beds and fixtures of the run as it will be drawn, where that differs from the run found (`own_clear`)."""
    s = types.SimpleNamespace(M=_tree(), px=lambda ft: ft, _access=types.SimpleNamespace(half=7.0))
    geom = {"house": (100.0, 100.0, 40.0, 28.0), "yard": (100.0, 60.0, 30.0, 20.0), "turn": 180.0, "boxes": {"fixtures": {"privy": (130.0, 30.0, 10.0, 10.0)}}}
    found = [(100.0, 48.0), (100.0, 20.0), (100.0, 0.0)]
    assert tree.own_clear(s, found, geom), "the path as found keeps off the privy"
    across = [(100.0, 48.0), (140.0, 20.0), (140.0, 0.0)]
    assert not tree.own_clear(s, across, geom), "...a leg through it does not"
    assert tree.own_clear(s, [(100.0, 48.0), (100.0, 0.0), (100.0, 0.0)], geom), "a last leg of no length passes unasked"
    judge = tree.seating_judge(s)
    assert judge(found, geom), "drawn as found: judged by the tree alone"
    monkeypatch.setattr(tree, "laid_run", lambda base, M, run: across)
    assert not judge(found, geom), "drawn across its own privy: refused"


def test_a_corridor_whose_drawn_form_crosses_another_homestead_is_refused(monkeypatch) -> None:  # noqa: ANN001
    """Feature 318 (the reference at 40 households, seed 25): the squaring dropped a bend in a channel and the drawn chord ran
    through a neighbor's privy - the reserved legs had cleared the standing homesteads, the drawn ones were never asked. The
    judge asks `access.standing_clear` of the run as drawn (`others_clear`) where it differs from the run found."""
    from l7r.diagram.settlement.rolling import access as A

    s = types.SimpleNamespace(M=_tree(), px=lambda ft: ft, _access=types.SimpleNamespace(half=7.0))
    geom = {"house": (100.0, 100.0, 40.0, 28.0), "yard": (100.0, 60.0, 30.0, 20.0), "turn": 180.0, "boxes": {"fixtures": {}}}
    found = [(100.0, 48.0), (100.0, 20.0), (100.0, 0.0)]
    chord = [(100.0, 48.0), (160.0, 0.0)]
    monkeypatch.setattr(A, "standing_clear", lambda s_, a, b: b != (160.0, 0.0) and a != b)
    assert tree.others_clear(s, found) and not tree.others_clear(s, chord)
    assert tree.others_clear(s, [(100.0, 48.0), (100.0, 0.0), (100.0, 0.0)]), "a last leg of no length passes unasked"
    monkeypatch.setattr(tree, "laid_run", lambda base, M, run: chord)
    monkeypatch.setattr(tree, "own_clear", lambda s_, run, g: True)
    assert not tree.seating_judge(s)(found, geom), "drawn through another homestead: refused"
    assert tree.seating_drawn(s)(found) == chord, "the drawing `access.reserve` keeps clear"


def test_a_house_another_is_reached_across_is_owed_its_way_and_never_pruned_of_it() -> None:
    """Feature 317 (Inashiro's glyph-check F1): the walk of a household reached across a neighbor's yard goes on along the
    neighbor's way, so the neighbor's corridor is owed however near the lanes its center stands, and never pruned."""
    M = _tree(houses=[_house(300.0, 100.0)], access_corridors=[{"pts": [[300.0, 80.0], [300.0, 0.0]], "of": [300.0, 100.0]}])
    M["lanes"] += [{"pts": [[0.0, 0.0], [260.0, 60.0]], "w": 3}]
    assert tree.owed(M) == [0], "every household's way is owed, an ordinary lane reaching its house or not (feature 318)"
    M["houses"].append({**_house(300.0, 400.0), "reached_across": [300.0, 100.0], "passage_depth": 1})
    assert tree.passage_anchors(M) == [(300.0, 100.0)] and tree.owed(M) == [0], "...and still when another household is reached across it"
    M["lanes"].append({"pts": [[300.0, 80.0], [300.0, 0.0]], "w": 3, "role": ACCESS_ROLE, "of": [300.0, 100.0]})
    assert tree.prune_the_tree(_S(M)) == 0 and any(ln.get("role") == ACCESS_ROLE for ln in M["lanes"]), "its way is not pruned"


def test_a_corridor_is_judged_beside_another_as_the_walker_reads_it() -> None:
    """`tree.walked_shadows` (feature 318, Inashiro): two records met end to end, each beside a third way for under a pitch,
    are one way beside it for more - the doubled band the web's joint pass left standing as one record."""
    beside = [(0.0, 25.0), (120.0, 25.0)]  # 25 ft off: a record of 60 ft is beside it for under 77 ft, the two together 120
    halves = [{"pts": [[0.0, 0.0], [60.0, 0.0]]}, {"pts": [[60.0, 0.0], [120.0, 0.0]]}]
    lanes = [{"pts": [list(q) for q in beside]}, *halves]
    assert not tree.tree_shadows([[(float(x), float(y)) for x, y in ln["pts"]] for ln in lanes]), "record by record: no band"
    assert tree.walked_shadows(lanes), "as walked: 120 ft beside it"
    assert not tree.walked_shadows([{"pts": [[0.0, 200.0], [120.0, 200.0]]}, *halves])


def test_an_ordinary_lane_beside_a_tree_lane_past_a_pitch_defers_at_the_middle_of_its_stretch() -> None:
    """`tree.tree_shadow_cuts` in `tree_faults` (feature 318, Sawada): an ordinary lane running beside a tree lane past a pitch
    is cut at the middle of its stretch beside it - the tree is never cut; under a pitch, or two ordinary lanes, nothing."""
    lanes = [
        {"pts": [[0.0, 0.0], [300.0, 0.0]], "role": ACCESS_ROLE, "w": 3.0},
        {"pts": [[100.0, 20.0], [260.0, 20.0], [260.0, 200.0]], "w": 5.0},
    ]
    faults = tree.tree_faults({"lanes": lanes})
    assert any(i == 1 and abs(q[1] - 20.0) < 1e-6 and 170.0 <= q[0] <= 190.0 for i, q in faults), faults
    short = [lanes[0], {"pts": [[100.0, 20.0], [140.0, 20.0], [140.0, 200.0]], "w": 5.0}]
    assert not tree.tree_shadow_cuts(short, [[(float(x), float(y)) for x, y in ln["pts"]] for ln in short])
    plain = [{**lanes[0], "role": None}, lanes[1]]
    assert not tree.tree_shadow_cuts(plain, [[(float(x), float(y)) for x, y in ln["pts"]] for ln in plain])


def test_a_corridor_zigzagging_across_a_joint_is_read() -> None:
    """Feature 328, Kuwabata: the access lane rounding a forecourt's corner onto its neighbor's house lane's end - each
    record bends like a path, the two walked as one do not. Only a joint the last lane makes is asked."""
    from l7r.diagram.hamletgen.ways.tree import zigzag_joint

    house_lane = {"pts": [[3868.7, 1760.0], [3798.9, 1693.7], [3717.9, 1536.9]], "w": 3.0, "role": "access"}
    run = {"pts": [[4042.0, 1765.8], [3918.9, 1808.7], [3848.9, 1783.7], [3868.7, 1760.0]], "w": 3.0, "role": "access"}
    assert zigzag_joint([house_lane, run])
    straight = {"pts": [[3990.0, 1880.0], [3918.9, 1808.7], [3868.7, 1760.0]], "w": 3.0, "role": "access"}
    assert not zigzag_joint([house_lane, straight])
    assert not zigzag_joint([run, house_lane, {"pts": [[0.0, 0.0], [50.0, 0.0]], "w": 3.0, "role": "access"}]), "a joint the last lane does not make"


def test_a_corridor_the_knot_pass_would_gather_into_a_zigzag_is_read() -> None:
    """Feature 328, Kuwabata as judged: the access lane's foot stands on its neighbor's house lane 5 ft short of that lane's
    door end - a T as judged, which the knot pass gathers onto the door end, a Z. An end with no other end in reach, or a
    gather that walks straight, is not one."""
    from l7r.diagram.hamletgen.ways.tree import gathered_zigzag

    house_lane = {"pts": [[3868.7, 1760.0], [3798.9, 1693.7], [3717.9, 1536.9]], "w": 3.0, "role": "access"}
    run = {"pts": [[4042.0, 1765.8], [3918.9, 1808.7], [3848.9, 1783.7], [3865.0, 1756.5]], "w": 3.0, "role": "access"}
    assert gathered_zigzag([house_lane, run])
    assert gathered_zigzag([house_lane, {**run, "pts": [*run["pts"][:-1], [3868.7, 1760.0]]}]), "as it stands"
    far = {"pts": [[4042.0, 1765.8], [3918.9, 1808.7], [3848.9, 1783.7], [3700.0, 1900.0]], "w": 3.0, "role": "access"}
    assert not gathered_zigzag([house_lane, far])
    straight = {"pts": [[3990.0, 1880.0], [3918.9, 1808.7], [3866.0, 1757.0]], "w": 3.0, "role": "access"}
    assert not gathered_zigzag([house_lane, straight])
    assert not gathered_zigzag([house_lane, {"pts": [[1.0, 1.0]], "w": 3.0}])
