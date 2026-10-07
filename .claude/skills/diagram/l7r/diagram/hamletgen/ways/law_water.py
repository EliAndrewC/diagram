"""THE LANE LAW'S WATER (lifted out of `law.py` at the 1,000-line bar, feature 328 wave 6; `law` re-exports every name):
where a way crosses a brook or a channel - over and back, off a ford, off square, unbridged, undeckable or a short deck, a
plank's faults - and the lane-record helpers the law and these share (`lane_pts`, `_ways`, `_brooks`, `_min_dist`).

Research: plumbing and wrappers - NONE: each rule is claimed at the predicate that decides it
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import seg_dist, seg_intersect, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement._knobs import bridge_carried_ways, bridge_crossed_waters
from l7r.diagram.settlement.city.bridges import PLANK_DITCH_FT, deck_covers, flooded_ground, plank_ditch, plank_on_supply, undeckable_at

from ..consts import FORD_HALF, Poly, Pt
from .checks import FORD_SQUARE_TOL_DEG
from .keeper import kept

DECK_NEAR_FT = 40.0
"""A deck this near a recorded watercourse is over it, and is judged against that course's width."""


def lane_pts(ln: Mapping[str, Any]) -> Poly:
    """A lane record's points as float tuples."""
    return [(float(x), float(y)) for x, y in (ln.get("pts") or [])]


def _ways(M: Mapping[str, Any]) -> list[Poly]:
    return [lane_pts(ln) for ln in (M.get("lanes") or [])]


def _brooks(M: Mapping[str, Any]) -> list[Poly]:
    return [[(float(p[0]), float(p[1])) for p in s["poly"]] for s in (M.get("streams") or []) if len(s.get("poly", ())) >= 2]


def _min_dist(pt: Pt, poly: Poly) -> float:
    return min(seg_dist(pt[0], pt[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1))


# ---- a lane's own shape --------------------------------------------------------------------------------------------


def _crossings(p: Poly, course: Poly) -> list[Pt]:
    return [x for _k, x in crossing_points(p, course)]


def over_and_back(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """(lane index, crossings) for every lane crossing one brook twice or more - out and home, two planks for nothing.
    Research: over and back - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    ways = _ways(M)
    return [(i, n) for brook in _brooks(M) for i, p in enumerate(ways) if (n := len(_crossings(p, brook))) >= 2]


@kept
def crossing_points(p: Poly, course: Poly) -> list[tuple[int, Pt]]:
    """(segment index, point) for every crossing of `course` by the run `p`, in the run's order.

    THE COURSE INDEXED ONCE (constitution X clause 15): a household's way out is sampled every 10 ft and a brook runs to
    hundreds of segments, so every pair was millions of tests a map (`settle_the_web`'s way-out step, 4.3 s of Kashikawa's
    5.0). The grid only prunes - a course segment whose box cannot meet the run segment's cannot cross it - and the same
    test decides, in the same order."""
    grid = PointGrid(64.0)
    grid.extend((j, c, d, min(c[0], d[0]), min(c[1], d[1]), max(c[0], d[0]), max(c[1], d[1])) for j, (c, d) in enumerate(zip(course, course[1:], strict=False)))
    out = []
    for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        near = {item[0]: item for item in grid.near(mx, my, math.dist(a, b) / 2 + 1.0)}
        for j in sorted(near):
            _j, c, d, *_box = near[j]
            if segments_cross(a, b, c, d) and (x := seg_intersect(a, b, c, d)) is not None:
                out.append((k, x))
    return out


def off_ford_at(M: Mapping[str, Any], reach: float = FORD_HALF) -> list[tuple[int, int, Pt]]:
    """(lane index, segment index, point) for every crossing of the brook by a lane farther than `reach` from every
    recorded ford (`meta.brook_fords`).
    Research:
        crossed at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        how far off a crossing place - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: within `FORD_HALF`, half the crossing place's 60 ft"""
    fords = [(float(f[0]), float(f[1])) for f in (M.get("meta") or {}).get("brook_fords") or []]
    return [(i, k, x) for brook in _brooks(M) for i, p in enumerate(_ways(M)) for k, x in crossing_points(p, brook) if min((math.dist(x, f) for f in fords), default=math.inf) > reach]


def off_ford_crossings(M: Mapping[str, Any], reach: float = FORD_HALF) -> list[tuple[int, int]]:
    """Every crossing of the brook by a lane that stands farther than `reach` from every recorded ford
    (`meta.brook_fords`) - ONE constant with the router's ford gap (`off_ford_at`)."""
    return [(round(x[0]), round(x[1])) for _i, _k, x in off_ford_at(M, reach)]


def water_courses(M: Mapping[str, Any], water: str = "brook") -> list[Poly]:
    """The brook's courses (`water="brook"`, the streams) or the drawn channels' (`water="channel"`)."""
    return _brooks(M) if water == "brook" else [[(float(q[0]), float(q[1])) for q in c["pts"]] for c in M.get("drawn_channels") or []]


def off_square(a: Pt, b: Pt, u: Pt, v: Pt) -> float:
    """How many degrees the run `a`-`b` crosses the course `u`-`v` off square."""
    t = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]) - math.atan2(v[1] - u[1], v[0] - u[0])) % 180.0
    return abs(90.0 - t)


def oblique_at(M: Mapping[str, Any], water: str = "brook") -> list[tuple[int, int, Pt, float]]:
    """(lane index, segment index, point, degrees off square) for every lane crossing of the brook or a drawn channel
    (`water_courses`) more than `FORD_SQUARE_TOL_DEG` off square.
    Research:
        square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        square ditch crossing - UNRESEARCHED: a channel crossing squared within `FORD_SQUARE_TOL_DEG`, 10 degrees (0084 squares only the standalone footplank)"""
    out = []
    ways = list(_ways(M))
    boxes = [_bbox(p) for p in ways]
    for course in water_courses(M, water):
        cb = _bbox(course)
        for i, p in enumerate(ways):
            # ...a lane whose box misses the course's crosses none of it (feature 314: the census's 1,000 comparisons a call)
            lb = boxes[i]
            if lb is None or cb is None or lb[2] < cb[0] or cb[2] < lb[0] or lb[3] < cb[1] or cb[3] < lb[1]:
                continue
            for k, (a, b) in enumerate(zip(p, p[1:], strict=False)):
                for u, v in zip(course, course[1:], strict=False):
                    if segments_cross(a, b, u, v) and (off := off_square(a, b, u, v)) > FORD_SQUARE_TOL_DEG:
                        out.append((i, k, seg_intersect(a, b, u, v) or a, off))
    return out


def _bbox(p: Sequence[Sequence[float]]) -> tuple[float, float, float, float] | None:
    """The box `(x0, y0, x1, y1)` of a polyline, or None for an empty one."""
    if not p:
        return None
    xs, ys = [float(q[0]) for q in p], [float(q[1]) for q in p]
    return (min(xs), min(ys), max(xs), max(ys))


def boxes_meet(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]], pad: float) -> bool:
    """Do the boxes of two polylines come within `pad` of each other (`_bbox`)? Two empty ones never do."""
    ba, bb = _bbox(a), _bbox(b)
    return ba is not None and bb is not None and not (ba[2] + pad < bb[0] or bb[2] + pad < ba[0] or ba[3] + pad < bb[1] or bb[3] + pad < ba[1])


def oblique_crossings(M: Mapping[str, Any], water: str = "brook") -> list[tuple[int, int, float]]:
    """(x, y, degrees off square) for every lane crossing more than `FORD_SQUARE_TOL_DEG` off square - of the brook
    (`water="brook"`, the streams) or of a drawn channel (`water="channel"`, `drawn_channels`) (`oblique_at`)."""
    return [(round(x[0]), round(x[1]), round(off, 1)) for _i, _k, x, off in oblique_at(M, water)]


def unbridged_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """Every crossing of water by a lane that no drawn deck covers (`deck_covers`): the brook, and every other course a way
    may have to be carried over (`bridge_crossed_waters`) - a drawn channel, a field ditch, the polder's drain (feature
    287: the drain takes no footplank, `plank_on_supply`, so a way over it is carried on the deck `bridges()` lays where
    the web's last pass left a crossing it can deck, and cut where it could not - never walked through the water).
    Research: every crossing decked - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html"""
    decks = M.get("bridges") or []
    waters = [*_brooks(M), *([(float(q[0]), float(q[1])) for q in wpts] for wpts, _w in bridge_crossed_waters(M) if len(wpts) >= 2)]
    hits = {(round(x[0]), round(x[1])) for course in waters for p in _ways(M) for x in _crossings(p, course) if not any(deck_covers(d, x[0], x[1]) for d in decks)}
    return sorted(hits)


def deck_seats(pts: Poly, width: float, waters: Sequence[tuple[Any, float]], ftpx: float = 1.0, wet: Sequence[Poly] = (), M: Any = None) -> list[tuple[int, int]]:
    """Every crossing of `waters` (`bridge_crossed_waters`) by a way along `pts` where no deck seats: `crossing_deck`, the
    very solve `bridges()` makes - grown, then skewed toward square, until every corner clears the whole crossed course
    (`_deck_corners_clear`) and lands off the flooded rice (`wet`, `flooded_ground`) (`undeckable_at`).
    Research: a deck's corners on dry ground - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html"""
    return [(round(p[0]), round(p[1])) for _k, p in undeckable_at(pts, width, waters, ftpx, wet, M)]


def undeckable_crossings(M: Mapping[str, Any]) -> list[tuple[int, int]]:
    """`deck_seats` over every carried way of the map (`bridge_carried_ways`) against every watercourse it may cross."""
    ftpx = float((M.get("meta") or {}).get("ftpx") or 1.0)
    waters = bridge_crossed_waters(M)
    wet = flooded_ground(M)
    return [x for rpts, rw in bridge_carried_ways(M) for x in deck_seats([(float(q[0]), float(q[1])) for q in rpts], float(rw), waters, ftpx, wet, M)]


def short_decks(M: Mapping[str, Any]) -> list[tuple[int, int, float, float]]:
    """(x, y, span, water width) for every deck over a recorded watercourse (within `DECK_NEAR_FT` of it) shorter than that
    course's full width - its abutment stands in the water (`bridges_span_their_water`).
    Research:
        a deck spans its water - research/questions/0087-road-bridges-over-rivers-and-canals-hashi.drawing.html
        assumed water widths - UNRESEARCHED: 3 ft for a ditch or channel, 6 ft for a stream, where none is recorded"""
    courses = [([(float(p[0]), float(p[1])) for p in d["poly"]], max(float(d.get("w", 3.0)), float(d.get("w_tail", 3.0)))) for d in (M.get("field_ditches") or [])]
    courses += [([(float(p[0]), float(p[1])) for p in c["poly"]], float(c.get("w", 3.0))) for c in (M.get("channels") or [])]
    courses += [([(float(p[0]), float(p[1])) for p in s["poly"]], float(s.get("w", 6.0))) for s in (M.get("streams") or [])]
    short = []
    for b in M.get("bridges") or []:
        bx, by, span = float(b["x"]), float(b["y"]), float(b["span"])
        near = min(((_min_dist((bx, by), poly), w) for poly, w in courses if len(poly) >= 2), key=lambda t: t[0], default=(math.inf, 0.0))
        if near[0] <= DECK_NEAR_FT and span < near[1]:
            short.append((round(bx), round(by), round(span, 1), round(near[1], 1)))
    return short


def plank_faults(M: Mapping[str, Any]) -> tuple[list[tuple[int, int]], list[tuple[int, int, str]]]:
    """(stranded, on the drain): footplanks farther than `PLANK_DITCH_FT` from every recorded field ditch, and planks whose
    nearest ditch is not a supply ditch (`SUPPLY_ROLES`: a main, a branch or a lateral) - the collector, the drain or the
    feeder. `plank_ditch` and `plank_on_supply` are the placer's own (`channel_footbridges`, ways W14).

    THE LATERAL IS A SUPPLY DITCH (feature 287; Kuwabata's six planks). The test this was lifted from read the comb's two roles
    only, and so named every plank on a polder's laterals and settlement-side ring canal - which record the role `lateral` -
    as laid on a drain. The record answers it: a plank is laid where a bund path meets an IRRIGATION ditch (research/questions/0084-plank-bridges-over-farm-ditches-itabashi.html),
    and the polder's inner ring canal and its field ditches are its distribution water (research/archetypes/110).
    Research: planks on supply ditches - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html"""
    ditches = M.get("field_ditches") or []
    stranded, on_drain = [], []
    for b in M.get("bridges") or []:
        if not b.get("foot"):
            continue
        pt = (float(b["x"]), float(b["y"]))
        dist, role = plank_ditch(pt, ditches)
        if dist >= PLANK_DITCH_FT:
            stranded.append((round(pt[0]), round(pt[1])))
        elif not plank_on_supply(pt, ditches):
            on_drain.append((round(pt[0]), round(pt[1]), str(role)))
    return stranded, on_drain


# ---- the ways out --------------------------------------------------------------------------------------------------
