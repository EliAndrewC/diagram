"""THE BROOK (feature 230) - the stream that is tapped at an intake and runs on past the fan, and what stands at the tap.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

import math
import random
import re
from collections.abc import Callable, Sequence

from l7r.diagram.settlement import Settlement, knob_rng, point_in_poly, seg_dist
from l7r.diagram.settlement._geom import fillet_polyline
from l7r.diagram.settlement._knobs import Knob, register_knob
from l7r.diagram.sitegen.geom import crosses_poly, unit

from ..consts import (
    BROOK_BEND_WIDTHS,
    BROOK_FRAME_MARGIN,
    BROOK_MAX_TURN_DEG,
    BROOK_SKIRT,
    BROOK_TAP_RUN,
    BROOK_WANDER,
    BROOK_WANDER_STEP,
    OFFTAKE_DEG,
    WEIR_HALF_FT,
    WEIR_SKEW_DEG,
    WEIR_THICK_FT,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .brook_rules import (
    AXIS_EPS_DEG,
    BEND_DIP_FT,
    BROOK_DRAWN_W,
    LEVEL_TOL_FT,
    RULED_TOL_FT,
    _dist_to_course,
    axis_segments,
    bar_on_race,
    course_enters,
    crosses_mid_run,
    ditch_strokes,
    ends_off_canvas,
    level_runs_any_view,
    max_turn_deg,
    monotone_down,
    reserved_box,
    ruled_excess,
    tap_index,
    to_edge,
    turn_deg,
)

# THE WEIR'S FORM (269 B22; research/water/300): a fence of stakes woven with brushwood (feature 280 M36: the woven stake
# fence is in the Man'yoshu, the reed weave only in a present-day weir - research/water/640), a frame of stakes and logs packed
# with clay, a crib of timber packed with stone, or a course of stone-filled baskets, each drawn at its own thickness
# (`WEIR_THICK_FT`). "The rule the map follows: a weir hamlet's weir takes one of four forms, rolled per settlement
# with an even chance" - the EVEN chance a GUESS, no source counting them. `crib` is the default because it is the
# one form the glyph drew before the knob. Declared as `meta.weir_form` on a weir hamlet only.
WEIR_FORM = register_knob(Knob("weir_form", list(WEIR_THICK_FT), default="crib"))

EXIT_BEND_FRAC = 0.12  # an exit leg's midpoint bend, as a share of the leg ...
EXIT_BEND_MAX_FT = 60.0  # ... at most this far aside


def exit_bend(start: tuple[float, float], heading: tuple[float, float], leg: float, side: float) -> tuple[float, float]:
    """The midpoint of an exit leg from `start` along `heading` for `leg` ft, set aside by `EXIT_BEND_FRAC` of the leg
    (at most `EXIT_BEND_MAX_FT`) on `side` (+1 or -1) - one gentle bend in a leg the page still shows (feature 261)."""
    off = side * min(EXIT_BEND_MAX_FT, EXIT_BEND_FRAC * leg)
    return (start[0] + heading[0] * leg / 2 - heading[1] * off, start[1] + heading[1] * leg / 2 + heading[0] * off)


def exit_legs(out: Sequence[Pt], fall: Pt, W: float, H: float) -> list[Pt]:
    """The course's way OFF the frame from its last station `out[-1]`: four legs turning from the course's own heading onto
    the fall `fall`, each still on the page bent once at its middle, the last lengthened down the fall until the mouth is
    off the (0, 0, W, H) canvas (feature 287 wave 5, water:W07) - lifted out of `brook_skirt` so the mouth's guarantee is
    tested on plain inputs. Returns the points to append."""
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
    no two consecutive vertices can share a bearing and none can lie on an axis."""
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
    itself reaches the box, which the margin is sized to prevent."""
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
    has nothing to drop and stays; the brook's placer judges the result and takes its next candidate."""
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


SETTLE_PASSES = 8  # the bounded repair's passes (plan D5: each ruled-run bend halves the run, so a handful suffices)
RULED_BENDS_PER_PASS = 8  # ...and the ruled runs bent within one pass, each re-read after the last bend


def finished_course(course: Sequence[Pt], w: float, taps: Sequence[Pt] = ()) -> Poly:
    """The brook's course AS DRAWN: `course` with its bends rounded at `BROOK_BEND_WIDTHS` of its width `w`, each vertex
    within a foot of a tap in `taps` held where it is (feature 287, M2 - lifted out of `Settlement.round_stream`).

    A natural brook turns on a curve like every earthen channel (`fillet_polyline`; research/water.html "Why does every
    ditch turn on a curve?"; settlement-review of Sawada, feature 261: mitred corners of 27-47 degrees). A held vertex
    splits the course and each stretch is rounded between its own ends, so the head race still leaves the course at the
    tap where its offtake angle is measured. A function of the course, its width and the taps only, so the placer that
    judges a brook and the stage that draws it read ONE geometry; a course of two points has no corner and comes back
    as it is."""
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


def course_corner(q: Pt, course: Sequence[Pt], tol: float = JOIN_ON_COURSE) -> bool:
    """Does `q` stand on a CORNER of `course` - within `tol` of an interior vertex the rounding bends (feature 287, labels
    L16)? Holding such a vertex would leave the bend mitred, which the brook's rounding exists to forbid, so the drain's
    confluence is not placed on one (`sink.brook_join`) and `join_vertices` does not hold one."""
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
    the corner - `0.5 * BROOK_BEND_WIDTHS * w * cos(half the angle)`, 8.75 px on the 7 px brook - under the rule's 13."""
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
    (`join_vertices`), so the rounding cannot draw the brook away from the mouth the record says joins it."""
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
    caller says which is which."""
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


def brook_skirt(plan: SitePlan, sluice: Pt, side: int, crop: Sequence[Poly] = (), skirt: float = BROOK_SKIRT, steps: int = 16) -> Poly:
    """The brook's course BELOW the intake: past the cultivated ground on one flank, then off the frame.

    A stream is tapped, not consumed - the intake takes what the field needs and the brook carries the rest
    on down (research/water.html, "Where does the brook stop being a brook and become the ditch"). So the
    course below the intake has one job: pass the crop without touching it, and be a stream while it does.

    It is built in the fall's own frame - `u` along the fall, `v` across it on the chosen flank - by walking
    down the fan and holding `v` outside the outermost cultivated ground seen so far, plus a skirt. Four
    things shape it, and every one of them is a review finding rather than a preference:

    THE PROFILE IS PER RING, over every cultivated ring. The first cut cleared the paddy ENVELOPE and the dry
    hem is laid outside it: 15 of 25 hem plots crossed on one map, 1,456 ft of brook with plow ink on both
    banks. The supply canals go in too, one step weaker - they mark the margin the brook stays outside of.
    And a ring enters the profile by the `u` its BODY starts at, not by each vertex's own `u`, because a
    plot's outermost corner can lie far downslope of the ground it covers.

    THE OFFSET WANDERS, on a seeded reflecting walk. Held at the floor it decayed onto a constant and drew
    1,284 ft at exactly 90.000 degrees - the ruled line the GM rejected on this map by name - and ran 1,360 ft
    parallel to the canal hemming that margin, which is the two-water-lines catch in another place.

    A STEP ACROSS THE FALL IS LED INTO. The profile jumps when a plot enters it, and an un-led jump is a
    mitred elbow: 67 degrees against 0.3-18 everywhere else, plainly cut to walk the water round two plots.

    AND IT STAYS ON THE SHEET. The picture is cropped to its content and a stream is not content, so a course
    that strays wide of the field strays off the picture - 77% of it on a diagonal fall, in two pieces, with
    the confluence 123 ft beyond the edge. The stations are held inside the field's bounds grown by
    `BROOK_FRAME_MARGIN`, and the course leaves the frame from the last one that fits."""
    dx, dy = plan.fall
    px, py = -dy * side, dx * side
    rings = [[(v[0] * dx + v[1] * dy, v[0] * px + v[1] * py) for v in ring] for ring in [list(plan.envelope), *[list(c) for c in crop]] if ring]
    # CROP AT THE FAN'S HEAD YIELDS TO THE BROOK - it does not floor it (feature 230, settlement-review pass 9).
    # Every brook map shipped its sharpest corner 49 ft below the weir: 72.4, 77.9, 71.9 and 51.9 degrees against
    # medians of 10 to 15, a spike pointing at the field in the one place a reader looks. Instrumented, the course
    # was not skirting the fan at all - the fan's plots do not begin until ~120 px down the fall - but a DRY HEM
    # plot laid round the fork, reaching up beside the intake itself (to 72 px below the tap and 104 px out on
    # the brook's flank on Kashikawa, 4 px below the fork on Mizuguchi). Floored against it, the corner-cut point
    # just past the tap run was thrown 138 px sideways in 33. The rule this module already keeps for the tap run
    # says what should happen instead: the crop that came close is what yields, and `_comb_draw_hem` drops any hem
    # plot the brook's band crosses. So a crop ring whose body reaches within one skirt of the fan's head is left
    # out of the profile. Measured: the corner falls to 41, 53, 53 and 52 degrees, one dry plot of ~20 gives way
    # on two maps, and every map keeps its households and its clearance from the crop.
    #
    # Two levers were measured first and did nothing: narrowing the first station's look-ahead window (71-73
    # degrees, unchanged), and a longer head race (the corner moved on two maps and grew to 88 on Sawada). What is
    # left at ~52 degrees is the fan's own divergence at its head, which `BROOK_FAN_TRIM` exists to ease.
    _head_u = min(u for u, _ in rings[0])
    rings = [rings[0], *[r for r in rings[1:] if min(u for u, _ in r) >= _head_u + skirt]]
    segs = [(a, b) for r in rings for a, b in zip(r, r[1:] + r[:1], strict=False)]
    u0, v0 = sluice[0] * dx + sluice[1] * dy, sluice[0] * px + sluice[1] * py
    umax = max(u for r in rings for u, _ in r)
    # THE BOUND IS IN MAP COORDINATES, because the view is (the sheet is cropped to an axis-aligned box round
    # its content, and a stream is not content). Bounding the lateral offset in the FALL's frame was the first
    # cut and on a diagonal fall it let the course leave the picture and come back: 77% of one brook outside
    # the view in two pieces a reader cannot join. `_v_within` returns the largest offset that keeps the
    # station inside the field's own bounds grown by the margin - never less than the crop clearance, which
    # wins if the two ever disagree.
    xs = [q[0] for ring in [list(plan.envelope), *[list(c) for c in crop]] for q in ring]
    ys = [q[1] for ring in [list(plan.envelope), *[list(c) for c in crop]] for q in ring]
    box = (min(xs) - BROOK_FRAME_MARGIN, min(ys) - BROOK_FRAME_MARGIN, max(xs) + BROOK_FRAME_MARGIN, max(ys) + BROOK_FRAME_MARGIN)
    rng = knob_rng(plan.spec.seed, "brook_wander")
    swing = 1 if rng.random() < 0.5 else -1
    # the tap's own stride: the brook runs on down the fall before it bends away, so the head race's offtake
    # angle is measured off a heading the brook is actually on
    out: Poly = [(sluice[0] + dx * BROOK_TAP_RUN, sluice[1] + dy * BROOK_TAP_RUN)]
    stray, stride = BROOK_WANDER / 2.0, (umax - u0 - BROOK_TAP_RUN) / steps
    for i in range(1, steps + 1):
        u = u0 + BROOK_TAP_RUN + stride * i
        stray, swing = _wander(rng, stray, swing)
        floor = _crop_edge(segs, u, stride + 40.0, v0) + skirt
        # THE COURSE BELOW THE TAP STILL READS RULED WHERE THE FIELD'S MARGIN IS STRAIGHT, and the two levers that would
        # loosen it are refused on measurement (settlement-review, feature 230 pass 11: 2,124 px of Kashikawa's brook, 46%
        # of its length, within 4 px of a straight line). Straying INWARD from the frame box when the box binds changed
        # nothing - the course here is held by the crop's floor, not by the box. Widening the walk (`BROOK_WANDER` 10 -> 26)
        # halves the ruled run to 1,116 px and costs the clearance the skirt exists to keep: Mizuguchi's brook came within
        # 6.2 px of a dry plot beyond the fan's head, against the 34 px skirt, because straying outward can approach crop
        # that lies outside the fan. What would loosen it honestly is a course that does not follow the field's margin at a
        # fixed offset at all - `future-work/farming-communities.md`.
        # ...and a THIRD measurement, from the other side (pass 12, which read Sawada's middle reach as "a ruled
        # horizontal line carrying a 3-px square-wave jitter", and noticed that the DUG drain wanders more than the
        # natural brook - the one cue that separates dug from natural, inverted). Widening the walk the other way -
        # `BROOK_WANDER` 10 -> 18 on a longer step of 5, the frame margin opened to 52 to hold it - moves nothing:
        # the straightest 12-vertex run over 200 ft came back 1,746 ft at 4.1 px of departure on Kashikawa against
        # 1,745 ft at 3.4 before it, and Inashiro's got STRAIGHTER (4.9 -> 2.1). The reason is the line above rather
        # than the amplitude: where the crop's floor binds, the walk is not what decides the offset at all, so a
        # wider walk only moves the few stations where the field's own edge is already crooked.
        v = _v_within(u, floor, floor + stray, (dx, dy), (px, py), box)
        # THE COURSE LEAVES WHERE THE FRAME WOULD PIN IT (settlement-review of Sawada, feature 261). A station the box
        # holds below its walk is laid flat against the box, and a run of them drew the brook dead level along the sheet's
        # top margin for 457 ft - the ruled line parallel to the edge the GM called out as a mistake (2026-08-26). Once
        # the course has run half its stations, the first one the box binds is where it turns off the frame instead.
        if i > steps // 2 and _v_within(u, float("-inf"), floor + stray, (dx, dy), (px, py), box) < floor + stray - 1.0:
            break
        out.append((u * dx + v * px, u * dy + v * py))
    # ...and off the frame from the last station, still wandering, the run measured along the fall from there.
    # THE FIRST EXIT LEG KEEPS THE COURSE'S OWN HEADING and only then turns onto the fall: driving it straight
    # downhill from a station that is well out to the side puts a corner exactly where the brook should be
    # running off the sheet (121 degrees on one map, and the sharpest thing on it).
    lx, ly = out[-1]
    out += exit_legs(out, (dx, dy), float(plan.W), float(plan.H))

    # THE CORNERS ARE CUT, not led into. Inserting lead stations per step was the first answer and it made the
    # thing it was meant to prevent: short jogs between long legs, 16 turns past 70 degrees on one map and a
    # median vertex of 34 against its siblings' 2 to 24 - a staircase rather than a meander. One corner-cutting
    # pass over the stations replaces each of them with two points a quarter in from either side, so a vertex
    # becomes two bends of about half the turn; each cut point is re-floored against the crop at its own place
    # down the fall, so a rounded course cannot round its way into the rice.
    # the TAP is the cut's leading anchor and is dropped from the result (`feed_brook` supplies it): the corner
    # the brook turns just below the tap is the sharpest on the course and the one a reader looks straight at,
    # and anchoring on the tap cuts it while leaving the stride below the tap on the fall, which is what makes
    # the head race's offtake angle the angle the record states
    u_end = lx * dx + ly * dy  # the last station: past it the course is leaving and owes the box nothing
    mid, keep_tail = [sluice, *out[:-1]], out[-1:]  # everything but the final off-frame point is cut, exits included
    cut: Poly = []
    for a, b in zip(mid, mid[1:], strict=False):
        # the cut is a DISTANCE from each end, not a fraction of the segment: at a fraction, a vertex whose
        # other arm is short is barely rounded at all, which left the two structural turns at the head as
        # mitres while the meandered middle came out smooth
        leg = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        d = min(0.3, 45.0 / leg)
        for t in (d, 1.0 - d):
            qx, qy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            cu, cv = qx * dx + qy * dy, qx * px + qy * py
            if cu > u_end:
                # past the last station this is the reach that LEAVES, and holding it inside the frame box is
                # what folded the exit back on itself - a 120 to 131 degree reversal on the two maps whose land
                # falls on a diagonal, in the last four vertices of each
                cut.append((qx, qy))
                continue
            # a NARROW window here, unlike the stations': a cut point sits between two stations that have each
            # already been floored with the wide one, so all it owes is the crop at its own place - and the wide
            # window would push the points just below the tap out to the fan's edge before the fan begins,
            # which swings the brook off the fall and takes the head race's offtake angle with it
            # ...and NO tap baseline. The stations floor on `v0` so that the course starts outside the intake's
            # own line; a cut point must not, or every point between the tap and the first station is pushed a
            # skirt's width sideways and the brook leaves the tap on a bearing that is not the fall - which is
            # the bearing the head race's offtake angle is measured against.
            if cu <= u0 + BROOK_TAP_RUN:
                # THE TAP RUN IS NOT FLOORED AT ALL, and that is the whole of what makes the offtake angle
                # true. The note above says a cut point must not take the tap's baseline; the floor itself is
                # the other half of the same hazard - where the crop comes close to the intake, flooring pushes
                # the points inside the first stride out by a skirt's width and the brook leaves the tap on a
                # bearing that is not the fall. Measured on Mizuguchi: the course left the intake at 281
                # degrees against a fall of 0, so the head race's recorded 35 degree offtake was drawn at 114
                # degrees off the brook's downstream heading - pointing upstream, with the dug ditch reading as
                # the continuation and the brook as the branch, which is the GM's original complaint in new
                # clothes. The crop that came close is what yields: `_comb_draw_hem` drops any hem plot the
                # brook's own band crosses, so holding this line puts no plow under water.
                cut.append((qx, qy))
                continue
            cfloor = _crop_edge(segs, cu, 12.0, -1e9) + skirt
            cv = _v_within(cu, cfloor, max(cfloor, cv), (dx, dy), (px, py), box)
            cut.append((cu * dx + cv * px, cu * dy + cv * py))
    cut.append(mid[-1])
    return unfold(
        _off_the_axes([*cut, *keep_tail], (px, py), hold=1), BROOK_MAX_TURN_DEG
    )  # the tap run: two cut points on the fall; the segment that leaves it is nudged off an axis like any other (feature 261: Sawada's drew exactly vertical below its tap)


def brook_violations(course: Sequence[Pt], plan: SitePlan, sluice: Pt, ditches: Sequence[Poly] = (), joins: Sequence[Pt] = ()) -> list[str]:
    """Which of the brook's rules the DRAWN course (`drawn_course` of `course`, its tap and any confluence `joins` held)
    breaks - empty for a course the placer may take. One predicate per rule: W01 `max_turn_deg`, W02 `level_runs_along_frame` over the whole canvas, W03
    `ruled_excess`, W04 `axis_segments`, W06 `course_enters`, W07 `ends_off_canvas` (the off-map source and the mouth), W08
    `crosses_mid_run`, W11 `monotone_down` below the tap."""
    fin = drawn_course(course, [sluice], joins)
    W, H = float(plan.W), float(plan.H)
    box = reserved_box(course, plan)
    run, bound, _a, _b = ruled_excess(fin, W, H, box)
    checks = {
        "fold": max_turn_deg(fin) > BROOK_MAX_TURN_DEG,
        "level": bool(level_runs_any_view(fin, W, H, box)),
        "ruled": run > bound,
        "axis": bool(axis_segments(fin, [sluice])),
        "enters": course_enters(fin, [plan.envelope]),
        "source": not ends_off_canvas(fin, W, H, ends=(0,)),
        "mouth": not ends_off_canvas(fin, W, H, ends=(-1,)),  # the brook runs on past the fan and leaves the map (feature 230)
        "crosses": any(crosses_mid_run(fin, d) for d in ditches),
        "climbs": not monotone_down(fin[tap_index(fin, [sluice]) :], plan.fall, slack=BEND_DIP_FT),
    }
    return [k for k, bad in checks.items() if bad]


def _pinned(course: Sequence[Pt], sluice: Pt) -> tuple[int, set[int]]:
    """(the tap's index, the vertices a repair may not move): the ends, the tap and the tap run's two points below it -
    the stride on the fall the head race's offtake angle is measured along."""
    tap = tap_index(course, [sluice])
    return tap, {0, len(course) - 1, tap, tap + 1, tap + 2}


def axes_off(course: Sequence[Pt], away: Pt, sluice: Pt, fall: Pt, eps: float = AXIS_EPS_DEG) -> Poly:
    """Every segment of a wander stride or more tilted off the screen axes, the tap run excepted (water:W04) - over the
    WHOLE course, the approach's last leg into the tap included (Inashiro's 1.2 degree leg, which `_off_the_axes` on the
    approach alone never saw). No ceiling on the tilt: the 11 px cap `_off_the_axes` keeps left a long off-map exit leg
    on the axis.

    A segment the flank's normal (`away`) turns is tilted by moving its far end across the fall - its near end where the
    far one is pinned (the tap: so the head race keeps its mouth). A segment lying ACROSS the fall, which `away` cannot
    turn, is tilted down the fall instead: its far end moved down it, or its near end up it, whichever leaves its
    neighbor still running downhill (water:W11) - the step round a ditch's tail lies across the fall, and turning it
    about its own normal made the course climb (the W08 unit case)."""
    out = list(course)
    tap, pinned = _pinned(out, sluice)
    u = lambda q: q[0] * fall[0] + q[1] * fall[1]  # noqa: E731
    for i in range(len(out) - 1):
        a, b = out[i], out[i + 1]
        L = math.dist(a, b)
        deg = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0
        if i in (tap, tap + 1) or L < BROOK_WANDER_STEP or min(deg, 90.0 - deg) >= eps:
            continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        cross = abs(away[0] * uy - away[1] * ux)
        step = L * math.tan(math.radians(2.0 * eps))
        if cross >= 0.3:
            k = i + 1 if i + 1 not in pinned else i
            moves = [(k, away[0] * step / cross, away[1] * step / cross)] if k not in pinned else []
        else:  # across the fall: down it at the far end, or up it at the near end, where the neighbor keeps its descent
            slack_b = u(out[i + 2]) - u(b) if i + 2 < len(out) else math.inf
            slack_a = u(a) - u(out[i - 1]) if i > 0 else math.inf
            moves = [(k, sg * fall[0] * step, sg * fall[1] * step) for k, sg, slack in ((i + 1, 1.0, slack_b), (i, -1.0, slack_a)) if k not in pinned and slack > step]
        for k, mx, my in moves[:1]:
            out[k] = (out[k][0] + mx, out[k][1] + my)
    return out


def bend_at(course: Sequence[Pt], span: Sequence[Pt], need: Callable[[Pt], tuple[float, float]], away: Pt, sluice: Pt, envelope: Sequence[Pt], cap: float = math.inf) -> Poly:
    """`course` with one bend inserted in the run `span` (drawn-course points): at the middle of the LONGEST segment lying
    along it (the tap run excepted), set ACROSS THE FALL (`away`, the flank's normal) by the smaller of the two offsets
    `need(base)` gives - the two that clear the run's reference line on either side - whose point is not in the field,
    and no more than half the segment, so the bend turns the course gently. The longest segment, because a bend on a
    short one is a spike the fillet rounds back inside the tolerance or `unfold` takes out (cohort seed 2: a brook pinned
    to the frame box in 8-70 ft legs kept its level run through every pass). Set along `away`: the caller passes the
    flank's normal, so the bend moves no vertex up or down the fall and the course below the tap stays monotone
    (water:W11) - or, for a run lying ACROSS the fall, which no bend across it can break (the step round the fan's head
    on the W08 unit case: 280 ft straight), the fall itself, a dip of a bend's depth that `BEND_DIP_FT` allows."""
    tap, _pinned_ = _pinned(course, sluice)
    along = [k for k in range(len(course) - 1) if k not in (tap, tap + 1) and _dist_to_course(((course[k][0] + course[k + 1][0]) / 2, (course[k][1] + course[k + 1][1]) / 2), span) <= 8.0]
    for k in sorted(along, key=lambda q: -math.dist(course[q], course[q + 1])):
        a, b = course[k], course[k + 1]
        base = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        for off in sorted(need(base), key=abs):  # the smaller of the two bends first
            q = (base[0] + away[0] * off, base[1] + away[1] * off)
            if abs(off) <= min(math.dist(a, b) / 2.0, cap) and not point_in_poly(q[0], q[1], list(envelope)):
                return [*course[: k + 1], q, *course[k + 1 :]]
    return list(course)


def bend_runs(course: Sequence[Pt], plan: SitePlan, sluice: Pt, away: Pt) -> Poly:
    """One bend for each level run along the canvas (water:W02) and for the straightest run where it is over its bound
    (water:W03), each at the run's middle, judged on the drawn course. A level run's bend clears the level by twice its
    tolerance and a foot; a ruled run's bend clears the chord by its tolerance and a foot and a half - so each bend
    breaks the run it was set in, halving a ruled run, and the repair's passes bound how many it takes."""
    W, H = float(plan.W), float(plan.H)
    out = list(course)
    # EVERY run over its bound, re-read after each bend - a course can carry several (cohort seed 13: three ruled runs of
    # ~500 ft, one per exit leg and one abreast of the field), and one bend a pass left the third standing when the passes
    # ran out. The level runs first, the longest of them first; then the straightest run, while it is over its bound.
    for _ in range(RULED_BENDS_PER_PASS):
        fin = finished_course(out, BROOK_DRAWN_W, [sluice])
        runs = level_runs_any_view(fin, W, H, reserved_box(out, plan))
        if not runs:
            break
        axis, i, j, _run = max(runs, key=lambda r: r[3])
        v = away if abs(away[axis]) >= 0.3 else plan.fall  # a level the flank's normal cannot leave is left down the fall
        bent = bend_at(out, fin[i : j + 1], level_offsets(fin[i][axis], axis, v), v, sluice, plan.envelope, BEND_DIP_FT if v is plan.fall else math.inf)
        if bent == out:
            break  # no segment along it takes a bend; the placer's judgment refuses the candidate
        out = bent
    for _ in range(RULED_BENDS_PER_PASS):
        fin = finished_course(out, BROOK_DRAWN_W, [sluice])
        run, bound, a, b = ruled_excess(fin, W, H, reserved_box(out, plan))
        if run <= bound:
            break
        v = away if abs(away[0] * (b[1] - a[1]) - away[1] * (b[0] - a[0])) >= 0.3 * run else plan.fall  # a run ACROSS the fall bends down it
        out = bend_at(out, [a, b], chord_offsets(a, b, v), v, sluice, plan.envelope, BEND_DIP_FT if v is plan.fall else math.inf)
    return out


def level_offsets(level: float, axis: int, away: Pt) -> Callable[[Pt], tuple[float, float]]:
    """For a level run held at `level` on `axis`: the two offsets along `away` that set a point `LEVEL_TOL_FT` and a foot
    and a half off that level, either side (water:W02) - measured from the run's own level, not the point's, so the bend
    breaks the run from its first vertex."""
    av = away[axis] if abs(away[axis]) >= 0.3 else math.copysign(0.3, away[axis] or 1.0)
    return lambda p: ((level + LEVEL_TOL_FT + 1.5 - p[axis]) / av, (level - LEVEL_TOL_FT - 1.5 - p[axis]) / av)


def chord_offsets(a: Pt, b: Pt, away: Pt) -> Callable[[Pt], tuple[float, float]]:
    """For a straight run on the chord a-b: the two offsets along `away` that set a point `RULED_TOL_FT` and a foot and a
    half off the chord's line, either side (water:W03), measured from the line, not from the course under the point."""
    L = math.dist(a, b) or 1.0
    n = (-(b[1] - a[1]) / L, (b[0] - a[0]) / L)
    an = away[0] * n[0] + away[1] * n[1]
    an = an if abs(an) >= 0.3 else math.copysign(0.3, an or 1.0)
    side = lambda p: (p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1]  # noqa: E731
    return lambda p: ((RULED_TOL_FT + 1.5 - side(p)) / an, (-RULED_TOL_FT - 1.5 - side(p)) / an)


def clear_of_field(course: Sequence[Pt], envelope: Sequence[Pt], away: Pt, sluice: Pt, step: float = 6.0, limit: int = 60) -> Poly:
    """Every segment of `course` that runs into the field moved out of it, across the fall on the flank (`away`), its
    free ends a step at a time until it clears (water:W06). The skirt's profile floors each station outside the crop, but
    the cut points between stations are floored against a narrow window, and a lobe between two of them still took the
    course through the rice (cohort seed 12: eight drawn vertices inside the envelope). Across the fall, so no vertex
    moves up or down it (water:W11); the tap run and the ends are not moved - the tap run stands at the fan's head, where
    the head race leaves it, and is the intake itself."""
    out = list(course)
    ring = list(envelope)
    tap, pinned = _pinned(out, sluice)
    for k in range(len(out) - 1):
        free = [q for q in (k, k + 1) if q not in pinned]
        for _ in range(limit if free else 0):
            inside = [q for q in (k, k + 1) if point_in_poly(out[q][0], out[q][1], ring)]
            # a crossing counts only where both ends are free to answer for it: the leg into the tap is the intake itself
            if not ([q for q in inside if q not in pinned] or (len(free) == 2 and k + 1 != tap and crosses_poly(out[k], out[k + 1], ring))):
                break
            for q in free:
                out[q] = (out[q][0] + away[0] * step, out[q][1] + away[1] * step)
    return out


def settle_course(course: Sequence[Pt], plan: SitePlan, sluice: Pt) -> Poly:
    """THE BOUNDED REPAIR (feature 287, water:W01-W04): off the axes, unfolded with the tap held, the level and ruled runs
    bent, off the axes again - to a fixed point, at most `SETTLE_PASSES` times. Off the axes runs LAST: unfold deleting a
    vertex makes a new segment, and a segment made after the nudge was the hole the axis rule fell through."""
    away = (-plan.fall[1] * plan.brook_side, plan.fall[0] * plan.brook_side)  # the flank's outward normal, as `brook_skirt`'s
    out = list(course)
    for _ in range(SETTLE_PASSES):
        before = out
        out = unfold(axes_off(clear_of_field(out, plan.envelope, away, sluice), away, sluice, plan.fall), BROOK_MAX_TURN_DEG, hold=[sluice])
        out = axes_off(bend_runs(out, plan, sluice, away), away, sluice, plan.fall)
        if out == before:
            break
    return out


def approach_legs(plan: SitePlan, sluice: Pt, th: float, run: float) -> Poly | None:
    """The approach on bearing `th` (radians, from the tap upslope): the off-map source, its bowed midpoint and three
    wandering points into the tap - or None where its chord runs through the rice.

    THE SOURCE IS OFF THE CANVAS BY CONSTRUCTION (water:W07): the run is `run` or the distance to the canvas edge along
    the bearing and 60 more, whichever is longer, as the exit sizes its span from the edge - a fixed 420 ft stopped on the
    map on a canvas wider than that."""
    d = (math.cos(th), math.sin(th))
    run = max(run, to_edge(sluice, d, float(plan.W), float(plan.H)) + 60.0)
    up = (sluice[0] + d[0] * run, sluice[1] + d[1] * run)
    mid = ((up[0] + sluice[0]) / 2 - d[1] * 26, (up[1] + sluice[1]) / 2 + d[0] * 26)
    near = (sluice[0] + d[0] * 40, sluice[1] + d[1] * 40)  # the last 40 px is the intake itself
    if crosses_poly(up, mid, plan.envelope) or crosses_poly(mid, near, plan.envelope):
        return None
    # the APPROACH wanders too. It was one ruled 420 ft line into the tap - 211 ft of it in frame, and
    # the reviewer counted it among the third of the course with no meander at all; a brook that is a
    # stream below its tap and a drawn line above it is not one brook.
    wob = knob_rng(plan.spec.seed, "brook_approach")
    legs = [up, mid]
    for t in (0.45, 0.68, 0.86):
        qx, qy = mid[0] + (sluice[0] - mid[0]) * t, mid[1] + (sluice[1] - mid[1]) * t
        j = wob.uniform(-16.0, 16.0)
        legs.append((qx - d[1] * j, qy + d[0] * j))
    # ...and off the screen axes, as the course below the tap is (`_off_the_axes`): Inashiro's approach drew a leg
    # 49 ft at 1.2 degrees off vertical (feature 261, found beside Sawada's tap-leaving segment). The nudge moves a
    # leg's far end across the approach, never the sluice, so the tap stays where the head race leaves it.
    return _off_the_axes(legs, (-d[1], d[0]))


def outside_stretches(plan: SitePlan, ditches: Sequence[Poly]) -> list[Poly]:
    """The stretches of the net's ditches that run outside the field's envelope, as two-point rings for `brook_skirt`'s
    profile - the delivery tails and the collector's end a brook passing the fan must go round (water:W08)."""
    return [[a, b] for d in ditches for a, b in zip(d, d[1:], strict=False) if not point_in_poly((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, list(plan.envelope))]


def feed_brook(plan: SitePlan, sluice: Pt, crop: Sequence[Poly] = (), run: float = 420.0) -> Poly:
    """The brook: down off the high ground to the intake, and ON PAST the fan to leave the map.

    Until feature 230 it ended AT the sluice and "became" the head race there - a handover with no
    feature at an arbitrary point, which is what the GM asked about. The record answers that a brook is
    tapped at an intake on one bank and keeps its own course below it, so the course has two halves: the
    approach, searched here as it always was, and `brook_skirt`'s passage down one flank.

    THE APPROACH is steered clear of the rice: a fan's head can carry a lobe out to one side and a brook
    coming straight down the fall line then clips it (`streams_avoid_fields`, which is right to object -
    a stream does not run through a flooded paddy). Bearings are tried outward from straight-upslope, so
    the brook stays as close to the fall line as the field allows. The last 40 px into the intake is
    legitimately against the crop and is not tested.

    EVERY RULE OF THE BROOK IS DECIDED HERE (feature 287): each candidate - a bearing, and the skirt as laid or, where
    that crosses a ditch mid-run, laid round the ditches' outside stretches - is repaired (`settle_course`) and taken
    only where `brook_violations` finds nothing on the course as drawn. THE LAST CANDIDATES go round the field
    (`around_the_field`): from straight up the fall and then from every other bearing, the shortest course that keeps
    half a skirt clear of the rice - repaired and judged like any other; past them the site is refused (`BrookRefused`).
    The other flank is NOT a
    candidate, though the design proposed it: the head race and the fan's trim were carved for the rolled flank before
    the brook is laid (`plan.head_deg`, `fit.py`), so a brook on the other side would run where the race leaves."""
    dx, dy = plan.fall
    base = math.degrees(math.atan2(-dy, -dx))  # upslope
    ditches = ditch_strokes(plan)
    skirt = brook_skirt(plan, sluice, plan.brook_side, crop)
    if any(crosses_mid_run(finished_course([sluice, *skirt], BROOK_DRAWN_W, [sluice]), d) for d in ditches):
        # the skirt as laid crosses a ditch mid-run, and no bearing of the approach moves the skirt: lay it again round
        # the ditches' outside stretches rather than judge fifteen approaches on a skirt that cannot pass
        skirt = brook_skirt(plan, sluice, plan.brook_side, [*crop, *outside_stretches(plan, ditches)])
    for swing in sorted((10.0 * k for k in range(-7, 8)), key=abs):
        legs = approach_legs(plan, sluice, math.radians(base + swing), run)
        if legs is None:
            continue
        course = settle_course([*legs, sluice, *skirt], plan, sluice)
        if not brook_violations(course, plan, sluice, ditches):
            return course
    # THE LAST CANDIDATES ARE JUDGED LIKE EVERY OTHER (feature 287 wave 5): the route round the field used to be returned
    # unjudged, so a brook it drew folded, ruled, on an axis, across a ditch or climbing reached the map with nothing to
    # refuse it. It is tried from straight up the fall first (the route this loop always drew), then from every other
    # bearing's source, then on the skirt laid round the ditches' outside stretches - and past the last the site is
    # refused by name (`BrookRefused`). Measured 2026-09-29 over cohort 1-60 and the pool: no brook reaches the refusal.
    for again in (False, True):
        sk = brook_skirt(plan, sluice, plan.brook_side, [*crop, *outside_stretches(plan, ditches)]) if again else skirt
        for swing in sorted((10.0 * k for k in range(-7, 8)), key=abs):
            course = settle_course([*round_the_field(plan, sluice, math.radians(base + swing), run), sluice, *sk], plan, sluice)
            if not brook_violations(course, plan, sluice, ditches):
                return course
    raise BrookRefused(f"{plan.spec.name}: no course of the feed brook - any bearing, round the field or not - keeps every rule of the brook")


class BrookRefused(ValueError):
    """The feed brook has no course its rules allow (feature 287, FR-005): refused by name, never drawn in breach - as
    `SinkRefused`, `SeatRefused` and `SiteRefused` refuse theirs."""


def round_the_field(plan: SitePlan, sluice: Pt, th: float, run: float) -> Poly:
    """The approach from the source on bearing `th` round the field to the tap (`around_the_field`) - the source off the
    canvas as `approach_legs` sets it; a way the field leaves clear is bowed at its middle as every approach is."""
    d = (math.cos(th), math.sin(th))
    reach = max(run, to_edge(sluice, d, float(plan.W), float(plan.H)) + 60.0)
    path = around_the_field(plan.envelope, (sluice[0] + d[0] * reach, sluice[1] + d[1] * reach), sluice)
    if len(path) == 1:  # the way from the source is clear: bowed at its middle as every approach is, off the axis
        path = [path[0], ((path[0][0] + sluice[0]) / 2 - d[1] * 26, (path[0][1] + sluice[1]) / 2 + d[0] * 26)]
    return path


def around_the_field(envelope: Sequence[Pt], start: Pt, goal: Pt, pad: float = BROOK_SKIRT / 2.0, intake: float = 40.0) -> Poly:
    """The shortest course from `start` to `goal` (the tap) that stays `pad` clear of the field, the tap excluded -
    everything up to it, as a polyline (water:W06, the approach's last candidate).

    A visibility graph over the corners of the field grown by `pad`: a leg is allowed where it does not enter that
    ground, and the leg into the tap where only its last `intake` ft does - the intake itself, against the crop by
    design. `ways.clearance.route_around`, the design's choice, is the lane router's and was measured failing here: on a
    lobe over the tap it pushed the approach's end back INTO the lobe. A tap the field closes round on every side has no
    such course; `head_sluice` seats the tap at the fan's head, so that is input the fit never makes, and the straight
    course is returned for the placer's judgment to refuse."""
    from shapely.geometry import LineString, Polygon  # noqa: PLC0415 - bound on first use

    field = Polygon(envelope).buffer(0)
    core = field.buffer(pad - 0.5, join_style="mitre")
    nodes = [start, *[(float(x), float(y)) for x, y in list(field.buffer(pad, join_style="mitre").exterior.coords)[:-1]], goal]
    last = len(nodes) - 1

    def clear(i: int, j: int) -> bool:
        seg = LineString([nodes[i], nodes[j]])
        if j == last:  # the leg into the tap: its last `intake` ft is the intake
            if seg.length <= intake:
                return True
            cut = seg.interpolate(seg.length - intake)
            seg = LineString([nodes[i], (cut.x, cut.y)])
        return not seg.intersects(core)

    best = {0: 0.0}
    prev: dict[int, int] = {}
    todo = set(range(len(nodes)))
    while True:  # Dijkstra over a graph of tens of nodes: the nearest unsettled node, settled in turn
        i = min((k for k in todo if k in best), key=best.__getitem__, default=None)
        if i is None or i == last:
            break
        todo.discard(i)
        for j in todo:
            nd = best[i] + math.dist(nodes[i], nodes[j])
            if nd < best.get(j, math.inf) and clear(i, j):
                best[j], prev[j] = nd, i
    if last not in prev:
        return [start]  # enclosed on every side - see the docstring
    path, k = [], last
    while k in prev:
        k = prev[k]
        path.append(nodes[k])
    return path[::-1]


def draw_intake(s: Settlement, plan: SitePlan, sluice: Pt) -> None:
    """What stands where the head race leaves the brook - a WEIR, or nothing at all.

    The record attests both and gives no proportion, so `plan.intake` is rolled per map
    (research/water.html, "Is there a weir at the intake?"). On an `open`
    hamlet the point is marked by the junction itself: the brook runs straight on and the race opens out of its
    bank at an acute angle (`open_race_mouth`), which is a fork a reader can see - no gate or boards, none being
    recorded at a village intake (research/water/310). On a `weir` hamlet a bar crosses the brook, set OBLIQUE -
    the old weirs ran diagonally upstream from the intake mouth, damming the shallow riffle and standing clear of
    the flood's fastest water - built in one of four forms rolled per hamlet (`WEIR_FORM`, research/water/300).

    One disclosed liberty, in the entry: the bar is drawn as a FULL closure of the brook, a map drawing convention,
    because a half-river closure - the common old form - is a pixel or two at a 7 ft brook. Each form's thickness is
    `WEIR_THICK_FT`'s, with its class beside it."""
    if plan.intake != "weir":
        return
    form = s.M["meta"]["weir_form"] = s.resolve("weir_form")
    nxt = next((q for q in plan.brook[plan.brook.index(sluice) + 1 :]), None) if sluice in plan.brook else None
    hx, hy = unit(nxt[0] - sluice[0], nxt[1] - sluice[1]) if nxt else plan.fall
    # THE WEIR STANDS BELOW THE MOUTH AND SLANTS UP FROM THE INTAKE BANK (settlement-review, feature 230 pass 10). The
    # bar was centered ON the intake point and skewed by a fixed turn that ignored which bank the race leaves from, so on
    # Kashikawa the head race took its water 0.6 ft below the downstream face - from the tailwater, not from the pool the
    # weir raises - and the bar ran diagonally DOWNSTREAM from the intake bank, which steers the flow away from the
    # intake. The sheet's own weir modal says the opposite, and so does the record: the bar runs diagonally upstream from
    # the intake mouth. So the intake bank is found from the race's own bearing, the bar's end on that bank is its
    # downstream end, and the whole bar is set just below the mouth.
    rx, ry = math.cos(math.radians(plan.head_deg)), math.sin(math.radians(plan.head_deg))
    nx, ny = (-hy, hx) if hx * ry - hy * rx >= 0.0 else (hy, -hx)  # the unit normal pointing to the intake bank
    skew = math.tan(math.radians(WEIR_SKEW_DEG))
    ax, ay = unit(-nx - hx * skew, -ny - hy * skew)  # from the intake bank's (downstream) end toward the far bank, upstream
    ang = math.atan2(ay, ax)
    half, half_t = WEIR_HALF_FT / plan.ftpx, WEIR_THICK_FT[form] / plan.ftpx / 2.0
    # ...AND CLEAR OF THE MOUTH ITSELF, not merely of the junction point (settlement-review, feature 230 pass 11). The race
    # leaves at `OFFTAKE_DEG`, so its opening cuts the bank over `w / sin(offtake)` - about 10 ft at Kashikawa's 6 ft race -
    # and a bar set a pixel below the junction stood IN that opening, with a third of the mouth in the tailwater. The bar
    # clears half the opening as well as its own half-thickness.
    _race = next((c for c in (plan.net or {}).get("channels") or [] if c.get("role") == "main"), None) or next(iter((plan.net or {}).get("channels") or []), None)
    _race_w = float(_race.get("w", 6.0)) if _race else 6.0
    _mouth = _race_w / max(math.sin(math.radians(OFFTAKE_DEG)), 0.2)
    # ...AND ITS ROOT KEYS INTO THE BANK CLEAR OF THE RACE (feature 287, water:W09; future-work "The weir's root lands on the
    # head race's mouth"): set below the mouth by the opening alone, the bar's intake-bank end - which the skew carries
    # further downstream and out past the bank - still lay on the race, 17% of the bar on all three weir maps, reading as a
    # gate across the ditch. The bar steps down the brook, a foot at a time, from that first seat to the first where none of
    # it lies on the race's stroke (`bar_on_race`): the root then keys into the bank at the mouth's downstream lip, the mouth
    # still in the pool the weir raises (pass 10's rule) and not under the bar. The race leaves at `OFFTAKE_DEG` and the
    # bar's end at the skew, so the two diverge and a clear seat exists within a few bar-lengths; the design row's "upstream
    # lip" would have put the mouth in the tailwater, which pass 10 measured and refused.
    _race_pts = [(float(x), float(y)) for x, y in _race["pts"]] if _race else []
    off = half_t + _mouth / 2.0 + 1.0  # below the mouth, not in it
    while True:
        cx, cy = sluice[0] + hx * off, sluice[1] + hy * off
        poly = [
            (cx + ax * half + hx * half_t, cy + ay * half + hy * half_t),
            (cx - ax * half + hx * half_t, cy - ay * half + hy * half_t),
            (cx - ax * half - hx * half_t, cy - ay * half - hy * half_t),
            (cx + ax * half - hx * half_t, cy + ay * half - hy * half_t),
        ]
        if bar_on_race(poly, _race_pts, _race_w) <= 1e-9:  # the race is a finite stroke, so a seat past its end always clears it
            break
        off += 1.0
    s.M.setdefault("weirs", []).append(
        {
            "x": round(cx, 1),
            "y": round(cy, 1),
            "len": round(2 * half, 1),
            "w": round(2 * half_t, 1),
            "deg": round(math.degrees(ang) % 180.0, 1),
            "form": form,
            "poly": [[round(x, 1), round(y, 1)] for x, y in poly],
        }
    )
    s.add(weir_glyph(form, poly, (cx, cy), (ax, ay), (hx, hy), half, half_t), cls="weir")


def open_race_mouth(s: Settlement, sluice: Pt) -> None:
    """The head race OPENS OUT OF THE BROOK'S BANK (269 B22; research/water/310, "What does the intake mouth look like").

    The attested bare intake is an opening: "water can easily be taken just by providing an entrance for it", a
    damless intake "opening a mouth at the concave side". So the ditch begins at the bank's edge, and nothing of it is
    drawn on the stream. It was: `field_channel` trims a channel's end to just inside the bank and the race's bed is
    in the late water block, painted after the brook, so its round cap printed a blob of ditch-colored water across
    the brook at every intake - a channel laid on top of the stream rather than one leaving it. Trimming harder cannot
    cure it: the race leaves at `OFFTAKE_DEG`, so any square or round end cuts the bank on a slant and leaves a notch
    of bare ground on one side or a tongue in the water on the other. The mouth is cut BY THE BANK instead: the race's
    first stroke is carried back to the tap on the brook's centerline, and the brook's bed is moved to paint after it,
    so the brook's own edge is where the ditch begins. No gate and no boards are drawn: none is recorded at a village
    intake, and at a two-foot opening either would be smaller than the map can show.

    Beds share one opacity group (`_water`), so the brook painting over the race is a join, not a darker seam. A brook
    with a pond `clip` is not moved (its bed is re-emitted at flush from the early list); a hamlet's brook has none."""
    tap = (float(sluice[0]), float(sluice[1]))
    brook = next((st for st in s.M.get("streams", []) if any(math.dist(tap, (float(q[0]), float(q[1]))) < 0.5 for q in st["poly"])), None)
    entry = next((w for w in s.water if w["rec"] is brook and w.get("clip") is None), None) if brook is not None else None
    if brook is None or entry is None:
        return
    reach = float(brook.get("w", 7)) / 2.0 + 8.0  # a race trimmed at this bank starts within this of the tap
    for w in s.late_water:
        pts = w["rec"].get("pts")
        if pts and 0.05 < math.dist(tap, (float(pts[0][0]), float(pts[0][1]))) <= reach:
            w["bed"] = re.sub(r' d="M', f' d="M{tap[0]:.1f},{tap[1]:.1f} L', w["bed"], count=1)
            pts.insert(0, [round(tap[0], 1), round(tap[1], 1)])
            break
    s.water.remove(entry)
    s.late_water.append(entry)


def weir_glyph(form: str, poly: Sequence[Pt], c: Pt, along: Pt, down: Pt, half: float, half_t: float) -> str:
    """The SVG of a weir bar by its FORM (269 B22, research/water/300), inside the bar's own `poly`.

    A WEIR IS NOT A BRIDGE, and it was drawn as one: the same brown oblique bar as the nine footbridges on the reference
    hamlet's own sheet, which `settlement-review` read as "the crossing" - actively misleading, since it is the only bar
    over the brook. So every form says what a weir does: a lip along the UPSTREAM face, the one thing a weir has and a
    bridge cannot - it holds water back - and a body that no deck on the map shares:

    - `crib`, timber packed with stone: stone gray, the crib's baulks ticked across it (the glyph before the knob);
    - `frame`, stakes and logs packed with clay: clay brown-gray, the logs drawn along it and the stakes as dots;
    - `gabion`, stone-filled baskets: gray, the baskets' seams across it and the weave hatched on the diagonal;
    - `fence`, stakes with brushwood woven between them: a thin straw-colored band with its stakes as dark dots."""
    cx, cy = c
    ax, ay = along
    hx, hy = down

    def at(t: float, v: float) -> Pt:  # a point `t` of the half-length along the bar and `v` of the half-thickness downstream
        return (cx + ax * half * t + hx * half_t * v, cy + ay * half * t + hy * half_t * v)

    def line(p: Pt, q: Pt, stroke: str, width: float) -> str:
        return f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="{stroke}" stroke-width="{width}"/>'

    def dots(v: float, n: int, r: float, fill: str) -> str:  # stakes: `n` evenly along the bar at depth `v`
        return "".join(f'<circle cx="{at(-0.9 + 1.8 * k / (n - 1), v)[0]:.1f}" cy="{at(-0.9 + 1.8 * k / (n - 1), v)[1]:.1f}" r="{r}" fill="{fill}"/>' for k in range(n))

    fill, stroke = {"crib": ("#9A9A90", "#63645C"), "frame": ("#A08C72", "#5E4A34"), "gabion": ("#A3A196", "#63645C"), "fence": ("#B9A86E", "#6E5E36")}[form]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
    body = [f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="0.9" stroke-linejoin="round"/>']
    if form == "crib":
        body += [line(at(t, -1.0), at(t, 1.0), "#6E6A60", 0.7) for t in (-0.62, -0.2, 0.2, 0.62)]
    elif form == "frame":
        body += [line(at(-0.95, v), at(0.95, v), "#6B5238", 0.8) for v in (-0.45, 0.45)]  # the logs laid along the stakes
        body.append(dots(0.0, 5, 0.7, "#4E3A26"))  # the stakes holding them
    elif form == "gabion":
        body += [line(at(t, -1.0), at(t, 1.0), "#6E6A60", 0.6) for t in (-0.5, 0.0, 0.5)]  # one basket to the next
        body += [line(at(t - 0.12, -1.0), at(t + 0.12, 1.0), "#7E7A70", 0.4) for t in (-0.75, -0.25, 0.25, 0.75)]  # the weave
    else:
        body.append(dots(0.0, 6, 0.55, "#4E3A26"))
    body.append(
        f'<line x1="{poly[3][0]:.1f}" y1="{poly[3][1]:.1f}" x2="{poly[2][0]:.1f}" y2="{poly[2][1]:.1f}" stroke="#8FA6AE" stroke-width="{min(1.6, 1.2 * half_t):.1f}" stroke-linecap="round"/>'
    )  # the lip, never wider than a thin bar's own half
    return "".join(body)
