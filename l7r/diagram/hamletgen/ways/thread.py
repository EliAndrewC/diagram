"""THE TRACK THREADED THROUGH THE FABRIC: `_thread_the_fabric` and its fallbacks, the spur's fold and the connector's room off a
grove band - lifted out of `track.py` at the 1,000-line bar (feature 405 T09, as `cluster_edge.py` was by feature 316); `track`
re-exports every name, so no importer changes. A test patches `_route` or `_out_of_bands` HERE, where `_thread_the_fabric` looks
them up.

Research: track plumbing - NONE"""

from __future__ import annotations

import math
from collections.abc import Sequence

from l7r.diagram.settlement import Settlement, edge_dist, point_in_poly, segments_cross
from l7r.diagram.settlement._geom import ring_offset
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import crop_polys

from ..consts import (
    FIELD_REACH_FT,
    FOOTPATH_FABRIC_GAP,
    GROVE_WORKING_ROOM_FT,
    TRACK_FABRIC_GAP,
    Poly,
    Pt,
)
from ..plan import SitePlan
from .clearance import _HAIRPIN_DEG, clip_to_clear
from .cluster_edge import _cluster_edge_toward, _cluster_gateway, gate_out_of_the_field  # noqa: F401 - re-exported: `gateway.py`, `ways/__init__.py` and the tests reach them here
from .fabric import _crosses_fabric, _homestead_polys
from .geom import _turn_deg, push_clear_of_fabric, push_out_of
from .route import _route

CONNECTOR_WIDTH = 6.0
"""The connector's tread, px: the cart track out to the wider world, drawn wider than the web's footpaths.

Research: connector width - research/questions/0081-village-lanes.drawing.html: 6 ft"""

CONNECTOR_BAND_GAP_FT = GROVE_WORKING_ROOM_FT + CONNECTOR_WIDTH / 2.0
"""How far the connector's line keeps off a farm's grove band (`connector_dry_exit`): 0036's working room off the trees and the
connector's half-width, 12.5 ft (feature 385 T98: it was a footpath's gap and the half-width, 7 ft at the 4 ft footpath, 10 at
7, never 0036's room). Dispersed farms' bands stand 32 ft apart (feature 291's measure), so the 25 ft it asks still passes.

Research: the connector off a grove band - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: some working room off the trees each side of the tread, 9.5 ft beyond the 6 ft connector's half-width"""


# how near the field a spur's end must stand to have reached it - `law.FIELD_REACH_FT`, which this layer cannot import (a test
# holds the two equal, 405 T22: one distance for the law and the placer)
SPUR_REACH_FT = FIELD_REACH_FT  # feature 417 T05: the one constant
"""Research: spur reaches the field - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: a lane end within 6 ft of the paddy's edge is drawn as joining it"""


def spur_cut_at_the_fold(pts: Poly, envelope: Poly) -> tuple[Poly, str | None]:
    """The field spur as it should be DRAWN, and the reason where it should not be.

    A spur threaded round the steadings can FOLD BACK ON ITSELF (settlement-review, feature 230 pass 11):
    the reference hamlet's ran 90 ft toward the field and straight back to within 14 px of where it began,
    the smoothing pass then rightly cut that hairpin away, and the hamlet's only path to its rice
    disappeared with no record of ever having been there. So the fold is cut here, before the map sees it.

    Keeping the outward arm regardless was tried first and was wrong: on that map the arm stopped 60.6 ft
    short of the field, with the marsh a path may not cross lying between, so it was a lane ending in open
    ground (`lanes_reach_something`). A folded spur is drawn only while its outward arm still REACHES the
    field; otherwise nothing is drawn and the caller records the returned reason, because a map with no
    path to its rice should say so rather than quietly have none.

    Lifted out of `stage_track` under the feature-146 doctrine: the decision is a question about a
    polyline and an envelope, and inside the stage it could only be reached by rolling a whole hamlet
    whose spur happens to fold.

    Research:
        spur fold cut - DEVIATION research/questions/0081-village-lanes.drawing.html: a folded field spur is cut at the fold whatever the returning leg's length, and drawn only while the arm reaches the field
        a folded spur's reach - GUESS research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the arm counts as reaching the field when it ends within `SPUR_REACH_FT` (6 ft, 0014's join) of it"""
    fold = next((k for k in range(1, len(pts) - 1) if _turn_deg(pts[k - 1], pts[k], pts[k + 1]) > _HAIRPIN_DEG), None)
    if fold is None:
        return pts, None
    cut = pts[: fold + 1]
    if edge_dist(cut[-1][0], cut[-1][1], envelope) <= SPUR_REACH_FT:
        return cut, None
    return cut, "folded back short of the field - the outward arm stops more than the join's reach from it"  # 405: the cause is not measured here


def _out_of_bands(p: Pt, bands: Sequence[Poly], toward: Pt) -> Pt:
    """`p` set outside the grove bands it stands in (feature 291): walked out toward `toward`, the run's other end, or put
    a footpath's gap past the nearest edge, whichever lands nearer `toward` - so a spur that began in a band leaves it by
    the side it was heading for rather than into the yard behind (seed 11). A point already clear comes back untouched.

    Research:
        a track's end out of the grove bands - UNRESEARCHED: set 8 ft (`FOOTPATH_FABRIC_GAP` + 1) clear of a grove band
        which side it leaves by - UNRESEARCHED: walked toward the run's other end, or pushed out the nearest edge, whichever lands nearer it"""
    if not any(point_in_poly(p[0], p[1], band) for band in bands):
        return p
    # walked in 2 px steps, asking containment as well as the gap: `push_clear_of_fabric` asks only the distance to the
    # ring, and a point at a band's middle is farther than a footpath's gap from every edge
    d = math.dist(p, toward)
    walked: Pt | None = None
    for k in range(int(d / 2.0)):
        q = (p[0] + (toward[0] - p[0]) * 2.0 * k / d, p[1] + (toward[1] - p[1]) * 2.0 * k / d)
        if not any(point_in_poly(q[0], q[1], band) or edge_dist(q[0], q[1], band) < FOOTPATH_FABRIC_GAP + 1.0 for band in bands):
            walked = q
            break
    near = p
    for band in bands:
        if point_in_poly(near[0], near[1], band):
            near = push_out_of(band, near, FOOTPATH_FABRIC_GAP + 1.0)
    return near if walked is None else min((walked, near), key=lambda q: math.dist(q, toward))


def _water_crossings(pts: Poly, lines: Sequence[tuple[Pt, Pt]]) -> int:
    """How many times the polyline crosses the water segments (feature 291's grove fallback weighs a route by it)."""
    return sum(1 for a, b in zip(pts, pts[1:], strict=False) for c, d in lines if segments_cross(a, b, c, d))


def _thread_the_fabric(s: Settlement, plan: SitePlan, run: Poly, gap: float = TRACK_FABRIC_GAP) -> Poly:
    """Route a track around the steadings that are already standing, and clip what will be drawn.

    THE OBLIGATION INVERTS WITH THE ORDER, and this is the half a reorder alone does not supply.
    While a lane was laid FIRST it was a no-build corridor and the HOUSES avoided it. Laid last,
    nothing stops the track being drawn straight through a farmstead - and nothing did: moving the
    connector and spur after the houses put a track through farmsteads on the reference hamlet - the retired checks
    `features_do_not_overlap`, `houses_clear_of_lanes` and `houses_off_corridors` all failed in one go.

    Feature 126 learned exactly this when it moved the skeleton (see `_lay_skeleton`), and the lesson
    generalizes: reordering the stages is not enough on its own, because every rule that pointed one
    way across that boundary has to be turned around to match.

    THE GAP IS THE WEB'S GAP (`TRACK_FABRIC_GAP` is `WEB_FABRIC_GAP`, 0246's 7 ft from a garden fence to a lane's
    middle). It was once wider, measured against a retired check (`houses_off_corridors`, a house center within 14 ft of
    the line); 0246 sets one gap for every lane. What still differs is the route: a connector or a spur runs PAST the
    settlement, routed round its steadings, not through the gaps between them as the web threads.
    A track that cannot be routed round is clipped, never drawn through a wall.

    ROUTE, then CLIP, and both are needed. `_route` threads the gap - a trodden way goes ROUND a wall
    rather than stopping at it - and the clip is the fallback for where no route exists, because the
    honest outcome there is a shortened track rather than a lane through somebody's house. The clip
    also catches the case the router cannot: a route is a PLAN, and a plan can start inside a wall
    when its endpoint came from a template.

    Research:
        track round the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: routed round, else clipped, else none
        gap off the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `gap` (`TRACK_FABRIC_GAP`, a lane's 7 ft from a garden fence) - the clip
            and the fabric test; the router walls the steadings as obstacles
        gap off a grove band - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: the grove fallback's route and clip keep
            `CONNECTOR_BAND_GAP_FT` (0036's working room past the connector's half-width, 12.5 ft) off the trees - the
            spur's too, half a foot more than its own 2.5 ft half-tread would need; the router's hard index holds the
            line about 13.5 ft off (`WEB_HARD_GAP` on the grown band), more room than the page's "about", never less
        detour swing - UNRESEARCHED: the midpoint swung 40, 80, 140 then 220 px out from the cluster
        never across a grove - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: routed round
            the bands, else only the part clear of them kept
        the track's route walled - research/questions/0081-village-lanes.drawing.html: never across row crops or the flooded paddy, and off wet ground (the field, crop, toe band and wet ground walled - a defense belt's reeds too, since no map draws a causeway: 405 T09)
        the track kept off drawn water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses water only at a crossing
        every fallback walled too - research/questions/0081-village-lanes.drawing.html: never across row crops or the flooded paddy, and off wet
            ground - the swing, the unrouted clip, the grove fallback's two routes and its far clip are each taken only where they cross no
            crop plot, no wet ground
            (a defense belt's reeds included), no toe band and no paddy (each field's outline, at 0 ft, 3 ft in from each end: a way may come up to the bund, and a
            spur ends on it), and the two routes wall the toe band and the wet ground (405 T09)
        an end walked clear along its own leg - GUESS: an end standing within the gap of the fabric is pushed out along the run's own first or
            last leg, so the track still leaves from where it was aimed
        the grove fallback's two routes in order - GUESS: each with the toe band and the wet ground walled, round the grown bands and the
            crop, then the bands alone (the spur's field end
            stands inside the crop's gap, so the crop is tested after the route, not walled in it); the first that crosses no band, nothing
            held (paddy, crop, toe band, wet ground), no steading at a footpath's gap and no more water than the run it replaces is taken. A third, with the water left out of its search, was dropped (405 T09): it
            crossed wherever it met the water, not at a crossing place
        water crossed only at a crossing place - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a
            grove fallback route is searched with the water lines, so it crosses at the fords; the swing, whose legs would meet the water
            anywhere, is taken only where it crosses none
        no more crossings than the run it replaces - GUESS: a grove fallback route is taken only where it crosses no more water than the
            run it replaces; 0035 does not say how many crossings a way may make (only that a crossing pays where it saves about 150 ft)
    """
    if len(run) < 2:
        return run
    # ...A GROVE BAND HELD AT 0036'S ROOM (feature 385 T109, D128): grown so every test below at `gap` keeps the line
    # `CONNECTOR_BAND_GAP_FT` (12.5 ft) off the trees, the other fabric at `gap` itself
    fabric = [list(ring_offset(poly, CONNECTOR_BAND_GAP_FT - gap, 0.0)[: len(poly)]) if kind == "groves" else poly for poly, _owner, kind in _homestead_polys(s)]
    if not fabric:
        return run
    crops = crop_polys(s)
    toe_now = s.toe_band() or None
    wet_now = marsh_ground(s.M)  # 405 T09: a defense belt's reeds too - no map draws a causeway (0081)
    drawn_water = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    obstacles = [list(plan.envelope), *crops, *fabric, *([toe_now] if toe_now else []), *wet_now]
    # 405 T09: what no fallback crosses - the flooded paddy as the lane law reads it (each field's outline, `law.span_walkable`),
    # not the field's whole frame: a spur's end stands on its bund
    paddy = [[(float(a), float(b)) for a, b in f["outline"]] for f in s.M.get("fields") or [] if f.get("outline")]
    held = [*paddy, *crops, *([toe_now] if toe_now else []), *wet_now]
    lines = list(plan.watercourses) + drawn_water
    # AN END STANDING IN THE FABRIC IS WALKED CLEAR ALONG THE RUN FIRST (feature 291). A farm's grove band is fabric now,
    # and the connector's gateway or the spur's start can land within the gap of one: the clip below then kept nothing,
    # and the fallback at the end of this function handed back the raw run across the band (the connector over a deep
    # north band on cohort seed 19, the spur over bands on 11 and 15). Walked along the run's own first and last legs, so
    # the track still leaves from where it was aimed.
    run = list(run)
    for i, j in ((0, 1), (-1, -2)):
        ux, uy = run[j][0] - run[i][0], run[j][1] - run[i][1]
        n = math.hypot(ux, uy)
        if n > 1e-9:
            run[i] = push_clear_of_fabric(run[i], (ux / n, uy / n), 0.0, fabric, gap)
    routed = _route(run[0], run[-1], obstacles, [], lines)
    out = clip_to_clear(routed if len(routed) >= 2 else run, fabric, gap)
    # ...AND THE UNROUTED CLIP WALLED AS THE ROUTE IS (405 T09, round 3): where the router found nothing, the run as it came is
    # clipped for the steadings alone, so it is taken only where it crosses nothing `held` and no water
    if len(out) >= 2 and not _crosses_fabric(out, fabric, gap) and (len(routed) >= 2 or _unrouted_clear(out, held, lines)):
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
            if len(cand) >= 2 and (_crosses_fabric(_inner(cand), held, 0.0) or _water_crossings(cand, lines)):
                continue  # 405 T09: walled as the first route is, and over no water - its legs would meet it anywhere
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
                return cand  # pragma: no cover - the swing ladder's accepted detour; no cohort cluster presents the obstacle it clears [174: KEPT, not deletable - it is the ladder's SUCCESS path, not a guard]
        # A DEAD END, MEASURED (feature 134 T50): a ladder that walked run[0] outward too, on the
        # theory that the offending leg was the first one and nothing above can move it. It changed
        # no map, because this function was never the one at fault - the fault was `_pull_back_to_service`
        # moving a connector's inner end AFTER this had cleared it (that pass went in feature 417 T19).
    kept = out if len(out) >= 2 else run  # the run the grove fallback weighs its crossings against
    # ...AND NEVER ACROSS A FARM'S GROVE (feature 291). Where neither the threaded route nor the swing clears every steading,
    # the clipped run - or the run as it came - went back across grove bands (the spur and the connector, cohort seeds 1, 5,
    # 11, 12, 14 and 15). A route that must clear only the grove bands and the crop, at a footpath's gap, is tried first; a
    # band is ground a track goes round. Each is taken only where it crosses no steading at all (feature 287's rule, below).
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    if bands and _crosses_fabric(kept, bands, 0.0):
        # an end standing IN a band (seed 11's spur began at a deep band's middle, where the walk along the run found no
        # clear ground) is set out of it first, by the side facing the run's other end: a route cannot start inside what it
        # avoids. Then two routes, the second looser: round the bands and the crop; round the bands alone (the spur's field end
        # stands on the bund, inside the crop's gap). A third, round the bands with the water left to the ford pass (seed 11's
        # spur already crossed the channel), was DROPPED by 405 T09: it crossed wherever it met the water, not at a crossing
        # place (0035) - where the two find nothing, the far clip or nothing is the answer
        ends = [_out_of_bands(run[0], bands, run[-1]), _out_of_bands(run[-1], bands, run[0])]
        # ...AT 0036'S ROOM OFF THE TREES (feature 385 T109, D128): the bands grown so a route and a clip at the footpath's gap keep
        # the line `CONNECTOR_BAND_GAP_FT` (12.5 ft) off them, the crops keeping their own gap in the same route
        roomy = [list(ring_offset(b, CONNECTOR_BAND_GAP_FT - FOOTPATH_FABRIC_GAP, 0.0)[: len(b)]) for b in bands]
        wet = [*([toe_now] if toe_now else []), *wet_now]  # 405 T09: every fallback walls the wet ground the first route does
        for hard, water in (([*roomy, *crops, *wet], lines), ([*roomy, *wet], lines)):
            around = _route(ends[0], ends[1], hard, [], water, gap=FOOTPATH_FABRIC_GAP)
            if (
                len(around) >= 2
                and not _crosses_fabric(around, bands, 0.0)
                and not _crosses_fabric(_inner(around), held, 0.0)
                and _water_crossings(around, lines) <= _water_crossings(kept, lines)
                and not _crosses_fabric(around, fabric, FOOTPATH_FABRIC_GAP)
            ):
                return around
        # ...and where the run starts inside a band there is no route from it: keep its FAR part, from the field or the
        # map's edge back to where it would first enter a band, and the web joins the near end (seed 1's spur, which began
        # inside its own farm's north band)
        far = clip_to_clear(kept[::-1], roomy, FOOTPATH_FABRIC_GAP)[::-1]
        if len(far) >= 2 and not _crosses_fabric(far, fabric, FOOTPATH_FABRIC_GAP) and _unrouted_clear(far, held, [] if kept is out and len(routed) >= 2 else lines):
            return far
    # AND NEVER THE OFFENDING RUN AT ALL (feature 287, ways W25, FR-005): this terminal handed back the clipped run whether or
    # not it still crossed the steadings, or the original when the clip left nothing - the fallback this docstring's own
    # rule forbids. It hands back nothing: the spur is then recorded as dropped, and the connector takes the dry exit
    # (`connector_through`).
    return []


def _unrouted_clear(run: Poly, held: Sequence[Poly], lines: Sequence[tuple[Pt, Pt]]) -> bool:
    """May a piece no route found be drawn (405 T09, round 3): it crosses nothing `held` (field, crop, toe band, wet ground) and,
    of `lines`, no water - each tested with its ends drawn in (`_inner`), so a piece ending on the bund or at a ford is not read
    as crossing it.

    Research:
        an unrouted piece over no water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way
            crosses water only at a crossing place, and a piece no route found was never brought to one
    """
    inner = _inner(run)
    return not _crosses_fabric(inner, held, 0.0) and not _water_crossings(inner, lines)


def _inner(run: Poly, d: float = 3.0) -> Poly:
    """`run` with each end drawn in `d` along its own leg (405 T09): a fallback's ends stand on the bund or at the field's edge,
    which a crossing test at 0 ft would read as crossing the field; a leg shorter than twice `d` is kept whole.

    Research: the ends drawn in - GUESS: 3 ft at each end, so a fallback whose end stands on the bund or at the field's edge is
    not read as crossing it; a crossing nearer an end than that goes untested"""
    out = list(run)
    for i, j in ((0, 1), (-1, -2)):
        n = math.dist(out[i], out[j])
        if n > 2 * d:
            out[i] = (out[i][0] + (out[j][0] - out[i][0]) * d / n, out[i][1] + (out[j][1] - out[i][1]) * d / n)
    return out
