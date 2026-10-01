"""`hamletgen/ways/last_resort.py`: the settle's last resort drops ORDINARY lanes only, and what only the tree could mend -
or a farmhouse or the reserved field left unreached - is refused by name (feature 287, FR-005; research R12's caveat on
ways W01 / W03, homes H16). Each case on constructed lanes, the violating one included."""

import pytest

from l7r.diagram.hamletgen.ways import corridors as co
from l7r.diagram.hamletgen.ways import last_resort as lr
from l7r.diagram.hamletgen.ways import law, settle

from .test_settle import _GEN, _S, BROOK, CONN, _c, _over_and_back_on_the_tree

DOUBLED_BACK = [(0.0, 2.0), (0.0, 200.0), (5.0, 150.0)]
"""An ordinary lane that runs on 200 ft and doubles back - a hook no round is given the chance to mend at `rounds=0`."""


def _no_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    """The last resort's re-asked steps as no-ops, so a case isolates its drops and its refusal."""
    for name in ("settle_joins", "settle_reach", "settle_defer", "settle_network", "settle_fragments", "prune_the_tree", "settle_widths", "settle_husks"):
        monkeypatch.setattr(lr, name, lambda s: 0)


def test_the_last_resort_drops_what_the_rounds_could_not_mend() -> None:
    """FR-005: when the rounds run out, an ordinary lane still breaking a rule goes whole - never kept as the least bad."""
    s = _S([CONN, DOUBLED_BACK])
    got = settle.settle_the_web(s, rounds=0)
    assert got["dropped"] == 1 and len(s.M["lanes"]) == 1
    assert lr.lane_violators(s) == []


def test_every_per_lane_rule_names_its_violator() -> None:
    lanes = [CONN, DOUBLED_BACK, [(900.0, 0.0), (900.0, 100.0), (1000.0, 100.0), (1000.0, 0.0)], [(50.0, 150.0), (120.0, 10.0), (153.6, 0.4)], [(0.0, 0.0), (160.0, 0.0)]]
    s = _S(lanes, houses=[(40.0, 320.0)], streams=[{"poly": [[950.0, -500.0], [950.0, 500.0]], "w": 6.0}], meta={"ftpx": 1.0, "brook_fords": [[950.0, 0.0], [950.0, 100.0]]})
    bad = lr.lane_violators(s)
    assert 1 in bad and 2 in bad and 0 not in bad
    # ...and a way out over the brook and back names every ordinary lane that crosses it
    out = _S(
        [_c((50.0, 0.0), (-1000.0, 0.0)), [(50.0, 0.0), (50.0, 100.0)], [(50.0, 100.0), (150.0, 100.0), (150.0, 300.0), (50.0, 300.0)]],
        houses=[(40.0, 320.0)],
        streams=[BROOK],
        meta={"ftpx": 1.0, "brook_fords": [[100.0, 100.0], [100.0, 300.0]]},
    )
    assert 2 in lr.lane_violators(out)


def test_the_last_resort_names_an_ordinary_lane_the_tree_faults(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _S([CONN, [(-100.0, 0.0), (-100.0, 170.0)]])
    s.M["lanes"].append({"pts": [[-50.0, 0.0], [-50.0, 100.0]], "w": 3, "role": co.ACCESS_ROLE})
    monkeypatch.setattr(lr, "tree_faults", lambda M: [(1, (0.0, 0.0)), (2, (0.0, 0.0))])
    assert lr.lane_violators(s) == [1], "the ordinary lane, never the tree's"


def test_the_last_resort_never_names_a_tree_lane_even_where_only_the_tree_carries_a_way_out_over_and_back() -> None:
    """The violating case R12 named: a household's way out over the brook and back carried on TREE lanes alone. The last
    resort used to drop them (`lane_violators` named the tree's carriers); it names none now."""
    s = _over_and_back_on_the_tree()
    assert law.way_outs_crossing(s.M) and all(co.is_tree(s.M["lanes"][i]) for i, _k, _y in law.way_out_carriers(s.M)), "the fixture provokes it on the tree"
    assert lr.lane_violators(s) == [] and lr.ordinary_carriers(s.M) == []


def test_a_way_out_only_the_tree_carries_after_the_last_resort_is_refused_not_dropped(monkeypatch: pytest.MonkeyPatch) -> None:
    """FR-005: a way out over the brook and back left on tree lanes when the rounds run out is refused by name - the map
    is not produced - and no tree lane is dropped to mend it (before: every carrier dropped, the house left unreached
    recorded in `meta.roll_failures`)."""
    s = _over_and_back_on_the_tree()
    _no_steps(monkeypatch)
    tree = [dict(ln) for ln in s.M["lanes"]]
    with pytest.raises(lr.WebRefused, match="way out crosses the brook and back on lanes 1 \\(way target\\), 2 \\(field way\\)"):
        settle.settle_the_web(s, rounds=0)
    assert s.M["lanes"] == tree, "no tree lane dropped"


def test_an_ordinary_lane_goes_and_a_tree_lane_still_breaking_a_rule_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ordinary lane breaking a rule is dropped; the tree lane breaking one (a doubled-back corridor) is kept, and the
    web refused naming it."""
    s = _S([CONN, DOUBLED_BACK, ([(300.0, 2.0), (300.0, 200.0), (305.0, 150.0)], {})])
    s.M["lanes"][2]["role"] = co.ACCESS_ROLE
    _no_steps(monkeypatch)
    with pytest.raises(lr.WebRefused, match="lanes 1 \\(access\\) still break a rule"):
        lr.last_resort(s)
    assert [ln.get("role") for ln in s.M["lanes"]] == [None, co.ACCESS_ROLE], "the ordinary lane dropped, the tree lane kept"


def test_an_ordinary_lane_left_carrying_a_way_out_after_the_steps_goes(monkeypatch: pytest.MonkeyPatch) -> None:
    """A way out over the brook and back the re-asked steps leave on an ORDINARY lane loses that lane, and the resort is
    asked again: the stub it left serving nothing goes on the next pass, and then it settles."""
    s = _S(
        [_c((50.0, 0.0), (-1000.0, 0.0)), [(50.0, 0.0), (50.0, 100.0)], [(50.0, 100.0), (150.0, 100.0), (150.0, 300.0), (50.0, 300.0)]],
        houses=[(40.0, 320.0)],
        streams=[BROOK],
        meta={"ftpx": 1.0, "brook_fords": [[100.0, 100.0], [100.0, 300.0]]},
    )
    _no_steps(monkeypatch)
    real, first = lr.lane_violators, [True]

    def violators(s: _S) -> list[int]:  # the first drop pass sees nothing, as if the steps had just laid the carrier
        if first:
            first.clear()
            return []
        return real(s)

    monkeypatch.setattr(lr, "lane_violators", violators)
    assert lr.ordinary_carriers(s.M) == [2]
    assert lr.last_resort(s) == 2 and law.way_outs_crossing(s.M) == [] and len(s.M["lanes"]) == 1


def test_the_last_resort_is_bounded_and_refuses_what_it_could_not_settle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Whatever the steps between passes do, the resort asks `LAST_RESORT_PASSES` times at most and then refuses."""
    s = _S([CONN])
    _no_steps(monkeypatch)
    calls = iter([[], [1]] * lr.LAST_RESORT_PASSES)  # the drop loop sees nothing; the settled check always something
    monkeypatch.setattr(lr, "lane_violators", lambda s: next(calls))
    monkeypatch.setattr(lr, "ordinary_carriers", lambda M: [])
    refused: list[int] = []
    monkeypatch.setattr(lr, "refuse_unmended", lambda s: refused.append(1))
    assert lr.last_resort(s) == 0 and refused == [1]
    assert next(calls, None) is None, "every pass asked"


def test_a_settled_web_that_leaves_a_farmhouse_unreached_is_refused() -> None:
    """Ways W01: a farmhouse the web does not reach is refused where the web settles - never recorded on the map."""
    s = _S([CONN], houses=[(300.0, 400.0)], meta=dict(_GEN))
    assert law.unreached_houses(s.M), "the violating case"
    with pytest.raises(lr.WebRefused, match="1 farmhouse\\(s\\) stand off the connected way network, at \\[\\(300, 400\\)\\]"):
        settle.settle_the_web(s)
    lr.refuse_unreached({**s.M, "houses": [{"x": 0.0, "y": 30.0, "w": 40.0, "h": 28.0}]})  # a reached house passes


def test_the_reserved_field_left_unreached_is_refused_and_an_unreserved_one_is_not() -> None:
    """Ways W03: the field the seating reserved a corridor to is refused unreached; with no reservation the seating has
    already refused the margin (`homesteads.stages.reserve_field_corridor`), and this rule does not name it."""
    field = [[200.0, -300.0], [500.0, -300.0], [500.0, 300.0], [200.0, 300.0]]
    M = {"lanes": [{"pts": [[0.0, 300.0], [0.0, 1000.0]], "connector": True}], "houses": [], "meta": dict(_GEN), "streams": [BROOK], "fields": [{"outline": field}]}
    assert law.field_unreached(M)
    lr.refuse_unreached(M)
    with pytest.raises(lr.WebRefused, match="the field its reserved corridor runs to is reached by no way"):
        lr.refuse_unreached({**M, "access_corridors": [{"pts": [[195.0, 150.0], [0.0, 150.0]], "field": True}]})


# ---- the settle's exit is a guarantee: a still round is asked the whole law ------------------------------------------


def _strip_doubled_on_the_connector() -> _S:
    """Cohort seed 14 with the straggler footpaths off, in small: the connector's start carried 41 ft off the strip, its first
    leg back through the strip's foot, and the exit strip drawn on along that leg to the start - a doubled tail and a needle
    join between two TREE lanes, which no repair cuts, so a round changes nothing with both standing."""
    s = _S([_c((1.0, -41.0), (0.0, 0.0), (-1000.0, 0.0))], meta=dict(_GEN))
    s.M["lanes"].append({"pts": [[300.0, 0.0], [1.0, 0.0], [1.0, -41.0]], "w": 3, "worn": True, "role": co.STRIP_ROLE})
    return s


def test_a_web_gone_still_with_a_rule_only_the_tree_breaks_is_refused_by_name_never_shipped(monkeypatch: pytest.MonkeyPatch) -> None:
    s = _strip_doubled_on_the_connector()
    assert {"doubled_tails", "needle_joins"} <= set(settle.unsettled(s.M)), "the violating case, the whole law asked"
    with pytest.raises(lr.WebRefused, match="lanes 1 \\(exit strip\\) still break a rule.*the web still breaks .*doubled_tails, needle_joins"):
        settle.settle_the_web(s)
    assert [ln.get("role") for ln in s.M["lanes"]] == [None, co.STRIP_ROLE], "no tree lane dropped"
    # ...and without the exit's question the still round shipped it: the hole this closes
    shipped = _strip_doubled_on_the_connector()
    monkeypatch.setattr(settle, "unsettled", lambda M, ground=None: {})
    got = settle.settle_the_web(shipped)
    assert got["rounds"] == 1 and got["changed"] == 0 and law.doubled_tails(shipped.M) == [1]


def test_a_web_gone_still_with_an_ordinary_lane_breaking_a_rule_against_the_tree_is_repaired(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ordinary lane's needle on the connector, with every repair step idle so the first round changes nothing: the
    exit asks the law, the last resort drops the ordinary lane, and what ships keeps it."""
    needle = [(-50.0, 150.0), (-120.0, 10.0), (-153.6, 0.4)]
    s = _S([CONN, needle])
    assert law.needle_joins(s.M["lanes"]), "the violating case"
    monkeypatch.setattr(settle, "STEPS", (settle.settle_husks,))
    got = settle.settle_the_web(s)
    assert got["rounds"] == 1 and got["changed"] == 0 and got["dropped"] == 1
    assert settle.unsettled(s.M) == {} and len(s.M["lanes"]) == 1 and s.M["lanes"][0]["connector"]
