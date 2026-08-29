"""STAGE 5-6: the houses on their lane frontage, their appurtenances, and the wells.

Split from hamletgen.py by feature 111; bodies verbatim. See hamletgen/CLAUDE.md.
"""

from __future__ import annotations

import math
import random
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, point_in_poly, seg_dist, segments_cross, surface_water_dist
from l7r.diagram.settlement._knobs import knob_rng
from l7r.diagram.settlement.farm_fixtures import FIXTURE_FT, PERSIMMON_CROWN_FT
from l7r.diagram.sitegen.geom import centroid, unit

from .consts import BUNDLE_PITCH, CLUSTER_DRAWN_ASPECT, CLUSTER_ROW_SPAN, CLUSTER_SPAN_FACTOR, LANE_FRONTAGE_STANDOFF, SUN_CORRIDOR_FT, WEST_SUN_FT, Poly, Pt
from .plan import SitePlan

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
    if len(span) < 2:  # pragma: no cover - a band always spans several outline vertices
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


_WELL_DRAWN_R = 12.0
"""The wellhead's DRAWN half-extent, used when asking how far a candidate seat would push the crop.
It is the `vr` the glyph draws (not the `r` clearance radius), because the frame follows the ink -
`crop_not_held_open_by_one_feature` quotes a well's extent as 16 px across."""

FORM_BOUND: dict[str, float] = {}
"""Per-FORM override of how far from the seat center a homestead may stand, as a multiple of the
seat band's diagonal. EMPTY, deliberately - every form uses the 1.15 default.

A FAILED FIX, recorded so it is not tried again (feature 126). Dispersed and linear maps were given
2.2 and 1.8 here to cure Inashiro seating 13 of its 15 households. It did not cure it: the cause was
`_nucleated` being set from the FORM, which gave a linear map grove-wrapped bundles too large to
fit, and fixing that fixed the count. Measured afterwards on Sawada, the dispersed pool map:
19/19 households in 53.4s at the uniform 1.15, against 19/19 in 53.7s at 2.2 - no seats gained, no
time lost, nothing bought. A wider search bound only permits sprawl the feature exists to prevent,
so the honest value is no override at all."""

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


def stage_homesteads(s: Settlement, plan: SitePlan) -> None:
    """Seat every declared household, and KNOW whether it worked.

    `households_consistent` wants the occupied farmhouses within 0.85-1.05x the declared households -
    a to-scale map depicts essentially every household - so a hamlet that declares 15 and seats 12
    fails, and the authored maps deal with that by tuning a hand-written candidate loop until the
    number comes out. The script instead asks the placer, which is the only thing that actually knows
    whether a seat is free: it draws candidates from the rolled cluster shape and, if the quota is
    still short, GROWS the band and draws more, up to a cap.

    Growing rather than re-rolling is deliberate. A retry with a different seed would re-roll the
    whole map to fix a local shortfall - the expensive, whack-a-mole loop the skill's dev notes warn
    about. Widening the band changes only the ground the candidates come from, so the houses already
    seated stay exactly where they are and the map converges instead of churning."""
    # A YARD KEEPS ITS SUN (GM 2026-08-13; researched in research/homesteads.md, "The threshing
    # yard's sun"). 39 ft is the 9-to-3 drying window at 38N in the 10th month for a minka's ~20 ft
    # ridge; the noon figure is 21. The engine's rule is opt-in and this is where the scripted tier
    # opts in - the hand-authored maps keep their packing until they are converted.
    s.sun_corridor(SUN_CORRIDOR_FT)
    # ...AND THE SAME CORRIDOR NOW COVERS THE GARDEN BEDS (feature 133 T10), inside `sun_corridor`.
    # The belt's afternoon lane is opted into HERE too, though it is only read at `stage_windbreak`:
    # the two sun rules are one decision, made at the same place, for the same reason.
    s.west_sun_lane(WEST_SUN_FT)
    seat = plan.seat
    ax, ay = seat["along"]
    ox, oy = seat["out"]
    rng = random.Random((plan.spec.seed * 2654435761) & 0xFFFFFFFF)
    placed = 0
    lat, dep = seat["lat"], seat["dep"]

    # THE FRONT ROW GOES DOWN FIRST, along the band's field-facing face. A cluster seeded only by
    # its SHAPE fills its whole depth evenly, and on a small hamlet that can leave the field ringed
    # by four houses where `field_ringed` wants five - the map then reads as a settlement that
    # happens to be near a paddy rather than one that works it. Seating a row against the margin
    # first is also just what a farming hamlet looks like: the houses front the field they farm, and
    # the back rows fill in behind them.
    # (no quota guard here: the row is capped at 8 seats and the tier's floor is 10 households, so
    # the front row alone can never meet the ask)
    # TWO passes at two standoffs. `field_ringed` wants five farmhouses within 165 px of the field
    # outline, and a single row of eight candidates at one standoff can land four when the near
    # ground is awkward - the placer refuses a bundle that laps a bund or a ditch, and every refusal
    # is a house that ends up in the back rows instead. Offering the same row again a little further
    # out costs nothing when the first pass filled it and rescues the ring when it did not.
    # EVERY SEAT MUST LIE IN THE BAND. The front row follows the field OUTLINE and the frontage rows
    # follow the lanes, and both can wander well past the cluster on a long fan - which produced a
    # nucleated hamlet with three or four farmsteads strung hundreds of px down the margin. That is
    # a form defect on its own (a nucleus is supposed to read as a nucleus), and it was ALSO the
    # cause of three separate gate failures: a windbreak sized off the furthest house became a green
    # blanket, a copse over the full house bbox left the map no blank ground, and a stray farm past
    # the last well tripped `settlement_dwellings_watered`. Fixing the seats fixes all of it at the
    # source, which is why the percentile guards elsewhere are belt-and-braces rather than the cure.
    # HOW FAR FROM THE SEAT CENTER A HOMESTEAD MAY STAND, and it depends on the FORM (feature 126).
    #
    # A nucleated cluster is the tight case this number was calibrated for and keeps 1.15. The other
    # two forms are not looser versions of it, they are different settlements, and their farmsteads
    # are physically BIGGER: a non-nucleated bundle carries its own grove and yard (see
    # `_place_bundle`, which branches on `_nucleated`), so the same bound seats fewer of them. Left
    # at 1.15 the generator simply dropped households - Inashiro rolled linear and seated 13 of 15,
    # which is a silent shortfall rather than an error.
    #
    # THIS WAS NOT WHAT FIXED THE SHORTFALL, and saying so here saves the next reader from crediting
    # it. Inashiro's 13-of-15 was caused by `_nucleated` being set from the FORM, which gave a linear
    # map grove-wrapped bundles too large to fit; the fix was to set `_nucleated` from whether the
    # form is dispersed (see `stage_water_frame`). Widening the bound alone changed nothing.
    #
    # It is kept because it is DESCRIPTIVE rather than corrective: a dispersed settlement genuinely
    # occupies more ground than a nucleated one - that is what the form IS - and holding it to a
    # nucleated cluster's radius would misrepresent it. The multipliers are not measured optima, and
    # they should not be quoted as if they were; they are the extents the two forms plausibly want.
    #   dispersed - the Tonami case: each farmstead sits in the middle of its OWN holding, so the
    #               settlement's extent is the extent of the land it farms, not of a cluster band.
    #   linear    - strung along the connector, so it grows LONG rather than wide; the bound is a
    #               radius, so a smaller widening buys the length the form needs.
    bound = FORM_BOUND.get(plan.settlement_form, 1.15) * math.hypot(lat, dep)

    def in_band(q: Pt) -> bool:
        return math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]) <= bound

    # THREE standoffs, not two. `field_ringed` wants five farmhouses within 165 px of the field
    # outline and the placer refuses any bundle that laps a bund or a ditch, so a single ring of
    # candidates can land four on awkward ground. Each extra pass is free when the earlier one
    # filled the row.
    # The FRONT ROW is allowed a little further out than the rest - a house hugging the field is
    # part of the settlement wherever the band's nominal circle happens to fall, and `field_ringed`
    # wants five of them within 165 px of the outline.
    # Standoffs run out to 150 px, which is still inside `field_ringed`'s 165 px band. The near
    # ground is often the busiest on the map - crop up to the bund, the collector's out-of-crop
    # stretches with their corridors, the field spur - so a row that stops at 92 px can land four
    # houses where five are wanted while perfectly good ground sits at 120. A farmhouse 150 px from
    # its paddy is still a farmhouse on its paddy.
    # THE FRONT ROW IS ONE RANK, NOT THE WHOLE HAMLET (settlement-review on Inashiro and Mizuguchi,
    # 2026-08-17). Once the row began sampling by density it could seat every household by itself,
    # and it did: the cluster came out a single file along the paddy margin - Mizuguchi 891 x 123 ft,
    # aspect 7.24, with an rms residual of 22 ft about a smooth curve, so NO house stood behind any
    # other anywhere on the map. Inashiro went the same way (elongation 3.79 -> 5.42, width 569 ->
    # 445 ft at unchanged length) against 1.22 for the authored Ikegami on the identical brief. It
    # took the courtyards with it: Mizuguchi's copse collapsed 11 -> 4 clumps and its byres were
    # pushed 20+ ft out of the homestead courtyards into the windbreak, because a one-rank cluster
    # has no interior gap ground left. `consts.py` says the pitch is chosen to keep the cluster
    # "dense enough to read as a nucleus and open enough for its courtyards, its wells and its
    # byres"; a single rank has neither half.
    #
    # THE CAP IS ONE RANK'S WORTH OF THE BAND, derived rather than picked: the margin band is `lat`
    # long, and homesteads in it stand a bundle pitch apart, so `2 * lat / pitch` is how many fit in
    # the rank that fronts the field. Everything past that is a household the flanking and cloud
    # passes should seat BEHIND, which is what makes a nucleus a nucleus. Floored at 6 so
    # `field_ringed` (five farmhouses within 165 px of a big field's outline) can always be met by
    # the row alone - the defect this row exists to prevent.
    front_cap = min(plan.spec.households, max(6, int(2 * lat / BUNDLE_PITCH)))
    # ...AND A FRONT-ROW SEAT MUST ALSO BE REACHABLE FROM A TRACK, not merely near the paddy
    # (settlement-review, Inashiro 2026-08-17 - the same review round as the rank cap above, which
    # is the OTHER half of this defect: that one bounds HOW MANY seats the row takes, this one bounds
    # WHICH). The row runs FIRST and follows the field OUTLINE, which on a long fan strings it
    # hundreds of px past wherever the rolled lane skeleton lies - so the row won every seat and the
    # frontage pass below got the leftovers. Measured on Inashiro: house-to-lane median 109 ft, five
    # houses past 150, a whole seven-farmstead lobe fronting nothing, and a 252 ft lane spur with no
    # house within 96 ft anywhere. That is the defect the frontage pass's own comment below records
    # curing ("a median house-to-lane distance of 94 ft ... with one lane dead-ending in open
    # ground"), returned by a different route - and no gate check can see it, because `field_ringed`
    # is satisfied by exactly the seats that cause it.
    #
    # A CAP, NOT A LADDER - the difference was MEASURED, because the ladder is the shape every other
    # rung in this function uses and here it did nothing. Offering the whole standoff ladder twice,
    # once capped and once admitting anything, left every median where it started (109/59/65/118 ft):
    # the capped pass cannot fill the row on a long fan, so the uncapped pass seated the very houses
    # the cap had just refused. A cap only bites when there is no second chance at the same seats -
    # and none is needed, because the passes BELOW this one (lane frontage, the in-band cloud, four
    # widening rounds) are the real fallback and seat in-band ground by construction.
    #
    # TIGHTENING THE BAND INSTEAD WAS TRIED AND IS WRONG - recorded so it is not retried. Dropping the
    # row's `bound * 1.3` allowance to `bound` made Inashiro WORSE (109 -> 158 ft, houses past 150 px
    # 4 -> 8) and Mizuguchi too (65 -> 93). A front row that cannot follow the field outline does not
    # move inward; it loses its seats to the cloud, which sits further from the tracks still. The
    # row's reach past the band was never the defect - its blindness to the tracks was.
    #
    for standoff in (46.0, 56.0, 66.0, 78.0, 92.0, 110.0, 130.0, 150.0):
        if placed >= front_cap:
            break
        for fx, fy in front_row(plan, min(plan.spec.households, 12), standoff=standoff):
            if placed >= front_cap:
                break
            # NO LANE TEST HERE ANY MORE (feature 126). This used to read
            # `_row_seats < _FIELD_RING_FLOOR or _lane_dist(...) <= _FRONT_ROW_LANE_CAP`, which
            # judged a front-row seat by how near it fell to a drawn lane. The internal lanes are
            # now laid AFTER this stage, so at this moment the only ways on the map are the
            # connector and the field spur - and the cap was therefore demoting good seats for
            # being far from a track that has nothing to do with them. Worse, it made the
            # settlement's shape depend on a way that has not been decided yet, which is the exact
            # inversion this feature exists to remove: a farmhouse is sited by the FIELD it works
            # and the ground it can stand on, and the lane is worn afterwards between the houses.
            if math.hypot(fx - seat["cx"], fy - seat["cy"]) <= bound * 1.3 and _seat_allowed(s, fx, fy) and s.try_place(fx, fy, "plain"):
                placed += 1
    # ...then rows FLANKING the lanes, before any shape fill. A lane exists to be fronted, and a
    # cluster seeded only by its shape leaves them running across empty middle: the review of the
    # first draft measured a median house-to-lane distance of 94 ft against Ikegami's 55, with one
    # lane dead-ending in open ground and no house at its end. Offering the placer seats at exactly
    # the corridor's edge is what puts the doors on the street.
    #
    # THIS PASS IS WHAT BUILDS THE BACK RANK (2026-08-17, and the history is worth two sentences
    # because a comment here was briefly WRONG about it). For part of one day `front_row` sampled by
    # density with no cap and seated every household by itself, this pass placed nothing, and a
    # comment was written saying so - "now a fallback". Three settlement-reviews then showed what
    # that actually meant: the cluster had become a single rank along the paddy, Mizuguchi at aspect
    # 7.24 with no house standing behind any other. The cap above is the fix, and it makes THIS pass
    # load-bearing again: the households past one rank's worth are seated here, behind the front row.
    # Measured on Mizuguchi after the cap, distance from each house to the field outline falls in
    # four bands - 18/41/58/58, then 96/101/116/128, then 193/193/216, then 297 ft - and everything
    # past 150 ft (the front row's furthest standoff) came from this loop.
    #
    # WHAT THE CAP COSTS, recorded rather than left implied: fronting loosens. Mizuguchi's median
    # house-to-lane went back to ~98 ft from the ribbon's 77, with 4 of 12 within 60 ft rather than
    # 10. The ribbon's tighter fronting was an artifact of the defect, not a baseline worth keeping -
    # but ~98 is the figure an early review criticized against Ikegami's 55, and this loop is where
    # a future tightening belongs, since it is the pass now doing the seating.
    # ONLY A LINEAR HAMLET FRONTS A WAY AT SEAT TIME, and the way it fronts is the CONNECTOR.
    #
    # This pass used to run for every map, offering seats along the verges of the internal lanes.
    # Those lanes no longer exist when this runs, so for a nucleated or dispersed hamlet the pass
    # now returns nothing and is pure cost - the front row and the cloud do the seating.
    #
    # For the LINEAR form it is the whole point. A row village IS a settlement strung along a
    # through-route: the road came first, the farmsteads front it, each holding lies behind its own
    # house. That is the one form in which siting a house against a way is historically right, and
    # the connector is the only way on the map that genuinely predates the houses. `lane_frontage`
    # skipped the connector precisely because fronting it "would string the hamlet along the road
    # instead of nucleating it (that is the `linear` settlement form, a different archetype)" - so
    # this is that archetype, asking for exactly what that comment described.
    if plan.settlement_form == "linear":
        for lx, ly in lane_frontage(s, seat, connector=True):
            if placed >= plan.spec.households:
                break
            if in_band((lx, ly)) and _seat_allowed(s, lx, ly) and s.try_place(lx, ly, "plain"):
                placed += 1
    _cloud_placed = 0
    for attempt in range(4):
        if placed >= plan.spec.households:
            break
        # each round widens the band a little (and reaches a little further back from the field)
        wlat, wdep = lat * (1.0 + 0.22 * attempt), dep * (1.0 + 0.16 * attempt)
        want = plan.spec.households * 6 + 30
        for lx, ly in s.cluster_seeds(plan.cluster_shape, 0.0, 0.0, wlat, wdep, want, rng, record=False):
            if placed >= plan.spec.households:
                break
            # THE CLOUD LEANS TOWARD THE FIELD. `cluster_seeds` returns a shape symmetric about the
            # band's middle, which spreads a hamlet's houses as far behind the settlement as in front
            # of it - and the ground in FRONT is the ground that matters: `field_ringed` wants five
            # farmhouses within 165 px of the outline, and on a map whose near margin is largely crop
            # and ditch corridor only four of them land there. Compressing the away-from-field
            # coordinate pulls the whole cloud a quarter closer without changing its shape or count,
            # which is also how a farming hamlet really sits - the houses crowd the fields they work
            # and thin out behind.
            ly = -wdep + (ly + wdep) * 0.75
            _sx4, _sy4 = seat["cx"] + ax * lx + ox * ly, seat["cy"] + ay * lx + oy * ly
            if _seat_allowed(s, _sx4, _sy4) and s.try_place(_sx4, _sy4, "plain"):
                placed += 1
                _cloud_placed += 1
    # THE SHAPE IS RECORDED ONLY IF THE CLOUD ACTUALLY SHAPED THE CLUSTER (2026-08-17).
    # `cluster_seeds` used to stamp `meta.cluster_shape` on its first attempt, BEFORE it knew how
    # many seats it would win - which was harmless while the cloud either ran for the whole hamlet
    # or not at all. The front-row cap changed that: the rows now seat one rank and the cloud seats
    # the SURPLUS, so on Sawada and Inashiro a knob describing a minority of the houses started
    # being stamped for the first time. It is not idle bookkeeping - `check_village/driver.py`'s
    # `TWIN_AXES` reads "the declared knob if present, else the cluster-bbox aspect", so Sawada
    # began reporting its shape as "round" to the twin detector while drawing a 3.48:1 band.
    #
    # A DECLARATION MUST DESCRIBE THE DRAWING. The cloud shaped the cluster only if it seated most
    # of it; below that the frontage rows did, and the rolled shape went unhonored exactly as it
    # does when the cloud never runs at all. `meta.cluster_seeding` still records which happened, so
    # nothing goes silent - that is the invariant `settlement_records_cluster_seeding` holds.
    # THE SHAPE IS ALWAYS HONORED NOW, so it is always declared (2026-08-19). This used to stamp the
    # knob only when the CLOUD seated most of the cluster, on the correct principle that a
    # declaration must describe the drawing - but the census behind `CLUSTER_BAND_ASPECT` showed the
    # cloud never runs at all, so the guard meant the knob was declared on no map and honored on no
    # map. It binds at the cluster BAND now (`seat_cluster`), which is what the front rows are seated
    # along, so every map both honors and declares it and `TWIN_AXES` reads a shape the sheet
    # actually has.
    # ...BUT ONLY IF THE SHEET ACTUALLY HAS THAT SHAPE. Measured, and this is the third thing the
    # shape work turned up: on a 20-household hamlet the LANE SKELETON seats most of the cluster
    # through `lane_frontage`, and a T spreads houses two ways whatever the band and the row do -
    # Kashikawa declares `elongated` and draws 1.0:1. The band and row bindings are real (Inashiro
    # 3.3:1 crescent, Mizuguchi 1.7:1 round, Sawada 1.1:1 round) but they do not outrank the
    # skeleton, so a blanket declaration would put a shape on the manifest that `TWIN_AXES` reads
    # and the sheet does not have - the same "declaration must describe the drawing" failure the
    # old cloud-only guard was written for, in a worse form because it would look honored.
    #
    # So the DRAWN aspect decides. Where the shape bound, it is declared; where the skeleton
    # overrode it, `cluster_shape_unhonored` records the roll that did not take, because a knob
    # that silently fails to bind is what this whole defect was. `cluster_shape_matches_the_drawing`
    # gates it.
    # MEASURED ON THE CLUSTER'S OWN AXIS, NOT THE PAGE'S (2026-08-19, and this is the second time
    # this one guard has been caught measuring the wrong quantity). The first cut took
    # `max(dx,dy)/min(dx,dy)` over the axis-aligned bbox of house centers - and that ratio collapses
    # toward 1.0 for a band on a diagonal no matter how string-like the cluster is, because it is a
    # function of the field margin's COMPASS BEARING rather than of the cluster's proportion. It is
    # maximally blind at exactly 45 degrees.
    #
    # Three independent settlement-review passes caught it on the same day, with numbers, and it
    # failed in BOTH directions across the shipped pool - axis-aligned vs own-axis:
    #     Kashikawa 1.22 vs 3.83  (rolled `elongated`, DREW 3.8:1, and was recorded unhonored)
    #     Sawada    1.25 vs 3.02  (declared `round`, drew a string - falsely HONORED)
    #     Mizuguchi 2.36 vs 2.77  (declared `round` over its own ceiling on the honest measure)
    #     Inashiro  3.18 vs 3.59  (band near vertical, so the two roughly agree)
    # So it denied an honored knob on one map and honored a contradicted one on another, and
    # `TWIN_AXES` reads this field. The `CLUSTER_DRAWN_ASPECT` docstring promises a quantity that can
    # be "read off a finished map with a ruler" - and a reader lays the ruler ALONG the cluster.
    _cxs = [h["x"] for h in s.M.get("houses", [])] or [0.0]
    _cys = [h["y"] for h in s.M.get("houses", [])] or [0.0]
    _drawn = cluster_aspect(_cxs, _cys)
    _lo, _hi = CLUSTER_DRAWN_ASPECT.get(plan.cluster_shape or "crescent", (1.9, 4.2))
    if _lo <= _drawn <= _hi:
        s.M["meta"]["cluster_shape"] = plan.cluster_shape
    else:
        s.M["meta"]["cluster_shape_unhonored"] = plan.cluster_shape
    s.M["meta"]["cluster_aspect_drawn"] = round(_drawn, 2)
    # THE ROLLED SHAPE MUST LEAVE A TRACE EVEN WHEN THE CLOUD NEVER RUNS (known-open ledger
    # 2026-08-16, Kashikawa: the front rows + lane frontage seated all 20 households, the
    # cluster-seeds cloud never ran, and the rolled cluster_shape knob went unhonored with no
    # trace on the manifest - a knob that can silently not-record is the "check that never runs"
    # shape). Record the seeding mode always: "cloud" when cluster_seeds ran (it records
    # meta.cluster_shape itself), "frontage" when the rows/frontage passes seated every house and
    # the rolled shape went unhonored. `settlement_records_cluster_seeding` holds the invariant.
    # ...and this stays a SEPARATE record, keyed on what actually seated the houses rather than on
    # whether the shape got stamped. It used to be derived from the presence of `cluster_shape`,
    # which stopped meaning anything the moment the shape was always declared.
    s.M["meta"]["cluster_seeding"] = "cloud" if _cloud_placed * 2 >= max(1, plan.spec.households) else "frontage"
    plan.placed = s.farmsteads()
    # THE TRIM MOVED OUT OF THIS STAGE (feature 126). It existed because the skeleton was laid
    # before the houses, so its arms had to be shortened afterwards once there was something to
    # measure them against. The arms are now laid after the houses and fitted to them, so there is
    # nothing here to trim: at this moment the only ways drawn are the connector and the field spur,
    # and trimming those against house positions is meaningless. `stage_web` trims once the lanes it
    # trims actually exist.


# ---- STAGE 6: what stands among the houses ------------------------------------------------------


def stage_appurtenances(s: Settlement, plan: SitePlan) -> None:
    """Communal wells and shared draft byres, dropped into the courtyards the homesteads left.

    AFTER the houses (they slot into the gaps the final layout produced, which is a thing only the
    finished layout knows) and BEFORE the grove (whose canopy then skips them). Both are sized off
    the houses that actually landed, not off the declared household count: a byre is roughly one per
    four or five households, and the wells cover the cluster's real extent."""
    houses = s.M.get("houses", [])
    if not houses:  # pragma: no cover - a hamlet with no houses fails the gate long before here
        return
    place_wells(s, plan, houses)
    s.draft_byres(fraction=0.22, gap=60)


# HOUSEHOLD BAMBOO (feature 133 T48, GM 2026-08-27; research/vegetation.md "Bamboo: how common, where it
# stood, and how to show it", the T48 pass). READ: on the Tonami plain every farmstead stood in its own
# grove (kainyo) and bamboo was one of its named species beside a dominant cedar, valued as "important
# daily-life material"; the bamboo stood WITH the storehouses on the plot's south side there, and at a
# plot's wet edge for its roots elsewhere; the grove as a whole faces the local wind (N+W, W, or S+W by
# region - summary-only). So the SIDE is rolled per farmstead, weighted toward the back and the shed's
# side, never fixed; and the PRESENCE rate is a GUESS - no source gives a share; "one of several secondary
# species" says common but not universal - set like the shed's, and labeled. Sizes are a working strip.
HOUSEHOLD_BAMBOO_PREVALENCE = 0.6
HOUSEHOLD_BAMBOO_FT = (22.0, 16.0)
_HOUSEHOLD_BAMBOO_SIDES = (("back", 0.45), ("shed", 0.30), ("wind", 0.15), ("side", 0.10))


def household_bamboo(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> list[Poly]:
    """Seat a small bamboo strip beside each farmstead that keeps one, per the `bamboo` knob.

    Seated in `stage_hinterland`, AFTER the web and the notice board (T49): seated with the sheds it
    was in the web's way, and the web threaded through it (two lanes on Inashiro) - and putting it in
    the web's fabric instead re-threaded the whole web and broke it. Seated after, the strip keeps 6 ft
    off every lane and clear of every placed footprint, the board and the wells, and the scrub keeps
    out of it (a soft keep-out, like every wood). Drawn by `stage_bamboo` with the stand glyph. Per house: presence by `HOUSEHOLD_BAMBOO_PREVALENCE`, side by the weighted roll
    above, both from the house's own position (positional randomness). A candidate that lands on a
    footprint, a lane, a paddy, the marsh or the pond is refused and the next side tried; a farmstead
    with no room keeps none. Returns the count seated."""
    out: list[Poly] = []
    if plan.bamboo not in ("homestead", "both") or not houses:
        return out
    px = s.px
    sw, sh = px(HOUSEHOLD_BAMBOO_FT[0]), px(HOUSEHOLD_BAMBOO_FT[1])
    wx, wy = plan.wind
    fields = [list(f) for f in s.field_polys]
    marsh = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("poly")]
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(6.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    for h in houses:
        hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
        if s._hjit(hx, hy, 95.0) >= HOUSEHOLD_BAMBOO_PREVALENCE:
            continue
        th = math.radians(float(h.get("rot", 0.0)))
        ca, sa = math.cos(th), math.sin(th)
        gap = px(6.0)
        # candidate centers in the house's local frame: back (-y, behind the house), the shed side
        # (local -x, with the kura), the windward side, the other flank
        shed_side = h.get("shed_side", "W")
        local = {
            "back": (0.0, -(hh / 2 + gap + sh / 2), sw, sh),
            "shed": ((-(hw / 2 + gap + sh / 2)) if shed_side != "N" else 0.0, 0.0 if shed_side != "N" else -(hh / 2 + gap + sh / 2), sh if shed_side != "N" else sw, sw if shed_side != "N" else sh),
            "side": (hw / 2 + gap + sh / 2, 0.0, sh, sw),
        }
        wlx, wly = wx * ca + wy * sa, -wx * sa + wy * ca  # the wind in the house's frame
        local["wind"] = (wlx * (hw / 2 + gap + sh / 2), wly * (hh / 2 + gap + sh / 2), sw if abs(wly) >= abs(wlx) else sh, sh if abs(wly) >= abs(wlx) else sw)
        # the rolled side first, then the others in their listed order as fallbacks
        roll = s._hjit(hx, hy, 96.0)
        first = _HOUSEHOLD_BAMBOO_SIDES[-1][0]
        acc = 0.0
        for name, wgt in _HOUSEHOLD_BAMBOO_SIDES:
            acc += wgt
            if roll < acc:
                first = name
                break
        order = [first] + [nm for nm, _ in _HOUSEHOLD_BAMBOO_SIDES if nm != first]
        seated = False
        for name in order:
            if seated:
                break
            lx0, ly0, cw, ch = local[name]
            # two offsets per side (T49): against the house, then a strip's depth further out - the
            # lanes now stand where the near seat often is, and a strip 16 ft off the wall is still
            # the household's own
            for k in (0.0, 1.0):
                d = math.hypot(lx0, ly0) or 1.0
                lx, ly = lx0 + lx0 / d * k * sh, ly0 + ly0 / d * k * sh
                cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                if _strip_blocked(s, cx, cy, cw, ch, hx, hy, fields, marsh, pond, lanes):
                    continue
                ring = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2)]
                out.append(ring)
                plan.bamboo_roles.append("homestead")
                s.placed.append((cx, cy, cw, ch))
                s.block_polys.append(ring)
                seated = True
                break
    return out


def _strip_blocked(
    s: Settlement, cx: float, cy: float, cw: float, ch: float, hx: float, hy: float, fields: Sequence[Poly], marsh: Sequence[Poly], pond: Any, lanes: Sequence[tuple[Poly, float]]
) -> bool:
    """Would a household bamboo strip centered here stand on something? Its own farmhouse is not something."""
    if cx - cw / 2 < 30 or cy - ch / 2 < 30 or cx + cw / 2 > s.W - 30 or cy + ch / 2 > s.H - 30:
        return True
    corners = [(cx - cw / 2, cy - ch / 2), (cx + cw / 2, cy - ch / 2), (cx + cw / 2, cy + ch / 2), (cx - cw / 2, cy + ch / 2), (cx, cy)]
    for px_, py_, pw, ph, *_ in s.placed:
        if px_ == hx and py_ == hy:
            continue
        if abs(cx - px_) < (cw + pw) / 2 + 2 and abs(cy - py_) < (ch + ph) / 2 + 2:
            return True
    for key in ("wells", "kosatsuba", "byres", "farm_sheds"):  # everything seated between the sheds and this pass (T49)
        for o in s.M.get(key, []):
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (cw + ow) / 2 + 6 and abs(cy - float(o["y"])) < (ch + oh) / 2 + 6:
                return True
    for poly in list(fields) + list(marsh):
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) or min(seg_dist(q[0], q[1], poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < 6.0 for q in corners):
            return True
    # A LANE THROUGH THE STRIP, not only past its corners (feature 137, cohort seed 03): five sample
    # points on a 22 by 16 ft strip let a lane cross it diagonally between them, and
    # `lanes_clear_of_bamboo` walks the tread's quarter-points. So the tread is also tested as a
    # segment against the strip's edges - a crossing, or an end inside, is a stand on a lane.
    _edges = [(corners[k], corners[(k + 1) % 4]) for k in range(4)]
    for pts, half in lanes:
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            if any(seg_dist(q[0], q[1], a, b) < half for q in corners):
                return True
            if any(segments_cross(a, b, e0, e1) for e0, e1 in _edges) or any(abs(p[0] - cx) < cw / 2 and abs(p[1] - cy) < ch / 2 for p in (a, b)):
                return True
    # the dry hem's plots and the watercourses (unlock tripwire seed 47: a fixture on a dry plot and one
    # on the stream - neither is a paddy, a lane or the pond, so nothing above saw them), and any crown
    # already drawn (seed 37: a fixture seated under a grove crown drawn two stages earlier)
    for o in s.M.get("dry_plots", []):
        poly = [(float(a), float(b)) for a, b in o.get("poly") or []]
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) or min(seg_dist(q[0], q[1], poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < 3.0 for q in corners):
            return True
    if any(s._on_watercourse(q[0], q[1], pad=4.0) for q in corners):
        return True
    tc = s.M.get("tree_crowns") or []
    for k in range(0, len(tc) - 2, 3):
        tx, ty, tr = float(tc[k]), float(tc[k + 1]), float(tc[k + 2])
        hd = math.hypot(cw, ch) / 2  # the check squares a RAKED footprint on its half-diagonal; mirror it
        if max(abs(cx - tx) - hd, 0.0) ** 2 + max(abs(cy - ty) - hd, 0.0) ** 2 < (tr + 0.6) ** 2:
            return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0


# FARMSTEAD FIXTURES (feature 133 T53-T59, GM 2026-08-27; research/homesteads.md "The farmstead's
# fixtures"). Each row: the kind, the per-hamlet PREVALENCE BAND (rolled once per map from the seed -
# two hamlets differ honestly where the record gives a range), and the seats tried in the house's
# local frame (+y = the sunny front where the yard is, -y = the back wall, -x = the kura side). The
# first seat is rolled where the record shows two forms; the rest are fallbacks. Every number is
# labeled in the research entry:
#   privy    READ  an independent outbuilding was "普通" (Nipponica) - near-universal; sited at the back
#                  door, by the naya, or at the gate (戸口便所) - three attested seats, so rolled
#   woodpile READ  a woodshed for firewood/charcoal on the reconstructed farmstead (Boso-no-Mura);
#                  Sugiura counts the SHED on 0.76 - a stack under the eaves is the cheaper, older
#                  form; its wall is a GUESS (the back wall or the kura's, out of the rain)
#   manure   READ  in Han China the latrine stood over the pigsty (AIC) - muck and privy are one
#                  cluster; in Japan the pit stood "near the stable, under the eaves" (SUMMARY-ONLY);
#                  so the heap is seated beyond the privy; the share is a GUESS (Sugiura: a SHED on 0.24)
#   bath     READ  the goemon-buro "was used widely in self-sufficient farm villages" (Mizumaki); Sugiura:
#                  a bath SHED on 0.29, IN the house on 0.53 - two forms, so only the shed share is drawn
#   coop     READ  "farmers in most regions of China managed to keep a pig and some chickens in their
#                  yard" (Animals through Chinese History); a ground-level enclosure (Qimin Yaoshu);
#                  the share is a GUESS bounded by "most regions"
#   shrine   READ  two patterns - every house, or only certain old families (Tokushima; ja.wikipedia);
#                  the GM chose the rare pattern (T58); Sugiura 0.03; corner NE (kimon, READ), NW
#                  (17 of 37, SUMMARY-ONLY), SW (Tokushima, READ) - rolled
#   persimmon READ "どこの庭先にも柿の木が植えてある" and Miyazaki Yasusada urged planting them round the
#                  homestead; it shades the house in summer, so it stands beside it (side a GUESS)
FIXTURE_BANDS: dict[str, tuple[float, float]] = {
    "privy": (0.85, 0.95),
    "woodpile": (0.75, 0.95),
    "manure": (0.40, 0.70),
    "bath": (0.20, 0.45),
    "coop": (0.50, 0.80),
    "shrine": (0.03, 0.08),
    "persimmon": (0.80, 0.95),
}
_FIXTURE_ORDER = ("privy", "manure", "bath", "coop", "woodpile", "shrine", "persimmon")  # the buildings before the stack, which has the most seats
_PRIVY_SEATS = (("back", 0.60), ("gate", 0.25), ("naya", 0.15))
PRIVY_SUN_MIN_FT = 18.0  # the sun-side search starts at the house wall and steps out; measured free ground begins 24-32 ft
# 48, NOT 72 (settlement-review 2026-08-29, acceptance). At 72 ft the search walked the privy out past
# its own work yard and, in a cluster where the next farmhouse is 50 ft away, out of its own homestead
# altogether: 15 of 86 privies and manure pits ended up nearer ANOTHER house than the one they serve,
# against 0 of 52 on main - a legibility defect this feature CREATED, and one no check can see, because
# nothing tests which farmstead a fixture belongs to. The comment that used to sit on 72 claimed it
# "stops where a fixture would no longer read as belonging to that homestead"; that was the property it
# was chosen for and it did not hold. Wang & Ochiai gives a DIRECTION, not a distance, so the radius is
# ours to set and it belongs against the house: the three attested seats are all at the wall.
PRIVY_SUN_MAX_FT = 48.0
PRIVY_SUNNY_SHARE = 0.727  # the share of outhouses seated SE-to-S: Wang & Ochiai 2022 measured 72.7% in
# Arakawa village, and the GM (2026-08-29) ruled the figure be used literally rather than rounded. The
# reason the record gives is fermentation, not wind - see the note at the seat roll.
_SHRINE_CORNERS = (("NW", 0.45), ("NE", 0.35), ("SW", 0.20))
_WALL_GAP_FT = 3.5  # the review measured -0.3 ft at 3.0 against the drawn wall; half a foot of true daylight
_SALT = {"privy": 101.0, "manure": 102.0, "woodpile": 103.0, "bath": 104.0, "coop": 105.0, "shrine": 106.0, "persimmon": 107.0}


def nearer_own_house(seat: tuple[float, float, float, float], hx: float, hy: float, ca: float, sa: float, others: Sequence[Pt]) -> tuple[int, float, float]:
    """Sort key preferring a fixture seat that is nearer its OWN farmhouse than any other house's.

    `seat` is (dx, dy, w, d) in the house's own raked frame; `ca`/`sa` are that rake's cosine and sine.
    Returns (0 if the seat belongs unambiguously to this house else 1, distance from it) - so a caller
    that sorts by it keeps its own candidate order within each class and only demotes the seats a
    reader would attribute to the neighbor.

    Lifted out of the privy branch's closure (GM 2026-08-28: an inner function that is hard to test
    gets lifted out) so the manure heap can share ONE body with it, and so the rule can be asked with
    two tuples instead of a whole settlement."""
    _mx, _my = hx + seat[0] * ca - seat[1] * sa, hy + seat[0] * sa + seat[1] * ca
    _dmine = math.hypot(_mx - hx, _my - hy)
    if not others:
        return (0, _dmine, -_dmine)
    _dother = min(math.dist((_mx, _my), _o) for _o in others)
    # The third element is the MARGIN, negative when the seat is unambiguously this house's. Sorting by
    # it does what a flag cannot: where no candidate is unambiguous - which is the common case for a
    # heap that must lie beyond a privy already on the neighbor's side - it still picks the LEAST
    # misattributable of them, instead of leaving the arbitrary first one in place.
    return (0 if _dmine < _dother else 1, _dmine, _dmine - _dother)


def _roll(weights: Sequence[tuple[str, float]], u: float) -> str:
    acc = 0.0
    for name, w in weights:
        acc += w
        if u < acc:
            return name
    return weights[-1][0]


def farmstead_fixtures(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat and draw the small fixtures of every farmstead. Returns the count placed.

    Seated in `stage_hinterland` after the web and the board, like the household bamboo (T49): a
    fixture hugs its house and is tested against every placed footprint, lane, paddy, marsh and pond
    (`_strip_blocked`), so the web is never re-threaded and nothing is drawn on anything. Presence
    per house is positional (`_hjit`) against the hamlet's own share, which is rolled once per map
    inside the band above and declared in meta for the gate. Every seated fixture joins `s.placed`
    and `s.block_polys`, so the bamboo strips and the scrub keep off it."""
    if not houses:
        return 0
    rng = knob_rng(s.seed, "farm_fixtures")
    shares = {k: round(lo + rng.random() * (hi - lo), 3) for k, (lo, hi) in FIXTURE_BANDS.items()}
    s.M["meta"]["farm_fixtures"] = dict(shares)
    mins = {k: int(v) for k, v in plan.fixtures_min.items() if k in FIXTURE_BANDS}
    if mins:
        s.M["meta"]["farm_fixtures_min"] = dict(mins)
    px = s.px
    g = px(_WALL_GAP_FT)
    fields = [list(f) for f in s.field_polys]
    marsh = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("poly")]
    pond = s.M.get("pond")
    lanes = [([(float(a), float(b)) for a, b in ln["pts"]], float(ln.get("w", 3)) / 2 + px(3.0)) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    count = 0
    shrines_left = max(1, round(shares["shrine"] * len(houses)), mins.get("shrine", 0))  # RARE means rare: positional luck cannot exceed the share (a spec floor may)
    # THE FLOOR (T61, GM 2026-08-27: "a min number of something which may or may not appear"): after the
    # rolled pass, any kind short of its spec'd minimum is forced onto the houses that lack it, in
    # positional order, until the floor is met or every house has been tried
    forced: set[str] = set()
    for h in list(houses) + [dict(h, _force=True) for h in sorted(houses, key=lambda q: s._hjit(float(q["x"]), float(q["y"]), 108.0))]:
        if h.get("_force"):
            have = {k: 0 for k in FIXTURE_BANDS}
            for rec in s.M.get("farm_fixtures", []):
                have[rec["kind"]] = have.get(rec["kind"], 0) + 1
            have["persimmon"] = len(s.M.get("persimmons", []))
            forced = {k for k, v in mins.items() if have.get(k, 0) < v}
            if not forced:
                break
        hx, hy, hw, hh = float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])
        rot = float(h.get("rot", 0.0))
        th = math.radians(rot)
        ca, sa = math.cos(th), math.sin(th)
        shed_side = h.get("shed_side", "W")
        privy_at: tuple[float, float] | None = None

        for kind in _FIXTURE_ORDER:
            if h.get("_force"):
                own = (round(hx, 1), round(hy, 1))
                has = any(r["kind"] == kind and tuple(r.get("of", ())) == own for r in s.M.get("farm_fixtures", [])) or (
                    kind == "persimmon" and any(tuple(r.get("of", ())) == own for r in s.M.get("persimmons", []))
                )
                if kind not in forced or has:
                    continue
            elif s._hjit(hx, hy, _SALT[kind]) >= shares[kind]:
                continue
            if kind == "shrine" and shrines_left <= 0:
                continue
            u = s._hjit(hx, hy, _SALT[kind] + 0.5)
            if kind == "persimmon":
                r = px(PERSIMMON_CROWN_FT)
                # a raked house is a circumscribed SQUARE to the canopy keep-out (_canopy_keepouts mirrors
                # structures_clear_of_trees), so the trunk stands a half-diagonal + the crown out from the center
                reach = math.hypot(hw / 2, hh / 2) + r + s.CANOPY_PAD + 1.0
                tseats = [(reach, hh * 0.1), (-reach, hh * 0.1), (reach * 0.75, -reach * 0.75), (-reach * 0.75, -reach * 0.75), (reach * 0.75, reach * 0.75), (-reach * 0.75, reach * 0.75)]
                if u < 0.5:
                    tseats[0], tseats[1] = tseats[1], tseats[0]
                for lx, ly in tseats:
                    cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                    # the TRUNK is tested against drawn footprints, not the plot reservations: a yard tree
                    # stands at a plot's edge, and in a nucleated cluster the reservations tile the ground
                    if _trunk_blocked(s, cx, cy, px(4.0), fields, marsh, pond, lanes):
                        continue
                    # no tree on a roof: the SAME keep-outs and the same test the grove drawer uses, so
                    # structures_clear_of_trees (which mirrors them) cannot disagree with this seat
                    rects, circles = s._canopy_keepouts((cx - r - 40, cy - r - 40, cx + r + 40, cy + r + 40))
                    if s._crown_covers(cx, cy, r, rects, circles, pad=s.CANOPY_PAD):
                        continue
                    s.persimmon(cx, cy, of=(hx, hy))
                    s.placed.append((cx, cy, px(4.0), px(4.0)))
                    count += 1
                    break
                continue
            w, d = px(FIXTURE_FT[kind][0]), px(FIXTURE_FT[kind][1])  # along the wall, out from it
            # candidate seats as (lx, ly, w_local, h_local); the fixture is drawn raked with the house
            if kind == "privy":
                seat = {
                    "back": (hw * 0.3, -(hh / 2 + g + d / 2), w, d),
                    "gate": (-hw * 0.35, hh / 2 + g + d / 2, w, d),
                    "naya": ((hw / 2 + g + d / 2), -hh * 0.25, d, w) if shed_side == "N" else (-(hw / 2 + hw * 0.32 + g + d / 2), -hh * 0.25, d, w),
                    # THE SUN SIDE, which the record documents and this seat table did not have (feature 152
                    # T07). The three seats above are all north or flank: measured on the pool before this
                    # change, every privy on every map sat at bearing 33-73 degrees from its house. The source
                    # the GM ruled on puts 72.7% of them SOUTHEAST to SOUTH, so a seat has to exist there.
                }
                first = _roll(_PRIVY_SEATS, u)
                seats = [seat[first]] + [seat[k] for k, _ in _PRIVY_SEATS if k != first]
                # THE OUTHOUSE FACES THE SUN, AT THE RATE THE RECORD GIVES (feature 152 T07, GM 2026-08-29:
                # "we should literally use the 72.7% number for the chance of any given outhouse being in the
                # southeast and south directions"). Wang & Ochiai's survey of farmhouses in Arakawa village
                # (JAABE 21:6, 2022) found toilets "tended to be located in southeast and south directions,
                # with a total percentage at 72.7%, as a relatively warm temperature helped quick fermentation
                # of excrements" - night soil was fertilizer, and the sun on that side sped the composting.
                #
                # NOT WIND. A settlement-review found every privy on Sawada standing upwind of its own house
                # and proposed seating them downwind; the research pass sent to settle it CONTRADICTED that -
                # the same paper's wind-siting finding covers storage buildings and retirement houses, not
                # toilets, and the words leeward, downwind, odor and hygiene appear nowhere in it. So the
                # defect the review found was real (the seat was north on every map, because these offsets are
                # in the HOUSE's frame and houses draw at rot 0-4) and its proposed cause was wrong.
                #
                # Direction is the primary rule and the attested seats are the tiebreak: the three seats keep
                # their own weights (`_PRIVY_SEATS`) WITHIN each group, so a map that cannot put a privy to the
                # southeast still seats it where the record says privies go.
                _u_dir = s._hjit(hx, hy, _SALT[kind] + 0.25)
                # THE SUN SIDE IS SEARCHED, NOT GUESSED AT (feature 152 T07 round 2, GM 2026-08-29).
                # The first attempt offered the sector a handful of hand-picked offsets - a couple of
                # bearings at a couple of radii, straight out from the house wall - and they happened to
                # land on the work yard or a garden, so the placer fell through to the old north-east seat
                # and the realized share stuck at 43.8%. I read that plateau as the ground being full and
                # said so; the GM asked the obvious question back - the real farmsteads the 72.7% comes
                # from had threshing yards too, so why can ours not do what they did? Measured in answer,
                # on Sawada: EVERY one of the 19 houses has free sun-side ground, 49 to 151 clear 6x6 ft
                # spots each, the nearest 24-32 ft out - the same radius the privy already uses on its
                # north-east side. The yard blocks a slice of a 90-degree arc, not the side. The plateau
                # was evidence about my offsets, not about the ground.
                #
                # So the sector is walked instead: bearings across SE-to-S, radii outward from the house,
                # NEAREST FIRST (the attested seats are all against the house - back door, gate, naya - so
                # the privy belongs as close as the ground allows), and `_strip_blocked` below takes the
                # first that is clear. Bearings are COMPASS bearings in map space, converted back through
                # the house's own rake, so a raked farmhouse still gets a true southeast seat.
                _sun: list[tuple[float, float, float, float]] = []
                for _r_ft in range(int(PRIVY_SUN_MIN_FT), int(PRIVY_SUN_MAX_FT) + 1, 4):
                    for _b in range(1125, 2026, 75):  # 112.5 to 202.5 degrees, tenths
                        _bd = _b / 10.0
                        _rr = px(float(_r_ft))
                        _dx, _dy = _rr * math.sin(math.radians(_bd)), -_rr * math.cos(math.radians(_bd))
                        _sun.append((_dx * ca + _dy * sa, -_dx * sa + _dy * ca, w, d))
                _sun.sort(key=lambda q: (math.hypot(q[0], q[1]), abs(math.degrees(math.atan2(q[0] * ca - q[1] * sa, -(q[0] * sa + q[1] * ca))) % 360.0 - 157.5)))
                # ...AND A FIXTURE BELONGS TO THE HOMESTEAD IT SERVES. A seat closer to a neighbor's
                # farmhouse than to its own is drawn in that neighbor's yard as far as a reader is
                # concerned, whatever the record says - so the sun list drops any seat that is not
                # strictly nearest its own house. This is the ownership test the 72 ft radius was
                # trusting the geometry to provide, made explicit.
                # A STRICT "must be nearest to its OWN house" filter was tried here and cost too much.
                # It states the defect exactly - a fixture nearer a neighbor's farmhouse reads as theirs -
                # but in a cluster the sun side of one house often IS nearer the next, and filtering on it
                # rejected seats that sit honestly in their own yard: privies fell to 2 of 11 declared on
                # Mizuguchi and the sun share to 49%. The bound that does the work without the collateral
                # is the RADIUS (`PRIVY_SUN_MAX_FT`, cut 72 -> 48): a seat against its own house is in its
                # own yard whoever else is near. Ownership stays as a TIE-BREAK - among seats the ground
                # allows, one that is nearer its own house than any other comes first.
                _others = [(float(_h["x"]), float(_h["y"])) for _h in houses if (float(_h["x"]), float(_h["y"])) != (hx, hy)]
                if _others:

                    def _mine_first(
                        _q: tuple[float, float, float, float], _hx: float = hx, _hy: float = hy, _ca: float = ca, _sa: float = sa, _oth: list[Pt] = _others
                    ) -> tuple[int, float]:  # the loop's values bound as defaults - this closure outlives the iteration
                        _k = nearer_own_house(_q, _hx, _hy, _ca, _sa, _oth)
                        return (_k[0], _k[1])

                    _sun.sort(key=_mine_first)
                seats = (_sun + seats) if _u_dir < PRIVY_SUNNY_SHARE else seats
            elif kind == "manure":
                if privy_at is not None:
                    plx, ply = privy_at
                    out_ = -1.0 if ply < 0 else 1.0
                    # BEYOND THE PRIVY, and with somewhere to go when that one spot is taken (feature 152
                    # T16). Three candidates seated 3 of a declared 8 per map: the heap is placed against
                    # the privy, and where the privy now sits on the sun side the ground just past it is
                    # often the work yard. The researched rule is only that the heap lies BEYOND the privy
                    # (research/homesteads.md) - which these all do; they differ in how far and how wide.
                    # ...AND NOT AT A FIXED OFFSET (feature 152 T17). Every heap sat the SAME distance
                    # beyond its privy - an acceptance review measured 15 of 19 pairs at |dy| 9.4-9.9 ft
                    # with |dx| under 1 ft - so the pair read as one stamp repeated down the row. The
                    # researched rule is only that the heap lies BEYOND the privy; how far beyond is ours,
                    # and real yards vary. Jittered off the homestead's own position so it is stable for a
                    # given farmstead and differs between them.
                    _pout = px(FIXTURE_FT["privy"][1]) / 2 + g + d / 2 + px(9.0) * (s._hjit(hx, hy, 102.4) - 0.5)
                    seats = [
                        (plx, ply + out_ * _pout, w, d),
                        (plx + w * 1.1, ply, w, d),
                        (plx - w * 1.1, ply, w, d),
                        (plx + w * 1.1, ply + out_ * _pout, w, d),
                        (plx - w * 1.1, ply + out_ * _pout, w, d),
                        (plx, ply + out_ * (_pout + px(10.0)), w, d),
                        (plx + w * 1.9, ply, w, d),
                        (plx - w * 1.9, ply, w, d),
                    ]
                    # ...AND THE HEAP IS THIS HOUSE'S HEAP (settlement-review 2026-08-29, acceptance
                    # re-check). One pit on Kuwabata sat 53.7 ft from the farmhouse it serves and 45.4 ft
                    # from another; a reader attributes it to the nearer house and the manifest says
                    # otherwise. Ownership is a TIE-BREAK only, the same as the privy's and for the same
                    # reason: in a cluster the ground beyond one house's privy is often nearer the next.
                    #
                    # TWO STRONGER LEVERS WERE TRIED AND REVERTED, MEASURED ACROSS THE 13-MAP POOL.
                    # (1) A SECTOR SEARCH beyond the privy, the shape that worked for the privy itself
                    #     (radii 2-24 ft past its far edge, swung +/-54 deg): 5 misattributed of 68, against
                    #     4 of 66 with the eight offsets. It seats more heaps, none of them better placed.
                    # (2) Sorting by the ownership MARGIN rather than the flag, so that where no candidate
                    #     is unambiguous the LEAST misattributable wins: 4 of 67, no better - and it pulled
                    #     heaps back toward the house to win the margin, so "the heap lies beyond the privy"
                    #     - the actual researched rule (research/homesteads.md) - fell from 16 of 16 to
                    #     9 of 15. A reader-legibility nicety is not worth a researched rule.
                    # (3) The margin sort applied INSIDE the beyond-the-privy group only - the shape the
                    #     acceptance review named as the one both attempts stepped over, and it is a real
                    #     new mechanism: partitioning on the `out_ * _pout` term means every seat it can
                    #     promote is already beyond the privy, so it cannot break the rule that killed (2).
                    #     Implemented and rolled: 4 of 66 by centers, 6 of 66 by footprints, 14 of 14
                    #     beyond - IDENTICAL to the shipped state on all three. Reverted as complexity
                    #     that buys nothing; the lever is sound and it is the geometry that is fixed.
                    #
                    # THE FIGURE IS 6, NOT 4, AND A READER IS WHY (settlement-review 2026-08-29). The sort
                    # above compares distances to recorded house CENTERS, and a reader compares against the
                    # drawn RECTANGLE. Against footprints the pool carries SIX of 66, and the worst case is
                    # much worse than the point metric renders it: Kashikawa's heap at (2194.1, 2759.2) is
                    # 32.0 ft from its own farmhouse's wall and 8.4 ft from a neighbor's, which the center
                    # metric flatters to 46.7 against 33.0. The count that belongs next to a claim about
                    # what a reader attributes is the footprint one.
                    # What is left is the geometry itself: where a privy sits on the sun side and the
                    # neighbor is that way too, every seat beyond it belongs to that arc. Four heaps in the
                    # pool are nearer a neighbor's house than their own, and the interactive page resolves
                    # ownership on click. Do not re-try either lever without a new mechanism.
                    _oth = [(float(_h["x"]), float(_h["y"])) for _h in houses if (float(_h["x"]), float(_h["y"])) != (hx, hy)]
                    if _oth:
                        seats.sort(key=lambda _q, _hx=hx, _hy=hy, _ca=ca, _sa=sa, _o=_oth: nearer_own_house(_q, _hx, _hy, _ca, _sa, _o)[0])
                else:
                    seats = [(hw * 0.3, -(hh / 2 + g + d / 2), w, d), (hw / 2 + g + d / 2, hh * 0.3, d, w)]
            elif kind == "woodpile":
                # a stack stands against whichever wall is free, out of the way: both ends of the back wall
                # and a second row behind it, the kura's outer wall, either flank at two heights
                back = -(hh / 2 + g + d / 2)
                seats = [(-hw * 0.25, back, w, d), (hw * 0.25, back, w, d), (-hw * 0.25, back - d - g, w, d), (hw * 0.25, back - d - g, w, d)]
                if shed_side != "N":
                    seats.insert(1, (-(hw / 2 + hw * 0.32 + g + d / 2), hh * 0.1, d, w))  # against the kura's outer wall
                else:
                    seats.insert(0, (-(hw * 0.46 / 2 + g + d / 2), -hh * 0.6, d, w))  # beside the back kura
                seats += [(hw / 2 + g + d / 2, hh * 0.1, d, w), (-(hw / 2 + g + d / 2), hh * 0.1, d, w), (hw / 2 + g + d / 2, -hh * 0.3, d, w), (-(hw / 2 + g + d / 2), -hh * 0.3, d, w)]
            elif kind == "bath":
                seats = [
                    (-hw * 0.3, -(hh / 2 + g + d / 2), w, d),
                    (-(hw / 2 + g + d / 2), hh * 0.2, d, w),
                    (hw / 2 + g + d / 2, -hh * 0.3, d, w),
                    (-hw * 0.3, -(hh / 2 + g + d * 1.5 + g), w, d),
                    (hw * 0.3, -(hh / 2 + g + d * 1.5 + g), w, d),
                ]
            elif kind == "coop":
                # ...and the back seat is not DEAD CENTRE on the wall, which is the stamp itself: at
                # x = 0.0 exactly, a coop taking it stands at bearing 0 from its house on every farmstead
                # (houses draw at rot 0-4), so 9 of 12 Kashikawa coops sat within 4 degrees of north. A
                # hen coop stands somewhere along the back wall, not on its midpoint.
                _cjx = hw * 0.34 * (s._hjit(hx, hy, 105.9) - 0.5) * 2.0
                seats = [(hw / 2 + g + d / 2, hh * 0.3, d, w), (_cjx, -(hh / 2 + g + d / 2), w, d), (-(hw / 2 + g + d / 2), -hh * 0.3, d, w)]
                # A COOP IS NOT ALWAYS DUE NORTH (feature 152 T17). Measured on the shipped maps before
                # this: 9 of 12 Kashikawa coops and 7 of 12 Sawada's stood within 4 degrees of north of
                # their house, because the seat list is in the house's frame and houses draw at rot 0-4.
                # The arrangement is right - a coop goes in the rear yard - and the INVARIANCE is not.
                # The list is rotated by the homestead's own hash so which rear seat is tried first
                # differs between farmsteads while every seat stays one the record supports.
                if seats:
                    _sh = int(s._hjit(hx, hy, 105.5) * len(seats)) % len(seats)
                    seats = seats[_sh:] + seats[:_sh]
            else:  # shrine: a plot corner, world frame
                off = px(14.0)
                corner = {"NW": (-(hw / 2 + off), -(hh / 2 + off)), "NE": (hw / 2 + off, -(hh / 2 + off)), "SW": (-(hw / 2 + off), hh / 2 + off)}
                first = _roll(_SHRINE_CORNERS, u)
                seats = [(*corner[first], w, d)] + [(*corner[k], w, d) for k, _ in _SHRINE_CORNERS if k != first]
            for lx, ly, cw, ch in seats:
                cx, cy = hx + lx * ca - ly * sa, hy + lx * sa + ly * ca
                ext = abs(cw * ca) + abs(ch * sa), abs(cw * sa) + abs(ch * ca)  # the raked rect's bbox
                if _strip_blocked(s, cx, cy, ext[0], ext[1], hx, hy, fields, marsh, pond, lanes):
                    continue
                spin = 90.0 if (cw, ch) == (d, w) and w != d else 0.0  # a flank seat turns the glyph to lie ALONG the wall (review at T99: stacks stood end-on)
                s.farm_fixture(kind, cx, cy, rot=rot + spin, of=(hx, hy), form=("pit" if kind == "manure" and plan.manure_form == "pit" else None))  # the rolled manure form (feature 150)
                ring = [(cx - ext[0] / 2, cy - ext[1] / 2), (cx + ext[0] / 2, cy - ext[1] / 2), (cx + ext[0] / 2, cy + ext[1] / 2), (cx - ext[0] / 2, cy + ext[1] / 2)]
                s.placed.append((cx, cy, ext[0], ext[1]))
                s.block_polys.append(ring)
                if kind == "privy":
                    privy_at = (lx, ly)
                elif kind == "shrine":
                    shrines_left -= 1
                count += 1
                break
    return count


def _trunk_blocked(s: Settlement, cx: float, cy: float, t: float, fields: Sequence[Poly], marsh: Sequence[Poly], pond: Any, lanes: Sequence[tuple[Poly, float]]) -> bool:
    """Would a tree trunk (a t x t box) stand on a drawn footprint, a lane, a paddy, the marsh or the pond?"""
    if cx - t < 30 or cy - t < 30 or cx + t > s.W - 30 or cy + t > s.H - 30:
        return True
    for key in ("houses", "farm_sheds", "gardens", "threshing_yards", "byres", "wells", "kosatsuba", "farm_fixtures", "persimmons", "bamboo_stands"):
        for o in s.M.get(key, []):
            if "x" not in o:
                continue
            ow, oh = float(o.get("w", 2 * float(o.get("r", 8)))), float(o.get("h", 2 * float(o.get("r", 8))))
            if abs(cx - float(o["x"])) < (t + ow) / 2 + 2 and abs(cy - float(o["y"])) < (t + oh) / 2 + 2:
                return True
    corners = [(cx - t / 2, cy - t / 2), (cx + t / 2, cy - t / 2), (cx + t / 2, cy + t / 2), (cx - t / 2, cy + t / 2)]
    for poly in list(fields) + list(marsh):
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) or min(seg_dist(q[0], q[1], poly[k], poly[(k + 1) % len(poly)]) for k in range(len(poly))) < 6.0 for q in corners):
            return True
    for pts, half in lanes:
        if any(seg_dist(q[0], q[1], pts[k], pts[k + 1]) < half for q in corners for k in range(len(pts) - 1)):
            return True
    for o in s.M.get("dry_plots", []):
        poly = [(float(a), float(b)) for a, b in o.get("poly") or []]
        if len(poly) >= 3 and any(point_in_poly(q[0], q[1], poly) for q in corners):
            return True
    if any(s._on_watercourse(q[0], q[1], pad=4.0) for q in corners):
        return True
    return bool(pond) and ((cx - pond[0]) / (pond[2] + 20.0)) ** 2 + ((cy - pond[1]) / (pond[3] + 20.0)) ** 2 <= 1.0


def well_target(households: int) -> int:
    """How many communal draw-wells a hamlet of this size keeps.

    `wells_sized_to_population` wants 2-20 households per well at hamlet scale (the setting's
    deliberate prosperity liberty runs generous wells), so the band for 12 households is 1 to 6.
    One per ~6 households sits mid-band and matches what the authored hamlets draw - a couple of
    shared wells among the courtyards, not one per farm and not one for the whole place."""
    return max(1, min(6, round(households / 6.0)))


def place_wells(s: Settlement, plan: SitePlan, houses: Sequence[Mapping[str, Any]]) -> int:
    """Seat the communal wells INSIDE the house cloud, not on a box around it.

    The engine's `place_wells` sweeps a grid over a bbox, which is right for a town's street blocks
    and wrong for a loose farm cluster: the bbox corners are open ground, so a well lands past the
    outermost homestead and, being a hard crop feature with a 16 px extent, drags the map's frame
    out after it and leaves a band of empty scrub on that side
    (`crop_not_held_open_by_one_feature`). Insetting the bbox was tried first and is not the fix -
    it starves an elongated cluster of wells entirely, because the inset box no longer holds a grid
    cell (`settlement_has_wells`, seed 3).

    So the seats are derived from the HOUSES: a candidate must have several homesteads around it and
    none too far, which is what "among the dwellings" means, and the innermost candidates are tried
    first. `well_at` gives the engine's own verdict on each - it refuses a seat on a lane, a crop, a
    footprint or too near another well - so nothing here restates a placement rule."""
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    ccx, ccy = sum(xs) / len(xs), sum(ys) / len(ys)
    want = well_target(plan.spec.households)
    placed: list[Pt] = []
    # A WELLHEAD MAY NOT STAND IN THE SHELTER BELT (settlement-review, Inashiro 2026-08-18). The
    # belt is drawn later, but `village_grove` SKIPS any clump whose canopy would reach a wellhead
    # (`wells_clear_of_trees` - a well lost under the grove reads wrong), so a well seated inside
    # the belt's footprint silently deletes the clumps around it. Measured on Inashiro after the
    # tie-break change moved a well to (1098,1387), inside the belt's own footprint: the 40 ft band
    # at y1360-1400 went from 8 clumps to 1, and the belt acquired its first zero-canopy latitude in
    # a 930 ft run - a hole straight through the WINDWARD side, which is the entire point of a
    # windbreak. Nothing caught it: the belt's continuity is not gated, and the well checks are all
    # about the well.
    #
    # The belt is DERIVED from the houses, which already stand, so the prospective footprint can be
    # asked for now - the same expression `stage_woodland` will call, so the two cannot disagree.
    # This is a PREFERENCE and not a veto, per this function's standing rule that a settlement with
    # a badly-placed well beats one with no well: it sorts belt seats last, so one is taken only
    # when nothing outside the belt serves at all. It also happens to push wells toward the
    # dooryards, which is where the idiom 井戸端会議 puts them.
    from .hinterland import belt_polygon  # local: hinterland is a later stage, module-level would invert the pipeline's reading order

    _belt = belt_polygon(s, plan)

    def _in_belt(c: tuple[float, float, float]) -> int:
        return 1 if _belt and point_in_poly(c[1], c[2], _belt) else 0

    # THE MINIMAX SERVES THE HOUSES THAT NEED A WELL (known-open ledger 2026-08-16): the
    # worst-served objective used to count every house, including those
    # `settlement_dwellings_watered` already treats as watered by a nearby stream / channel /
    # pond (Kashikawa's SW pocket, 77-182 ft from the stream head - the GM-settled "no redundant
    # well beside a living stream" case), so the objective and the check read two definitions of
    # "needs a well". `surface_water_dist` is the check's own predicate; a house within its
    # reach of surface water drops out of the objective and out of the rescue pass below. If
    # EVERY house is surface-watered the objective falls back to all of them - wells are still
    # dug (well_target), they just stop chasing houses the water already serves.
    _sw_reach = 760.0 / max(plan.ftpx, 0.01)
    needy = [h for h in houses if surface_water_dist(s.M, h["x"], h["y"]) > _sw_reach] or list(houses)
    # A RELAXATION LADDER, not a single rule. The tight neighborhood test is right for a compact
    # cluster and impossible for a stretched one: an `elongated` cluster strung along a margin has
    # no point with three homesteads inside 190 px, so the strict pass found nothing at all and the
    # map shipped with no well (seeds 3 and 12). A settlement WITHOUT a well is a much worse map
    # than one whose well sits a little wide, so the test loosens until it finds seats. It never
    # loosens into "anywhere": every seat still has to be nearer a house than the crop.
    # Only the THIRD-nearest distance relaxes - the "is this in a neighborhood" test. The distance to
    # the NEAREST house stays tight, because `wells_among_dwellings` is a 95 px gap verdict against
    # the served building's edge: a well 220 px from its closest farmhouse is standing in the fields
    # by any measure, and relaxing that rung traded one failure for another.
    # The last rung also serves a PAIR. Every rung above asks for three homesteads around a seat,
    # which is the right shape for a nucleus and leaves a two-farm satellite with no well of its own
    # - and then the coverage pass cannot rescue it either, because the ground among two farms is
    # their own courtyards. Seed 18 stranded exactly that: a pair 500 px off the cluster, 760 and
    # 777 px from the nearest well, with all 118 legal-neighborhood probes around them refused.
    # Two households sharing a draw-well is an ordinary thing; three is not a threshold nature knows.
    for third, nearest, want_near in ((190.0, 105.0, 3), (300.0, 110.0, 3), (520.0, 112.0, 3), (520.0, 112.0, 2)):
        if len(placed) >= want:
            break
        seats: list[tuple[float, float, float]] = []
        step = 22.0
        # THE SWEEP BOX IS THE HOMESTEADS', NOT THE HOUSE CENTERS' (2026-08-15, cohort seed 44).
        # A bundle's courtyard ground extends ~a house-length past its house CENTER, so a cluster
        # strung along its field margin can keep every legal well pocket just OUTSIDE the centers'
        # bbox - seed 44 had 84 legal seats, nearly all north-west of min(xs)/min(ys), and the
        # unpadded grid visited none of them (0 of 1440 probes passed; the map shipped well-less).
        # The pad only restores ground the bundles themselves cover: every rung still demands
        # near[0] <= ~105 px, so an open-field corner of the padded box is rejected exactly as the
        # docstring above promises.
        pad = 120.0
        y = min(ys) - pad
        while y <= max(ys) + pad:
            x = min(xs) - pad
            while x <= max(xs) + pad:
                near = sorted(math.hypot(x - h["x"], y - h["y"]) for h in houses)
                if len(near) >= want_near and near[want_near - 1] <= third and near[0] <= nearest:
                    seats.append((math.hypot(x - ccx, y - ccy), x, y))
                x += step
            y += step
        # GREEDY COVERAGE, not central-first throughout (settlement-review, Mizuguchi/Sawada
        # 2026-08-15): sorting every well toward the centroid put both of Mizuguchi's wells in one
        # lobe of a two-lobed cluster - the six eastern households walked 248-424 ft while the west
        # had a well within 63. The FIRST well is central (innermost legal seat, as before); every
        # LATER well takes the legal seat FARTHEST from the wells already standing, ties toward the
        # center - i.e. it serves the households the placed wells do not, which is why a real hamlet
        # digs a second well at all.
        pool = sorted(seats, key=lambda c: (_in_belt(c), c[0]))  # the FIRST well is central too, but never in the belt if anywhere else will do
        while pool and len(placed) < want:
            if placed:
                # ...by MINIMAX NEED, in ~3-grid-step buckets, centrality breaking ties inside a
                # bucket. Two failed rankings led here, and both are worth remembering. Strict
                # farthest-first (the 2026-08-15 greedy-coverage fix) let a seat 91 px OUTSIDE the
                # cluster beat an interior seat covering the same households - the exterior well
                # held Sawada's whole frame open (crop_not_held_open_by_one_feature). Bucketing
                # that same farthest-first score fixed the frame and re-broke coverage the other
                # way: on Mizuguchi the spread rung walked EAST past the last house into scrub
                # while the one under-served household stood at the WEST end (settlement-review
                # 2026-08-16). Both fail because "far from the standing wells" is a proxy for the
                # real quantity, which is the walk of the household WORST served after the well is
                # dug - so score that directly: pick the seat minimizing the farthest any house
                # would remain from its nearest well. A seat past the row's end cannot beat an
                # in-row seat (it serves nobody the row seat does not), and a seat in an unserved
                # lobe wins outright, which is what the greedy fix was for in the first place.
                def _worst_after(c: tuple[float, float, float]) -> float:
                    return max(
                        min(
                            min(math.hypot(h["x"] - wx, h["y"] - wy) for wx, wy in placed),
                            math.hypot(h["x"] - c[1], h["y"] - c[2]),
                        )
                        for h in needy
                    )

                # AND AN INTERIOR SEAT BEATS A PADDED ONE THAT SERVES THE SAME HOUSEHOLDS. The sweep
                # box above is padded 120 px past the house CENTERS because a bundle's courtyard
                # really does reach that far, and without the pad seed 44 shipped well-less. But the
                # pad is symmetric, so it equally offers seats BEYOND the outermost homestead on
                # every side - and a wellhead is a hard crop feature with a 16 px extent, so one
                # seated out there drags the map's frame after it and leaves a band of empty scrub
                # (`crop_not_held_open_by_one_feature`). The RESCUE pass below already refuses
                # exactly that, with its `min(xs) <= x <= max(xs)` test and a comment giving this
                # very reason; the greedy pass did not - two passes carrying two definitions of
                # "inside the house cloud", with the looser one running first.
                #
                # MEASURED on cohort seed 41: the second well won its minimax bucket on the strength
                # of one north-east household, then seated 76 px NORTH of that household and 66 px
                # past every other feature on the map. The minimax objective is right and is not
                # what moved here - the tie-break was, because distance-to-centroid cannot express
                # "this seat is outside the settlement".
                #
                # SO IT IS A TIE-BREAK AHEAD OF CENTRALITY, NOT A FILTER. The padded ground stays in
                # the pool and still wins when nothing inside the cloud serves the same households,
                # which is what the pad was added for; it simply can no longer outrank an interior
                # seat that does. Same shape as every other rule in this function: relax rather than
                # forbid, because a settlement with a badly-placed well beats one with no well.
                # OUTSIDE WHAT, EXACTLY - the CROP's own box, not a box round the house CENTERS. The
                # first version of this tie-break tested `min(xs)..max(xs)`, an AABB of house centers,
                # and settlement-review (Inashiro 2026-08-17) named the flaw before it bit: an AABB
                # cannot tell "in the settlement" from "in the box", so on a two-lobed cluster the
                # ~345 px of grove and scrub BETWEEN the lobes scores as interior, exactly like a
                # courtyard. Cohort seed 29 then did bite - a well 64 px north of every other feature,
                # inside the centers' box and holding the whole frame open.
                #
                # `_crop_boxes` is what `crop_to_content` itself reads, so asking it is asking the
                # question the check will ask: a seat inside the box the crop will set cannot hold the
                # frame open, whatever its relation to the house centers. Same-source doctrine, and it
                # picks up the houses' DRAWN extents plus their yards, gardens, sheds and byres rather
                # than a point per house. (The box can only GROW later - the woodland and the pond are
                # placed after - so this is conservative in the safe direction.)
                _cb = s._crop_boxes(city=False)
                _bx0 = min((b[0] for b in _cb), default=min(xs))
                _bx1 = max((b[1] for b in _cb), default=max(xs))
                _by0 = min((b[2] for b in _cb), default=min(ys))
                _by1 = max((b[3] for b in _cb), default=max(ys))

                # A TIE-BREAK CANNOT REACH A SEAT WITH NO RIVAL IN ITS BUCKET, so the FRAME goes into
                # the score itself. Ranking outside-ness ahead of centrality fixed cohort seed 29 and
                # left seed 7 failing for the reason a tie-break always leaves one: its pad seat was
                # alone in its minimax bucket, so there was nothing to break the tie against. Seed 7's
                # well sits 25 px past the northernmost byre and holds the whole frame open
                # (`crop_not_held_open_by_one_feature`), because a wellhead is a hard crop feature with
                # a 16 px extent and the crop follows it out.
                #
                # THE EXCHANGE RATE IS 1:1 IN PIXELS, which is what makes this a rule rather than a
                # knob: a seat that drags the frame out by N px must save at least N px of the
                # worst-served household's walk to be worth it. Both quantities are distances in the
                # same units, so no weighting has to be invented - and the well that genuinely serves
                # an outlying lobe still wins, because the coverage it buys is real.
                def _extent_added(c: tuple[float, float, float], bx0: float = _bx0, bx1: float = _bx1, by0: float = _by0, by1: float = _by1) -> float:
                    """How far past the crop's predicted box this seat (drawn radius included) reaches."""
                    return max(0.0, bx0 - (c[1] - _WELL_DRAWN_R), (c[1] + _WELL_DRAWN_R) - bx1, by0 - (c[2] - _WELL_DRAWN_R), (c[2] + _WELL_DRAWN_R) - by1)

                # ...AND THE LAST TIE-BREAK IS THE NEIGHBORHOOD, NOT THE CENTROID (settlement-review,
                # Sawada 2026-08-18). Once the minimax bucket and the frame term are equal, the
                # remaining sort was `c[0]` - the seat's distance to the cluster CENTROID, computed
                # when the pool was built. On a ONE-lobed cluster that reads as "the most central
                # seat wins" and is fine. On a TWO-lobed one the centroid is the empty ground
                # BETWEEN the lobes, so the tie-break actively prefers the gap: Sawada's second well
                # moved off a seat serving 11 households within 300 ft onto one serving 5, and the
                # worst walk went 364 -> 493 ft. Same family as the `_extent_added` fix above and as
                # the standing rule against letting an aggregate stand in for the distributed thing
                # a verdict is about - a centroid is not a place anybody lives.
                #
                # The measure that IS the question: how tightly is this seat surrounded by
                # homesteads - the distance to the `want_near`-th nearest house, which is exactly
                # the rung's own "is this in a neighborhood" test, reused rather than restated.
                # Distance to the SINGLE nearest house was the ledger's sketch and is rejected: it
                # is minimized by hugging one outlying farmhouse, which is the same mistake in the
                # other direction. Every seat in the pool already passed the rung, so this only
                # orders seats that are all legally "among the dwellings".
                def _neighborhood(c: tuple[float, float, float], wn: int = want_near) -> float:
                    return sorted(math.hypot(c[1] - h["x"], c[2] - h["y"]) for h in houses)[wn - 1]

                # THE BELT TERM SITS BEHIND COVERAGE, not in front of it. Ranked first it is a
                # filter, and it behaved like every other filter this function has tried: Mizuguchi's
                # second well moved off a seat inside the belt and its worst walk went 203 -> 264 ft,
                # on a map whose belt hole turned out not to be well-caused at all, so the trade
                # bought nothing. Behind the minimax bucket it can only decide between seats that
                # serve the households equally well - which is all "do not stand in the windbreak"
                # was ever entitled to decide.
                pool.sort(key=lambda c: ((_worst_after(c) + _extent_added(c)) // 66.0, _in_belt(c), _extent_added(c), _worst_after(c), _neighborhood(c)))
            _, x, y = pool.pop(0)
            if any(math.hypot(x - px, y - py) < 170.0 for px, py in placed):
                continue  # `wells_not_clustered`: shared wells serve separate courtyards
            if s.well_at(x, y):
                placed.append((x, y))
    # ...then a COVERAGE pass. `settlement_dwellings_watered` gives every dwelling ~760 real feet to
    # the nearest well, channel, pond or stream - generous, and still not automatic once a cluster is
    # sized from the real bundle pitch and runs 700+ px along its margin: a single well at one end
    # leaves the far end dry. So any house still out of reach gets a well sought beside it.
    reach = 760.0 / max(plan.ftpx, 0.01)
    for h in houses:
        if any(math.hypot(h["x"] - px, h["y"] - py) <= reach for px, py in placed):
            continue
        if surface_water_dist(s.M, h["x"], h["y"]) <= reach:
            continue  # watered by a stream/channel/pond - the check's own verdict; no rescue well
        # A RING PROBE, spiraling out from the house, asking `well_at` directly.
        #
        # AND EVERY CANDIDATE MUST STILL STAND AMONG THE DWELLINGS - near SOME house, not necessarily
        # the one being rescued. `wells_among_dwellings` is a 95 px edge-gap verdict against the
        # served building, and this probe used to take the first seat `well_at` allowed at any radius
        # out to 340. That was harmless while nothing reached this branch, and stopped being harmless
        # the moment the sun corridor (2026-08-13) spread a cluster enough to strand a household:
        # seed 18 seated a well 161 px from its nearest dwelling. Capping the RADIUS was the obvious
        # fix and the wrong one - it just traded the failure for `settlement_dwellings_watered`,
        # leaving the household dry. The honest constraint is the one the check states: a well may
        # be dug well away from the farm it rescues, as long as it is in somebody's courtyard.
        #
        # `open_seat` was tried here first and is the wrong tool: it optimizes a seat over a
        # RECTANGLE - furthest from what it is told to clear, ties toward the center - and it
        # returned None at every radius from 60 to 430 px around a stranded farmstead that had a
        # perfectly legal spot 40 px to its east. What this needs is not the best seat in a region
        # but ANY seat near THIS house, so it asks the question that way round, and it asks it of
        # `well_at`, which is the call that actually places a well.
        spot = None  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
        for radius in range(40, 340, 20):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
            for bearing in range(0, 360, 20):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                cand = (
                    h["x"] + math.cos(math.radians(bearing)) * radius,
                    h["y"] + math.sin(math.radians(bearing)) * radius,
                )  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                if not (
                    min(xs) <= cand[0] <= max(xs) and min(ys) <= cand[1] <= max(ys)
                ):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # a rescue well still sits INSIDE the house cloud. A wellhead is a hard crop  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # feature with a 16 px extent, so one seated past the outermost homestead drags  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # the frame out after it (`crop_not_held_open_by_one_feature`) - the same reason  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    # the grid above is laid over the cloud rather than a box grown around it.  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    continue  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                if not any(math.hypot(cand[0] - hh2["x"], cand[1] - hh2["y"]) <= 95.0 for hh2 in houses):  # pragma: no cover - the rescue's among-the-dwellings floor
                    continue  # pragma: no cover - center distance <= 95 is strictly inside the check's 95 px EDGE gap
                if any(
                    math.hypot(cand[0] - px, cand[1] - py) < 110.0 for px, py in placed
                ):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    continue  # `wells_not_clustered`: shared wells serve separate courtyards  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                if s.well_at(cand[0], cand[1]):  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    spot = cand  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                    break  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
            if spot is not None:  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                placed.append(spot)  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
                break  # pragma: no cover - the well ring-probe rescue; the bundle-pitch fix left the courtyards open enough that no cohort map strands a household
    if not placed:
        # LAST RESORT: ask the engine. A settlement with NO well fails the gate outright, and by
        # this point the lattice has been refused everywhere - which means the courtyards are full,
        # not that there is no room. `open_seat` runs the engine's own `_fits` over the ground and
        # returns the best clear spot or None, which is the documented answer to "this pocket needs
        # one more X" and finds seats a hand-rolled scan misses (the skill's dev notes: a manifest
        # scan cannot predict `_fits`).
        spot = s.open_seat(
            (min(xs), min(ys), max(xs), max(ys)), 16.0, 16.0, well=True
        )  # pragma: no cover - reached only when the lattice above found NOTHING, which the bundle-pitch fix made rare; a settlement with no well fails the gate outright, so the branch stays
        if spot is not None and s.well_at(spot[0], spot[1]):  # pragma: no cover - the last-resort seat; unreached since the bundle-pitch fix left the courtyards open
            placed.append(spot)
    return len(placed)
