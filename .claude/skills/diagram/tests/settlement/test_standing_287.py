"""The registry of what stands (feature 287 M8): every footprint recorded through one indexed registry that answers
"may this kind lie on what is already here" by the overlap matrix, and refuses by name at record time."""

from __future__ import annotations

import copy
import pickle

import pytest

from l7r.diagram.overlap import matrix_extents, matrix_violations
from l7r.diagram.overlap.registry import (
    Kept,
    OverlapRefused,
    Standing,
    StandingList,
    StandingManifest,
    element_extents,
    elements,
    forbidden_segment,
    pair_forbidden,
    pair_permitted,
)
from l7r.diagram.overlap.registry import (
    tested as is_tested,
)
from l7r.diagram.overlap.reserved import Reservations, poly_seg_gap, seat_radius
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom.indexes import Indexed

GARDEN = {"x": 100.0, "y": 100.0, "w": 20.0, "h": 20.0, "rot": 0.0, "of": [100.0, 60.0]}
YARD = {"x": 100.0, "y": 100.0, "w": 40.0, "h": 20.0, "rot": 0.0, "of": [100.0, 60.0]}
HOUSE = {"x": 100.0, "y": 60.0, "w": 40.0, "h": 24.0, "rot": 0.0}


def _registry(strict: bool = True) -> tuple[Standing, StandingManifest]:
    st = Standing({}, 1000.0, 1000.0)
    M = StandingManifest(st, {"meta": {"ftpx": 1.0}, "houses": [], "gardens": [], "lanes": []})
    st.M = M
    st.strict = strict
    return st, M


# ---- the shared extractor and pair test --------------------------------------------------------------------------------


def test_which_keys_are_recorded_and_how_a_value_splits_into_records() -> None:
    assert is_tested("houses") and is_tested("lanes") and not is_tested("village_groves") and not is_tested("labels") and not is_tested("no_such_key")
    assert elements("road", [[0, 0], [10, 0]]) == [[[0, 0], [10, 0]]] and elements("road", None) == []
    assert elements("governor_mansion", {"x": 1}) == [{"x": 1}] and elements("houses", [HOUSE]) == [HOUSE] and elements("houses", None) == []


def test_the_matrix_on_a_finished_map_reads_the_same_extractor_and_pair_test() -> None:
    """`matrix_violations` / `matrix_extents` over `element_extents` and `pair_forbidden`: a garden on a stranger's house is
    named, the same garden on its own household's yard is not (an annex of one household)."""
    M = {"meta": {"W": 400, "H": 400}, "houses": [HOUSE], "gardens": [dict(GARDEN, of=[500.0, 500.0])]}
    assert len(matrix_extents(M)) == 2 and matrix_violations(M) == []  # apart: nothing
    M["gardens"][0]["y"] = 60.0
    assert [v[:2] for v in matrix_violations(M)] == [("houses", "gardens")]
    own = {"meta": {"W": 400, "H": 400}, "threshing_yards": [YARD], "gardens": [GARDEN]}
    assert matrix_violations(own) == [], "two annexes of one household abut"
    a, b = element_extents("gardens", GARDEN, {})[0], element_extents("threshing_yards", dict(YARD, of=[9.0, 9.0]), {})[0]
    assert not pair_permitted(a, b, set()) and pair_forbidden(a, b, set())
    far = element_extents("gardens", dict(GARDEN, x=900.0), {})[0]
    assert not pair_forbidden(a, far, set()), "boxes apart: no overlap"
    from l7r.diagram.overlap.registry import box_of

    assert not pair_permitted(far, b, set()), "a stranger's garden and yard: forbidden where they meet"
    assert not pair_forbidden(far, b, set()) and not pair_forbidden(far, b, set(), box_of(far[1]), box_of(b[1])), "boxes apart, derived or handed in"
    st = Standing({})
    priv = {"x": 100.0, "y": 100.0, "r": 8, "private": True}
    st.record("wells", priv)
    assert st.priv == {(100.0, 100.0)}
    st.forget("wells", priv)
    assert st.priv == set(), "a private well taken away takes its permission with it"
    well = element_extents("wells", priv, {})[0]
    assert pair_permitted(well, a, {(100.0, 100.0)}), "a trade work's private well"


# ---- the registry ------------------------------------------------------------------------------------------------------


def test_a_record_the_matrix_forbids_on_what_stands_raises_by_name_and_is_not_recorded() -> None:
    st, M = _registry()
    M["houses"].append(HOUSE)
    assert st.admits("gardens", dict(GARDEN, of=None)) and len(st) == 1
    bad = dict(GARDEN, y=60.0, of=None)
    assert not st.admits("gardens", bad)
    with pytest.raises(OverlapRefused, match="gardens would be recorded on a houses") as exc:
        M["gardens"].append(bad)
    assert exc.value.key == "gardens" and exc.value.other == "houses" and M["gardens"] == [] and len(st) == 1
    again = pickle.loads(pickle.dumps(exc.value))
    assert (again.key, again.other, again.at) == (exc.value.key, exc.value.other, exc.value.at), "raised across a process pool"


def test_a_non_strict_registry_records_what_the_matrix_forbids_and_answers_all_the_same() -> None:
    st, M = _registry(strict=False)
    M["houses"].append(HOUSE)
    M["houses"].append(dict(HOUSE))  # on the first: recorded, as the frozen town generators always drew
    assert len(M["houses"]) == 2 and not st.admits("houses", dict(HOUSE))


def test_a_records_own_pieces_are_judged_against_each_other_and_off_canvas_pieces_against_nothing() -> None:
    st, M = _registry()
    M["lanes"].append({"pts": [[-9000.0, -9000.0], [-8000.0, -9000.0]], "w": 6})  # wholly off the canvas: indexed nowhere
    assert st.conflicts("lanes", {"pts": [[-9000.0, -9000.0], [-8000.0, -9000.0]], "w": 6}) == []
    M["lanes"].pop()
    kido = {"x": 10.0, "y": 10.0, "parts": [[[0, 0], [10, 0], [10, 10], [0, 10]], [[5, 5], [15, 5], [15, 15], [5, 15]]], "guard": [[5, 5], [15, 5], [15, 15], [5, 15]]}
    assert st.conflicts("kido", kido) == [], "the pieces of one gate share one id"
    assert st.conflicts("houses", {"x": 1.0}) == [], "a record with no drawn extent covers nothing"


def test_the_pieces_of_one_record_that_the_matrix_forbids_to_overlap_are_named() -> None:
    st, _M = _registry()
    # no single key's record draws two pieces the matrix forbids to meet today (a gate's guard box is excused by its id), so
    # the extractor is stood in for: two extents of one record, a house and a lane, lying on each other
    st.extents = lambda key, o: [("houses", [(0, 0), (10, 0), (10, 10), (0, 10)], None, None), ("lanes", [(2, 2), (8, 2), (8, 8), (2, 8)], None, None)]  # type: ignore[method-assign]
    assert st.conflicts("houses", {}) == [("houses", "lanes", 5, 5)]


def test_a_rewrite_is_judged_without_the_record_it_replaces() -> None:
    st, M = _registry()
    M["lanes"].append(st.kept("lanes", {"pts": [[0.0, 0.0], [200.0, 0.0]], "w": 6}))
    ln = M["lanes"][0]
    assert isinstance(ln, Kept) and not isinstance(pickle.loads(pickle.dumps(ln)), Kept)
    assert st.admits("lanes", {**ln, "pts": [[0.0, 0.0], [300.0, 0.0]]}, ignore=ln)
    M["houses"].append(dict(HOUSE, x=250.0, y=0.0))
    with pytest.raises(OverlapRefused):
        ln["pts"] = [[0.0, 0.0], [300.0, 0.0]]  # the write asks the registry, and it is refused
    assert ln["pts"] == [[0.0, 0.0], [200.0, 0.0]], "the refused write leaves the record as it was"
    ln["pts"] = [[0.0, 0.0], [150.0, 0.0]]
    ln.update(role="web", w=5)
    assert ln["role"] == "web" and st.admits("gardens", dict(GARDEN, x=180.0, y=0.0, of=None)), "the shortened lane is recorded again"
    loose = st.kept("lanes", {"pts": [[0.0, 0.0], [1.0, 0.0]]})
    loose["pts"] = [[0.0, 0.0], [260.0, 0.0]]  # not on the map: nothing to ask
    assert loose["pts"][1] == [260.0, 0.0]


def test_hold_keeps_a_part_standing_until_it_is_released() -> None:
    st, M = _registry()
    pocket = st.hold("wells", {"x": 100.0, "y": 100.0, "r": 8, "vr": 12.4})
    assert not st.admits("lanes", {"pts": [[0.0, 100.0], [200.0, 100.0]], "w": 6})
    st.resync()
    assert not st.admits("lanes", {"pts": [[0.0, 100.0], [200.0, 100.0]], "w": 6}), "a resync keeps a hold though no list holds it"
    st.release("wells", pocket)
    assert st.admits("lanes", {"pts": [[0.0, 100.0], [200.0, 100.0]], "w": 6})
    assert M["lanes"] == []


def test_forbidding_lists_what_a_way_may_not_lie_on() -> None:
    st, M = _registry()
    M["houses"].append(HOUSE)
    M["lanes"].append({"pts": [[0.0, 0.0], [10.0, 0.0]], "w": 6})
    kinds = [e[0] for e in st.forbidding("lanes")]
    assert kinds == ["houses"], "a house walls a way; another way does not"
    st.reserved.reserve_seats([(500.0, 500.0)], 22.0, 15.0)
    walls = [e for e in st.forbidding("lanes") if e[0] == "wood seat"]
    assert len(walls) == 1 and all(abs(((x - 500) ** 2 + (y - 500) ** 2) ** 0.5 - 15.0 / 0.9659) < 0.01 for x, y in walls[0][1])
    assert [e[0] for e in st.forbidding("houses")] == ["houses", "lanes"]


def test_resync_records_again_what_a_stage_reshaped_forgets_what_left_and_takes_in_a_stray() -> None:
    st, M = _registry()
    M["houses"].append(dict(HOUSE))
    M["houses"][0]["x"] = 300.0  # reshaped in place, behind the registry's back
    assert not st.admits("gardens", dict(GARDEN, y=60.0, of=None)), "stale: the registry still holds the old house"
    st.resync()
    assert not st.admits("gardens", dict(GARDEN, x=300.0, y=60.0, of=None)) and st.admits("gardens", dict(GARDEN, y=60.0, of=None))
    stray = [dict(HOUSE, x=600.0)]
    dict.__setitem__(M, "farm_sheds", stray)  # a list the manifest never wrapped
    dict.__setitem__(M, "houses", [])  # ...and the house gone by a rebind the registry did not see
    st.resync()
    assert len(st) == 1 and not st.admits("gardens", dict(GARDEN, x=600.0, y=60.0, of=None))
    before = len(st._ext)
    st.resync()
    assert len(st._ext) == before, "nothing moved: nothing recorded again"


def test_forbidden_segment_names_the_first_segment_the_matrix_refuses() -> None:
    st, M = _registry()
    M["houses"].append(HOUSE)
    assert forbidden_segment(M, "lanes", [(0.0, 0.0), (50.0, 0.0), (100.0, 60.0)], 3.0) == 1
    assert forbidden_segment(M, "lanes", [(0.0, 0.0), (50.0, 0.0)], 3.0) is None
    assert forbidden_segment({"houses": [HOUSE]}, "lanes", [(0.0, 60.0), (200.0, 60.0)], 3.0) is None, "a bare manifest has no registry"


# ---- the recording containers ------------------------------------------------------------------------------------------


def test_every_list_mutation_records_or_forgets() -> None:
    st, M = _registry()
    L = M["gardens"]
    assert isinstance(L, StandingList)
    a, b, c = (dict(GARDEN, x=float(x), of=None) for x in (100, 300, 500))
    L.extend([a])
    L.insert(0, b)
    L += [c]
    assert len(st) == 3 and L.version > 0
    L.remove(a)
    assert L.pop() is c and len(st) == 1
    L[0] = dict(a)
    L[0:1] = [dict(b)]
    del L[0]
    assert len(st) == 0
    L.append(a)
    L *= 1
    assert len(L) == 1
    L *= 0
    assert L == [] and len(st) == 0
    L.append(a)
    L.clear()
    assert len(st) == 0
    L.append(a)
    del L[0:1]
    assert len(st) == 0
    assert type(pickle.loads(pickle.dumps(StandingList(Standing({}), "gardens", [a])))) is Indexed
    L.append(a)
    with pytest.raises(OverlapRefused):
        L *= 2  # the repeat stands on its original
    assert len(L) == 1, "the refused repeat is not added"


def test_a_refused_item_set_puts_the_old_items_back() -> None:
    st, M = _registry()
    M["houses"].append(HOUSE)
    M["gardens"].append(dict(GARDEN, x=300.0, of=None))
    with pytest.raises(OverlapRefused):
        M["gardens"][0:1] = [dict(GARDEN, x=500.0, of=None), dict(GARDEN, y=60.0, of=None)]
    assert M["gardens"][0]["x"] == 300.0 and not st.admits("houses", dict(HOUSE, x=300.0, y=100.0)), "the old bed stands again"


def test_the_manifest_records_whole_values_rebinds_and_single_records() -> None:
    st, M = _registry()
    M["road"] = [[0.0, 0.0], [400.0, 0.0]]
    assert not st.admits("houses", dict(HOUSE, y=0.0))
    M["road"] = None
    assert st.admits("houses", dict(HOUSE, y=0.0)), "the road taken away is forgotten"
    M["theater_stage"] = dict(HOUSE, x=700.0)  # a single record stored as a dict
    assert not st.admits("houses", dict(HOUSE, x=700.0))
    M.update(houses=[HOUSE])
    assert isinstance(M["houses"], StandingList) and not st.admits("gardens", dict(GARDEN, y=60.0, of=None))
    M["houses"] = [dict(HOUSE, x=300.0)]
    assert st.admits("gardens", dict(GARDEN, y=60.0, of=None)), "the rebind forgot the old list"
    assert M.setdefault("wells", []) is M["wells"] and isinstance(M["wells"], StandingList)
    assert M.setdefault("houses", []) is M["houses"]
    M["notes"] = ["free text"]
    assert M.pop("notes") == ["free text"] and M.pop("absent", 7) == 7
    del M["houses"]
    assert "houses" not in M and st.admits("houses", dict(HOUSE, x=300.0))
    assert M.pop("theater_stage")["x"] == 700.0


def test_a_refused_rebind_restores_what_stood() -> None:
    st, M = _registry()
    M["houses"] = [HOUSE]
    M["gardens"] = [dict(GARDEN, x=400.0, of=None)]
    with pytest.raises(OverlapRefused):
        M["gardens"] = [dict(GARDEN, y=60.0, of=None)]
    assert M["gardens"][0]["x"] == 400.0 and not st.admits("houses", dict(HOUSE, x=400.0, y=100.0))
    snap = copy.deepcopy(M)
    assert type(snap) is dict and type(pickle.loads(pickle.dumps(M))) is dict, "a copy is a plain manifest"


def test_a_settlement_records_through_its_registry_and_asks_it() -> None:
    s = Settlement(W=600, H=600, seed=1)
    assert isinstance(s.M, StandingManifest) and s.standing.M is s.M and not s.standing.strict
    s.M["houses"].append(HOUSE)
    assert not s.admits("gardens", dict(GARDEN, y=60.0, of=None)) and s.admits("gardens", dict(GARDEN, of=None))


# ---- the seating's reservations ----------------------------------------------------------------------------------------


def test_a_reserved_corridor_is_kept_off_by_built_ground_but_its_own_households() -> None:
    res = Reservations()
    assert not res and res.conflicts("houses", HOUSE, element_extents("houses", HOUSE, {})) == []
    res.reserve_corridor((0.0, 100.0), (400.0, 100.0), 7.0, owner=[100.0, 60.0])
    assert res
    shed = {"x": 300.0, "y": 100.0, "w": 10.0, "h": 6.0, "rot": 0.0}
    assert [c[1] for c in res.conflicts("farm_sheds", shed, element_extents("farm_sheds", shed, {}))] == ["access corridor"]
    own = dict(shed, of=[100.0, 60.0])
    assert res.conflicts("farm_sheds", own, element_extents("farm_sheds", own, {})) == [], "its own household's part"
    lane = {"pts": [[0.0, 100.0], [400.0, 100.0]], "w": 3}
    assert res.conflicts("lanes", lane, element_extents("lanes", lane, {})) == [], "a way runs along it"
    beside = dict(shed, y=120.0)
    assert res.conflicts("farm_sheds", beside, element_extents("farm_sheds", beside, {})) == []
    assert res.box_covers(90.0, 90.0, 110.0, 110.0, 0.0) and not res.box_covers(90.0, 200.0, 110.0, 220.0, 0.0)
    res.release_corridors()
    assert not res


def test_a_reserved_seat_is_kept_off_by_occupiers_wells_and_lanes() -> None:
    res = Reservations()
    res.reserve_seats([(100.0, 100.0), (400.0, 400.0)], 22.0, 15.0)
    assert seat_radius("houses", HOUSE, 22.0) == pytest.approx(0.5 * (40**2 + 24**2) ** 0.5 + 13.0)
    assert seat_radius("wells", {"x": 0.0, "y": 0.0, "vr": 12.4}, 22.0) == pytest.approx(12.4 + 23.1 + 1.0)
    assert seat_radius("lanes", {}, 22.0) is None and seat_radius("houses", {"x": 1.0}, 22.0) is None
    near = dict(HOUSE, x=100.0, y=130.0)
    assert [c[1] for c in res.conflicts("houses", near, [])] == ["wood seat"]
    lane = {"pts": [[0.0, 110.0], [200.0, 110.0]], "w": 3}
    assert [c[1] for c in res.conflicts("lanes", lane, [])] == ["wood seat"]
    clear = {"pts": [[0.0, 200.0], [200.0, 200.0]], "w": 3}
    assert res.conflicts("lanes", clear, []) == [] and res.conflicts("torii", [1.0, 2.0], []) == []
    assert res.box_covers(90.0, 90.0, 95.0, 95.0, 11.0)
    assert res.release_seats_along([(0.0, 400.0), (800.0, 400.0)], 6.0) == [(400.0, 400.0)] and res.seats == [(100.0, 100.0)]
    assert res.release_seats_along([(0.0, 700.0), (800.0, 700.0)], 6.0) == []
    res.release_seats()
    assert not res


def test_the_gap_between_a_ring_and_a_segment() -> None:
    sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert poly_seg_gap(sq, (5.0, 5.0), (50.0, 5.0)) == 0.0, "an end inside"
    assert poly_seg_gap(sq, (-5.0, 5.0), (15.0, 5.0)) == 0.0, "through it"
    assert poly_seg_gap(sq, (0.0, 20.0), (10.0, 20.0)) == pytest.approx(10.0)
