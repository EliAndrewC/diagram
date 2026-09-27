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

It runs LAST in the web stage, after every pass that can lay a joint, so no rewrite may break what those passes
settled: a rewrite is kept only when every other lane end that touched the old line still touches the new one,
and every farmhouse a way served still has one within `_SERVE_FT` (`keeps_the_web`) - and `commit_lane` still
refuses anything that splits the web.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist

from ..consts import Poly, Pt
from .clearance import _HAIRPIN_DEG, _clear_link, _clear_touch
from .geom import _TOUCH_GAP, _seg_cross, _turn_deg
from .smooth import _JOG_FT, commit_lane, web_pieces
from .sweeps import _SERVE_FT

_JOINT_FT = 1.0  # two lane ends this close are one point: the knot pass and the touch passes put them on the same vertex
# A HOOK: a lane's last leg this short that turns back this far (GM 2026-09-26, "they are not going to walk in one
# direction and then turn at a 30-degree angle"). Measured on the pool before this pass: three end legs of 9-11 ft
# turning 122-128 degrees (Kashikawa twice, Kuwabata once) - each a lane overshooting the way it joins and bending
# back onto it, or a nub past a junction. Both figures are drawing thresholds, not findings: 12 ft is about four
# paces, too short a leg to be a route of its own, and 90 degrees is where the turn stops reading as a bend.
_HOOK_FT = 12.0
_HOOK_DEG = 90.0


def _pts(ln: Mapping[str, Any]) -> Poly:
    return [(float(x), float(y)) for x, y in ln.get("pts") or []]


def _segs(p: Poly) -> list[tuple[Pt, Pt]]:
    return list(zip(p, p[1:], strict=False))


def joints(lanes: Sequence[Mapping[str, Any]]) -> list[tuple[int, int, int, int]]:
    """Every point where exactly two lane ENDS meet and no other way touches: `(i, end_i, j, end_j)`, an end
    being 0 or -1. A connector's end counts as a way touching (the cart route is not merged into a footpath), and
    two lanes that meet at both ends are a loop, not a joint."""
    live = [m for m, ln in enumerate(lanes) if not ln.get("connector") and len(ln.get("pts") or []) >= 2]
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


def oriented(lanes: Sequence[Mapping[str, Any]], i: int, ei: int, j: int, ej: int) -> tuple[Poly, Poly]:
    """The two lanes of a joint as one walk: `x` ENDS at the joint and `y` STARTS there."""
    x, y = _pts(lanes[i]), _pts(lanes[j])
    return (x[::-1] if ei == 0 else x), (y[::-1] if ej == -1 else y)


def tee(x: Poly, y: Poly, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> Poly | None:
    """`x` (ending at the joint) re-laid to meet `y`'s first leg as a T, from the vertex before its end: that
    vertex's foot on the leg, when the link is clear at footprint margins and the new last turn is no hairpin.
    `None` when there is nothing to gain (the foot IS the joint) or the link is not walkable."""
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
    pieces as it was, and every farmhouse some way served must still be served."""
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
    `None` when there is no hook or neither cut keeps the end on its ways."""
    if len(pts) < 3 or math.dist(pts[-2], pts[-1]) > _HOOK_FT or _turn_deg(pts[-3], pts[-2], pts[-1]) < _HOOK_DEG:
        return None
    end = pts[-1]
    met = [o for o in others if any(seg_dist(end[0], end[1], u, v) <= _TOUCH_GAP for u, v in _segs(o))]
    if not met or any(any(seg_dist(pts[-2][0], pts[-2][1], u, v) <= _TOUCH_GAP for u, v in _segs(o)) for o in met):
        return pts[:-1]  # a nub reaching nothing, or the vertex before already stands on a way the hook met
    if len(met) != 1:
        return None
    a, b = pts[-3], pts[-2]
    hits = [x for u, v in _segs(met[0]) if (x := _seg_cross(a, b, u, v)) is not None]
    if not hits:
        return None
    return [*pts[:-2], min(hits, key=lambda x: math.dist(a, x))]


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(a, 1), round(b, 1)] for a, b in p]


def straighten_joints(s: Settlement, hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> int:
    """The pass (see the module docstring). Returns the number of joints rewritten."""
    lanes: list[dict[str, Any]] = s.M.get("lanes") or []
    houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]
    changed = 0
    for _round in range(len(lanes) + 1):  # each rewrite removes a joint or a vertex, so this is a bound, not a budget
        if not (_one_hook(s, lanes, houses, hard, walls, water) or _one_joint(s, lanes, houses, hard, walls, water)):
            break
        changed += 1
    return changed


def _one_hook(s: Settlement, lanes: list[dict[str, Any]], houses: Sequence[Pt], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> bool:
    """Take the hook off the first lane end that has one and can lose it; False when none can."""
    for i, ln in enumerate(lanes):
        p = _pts(ln)
        if ln.get("connector") or len(p) < 3:
            continue
        others = [_pts(o) for k, o in enumerate(lanes) if k != i and len(o.get("pts") or []) >= 2]
        for q, back in ((p, False), (p[::-1], True)):
            new = unhooked(q, others)
            if new is None:
                continue
            new = new[::-1] if back else new
            if keeps_the_web(lanes, {i}, p, new, houses) and commit_lane(lanes, i, _rounded(new), hard, walls, water, s.reink_lane):
                return True
    return False


def _one_joint(s: Settlement, lanes: list[dict[str, Any]], houses: Sequence[Pt], hard: list[Poly], walls: Sequence[Poly], water: list[tuple[Pt, Pt]]) -> bool:
    """Rewrite the first joint that can be improved; False when none can."""
    for i, ei, j, ej in joints(lanes):
        x, y = oriented(lanes, i, ei, j, ej)
        old = [*x, *y[1:]]
        if _turn_deg(x[-2], x[-1], y[1]) >= _HAIRPIN_DEG:
            # the arriving lane that makes the SHORTER clear link becomes the T's stem
            tees = [(m, t) for m, t in ((i, tee(x, y, hard, walls, water)), (j, tee(y[::-1], x[::-1], hard, walls, water))) if t is not None]
            for m, t in sorted(tees, key=lambda mt: math.dist(mt[1][-2], mt[1][-1])):
                other = y if m == i else x[::-1]
                if keeps_the_web(lanes, {i, j}, old, [*t, *other], houses) and commit_lane(lanes, m, _rounded(t), hard, walls, water, s.reink_lane):
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
        if len(new) == len(old) or not keeps_the_web(lanes, {i, j}, old, new, houses):
            continue
        if commit_lane(lanes, i, _rounded(new), hard, walls, water, s.reink_lane):
            commit_lane(lanes, j, [], hard, walls, water, s.reink_lane)
            return True
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
    the other lane (no slide along it changes the distance)."""
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
    return to


def center_lane_ends(s: Settlement) -> int:
    """Every lane end that stops on another lane's tread is set where `centered_end` says, record and ink together.
    Runs after `straighten_joints`, the last pass that moves a lane end. Returns the number of ends moved."""
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
        if p != _pts(ln):
            ln["pts"] = _rounded(p)
            s.reink_lane(i)
    return moved
