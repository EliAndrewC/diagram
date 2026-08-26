"""gate tests split out of `tests.hamletgen.test_sink` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import hamletgen as hg


@pytest.mark.rolls_map
def test_a_pond_the_canvas_cannot_hold_falls_back_to_draining_OFF_MAP(monkeypatch: pytest.MonkeyPatch) -> None:
    """A CLAMPED pond is no pond, and the map must say so rather than draw one on the rice.

    `pond_setback` walks the tameike downslope until its rim clears the crop; the canvas clamp then
    pulls it back on-frame - and straight back onto the rice it had just cleared. The stage treats
    that as the same finding as a set-back past the limit and drains the field off the frame
    instead. Forced here by making the solver ask for a set-back the canvas cannot give, because no
    cohort seed currently produces one: the branch is real logic that the demo maps do not reach,
    which is exactly what this file is for."""
    # The set-back must pass the LIMIT test and still clamp - those are two different findings with
    # the same answer, and only the clamp is under test here.
    monkeypatch.setattr(hg.sink, "POND_SETBACK_LIMIT", 1e9)
    monkeypatch.setattr(hg.sink, "pond_setback", lambda plan, out, prx, pry, **kw: 5000.0)
    plan = hg.plan_site(hg.HamletSpec(name="Clamped", seed=23, households=12, water_sink="pond"))
    assert plan.water_sink == "pond", "the fixture must START as a pond map, or it proves nothing"
    s = hg.build(plan)
    assert plan.water_sink == "offmap", "a pond the canvas cannot hold must fall back to the off-map brook"
    assert not s.M.get("ponds"), "and no pond may be drawn"
    assert plan.sink_brook, "the fallback must actually cut the brook it promised"
