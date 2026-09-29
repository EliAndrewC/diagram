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


# ---- feature 287: every sink rule decided where the route is chosen (water:W10, W11, W12, W49) -------------------------


def test_a_run_downhill_keeps_a_fifth_of_its_travel_on_the_fall() -> None:
    """water:W10: the channel test's rule, lifted - net travel down the fall of at least a fifth of its length."""
    fall = (0.0, 1.0)
    assert hg.sink.runs_downhill([(0.0, 0.0), (100.0, 30.0)], fall)
    assert not hg.sink.runs_downhill([(0.0, 0.0), (100.0, 10.0)], fall), "a near-level ditch that merely descends"
    assert not hg.sink.runs_downhill([(0.0, 0.0), (0.0, -50.0)], fall)
    assert hg.sink.runs_downhill([(5.0, 5.0), (9.0, 9.0), (5.0, 5.0)], fall), "no net travel: nothing to judge"


def test_a_confluence_the_drain_would_reach_on_the_level_is_refused() -> None:
    """water:W10: a brook passing 250-700 ft along the collector's line and only 30 ft down it. Its points have fallen the
    20 ft a junction needs, but a ditch to any of them runs down the fall by less than a fifth of its length - the
    level ditch the channel rule forbids. A brook passing below the outfall is still joined, and the run to it is
    downhill."""
    plan = a_plan()
    out = (700.0, 1010.0)
    plan.brook = [(950.0, 1040.0), (1400.0, 1060.0), (1800.0, 1070.0), (2200.0, 1080.0)]
    assert hg.brook_join(plan, out) is None
    plan.brook = [(760.0, 1040.0), (760.0, 1400.0), (760.0, 2000.0)]
    q = hg.brook_join(plan, out)
    assert q is not None and hg.sink.runs_downhill([out, q], plan.fall)


def test_the_pond_seat_refuses_a_sway_whose_ditch_would_run_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """water:W10/W11: the pond's ditch ends at its center, and a seat whose ditch the channel rule refuses is no seat - the
    next sway is taken. By construction the first is never refused; the refusal is made to fire."""
    plan = a_plan()
    calls: list[int] = []
    real = hg.sink.runs_downhill
    monkeypatch.setattr(hg.sink, "runs_downhill", lambda course, fall, frac=0.2: bool(calls.append(1)) or len(calls) > 1 and real(course, fall, frac))
    back, sway = hg.sink.pond_seat(plan, (700.0, 1010.0), 60.0, 40.0)
    assert sway != 0.0 and len(calls) == 2


def _u_field_stage(monkeypatch: pytest.MonkeyPatch) -> tuple[Any, list[tuple[list[tuple[float, float]], str]], tuple[float, float]]:
    """A field closing round the outfall on every side a searched route could take: the collector ends in a slot cut into
    a block of rice 1,200 ft wide and 750 deep, and runs east along the fall's contour."""
    plan = a_plan()
    plan.water_sink = "offmap"
    plan.W, plan.H = 3000, 3000
    plan.envelope = [(900.0, 950.0), (1480.0, 950.0), (1480.0, 1010.0), (1520.0, 1010.0), (1520.0, 950.0), (2100.0, 950.0), (2100.0, 1700.0), (900.0, 1700.0)]
    plan.brook = []
    drawn: list[tuple[list[tuple[float, float]], str]] = []
    out = (1500.0, 1005.0)
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: out)
    monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (1.0, 0.0))
    monkeypatch.setattr(hg.sink, "drain_run", lambda s_, pts, to: drawn.append((list(pts), to)))
    return plan, drawn, out


def test_where_no_searched_route_is_clean_the_constructed_route_is_drawn_and_breaks_no_rule(monkeypatch: pytest.MonkeyPatch) -> None:
    """water:W12, the least-bad route's case constructed: every bearing at every junction distance runs into the rice, climbs
    or kinks. The old stage drew the least-bad of them; the stage now draws the route round the field's hull, which
    passes every refusal - on along the collector, round the hull down the fall, and off the canvas."""
    plan, drawn, out = _u_field_stage(monkeypatch)
    anchored_out = (1476.0, 1005.0)  # backed up the collector until it stands in the field, as the stage does
    heading = (1.0, 0.0)
    th = math.radians(90.0)
    bis = hg.sink.unit(heading[0] + math.cos(th), heading[1] + math.sin(th))
    probe = [anchored_out, (anchored_out[0] + bis[0] * 70.0, anchored_out[1] + bis[1] * 70.0), (anchored_out[0], 3200.0)]
    assert hg.sink.route_refusals(plan, anchored_out, heading, True, probe, []), "a searched route is refused"
    built: list[int] = []
    real = hg.sink.hull_route
    monkeypatch.setattr(hg.sink, "hull_route", lambda *a, **k: bool(built.append(1)) or real(*a, **k))
    hg.sink.stage_sink(Settlement(W=plan.W, H=plan.H, seed=1), plan)
    assert built == [1], "every searched route was refused: the constructed one is drawn"
    route, to = drawn[0]
    assert to == "offmap" and route == plan.sink_brook
    assert hg.sink.route_refusals(plan, route[0], heading, True, route, []) == []
    assert not (0.0 <= route[-1][0] <= plan.W and 0.0 <= route[-1][1] <= plan.H), "it leaves the canvas"


def test_the_constructed_route_meets_a_brook_across_it_as_a_confluence() -> None:
    """water:W08/W12: where the brook lies across the constructed route, the run ends on the brook - a confluence, never a
    crossing."""
    plan = a_plan()
    plan.W, plan.H = 3000, 3000
    brook = [(0.0, 1500.0), (3000.0, 1520.0)]
    route, to = hg.sink.hull_route(plan, (700.0, 990.0), (0.0, 1.0), brook)
    assert to == "stream" and abs(route[-1][1] - 1500.0) < 30.0
    assert not hg.sink.crosses_mid_run(brook, route)


def test_a_constructed_route_from_outside_the_hull_starts_on_its_nearest_edge() -> None:
    plan = a_plan()
    plan.W, plan.H = 3000, 3000
    route, to = hg.sink.hull_route(plan, (1200.0, 700.0), (1.0, 0.0), [])
    assert to == "offmap" and hg.sink.runs_downhill(route, plan.fall)
    assert math.dist(route[1], (1012.0, 700.0)) < 1.0


def test_the_route_refusals_name_each_rule() -> None:
    plan = a_plan()
    out = (700.0, 990.0)
    kinked = [out, (700.0, 1100.0), (700.0, 3200.0)]
    assert "kink" in hg.sink.route_refusals(plan, out, (1.0, 0.0), True, kinked, [])
    assert "field" in hg.sink.route_refusals(plan, out, (0.0, 1.0), False, [(700.0, 300.0), (700.0, 1100.0), (700.0, 3200.0)], [])
    assert {"uphill", "upstream"} <= set(hg.sink.route_refusals(plan, out, (0.0, -1.0), True, [out, (700.0, 300.0), (700.0, -500.0)], []))
    assert "brook" in hg.sink.route_refusals(plan, out, (0.0, 1.0), True, kinked, [(500.0, 1500.0), (900.0, 1500.0)])
    assert hg.sink.route_refusals(plan, out, (0.0, 1.0), True, kinked, []) == []


def test_the_drawn_brook_is_the_finished_course_at_the_head_races_tap() -> None:
    plan = a_plan()
    s = Settlement(W=plan.W, H=plan.H, seed=1)
    assert hg.sink.drawn_brook(s, plan) == []
    plan.brook = [(700.0, 100.0), (700.0, 300.0), (900.0, 600.0), (900.0, 900.0)]
    s.M["channels"].append({"poly": [[700.0, 300.0], [760.0, 380.0]], "frm": {"kind": "stream"}})
    drawn = hg.sink.drawn_brook(s, plan)
    assert (700.0, 300.0) in drawn and len(drawn) > len(plan.brook)


def test_a_pond_sink_draws_a_ditch_ending_on_the_pond(monkeypatch: pytest.MonkeyPatch) -> None:
    """water:W49: a drainage pond has the drain's ditch ending on it - `pond_run` ends at the pond's center."""
    plan = a_plan()
    plan.water_sink = "pond"
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.meta(name="Test", scale="hamlet", ftpx=1)
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 1010.0))
    monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (1.0, 0.0))
    hg.sink.lay_sink(s, plan)
    pond = s.M["pond"]
    assert s.M["meta"]["pond_role"] == "drainage"
    ends = [c["poly"][-1] for c in s.M["channels"] if (c.get("to") or {}).get("kind") == "pond"]
    assert ends and all(((e[0] - pond[0]) / pond[2]) ** 2 + ((e[1] - pond[1]) / pond[3]) ** 2 <= 1.0 for e in ends)
    assert all(hg.sink.runs_downhill(c["poly"], plan.fall) for c in s.M["channels"])


def test_a_clean_searched_route_is_drawn_as_it_always_was(monkeypatch: pytest.MonkeyPatch) -> None:
    """The first searched route that passes every refusal is the one drawn - the constructed route is only the terminal."""
    plan = a_plan()
    plan.water_sink = "offmap"
    plan.brook = []
    drawn: list[tuple[list[tuple[float, float]], str]] = []
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 990.0))
    monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (1.0, 0.0))
    monkeypatch.setattr(hg.sink, "drain_run", lambda s_, pts, to: drawn.append((list(pts), to)))
    hg.sink.stage_sink(Settlement(W=plan.W, H=plan.H, seed=1), plan)
    route, to = drawn[0]
    assert to == "offmap" and len(route) == 3 and hg.sink.route_refusals(plan, route[0], (1.0, 0.0), True, route, []) == []


def test_the_constructed_route_ends_on_a_brook_across_it_and_records_the_confluence(monkeypatch: pytest.MonkeyPatch) -> None:
    plan, drawn, _out = _u_field_stage(monkeypatch)
    plan.brook = [(0.0, 2400.0), (1500.0, 2420.0), (3000.0, 2440.0)]
    hg.sink.stage_sink(Settlement(W=plan.W, H=plan.H, seed=1), plan)
    route, to = drawn[0]
    assert to == "stream" and plan.confluence == route[-1]


def test_the_constructed_route_runs_on_down_the_fall_until_it_is_downhill() -> None:
    """A hull walk that carries the run far across the fall: the leg off the canvas is lengthened until the whole run is
    downhill by the channel rule."""
    plan = a_plan()
    plan.W, plan.H = 3000, 1100
    plan.envelope = [(100.0, 900.0), (2900.0, 900.0), (2900.0, 1000.0), (100.0, 950.0)]
    route, to = hg.sink.hull_route(plan, (150.0, 925.0), (1.0, 0.0), [])
    assert to == "offmap" and hg.sink.runs_downhill(route, plan.fall)
    assert route[-1][1] > plan.H + 260.0 + 300.0, "lengthened past its first reach"


def test_a_pond_reached_only_across_the_brook_is_no_pond_and_the_field_drains_by_a_route_that_crosses_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """water:W08 at the pond run, on the violating case (feature 287 wave 5): the brook runs across the fall between the
    outfall and every seat the pond can take, so the ditch to the pond would cross the open water mid-run. The pond is
    refused and the field drains by the off-map routes, which refuse the crossing too - no channel crosses the brook."""
    from l7r.diagram.hamletgen.water.brook_rules import crosses_mid_run

    plan = a_plan()
    plan.water_sink = "pond"
    plan.brook = [(0.0, 1090.0), (1400.0, 1080.0)]
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.meta(name="Test", scale="hamlet", ftpx=1)
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 1010.0))
    monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (1.0, 0.0))
    back, sway = hg.sink.pond_seat(plan, (700.0, 1010.0), 116.0, 74.0)
    ditch = hg.sink.pond_run((700.0, 1010.0), (1.0, 0.0), (700.0 - plan.fall[1] * sway + plan.fall[0] * back, 1010.0 + plan.fall[1] * back + plan.fall[0] * sway), plan.fall)
    assert crosses_mid_run(plan.brook, ditch), "the case: the pond's ditch would cross the brook"
    hg.sink.lay_sink(s, plan)
    assert plan.water_sink == "offmap" and not s.M.get("pond")
    assert s.M["channels"] and not any(crosses_mid_run(hg.sink.drawn_brook(s, plan), c["poly"]) for c in s.M["channels"])


def test_the_confluence_is_the_nearest_one_the_brook_as_drawn_keeps_its_rules_with(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287 wave 5: the drain's confluence is held as a vertex when the brook is rounded (`drawn_course`), so it is
    judged with the brook as drawn (`confluence_keeps_the_brook`) - the nearest junction whose drawing breaks a rule of
    the brook is passed over for the next; where the constructed route's meeting would, the sink is refused by name."""
    plan = a_plan()
    plan.brook = [(1130.0, 400.0), (1130.0, 1600.0)]
    near = hg.brook_join(plan, (1050.0, 1050.0))
    assert near is not None
    other = hg.brook_join(plan, (1050.0, 1050.0), keeps=lambda q: q != near)
    assert other is not None and other != near and other[1] > near[1]
    assert hg.brook_join(plan, (1050.0, 1050.0), keeps=lambda q: False) is None
    tap = (700.0, 300.0)
    plan = a_plan()
    plan.brook = hg.water.brook.feed_brook(plan, tap)
    s = Settlement(W=plan.W, H=plan.H, seed=1)
    assert hg.sink.confluence_keeps_the_brook(s, plan, plan.brook[-2]), "no head race recorded yet: nothing to judge against"
    s.M["channels"].append({"poly": [list(tap), [720.0, 400.0]], "frm": {"kind": "stream"}, "to": {"kind": "field"}})
    k = plan.brook.index(tap) + 3
    mid = ((plan.brook[k][0] + plan.brook[k + 1][0]) / 2, (plan.brook[k][1] + plan.brook[k + 1][1]) / 2)
    assert hg.sink.confluence_keeps_the_brook(s, plan, mid)
    monkeypatch.setattr(hg.sink, "brook_violations", lambda course, plan_, sluice, ditches=(), joins=(): ["fold"] if joins else [])
    assert not hg.sink.confluence_keeps_the_brook(s, plan, mid)
    plan2, drawn, _out = _u_field_stage(monkeypatch)
    plan2.brook = [(0.0, 2400.0), (1500.0, 2420.0), (3000.0, 2440.0)]
    monkeypatch.setattr(hg.sink, "confluence_keeps_the_brook", lambda s_, plan_, q: False)
    with pytest.raises(hg.sink.SinkRefused, match="meets the brook"):
        hg.sink.stage_sink(Settlement(W=plan2.W, H=plan2.H, seed=1), plan2)


def test_the_pond_seat_steps_across_the_fall_to_where_its_ditch_crosses_no_brook() -> None:
    """water:W08 at the pond's seat (feature 287 wave 5): a brook ending just below the outfall lies across the straight
    seat's ditch; the seat steps across the fall to one whose ditch reaches the pond without crossing the water - the
    reservoir kept, as on the six maps of cohort 1-60 and the pool whose ditch crossed their brook at HEAD."""
    from l7r.diagram.hamletgen.water.brook_rules import crosses_mid_run

    plan = a_plan()
    out, heading = (700.0, 1010.0), (1.0, 0.0)
    brook = [(400.0, 1085.0), (715.0, 1080.0)]
    straight = hg.sink.pond_seat(plan, out, 116.0, 74.0)
    assert straight[1] == 0.0
    center = (out[0] + plan.fall[0] * straight[0], out[1] + plan.fall[1] * straight[0])
    assert crosses_mid_run(brook, hg.sink.pond_run(out, heading, center, plan.fall)), "the case: the straight seat's ditch crosses"
    back, sway = hg.sink.pond_seat(plan, out, 116.0, 74.0, heading, brook)
    assert sway != 0.0
    center = (out[0] - plan.fall[1] * sway + plan.fall[0] * back, out[1] + plan.fall[0] * sway + plan.fall[1] * back)
    assert not crosses_mid_run(brook, hg.sink.pond_run(out, heading, center, plan.fall))
