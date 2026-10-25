"""The cluster's SKELETON and the web's cut lines: the arms laid after the houses, served, and the lines the web cuts along. Split from `ways/web.py` at the 1,000-line bar (feature 405 T57).

Research: web plumbing - NONE"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, seg_dist, skeleton_layout, web_cuts
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from ...cluster import _arm_crossing_accidental
from ...consts import (
    BUNDLE_PITCH,
    LANE_CLEARANCE,
    LANE_SKELETONS_BY_WATER,
    MIN_WEB_GAP,
    WATER_ALONG_FT,
    WATER_ALONG_SHARE,
    WEB_FABRIC_GAP,
    WEB_REACH_FT,
    Poly,
    Pt,
)
from ...plan import SitePlan, _roll
from ..checks import ford_crossing
from ..clearance import clip_to_clear
from ..fabric import _WEB_MIN_FT, _homestead_polys, _margin_frame, _net_segs
from ..geom import _trim_to_service, memo_ground, polyline_len, steading_footprints, worked_ground
from ..law_water import _brooks
from ..route import _route

SKELETON_ARM_WIDTH = 5.0

"""The skeleton arm's drawn width, a web lane's.

Research: skeleton arm width - research/questions/0081-village-lanes.drawing.html: a web arm 5 ft"""


def water_along_side(brooks: Sequence[Poly], to_map: Any, lat: float, dep: float) -> int | None:
    """The flank of the houses' extent a brook runs ALONG - -1 or +1 in the skeleton's local x - or None.

    A brook runs along a flank when it passes within `WATER_ALONG_FT` of that flank's line (local x = side * lat, y from
    -dep to dep, mapped by `to_map`) at `WATER_ALONG_SHARE` of nine points along it; of two such flanks, the nearer on
    average. A pure function of its inputs, so the lane shape's offer is tested with plain polylines.

    Research:
        water along the cluster - GUESS research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a brook within WATER_ALONG_FT of a flank over WATER_ALONG_SHARE of it"""
    if not brooks:
        return None
    best: tuple[float, int] | None = None
    for side in (-1, 1):
        pts = [to_map((side * lat, -dep + 2.0 * dep * i / 8.0)) for i in range(9)]
        d = [min(seg_dist(p[0], p[1], a, b) for brook in brooks for a, b in zip(brook, brook[1:], strict=False)) for p in pts]
        if sum(1 for x in d if x <= WATER_ALONG_FT) >= WATER_ALONG_SHARE * len(d) and (best is None or sum(d) / len(d) < best[0]):
            best = (sum(d) / len(d), side)
    return None if best is None else best[1]


def lane_skeleton_for(rolled: str, seed: int, side: int | None) -> str:
    """The lane shape the skeleton is laid in: the plan's roll among the four shapes, unless a brook runs along the
    cluster, where the roll is among five - the lane along the water among them (feature 374 wave 138, plan W138-1).

    Research:
        lane along the water - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the fifth shape offered where water runs along the cluster, the five at even odds"""
    if side is None:
        return rolled
    return str(_roll(seed, "lane_skeleton_by_water", LANE_SKELETONS_BY_WATER))


def oriented_skeleton(kind: str, side: int | None, lat: float, dep: float) -> dict[str, Any]:
    """`skeleton_layout`'s template in the skeleton's local frame, its lane along the water turned onto the flank the water
    runs along: the template lays it at local -x, so on the +x flank (`side` 1) it is mirrored (feature 374 wave 138).

    Research: lane along the water on its flank - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: a lane along the water, on the side the water runs"""
    layout = skeleton_layout(kind, 0.0, 0.0, lat, dep)
    if kind == "waterside" and side == 1:
        layout["lanes"] = [[(-x, y) for x, y in lane] for lane in layout["lanes"]]
    return layout


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
    Returns the kept arms, for the web to treat as existing network.

    Research:
        skeleton laid after the houses - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the farmhouses are placed first
        skeleton form - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: the rolled lane shape
        clear of crop, wet and water - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane never crosses row crops and keeps off wet ground
        skeleton arm over the brook - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: an inner arm crossing the brook takes the ford that makes its walk shortest, square to the reach
        skeleton arm off the ditches - research/questions/0055-where-a-field-meets-its-ditch-the-bank-the-bund-and-the-inlet-mizuguchi.html, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a path runs on the bank of every grade of field channel, and the bund is a path - a skeleton arm never crosses a ditch, a departure the code keeps until feature 417 T32; an inner arm clipped at the ditches and drawn channels, never crossing one
        spine along the houses - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the spine spans the houses' own extent - a lane follows the houses and runs only along those it serves
        spine centered on the houses - GUESS: on the houses' arc midpoint and mean stand
        no accidental crossing - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); an arm that would cross an arm already kept, by accident of the template, is not laid (`_arm_crossing_accidental`)
        skeleton margin off the crop - research/questions/0081-village-lanes.drawing.html: a lane may touch a plot's boundary - the arm clipped at its tread's edge (half its 5 ft width) off the field and the dry plots
        skeleton margin off the wet and the ditches - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); 20 px off the toe band and the marsh, 14 px off the drawn water (`clip_to_clear`'s line margin)
        routed round the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: nothing is built on a lane
        skeleton width - research/questions/0081-village-lanes.drawing.html: 5 ft
        skeleton drawn worn - research/questions/0081-village-lanes.html, research/questions/0081-village-lanes.drawing.html: narrow, packed earth, no centerline (`worn=True`)
        no skeleton under two houses - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); a cluster of fewer than two houses lays no skeleton lanes (`len(arcs) < 2`), there being no two houses to join
        skeleton arm's corridor - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's middle 7 ft clear of a garden fence; each arm registers `LANE_CLEARANCE`, 7 ft from its middle, a footprint held to it at its corners
        skeleton span floor - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A1, 2026-10-25); each half-extent floored at half a bundle pitch (50 ft), a pitch across; a run under 70 ft dropped by `clip_to_clear`, an arm under 30 ft (`_WEB_MIN_FT`) not laid
        skeleton arm trimmed back to the last point serving a house - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end reaching nothing pulled back to the last house it serves
        skeleton arm clipped WEB_FABRIC_GAP (7 ft) off the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's middle keeps at least 7 ft clear of a garden fence"""
    if len(arcs) < 2:
        return []
    arc0 = (min(arcs) + max(arcs)) / 2.0

    stand0 = sum(stands) / len(stands)
    # SIZED FROM THE HOUSES, not from `seat["lat"]`/`seat["dep"]`. Half-extents, because
    # `skeleton_layout` takes half-widths, and floored at half a bundle pitch (a pitch across) so a tight cluster still
    # gets a spine with somewhere to run.
    lat = max((max(arcs) - min(arcs)) / 2.0, BUNDLE_PITCH * 0.5)
    dep = max((max(stands) - min(stands)) / 2.0, BUNDLE_PITCH * 0.5)

    def _on_margin(p: Pt) -> Pt:
        # local +x runs along the band, local +y toward the field (so OUT of the frame is -y).
        q = frame(arc0 + p[0], stand0 - p[1])
        return (float(q[0]), float(q[1]))

    # the fifth shape, the lane along the water, is offered where a brook runs along a flank of the houses (W138-1); its
    # lane is laid on that flank (`skeleton_layout` draws it at local -x, mirrored for the +x flank)
    side = water_along_side(_brooks(s.M), _on_margin, lat, dep)
    kind = lane_skeleton_for(plan.lane_skeleton, plan.spec.seed, side)
    layout = oriented_skeleton(kind, side, lat, dep)

    raw_arms = [[_on_margin((float(p[0]), float(p[1]))) for p in lane_pts] for lane_pts in layout["lanes"]]
    crops = crop_polys(s)
    # what is already standing: houses, yards, gardens, sheds - the arm must go round all of it
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    toe_now = s.toe_band() or None
    wet_now = marsh_ground(s.M)  # 405 T121: a defense belt too - no map draws a causeway (0081)
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
        # ...OVER THE BROOK SQUARE AT A CROSSING PLACE (feature 328 wave 48, 0035's drawing page): an arm whose run would cross
        # the brook takes the ford that makes its walk shortest, landings square to the reach, as the field spur does - the
        # brook's line is gapped at the fords (`stream_segs`), so only a crossing elsewhere is clipped below
        _via = ford_crossing(raw_arms[ai][0], raw_arms[ai][-1], plan.brook or [], getattr(s, "brook_fords", ())) if len(raw_arms[ai]) >= 2 and len(plan.brook or []) >= 2 else []
        if _via:
            raw_arms[ai] = [raw_arms[ai][0], *_via, raw_arms[ai][-1]]
        # ...THE CROP AT THE TREAD'S EDGE, NOT 20 FT OFF IT (feature 328 wave 48, 0081: "a lane may touch a plot's boundary"):
        # the wet ground and the water keep the full margin
        arm = clip_to_clear(raw_arms[ai], [*([toe_now] if toe_now else []), *wet_now], 20.0, lines=list(plan.watercourses) + drawn_water)
        arm = clip_to_clear(arm, [list(plan.envelope), *crops], SKELETON_ARM_WIDTH / 2.0) if len(arm) >= 2 else arm
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
            # shortened arm, it is debris, and the houses it would have served are the settle's
            # business (their reserved corridors, `settle.settle_the_web`).
            #
            # SERVICE IS JUDGED AGAINST THE HOUSES, NOT AGAINST THE WAYS. `_lay_skeleton` runs BEFORE
            # the web cuts, on purpose - the web reads the skeleton as existing network to thread
            # around - so at this moment `_net_segs` holds only the connector and the field spur.
            # Judging an arm against that says "reaches nothing" about an arm running down the middle
            # of the cluster, because the lanes that would justify it are three passes away. The
            # houses it was derived from are already on the map, and they are what an arm exists for.
            arm = served_arm(s, arm)
        arm = s.trim_off_marsh(arm)
        if len(arm) >= 2:
            if _arm_crossing_accidental(arm, raw_arms[ai], kept):
                continue
            kept.append((arm, raw_arms[ai]))
            # ...laid only where the overlap matrix admits it (feature 287 M8): an arm across a byre or a house is cut there,
            # as the settle would cut it, and a piece left too short to be a way is not laid
            for piece in s.admitted_runs(arm, 5):
                if polyline_len(piece) >= _WEB_MIN_FT:
                    s.lane(piece, width=SKELETON_ARM_WIDTH, clearance=LANE_CLEARANCE, worn=True)
    s.M["meta"]["lane_skeleton"] = kind
    return kept


def served_arm(s: Settlement, arm: Poly) -> Poly:
    """A skeleton arm with its ends trimmed to service, or none where too little is left. The skeleton is drawn before anything
    serves the houses, so its ends are trimmed to the bar the gate asks of a lane end (feature 227: two of Inashiro's arms
    ended 81-97 ft from the nearest house), against the houses alone; an arm left under `_WEB_MIN_FT` is no arm. Lifted from
    `_lay_skeleton` (feature 308): the re-grown pool no longer leaves an arm that short, so it is tested on plain inputs.

    Research:
        skeleton arm trimmed to service - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: an end reaching nothing pulled back to the houses it serves; one reaching a way drawn so far or the bund stays
        shortest arm - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass A2, 2026-10-25); an arm under 30 ft (`_WEB_MIN_FT`) is not drawn"""
    if len(arm) >= 2:
        # ...JUDGED AGAINST WHAT IT REACHES (405 T63, D40): the ways drawn so far and the bund too, not the houses alone - 0246 pulls
        # back only an end that reaches nothing, and an arm ending on the connector, the spur or the bund was cut back to its last house
        ground = memo_ground(s, "worked", worked_ground) if s.M.get("fields") or s.M.get("dry_plots") else None
        houses = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses", [])]
        arm = _trim_to_service(arm, _net_segs(s), houses, ground=ground, steadings=steading_footprints(s.M))
    return [] if len(arm) >= 2 and polyline_len(arm) < _WEB_MIN_FT else arm


def _web_cut_lines(plan: SitePlan, frame: _margin_frame, arcs: list[float], stands: list[float]) -> list[Poly]:
    """The web's candidate lines, one per cut, in the house-fitted frame - the rolled lane form's own geometry (lifted out
    of `stage_web` by feature 370, the 100-statement cap; same order, same arithmetic).

    Research:
        lane form knob - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: side lanes or a back lane, rolled per map
        lane runs past its last steading - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: about 30 ft
        back lane ties - research/questions/0081-village-lanes.html: cross-ways frame the back lanes
        back lane tie spacing - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: cross lanes about one to every 300 ft - `web_cuts` at a reach of 1.5 x BUNDLE_PITCH (150 ft), so the ties stand up to about 300 ft apart
        web cut spacing - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: every house within WEB_REACH_FT (100 ft) of a cut, so the cuts stand up to about twice that apart
        a cut's room - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: MIN_WEB_GAP, 7 ft clear of a garden fence on each side and a 4 ft tread, within the page's 3 ft footpath to 5 ft spine
        a web lane's span - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane runs only along the houses it serves - those within WEB_REACH_FT (100 ft) of its cut, of every house but one reached across a neighbor's yard (owed no lane; `stage_web` leaves those out of the arcs and stands)
        the side lanes' reach - GUESS research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the page gives WEB_REACH_FT (100 ft) for back lanes; the side-lane form reuses it, the page silent there
        a tie's run past the back lanes - GUESS: a cross lane runs the back lanes' own 30 ft pad (`pad`) past the outermost of them; no page gives a distance
    """
    pad = 30.0  # a lane runs a little past the last steading it serves, not up to its wall; a tie runs as far past the outermost back lane

    # A WEB LANE SPANS THE HOUSES IT SERVES, AND NO MORE. Spanning the whole cluster's extent
    # instead leaves a tail running past the last steading into open ground at whichever end has no
    # houses at that cut - a tread that serves nobody, which is exactly what `lanes_reach_something`
    # exists to catch, and it was 13 of 24 cohort seeds. So each lane's extent is read off the
    # houses within reach of ITS OWN cut, not off the cluster as a whole.
    # NO WHOLE-CLUSTER FALLBACK (405 T11, D16): `web_cuts`, given these coordinates and this reach, puts every cut within reach
    # of the house that called for it; the `or along` (every house) never ran, and read as a lane serving none (DRIFTED, 385 T106).
    local = WEB_REACH_FT

    def _extent(cuts_at: float, along: list[float], across: list[float]) -> tuple[float, float]:
        near_by = [v for v, w in zip(along, across, strict=False) if abs(w - cuts_at) <= local]
        return (min(near_by) - pad, max(near_by) + pad)

    lines: list[Poly] = []
    if plan.lane_web == "alleys":
        # A lateral spans the cluster's DEPTH at a cut along the margin. Straight in outline
        # coordinates, which is a gentle curve on the ground - it runs square out from the field
        # edge, which is the way a path between two plots actually leaves the paddy.
        for cut in web_cuts(arcs, WEB_REACH_FT, MIN_WEB_GAP):
            d0, d1 = _extent(cut, stands, arcs)
            lines.append([frame(cut, d0 + (d1 - d0) * i / 12.0) for i in range(13)])
        return lines
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
    # same question `web_cuts` answers, asked along the other axis. They stand about one to every
    # 300 ft of the cluster's length (research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html):
    # a reach of 1.5 pitches each way, so cuts up to three pitches apart - the form still reads as
    # a laid-out place with a few cross-ways, not as the alleys form with extra steps.
    if cuts:
        lo_c, hi_c = min(cuts) - pad, max(cuts) + pad
        for tie in web_cuts(arcs, 1.5 * BUNDLE_PITCH, MIN_WEB_GAP):
            lines.append([frame(tie, lo_c + (hi_c - lo_c) * i / 8.0) for i in range(9)])
    return lines
