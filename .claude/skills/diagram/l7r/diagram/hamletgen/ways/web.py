"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, seg_dist, skeleton_layout, web_cuts
from l7r.diagram.sitegen.geom import crop_polys

from ..cluster import _arm_crossing_accidental
from ..consts import (
    BUNDLE_PITCH,
    CLUSTER_SPAN_FACTOR,
    LANE_CLEARANCE,
    MIN_WEB_GAP,
    WEB_FABRIC_GAP,
    WEB_HARD_GAP,
    WEB_REACH_FT,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .checks import drawn_water_segs
from .clearance import clear_runs, clip_to_clear
from .fabric import _LANE_JOIN_FT, _WEB_MIN_FT, _homestead_polys, _margin_frame, _net_segs, _pass, _pull_back_to_service
from .geom import _trim_to_service, polyline_len
from .route import _route
from .serve import _lay_web_lane, _serve_stragglers
from .smooth import _STUB_REACH_FT, _smooth_web
from .sweeps import _bridge_collinear_breaks, _drop_end_nubs, _join_orphan_ways, _keep_the_route_wide, _sweep_debris, _sweep_doubled_remnants, _sweep_steading_fouls
from .touch import _touch_junctions


def _lay_skeleton(s: Settlement, plan: SitePlan, frame: _margin_frame, arcs: Sequence[float], stands: Sequence[float]) -> list[tuple[Poly, Poly]]:
    """The cluster's internal SKELETON, laid AFTER the houses and fitted to where they went.

    THIS USED TO RUN BEFORE THE HOUSES, and moving it is feature 126's whole point. The GM asked
    whether pre-laying lanes reflects how they form, and it does not: a lane between farmsteads is
    trodden by households already living there. The project had reached that conclusion once already
    for the lane WEB - "an alley IS the residual gap between two plots ... not a corridor set aside
    in advance" - and this is the half that was still laid first.

    It was also measurably wrong. The skeleton was sized on the SEAT BAND while the houses spread
    wider than the band, so it could not be guaranteed to reach them; that mismatch is the root of
    the `farmhouses_reach_a_way` defect that survived seventeen recorded attempts. Fitted to the
    houses' own arc extent instead, the question does not arise - the arms span the settlement that
    actually exists rather than the one the band predicted.

    The frame, arcs and stands are the caller's, already measured off the placed houses, so the
    skeleton and the web share one coordinate domain and cannot disagree about where the cluster is.
    Returns the kept arms, for the web to treat as existing network."""
    if len(arcs) < 2:
        return []
    arc0 = (min(arcs) + max(arcs)) / 2.0

    stand0 = sum(stands) / len(stands)
    # SIZED FROM THE HOUSES, not from `seat["lat"]`/`seat["dep"]`. Half-extents, because
    # `skeleton_layout` takes half-widths, and floored at one bundle pitch so a tight cluster still
    # gets a spine with somewhere to run.
    lat = max((max(arcs) - min(arcs)) / 2.0, BUNDLE_PITCH * 0.5)
    dep = max((max(stands) - min(stands)) / 2.0, BUNDLE_PITCH * 0.5)
    layout = skeleton_layout(plan.lane_skeleton, 0.0, 0.0, lat, dep)

    def _on_margin(p: Pt) -> Pt:
        # local +x runs along the band, local +y toward the field (so OUT of the frame is -y).
        q = frame(arc0 + p[0], stand0 - p[1])
        return (float(q[0]), float(q[1]))

    raw_arms = [[_on_margin((float(p[0]), float(p[1]))) for p in lane_pts] for lane_pts in layout["lanes"]]
    crops = crop_polys(s)
    # what is already standing: houses, yards, gardens, sheds - the arm must go round all of it
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    toe_now = s.toe_band() or None
    wet_now = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") != "defense" and m.get("poly")]
    drawn_water = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    kept: list[tuple[Poly, Poly]] = []
    for ai in range(len(raw_arms)):
        # Clipped exactly as before the move: off the crop, off the wet toe and every drawn marsh,
        # and off the water - an internal arm serves the houses and has no business crossing a ditch
        # (the spur and the connector are the ways that LEAVE, and they meet water squarely).
        # THE OBLIGATION INVERTED WITH THE ORDER, and this is the half that was missing (feature
        # 126). While the skeleton was laid FIRST, a lane was a no-build corridor and the HOUSES
        # avoided it. Laid last, nothing was stopping the arm from being drawn straight through a
        # farmstead - and nothing was: the in-gate ratchet went to 0 of 4, failing
        # `houses_clear_of_lanes`, `houses_off_corridors` and `features_do_not_overlap` on seeds
        # 41, 42 and 44. Reordering the stages is not enough on its own; every rule that pointed one
        # way across that boundary has to be turned around to match.
        #
        # `_homestead_polys` is the same fabric the web threads between (see `stage_web`), so the
        # skeleton and the web now agree about what is already standing.
        # TWO CLEARANCES, BECAUSE THEY ARE TWO DIFFERENT RULES.
        #
        # Crop, water and marsh want the full 20 px: a track keeps clear of standing rice and does
        # not skim a ditch. The FABRIC does not, and holding it to the same figure is what made the
        # first version of this pathological. A 20 px margin demands a 40 px clear corridor between
        # two steadings, which a packed cluster does not have - so instead of threading the gap the
        # arm was clipped away entirely, the cluster went unserved, and `_serve_stragglers` spent its
        # four passes routing rescue footpaths that mostly failed and were retried. Measured on
        # THIS DID NOT FIX THE SEED-25 COST, and the honest note matters more than the tidy one:
        # measured before and after, `stage_web` stayed at ~299 s with `_route` called 817 times
        # either way. So the arms were NOT being clipped out of existence by the fabric margin, and
        # whatever drives the straggler routing lies elsewhere. The split is kept because it is
        # right on its own terms, not because it bought anything.
        #
        # FABRIC_GAP is what these lanes actually are. The sources describe the lateral ones as
        # "colonized as semi-private space by the adjoining house" and barely more than the gap
        # between two walls - so the arm needs its own half-width and a little air, not a highway
        # verge. This is the same `WEB_FABRIC_GAP` the lane web already threads by, so the skeleton
        # and the web now agree about how close a lane may pass a wall.
        arm = clip_to_clear(raw_arms[ai], [list(plan.envelope), *crops, *([toe_now] if toe_now else []), *wet_now], 20.0, lines=list(plan.watercourses) + drawn_water)
        # ROUTE ROUND THE FABRIC, DO NOT CLIP THROUGH IT (feature 126, after review).
        #
        # Clipping was the first version and it deletes the form. An arm that crosses a packed
        # cluster meets a steading, gets cut, and what survives is whichever end happened to fall in
        # open ground - so a declared `Y` shipped ONE arm of three on Sawada and Mizuguchi, a `T`
        # shipped two arms that never meet on Kashikawa, and Inashiro's spine covered the middle
        # third of a crescent with 60% of its planned run trimmed away. Three independent
        # settlement-reviews found the same thing from three different maps.
        #
        # A trodden way does not stop at a wall, it goes ROUND it, and `_route` is the same Dijkstra
        # the lane web already uses for exactly this. The clip stays as the fallback: where no route
        # exists the honest outcome is still a shortened arm rather than a lane through a house.
        if len(arm) >= 2:
            routed = _route(arm[0], arm[-1], [list(plan.envelope), *crops, *fabric, *([toe_now] if toe_now else []), *wet_now], [], list(plan.watercourses) + drawn_water)
            arm = routed if len(routed) >= 2 else arm
            # AND CLIP WHAT WILL BE DRAWN, ALWAYS - not only when the router gave up.
            #
            # Routing round the fabric is a PLAN, and a plan can start inside a wall: the arm's
            # endpoints come from the template mapped onto the margin, so an endpoint can land on a
            # steading, and `_route` from a blocked start returns a path that leaves one. Measured on
            # cohort seed 7, a 5 px skeleton arm was drawn across a farmhouse and reported twice -
            # `features_do_not_overlap ('houses','lanes')` and `houses_clear_of_lanes`, the latter
            # quoting the doctrine this feature retired ("lay lanes BEFORE the houses").
            #
            # The clip is cheap and it is a GUARANTEE rather than a hope: whatever the router
            # produced, what gets drawn keeps its distance from everything already built.
            # A DEAD END, IMPLEMENTED AND REVERTED (feature 128, 2026-08-24). Do not re-try it
            # without new evidence.
            #
            # THE HYPOTHESIS was sound and the fix did nothing. `WEB_FABRIC_GAP` is 7 px, the clip
            # measures to the FOOTPRINT, and `houses_clear_of_lanes` measures to the CENTER at 14 -
            # so an arm can finish 11.6 px from a house center and fail, which is exactly what cohort
            # seed 27 reported. Splitting the clip (houses at TRACK_FABRIC_GAP, everything else at
            # WEB_FABRIC_GAP) is the same correction `TRACK_FABRIC_GAP` was introduced to make one
            # stage over, and it is defensible on its own terms.
            #
            # MEASURED: seed 27 failed at the identical coordinates afterwards, because the lane
            # standing on that house is the SPUR, not a skeleton arm. The attribution said
            # "skeleton/spur" and the two were not distinguished; assuming the wrong half cost the
            # attempt. Reverted rather than kept, because a behavior change with no measured benefit
            # is how a generator accumulates drift nobody can account for.
            arm = clip_to_clear(arm, fabric, WEB_FABRIC_GAP)
            # ...AND WHAT SURVIVES THE CLIP MUST STILL SERVE SOMETHING.
            #
            # The clip above cures a lane drawn over a steading by CUTTING it, and nothing then asks
            # whether the remainder is still a way. Both failure modes appeared at once across the
            # cohort, opposite symptoms of the same cut: seed 47 kept stubs whose ends reached
            # nothing (`lanes_reach_something`), and seed 8 lost so much arm that seven farmhouses
            # stood over 100 ft from any way, worst 260 (`farmhouses_reach_a_way`).
            #
            # `_trim_to_service` pulls the ends back to the last point that reaches a way or a house,
            # and `_WEB_MIN_FT` drops what is left if it is no longer a way at all - the same pair of
            # rules every web lane already passes through. An arm that serves nobody is not a
            # shortened arm, it is debris, and the houses it would have served are the straggler
            # pass's business.
            #
            # SERVICE IS JUDGED AGAINST THE HOUSES, NOT AGAINST THE WAYS. `_lay_skeleton` runs BEFORE
            # the web cuts, on purpose - the web reads the skeleton as existing network to thread
            # around - so at this moment `_net_segs` holds only the connector and the field spur.
            # Judging an arm against that says "reaches nothing" about an arm running down the middle
            # of the cluster, because the lanes that would justify it are three passes away. The
            # houses it was derived from are already on the map, and they are what an arm exists for.
            if len(arm) >= 2:
                arm = _trim_to_service(arm, [], [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])])
            if len(arm) >= 2 and polyline_len(arm) < _WEB_MIN_FT:
                arm = []
        arm = s.trim_off_marsh(arm)
        if len(arm) >= 2:
            if _arm_crossing_accidental(arm, raw_arms[ai], kept):
                continue  # pragma: no cover - no rolled map currently trips the drop; the decision logic is unit-tested via _arm_crossing_accidental
            kept.append((arm, raw_arms[ai]))
            s.lane(arm, width=5, clearance=LANE_CLEARANCE, worn=True)
    s.M["meta"]["lane_skeleton"] = plan.lane_skeleton
    return kept


def stage_web(s: Settlement, plan: SitePlan) -> None:
    _pass("cut")
    """STAGE 5b: the LANE WEB - the lanes that make every farmhouse reachable.

    WHY IT EXISTS. The record is decisive that a house in a nucleated cluster is reached by a way:
    "every house in the nucleated village is accessible via the interconnected system of narrow lanes
    and alleys" (research/homesteads.md). The skeleton alone does not deliver that - it is sized on
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
    houses = [h for h in s.M.get("houses", []) if h.get("role") != "headman" or True]
    if len(houses) < 2 or not plan.envelope:
        return  # pragma: no cover - every hamlet seats several houses
    # A DISPERSED HAMLET HAS NO INTERNAL LANE NETWORK AT ALL, and that is the form, not a shortfall.
    # Tonami's farmsteads stand in the middle of their own holdings; what joins them to the world is
    # the connector out to the road, which `stage_track` has already drawn, and what joins them to
    # each other is the field baulks they walk on. Drawing a web here would erase the one thing that
    # makes the form legible at a glance. The two access checks are conditioned on the form to
    # match - see `research/homesteads.md`, "Does a hamlet have to be NUCLEATED at all?".
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
    proj = [frame.project((float(h["x"]), float(h["y"]))) for h in houses]
    arcs = [a for a, _ in proj]
    stands = [d for _, d in proj]
    # THE SKELETON GOES IN FIRST, in this same house-fitted frame (feature 126). It used to be laid
    # two stages earlier, before any house existed; now it is derived from where they actually went.
    # It runs before the web cuts so the web sees it as existing network to thread around and join,
    # which is what `_net_segs` reads.
    _pass("skeleton")
    _lay_skeleton(s, plan, frame, arcs, stands)

    pad = 30.0  # a lane runs a little past the last steading it serves, not up to its wall

    # A WEB LANE SPANS THE HOUSES IT SERVES, AND NO MORE. Spanning the whole cluster's extent
    # instead leaves a tail running past the last steading into open ground at whichever end has no
    # houses at that cut - a tread that serves nobody, which is exactly what `lanes_reach_something`
    # exists to catch, and it was 13 of 24 cohort seeds. So each lane's extent is read off the
    # houses within reach of ITS OWN cut, not off the cluster as a whole.
    local = WEB_REACH_FT * 1.5

    def _extent(cuts_at: float, along: list[float], across: list[float]) -> tuple[float, float]:
        near_by = [v for v, w in zip(along, across, strict=False) if abs(w - cuts_at) <= local] or along
        return (min(near_by) - pad, max(near_by) + pad)

    lines: list[Poly] = []
    if plan.lane_web == "alleys":
        # A lateral spans the cluster's DEPTH at a cut along the margin. Straight in outline
        # coordinates, which is a gentle curve on the ground - it runs square out from the field
        # edge, which is the way a path between two plots actually leaves the paddy.
        for cut in web_cuts(arcs, WEB_REACH_FT, MIN_WEB_GAP):
            d0, d1 = _extent(cut, stands, arcs)
            lines.append([frame(cut, d0 + (d1 - d0) * i / 12.0) for i in range(13)])
    else:
        # A back lane spans the cluster's LENGTH at a cut in the standoff, sampled finely enough to
        # follow the margin's curve - a straight one parallels a curved field edge for a hundred feet
        # and then walks into the rice.
        cuts = web_cuts(stands, WEB_REACH_FT, MIN_WEB_GAP)
        for cut in cuts:
            a0, a1 = _extent(cut, arcs, stands)
            n = max(4, int((a1 - a0) / 40.0))
            lines.append([frame(a0 + (a1 - a0) * i / n, cut) for i in range(n + 1)])
        # ...AND THE CROSS-LINKS THAT MAKE IT A FRAMEWORK RATHER THAN A LADDER OF SEPARATE RUNGS.
        #
        # PARALLEL LANES NEVER MEET. That is arithmetic, not a bug to tune around, and it is why the
        # back-lane form came out of three settlement-reviews as two and three disconnected
        # components while the alleys form did not: an alley crosses the spine it branches from, a
        # back lane runs beside its neighbor forever. The source is not silent about this - the
        # planned form is "back lanes on each side of the main street WHICH, TOGETHER WITH THE MAIN
        # STREET ITSELF, PROVIDES A RECTANGULAR FRAMEWORK for the development of the village". A
        # framework is the parallels PLUS the ties. We were drawing only the parallels.
        #
        # The ties go where a lateral can physically pass - the gaps between steadings - which is the
        # same question `web_cuts` answers, asked along the other axis. They are spaced about three
        # bundle pitches apart rather than one, so the form still reads as a laid-out place with a
        # few cross-ways, not as the alleys form with extra steps.
        if cuts:
            lo_c, hi_c = min(cuts) - pad, max(cuts) + pad
            for tie in web_cuts(arcs, 3.0 * BUNDLE_PITCH, MIN_WEB_GAP):
                lines.append([frame(tie, lo_c + (hi_c - lo_c) * i / 8.0) for i in range(9)])

    crops = crop_polys(s)
    toe = s.toe_band() or None
    wet = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") != "defense" and m.get("poly")]
    hard = [list(plan.envelope), *crops, *([toe] if toe else []), *wet]
    fabric = _homestead_polys(s)
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
    # Ground cover is NOT fabric, for the same reason `_serve_stragglers` excludes it: a footpath may
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
    for run in _reachable_runs(cands, _net_segs(s)):
        _lay_web_lane(s, run, hard, walls, list(plan.watercourses) + drawn_water, belts=belts, houses=[(float(h["x"]), float(h["y"])) for h in houses])
    # A WEB LANE STOPS WHERE IT STOPS SERVING. Clipping ends an arm wherever the crop or a steading
    # happens to begin, which can leave a tail running on into bare grass - `lanes_reach_something`
    # is right to call that a tread that serves nobody. The engine already owns this trim; the web
    # simply has to ask for it after adding to the network.
    s.trim_lane_stubs()
    # STRAGGLERS COME AFTER THE TRIM, NEVER BEFORE IT. `trim_lane_stubs` drops any lane under its
    # 71 ft minimum, and a footpath from a door to the nearest way is about 65 ft by construction -
    # so run the other way round, every spur this pass drew was silently deleted again and the eight
    # unreached houses stayed exactly eight. A door path is short on purpose; it is not a stub.
    # ONE NETWORK FIRST, then the houses that it still does not reach. Order matters: a footpath
    # that joins an orphaned component is worth nothing while the component itself is an island.
    _pass("join-orphans")
    _join_orphan_ways(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # ...and close any break where one way was drawn as two. Before the stragglers: a house beside
    # the hole is served by the bridged street, and drawing it a footpath of its own first would be
    # curing the symptom.
    _pass("bridge-breaks")
    _bridge_collinear_breaks(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    _pass("straggler")
    _serve_stragglers(s, plan, hard, fabric, list(plan.watercourses) + drawn_water)
    _pass("touch")
    _touch_junctions(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # ...AND JOIN ORPHANS AGAIN, LAST. The first pass runs before the bridges and the footpaths, so
    # it can only see the lanes that exist then - on cohort seed 39 that was FOUR of the twelve the
    # map finishes with, and the eight added afterwards formed a second network of their own. Every
    # house on that map is within 86 ft of a lane and twelve of them still counted as unreached,
    # because the lane serving them was not on the network the connector is on. A repair pass that
    # runs before the things it repairs is not a repair pass.
    # ...and CLOSE BREAKS again before joining, for the same reason the join runs twice: the
    # footpath pass draws lanes, and a lane drawn after the bridge pass can leave a hole the bridge
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
    # laid before the houses, and running it here eats the footpaths the straggler pass just drew -
    # measured once at 43/48 -> 9/48.
    _final_houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]
    _W, _H = float(s.M["meta"].get("W", s.W)), float(s.M["meta"].get("H", s.H))

    def _inside(q: Pt) -> bool:
        return 0.0 <= q[0] <= _W and 0.0 <= q[1] <= _H

    _fabric_now = [poly for poly, _owner, _kind in _homestead_polys(s)]  # what the connector's end must stay clear of, as `_thread_the_fabric` left it
    for _i, _ln in enumerate(list(s.M.get("lanes", []))):
        # KEPT AND NOT REACHABLE TODAY, deliberately (feature 146). Every pass that can empty a lane
        # DELETES the record with the ink (feature 145's "the husk goes with the ink"), so no husk
        # survives to here - and injecting one to prove it fails earlier, in the orphan joiner, which
        # cannot handle a one-point way at all. As of feature 155 that is true of the knot-collapse
        # drop BELOW this line as well, which used to be the exception this comment pointed at. The
        # guard stays because a future reorder would hand one straight to `_ln["pts"][0]`, and because
        # three separate passes have now had to learn this rule one at a time.
        if len(_ln.get("pts") or []) < 2:  # pragma: no cover - see above
            continue
        _pts = [(float(x), float(y)) for x, y in _ln["pts"]]
        _others = [
            sg
            for _o in s.M.get("lanes", [])
            if _o is not _ln and len(_o.get("pts") or []) >= 2
            for sg in zip([(float(x), float(y)) for x, y in _o["pts"]], [(float(x), float(y)) for x, y in _o["pts"]][1:], strict=False)
        ]
        _kept = _pull_back_to_service(_pts, _others, _final_houses, _inside, _fabric_now) if _ln.get("connector") else _trim_to_service(_pts, _others, _final_houses, [list(plan.envelope)])
        if len(_kept) >= 2 and polyline_len(_kept) >= _WEB_MIN_FT and _kept != _pts:
            _ln["pts"] = [[round(x, 1), round(y, 1)] for x, y in _kept]
            # AND THE INK WITH IT - see `Settlement.reink_lane`. Shortening the record alone left the
            # drawn lane longer than the checked one, which is the quietest kind of wrong there is.
            s.reink_lane(_i)
    # LAST: read every lane as a shape and take out what feet would never wear (T32) - after the
    # trim, because the trim is the last pass that changes a record; then touch once more, because
    # cutting a hairpin's arm can move an end.
    _pass("smooth")
    _smooth_web(s, hard_built, walls, list(plan.watercourses) + drawn_water)
    # AND TOUCH AGAIN (T99 unlock, tripwire seed 37): the smoothing cuts knots and hairpins into stubs,
    # and a stub that ends 3-30 ft short of the run it left is exactly the gap _touch_junctions closes -
    # but that pass ran BEFORE the smoothing. A way the knot collapse emptied to one point is dropped first.
    _collapsed: list[int] = []
    for _i, _ln in enumerate(s.M.get("lanes", [])):
        _p = _ln.get("pts") or []
        if not _ln.get("connector") and (len(_p) < 2 or math.dist(_p[0], _p[-1]) < 1.0 and len(_p) == 2):
            _ln["pts"] = []
            s.reink_lane(_i)
            _collapsed.append(_i)
    # AND THE HUSK GOES WITH THE INK HERE TOO (settlement-review x2, feature 155). This was the third
    # and last place that emptied a record without removing it, and it was the one that survived the
    # other two being fixed: sawada still shipped a `role=bridge-breaks` record with no points, a
    # bridge the smoothing had collapsed. Removed back-to-front so the earlier indices stay valid.
    for _i in sorted(_collapsed, reverse=True):
        del s.M["lanes"][_i]
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
    _sweep_debris(s)  # a fragment the passes above whittled below the floor and left standing alone
    _keep_the_route_wide(s, hard_built, walls, list(plan.watercourses) + drawn_water)  # ...and a cart route may not neck to a footpath
    s.M["meta"]["lane_web"] = plan.lane_web


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
    resolution; neither decides anything, which is the project's standing rule for both."""
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
    if seed_box is None:  # pragma: no cover - a hamlet always has a skeleton by now
        reached = {0}
    frontier = list(reached)
    while frontier:
        i = frontier.pop()
        for j in range(len(thin)):
            if j not in reached and near(i, j):
                reached.add(j)
                frontier.append(j)
    return [runs[i] for i in sorted(reached)]
