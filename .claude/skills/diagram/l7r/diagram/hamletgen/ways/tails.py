"""The DOUBLED TAIL (feature 261; split from `sweeps.py` by feature 280 at the 1,000-line bar): a lane whose end runs on
beside the way it met is cut back to where it came alongside, unless the cut would strand a lane that met the tail, and a
lane stranded only by the touch gap is carried onto the way first. `sweeps.py` re-exports every name here."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_closest, seg_dist, seg_intersect, segments_cross

from ..consts import Pt
from .geom import _TOUCH_GAP, _components, polyline_len
from .keeper import kept

_ALONG_FT = 14.0  # ft: two centerlines this close read as one tread doubled - a 6 ft way's width plus its soft shoulders
_ALONG_MIN_FT = 30.0  # ft: shorter than this, running beside a way is just the approach to the junction
_ALONG_DEG = 25.0  # deg: nearer to parallel than this, the lane is running WITH the way, not meeting it
_DOUBLED_DEG = 15.0  # deg: a finished tail this near parallel is one tread doubled (Kuwabata's ran at ~3, Sawada's at 9.5); between
# this and `_ALONG_DEG` the sweep still cuts it, to the crossing it overran, which then stands as a shallow Y - a junction, not a
# doubling (Inashiro's straggler meets its join lane at 21.6 degrees)
_CROSS_BACK_FT = 40.0  # ft: a crossing this close before the cut is the junction the doubled tail overran (Sawada's was 24)


def _parallel(u: Pt, v: Pt, deg: float) -> bool:
    """Whether two directions lie within `deg` of parallel, either way along; a zero-length one counts as parallel."""
    nu, nv = math.hypot(*u), math.hypot(*v)
    return not (nu and nv) or math.degrees(math.acos(min(1.0, abs(u[0] * v[0] + u[1] * v[1]) / (nu * nv)))) <= deg


@kept
def along_tail(pts: Sequence[Pt], other: Sequence[Pt], step: float = 4.0, deg: float = _ALONG_DEG) -> int | None:
    """The index in `pts`' samples where its END starts running alongside `other` - within `_ALONG_FT` of it, nearly
    parallel (within `deg`), for at least `_ALONG_MIN_FT` - or None. Samples every `step` along `pts` from its end inward."""
    samples: list[Pt] = []
    for a, b in zip(pts, pts[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        samples += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    samples.append(pts[-1])
    segs = list(zip(other, other[1:], strict=False))
    if not segs:
        return None
    k = len(samples) - 1
    while k > 0:
        q = samples[k]
        u = (samples[k][0] - samples[k - 1][0], samples[k][1] - samples[k - 1][1])
        # ALONGSIDE ANY REACH OF THE WAY WITHIN `_ALONG_FT`, NOT ONLY THE NEAREST (feature 293 I, Inashiro re-packed): a tail
        # that runs back along a way to that way's own vertex is nearest, at the vertex, to the OTHER reach meeting there - a
        # tie at zero - and was judged against that one, 27 degrees off, so a straggler's 95 ft retrace of lane 2 never counted
        near = [(a, b) for a, b in segs if seg_dist(q[0], q[1], a, b) <= _ALONG_FT]
        # ...WALKED THROUGH THE JUNCTION'S OWN APPROACH (feature 293 on 291): within `_ALONG_FT` of its end a lane still
        # beside the way may meet it at an angle - Mizuguchi's field spur left its street 20 degrees off the reach there,
        # then ran 10-12 ft beside it for 210 ft, and the tail was judged at its first sample alone. A T or a needle is
        # no nearer parallel past that approach, so neither reads as a tail for it
        if not near or not (any(_parallel(u, (b[0] - a[0], b[1] - a[1]), deg) for a, b in near) or polyline_len(samples[k - 1 :]) <= _ALONG_FT):
            break
        k -= 1
    if polyline_len(samples[k:]) < _ALONG_MIN_FT:
        return None
    return k


def cut_at_tail(pts: Sequence[Pt], k: int, other: Sequence[Pt], step: float = 4.0) -> list[Pt]:
    """`pts` cut at its `k`th sample (the `along_tail` index) and ended on its snap onto `other`: the vertices before the
    cut, the cut point, and the nearest point of `other` to it."""
    samples: list[Pt] = []
    for a, b in zip(pts, pts[1:], strict=False):
        n = max(1, int(math.dist(a, b) // step))
        samples += [(a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n) for t in range(n)]
    samples.append(pts[-1])
    cut = samples[k]
    cut_at = polyline_len(samples[: k + 1])
    out, acc = [pts[0]], 0.0
    for a, b in zip(pts, pts[1:], strict=False):
        acc += math.dist(a, b)
        if acc >= cut_at:
            break
        out.append(b)
    # ...UNLESS IT HAS ALREADY CROSSED THE WAY on its last run in (settlement-review of Sawada, feature 261): the snap then
    # lies behind the crossing, and the cut lane ran 24 ft past the way it met and bent back 116 degrees onto it - a hook.
    # A crossing within `_CROSS_BACK_FT` of the cut is where the lane met the way, and it ends there.
    kept = [*out, cut]
    walked = 0.0
    for m in range(len(kept) - 1, 0, -1):
        u, v = kept[m - 1], kept[m]
        hit = next((seg_intersect(u, v, c, d) for c, d in zip(other, other[1:], strict=False) if segments_cross(u, v, c, d)), None)
        if hit is not None:
            return [*kept[:m], (float(hit[0]), float(hit[1]))]
        walked += math.dist(u, v)
        if walked > _CROSS_BACK_FT:
            break
    a, b = min(zip(other, other[1:], strict=False), key=lambda ab: seg_dist(cut[0], cut[1], ab[0], ab[1]))
    snap = seg_closest(cut[0], cut[1], a, b)
    return [*kept, (float(snap[0]), float(snap[1]))]


def cut_keeps_network(lanes: Sequence[Mapping[str, Any]], i: int, before: Sequence[Pt], after: Sequence[Pt]) -> bool:
    """Whether replacing lane `i`'s points `before` with `after` leaves the lanes in no more pieces at the ink tolerance
    (`_TOUCH_GAP`) than they were. FOUND BY FEATURE 280 (Sawada, once the larger yards moved its rows): a straggler's tail
    running beside the way it met was cut back to where it came alongside, and a third straggler that had joined that
    tail was left 13.7 ft from anything - two lane networks, which `test_every_shipped_hamlets_lanes_are_one_network`
    caught. A tail that carries another lane's junction is not a doubled tail; it is part of the network."""
    ways = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in lanes]

    def pieces(pts: Sequence[Pt]) -> int:
        ws = [list(pts) if j == i else w for j, w in enumerate(ways)]
        live = [w for w in ws if len(w) >= 2]
        return len(set(_components(live, _TOUCH_GAP))) if len(live) > 1 else 1

    return pieces(after) <= pieces(before)


_RESEAT_FT = 2.0 * _TOUCH_GAP
"""How far a lane end left on a cut tail may be carried onto the way the tail ran beside (Sawada, feature 280: 4.4 ft)."""


def reseat_on_way(lanes: Sequence[Mapping[str, Any]], i: int, before: Sequence[Pt], after: Sequence[Pt], way: Sequence[Pt]) -> dict[int, list[Pt]]:
    """The lanes whose end stood on lane `i`'s tail (`before`) and on nothing once it is cut (`after`), each with that end
    carried onto `way` - the way the tail ran beside - where it lies within `_RESEAT_FT` of it. FOUND BY FEATURE 280
    (Sawada): a straggler met the doubled tail 4.4 ft off the way beside it, just past the touch gap, so the cut would
    strand it and the tail stayed doubled; a tail 4 ft off a way is that way, and the straggler meets it there."""
    ways = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in lanes]
    tail, kept, road = list(zip(before, before[1:], strict=False)), list(zip(after, after[1:], strict=False)), list(zip(way, way[1:], strict=False))
    moved: dict[int, list[Pt]] = {}
    for j, w in enumerate(ways):
        if j == i or len(w) < 2 or not road:
            continue
        rest = [sg for k, o in enumerate(ways) if k not in (i, j) for sg in zip(o, o[1:], strict=False)]
        for end in (0, len(w) - 1):
            e = w[end]
            if not any(seg_dist(e[0], e[1], a, b) <= _TOUCH_GAP for a, b in tail) or any(seg_dist(e[0], e[1], a, b) <= _TOUCH_GAP for a, b in kept + rest):
                continue
            to = min((seg_closest(e[0], e[1], a, b) for a, b in road), key=lambda z: math.dist(e, z))
            if math.dist(e, to) <= _RESEAT_FT:
                w = moved.get(j, w)[:]
                w[end] = (float(to[0]), float(to[1]))
                moved[j] = w
    return moved


def _sweep_doubled_tails(s: Settlement) -> int:
    """A lane whose end runs ALONGSIDE another way has met that way where it first came alongside, and ends there
    (settlement-review of Kuwabata, feature 261: a join lane ran back 122 ft beside the connector, 12.7 ft apart and
    merging to one stroke, past the corner where it met it - a doubled road and a dead end). The tail is cut at its first
    sample alongside and the end snapped onto the way, so the two meet in one junction. Each end is asked in turn."""
    lanes = s.M.get("lanes") or []
    fixed = 0
    # THE NARROWER TAIL IS CUT, NEVER THE WIDER (settlement-review of Sawada, feature 261): a 6 ft track and a 3 ft
    # straggler ran into the hub side by side, the track was cut, and the route out necked to 69.7 ft of footpath -
    # the thing `_keep_the_route_wide` exists to prevent, arriving after it ran. Narrow lanes are asked first, and a lane
    # is never cut back along a narrower one.
    for i in sorted(range(len(lanes)), key=lambda k: float(lanes[k].get("w") or 3)):
        ln = lanes[i]
        if (ln.get("connector") or ln.get("street")) or ln.get("spur") or len(ln.get("pts") or []) < 2:
            continue
        pts = [(float(x), float(y)) for x, y in ln["pts"]]
        changed = False
        for _end in range(2):
            for j, o in enumerate(lanes):
                op = [(float(x), float(y)) for x, y in (o.get("pts") or [])]
                if j == i or len(op) < 2 or float(o.get("w") or 3) < float(ln.get("w") or 3):
                    continue
                k = along_tail(pts, op)
                if k is not None:
                    cut = cut_at_tail(pts, k, op)
                    moved = reseat_on_way(lanes, i, pts, cut, op)
                    if not cut_keeps_network([{"pts": moved.get(n, lx.get("pts") or [])} for n, lx in enumerate(lanes)], i, pts, cut):
                        continue  # the tail carries another lane's junction: cutting it would strand that lane
                    # ...AND EVERY LANE CARRIED ONTO THE WAY IS ADMITTED BY THE OVERLAP MATRIX (feature 287 M8), all or none:
                    # a carried end the matrix refuses would be left on the cut tail, stranded, so the tail is not cut
                    if not all(s.admits("lanes", {**lanes[n], "pts": [[round(x, 1), round(y, 1)] for x, y in w]}, ignore=lanes[n]) for n, w in moved.items()):
                        continue
                    for n, w in moved.items():
                        s.reshape_lane(lanes[n], w)
                        s.reink_lane(n)
                    pts, changed = cut, True
                    fixed += 1
                    break
            pts.reverse()
        if changed and s.reshape_lane(ln, pts):  # asked of the overlap matrix (feature 287 M8)
            s.reink_lane(i)
    return fixed
