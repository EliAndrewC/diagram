"""THE BROOK'S COURSE (feature 230) - the shape of the course below and beyond the tap, and the course as the map draws it.

Split from `brook.py` by feature 316 (constitution X clause 13); bodies verbatim, and `brook.py` re-exports every name:
the exit off the frame, the reflecting wander, the crop's cross-section, the frame bound, the unfold, the rounding with
the taps and confluences held, and the screen-axis backstop. Leaf helpers only - `brook.py`'s placer, repair and
judgment, which the tests patch, stay there.

Research: plumbing - NONE: every unit that decides something carries its own claims
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement._geom import fillet_polyline
from l7r.diagram.sitegen.geom import unit

from ..consts import BROOK_BEND_WIDTHS, BROOK_WANDER, BROOK_WANDER_STEP, Poly, Pt
from .brook_rules import BROOK_DRAWN_W, to_edge, turn_deg

EXIT_BEND_FRAC = 0.12  # an exit leg's midpoint bend, as a share of the leg ...
"""Research: exit leg bend - UNRESEARCHED: an exit leg still on the page bends aside at its middle by 0.12 of its length"""
EXIT_BEND_MAX_FT = 60.0  # ... at most this far aside
"""Research: exit bend cap - UNRESEARCHED: the exit leg's bend at most 60 ft aside"""


def exit_bend(start: tuple[float, float], heading: tuple[float, float], leg: float, side: float) -> tuple[float, float]:
    """The midpoint of an exit leg from `start` along `heading` for `leg` ft, set aside by `EXIT_BEND_FRAC` of the leg
    (at most `EXIT_BEND_MAX_FT`) on `side` (+1 or -1) - one gentle bend in a leg the page still shows (feature 261).

    Research: exit leg bend - UNRESEARCHED: one bend at the leg's middle, EXIT_BEND_FRAC of the leg and at most EXIT_BEND_MAX_FT aside
    """
    off = side * min(EXIT_BEND_MAX_FT, EXIT_BEND_FRAC * leg)
    return (start[0] + heading[0] * leg / 2 - heading[1] * off, start[1] + heading[1] * leg / 2 + heading[0] * off)


def exit_legs(out: Sequence[Pt], fall: Pt, W: float, H: float) -> list[Pt]:
    """The course's way OFF the frame from its last station `out[-1]`: four legs turning from the course's own heading onto
    the fall `fall`, each still on the page bent once at its middle, the last lengthened down the fall until the mouth is
    off the (0, 0, W, H) canvas (feature 287 wave 5, water:W07) - lifted out of `brook_skirt` so the mouth's guarantee is
    tested on plain inputs. Returns the points to append.

    Research:
        off-map mouth - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: the course runs on down the fall and its last leg is carried 60 past the canvas edge
        exit span - UNRESEARCHED: max(120, the distance to the edge down the fall) + 260
        turn onto the fall - UNRESEARCHED: four legs of 0.22-0.26 of the span, blending 0.3, 0.6, 0.85, 1.0 from the course's heading onto the fall, no wander
        exit leg bend - UNRESEARCHED: each leg starting on the page bent once at its middle, alternating sides (`exit_bend`)
    """
    dx, dy = fall
    lx, ly = out[-1]
    legs: list[Pt] = []
    edge = [((W if dx > 0 else 0.0) - lx) / dx if abs(dx) > 1e-6 else 1e9, ((H if dy > 0 else 0.0) - ly) / dy if abs(dy) > 1e-6 else 1e9]
    span = max(120.0, min(edge)) + 260.0
    # the heading the exit starts on is the course's own over its LAST FEW stations, and never one that has
    # stopped descending: a single segment's bearing can point back up the slope where the last station was held
    # against the frame bound, and the exit then folded the course back on itself (131 and 119 degrees, the last
    # two corners left on the pool)
    _back = out[max(0, len(out) - 4)]
    # the course's own heading, unless it has stopped going downhill - a tail that runs across the fall or back
    # up it has no heading worth keeping, and the exit takes the fall directly (one expression, so the fall case
    # is not a branch that only a particular crop shape can reach)
    _h = unit(lx - _back[0], ly - _back[1]) if len(out) > 1 else (dx, dy)
    heading = _h if _h[0] * dx + _h[1] * dy > 0.15 else (dx, dy)
    px_, py_ = lx, ly
    # NO WANDER IN THE EXIT, and the turn onto the fall spread over four legs. A lateral term on a leg
    # hundreds of feet long folded the course back on itself (129 degrees on one map, 113 on another, both in
    # the last four vertices), and the part that leaves the sheet is the one place a straight run costs nothing.
    for k, (f, blend) in enumerate(((0.22, 0.3), (0.26, 0.6), (0.26, 0.85), (0.26, 1.0))):
        hx, hy = unit(heading[0] * (1.0 - blend) + dx * blend, heading[1] * (1.0 - blend) + dy * blend)
        # ...BUT A LEG STILL ON THE PAGE BENDS AT ITS MIDDLE (settlement-review of Sawada, feature 261): the exit starts
        # where the frame would pin the course, and on a map where that is 940 ft inside the sheet the straight legs drew
        # 70% of the brook as a ruled line. One gentle bend per leg that starts in frame, alternating side, sized to the
        # leg (`exit_bend`) - a turn of about 27 degrees, where the long lateral terms that folded the course were 113-129
        if 0.0 <= px_ <= W and 0.0 <= py_ <= H:
            legs.append(exit_bend((px_, py_), (hx, hy), span * f, 1.0 if k % 2 == 0 else -1.0))
        px_, py_ = px_ + hx * span * f, py_ + hy * span * f
        legs.append((px_, py_))
    # ...AND THE MOUTH LEAVES THE CANVAS BY CONSTRUCTION (feature 287 wave 5, water:W07): `span` is measured along the fall
    # from the last station, but the legs run the blend of the course's heading and the fall, so a heading far across
    # the fall left the mouth on the sheet (cohort seed 48: the brook stopped 60 ft inside it). The last leg runs straight
    # down the fall (its blend is 1), so it is lengthened along itself past the edge - no new turn, no new vertex.
    if 0.0 <= px_ <= W and 0.0 <= py_ <= H:
        reach = to_edge((px_, py_), (dx, dy), W, H) + 60.0
        legs[-1] = (px_ + dx * reach, py_ + dy * reach)
    return legs


def _wander(rng: random.Random, stray: float, swing: int) -> tuple[float, int]:
    """One step of the brook's lateral walk: (how far outside the skirt floor, which way it is going).

    A REFLECTING walk with a floor on the step, not a clamped one. Clamped, the walk saturates at an end and
    stands still there - which draws exactly the ruled segment the wander exists to prevent, and a segment
    that stands still on a map whose fall is due south is a line at 90.000 degrees. Reflecting off the ends
    and stepping at least `BROOK_WANDER_STEP / 4` keeps every station's offset different from the last, so
    no two consecutive vertices can share a bearing and none can lie on an axis.

    Research: meander - UNRESEARCHED: a seeded reflecting walk across the fall between 0 and BROOK_WANDER (10 px), stepping BROOK_WANDER_STEP / 4 to BROOK_WANDER_STEP
    """
    step = rng.uniform(BROOK_WANDER_STEP / 4.0, BROOK_WANDER_STEP) * swing
    nxt = stray + step
    if not 0.0 <= nxt <= BROOK_WANDER:
        swing = -swing
        nxt = min(BROOK_WANDER, max(0.0, stray - step))
    return nxt, swing


def _crop_edge(segs: Sequence[tuple[Pt, Pt]], u: float, window: float, floor: float) -> float:
    """How far ACROSS the fall the cultivated ground reaches at this point down it - a cross-section, not a
    bounding box.

    Two cuts got this wrong before it, and both are the same mistake at different scales. Taking each ring's
    greatest width made the brook jump the fan's whole half-width the moment it left the tap, a 72 to 85 degree
    elbow that `settlement-review` read as a canal jog cut round the plots. Taking the greatest width of any
    ring lying ABREAST of the station was no better, because the field envelope is one ring lying abreast of
    every station: the brook was pushed out to the fan's shoulder for its whole length, 400 to 600 ft from
    ground it was supposed to be skirting at 34. A fan is narrow at its head and broad at its foot, and the
    course has to be able to see that. So every edge that CROSSES this station's line is cut there, and the
    vertices inside a window either side are taken as they stand - the window covering the reach to the next
    station, so nothing that sticks out between two stations is missed by both."""
    best = floor
    for (ua, va), (ub, vb) in segs:
        if abs(ua - u) <= window:
            best = max(best, va)
        if (ua - u) * (ub - u) <= 0 and ua != ub:
            best = max(best, va + (vb - va) * (u - ua) / (ub - ua))
    return best


def _v_within(u: float, floor: float, want: float, d: Pt, p: Pt, box: tuple[float, float, float, float]) -> float:
    """The largest offset at or below `want` that keeps the station inside `box`, never below `floor`.

    The station is `u * d + v * p`, so each side of the box is one linear bound on `v`; the tightest of the
    four caps it. The floor is the crop clearance and wins outright: a course held inside the picture at the
    price of running through the rice would be the wrong trade, and the two only disagree where the field
    itself reaches the box, which the margin is sized to prevent.

    Research:
        on the sheet - CONVENTION: the station's offset capped so it stays inside `box`, the field's bounds grown by BROOK_FRAME_MARGIN
        crop clearance wins - UNRESEARCHED: never below `floor`, the crop clearance, where the two disagree
    """
    hi = want
    for coord, lo_b, hi_b in ((0, box[0], box[2]), (1, box[1], box[3])):
        base, slope = u * d[coord], p[coord]
        if abs(slope) < 1e-9:
            continue
        a, b = (lo_b - base) / slope, (hi_b - base) / slope
        hi = min(hi, max(a, b))
    return max(floor, hi)


def unfold(course: Poly, limit_deg: float, hold: Sequence[Pt] = ()) -> Poly:
    """The course with every vertex that turns it more than `limit_deg` taken out, repeated until none does.

    A NATURAL BROOK DOES NOT DOUBLE BACK (feature 261, settlement-review of Sawada): where the last stations are held
    against the frame box and the corner-cutting pass re-clamps its points onto the same edge, the exit leaves from a
    point behind the one before it and the course folds - 123 degrees, 51 ft inside the sheet, drawn as an acute V. The
    exit block above already guards the heading it starts on; this holds the property itself on the finished course,
    whatever produced the fold. Dropping the vertex keeps the ends and the order of everything else.

    A HELD vertex (`hold` - the tap, feature 287 water:W01) is never the one dropped: where it is the fold, the free
    vertex before it goes instead (the approach's last wobble), else the one after it. A fold between two held vertices
    has nothing to drop and stays; the brook's placer judges the result and takes its next candidate.

    Research: no fold-back - UNRESEARCHED: every vertex turning past `limit_deg` (BROOK_MAX_TURN_DEG, 100 deg) dropped, a held tap never
    """
    out = list(course)
    held = {(float(x), float(y)) for x, y in hold}
    changed = True
    while changed and len(out) > 2:
        changed = False
        for i in range(1, len(out) - 1):
            if turn_deg(out[i - 1], out[i], out[i + 1]) <= limit_deg:
                continue
            k = next((j for j in (i, i - 1, i + 1) if 0 < j < len(out) - 1 and out[j] not in held), None)
            if k is not None:
                del out[k]
                changed = True
                break
    return out


def finished_course(course: Sequence[Pt], w: float, taps: Sequence[Pt] = ()) -> Poly:
    """The brook's course AS DRAWN: `course` with its bends rounded at `BROOK_BEND_WIDTHS` of its width `w`, each vertex
    within a foot of a tap in `taps` held where it is (feature 287, M2 - lifted out of `Settlement.round_stream`).

    A natural brook turns on a curve like every earthen channel (`fillet_polyline`; research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html; settlement-review of Sawada, feature 261: mitred corners of 27-47 degrees). A held vertex
    splits the course and each stretch is rounded between its own ends, so the head race still leaves the course at the
    tap where its offtake angle is measured. A function of the course, its width and the taps only, so the placer that
    judges a brook and the stage that draws it read ONE geometry; a course of two points has no corner and comes back
    as it is.

    Research:
        bends rounded - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: every corner filleted at BROOK_BEND_WIDTHS (2.5) of the drawn width
        tap not rounded - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a vertex at a tap is held, the offtake a junction and not a bend
    """
    pts = [(float(x), float(y)) for x, y in course]
    if len(pts) < 3:
        return pts
    hold = {min(range(len(pts)), key=lambda k, t=t: math.dist(pts[k], t)) for t in taps if min(math.dist(p, t) for p in pts) <= 1.0}
    out: Poly = []
    start = 0
    for k in [*sorted(k for k in hold if 0 < k < len(pts) - 1), len(pts) - 1]:
        part = fillet_polyline(pts[start : k + 1], BROOK_BEND_WIDTHS * w)
        out += part[1:] if out else part
        start = k
    return out


JOIN_ON_COURSE = 1.0  # px: a declared channel end this near a brook's course lies ON it - the hold's own reach in `finished_course`
FILLET_MIN_TURN_DEG = 8.0  # `fillet_polyline`'s own threshold: a vertex turning less is left as it is, so holding it rounds nothing less
"""Research: turn left sharp - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: a turn under 8 deg is not rounded, mirrored from `fillet_polyline`"""


def course_corner(q: Pt, course: Sequence[Pt], tol: float = JOIN_ON_COURSE) -> bool:
    """Does `q` stand on a CORNER of `course` - within `tol` of an interior vertex the rounding bends (feature 287, labels
    L16)? Holding such a vertex would leave the bend mitred, which the brook's rounding exists to forbid, so the drain's
    confluence is not placed on one (`sink.brook_join`) and `join_vertices` does not hold one.

    Research: plumbing - NONE: a geometric predicate
    """
    pts = [(float(x), float(y)) for x, y in course]
    for k in range(1, len(pts) - 1):
        if math.dist(pts[k], q) > tol:
            continue
        v0 = (pts[k - 1][0] - pts[k][0], pts[k - 1][1] - pts[k][1])
        v1 = (pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
        l0, l1 = math.hypot(*v0), math.hypot(*v1)
        if l0 < 1e-6 or l1 < 1e-6:
            continue
        cosang = max(-1.0, min(1.0, (v0[0] * v1[0] + v0[1] * v1[1]) / (l0 * l1)))
        if 180.0 - math.degrees(math.acos(cosang)) >= FILLET_MIN_TURN_DEG:
            return True
    return False


def join_vertices(course: Sequence[Pt], ends: Sequence[Pt], hold_corners: bool = True, tol: float = JOIN_ON_COURSE) -> tuple[Poly, list[Pt]]:
    """`course` with every channel end in `ends` that lies ON it (within `tol`) made a vertex, and the ends to hold there
        (feature 287, labels L16). A confluence mid-segment - the drain's `brook_join` walks the brook at a stride - is not a
        vertex, so `finished_course` could not hold it and the fillet of a nearby bend moved the course off the mouth; it is
        inserted, and held. An end on a CORNER is held only where `hold_corners` says (the head race's tap, whose run is a
        deliberate line); a confluence there is left to the rounding, which moves the course at most half its cut-back off
        the corner - `0.5 * BROOK_BEND_WIDTHS * w * cos(half the angle)`, 8.75 px on the 7 px brook, past its 3.5 px half-width, so a
    mouth there would stand out of the water (0054: a junction only where an end lies inside the other's drawn width). So no
    confluence is seated on a corner: `sink.brook_join` refuses one (`course_corner`), and a corner is never held mitred for one
    (0054: "no watercourse on them has a mitered corner"; feature 328 tried the hold and withdrew it).

        Research: plumbing - NONE: vertex insertion, so the rounding keeps a declared mouth on the course
    """
    pts = [(float(x), float(y)) for x, y in course]
    held: list[Pt] = []
    for e in ends:
        q = (float(e[0]), float(e[1]))
        if len(pts) < 2:
            break
        best = min(range(len(pts) - 1), key=lambda k: seg_dist(q[0], q[1], pts[k], pts[k + 1]))
        if seg_dist(q[0], q[1], pts[best], pts[best + 1]) > tol:
            continue
        near = min(range(len(pts)), key=lambda k: math.dist(pts[k], q))
        if math.dist(pts[near], q) <= tol:
            if hold_corners or not course_corner(pts[near], pts, tol=1e-9):
                held.append(pts[near])
            continue
        a, b = pts[best], pts[best + 1]
        ab = (b[0] - a[0], b[1] - a[1])
        t = ((q[0] - a[0]) * ab[0] + (q[1] - a[1]) * ab[1]) / ((ab[0] ** 2 + ab[1] ** 2) or 1.0)
        on = (a[0] + ab[0] * t, a[1] + ab[1] * t)
        pts.insert(best + 1, on)
        held.append(on)
    return pts, held


def round_the_brooks(s: Settlement) -> None:
    """Every brook drawn at its `finished_course`, THE FINAL WATER BEFORE ANYTHING READS IT (feature 287, M2).

    Run as the last step of `stage_sink`, the end of the water stages, so every later bank, seat, corridor, ford and deck
    test reads the course the map draws. It ran in `stage_crossings` until feature 287, six stages after the brook was
    laid: the houses were seated against one course and the crossings squared and decked against another, and the test
    of a ford read a course the fords were never set on. The WAYS STILL ROUTE AGAINST THE COURSE AS FIRST DRAWN
    (`ways.checks.stream_segs` reads its `stations`; the fords and the crossing band read `plan.brook`), for the reason
    `Settlement.round_stream` records: rounding the brook before the ways were routed moved every way its corners had
    shaped. The tap - the first point of every head race taken off a stream - is held. Rounded from the `stations` when
    they are recorded, so a second pass draws the same course rather than rounding the rounded one.

    ...AND EVERY CONFLUENCE IS HELD TOO (feature 287, labels L16): a channel that declares a stream at its far end (the
    drain's `brook_join`, the constructed route's meeting) has that end made a vertex of the course and held
    (`join_vertices`), so the rounding cannot draw the brook away from the mouth the record says joins it.

    Research: plumbing - NONE: stage ordering, the rounding itself is `finished_course`'s
    """
    chans = [c for c in s.M.get("channels") or [] if len(c.get("poly") or ()) >= 2]
    heads = [(float(c["poly"][0][0]), float(c["poly"][0][1])) for c in chans if (c.get("frm") or {}).get("kind") == "stream"]
    joins = [(float(c["poly"][-1][0]), float(c["poly"][-1][1])) for c in chans if (c.get("to") or {}).get("kind") == "stream"]
    for rec in s.M.get("streams") or []:
        course = rec.get("stations") or rec.get("poly") or []
        if len(course) < 3:
            continue
        s.round_stream(rec, drawn_course(course, heads, joins, float(rec.get("w") or 7.0)))


def drawn_course(course: Sequence[Pt], taps: Sequence[Pt], joins: Sequence[Pt] = (), w: float = BROOK_DRAWN_W) -> Poly:
    """The brook AS THE MAP DRAWS IT (feature 287 wave 5): every tap and confluence on `course` made a vertex and held
    (`join_vertices` - a confluence on a corner left to the rounding), then rounded (`finished_course`). The ONE geometry
    `round_the_brooks` draws and `brook_violations` judges, so a confluence the sink adds after the brook was judged is
    judged with it - where the rounding round a held join changed the course, the judged and the drawn used to differ."""
    pts, held = join_vertices(course, taps)
    pts, held_j = join_vertices(pts, joins, hold_corners=False)
    return finished_course(pts, w, held + held_j)


def _off_the_axes(course: Poly, away: Pt, eps: float = 1.6, nudge: float = 11.0, hold: int = 0) -> Poly:
    """No segment of a drawn watercourse lies along a screen axis.

    The GM's own words on this map (2026-08-26): a course that "appears to run exactly east to west parallel
    to the edge of the map ... makes it look like a mistake". The wander makes a held offset impossible and
    that is the cause; this is the backstop for the coincidence, since a fall on a diagonal can still put one
    segment of an honest walk on the horizontal. The nudge moves the segment's far end AWAY from the crop -
    `away` is the flank's own outward normal - and never across it: nudging along the segment's own normal
    was the first cut and it can push the vertex INWARD, which is how one ended up inside a barley plot.

    `hold` exempts the leading segments - the TAP RUN. That stride is not a coincidence to be broken up: it is
    the structural line that makes the head race's offtake angle the angle the record states, and on a map whose
    land falls due east or due south it lies on a screen axis by construction. Nudging it moved Mizuguchi's
    brook 11 ft off the fall 49 ft below its own intake, so the race left at 87 degrees off the brook's heading
    where the record says 35. A deliberate line and an accidental one look the same to this function, so the
    caller says which is which.

    Research:
        screen-axis backstop - CONVENTION: a segment within `eps` (1.6 deg) of a screen axis tilted to twice that, at most `nudge` (11 px), away from the crop
        tap run kept - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: the `hold` segments are not nudged, so the race leaves 35 deg off the brook's heading
    """
    out = list(course)
    for i in range(len(out) - 1):
        if i < hold:
            continue  # the tap run - see below
        (ax, ay), (bx, by) = out[i], out[i + 1]
        deg = math.degrees(math.atan2(by - ay, bx - ax)) % 90.0
        if min(deg, 90.0 - deg) < eps:
            # JUST ENOUGH TO CLEAR THE AXIS, never a fixed kick (settlement-review, feature 230 pass 10). A flat
            # 11 px nudge on a reach that runs straight down a due-south fall flagged every other leg, moved its
            # end 11 px out and left the next leg to come back: Inashiro's brook drew a +/-29 degree sawtooth,
            # fourteen periods down the fan's west flank, x alternating 1370 / 1381. Tilting the leg to twice the
            # detector's own angle clears it with a turn a reader cannot see, and `nudge` stays the ceiling.
            step = min(nudge, math.hypot(bx - ax, by - ay) * math.tan(math.radians(2.0 * eps)))
            out[i + 1] = (bx + away[0] * step, by + away[1] * step)
    return out
