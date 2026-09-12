"""Split from hamletgen/homesteads.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
import random

from l7r.diagram.settlement import Settlement

from ..consts import BUNDLE_PITCH, CLUSTER_DRAWN_ASPECT, MIN_WEB_GAP, SUN_CORRIDOR_FT, WEB_FABRIC_GAP, WEST_SUN_FT, Pt
from ..plan import SitePlan
from .boundary import install_site_boundary
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
    """The farmhouses.

    Every household is seated here, and at this moment there is NOT ONE LANE ANYWHERE ON THE MAP: the houses
    answer to the field, the water and each other, and nothing else has taken ground before them. Every way on the
    finished map - the connector, the field spur, the cluster's spine and the alleys - is laid after this plate and
    positioned from where these houses actually landed.

    The ground is asked ONCE. Before the first seat, the site boundary is computed from everything the map holds:
    the paddy's outline as a few facing chords, everything else - the hem, the marshes, the ponds, the reed toe that
    will be drawn later, the no-build ground - as one outline with holes, and the water courses and registered
    corridors as segments. A candidate rectangle is judged at nine points against those and nothing else.

    The seats are proposed where a house can stand. The FRONT ROW walks the paddy's chords at the bundle pitch, each
    seat at a computed standoff - the wall rule's distance plus the reach of the homestead's core (the house, its
    yard, its kura) toward that chord - pushed once further where the boundary's outline lies beyond the chord (a
    dike's bank), and takes about the square root of (households times the rolled shape's aspect) houses, so a
    crescent fronts the field with more of its houses than a round cluster does. The RANKS BEHIND are proposed behind
    every standing house, one homestead's depth further from the field (and the yard's sun corridor where the ranks
    climb north), in a brick pattern; only when a round seats nothing behind does the cluster grow along the field,
    by the seats a pitch beyond each end of the rank. Only while the quota is still short after four rounds do the RESCUE rounds run: the old random cloud
    over a wider band, seeded a third of a pitch apart, spending guesses on purpose. A re-roll after a stranded
    farmhouse draws a different cloud.

    Each seat is one placer call, and a call tests one rectangle first: the box around the homestead's
    configurations, against the boundary and the placed boxes; where that is refused, each configuration's own box
    in turn, with at most one computed move away from a single overlapping neighbor. The parts - the garden's side,
    its beds, the kura - are laid inside a box the ground admitted, and the rules that read the parts (the wall rule,
    the eave gap, the sun corridors) are asked once. No spiral of offsets, no sliding: a seat that does not fit is
    refused and the next seat is offered. `meta.seat_search` counts every guess - candidates, placer calls,
    rectangles, part layouts, the front row's share and the rounds - so the search is measured, never assumed.

    `households_consistent` wants the occupied farmhouses within 0.85-1.05x the declared households - a to-scale map
    depicts essentially every household (research/settlements.html "Is every household in a hamlet actually drawn?") -
    so a hamlet that declares 15 and seats 12 fails, and the stage records
    the shortfall on the roll rather than re-rolling the whole map to fix a local one.

    Steps:
        l7r.diagram.hamletgen.homesteads.boundary.install_site_boundary
        l7r.diagram.hamletgen.homesteads.boundary.site_boundary
        l7r.diagram.hamletgen.homesteads.seats.front_row
        l7r.diagram.hamletgen.homesteads.seats._front_row_from_chains
        l7r.diagram.hamletgen.homesteads.seats.lane_frontage
        l7r.diagram.hamletgen.homesteads.seats._seat_allowed
        l7r.diagram.settlement.Settlement.try_place
        l7r.diagram.settlement.Settlement._place_bundle_nucleated
        l7r.diagram.settlement.Settlement._bundle_envelope
        l7r.diagram.settlement.Settlement._envelope_blocked
        l7r.diagram.settlement.Settlement._parts_fit
        l7r.diagram.settlement.Settlement.cluster_seeds
        l7r.diagram.settlement.Settlement.farmsteads
    """
    # A YARD KEEPS ITS SUN (GM 2026-08-13; researched in research/homesteads.html, "The threshing
    # yard's sun"). 39 ft is the 9-to-3 drying window at 38N in the 10th month for a minka's ~20 ft
    # ridge; the noon figure is 21. The engine's rule is opt-in and this is where the scripted tier
    # opts in - the hand-authored maps keep their packing until they are converted.
    s.sun_corridor(SUN_CORRIDOR_FT)
    # ...AND THE SAME CORRIDOR NOW COVERS THE GARDEN BEDS (feature 133 T10), inside `sun_corridor`.
    # The belt's afternoon lane is opted into HERE too, though it is only read at `stage_windbreak`:
    # the two sun rules are one decision, made at the same place, for the same reason.
    s.west_sun_lane(WEST_SUN_FT)
    seat = plan.seat
    # THE SITE BOUNDARY FIRST (feature 226): one outline separating the buildable ground from everything the map holds,
    # computed once; the fit test reads it instead of its five ground scans, and the seats below are proposed from it.
    install_site_boundary(s, plan)
    s._seat_search = {"candidates": 0, "placer_calls": 0, "positions": 0, "rects": 0, "rounds": 0}  # rounds: lattice rounds run (0 when the front row seated everything; over 4 = the rescue ran)
    _house_max = (s.px(46) * 1.35, s.px(28) * 1.10)  # the LARGEST house `_try_place_bundle` rolls: the front row's computed standoff clears it

    def _pretest(x: float, y: float) -> bool:
        """Count a candidate (feature 226 FR-003). The cheap refusal that stood here - a house-sized box against the
        boundary and the placed boxes - is the placer's own first test now (feature 227: the whole homestead's
        ENVELOPE, `_envelope_blocked`), so nothing is asked twice and a seat the envelope refuses costs one rectangle."""
        s._seat_search["candidates"] += 1
        return True

    ax, ay = seat["along"]
    ox, oy = seat["out"]
    # A RE-ROLL DRAWS A DIFFERENT LATTICE (feature 226, cohort seeds 11 and 25). `generate` re-rolls a map that stranded a
    # farmhouse with that ground forbidden, and under the old random cloud the retry explored new pockets by itself; the
    # lattice keeps the FIRST survivors of the same draw, so a retry that forbade one seat kept every other, and the
    # stranded house came back a pitch away. The draw is salted by how many seats are forbidden - the first roll is
    # unchanged, and each retry lays the lattice at a new phase.
    rng = random.Random((plan.spec.seed * 2654435761 + 7919 * len(getattr(s, "_avoid_seats", None) or ())) & 0xFFFFFFFF)
    placed = 0
    lat, dep = seat["lat"], seat["dep"]

    # THE FRONT ROW GOES DOWN FIRST, along the band's field-facing face. A cluster seeded only by
    # its SHAPE fills its whole depth evenly, and on a small hamlet that can leave the field ringed
    # by four houses where `field_ringed` (retired, feature 141) wants five - the map then reads as a settlement that
    # happens to be near a paddy rather than one that works it. Seating a row against the margin
    # first is also just what a farming hamlet looks like: the houses front the field they farm, and
    # the back rows fill in behind them.
    # (no quota guard here: the row is capped at 8 seats and the tier's floor is 10 households, so
    # the front row alone can never meet the ask)
    # TWO passes at two standoffs. `field_ringed` (retired, feature 141) wants five farmhouses within 165 px of the field
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

    # THREE standoffs, not two. `field_ringed` (retired, feature 141) wants five farmhouses within 165 px of the field
    # outline and the placer refuses any bundle that laps a bund or a ditch, so a single ring of
    # candidates can land four on awkward ground. Each extra pass is free when the earlier one
    # filled the row.
    # The FRONT ROW is allowed a little further out than the rest - a house hugging the field is
    # part of the settlement wherever the band's nominal circle happens to fall, and `field_ringed` (retired, feature 141)
    # wants five of them within 165 px of the outline.
    # Standoffs run out to 150 px, which is still inside `field_ringed` (retired, feature 141)'s 165 px band. The near
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
    # `field_ringed` (retired, feature 141) (five farmhouses within 165 px of a big field's outline) can always be met by
    # the row alone - the defect this row exists to prevent.
    # THE ROW'S SHARE FOLLOWS THE ROLLED SHAPE (feature 227): under the envelope-first placer the row fills every seat it
    # is offered, and "one rank's worth of the band" (2 * lat / pitch) is the whole quota on a long margin - Inashiro
    # strung all 15 along the paddy at a drawn aspect of 5.07 against a rolled crescent's 1.9-4.2. A cluster of N
    # houses drawn at aspect A is about sqrt(N * A) houses long, so that many front the field and the lattice seats the
    # rest behind them, and the shape knob binds where the band alone could not. The middle of the shape's band is
    # the aspect aimed at; the floor of 6 keeps `field_ringed` (retired, feature 141) reachable by the row alone, as before.
    _lo_a, _hi_a = CLUSTER_DRAWN_ASPECT.get(plan.cluster_shape or "crescent", (1.9, 4.2))
    # ...times two, MEASURED: the ranks stand an envelope's depth apart (about 1.2 pitches) along an ARC, and the drawn
    # aspect is read on the house centers' own axis, so a block of L by N/L houses reads about half of L*L/N - seven
    # in Inashiro's row drew 1.66 on a rolled crescent (1.9-4.2), six in Kuwabata's 1.71 on a round (1.0-2.0).
    front_cap = min(plan.spec.households, max(6, round(math.sqrt(plan.spec.households * (_lo_a + _hi_a)))))

    # ...AND A FRONT-ROW SEAT MUST ALSO BE REACHABLE FROM A TRACK, not merely near the paddy
    # (settlement-review, Inashiro 2026-08-17 - the same review round as the rank cap above, which
    # is the OTHER half of this defect: that one bounds HOW MANY seats the row takes, this one bounds
    # WHICH). The row runs FIRST and follows the field OUTLINE, which on a long fan strings it
    # hundreds of px past wherever the rolled lane skeleton lies - so the row won every seat and the
    # frontage pass below got the leftovers. Measured on Inashiro: house-to-lane median 109 ft, five
    # houses past 150, a whole seven-farmstead lobe fronting nothing, and a 252 ft lane spur with no
    # house within 96 ft anywhere. That is the defect the frontage pass's own comment below records
    # curing ("a median house-to-lane distance of 94 ft ... with one lane dead-ending in open
    # ground"), returned by a different route - and no gate check can see it, because `field_ringed` (retired, feature 141)
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
    # ONE RUNG, COMPUTED (feature 227 FR-002), where a ladder of eight standoffs (46 to 150 px) stood: the seat is where
    # the homestead stands - the wall rule, the tilt's slack, and the whole homestead's reach toward the chord (the
    # union envelope at the largest house the roll can take: a paddy the yard faces gets the yard's depth, a paddy the
    # kura faces the kura's). The ladder's other rungs were a second rank built ten to twenty pixels at a time behind
    # the first, which under the envelope-first placer (no spiral to slide the seats apart) was two hundred refused
    # candidates per map and a cluster strung along the paddy whatever shape it rolled; a rung of one house depth
    # seated NOBODY on Kuwabata's dike heads (the yard faces the paddy there) and the cluster drifted 112 px off its
    # field. The ranks behind the front row are proposed behind the standing houses, below.
    def _ground_push(s_: Settlement, seat_: Pt, n_: Pt, house_: tuple[float, float]) -> Pt:
        """The seat moved once along `n_` by the outline's reach past the homestead's near edge - zero when the box is clear."""
        _bx = s_._bundle_envelope(seat_[0], seat_[1], house_[0], house_[1], shed=True)
        _pts = [(_bx[0] + dx * _bx[2] / 2, _bx[1] + dy * _bx[3] / 2) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        if s_._site_corridors is None or not s_._site_corridors.hit_points(_pts):
            return seat_
        lx, ly = -n_[1], n_[0]  # the lateral axis
        half_lat = abs(lx) * _bx[2] / 2 + abs(ly) * _bx[3] / 2
        near = _bx[0] * n_[0] + _bx[1] * n_[1] - (abs(n_[0]) * _bx[2] / 2 + abs(n_[1]) * _bx[3] / 2)  # the box's near edge along n
        far = near + (abs(n_[0]) * _bx[2] + abs(n_[1]) * _bx[3])
        push = 0.0
        for ring in s_._site_corridors.ring_pts:
            for x, y in ring:
                if abs((x - _bx[0]) * lx + (y - _bx[1]) * ly) <= half_lat:
                    d = x * n_[0] + y * n_[1]
                    if near <= d <= far:
                        push = max(push, d - near)
        if push <= 0.0:
            return seat_
        # ...cleared by a FOOTPATH's room, not a hair: a homestead pushed to two pixels off a dike's bank left no way a
        # lane could pass between them, the web stranded it, and the re-roll then forbade the only front seats the
        # dike heads offer (Kuwabata: front 0 on the kept roll, the cluster 162 px off its polder)
        push += WEB_FABRIC_GAP * 2.0 + 6.0
        return (seat_[0] + n_[0] * push, seat_[1] + n_[1] * push)

    # the homestead's CORE - the house, the yard south of it, the kura north - is what always faces the paddy the same
    # way; the garden's side is chosen later by the sun, so it is not in the reach (counted, it stood every front house
    # off a paddy beside it by a garden's width, 81 px on Inashiro against the 60 the cluster is held to)
    _g0 = s._bundle_geom(0.0, 0.0, _house_max[0], _house_max[1], "E", shed=True)
    _core = s._bbox_of([r for r in (_g0["house"], _g0["yard"], _g0.get("shed")) if r is not None])
    _reach = (_core[0] - _core[2] / 2, _core[1] - _core[3] / 2, _core[0] + _core[2] / 2, _core[1] + _core[3] / 2)  # (left, top, right, bottom) about the house center
    for _rung in (0,):
        for (fx, fy), _n in front_row(plan, min(plan.spec.households, 12), standoff=None, chains=s._site_chains, house=_house_max, envelope=_reach, with_normals=True):
            if placed >= front_cap:
                break
            # THE ONE COMPUTED MOVE AGAINST THE GROUND (feature 227 FR-002, the GM's "measuring the distance ... and then
            # moving however much the correct amount is", applied to the outline): the chord is the crop's edge, but the
            # buildable line is the outline's - the dike's bank, a pond's fringe - which can lie tens of pixels beyond
            # it (Kuwabata's dike heads: every front seat refused, the cluster 112 px off its polder). Where the seat's
            # box is inside the outline, it is pushed once along the chord's normal by the outline's measured reach
            # past the box's near edge, and offered there.
            fx, fy = _ground_push(s, (fx, fy), _n, _house_max)
            # NO LANE TEST HERE ANY MORE (feature 126). This used to read
            # `_row_seats < _FIELD_RING_FLOOR or _lane_dist(...) <= _FRONT_ROW_LANE_CAP`, which
            # judged a front-row seat by how near it fell to a drawn lane. The internal lanes are
            # now laid AFTER this stage, so at this moment the only ways on the map are the
            # connector and the field spur - and the cap was therefore demoting good seats for
            # being far from a track that has nothing to do with them. Worse, it made the
            # settlement's shape depend on a way that has not been decided yet, which is the exact
            # inversion this feature exists to remove: a farmhouse is sited by the FIELD it works
            # and the ground it can stand on, and the lane is worn afterwards between the houses.
            if math.hypot(fx - seat["cx"], fy - seat["cy"]) <= bound * 1.3 and _seat_allowed(s, fx, fy) and _pretest(fx, fy) and s.try_place(fx, fy, "plain"):
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
            if in_band((lx, ly)) and _seat_allowed(s, lx, ly) and _pretest(lx, ly) and s.try_place(lx, ly, "plain"):
                placed += 1
    _cloud_placed = 0
    s._seat_search["front"] = placed  # the households the front row seated (R2 reads it beside the cap)
    _row: list[Pt] = [(h["x"], h["y"]) for h in s.M.get("houses", [])]  # the front row as it stands: the lattice's rank 0
    # THE RANKS BEHIND THE FRONT ROW ARE PROPOSED BEHIND THE STANDING HOUSES (feature 227 FR-002/D8). The random cloud
    # deduped to a lattice (feature 226) relied on the placer's spiral to slide its seeds into a fit; the envelope-first
    # placer takes the seat it is given or makes one computed move, so the seats have to be RIGHT: each round offers,
    # behind every house of the rank before it, the seat one envelope's depth further from the field along the band's
    # outward vector, and the staggered seat behind the midpoint of each neighboring pair (a brick pattern). A house
    # seated there fits by construction unless the ground refuses it or the band ends. Measured before this: Kuwabata
    # 14 of 16 and Inashiro strung along the paddy at 5.1 (rolled crescent, 1.9-4.2) on the deduped cloud.
    # The rescue (rounds five to seven) keeps the old cloud over a wider band, seeded a third of a pitch apart.
    _env = s._bundle_envelope(seat["cx"], seat["cy"], _house_max[0], _house_max[1], shed=True)
    # one envelope's depth along the outward vector, plus THE ROOM A LANE NEEDS BETWEEN THE RANKS (`MIN_WEB_GAP`,
    # both neighbors' clearance and the tread between them) - four pixels was the first figure and it left the pool's
    # ranks abutting at a median 4 px, which no alley can thread: the web then could not reach the interior and
    # cohort seed 39 stranded a farmhouse the re-roll could not save. A rank is separated from the rank in front by
    # the lane that serves it. And, where the ranks climb NORTH away from the
    # field, the sun corridor a yard owes to its south (`SUN_CORRIDOR_FT`): the rank in front stands exactly there,
    # and at the bare depth every seat behind it was clear of the ground and refused by the parts' rules (cohort
    # seed 8, the paddy to the south: the "clear" seats of every rank round failed, 9 of 11 seated)
    _rank_step = abs(ox) * _env[2] + abs(oy) * _env[3] + s.px(MIN_WEB_GAP) + max(0.0, -oy) * s.px(SUN_CORRIDOR_FT)
    for attempt in range(7):
        if placed >= plan.spec.households:
            break
        s._seat_search["rounds"] = attempt + 1  # the rounds this roll needed (over 4 = the rescue ran); R2 reads it per map
        wlat, wdep = lat * (1.0 + 0.22 * attempt), dep * (1.0 + 0.16 * attempt)
        _kept: list[Pt] = []
        _standing: list[Pt] = [(h["x"], h["y"]) for h in s.M.get("houses", [])]
        if attempt < 4 and _standing:
            # A LATTICE MEASURED FROM THE ROW, NOT A STEP BEHIND WHOEVER STANDS IN FRONT (settlement-review, feature
            # 227). Offering each seat one step behind a STANDING house compounds: rank 2 is measured from rank 1,
            # which was measured from the row, and every refusal along the way shifts what follows it, so the cluster's
            # centroid walks away from the field round by round and the ranks stop being ranks. Kuwabata's cluster
            # ended 114 px off its polder and Sawada's resolved into eight pieces. The lateral positions still come
            # from the houses that stand - the cluster is as wide as it is - but the DEPTH of round k is the row's own
            # depth plus k steps, measured once from the seat, so a rank is where a rank should be and four rounds
            # reach exactly four steps back. A brick: the even rounds offer the midpoints between neighbors, the odd
            # rounds the seats straight behind.
            _a_of = lambda q: (q[0] - seat["cx"]) * ax + (q[1] - seat["cy"]) * ay  # noqa: E731 - the band's two coordinates, used here only
            _o_of = lambda q: (q[0] - seat["cx"]) * ox + (q[1] - seat["cy"]) * oy  # noqa: E731
            _along = sorted(_standing, key=_a_of)
            _row_out = min(_o_of(q) for q in (_row or _standing))  # the front row's own depth: `out` runs away from the field
            _depth = _row_out + _rank_step * (attempt + 1)

            def _seat_at(u: float, _d: float = _depth) -> Pt:
                return (seat["cx"] + ax * u + ox * _d, seat["cy"] + ay * u + oy * _d)

            _us = [_a_of(q) for q in _along]
            _ends = [(_along[0][0] - ax * BUNDLE_PITCH, _along[0][1] - ay * BUNDLE_PITCH), (_along[-1][0] + ax * BUNDLE_PITCH, _along[-1][1] + ay * BUNDLE_PITCH)]
            if attempt % 2 == 0:
                _cands = [_seat_at((p + q) / 2) for p, q in zip(_us, _us[1:], strict=False)]
                # the brick's outer half-seats grow the rank along the field by half a pitch each: with the full-pitch
                # ends, offered only when the back is refused (Mizuguchi's round strung to 4.5 with them in every round)
                _ends += [_seat_at(_us[0] - BUNDLE_PITCH / 2), _seat_at(_us[-1] + BUNDLE_PITCH / 2)]
            else:
                _cands = [_seat_at(u) for u in _us]
            _cands.sort(key=lambda q: math.hypot(q[0] - seat["cx"], q[1] - seat["cy"]))  # center-out, as every proposer here
            # FILL BEFORE YOU GROW (settlement-review, feature 227): a seat the front row could not take leaves a HOLE
            # in the row, and the ranks - proposed behind the houses that did stand - carry the hole backward through
            # the whole cluster. Inashiro shipped a 211 px gap in its row and read as three pieces (components
            # [10, 4, 1] at a 165 px link) on a map whose form is nucleated. So the first rank round offers the
            # midpoints of the row's own over-wide gaps AT THE ROW'S OWN DEPTH, ahead of anything behind it.
            if attempt == 0:
                _cands = [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) for p, q in zip(_along, _along[1:], strict=False) if math.dist(p, q) > BUNDLE_PITCH * 1.45] + _cands
        else:
            # THE RESCUE offers the along-the-field seats first - a pitch beyond each end of the standing rank, and the
            # brick's outer half-seats behind it - then the old cloud over the widened band; a quota the ranks could not
            # seat (cohort seed 25: 19 of 20 once the ends left the ordinary rounds) is seated where the ground is
            _ends = []
            _cands = []
            if _standing:
                _along = sorted(_standing, key=lambda q: (q[0] - seat["cx"]) * ax + (q[1] - seat["cy"]) * ay)
                _cands = [(_along[0][0] - ax * BUNDLE_PITCH, _along[0][1] - ay * BUNDLE_PITCH), (_along[-1][0] + ax * BUNDLE_PITCH, _along[-1][1] + ay * BUNDLE_PITCH)]
                _cands += [
                    (_along[0][0] - ax * BUNDLE_PITCH / 2 + ox * _rank_step, _along[0][1] - ay * BUNDLE_PITCH / 2 + oy * _rank_step),
                    (_along[-1][0] + ax * BUNDLE_PITCH / 2 + ox * _rank_step, _along[-1][1] + ay * BUNDLE_PITCH / 2 + oy * _rank_step),
                ]
            want = plan.spec.households * 6 + 30
            for lx, ly in s.cluster_seeds(plan.cluster_shape, 0.0, 0.0, wlat, wdep, want, rng, record=False):
                ly = -wdep + (ly + wdep) * 0.75  # the cloud leans toward the field (feature 133)
                _cands.append((seat["cx"] + ax * lx + ox * ly, seat["cy"] + ay * lx + oy * ly))
        _before_round = placed
        # THE ENDS GO THROUGH THE SAME BODY (feature 227): they are offered only after a round that seated nothing
        # behind - the cluster grows along the field only when its back is refused - but a second loop of its own
        # meant a second copy of the dedupe and the jitter, which is how two rules drift apart.
        _offered, _along_the_field = _cands, False
        while True:
            for _sx4, _sy4 in _offered:
                if placed >= plan.spec.households:
                    break
                # A PITCH IS A SPACING, NOT A RULING (settlement-review, feature 227: 11 of Mizuguchi's 12 houses fell in
                # one 10 px bucket of nearest-neighbor distance, where the hand-packed maps spread over three). The seat is
                # nudged along the band by up to a tenth of a pitch, from the map's own position hash - enough to break the
                # modal spike, far too little to move a rank or to reopen a gap the round above just filled.
                _jit = (s._hjit(_sx4, _sy4, 13.0) - 0.5) * BUNDLE_PITCH * 0.2
                _sx4, _sy4 = _sx4 + ax * _jit, _sy4 + ay * _jit
                if not in_band((_sx4, _sy4)) and attempt >= 4:
                    continue
                if any(math.hypot(_sx4 - kx, _sy4 - ky) < BUNDLE_PITCH * (0.5 if attempt < 4 else 0.3) for kx, ky in _kept) or any(
                    math.hypot(_sx4 - h["x"], _sy4 - h["y"]) < BUNDLE_PITCH * 0.5 for h in s.M.get("houses", [])
                ):
                    continue  # the same guess again
                _kept.append((_sx4, _sy4))
                if _seat_allowed(s, _sx4, _sy4) and _pretest(_sx4, _sy4) and s.try_place(_sx4, _sy4, "plain"):
                    placed += 1
                    _cloud_placed += 1
            if _along_the_field or not (attempt < 4 and _standing and placed == _before_round and placed < plan.spec.households):
                break
            _offered, _along_the_field = _ends, True

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
    s.M["meta"]["seat_search"] = dict(s._seat_search)  # the guesses counted (feature 226 FR-003): candidates, placer calls, positions, rectangles
    s._site_chains = None  # the boundary is the homestead stage's; every later placer runs the fit test's own path
    s._site_corridors = None
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
    """Yards, gardens, byres, wells, sheds.

    The rest of each steading, plus the shared fixtures. Kept as its own stage after the houses because several
    of them are sited RELATIVE to a house that must already exist - a threshing yard south of its own farmhouse,
    a byre off the frontage, a well between steadings.

    Communal wells and shared draft byres, dropped into the courtyards the homesteads left.

    AFTER the houses (they slot into the gaps the final layout produced, which is a thing only the
    finished layout knows) and BEFORE the grove (whose canopy then skips them). Both are sized off
    the houses that actually landed, not off the declared household count: a byre is roughly one per
    four or five households, and the wells cover the cluster's real extent.

    Steps:
        l7r.diagram.hamletgen.homesteads.wells.place_wells
        l7r.diagram.settlement.Settlement.draft_byres
    """
    houses = s.M.get("houses", [])
    place_wells(s, plan, houses)
    s.draft_byres(fraction=0.22, gap=60)
