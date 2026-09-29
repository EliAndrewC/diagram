"""The web settles itself: the LAST pass of `stage_web` (feature 287, M4).

WHY IT EXISTS. The web is some forty passes, each with its own partial guard - "no worse than it was", "the least bad",
"keep the orphan" - and nothing after them re-asks the rules the finished-map tests assert. So a rule held on the seeds the
tests roll and nothing stopped the next seed breaking it. This pass asks every rule of the lane law (`law.py`, the ONE
predicate per rule that the tests call too) of the web as it stands, and repairs what breaks one, until a whole round
changes nothing. It is the guarantee; the passes before it are best-effort drawing.

WHAT A REPAIR MAY DO. It only takes material AWAY from an ordinary lane - cuts a crossing, a fold or a foul out of it,
shortens an end, re-aims an end's last leg at the foot of its own previous vertex (never longer than the leg it replaces),
drops a piece that no longer joins the connector's network - or squares a crossing. It never moves the connector, except to
take a hook off its end. That is the termination argument: every repair but the squaring strictly shortens the non-connector
web, and the squaring is idempotent (`checks.square_crossings`). Should the rounds run out with a rule still broken, the
lanes still breaking one are dropped whole, round by round, until none is (FR-005: a lane that cannot be repaired is dropped;
it is never kept as "the least bad").

WHAT IT CANNOT DO ALONE. A lane it cuts may have been some farmhouse's only way. The access corridor reserved at seating
(M3, the homesteads area) is what serves that house; until the corridor lands, `stage_web` redraws the straggler paths once
after this pass and settles again, and the driver's re-roll still stands behind `unreached_houses` (T66 retires it).

THE CROSSINGS ARE SQUARED HERE (ways W11): the squaring `stage_crossings` did after the woods now runs as this pass's first
step, so every guarantee below is judged on the squared lane and no stage after the web rewrites one."""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_closest, seg_dist
from l7r.diagram.settlement._knobs import bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import flooded_ground
from l7r.diagram.settlement.structures.fixtures._helpers import departure_routes

from ..consts import WEB_CLEARANCE, Poly, Pt
from . import law
from .checks import square_crossings, unreached_houses
from .clearance import kink_spans
from .fabric import _crosses_fabric, _homestead_polys, house_hit
from .geom import _TOUCH_GAP, _components, _trim_to_service, memo_ground, polyline_len, steading_footprints, worked_ground
from .joints import joints
from .sweeps import _DOUBLED_DEG, along_tail, cut_at_tail

SETTLE_ROUNDS = 8
"""Repair rounds before the lanes still breaking a rule are dropped whole. Each round runs every rule once; a measured
pool map settles in one or two (T55's measurement), so eight is a bound, not a tuning."""

SQUARE_PASSES = 4
"""How many times one lane is squared against one water in a round - squaring is idempotent after the first, so this is
the bound for a lane crossing the same course several times."""

CROSSING_GAP_FT = 2.0
"""How far past the water's edge each piece of a cut crossing stops - the lane ends on the bank, not in the water."""

SQUARE_MARGIN_FT = 6.0
"""The square leg's reach past the water's half-width (`stage_crossings`' own figure, moved here with the squaring)."""


# ---- a lane as a run of arc length -----------------------------------------------------------------------------------


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in (ln.get("pts") or [])]


def sub_run(p: Poly, s0: float, s1: float) -> Poly:
    """The part of the run `p` between arc lengths `s0` and `s1` (clamped to the run) - [] when that is nothing."""
    total = polyline_len(p)
    s0, s1 = max(0.0, s0), min(total, s1)
    if s1 - s0 < 1e-6 or len(p) < 2:
        return []
    out: Poly = []
    acc = 0.0
    for a, b in zip(p, p[1:], strict=False):
        d = math.dist(a, b)
        lo, hi = acc, acc + d
        if hi >= s0 and lo <= s1 and d > 0:
            t0 = max(0.0, (s0 - lo) / d)
            t1 = min(1.0, (s1 - lo) / d)
            q0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            q1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            if not out:
                out.append(q0)
            if math.dist(out[-1], q1) > 1e-9:
                out.append(q1)
        acc = hi
    return out if len(out) >= 2 else []


def arc_at(p: Poly, k: int, x: Pt) -> float:
    """The arc length along `p` of the point `x` on its segment `k`."""
    return polyline_len(p[: k + 1]) + math.dist(p[k], x)


def cut_around(p: Poly, at: float, gap: float) -> list[Poly]:
    """`p` with the stretch within `gap` of arc length `at` taken out: the pieces either side."""
    return [q for q in (sub_run(p, 0.0, at - gap), sub_run(p, at + gap, polyline_len(p))) if q]


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(a, 1), round(b, 1)] for a, b in p]


def apply_pieces(s: Any, edits: Mapping[int, list[Poly]]) -> int:
    """Replace each lane `i` of `edits` by its pieces - the first in place, record and ink together, the rest as new lanes of
    the same width and kind - and drop a lane left with no piece of 1 ft or more. Returns the lanes changed."""
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    drops = []
    for i, pieces in edits.items():
        ln = lanes[i]
        keep = [q for q in pieces if len(q) >= 2 and polyline_len(q) >= 1.0]
        if not keep:
            drops.append(i)
            continue
        ln["pts"] = _rounded(keep[0])
        s.reink_lane(i)
        for q in keep[1:]:
            s.lane(q, width=float(ln.get("w") or 3.0), clearance=WEB_CLEARANCE, worn=bool(ln.get("worn", True)))
            lanes[-1].update({key: ln[key] for key in ("role", "web") if key in ln})
    if drops:
        s.drop_lanes(drops)
    return len(edits)


def _ordinary(M: Mapping[str, Any]) -> list[int]:
    return [i for i, ln in enumerate(M.get("lanes") or []) if not ln.get("connector") and len(ln.get("pts") or []) >= 2]


# ---- step 1: every crossing square -------------------------------------------------------------------------------------


def square_waters(M: Mapping[str, Any]) -> list[tuple[Poly, float]]:
    """(course, half-width plus the leg's margin) for the brook and every drawn channel - what `stage_crossings` squared."""
    margin = SQUARE_MARGIN_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = [([(float(x), float(y)) for x, y in f["poly"]], float(f.get("w", 8.0)) / 2 + margin) for f in M.get("streams") or [] if len(f.get("poly") or ()) >= 2]
    waters += [([(float(x), float(y)) for x, y in c["pts"]], float(c.get("w0", 4.0)) / 2 + margin) for c in M.get("drawn_channels") or [] if len(c.get("pts") or ()) >= 2]
    return waters


def square_every_crossing(s: Any) -> int:
    """Square every lane at every crossing of the brook and the drawn channels (`square_crossings`), the connector's too.
    Returns the lanes changed."""
    waters = square_waters(s.M)
    lanes = s.M.get("lanes") or []
    changed = 0
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 2:
            continue
        q = p
        for course, half in waters:
            for _ in range(SQUARE_PASSES):
                nq = square_crossings(q, course, half)
                if nq == q:
                    break
                q = nq
        if q != p:
            ln["pts"] = _rounded(q)
            s.reink_lane(i)
            changed += 1
            # AN END THE SQUARING MOVED CARRIES ITS JOINT WITH IT: another lane that ended at the same point still ends
            # where this one does, so the two stay one way (Mizuguchi: the field path and the lane it continued met at the
            # brook's bank, and squaring the path's crossing left the lane 10 ft short of it)
            for old, new in ((p[0], q[0]), (p[-1], q[-1])):
                if math.dist(old, new) < 1e-6:
                    continue
                for j, other in enumerate(lanes):
                    op = other.get("pts") or []
                    for e in (0, -1):
                        if j != i and len(op) >= 2 and math.dist((float(op[e][0]), float(op[e][1])), old) <= 1.0:
                            op[e] = [round(new[0], 1), round(new[1], 1)]
                            s.reink_lane(j)
    return changed


# ---- step 2: a lane's own shape and its crossings ----------------------------------------------------------------------


Yards = list[tuple[Poly, Pt | None]]


def _fabric(s: Any) -> tuple[Yards, list[Mapping[str, Any]]]:
    yards = [(poly, owner) for poly, owner, kind in _homestead_polys(s) if kind in ("threshing_yards", "gardens")]
    return yards, list(s.M.get("houses") or [])


def theirs(p: Poly, yards: Yards, houses: Sequence[Mapping[str, Any]]) -> list[Poly]:
    """The yards and gardens a lane along `p` may not come near: every household's but those of a house one of its ENDS
    stands at (within `law.DOORSTEP_FT`) - a door path leaves its own dooryard, and is exempt from that steading alone
    (`law.fouls_fabric`'s `own`)."""
    own = [(float(h["x"]), float(h["y"])) for h in houses if min(math.dist(p[0], (float(h["x"]), float(h["y"]))), math.dist(p[-1], (float(h["x"]), float(h["y"])))) <= law.DOORSTEP_FT]
    return [poly for poly, owner in yards if owner is None or all(math.dist(owner, c) > 1.0 for c in own)]


def fouled_segment(p: Poly, width: float, houses: Sequence[Mapping[str, Any]], yards: Yards, solid: Sequence[tuple[float, float, float, float]]) -> int | None:
    """The first segment of `p` that fouls the fabric: ink on a farmhouse (`house_hit`), within `_TOUCH_GAP` of another
    household's yard or garden (`law.fouls_fabric`, `theirs`), or a long leg through a building's box (`law.breaks_mid_run`)."""
    near = theirs(p, yards, houses)
    for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
        if house_hit([a, b], width, houses) or _crosses_fabric([a, b], near, _TOUCH_GAP):
            return k
        if math.dist(a, b) > law.BREAK_SPAN_FT:
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if any(x0 <= mid[0] <= x1 and y0 <= mid[1] <= y1 for x0, y0, x1, y1 in solid):
                return k
    return None


def _crossing_fault(M: Mapping[str, Any], i: int, p: Poly, wet: Sequence[Poly]) -> list[Poly] | None:
    """The pieces lane `i` is cut into for its first crossing fault, or None: a brook crossed twice (the stretch between the
    two crossings goes), a crossing off a ford, off square after the squaring, or where no deck seats (the crossing goes)."""
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
    for k, x in law.undeckable_at(p, width, waters, ftpx, wet):
        # A CROSSING NO DECK SEATS is squared to the water it crosses first - a square deck is the shortest, and the
        # one most likely to land on the bank (the field path over its canal, R3) - and cut only if even that will not seat
        for wpts, ww in waters:
            course = [(float(q[0]), float(q[1])) for q in wpts]
            if len(course) >= 2 and any(math.dist(x, y) < 1.0 for _k, y in law.crossing_points(p, course)):
                sq = square_crossings(p, course, float(ww) / 2 + SQUARE_MARGIN_FT / ftpx)
                if sq != p and not law.undeckable_at(sq, width, waters, ftpx, wet):
                    return [sq]
        return cut_around(p, arc_at(p, k, x), _cut_gap(M, x) + gap)
    return None


def _cut_gap(M: Mapping[str, Any], x: Pt) -> float:
    """Half the width of the widest recorded water within reach of the crossing `x` - where its bank stands."""
    near = [
        float(w) / 2
        for wpts, w in bridge_crossed_waters(M)
        if len(wpts) >= 2 and min(seg_dist(x[0], x[1], (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in zip(wpts, wpts[1:], strict=False)) <= float(w)
    ]
    return max(near, default=3.0)


def _unkinked(p: Poly, span: tuple[str, int, int]) -> list[Poly]:
    """A run that doubles back keeps its longer arm; one that kinks loses the stretch between its two turns."""
    kind, ka, kb = span
    if kind == "doubles back":
        head, tail = p[: ka + 1], p[ka:]
        return [max(head, tail, key=polyline_len)]
    return [q for q in (p[: ka + 1], p[kb:]) if len(q) >= 2]


def settle_shapes(s: Any) -> int:
    """Step 2: cut from every ordinary lane what breaks its own shape or its crossings (ways W07, W09, W11, W12, W18, W19),
    and take a hook off the connector's end. One fault per lane per round; the next round asks again."""
    M = s.M
    lanes = M.get("lanes") or []
    yards, houses = _fabric(s)
    solid = law.solid_boxes(M)
    wet = flooded_ground(M)
    edits: dict[int, list[Poly]] = {}
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 2:
            continue
        ends = law.hooked(p)
        if ends:
            # A HOOK is a lane overshooting the way it joins and bending back onto it: re-laid as a T on that way where it
            # joins one (so the web stays one network), else its hook leg is taken off
            seq = _as_end(p, ends[0])
            j = joined_way(lanes, i, seq[-1])
            edits[i] = [_back(reaimed(seq, _pts(lanes[j]), bool(lanes[j].get("connector"))) if j is not None else seq[:-1], ends[0])]
            continue
        if ln.get("connector"):
            continue
        spans = kink_spans(p)
        if spans:
            edits[i] = _unkinked(p, spans[0])
            continue
        pieces = _crossing_fault(M, i, p, wet)
        if pieces is not None:
            edits[i] = pieces
            continue
        k = fouled_segment(p, float(ln.get("w") or 3.0), houses, yards, solid)
        if k is not None:
            edits[i] = [q for q in (p[: k + 1], p[k + 1 :]) if len(q) >= 2]  # the fouling segment goes; a lane of one goes whole
    return apply_pieces(s, edits)


# ---- step 3: the ways out ----------------------------------------------------------------------------------------------


def settle_way_outs(s: Any) -> int:
    """Step 3 (ways W08): while some household's way out crosses one brook more than once, cut the crossing nearest that
    household out of the ordinary lane that carries it."""
    M = s.M
    routes = departure_routes(M)
    lanes = M.get("lanes") or []
    for brook in law._brooks(M):
        for r in routes:
            xs = [x for _k, x in law.crossing_points(list(r), brook)]
            if len(xs) <= 1:
                continue
            for x in xs:
                for i in _ordinary(M):
                    p = _pts(lanes[i])
                    for k, y in law.crossing_points(p, brook):
                        if math.dist(x, y) <= 12.0:
                            return apply_pieces(s, {i: cut_around(p, arc_at(p, k, y), _cut_gap(M, y) + CROSSING_GAP_FT)})
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


def reaimed(seq: Poly, tread: Poly, connector: bool = False) -> Poly:
    """`seq` (ending on the way `tread`) re-laid to meet it cleanly (`meets_clean`): from the last vertex before its end
    whose leg to its foot on the tread keeps the law, that leg - never longer than what it replaces, since a foot is the
    nearest point; a vertex already standing on the tread simply ends the lane there. With no such vertex the last leg is
    dropped."""
    for m in range(len(seq) - 2, -1, -1):
        b = seq[m]
        f = _foot(b, tread)
        cand = seq[: m + 1] if math.dist(b, f) <= _TOUCH_GAP else [*seq[: m + 1], f]
        if len(cand) >= 2 and cand != seq and meets_clean(cand, tread, connector):
            return cand
    return seq[:-1]


def settle_ends(s: Any) -> int:
    """Step 4: the joints and the ends (ways W05, W10, W16, W20, W21, W22) - each fixed by shortening, never lengthening.

    ONE FIX PER MEETING PER ROUND: a repair names every lane it involves (the lane it edits and the way it meets), and a
    later repair touching any of them waits for the next round. Two repairs made at once on the two sides of one joint -
    Kashikawa's field path re-aimed off a needle while the lane it continued was re-aimed off the fold at the same point -
    each assumed the other side stood still, and the web came apart there."""
    M = s.M
    lanes = M.get("lanes") or []
    edits: dict[int, list[Poly]] = {}
    touched: set[int] = set()

    def claim(involved: set[int], i: int, pieces: list[Poly]) -> None:
        if not involved & touched:
            edits[i] = pieces
            touched.update(involved)

    for ci, i, end in law.connector_hairpin_ends(lanes):
        claim({ci, i}, i, [_back(reaimed(_as_end(_pts(lanes[i]), end), _pts(lanes[ci]), connector=True), end)])
    for i, end, k, _u, _v in law.needle_ends(lanes):
        claim({i, k}, i, [_back(reaimed(_as_end(_pts(lanes[i]), end), _pts(lanes[k]), bool(lanes[k].get("connector"))), end)])
    for i, ei, j, ej in law.folded_joint_pairs(lanes):
        # the SHORTER record of the two that has a vertex to fall back to is re-aimed as a T on the other; two bare legs
        # folded on each other lose the shorter
        x, y = _as_end(_pts(lanes[i]), ei), _as_end(_pts(lanes[j]), ej)
        both = sorted(((polyline_len(q), m, q, e, o) for m, q, e, o in ((i, x, ei, y), (j, y, ej, x))), key=lambda c: c[0])
        bent = [c for c in both if len(c[2]) >= 3]
        if bent:
            _len, m, seq, me, other = bent[0]
            claim({i, j}, m, [_back(reaimed(seq, other), me)])
        else:
            claim({i, j}, both[0][1], [])
    for i in law.doubled_tails(M):
        p = _pts(lanes[i])
        for j, o in enumerate(lanes):
            op = _pts(o)
            if j != i and len(op) >= 2 and (k := along_tail(p, op, deg=_DOUBLED_DEG)) is not None:
                claim({i, j}, i, [cut_at_tail(p, k, op)])
                break
    houses = M.get("houses") or []
    for h, ends in law.fronting_ends(M).items():
        c = (float(houses[h]["x"]), float(houses[h]["y"]))
        for i, end in sorted(ends, key=lambda ie: math.dist(c, _pts(lanes[ie[0]])[ie[1]]))[law.DOORSTEP_MAX :]:
            seq = _as_end(_pts(lanes[i]), end)
            walk = next((polyline_len(seq[: k + 1]) for k in range(len(seq) - 1, -1, -1) if math.dist(seq[k], c) > law.DOORSTEP_FT), 0.0)
            claim({i}, i, [_back(sub_run(seq, 0.0, walk), end)] if walk > 0 else [])
    if edits:
        return apply_pieces(s, edits)
    return settle_dangling(s)


def settle_dangling(s: Any) -> int:
    """Every ordinary lane is trimmed to service (`_trim_to_service`, at the law's own segment set): an end that reaches
    nothing but the way it left (W16), and an end served by a house alone that runs on past it (the road to nowhere, H41 -
    `_trim_to_service` stops it at its closest approach). No exemption for a house the lane alone reaches - that house is
    the corridor's. A lane the law still calls dangling after its trim goes whole."""
    M = s.M
    lanes = M.get("lanes") or []
    ground, steadings = memo_ground(s, "worked", worked_ground), steading_footprints(M)
    bad = {i for i, _e in law.dangling_lane_ends(M, ground)}
    ways = [_pts(ln) for ln in lanes]
    centers = [(float(h["x"]), float(h["y"])) for h in M.get("houses") or []]
    edits: dict[int, list[Poly]] = {}
    for i in _ordinary(M):
        others = [sg for k, o in enumerate(ways) if k != i and len(o) >= 2 for sg in zip(o, o[1:], strict=False)]
        trimmed = _trim_to_service(ways[i], others, centers, ground, (), steadings)
        if len(trimmed) < 2:
            edits[i] = []
        elif trimmed != ways[i] and (i in bad or polyline_len(ways[i]) - polyline_len(trimmed) > TRIM_GRAIN_FT):
            edits[i] = [trimmed]
    return apply_pieces(s, edits) if edits else 0


TRIM_GRAIN_FT = 1.0
"""A trim that takes less than this off a lane whose ends the law already calls served is the record's own rounding, not a
trim, and changes nothing; on a lane the law calls dangling any trim is taken."""


# ---- step 5: every join touches, then one network -----------------------------------------------------------------------


def settle_joins(s: Any) -> int:
    """Every join that stops short (`law.near_misses`: a free end making for a way within its reach, over walkable ground)
    is carried onto that way - it ends ON the tread it joins (homes H37), and a way drawn as two across a hole is one again
    (H38; the span may not run along a tread, H39). The only step that adds tread, and only to close a hole, once per end:
    an end it closes is no longer free. Before the network rule, so a piece the ink tolerance would drop is joined first."""
    edits: dict[int, list[Poly]] = {}
    for i, end, f in law.near_misses(s.M):
        if i in edits:
            continue
        p = _pts(s.M["lanes"][i])
        edits[i] = [[*p, f] if end == -1 else [f, *p]]
    return apply_pieces(s, edits) if edits else 0


def settle_fragments(s: Any) -> int:
    """A fragment that earns nothing (`law.short_fragments`) is dropped (homes H40) - one a round, since two fragments can
    each be redundant only while the other stands."""
    gone = law.short_fragments(s.M)[:1]
    if gone:
        s.drop_lanes(gone)
    return len(gone)


def rewidth(s: Any, i: int, width: float) -> None:
    """Lane `i` drawn at `width`: its record, and its ink re-laid at that width (the old ink blanked) where the settlement
    keeps ink - a stand-in with no ink has only the record."""
    ln = s.M["lanes"][i]
    ln["w"] = width
    ink = getattr(s, "_lane_ink", None)
    if ink is None:
        return
    for z in ink[i]:
        for part in ("edge", "bed", "top"):
            if s.ground[z].get(part):
                s.ground[z][part] = ""
    ink[i] = s._lane_ink_at(ln["pts"], width, bool(ln.get("worn")), ln)


def settle_widths(s: Any) -> int:
    """One way keeps one width (homes H42): every chain of lanes meeting end to end (`joints`) is drawn at its widest
    member's width - the rank of the way - unless a member drawn that wide would foul the fabric (`fouled_segment`), in
    which case at its narrowest. Either way no joint steps (`law.width_steps`) and no tread is widened onto a steading."""
    lanes = s.M.get("lanes") or []
    steps = law.width_steps(lanes)
    if not steps:
        return 0
    par = list(range(len(lanes)))

    def find(k: int) -> int:
        while par[k] != k:
            k = par[k]
        return k

    for i, _ei, j, _ej in joints(lanes):
        par[find(i)] = find(j)
    yards, houses = _fabric(s)
    solid = law.solid_boxes(s.M)
    changed = 0
    for root in {find(i) for i, _j in steps}:
        chain = [k for k in range(len(lanes)) if find(k) == root]
        widths = [float(lanes[k].get("w") or 3.0) for k in chain]
        wide = max(widths)
        target = wide if all(fouled_segment(_pts(lanes[k]), wide, houses, yards, solid) is None for k in chain) else min(widths)
        for k in chain:
            if float(lanes[k].get("w") or 3.0) != target:
                rewidth(s, k, target)
                changed += 1
    return changed


def settle_network(s: Any) -> int:
    """Step 5 (ways W17): drop every lane not in the connector's network at the ink tolerance (`law.JOIN_TOL`)."""
    lanes = s.M.get("lanes") or []
    live = [i for i, ln in enumerate(lanes) if len(ln.get("pts") or []) >= 2]
    labels = _components([_pts(lanes[i]) for i in live], law.JOIN_TOL)
    if len(set(labels)) <= 1:
        return 0
    roots = {labels[n] for n, i in enumerate(live) if lanes[i].get("connector")}
    if not roots:
        roots = {max(set(labels), key=lambda lb: sum(polyline_len(_pts(lanes[live[n]])) for n, x in enumerate(labels) if x == lb))}
    gone = [i for n, i in enumerate(live) if labels[n] not in roots]
    s.drop_lanes(gone)
    return len(gone)


def settle_husks(s: Any) -> int:
    """Drop every lane record that draws nothing (ways W04)."""
    gone = law.husks(s.M)
    if gone:
        s.drop_lanes(gone)
    return len(gone)


# ---- the loop ----------------------------------------------------------------------------------------------------------


def lane_violators(s: Any) -> list[int]:
    """Every ordinary lane some per-lane rule of the law still names - what the last resort drops."""
    M = s.M
    lanes = M.get("lanes") or []
    yards, houses = _fabric(s)
    solid = law.solid_boxes(M)
    wet = flooded_ground(M)
    bad: set[int] = set()
    for i in _ordinary(M):
        p = _pts(lanes[i])
        if law.hooked(p) or kink_spans(p) or _crossing_fault(M, i, p, wet) is not None or fouled_segment(p, float(lanes[i].get("w") or 3.0), houses, yards, solid) is not None:
            bad.add(i)
    bad |= {i for _c, i, _e in law.connector_hairpin_ends(lanes)}
    bad |= {i for i, _e, _k, _u, _v in law.needle_ends(lanes)}
    bad |= {i for i, _ei, _j, _ej in law.folded_joint_pairs(lanes)}
    bad |= set(law.doubled_tails(M))
    bad |= {i for i, _e in law.dangling_lane_ends(M, memo_ground(s, "worked", worked_ground))}
    bad |= {i for ends in law.fronting_ends(M).values() if len(ends) > law.DOORSTEP_MAX for i, _e in ends}
    if law.way_outs_crossing(M):
        bad |= {i for brook in law._brooks(M) for i in _ordinary(M) if law.crossing_points(_pts(lanes[i]), brook)}
    return sorted(i for i in bad if not lanes[i].get("connector"))


STEPS = (settle_husks, square_every_crossing, settle_shapes, settle_way_outs, settle_ends, settle_joins, settle_network, settle_fragments, settle_widths, settle_husks)


def settle_the_web(s: Any, rounds: int = SETTLE_ROUNDS) -> dict[str, Any]:
    """Repair the web until every rule of the lane law holds (see the module docstring) and report what it took: `rounds`,
    `seconds`, `changed` (lane edits), `dropped` (lanes the last resort dropped whole), and `unreached_before` / `_after`
    (`unreached_houses`, the houses the corridor is owed)."""
    t0 = time.perf_counter()
    before = len(unreached_houses(s.M))
    changed = dropped = done = 0
    settled = False
    while done < rounds and not settled:
        done += 1
        n = sum(step(s) for step in STEPS)
        changed += n
        settled = not n
    if not settled:
        # THE LAST RESORT (FR-005): the rounds ran out with a lane still breaking a rule, so every such lane goes whole -
        # never kept as the least bad - and the network and husk rules are asked again of what is left. Each pass drops at
        # least one lane, so this ends.
        while bad := lane_violators(s):
            s.drop_lanes(bad)
            dropped += len(bad)
            settle_network(s)
            settle_husks(s)
        # ...and the rules no drop can break are asked once more of what is left: a join closed only where it meets
        # cleanly, the network, a fragment that no longer earns, one width a way
        for step in (settle_joins, settle_network, settle_fragments, settle_widths, settle_husks):
            step(s)
    return {"rounds": done, "seconds": round(time.perf_counter() - t0, 3), "changed": changed, "dropped": dropped, "unreached_before": before, "unreached_after": len(unreached_houses(s.M))}


def settle_and_redraw(s: Any, redraw: Callable[[], None]) -> dict[str, Any]:
    """`settle_the_web`, and - where its cuts left a farmhouse newly unreached or the field without its way - `redraw` (the
    straggler paths and the field path, drawn again) and settle once more: the interim reach repair until the access corridor
    reserved at seating serves them (M3). The report sums the two settles and says `redrawn`."""
    field_before = law.field_unreached(s.M)
    settled = settle_the_web(s)
    if settled["unreached_after"] > settled["unreached_before"] or (law.field_unreached(s.M) and not field_before):
        redraw()
        again = settle_the_web(s)
        first = settled
        settled = {key: (first[key] + again[key] if key in ("rounds", "seconds", "changed", "dropped") else again[key]) for key in again}
        settled |= {"unreached_before": first["unreached_before"], "redrawn": True}
    return {key: (round(v, 3) if isinstance(v, float) else v) for key, v in settled.items()}
