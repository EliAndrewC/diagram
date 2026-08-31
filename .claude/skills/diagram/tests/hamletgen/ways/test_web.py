"""Split from test_ways.py by feature 173 - see this directory's CLAUDE.md."""

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from .._builders import a_plan


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
