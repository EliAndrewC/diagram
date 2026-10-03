"""A lane as a run of arc length, the edits the settle makes to one, and the squaring of its crossings (moved from
`settle.py` by feature 316, bodies verbatim; `settle.py` re-exports every name, so `settle.sub_run` and the rest resolve).

Research: lane run plumbing - NONE: arc lengths, cuts, re-orientation and the bookkeeping of a lane's pieces
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_closest, seg_dist

from ..consts import WEB_CLEARANCE, Poly, Pt
from . import law
from .checks import square_crossings
from .geom import _components, polyline_len

SQUARE_PASSES = 4
"""How many times one lane is squared against one water in a round - squaring is idempotent after the first, so this is
the bound for a lane crossing the same course several times."""

SQUARE_MARGIN_FT = 6.0
"""The square leg's reach past the water's half-width (`stage_crossings`' own figure, moved here with the squaring).

Research: the square leg - UNRESEARCHED: 6 ft past the water's half-width"""


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
        if not s.reshape_lane(ln, keep[0]):
            continue  # the matrix refuses what the cut would leave (feature 287 M8): the lane stands as it was
        s.reink_lane(i)
        for q in keep[1:]:
            s.lane(q, width=float(ln.get("w") or 3.0), clearance=WEB_CLEARANCE, worn=bool(ln.get("worn", True)))
            lanes[-1].update({key: ln[key] for key in ("role", "web") if key in ln})
    if drops:
        s.drop_lanes(drops)
    return len(edits)


def _unkinked(p: Poly, span: tuple[str, int, int]) -> list[Poly]:
    """A run that doubles back keeps its longer arm; one that kinks loses the stretch between its two turns.

    Research: no hairpin or zigzag - research/questions/0081-village-lanes.drawing.html: longer arm kept, or the turns' stretch cut"""
    kind, ka, kb = span
    if kind == "doubles back":
        head, tail = p[: ka + 1], p[ka:]
        return [max(head, tail, key=polyline_len)]
    return [q for q in (p[: ka + 1], p[kb:]) if len(q) >= 2]


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


def with_edits(M: Mapping[str, Any], edits: Mapping[int, Sequence[Poly]]) -> dict[str, Any]:
    """`M` as `apply_pieces` would leave it after `edits`, its lane indices kept: each edited lane's first piece in place (a
    lane with none left empty rather than removed) and the further pieces appended."""
    lanes = [dict(ln) for ln in M.get("lanes") or []]
    extra = []
    for i, pieces in edits.items():
        lanes[i]["pts"] = [list(q) for q in pieces[0]] if pieces else []
        extra += [{"pts": [list(q) for q in p]} for p in pieces[1:]]
    return {**M, "lanes": [*lanes, *extra]}


def connector_component(lanes: Sequence[Mapping[str, Any]]) -> set[int]:
    """The lanes joined to the connector's network at the ink tolerance (`law.JOIN_TOL`) - what `settle_network` keeps."""
    live = [i for i, ln in enumerate(lanes) if len(ln.get("pts") or []) >= 2]
    labels = _components([_pts(lanes[i]) for i in live], law.JOIN_TOL)
    roots = {labels[n] for n, i in enumerate(live) if lanes[i].get("connector")}
    return {i for n, i in enumerate(live) if labels[n] in roots}


def _box(p: Poly, pad: float) -> tuple[float, float, float, float]:
    return (min(q[0] for q in p) - pad, min(q[1] for q in p) - pad, max(q[0] for q in p) + pad, max(q[1] for q in p) + pad)


# ---- step 1: every crossing square -------------------------------------------------------------------------------------


def square_waters(M: Mapping[str, Any]) -> list[tuple[Poly, float]]:
    """(course, half-width plus the leg's margin) for the brook and every drawn channel - what `stage_crossings` squared."""
    margin = SQUARE_MARGIN_FT / float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = [([(float(x), float(y)) for x, y in f["poly"]], float(f.get("w", 8.0)) / 2 + margin) for f in M.get("streams") or [] if len(f.get("poly") or ()) >= 2]
    waters += [([(float(x), float(y)) for x, y in c["pts"]], float(c.get("w0", 4.0)) / 2 + margin) for c in M.get("drawn_channels") or [] if len(c.get("pts") or ()) >= 2]
    return waters


def square_every_crossing(s: Any) -> int:
    """Square every lane at every crossing of the brook and the drawn channels (`square_crossings`), the connector's too.
    Returns the lanes changed.

    Research:
        square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the track out too
        square ditch crossing - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the drawn channels
        a moved end keeps its joint - NONE: another lane ending there is moved with it"""
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
        if q != p and s.reshape_lane(ln, q):
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
                            moved = [list(q) for q in op]
                            moved[e] = [round(new[0], 1), round(new[1], 1)]
                            if s.reshape_lane(other, moved):
                                s.reink_lane(j)
    return changed


def square_run(M: Mapping[str, Any], run: Poly) -> Poly:
    """`run` squared at every crossing of the brook and the drawn channels (`square_crossings`), as settle step 1 squares
    every lane - so a tree lane is judged, and drawn, square where it crosses water (cohort seed 8: the exit strip crossed the
    brook at its ford 38 degrees off square, and the corridor was refused for it).

    Research:
        square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        square ditch crossing - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html"""
    q = list(run)
    for course, half in square_waters(M):
        if not law.boxes_meet(q, course, half):  # out of its reach the squaring changes nothing (feature 314)
            continue
        for _ in range(SQUARE_PASSES):
            nq = square_crossings(q, course, half)
            if nq == q:
                break
            q = nq
    return q


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
