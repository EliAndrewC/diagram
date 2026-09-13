"""Unit tests for where the runoff goes - the drain, the brook, the tameike (`hamletgen/sink.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import math
from typing import Any, cast

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from ._builders import a_plan


def _with_drain(poly: list[tuple[float, float]]) -> Settlement:
    """The only thing `drain_heading` reads is the manifest, so the manifest is the whole fixture."""
    stub: Any = type("_S", (), {})()
    stub.M = {"field_ditches": [{"role": "drain", "field": "test-paddies", "poly": [list(p) for p in poly]}]}
    return cast(Settlement, stub)


def _bearing(v: tuple[float, float] | None) -> float:
    assert v is not None
    return math.degrees(math.atan2(v[1], v[0]))


def test_the_run_to_the_map_edge_is_measured_along_the_fall() -> None:
    plan = a_plan()  # falls due south
    assert hg.edge_run(plan, (500.0, plan.H - 300.0)) == pytest.approx(300.0)


def test_the_drain_heading_is_read_over_the_gates_span_not_the_final_vertex_pair() -> None:
    """A collector's LAST SEGMENT is noise, and reading the heading off it is what let cohort seed 2
    draw a brook 1,100 px uphill.

    `drainage_junction_smooth` measures the corner with `_flow_dir(..., span=40.0)` - it walks back
    up the collector until the chord is at least 40 px long. Here the collector runs due east and
    then hooks 2 px east, 4 px north at its outfall: the final pair reads -63.4 deg, the gate's span
    reads -5.4 deg. The placer must agree with the gate, or it optimizes a corner nobody measures."""
    heading = hg.drain_heading(_with_drain([(0.0, 0.0), (100.0, 0.0), (140.0, 0.0), (142.0, -4.0)]), "test-paddies")
    assert _bearing(heading) == pytest.approx(-5.44, abs=0.1), "the span bearing, over the last 40+ px"
    assert _bearing(heading) != pytest.approx(-63.4, abs=1.0), "NOT the final vertex pair's hook"


def test_a_collector_shorter_than_the_span_is_read_end_to_end() -> None:
    """The walk-back can run out of collector before it runs out of span, and then the whole ditch IS
    the chord - there is no shorter honest answer, and no reason to fall back to the noisy last pair."""
    heading = hg.drain_heading(_with_drain([(0.0, 0.0), (10.0, 0.0), (20.0, 0.0)]), "test-paddies")
    assert heading == pytest.approx((1.0, 0.0)), "due east, measured over the entire 20 px ditch"


def test_pond_setback_walks_past_blocked_probes() -> None:
    """An outfall INSIDE the field envelope blocks the first probes (every near rim point lands in
    the crop), so the walk must step outward (`d += step`) until the ellipse clears, and the
    returned distance carries the 12 px cushion past that first clear seat."""
    plan = a_plan()
    d = hg.pond_setback(plan, (700.0, 700.0), 60.0, 40.0)
    assert d > 40.0 + 46.0 + 14.0  # further than the first probe: the walk really stepped
    cx, cy = 700.0 + plan.fall[0] * d, 700.0 + plan.fall[1] * d
    assert hg.pond_clear_of_crop(plan, (cx, cy), 60.0, 40.0)


def test_a_pond_laid_over_the_crop_is_recognized() -> None:
    """The predicate `stage_sink` uses to check its own clamp: `pond_clear_of_field`'s two tests, on
    the same envelope, so the siting and the check cannot disagree."""
    plan = a_plan()
    assert hg.pond_clear_of_crop(plan, (700.0, 1400.0), 100.0, 60.0), "well below the field: clear"
    assert not hg.pond_clear_of_crop(plan, (700.0, 700.0), 100.0, 60.0), "sitting in the middle of it: not clear"
    assert not hg.pond_clear_of_crop(plan, (700.0, 1040.0), 100.0, 60.0), "rim overlapping the low edge: not clear"


@pytest.mark.parametrize(("down_deg", "start", "expect"), [(0.0, (500.0, 500.0), None), (180.0, (500.0, 500.0), 500.0), (90.0, (500.0, 500.0), None)])
def test_the_run_to_the_frame_is_measured_on_every_axis(down_deg, start, expect) -> None:  # type: ignore[no-untyped-def]
    """`edge_run` walks whichever axis the fall actually points along - east and west included, which
    the south-falling fixtures elsewhere in this file never exercise."""
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, down_deg=down_deg))
    run = hg.edge_run(plan, start)
    assert run > 0
    if expect is not None:
        assert run == pytest.approx(expect)


# ---- end to end ---------------------------------------------------------------------------------


def test_the_pond_setback_search_gives_up_at_its_own_limit() -> None:
    """The search walks downhill from the outfall until the pond's rim clears the field, and it is
    BOUNDED - without the bound a fan whose envelope never clears would search forever. Production
    fans always clear ("a fan is never 900 px deep past its own outfall"), which is why the terminal
    was excluded from coverage rather than tested; but the function's own domain reaches it in one
    call, and a bound nothing exercises is a bound nobody knows still holds."""
    plan = a_plan()
    plan.envelope = [(-5000.0, -5000.0), (5000.0, -5000.0), (5000.0, 5000.0), (-5000.0, 5000.0)]
    assert hg.sink.pond_setback(plan, (0.0, 0.0), 20.0, 14.0, step=50.0, limit=300.0) == 300.0


def test_a_pond_the_canvas_cannot_hold_falls_back_to_draining_OFF_MAP(monkeypatch: pytest.MonkeyPatch) -> None:
    """A CLAMPED pond is no pond, and the stage must say so rather than draw one on the rice. `pond_setback` walks the
    tameike downslope until its rim clears the crop; the canvas clamp then pulls it back on-frame - and straight back
    onto the rice it had just cleared. The stage treats that as the same finding as a set-back past the limit and
    drains the field off the frame instead. THE DECISION, asserted directly (feature 216; until then a rostered roll,
    `Clamped` seed 23, forced by the same patches around a full build): the solver is made to ask for a set-back the
    canvas cannot give, and the stage must flip the sink to off-map and re-enter itself for the brook. What this no
    longer proves, stated (specs/216 FR-005 b): that the brook it promised was actually cut on a real map."""
    plan = a_plan()
    plan.water_sink = "pond"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    real = hg.sink.stage_sink
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (plan.W / 2.0, plan.H / 2.0))
    monkeypatch.setattr(hg.sink, "POND_SETBACK_LIMIT", 1e9)
    monkeypatch.setattr(hg.sink, "pond_setback", lambda plan_, out, prx, pry, **kw: 5000.0)
    reentered: list[str] = []
    monkeypatch.setattr(hg.sink, "stage_sink", lambda s_, plan_: reentered.append(plan_.water_sink))  # the recursive call resolves the module name
    real(s, plan)
    assert plan.water_sink == "offmap", "a pond the canvas cannot hold must fall back to the off-map brook"
    assert reentered == ["offmap"], "and the stage re-enters itself once, as an off-map map, to cut the brook"
    assert not s.M.get("ponds"), "and no pond may be drawn"


# ---- the third sink: the drain reaching the brook that passes (feature 230) -----------------------


def test_the_drain_joins_the_passing_brook_when_one_runs_within_reach_downslope() -> None:
    """`brook_join`. Before modern consolidation a village's drainage went back to the watercourse to be
    taken up below, so where the field's own brook passes near the collector's outfall the drain runs
    to it. The candidate must lie downslope and be reachable without crossing the crop."""
    plan = a_plan()  # falls due south, the square crop at x 400-1000, y 400-1000
    plan.brook = [(1200.0, 1100.0), (1200.0, 1600.0)]
    join = hg.brook_join(plan, (1050.0, 1050.0))
    assert join is not None and join[0] == pytest.approx(1200.0) and join[1] >= 1050.0 + hg.BROOK_JOIN_DESCENT


def test_a_brook_abreast_of_the_outfall_is_joined_a_little_way_down_it() -> None:
    """The nearest point on a brook running down the flank is LEVEL with the outfall, and taking it sent
    Sawada's drain off the frame beside its own brook. The join is the nearest point that has FALLEN."""
    plan = a_plan()
    plan.brook = [(1130.0, 400.0), (1130.0, 1600.0)]  # abreast of the outfall, then on downslope
    join = hg.brook_join(plan, (1050.0, 1050.0))
    assert join is not None and join[1] == pytest.approx(1050.0 + hg.BROOK_JOIN_DESCENT, abs=10.0)


def test_a_brook_that_passes_uphill_of_the_outfall_is_no_sink() -> None:
    """Water does not run up to its confluence: a brook whose nearest point is upslope is refused, and
    the runoff leaves the frame as it did before."""
    plan = a_plan()
    plan.brook = [(1200.0, 100.0), (1205.0, 200.0)]
    assert hg.brook_join(plan, (1050.0, 1050.0)) is None


def test_a_brook_beyond_the_crop_is_not_reached_across_it() -> None:
    """A ditch does not run through the rice to find its confluence."""
    plan = a_plan()
    plan.brook = [(200.0, 900.0), (200.0, 1600.0)]  # on the far side of the square from the outfall
    assert hg.brook_join(plan, (1050.0, 700.0)) is None


def test_a_brook_out_of_reach_is_no_sink() -> None:
    plan = a_plan()
    plan.brook = [(4000.0, 1100.0), (4000.0, 1600.0)]
    assert hg.brook_join(plan, (1050.0, 1050.0)) is None


def test_the_outfalls_own_crop_edge_is_exempt_but_a_ditch_through_the_rice_is_not() -> None:
    """`_through_the_crop`. The outfall stands ON the field's edge, so the first strides of any route from
    it are on the crop's own ground - the exemption the gate makes for a brook's leading vertices. Past
    `BROOK_JOIN_LEAD` of the run the route is a ditch driven through the rice and is refused."""
    plan = a_plan()  # the square crop, x 400-1000, y 400-1000
    from l7r.diagram.hamletgen.sink import _through_the_crop

    assert not _through_the_crop(plan, (1000.0, 700.0), (1120.0, 760.0)), "leaving the crop at once is the outfall's own edge"
    assert _through_the_crop(plan, (450.0, 700.0), (1120.0, 760.0)), "most of this run is inside the rice"


def test_a_confluence_is_taken_only_where_the_junction_is_in_the_picture() -> None:
    """Feature 230, settlement-review passes 6 and 7. The drain joins the passing brook where one falls within
    reach - but a junction drawn at or past the sheet's edge is not a junction a reader can see, and both of the
    pool's brook-fed maps whose drain leaves the frame put their outfall near the canvas edge, where no visible
    confluence exists. So the accepting branch is proved here rather than on a map: a brook running well inside
    the field's own box, falling past the outfall with a long run below it, is joined; the same brook shifted so
    that the junction lands outside the box the crop must contain is not."""
    from l7r.diagram.hamletgen import sink

    plan = a_plan()
    out = (700.0, 1010.0)  # just below the square field's low edge
    plan.brook = [(760.0, 900.0), (760.0, 1000.0), (760.0, 1100.0), (760.0, 1400.0), (760.0, 1700.0)]
    joined = sink.brook_join(plan, out)
    assert joined is not None, "a brook passing the outfall inside the picture, with a trunk below it, is joined"
    assert 900.0 <= joined[1] <= 1700.0 and abs(joined[0] - 760.0) < 1e-6, "the junction stands on the brook"
    assert (joined[1] - out[1]) > 0, "and below the outfall, not level with it"

    plan.brook = [(760.0 + 4000.0, y) for _x, y in plan.brook]  # the same brook, carried far outside the picture
    assert sink.brook_join(plan, out) is None, "a junction outside the box the crop must contain is refused"


def test_a_confluence_is_refused_when_the_run_to_it_crosses_the_crop() -> None:
    """A ditch does not run through the rice to find its confluence - the same rule the reach and the descent
    stand beside. Exercised here because the pool's own maps reach their sinks another way."""
    from l7r.diagram.hamletgen import sink

    plan = a_plan()  # the square field at x 400-1000, y 400-1000, falling due south
    # the brook runs down THROUGH the field and on past it, and the outfall stands high inside the rice: every
    # candidate within reach has fallen, so what refuses them is the run - straight down the planted ground
    plan.brook = [(700.0, 800.0), (700.0, 1600.0)]
    assert sink.brook_join(plan, (700.0, 450.0)) is None


def test_the_pond_set_back_gives_up_past_its_limit() -> None:
    """`pond_seat` walks the reservoir downslope and across the fall to clear the crop and the brook. Where no
    step inside the limit does, it says so with a distance past the limit rather than returning a seat that
    does not clear - the caller then falls back to draining off the frame."""
    from l7r.diagram.hamletgen import sink
    from l7r.diagram.hamletgen.consts import POND_SETBACK_LIMIT

    plan = a_plan()
    plan.envelope = [(0.0, 0.0), (3000.0, 0.0), (3000.0, 3000.0), (0.0, 3000.0)]  # crop over the whole canvas
    back, sway = sink.pond_seat(plan, (1500.0, 1500.0), 120.0, 90.0)
    assert back > POND_SETBACK_LIMIT and sway == 0.0


def test_the_drain_runs_to_the_brook_and_records_the_junction_for_the_frame(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stage_sink`'s confluence branch, driven directly. Where `brook_join` names a junction the drain is drawn
    to it with a bow rather than a ruled connector, and the junction is RECORDED on the plan so `stage_frame` can
    reserve it as content - which is how a junction stays on the sheet (research R7; no pool map's geometry takes
    this sink today, so the branch is proved here rather than on a map)."""
    plan = a_plan()
    plan.water_sink = "offmap"
    plan.brook = [(760.0, 900.0), (760.0, 1200.0), (760.0, 1600.0), (760.0, 2000.0)]
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    drawn: list[tuple[list[tuple[float, float]], str]] = []
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 1010.0))
    monkeypatch.setattr(hg.sink, "drain_run", lambda s_, pts, to: drawn.append(([(round(p[0], 1), round(p[1], 1)) for p in pts], to)))
    hg.sink.stage_sink(s, plan)
    assert plan.confluence is not None, "the junction is recorded for the frame to reserve"
    assert drawn and drawn[0][1] == "stream", "and the run is drawn to the stream"
    pts = drawn[0][0]
    assert len(pts) == 3 and pts[-1] == (round(plan.confluence[0], 1), round(plan.confluence[1], 1))
    mid = pts[1]
    assert mid != ((pts[0][0] + pts[2][0]) / 2, (pts[0][1] + pts[2][1]) / 2), "the run bows - dug earth, not a ruled connector"


def test_a_pond_behind_the_collector_is_reached_by_a_curve_not_a_hairpin() -> None:
    """`pond_run`, settlement-review pass 10. A pond straight downslope of an outfall on a collector running across the
    fall keeps the ordinary bowed run; a pond BEHIND the collector's heading - Mizuguchi's, stepped across the fall by
    the brook - is led round along the heading instead of doubling back 111 degrees in one corner."""
    import math

    from l7r.diagram.hamletgen.sink import pond_run

    def worst(pl: list[tuple[float, float]]) -> float:
        return max(abs((math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(b[1] - a[1], b[0] - a[0])) + 180.0) % 360.0 - 180.0) for a, b, c in zip(pl, pl[1:], pl[2:], strict=False))

    ahead = pond_run((100.0, 100.0), (1.0, 0.0), (100.0, 250.0), (0.0, 1.0))
    assert len(ahead) == 3 and ahead[-1] == (100.0, 250.0), "downslope of a cross-fall collector: the ordinary three-point run"
    prev = (1596.0, 902.0)
    behind = pond_run((1647.0, 771.0), (51.0, -131.0), (1771.0, 864.0), (1.0, 0.0))
    assert behind[0] == (1647.0, 771.0) and behind[-1] == pytest.approx((1771.0, 864.0))
    assert worst([prev, *behind]) <= 60.0, "the turn is spread over gentle bends, not one hairpin"
    # ...AND THE RUN NEVER CLIMBS AWAY FROM ITS OWN POND (pass 12). The bends were inside tolerance while the curve
    # arched 26 ft further from the pond and 53 ft past its far rim, because a per-bend limit cannot see an
    # excursion. The measure that catches it is monotone-ish approach: no point of the run stands further from the
    # pond than its own outfall does. The larger turn at the junction above is what buys it, and it is still obtuse.
    _d = [math.dist(q, (1771.0, 864.0)) for q in behind]
    assert max(_d) <= _d[0] + 1e-6, "every stride of the run is nearer the pond than the outfall was"


def test_a_pond_exactly_back_along_the_heading_has_no_bisector_to_leave_on() -> None:
    """`pond_run`'s one degenerate case. The run leaves on the bisector of the collector's heading and the chord
    to the pond; where the pond lies exactly BACK along that heading the two cancel, and there is no bisector to
    take. The chord is what is left - the run simply turns round and goes to the pond."""
    import math

    from l7r.diagram.hamletgen.sink import pond_run

    back = pond_run((100.0, 100.0), (1.0, 0.0), (0.0, 100.0), (0.0, 1.0))
    assert back[0] == (100.0, 100.0) and back[-1] == (0.0, 100.0)
    assert all(abs(q[1] - 100.0) < 1e-6 for q in back), "with no bisector the run lies on the chord itself"
    assert all(math.dist(q, (0.0, 100.0)) <= math.dist(back[0], (0.0, 100.0)) + 1e-6 for q in back), "and never climbs away from the pond"
