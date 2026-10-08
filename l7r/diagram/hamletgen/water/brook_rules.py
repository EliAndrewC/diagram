"""THE BROOK'S RULES, one predicate each (feature 287, M1, water:W01-W11) - lifted out of the pool and gate tests, read by the
brook's placer (`brook.py`, `feed_brook`), by the sink's route search (`sink.py`) and by the tests alike, so a rule a
placer decides and the rule a test asserts are one function. Split from `brook.py` when the placer's repair took that
file past the 1,000-line bar (constitution X clause 13). See `CLAUDE.md` in this directory.

Research: course measurement - NONE: turns, chords, distances and view bounds read off the drawn course; each rule is claimed on its own unit
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import point_in_poly

from ..consts import BROOK_FRAME_MARGIN, BROOK_SKIRT, BROOK_WANDER_STEP, Poly, Pt
from ..plan import SitePlan


def turn_deg(p: Pt, q: Pt, r: Pt) -> float:
    """How far the course p -> q -> r turns at `q`, degrees (0 straight on, 180 straight back); 0 where a leg has no
    length, since a vertex on top of its neighbor turns nothing. The one reading of a turn: `max_turn_deg`, `unfold` and
    the pool test all ask it (feature 287, water:W01)."""
    ax, ay, bx, by = q[0] - p[0], q[1] - p[1], r[0] - q[0], r[1] - q[1]
    na, nb = math.hypot(ax, ay), math.hypot(bx, by)
    return math.degrees(math.acos(max(-1.0, min(1.0, (ax * bx + ay * by) / (na * nb))))) if na and nb else 0.0


def max_turn_deg(course: Sequence[Pt]) -> float:
    """The sharpest turn anywhere on `course`, degrees - held at or under `BROOK_MAX_TURN_DEG` on the drawn course
    (water:W01, the retired `test_no_brook_folds_back_on_itself`)."""
    return max((turn_deg(p, q, r) for p, q, r in zip(course, course[1:], course[2:], strict=False)), default=0.0)


# ---- THE BROOK'S RULES, one predicate each (feature 287, M1): the placer below judges its candidate with these, and the
# pool tests read the same functions. Every one is measured on the DRAWN course, `finished_course`.

LEVEL_NEAR_FT = 80.0  # water:W02 - a stretch this close to the view's edge ...
"""Research: level run near the frame - CONVENTION: within 80 ft of the view's edge, a line ruled along the frame reads as a mistake (GM 2026-08-26)"""
LEVEL_TOL_FT = 4.0  # ... that holds one coordinate within this ...
"""Research: level run tolerance - CONVENTION: a coordinate held within 4 ft"""
LEVEL_MAX_RUN_FT = 150.0  # ... for longer than this runs ruled along the frame (the GM on Sawada, 2026-08-26)
"""Research: level run length - CONVENTION: over 150 ft along the frame is refused"""
RULED_TOL_FT = 3.1  # water:W03 - a straight run: every vertex within this of its chord ...
"""Research: straight run tolerance - UNRESEARCHED: every vertex within 3.1 ft of its chord"""
RULED_SHARE = 0.4  # ... may cover at most this share of the brook's length on the page ...
"""Research: straight run share - UNRESEARCHED: at most 0.4 of the brook's length in view"""
RULED_MIN_LEN_FT = 300.0  # ... once that length is at least this (settlement-review of Sawada, round 0ae309f0)
"""Research: straight run floor - UNRESEARCHED: the share rule applies from 300 ft of brook in view"""
AXIS_EPS_DEG = 1.6  # water:W04 - a segment of a wander stride or more this near a screen axis is a ruled line
"""Research: screen-axis segment - CONVENTION: a segment within 1.6 deg of a screen axis reads as ruled"""
BROOK_DRAWN_W = 7.0  # the width `draw_comb_field` draws a hamlet's brook at (`settlement/fields/comb.py`, `stream(width=7)`)
"""Research: brook width - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: 7 ft, mirrored from `draw_comb_field`"""
CROSSING_END_TOL = BROOK_DRAWN_W / 2  # water:W08 - a joiner whose end lies inside the brook's drawn width meets it at a confluence
"""Research: a joiner meets the water - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: "a meeting is a junction when either channel's end lies inside the other's drawn width" (it was a flat 13 px, feature 328 wave 42)"""
# THE ROOM A LEVEL-RUN BEND NEEDS (water:W02): a station held against the frame box still has the skirt's floor 10 px
# inside it, so a bend of the level tolerance plus a foot either way fits between the two. Asserted at import: a consts
# change that took the room away fails here, not on a map.
assert BROOK_FRAME_MARGIN - BROOK_SKIRT >= 2 * (LEVEL_TOL_FT + 1.0), "the frame box leaves the brook no room to bend off a level run"


def level_runs_along_frame(course: Sequence[Pt], view: Sequence[float], near: float = LEVEL_NEAR_FT, tol: float = LEVEL_TOL_FT, max_run: float = LEVEL_MAX_RUN_FT) -> list[tuple[int, int, int, float]]:
    """Every stretch of `course` within `near` of the view's (x, y, w, h) edge that holds one coordinate within `tol` for
    more than `max_run` ft - (axis, first vertex, last vertex, length) - the test's loop, lifted (water:W02). The placer
    asks it of the whole canvas with `near` infinite, a superset of every view the crop can choose.
    Research: level run along the frame - CONVENTION: the W02 rule, a stretch near the view's edge holding one coordinate
    """
    x0, y0, w, h = (float(v) for v in view)
    runs = []
    for i in range(len(course)):
        for axis, lo, hi in ((0, x0, x0 + w), (1, y0, y0 + h)):
            if min(abs(course[i][axis] - lo), abs(course[i][axis] - hi)) > near:
                continue
            j = i
            while j + 1 < len(course) and abs(course[j + 1][axis] - course[i][axis]) <= tol:
                j += 1
            run = sum(math.dist(course[k], course[k + 1]) for k in range(i, j))
            if run > max_run:
                runs.append((axis, i, j, run))
    return runs


def _clip_arcs(arcs: list[tuple[float, float]], c: float, half: float) -> list[tuple[float, float]]:
    """`arcs` (bearing intervals, radians, a line's bearing taken mod pi) cut to within `half` of `c` mod pi."""
    out = []
    for lo, hi in arcs:
        for k in (-2, -1, 0, 1, 2):
            a, b = max(lo, c + k * math.pi - half), min(hi, c + k * math.pi + half)
            if a <= b:
                out.append((a, b))
    return out


def straightest_run(pts: Sequence[Pt], tol: float) -> float:
    """The longest chord between two vertices of `pts` (at least one vertex apart) with every vertex between within `tol`
    of its line - the pool test's `_straightest`, lifted (water:W03) and made quadratic: from each start, the bearings a
    chord may take narrow with every vertex passed (a vertex `r` out allows those within asin(tol / r) of its own), and
    once none is left no longer chord from that start can qualify.
    Research: straight run - UNRESEARCHED: the W03 chord a natural brook is held off
    """
    return straightest_chord(pts, tol)[0]


def straightest_chord(pts: Sequence[Pt], tol: float) -> tuple[float, int, int]:
    """`straightest_run` with the chord's two vertex indices - what the placer's repair bends at the middle of.
    Research: straight run - UNRESEARCHED: the W03 chord a natural brook is held off
    """
    best, at = 0.0, (0, 0)
    for i, (ax, ay) in enumerate(pts):
        arcs: list[tuple[float, float]] | None = None  # None: every bearing is still open
        for j in range(i + 1, len(pts)):
            qx, qy = pts[j][0] - ax, pts[j][1] - ay
            r = math.hypot(qx, qy)
            phi = math.atan2(qy, qx)
            if j >= i + 2 and r > best and (arcs is None or any(lo <= phi + k * math.pi <= hi for lo, hi in arcs for k in (-2, -1, 0, 1, 2))):
                best, at = r, (i, j)
            if r > tol:
                arcs = _clip_arcs(arcs if arcs is not None else [(phi - math.pi / 2, phi + math.pi / 2)], phi, math.asin(tol / r))
                if not arcs:
                    break
    return best, at[0], at[1]


def ruled_share_ok(course: Sequence[Pt], view: Sequence[float], tol: float = RULED_TOL_FT, share: float = RULED_SHARE, min_len: float = RULED_MIN_LEN_FT) -> bool:
    """No straight run covers more than `share` of the course's length inside the view, when that length is at least
    `min_len` - the pool test's whole body (water:W03).
    Research: straight run share - UNRESEARCHED: no straight run over RULED_SHARE of the brook in view
    """
    x0, y0, w, h = (float(v) for v in view)
    on = [p for p in course if x0 <= p[0] <= x0 + w and y0 <= p[1] <= y0 + h]
    length = sum(math.dist(a, b) for a, b in zip(on, on[1:], strict=False))
    return length < min_len or straightest_run(on, tol) <= share * length


def tap_index(course: Sequence[Pt], taps: Sequence[Pt]) -> int:
    """The vertex the head race leaves from - the one nearest a tap, found by position as the pool test finds it."""
    return min(range(len(course)), key=lambda k: min((math.dist(course[k], t) for t in taps), default=0.0))


def axis_segments(course: Sequence[Pt], taps: Sequence[Pt], eps: float = AXIS_EPS_DEG, min_len: float = BROOK_WANDER_STEP) -> list[int]:
    """The segments of `min_len` or more lying within `eps` degrees of a screen axis, the two leaving the tap excepted -
    the pool test's loop, lifted (water:W04, one of the five rules the GM named).
    Research: screen-axis segment - CONVENTION: the W04 rule, the tap run excepted
    """
    tap = tap_index(course, taps)
    bad = []
    for i, (a, b) in enumerate(zip(course, course[1:], strict=False)):
        if i in (tap, tap + 1) or math.dist(a, b) < min_len:
            continue
        deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0
        if min(deg, 90.0 - deg) < eps:
            bad.append(i)
    return bad


def course_enters(course: Sequence[Pt], rings: Sequence[Sequence[Pt]]) -> bool:
    """Does any interior vertex of `course` lie inside one of `rings` - a stream through a field (water:W06).
    Research: brook skirts the field - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: no interior vertex inside a field ring
    """
    return any(point_in_poly(p[0], p[1], list(r)) for r in rings if len(r) >= 3 for p in course[1:-1])


def ends_off_canvas(course: Sequence[Pt], W: float, H: float, ends: Sequence[int] = (0, -1)) -> bool:
    """Do the named ends of `course` lie off the (0, 0, W, H) canvas - an end declared off-map (water:W07).
    Research: both ends off the map - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the source upslope and the mouth below the fan off the canvas
    """
    return all(not (0.0 <= course[e][0] <= W and 0.0 <= course[e][1] <= H) for e in ends)


def _proper_cross(a0: Pt, a1: Pt, b0: Pt, b1: Pt) -> bool:
    """Do the two open segments properly cross (a shared end is a junction) - the junction test's own predicate."""

    def side(p: Pt, q: Pt, r: Pt) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    return ((side(a0, a1, b0) > 0) != (side(a0, a1, b1) > 0)) and ((side(b0, b1, a0) > 0) != (side(b0, b1, a1) > 0))


def _dist_to_course(p: Pt, course: Sequence[Pt]) -> float:
    """The distance from `p` to the polyline `course`."""
    best = math.inf
    for a, b in zip(course, course[1:], strict=False):
        vx, vy = b[0] - a[0], b[1] - a[1]
        L2 = vx * vx + vy * vy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2))
        best = min(best, math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy))
    return best


def crosses_mid_run(water: Sequence[Pt], joiner: Sequence[Pt], tol: float = CROSSING_END_TOL) -> bool:
    """Does `joiner` cross `water` away from a confluence - a crossing where neither end of the joiner stands within `tol`
    of the water (water:W08, the junction test's rule, lifted).
    Research: no crossing mid-run - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html: a ditch meets the brook only at a confluence, never across it
    """
    if len(joiner) < 2 or len(water) < 2 or min(_dist_to_course(e, water) for e in (joiner[0], joiner[-1])) < tol:
        return False
    return any(_proper_cross(j0, j1, w0, w1) for j0, j1 in zip(joiner, joiner[1:], strict=False) for w0, w1 in zip(water, water[1:], strict=False))


def monotone_down(course: Sequence[Pt], fall: Pt, slack: float = 0.01) -> bool:
    """Does every step of `course` run down the fall (or level) - the brook below its tap carrying the runoff on
    downhill (water:W11).
    Research: runs downhill - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every step below the tap runs down the fall
    """
    us = [p[0] * fall[0] + p[1] * fall[1] for p in course]
    return all(b >= a - slack for a, b in zip(us, us[1:], strict=False))


def bar_on_race(bar: Sequence[Pt], race: Sequence[Pt], race_w: float) -> float:
    """The area of the weir's bar lying on the head race's stroke, sq px - 0 where the bar keys into the bank clear of
    the mouth (water:W09; future-work "The weir's root lands on the head race's mouth": 17% of the bar lay on it).
    Research: weir root clear of the race - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the bar keys into the bank below the mouth, none of it on the race
    """
    from shapely.geometry import LineString, Polygon  # noqa: PLC0415 - bound on first use (plan: numpy/shapely lazily)

    if len(race) < 2 or len(bar) < 3:
        return 0.0
    return float(Polygon(bar).intersection(LineString(race).buffer(race_w / 2.0, cap_style="flat")).area)


def to_edge(p: Pt, d: Pt, W: float, H: float) -> float:
    """How far from `p` along the unit bearing `d` the (0, 0, W, H) canvas ends (0 where `p` is already past it)."""
    spans = [((W if d[0] > 0 else 0.0) - p[0]) / d[0]] if abs(d[0]) > 1e-9 else []
    spans += [((H if d[1] > 0 else 0.0) - p[1]) / d[1]] if abs(d[1]) > 1e-9 else []
    return max(0.0, min(spans)) if spans else 0.0


def reserved_box(course: Sequence[Pt], plan: SitePlan) -> tuple[float, float, float, float]:
    """(x0, y0, x1, y1): ground EVERY view the crop can choose contains, on the canvas (water:W02/W03, plan D5) - read
    from what the frame itself will read, so it is known when the brook is laid:

    - the paddies' visible box: the crop frames each field by its `vis_bbox`, the box of its plots (`crop_boxes`);
    - each station of `course` within `BROOK_FRAME_MARGIN` of the field and the dry hem, at the brook's half width -
      `hinterland.frame.brook_beside_the_field` reserves exactly those as content. The hem it reads is the hem DRAWN, and
      `_comb_draw_hem` drops a plot the brook's own band crosses (`hem_on_water`, the course with a bund's margin), so
      the plots it would drop are left out here by the same predicate.

    A view is a box, so it holds the box round them all."""
    from l7r.diagram.settlement.fields.comb import WetLines, hem_on_water  # noqa: PLC0415 - the settlement package imports late here

    net = plan.net or {}
    paddies = [list(p["poly"]) for p in net.get("plots") or []] or [list(plan.envelope)]
    xs, ys = [float(q[0]) for r in paddies for q in r], [float(q[1]) for r in paddies for q in r]
    wet = WetLines([([(float(x), float(y)) for x, y in course], 9.0 / 2 + 3.0)])  # filed once, asked per hem plot
    hem = [list(p["poly"]) for p in net.get("dry_plots") or [] if not hem_on_water(p["poly"], wet, None)]
    fx = [float(q[0]) for r in [list(plan.envelope), *hem] for q in r]
    fy = [float(q[1]) for r in [list(plan.envelope), *hem] for q in r]
    m, hw = BROOK_FRAME_MARGIN + 1.0, BROOK_DRAWN_W / 2.0
    for q in course:
        if min(fx) - m <= q[0] <= max(fx) + m and min(fy) - m <= q[1] <= max(fy) + m:
            xs += [q[0] - hw, q[0] + hw]
            ys += [q[1] - hw, q[1] + hw]
    return (max(0.0, min(xs)), max(0.0, min(ys)), min(float(plan.W), max(xs)), min(float(plan.H), max(ys)))


def ruled_excess(fin: Sequence[Pt], W: float, H: float, box: Sequence[float]) -> tuple[float, float, Pt, Pt]:
    """(straightest run on the canvas, the most it may be, its two ends) - water:W03's VIEW-INDEPENDENT bound (plan D5).

    The view is decided six stages after the brook, and the rule is a share of the brook's length IN it. So the placer
    asks a sufficient bound: the straightest run on the whole canvas at most `RULED_SHARE` of the larger of
    `RULED_MIN_LEN_FT` and the length inside `box` (`reserved_box`, which every view contains). Any view where the rule
    applies then holds at least that length, and no longer a straight run than the canvas has, so the test's inequality
    follows. Stricter than the test by design - the engine's standing convention for a placer."""
    on = [p for p in fin if 0.0 <= p[0] <= W and 0.0 <= p[1] <= H]
    inside = lambda q: box[0] <= q[0] <= box[2] and box[1] <= q[1] <= box[3]  # noqa: E731
    held = sum(math.dist(a, b) for a, b in zip(fin, fin[1:], strict=False) if inside(a) and inside(b))
    run, i, j = straightest_chord(on, RULED_TOL_FT)
    return run, RULED_SHARE * max(RULED_MIN_LEN_FT, held), on[i] if on else (0.0, 0.0), on[j] if on else (0.0, 0.0)


def level_runs_any_view(fin: Sequence[Pt], W: float, H: float, box: Sequence[float]) -> list[tuple[int, int, int, float]]:
    """water:W02 for EVERY view the crop can choose: `level_runs_along_frame` over the canvas with no nearness limit, kept
    where the run's first vertex could lie within `LEVEL_NEAR_FT` of some view's edge. A view holds `box` (`reserved_box`)
    and lies on the canvas, so its left edge is at or left of the box's; a vertex further than that inside the box can
    be near no view's edge. A superset of what any view's test reads, and no more than that."""
    return [r for r in level_runs_along_frame(fin, (0.0, 0.0, W, H), near=math.inf) if not (box[r[0]] + LEVEL_NEAR_FT < fin[r[1]][r[0]] < box[r[0] + 2] - LEVEL_NEAR_FT)]


def ditch_strokes(plan: SitePlan) -> list[Poly]:
    """Every ditch of the fitted net the brook must not cross mid-run (water:W08) - the head race included, whose mouth on
    the brook is its confluence and so exempt by the predicate itself."""
    return [[(float(x), float(y)) for x, y in c["pts"]] for c in (plan.net or {}).get("channels") or [] if len(c.get("pts") or ()) >= 2]


def without_straight_joins(fin: Sequence[Pt], joins: Sequence[Pt], tol: float, deg: float = 0.5) -> Poly:
    """`fin` less each confluence vertex (`joins`, matched within `tol`) that lies on a straight line between its neighbors - what the ruled rule
    (water:W03) reads. A confluence held mid-leg changes no stroke the map draws, but its vertex made a single straight leg,
    which the rule's chord test leaves alone, a three-vertex run it counts: on Kashikawa (feature 302) every meeting the drain
    could make with its brook read "ruled" while the brook itself, judged without the join, kept the rule."""
    out = [fin[0]] if fin else []
    for k in range(1, len(fin) - 1):
        p = fin[k]
        if any(math.dist(p, q) <= tol for q in joins):
            (ax, ay), (bx, by) = fin[k - 1], fin[k + 1]
            h1, h2 = math.atan2(p[1] - ay, p[0] - ax), math.atan2(by - p[1], bx - p[0])
            if abs((math.degrees(h2 - h1) + 180.0) % 360.0 - 180.0) < deg:
                continue
        out.append(p)
    return [*out, fin[-1]] if len(fin) >= 2 else list(fin)
