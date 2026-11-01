"""THE BROOK'S COURSE (feature 230) - the shape of the course below and beyond the tap, and the course as the map draws it.

Split from `brook.py` by feature 316 (constitution X clause 13); bodies verbatim, and `brook.py` re-exports every name:
the exit off the frame, the reflecting wander, the crop's cross-section, the frame bound, the unfold, the rounding with
the taps and confluences held, and the screen-axis backstop. Leaf helpers only - `brook.py`'s placer, repair and
judgment, which the tests patch, stay there.

Research: plumbing - NONE: every unit that decides something carries its own claims
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement._geom import fillet_polyline

from ..consts import BROOK_BEND_WIDTHS, Poly, Pt
from .brook_rules import BROOK_DRAWN_W


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
        its fallback brook width - research/questions/0059-where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki.drawing.html: a brook whose record has no `w` taken at `BROOK_DRAWN_W`, the page's brook about 5.25 ft
    """
    chans = [c for c in s.M.get("channels") or [] if len(c.get("poly") or ()) >= 2]
    heads = [(float(c["poly"][0][0]), float(c["poly"][0][1])) for c in chans if (c.get("frm") or {}).get("kind") == "stream"]
    joins = [(float(c["poly"][-1][0]), float(c["poly"][-1][1])) for c in chans if (c.get("to") or {}).get("kind") == "stream"]
    for rec in s.M.get("streams") or []:
        course = rec.get("stations") or rec.get("poly") or []
        if len(course) < 3:
            continue
        s.round_stream(rec, drawn_course(course, heads, joins, float(rec.get("w") or BROOK_DRAWN_W)))


def drawn_course(course: Sequence[Pt], taps: Sequence[Pt], joins: Sequence[Pt] = (), w: float = BROOK_DRAWN_W) -> Poly:
    """The brook AS THE MAP DRAWS IT (feature 287 wave 5): every tap and confluence on `course` made a vertex and held
    (`join_vertices` - a confluence on a corner left to the rounding), then rounded (`finished_course`). The ONE geometry
    `round_the_brooks` draws and `brook_violations` judges, so a confluence the sink adds after the brook was judged is
    judged with it - where the rounding round a held join changed the course, the judged and the drawn used to differ."""
    pts, held = join_vertices(course, taps)
    pts, held_j = join_vertices(pts, joins, hold_corners=False)
    return finished_course(pts, w, held + held_j)
