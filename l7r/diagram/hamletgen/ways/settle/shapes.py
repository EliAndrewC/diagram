"""The web settles itself - the settle's bookkeeping and its first repairs: applying a lane's pieces, the crossing and foul cuts, the shapes, the ways out, an end re-aimed. Split from `ways/settle.py` at the 1,000-line bar (feature 405 T54, under T53's rule); the package docstring (`settle/__init__.py`) is the whole account.

Research: settle plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.overlap.registry import forbidden_segment
from l7r.diagram.settlement import seg_closest, seg_dist
from l7r.diagram.settlement._knobs import bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import flooded_ground
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes

from ...consts import TAIL_CUT_FT, WEB_CLEARANCE, WEB_FABRIC_GAP, Poly, Pt
from .. import law
from ..arcs import arc_at, cut_around, sub_run
from ..checks import square_crossings
from ..corridors import (
    is_tree,
)
from ..fabric import _crosses_fabric, house_hit
from ..fabric import lane_fabric as _fabric
from ..forced import lazy_ground
from ..geom import _TOUCH_GAP, lane_owner, polyline_len
from ..joints import _JOINT_FT
from ..squaring import (
    SQUARE_MARGIN_FT,
    _pts,
)

SETTLE_ROUNDS = 8
"""Repair rounds before the lanes still breaking a rule are dropped whole. Each round runs every rule once; a measured
pool map settles in one or two (T55's measurement), so eight is a bound, not a tuning."""

CROSSING_GAP_FT = 2.0
"""How far past the water's edge each piece of a cut crossing stops - the lane ends on the bank, not in the water.

Research: a cut crossing ends on the bank - UNRESEARCHED: 2 ft past the water's edge"""

# ---- a lane as a run of arc length -----------------------------------------------------------------------------------


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(a, 1), round(b, 1)] for a, b in p]


def apply_pieces(s: Any, edits: Mapping[int, list[Poly]]) -> int:
    """Replace each lane `i` of `edits` by its pieces - the first in place, record and ink together, the rest as new lanes of

    Research:
        split piece's room - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each split piece keeps WEB_CLEARANCE, the 18 ft lane room (9 ft each side of its middle), whatever its source kept
        split piece's width - research/questions/0081-village-lanes.drawing.html: a piece with no width is drawn 3 ft wide, a footpath
    the same width and kind - and drop a lane left with no piece of 1 ft or more. Returns the lanes changed."""
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    drops = []
    for i, pieces in edits.items():
        ln = lanes[i]
        keep = [q for q in pieces if len(q) >= 2 and polyline_len(q) >= 1.0]
        if not keep:
            drops.append(i)
            continue
        if not s.reshape_lane(ln, keep[0]):
            continue  # the matrix refuses what the cut would leave (feature 287 M8): the lane stands as it was
        s.reink_lane(i)
        for q in keep[1:]:
            s.lane(q, width=float(ln.get("w") or 3.0), clearance=WEB_CLEARANCE, worn=bool(ln.get("worn", True)))
            lanes[-1].update({key: ln[key] for key in ("role", "web") if key in ln})
    if drops:
        s.drop_lanes(drops)
    return len(edits)


def _ordinary(M: Mapping[str, Any]) -> list[int]:
    """The lanes a repair may cut: every lane but the tree (`is_tree` - the connector and the drawn access corridors)."""
    return [i for i, ln in enumerate(M.get("lanes") or []) if not is_tree(ln) and len(ln.get("pts") or []) >= 2]


# ---- step 2: a lane's own shape and its crossings ----------------------------------------------------------------------


Yards = list[tuple[Poly, Pt | None]]


def theirs(yards: Yards, owner: Pt | None = None) -> list[Poly]:
    """The yards and gardens a lane may not come near: all but its OWN household's, where it is a household's own way
    (`owner`, `lane_owner`) - every one where it is not (405 T18: every steading within `DOORSTEP_FT`, 80 ft, of either end
    was exempt, so a neighbor's garden beside a junction lost the gap; 0246 gives the exemption to a household's own way, and
    a back lane or cross lane belongs to no household).

    Research:
        a lane arrives at its own dooryard - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: its way leaves its dooryard round its own beds and fixtures
        its own household the one it serves - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the gap is kept from another household's garden, and a household's own way may run beside its own - the lane's record names its household (`of`, `serves`); a lane with none is no household's own"""
    return [poly for poly, own in yards if own is None or owner is None or math.dist(own, owner) > 1.0]


def fouled_segment(
    p: Poly,
    width: float,
    houses: Sequence[Mapping[str, Any]],
    yards: Yards,
    solid: Sequence[tuple[float, float, float, float]],
    fixtures: Sequence[Poly] = (),
    M: Any = None,
    owner: Pt | None = None,
    gap: float = WEB_FABRIC_GAP,
) -> int | None:
    """The first segment of `p` that fouls the fabric: ink on a farmhouse (`house_hit`), within `gap` (`WEB_FABRIC_GAP` unless
    the caller passes another) of another household's yard or garden (`theirs`), a long leg through a building's box (`law.breaks_through`),
    a tread over a farmstead fixture, the lane's own household's too (`law.over_a_fixture`), or a tread the overlap matrix
    forbids on what stands on `M` (`registry.forbidden_segment`, feature 287 M8: a yard, a garden, a well, a burial
    ground - its own household's too, since a path arrives at its dooryard and does not cross it).

    Research:
        no tread on a farmhouse - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html
        off another household's garden - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the line within `gap`, `WEB_FABRIC_GAP` (7 ft) unless the caller passes another
        a knot's join beside a fence - DEVIATION research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the knots step's second pass passes 3 ft (`WEB_CROP_GAP`'s value) for the page's 7 ft - the exception the page records, with its reason (405 T114)
        off another household's yard - UNRESEARCHED: the garden fence's gap (`gap`, 7 ft unless the caller passes another) held off a yard too; no page sets a gap from a yard
        no long leg through a building - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `law.breaks_through`
        off the fixtures - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: its own household's too
        what the overlap matrix forbids - NONE: each pair is claimed in the matrix"""
    near = theirs(yards, owner)
    over = law.over_a_fixture(p, width, fixtures) if fixtures else None
    matrix = forbidden_segment(M, "lanes", p, width) if M is not None else None
    for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
        if k in (over, matrix):
            return k
        if house_hit([a, b], width, houses) or _crosses_fabric([a, b], near, gap):
            return k
        if law.breaks_through([a, b], solid):
            return k
    return None


def _crossing_fault(M: Mapping[str, Any], i: int, p: Poly, wet: Sequence[Poly]) -> list[Poly] | None:
    """The pieces lane `i` is cut into for its first crossing fault, or None: a brook crossed twice (the stretch between the
    two crossings goes), a crossing off a ford, off square after the squaring, or where no deck seats (the crossing goes).

    Research:
        brook crossed twice - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the stretch between goes
        crossed off a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the crossing goes
        crossed off square - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html,
            research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the crossing goes
        a crossing no deck seats - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html: squared, else cut"""
    ftpx = float((M.get("meta") or {}).get("ftpx") or 1.0)
    gap = CROSSING_GAP_FT / ftpx
    for brook in law._brooks(M):
        xs = law.crossing_points(p, brook)
        if len(xs) >= 2:
            (k0, x0), (k1, x1) = xs[0], xs[1]
            return [q for q in (sub_run(p, 0.0, arc_at(p, k0, x0) - _cut_gap(M, x0) - gap), sub_run(p, arc_at(p, k1, x1) + _cut_gap(M, x1) + gap, polyline_len(p))) if q]
    lone = {**M, "lanes": [M["lanes"][i]]}
    for _j, k, x in law.off_ford_at(lone):
        return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    for water in ("brook", "channel"):
        for _j, k, x, _off in law.oblique_at(lone, water):
            return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    ln = M["lanes"][i]
    width = float(ln.get("w") or 3.0)
    waters = bridge_crossed_waters(M)
    for k, x in law.undeckable_at(p, width, waters, ftpx, wet, M):
        # A CROSSING NO DECK SEATS is squared to the water it crosses first - a square deck is the shortest, and the
        # one most likely to land on the bank (the field path over its canal, R3) - and cut only if even that will not seat
        for wpts, ww in waters:
            course = [(float(q[0]), float(q[1])) for q in wpts]
            if len(course) >= 2 and any(math.dist(x, y) < 1.0 for _k, y in law.crossing_points(p, course)):
                sq = square_crossings(p, course, float(ww) / 2 + SQUARE_MARGIN_FT / ftpx)
                if sq != p and not law.undeckable_at(sq, width, waters, ftpx, wet, M):
                    return [sq]
        return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    return None


def _cut_gap(M: Mapping[str, Any], x: Pt) -> float:
    """Half the width of the widest recorded water within reach of the crossing `x` - where its bank stands.

    Research: lane cut at the water's bank - UNRESEARCHED: a lane cut at a water crossing stops half the widest nearby water's width off the crossing, 3 ft where none is recorded"""
    near = [
        float(w) / 2
        for wpts, w in bridge_crossed_waters(M)
        if len(wpts) >= 2 and min(seg_dist(x[0], x[1], (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in zip(wpts, wpts[1:], strict=False)) <= float(w)
    ]
    return max(near, default=3.0)


def _unkinked(p: Poly, span: tuple[str, int, int]) -> list[Poly]:
    """A run that doubles back loses its returning leg (the shorter arm): 0081 cuts one under 40 ft, and a lane never
    doubles back, so a longer one goes too - left standing it broke the law every round and the last resort dropped the whole
    lane (feature 328 wave 45, spec-fidelity). One that zigzags is pulled straight - its two turns dropped, the way running from
    the vertex before the first to the vertex after the second (it cut the middle out, leaving two lanes where there was one).

    Research:
        no hairpin or zigzag - research/questions/0081-village-lanes.drawing.html: "a returning leg under 40 ft is cut"; and two turns of more than 50 degrees within 40 ft of path are pulled straight
        a returning leg of 40 ft or more - GUESS research/questions/0081-village-lanes.drawing.html: cut as a shorter one is - the page says a lane never doubles back but gives the cut only under 40 ft"""
    kind, ka, kb = span
    if kind == "doubles back":
        head, tail = p[: ka + 1], p[ka:]
        return [max(head, tail, key=polyline_len)]
    return [[*p[:ka], *p[kb + 1 :]]]


def settle_shapes(s: Any) -> int:
    """Step 2: cut from every ordinary lane what breaks its own shape or its crossings (ways W07, W09, W11, W12, W18, W19),
    and take a hook off the connector's end. One fault per lane per round; the next round asks again.

    Research:
        a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: re-laid as a T where it joins a way, else cut
        no hairpin or zigzag - research/questions/0081-village-lanes.drawing.html: cut as `_unkinked` cuts it
        crossings and fouls - NONE: claimed at `_crossing_fault` and `fouled_segment`
        a fouling segment cut out - UNRESEARCHED: a lane's fouling segment is cut out and the lane split into its two remaining pieces
            (405 T127)"""
    M = s.M
    lanes = M.get("lanes") or []
    yards, houses = _fabric(s)
    solid = law.solid_boxes(M)
    fixtures = law.fixture_quads(M)
    wet = flooded_ground(M)
    edits: dict[int, list[Poly]] = {}
    blocked = lazy_ground(M, s)  # ...a hook or kink the ground forces is walked round what stands there, not repaired (feature 385 plan D2)
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 2 or (is_tree(ln) and not ln.get("connector")):
            continue
        ends = law.hook_faults(p, float(ln.get("w") or 3.0), blocked)
        if ends:
            # A HOOK is a lane overshooting the way it joins and bending back onto it: re-laid as a T on that way where it
            # joins one (so the web stays one network), else its hook leg is taken off
            seq = _as_end(p, ends[0])
            j = joined_way(lanes, i, seq[-1])
            edits[i] = [_back(reaimed(seq, _pts(lanes[j]), bool(lanes[j].get("connector"))) if j is not None else seq[:-1], ends[0])]
            continue
        if ln.get("connector"):
            continue
        spans = law.kink_faults(p, float(ln.get("w") or 3.0), blocked)
        if spans:
            edits[i] = _unkinked(p, spans[0])
            continue
        pieces = _crossing_fault(M, i, p, wet)
        if pieces is not None:
            edits[i] = pieces
            continue
        k = fouled_segment(p, float(ln.get("w") or 3.0), houses, yards, solid, fixtures, M, lane_owner(ln))
        if k is not None:
            edits[i] = [q for q in (p[: k + 1], p[k + 1 :]) if len(q) >= 2]  # the fouling segment goes; a lane of one goes whole
    return apply_pieces(s, edits)


# ---- step 3: the ways out ----------------------------------------------------------------------------------------------


def settle_way_outs(s: Any) -> int:
    """Step 3 (ways W08): while some household's way out crosses one brook more than once (`law.way_out_carriers`), cut the
    crossing nearest that household out of the ordinary lane that carries it. WHERE ONLY TREE LANES CARRY IT (a corridor, a
    spur or the field way, laid when a lane since cut gave that household a shorter way out), the first of them goes whole:
    step 4 lays its reach again under `Lawful`, which refuses a lane that adds such a way out - so the tree is no exemption
    from the rule, only from the cutting.

    Research: no way out over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    M = s.M
    lanes = M.get("lanes") or []
    carriers = law.way_out_carriers(M, departure_routes(M))
    for i, k, y in carriers:
        if not is_tree(lanes[i]):
            p = _pts(lanes[i])
            return apply_pieces(s, {i: cut_around(p, arc_at(p, k, y), _cut_gap(M, y) + CROSSING_GAP_FT)})
    if carriers:
        s.drop_lanes([carriers[0][0]])
        return 1
    return 0


# ---- step 4: where lanes end and meet ----------------------------------------------------------------------------------


def joined_way(lanes: Sequence[Mapping[str, Any]], i: int, q: Pt) -> int | None:
    """The index of the nearest OTHER lane whose tread the point `q` stands on (within `law.JOIN_TOL`), or None."""
    best: tuple[float, int | None] = (law.JOIN_TOL, None)
    for j, ln in enumerate(lanes):
        o = _pts(ln)
        if j == i or len(o) < 2:
            continue
        d = min(seg_dist(q[0], q[1], u, v) for u, v in zip(o, o[1:], strict=False))
        if d <= best[0]:
            best = (d, j)
    return best[1]


def _as_end(p: Poly, end: int) -> Poly:
    """`p` oriented so the named end (-1 last, 0 first) is its last point."""
    return p if end == -1 else p[::-1]


def _back(q: Poly, end: int) -> Poly:
    return q if end == -1 else q[::-1]


def _foot(q: Pt, tread: Poly) -> Pt:
    """The point of the run `tread` nearest `q`."""
    return min((seg_closest(q[0], q[1], u, v) for u, v in zip(tread, tread[1:], strict=False)), key=lambda f: math.dist(q, f))


meets_clean = law.meets_clean


def _crossing(a: Pt, b: Pt, c: Pt, d: Pt) -> Pt | None:
    """Where leg a-b crosses tread c-d more than `_JOINT_FT` (1 ft, two ends one point) inside both - measured in feet, where `geom._seg_cross` measures its
    margin as a share of a segment (60 ft on a 3,000 ft track, which missed cohort seed 10's crossing 30 ft from the track's
    head - 405 T134, D124).

    Research: plumbing - NONE: segment geometry"""
    r, q = (b[0] - a[0], b[1] - a[1]), (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) < 1e-9:
        return None
    w = (c[0] - a[0], c[1] - a[1])
    t, u = (w[0] * q[1] - w[1] * q[0]) / den, (w[0] * r[1] - w[1] * r[0]) / den
    la, lc = math.hypot(*r), math.hypot(*q)
    if _JOINT_FT < t * la < la - _JOINT_FT and _JOINT_FT < u * lc < lc - _JOINT_FT:
        return (a[0] + t * r[0], a[1] + t * r[1])
    return None


JOIN_ROLE = "join-orphans"
"""The role of a lane laid only to join two others - the web's orphan links (`sweeps._join_orphan_ways`, named by its pass).

Research: a lane laid only to join two others - research/questions/0081-village-lanes.drawing.html: "A lane laid only to join two others ends where it first meets one" (0081)"""

_CROSSING_TAIL_FT = TAIL_CUT_FT  # feature 417 T05: the one constant
"""Research: a tail beyond a crossing - research/questions/0081-village-lanes.drawing.html: "A tail of under 40 ft beyond a crossing is cut" (0081)"""


def reaimed(seq: Poly, tread: Poly, connector: bool = False, joiner: bool = False) -> Poly:
    """`seq` (ending on the way `tread`) re-laid to meet it cleanly (`meets_clean`): FIRST, where it crossed the way before
    its end, cut at that first crossing - when the tail beyond it is under `_CROSSING_TAIL_FT`, or however long it is for a
    `joiner` (a lane laid only to join two others, `JOIN_ROLE`) - 405 T134, D124: cohort seed 10 with T26's sheds, an orphan
    link crossing the track 30 ft from its head and hooking back to the head was teed from its last vertex 12 ft from the
    head, a knot; otherwise from the last vertex before its end
    whose leg to its foot on the tread keeps the law, that leg - never longer than what it replaces, since a foot is the
    nearest point; a vertex already standing on the tread simply ends the lane there. With no such vertex the last leg is
    dropped.

    Research:
        a lane meets another as a T - research/questions/0081-village-lanes.drawing.html: the end re-laid, never longer
        a tail beyond a crossing cut - research/questions/0081-village-lanes.drawing.html: "A tail of under 40 ft beyond a crossing is cut. A lane laid only to join two others ends where it first meets one, its tail cut however long it is"
        an end within a hand's width ends there - UNRESEARCHED: a vertex within `_TOUCH_GAP` (4 ft) of the way ends the lane at it, unjoined
            by ink (405 T127)"""
    # ...A TAIL BEYOND A CROSSING (0081): cut where the lane first crossed the way - under 40 ft, or any length for a joiner
    for k in range(len(seq) - 2):
        x = next((c for u, v in zip(tread, tread[1:], strict=False) if (c := _crossing(seq[k], seq[k + 1], u, v)) is not None), None)
        if x is not None:
            cand = [*seq[: k + 1], x]
            if (joiner or polyline_len([x, *seq[k + 1 :]]) < _CROSSING_TAIL_FT) and math.dist(cand[-2], x) > 1e-6 and meets_clean(cand, tread, connector):
                return cand
            break
    for m in range(len(seq) - 2, -1, -1):
        b = seq[m]
        f = _foot(b, tread)
        cand = seq[: m + 1] if math.dist(b, f) <= _TOUCH_GAP else [*seq[: m + 1], f]
        if len(cand) >= 2 and cand != seq and meets_clean(cand, tread, connector):
            return cand
    return seq[:-1]
