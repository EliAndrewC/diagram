"""269 E3 (B04, B17): a way that makes for the field runs on to the bund (research/fields/290, research/homesteads/310).

`hamletgen/ways/bund.py`, `WorkedGround` in `ways/geom.py`, and `meet_end_to_end` in `ways/joints.py`.
"""

import pytest

from l7r.diagram.hamletgen.ways import bund as B
from l7r.diagram.hamletgen.ways.geom import BUND_REACH_FT, WorkedGround, worked_ground

from ._builders import _StubSettlement

_FIELD = [(400.0, 0.0), (600.0, 0.0), (600.0, 200.0), (400.0, 200.0)]
"""A paddy 200 ft square, its west bund at x=400."""


def _field_M() -> dict:
    return {"fields": [{"outline": [list(p) for p in _FIELD], "plot_rings": [[[410.0, 10.0], [590.0, 10.0], [590.0, 190.0], [410.0, 190.0]]]}]}


def test_worked_ground_is_the_edge_of_the_outline_the_dry_plots_and_the_rice() -> None:
    g = WorkedGround([_FIELD])
    assert g.dist((390.0, 100.0)) == pytest.approx(10.0) and g.inside((500.0, 100.0)) and not g.inside((300.0, 100.0))
    assert g.nearest((390.0, 100.0)) == pytest.approx((400.0, 100.0))
    empty = WorkedGround([])
    assert empty.dist((0.0, 0.0)) == float("inf") and empty.nearest((0.0, 0.0)) is None and not empty.inside((0.0, 0.0))
    proud = {"fields": [{"outline": [list(p) for p in _FIELD], "plot_rings": [[[390.0, 50.0], [420.0, 50.0], [420.0, 80.0], [390.0, 80.0]]]}]}
    assert worked_ground(proud).dist((385.0, 60.0)) == pytest.approx(5.0), "rice standing proud of the outline is the bund there"


def test_an_end_short_of_the_bund_is_carried_on_to_it_and_no_further() -> None:
    g = WorkedGround([_FIELD])
    tgt = B.run_on_target((360.0, 100.0), g, 1.5)
    assert tgt == pytest.approx((400.0 - 1.5 - B.TIP_MARGIN_FT, 100.0)), "the tread's cap on the bund line"
    assert B.run_on_target((500.0, 100.0), g, 1.5) is None, "an end in the field is not carried"
    assert B.run_on_target((400.0 - BUND_REACH_FT + 1.0, 100.0), g, 1.5) is None, "an end on the bund has arrived"
    assert B.run_on_target((300.0, 100.0), g, 1.5) is None, "past the reach: the trims decide"
    assert B.run_on_target((300.0, 100.0), g, 1.5, reach=float("inf")) is not None
    assert B.run_on_target((300.0, 100.0), WorkedGround([]), 1.5) is None, "no ground, nothing to run on to"


def test_an_end_in_the_crop_is_pulled_back_onto_the_bund() -> None:
    g = WorkedGround([_FIELD])
    out = B.pulled_out_of_the_ground([(300.0, 100.0), (420.0, 100.0)], g, 2.5)
    assert out[-1][0] == pytest.approx(400.0 - 3.5, abs=1.0) and len(out) == 2
    bent = B.pulled_out_of_the_ground([(300.0, 100.0), (420.0, 100.0), (500.0, 100.0)], g, 2.5)
    assert len(bent) == 2 and bent[-1][0] < 400.0, "a whole leg in the crop is dropped"
    assert len(B.pulled_out_of_the_ground([(450.0, 100.0), (500.0, 100.0)], g, 2.5)) == 1, "a path in the crop end to end"
    assert B.pulled_out_of_the_ground([(300.0, 100.0), (350.0, 100.0)], g, 2.5) == [(300.0, 100.0), (350.0, 100.0)]


def test_a_run_on_that_would_double_back_is_refused() -> None:
    assert not B.turns_back((0.0, 0.0), (10.0, 0.0), (20.0, 0.0))
    assert B.turns_back((0.0, 0.0), (10.0, 0.0), (0.0, 1.0))
    assert not B.turns_back((0.0, 0.0), (0.0, 0.0), (5.0, 5.0)), "a leg of no length has no heading"


def test_the_spur_tip_is_set_on_the_bund() -> None:
    g = WorkedGround([_FIELD])
    assert B.tip_onto_the_bund([(360.0, 100.0)], g, 2.5) == [(360.0, 100.0)]
    assert B.tip_onto_the_bund([(300.0, 100.0), (420.0, 100.0)], g, 2.5)[-1][0] < 400.0, "pulled out of the crop"
    on = B.tip_onto_the_bund([(300.0, 100.0), (360.0, 100.0)], g, 2.5)
    assert len(on) == 3 and g.dist(on[-1]) <= BUND_REACH_FT, "carried on to the bund"
    back = B.tip_onto_the_bund([(380.0, 100.0), (360.0, 100.0)], g, 2.5)
    assert back == [(380.0, 100.0), (360.0, 100.0)], "the bund lies behind the end: not run on"


def _stub(**M) -> _StubSettlement:
    s = _StubSettlement(lanes=[[(0.0, 0.0), (0.0, 50.0)]], houses=[])
    s.M.update(_field_M())
    s.M.update(M)
    return s


def test_a_run_on_crosses_no_water_no_marsh_and_no_steading() -> None:
    assert B.RunOnBlocks(_stub()).clear((300.0, 100.0), (396.0, 100.0), 3.0)
    brook = {"streams": [{"poly": [[350.0, 0.0], [350.0, 200.0]], "w": 6}]}
    assert not B.RunOnBlocks(_stub(**brook)).clear((300.0, 100.0), (396.0, 100.0), 3.0)
    marsh = {"marshes": [{"poly": [[340.0, 90.0], [360.0, 90.0], [360.0, 110.0], [340.0, 110.0]]}]}
    assert not B.RunOnBlocks(_stub(**marsh)).clear((300.0, 100.0), (396.0, 100.0), 3.0)
    swamp = {"marshes": [{"poly": [[380.0, 80.0], [420.0, 80.0], [420.0, 120.0], [380.0, 120.0]]}]}
    assert not B.RunOnBlocks(_stub(**swamp)).clear((300.0, 100.0), (390.0, 100.0), 3.0), "the tip itself in the marsh"
    s = _stub()
    s.M["houses"] = [{"x": 350.0, "y": 100.0, "w": 46.0, "h": 28.0, "rot": 0.0}]
    assert not B.RunOnBlocks(s).clear((300.0, 100.0), (396.0, 100.0), 3.0)
    wet = _stub()
    wet.toe_band = lambda: [(340.0, 90.0), (360.0, 90.0), (360.0, 110.0), (340.0, 110.0)]  # type: ignore[method-assign]
    assert not B.RunOnBlocks(wet).clear((300.0, 100.0), (396.0, 100.0), 3.0), "the wet toe counts as marsh"


def test_every_lane_end_that_reaches_nothing_is_carried_on_to_the_bund() -> None:
    s = _stub()
    s.M["lanes"] += [
        {"pts": [[200.0, 100.0], [360.0, 100.0]], "w": 3},  # its east end 40 ft short of the bund, reaching nothing
        {"pts": [[200.0, 20.0], [420.0, 20.0]], "w": 3},  # its east end in the crop
        {"pts": [[900.0, 900.0]], "w": 3},  # a husk
    ]
    s.M["lanes"][0]["connector"] = True
    g = WorkedGround([_FIELD])
    assert B.run_lanes_on_to_the_bund(s, g) == 2
    assert g.dist(tuple(s.M["lanes"][1]["pts"][-1])) <= BUND_REACH_FT and len(s.M["lanes"][1]["pts"]) == 3
    assert s.M["lanes"][2]["pts"][-1][0] < 400.0 and g.dist(tuple(s.M["lanes"][2]["pts"][-1])) <= BUND_REACH_FT
    assert s.M["lanes"][0]["pts"] == [[0.0, 0.0], [0.0, 50.0]], "the connector is its own job"
    assert B.run_lanes_on_to_the_bund(s, g) == 0, "and a second pass finds nothing left to move"


def test_the_paddy_is_reached_by_a_joined_end_a_run_on_a_branch_or_the_map_says_why_not() -> None:
    assert B.a_way_onto_the_bund(_StubSettlement(lanes=[[(0.0, 0.0), (0.0, 50.0)]])) == "none: no paddy"
    joined = _stub()
    joined.M["lanes"].append({"pts": [[200.0, 100.0], [396.0, 100.0]], "w": 3})
    assert B.a_way_onto_the_bund(joined) == "joined"
    run = _stub()
    run.M["lanes"].append({"pts": [[100.0, 100.0], [300.0, 100.0]], "w": 3})
    assert B.a_way_onto_the_bund(run) == "run_on" and len(run.M["lanes"][1]["pts"]) == 3
    branch = _stub()
    branch.M["lanes"].append({"pts": [[300.0, 300.0], [300.0, 250.0]], "w": 3})  # both ends turn away from the paddy
    assert B.a_way_onto_the_bund(branch) == "branch" and branch.M["lanes"][-1]["w"] == B.BRANCH_WIDTH
    moat = _stub(streams=[{"poly": [[380.0, -100.0], [380.0, 400.0]], "w": 6}])
    moat.M["lanes"].append({"pts": [[300.0, 100.0], [300.0, 150.0]], "w": 3})
    assert B.a_way_onto_the_bund(moat).startswith("none: "), "every way to the paddy crosses the water"


def test_the_ground_falls_back_to_the_envelope_where_the_map_records_no_field() -> None:
    s = _StubSettlement()
    assert B.worked_ground_of(s, _FIELD).dist((390.0, 100.0)) == pytest.approx(10.0)
    s.M.update(_field_M())
    assert B.worked_ground_of(s, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]).inside((500.0, 100.0))


def test_two_ends_a_hands_width_apart_are_joined_and_the_connector_is_never_moved() -> None:
    from l7r.diagram.hamletgen.ways.joints import meet_end_to_end

    s = _StubSettlement(lanes=[[(107.0, 100.0), (107.0, 400.0)], [(0.0, 100.0), (100.0, 100.0)], [(500.0, 500.0), (600.0, 500.0)]])
    assert meet_end_to_end(s) == 1
    assert s.M["lanes"][1]["pts"][-1] == [107.0, 100.0], "the footpath's end moved onto the connector's"
    assert s.M["lanes"][0]["pts"][0] == [107.0, 100.0], "the connector stayed where it was"
    s.M["lanes"].append({"pts": [[300.0, 300.0], [300.0, 102.0]], "w": 3})  # ends near no other end
    s.M["lanes"].append({"pts": [[107.0, 250.0], [200.0, 250.0]], "w": 3})  # an end already on a way
    assert meet_end_to_end(s) == 0
    s.M["lanes"] = [{"pts": [[0.0, 0.0], [0.0, 1.0]], "connector": True}, {"pts": [[5.0, 0.0]], "w": 3}]
    assert meet_end_to_end(s) == 0, "a husk is stepped over"


def test_the_worked_ground_is_built_once_per_settlement_until_its_registries_grow() -> None:
    from l7r.diagram.hamletgen.ways.geom import memo_ground

    s = _stub()
    calls = []

    def build(M: dict) -> WorkedGround:
        calls.append(1)
        return WorkedGround([_FIELD])

    first = memo_ground(s, "worked", build)
    assert memo_ground(s, "worked", build) is first and len(calls) == 1, "asked twice, built once"
    s.M.setdefault("dry_plots", []).append({"poly": [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0]]})
    assert memo_ground(s, "worked", build) is not first and len(calls) == 2, "a plot laid since: built again"
    assert memo_ground(_stub(), "worked", build) is not first, "another settlement never reads it"
