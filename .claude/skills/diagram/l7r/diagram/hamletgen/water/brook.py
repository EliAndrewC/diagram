"""THE BROOK (feature 230) - the stream that is tapped at an intake and runs on past the fan, and what stands at the tap.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, knob_rng
from l7r.diagram.sitegen.geom import crosses_poly, unit

from ..consts import (
    BROOK_FRAME_MARGIN,
    BROOK_SKIRT,
    BROOK_TAP_RUN,
    BROOK_WANDER,
    BROOK_WANDER_STEP,
    WEIR_HALF_FT,
    WEIR_SKEW_DEG,
    WEIR_THICK_FT,
    Poly,
    Pt,
)
from ..plan import SitePlan


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
            out[i + 1] = (bx + away[0] * nudge, by + away[1] * nudge)
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
        v = _v_within(u, floor, floor + stray, (dx, dy), (px, py), box)
        out.append((u * dx + v * px, u * dy + v * py))
    # ...and off the frame from the last station, still wandering, the run measured along the fall from there.
    # THE FIRST EXIT LEG KEEPS THE COURSE'S OWN HEADING and only then turns onto the fall: driving it straight
    # downhill from a station that is well out to the side puts a corner exactly where the brook should be
    # running off the sheet (121 degrees on one map, and the sharpest thing on it).
    lx, ly = out[-1]
    edge = [((plan.W if dx > 0 else 0.0) - lx) / dx if abs(dx) > 1e-6 else 1e9, ((plan.H if dy > 0 else 0.0) - ly) / dy if abs(dy) > 1e-6 else 1e9]
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
    for f, blend in ((0.22, 0.3), (0.26, 0.6), (0.26, 0.85), (0.26, 1.0)):
        hx, hy = unit(heading[0] * (1.0 - blend) + dx * blend, heading[1] * (1.0 - blend) + dy * blend)
        px_, py_ = px_ + hx * span * f, py_ + hy * span * f
        out.append((px_, py_))

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
    return _off_the_axes([*cut, *keep_tail], (px, py), hold=2)  # the tap run: two cut points on the fall, and the segment that leaves it


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
    legitimately against the crop and is not tested."""
    dx, dy = plan.fall
    base = math.degrees(math.atan2(-dy, -dx))  # upslope
    for swing in sorted((10.0 * k for k in range(-7, 8)), key=abs):
        th = math.radians(base + swing)
        up = (sluice[0] + math.cos(th) * run, sluice[1] + math.sin(th) * run)
        mid = ((up[0] + sluice[0]) / 2 - math.sin(th) * 26, (up[1] + sluice[1]) / 2 + math.cos(th) * 26)
        near = (sluice[0] + math.cos(th) * 40, sluice[1] + math.sin(th) * 40)  # the last 40 px is the intake itself
        if not (crosses_poly(up, mid, plan.envelope) or crosses_poly(mid, near, plan.envelope)):
            # the APPROACH wanders too. It was one ruled 420 ft line into the tap - 211 ft of it in frame, and
            # the reviewer counted it among the third of the course with no meander at all; a brook that is a
            # stream below its tap and a drawn line above it is not one brook.
            wob = knob_rng(plan.spec.seed, "brook_approach")
            legs = [up, mid]
            for t in (0.45, 0.68, 0.86):
                qx, qy = mid[0] + (sluice[0] - mid[0]) * t, mid[1] + (sluice[1] - mid[1]) * t
                j = wob.uniform(-16.0, 16.0)
                legs.append((qx - math.sin(th) * j, qy + math.cos(th) * j))
            return [*legs, sluice, *brook_skirt(plan, sluice, plan.brook_side, crop)]
    up = (
        sluice[0] - dx * run,
        sluice[1] - dy * run,
    )  # pragma: no cover - a fan head never blocks all fifteen [174: KEPT, not deletable - the loop's terminal; without it the function returns None where a route is promised]
    return [
        up,
        ((up[0] + sluice[0]) / 2 + dy * 26, (up[1] + sluice[1]) / 2 - dx * 26),
        sluice,
        *brook_skirt(plan, sluice, plan.brook_side, crop),
    ]  # pragma: no cover - the same unreachable fallback, one line down [174: KEPT, not deletable - part of that same terminal return]


def draw_intake(s: Settlement, plan: SitePlan, sluice: Pt) -> None:
    """What stands where the head race leaves the brook - a WEIR, or nothing at all.

    The record attests both and gives no proportion, so `plan.intake` is rolled per map
    (research/water.html, "Where does the brook stop being a brook and become the ditch"). On an `open`
    hamlet the point is marked by the junction itself: the brook runs straight on and the race leaves its
    bank at an acute angle, which is a fork a reader can see. On a `weir` hamlet a bar of stone-packed
    timber crib crosses the brook, set OBLIQUE - the old weirs ran diagonally upstream from the intake
    mouth, damming the shallow riffle and standing clear of the flood's fastest water.

    Two disclosed liberties, both in the entry: the bar is drawn as a FULL closure of the brook, a map
    drawing convention, because a half-river closure - the common old form - is a pixel or two at a 7 ft
    brook; and its thickness is a guess, the histories giving cross-sections only for river weirs."""
    if plan.intake != "weir":
        return
    nxt = next((q for q in plan.brook[plan.brook.index(sluice) + 1 :]), None) if sluice in plan.brook else None
    hx, hy = unit(nxt[0] - sluice[0], nxt[1] - sluice[1]) if nxt else plan.fall
    ang = math.atan2(hy, hx) + math.radians(90.0 + WEIR_SKEW_DEG)
    ax, ay = math.cos(ang), math.sin(ang)
    half, half_t = WEIR_HALF_FT / plan.ftpx, WEIR_THICK_FT / plan.ftpx / 2.0
    poly = [
        (sluice[0] + ax * half + hx * half_t, sluice[1] + ay * half + hy * half_t),
        (sluice[0] - ax * half + hx * half_t, sluice[1] - ay * half + hy * half_t),
        (sluice[0] - ax * half - hx * half_t, sluice[1] - ay * half - hy * half_t),
        (sluice[0] + ax * half - hx * half_t, sluice[1] + ay * half - hy * half_t),
    ]
    s.M.setdefault("weirs", []).append(
        {
            "x": round(sluice[0], 1),
            "y": round(sluice[1], 1),
            "len": round(2 * half, 1),
            "w": round(2 * half_t, 1),
            "deg": round(math.degrees(ang) % 180.0, 1),
            "poly": [[round(x, 1), round(y, 1)] for x, y in poly],
        }
    )
    # A WEIR IS NOT A BRIDGE, and it was drawn as one: the same brown oblique bar as the nine footbridges on
    # the reference hamlet's own sheet, which `settlement-review` read as "the crossing" - actively misleading,
    # since it is the only bar over the brook. So the glyph says what a weir does instead. Stone gray rather
    # than timber brown, because the bar is crib-work packed with stone and the map's timber decks are brown;
    # the crib's own baulks ticked across it, which a plank deck's single stripe cannot be mistaken for; and a
    # lip along the upstream face, the one thing a weir has and a bridge cannot - it holds water back.
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in poly)
    ticks = "".join(
        f'<line x1="{sluice[0] + ax * half * t - hx * half_t:.1f}" y1="{sluice[1] + ay * half * t - hy * half_t:.1f}" '
        f'x2="{sluice[0] + ax * half * t + hx * half_t:.1f}" y2="{sluice[1] + ay * half * t + hy * half_t:.1f}" stroke="#6E6A60" stroke-width="0.7"/>'
        for t in (-0.62, -0.2, 0.2, 0.62)
    )
    lip = f'<line x1="{poly[3][0]:.1f}" y1="{poly[3][1]:.1f}" x2="{poly[2][0]:.1f}" y2="{poly[2][1]:.1f}" stroke="#8FA6AE" stroke-width="1.6" stroke-linecap="round"/>'
    s.add(f'<polygon points="{pts}" fill="#9A9A90" stroke="#63645C" stroke-width="0.9" stroke-linejoin="round"/>{ticks}{lip}', cls="weir")
