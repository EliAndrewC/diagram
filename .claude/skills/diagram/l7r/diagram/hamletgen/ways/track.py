"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index."""

import math
from collections.abc import Mapping, Sequence
from typing import cast

from l7r.diagram.settlement import Settlement, skeleton_layout
from l7r.diagram.settlement._geom import ring_offset
from l7r.diagram.sitegen.geom import centroid, crop_polys, pull_clear, unit

from ..cluster import _fork_spur, seat_cluster
from ..consts import (
    LANE_CLEARANCE,
    POLDER_ARCHETYPES,
    SPUR_SETBACK,
    TRACK_FABRIC_GAP,
    WIND_VECTORS,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .checks import drawn_water_segs, path_violations
from .clearance import clip_to_clear, route_around
from .fabric import _crosses_fabric, _fabric_hits, _homestead_polys
from .geom import polyline_len, push_clear_of_fabric, push_out_of
from .route import _route


def _cluster_gateway(s: Settlement, seat: Mapping[str, object], fallback: Pt) -> Pt:
    """Where a track leaves the settlement - measured from the PLACED houses, not the predicted band.

    FR-002, and feature 126's unfinished task T009. Until now the gateway came from
    `skeleton_layout(plan.lane_skeleton, 0, 0, seat["lat"], seat["dep"])` - a pure function of the
    rolled knob and the SEAT BAND, which is where the cluster was PREDICTED to go. The houses land
    where they land, and the two disagree; that mismatch is the recorded root of the
    `farmhouses_reach_a_way` defect that survived seventeen attempts.

    It also had a concrete cost the moment the track moved after the houses: a band-derived gateway
    can sit INSIDE the house cloud, and a track starting there has to leave through the settlement.
    One house on the reference hamlet ended up within 14 px of the connector's centerline - the
    threshold `houses_off_corridors` measures - and no amount of routing around the fabric fixed it,
    because the route's own start was in the middle of it.

    So: take the cloud's own extent along the seat axes and put the gateway on its DOWNSLOPE edge,
    clear of the last house. The fallback is the old band point, for the case where no house has been
    placed yet - which cannot happen in the shipped order, but a helper that assumes its caller is
    the failure mode this file has met repeatedly.
    """
    hs = s.M.get("houses") or []
    if not hs:
        return fallback
    ax, ay = cast(Pt, seat["along"])
    ox, oy = cast(Pt, seat["out"])
    xs = [float(h["x"]) for h in hs]
    ys = [float(h["y"]) for h in hs]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    # how far the cloud actually reaches, along each seat axis
    out_reach = max((x - cx) * ox + (y - cy) * oy for x, y in zip(xs, ys, strict=False))
    along_mid = sum((x - cx) * ax + (y - cy) * ay for x, y in zip(xs, ys, strict=False)) / len(xs)
    # THE CLOUD IS NOT ONLY THE HOUSES. Wells, byres, sheds and yards are seated in
    # `stage_appurtenances`, which runs BEFORE the track, and some of them stand outside the house
    # extent. A gateway measured from houses alone landed 3.6 px from a well on the reference hamlet
    # and the connector drew straight over it - `features_do_not_overlap`, wells x lanes.
    #
    # So walk outward until the gateway clears every standing thing by the track's own gap. Stepping
    # rather than solving: the fabric is an arbitrary set of polygons, the step is cheap, and a
    # bounded walk cannot fail to terminate the way a solve can.
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    return push_clear_of_fabric((cx + ax * along_mid, cy + ay * along_mid), (ox, oy), out_reach + TRACK_FABRIC_GAP + 8.0, fabric)


def _cluster_edge_toward(s: Settlement, target: Pt, fallback: Pt) -> Pt:
    """The point on the placed cluster's edge that FACES `target`.

    NOT `_cluster_gateway`, and confusing the two cost the reference map its field access. That helper
    pushes outward along `seat["out"]` - the downslope exit, which is where a track LEAVES for the
    wider world and by construction points AWAY from the field. Feature 128 re-originated both tracks
    from the placed houses and reused it for the spur as well, so the spur began on the far side of
    the settlement from its own destination, ran 104 degrees off the field bearing, and dead-ended in
    the shelter belt RECEDING from the paddy: 281 ft from the field envelope at its tip against 248 ft
    at its start. Found by `settlement-review`; the gate could not see it, because
    `lanes_reach_something` is satisfied by an end lying near a house and a way dying in the trees
    still fronts one.

    A spur goes TO somewhere. Its origin therefore belongs on the side of the cluster that faces the
    somewhere - measured from the placed houses like everything else in this feature, not from the
    seat band.
    """
    hs = s.M.get("houses") or []
    if not hs:
        return fallback
    xs = [float(h["x"]) for h in hs]
    ys = [float(h["y"]) for h in hs]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    ux, uy = target[0] - cx, target[1] - cy
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    reach = max(((x - cx) * ux + (y - cy) * uy for x, y in zip(xs, ys, strict=False)), default=0.0)
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    return push_clear_of_fabric((cx, cy), (ux, uy), reach + TRACK_FABRIC_GAP + 8.0, fabric)


def _thread_the_fabric(s: Settlement, plan: SitePlan, run: Poly, gap: float = TRACK_FABRIC_GAP) -> Poly:
    """Route a track around the steadings that are already standing, and clip what will be drawn.

    THE OBLIGATION INVERTS WITH THE ORDER, and this is the half a reorder alone does not supply.
    While a lane was laid FIRST it was a no-build corridor and the HOUSES avoided it. Laid last,
    nothing stops the track being drawn straight through a farmstead - and nothing did: moving the
    connector and spur after the houses turned the reference hamlet red on
    `features_do_not_overlap`, `houses_clear_of_lanes` and `houses_off_corridors` in one go.

    Feature 126 learned exactly this when it moved the skeleton (see `_lay_skeleton`), and the lesson
    generalizes: reordering the stages is not enough on its own, because every rule that pointed one
    way across that boundary has to be turned around to match.

    THE GAP IS NOT THE WEB'S GAP, and the difference is measured rather than chosen. The web threads
    BETWEEN plots and is barely more than the space between two walls, so `WEB_FABRIC_GAP` is 7 px.
    A track clipped at 7 px from a footprint still leaves the house CENTER inside the 14 px the gate
    measures (`houses_off_corridors` counts a hit at `seg_dist(center, lane) < 14`), and it did: 3 of
    15 houses on the reference hamlet. A connector or a spur also has no business hugging a wall - it
    runs past the settlement, not through its gaps.

    ROUTE, then CLIP, and both are needed. `_route` threads the gap - a trodden way goes ROUND a wall
    rather than stopping at it - and the clip is the fallback for where no route exists, because the
    honest outcome there is a shortened track rather than a lane through somebody's house. The clip
    also catches the case the router cannot: a route is a PLAN, and a plan can start inside a wall
    when its endpoint came from a template.
    """
    if len(run) < 2:
        return run
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    if not fabric:
        return run
    crops = crop_polys(s)
    toe_now = s.toe_band() or None
    wet_now = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") != "defense" and m.get("poly")]
    drawn_water = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    obstacles = [list(plan.envelope), *crops, *fabric, *([toe_now] if toe_now else []), *wet_now]
    lines = list(plan.watercourses) + drawn_water
    routed = _route(run[0], run[-1], obstacles, [], lines)
    out = clip_to_clear(routed if len(routed) >= 2 else run, fabric, gap)
    if len(out) >= 2 and not _crosses_fabric(out, fabric, gap):
        return out

    # THE FALLBACK MUST NOT BE THE OFFENDING RUN, which is what the first version did: when routing
    # and clipping both failed it returned the original path, silently re-drawing the lane straight
    # through the steadings it was supposed to avoid. That is worse than failing - the map ships
    # looking finished and the gate is what discovers it, if anything does.
    #
    # So take a wider berth instead. A track that cannot thread the cluster goes AROUND it, which is
    # what a real one does: the detour is the answer, not the straight line. Each attempt swings the
    # midpoint further out along the cluster's outward normal.
    if len(run) >= 2:
        mx, my = (run[0][0] + run[-1][0]) / 2, (run[0][1] + run[-1][1]) / 2
        cx = sum(float(h["x"]) for h in s.M.get("houses", [])) / max(1, len(s.M.get("houses", [])))
        cy = sum(float(h["y"]) for h in s.M.get("houses", [])) / max(1, len(s.M.get("houses", [])))
        ux, uy = mx - cx, my - cy
        n = math.hypot(ux, uy) or 1.0
        ux, uy = ux / n, uy / n
        for step in (40.0, 80.0, 140.0, 220.0):
            detour = [run[0], (mx + ux * step, my + uy * step), run[-1]]
            cand = clip_to_clear(detour, fabric, gap)
            # THE SWING THAT WORKS. Not reached by any test, and the structural reason is worth stating
            # rather than leaving for the next session to re-derive (feature 146, ~25 configurations
            # tried): the detour KEEPS `run[0]` and `run[-1]`, so whatever refused the straight run
            # usually refuses the detour on the same grounds. The two ways into this block are a clipped
            # run that still crosses - whose only cause `clip_to_clear` cannot see is `run[0]` itself
            # sitting in the fabric, which the detour inherits - and a clip that died under the 70 ft
            # floor, where the surviving stub is short because the obstacle is near `run[0]`, which the
            # detour's first leg then has to pass anyway. It is kept because the alternative below is to
            # hand back a run known to cross the steadings, and because a real cluster (not a fixture)
            # can present an obstacle the swing clears where the straight line does not.
            if len(cand) >= 2 and not _crosses_fabric(cand, fabric, gap):
                return cand  # pragma: no cover - see above
        # A DEAD END, MEASURED (feature 134 T50): a ladder that walked run[0] outward too, on the
        # theory that the offending leg was the first one and nothing above can move it. It changed
        # no map, because this function was never the one at fault - see `_pull_back_to_service`,
        # which moves a connector's inner end AFTER this has cleared it.
    return out if len(out) >= 2 else run


def stage_seat(s: Settlement, plan: SitePlan) -> None:
    """Decide WHERE the settlement sits. Draws nothing at all.

    THIS IS THE HALF THAT HAS TO RUN FIRST, and separating it is the whole of feature 128. The old
    `stage_ways` did two unrelated jobs in one pass: it SEATED the cluster - `seat_cluster` sets
    `plan.seat`, which `stage_homesteads` reads on its first lines - and it DREW the connector and
    the field spur. Because the seating is a hard dependency of the houses, the stage could not
    simply be moved after them, and feature 126 worked around that by moving only the skeleton. That
    is how the connector and spur were left reserving ground before a single house existed.

    Split, the dependency and the drawing go to opposite sides of the houses. Nothing here calls
    `s.lane`, and `tests/hamletgen/test_ways.py` asserts it: no lane and no corridor may exist when
    this returns.
    """
    drain = None
    for ditch in s.M.get("field_ditches", []):
        if ditch.get("role") == "drain" and len(ditch["poly"]) >= 2:
            drain = [(float(v[0]), float(v[1])) for v in ditch["poly"]]
            break
    # EVERY watercourse on the map, not just the field's own ditches. The ways are routed to meet
    # water squarely and to keep their decks off the crop, and that is only as good as the list they
    # are handed: the STREAMS - the feed brook coming down to the intake, the drain brook leaving
    # the frame - are drawn in the two stages before this one and were missing from it, so a track
    # could cross one at a slant and `bridges_span_their_water` would fail on a deck too short for
    # the water beneath it.
    # ...and the DRAWN lines, not only the recorded ones. `field_channel` fillets its polyline before
    # drawing it (`fillet_polyline`, so a mitred corner does not spike), and it is the drawn line a
    # bridge gets placed on - so routing against the recorded one can send a way across a ditch at a
    # slant the router never saw. Same rule as the connector's own bow: measure what is drawn.
    plan.watercourses = [
        ((float(a[0]), float(a[1])), (float(b[0]), float(b[1])))
        for rec in list(s.M.get("field_ditches", [])) + list(s.M.get("channels", [])) + list(s.M.get("streams", []))
        for a, b in zip(rec["poly"], rec["poly"][1:], strict=False)
    ] + [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    seat = seat_cluster(
        plan, dry_plots=crop_polys(s), drain=drain, toe=s.toe_band() or None, wet=[[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") == "pond_fringe"]
    )  # the reservoir's reed fringe: not building ground (feature 150 T50)
    plan.seat = seat
    # THE SITE'S BACK IS THE WINDWARD SIDE, and where the two disagree the site wins.
    #
    # The wind is derived from the slope (cold air drains off the high ground) and the cluster is
    # seated partly by it - back to the hill, face to the water. But the seat has hard constraints
    # the wind does not: not below the drain, not on the hem, not off the canvas. When those rule
    # out every wind-facing margin, the settlement ends up with its back to the FIELD, and a belt
    # placed on the declared windward side is then planted in the rice - where `village_grove`
    # throws away almost every clump and the map fails both windbreak checks with a grove of eight
    # trees. Re-reading the exposure off the seat is the self-consistent answer and the true one: a
    # settlement's sheltered side is the side it actually turns its back to, and this map is
    # declaring which quarter that is. A GM who knows the region's real prevailing wind pins it on
    # the spec, and then the seat search is what bends instead.
    if plan.wind[0] * seat["out"][0] + plan.wind[1] * seat["out"][1] < 0.34:  # more than ~70 deg apart
        plan.windward = min(WIND_VECTORS, key=lambda q: -(WIND_VECTORS[q][0] * seat["out"][0] + WIND_VECTORS[q][1] * seat["out"][1]))
        s.M["meta"]["windward"] = plan.windward
    s.M["meta"]["lane_skeleton"] = plan.lane_skeleton
    # THE SIDE THE HOUSES STAND ON, told to the settlement (feature 140): every field test from here on measures
    # the outline's few chords facing this seat (`rolling/fit.py::_field_chains`), never the whole outline.
    if plan.seat:
        s.field_face = (float(plan.seat["cx"]), float(plan.seat["cy"]))


def stage_track(s: Settlement, plan: SitePlan) -> None:
    """The connector out to the road and the spur to the field - drawn AFTER the houses.

    THE GM, stating the whole feature (2026-08-24): *"We are reordering the procedural layout of the
    hamlet generation so that farmhouses are rendered after the fields and water, but before any
    village lanes. That is what the feature is. Full stop."*

    ANY. There is no exogenous class and no connector exception. A road can predate a settlement in
    the world, but this generator does not import one - it DRAWS one, and a lane drawn before the
    houses registers a no-build corridor (`settlement/water_ways.py:514`) that `_fits` then refuses
    seats against (`settlement/houses.py:309-311`). It takes ground the houses cannot have, which is
    exactly what the GM reported: *"the lanes being there was the thing that was making it difficult
    to lay out the farmhouses."*

    That reasoning - ground reservation - is the one that carries, and it is deliberately NOT an
    argument about provenance. An earlier draft justified moving the spur by claiming a field path
    cannot predate the households who walk it; the fidelity review showed that is not universally
    true (land assarted from an older settlement, a bund track along an existing paddy, a hamlet
    founded against a through-path) and that resting on provenance produced a false asymmetry between
    the spur and the connector. Ground reservation is true of every lane whatever it represents.

    **Both branches.** The polder path returns early with its own connector; a fix applied only to
    the valley path would leave polder hamlets reserving ground, and the reference hamlet is a valley
    map so it would not notice.
    """
    seat = plan.seat
    ax, ay = seat["along"]
    ox, oy = seat["out"]
    cx, cy = seat["cx"], seat["cy"]

    crops = crop_polys(s)
    # The steadings, read ONCE for the whole stage: the bearing sweep ranks against them and
    # `_thread_the_fabric` re-reads them for the clip. They cannot change during this stage -
    # nothing here draws a homestead - so a second walk would only be a second chance to disagree.
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]

    def to_screen(p: Pt) -> Pt:
        """Seat frame (along the margin, away from the field) -> screen."""
        return (cx + ax * p[0] + ox * p[1], cy + ay * p[0] + oy * p[1])

    toe_now = s.toe_band() or None
    # THE SKELETON IS NO LONGER LAID HERE (feature 126). Its arms are drawn in `stage_lanes`,
    # after the houses exist, and are fitted to where the houses actually went. What survives in
    # this stage is the LAYOUT OBJECT ALONE, and only for its `gateway` - the downslope exit the
    # connector starts from. `skeleton_layout` is a pure function of (rolled knob, seat band), so
    # computing the gateway needs no houses and the connector's origin is unchanged by the move.
    #
    # THE RECORDED DEAD END ABOVE DOES NOT APPLY ANY MORE, and a reader who finds it in the git
    # history should know why. Feature 123 tried sizing the skeleton over the ground the houses
    # take and reverted it: longer arms offered the placer more frontage seats far from the
    # middle, and the cluster stretched to meet them. That was a FEEDBACK loop, and it existed
    # only because the skeleton was laid BEFORE the houses and its arms generated seats. Laid
    # afterwards there are no seats to generate, so the loop is severed rather than re-entered.
    layout = skeleton_layout(plan.lane_skeleton, 0.0, 0.0, seat["lat"], seat["dep"])
    # The spur no longer forks into the skeleton's arms, because they do not exist yet. It forks
    # into nothing and simply runs to the field; `stage_lanes` joins the network up afterwards.
    _kept_arms: list[tuple[Poly, Poly]] = []

    # the SPUR to the field: from the middle of the cluster to the nearest envelope point THE TRACK
    # CAN ACTUALLY REACH. Nearest-by-distance alone routes the path straight over the dry hem when
    # the hem lies between cluster and paddy - and a trodden path crosses no row crops
    # (`lanes_clear_of_dry_plots`; a real farm track runs on the baulk between plots, or round the
    # hem). So candidates are ordered by distance and the first one whose straight run is clear of
    # every hem plot wins; if none is, the nearest is used and the gate says so rather than the map
    # quietly shipping a lane through the barley.
    # A POLDER HAS NO FIELD SPUR. The valley hamlet's spur is a path from the cluster to the paddy's
    # edge, and it is meaningful there because the crop's margin is walkable ground. A polder is
    # ringed by its perimeter DIKE and, just inside that, the ring canal - so the way in is over the
    # dike at its sluice gaps, and a spur to the crop edge is a path to a bank. Drawn anyway it was
    # worse than pointless: every near target crosses the ring canal, so `path_violations` scored the
    # nearby vertices badly and the least-bad candidate ran from the cluster straight ACROSS the
    # block to a vertex on the far side (`fields_clear_of_road` on 4 of 12 cardinal polders).
    if plan.field_archetype in POLDER_ARCHETYPES:  # both polder archetypes (feature 150)
        s.M["meta"]["lane_skeleton"] = plan.lane_skeleton
        toe = s.toe_band()
        drawn_wet = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") != "defense" and m.get("poly")]
        _band_gate = to_screen((float(layout["gateway"][0]), float(layout["gateway"][1])))
        gate_pt = push_out_of(plan.envelope, _cluster_gateway(s, seat, _band_gate), SPUR_SETBACK)
        track = connector_track(plan, gate_pt, avoid=[list(plan.envelope), *crops], wet=([toe] if toe else []) + drawn_wet, waters=drawn_water_segs(s), fabric=fabric)
        s.lane(_thread_the_fabric(s, plan, route_around(plan.envelope, track, SPUR_SETBACK)), width=6, clearance=LANE_CLEARANCE, worn=True, connector=True)
        return

    # THE SPUR STARTS AT THE CLUSTER'S EDGE, NOT AT THE BAND'S CENTER (FR-002, feature 128).
    #
    # `to_screen((0, 0))` is the middle of the PREDICTED seat band, and with the spur now drawn after
    # the houses that point sits inside the house cloud - so the path began among the steadings and
    # had to leave through them. One house on the reference hamlet finished within 14 px of the
    # spur's centerline, which is exactly what `houses_off_corridors` counts, and no amount of
    # routing around the fabric could fix it because the route's own START was in the middle of what
    # it was supposed to avoid.
    #
    # `_cluster_gateway` measures the placed cloud's reach along the seat axes and puts the origin
    # just outside it. The band point is kept only as the no-houses fallback.
    _band_start = to_screen((0.0, 0.0))
    cen = centroid(plan.envelope)
    brook_segs = [(plan.sink_brook[i], plan.sink_brook[i + 1]) for i in range(len(plan.sink_brook) - 1)]

    def spur_path(target: Pt) -> Poly:
        # THE TIP STOPS OUTSIDE THE FIELD, measured on the LOCAL edge normal (GM 2026-08-12:
        # "Inashiro has village paths overlapping with rice paddies"). It used to pull back 8 px
        # along the SEAT's outward normal, which is one fixed direction for the whole map - so at a
        # target vertex whose own outline runs a different way, the pull-back was sideways and the
        # tip finished 28 px INSIDE the envelope, a track ending in the standing water. The normal
        # is taken from the two outline edges meeting at the target and oriented away from the
        # field's centroid, and the set-back covers the lane's own half-width plus the tolerance
        # `fields_clear_of_road` allows. A path stops AT the bund; the last few feet are the baulk.
        env = plan.envelope
        k = min(range(len(env)), key=lambda i2: math.hypot(env[i2][0] - target[0], env[i2][1] - target[1]))
        nx, ny = 0.0, 0.0
        for a2, b2 in ((env[k - 1], env[k]), (env[k], env[(k + 1) % len(env)])):
            ex, ey = unit(-(b2[1] - a2[1]), b2[0] - a2[0])
            nx, ny = nx + ex, ny + ey
        nx, ny = unit(nx, ny)
        if nx * (target[0] - cen[0]) + ny * (target[1] - cen[1]) < 0:
            nx, ny = -nx, -ny
        edge = (target[0] + nx * SPUR_SETBACK, target[1] + ny * SPUR_SETBACK)
        # THE WHOLE PATH IS IN ONE FRAME, which the first cut of feature 128 broke. It moved the
        # START to the placed houses and left the bow point on the PREDICTED band's `cx, cy, ax, ay`,
        # so the two ends of the same three-point path described different settlements. Combined with
        # a start taken from the outward gateway - the direction a track LEAVES by, which faces away
        # from the field - the spur ran 104 degrees off its own target and died in the windbreak.
        #
        # Now: the origin faces THIS target, and the bow is the midpoint of the actual run with a
        # small lateral swing so the path reads as walked rather than ruled.
        _s = _cluster_edge_toward(s, target, _band_start)
        _mx, _my = (_s[0] + edge[0]) / 2, (_s[1] + edge[1]) / 2
        return [_s, (_mx + ax * 14, _my + ay * 14), edge]

    # ...and again the candidate is the DRAWN path, bow and all - see `path_is_clear`.
    spur = min(
        (spur_path(q) for q in sorted(plan.envelope, key=lambda v: math.hypot(v[0] - cx, v[1] - cy))),
        key=lambda p: (path_violations(p, crops, plan.sink_pond, brook_segs, plan.watercourses), polyline_len(p)),
    )
    _spur_pts = s.trim_off_marsh(clip_to_clear(spur, [*crops, *([toe_now] if toe_now else [])], 12.0))
    _spur_pts = _fork_spur(_spur_pts, _kept_arms)
    if len(_spur_pts) >= 2 and sum(math.dist(_spur_pts[k], _spur_pts[k + 1]) for k in range(len(_spur_pts) - 1)) > 20.0:
        s.lane(_thread_the_fabric(s, plan, _spur_pts), width=5, clearance=LANE_CLEARANCE, worn=True)

    # the CONNECTOR, out to the frame
    # ...and the gate the connector starts FROM must itself be out of the crop. The skeleton's
    # gateway is a point in the seat frame, so on a cluster that sits against a concave stretch of
    # the fan it can land INSIDE the field envelope - and the connector then starts in the rice and
    # crosses the outline twice on its way out (Inashiro, GM 2026-08-12).
    _band_gate = to_screen((float(layout["gateway"][0]), float(layout["gateway"][1])))
    gate = push_out_of(plan.envelope, _cluster_gateway(s, seat, _band_gate), SPUR_SETBACK)
    # THE TRACK LEAVES CLEAR OF THE WET TOE (GM 2026-08-12: "there's supposed to be a rule that
    # paths don't pass through marshland"). The marsh is not drawn until `stage_hinterland`, long
    # after this, so the router asks the ENGINE where it will be - `toe_band` is the same derivation
    # `hinterland()` lays the reeds on, factored out precisely so the two cannot disagree. With the
    # band in the obstacle list every straight-downslope bearing scores as a violation and the sweep
    # settles on a contour-following one, which is what a real valley track does anyway: roads run
    # ALONG the valley, they do not dive into the swamp at its foot.
    # ...and the wet ground is EVERY marsh, not just the toe band: the pond's reed fringe is drawn
    # back in `stage_sink`, before this, and a cohort sweep found ways ending in it on two maps.
    toe = s.toe_band()
    drawn_wet = [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes", []) if m.get("role") != "defense" and m.get("poly")]
    track = connector_track(plan, gate, avoid=[list(plan.envelope), *crops], wet=([toe] if toe else []) + drawn_wet, waters=drawn_water_segs(s), fabric=fabric)
    s.lane(_thread_the_fabric(s, plan, route_around(plan.envelope, track, SPUR_SETBACK)), width=6, clearance=LANE_CLEARANCE, worn=True, connector=True)


def connector_track(plan: SitePlan, start: Pt, avoid: Sequence[Poly] = (), reach: float = 4000.0, wet: Sequence[Poly] = (), waters: Sequence[tuple[Pt, Pt]] = (), fabric: Sequence[Poly] = ()) -> Poly:
    """The track from the settlement's gateway to the map edge, steered clear of the crop.

    Bearings are tried outward from "away from the field, leaning downslope" - the direction a real
    track leaves by, since the wider world is downstream and the paddy is not walkable - and the
    first that reaches the frame without crossing the field envelope wins. Sweeping alternate sides
    at growing angles keeps the chosen bearing as close to the ideal as the geometry allows instead
    of jumping to whatever happens to be clear.

    The track is drawn PAST the canvas edge, not up to it: the gate wants an endpoint at the frame,
    and the crop is set later from the hard features, so a track that overshoots is trimmed by the
    viewBox while one that stops short reads as a dead end."""
    dx, dy = plan.fall
    ox, oy = plan.seat["out"]
    base = math.degrees(math.atan2(0.55 * oy + 0.85 * dy, 0.55 * ox + 0.85 * dx))
    # ...and clear of the POND. A track skirting the tameike ends up crossing the short drainage
    # ditch between field and pond at a very shallow angle, and an oblique crossing needs a much
    # longer deck than a square one - `bridges_span_their_water` caught exactly that, with an
    # abutment standing in the water. Steering around the pond removes the crossing instead of
    # widening the bridge, which is also what a real track does: you ford or bridge a ditch where it
    # is narrow and square, not where it fans into a reservoir.
    pond = plan.sink_pond
    brook = [(plan.sink_brook[i], plan.sink_brook[i + 1]) for i in range(len(plan.sink_brook) - 1)]
    # The planned net PLUS whatever water is actually drawn - the caller passes the streams, which
    # `plan.watercourses` does not carry and which nothing here used to test against.
    waters = [*plan.watercourses, *waters]
    # A FINE sweep, nearest bearing first. Sixteen coarse tries were enough when the only obstacle
    # was the field; with the pond and the drain brook added, a whole quadrant can be closed and a
    # coarse sweep steps straight over the gap between them - which drops through to the fallback,
    # and the fallback ignores every constraint. Forty bearings is a few hundred point tests.
    # The gateway can itself stand on hem ground when the cluster's back is partly hemmed, and a
    # start point inside a crop makes EVERY bearing fail - which is how the fallback below came to
    # fire at all. Step it clear first.
    start = pull_clear(start, (plan.seat["cx"], plan.seat["cy"]), avoid or [plan.envelope], 12.0)

    # A WET POLY IS SCORED WITH THE LANE'S WIDTH ON, not as a bare region (Cohort-41 2026-08-16).
    # `roads_clear_of_marsh` measures every marsh VERTEX against the way's CENTERLINE with the
    # way's half-width + 2 px of pad - so a track whose centerline clears the toe band's corner by
    # 4.5 px routes clean here and fails there. Inflating the polygon by 8 px (half the 6 px
    # connector lane + the gate's 2 px pad + 3 px slack) makes the router score the tread the gate
    # will measure, the same probe-measures-what-the-check-measures rule the bow comment below
    # states for the crop.
    # ...AND GROWN ALONG ITS NORMALS, NOT SCALED ABOUT ITS CENTROID (feature 145, Sawada after the field
    # moved). The toe band is a contour strip 2,900 px long and ~200 wide; pushing each vertex 8 px AWAY
    # FROM THE CENTROID moves the vertices near the band's middle almost entirely along its length and
    # its far corners not at all in the direction that matters, so the connector routed "clean" past a
    # corner it then grazed by 4.5 px. `ring_offset` (feature 140) pushes every vertex 8 px along the
    # ring's own outward normal; its first n vertices are that outer ring.
    def _inflated(w: Poly) -> Poly:
        return list(ring_offset(w, 8.0, 0.0)[: len(w)])

    wet_grown = [_inflated(w) for w in wet if len(w) >= 3]
    best: tuple[tuple[int, int, int], Poly] | None = None
    for swing in sorted((9.0 * k for k in range(-20, 21)), key=abs):
        theta = math.radians(base + swing)
        # THE CANDIDATE IS THE PATH THAT WILL BE DRAWN, not the straight line to its endpoint. A
        # foot track wanders, so the drawn polyline bows ~40 px either side of the bearing - and
        # testing the CHORD while drawing the BOW is how a track ended up crossing a hem plot and a
        # drainage ditch on maps whose straight line cleared both. (The skill's dev notes state the
        # rule in the label-probe case: a probe must measure what the check will measure. It applies
        # to routing just as squarely.)
        px, py = -math.sin(theta), math.cos(theta)
        path: Poly = [
            start,
            (start[0] + math.cos(theta) * reach * 0.18 + px * 34, start[1] + math.sin(theta) * reach * 0.18 + py * 34),
            (start[0] + math.cos(theta) * reach * 0.44 - px * 46, start[1] + math.sin(theta) * reach * 0.44 - py * 46),
            (start[0] + math.cos(theta) * reach, start[1] + math.sin(theta) * reach),
        ]
        # WET GROUND OUTRANKS EVERYTHING ELSE (GM 2026-08-12). The toe marsh is a contour band
        # spanning the whole canvas below the crop, so on a map whose cluster sits in a pocket of
        # the fan NO bearing is clean of both - and a single violation count lets one crop clip
        # outweigh a thousand feet of swamp. Scoring them separately, wet first, makes the sweep
        # leave along the contour and exit the frame ABOVE the marsh, which is what a real valley
        # road does; whatever crop it then clips is bent round afterwards by `route_around`, which
        # the marsh has no equivalent of because a track through a marsh cannot be nudged dry.
        soaked = sum(path_violations(path, [w], None, ()) for w in wet_grown)  # the WET POLYGON only - pond and brook are scored once, below
        # THE STEADINGS ARE SCORED TOO, and they have to be scored HERE (feature 128). With the
        # houses standing before any track is drawn, the sweep's ideal bearing can point straight back
        # through the cluster - and nothing downstream can rescue that. `_thread_the_fabric` routes
        # and clips, but `_route` gives up on a span this long (its lattice exceeds the cell cap and
        # it returns [] for any connector reaching the frame), and a clip can only SHORTEN a run, so a
        # through-road laid across the hamlet stays laid across the hamlet.
        #
        # Measured on Mizuguchi: the gateway sat at the cluster's west face against the map edge, every
        # westward bearing was blocked, and the sweep swung a full 180 deg and left EAST - back over
        # the settlement, 0.2 px from a garden and 14.6 px from a farmhouse.
        #
        # It ranks between wet and crop, and that ordering is a judgment about what a track can and
        # cannot be nudged out of afterwards. A marsh cannot (a road through a swamp is not a road), so
        # wet still outranks everything. A crop clip CAN - `route_around` bends the drawn track round
        # the hem, which is what that call exists for. A farmstead cannot be nudged either, and it is
        # somebody's house, so it sits directly under wet and above the crop.
        steaded = _fabric_hits(path, fabric, TRACK_FABRIC_GAP)
        # PRUNE BEFORE THE EXPENSIVE HALF. `violations` tests every crop polygon on the map and is by
        # far the costliest term here; `soaked` and `steaded` are cheap by comparison. The rank is
        # lexicographic, so a candidate already behind on the first two terms cannot win no matter
        # what the third says - which means it never needs computing.
        #
        # This is not an optimization looking for a problem. Adding the fabric term COST time by
        # itself: a bearing that used to score a clean zero and return on the first try now often
        # scores a steading, so the sweep runs all 41 candidates instead of stopping at one, and the
        # measured bill was +25% on the reference seed. Pruning gives it back without changing a
        # single verdict - the skipped candidates are exactly the ones whose full tuple is already
        # known to be larger.
        if best is not None and (soaked, steaded) > best[0][:2]:
            continue
        violations = path_violations(path, avoid or [plan.envelope], pond, brook, waters)
        if soaked == 0 and steaded == 0 and violations == 0:
            return path
        if best is None or (soaked, steaded, violations) < best[0]:
            best = ((soaked, steaded, violations), path)
    # NO CLEAN BEARING: take the LEAST-BAD one rather than a fixed escape route.
    #
    # This used to return `start` plus a ray straight away from the field, and that fallback is what
    # actually shipped the defect: it consulted nothing, so on any map where the sweep came up empty
    # the connector was drawn through the hem and across the drainage ditch, failing three checks at
    # once. A fallback that ignores the constraints is worse than no fallback, because it looks like
    # a decision. Scoring every candidate and keeping the best means a hard map degrades by one
    # crossing instead of by everything.
    assert best is not None
    return best[1]
