"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: plumbing - NONE
"""

from __future__ import annotations

import functools
import math
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, seg_intersect, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.settlement._geom.primitives import seg_dists
from l7r.diagram.sitegen.geom import crosses_disc, crosses_poly, unit

from ..clearance import pairs_within
from ..consts import (
    FORD_HALF,
    WEB_REACH_FT,
    Poly,
    Pt,
)
from .geom import _TOUCH_GAP
from .geom import lanes_share_tread as lanes_share_tread


def stream_segs(s: Settlement) -> list[tuple[Pt, Pt]]:
    """Just the STREAMS - the water a way needs a real deck to cross, as opposed to a plank.

    SPLIT OUT FROM `drawn_water_segs` BECAUSE THE DISTINCTION IS LOAD-BEARING, and it was measured
    the hard way. A peer session wired a blanket `shallow_crossing` veto into the link pass against
    the undifferentiated list (`plan.watercourses` plus every drawn channel) and the cohort went
    **41/48 -> 26/48, with 21 seeds failing `farmhouses_reach_a_way`**. The cause was the LIST, not
    the placement: a link joining two halves of a hamlet crosses field ditches constantly and often
    obliquely, and an aze ditch is a stride across - demanding a square crossing of every one strands
    the very components the pass exists to join. A far bigger defect than the oblique stream crossing
    the veto was written for.

    So the rule a way must respect is not "never cross water at a slant", it is "never cross water
    that needs a DECK at a slant", and this is that subset. `drawn_water_segs` still returns
    everything, for callers that want to avoid or bridge any water at all.

    Consumer note: `_join_orphan_ways` is the pass that needs this - it deliberately passes an EMPTY
    water list today ("a link may go the long way round, and may be planked"), which is exactly why
    it is the pass that can lay a way down the length of a brook (cohort seed 47).
    `_bridge_collinear_breaks` did NOT (it went in feature 417 T26): it handed its water to `_route`, which already refuses
    to cross a watercourse at any angle.

    THE BROOK HAS CROSSINGS (feature 261): where `stage_ways` has opened fords (`s.brook_fords`), the stream's
    segments come back with a short gap at each, so the router may carry a way over the brook there - and only
    there, and only near square, because the gap is shorter than the corridor is deep. `bridges()` reads the
    UNgapped `M["streams"]` and decks every such crossing.

    THE COURSE AS FIRST DRAWN (feature 287, M2): the brook is rounded at the end of the water stages now, before the ways,
    and a way is still routed against its `stations` - the course before the rounding - because rounding the brook before
    the ways were routed moved every way its corners had shaped (`Settlement.round_stream`). The fords (`brook_fords`) and
    the crossing band (`set_crossing`) read the same unrounded course, `plan.brook`.

    Research:
        the brook crossed only at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html:
            the stream's segments gapped at each crossing place, 30 ft either side
        ditches cross freely - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a ditch is
            planked, not held to the deck rule"""
    courses = [st.get("stations") or st.get("poly") or [] for st in s.M.get("streams", [])]
    segs = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for c in courses for a, b in zip(c, c[1:], strict=False)]
    return gap_segments(segs, getattr(s, "brook_fords", ()), FORD_HALF)


def brook_fords(brook: Sequence[Pt], spacing: float, bend_deg: float) -> list[Pt]:
    """Where the brook may be crossed: points every `spacing` along its course where it runs straight for the
    deck's length either side (the turn between the reaches `FORD_HALF` behind and ahead is under `bend_deg`),
    so a way crossing there crosses it square and the plank lands on both banks. A bend is skipped, not moved:
    the next site along is `spacing` further on.

    Research:
        crossing places along the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html:
            every `spacing` (160 ft), a GUESS there
        only on a straight reach - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a bend
            skipped, so the crossing is square"""
    out: list[Pt] = []
    legs = [(a, b, math.dist(a, b)) for a, b in zip(brook, brook[1:], strict=False) if math.dist(a, b) > 0.0]
    total = sum(n for _a, _b, n in legs)

    def at(d: float) -> tuple[Pt, Pt]:
        # the loop below only asks inside the course (d + FORD_HALF < total); the LAST leg answers whatever falls past
        # the legs before it, float rounding past the end included, clamped to its far point
        run = 0.0
        for a, b, n in legs[:-1]:
            if run + n >= d:
                t = (d - run) / n
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / n, (b[1] - a[1]) / n)
            run += n
        a, b, n = legs[-1]
        t = min(1.0, (d - run) / n)
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / n, (b[1] - a[1]) / n)

    d = spacing / 2.0
    while legs and d + FORD_HALF < total and d - FORD_HALF > 0.0:
        c, _ = at(d)
        _p, u0 = at(d - FORD_HALF)
        _q, u1 = at(d + FORD_HALF)
        if math.degrees(math.acos(max(-1.0, min(1.0, u0[0] * u1[0] + u0[1] * u1[1])))) < bend_deg:
            out.append(c)
        d += spacing
    return out


@functools.lru_cache(maxsize=64)
def brook_boxes(brook: tuple[Pt, ...]) -> tuple[tuple[Pt, Pt, float, float, float, float], ...]:
    """Each leg of the brook with its bounding box (x0, x1, y0, y1) - built once a brook (`ford_crossing`'s prefilter).

    Research: plumbing - NONE: a memo of the legs' boxes
        its cache size - NONE: a memo's size, which decides nothing about the place - 64
    """
    return tuple((a, b, min(a[0], b[0]), max(a[0], b[0]), min(a[1], b[1]), max(a[1], b[1])) for a, b in zip(brook, brook[1:], strict=False))


@functools.lru_cache(maxsize=256)
def ford_leg(f: Pt, brook: tuple[Pt, ...]) -> tuple[Pt, Pt]:
    """The brook's segment nearest the ford `f` - asked once a ford (feature 320, perf-audit: `settle_field` asked it of
    every network point, 703k `seg_dist` calls on cohort seed 39 at 10 households, half the step's time).

    Research: plumbing - NONE: a memo of the nearest segment
        its cache size - NONE: a memo's size, which decides nothing about the place - 256
    """
    return min(zip(brook, brook[1:], strict=False), key=lambda ab: seg_dist(f[0], f[1], ab[0], ab[1]))


def ford_crossing(start: Pt, end: Pt, brook: Sequence[Pt], fords: Sequence[Pt], landing: float = 22.0) -> list[Pt]:
    """The two landings of a square crossing at the ford that makes start -> ford -> end shortest, ordered from the
    start's bank - or nothing, when the straight run from `start` to `end` does not cross the brook (or there is no
    ford). A landing stands `landing` px off the brook square to its local reach: past the 14 px the router keeps off
    water, and inside the ford's gap, so a path through the two lands on the deck `bridges()` puts there.

    Research:
        square at the ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the ford
            that makes the walk shortest, landings square to the reach
        landing 22 px off the brook - NONE: fitted to the router's water margin and the ford's gap"""
    if not fords:
        return []
    x0, x1, y0, y1 = min(start[0], end[0]), max(start[0], end[0]), min(start[1], end[1]), max(start[1], end[1])
    # ...ASKED ONLY OF THE LEGS WHOSE BOX MEETS THE RUN'S (`brook_boxes`, once a brook): a leg whose box misses the run's
    # cannot cross it (feature 320, perf-audit: 484k crossing tests a seed against a brook that never changes)
    if not any(
        segments_cross(start, end, a, b) for a, b, bx0, bx1, by0, by1 in brook_boxes(brook if isinstance(brook, tuple) else tuple(brook)) if bx0 <= x1 and bx1 >= x0 and by0 <= y1 and by1 >= y0
    ):
        return []
    f = min(fords, key=lambda c: math.dist(start, c) + math.dist(c, end))
    a, b = ford_leg((float(f[0]), float(f[1])), brook if isinstance(brook, tuple) else tuple(brook))
    ux, uy = unit(b[0] - a[0], b[1] - a[1])
    nx, ny = -uy, ux  # square to the reach
    p1, p2 = (f[0] + nx * landing, f[1] + ny * landing), (f[0] - nx * landing, f[1] - ny * landing)
    return [p1, p2] if math.dist(start, p1) <= math.dist(start, p2) else [p2, p1]


def gap_segments(segs: Sequence[tuple[Pt, Pt]], centers: Sequence[Pt], half: float) -> list[tuple[Pt, Pt]]:
    """`segs` with every stretch within `half` of a center cut out - the pieces either side kept."""
    out = list(segs)
    for c in centers:
        nxt: list[tuple[Pt, Pt]] = []
        for a, b in out:
            dx, dy = b[0] - a[0], b[1] - a[1]
            n2 = dx * dx + dy * dy
            t = ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / n2 if n2 else 0.0
            px, py = a[0] + dx * t, a[1] + dy * t
            d2 = (c[0] - px) ** 2 + (c[1] - py) ** 2
            if not n2 or d2 >= half * half:
                nxt.append((a, b))
                continue
            w = math.sqrt(half * half - d2) / math.sqrt(n2)
            t0, t1 = t - w, t + w
            if t0 > 0.0:
                nxt.append((a, (a[0] + dx * min(t0, 1.0), a[1] + dy * min(t0, 1.0))))
            if t1 < 1.0:
                nxt.append(((a[0] + dx * max(t1, 0.0), a[1] + dy * max(t1, 0.0)), b))
        out = nxt
    return out


def drawn_water_segs(s: Settlement) -> list[tuple[Pt, Pt]]:
    """Every DRAWN watercourse on the map, as segments - channels AND streams.

    THE STREAMS WERE MISSING FROM EVERY WAY-VS-WATER TEST, and that is the whole reason this helper
    exists rather than the inline `drawn_channels` comprehension it replaces. `drawn_channels` holds
    the irrigation net; `M["streams"]` holds the feed brook and any natural course, and nothing in
    this module ever looked at it. So `shallow_crossing` - which exists, is correct, and is wired
    into `path_violations` - simply never saw the brook: on cohort seed 47 a connector crossed a
    7 px stream at 17 degrees, and `bridges_span_their_water` failed the deck it produced, with the
    guard that was written for exactly that case sitting one list away.

    Same family as this engine's recurring defect - a guard keyed on the wrong input measures
    something other than what it protects. `trades.py` already reads both records together; this is
    that pattern, applied where the ways are laid."""
    segs = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    return segs + stream_segs(s)  # ONE definition of what a stream is, shared with the deck-needing subset


def path_violations(path: Poly, avoid: Sequence[Poly], pond: tuple[float, float, float, float] | None, brook: Sequence[tuple[Pt, Pt]], waters: Sequence[tuple[Pt, Pt]] = ()) -> int:
    """How many segments of a drawn way foul the crop, the pond or the drain brook (0 = clear).

    A COUNT rather than a boolean, so a caller with no clean option can still take the least-bad one.

    The pond and the brook are avoided outright rather than bridged: a way meeting water at a
    shallow angle needs a far longer deck than a square crossing, and `bridges_span_their_water`
    measures the deck the engine actually drew. Going around removes the crossing entirely, which
    is also what a real track does - you ford a ditch where it is narrow and square.

    Research:
        pond kept off - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); 80 ft past the pond's larger half-axis
        drain brook never crossed - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the lanes among the houses cross a ditch where their line takes them, a crossing landing on cultivated ground, wet or dry - the drain brook is never crossed, a departure the code keeps until feature 417 T32; avoided outright, not bridged
        off the crop - research/questions/0081-village-lanes.drawing.html: no segment through an avoid polygon
        square over water - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: no crossing under
            42 degrees
        no deck on crop - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the lanes among the houses cross a ditch where their line takes them, a crossing landing on cultivated ground, wet or dry - a deck landing on crop is refused, a departure the code keeps until feature 417 T32; a crossing within 14 ft of a crop polygon fouls
        two decks too close - CONVENTION: crossings under 46 ft apart counted, decks drawn over each other"""
    bad = 0
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        if (
            (pond is not None and crosses_disc(a, b, (pond[0], pond[1]), max(pond[2], pond[3]) + 80.0))
            or any(segments_cross(a, b, p, q) for p, q in brook)
            or any(crosses_poly(a, b, poly) for poly in avoid)
            or any(shallow_crossing(a, b, p, q) for p, q in waters)
            or any(crossing_lands_on_crop(a, b, p, q, avoid) for p, q in waters)
        ):
            bad += 1
    # ...and a way may not bridge TWICE within a deck's length. `s.bridges()` decks every crossing
    # it finds, so a way cutting two ditches a few tens of px apart gets two decks drawn on top of
    # each other - which `features_do_not_overlap` reads as a ('bridges', 'bridges') pair, and which
    # is a drawing error rather than a siting one. Crossing further along, where the ditches have
    # separated, is what a track does anyway.
    hits = [
        x for i in range(len(path) - 1) for p, q in waters if segments_cross(path[i], path[i + 1], p, q) and (x := seg_intersect(path[i], path[i + 1], p, q)) is not None
    ]  # the segments must MEET: `seg_intersect` alone answers for the lines (feature 261)
    bad += pairs_within(hits, 46.0)  # the same pairs the every-pair form counted (170 million `hypot` on a polder - feature 138), by a sweep
    return bad


class PathChecker:
    """`path_violations` for many candidate paths against the SAME water, crop and pond, with that geometry indexed
    ONCE (feature 276, FR-005). The stage asked `path_violations` 176 times per roll and each call walked every brook
    segment, every avoid polygon and every water segment for every segment of the candidate: 0.966 s of Inashiro's
    1.308 s track stage (specs/276 research R4).

    THE INDEX PRUNES, THE SAME TESTS DECIDE. Two segments can cross only if their boxes overlap, and a path segment
    can enter or lie inside a polygon only if its box overlaps the polygon's - so asking the grid for the items whose
    boxes meet each path segment's box drops nothing a test could have counted. `violations` then runs
    `path_violations`' own per-segment tests on those items, and `path_violations` stays as the oracle a test compares
    this with on real candidate paths."""

    __slots__ = ("avoid", "brook", "pond", "waters")

    def __init__(self, avoid: Sequence[Poly], pond: tuple[float, float, float, float] | None, brook: Sequence[tuple[Pt, Pt]], waters: Sequence[tuple[Pt, Pt]] = ()) -> None:
        self.pond = pond
        self.avoid = PointGrid()
        self.avoid.extend([(poly, min(p[0] for p in poly), min(p[1] for p in poly), max(p[0] for p in poly), max(p[1] for p in poly)) for poly in avoid if len(poly) >= 3])
        self.brook = _seg_grid(brook)
        self.waters = _seg_grid(waters)

    def violations(self, path: Poly) -> int:
        """`path_violations` for one path, asked of the indexed geometry.

        Research:
            pond kept off - GUESS: searched, the record silent (feature 417 T29 pass A1, 2026-10-25); 80 ft past the pond's larger half-axis
            drain brook never crossed - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the lanes among the houses cross a ditch where their line takes them, a crossing landing on cultivated ground, wet or dry - the drain brook is never crossed, a departure the code keeps until feature 417 T32; avoided outright, not bridged
            off the crop - research/questions/0081-village-lanes.drawing.html: no segment through an avoid polygon
            square over water - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: no crossing
                under 42 degrees
            no deck on crop - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the lanes among the houses cross a ditch where their line takes them, a crossing landing on cultivated ground, wet or dry - a deck landing on crop is refused, a departure the code keeps until feature 417 T32; a crossing within 14 ft of a crop fouls
            two decks too close - CONVENTION: crossings under 46 ft apart counted
        """
        bad = 0
        hits: list[Pt] = []
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            box = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            brook = _meeting(self.brook, box)
            waters = _meeting(self.waters, box)
            avoid = _meeting(self.avoid, box)
            # the crop-landing test reads EVERY avoid polygon at the crossing point, which lies on this segment - so
            # the polygons whose boxes meet the segment's box are every polygon that point could be in or near (pad 14)
            landing = _meeting(self.avoid, (box[0] - 14.0, box[1] - 14.0, box[2] + 14.0, box[3] + 14.0))
            if (
                (self.pond is not None and crosses_disc(a, b, (self.pond[0], self.pond[1]), max(self.pond[2], self.pond[3]) + 80.0))
                or any(seg_intersect(a, b, p, q) is not None for p, q in brook)
                or any(crosses_poly(a, b, poly) for poly in avoid)
                or any(shallow_crossing(a, b, p, q) for p, q in waters)
                or any(crossing_lands_on_crop(a, b, p, q, landing) for p, q in waters)
            ):
                bad += 1
            hits += [x for p, q in waters if (x := seg_intersect(a, b, p, q)) is not None]
        return bad + pairs_within(hits, 46.0)


def _seg_grid(segs: Sequence[tuple[Pt, Pt]]) -> PointGrid:
    grid = PointGrid()
    grid.extend([((p, q), min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])) for p, q in segs])
    return grid


def _meeting(grid: PointGrid, box: tuple[float, float, float, float]) -> list[Any]:
    """The payload of every item of `grid` whose box meets `box`, once each. Order is not kept, and nothing needs it:
    every caller asks `any(...)` or counts crossing pairs."""
    x0, y0, x1, y1 = box
    seen: set[int] = set()
    out = []
    for it in grid.near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2):
        if id(it) in seen or it[-4] > x1 or it[-2] < x0 or it[-3] > y1 or it[-1] < y0:
            continue
        seen.add(id(it))
        out.append(it[0])
    return out


def crossing_lands_on_crop(a: Pt, b: Pt, p: Pt, q: Pt, crops: Sequence[Poly], pad: float = 14.0) -> bool:
    """Does the way a->b meet the watercourse p->q at a point standing on cropland?

    A crossing gets a DECK, and a deck laid on a hem plot is a bridge across the barley
    (`features_do_not_overlap` reports it as a dry_plots/bridges pair). The way is free to cross the
    same ditch a little further along where the crop stops - which is where the bund is anyway.

    Research: no deck on crop - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: the lanes among the houses cross a ditch where their line takes them, a crossing landing on cultivated ground, wet or dry - a deck landing on crop is refused, a departure the code keeps until feature 417 T32; within 14 ft of a dry plot"""
    hit = seg_intersect(a, b, p, q)
    if hit is None:
        return False
    return any(point_in_poly(hit[0], hit[1], list(c)) or min(seg_dist(hit[0], hit[1], c[i], c[(i + 1) % len(c)]) for i in range(len(c))) < pad for c in crops)


def shallow_crossing(a: Pt, b: Pt, p: Pt, q: Pt, limit_deg: float = 42.0) -> bool:
    """Does the way a->b cross the watercourse p->q at a SHALLOW angle?

    A way is allowed to cross an irrigation ditch - that is what a plank or a small timber bridge is
    for, and forbidding it outright would cut the field spur off from the field. What it may not do
    is cross at a slant: an oblique crossing needs a deck of (width + deck_w x |cos|) / sin plus a
    landing each side, so `bridges_span_their_water` fails it with an abutment standing in the
    water. Steering the way to meet the ditch square is the fix a farmer would recognize.

    Research: square over water - research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: under 42 deg fouls"""
    if seg_intersect(a, b, p, q) is None:
        return False
    ux, uy = unit(b[0] - a[0], b[1] - a[1])
    vx, vy = unit(q[0] - p[0], q[1] - p[1])
    return abs(math.degrees(math.asin(max(-1.0, min(1.0, ux * vy - uy * vx))))) < limit_deg


# ---- WHICH HOUSES THE LANE NETWORK ACTUALLY SERVES (feature 166) --------------------------------
# Lifted out of the retired `farmhouses_reach_a_way` gate check, whose body this is. The generator's
# re-roll ladder used to obtain this by running the whole battery and PARSING its printed output; it
# now asks here.
#
# LIFTED, NOT RE-DERIVED, and that distinction is the whole reason this code looks like the check
# rather than like its neighbors. `driver.py` records what happened the last time someone wrote a
# reach measure from scratch: it "was wrong on five of six seeds... it over-counted and never read
# zero", so anything steered by it was steered by noise.
#
# The join itself, `lanes_share_tread`, lives in `geom` (feature 417 T06): every network test asks the one predicate.


class NetworkMemo:
    """Each pair of lanes' answer to the one join (`geom.lanes_share_tread`), KEPT by the two lanes' points (feature 417 T53):
    the one network is asked again and again as the web is laid (67 asks a 40-household roll on seed 39), while between two asks
    a lane or two is appended, edited or dropped (764 asks on the 48-seed cohort and pinned rows: 603 after appends only, 123
    after an edit or a drop, measured 2026-10-27), so an ask judges only the pairs a new or changed lane is in, every other pair's
    answer the one already given; the union-find over the answers is rebuilt each ask from the boxes alone. Its components are
    `geom._components`' - a test holds the two equal.

    Research: plumbing - NONE: the one network (`served_lanes`) asked of what changed"""

    KEEP = 200_000
    """Pairs kept before the memo starts over (a roll's web is tens of lanes; this bounds a long-lived process's memory)."""

    def __init__(self) -> None:
        self.join: float | None = None
        self.pairs: dict[tuple[tuple[Pt, ...], tuple[Pt, ...]], bool] = {}
        self.boxes: dict[tuple[Pt, ...], tuple[float, float, float, float]] = {}

    def labels(self, ways: Sequence[Poly], join: float) -> list[int]:
        """Each way's component root under the one join at `join`, each pair's answer kept by its two ways' points."""
        if join != self.join or len(self.pairs) > self.KEEP:
            self.join, self.pairs, self.boxes = join, {}, {}
        keys = [tuple(w) for w in ways]
        boxes: list[tuple[float, float, float, float] | None] = []
        for k in keys:
            if len(k) < 2:
                boxes.append(None)
            elif k in self.boxes:
                boxes.append(self.boxes[k])
            else:
                b = self.boxes[k] = (min(v[0] for v in k), min(v[1] for v in k), max(v[0] for v in k), max(v[1] for v in k))
                boxes.append(b)
        par = list(range(len(keys)))

        def find(i: int) -> int:
            while par[i] != i:
                par[i] = par[par[i]]
                i = par[i]
            return i

        pairs = self.pairs
        for i in range(len(keys)):
            bi = boxes[i]
            if bi is None:
                continue
            for j in range(i + 1, len(keys)):
                bj = boxes[j]
                if bj is None or bj[0] - bi[2] > join or bi[0] - bj[2] > join or bj[1] - bi[3] > join or bi[1] - bj[3] > join:
                    continue
                if find(i) == find(j):
                    continue
                key = (keys[i], keys[j])
                if key in pairs:
                    met = pairs[key]
                else:
                    met = pairs[key] = lanes_share_tread(ways[i], ways[j], join)
                if met:
                    par[find(i)] = find(j)
        return [find(i) for i in range(len(keys))]


_NETWORK = NetworkMemo()


def served_lanes(lanes: Sequence[Mapping[str, Any]], join: float = _TOUCH_GAP) -> set[int]:
    """The lanes of the CONNECTED network (`served_network`'s), by index: the component grown from the connector if one is
    drawn, else from the longest lane; empty where no lane is drawn.

    Research: one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: grown from the connector"""
    ways = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in lanes]
    seed = next((i for i, ln in enumerate(lanes) if ln.get("connector")), None)
    if seed is None and ways:
        seed = max(range(len(ways)), key=lambda i: sum(math.dist(a, b) for a, b in zip(ways[i], ways[i][1:], strict=False)))
    if seed is None:
        return set()
    labels = _NETWORK.labels(ways, join)
    return {i for i, lb in enumerate(labels) if lb == labels[seed]}


def served_network(lanes: Sequence[Mapping[str, Any]], join: float = _TOUCH_GAP) -> list[tuple[Pt, Pt]]:
    """The segments of the CONNECTED network - the component containing the settlement's link to the world.

    THE NETWORK, NOT ANY LINE ON THE GROUND. The rule this serves is that every house in a nucleated
    cluster is reached by the INTERCONNECTED system of lanes, so a house served only by an isolated stub
    is not served. The component is grown from the connector if one is drawn, else from the longest lane;
    a check satisfiable by an island rewards drawing an island.

    Research: one network - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: grown from the connector"""
    main = served_lanes(lanes, join)
    ways = [[(float(x), float(y)) for x, y in (lanes[i].get("pts") or [])] for i in sorted(main)]
    return [(a, b) for w in ways for a, b in zip(w, w[1:], strict=False)]


def unreached_houses(M: Mapping[str, Any], reach: float = WEB_REACH_FT, near: Callable[[float, float], float] | None = None) -> list[tuple[int, int, int]]:
    """(x, y, distance) for every farmhouse the connected lane network does not reach. [] when the rule
    does not apply to this map. `near`, where the caller keeps it (`knots.WebMemo`), answers a house center's distance to
    the network (`served_network`'s segments, a network of at least one) in its place - the same nearest segment.

    FORM-CONDITIONAL, NOT WAIVED, and the condition is carried verbatim from the check. The rule's own
    justification is about ONE form - every house in the NUCLEATED village is reached by the lane network -
    and a DISPERSED hamlet has no internal network by definition, so the rule is not about it. A waiver
    would have been the wrong tool: a waiver says "this map breaks a rule that is true of it"; a dispersed
    hamlet does not break this rule, the rule does not apply. Defaults to nucleated so a map that declares
    no form keeps its old treatment.

    Research:
        every farmhouse served - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: within 100 ft of the network
        dispersed hamlet exempt - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: no
            lanes among its farms"""
    meta = M.get("meta") or {}
    if not meta.get("generated_by") or meta.get("settlement_form", "nucleated") == "dispersed":
        return []
    if near is None:
        segs = served_network(M.get("lanes") or [])
        if not segs:
            return []
        near = lambda cx, cy: min(seg_dist(cx, cy, a, b) for a, b in segs)  # noqa: E731
    far: dict[tuple[int, int], tuple[int, int, int]] = {}
    for h in M.get("houses") or []:
        cx, cy = float(h["x"]), float(h["y"])  # x, y ARE the center here - the manifest's convention
        d = near(cx, cy)
        if d > reach:
            far[(round(cx), round(cy))] = (round(cx), round(cy), round(d))
    # ...AND A HOUSEHOLD REACHED ACROSS A NEIGHBOR'S YARD IS REACHED WHERE ITS NEIGHBOR IS (feature 317, `rolling/passage.py`): the
    # custom of passage over a neighbor's land - so it is asked of the chain, shallowest first, never of a lane of its own
    across = sorted((h for h in M.get("houses") or [] if h.get("reached_across")), key=lambda h: int(h.get("passage_depth") or 1))
    for h in across:
        me, nb = (round(float(h["x"])), round(float(h["y"]))), (round(float(h["reached_across"][0])), round(float(h["reached_across"][1])))
        if me in far and nb not in far:
            del far[me]
    return list(far.values())


FORD_SQUARE_TOL_DEG = 10.0
"""A way that crosses the brook more than this far off square is squared at the crossing (`square_crossings`). The ford
gap lets a string-pulled way through it at up to about 40 degrees off square, and the deck takes the angle of the way it
carries - Kashikawa drew a plank 52 degrees off square (settlement-review, feature 261). 10 degrees is a map drawing
convention: square to the eye, and small enough that a gently angled approach is left as the router drew it.

Research: square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: within 10 deg"""


def square_crossings(pts: Sequence[Pt], brook: Sequence[Pt], half: float) -> list[Pt]:
    """`pts` with every crossing of `brook` that is more than `FORD_SQUARE_TOL_DEG` off square replaced by a leg `2 *
    (half + `SQUARE_LEG_PAD`)` long along the brook's normal at the crossing, so the way - and the deck laid on it - crosses
    square.

    AN ELBOW IN THE WATER IS TAKEN OUT FIRST (settlement-review of Kashikawa, feature 261): a lane that bent 3 ft inside the
    brook crossed on a segment too short to square, and its plank took the angle of the leg after the bend - 44 degrees off
    square. An interior vertex within `half` of the brook is dropped, so the crossing lies on one segment that can hold
    the square leg.

    TOTAL (feature 287, ways W11): every oblique crossing on a segment is squared, not the first alone, and a crossing too
    near the lane's own END to hold the leg is squared too - the end moves onto the leg rather than the crossing being
    "left as drawn" oblique (the elbow pass has already taken out every INTERIOR vertex that near the water, so only an end
    can be). The leg reaches `SQUARE_LEG_PAD` past `half` each side, so its own points stand clear of the elbow pass and
    squaring a squared lane changes nothing: the web's last pass (`settle_the_web`) runs this until a round is still.

    Research: square brook crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    if len(pts) > 2 and len(brook) > 1:
        inner = pts[1:-1]
        far = seg_dists(inner, list(zip(brook, brook[1:], strict=False))).min(axis=1) > half if inner else []
        pts = [pts[0], *(p for p, f in zip(inner, far, strict=True) if f), pts[-1]]
    leg = half + SQUARE_LEG_PAD
    out: list[Pt] = [pts[0]] if pts else []
    for k, (a, b) in enumerate(zip(pts, pts[1:], strict=False)):
        seg_len = math.dist(a, b)
        legs: list[tuple[float, Pt, Pt]] = []
        for c, d in zip(brook, brook[1:], strict=False):
            if seg_len == 0.0 or math.dist(c, d) == 0.0 or not segments_cross(a, b, c, d):
                continue
            x = seg_intersect(a, b, c, d)  # `seg_intersect` answers for the LINES; `segments_cross` said the segments meet
            if x is None:  # pragma: no cover - segments that cross are not parallel
                continue
            tx, ty = (d[0] - c[0]) / math.dist(c, d), (d[1] - c[1]) / math.dist(c, d)
            nx, ny = -ty, tx
            ux, uy = (b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len
            dot = ux * nx + uy * ny
            if dot < 0:
                nx, ny, dot = -nx, -ny, -dot
            if math.degrees(math.acos(min(1.0, dot))) <= FORD_SQUARE_TOL_DEG:
                continue
            legs.append((math.dist(a, x), (x[0] - nx * leg, x[1] - ny * leg), (x[0] + nx * leg, x[1] + ny * leg)))
        legs.sort(key=lambda t: t[0])
        for n, (along, p0, p1) in enumerate(legs):
            if k == 0 and n == 0 and along <= leg:
                out[-1] = p0  # the lane STARTS too near the water to hold the leg: it starts on the leg instead
            else:
                out.append(p0)
            out.append(p1)
        if legs and k == len(pts) - 2 and seg_len - legs[-1][0] <= leg:
            continue  # ...and it ENDS too near: it ends on the leg
        out.append(b)
    return out


SQUARE_LEG_PAD = 1.0
"""How far past `half` the square leg reaches each side of the water, in feet - enough that the leg's own points stand
outside the elbow pass's reach, so the squaring is idempotent (a map drawing convention)."""


def track_ends_off_the_web(M: Mapping[str, Any]) -> list[tuple[int, int, float]]:
    """(lane index, end, feet off) for every TRACK OUT whose inner end - the end nearer the other ways - stands more than
    `_TOUCH_GAP` (the law's `JOIN_TOL`) from every one of them: a track that stops short of the ways it serves. A
    FINISHED-MAP check, asked by the cohort only (`tools/cohort_audit.py`) and never by the settle (constitution XIX; feature
    417 D27): its placer is feature 417 T27's. The other end is the track's way out and is not asked - read by distance, not
    by the canvas, because the finished manifest's frame is cropped about the content and its `W` / `H` need not bound the
    lanes (the first form, asking every end inside `W` x `H`, named the way-out end of 18 of the 54 landing seeds). ONLY A
    MAP WITH A WEB IS ASKED - a lane besides the track and the field spur: a dispersed hamlet lays none, and its track ends
    among the farms with no way to meet (every dispersed seed of the 54, seed 5's 154 ft from the nearest house; whether
    that is open country is the GM's, feature 417 D27).

    Research:
        the track meets the lanes - research/questions/0081-village-lanes.drawing.html: never stops in open country, its inner
            end on the way it joins"""
    lanes = M.get("lanes") or []
    ways = [[(float(x), float(y)) for x, y in ln.get("pts") or []] for ln in lanes]
    web = any(not (ln.get("connector") or ln.get("spur")) for ln in lanes)
    out = []
    for i, ln in enumerate(lanes):
        p = ways[i]
        segs = [sg for k, o in enumerate(ways) if k != i for sg in zip(o, o[1:], strict=False)]
        if not ln.get("connector") or len(p) < 2 or not segs or not web:
            continue
        d, e = min((min(seg_dist(p[e][0], p[e][1], a, b) for a, b in segs), e) for e in (0, -1))
        if d > _TOUCH_GAP:
            out.append((i, e, round(d, 1)))
    return out
