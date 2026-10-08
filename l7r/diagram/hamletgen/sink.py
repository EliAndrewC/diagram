"""STAGE 3: where the runoff goes - the drain and the tameike it feeds.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.

Research: drain plumbing - NONE: reading the collector back, records, admissions, spans and the refusal type
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from typing import Any

from l7r.diagram.overlap.registry import refuse_unadmitted
from l7r.diagram.settlement import Settlement, point_in_poly, seg_closest
from l7r.diagram.settlement.fields.comb import DOWNHILL_FRACTION as DOWNHILL_FRACTION
from l7r.diagram.settlement.fields.comb import runs_downhill  # the channel rule, one predicate for every channel writer (water:W10)
from l7r.diagram.settlement.land.dikes import breaches_any_dike
from l7r.diagram.settlement.land.wet import pond_fringe_ring
from l7r.diagram.settlement.water_ways.water import DRAIN_HUE, DRAINAGE_DITCH
from l7r.diagram.sitegen.geom import crosses_poly, unit
from l7r.diagram.waterfields import DRAIN_FT, chan_px
from l7r.diagram.waterfields.twins import TWIN_HI_FT, TWIN_RUN_FT, twin_run_ft

from .consts import GRAIN, POND_SETBACK_LIMIT, REF_HOUSEHOLDS, Poly, Pt
from .plan import SitePlan
from .water.brook import brook_violations, course_corner, finished_course, round_the_brooks
from .water.brook_rules import BROOK_DRAWN_W, course_enters, crosses_mid_run, ditch_strokes, to_edge


class SinkRefused(RuntimeError):
    """The drain has no route the rules allow (feature 287, FR-005: refused by name, never drawn in breach)."""


# ---- STAGE 3: where the runoff goes -------------------------------------------------------------


def drain_outfall(s: Settlement, name: str) -> Pt | None:
    """The last vertex of the field's drain collector, READ BACK from the manifest.

    Read back rather than remembered, because the manifest is what every later reader reads: the pond is
    sited from the same record the ditch to it is drawn from - "placement and its test read the SAME
    source", one level down."""
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
    ends" read off `poly[-2] -> poly[-1]` is noise, while the 40 px span (`GATE_FLOW_SPAN`, the span the retired
    `drainage_junction_smooth` check read) gets the collector's real bearing. On cohort seed 2 the two disagreed by
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
    to the river to be taken up below (`research/questions/0060-field-drains-akusuiro.html`) - a dug channel that reaches a watercourse, never a brook of its own. So every
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

    NO NO-BUILD CORRIDOR ON A HAMLET (feature 328). This run once registered the 33 ft corridor `s.channel` and
    `s.stream` register, but that strip is the town and city maps' rule (0058). A nucleated cluster is exempt from the
    page's below-drain rule; that rule for a dispersed hamlet's farmsteads is not yet asked (feature 328 row 669, E3).

    Research:
        a drain is a dug ditch - research/questions/0060-field-drains-akusuiro.html, research/questions/0060-field-drains-akusuiro.drawing.html: the drainage-ditch class whichever way it runs
        drain width - research/questions/0060-field-drains-akusuiro.drawing.html: the collector's own outfall width
        no no-build corridor on a hamlet - research/questions/0058-ground-too-wet-to-build-on.drawing.html: the 33 ft strip is the town and city maps' rule; on a hamlet the drain's rule is the marsh and the wet ground below it"""
    outfall_w = chan_px(DRAIN_FT[1], GRAIN)
    rec = drain_record(pts, to)
    refuse_unadmitted(s.M, "channels", rec)  # its route was chosen among those the registry admits (`drain_admitted`)
    s.field_channel(pts, DRAIN_HUE, outfall_w, outfall_w, cls=DRAINAGE_DITCH)
    s.M["channels"].append(rec)  # no 33 ft no-build corridor: that is a town's or city's rule (0058); the below-drain rule for dispersed farmsteads is open (row 669)


def drain_record(pts: Sequence[Pt], to: str) -> dict[str, Any]:
    """The `channels` record a drain run along `pts` into `to` is written as (`drain_run`)."""
    return {"poly": [[round(x, 1), round(y, 1)] for x, y in pts], "frm": {"kind": "drain"}, "to": {"kind": to}, "w": 2.5}


def drain_admitted(s: Settlement, pts: Sequence[Pt], to: str) -> bool:
    """May a drain run along `pts` into `to` be recorded on what stands (the overlap matrix, feature 287 water W53)? Every
    route the sink offers asks it - the confluence, each searched run off the frame, the constructed route, the pond run -
    so a run across a resting basin or a stranger's ground is refused and the next taken."""
    return s.admits("channels", drain_record(pts, to))


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
    """The pond clear of the crop, on the field's envelope: no rim point inside the crop, no crop vertex inside the
    pond (the two tests `pond_setback` walks with).

    Research: tameike clear of the paddy - research/questions/0060-field-drains-akusuiro.drawing.html: the pond at the field's foot"""
    env = list(plan.envelope)
    rim = [(math.cos(a), math.sin(a)) for a in [i * math.pi / 12 for i in range(24)]]
    if any(point_in_poly(center[0] + prx * ux, center[1] + pry * uy, env) for ux, uy in rim):
        return False
    return not any(((v[0] - center[0]) / prx) ** 2 + ((v[1] - center[1]) / pry) ** 2 <= 1.0 for v in env)


def pond_setback(plan: SitePlan, out: Pt, prx: float, pry: float, step: float = 14.0, limit: float = 900.0) -> float:
    """How far DOWNSLOPE of the drain outfall the pond must stand to clear the crop entirely.

    Walks outward in small steps and returns the first distance at which no rim point of the ellipse
    falls inside the field envelope, no envelope vertex falls inside the ellipse (`pond_clear_of_crop`'s two
    tests), and the pond's ellipse grown by 12 px clears the brook. A 12 px cushion past the first clear
    position keeps it off the line.

    Research:
        pond downslope of the outfall - research/questions/0060-field-drains-akusuiro.drawing.html: the nearest seat at the field's foot
        set-back margins - UNRESEARCHED: at least the rim plus 46 ft, a 12 ft cushion, 12 ft off the brook"""
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
CROP_MARGIN_PX = 48.0
"""Research: crop margin - CONVENTION: 48 ft"""
#: The margin `crop_to_content` adds around the hard content it crops to - so the field's box grown by it is a
#: box the finished picture cannot fail to show, which is what a junction needs to be judged against.

BROOK_JOIN_TRUNK = 150.0
"""Research: brook below a confluence - CONVENTION: 150 ft on the canvas, so the junction reads"""
#: How much of the run from the outfall to the confluence may lie inside the crop before the route is
#: refused. The outfall is AT the field's edge and a comb's envelope bows out around its own collector, so
#: the first strides of any route from it are legitimately on the crop's own ground - which is why the gate
#: trims a brook's leading vertices before it judges one (`streams_avoid_fields`). Anything past this is a
#: ditch driven through the rice.
BROOK_JOIN_LEAD = 0.3
"""Research: crop lead tolerance - UNRESEARCHED: 0.3 of the drain's run may lie in the rice as the field's own edge"""
#: How far the confluence must have FALLEN below the outfall, px. A drain runs downhill into the brook it
#: joins, and a junction level with the outfall is neither a fall nor a join; a stride of the collector's
#: own tail width is enough to read as one on the sheet.
BROOK_JOIN_DESCENT = 20.0
"""Research: confluence fallen below the outfall - UNRESEARCHED: 20 ft down the fall"""


def drawn_brook(s: Settlement, plan: SitePlan) -> Poly:
    """The feed brook as the map will draw it - `finished_course` at the taps `round_the_brooks` will hold - which a drain
    must not cross mid-run (water:W08). Empty where the map has no brook."""
    heads = [(float(c["poly"][0][0]), float(c["poly"][0][1])) for c in s.M.get("channels") or [] if (c.get("frm") or {}).get("kind") == "stream" and c.get("poly")]
    return finished_course(plan.brook, BROOK_DRAWN_W, heads) if len(plan.brook) >= 2 else []


JUNCTION_TURN_MAX_DEG = 55.0
"""Research: drain junction turn - research/questions/0060-field-drains-akusuiro.drawing.html: the run curves out of the collector, at most 55 degrees"""
#: The most the drain's continuation may turn off the collector's own heading at the outfall (water:W12) - the placer's
#: bar, under the 65 degrees `drainage_junction_smooth` allowed, so the route the placer takes is not one the rule tolerates.


def route_refusals(plan: SitePlan, out: Pt, heading: Pt, anchored: bool, route: Sequence[Pt], brook: Sequence[Pt], dikes: Any = ()) -> list[str]:
    """Why the drain's continuation `route` (from the outfall `out`) may not be drawn - empty where it may. One predicate
    per term (feature 287, water:W10-W12): the junction turn (`JUNCTION_TURN_MAX_DEG`), the rice (an interior vertex in the
    field, or a leg through it - the first leg exempt where the outfall stands inside the field, as the gate trims it),
    downhill (`runs_downhill`), the drainage bearing (under 90 degrees off `water_flow`), the brook (`crosses_mid_run`, and
    `twin_run_ft`: not run beside it, feature 294) and the dike (`breaches_any_dike` over the recorded `dikes`: a drain crosses a dike's crest only at one of its gaps, water
    W42).

    Research:
        junction turn - research/questions/0060-field-drains-akusuiro.drawing.html: at most JUNCTION_TURN_MAX_DEG
        not through the rice - UNRESEARCHED: no interior vertex or leg in the field
        runs downhill - research/questions/0060-field-drains-akusuiro.drawing.html: a fifth of the run down the fall
        with the drainage bearing - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: under 90 degrees off the water's flow
        brook not crossed mid-run - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.html: ditches join rather than cross
        not the brook's twin - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html
        dike crossed only at a gap - research/questions/0019-polders-fields-diked-against-the-fluctuating-water-weitian-waju.drawing.html"""
    lead = (route[1][0] - route[0][0], route[1][1] - route[0][1])
    ln = math.hypot(*lead) or 1.0
    turn = math.degrees(math.acos(max(-1.0, min(1.0, (heading[0] * lead[0] + heading[1] * lead[1]) / ln))))
    legs = list(zip(route, route[1:], strict=False))
    bear = math.degrees(math.atan2(route[-1][1] - out[1], route[-1][0] - out[0]))
    checks = {
        "kink": turn > JUNCTION_TURN_MAX_DEG,
        "field": course_enters(route, [plan.envelope]) or any(crosses_poly(a, b, plan.envelope) for a, b in legs[1:]) or (not anchored and crosses_poly(*legs[0], plan.envelope)),
        "uphill": not runs_downhill(route, plan.fall),
        "upstream": abs((bear - plan.water_flow + 180.0) % 360.0 - 180.0) >= 90.0,
        "brook": len(brook) >= 2 and crosses_mid_run(brook, route),
        "dike": breaches_any_dike(list(route), dikes),
        # ...and it does not run down beside the brook as its twin (feature 294 B4, `waterfields/twins.py`): Kashikawa's outfall
        # ran 12-32 ft off the brook for 130 ft to the frame's edge instead of joining it
        "twin": len(brook) >= 2 and twin_run_ft(list(route), list(brook), plan.ftpx) > TWIN_RUN_FT,
    }
    return [k for k, bad in checks.items() if bad]


def hull_route(plan: SitePlan, out: Pt, heading: Pt, brook: Sequence[Pt], pad: float = 12.0) -> tuple[Poly, str]:
    """THE CONSTRUCTED ROUTE (feature 287, water:W12), taken where no searched route passes `route_refusals`: on along the
    collector's own heading until it leaves the field's convex hull grown by `pad` (a turn of 0 at the junction), round
    that hull on the side the land falls to (every step of it further down the fall), and from the hull's lowest point
    straight down the fall off the canvas - lengthened until the whole run is downhill by the channel rule and within 90
    degrees of the drainage bearing. The hull is convex, so no step round it and no leg down from its lowest point can
    enter the field. Where the brook lies across it, the run ends where it meets the brook, a confluence (to "stream").
    Returns (the route, what it ends at).

    Research:
        constructed route - NONE: hull geometry under route_refusals' rules
        hull standoff - UNRESEARCHED: the drain skirts the field's hull 12 ft off
        ends at the brook or off the map - research/questions/0060-field-drains-akusuiro.drawing.html"""
    from shapely.geometry import LineString, Point, Polygon  # noqa: PLC0415 - bound on first use

    fall = plan.fall
    hull = Polygon(plan.envelope).convex_hull.buffer(pad)
    ring = [(float(x), float(y)) for x, y in list(hull.exterior.coords)[:-1]]
    u = lambda p: p[0] * fall[0] + p[1] * fall[1]  # noqa: E731
    edge = hull.exterior
    if hull.contains(Point(out)):
        hits = LineString([out, (out[0] + heading[0] * 1e5, out[1] + heading[1] * 1e5)]).intersection(edge)
        pts = [(float(g.x), float(g.y)) for g in getattr(hits, "geoms", [hits]) if not g.is_empty]
        p1 = min(pts, key=lambda q: math.dist(q, out))
    else:
        g = edge.interpolate(edge.project(Point(out)))
        p1 = (float(g.x), float(g.y))
    # the vertex after p1 each way round; the way whose next vertex lies further down the fall walks down the hull
    at = edge.project(Point(p1))
    cum = [0.0]
    for a, b in zip(ring, ring[1:], strict=False):
        cum.append(cum[-1] + math.dist(a, b))
    seg = max(k for k in range(len(ring)) if cum[k] <= at + 1e-9)  # p1 lies on the edge from ring[seg] to the next
    fwd, bwd = (seg + 1) % len(ring), seg
    step, k = (1, fwd) if u(ring[fwd]) >= u(ring[bwd]) else (-1, bwd)
    low = max(range(len(ring)), key=lambda q: u(ring[q]))
    walk = [ring[k]]
    while k != low:
        k = (k + step) % len(ring)
        walk.append(ring[k])
    q = walk[-1]
    reach = to_edge(q, fall, float(plan.W), float(plan.H)) + 260.0
    route: Poly = [out, p1, *walk, (q[0] + fall[0] * reach, q[1] + fall[1] * reach)]
    for _ in range(40):  # the leg down the fall is off the canvas, so its length is free
        bear = math.degrees(math.atan2(route[-1][1] - out[1], route[-1][0] - out[0]))
        if runs_downhill(route, fall) and abs((bear - plan.water_flow + 180.0) % 360.0 - 180.0) < 90.0:
            break
        reach += 400.0
        route[-1] = (q[0] + fall[0] * reach, q[1] + fall[1] * reach)
    route = [p for i, p in enumerate(route) if i == 0 or math.dist(p, route[i - 1]) > 0.5]
    if len(brook) >= 2 and crosses_mid_run(brook, route):
        for i, (a, b) in enumerate(zip(route, route[1:], strict=False)):
            meet = LineString([a, b]).intersection(LineString(brook))
            if not meet.is_empty:
                m = min(((float(g.x), float(g.y)) for g in getattr(meet, "geoms", [meet]) if g.geom_type == "Point"), key=lambda p: math.dist(p, a), default=None)
                if m is not None and math.dist(m, a) > 0.5:
                    return [*route[: i + 1], m], "stream"
    if len(brook) >= 2:
        return join_beside(route, brook, plan.ftpx)
    return route, "offmap"


def join_beside(route: Poly, brook: Sequence[Pt], ftpx: float) -> tuple[Poly, str]:
    """A drain route that would run down beside the brook as its twin (feature 294 B4, `waterfields/twins.py`) JOINS it
    instead: cut where the route first comes within `TWIN_HI_FT` of the brook, and carried onto the brook's nearest point,
    a confluence (to "stream"). A route that keeps its distance runs off the map (to "offmap").

    Research: a twin joins the brook - research/questions/0067-do-two-ditches-run-side-by-side-across-the-fields-not-in-the-old-forms-the-map-draws.html: cut within TWIN_HI_FT and carried onto the brook"""
    from shapely.geometry import LineString, Point  # noqa: PLC0415 - bound on first use

    if twin_run_ft(list(route), list(brook), ftpx) <= TWIN_RUN_FT:
        return route, "offmap"
    line, water = LineString(route), LineString(brook)
    reach = TWIN_HI_FT / ftpx
    s = next(k * 2.0 for k in range(int(line.length // 2.0) + 1) if water.distance(line.interpolate(k * 2.0)) <= reach)
    head = [p for p in route if line.project(Point(p)) < s]
    at = line.interpolate(s)
    meet = water.interpolate(water.project(at))
    return [*head, (float(at.x), float(at.y)), (float(meet.x), float(meet.y))], "stream"


def _through_the_crop(plan: SitePlan, out: Pt, q: Pt) -> bool:
    """Would a ditch from the outfall to `q` run through the rice - past the crop edge the outfall stands on?

    Lifted out of `brook_join` so the exemption can be tested on a square (feature 146's rule). The route
    is walked from the outfall until it is clear of the envelope; leaving within `BROOK_JOIN_LEAD` of the
    run is the field's own edge and is exempt, and the rest of the route is judged in full.

    Research: drain not through the rice - UNRESEARCHED: the first 0.3 of the run exempt as the field's edge"""
    lead = next((t / 20.0 for t in range(21) if not point_in_poly(out[0] + (q[0] - out[0]) * t / 20.0, out[1] + (q[1] - out[1]) * t / 20.0, plan.envelope)), 1.0)
    if lead > BROOK_JOIN_LEAD:
        return True
    frm = (out[0] + (q[0] - out[0]) * lead, out[1] + (q[1] - out[1]) * lead)
    return crosses_poly(frm, q, plan.envelope)


def brook_join(plan: SitePlan, out: Pt, reach: float = 420.0, stride: float = 10.0, keeps: Callable[[Pt], bool] | None = None) -> Pt | None:
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
    meeting.

    `keeps` (feature 287 wave 5): whether the brook AS DRAWN with the confluence held still keeps every rule of the brook
    (`confluence_keeps_the_brook`) - the nearest candidate that does is the confluence, so the brook the map draws round
    its joins is the brook its placer judged.

    Research:
        drain joins the passing brook - research/questions/0060-field-drains-akusuiro.drawing.html: drainage returned to the river
        join reach - UNRESEARCHED: 420 ft from the outfall
        confluence below the outfall - research/questions/0060-field-drains-akusuiro.drawing.html: fallen BROOK_JOIN_DESCENT, the run downhill
        trunk below the junction - CONVENTION: BROOK_JOIN_TRUNK on the canvas
        not on a corner of the brook - CONVENTION
        the nearest fallen point, off the crop - research/questions/0060-field-drains-akusuiro.drawing.html: the drain never crosses the crop; the nearest fallen candidate is the confluence"""
    dx, dy = plan.fall
    found: list[tuple[float, Pt]] = []
    legs = list(zip(plan.brook, plan.brook[1:], strict=False))

    # THE TRUNK IS MEASURED ON THE CANVAS, NOT ALONG THE COURSE (feature 230, settlement-review passes 6 and 7).
    # `BROOK_JOIN_TRUNK` exists so a confluence is not drawn with nothing below it to read, and it counted ARC
    # LENGTH - which a brook may spend entirely off the sheet: pass 6 measured Sawada's junction with all 359 ft
    # of its trunk outside the canvas. Two attempts to predict the PICTURE here were both wrong, and the second
    # is the instructive one: the crop's guaranteed box is the field's own extent plus the crop margin, the brook
    # runs OUTSIDE the field by a skirt's width by design, and the drain's outfall stands at the field's low
    # corner - so no junction can be deep inside that box, and predicting it refused every confluence the
    # generator can draw. The frame is not knowable here. What IS knowable is whether the brook runs on across
    # the map below the junction, and that is what this asks; whether the junction is SHOWN is settled where the
    # frame is settled, by `stage_frame` reserving it as content (`plan.confluence`).
    def _seen(c: Pt, d: Pt) -> float:
        """How much of the leg c->d lies on the CANVAS, sampled at the walk's own stride."""
        n = max(1, int(math.hypot(d[0] - c[0], d[1] - c[1]) / stride))
        inside = sum(1 for i in range(n + 1) if 0.0 <= c[0] + (d[0] - c[0]) * i / n <= plan.W and 0.0 <= c[1] + (d[1] - c[1]) * i / n <= plan.H)
        return math.hypot(d[0] - c[0], d[1] - c[1]) * inside / (n + 1)

    below = [sum(_seen(c, d) for c, d in legs[k + 1 :]) for k in range(len(legs))]
    for k, (a, b) in enumerate(legs):
        run = math.hypot(b[0] - a[0], b[1] - a[1])
        for i in range(int(run / stride) + 1):
            t = min(1.0, i * stride / run) if run else 0.0
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            if below[k] + _seen(q, b) < BROOK_JOIN_TRUNK:
                continue  # the brook must run on below the junction far enough to read as a trunk
            d = math.hypot(q[0] - out[0], q[1] - out[1])
            # ...AND THE RUN TO IT IS A DRAIN RUNNING DOWNHILL (feature 287, water:W10): the 20 px descent says the junction
            # has fallen; `runs_downhill` says the ditch to it runs down the fall by a fifth of its length, the rule every
            # channel on the map is held to - a junction 300 px along the collector's line and 20 px down was a level ditch
            if d > reach or (q[0] - out[0]) * dx + (q[1] - out[1]) * dy < BROOK_JOIN_DESCENT:  # fallen 20 ft is a net descent, so the run is downhill (0054's strict rule, feature 328)
                continue
            if _through_the_crop(plan, out, q):
                continue
            # ...AND NOT ON A CORNER OF THE BROOK (feature 287, labels L16): `round_the_brooks` holds the confluence as a vertex
            # of the course, and a held corner is a mitred bend - the walk's first stride of every leg IS the corner.
            if course_corner(q, plan.brook):
                continue
            found.append((d, q))
    return next((q for _d, q in sorted(found, key=lambda t: t[0]) if keeps is None or keeps(q)), None)


def confluence_keeps_the_brook(s: Settlement, plan: SitePlan, q: Pt) -> bool:
    """Does the feed brook, drawn with a confluence at `q` held (`drawn_course`, as `round_the_brooks` will draw it), keep
    every rule of the brook (`brook_violations`)? The drain's join and the constructed route's meeting both ask it."""
    heads = [(float(c["poly"][0][0]), float(c["poly"][0][1])) for c in s.M.get("channels") or [] if (c.get("frm") or {}).get("kind") == "stream" and c.get("poly")]
    if len(plan.brook) < 2 or not heads:
        return True
    return not brook_violations(plan.brook, plan, heads[0], ditch_strokes(plan), joins=[q])


def pond_run(out: Pt, heading: Pt, pond: Pt, fall: Pt) -> Poly:
    """The drainage ditch from the collector's outfall to the pond's center.

    ON THE LINE WHEN THE POND IS AHEAD, bowed slightly off it so it reads as dug earth rather than a ruled connector
    (`channel_winds_gently`), the bow proportional because a fixed 10 px bow on a short run is an acute hairpin
    (`water_channels_obtuse_turns`).

    LED ROUND WHEN IT IS NOT (settlement-review, feature 230 pass 10). Since the brook runs on down one flank, `pond_seat`
    may step the pond across the fall to a pocket beside the outfall rather than ahead of it - which is right - and a
    straight run to it then doubles back on the collector: Mizuguchi's turned 111.6 degrees at the field's tip, an
    inverted V. So where the pond lies more than 100 degrees off the collector's own heading the run leaves ALONG that
    heading and curves round to the pond, spreading the same turn over a dozen gentle bends.

    Research:
        bowed ditch - CONVENTION: up to 10 ft off the chord, so it reads as dug earth
        led round a pond behind - CONVENTION: a cubic past 100 degrees off the heading
    """
    tx, ty = pond[0] - out[0], pond[1] - out[1]
    dist = math.hypot(tx, ty)
    hn = math.hypot(heading[0], heading[1]) or 1.0
    cos_off = (tx * heading[0] + ty * heading[1]) / ((dist or 1.0) * hn)
    # 100 degrees, not 60: a collector runs ALONG the field's low edge, across the fall, so a pond straight downslope of
    # the outfall is already about 90 degrees off its heading - the ordinary outfall, a corner every pond map draws and no
    # review has faulted. A 60 degree cut bent that one too and moved Inashiro's lane web; the defect is a pond BEHIND it.
    if cos_off >= math.cos(math.radians(100.0)):
        bow = min(10.0, 0.08 * dist)
        return [out, ((out[0] + pond[0]) / 2 - fall[1] * bow, (out[1] + pond[1]) / 2 + fall[0] * bow), pond]
    # A CUBIC, leaving along the heading and arriving along the chord, sampled at twelfths. A quadratic sampled at quarters
    # was the first cut and crowded the turn into one bend (66.9 degrees on Mizuguchi); the whole turn is fixed by where
    # the pond is, so what can be chosen is how evenly it is spread. Measured on Mizuguchi's own coordinates, handles of
    # 0.6 of the distance at twelfths hold every bend at 36 degrees or less on legs of 10 px or more.
    # ...AND IT LEAVES ON THE BISECTOR, NOT ON THE HEADING (settlement-review, feature 230 pass 12). Pass 10's handle
    # was thrown 0.6 of the distance ALONG the collector's heading, which is sound while the pond is somewhere ahead
    # and absurd once it is behind: on Mizuguchi the pond lay 127 degrees round while the run left at 27, so the curve
    # climbed 26 ft FURTHER from the pond, topped out 53 ft past its north rim and came back down - 121 ft of ditch on
    # an 87 ft chord, an inverted U that reads as a handle rather than a watercourse, and whose apex passed 11 ft from
    # the brook it does not join, posing a junction the map does not make. Every per-bend angle was inside tolerance,
    # which is why nothing caught it: the defect is the EXCURSION, not the bends.
    # So the first handle points along the BISECTOR of the heading and the chord. The run still leaves without a kink
    # at the outfall - it keeps half of the heading - and it commits to the pond at once instead of overshooting it.
    ux, uy = heading[0] / hn, heading[1] / hn
    cxu, cyu = tx / (dist or 1.0), ty / (dist or 1.0)
    bx, by = ux + cxu, uy + cyu
    bn = math.hypot(bx, by)
    if bn < 1e-9:  # the pond lies exactly back along the heading, so there is no bisector: leave on the chord
        bx, by, bn = cxu, cyu, 1.0
    k = 0.45 * dist
    c1 = (out[0] + bx / bn * k, out[1] + by / bn * k)
    c2 = (pond[0] - tx / (dist or 1.0) * k * 0.5, pond[1] - ty / (dist or 1.0) * k * 0.5)
    return [
        (
            (1 - u) ** 3 * out[0] + 3 * (1 - u) ** 2 * u * c1[0] + 3 * (1 - u) * u * u * c2[0] + u**3 * pond[0],
            (1 - u) ** 3 * out[1] + 3 * (1 - u) ** 2 * u * c1[1] + 3 * (1 - u) * u * u * c2[1] + u**3 * pond[1],
        )
        for u in [n / 12.0 for n in range(13)]
    ]


def pond_seat(plan: SitePlan, out: Pt, prx: float, pry: float, heading: Pt | None = None, brook: Sequence[Pt] = ()) -> tuple[float, float]:
    """(how far downslope, how far across the fall) the reservoir must stand to clear the crop AND the
    brook - the set-back search with one more degree of freedom.

    The walk downslope alone was enough while the brook stopped at the intake. Since feature 230 it runs
    on down one flank of the fan, and on a map whose flank is the drain's own side the two want the same
    ground: Mizuguchi's tameike - the reservoir the place is named for - was pushed past the canvas and
    the stage fell back to draining off the frame, losing a feature its spec had declared. Stepping the
    pond ACROSS the fall is the cheaper move and the truer one: a valley's reservoir sits in whatever
    pocket the ground offers below the fields, not on a plumb line under the outfall. The sways are
    tried nearest-first and the straight seat still wins whenever it is clear, so every map whose pond
    already had room keeps the seat it had.

    ...AND THE DITCH TO IT NEVER CROSSES THE BROOK (feature 287 wave 5, water:W08): given the collector's `heading` and the
    `brook` as drawn, a seat whose run (`pond_run`) would cross the open water mid-run is no seat - measured at HEAD on six
    of cohort 1-60 and the pool (Mizuguchi among them), where the ditch was drawn straight over the brook.

    Research:
        pond in a pocket below the fields - research/questions/0060-field-drains-akusuiro.drawing.html: the pond at the field's foot
        sways across the fall - UNRESEARCHED: 0.9 and 1.8 long radii
        set-back limit - UNRESEARCHED: POND_SETBACK_LIMIT
        ditch runs downhill, not over the brook - research/questions/0060-field-drains-akusuiro.drawing.html, research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html"""
    for sway in (0.0, -0.9 * prx, 0.9 * prx, -1.8 * prx, 1.8 * prx):
        moved = (out[0] - plan.fall[1] * sway, out[1] + plan.fall[0] * sway)
        back = pond_setback(plan, moved, prx, pry)
        # ...AND THE DITCH TO IT RUNS DOWNHILL (feature 287, water:W10/W11): the run ends at the pond's center, `back` down
        # the fall and `sway` across it, and a seat stepped so far across that the run is more level than downhill is no
        # seat. By construction it never is (`back` is at least the pond's short radius and 58 more, `sway` at most 1.8 of
        # its long one, so the run keeps a third of its length down the fall at any size); the rule is asked, not assumed.
        center = (moved[0] + plan.fall[0] * back, moved[1] + plan.fall[1] * back)
        if back <= POND_SETBACK_LIMIT and runs_downhill([out, center], plan.fall) and not (heading and crosses_mid_run(brook, pond_run(out, heading, center, plan.fall))):
            return back, sway
    return POND_SETBACK_LIMIT + 1.0, 0.0


def stage_sink(s: Settlement, plan: SitePlan) -> None:
    """Where the runoff goes.

    The tail drain and its pond or off-map outfall. It runs with the water rather than with the ground cover
    because the pond is a HARD feature - houses, lanes and trees all have to avoid it, so it must exist before
    any of them are seated.

    The tameike the field drains into - DERIVED from the drain, never placed by hand.

    A reservoir below the fields is sited by one fact: it must sit clear of the paddies and low
    enough that the drain reaches it downhill. So it stands at the nearest seat DOWNSLOPE of the drain's own
    outfall - the set-back SOLVED (`pond_setback`), the pond stepped across the fall where it must be (`pond_seat`) -
    where its rim clears the crop and the brook, and the drainage ditch is drawn from the outfall to the pond
    (`pond_run`) so the two are visibly joined. Both scale with the map: a bigger hamlet drains more water into a
    bigger pond. Where no seat fits - past `POND_SETBACK_LIMIT`, or a run that would cross a dike, the brook or
    forbidden ground - the field drains off the frame instead.

    `water_sink="offmap"` drains the collector off the frame instead of into a pond - first into the passing brook at a
    confluence where one is in reach (`brook_join`, the researched sink), else a drainage ditch run off the frame
    (`drain_run`), which is what most valleys do and what the GM's brief allows. Every route it may take is judged by
    `route_refusals`, and where no searched route passes, `hull_route` constructs one that does (feature 287,
    water:W10-W12).

    THE WATER IS FINISHED HERE (feature 287, M2): the brook is rounded to the course the map draws as this stage's last
    step, so the seat, the houses, the fords' tests and the decks all read one course.

    Steps:
        l7r.diagram.hamletgen.sink.drain_outfall
        l7r.diagram.hamletgen.sink.drain_heading
        l7r.diagram.hamletgen.sink.pond_setback
        l7r.diagram.hamletgen.sink.pond_clear_of_crop
        l7r.diagram.hamletgen.sink.pond_seat
        l7r.diagram.hamletgen.sink.pond_run
        l7r.diagram.hamletgen.sink.brook_join
        l7r.diagram.hamletgen.sink.route_refusals
        l7r.diagram.hamletgen.sink.hull_route
        l7r.diagram.hamletgen.sink.drain_run
        l7r.diagram.settlement.Settlement.pond
        l7r.diagram.settlement.land.wet.pond_fringe_ring
        l7r.diagram.settlement.Settlement.marsh
        l7r.diagram.hamletgen.water.brook.round_the_brooks

    Research:
        where the runoff goes - research/questions/0060-field-drains-akusuiro.drawing.html: a pond at the foot, the passing brook, or off the map
        tameike below the fields - GUESS: a drain ending in a pond of its own, a guess on research/questions/0060-field-drains-akusuiro.drawing.html
        sink before the houses - NONE: stage order, the pond a hard feature
        brook rounded - research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html: bends on a radius
    """
    lay_sink(s, plan)
    # the sink as DRAWN, after a pond the canvas cannot hold fell back to off-map: a choice on the title card (feature 319 plan D10)
    s.M["meta"]["water_sink"] = plan.water_sink
    round_the_brooks(s)


def lay_sink(s: Settlement, plan: SitePlan) -> None:
    """`stage_sink` before the brook is rounded: the drain run to its tameike, to the passing brook or off the frame. A pond
    the canvas cannot hold re-enters `stage_sink` as an off-map sink, whose rounding is the same course again.

    Research:
        brook first, then off the frame - research/questions/0060-field-drains-akusuiro.drawing.html
        off-map route search - NONE: swings, junction distances and run lengths under route_refusals
        pond area - research/questions/0061-reservoir-ponds-tameike.drawing.html: held below two or three tenths of its paddy
        pond's role - research/questions/0060-field-drains-akusuiro.drawing.html: a drain that ends in a pond of its own is a GUESS recorded there; the pond is laid at the drain's foot as the
            field's sink, not as a reservoir that waters the paddy
        pond bank form - research/questions/0061-reservoir-ponds-tameike.drawing.html: every bank bare; the second attested form,
            a bank planted sparsely with mulberry and cudrania, is never rolled
        pond reference size - UNRESEARCHED: 116 x 74 ft radii at 15 households, scaled by the square root
        too far below, no pond - UNRESEARCHED: past POND_SETBACK_LIMIT the field drains off the frame
        reed fringe - research/questions/0061-reservoir-ponds-tameike.drawing.html: a fringe of reeds at the shore
        reed fringe width - UNRESEARCHED: a 44 ft ring
        no building on the water - UNRESEARCHED: 10 ft round the pond's box
        bowed ditch - CONVENTION"""
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
        join = brook_join(plan, out, keeps=lambda q: confluence_keeps_the_brook(s, plan, q))
        dikes = s.M.get("dikes") or []
        mid_j = out
        if join is not None:
            bow = min(10.0, 0.08 * math.hypot(join[0] - out[0], join[1] - out[1]))  # dug earth, not a ruled connector; proportional keeps the turn obtuse at any length
            mid_j = ((out[0] + join[0]) / 2 - dy * bow, (out[1] + join[1]) / 2 + dx * bow)
            # ...NEVER THROUGH A DIKE OFF ITS GAPS (feature 287, water W42): a confluence reached only across the crest is
            # no confluence, and the drain takes the off-map route search below, which refuses the crest too
            # ...AND NEVER WHERE THE REGISTRY OF WHAT STANDS REFUSES IT (feature 287, water W53): the off-map search below takes it
            if breaches_any_dike([out, mid_j, join], dikes) or not drain_admitted(s, [out, mid_j, join], "stream"):
                join = None
        if join is not None:
            drain_run(s, [out, mid_j, join], "stream")
            plan.sink_brook = [out, mid_j, join]
            plan.confluence = join  # `stage_frame` reserves it: the junction is a feature, and the crop must show it
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
        brook = drawn_brook(s, plan)
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
        # ...and WIDENED before anything is constructed (feature 287, water:W12): junctions 300 and 400 px out, every bearing
        # again, AFTER the first sweep so a map whose clean route the first sweep found keeps it
        _swings = (0, 12, -12, 24, -24, 38, -38, 54, -54)
        _first = ((bd, sw, j) for sw in _swings for bd in (exit_deg, head_deg) for j in (70.0, 110.0, 160.0, 230.0))
        _wider = ((bd, sw, j) for j in (300.0, 400.0) for sw in _swings for bd in (exit_deg, head_deg))
        for base_deg, swing, jd in (*_first, *_wider):
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
            # ...AND NOW REFUSED, NOT SCORED (feature 287, water:W10-W12): each term above is one predicate, the route is taken
            # only where every one holds, and the least-bad route that used to be drawn when none did - a route that broke
            # at least one of them, by construction - is gone. The downhill term is the channel rule itself (`runs_downhill`,
            # a fifth of the run down the fall, where "any descent" let a near-level ditch through) and the route may not
            # cross the brook mid-run (`crosses_mid_run`, water:W08).
            if not route_refusals(plan, out, heading, anchored, [out, mid, end], brook, dikes) and drain_admitted(s, [out, mid, end], "offmap"):
                drain_run(s, [out, mid, end], "offmap")
                plan.sink_brook = [out, mid, end]
                return
        route, to = hull_route(plan, out, heading, brook)
        if breaches_any_dike(route, dikes):
            # THE CONSTRUCTED ROUTE IS NOT DRAWN THROUGH A DIKE (feature 287, water W42). No map reaches this - a polder's field
            # is named for the polder and has no `-paddies` collector, so the sink has no outfall where a dike stands - and a
            # route that breaches is refused by name rather than drawn.
            raise SinkRefused(f"{plan.spec.name}: the drain's constructed route crosses the dike away from its gaps")
        if to == "stream" and not confluence_keeps_the_brook(s, plan, route[-1]):
            # THE MEETING IS JUDGED WITH THE BROOK AS DRAWN (feature 287 wave 5): the constructed route is the last candidate,
            # so a meeting whose held vertex would take the drawn brook out of its rules is refused by name, never drawn
            raise SinkRefused(f"{plan.spec.name}: the drain's constructed route meets the brook where the brook as drawn breaks its rules")
        if not drain_admitted(s, route, to):
            # ...and the last candidate the registry of what stands refuses is refused by name, never recorded (water W53)
            raise SinkRefused(f"{plan.spec.name}: the drain's constructed route lies where the overlap matrix forbids it")
        drain_run(s, route, to)
        plan.sink_brook = list(route)
        if to == "stream":
            plan.confluence = route[-1]  # `stage_frame` reserves it, as for a join found by `brook_join`
        return
    # Sized to the settlement: a tameike serving ~15 households reads at roughly Ikegami's 116x74 px
    # (~230 x 150 ft), and the radius scales with the square root of the households it waters, since
    # a reservoir's job is a VOLUME and its depth does not grow with the hamlet. By AREA (feature 280 M12,
    # research/questions/0061-reservoir-ponds-tameike.html): a pond that is its fields' only water took two or three
    # tenths of the land in a Song
    # manual of 1149; this one gathers the fan's drainage below a stream-fed field, so it is held well below that
    # measure - a GUESS, since no page gives how much a feeding stream saves. No storage per hectare is used: the
    # m3/ha figures once cited are on no page read, in any period.
    grow = math.sqrt(plan.spec.households / REF_HOUSEHOLDS)
    prx, pry = 116.0 * grow, 74.0 * grow
    # THE SET-BACK IS SOLVED, NOT PICKED. `pond_clear_of_field` wants the whole ellipse outside the
    # field envelope, and the drain's outfall is not reliably outside it - a comb's envelope bows out
    # around the collector, so on some fans the outfall sits well inside the outline. Ikegami's
    # authored constant (rim + 46 px below the outfall) is true for Ikegami's fan and false for
    # others, which is exactly the failure mode the project's "derive, don't pin" rule names. So the
    # pond walks DOWNSLOPE from the outfall until its rim is genuinely clear, and stops at the first
    # position that is - the nearest legal seat, so the ditch between field and pond stays a ditch.
    back, sway = pond_seat(plan, out, prx, pry, drain_heading(s, name) or (dx, dy), drawn_brook(s, plan))
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
        plan.water_sink = "offmap"
        stage_sink(s, plan)
        return
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
    # The drainage ditch, bowed slightly off the straight line so it reads as dug earth rather than
    # a ruled connector (the gate's `channel_winds_gently` wants the same thing). Drawn in the BASE
    # water block, not the late one: the pond's fill has to paint OVER the ditch's mouth where it
    # overshoots the rim, and a late stroke composites above the fill instead
    # (`pond_fill_covers_channel_mouths`).
    ditch = pond_run(out, drain_heading(s, name) or (dx, dy), (pcx, pcy), (dx, dy))
    # ...and a pond or a run the registry of what stands refuses sends the drain off the frame instead (feature 287, water W53)
    if breaches_any_dike(ditch, s.M.get("dikes") or []) or crosses_mid_run(drawn_brook(s, plan), ditch) or not (s.admits("pond", [pcx, pcy, prx, pry]) and drain_admitted(s, ditch, "pond")):
        # ...and a pond reached only across a dike's crest off its gaps is no pond for this field (feature 287, water W42):
        # the field drains off the frame, whose routes refuse the crest, as for a pond the canvas cannot hold. So is one
        # reached only ACROSS THE BROOK (feature 287 wave 5, water:W08): the ditch would run over the open water mid-run,
        # and the off-map routes refuse that crossing too (`route_refusals`, `hull_route`)
        plan.water_sink = "offmap"
        lay_sink(s, plan)
        return
    s.pond(pcx, pcy, prx, pry)
    plan.sink_pond = (pcx, pcy, prx, pry)
    s.M["meta"]["pond_role"] = "drainage"
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
