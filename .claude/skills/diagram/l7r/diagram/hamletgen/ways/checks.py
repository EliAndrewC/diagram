"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, seg_intersect, segments_cross
from l7r.diagram.settlement._geom.indexes import PointGrid
from l7r.diagram.sitegen.geom import crosses_disc, crosses_poly, unit

from ..clearance import pairs_within
from ..consts import (
    FORD_HALF,
    LANE_JOIN_FT,
    WEB_REACH_FT,
    Poly,
    Pt,
)


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
    `_bridge_collinear_breaks` does NOT: it hands its water to `_route`, which already refuses to
    cross a watercourse at any angle, so a veto there would be unreachable code.

    THE BROOK HAS CROSSINGS (feature 261): where `stage_ways` has opened fords (`s.brook_fords`), the stream's
    segments come back with a short gap at each, so the router may carry a way over the brook there - and only
    there, and only near square, because the gap is shorter than the corridor is deep. `bridges()` reads the
    UNgapped `M["streams"]` and decks every such crossing.

    THE COURSE AS FIRST DRAWN (feature 287, M2): the brook is rounded at the end of the water stages now, before the ways,
    and a way is still routed against its `stations` - the course before the rounding - because rounding the brook before
    the ways were routed moved every way its corners had shaped (`Settlement.round_stream`). The fords (`brook_fords`) and
    the crossing band (`set_crossing`) read the same unrounded course, `plan.brook`."""
    courses = [st.get("stations") or st.get("poly") or [] for st in s.M.get("streams", [])]
    segs = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for c in courses for a, b in zip(c, c[1:], strict=False)]
    return gap_segments(segs, getattr(s, "brook_fords", ()), FORD_HALF)


def brook_fords(brook: Sequence[Pt], spacing: float, bend_deg: float) -> list[Pt]:
    """Where the brook may be crossed: points every `spacing` along its course where it runs straight for the
    deck's length either side (the turn between the reaches `FORD_HALF` behind and ahead is under `bend_deg`),
    so a way crossing there crosses it square and the plank lands on both banks. A bend is skipped, not moved:
    the next site along is `spacing` further on."""
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


def ford_crossing(start: Pt, end: Pt, brook: Sequence[Pt], fords: Sequence[Pt], landing: float = 22.0) -> list[Pt]:
    """The two landings of a square crossing at the ford that makes start -> ford -> end shortest, ordered from the
    start's bank - or nothing, when the straight run from `start` to `end` does not cross the brook (or there is no
    ford). A landing stands `landing` px off the brook square to its local reach: past the 14 px the router keeps off
    water, and inside the ford's gap, so a path through the two lands on the deck `bridges()` puts there."""
    legs = list(zip(brook, brook[1:], strict=False))
    if not fords or not any(segments_cross(start, end, a, b) for a, b in legs):
        return []
    f = min(fords, key=lambda c: math.dist(start, c) + math.dist(c, end))
    a, b = min(legs, key=lambda ab: seg_dist(f[0], f[1], ab[0], ab[1]))
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
    is also what a real track does - you ford a ditch where it is narrow and square."""
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
    same ditch a little further along where the crop stops - which is where the bund is anyway."""
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
    water. Steering the way to meet the ditch square is the fix a farmer would recognize."""
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
# AND IT DOES NOT REUSE `_components`, WHICH IS THE NEAR-MISS THAT WOULD HAVE MOVED MAPS.
# `_components` joins two ways when an END of one comes within tolerance of the other's tread.
# This rule joins them when ANY VERTEX does. The stricter predicate yields a smaller network, so
# more houses read as unserved, so the ladder re-rolls maps it used to keep. Two connectivity
# helpers that look interchangeable and are not - the exact shape `dev/gate.md` collects under
# "MEASURE WHAT THE RULE MEASURES".


def lanes_share_tread(p: Poly, q: Poly, join: float = LANE_JOIN_FT) -> bool:
    """Do two drawn treads come within `join` anywhere - by ANY vertex of either against the other's run?

    Lifted from the check's own inner `_fw_touch` so it can be tested with two lists of tuples instead
    of a settlement (the project's standing rule on closures that are hard to reach)."""
    return any(seg_dist(v[0], v[1], a, b) <= join for v in p for a, b in zip(q, q[1:], strict=False)) or any(seg_dist(v[0], v[1], a, b) <= join for v in q for a, b in zip(p, p[1:], strict=False))


def served_network(lanes: Sequence[Mapping[str, Any]], join: float = LANE_JOIN_FT) -> list[tuple[Pt, Pt]]:
    """The segments of the CONNECTED network - the component containing the settlement's link to the world.

    THE NETWORK, NOT ANY LINE ON THE GROUND. The rule this serves is that every house in a nucleated
    cluster is reached by the INTERCONNECTED system of lanes, so a house served only by an isolated stub
    is not served. The component is grown from the connector if one is drawn, else from the longest lane;
    a check satisfiable by an island rewards drawing an island."""
    ways = [[(float(x), float(y)) for x, y in (ln.get("pts") or [])] for ln in lanes]
    seed = next((i for i, ln in enumerate(lanes) if ln.get("connector")), None)
    if seed is None and ways:
        seed = max(range(len(ways)), key=lambda i: sum(math.dist(a, b) for a, b in zip(ways[i], ways[i][1:], strict=False)))
    main = set() if seed is None else {seed}
    grew = True
    while grew:
        grew = False
        for i, p in enumerate(ways):
            if i in main or len(p) < 2:
                continue
            if any(lanes_share_tread(p, ways[j], join) for j in main if len(ways[j]) >= 2):
                main.add(i)
                grew = True
    return [(a, b) for i in sorted(main) for a, b in zip(ways[i], ways[i][1:], strict=False)]


def unreached_houses(M: Mapping[str, Any], reach: float = WEB_REACH_FT) -> list[tuple[int, int, int]]:
    """(x, y, distance) for every farmhouse the connected lane network does not reach. [] when the rule
    does not apply to this map.

    FORM-CONDITIONAL, NOT WAIVED, and the condition is carried verbatim from the check. The rule's own
    justification is about ONE form - every house in the NUCLEATED village is reached by the lane network -
    and a DISPERSED hamlet has no internal network by definition, so the rule is not about it. A waiver
    would have been the wrong tool: a waiver says "this map breaks a rule that is true of it"; a dispersed
    hamlet does not break this rule, the rule does not apply. Defaults to nucleated so a map that declares
    no form keeps its old treatment."""
    meta = M.get("meta") or {}
    if not meta.get("generated_by") or meta.get("settlement_form", "nucleated") == "dispersed":
        return []
    segs = served_network(M.get("lanes") or [])
    if not segs:
        return []
    far: list[tuple[int, int, int]] = []
    for h in M.get("houses") or []:
        cx, cy = float(h["x"]), float(h["y"])  # x, y ARE the center here - the manifest's convention
        d = min(seg_dist(cx, cy, a, b) for a, b in segs)
        if d > reach:
            far.append((round(cx), round(cy), round(d)))
    return far


FORD_SQUARE_TOL_DEG = 10.0
"""A way that crosses the brook more than this far off square is squared at the crossing (`square_crossings`). The ford
gap lets a string-pulled way through it at up to about 40 degrees off square, and the deck takes the angle of the way it
carries - Kashikawa drew a plank 52 degrees off square (settlement-review, feature 261). 10 degrees is a map drawing
convention: square to the eye, and small enough that a gently angled approach is left as the router drew it."""


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
    squaring a squared lane changes nothing: the web's last pass (`settle_the_web`) runs this until a round is still."""
    if len(pts) > 2 and len(brook) > 1:
        pts = [pts[0], *(p for p in pts[1:-1] if min(seg_dist(p[0], p[1], c, d) for c, d in zip(brook, brook[1:], strict=False)) > half), pts[-1]]
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
