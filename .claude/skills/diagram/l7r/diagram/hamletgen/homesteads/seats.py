"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.sitegen.geom import centroid, unit

from ..consts import BUNDLE_PITCH, CLUSTER_ROW_SPAN, CLUSTER_SPAN_FACTOR, LANE_FRONTAGE_STANDOFF, Pt
from ..plan import SitePlan

# ---- STAGE 5: the homesteads --------------------------------------------------------------------


def front_row(plan: SitePlan, count: int, standoff: float = 46.0) -> list[Pt]:
    """Seats for the row of homesteads that FRONTS the field, offset from the field OUTLINE itself.

    Offsetting from the cluster band's straight near face is not the same thing and is not good
    enough: the outline curves away from the band, so a row laid along the face can sit 32 px from
    the field at its middle and 300 px from it at its ends, and `field_ringed` (five farmhouses
    within 165 px of the outline) then fails on a map whose cluster is plainly beside its paddy.
    Following the outline also draws better - a farming hamlet's front row bends with the field edge
    the way a real one does, rather than ruling a straight line across a curved margin."""
    env = plan.envelope
    cen = centroid(env)
    seat = plan.seat
    ax, ay = seat["along"]
    # the stretch of outline this cluster fronts: everything within the band's lateral reach
    # The row spans 1.6x the band's own length along the outline. Confined to `lat` exactly, all its
    # candidates come off one short arc - and if that arc happens to be blocked (crop up to the bund,
    # a delivery ditch's corridor, the field spur), the whole row is refused together and the field
    # ends up ringed by four houses instead of five. Wrapping further round the field costs nothing:
    # a seat too far along is dropped by the caller's own band test.
    # The rolled shape governs how far the row wraps - see `CLUSTER_ROW_SPAN`. Without it the band
    # aspect alone left an "elongated" map drawing 1.2:1, i.e. a declared knob that did not
    # describe the sheet.
    _rowspan = CLUSTER_ROW_SPAN.get(plan.cluster_shape or "crescent", CLUSTER_SPAN_FACTOR)
    span = [(i, p) for i, p in enumerate(env) if abs((p[0] - seat["anchor"][0]) * ax + (p[1] - seat["anchor"][1]) * ay) <= seat["lat"] * _rowspan]
    if len(span) < 2:
        return []
    span.sort(key=lambda ip: (ip[1][0] - seat["anchor"][0]) * ax + (ip[1][1] - seat["anchor"][1]) * ay)
    # SAMPLE BY DENSITY, NOT BY HOUSEHOLD COUNT (2026-08-17). `count` is what the caller still WANTS
    # seated, but using it to space the candidates too made the row's resolution depend on the size
    # of the village rather than on the length of the field edge it fronts - so a 10-household
    # hamlet beside a 28-acre paddy got ten seats spread over a very long outline, several hundred
    # px apart. The near margin is the busiest ground on the map (crop up to the bund, delivery
    # ditches and their corridors, the field spur), so a coarse row loses most of its candidates to
    # blocked ground and leaves the field ringed by three houses instead of five - which is cohort
    # seed 22, where the front row placed 5 of 32 offers and only 3 finished inside `field_ringed`'s
    # 165 px band.
    #
    # THE HONEST SPACING IS ONE BUNDLE PITCH: two homesteads cannot stand closer than that, so
    # sampling finer wastes offers, and sampling coarser leaves gaps a blocked seat cannot recover
    # from. Offering more costs nothing - a seat too far along is dropped by the caller's own band
    # test, and the loop stops as soon as the households are seated. Measured across the cohort:
    # seed 22 goes 3 -> 10 farmhouses within the band (and its gate clean), seed 1 goes 11 -> 15,
    # seed 4 goes 15 -> 16, and no map loses ground. It is also how a farming hamlet really sits -
    # the houses crowd the field they work.
    _span_len = sum(math.dist(span[i][1], span[i + 1][1]) for i in range(len(span) - 1))
    count = max(count, min(int(_span_len / BUNDLE_PITCH) + 1, 64))  # capped so a huge fan cannot make the row unbounded
    out: list[Pt] = []
    for k in range(count):
        idx = span[min(len(span) - 1, round(k * (len(span) - 1) / max(1, count - 1)))][0]
        a, b = env[idx], env[(idx + 1) % len(env)]
        nx, ny = unit(-(b[1] - a[1]), b[0] - a[0])
        if nx * (a[0] - cen[0]) + ny * (a[1] - cen[1]) < 0:
            nx, ny = -nx, -ny
        out.append((a[0] + nx * standoff, a[1] + ny * standoff))
    # ORDER CENTER-OUT, so the row FILLS rather than SPREADS (settlement-review on Inashiro,
    # 2026-08-17). Sampling by density fixed the starved row, but it also handed the placer a dense
    # line of seats along the WHOLE reachable margin in span order, and the caller takes them until
    # the households run out - so the row walked from one end of the arc to the other and the
    # cluster stretched with it. Measured cost on Inashiro: width 569 -> 445 ft at unchanged length,
    # elongation 3.79 -> 5.42 against 1.22 for the authored Ikegami on the identical brief, and two
    # more households pushed past the end of the lane skeleton.
    #
    # Offering the same seats in a different ORDER fixes it without giving the density back: the
    # busiest ground is the middle of the band, the row fills there first, and the `placed >=
    # households` break stops it before it reaches the far ends - which is exactly what
    # `lane_frontage` already does ("ordered from the cluster's center outward, so the lanes fill
    # from their busy end"), and a nucleated hamlet grows the same way, outward from its middle.
    return sorted(out, key=lambda q: math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]))


# `_FIELD_RING_FLOOR` and `_FRONT_ROW_LANE_CAP` lived here and are GONE (feature 126). They were the
# two halves of a rule that judged a front-row seat by its distance to a drawn lane, and they existed
# only because the lanes were drawn BEFORE the houses. Now that the internal lanes are worn
# afterwards, a seat has no lane to be near and the rule had nothing left to mean.
#
# DO NOT REINTRODUCE A DISTANCE-TO-LANE TEST IN THIS STAGE. That is the inversion the whole feature
# removes: a farmhouse is sited by the field it works and the ground it can stand on. Two earlier
# attempts to TUNE this cap are recorded in the git history as dead ends; a third would be worse than
# either, because the thing it measures is no longer on the map when it runs.


def lane_frontage(s: Settlement, seat: Mapping[str, Any], step: float = 86.0, connector: bool = False) -> list[Pt]:
    """Candidate seats along BOTH verges of every internal lane, just outside its no-build corridor.

    Ordered from the cluster's center outward, so the lanes fill from their busy end. The connector
    is skipped: it is the track OUT of the settlement, and lining it with farmhouses would string the
    hamlet along the road instead of nucleating it (that is the `linear` settlement form, a
    different archetype)."""
    out: list[Pt] = []
    off = LANE_FRONTAGE_STANDOFF
    for lane in s.M.get("lanes", []):
        # `connector=True` INVERTS the skip: the caller wants the road itself, because it is siting a
        # linear hamlet along it. Everything else is unchanged.
        if lane.get("web") or (bool(lane.get("connector")) is not connector):
            continue
        pts = lane["pts"]
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            run = math.hypot(x1 - x0, y1 - y0)
            nx, ny = unit(-(y1 - y0), x1 - x0)
            k = 1
            while k * step < run:
                px, py = x0 + (x1 - x0) * (k * step / run), y0 + (y1 - y0) * (k * step / run)
                out += [(px + nx * off, py + ny * off), (px - nx * off, py - ny * off)]
                k += 1
    return sorted(out, key=lambda q: math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]))


def cluster_aspect(xs: list[float], ys: list[float]) -> float:
    """The house cloud's long:short ratio measured on ITS OWN principal axis - rotation-invariant.

    The observable `CLUSTER_DRAWN_ASPECT` is stated in, and the quantity a reader gets by laying a
    ruler along the cluster rather than along the page. A page-axis bbox ratio is not that quantity:
    it tends to 1.0 for any band on a diagonal, and is maximally blind at 45 degrees.

    Principal axis by second moments (a 2x2 covariance eigenvector, closed form via atan2), then the
    EXTENT along and across it. Extent rather than the eigenvalue ratio on purpose - a ruler measures
    the cloud's span, not its variance, and the two differ for an uneven rank (Sawada 3.02 by extent,
    2.72 by PCA sd). Mirrored in the gate; `tests/hamletgen/test_cluster_shape.py` pins the two equal
    by evaluating both on the same point sets, not by comparing source."""
    _n = len(xs)
    if _n < 2:
        return 1.0
    _mx, _my = sum(xs) / _n, sum(ys) / _n
    _sxx = sum((x - _mx) ** 2 for x in xs) / _n
    _syy = sum((y - _my) ** 2 for y in ys) / _n
    _sxy = sum((x - _mx) * (y - _my) for x, y in zip(xs, ys, strict=True)) / _n
    _th = 0.5 * math.atan2(2.0 * _sxy, _sxx - _syy)
    _c, _s = math.cos(_th), math.sin(_th)
    _along = [x * _c + y * _s for x, y in zip(xs, ys, strict=True)]
    _across = [-x * _s + y * _c for x, y in zip(xs, ys, strict=True)]
    _du = max(_along) - min(_along)
    _dv = max(_across) - min(_across)
    return max(_du, _dv) / max(1.0, min(_du, _dv))


def _seat_allowed(s: Settlement, x: float, y: float) -> bool:
    """Is this ground allowed to take a steading on this roll?

    Empty on a first roll. `generate` re-rolls a map whose finished manifest stranded a farmhouse and
    passes the ground those houses stood on - which the previous roll PROVED no way can reach - so the
    retry seats elsewhere. Half a bundle pitch is the radius: enough to clear the pocket, not so much
    that the retry merely nudges the same steading along it."""
    avoid = getattr(s, "_avoid_seats", None)
    if not avoid:
        return True
    return all(math.hypot(x - ax, y - ay) > BUNDLE_PITCH / 2 for ax, ay in avoid)
