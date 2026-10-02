"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from .._builders import a_plan
from ._builders import AdmitsAll


def test_reachable_runs_admits_a_run_that_joins_THROUGH_another_run() -> None:
    """A back lane may join through a cross-tie and a tie through a back lane - that is what makes a
    framework a framework, and it is why the decision is made over candidates rather than as each
    lane is drawn: judged one at a time, a run is refused merely for being early in the loop."""
    skeleton = [((0.0, 0.0), (100.0, 0.0))]
    touching = [(100.0, 0.0), (200.0, 0.0)]
    second_hop = [(200.0, 0.0), (300.0, 0.0)]
    island = [(9000.0, 9000.0), (9100.0, 9000.0)]
    kept = hg.ways._reachable_runs([island, second_hop, touching], skeleton)
    assert touching in kept and second_hop in kept, "the far run joins through the near one"
    assert island not in kept, "an island is never drawn"


def test_reachable_runs_with_no_seed_network_seeds_from_the_first_run() -> None:
    """A hamlet always has its skeleton by the time the web is laid, so this is a defensive branch
    rather than a real case - but it must not silently return nothing, or a map that somehow reached
    it would come out with no web at all instead of with an obvious one."""
    runs = [[(0.0, 0.0), (10.0, 0.0)], [(9000.0, 9000.0), (9010.0, 9000.0)]]
    assert hg.ways._reachable_runs(runs, []) == [runs[0]]


def test_reachable_runs_with_no_candidates_is_empty() -> None:
    assert hg.ways._reachable_runs([], [((0.0, 0.0), (10.0, 0.0))]) == []
    assert hg.ways._reachable_runs([[(0.0, 0.0)]], [((0.0, 0.0), (10.0, 0.0))]) == [], "a one-point run is not a run"


def test_a_dispersed_hamlet_draws_no_internal_lanes() -> None:
    """The dispersed form's defining feature, pinned so a later change cannot quietly restore the web.

    A Tonami farmstead stands in the middle of its own holding; what joins it to the world is the
    connector, and what joins it to its neighbors is the field baulk. Drawing a web here would erase
    the one thing that makes the form legible at a glance."""
    plan = a_plan(settlement_form="dispersed")
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 120.0}]
    hg.ways.stage_web(s, plan)
    assert not s.M.get("lanes"), "a dispersed hamlet must have no internal lane network"
    assert s.M["meta"]["lane_skeleton"] == "none"


def test_only_the_dispersed_form_short_circuits_stage_web() -> None:
    """The converse of the test above, and it needs to exist: a dispersed map with no lanes would
    also pass if `stage_web` had simply stopped drawing lanes for EVERYONE.

    The discriminator is that a nucleated map runs on past the guard into the seat-dependent code,
    so on this deliberately seatless fixture it raises where the dispersed map returned cleanly.
    That is an indirect assertion, and it is used here because building a real seat means running
    the whole pre-house pipeline; the direct evidence that nucleated maps still get lanes is the
    cohort, where they do."""
    plan = a_plan(settlement_form="nucleated")
    assert plan.settlement_form == "nucleated"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 120.0}]
    with pytest.raises(KeyError):
        hg.ways.stage_web(s, plan)


# ---- feature 126: the defensive branches in the derived-lane machinery -------------------------


def test_a_dispersed_hamlet_records_that_it_has_no_skeleton() -> None:
    """The dispersed form draws no internal network, and says so in `meta` rather than leaving the
    knob reading as though a skeleton were drawn."""
    plan = a_plan(settlement_form="dispersed")
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 100.0, "y": 100.0}, {"x": 200.0, "y": 120.0}]
    hg.ways.stage_web(s, plan)
    assert s.M["meta"]["lane_skeleton"] == "none"
    assert not s.M.get("lanes")


def test_the_skeleton_needs_two_house_projections() -> None:
    """`_lay_skeleton` is handed the arcs the caller measured off the placed houses. With fewer than
    two there is no extent to fit an arm to, and it draws nothing rather than guessing one."""
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    # The frame is never consulted on this path - the arc count is checked first - so a sentinel is
    # honest here and keeps the test off `_margin_frame`, which needs a seated cluster to exist.
    assert hg.ways._lay_skeleton(s, plan, None, [], []) == []  # type: ignore[arg-type]
    assert hg.ways._lay_skeleton(s, plan, None, [10.0], [5.0]) == []  # type: ignore[arg-type]


def test_an_arm_clipped_down_to_a_stub_is_debris_and_is_not_drawn() -> None:
    """A skeleton arm that survives clipping as a few pixels is not a short lane, it is debris.

    The arms are the layout template mapped onto the margin frame, so what reaches the drawing call
    is whatever is left after the crop, the water and the standing fabric have each taken their bite.
    Nothing in that chain has an opinion about whether the remainder is still a WAY - `clip_to_clear`
    stops where the ground stops being walkable, and `_trim_to_service` pulls the ends back to what
    they serve but never below two points. So a run of half a pixel arrives at `s.lane` looking
    exactly like a legitimate short arm, and gets ink.

    Driven through a frame that collapses the template rather than through a rolled map, because no
    pool map or cohort seed produces the case - the whole 3,448-test suite leaves this branch
    unexecuted - and a test that cannot be provoked deterministically is not a test. The houses sit
    clear of the collapsed arm on purpose: parked on top of it the fabric clip removes the run one
    step earlier, which passes for the wrong reason."""
    plan = a_plan(lane_skeleton="spine")
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 200.0, "y": 270.0, "w": 20.0, "h": 14.0}, {"x": 230.0, "y": 270.0, "w": 20.0, "h": 14.0}]

    # every (arc, standoff) lands within half a pixel of the same spot, well clear of SQUARE
    def flat(arc: float, standoff: float) -> tuple[float, float]:
        return (200.0 + arc * 0.005, 200.0 - standoff * 0.005)

    assert hg.ways._lay_skeleton(s, plan, flat, [0.0, 20.0], [0.0, 10.0]) == []  # type: ignore[arg-type]
    assert not s.M.get("lanes"), "a half-pixel arm must not be inked"


def test_the_web_stage_draws_nothing_for_fewer_than_two_houses_or_no_envelope() -> None:
    """`stage_web`'s first return (feature 216: only the seatings' full rolls reached it): a hamlet of one house has no
    internal network to draw, and neither has a plan with no envelope."""
    from l7r.diagram.hamletgen.ways.web import stage_web

    from .._builders import a_plan
    from ._builders import _StubSettlement

    plan = a_plan()
    s = _StubSettlement(lanes=[], houses=[(300.0, 300.0)])
    stage_web(s, plan)
    assert s.M["lanes"] == [], "one house: no web"
    s2 = _StubSettlement(lanes=[], houses=[(300.0, 300.0), (400.0, 300.0)])
    plan.envelope = []
    stage_web(s2, plan)
    assert s2.M["lanes"] == [], "no envelope: no web"


def test_an_arm_that_crosses_a_kept_arm_by_accident_is_dropped(monkeypatch: pytest.MonkeyPatch) -> None:
    """`_lay_skeleton` drops an arm `_arm_crossing_accidental` refuses, and inks nothing for it. The
    crossing predicate has its own tests; this is the branch that ACTS on its verdict, which feature
    216 found reached only by a roll the gate no longer makes. The control half proves the frame
    below yields a real arm, so the empty result is the predicate's doing."""
    from l7r.diagram.hamletgen.ways import web as _web

    def frame(arc: float, standoff: float) -> tuple[float, float]:
        return (200.0 + arc, 200.0 - standoff)

    def fresh() -> Settlement:
        plan = a_plan(lane_skeleton="spine")
        s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
        s.M["houses"] = [{"x": 250.0, "y": 230.0, "w": 20.0, "h": 14.0}, {"x": 350.0, "y": 230.0, "w": 20.0, "h": 14.0}]
        return s

    plan = a_plan(lane_skeleton="spine")
    s = fresh()
    assert hg.ways._lay_skeleton(s, plan, frame, [0.0, 200.0], [0.0, 10.0]), "control: the frame yields an arm"  # type: ignore[arg-type]
    assert s.M.get("lanes"), "control: the arm is inked"
    monkeypatch.setattr(_web, "_arm_crossing_accidental", lambda arm, raw, kept: True)
    s = fresh()
    assert hg.ways._lay_skeleton(s, plan, frame, [0.0, 200.0], [0.0, 10.0]) == []  # type: ignore[arg-type]
    assert not s.M.get("lanes"), "an accidental crossing is not inked"


def test_a_lane_the_smoothing_collapsed_is_emptied_reinked_and_deleted() -> None:
    """`_drop_collapsed` (lifted from `stage_web` by feature 216): a non-connector lane the knot
    collapse left with one point, or two points under a foot apart, is emptied, its ink pulled, and
    the husk removed back-to-front so the survivors keep their order. The connector is kept whatever
    its shape - it is the map's way out."""
    from l7r.diagram.hamletgen.ways import web as _web

    class _S(AdmitsAll):
        def __init__(self) -> None:
            self.M: dict = {
                "lanes": [
                    {"pts": [[0.0, 0.0]], "connector": True},
                    {"pts": [[10.0, 10.0]]},
                    {"pts": [[20.0, 20.0], [20.0, 20.5]]},
                    {"pts": [[30.0, 30.0], [80.0, 30.0], [80.0, 80.0]]},
                    {"pts": []},
                ]
            }
            self.reinked: list[int] = []

        def reink_lane(self, i: int) -> None:
            self.reinked.append(i)

        def drop_lanes(self, idxs: list[int]) -> None:
            for i in sorted(set(idxs), reverse=True):
                del self.M["lanes"][i]

    s = _S()
    assert _web._drop_collapsed(s) == [1, 2, 4]  # type: ignore[arg-type]
    assert s.reinked == [1, 2, 4], "each collapsed lane is reinked at its ORIGINAL index before any deletion"
    assert [ln["pts"] for ln in s.M["lanes"]] == [[[0.0, 0.0]], [[30.0, 30.0], [80.0, 30.0], [80.0, 80.0]]]


def test_a_lane_that_is_the_only_link_between_two_parts_of_the_web_is_not_dropped() -> None:
    """`unsplitting_drops` (the 269 landing, Inashiro): of two lanes the tidy would drop, the one tying an arm to the web
    stays and the loose one goes."""
    from l7r.diagram.hamletgen.ways.web import unsplitting_drops

    lanes = [
        {"pts": [[0.0, 0.0], [100.0, 0.0]]},  # the web
        {"pts": [[100.0, 0.0], [100.0, 100.0]]},  # the only link to the arm below
        {"pts": [[100.0, 100.0], [200.0, 100.0]]},  # the arm
        {"pts": [[0.0, 0.0], [0.0, 50.0]]},  # a spur hanging off the web, tied to nothing else
    ]
    assert unsplitting_drops(lanes, [1, 3]) == [3]
    assert unsplitting_drops(lanes, []) == []


def test_the_late_pass_keeps_the_connector_as_placed_where_its_pulled_back_end_would_run_through_a_building() -> None:
    """`kept_connector` (ways, the connector half of break-mid-run): the pull-back walks the inner end on to the network,
    and where the new leg's middle stands in a building's box the connector stays as placed."""
    from l7r.diagram.hamletgen.ways.web import kept_connector

    placed = [(0.0, 0.0), (0.0, 200.0), (-900.0, 200.0)]
    pulled = [(100.0, 100.0), (0.0, 200.0), (-900.0, 200.0)]
    box = (40.0, 140.0, 60.0, 160.0)  # the middle of the pulled end's new 141 ft leg
    assert kept_connector(placed, pulled, [box]) == placed
    assert kept_connector(placed, pulled, []) == pulled


def test_lay_reachable_runs_draws_each_run_the_network_reaches(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stage_web`'s drawing loop, lifted (2026-10-02): every reachable run goes through `_lay_web_lane`, an island does
    not, and the count is of the lanes it drew."""
    import l7r.diagram.hamletgen.ways.web as web

    s = Settlement(1000, 1000, seed=1)
    s.lane([(0.0, 500.0), (400.0, 500.0)], width=5, clearance=11, worn=True)
    laid: list[object] = []
    monkeypatch.setattr(web, "_lay_web_lane", lambda s, run, *a, **k: laid.append(run) or True)
    touching = [(400.0, 500.0), (400.0, 700.0)]
    island = [(900.0, 900.0), (950.0, 900.0)]
    assert web.lay_reachable_runs(s, [touching, island], [], [], [], [], []) == 1
    assert laid == [touching]


def test_a_skeleton_arm_trimmed_under_the_web_floor_is_no_arm(monkeypatch: pytest.MonkeyPatch) -> None:
    """`served_arm` (feature 308, lifted from `_lay_skeleton`): the arm trimmed to service, and none where it falls short."""
    from l7r.diagram.hamletgen.ways import web

    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["houses"] = [{"x": 0.0, "y": 0.0}]
    monkeypatch.setattr(web, "_trim_to_service", lambda arm, *a, **k: arm[:2])
    assert web.served_arm(s, [(0.0, 0.0), (5.0, 0.0), (500.0, 0.0)]) == [], "trimmed to 5 ft: under the floor"
    assert web.served_arm(s, [(0.0, 0.0), (400.0, 0.0), (500.0, 0.0)]) == [(0.0, 0.0), (400.0, 0.0)]
    assert web.served_arm(s, [(0.0, 0.0)]) == [(0.0, 0.0)], "a point is passed through untrimmed"
