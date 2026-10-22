"""STAGE 4b, the lane web (`stage_web`), and the runs it lays and resettles. Split from `ways/web.py` at the 1,000-line bar (feature 405 T57).

Research: web plumbing - NONE"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from l7r.diagram.overlap.registry import PLACER_MARGIN_PX
from l7r.diagram.settlement import Settlement, seg_dist
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from ...clearance import Gapped
from ...consts import (
    BUNDLE_PITCH,
    CLUSTER_SPAN_FACTOR,
    WEB_CROP_GAP,
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    Poly,
    Pt,
)
from ...plan import SitePlan
from ..bund import a_way_onto_the_bund, cut_past_the_junction
from ..checks import drawn_water_segs
from ..clearance import clear_runs
from ..fabric import _LANE_JOIN_FT, _homestead_polys, _margin_frame, _net_segs, _pass
from ..geom import _TOUCH_GAP, polyline_len
from ..joints import center_lane_ends, fold_the_connector_hairpin, meet_end_to_end, split_at_crossings, straighten_joints
from ..serve import _lay_web_lane, lay_door_paths, street_anchors
from ..settle import settle_the_web
from ..smooth import _STUB_REACH_FT, _smooth_web
from ..street import lay_row_streets, trim_streets
from ..sweeps import (
    _bridge_collinear_breaks,
    _drop_end_nubs,
    _join_orphan_ways,
    _keep_the_route_wide,
    _sweep_dangling_ends,
    _sweep_debris,
    _sweep_doubled_remnants,
    _sweep_doubled_tails,
    _sweep_steading_fouls,
)
from ..touch import _touch_junctions
from .skeleton import _lay_skeleton, _web_cut_lines
from .tidy import _drop_collapsed, cut_the_overruns, tidy_lane_ends


def stage_web(s: Settlement, plan: SitePlan) -> None:
    """The lanes the settlement wore.

    Every ENDOGENOUS way - the cluster's spine and the web of alleys off it - drawn now because only now is
    there a settlement to derive them from. Both are fitted to where the houses actually landed rather than to
    where the seat band predicted they would land, which is the distinction that matters: the spine used to be
    sized on the band while the houses spread wider than it, so it could not be guaranteed to reach them. Laid
    first, these lanes competed for ground with the very houses they exist to serve - measured, the four pool
    clusters' long axes grew 15-97%, sprawl no check measures. They also run after the byres and wells, not
    merely after the houses; between the two, their corridors reserved courtyard ground and exiled fixtures up
    to 210 ft. A DISPERSED hamlet draws nothing here at all, because it has no internal network - its farmsteads
    stand in their own holdings and the connector is the only way on the map. The web is then READ AS SHAPES
    before the stage ends (feature 133 T31/T32): every near-junction is closed so the lanes are one network in
    ink rather than by tolerance, each junction is made once, ends within a few paces meet at one node, and
    every lane is string-pulled and cleared of hairpins and zigzags - a worn path minimizes its turns, and a
    bend sits at a plot corner.

    Steps:
        l7r.diagram.hamletgen.ways.fabric._margin_frame
        l7r.diagram.hamletgen.ways.web._lay_skeleton
        l7r.diagram.hamletgen.ways.web._web_cut_lines
        l7r.diagram.settlement._knobs.web_cuts
        l7r.diagram.hamletgen.ways.web.lay_reachable_runs
        l7r.diagram.hamletgen.ways.web._reachable_runs
        l7r.diagram.hamletgen.ways.serve._lay_web_lane
        l7r.diagram.hamletgen.ways.sweeps._join_orphan_ways
        l7r.diagram.hamletgen.ways.sweeps._bridge_collinear_breaks
        l7r.diagram.hamletgen.ways.touch._touch_junctions
        l7r.diagram.hamletgen.ways.smooth._smooth_web
        l7r.diagram.hamletgen.ways.web._drop_collapsed
        l7r.diagram.hamletgen.ways.sweeps._sweep_debris
        l7r.diagram.hamletgen.ways.sweeps._drop_end_nubs
        l7r.diagram.hamletgen.ways.sweeps._sweep_steading_fouls
        l7r.diagram.hamletgen.ways.sweeps._sweep_doubled_remnants
        l7r.diagram.hamletgen.ways.sweeps._keep_the_route_wide
        l7r.diagram.hamletgen.ways.joints.straighten_joints
        l7r.diagram.hamletgen.ways.joints.center_lane_ends
        l7r.diagram.settlement.Settlement.trim_lane_stubs
        l7r.diagram.hamletgen.ways.bund.run_lanes_on_to_the_bund
        l7r.diagram.hamletgen.ways.joints.meet_end_to_end
        l7r.diagram.hamletgen.ways.bund.a_way_onto_the_bund
        l7r.diagram.hamletgen.ways.settle.settle_the_web

    Research:
        dispersed hamlet draws no web - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html
        lanes after the houses - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html
        belt crossed not followed - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a lane
            may cross a shelter belt, the planting resuming on both sides, but not run its length
        door path reach - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a farm takes no door path where a way's point nearest its house stands within 60 ft of it or `STEADING_ARRIVAL_FT` (12 ft) of its built ground (`serve.street_arrives`)
        web lanes off the hard ground - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html, research/questions/0081-village-lanes.drawing.html: a stretch that would cross the field, a crop or wet ground is cut out
        web lane margin off the hard ground - research/questions/0081-village-lanes.drawing.html: the page lets a lane touch a plot's boundary - a web lane kept a half-tread off the field and the crop (`WEB_CROP_GAP`), 8 ft off the toe and marsh (`WEB_HARD_GAP`, UNRESEARCHED)
        a web lane's middle off the fabric - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: WEB_FABRIC_GAP, 7 ft clear of a garden fence (`clear_runs`' tight margin)
        ground cover is not fabric - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a lane crosses a tree belt and the planting resumes on both sides
        scrub and commons crossed - UNRESEARCHED: a lane may cross grazing scrub and the commons
        a further row street's end - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: pulled back to the last house it serves - it ends at its outermost joint, or abreast the house of the last farm it serves without a path (`trim_streets` at `street_anchors`)
        the web's frame - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a back lane is laid about 30 ft past the last house it serves and its end then pulled back to that house - the frame (`BUNDLE_PITCH`, 100 ft past the outermost house, or `CLUSTER_SPAN_FACTOR` times the seat band) is only the room the cuts are laid in, and the trims (`tidy_lane_ends`) bring each end back to the last house it serves
        a row village laid without web cuts - research/questions/0033-row-villages-resson.drawing.html: its farms are strung along their street and reach it by a path where their grove is in the way - its ways are its streets and those paths; no back lane or alley is cut among its farms (a map drawing convention)
        web lanes off the water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way keeps to its own bank; web cuts and joins clipped at the watercourses and drawn channels, a join crossing the brook only at a ford, one of the crossing places
        orphan stub joined - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the lanes are one network, so a stranded stub is joined into it
        orphan stub's reach - research/questions/0081-village-lanes.drawing.html: within `_STUB_REACH_FT`, 25 ft, the page's join reach, a stub is joined into the network
        web lanes routed round the households' reserved wood seats as fabric - GUESS research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: every pass clips and routes round each reserved wood seat by the copse's lane buffer, as it does a steading; no page read shows a lane through a household's grove
        row streets laid - research/questions/0033-row-villages-resson.drawing.html
        every farmhouse served - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every farmhouse but the few reached across a neighbor's land, which `checks.unreached_houses` counts reached through their neighbor's chain
        a row farm's door point - GUESS research/questions/0033-row-villages-resson.drawing.html: where such a farm's gate stood was not found; set 8 ft past its yard (`front_door` at `DOOR_STEP_FT`); it picks the farm's own street (`own_street`) and starts its door path, while arrival and the trim are judged from the house
    """
    _pass("cut")
    """STAGE 5b: the LANE WEB - the lanes that make every farmhouse reachable.

    WHY IT EXISTS. The record finds a house in a nucleated cluster reached by a way - "every house in the nucleated
    village is accessible via the interconnected system of narrow lanes and alleys" (research/contents.json#homesteads) -
    but not always: a household whose land has no way of its own is reached across its neighbor's (feature 317,
    research/questions/0081-village-lanes.html), and counts reached through its neighbor (`checks.unreached_houses`), so
    the web owes it no lane. The skeleton alone does not deliver the rest - it is sized on
    the seat band while the houses spread wider - and before this stage a third of the pool's
    farmhouses stood more than 100 ft from any way, with a whole block of Sawada touched by nothing.

    WHY IT RUNS AFTER THE HOUSES - which is now true of EVERY lane, not just this one (feature 128).
    Until then the web was the exception and the rest were laid first. `stage_seat`
    lays its lanes first precisely so the homesteads FRONT them, and the first attempt at this
    feature followed that rule and laid the web first too. It does not work, and the reason is worth
    keeping: a lane laid before the houses has to reserve its ground from a cluster that has not been
    packed yet, so it competes with the very houses it exists to serve. Given a normal corridor it
    pushed them outward and the four hamlets' long axes grew 51%, 58%, 15% and 97% - sprawl no check
    measures. Given a narrow one the houses collided with it instead. Laid AFTERWARDS the conflict
    simply is not there: placement is untouched, the cluster is exactly as compact as it was, and the
    web goes in the room that is actually left. That is also the truer account of these ways - an
    alley IS the residual gap between two plots, "colonized as semi private space by the adjoining
    house", not a corridor set aside in advance.

    THE FORM IS THE ROLLED KNOB, and the two differ by which axis is cut (`web_cuts` does both):
      - "alleys"    - laterals running back through the cluster, between columns of houses. The
                      accretive Chinese gridiron; it reads as a place that GREW.
      - "back_lane" - lanes running the length of the settlement, behind a rank. The planned form,
                      where the outermost one doubles as the village/farmland edge; it reads as a
                      place that was LAID OUT.
    Everything else about them is identical, which is what makes the knob honest: the difference a
    reader sees is the difference the research actually attests."""
    houses = list(s.M.get("houses", []))  # every house, the headman's too (feature 385 T125, D148: an `or True` test filtered none)
    if len(houses) < 2 or not plan.envelope:
        return
    # A DISPERSED HAMLET HAS NO INTERNAL LANE NETWORK AT ALL, and that is the form, not a shortfall.
    # Tonami's farmsteads stand in the middle of their own holdings; what joins them to the world is
    # the connector out to the road, which `stage_track` has already drawn, and what joins them to
    # each other is the field baulks they walk on. Drawing a web here would erase the one thing that
    # makes the form legible at a glance. The two access checks are conditioned on the form to
    # match - see `research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`.
    if plan.settlement_form == "dispersed":
        s.M["meta"]["lane_skeleton"] = "none"
        return
    # THE FRAME SPANS THE HOUSES, MEASURED - not a multiple of the seat band. `CLUSTER_SPAN_FACTOR`
    # describes the row `front_row` offers seats along, and for a round or elongated cluster it is a
    # fair proxy for where the houses end up. For a CRESCENT it is not: the cluster wraps around the
    # field and its ends run well past the band, so the web's whole coordinate domain stopped short
    # of them and their houses could not be reached at all. That was every remaining cohort failure
    # and nothing else - all four were `shape=crescent`, worst house 431 ft from any way. The houses
    # are already placed by the time this runs, so there is no need to predict where they went.
    _ax, _ay = plan.seat["along"]
    _anchor = plan.seat["anchor"]
    _reach_along = max(abs((float(h["x"]) - _anchor[0]) * _ax + (float(h["y"]) - _anchor[1]) * _ay) for h in houses)
    frame = _margin_frame(plan, max(plan.seat["lat"] * CLUSTER_SPAN_FACTOR, _reach_along + BUNDLE_PITCH), near=[(float(h["x"]), float(h["y"])) for h in houses])
    # ...the cuts cover every house BUT one reached across its neighbor's yard, which is owed no lane (feature 317)
    proj = [frame.project((float(h["x"]), float(h["y"]))) for h in houses if not h.get("reached_across")]
    arcs = [a for a, _ in proj]
    stands = [d for _, d in proj]
    # THE SKELETON GOES IN FIRST, in this same house-fitted frame (feature 126). It used to be laid
    # two stages earlier, before any house existed; now it is derived from where they actually went.
    # It runs before the web cuts so the web sees it as existing network to thread around and join,
    # which is what `_net_segs` reads.
    # A ROW VILLAGE WITH PLANNED STREETS lays those, not a skeleton and cuts sized on the house cloud (feature 291 plan
    # D17): the streets are laid below, once the steadings' fabric is known, and the stragglers and door paths still run.
    _rows = plan.settlement_form == "linear" and bool(getattr(s, "_row_streets", None))
    _pass("skeleton")
    if not _rows:
        _lay_skeleton(s, plan, frame, arcs, stands)

    lines = [] if _rows else _web_cut_lines(plan, frame, arcs, stands)  # no cuts on a row: its farms are served by their street

    crops = crop_polys(s)
    toe = s.toe_band() or None
    wet = marsh_ground(s.M)  # 405 T121: a defense belt too - no map draws a causeway (0081)
    # THE CROP AT A WEB LANE'S HALF-TREAD, THE TOE AND THE MARSH AT `WEB_HARD_GAP` (feature 374 wave 143, 0081): each crop polygon
    # carries its own gap (`Gapped`), so every reader handed `hard` keeps a lane on the bund and off the wet
    hard = [Gapped(plan.envelope, WEB_CROP_GAP), *(Gapped(c, WEB_CROP_GAP) for c in crops), *([toe] if toe else []), *wet]
    # ...AND THE HOUSEHOLDS' RESERVED WOOD SEATS ARE FABRIC TO THE WEB (feature 287 M8): the registry refuses a lane within
    # the copse's lane buffer of a seat, so every pass clips and routes round them - sized so the web's own fabric margin
    # (`WEB_FABRIC_GAP`) plus a footpath's half-tread lands on the buffer - rather than laying a cut the registry then
    # refuses and leaving its houses unreached (seed 39: 60 routes against 7, when a straggler search still served them)
    fabric = _homestead_polys(s) + [(w, None, "wood seat") for w in s.standing.reserved.seat_walls(reach=seat_wall_reach(s))]
    # WHAT A LANE MAY NOT BE DRAWN THROUGH, now that lanes come LAST (feature 126).
    #
    # `hard` is ground: the field, the crop, the wet toe. It says nothing about what the settlement
    # has BUILT, which was fine while the lanes were laid first and the houses packed around them.
    # With the order inverted, every pass that draws a way has to avoid the fabric itself - and the
    # repair passes did not, so they routed links straight through steadings:
    #   seed  7  ('houses', 'lanes')          - a tread over a farmhouse
    #   seed 19  ('lanes', 'threshing_yards')
    #   seed 26  ('lanes', 'gardens')
    # Seed 7's second failure even quotes the old doctrine back - "lay lanes BEFORE the houses" -
    # which is precisely the assumption this feature removes.
    #
    # Ground cover is NOT fabric, for the same reason the straggler footpaths excluded it: a footpath may
    # cross grazing scrub and run along a tree belt, because those are what the ground IS rather than
    # things built on it. Counting them walls a steading in behind its own commons.
    _solid = [poly for poly, _own, kind in fabric if kind not in ("commons", "village_groves")]
    # A WOODPILE-YIELDS FALLBACK WAS BUILT HERE AND MEASURED AS A NO-OP (feature 152 T13, 2026-08-29).
    # The recorded defect was Kuwabata's back lane coming apart with 25 ft between two rounded caps and a
    # 10 x 3.5 ft woodpile 5.6 ft off the line, so the short-gap router was given a wall set with the small
    # movable fixtures removed - a household shifts a stack when the path it walks says to. It closed
    # nothing: measured after, the facing gaps on all four maps were unchanged, because by then every
    # scripted map's lane web was already ONE connected component. The severance had been fixed upstream
    # by this feature's other work, and what my gap detector was finding was two ends of an already-joined
    # web standing near each other, which is not a defect. Do not build it again without a map whose web
    # is genuinely in two pieces AND whose gap holds a fixture.
    hard_built = [*hard, *_solid]
    walls = [poly for poly, _, _ in fabric]
    # The shelter belts, separately: a web lane may CROSS one but may not run its length.
    belts = [[(float(a), float(b)) for a, b in g["poly"]] for g in s.M.get("village_groves", []) if g.get("poly")]
    drawn_water = drawn_water_segs(s)  # channels AND streams - see the helper for why the streams were missing
    if _rows:
        lay_row_streets(s, houses, hard_built, walls, list(plan.watercourses) + drawn_water, plan.brook or [])
    cands: list[Poly] = []
    for line in lines:
        # FINER SAMPLING AND A WIDER FABRIC MARGIN THAN THE DEFAULTS. A web lane runs among the
        # steadings rather than past them, so it gets many more chances to clip a corner: sampled
        # every 8 ft with a 6 ft margin it cut across dooryard gardens on 7 of 24 cohort seeds, both
        # endpoints of the offending step legally clear while the step between them crossed the bed.
        # 4 ft samples and an 8 ft margin close that; the cost is sampling time on a short line.
        cands.extend(clear_runs(line, hard, WEB_HARD_GAP, step=4.0, lines=list(plan.watercourses) + drawn_water, tight=walls, tight_margin=WEB_FABRIC_GAP))
    # DECIDE CONNECTIVITY BEFORE ANY INK GOES DOWN. A run that cannot be reached from the skeleton is
    # not drawn at all, which is only possible because the decision is made over CANDIDATES - once a
    # lane is drawn there is no clean way to take it back, and the version that judged each run as it
    # went could only ever refuse the ones it had not reached yet. Growing the component from the
    # skeleton outward also lets a run join THROUGH another web run, which is what a framework is.
    lay_reachable_runs(s, cands, hard, walls, list(plan.watercourses) + drawn_water, belts, [(float(h["x"]), float(h["y"])) for h in houses])
    # A WEB LANE STOPS WHERE IT STOPS SERVING. Clipping ends an arm wherever the crop or a steading
    # happens to begin, which can leave a tail running on into bare grass - `lanes_reach_something`
    # is right to call that a tread that serves nobody. The engine already owns this trim; the web
    # simply has to ask for it after adding to the network.
    s.trim_lane_stubs()
    # ONE NETWORK FIRST: a lane that joins an orphaned component is worth nothing while the component itself is an island.
    # A HOUSE THE WEB STILL LEAVES UNREACHED IS THE SETTLE'S (feature 287, GM 2026-09-30): the straggler footpath pass that
    # stood here - a door path routed to every house the web left more than 90 ft from a way - was dropped once the seating
    # reserved every house's corridor (`tree.admits`) and the settle drew it for any house left unreached (`settle_the_web`,
    # `last_resort.refuse_unreached`). Measured with it off: the reference snapshot 26.85 s -> 23.85 s, lanes 380 -> 347
    # (`specs/287-placer-guarantees/measurements.json`, `straggler-footpaths-off`).
    _pass("join-orphans")
    _join_orphan_ways(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # ...and close any break where one way was drawn as two.
    _pass("bridge-breaks")
    _bridge_collinear_breaks(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    _pass("touch")
    _touch_junctions(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # ...AND JOIN ORPHANS AGAIN, LAST. The first pass runs before the bridges and the footpaths, so
    # it can only see the lanes that exist then - on cohort seed 39 that was FOUR of the twelve the
    # map finishes with, and the eight added afterwards formed a second network of their own. Every
    # house on that map is within 86 ft of a lane and twelve of them still counted as unreached,
    # because the lane serving them was not on the network the connector is on. A repair pass that
    # runs before the things it repairs is not a repair pass.
    # ...and CLOSE BREAKS again before joining, for the same reason the join runs twice: the
    # touch pass draws lanes, and a lane drawn after the bridge pass can leave a hole the bridge
    # pass never saw. On cohort seed 48 the bridge found ZERO candidates and the finished map still
    # had a 78 ft hole in a street, because the hole did not exist yet when it looked.
    _pass("bridge-breaks")
    _bridge_collinear_breaks(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    _pass("join-orphans")
    _join_orphan_ways(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # ...AND TRIM AGAINST THE FINAL NETWORK, ONCE, LAST.
    #
    # Every lane is trimmed to service when it is drawn, against the ways and houses that exist AT
    # THAT MOMENT - and then later passes draw more lanes, join orphans and bridge breaks, none of
    # which revisits an earlier lane's ends. So a web lane trimmed correctly at draw time can finish
    # with an end reaching nothing: the ratchet's Cohort-42 shipped a 146 ft web lane whose end stood
    # 80 ft from the nearest house, just past the 40 ft way / 90 ft house thresholds
    # `lanes_reach_something` measures.
    #
    # Trimming ONLY at the end would be wrong the other way - `_lay_web_lane` needs its ends settled
    # before the join is computed from them ("TRIM FIRST, JOIN SECOND", above) - so this is a final
    # pass rather than a replacement, and it only ever SHORTENS. A lane reduced below the debris
    # floor is dropped, because a way that serves nothing is not a short way, it is not a way.
    #
    # NOT `trim_lane_stubs`: that is a different, harsher rule (71 ft floor) meant for a skeleton arm
    # laid before the houses, and running it here ate the short door paths the web draws - measured
    # once at 43/48 -> 9/48, when a straggler pass still drew them.
    tidy_lane_ends(s, list(plan.envelope))
    # LAST: read every lane as a shape and take out what feet would never wear (T32) - after the
    # trim, because the trim is the last pass that changes a record; then touch once more, because
    # cutting a hairpin's arm can move an end.
    _pass("smooth")
    _smooth_web(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # AND TOUCH AGAIN (T99 unlock, tripwire seed 37): the smoothing cuts knots and hairpins into stubs,
    # and a stub that ends 3-30 ft short of the run it left is exactly the gap _touch_junctions closes -
    # but that pass ran BEFORE the smoothing. A way the knot collapse emptied to one point is dropped first.
    _drop_collapsed(s)
    _touch_junctions(
        s, hard_built, walls, list(plan.watercourses) + drawn_water, reach=_STUB_REACH_FT, only_orphans=True, final=True
    )  # the stubs the smoothing leaves stop 30-35 ft short (seed 37); a connected web is untouched
    _pass("touch")
    _touch_junctions(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # AND SWEEP WHAT IS LEFT (feature 134 T50): the passes above shorten lanes, and `_WEB_MIN_FT` was
    # only ever asked at draw time. Last, so it judges the tread the map actually ships.
    _sweep_debris(s)
    _drop_end_nubs(s, hard_built)  # every pass above can leave a nub at a junction it laid
    # LAST OF ALL, AFTER THE NUB DROP AND NOT BEFORE IT (feature 155). Placed ahead of them this swept a
    # foul that did not exist yet: `_drop_end_nubs` shortens a lane, and the END IT LEAVES BEHIND can be
    # nearer a steading than the one it removed. So the steading sweep has to be the last thing that looks
    # at a lane, for the same reason the nub drop is placed after everything else.
    _sweep_steading_fouls(s)
    # ...AND RE-JOIN WHAT THE TRIMS SEPARATED (settlement-review, feature 155). `_bridge_collinear_breaks`
    # already runs twice above, but both times BEFORE the trims that can open a break - kashikawa came back
    # with one route drawn as two and 19.5 ft of bare ground between two ends pointing straight at each
    # other. Running it once more here closes what this pass opened; it routes against the same obstacle set
    # as every other join, so it cannot bridge THROUGH a steading, and the sweep below re-checks anyway.
    # THE REMNANT SWEEP RUNS BEFORE THE LAST BRIDGE, NOT AFTER (settlement-review, feature 155). With
    # it after, the two passes built and then deleted each other's work: sawada's 37.6 ft remnant left
    # lane 11 at 1.2 ft and died 11.4 ft from it, which sits inside the restored short-gap band, so the
    # bridge pass dutifully closed the remnant back onto its own parent - and the remnant sweep then
    # dropped both, because the bridge's two ends were now also on lane 11. One wasted routing pass and
    # two husks for a picture that was correct either way.
    _sweep_doubled_remnants(s)  # doubled ink is debris however long it is
    _bridge_collinear_breaks(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    _sweep_steading_fouls(s)  # a bridge is a lane too, and it gets the same last look
    _sweep_doubled_remnants(s)  # ...and a bridge can itself be doubled ink
    _sweep_dangling_ends(s)  # LAST: an end the passes above left in open ground is pulled back to something, or dropped
    _sweep_debris(s)  # a fragment the passes above whittled below the floor and left standing alone
    # A WAY OUT OVER THE BROOK AND BACK is the settle's to mend (`law.way_out_carriers`, `settle_the_web`): the home-bank
    # re-serve that stood here (feature 261) routed a straggler footpath on the house's own bank, and went with that pass
    # (feature 287, GM 2026-09-30)
    _keep_the_route_wide(s, hard_built, walls, list(plan.watercourses) + drawn_water)  # ...and a cart route may not neck to a footpath
    # AND READ THE JOINTS AS ONE WAY (GM 2026-09-26): two records meeting end to end are one lane to the walker;
    # a fold there becomes a T and a jog is pulled straight. Last, because every pass above can lay a joint.
    straighten_joints(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    fold_the_connector_hairpin(s, walls)  # ...and a lane and the connector doubling back over a short leg meet as a T (the 269 landing)
    # ...AND THE ENDS ARE ASKED ONCE MORE, after the joints are read as one way (feature 261). An end that reached the lane it
    # was about to be joined to passed the sweep above and was left, after the join, reaching only its own lane: Mizuguchi's
    # (558, 1096) stood 56 ft from lane 2's end until the two became one lane, and then 104 ft from anything.
    _sweep_doubled_tails(s)  # a lane that runs on beside the way it met ends where it met it (feature 261)
    _sweep_dangling_ends(s)
    # ...AND A LANE THAT ENDS ON ANOTHER STANDS ON ITS CENTERLINE (GM 2026-09-27): an end a few feet off it shows its round cap past the far edge.
    # A NEEDLE JOIN SQUARED HERE WAS TRIED AND REVERTED (the 269 landing, 2026-09-28): Mizuguchi's orphan join runs 35 ft
    # back along the skeleton lane at 16 degrees before meeting it, and moving its end to the foot of the vertex before it
    # (square to the tread) let the tidy trim the skeleton's tail, which had been a gable-end house's nearest way - two
    # households' ways out then left by another lane and missed the entrance board (`test_an_entrance_board_stands_at_the_
    # entrance`). Feature 287 relays a needle end in `settle_ends` (`law.needle_ends`, ways W21) instead; a fix here has
    # to keep the tail's service.

    center_lane_ends(s)
    cut_the_overruns(s)
    cut_past_the_junction(s)  # ...and a free end run on past its own junction to nothing (the 269 landing, Mizuguchi)
    # ...and a record the joins emptied is not a lane: a husk with no points declares a way nothing draws (a review
    # counted three on Kashikawa and two on Kuwabata) - dropped with its ink slot, the one way lanes leave
    # ...and a record whose points are all one point is a husk too (Mizuguchi, feature 261: seven three-point records at a
    # single spot, left by the passes that re-cut the home-bank footpath)
    s.drop_lanes([i for i, ln in enumerate(s.M.get("lanes") or []) if len(ln.get("pts") or []) < 2 or polyline_len([(float(x), float(y)) for x, y in ln["pts"]]) < 1.0])
    # ...AND THE ENDS ARE TRIMMED TO SERVICE ONCE MORE, LAST (feature 261, once main's placer re-laid the pool): every pass
    # after the first tidy can leave an end in open ground - the dangling-end sweeps, the joint straightening and the cut
    # past the connector all reshape lanes - and Kuwabata shipped a skeleton arm into the scrub that the first tidy had
    # seen as part of a longer lane. The same trim, with the same `keep` for a house whose only way a lane is.
    split_at_crossings(s)  # a crossing is a junction: recorded as one before the trim judges what each end serves (the 269 landing)
    tidy_lane_ends(s, list(plan.envelope))
    meet_end_to_end(s, walls)  # ...and two ends the trims left facing each other across a hand's width are joined
    # ...AND DOUBLED INK IS SWEPT ONCE MORE, AFTER THE SPLIT (feature 293; Sawada in the earlier 293 pass): a join lane laid
    # to an "orphan" that in fact crossed the web mid-run is the only link at the ink tolerance until `split_at_crossings`
    # records that crossing as a junction - and from then it is a tread doubled beside another, which both doubled-ink
    # sweeps above had kept as a link. The same sweep, with the same stranding and one-network refusals.
    _sweep_doubled_remnants(s)
    # ...AND THE PADDY IS REACHED (269 B04, research/fields/290): where no lane end stands on its bund - the spur swept, or
    # never drawn - the nearest lane runs on to it, or a field path is drawn off the nearest lane; recorded either way
    # ...AND A GROVE FARM IS REACHED AT ITS FRONT DOOR (feature 291 FR-019), LAST: laid before the trims, a door path was cut
    # back off its door by them (Mizuguchi: the farm at (232,1582) served, its door 60 ft from the path's trimmed end)
    # ...EVERY ROW FARM, unless its door is on its street (feature 291 on feature 287's lane law): a row farm's house stands
    # most of a frame off its street, so the street's end past the last farm served nothing the law counts (`end_serves`,
    # 60 ft of a house center) and the settle trimmed it back farm by farm - Mizuguchi's east row, its doors 33-39 ft off the
    # street and so given no path at the 40 ft reach, ended 200-1,090 ft off any way. Each farm's own path meets its street,
    # as the seating's corridor meets the tree on a nucleated map, and the street's end then stands at a junction.
    lay_door_paths(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    if _rows:
        # ...and a door path laid beside a lane that was there first meets it rather than doubling it (Kashikawa: a
        # join-orphans lane ran on 64 ft beside the door path of the farm at (2299, 2724)) - the sweep that ran above,
        # before any door path existed
        _sweep_doubled_tails(s)
        tidy_lane_ends(s, list(plan.envelope), streets=True)
        # ...and a further street ends at its outermost joint, not past its last farm's path - or the last farm it serves without
        # one (`street_anchors`, T97: the street's point nearest each such house); the first runs on off the map as the road (0033)
        trim_streets(s, _TOUCH_GAP, street_anchors(s), 1.0)
    s.M["meta"]["field_path"] = a_way_onto_the_bund(s)
    s.M["meta"]["lane_web"] = plan.lane_web
    # ...AND THE WEB SETTLES ITSELF, LAST (feature 287, M4): every rule of the lane law is asked of the web as it stands and
    # what breaks one is cut away or re-laid (`settle_the_web`), the crossings squared first - so no stage after this one
    # rewrites a lane. A cut can take a farmhouse's only way or the field path, so the settle draws what the web still owes -
    # each stranded house's reserved corridor, a spur to each way target, the field way (M3's web half) - as lanes it never
    # cuts; the straggler redraw that stood in for the corridor until it landed is gone with the driver's re-roll.
    _pass("settle")
    # ...and its wall-clock seconds stay out of the manifest: a timing written there rewrote all five pool maps on every
    # regeneration with nothing on them moved (287, 2026-09-29); the rounds and the lane counts are the record.
    s.M["meta"]["web_settle"] = {k: v for k, v in settle_the_web(s).items() if k != "seconds"}
    resettle_straightened(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # THE CORRIDORS HAVE SERVED (feature 287 M8): every way the seating held them for is drawn, so the registry's reservation
    # of them ends here - the notice board may stand beside a way drawn along one, as beside any way
    s.standing.reserved.release_corridors()


def seat_wall_reach(s: Settlement) -> float:
    """The radius a reserved seat is walled at for the web (`stage_web`): the copse's lane buffer about it, a footpath's
    half-tread and the placer's margin, less the fabric margin every web pass keeps off a wall - never under a foot."""
    return max(1.0, s.standing.reserved.lane_buffer + 1.5 + PLACER_MARGIN_PX - WEB_FABRIC_GAP)


def lay_reachable_runs(s: Settlement, cands: Sequence[Poly], hard: list[Poly], walls: list[Poly], water: list[tuple[Pt, Pt]], belts: Sequence[Poly], houses: Sequence[Pt]) -> int:
    """Draw every candidate run the way network can reach (`_reachable_runs`), each through `_lay_web_lane`; how many it
    drew. Lifted from `stage_web` (feature 146's rule) when the pool's maps stopped laying a web lane at all (2026-10-02)."""
    return sum(1 for run in _reachable_runs(cands, _net_segs(s)) if _lay_web_lane(s, run, hard, walls, water, belts=belts, houses=houses))


def _reachable_runs(cands: Sequence[Poly], seed_segs: Sequence[tuple[Pt, Pt]]) -> list[Poly]:
    """The candidate runs that can be REACHED from the existing way network, growing outward.

    A run joins if it comes within `_LANE_JOIN_FT` of the skeleton or of a run already admitted, so a
    back lane may join through a cross-tie and a tie may join through a back lane - which is exactly
    what makes a framework a framework. Everything left over is an island and is never drawn.

    Deciding this over candidates rather than over drawn lanes is the whole point: a lane that has
    been inked cannot be taken back, so an earlier version - which asked each run as it was about to
    be drawn whether it touched anything yet - refused runs merely for being early in the loop and
    admitted islands that happened to be laid first. Order should not decide what a village looks
    like.

    ADJACENCY IS COMPUTED ONCE, over a bounding-box prefilter, and the runs are subsampled to a
    stride before any distance is measured. The naive version re-measured every admitted segment
    against every remaining run on every pass - a candidate is ~175 points at the 4 ft clip step and
    the admitted network grows without bound, so it went quadratic in samples on top of quadratic in
    passes and killed a cohort worker outright. The prefilter is the index and the stride is the
    resolution; neither decides anything, which is the project's standing rule for both.

    Research: islands never drawn - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: one network grown from the skeleton"""
    runs = [r for r in cands if len(r) >= 2]
    if not runs:
        return []
    stride = max(1, int(_LANE_JOIN_FT / 8.0))
    thin = [r[::stride] + [r[-1]] for r in runs]

    def box(pts: Sequence[Pt]) -> tuple[float, float, float, float]:
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        return (min(xs) - _LANE_JOIN_FT, min(ys) - _LANE_JOIN_FT, max(xs) + _LANE_JOIN_FT, max(ys) + _LANE_JOIN_FT)

    boxes = [box(r) for r in thin]

    def near(i: int, j: int) -> bool:
        a, b = boxes[i], boxes[j]
        if a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1]:
            return False
        return any(seg_dist(q[0], q[1], u, v) <= _LANE_JOIN_FT for q in thin[i] for u, v in zip(thin[j], thin[j][1:], strict=False))

    seed_pts = [q for a, b in seed_segs for q in (a, b)]
    seed_box = box(seed_pts) if seed_pts else None
    reached = set()
    for i, r in enumerate(thin):
        if seed_box is None:
            continue
        bx = boxes[i]
        if bx[2] < seed_box[0] or seed_box[2] < bx[0] or bx[3] < seed_box[1] or seed_box[3] < bx[1]:
            continue
        if any(seg_dist(q[0], q[1], u, v) <= _LANE_JOIN_FT for q in r for u, v in seed_segs):
            reached.add(i)
    if seed_box is None:
        reached = {0}
    frontier = list(reached)
    while frontier:
        i = frontier.pop()
        for j in range(len(thin)):
            if j not in reached and near(i, j):
                reached.add(j)
                frontier.append(j)
    return [runs[i] for i in sorted(reached)]


def resettle_straightened(s: Settlement, hard: list[Any], walls: Sequence[Any], water: list[Any]) -> None:
    """THE JOINTS READ AS ONE WAY ONCE MORE, where the settle laid a Z at one (feature 308, Inashiro on the merged engine: a
    crossing squared near the field spur's end turned it back against the link joined there - `square_every_crossing` runs
    after the web's joint pass); a joint it rewrites is settled again, and the settle's record replaced. Its wall-clock seconds
    stay out of the manifest (287, 2026-09-29).

    Research: joints read as one way - research/questions/0081-village-lanes.drawing.html: two lanes meeting end to end are one"""
    if straighten_joints(s, hard, walls, water):
        s.M["meta"]["web_settle"] = {k: v for k, v in settle_the_web(s).items() if k != "seconds"}
