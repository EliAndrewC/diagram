"""The DOUBLED TAIL (feature 261; split from `sweeps.py` by feature 280 at the 1,000-line bar): a lane whose end runs on
beside the way it met is cut back to where it came alongside, unless the cut would strand a lane that met the tail, and a
lane stranded only by the touch gap is carried onto the way first. `sweeps.py` re-exports every name here.

Research: doubled tail plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import seg_closest, seg_dist, seg_intersect, segments_cross

from ..consts import Pt
from .geom import polyline_len
from .keeper import kept

_ALONG_FT = 14.0  # ft: two centerlines this close read as one tread doubled - a 6 ft way's width plus its soft shoulders
"""Research: doubled tread distance - CONVENTION: centerlines within 14 ft read as one tread"""
_ALONG_MIN_FT = 30.0  # ft: shorter than this, running beside a way is just the approach to the junction
"""Research: tail run length - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); 30 ft beside a way before it is a doubled tail"""
_ALONG_DEG = 25.0  # deg: nearer to parallel than this, the lane is running WITH the way, not meeting it
"""Research: running with the way - CANON: the GM's ruling of 2026-10-25 - the doubled tail's angle is a goal of 20, "arbitrary and not an actual hard requirement", free to move to 15 or 25 if placement or the look needs it; asked here at 25, beside 0081's drawing-page convention of 20, because both at 20 refuse cohort seed 40 (feature 417 D30, observed 2026-10-25)"""
_DOUBLED_DEG = 15.0  # deg: a finished tail this near parallel is one tread doubled (Kuwabata's ran at ~3, Sawada's at 9.5); between
"""Research: doubled tail angle - CANON: the GM's ruling of 2026-10-25 - the angle is a goal of 20, "arbitrary and not an actual hard requirement", free to move to 15 or 25 if placement or the look needs it; asked here at 15, departing from the 20 that 0081's drawing page draws as its convention, because both at 20 refuse cohort seed 40 (a shallow crossing left; feature 417 D30, observed 2026-10-25); no source gives where a meeting stops reading as a junction (feature 417 R7)"""
# this and `_ALONG_DEG` the sweep still cuts it, to the crossing it overran, which then stands as a shallow Y - a junction, not a
# doubling (Inashiro's straggler meets its join lane at 21.6 degrees)
_CROSS_BACK_FT = 40.0  # ft: a crossing this close before the cut is the junction the doubled tail overran (Sawada's was 24)
"""Research: tail ends at the crossing it overran - research/questions/0081-village-lanes.drawing.html: within 40 ft"""


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


def tail_doubled(p: Sequence[Pt], o: Sequence[Pt]) -> bool:
    """Does an end of way `p` - EITHER end - run on beside way `o` at `_DOUBLED_DEG` (`along_tail`, asked of `p` and of it
    reversed)? The pair test of `law.doubled_tails`, asked pair by pair by a caller that keeps the answers (`knots.WebMemo`).

    Research: no doubled tail - research/questions/0081-village-lanes.drawing.html: an end running back along another way under 20 degrees is refused, cut where it comes alongside - asked at `_DOUBLED_DEG`, 15, a known gap carried to 405 T101"""
    return len(o) >= 2 and any(along_tail(q, o, deg=_DOUBLED_DEG) is not None for q in (p, p[::-1]))


def cut_at_tail(pts: Sequence[Pt], k: int, other: Sequence[Pt], step: float = 4.0) -> list[Pt]:
    """`pts` cut at its `k`th sample (the `along_tail` index) and ended on its snap onto `other`: the vertices before the
    cut, the cut point, and the nearest point of `other` to it.

    Research: tail ends at the crossing it overran - research/questions/0081-village-lanes.drawing.html: within 40 ft"""
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
