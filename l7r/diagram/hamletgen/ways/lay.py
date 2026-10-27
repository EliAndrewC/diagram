"""A candidate lane held to the lane law's end rules BEFORE it is drawn (feature 417 T06, T31 part C item 1).

The settle's `settle_ends` mended the end rules after the web was laid - a needle, fold or connector hairpin re-aimed as a T,
a doubled tail or a shallow crossing cut - on lanes already drawn. Here each placer of an ordinary lane (the skeleton's arms,
the web's runs, the way onto the bund) asks the same predicates of its candidate against the lanes standing: the candidate
is re-aimed or cut (the new lane only, by the settle's own `reaimed`, `cut_at_tail` and `cut_at_shallow_crossing`), asked
again, and refused where it still breaks one, where the overlap matrix refuses the changed run, or where only a lane already
drawn could be moved. Nothing drawn is touched.

Research: plumbing - NONE: each rule is claimed at its predicate in `law` and at the settle's own repair it reuses
"""

from __future__ import annotations

import math
from typing import Any

from ..consts import Poly, Pt
from .geom import polyline_len

TRIES = 3
"""How many times a candidate is re-aimed or cut and asked again before it is refused - one fix per end and one for the
crossing, as the settle mended at most one meeting a lane a round.

Research: its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T06); three asks"""


def laid_lawfully(s: Any, run: Poly, width: float = 3.0, whole: bool = False, keep: Pt | None = None) -> Poly | None:
    """`run` held to the lane law's end rules (`_held`), each end that would arrive a few feet beside a junction already
    standing first gathered onto it (`gathered_forms`, feature 417 T06 part D): the gathered forms asked in turn, then the run as it
    came - a knot left is a lane laid, never a lane refused for want of a gather. A link (`whole`) is laid as it came and a
    run's joint (`keep`) stays where its link meets it, so neither is gathered.

    Research:
        lane ends gathered at lay - research/questions/0081-village-lanes.drawing.html: ends within 25 ft of one another are joined at a single point, so three lanes never arrive a few feet apart in a knot - the new lane's end moved onto the junction standing, never a drawn lane's; where no gathered form holds the lane is laid as it came and its knot is gathered by the settle's `settle_knots`, still a step (feature 417 T70)"""
    from .forced import lazy_ground

    run = [(float(q[0]), float(q[1])) for q in run]
    ends = () if whole else tuple(e for e in (0, -1) if keep is None or math.dist(run[e], keep) >= 1e-6)
    for form in [*gathered_forms(s, run, ends, lazy_ground(s.M, s)), run]:
        held = _held(s, form, width, whole, keep)
        if held is not None:
            return held
    return None


def gathered_forms(s: Any, run: Poly, ends: tuple[int, ...], blocked: Any) -> list[Poly]:
    """`run` with each of `ends` that stands a few feet beside a junction of the lanes standing - within the knot reach
    (`knots.lane_knots`' own, `KNOT_MARGIN * _KNOT_FT`) and beyond one point (`_JOINT_FT`), with lawful ground between
    (`blocked`, the knot rule's `ground_apart`) - moved onto the nearest such junction (`knots.moved_onto`, its forms in turn);
    none where no end stands so.

    Research:
        lane ends gathered at lay - research/questions/0081-village-lanes.drawing.html: ends within 25 ft are joined at a single point - the reach `KNOT_MARGIN * _KNOT_FT`, 1.0 x 25 ft (`gap_ways.KNOT_FT`)
        a knot is ends that could meet - research/questions/0081-village-lanes.drawing.html: ends a fence parts are not a knot, the join tested at the footpath's 3 ft"""
    from l7r.diagram.settlement.rolling.gap_ways import KNOT_MARGIN

    from .joints import _JOINT_FT
    from .knots import end_nodes, moved_onto
    from .smooth import _KNOT_FT

    if len(run) < 2 or not ends:
        return []
    nodes = [at for at, _members in end_nodes(list(s.M.get("lanes") or []))]
    forms: list[Poly] = []
    for e in ends:
        q = run[e]
        near = [at for at in nodes if _JOINT_FT < math.dist(at, q) <= KNOT_MARGIN * _KNOT_FT and not blocked(q, at, 3.0)]
        if near:
            forms += [f for f in moved_onto(run, e, min(near, key=lambda at: math.dist(at, q))) if f not in forms]
    return forms


def _held(s: Any, run: Poly, width: float = 3.0, whole: bool = False, keep: Pt | None = None) -> Poly | None:
    """`run` as it may be drawn among the lanes standing - re-aimed as a T where its end meets a way as a needle, a fold or a
    hairpin at the connector, cut where its tail doubles a way or it crosses one at a needle's angle - or None where it still
    breaks one after `TRIES` asks, or where a lane already drawn would have to move (its end a needle along the candidate). Each
    candidate changed is squared at the water again (`square_run`) and asked again. `whole`: the candidate is laid only as it
    came - a link, whose join was computed for it (`serve._lay_web_lane`); `keep`: a point the candidate must still pass
    through as laid - where the run a link joins meets its link.

    Research:
        lanes met end to end read as one - research/questions/0081-village-lanes.drawing.html: a needle, fold or hairpin re-laid as a T
        a doubled tail asked at 15 degrees - DEVIATION research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees, cut where it comes alongside at whichever end runs on (the candidate is an ordinary lane, never a household's way, whose door end the page keeps) - asked at `_DOUBLED_DEG`, 15, the one constant every doubled-tail reader shares (the GM's 2026-10-25 ruling: 20 a goal, not a hard requirement), and doubled with no way alongside within it, not laid - a departure the code keeps until feature 405 T101
        two paths side by side become one - research/questions/0081-village-lanes.drawing.html: a lane crossing another at under 20 degrees (`law.NEEDLE_DEG`, 20) cut at the crossing (`cut_at_shallow_crossing`); where no cut holds (the cut would leave the connector's network or no lane), not laid - a value of ours, the page silent on a crossing no cut can mend
        a bare leg folded on a way not laid - research/questions/0081-village-lanes.drawing.html: where a fold cannot be pulled straight the meeting moves back one bend (itself a GUESS there); a two-point candidate has no bend to move back to, and is refused - a value of ours (feature 417 T06), as the settle dropped the shorter of two bare legs
        a lane with no width judged as a footpath - research/questions/0081-village-lanes.drawing.html: a candidate with no width given is judged at the footpath's 3 ft
        a drawn lane not moved for a new one - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each way laid in turn; a candidate that only a standing lane's move could admit is not laid"""
    from . import law
    from .forced import lazy_ground
    from .settle.shapes import _as_end, _back, reaimed
    from .squaring import cut_at_shallow_crossing, square_run
    from .sweeps import _DOUBLED_DEG
    from .tails import along_tail, cut_at_tail

    M = s.M
    lanes = list(M.get("lanes") or [])
    k = len(lanes)
    blocked = lazy_ground(M, s)
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    run = first = [(float(q[0]), float(q[1])) for q in run]
    for _ in range(TRIES):
        run = square_run(M, run)  # ...a re-aimed or cut candidate squared at the water again, and asked again as squared
        if len(run) < 2 or polyline_len(run) < 1.0:
            return None
        tl = [*lanes, {"pts": [list(q) for q in run], "w": width}]
        fix: Poly | None = None
        settled = True
        for n, e, m, _u, _v in law.needle_ends(tl, blocked):
            if m == k and n != k:
                return None  # ...a standing lane's end a needle along the candidate: only that lane's move could mend it
            if n == k:
                fix, settled = _back(reaimed(_as_end(run, e), law.lane_pts(tl[m]), bool(tl[m].get("connector"))), e), False
                break
        if settled:
            for ci, n, e in law.connector_hairpin_ends(tl, blocked):
                if n == k:
                    fix, settled = _back(reaimed(_as_end(run, e), law.lane_pts(tl[ci]), connector=True), e), False
                    break
        if settled:
            for i, ei, j, ej in law.folded_joint_pairs(tl, blocked):
                if k in (i, j):
                    me, other, oe = (ei, j, ej) if i == k else (ej, i, ei)
                    seq = _as_end(run, me)
                    if len(seq) < 3:
                        return None  # ...a bare leg folded on a standing way: the settle dropped the shorter, here the candidate
                    fix, settled = _back(reaimed(seq, _as_end(law.lane_pts(tl[other]), oe)), me), False
                    break
        if settled and law.doubled_tails({**M, "lanes": tl}, only=k):
            for o in lanes:
                op = law.lane_pts(o)
                if len(op) < 2:
                    continue
                hit = next(((q, at, back) for q, back in ((run, False), (run[::-1], True)) if (at := along_tail(q, op, deg=_DOUBLED_DEG)) is not None), None)
                if hit is not None:
                    q, at, back = hit
                    cut = cut_at_tail(q, at, op)
                    fix, settled = (cut[::-1] if back else cut), False
                    break
            if settled:
                return None  # ...doubled, with no way alongside within `_DOUBLED_DEG` to cut it at: not laid
        if settled:
            for i, _seg, o, _x in law.shallow_crossing_at(tl):
                if k in (i, o):
                    got = cut_at_shallow_crossing(tl, k, o if i == k else i, centers)
                    if got is None:
                        return None
                    fix, settled = got[0], False
                    break
        if settled:
            served = _served(s, lanes, run, width)
            # ...a re-aimed or cut candidate asked of the overlap matrix again: the caller admitted the run it handed in, not this
            if served is not None and ((whole and served != first) or (keep is not None and not any(math.dist(q, keep) < 1e-6 for q in served))):
                return None
            return served if served is not None and (served == first or s.admits_lane(served, width)) else None
        if whole:
            return None  # ...a join computed for the candidate as it came holds only for it unchanged (`whole`)
        run = [(float(q[0]), float(q[1])) for q in fix or []]
    return None


def _served(s: Any, lanes: list[dict[str, Any]], run: Poly, width: float) -> Poly | None:
    """`run` with an end cut back past the doorstep where it would be a third end at one farmhouse, then trimmed to service
    (the trim every ordinary lane had at the settle's `settle_dangling`), or None where nothing serving is left.

    Research:
        no fan of stubs at a door - GUESS: searched, the record silent (feature 417 T29 pass A2, 2026-10-25) - one main door served a minka's household (JAANUS, Edo period, pass A2); past two ends at one house, the candidate's cut back past the doorstep
        a lane ends at the dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end within 60 ft of the house or 12 ft of its built ground reaches it on any side; one that reaches nothing is trimmed to service, else not laid"""
    from . import law
    from .arcs import sub_run
    from .geom import _trim_to_service, memo_ground, steading_footprints, worked_ground
    from .settle.shapes import _as_end, _back

    M = s.M
    k = len(lanes)
    houses = M.get("houses") or []
    for h, ends in law.fronting_ends({**M, "lanes": [*lanes, {"pts": [list(q) for q in run], "w": width}]}).items():
        mine = [e for i, e in ends if i == k]
        if len(ends) <= law.DOORSTEP_MAX or not mine:
            continue  # ...a standing lane's crowding is not the candidate's to mend; the candidate's own end at a full door is
        # cut back past the doorstep, or the candidate is not laid where nothing stands beyond it
        c = (float(houses[h]["x"]), float(houses[h]["y"]))
        seq = _as_end(run, mine[0])
        walk = next((polyline_len(seq[: j + 1]) for j in range(len(seq) - 1, -1, -1) if math.dist(seq[j], c) > law.DOORSTEP_FT), 0.0)
        if walk <= 0:
            return None
        run = _back(sub_run(seq, 0.0, walk), mine[0])
    ground = memo_ground(s, "worked", worked_ground)
    segs = [sg for o in lanes if len(o["pts"]) >= 2 for sg in zip(law.lane_pts(o), law.lane_pts(o)[1:], strict=False)]
    run = _trim_to_service(run, segs, [(float(h["x"]), float(h["y"])) for h in houses], ground, (), steading_footprints(M))
    if len(run) < 2 or polyline_len(run) < 1.0:
        return None
    tl = [*lanes, {"pts": [list(q) for q in run], "w": width}]
    return None if law.dangling_lane_ends({**M, "lanes": tl}, ground, only=k) else run
