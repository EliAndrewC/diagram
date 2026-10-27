"""`hamletgen/ways/lay.py`: a candidate lane held to the lane law's end rules BEFORE it is drawn (feature 417 T06) - each end
rule provoked by a candidate among standing lanes, the candidate re-aimed or cut (never a standing lane), or refused."""

import math

import pytest

from l7r.diagram.hamletgen.ways import law
from l7r.diagram.hamletgen.ways.lay import laid_lawfully

from ._settle_builders import _S, CONN, _c


def _with(s: _S, run: list[tuple[float, float]]) -> list[dict]:
    return [*s.M["lanes"], {"pts": [list(q) for q in run], "w": 3}]


def test_a_clean_candidate_is_laid_as_it_came() -> None:
    s = _S([CONN, [(0.0, 0.0), (300.0, 0.0)]], houses=[(150.0, 230.0)])
    run = [(150.0, 200.0), (150.0, 0.0)]
    assert laid_lawfully(s, run) == run
    assert laid_lawfully(s, [(5.0, 5.0)]) is None and laid_lawfully(s, [(5.0, 5.0), (5.0, 5.5)]) is None, "nothing to lay"


def test_a_needle_join_is_re_aimed_as_a_tee_and_the_standing_way_untouched() -> None:
    tread = [(0.0, 0.0), (300.0, 0.0)]
    s = _S([CONN, tread], houses=[(50.0, 180.0)])
    needle = [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)]
    assert law.needle_ends(_with(s, needle))
    got = laid_lawfully(s, needle)
    assert got is not None and got != needle and not law.needle_ends(_with(s, got))
    assert [tuple(q) for q in s.M["lanes"][1]["pts"]] == tread, "the lane drawn is not moved"


def test_a_standing_ends_needle_along_the_candidate_refuses_it() -> None:
    s = _S([CONN, [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)]])
    assert laid_lawfully(s, [(0.0, 0.0), (300.0, 0.0)]) is None, "only the standing lane's move could mend it"


def test_a_fold_at_a_joint_is_re_aimed_and_a_bare_folded_leg_refused() -> None:
    s = _S([CONN, [(0.0, 0.0), (100.0, 0.0)]])
    fold = [(-50.0, 30.0), (50.0, 8.0), (100.0, 0.0)]
    assert law.folded_joint_pairs(_with(s, fold))
    got = laid_lawfully(s, fold)
    assert got is None or not law.folded_joint_pairs(_with(s, got))
    bare = _S([CONN, [(0.0, 150.0), (100.0, 150.0)]])
    assert laid_lawfully(bare, [(100.0, 150.0), (20.0, 170.0)]) is None


def test_a_hairpin_at_the_connector_is_re_aimed() -> None:
    s = _S([_c((2055.3, 25.3), (1408.0, -20.4), (366.5, 35.3), (-1871.9, -62.9))])
    lane = [(2158.0, 457.2), (1957.1, 462.4), (1929.1, 56.4), (2054.3, 40.0), (2055.3, 25.3)]
    assert law.connector_hairpin_ends(_with(s, lane), None)
    got = laid_lawfully(s, lane)
    assert got is None or not law.connector_hairpin_ends(_with(s, got), None)


def test_a_doubled_tail_is_cut_where_it_comes_alongside() -> None:
    s = _S([_c((100.0, 5.0), (300.0, 5.0), (1300.0, 5.0))], houses=[(0.0, 90.0)])
    for run in ([(0.0, 60.0), (100.0, 0.0), (140.0, 2.0)], [(140.0, 2.0), (100.0, 0.0), (0.0, 60.0)]):
        got = laid_lawfully(s, run)
        assert got is not None and len(law.doubled_tails({**s.M, "lanes": _with(s, got)})) == 0, run


def test_a_shallow_crossing_is_cut_at_the_crossing() -> None:
    s = _S([CONN, [(0.0, 0.0), (400.0, 0.0)]])
    s.M["lanes"][1]["role"] = "field way"
    got = laid_lawfully(s, [(300.0, 40.0), (100.0, -25.0)])
    assert got is None or not law.shallow_crossing_at(_with(s, got))


def test_a_changed_candidate_is_asked_of_the_matrix_again() -> None:
    """Inashiro (seed 4) under T06's first cut: a skeleton arm re-aimed as a T ran over a threshing yard the matrix forbids -
    the caller had admitted the arm it handed in, not the one re-aimed."""

    class Refusing(_S):
        def admits_lane(self, pts, width):
            return False

    s = Refusing([CONN, [(0.0, 0.0), (300.0, 0.0)]], houses=[(50.0, 180.0), (150.0, 230.0)])
    assert laid_lawfully(s, [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)]) is None, "re-aimed, then refused"
    assert laid_lawfully(s, [(150.0, 200.0), (150.0, 0.0)]) == [(150.0, 200.0), (150.0, 0.0)], "unchanged: the caller's admission stands"


def test_an_end_reaching_nothing_is_trimmed_to_service_or_not_laid() -> None:
    """The trim the settle's `settle_dangling` gave every ordinary lane, asked at lay: Inashiro's skeleton lane and Kuwabata's
    run, laid reaching nothing, went to the last resort under T06's first cut."""
    s = _S([CONN, [(0.0, 0.0), (300.0, 0.0)]], houses=[(150.0, 230.0)])
    got = laid_lawfully(s, [(150.0, 0.0), (150.0, 200.0), (150.0, 600.0)])
    assert got is not None and got[-1][1] < 600.0, "run on past the house: cut back to it"
    assert laid_lawfully(s, [(250.0, 0.0), (250.0, 120.0)]) is None, "reaching nothing: not laid"


def test_a_third_end_at_a_door_is_cut_back_past_the_doorstep() -> None:
    ends = [[(x, 300.0), (x, 80.0)] for x in (-40.0, 0.0)]
    s = _S([CONN, [(-200.0, 300.0), (200.0, 300.0)], *ends], houses=[(0.0, 50.0)])
    got = laid_lawfully(s, [(40.0, 300.0), (40.0, 80.0)])
    tl = [*s.M["lanes"], {"pts": [list(q) for q in got or []], "w": 3}]
    assert got is None or len(law.fronting_ends({**s.M, "lanes": tl}).get(0, [])) <= law.DOORSTEP_MAX


# ---- each branch of the ask, provoked by the law's own predicate (patched where `lay` looks it up: the `law` package) ----

_DOOR = [(150.0, 200.0), (150.0, 100.0), (150.0, 0.0)]


def _door_settlement() -> _S:
    return _S([CONN, [(0.0, 0.0), (300.0, 0.0)]], houses=[(150.0, 230.0)])


def test_a_fold_with_no_vertex_to_fall_back_to_is_not_laid_and_one_with_a_vertex_is_re_aimed(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _door_settlement()
    monkeypatch.setattr(law, "folded_joint_pairs", lambda tl, blocked=None: [(1, -1, 2, -1)])
    assert laid_lawfully(s, [(150.0, 200.0), (150.0, 0.0)]) is None, "a bare leg folded on a standing way"
    asked: list[list] = []

    def once(tl, blocked=None):  # type: ignore[no-untyped-def]
        asked.append([tuple(q) for q in tl[-1]["pts"]])
        return [(2, 0, 1, 0)] if len(asked) == 1 else []

    monkeypatch.setattr(law, "folded_joint_pairs", once)
    laid_lawfully(s, _DOOR)
    assert len(asked) >= 2 and asked[1] != asked[0], "re-aimed from its last vertex, then asked again"


def test_a_doubled_tail_with_no_way_alongside_to_cut_at_is_not_laid(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _door_settlement()
    monkeypatch.setattr(law, "doubled_tails", lambda M, only=None: [only])
    assert laid_lawfully(s, _DOOR) is None


def test_a_shallow_crossing_the_cut_cannot_mend_is_not_laid(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.hamletgen.ways import squaring

    s = _door_settlement()
    monkeypatch.setattr(law, "shallow_crossing_at", lambda tl: [(2, 0, 1, (150.0, 0.0))])
    monkeypatch.setattr(squaring, "cut_at_shallow_crossing", lambda *a: None)
    assert laid_lawfully(s, _DOOR) is None


def test_a_third_end_wholly_within_the_doorstep_is_not_laid(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _door_settlement()
    monkeypatch.setattr(law, "fronting_ends", lambda M: {0: [(1, -1), (0, -1), (2, -1)]})
    assert laid_lawfully(s, [(150.0, 225.0), (152.0, 225.0)]) is None


def test_one_lane_asked_alone_gets_the_verdict_the_whole_web_gives_it() -> None:
    s = _S([_c((100.0, 5.0), (300.0, 5.0), (1300.0, 5.0)), [(0.0, 60.0), (100.0, 0.0), (140.0, 2.0)], [(-50.0, 0.0), (-50.0, 300.0)]])
    for i in range(len(s.M["lanes"])):
        assert law.doubled_tails(s.M, only=i) == [j for j in law.doubled_tails(s.M) if j == i]
        assert law.dangling_lane_ends(s.M, only=i) == [(j, e) for j, e in law.dangling_lane_ends(s.M) if j == i]


def test_a_doubled_tail_is_cut_where_a_way_runs_alongside(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _S([[(0.0, 0.0)], _c((100.0, 5.0), (300.0, 5.0), (1300.0, 5.0))], houses=[(0.0, 90.0)])  # a lane of one point is passed over
    from l7r.diagram.hamletgen.ways import tails

    asks = iter([True])
    monkeypatch.setattr(law, "doubled_tails", lambda M, only=None: [only] if next(asks, False) else [])
    monkeypatch.setattr(tails, "along_tail", lambda q, op, deg=0.0: 1)  # alongside from the last leg's start
    got = laid_lawfully(s, [(0.0, 60.0), (100.0, 0.0), (140.0, 2.0)])
    assert got is None or got[-1] != (140.0, 2.0), "cut where it came alongside"


def test_a_lane_still_breaking_a_rule_after_its_tries_is_not_laid(monkeypatch: pytest.MonkeyPatch) -> None:
    from l7r.diagram.hamletgen.ways.settle import shapes

    s = _door_settlement()
    monkeypatch.setattr(shapes, "reaimed", lambda seq, *a, **k: seq)  # a re-aim that mends nothing
    monkeypatch.setattr(law, "needle_ends", lambda tl, blocked=None: [(len(tl) - 1, -1, 1, (0.0, 0.0), (1.0, 0.0))])
    assert laid_lawfully(s, _DOOR) is None


def test_a_third_end_reaching_past_the_doorstep_is_cut_back_to_it(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _door_settlement()
    monkeypatch.setattr(law, "fronting_ends", lambda M: {0: [(1, -1), (0, -1), (2, -1)]})
    got = laid_lawfully(s, [(150.0, 0.0), (150.0, 100.0), (150.0, 225.0)])
    assert got is None or math.dist(got[-1], (150.0, 230.0)) > law.DOORSTEP_FT


def test_a_candidate_laid_whole_is_refused_where_it_would_change() -> None:
    """`whole` (feature 417 T06, impl-drift): a link, or the run a link joins, holds its join only as it came - refused rather
    than re-aimed or cut; a lawful one is laid unchanged."""
    tread = [(0.0, 0.0), (300.0, 0.0)]
    s = _S([CONN, tread], houses=[(50.0, 180.0), (150.0, 230.0)])
    assert laid_lawfully(s, [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)], whole=True) is None, "a needle, not re-aimed"
    assert laid_lawfully(s, [(150.0, 200.0), (150.0, 0.0)], whole=True) == [(150.0, 200.0), (150.0, 0.0)]
    assert laid_lawfully(s, [(150.0, 0.0), (150.0, 200.0), (150.0, 600.0)], whole=True) is None, "trimmed to service: changed"


def test_a_run_its_link_joins_is_laid_only_through_the_joint() -> None:
    """`keep` (feature 417 T06, impl-drift): the run a link joins may be trimmed at its far end, never off the point its link
    meets - there the join would no longer hold."""
    s = _S([CONN, [(0.0, 0.0), (300.0, 0.0)]], houses=[(150.0, 230.0)])
    run = [(150.0, 0.0), (150.0, 200.0), (150.0, 600.0)]
    got = laid_lawfully(s, run, keep=(150.0, 0.0))
    assert got is not None and got[0] == (150.0, 0.0) and got[-1][1] < 600.0, "trimmed at its far end, the joint kept"
    assert laid_lawfully(s, run, keep=(150.0, 600.0)) is None, "the joint trimmed away: not laid"


# ---- the gather at lay (feature 417 T06 part D): an end a few feet beside a junction standing moved onto it ----


def test_an_end_beside_a_junction_is_gathered_onto_it() -> None:
    """0081: ends within 25 ft are joined at a single point - the new lane's end moved onto the junction standing, never a
    drawn lane's; an end one point with it (within `_JOINT_FT`) or past the reach is left."""
    s = _S([CONN, [(0.0, 0.0), (300.0, 0.0)], [(150.0, 0.0), (150.0, -200.0)]], houses=[(160.0, 230.0)])
    got = laid_lawfully(s, [(160.0, 200.0), (160.0, 0.0)])  # its foot 10 ft beside the T at (150, 0)
    assert got is not None and got[-1] == (150.0, 0.0), got
    assert [tuple(q) for q in s.M["lanes"][2]["pts"]] == [(150.0, 0.0), (150.0, -200.0)], "the standing lane untouched"
    far = laid_lawfully(s, [(190.0, 200.0), (190.0, 0.0)])  # 40 ft off any junction: no knot
    assert far is not None and far[-1] == (190.0, 0.0)


def test_a_link_and_a_joint_are_never_gathered_and_a_fence_parts_a_knot() -> None:
    from l7r.diagram.hamletgen.ways.lay import gathered_forms

    s = _S([CONN, [(0.0, 0.0), (300.0, 0.0)], [(150.0, 0.0), (150.0, -200.0)]], houses=[(160.0, 230.0)])
    run = [(160.0, 200.0), (160.0, 0.0)]
    assert laid_lawfully(s, run, whole=True) == run, "a link laid as it came"
    assert laid_lawfully(s, run, keep=(160.0, 0.0)) == run, "a run's joint stays where its link meets it"
    assert gathered_forms(s, run, (-1,), lambda a, b, w: True) == [], "ground between: two paths either side of a fence"
    assert gathered_forms(s, [(1.0, 1.0)], (-1,), lambda a, b, w: False) == [] and gathered_forms(s, run, (), lambda a, b, w: False) == []
