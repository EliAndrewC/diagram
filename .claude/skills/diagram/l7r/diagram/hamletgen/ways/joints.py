"""Where two lanes meet END TO END, read them as one way (GM 2026-09-26).

The web is recorded as pieces, and every shape repair before this one - the string-pull, the hairpin cut, the
un-jog - reads ONE record at a time. Where one record ends exactly where the next begins and nothing else
touches the point, the walker sees one lane and the repairs see two, so a fold or a jog AT the joint survived
every pass and every check (`lanes_bend_like_paths` read records too). Inashiro showed both, and the GM:
*"people tend to walk in straight lines. Or, more generally, they walk in reasonably efficient paths. So they
may walk in a curved line, but they are not going to walk in one direction and then turn at a 30-degree angle
to keep walking."*

- Beside the bamboo stand, lane 8 came down the gap between a garden and the stand, turned back west for
  35 ft to where lane 7 began, and lane 7 ran straight back east: one walk, doubled back on itself at a joint.
  A HAIRPIN AT A JOINT becomes a T - the arriving lane drops its last leg and meets the other lane's side at
  the foot of the vertex before it, so the other lane keeps the ground it served.
- On the northeast lane, three records (1, 5, 2) were one line with a 3 ft sideways step in the 20 ft middle
  record. ANY OTHER JOINT is merged into one record and string-pulled across, under the smoothing pass's own
  chord rule (`_clear_link`, or `_clear_touch` at the lane's own keep-out when every vertex the chord replaces
  lies within `_JOG_FT` of it).
- A HOOK AT A LANE'S END - a last leg of `_HOOK_FT` or less turning back `_HOOK_DEG` or more - is taken off: the lane
  ends at the vertex before it, or where the leg before first reaches the way the hook was bending back onto.

It runs after the web's sweeps, and once more after `settle_the_web` (feature 308): the settle squares a crossing after
the first run and can lay a Z across a joint, which the second mends - a Z becomes a T like a fold, or, where no T fits,
the joint moves back one vertex (`_joint_moved_back`). No rewrite may break what the passes before it settled: a rewrite is kept only when every other lane end that touched the old line still touches the new one,
and every farmhouse a way served still has one within `_SERVE_FT` (`keeps_the_web`) - and `commit_lane` still
refuses anything that splits the web.

Research: plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import WEB_CLEARANCE, Poly, Pt
from .clearance import _HAIRPIN_DEG, _bends_badly, _clear_link, _clear_touch, kink_spans
from .geom import _HOOK_DEG, _HOOK_FT, _TOUCH_GAP, _seg_cross, _turn_deg
from .smooth import _JOG_FT, admits_lane, commit_lane, web_pieces
from .sweeps import _SERVE_FT

_JOINT_FT = 1.0  # two lane ends this close are one point: the knot pass and the touch passes put them on the same vertex
# A HOOK: a lane's last leg this short that turns back this far (GM 2026-09-26, "they are not going to walk in one
# direction and then turn at a 30-degree angle"). Measured on the pool before this pass: three end legs of 9-11 ft
# turning 122-128 degrees (Kashikawa twice, Kuwabata once) - each a lane overshooting the way it joins and bending
# back onto it, or a nub past a junction. Both figures are drawing thresholds, not findings: 12 ft is about four
# paces, too short a leg to be a route of its own, and 90 degrees is where the turn stops reading as a bend.
# (the two figures live in `geom`, a layer below, since feature 291: the door paths in `serve` take their hook off too)


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in ln.get("pts") or []]


def _segs(p: Poly) -> list[tuple[Pt, Pt]]:
    return list(zip(p, p[1:], strict=False))


def joints(lanes: Sequence[Mapping[str, Any]]) -> list[tuple[int, int, int, int]]:
    """Every point where exactly two lane ENDS meet and no other way touches: `(i, end_i, j, end_j)`, an end
    being 0 or -1. A connector's end counts as a way touching (the cart route is not merged into a footpath), and
    two lanes that meet at both ends are a loop, not a joint."""
    live = [m for m, ln in enumerate(lanes) if not (ln.get("connector") or ln.get("street")) and len(ln.get("pts") or []) >= 2]
    ends = [(m, e, _pts(lanes[m])[e]) for m in live for e in (0, -1)]
    out: list[tuple[int, int, int, int]] = []
    for a, (i, ei, q) in enumerate(ends):
        for j, ej, r in ends[a + 1 :]:
            if j == i or math.dist(q, r) > _JOINT_FT:
                continue
            if math.dist(_pts(lanes[i])[-1 - ei], _pts(lanes[j])[-1 - ej]) <= _JOINT_FT:
                continue  # a loop
            third = any(k not in (i, j) and len(ln.get("pts") or []) >= 2 and any(seg_dist(q[0], q[1], u, v) <= _TOUCH_GAP for u, v in _segs(_pts(ln))) for k, ln in enumerate(lanes))
            if not third:
                out.append((i, ei, j, ej))
    return out


def as_walked(lanes: Sequence[Mapping[str, Any]]) -> tuple[list[Poly], list[int]]:
    """The ways a walker reads: every chain of lanes met end to end at a `joints` joint joined into one polyline (two records
    meeting end to end are one way, the module's rule), and each lane's index into them. A lane of under two points is a way
    of its own, as it stands.

    Research: lanes met end to end are one - research/questions/0081-village-lanes.drawing.html: read as one way"""
    n = len(lanes)
    link: dict[tuple[int, int], tuple[int, int]] = {}
    for i, ei, j, ej in joints(lanes):
        link[(i, ei)], link[(j, ej)] = (j, ej), (i, ei)
    owner = [-1] * n
    ways: list[Poly] = []
    for start in range(n):
        if owner[start] >= 0:
            continue
        # ...walk back to the chain's first lane (one end free of a joint), or round once where the chain is a loop
        cur, free_end = start, 0
        seen = {start}
        while (cur, free_end) in link and link[(cur, free_end)][0] not in seen:
            nxt, at = link[(cur, free_end)]
            cur, free_end = nxt, -1 - at
            seen.add(cur)
        way: Poly = []
        k = len(ways)
        while True:
            owner[cur] = k
            p = _pts(lanes[cur]) if len(lanes[cur].get("pts") or []) >= 2 else [tuple(q) for q in lanes[cur].get("pts") or []]
            p = p if free_end == 0 else p[::-1]
            way = [*way, *p[1:]] if way else list(p)
            nxt = link.get((cur, -1 - free_end))
            if nxt is None or owner[nxt[0]] >= 0:
                break
            cur, free_end = nxt[0], nxt[1]
        ways.append(way)
    return ways, owner


def oriented(lanes: Sequence[Mapping[str, Any]], i: int, ei: int, j: int, ej: int) -> tuple[Poly, Poly]:
    """The two lanes of a joint as one walk: `x` ENDS at the joint and `y` STARTS there."""
    x, y = _pts(lanes[i]), _pts(lanes[j])
    return (x[::-1] if ei == 0 else x), (y[::-1] if ej == -1 else y)


def tee(x: Poly, y: Poly, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> Poly | None:
    """`x` (ending at the joint) re-laid to meet `y`'s first leg as a T, from the vertex before its end: that
    vertex's foot on the leg, when the link is clear at footprint margins and the new last turn is no hairpin.
    `None` when there is nothing to gain (the foot IS the joint) or the link is not walkable.

    Research: a fold at a joint becomes a T - research/questions/0081-village-lanes.drawing.html: met at the other's side"""
    p, n = x[-2], x[-1]
    f = seg_closest(p[0], p[1], n, y[1])
    if math.dist(f, n) <= _JOINT_FT:
        return None
    if math.dist(p, f) <= _TOUCH_GAP:
        # the vertex before the joint already stands on `y`'s tread: the lane simply stops there, rather than
        # ending in a 1-2 ft nub to the foot (Kuwabata and Sawada, the first run of this pass)
        return x[:-1] if len(x) >= 3 else None
    if not _clear_touch(p, f, hard, walls, water):
        return None
    new = [*x[:-1], f]
    if len(new) >= 3 and _turn_deg(new[-3], new[-2], new[-1]) >= _HAIRPIN_DEG:
        return None
    return new


def pulled(pts: Poly, ok: Callable[[int, int], bool]) -> Poly:
    """The string-pull: from each vertex, jump to the furthest later vertex `ok` allows (`_smooth_web`'s own)."""
    out = [pts[0]]
    a = 0
    while a < len(pts) - 1:
        b = len(pts) - 1
        while b > a + 1 and not ok(a, b):
            b -= 1
        out.append(pts[b])
        a = b
    return out


def keeps_the_web(lanes: Sequence[Mapping[str, Any]], mine: set[int], old: Poly, new: Poly, houses: Sequence[Pt]) -> bool:
    """Does replacing lanes `mine` (whose tread is `old`) with the one tread `new` leave the web as it was? Every
    other lane end that touched `old` must still touch a way - `new`, or another lane (Kashikawa: a hook that three
    lanes met at, where the third still meets the second after the hook goes) - the web must stay in as many
    pieces as it was, and every farmhouse some way served must still be served.

    Research:
        one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no rewrite splits the web
        every farmhouse served - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft, how close counts as serving"""
    others = [_pts(ln) for k, ln in enumerate(lanes) if k not in mine and len(ln.get("pts") or []) >= 2]
    for n, p in enumerate(others):
        rest_segs = [sg for m, o in enumerate(others) if m != n for sg in _segs(o)]
        for e in (p[0], p[-1]):
            if any(seg_dist(e[0], e[1], u, v) <= _TOUCH_GAP for u, v in _segs(old)) and not any(seg_dist(e[0], e[1], u, v) <= _TOUCH_GAP for u, v in _segs(new) + rest_segs):
                return False
    if web_pieces([{"pts": q} for q in [*others, new]]) > web_pieces([{"pts": q} for q in [*others, old]]):
        return False
    rest = [sg for p in others for sg in _segs(p)]

    def served(tread: Poly) -> set[Pt]:
        segs = rest + _segs(tread)
        return {h for h in houses if min((seg_dist(h[0], h[1], u, v) for u, v in segs), default=math.inf) <= _SERVE_FT}

    return served(old) <= served(new)


def unhooked(pts: Poly, others: Sequence[Poly]) -> Poly | None:
    """`pts` (its hook at the END - reverse it for the start) without the hook: ended at the vertex before, when that
    still touches every way the old end touched; else cut where the leg before the hook first reaches such a way.
    `None` when there is no hook or neither cut keeps the end on its ways.

    Research: a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: 12 ft, 90 degrees"""
    if len(pts) < 3 or math.dist(pts[-2], pts[-1]) > _HOOK_FT or _turn_deg(pts[-3], pts[-2], pts[-1]) < _HOOK_DEG:
        return None
    end = pts[-1]
    met = [o for o in others if any(seg_dist(end[0], end[1], u, v) <= _TOUCH_GAP for u, v in _segs(o))]
    if not met or any(any(seg_dist(pts[-2][0], pts[-2][1], u, v) <= _TOUCH_GAP for u, v in _segs(o)) for o in met):
        return pts[:-1]  # a nub reaching nothing, or the vertex before already stands on a way the hook met
    if len(met) != 1:
        return None
    a, b = pts[-3], pts[-2]
    # a long leg overshooting by a few feet crosses within the last 2% of it (Kashikawa: 7.6 ft past, on a 720 ft
    # leg), so the crossing need only lie 0.1 ft inside the leg
    near = min(0.02, 0.1 / max(math.dist(a, b), 1e-9))
    hits = [x for u, v in _segs(met[0]) if (x := _seg_cross(a, b, u, v, near)) is not None]
    if not hits:
        return None
    return [*pts[:-2], min(hits, key=lambda x: math.dist(a, x))]


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(a, 1), round(b, 1)] for a, b in p]


def straighten_joints(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """The pass (see the module docstring). Returns the number of joints rewritten.

    Research:
        lanes met end to end are one - research/questions/0081-village-lanes.drawing.html: a fold a T, a jog pulled straight
        a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html"""
    # A FIX THAT FAILED (feature 280, Kashikawa's skeleton lanes 8 and 10, bends 140 and 232 ft out in the grazing): pulling a
    # stray bend in along the line to its neighbors' midpoint. Measured on both lanes, every step of ten was refused - the
    # chord side crosses the farmhouse and its yard, so the clear bend is round the yard's far corner, not on that line. The
    # fix is a re-route (future-work/farming-communities.md, "Found by feature 280's settlement-reviews").
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]
    changed = 0
    for _round in range(len(lanes) + 1):  # each rewrite removes a joint or a vertex, so this is a bound, not a budget
        if not (_one_hook(s, lanes, houses, hard, walls, water) or _one_joint(s, lanes, houses, hard, walls, water)):
            break
        changed += 1
    return changed


def _one_hook(s: Settlement, lanes: list[dict[str, Any]], houses: Sequence[Pt], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> bool:
    """Take the hook off the first lane end that has one and can lose it; False when none can. The connector is
    read at its START only - the end on the web; its other end runs off the map (Kashikawa, feature 280: the
    connector overshot a 3 ft lane by 7.6 ft and hooked back onto it, and no pass read a connector's hook).

    Research: a lane's end loses its hook - research/questions/0081-village-lanes.drawing.html: the connector's web end too"""
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 3:
            continue
        others = [_pts(o) for k, o in enumerate(lanes) if k != i and len(o.get("pts") or []) >= 2]
        for q, back in ((p[::-1], True),) if ln.get("connector") else ((p, False), (p[::-1], True)):
            new = unhooked(q, others)
            if new is None:
                continue
            new = new[::-1] if back else new
            if keeps_the_web(lanes, {i}, p, new, houses) and commit_lane(lanes, i, _rounded(new), hard, walls, water, s.reink_lane, admits_lane(s)):
                return True
    return False


def _one_joint(s: Settlement, lanes: list[dict[str, Any]], houses: Sequence[Pt], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> bool:
    """Rewrite the first joint that can be improved; False when none can.

    Research:
        a fold or Z at a joint becomes a T - research/questions/0081-village-lanes.drawing.html: the shorter link the stem
        a jog across a joint pulled straight - research/questions/0081-village-lanes.drawing.html: string-pulled, a vertex
            within 6 ft of the chord dropped
        ways of two kinds stay two - UNRESEARCHED: a cart route and a footpath, or a web and a non-web lane, met end to end
            are never straightened as one"""
    for i, ei, j, ej in joints(lanes):
        x, y = oriented(lanes, i, ei, j, ej)
        old = [*x, *y[1:]]
        # a fold at the joint - or a Z across it, two clean records one zigzag to the walker (feature 308: the settle squares a
        # crossing after the pass above ran, `test_no_zigzag_straddles_a_joint`) - becomes a T
        if _turn_deg(x[-2], x[-1], y[1]) >= _HAIRPIN_DEG or (not _bends_badly(x) and not _bends_badly(y) and _bends_badly(old)):
            # the arriving lane that makes the SHORTER clear link becomes the T's stem
            tees = [(m, t) for m, t in ((i, tee(x, y, hard, walls, water)), (j, tee(y[::-1], x[::-1], hard, walls, water))) if t is not None]
            for m, t in sorted(tees, key=lambda mt: math.dist(mt[1][-2], mt[1][-1])):
                other = y if m == i else x[::-1]
                if keeps_the_web(lanes, {i, j}, old, [*t, *other], houses) and commit_lane(lanes, m, _rounded(t), hard, walls, water, s.reink_lane, admits_lane(s)):
                    return True
            if _turn_deg(x[-2], x[-1], y[1]) < _HAIRPIN_DEG and _joint_moved_back(s, lanes, (i, ei, j, ej), x, y, houses, hard, walls, water):
                return True
            continue
        if lanes[i].get("w") != lanes[j].get("w") or bool(lanes[i].get("web")) != bool(lanes[j].get("web")):
            continue  # a cart route and a footpath meeting end to end are two ways
        gap = max(_TOUCH_GAP, float(lanes[i].get("w") or 5.0) / 2.0 + 2.0)

        def ok(a: int, b: int, p: Poly = old, g: float = gap) -> bool:
            if _clear_link(p[a], p[b], hard, walls, water):
                return True
            return _clear_touch(p[a], p[b], hard, walls, water, g) and all(seg_dist(v[0], v[1], p[a], p[b]) <= _JOG_FT for v in p[a + 1 : b])

        new = pulled(old, ok)
        # ...NEVER INTO A KINK THE TWO DID NOT HAVE (feature 317): two access lanes met end to end at a door (one corridor hung
        # from another's start, the route round its own beds), the pull took out a vertex of a bend and left a kink at the next,
        # and a tree lane no settle may cut was refused with it (seed 47 at 20 households, `WebRefused`: bends) - the test a
        # join that stops short is held to (`law.near_misses`)
        if len(new) == len(old) or len(kink_spans(new)) > len(kink_spans(old)) or not keeps_the_web(lanes, {i, j}, old, new, houses):
            continue
        if commit_lane(lanes, i, _rounded(new), hard, walls, water, s.reink_lane, admits_lane(s)):
            commit_lane(lanes, j, [], hard, walls, water, s.reink_lane)
            return True
    return False


def moved_back(x: Poly, y: Poly) -> list[tuple[Poly, Poly]]:
    """The joint of `x` (ending there) and `y` (starting there) moved one vertex back along either: `x` shortened by its last
    vertex and `y` started from its new end, or `y` shortened by its first and `x` carried on to its new start - the walk
    without the joint's own vertex. Only a lane of three points or more gives one up."""
    out: list[tuple[Poly, Poly]] = []
    if len(x) >= 3:
        out.append((x[:-1], [x[-2], *y[1:]]))
    if len(y) >= 3:
        out.append(([*x[:-1], y[1]], y[1:]))
    return out


def _joint_moved_back(
    s: Settlement, lanes: list[dict[str, Any]], joint: tuple[int, int, int, int], x: Poly, y: Poly, houses: Sequence[Pt], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]
) -> bool:
    """A Z across a joint no T mends (feature 308, Inashiro: the settle squared a crossing 10 ft from the field spur's end and
    the link joined there turned back across it) mended by moving the joint one vertex back (`moved_back`), where the new
    leg is clear, the walk then bends like a path and the web keeps every house it served. Both records are rewritten;
    the first is put back if the second is refused.

    Research: no zigzag at a joint - research/questions/0081-village-lanes.drawing.html: the joint moved back a vertex"""
    i, ei, j, ej = joint
    old = [*x, *y[1:]]
    for nx, ny in moved_back(x, y):
        if not _clear_link(nx[-1], ny[1], hard, walls, water) or _bends_badly([*nx, *ny[1:]]):
            continue
        if not keeps_the_web(lanes, {i, j}, old, [*nx, *ny[1:]], houses):
            continue
        was = [list(q) for q in lanes[i]["pts"]]
        if not commit_lane(lanes, i, _rounded(nx[::-1] if ei == 0 else nx), hard, walls, water, s.reink_lane, admits_lane(s)):
            continue
        if commit_lane(lanes, j, _rounded(ny[::-1] if ej == -1 else ny), hard, walls, water, s.reink_lane, admits_lane(s)):
            return True
        commit_lane(lanes, i, was, hard, walls, water, s.reink_lane)
    return False


_ON_LINE_FT = 0.1
"""An end this near where it should stand is already there - the rounding of a record, not a step to mend."""


def centered_end(q: Pt, back: Pt, width: float, others: Sequence[tuple[Pt, Pt, float]]) -> Pt | None:
    """Where a lane end that stops ON another lane's tread should stand, slid along its own last leg from `back`.

    THE BUMP AT A T (GM 2026-09-27). Once the treads composited as one surface (`group_shared_opacity`), what
    still showed at a junction was the arriving lane's round cap: its end stood 0.5-3 ft off the other lane's
    centerline, so half a cap poked out past the far side of a 3 ft tread. An end within `_TOUCH_GAP` of another
    way is a junction (the figure `_components` joins a web by), and it is moved so its cap's far point lies on
    the other lane's far edge: `(width - other) / 2` short of the centerline, on its own side. For two lanes of one
    width that IS the centerline; for the 6 ft track arriving on a 3 ft lane it is 1.5 ft short, so the track's
    round end touches the lane's far edge instead of bulging past it and the edge runs straight through - the
    track widens into the junction. The end slides along its own last leg, never sideways, so no kink is made at
    the tip. Returns None when the end is not at a junction, is already where it should be, or its leg runs along
    the other lane (no slide along it changes the distance), or where the two meet end to end rather than at a T.

    Research: the cap at a T - CONVENTION: the arriving tread's round end on the other's far edge"""
    best: tuple[float, Pt, Pt, float] | None = None
    for a, b, w in others:
        d = seg_dist(q[0], q[1], a, b)
        if d <= _TOUCH_GAP and (best is None or d < best[0]):
            best = (d, a, b, w)
    if best is None:
        return None
    _d, a, b, other = best
    ln = math.dist(a, b)
    if ln <= 0.0:
        return None

    def side(p: Pt) -> float:  # signed distance from the other lane's centerline
        return ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) / ln

    sb, sq = side(back), side(q)
    if abs(sq - sb) < 1e-9 or sb == 0.0:
        return None
    want = math.copysign(max(0.0, (width - other) / 2.0), sb)
    t = (want - sb) / (sq - sb)
    to = (back[0] + (q[0] - back[0]) * t, back[1] + (q[1] - back[1]) * t)
    if t <= 0.0 or math.dist(to, q) <= _ON_LINE_FT:
        return None
    # ONLY AT A T: the new end must stand beside the other lane's SIDE. Where the two meet end to end (Kashikawa's
    # track arriving on a footpath's tip) sliding back pulls the end off that tip and splits the web.
    if seg_dist(to[0], to[1], a, b) > abs(want) + _ON_LINE_FT:
        return None
    return to


def center_lane_ends(s: Settlement) -> int:
    """Every lane end that stops on another lane's tread is set where `centered_end` says, record and ink together.
    Runs after the first `straighten_joints`; the trims, the bund run-on, the settle and the second joint pass can still
    move an end, and are not re-centered. Returns the number of ends moved.

    Research: the cap at a T - CONVENTION"""
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    moved = 0
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if len(p) < 2:
            continue
        others = [(a, b, float(o.get("w", 3))) for j, o in enumerate(lanes) if j != i for a, b in _segs(_pts(o))]
        for k, back in ((0, 1), (-1, -2)):
            to = centered_end(p[k], p[back], float(ln.get("w", 3)), others)
            if to is not None:
                p[k] = to
                moved += 1
        if p != _pts(ln) and s.reshape_lane(ln, p):  # asked of the overlap matrix (feature 287 M8)
            s.reink_lane(i)
    return moved


# TWO ENDS THIS NEAR ARE ONE WAY WITH A HOLE IN IT: the lane page's own figure, "ends within 25 ft of one another are
# joined at a single point" (feature 328; it was 11.5 ft, a steading's keep-out plus two half-treads, on no page) - and
# wider than `_TOUCH_GAP`, where `center_lane_ends` already sets an end on the tread it stops on.
_MEET_FT = 25.0
"""Research: ends that nearly meet - research/questions/0081-village-lanes.drawing.html: within 25 ft, joined at a single point"""


def meet_end_to_end(s: Settlement, fabric: Sequence[Poly] = ()) -> int:
    """Close the last hole between two lane ENDS that stop within `_MEET_FT` of each other and on nothing else: the free
    end is moved onto the other's end point, when the moved lane may be written (`may_write` - no nearer the fabric, no
    worse bent). The connector's end is a target, never moved: its off-map run is its own job.

    FOUND ON KASHIKAWA (269 E3): a straggler path and the skeleton arm stopped 9.6 ft apart end to end; the touch pass's
    end-meets-end branch was refused its move and skipped the end, and the connector the later passes laid there stood
    6.9 ft off it - one way in the picture, two networks at the 4 ft ink tolerance (`lanes_form_one_network`).

    Research: ends that nearly meet are joined - research/questions/0081-village-lanes.drawing.html: ends within 25 ft (`_MEET_FT`), the free end moved onto the other's"""
    from .clearance import may_write

    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    closed = 0
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if (ln.get("connector") or ln.get("street")) or len(p) < 2:
            continue
        for k in (0, -1):
            q = p[k]
            others = [(j, _pts(o)) for j, o in enumerate(lanes) if j != i and len(o.get("pts") or []) >= 2]
            if any(seg_dist(q[0], q[1], a, b) <= _TOUCH_GAP for _j, op in others for a, b in _segs(op)):
                continue  # already on a way
            near = [(math.dist(q, op[e]), op[e]) for _j, op in others for e in (0, -1) if _TOUCH_GAP < math.dist(q, op[e]) <= _MEET_FT]
            if not near:
                continue
            _d, to = min(near)
            new = list(p)
            new[k] = to
            if may_write(p, new, float(ln.get("w") or 3.0), fabric) and s.reshape_lane(ln, new):  # ...and the matrix (M8)
                p = new
                s.reink_lane(i)
                closed += 1
    return closed


def split_at_crossings(s: Settlement) -> int:
    """Cut a lane where it crosses another mid-run, so the junction a walker uses is one the records hold: the lane becomes
    two records, each ending on the crossing, which stands on the other lane's tread. Where either lane already ends within
    `_TOUCH_GAP` of the crossing it is a junction already and nothing is cut; the connector is never cut, and a lane that
    crosses it is. Returns the cuts made.

    FOUND AT THE 269 LANDING (Inashiro, the house bearings re-laid): a skeleton arm crossed a web lane 5 ft past its own
    bend, and the only record of the junction was a 2.4 ft "touch" nub - shorter than the gap every end test allows, so the
    tidy pass dropped it as serving nothing and the map shipped as two networks (`lanes_form_one_network`), while kept it
    failed `test_no_lane_end_is_served_only_by_the_way_it_left`. A crossing is a junction; now it is recorded as one."""
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    cuts = 0
    i = 0
    while i < len(lanes):
        ln = lanes[i]
        p = _pts(ln)
        cut: tuple[int, Pt] | None = None
        if not (ln.get("connector") or ln.get("street")) and len(p) >= 2:
            for j, other in enumerate(lanes):
                op = _pts(other)
                if j == i or len(op) < 2:
                    continue
                for k, (a, b) in enumerate(_segs(p)):
                    x = next((c for c in (_seg_cross(a, b, c0, d0) for c0, d0 in _segs(op)) if c is not None), None)
                    if x is None or min(math.dist(x, e) for e in (p[0], p[-1], op[0], op[-1])) <= _TOUCH_GAP:
                        continue
                    cut = (k, x)
                    break
                if cut is not None:
                    break
        if cut is None:
            i += 1
            continue
        k, x = cut
        head, tail = [*p[: k + 1], x], [x, *p[k + 1 :]]
        ln["pts"] = _rounded(head)  # a cut: the lane on less of the ground it was admitted on (its `Kept` record asks all the same)
        s.reink_lane(i)
        s.lane(tail, width=float(ln.get("w") or 3.0), clearance=WEB_CLEARANCE, worn=bool(ln.get("worn", True)))
        lanes[-1].update({key: ln[key] for key in ("role", "web") if key in ln})
        cuts += 1  # lane i is asked again: its head may cross a second lane
    return cuts


_SHORT_LEG_FT = 40.0  # a last leg this short, with the joint beyond it, is a returning leg (0081; 25 ft until feature 328)
"""Research: two turns read as one - research/questions/0081-village-lanes.drawing.html: a returning leg under 40 ft is cut"""


def hairpin_over_a_short_leg(a: Pt, b: Pt, j: Pt, c: Pt) -> bool:
    """Do a lane's last two points `a` -> `b`, its short last leg `b` -> `j` and the other way's first leg `j` -> `c`
    double back - more than `_HAIRPIN_DEG` of turn in total, the leg under `_SHORT_LEG_FT`? Each turn alone can stay under
    the limit, which is how the joint pass missed one (the 269 landing's round-2 review of Kuwabata: 79 + 90 degrees
    across a 15 ft leg, a lane and the connector running back side by side 15-40 ft apart).

    Research: no hairpin - research/questions/0081-village-lanes.drawing.html: a turn past 140 degrees, summed over a returning leg under 40 ft"""
    if math.dist(b, j) > _SHORT_LEG_FT:
        return False

    def signed(p: Pt, q: Pt, r: Pt) -> float:
        h1, h2 = math.atan2(q[1] - p[1], q[0] - p[0]), math.atan2(r[1] - q[1], r[0] - q[0])
        return math.degrees((h2 - h1 + math.pi) % (2 * math.pi) - math.pi)

    return abs(signed(a, b, j) + signed(b, j, c)) > _HAIRPIN_DEG


def fold_the_connector_hairpin(s: Settlement, fabric: Sequence[Poly] = ()) -> int:
    """Where a lane's short last leg meets the CONNECTOR's start and the two double back (`hairpin_over_a_short_leg`), the
    connector is started at the lane's vertex before that leg instead - a T - and the leg dropped, record and ink
    together, when the moved connector may be written (`may_write`). Returns the folds made.

    Research: a hairpin at the track becomes a T - research/questions/0081-village-lanes.drawing.html"""
    from .clearance import may_write
    from .law import breaks_through, solid_boxes  # the law sits above this layer (it reads `hairpin_over_a_short_leg`)

    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    # ...NOT WHERE THE CONNECTOR STARTS AT THE WAY OUT'S GATE (feature 320; the exit strip's rule before it): the households'
    # ways reach it there, and moved off it they stood off the network; the settle re-aims the lane's end instead
    conn = [] if s.M.get("way_out_gate") else [(k, o) for k, o in enumerate(lanes) if o.get("connector") and len(o.get("pts") or []) >= 2]
    folds = 0
    for ci, co in conn:
        cp = _pts(co)
        for i, ln in enumerate(lanes):
            p = _pts(ln)
            if i == ci or (ln.get("connector") or ln.get("street")) or len(p) < 3:
                continue
            for seq, back in ((p, False), (p[::-1], True)):
                a, b, j = seq[-3], seq[-2], seq[-1]
                if math.dist(j, cp[0]) > 1.5 or not hairpin_over_a_short_leg(a, b, j, cp[1]):
                    continue
                new_c = [b, *cp[1:]]
                if not may_write(cp, new_c, float(co.get("w") or 5.0), fabric) or breaks_through(new_c, solid_boxes(s.M)):
                    continue  # ...nor a connector started so that its new first leg runs through a building (the lane law's reading)
                kept = seq[:-1]
                if not (admits_lane(s)(ln, kept) and admits_lane(s)(co, new_c)):
                    continue  # ...nor where the overlap matrix refuses either as it would become (feature 287 M8)
                ln["pts"] = _rounded(kept[::-1] if back else kept)
                co["pts"] = _rounded(new_c)
                s.reink_lane(i)
                s.reink_lane(ci)
                folds += 1
                cp = new_c
                break
    return folds
