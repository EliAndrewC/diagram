"""Where two lanes meet END TO END, read them as one way (GM 2026-09-26).

The web is recorded as pieces, and a shape rule read ONE record at a time misses a fold or a jog AT a joint: where one
record ends exactly where the next begins and nothing else touches the point, the walker sees one lane. Inashiro showed
both, and the GM: *"people tend to walk in straight lines. Or, more generally, they walk in reasonably efficient paths.
So they may walk in a curved line, but they are not going to walk in one direction and then turn at a 30-degree angle
to keep walking."* So the lane law reads the joints (`joints`, `as_walked`, `oriented`) and judges the walk.

The pass that rewrote the joints after the web was laid (`straighten_joints`, with `center_lane_ends`, `meet_end_to_end`,
`split_at_crossings` and `fold_the_connector_hairpin`) went in feature 417 T26: switched off over the fixed seeds and the
pinned rows it moved no verdict, the settle (`settle_the_web`) keeping what it mended.

Research: plumbing - NONE
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_dist

from ..consts import Poly, Pt
from .clearance import _HAIRPIN_DEG
from .geom import _TOUCH_GAP
from .smooth import web_pieces
from .sweeps import _SERVE_FT

_JOINT_FT = 1.0  # two lane ends this close are one point: the knot pass and the touch passes put them on the same vertex
# A HOOK: a lane's last leg this short that turns back this far (GM 2026-09-26, "they are not going to walk in one
# direction and then turn at a 30-degree angle"). Measured on the pool before this pass: three end legs of 9-11 ft
# turning 122-128 degrees (Kashikawa twice, Kuwabata once) - each a lane overshooting the way it joins and bending
# back onto it, or a nub past a junction. Both figures are drawing thresholds, not findings: 12 ft is about four
# paces, too short a leg to be a route of its own, and 90 degrees is where the turn stops reading as a bend.
# (the two figures live in `geom`, a layer below, since feature 291: the door paths in `serve` take their hook off too)


RANK_WIDTHS = {"access": 3.0, "way target": 3.0, "field way": 5.0}
"""A lane's width by the rank its role gives it (a household's way and a way target's are footpaths; the field way is the
field spur's rank), with the spur `spur` 5 and the connector 6 (`rank_width`).

Research: a width by rank - research/questions/0081-village-lanes.drawing.html: a footpath is drawn 3 ft wide, the cluster's spine and its spur to the fields 5 ft, and the track out to the wider world 6 ft"""


def rank_width(ln: Mapping[str, Any]) -> float | None:
    """The width lane `ln`'s role ranks it at - the connector the track out's 6 ft, the field spur its 5, a household's way
    or a way target's a footpath's 3 (`RANK_WIDTHS`) - or None for a lane its role does not rank (a web lane, a link, a
    street), which takes the width of the way it continues.

    Research: a width by rank - research/questions/0081-village-lanes.drawing.html: 3 ft footpath, 5 ft spine and field spur, 6 ft track out"""
    if ln.get("connector"):
        return 6.0
    if ln.get("spur"):
        return 5.0
    return RANK_WIDTHS.get(str(ln.get("role")))


def at_rank(ln: Mapping[str, Any]) -> bool:
    """Lane `ln` is ranked by its role and drawn at that rank (`rank_width`): a width step at its joint is where one rank of way
    meets another (a household's footpath ending where the field spur begins), not a way changing its tread.

    Research: a width by rank - research/questions/0081-village-lanes.drawing.html: each way drawn at its rank's width"""
    r = rank_width(ln)
    return r is not None and float(ln.get("w") or 3.0) == r


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


def pulled(pts: Poly, ok: Callable[[int, int], bool]) -> Poly:
    """The string-pull: from each vertex, jump to the furthest later vertex `ok` allows (the one `_smooth_web` asked, until feature 417 T26)."""
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


def _key(q: Poly) -> tuple[tuple[float, float], ...]:
    return tuple((float(x), float(y)) for x, y in q)


def _rounded(p: Poly) -> list[list[float]]:
    return [[round(a, 1), round(b, 1)] for a, b in p]


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
