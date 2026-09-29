"""Feature 287, the water placers' wave 3 guarantees - each on constructed inputs that include the violating case.

water W42 (the sink's drain routes refuse a dike's crest off its gaps), labels L16 (the brook's rounding holds every
confluence), water W50 (the sty's seat reserved before the houses), the polder's crossing caps asking no plank of a
drain (ways W14's `plank_on_supply`), and the same-flank re-seat leaving the waterward fringe valid.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.hamletgen.pondstock import _bank_seats, reserve_sty_seat, stage_pond_stock, sty_on_near_half
from l7r.diagram.hamletgen.water.brook import course_corner, join_vertices, round_the_brooks
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.city.bridges import SUPPLY_ROLES
from l7r.diagram.settlement.fields.comb import channel_end_on_stream
from l7r.diagram.settlement.land.dikes import breaches_any_dike, course_breaches

from ._builders import a_plan

# ---- water W42: a drain never crosses a dike's crest off its gaps ------------------------------------------------------

CREST = [(380.0, 380.0), (1020.0, 380.0), (1020.0, 1020.0), (380.0, 1020.0)]  # a square crest round the square crop


def _dike(*gaps: tuple[float, float]) -> dict[str, Any]:
    return {"crest": [list(p) for p in CREST], "gaps": [list(g) for g in gaps]}


def test_a_course_crossing_the_crest_away_from_every_gap_breaches_it_and_one_at_a_gap_does_not() -> None:
    """W42: the rule's predicate (`course_breaches`) asked over the course walked at a foot - a long leg whose own midpoint
    is nowhere near the crest still breaches it where it crosses, 200 px from either sluice."""
    leg = [(700.0, 900.0), (700.0, 1500.0)]  # its midpoint (700, 1200) is 180 px off the crest
    assert not course_breaches(leg, CREST, [(380.0, 380.0)]), "the bare predicate reads midpoints only"
    assert breaches_any_dike(leg, [_dike((380.0, 380.0), (1020.0, 380.0))])
    assert not breaches_any_dike(leg, [_dike((700.0, 1020.0))]), "within the gap's reach: the outfall, a decided crossing"
    assert not breaches_any_dike(leg, []), "no dike, nothing to breach"


def test_the_route_refusals_name_the_dike() -> None:
    plan = a_plan()
    out = (700.0, 990.0)
    route = [out, (700.0, 1100.0), (700.0, 3200.0)]
    assert "dike" in hg.sink.route_refusals(plan, out, (0.0, 1.0), True, route, [], [_dike((380.0, 380.0))])
    assert hg.sink.route_refusals(plan, out, (0.0, 1.0), True, route, [], [_dike((700.0, 1020.0))]) == []


def _sink_stage(monkeypatch: pytest.MonkeyPatch, *gaps: tuple[float, float], sink: str = "offmap") -> tuple[Any, Settlement, list[tuple[list[tuple[float, float]], str]]]:
    plan = a_plan()  # falls due south, the square crop at x 400-1000, y 400-1000
    plan.water_sink = sink
    plan.brook = []
    s = Settlement(W=plan.W, H=plan.H, seed=plan.spec.seed)
    s.M["dikes"] = [_dike(*gaps)]
    drawn: list[tuple[list[tuple[float, float]], str]] = []
    monkeypatch.setattr(hg.sink, "drain_outfall", lambda s_, name: (700.0, 990.0))
    monkeypatch.setattr(hg.sink, "drain_heading", lambda s_, name: (0.0, 1.0))
    monkeypatch.setattr(hg.sink, "drain_run", lambda s_, pts, to: drawn.append((list(pts), to)))
    return plan, s, drawn


def test_the_drain_is_drawn_through_the_dike_only_at_its_gap(monkeypatch: pytest.MonkeyPatch) -> None:
    """W42's second half: the sink's searched routes ask the predicate, so the drain drawn leaves the dike at its gap."""
    _plan, s, drawn = _sink_stage(monkeypatch, (700.0, 1020.0))
    hg.sink.lay_sink(s, _plan)
    assert drawn and not breaches_any_dike(drawn[0][0], s.M["dikes"])


def test_a_drain_with_no_route_through_a_gap_is_refused_by_name_never_drawn_across_the_crest(monkeypatch: pytest.MonkeyPatch) -> None:
    """W42 / FR-005: every searched route and the constructed one cross the crest 200+ px from the only gap - the sink
    refuses by name rather than draw a breach."""
    plan, s, drawn = _sink_stage(monkeypatch, (380.0, 380.0))
    with pytest.raises(hg.sink.SinkRefused, match="crosses the dike"):
        hg.sink.lay_sink(s, plan)
    assert drawn == []


def test_a_confluence_reached_only_across_the_crest_is_not_taken(monkeypatch: pytest.MonkeyPatch) -> None:
    plan, s, drawn = _sink_stage(monkeypatch, (700.0, 1020.0))
    monkeypatch.setattr(hg.sink, "brook_join", lambda plan_, out: (1000.0, 1060.0))  # crosses the crest ~130 px east of the gap
    hg.sink.lay_sink(s, plan)
    assert drawn and drawn[0][1] == "offmap" and not breaches_any_dike(drawn[0][0], s.M["dikes"])


def test_a_pond_reached_only_across_the_crest_drains_off_the_frame_instead(monkeypatch: pytest.MonkeyPatch) -> None:
    """W42: the tameike's ditch is asked before the pond is dug; one that breaches sends the field off the frame."""
    plan, s, drawn = _sink_stage(monkeypatch, (700.0, 1020.0), sink="pond")
    calls: list[int] = []
    monkeypatch.setattr(hg.sink, "breaches_any_dike", lambda course, dikes: not calls and not calls.append(1))
    hg.sink.lay_sink(s, plan)
    assert plan.water_sink == "offmap" and not s.M.get("pond") and drawn and drawn[0][1] == "offmap"


# ---- labels L16: the rounding holds every confluence ------------------------------------------------------------------


def _bent() -> list[tuple[float, float]]:
    """A brook with a 100 degree corner at (300, 0), then a gentler one."""
    t = math.radians(100.0)
    b = (300.0 + 300.0 * math.cos(t), 300.0 * math.sin(t))
    return [(0.0, 0.0), (300.0, 0.0), b, (b[0] + 200.0, b[1] + 100.0)]


def test_every_confluence_stays_on_the_rounded_brook_and_the_corner_is_still_rounded() -> None:
    """L16's rounding half: a drain joining exactly on the 100 degree corner, a second joining mid-segment 5 px inside the
    corner's cut-back, and an intake mid-segment - after `round_the_brooks`, `channel_end_on_stream` holds for all three,
    the mid-segment confluence is a held vertex of the drawn course, and the corner is filleted."""
    s = Settlement(W=1200, H=1200, seed=1)
    s.meta(name="Rb", scale="hamlet", ftpx=1, down_deg=90)
    s.stream(_bent(), frm={"kind": "offmap"}, width=9)
    tangent = (300.0 - 2.5 * 9.0, 0.0)
    mid_join = (tangent[0] + 5.0, 0.0)
    s.M["channels"] += [
        {"poly": [[300.0, -80.0], [300.0, 0.0]], "frm": {"kind": "drain"}, "to": {"kind": "stream"}, "w": 2.5},
        {"poly": [[282.0, -90.0], list(mid_join)], "frm": {"kind": "drain"}, "to": {"kind": "stream"}, "w": 2.5},
        {"poly": [[100.0, 0.0], [100.0, -120.0]], "frm": {"kind": "stream"}, "to": {"kind": "field"}, "w": 2.5},
    ]
    round_the_brooks(s)
    drawn = [(float(p[0]), float(p[1])) for p in s.M["streams"][0]["poly"]]
    for c in s.M["channels"][-3:]:
        end = c["poly"][-1] if c["to"]["kind"] == "stream" else c["poly"][0]
        assert channel_end_on_stream(end, drawn), c
    assert mid_join in drawn, "the mid-segment confluence is held where it joins"
    assert (300.0, 0.0) not in drawn, "the corner is rounded, not held mitred"
    round_the_brooks(s)
    assert [(float(p[0]), float(p[1])) for p in s.M["streams"][0]["poly"]] == drawn, "a second pass draws the same course"


def test_join_vertices_inserts_an_end_on_a_segment_and_leaves_one_off_the_course() -> None:
    course = [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0)]
    out, held = join_vertices(course, [(40.0, 0.4), (300.0, 300.0), (100.0, 0.0), (0.0, 0.0)], hold_corners=False)
    assert (40.0, 0.0) in out and held[0] == (40.0, 0.0)
    assert (100.0, 0.0) not in held, "an end on a corner is left to the rounding"
    assert (0.0, 0.0) in held, "an end on the course's own end is no corner, and is held"
    assert join_vertices([(0.0, 0.0)], [(0.0, 0.0)]) == ([(0.0, 0.0)], [])
    assert course_corner((100.0, 0.0), course) and not course_corner((50.0, 0.0), course)
    assert not course_corner((100.0, 0.0), [(0.0, 0.0), (100.0, 0.0), (100.0, 0.0), (200.0, 0.0)]), "a repeated vertex turns nothing"


def test_the_drain_is_not_joined_to_the_brook_on_a_corner() -> None:
    """L16: the stride walk's first candidate on every leg is the leg's start - a corner - and a confluence held there would
    be a mitred bend. The nearest fallen point here IS the apex of a V; the join is taken off it."""
    plan = a_plan()
    plan.brook = [(1350.0, 950.0), (1100.0, 1150.0), (1350.0, 1350.0), (1350.0, 2400.0)]
    join = hg.brook_join(plan, (1050.0, 1050.0))
    assert join is not None and join != (1100.0, 1150.0) and not course_corner(join, plan.brook)


# ---- water W50: the sty's seat is reserved before the houses ----------------------------------------------------------


def _pond(x: float, y: float) -> dict[str, Any]:
    parcel = [(x - 60.0, y - 40.0), (x + 60.0, y - 40.0), (x + 60.0, y + 40.0), (x - 60.0, y + 40.0)]
    return {"parcel": parcel, "water": parcel, "kind": "growout"}


def _dikepond() -> tuple[Settlement, Any]:
    plan = hg.plan_site(hg.HamletSpec(name="X", seed=3, households=16, field_archetype="mulberry_dike_fishpond"))
    plan.seat = {"cx": 450.0, "cy": 150.0, "out": (0.0, -1.0)}
    s = Settlement(W=900, H=900, seed=1)
    s.meta(name="X", scale="hamlet")
    s.M["dikeponds"] = [_pond(450.0, 400.0), _pond(450.0, 650.0)]
    return s, plan


def test_the_reserved_sty_seat_is_taken_when_every_other_near_bank_seat_is_built_on() -> None:
    """W50: `reserve_sty_seat` decides the sty's seat once the flank is known and holds it in `block_polys` against the
    homesteads. Houses on every other near-half bank seat of both ponds (the ground the reservation leaves them): the
    stage still seats one sty, on the reserved seat, on the near half for the houses as seated."""
    s, plan = _dikepond()
    got = reserve_sty_seat(s, plan)
    assert got is not None and s.block_polys, "the seat is decided and held"
    (rx, ry), _rot, ri = got
    hold = s.block_polys[-1]
    assert ri == 0 and all(math.dist(p, (rx, ry)) > 30.0 for p in hold)
    hc = (450.0, 150.0)
    houses = [{"x": 450.0, "y": 100.0, "w": 20.0, "h": 14.0} for _ in range(30)]  # the village, above the ponds
    for pond in s.M["dikeponds"]:
        for q, _r in _bank_seats(pond["parcel"], hc):
            if sty_on_near_half(q, pond["parcel"], hc) and not hg.point_in_poly(q[0], q[1], hold):
                houses.append({"x": q[0], "y": q[1], "w": 20.0, "h": 14.0})
    s.M["houses"] = houses
    stage_pond_stock(s, plan)
    sties = s.M.get("pig_sties") or []
    assert len(sties) >= 1 and (sties[0]["x"], sties[0]["y"]) == (round(rx, 1), round(ry, 1))
    assert sty_on_near_half((rx, ry), s.M["dikeponds"][ri]["parcel"], (sum(h["x"] for h in houses) / len(houses), sum(h["y"] for h in houses) / len(houses)))


def test_a_reservation_off_the_near_half_for_the_seated_houses_gives_way_to_the_walk() -> None:
    s, plan = _dikepond()
    reserve_sty_seat(s, plan)
    s.M["houses"] = [{"x": 450.0, "y": 850.0, "w": 20.0, "h": 14.0}]  # the village turned out to stand below the ponds
    stage_pond_stock(s, plan)
    st = s.M["pig_sties"][0]
    assert st["pond"] == 1 and sty_on_near_half((st["x"], st["y"]), s.M["dikeponds"][1]["parcel"], (450.0, 850.0))


def test_no_reservation_where_the_hamlet_keeps_no_ponds_or_no_seat() -> None:
    s, plan = _dikepond()
    plan.seat = {}
    assert reserve_sty_seat(s, plan) is None
    s, plan = _dikepond()
    s.M["dikeponds"] = []
    assert reserve_sty_seat(s, plan) is None
    s, plan = _dikepond()
    s.M["dikepond_sluices"] = [{"a": [p[0], p[1]], "b": [p[0] + 0.1, p[1]]} for pond in s.M["dikeponds"] for p, _r in _bank_seats(pond["parcel"], (450.0, 150.0))]
    assert reserve_sty_seat(s, plan) is None, "a pond with every bank seat on a sluice gives no seat"


# ---- the polder's crossings ask no plank the law refuses; a same-flank re-seat keeps the fringe ----------------------


def test_no_polder_seat_asks_a_plank_of_a_ditch_the_law_refuses() -> None:
    """ways W14 (`plank_on_supply`): a footplank stands on a supply ditch. Every seg the caps give a plank to is, on the ring
    `build_polder` lays, a supply role - at the foot the village's crossings go on the toes, none on the drain."""
    from l7r.diagram.waterfields import build_polder

    roles = {c["seg"]: c["role"] for c in build_polder(2200, 2600, (360, 320), 21)["channels"] if c.get("seg")}
    assert set(roles) >= {"feeder", "e_toe", "w_toe", "drain", "lateral"}
    plan = a_plan(field_archetype="polder_grid")
    for out in ((1.0, 0.0), (-1.0, 0.0), (0.0, -1.0), (0.0, 1.0)):
        plan.seat = {"out": out}
        caps = hg.polder_crossing_caps(plan)
        assert all(roles[seg] in SUPPLY_ROLES for seg, n in caps.items() if n > 0), (out, caps)
        assert sum(caps.values()) >= 3, "the village still has its crossings"


def test_a_reseat_on_the_same_flank_leaves_the_fringe_and_the_crossings_as_they_were() -> None:
    """The polder re-seat (HOMES' `margin_ladder` keeps to the chosen seat's compass flank): the waterward flanks, their
    strips and the crossing caps read the flank alone, so a seat moved along it redraws nothing."""
    plan = a_plan(field_archetype="polder_grid")
    for first, other in (((1.0, 0.0), (0.8, 0.5)), ((0.0, 1.0), (-0.3, 0.9)), ((-1.0, 0.0), (-0.7, -0.6))):
        plan.seat = {"out": first}
        before = (hg.waterward_flanks(plan), hg.polder_crossing_caps(plan))
        plan.seat = {"out": other}
        assert (hg.waterward_flanks(plan), hg.polder_crossing_caps(plan)) == before
