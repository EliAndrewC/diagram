"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
import random

from l7r.diagram.settlement import Settlement

from ..consts import BUNDLE_PITCH, CLUSTER_DRAWN_ASPECT, SUN_CORRIDOR_FT, WEST_SUN_FT, Pt
from ..plan import SitePlan
from .seats import _seat_allowed, cluster_aspect, front_row, lane_frontage
from .wells import place_wells

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
