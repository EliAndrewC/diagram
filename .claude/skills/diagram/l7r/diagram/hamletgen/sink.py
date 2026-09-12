"""STAGE 3: where the runoff goes - the drain and the tameike it feeds.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

from __future__ import annotations

import math

from l7r.diagram.settlement import Settlement, point_in_poly, seg_closest
from l7r.diagram.settlement.land.wet import pond_fringe_ring
from l7r.diagram.settlement.water_ways.water import DRAIN_HUE, DRAINAGE_DITCH
from l7r.diagram.sitegen.geom import crosses_poly, unit
from l7r.diagram.waterfields import DRAIN_FT, chan_px

from .consts import GRAIN, POND_SETBACK_LIMIT, REF_HOUSEHOLDS, Poly, Pt
from .plan import SitePlan

# ---- STAGE 3: where the runoff goes -------------------------------------------------------------


def drain_outfall(s: Settlement, name: str) -> Pt | None:
    """The last vertex of the field's drain collector, READ BACK from the manifest.

    Read back rather than remembered, because the manifest is what the gate reads: siting the pond
    from the same record `pond_connected_to_field` will measure against is the skill's "placement and
    its check must read the SAME manifest source" rule, one level down."""
    for ditch in s.M.get("field_ditches", []):
        if ditch.get("role") == "drain" and ditch.get("field") == name:
            pts = ditch["poly"]
            return (float(pts[-1][0]), float(pts[-1][1]))
    return None


# THE SPAN THE GATE MEASURES A JUNCTION OVER. `drainage_junction_smooth` does not read a watercourse's
# final vertex pair; it calls `_flow_dir(poly, at_start=..., span=40.0)`, which walks back from the end
# until it is at least 40 px away and takes the bearing over THAT chord. Mirrored here as a named
# constant so the placer optimizes the number the gate will actually compute - if the gate's span ever
# moves, this is the one line to move with it. (Diagnosed 2026-08-17; see `drain_heading` below.)
GATE_FLOW_SPAN = 40.0


def drain_heading(s: Settlement, name: str, span: float = GATE_FLOW_SPAN) -> Pt | None:
    """The direction the drain collector is running where it ends - so its continuation leaves it as
    a smooth junction rather than a hard corner.

    MEASURED OVER THE GATE'S 40 px SPAN, NOT OVER THE FINAL VERTEX PAIR, and that distinction is the
    whole defect this function used to carry. A comb's collector ends in a short hook - its last
    segment can be a couple of px long and point anywhere - so "the direction it is running where it
    ends" read off `poly[-2] -> poly[-1]` is noise, while `drainage_junction_smooth` reads the same
    corner over 40 px and gets the collector's real bearing. On cohort seed 2 the two disagreed by
    76.1 deg (last-pair 347.1, span 63.3): the placer therefore believed that continuing straight
    along the collector was a PERFECT junction (turn 0.0) when the gate scored that same route a
    76.1 deg kink, and it believed the genuinely smooth route (2.2 deg by the gate) was a 73.9 deg
    corner and refused it. One corner, two verdicts, split by the definition - the same "placement
    and its check must read the SAME manifest source" rule `drain_outfall` above obeys, one level
    down."""
    for ditch in s.M.get("field_ditches", []):
        if ditch.get("role") == "drain" and ditch.get("field") == name and len(ditch["poly"]) >= 2:
            pts = ditch["poly"]
            end = pts[-1]
            ref = end
            for q in pts[-2::-1]:  # walk back up the collector until the chord is long enough to mean something
                ref = q
                if math.hypot(float(q[0]) - float(end[0]), float(q[1]) - float(end[1])) >= span:
                    break
            return unit(float(end[0]) - float(ref[0]), float(end[1]) - float(ref[1]))


def drain_run(s: Settlement, pts: Poly, to: str) -> None:
    """The collector's continuation past its outfall - a DRAINAGE DITCH whichever way the water goes.

    Feature 230 (GM 2026-09-12): the run into the tameike was drawn by `field_channel` and the run off
    the frame by `stream` at 8 px, so the same thing carried two classes and two record kinds on two
    maps ("the inconsistency you mentioned"). The research settled what it is: before modern field
    consolidation a village's drainage went field to field, or back into a shared channel, and returned
    to the river to be taken up below (`research/water.html`, "Where does the water go once it has
    watered the paddies") - a dug channel that reaches a watercourse, never a brook of its own. So every
    sink draws the same stroke: the collector's tail width, the drain's hue, the drainage-ditch class.

    WIDTH IS THE DRAIN'S OWN, NOT A LITERAL. This is the collector's last strides, so it carries everything
    the collector carries - a flat 2.5 px stub at the pond mouth read as a pinch rather than a mouth on the
    sheet's most visible water feature (`settlement-review`, at true scale). Derived from `DRAIN_FT[1]` so it
    tracks any change to the ladder.

    ...but the TOPOLOGY record stays at the hairline. `M["channels"]` is the connectivity graph the anchor
    checks walk, and its widths are held in a hairline band on purpose (a natural watercourse must
    out-measure a field ditch by a wide margin). The DRAWN truth lives in `M["drawn_channels"]`, which is
    where `field_channel` records the widened stroke. Writing the drawn width into the topology record
    instead fired two checks on 14 cohort maps apiece - measured, not guessed.

    RESERVE IT AS A NO-BUILD CORRIDOR. `s.channel` and `s.stream` register one; `s.field_channel` does not -
    fine for the comb's own ditches inside a blocked envelope, wrong for this one, which runs OUT of the field
    across open margin where the placer is free to seat a homestead on it."""
    outfall_w = chan_px(DRAIN_FT[1], GRAIN)
    s.field_channel(pts, DRAIN_HUE, outfall_w, outfall_w, cls=DRAINAGE_DITCH)
    s.M["channels"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in pts], "frm": {"kind": "drain"}, "to": {"kind": to}, "w": 2.5})
    s.corridors.append((list(pts), 33.0))


def edge_run(plan: SitePlan, frm: Pt) -> float:
    """Distance from `frm` to the canvas edge along the fall - how far a watercourse has to run to
    leave the map from here."""
    dx, dy = plan.fall
    spans = []
    if abs(dx) > 1e-6:
        spans.append(((plan.W if dx > 0 else 0.0) - frm[0]) / dx)
    if abs(dy) > 1e-6:
        spans.append(((plan.H if dy > 0 else 0.0) - frm[1]) / dy)
    return max(0.0, min(spans)) if spans else 0.0


def pond_clear_of_crop(plan: SitePlan, center: Pt, prx: float, pry: float) -> bool:
    """The two tests `pond_clear_of_field` makes, on the same envelope: no rim point inside the crop,
    no crop vertex inside the pond."""
    env = list(plan.envelope)
    rim = [(math.cos(a), math.sin(a)) for a in [i * math.pi / 12 for i in range(24)]]
    if any(point_in_poly(center[0] + prx * ux, center[1] + pry * uy, env) for ux, uy in rim):
        return False
    return not any(((v[0] - center[0]) / prx) ** 2 + ((v[1] - center[1]) / pry) ** 2 <= 1.0 for v in env)


def pond_setback(plan: SitePlan, out: Pt, prx: float, pry: float, step: float = 14.0, limit: float = 900.0) -> float:
    """How far DOWNSLOPE of the drain outfall the pond must stand to clear the crop entirely.

    Walks outward in small steps and returns the first distance at which no rim point of the ellipse
    falls inside the field envelope and no envelope vertex falls inside the ellipse - the same two
    tests `pond_clear_of_field` makes, run against the same envelope, so the siting and the check
    cannot disagree (the skill's "adjudicate against the gate, never a re-statement of it" rule, in
    its cheap form: the predicate is copied from the check and measured on the same manifest
    geometry). A 12 px cushion past the first clear position keeps it off the line."""
    dx, dy = plan.fall
    env = list(plan.envelope)
    rim = [(math.cos(a), math.sin(a)) for a in [i * math.pi / 12 for i in range(24)]]
    d = pry + 46.0  # never closer than a rim's worth below the outfall, whatever the geometry says
    while d <= limit:
        cx, cy = out[0] + dx * d, out[1] + dy * d
        clear = not any(point_in_poly(cx + prx * ux, cy + pry * uy, env) for ux, uy in rim)
        if clear:
            clear = not any(((v[0] - cx) / prx) ** 2 + ((v[1] - cy) / pry) ** 2 <= 1.0 for v in env)
        if clear:
            # ...and clear of the BROOK, which since feature 230 runs on down one flank of the fan and can
            # pass exactly where the reservoir wants to stand. Measured against the pond's OWN ellipse plus a
            # rim's margin, never a circle of its long radius: at 116 x 74 px that circle is half again the
            # pond across its short axis, and it cost Mizuguchi's tameike its seat - the stage fell back to
            # draining off the frame and the map lost the reservoir it is named for. A brook running past a
            # reservoir's shoulder is a normal thing to draw; a brook through the water is not.
            clear = all(
                ((seg_closest(cx, cy, a, b)[0] - cx) / (prx + 12.0)) ** 2 + ((seg_closest(cx, cy, a, b)[1] - cy) / (pry + 12.0)) ** 2 > 1.0 for a, b in zip(plan.brook, plan.brook[1:], strict=False)
            )
        if clear:
            return d + 12.0
        d += step
    return limit


#: How much BROOK must remain below the confluence, px. A junction drawn at the frame's edge is not a
#: junction a reader can see - `settlement-review` measured Sawada's joined trunk at 4.5 ft before the crop
#: cut it, two lines leaving the map at one point rather than a tributary entering a stream. A road running
#: off the frame implies more beyond; a junction implies nothing.
BROOK_JOIN_TRUNK = 150.0
#: How much of the run from the outfall to the confluence may lie inside the crop before the route is
#: refused. The outfall is AT the field's edge and a comb's envelope bows out around its own collector, so
#: the first strides of any route from it are legitimately on the crop's own ground - which is why the gate
#: trims a brook's leading vertices before it judges one (`streams_avoid_fields`). Anything past this is a
#: ditch driven through the rice.
BROOK_JOIN_LEAD = 0.3
#: How far the confluence must have FALLEN below the outfall, px. A drain runs downhill into the brook it
#: joins, and a junction level with the outfall is neither a fall nor a join; a stride of the collector's
#: own tail width is enough to read as one on the sheet.
BROOK_JOIN_DESCENT = 20.0


def _through_the_crop(plan: SitePlan, out: Pt, q: Pt) -> bool:
    """Would a ditch from the outfall to `q` run through the rice - past the crop edge the outfall stands on?

    Lifted out of `brook_join` so the exemption can be tested on a square (feature 146's rule). The route
    is walked from the outfall until it is clear of the envelope; leaving within `BROOK_JOIN_LEAD` of the
    run is the field's own edge and is exempt, and the rest of the route is judged in full."""
    lead = next((t / 20.0 for t in range(21) if not point_in_poly(out[0] + (q[0] - out[0]) * t / 20.0, out[1] + (q[1] - out[1]) * t / 20.0, plan.envelope)), 1.0)
    if lead > BROOK_JOIN_LEAD:
        return True
    frm = (out[0] + (q[0] - out[0]) * lead, out[1] + (q[1] - out[1]) * lead)
    return crosses_poly(frm, q, plan.envelope)


def brook_join(plan: SitePlan, out: Pt, reach: float = 420.0, stride: float = 10.0) -> Pt | None:
    """Where the collector meets the brook that passes the field, or None if it does not pass near.

    The third sink, and the researched one (feature 230): before modern consolidation a village's
    drainage went back to the watercourse to be taken up by the district below, so where the brook the
    field is fed from runs on within reach of the collector's outfall, the drain runs to it and joins it
    at a confluence. The candidate must lie downslope, be within reach, and be reachable without crossing
    the crop; without one the runoff leaves the frame as before.

    THE NEAREST POINT ON THE BROOK IS THE WRONG CANDIDATE, and taking it is what hid this sink on the two
    maps that most wanted it. A brook running down the flank passes ABREAST of the outfall, so its closest
    point is level with it or a few feet above - Sawada's was 80 px away and 4 px uphill - and a test for
    "downslope" then refuses the join and sends the drain off the frame on its own, two watercourses
    leaving the map side by side. So the brook is walked at a stride and only the points that have
    genuinely fallen are considered; the nearest of THOSE is the confluence, a little way down the brook
    from where it passes. `BROOK_JOIN_DESCENT` is what makes the junction a junction rather than a level
    meeting."""
    dx, dy = plan.fall
    best: tuple[float, Pt] | None = None
    legs = list(zip(plan.brook, plan.brook[1:], strict=False))
    # THE TRUNK IS MEASURED IN THE PICTURE, NOT ALONG THE COURSE (feature 230, settlement-review pass 6).
    # `BROOK_JOIN_TRUNK` exists so a confluence is not drawn at the frame's edge with nothing below it to read,
    # and it was measured as ARC LENGTH - which a brook can spend entirely off the sheet. Sawada's join came out
    # 6 ft inside the view of a 2,091 ft-wide picture with all 359 ft of its joined trunk outside the canvas, so
    # the rule's own defect was available to it. The frame is not decided until `stage_frame`, four stages later,
    # but its floor is: the crop always contains the field, and the scatter's own predicted frame (feature 224)
    # grows the crop boxes by 48 + 120. So the trunk is counted only where it lies inside the field's box grown
    # by that margin - a conservative reading of the picture, which is the safe direction for a rule that exists
    # to keep a junction ON the sheet.
    _fx = [q[0] for q in plan.envelope] or [0.0, float(plan.W)]
    _fy = [q[1] for q in plan.envelope] or [0.0, float(plan.H)]
    _pic = (min(_fx) - 168.0, min(_fy) - 168.0, max(_fx) + 168.0, max(_fy) + 168.0)

    def _seen(c: Pt, d: Pt) -> float:
        """How much of the leg c->d lies inside the predicted picture, sampled at the walk's own stride."""
        n = max(1, int(math.hypot(d[0] - c[0], d[1] - c[1]) / stride))
        inside = sum(1 for i in range(n + 1) if _pic[0] <= c[0] + (d[0] - c[0]) * i / n <= _pic[2] and _pic[1] <= c[1] + (d[1] - c[1]) * i / n <= _pic[3])
        return math.hypot(d[0] - c[0], d[1] - c[1]) * inside / (n + 1)

    below = [sum(_seen(c, d) for c, d in legs[k + 1 :]) for k in range(len(legs))]
    for k, (a, b) in enumerate(legs):
        run = math.hypot(b[0] - a[0], b[1] - a[1])
        for i in range(int(run / stride) + 1):
            t = min(1.0, i * stride / run) if run else 0.0
            if below[k] + _seen((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), b) < BROOK_JOIN_TRUNK:
                continue  # the join would sit at the frame's edge with no trunk to read
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            d = math.hypot(q[0] - out[0], q[1] - out[1])
            if d > reach or (q[0] - out[0]) * dx + (q[1] - out[1]) * dy < BROOK_JOIN_DESCENT:
                continue
            if _through_the_crop(plan, out, q):
                continue
            if best is None or d < best[0]:
                best = (d, q)
    return best[1] if best else None


def pond_seat(plan: SitePlan, out: Pt, prx: float, pry: float) -> tuple[float, float]:
    """(how far downslope, how far across the fall) the reservoir must stand to clear the crop AND the
    brook - the set-back search with one more degree of freedom.

    The walk downslope alone was enough while the brook stopped at the intake. Since feature 230 it runs
    on down one flank of the fan, and on a map whose flank is the drain's own side the two want the same
    ground: Mizuguchi's tameike - the reservoir the place is named for - was pushed past the canvas and
    the stage fell back to draining off the frame, losing a feature its spec had declared. Stepping the
    pond ACROSS the fall is the cheaper move and the truer one: a valley's reservoir sits in whatever
    pocket the ground offers below the fields, not on a plumb line under the outfall. The sways are
    tried nearest-first and the straight seat still wins whenever it is clear, so every map whose pond
    already had room keeps the seat it had."""
    for sway in (0.0, -0.9 * prx, 0.9 * prx, -1.8 * prx, 1.8 * prx):
        moved = (out[0] - plan.fall[1] * sway, out[1] + plan.fall[0] * sway)
        back = pond_setback(plan, moved, prx, pry)
        if back <= POND_SETBACK_LIMIT:
            return back, sway
    return POND_SETBACK_LIMIT + 1.0, 0.0


def stage_sink(s: Settlement, plan: SitePlan) -> None:
    """The tameike the field drains into - DERIVED from the drain, never placed by hand.

    A reservoir below the fields is sited by one fact: it must sit clear of the paddies and low
    enough that the drain reaches it downhill. So it goes a fixed set-back DOWNSLOPE of the drain's
    own outfall, wherever that outfall landed, and the drainage ditch is drawn from the outfall to
    the pond's center so the two are visibly joined. Both scale with the map: a bigger hamlet drains
    more water into a bigger pond.

    `water_sink="offmap"` draws the collector's continuation off the frame instead of a pond - a drainage
    ditch like the pond run (`drain_run`), which is what most valleys do and what the GM's brief allows."""
    name = f"{plan.spec.name.lower()}-paddies"
    out = drain_outfall(s, name)
    if out is None:
        return
    dx, dy = plan.fall
    if plan.water_sink != "pond":
        # OFF THE FRAME: the collector's brook runs on downhill and leaves the map, to join a stream
        # or another farm's drain somewhere the map does not have to care about. Its LENGTH is
        # derived per bearing below - the distance from the junction to the canvas edge along the
        # heading actually taken - because a fixed length only works on the canvas it was tuned for,
        # and a length derived for the FALL is wrong for any other bearing the search tries.
        # THE BROOK FIRST. Where the field's own brook passes within reach of the outfall, the drain joins
        # it rather than running its own way off the map - what a village's drainage did (`brook_join`).
        join = brook_join(plan, out)
        if join is not None:
            bow = min(10.0, 0.08 * math.hypot(join[0] - out[0], join[1] - out[1]))  # dug earth, not a ruled connector; proportional keeps the turn obtuse at any length
            mid_j = ((out[0] + join[0]) / 2 - dy * bow, (out[1] + join[1]) / 2 + dx * bow)
            drain_run(s, [out, mid_j, join], "stream")
            plan.sink_brook = [out, mid_j, join]
            return
        heading = drain_heading(s, name) or (dx, dy)
        # THE ROUTE IS CHOSEN AS A WHOLE - junction and exit together.
        #
        # The brook leaves the collector at a junction point and then runs downhill off the frame.
        # The junction sits on the BISECTOR of the drain's heading and the chosen exit, so the brook
        # turns through half the angle twice rather than all of it once, and half of any angle is
        # obtuse (`water_channels_obtuse_turns`; a ditch does not fold back on itself). It TURNS WITH
        # THE BEARING for a reason learned the hard way: pinned to the fall line it was identical for
        # every candidate, so when that one leg crossed the crop all nine bearings failed alike and
        # the sweep dropped through to an untested straight line - the exact defect the sweep exists
        # to prevent, chosen deliberately.
        #
        # "Straight downhill" is right on most fans and wrong on the ones whose toe is concave, where
        # the exit clips back across the rice - so the bearing swings off the fall until the route is
        # clear, nearest first. A brook does follow the fall; the swing is small, and the alternative
        # is a watercourse drawn through a paddy.
        #
        # The junction leg is exempt from the crop test exactly when the GATE exempts it, on the same
        # test: `streams_avoid_fields` trims leading vertices that are INSIDE the field outline, so a
        # leg whose start is outside gets measured in full. Anything looser skips the one leg that
        # was crossing - a 35%-along start was tried, and the crossing was in the first 35%.
        # THE BROOK STARTS WHERE THE GATE WILL TRIM IT. `streams_avoid_fields` drops leading vertices
        # that are strictly INSIDE the field outline, which is how it exempts the anchored end - but a
        # collector whose outfall lands exactly ON the outline (within rounding) is neither in nor
        # out, so nothing is trimmed and every route from it reads as crossing the crop. There is no
        # bearing that fixes that; the start is the problem. Backing up the drain until the point is
        # genuinely inside costs nothing - the brook is the drain's own continuation, so it still
        # touches the collector at its end - and it lets the exemption do its job.
        for back_off in (0.0, 12.0, 24.0, 40.0, 60.0):
            cand = (out[0] - heading[0] * back_off, out[1] - heading[1] * back_off)
            if point_in_poly(cand[0], cand[1], plan.envelope):
                out = cand
                break
        exit_deg = math.degrees(math.atan2(dy, dx))
        anchored = point_in_poly(out[0], out[1], plan.envelope)
        best: tuple[int, Poly] | None = None
        # ...and the junction's DISTANCE from the outfall is searched too. At a fixed 70 px the
        # junction can sit inside a lobe of the fan that the collector runs past, so every bearing
        # crosses on its first leg and the best available route is still a bad one. Letting the brook
        # run a little further before it turns is what gets it clear, and it is what a brook does.
        # Ordered SWING-major and capped at +/-54 deg: `drainage_junction_smooth` wants the brook to
        # leave the collector without a kink, so a wide swing bought to clear a lobe costs more than
        # it saves. Try the nearest bearings at every junction distance before widening the angle.
        # Bearings are tried around the FALL first and then around the DRAIN'S OWN HEADING. A brook
        # continuing along the collector's line before it turns downhill is both perfectly smooth at
        # the junction (turn = 0) and already clear of the rice, since the collector is - which is the
        # combination a fan whose toe wraps a lobe cannot get any other way.
        head_deg = math.degrees(math.atan2(heading[1], heading[0]))
        for base_deg, swing, jd in ((bd, sw, j) for sw in (0, 12, -12, 24, -24, 38, -38, 54, -54) for bd in (exit_deg, head_deg) for j in (70.0, 110.0, 160.0, 230.0)):
            th = math.radians(base_deg + swing)
            bis = unit(heading[0] + math.cos(th), heading[1] + math.sin(th))
            mid = (out[0] + bis[0] * jd, out[1] + bis[1] * jd)
            # the run is measured along THIS bearing, not along the fall: a ray sized for the fall
            # and fired on another heading either stops on the map or sweeps far past it
            spans = [
                ((plan.W if math.cos(th) > 0 else 0.0) - mid[0]) / math.cos(th) if abs(math.cos(th)) > 1e-6 else 1e9,
                ((plan.H if math.sin(th) > 0 else 0.0) - mid[1]) / math.sin(th) if abs(math.sin(th)) > 1e-6 else 1e9,
            ]
            run_here = max(120.0, min(spans)) + 260.0
            end = (mid[0] + math.cos(th) * run_here, mid[1] + math.sin(th) * run_here)
            # THE JUNCTION ANGLE IS SCORED, not left to the ordering. `drainage_junction_smooth`
            # wants under 65 degrees between the drain's own heading and the brook's first leg, and
            # the crop and the angle pull against each other on a fan whose collector runs past a
            # lobe: clearing the rice wants a wide swing, the smooth junction wants a narrow one.
            # Scoring both together picks a route that satisfies both when one exists, instead of
            # ping-ponging between two rules each satisfied at the other's expense.
            turn = math.degrees(math.acos(max(-1.0, min(1.0, heading[0] * bis[0] + heading[1] * bis[1]))))
            bad = int(point_in_poly(mid[0], mid[1], plan.envelope)) + int(crosses_poly(mid, end, plan.envelope))
            bad += int(not anchored and crosses_poly(out, mid, plan.envelope))
            bad += int(turn > 55.0)
            # AND THE WATER MUST RUN DOWNHILL - scored, because nothing else here scores it.
            #
            # Every other term is about where the brook GOES; none of them is about whether it goes
            # DOWN, and the search happily returns a route that climbs. Cohort seed 2 drew one 1,100
            # px uphill and 147.9 deg off the fall, failing `drainage_discharges_downhill` and
            # `watercourses_flow_downstream` (and `features_do_not_overlap`, because a brook running
            # back up the valley re-crosses the dry plots it already passed). The bearing list is why
            # the hole is reachable at all: candidates are tried around the DRAIN'S OWN HEADING as
            # well as around the fall, and a collector runs CROSS-SLOPE by design
            # (`drain_runs_cross_slope`), so "continue along the collector" is a bearing that can sit
            # 90+ deg off the fall before any swing is added. Downhill is not an emergent property of
            # a smooth junction; it has to be asked for.
            #
            # Scored on the gate's own two predicates so the placer cannot pass its own test and fail
            # the real one: net descent along the fall (`drainage_discharges_downhill` fails below
            # -8 px; the placer wants a real descent, not a tolerated one) and divergence of the
            # net upstream->downstream bearing from the map's flow (`watercourses_flow_downstream`
            # fails at 90 deg). Both are measured out->end, exactly the span those checks read.
            #
            # AND THEY ARE MEASURED AGAINST TWO DIFFERENT BEARINGS, which is not a slip. The land's
            # fall (`down_deg`) and the drainage bearing (`water_flow`) are separate declarations -
            # `plan.water_flow` merely DEFAULTS to `down_deg` - and the two checks read one each:
            # `drainage_discharges_downhill` projects on the fall, `watercourses_flow_downstream`
            # compares to `meta.water_flow`. Scoring both against the fall would silently mis-judge
            # every map that declares its own flow (they may sit up to 90 deg apart before
            # `water_flow_consistent_with_slope` objects).
            descent = (end[0] - out[0]) * dx + (end[1] - out[1]) * dy
            bear = math.degrees(math.atan2(end[1] - out[1], end[0] - out[0]))
            div = abs((bear - plan.water_flow + 180.0) % 360.0 - 180.0)
            bad += int(descent <= 0.0) + int(div >= 90.0)
            if bad == 0:
                drain_run(s, [out, mid, end], "offmap")
                plan.sink_brook = [out, mid, end]
                return
            if best is None or bad < best[0]:  # pragma: no cover - the least-bad brook route; no cohort fan currently blocks every bearing at every junction distance
                best = (bad, [out, mid, end])  # pragma: no cover - the least-bad brook route; no cohort fan currently blocks every bearing at every junction distance
        assert (
            best is not None
        )  # ...and if none is clean, the LEAST-BAD route, never an untested one  # pragma: no cover - the least-bad brook route; no cohort fan currently blocks every bearing at every junction distance
        drain_run(s, best[1], "offmap")  # pragma: no cover - the least-bad brook route; no cohort fan currently blocks every bearing at every junction distance
        plan.sink_brook = list(best[1])  # pragma: no cover - the least-bad brook route; no cohort fan currently blocks every bearing at every junction distance
        return  # pragma: no cover - the least-bad brook route; no cohort fan currently blocks every bearing at every junction distance
    # Sized to the settlement: a tameike serving ~15 households reads at roughly Ikegami's 116x74 px
    # (~230 x 150 ft), and the radius scales with the square root of the households it waters, since
    # a reservoir's job is a VOLUME and its depth does not grow with the hamlet.
    grow = math.sqrt(plan.spec.households / REF_HOUSEHOLDS)
    prx, pry = 116.0 * grow, 74.0 * grow
    # THE SET-BACK IS SOLVED, NOT PICKED. `pond_clear_of_field` wants the whole ellipse outside the
    # field envelope, and the drain's outfall is not reliably outside it - a comb's envelope bows out
    # around the collector, so on some fans the outfall sits well inside the outline. Ikegami's
    # authored constant (rim + 46 px below the outfall) is true for Ikegami's fan and false for
    # others, which is exactly the failure mode the project's "derive, don't pin" rule names. So the
    # pond walks DOWNSLOPE from the outfall until its rim is genuinely clear, and stops at the first
    # position that is - the nearest legal seat, so the ditch between field and pond stays a ditch.
    back, sway = pond_seat(plan, out, prx, pry)
    if back > POND_SETBACK_LIMIT:
        # NO ROOM FOR A RESERVOIR HERE, so the field drains off the frame instead.
        #
        # `pond_setback` walks downslope until the pond's rim clears the crop, and on a fan whose
        # toe reaches well past its own drain outfall that can be most of a canvas - at which point
        # the pond is a hard crop feature stranded in open scrub, holding the map's frame open by
        # hundreds of px for its own sake (`crop_not_held_open_by_one_feature` caught one 575 px
        # proud). A tameike is dug just below the fields it collects; one a quarter mile out is not
        # a tameike, it is a lake. Falling back to the off-map brook is the honest reading of the
        # same geometry, and the GM's brief names both sinks as equally ordinary.
        plan.water_sink = "offmap"  # pragma: no cover - the pond-to-offmap fallback; no cohort fan currently needs a tameike further than the limit
        stage_sink(s, plan)  # pragma: no cover - the pond-to-offmap fallback; no cohort fan currently needs a tameike further than the limit
        return  # pragma: no cover - the pond-to-offmap fallback; no cohort fan currently needs a tameike further than the limit
    pcx, pcy = out[0] + dx * back - dy * sway, out[1] + dy * back + dx * sway
    clamped = (max(prx + 20.0, min(plan.W - prx - 20.0, pcx)), max(pry + 20.0, min(plan.H - pry - 20.0, pcy)))
    if math.hypot(clamped[0] - pcx, clamped[1] - pcy) > 1.0 or not pond_clear_of_crop(plan, clamped, prx, pry):
        # THE CLAMP UNDOES THE SOLVE, so a clamped pond is no pond. `pond_setback` walks the tameike
        # downslope until its rim clears the crop; the clamp then pulls it back onto the canvas - and
        # straight back onto the rice it had just cleared (`pond_clear_of_field`). The reservoir has
        # nowhere to go on this map, which is the same finding as a set-back over the limit, so it
        # takes the same answer: the field drains off the frame instead.
        plan.water_sink = "offmap"
        stage_sink(s, plan)
        return
    pcx, pcy = clamped
    s.pond(pcx, pcy, prx, pry)
    plan.sink_pond = (pcx, pcy, prx, pry)
    s.M["meta"]["pond_role"] = "drainage"
    # The drainage ditch, bowed slightly off the straight line so it reads as dug earth rather than
    # a ruled connector (the gate's `channel_winds_gently` wants the same thing). Drawn in the BASE
    # water block, not the late one: the pond's fill has to paint OVER the ditch's mouth where it
    # overshoots the rim, and a late stroke composites above the fill instead
    # (`pond_fill_covers_channel_mouths`).
    bow = min(10.0, 0.08 * math.hypot(pcx - out[0], pcy - out[1]))  # a fixed 10 px bow on a SHORT run is an
    # acute hairpin (`water_channels_obtuse_turns`); proportional keeps the turn obtuse at any length
    mid = ((out[0] + pcx) / 2 - dy * bow, (out[1] + pcy) / 2 + dx * bow)
    ditch: Poly = [out, mid, (pcx, pcy)]
    # WIDTH IS THE DRAIN'S OWN, NOT A LITERAL. This is the collector's last few strides into the
    # tameike, so it carries everything the collector carries - and it used to be drawn at a flat
    # 2.5 px whatever the drain arrived at. Harmless while the net was 5-6x oversize (12.0 -> 2.5
    # reads as one line among many fat ones) and conspicuous the moment the net went to TRUE SIZE:
    # `settlement-review` measured a 5.5 px collector butting a 2.5 px stub at the pond mouth and
    # called it a pinch rather than a mouth, on the sheet's most visible water feature. Derived from
    # `DRAIN_FT[1]` so it tracks any future change to the ladder - the standing derive-don't-pin
    # rule, which a literal here quietly broke.
    drain_run(s, ditch, "pond")
    # A reedy fringe rims the shore - the shallow margin of any standing water.
    ring: Poly = pond_fringe_ring(pcx, pcy, prx, pry, 44.0)  # the shared ring (feature 151); a tameike keeps a wider fringe than a comb's source pond
    s.marsh(ring, role="pond_fringe")
    # No building on the water.
    s.block_polys.append([(pcx - prx - 10, pcy - pry - 10), (pcx + prx + 10, pcy - pry - 10), (pcx + prx + 10, pcy + pry + 10), (pcx - prx - 10, pcy + pry + 10)])
