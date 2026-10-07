"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: track plumbing - NONE"""

from __future__ import annotations

import contextlib
import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.overlap.registry import forbidden_segment
from l7r.diagram.settlement import Settlement, edge_dist, point_in_poly, segments_cross, skeleton_layout
from l7r.diagram.settlement._geom import ring_offset
from l7r.diagram.settlement.land.wet import marsh_ground
from l7r.diagram.sitegen.geom import centroid, crop_polys, pull_clear, unit

from ..cluster import _fork_spur, seat_cluster
from ..consts import (
    BROOK_CROSSING_COST_FT,
    FOOTPATH_FABRIC_GAP,
    FORD_BEND_DEG,
    FORD_HALF,
    FORD_SPACING,
    LANE_CLEARANCE,
    POLDER_ARCHETYPES,
    SPUR_SETBACK,
    TRACK_FABRIC_GAP,
    Poly,
    Pt,
)
from ..plan import SitePlan
from . import law
from .bund import RunOnBlocks, tip_onto_the_bund
from .checks import PathChecker, brook_fords, drawn_water_segs, ford_crossing, gap_segments, stream_segs
from .clearance import _HAIRPIN_DEG, clip_to_clear, route_around
from .cluster_edge import _cluster_edge_toward, _cluster_gateway, gate_out_of_the_field  # noqa: F401 - re-exported: `gateway.py`, `ways/__init__.py` and the tests reach them here
from .dry_exit import EXIT_CELL_FT, GROVE_EXIT_CELL_FT, clear_of_bands, dry_exit
from .fabric import _crosses_fabric, _fabric_hits, _homestead_polys
from .geom import _turn_deg, memo_ground, polyline_len, push_clear_of_fabric, push_out_of, worked_ground
from .route import _route, set_crossing

# how near the field a spur's end must stand to have reached it - `lanes_reach_something`'s own 60 ft for a lane end
SPUR_REACH_FT = 60.0
"""Research: spur reaches the field - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: within 60 ft of its edge"""
SPUR_WIDTH = 5  # the field spur's tread, a worn path: the web's ways are 3, the connector 6
"""Research: field spur width - research/questions/0081-village-lanes.drawing.html: 5 ft"""


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
        a folded spur's reach - UNRESEARCHED: the arm counts as reaching the field when it ends within `SPUR_REACH_FT` (60 ft) of it"""
    fold = next((k for k in range(1, len(pts) - 1) if _turn_deg(pts[k - 1], pts[k], pts[k + 1]) >= _HAIRPIN_DEG), None)
    if fold is None:
        return pts, None
    cut = pts[: fold + 1]
    if edge_dist(cut[-1][0], cut[-1][1], envelope) <= SPUR_REACH_FT:
        return cut, None
    return cut, "folded back short of the field - the ground between is marsh a path may not cross"


def _out_of_bands(p: Pt, bands: Sequence[Poly], toward: Pt) -> Pt:
    """`p` set outside the grove bands it stands in (feature 291): walked out toward `toward`, the run's other end, or put
    a footpath's gap past the nearest edge, whichever lands nearer `toward` - so a spur that began in a band leaves it by
    the side it was heading for rather than into the yard behind (seed 11). A point already clear comes back untouched."""
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

    THE GAP IS NOT THE WEB'S GAP, and the difference is measured rather than chosen. The web threads
    BETWEEN plots and is barely more than the space between two walls, so `WEB_FABRIC_GAP` is 7 px.
    A track clipped at 7 px from a footprint still leaves the house CENTER inside 14 px of it (the retired
    `houses_off_corridors` check counted a hit at `seg_dist(center, lane) < 14`), and it did: 3 of 15 houses on the
    reference hamlet. A connector or a spur also has no business hugging a wall - it
    runs past the settlement, not through its gaps.

    ROUTE, then CLIP, and both are needed. `_route` threads the gap - a trodden way goes ROUND a wall
    rather than stopping at it - and the clip is the fallback for where no route exists, because the
    honest outcome there is a shortened track rather than a lane through somebody's house. The clip
    also catches the case the router cannot: a route is a PLAN, and a plan can start inside a wall
    when its endpoint came from a template.

    Research:
        track round the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: routed round, else clipped, else none
        gap off the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: `TRACK_FABRIC_GAP`, a lane's 7 ft from a garden fence,
            off every footprint, a footpath's gap off a grove band
        detour swing - UNRESEARCHED: the midpoint swung 40, 80, 140 then 220 px out from the cluster
        never across a grove - research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html: routed round
            the bands, else only the part clear of them kept
        the track's route walled - research/questions/0081-village-lanes.drawing.html: never across row crops or the flooded paddy, and off wet ground (the field, crop, toe band and wet ground walled)
        the track kept off drawn water - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: a way crosses water only at a crossing
    """
    if len(run) < 2:
        return run
    fabric = [poly for poly, _owner, _kind in _homestead_polys(s)]
    if not fabric:
        return run
    crops = crop_polys(s)
    toe_now = s.toe_band() or None
    wet_now = marsh_ground(s.M, but=("defense",))
    drawn_water = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    obstacles = [list(plan.envelope), *crops, *fabric, *([toe_now] if toe_now else []), *wet_now]
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
                return cand  # pragma: no cover - the swing ladder's accepted detour; no cohort cluster presents the obstacle it clears [174: KEPT, not deletable - it is the ladder's SUCCESS path, not a guard]
        # A DEAD END, MEASURED (feature 134 T50): a ladder that walked run[0] outward too, on the
        # theory that the offending leg was the first one and nothing above can move it. It changed
        # no map, because this function was never the one at fault - see `_pull_back_to_service`,
        # which moves a connector's inner end AFTER this has cleared it.
    kept = out if len(out) >= 2 else run  # the run the grove fallback weighs its crossings against
    # ...AND NEVER ACROSS A FARM'S GROVE (feature 291). Where neither the threaded route nor the swing clears every steading,
    # the clipped run - or the run as it came - went back across grove bands (the spur and the connector, cohort seeds 1, 5,
    # 11, 12, 14 and 15). A route that must clear only the grove bands and the crop, at a footpath's gap, is tried first; a
    # band is ground a track goes round. Each is taken only where it crosses no steading at all (feature 287's rule, below).
    bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]
    if bands and _crosses_fabric(kept, bands, 0.0):
        # an end standing IN a band (seed 11's spur began at a deep band's middle, where the walk along the run found no
        # clear ground) is set out of it first, by the side facing the run's other end: a route cannot start inside what it
        # avoids. Then three routes, each looser: round the bands and the crop; round the bands alone (the spur's field end
        # stands on the bund, inside the crop's gap); round the bands with the water left to the ford pass (seed 11's spur
        # already crossed the channel) - the last taken only if it crosses no more water than the run it replaces
        ends = [_out_of_bands(run[0], bands, run[-1]), _out_of_bands(run[-1], bands, run[0])]
        for hard, water in (([*bands, *crops], lines), (bands, lines), (bands, [])):
            around = _route(ends[0], ends[1], hard, [], water, gap=FOOTPATH_FABRIC_GAP)
            if (
                len(around) >= 2
                and not _crosses_fabric(around, bands, 0.0)
                and _water_crossings(around, lines) <= _water_crossings(kept, lines)
                and not _crosses_fabric(around, fabric, FOOTPATH_FABRIC_GAP)
            ):
                return around
        # ...and where the run starts inside a band there is no route from it: keep its FAR part, from the field or the
        # map's edge back to where it would first enter a band, and the web joins the near end (seed 1's spur, which began
        # inside its own farm's north band)
        far = clip_to_clear(kept[::-1], bands, FOOTPATH_FABRIC_GAP)[::-1]
        if len(far) >= 2 and not _crosses_fabric(far, fabric, FOOTPATH_FABRIC_GAP):
            return far
    # AND NEVER THE OFFENDING RUN AT ALL (feature 287, ways W25, FR-005): this terminal handed back the clipped run whether or
    # not it still crossed the steadings, or the original when the clip left nothing - the fallback this docstring's own
    # rule forbids. It hands back nothing: the spur is then recorded as dropped, and the connector takes the dry exit
    # (`connector_through`).
    return []


def stage_seat(s: Settlement, plan: SitePlan) -> None:
    """Where the settlement will sit.

    The seat band: which stretch of the field margin the cluster will occupy, with its back to the high ground
    and its face to the water. NOTHING IS DRAWN HERE - this stage decides a place and reserves no ground at all,
    which is why it can run before the houses without constraining them. It used to be the front half of a stage
    that also drew the connector and the field spur, and separating the two is what let every lane move after
    the farmhouses.

    Decide WHERE the settlement sits. Draws nothing at all.

    THIS IS THE HALF THAT HAS TO RUN FIRST, and separating it is the whole of feature 128. The old
    `stage_ways` did two unrelated jobs in one pass: it SEATED the cluster - `seat_cluster` sets
    `plan.seat`, which `stage_homesteads` reads on its first lines - and it DREW the connector and
    the field spur. Because the seating is a hard dependency of the houses, the stage could not
    simply be moved after them, and feature 126 worked around that by moving only the skeleton. That
    is how the connector and spur were left reserving ground before a single house existed.

    Split, the dependency and the drawing go to opposite sides of the houses. Nothing here calls
    `s.lane`: no lane and no corridor exists when this returns. Before the seat is chosen, the brook's fords are
    opened and the cost every later route pays to cross the brook is set.

    Steps:
        l7r.diagram.hamletgen.ways.checks.brook_fords
        l7r.diagram.hamletgen.ways.route.set_crossing
        l7r.diagram.sitegen.geom.crop_polys
        l7r.diagram.settlement.Settlement.toe_band
        l7r.diagram.hamletgen.cluster.seat_cluster

    Research:
        brook crossed only at crossing places - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html:
            fords opened on straight reaches, the only free cells in the brook's band
        every way pays the crossing - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html:
            `BROOK_CROSSING_COST_FT` set on the router for the whole roll
        seat off the reed fringe - research/questions/0058-ground-too-wet-to-build-on.drawing.html: the pond's fringe passed as wet
        the wind is kept - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a seat off the
            wind is recorded, never the wind renamed
    """
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
    # THE FORDS ARE OPENED FIRST (feature 261): every routing list below reads the brook through `stream_segs`, which
    # gaps it at these, so a way may cross the brook at a ford and nowhere else.
    s.brook_fords = brook_fords(plan.brook or [], FORD_SPACING, FORD_BEND_DEG)  # type: ignore[attr-defined]
    # every route this roll draws pays to cross the brook, at the fords (the only free cells in its band)
    set_crossing(plan.brook or [], FORD_HALF, s.px(BROOK_CROSSING_COST_FT))
    s.M["meta"]["brook_fords"] = [[round(x, 1), round(y, 1)] for x, y in s.brook_fords]  # type: ignore[attr-defined]
    plan.watercourses = (
        [
            ((float(a[0]), float(a[1])), (float(b[0]), float(b[1])))
            for rec in list(s.M.get("field_ditches", [])) + list(s.M.get("channels", []))
            for a, b in zip(rec["poly"], rec["poly"][1:], strict=False)
        ]
        + stream_segs(s)
        + [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for rec in s.M.get("drawn_channels", []) for a, b in zip(rec["pts"], rec["pts"][1:], strict=False)]
    )
    seat = seat_cluster(
        plan,
        dry_plots=crop_polys(s),
        toe=s.toe_band() or None,
        wet=marsh_ground(s.M, only=("pond_fringe",)),
        brook=plan.brook,  # the stream runs past the fan since feature 230; a cluster does not straddle it
    )  # the reservoir's reed fringe: not building ground (feature 150 T50)
    plan.seat = seat
    # THE SEAT BENDS TO THE WIND, NEVER THE WIND TO THE SEAT (feature 261). Until then this stage renamed the
    # wind after whatever the seat's back faced whenever the two disagreed by more than ~70 degrees, which is how
    # Kashikawa's belt came to stand on the south and east: the wind a map declares was being rewritten by where
    # its houses happened to land. `seat_cluster` now seats only on a margin whose back faces the wind, and a map
    # that had to fall back to one that does not says so here, rather than changing the wind to hide it.
    s.M["meta"]["seat_offwind"] = bool(seat.get("offwind"))
    s.M["meta"]["lane_skeleton"] = plan.lane_skeleton
    # THE SIDE THE HOUSES STAND ON, told to the settlement (feature 140): every field test from here on measures
    # the outline's few chords facing this seat (`rolling/fit.py::_field_chains`), never the whole outline.
    if plan.seat:
        s.field_face = (float(plan.seat["cx"]), float(plan.seat["cy"]))


def recorded_track(s: Settlement) -> Poly | None:
    """The track out the homesteads stage chose once the last house stood (`choose_track_out`, feature 320 FR-008) - the
    track every household's way was laid to, drawn here as chosen - None on a form that records none.

    Research: the track out decided once - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out"""
    r = s.M.get("way_out_track")
    return [(float(q[0]), float(q[1])) for q in r] if r and len(r) >= 2 else None


def choose_track_out(s: Settlement, plan: SitePlan) -> Poly:
    """THE TRACK OUT, CHOSEN ONCE (feature 320, FR-008; the GM: "collapsing the multiple decisions into a single decision
    regarding the lane"): from the cluster's downslope edge (`_cluster_gateway`, out of the field), swept clear of the wet
    ground, the steadings and the crop (`gateway_track`, on a polder `connector_track`), bent round the field and threaded
    through the steadings (`connector_through`). Asked once the last house stands, before any farmstead is drawn, with the
    homesteads as seated standing in for them (`fabric._homestead_polys` reads `s._seated_parts`), so the households' ways are
    laid to the track as it will be drawn; asked by `stage_track` on a form that records none. Its first leg and the rest are
    one choice: a first leg set on the seating's bearing apart from it met a household's way in a 164 degree nub (Inashiro's
    glyph check).

    Research: the track out decided once - research/questions/0081-village-lanes.drawing.html: away from the field leaning downslope, off the wet, out past the frame"""
    from .gateway import gateway_track  # the layer above this one: its fallbacks sweep with `connector_track` (feature 315)

    seat = plan.seat
    ax, ay = seat["along"]
    ox, oy = seat["out"]
    layout = skeleton_layout(plan.lane_skeleton, 0.0, 0.0, seat["lat"], seat["dep"])
    gx, gy = float(layout["gateway"][0]), float(layout["gateway"][1])
    band_gate = (seat["cx"] + ax * gx + ox * gy, seat["cy"] + ay * gx + oy * gy)
    polys = _homestead_polys(s)
    fabric = [poly for poly, _owner, _kind in polys] + law.solid_quads(s.M)
    plan.grove_bands = [poly for poly, _owner, kind in polys if kind == "groves"]  # for the dry exit (feature 291)
    toe = s.toe_band()
    wet = ([toe] if toe else []) + marsh_ground(s.M, but=("defense",))
    avoid = [list(plan.envelope), *crop_polys(s)]
    gate = gate_out_of_the_field(plan.envelope, _cluster_gateway(s, seat, band_gate))
    if plan.field_archetype in POLDER_ARCHETYPES:
        track = connector_track(plan, gate, avoid=avoid, wet=wet, waters=drawn_water_segs(s), fabric=fabric)
    else:
        track = gateway_track(s, plan, seat, band_gate, gate, avoid, wet, drawn_water_segs(s), fabric)
    return connector_through(s, plan, track, avoid, wet, [*plan.watercourses, *drawn_water_segs(s)], fabric)


def stage_track(s: Settlement, plan: SitePlan) -> None:
    """The connector and the field spur.

    The track out to the off-map road, and the path to the fields - drawn NOW, after the farmhouses, because a
    lane drawn earlier takes ground the houses then cannot have. That is true whatever the lane represents: a
    road may well predate a settlement in the world, but this generator does not inherit a road, it DRAWS one,
    and drawing it first reserves a no-build corridor the placer then refuses seats against. Both tracks now
    start from the settlement as it actually stands rather than from where it was predicted to go.

    The connector out to the road and the spur to the field - drawn AFTER the houses.

    THE GM, stating the whole feature (2026-08-24): *"We are reordering the procedural layout of the
    hamlet generation so that farmhouses are rendered after the fields and water, but before any
    village lanes. That is what the feature is. Full stop."*

    ANY. There is no exogenous class and no connector exception. A road can predate a settlement in
    the world, but this generator does not import one - it DRAWS one, and a lane drawn before the
    houses registers a no-build corridor (`settlement/water_ways/lanes.py`, `Settlement.lane`) that the seating then
    refuses seats against. It takes ground the houses cannot have, which is
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

    Steps:
        l7r.diagram.hamletgen.ways.track.connector_track
        l7r.diagram.hamletgen.ways.track._cluster_gateway
        l7r.diagram.hamletgen.ways.track._thread_the_fabric
        l7r.diagram.hamletgen.ways.bund.tip_onto_the_bund
        l7r.diagram.hamletgen.ways.clearance.route_around
        l7r.diagram.hamletgen.ways.clearance.clip_to_clear
        l7r.diagram.settlement.Settlement.trim_off_marsh
        l7r.diagram.settlement.Settlement.lane

    Research:
        lanes after the farmhouses - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: connector and spur drawn after every house
        polder has no spur - GUESS: the connector alone, the way into the fields taken to be over the dike's crest where the record runs a field path on to the outer bund
        spur to the field - research/questions/0081-village-lanes.drawing.html: the outline point whose path crosses least, then
            the shortest, clipped off the dry plots and the marsh
        spur bow - research/questions/0081-village-lanes.drawing.html: a 14 px sideways swing at the midpoint
        spur over the brook at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html
        field spur tip on the bund - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: set on the worked
            ground's edge, again after threading
        spur kept however short - research/questions/0014-bunds-between-the-paddies-aze.drawing.html: drawn down to its 5 ft tread
        row road - research/questions/0033-row-villages-resson.drawing.html: the street carried on off the map, over a ford
        row road width - research/questions/0033-row-villages-resson.drawing.html: 6 ft
        track off the map - research/questions/0081-village-lanes.drawing.html: from the gateway, out of the field, to the frame
        track off the wet - research/questions/0081-village-lanes.drawing.html: the toe band and every drawn marsh are wet
        spur clip margin - research/questions/0081-village-lanes.drawing.html: a lane may touch a plot's boundary; the code clips the spur 12 ft off the dry plots
        toe-band margin - UNRESEARCHED: the spur clipped 12 ft off the toe band
        spur tip set back - UNRESEARCHED: SPUR_SETBACK, 17 ft off the field outline's vertex
        connector width - research/questions/0081-village-lanes.drawing.html: the track out 6 ft (`CONNECTOR_WIDTH`), valley and polder alike
        lane clearance - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's middle keeps 7 ft clear of a garden fence; the connector and spur keep `LANE_CLEARANCE`, 7 ft to a fence held as a 40 ft center corridor
    """
    seat = plan.seat
    ax, ay = seat["along"]
    ox, oy = seat["out"]
    cx, cy = seat["cx"], seat["cy"]

    crops = crop_polys(s)
    # The steadings, read ONCE for the whole stage: the bearing sweep ranks against them and
    # `_thread_the_fabric` re-reads them for the clip. They cannot change during this stage -
    # nothing here draws a homestead - so a second walk would only be a second chance to disagree.
    # ...WITH THE BUILDINGS' BOXES AS THE LANE LAW READS THEM (`law.solid_quads`, ways: break-mid-run): the sweep and the
    # dry exit keep `TRACK_FABRIC_GAP` off the very boxes `law.breaks_through` asks a connector leg's midpoint to stay out
    # of, so the connector they hand back cannot run through a building by the rule's own reading (a turned house's box
    # is not its drawn quad)
    plan.grove_bands = [poly for poly, _owner, kind in _homestead_polys(s) if kind == "groves"]  # for the dry exit (feature 291)

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
        s.lane(recorded_track(s) or choose_track_out(s, plan), width=CONNECTOR_WIDTH, clearance=LANE_CLEARANCE, worn=True, connector=True)
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
    # ...GAPPED AT THE FORDS (feature 261): a spur that crosses at a ford crosses legally - `bridges()` decks it - so only
    # a crossing between fords counts against it. Judged against the whole course, every spur to rice across the brook
    # scored the same violation, the shortest won the tie, and the clip cut that straight run to a 28 ft stub that was
    # never drawn: Inashiro and Kashikawa lost their only way to the field.
    brook_segs = gap_segments([(plan.sink_brook[i], plan.sink_brook[i + 1]) for i in range(len(plan.sink_brook) - 1)], getattr(s, "brook_fords", ()), FORD_HALF)

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
        # ...AND OVER THE BROOK AT A FORD (feature 261). Where the houses stand across the brook from their rice, the
        # path crosses it square at the ford that makes the walk shortest, and `bridges()` decks the crossing - a
        # straight run would meet the brook wherever it happened to, between fords, and the clip would cut it there.
        _via = ford_crossing(_s, edge, plan.brook or [], getattr(s, "brook_fords", ()))
        if _via:
            return [_s, *_via, edge]
        _mx, _my = (_s[0] + edge[0]) / 2, (_s[1] + edge[1]) / 2
        return [_s, (_mx + ax * 14, _my + ay * 14), edge]

    # ...and again the candidate is the DRAWN path, bow and all - see `path_is_clear`.
    spur_check = PathChecker(crops, plan.sink_pond, brook_segs, plan.watercourses)  # built once for every candidate (FR-005)
    spur = min(
        (spur_path(q) for q in sorted(plan.envelope, key=lambda v: math.hypot(v[0] - cx, v[1] - cy))),
        key=lambda p: (spur_check.violations(p), polyline_len(p)),
    )
    _spur_pts = s.trim_off_marsh(clip_to_clear(spur, [*crops, *([toe_now] if toe_now else [])], 12.0))
    _spur_pts = _fork_spur(_spur_pts, _kept_arms)
    # ...AND ITS TIP IS SET ON THE BUND (269 B04, research/questions/0014-bunds-between-the-paddies-aze.drawing.html: the path "runs from the hamlet to the paddy's outer bund
    # and joins it ... it never ends in open ground short of the bund"). The clip leaves it 12 ft off the hem and the set-back
    # 17 ft off an outline vertex - short of the bund - and where the rice stands proud of the outline it could stop in the
    # rice (Sawada: 4 ft in). Carried on to the worked ground's edge, or pulled back out of it.
    _spur_pts = tip_onto_the_bund(_spur_pts, memo_ground(s, "worked", worked_ground), SPUR_WIDTH / 2.0, RunOnBlocks(s))
    _spur_ft = sum(math.dist(_spur_pts[k], _spur_pts[k + 1]) for k in range(len(_spur_pts) - 1)) if len(_spur_pts) >= 2 else 0.0
    # WHAT WAS LEFT OF THE SPUR IS RECORDED, drawn or not (feature 230): a spur that fails the floor below vanished in
    # silence, and a reviewer asking what the nearest way to the paddy was is how the reference hamlet turned out to have
    # none. Where a field path ends was the open question this measured for; research/questions/0014-bunds-between-the-paddies-aze.drawing.html answers it (on the bund).
    s.M["meta"]["field_spur_ft"] = round(_spur_ft, 1)
    # ...AND A SPUR THAT NO LONGER REACHES THE WEB IS NOT DRAWN. The clip takes the spur out of the crop and off
    # the marsh from BOTH ends, so what survives can be a length of path in the middle of open ground: on the
    # reference hamlet it came back 111 ft long, 152 ft from the nearest lane and 72 ft from the field, joining
    # nothing to nothing - a second lane "network" of one fragment, which is a worse thing to draw than no path
    # at all and which the gate's own one-network rule catches. So the survivor is drawn only while its head is
    # still on the fabric it forked from; otherwise the LENGTH stands as the record and `field_spur_head_ft`
    # says how far short it fell. That is the shortfall reported rather than swallowed - the thing the fifth
    # review pass asked for - and it is not the same as the sweep silently dropping it, which is what made the
    # reference hamlet's missing path invisible in the first place.
    # Whether it SURVIVES is decided later and elsewhere: nothing is on the map to attach to at this point in
    # the stage - not the connector, which is drawn below this, and not the web, which is two stages away - so
    # the spur is drawn on its own length and the sweeps judge it against the finished network (`sweeps.py`).
    # THE FLOOR IS THE TREAD'S OWN WIDTH, NOT 20 FT (269 B04: "however short that leaves the path"). A run shorter than the
    # path is wide is not a line; anything longer is the path to the rice, and a spur swept later is answered at the end of
    # the web by the nearest lane running on to the bund (`a_way_onto_the_bund`).
    if _spur_ft >= SPUR_WIDTH:
        # ...AND NEVER DRAWN AS AN OUT-AND-BACK (settlement-review, feature 230 pass 11). Threading the clipped spur round
        # the steadings can fold it back on itself: the reference hamlet's ran 90 ft toward the field and straight back to
        # within 14 px of where it began, the smoothing pass then rightly cut that hairpin away, and the hamlet's only path
        # to its rice disappeared with no record. Keeping the arm toward the field was tried first and was wrong: that arm
        # stopped 60.6 ft short of the field, where the marsh the path may not cross lies between, so it was a lane ending
        # in open ground (`lanes_reach_something`). A folded spur is drawn only when its outward arm still reaches the
        # field; otherwise the map says why it has no path to its rice.
        _threaded = _thread_the_fabric(s, plan, _spur_pts)
        _drawn_spur, _swept = spur_cut_at_the_fold(_threaded, plan.envelope) if len(_threaded) >= 2 else (_threaded, "no way to the field clear of the steadings - the field path is the web's")
        # ...AND THE DRAWN TIP IS SET ON THE BUND AGAIN (269 B04): the tip was set above, but the threading moves the spur's
        # free bow vertex round the steadings and the fold cut then keeps the arm out to it, so the path drawn can end at a
        # vertex neither step held to the field's edge. Cohort seed 905 (feature 304 T03, dispersed): a 6 ft spur bowed 14 ft
        # sideways was threaded out to a bow 20 ft inside a paddy plot, and the arm kept ran across the comb's main ditch at the
        # field's head onto a 2 ft bund strip - no deck lands dry there (`crossing_deck`), and a dispersed hamlet runs no web
        # settle to cut it, so `bridges()` raised `UndeckableCrossing`. Pulled back out of the worked ground, the tip stops on
        # this side of the bund, as the tip set above does.
        if _swept is None:
            _drawn_spur = tip_onto_the_bund(_drawn_spur, memo_ground(s, "worked", worked_ground), SPUR_WIDTH / 2.0, RunOnBlocks(s))
            if len(_drawn_spur) < 2:
                _swept = "the threaded spur runs in the worked ground end to end - the field path is the web's"
        if _swept is None and not s.admits_lane(_drawn_spur, SPUR_WIDTH):
            _swept = "the overlap matrix refuses the spur (a dry plot or a steading's part on it) - the field path is the web's"
        if _swept is None:
            s.lane(_drawn_spur, width=SPUR_WIDTH, clearance=LANE_CLEARANCE, worn=True, spur=True)  # flagged so neither sweep can drop the FIELD's only way
        else:
            s.M["meta"]["field_spur_swept"] = _swept

    # the CONNECTOR, out to the frame
    # ...and the gate the connector starts FROM must itself be out of the crop. The skeleton's
    # gateway is a point in the seat frame, so on a cluster that sits against a concave stretch of
    # the fan it can land INSIDE the field envelope - and the connector then starts in the rice and
    # crosses the outline twice on its way out (Inashiro, GM 2026-08-12).
    # A ROW VILLAGE'S ROAD IS ITS STREET (feature 291 plan D17; research/questions/0033-row-villages-resson.html: the road village's farms stand
    # along the road): the connector carries the first planned street on out of the frame along its own line, from
    # whichever end is nearer the sheet's edge. Laid from the gateway, it ran straight across the far row's holdings.
    # ...FROM THE STREET AS IT WILL BE DRAWN, its farms' span (`street.drawn_span`), not the whole planned line: run out from
    # the plan's end, the road stopped 481 ft short of a street the web lays only along its farms, no lawful join closed
    # the gap, and the street was dropped from the network with all ten of its farms (cohort seed 22, 2026-10-01)
    _row = (getattr(s, "_row_streets", None) or [None])[0] if plan.settlement_form == "linear" else None
    if _row and len(_row) >= 2:
        from .street import drawn_span, street_runs_out  # the street module reads the web's settle, laid after this stage

        _span = drawn_span(s, 0, s.M.get("houses") or [], plan.brook or [])
        _a, _b = street_runs_out(_span if len(_span) >= 2 else _row, s.W, s.H)
        # THE ROAD LEAVES BY THE NEARER EDGE, AND THE STREET RUNS ON OFF THE MAP AT ITS OTHER END TOO (feature 328 wave 5,
        # research/questions/0033-row-villages-resson.drawing.html: "The street runs on off the map as the road into it"): cut
        # back to its last farm's path at the far end, the street stopped where the road it stands for went on
        for _k, _out in enumerate(sorted((_a, _b), key=lambda r: r[0])):
            _out = _out[1]
            # ...AND OVER THE BROOK AT A FORD, as every other way crosses it (`ford_crossing`): run straight on along the
            # street's line, the road crossed the brook 72 ft from the nearest ford (cohort seed 3, 2026-10-01)
            _out = [_out[0], *ford_crossing(_out[0], _out[-1], plan.brook or [], getattr(s, "brook_fords", ())), _out[-1]]
            s.lane(_thread_the_fabric(s, plan, _out), width=6, clearance=LANE_CLEARANCE, worn=True, connector=True)
            if _k:  # ...the far end's run is the road running on, not the way in: the board stands at the entrance (`run_on`)
                s.M["lanes"][-1]["run_on"] = True
        return
    # THE TRACK OUT AS CHOSEN ONCE THE LAST HOUSE STOOD (feature 320, FR-008), the households' ways already laid to it; chosen
    # here only on a form that records none
    s.lane(recorded_track(s) or choose_track_out(s, plan), width=CONNECTOR_WIDTH, clearance=LANE_CLEARANCE, worn=True, connector=True)


def connector_track(plan: SitePlan, start: Pt, avoid: Sequence[Poly] = (), reach: float = 4000.0, wet: Sequence[Poly] = (), waters: Sequence[tuple[Pt, Pt]] = (), fabric: Sequence[Poly] = ()) -> Poly:
    """The track from the settlement's gateway to the map edge, steered clear of the crop.

    Bearings are tried outward from "away from the field, leaning downslope" - the direction a real
    track leaves by, since the wider world is downstream and the paddy is not walkable - and the
    first that is clean of wet ground, the steadings and every crop, pond and water wins. Sweeping alternate sides
    at growing angles (41 bearings) keeps the chosen bearing as close to the ideal as the geometry allows instead
    of jumping to whatever happens to be clear. Where none is clean, the least-bad bearing is kept only where it is
    dry and clear of every steading; otherwise the dry exit's flood fill finds the way out (`connector_dry_exit`).

    The track is drawn PAST the canvas edge, not up to it: the gate wants an endpoint at the frame,
    and the crop is set later from the hard features, so a track that overshoots is trimmed by the
    viewBox while one that stops short reads as a dead end.

    Research:
        track out off the wet - research/questions/0081-village-lanes.drawing.html: away from the field leaning downslope, wet
            ground refused first, run past the frame
        leaning downslope - UNRESEARCHED: the ideal bearing weighs 0.55 away from the field and 0.85 downslope
        wet, then steadings, then crop - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: wet ground and crop refused (0081), no tread on a steading (0246)
        the three ranked - NONE: search order; wet and steaded bearings are both refused in the end
        track's wander - research/questions/0081-village-lanes.drawing.html: bowed 34 and 46 px either side of the bearing
        track off the steadings - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: kept `TRACK_FABRIC_GAP` (7 ft) off the steadings"""
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
    wet_grown = [wet_grown_by_the_lane(w) for w in wet if len(w) >= 3]
    # THE WATER, THE CROP AND THE POND INDEXED ONCE FOR THE WHOLE SWEEP (feature 276, FR-005): 41 bearings each asked
    # every segment and polygon again. `PathChecker` answers exactly what `path_violations` did.
    wet_checks = [PathChecker([w], None, ()) for w in wet_grown]
    ground_check = PathChecker(avoid or [plan.envelope], pond, brook, waters)
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
        soaked = sum(chk.violations(path) for chk in wet_checks)  # the WET POLYGON only - pond and brook are scored once, below
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
        violations = ground_check.violations(path)
        if soaked == 0 and steaded == 0 and violations == 0:
            return path
        if best is None or (soaked, steaded, violations) < best[0]:
            best = ((soaked, steaded, violations), path)
    # NO CLEAN BEARING: the least-bad one only where it is DRY and clear of every steading.
    #
    # This used to return `start` plus a ray straight away from the field, and that fallback is what
    # actually shipped the defect: it consulted nothing, so on any map where the sweep came up empty
    # the connector was drawn through the hem and across the drainage ditch, failing three checks at
    # once. The least-bad bearing that replaced it degraded a hard map by one violation instead of by
    # everything - but still emitted it, a track through the marsh or across a farmstead (feature 287,
    # ways W23, FR-005). A crop clip stays the best bearing's, because `route_around` bends the drawn
    # track round the field afterwards; a wet or steaded bearing is refused, and the track is found by
    # the flood fill instead (`dry_exit`).
    assert best is not None
    if best[0][:2] == (0, 0):
        return best[1]
    return connector_dry_exit(plan, start, avoid, wet, waters, fabric)


def wet_grown_by_the_lane(w: Poly) -> Poly:
    """A wet polygon grown 8 px along its own outward normals (`ring_offset`) - the lane's half-width and the gate's pad,
    so the sweep scores the tread the gate measures (see `connector_track`)."""
    return list(ring_offset(w, 8.0, 0.0)[: len(w)])


def connector_through(s: Settlement, plan: SitePlan, track: Poly, avoid: Sequence[Poly], wet: Sequence[Poly], waters: Sequence[tuple[Pt, Pt]], fabric: Sequence[Poly]) -> Poly:
    """The connector as drawn (`_connector_through`), rounded to the record's 0.1 ft."""
    run = _connector_through(s, plan, track, avoid, wet, waters, fabric)
    # ...AT THE RECORD'S 0.1 FT, as every other lane is written (`reshape_lane`): a start left unrounded stood a hair off the
    # rounded copies of it the web's lanes end on, and they closed a face of no area (cohort seed 20)
    return [(round(x, 1), round(y, 1)) for x, y in run]


def _connector_through(s: Settlement, plan: SitePlan, track: Poly, avoid: Sequence[Poly], wet: Sequence[Poly], waters: Sequence[tuple[Pt, Pt]], fabric: Sequence[Poly]) -> Poly:
    """The connector as drawn: the swept track bent round the field (`route_around`) and threaded through the steadings
    (`_thread_the_fabric`); where either cannot make it clean, the flood fill's dry exit from the same gateway (ways W24,
    W25) - never the track still across the field or a farmstead. It is SQUARED at its water crossings first (`settle.
    square_run`, what the web's last pass does to every lane) and judged as squared (`connector_keeps_the_law`): the web's
    squaring drops a vertex standing in the water and so merges two legs into one, which is a new leg the rule must see
    here, since no repair cuts the connector afterwards.

    Research:
        connector round the field and the steadings - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: bent and threaded,
            else the dry exit
        gives up a wood seat as last resort - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html:
            the seats the way out crosses are released
        connector's berth off the field - UNRESEARCHED: bent round the field at `SPUR_SETBACK`, 17 ft off its envelope"""
    from .settle import square_run  # the web's last pass sits above this layer

    around = route_around(plan.envelope, track, SPUR_SETBACK)
    run = _thread_the_fabric(s, plan, around) if around is not None else []
    run = square_run(s.M, run) if len(run) >= 2 else run
    if len(run) >= 2 and connector_keeps_the_law(s.M, run):
        return run
    # THE DRY EXIT IS WALLED BY WHAT THE REGISTRY OF WHAT STANDS FORBIDS A WAY ON (feature 287 M8): the overlap matrix's
    # extents and the households' reserved wood seats (`Reservations.seat_walls`, the copse's lane buffer about each)
    st = getattr(s.M, "standing", None)
    forbid = st.forbidding("lanes") if st is not None else []
    matrix = [e[1] for e in forbid if e[0] != "wood seat"]
    seats = [e[1] for e in forbid if e[0] == "wood seat"]
    with contextlib.suppress(NoDryExit):
        return connector_dry_exit(plan, track[0], [*avoid, *matrix, *seats], wet, waters, fabric)
    # ...AND ONLY THEN OVER A RESERVED SEAT, WHICH THE WAY OUT TAKES: a gateway the seats wall in on every side has one way out,
    # and the seats it crosses are given up by name (`meta.wood_seats_to_the_connector`) rather than the hamlet left with none
    run = connector_dry_exit(plan, track[0], [*avoid, *matrix], wet, waters, fabric)
    if st is not None:
        gone = st.reserved.release_seats_along(run, CONNECTOR_WIDTH)
        if gone:
            s.M["meta"]["wood_seats_to_the_connector"] = [[round(x, 1), round(y, 1)] for x, y in gone]
    return run


CONNECTOR_WIDTH = 6.0
"""The connector's tread, px: the cart track out to the wider world, drawn wider than the web's footpaths.

Research: connector width - research/questions/0081-village-lanes.drawing.html: 6 ft"""


def connector_keeps_the_law(M: Mapping[str, Any], run: Poly) -> bool:
    """May `run` be drawn as the connector? Its legs run through no building (`law.breaks_through` over `law.solid_boxes`,
    the lane law's own reading - the connector is a tree lane no settle repair cuts, so this is where the rule is decided),
    and it crosses each brook at most once (`law.crossing_points`), so a household's way out along it never crosses the
    brook twice on the connector alone (`law.way_out_carriers` names a crossing on another lane for every such way out).
    A run refused here is replaced by the dry exit, which crosses no water line and keeps `TRACK_FABRIC_GAP` off every
    box (`stage_track` walls it with `law.solid_quads`).

    Research:
        no building on the connector - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no leg through a building's box
        nothing the matrix forbids - research/questions/0081-village-lanes.drawing.html, research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: no dry plot, well or steading part
        each brook crossed at most once - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html"""
    if law.breaks_through(run, law.solid_boxes(M)):
        return False
    if forbidden_segment(M, "lanes", run, CONNECTOR_WIDTH) is not None:
        return False  # ...and it lies on nothing the overlap matrix forbids a way on (feature 287 M8): a dry plot, a well
    return all(len(law.crossing_points(run, brook)) <= 1 for brook in law._brooks(M))


class NoDryExit(ValueError):
    """The cluster's gateway has no dry way out of the frame: every route crosses marsh, a steading, the field or the brook.
    That is a property of the seat (`seat_cluster` must refuse such an anchor - the homesteads area's rule), raised here
    rather than drawn as a track through the wet (feature 287, ways W23)."""


def connector_dry_exit(plan: SitePlan, start: Pt, avoid: Sequence[Poly], wet: Sequence[Poly], waters: Sequence[tuple[Pt, Pt]], fabric: Sequence[Poly]) -> Poly:
    """The connector by the flood fill (`dry_exit`): walled by the wet ground (grown by the lane's width), every steading at
    `TRACK_FABRIC_GAP`, the field and the pond; the brook and the drawn water are lines it may not cross.

    Research:
        dry exit off the wet - research/questions/0081-village-lanes.drawing.html: walled by the marsh, the steadings and the field
        pond berth - UNRESEARCHED: 80 ft past the pond's larger half-axis
        grove band gap - UNRESEARCHED: a footpath's gap plus half the tread, on a finer grid
        brook not crossed - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: no water line crossed"""
    # ...A FARM'S GROVE BAND AT A FOOTPATH'S GAP, over a grid fine enough to pass between two (feature 291 on 287): dispersed
    # farms stand a lane's room (32 ft) apart, and at the track's gap on the 20 ft grid every way between them was walled -
    # cohort seeds 5 and 16 had no dry exit at all
    bands = {tuple(map(tuple, b)) for b in getattr(plan, "grove_bands", None) or ()}
    walls = (
        [(wet_grown_by_the_lane(w), 0.0) for w in wet if len(w) >= 3]
        + [(list(f), FOOTPATH_FABRIC_GAP + CONNECTOR_WIDTH / 2.0 if tuple(map(tuple, f)) in bands else TRACK_FABRIC_GAP) for f in fabric]
        + [(list(a), 0.0) for a in (avoid or [plan.envelope])]
    )
    if plan.sink_pond:
        px, py, rx, ry = plan.sink_pond  # the pond's disc, at the sweep's own 80 ft berth (`path_violations`)
        r = max(rx, ry)
        walls.append(([(px + r * math.cos(k * math.pi / 8), py + r * math.sin(k * math.pi / 8)) for k in range(16)], 80.0))
    lines = [(plan.sink_brook[i], plan.sink_brook[i + 1]) for i in range(len(plan.sink_brook) - 1)] + list(waters)
    # ...FROM OUTSIDE ANY GROVE BAND: a dispersed seat's gateway can fall inside a farm's deep band, and the fill's start cell
    # alone is walkable there - every cell round it was band (cohort seed 5); a track may not start in a grove in any case
    if bands:
        start = clear_of_bands(start, [list(b) for b in bands], FOOTPATH_FABRIC_GAP + CONNECTOR_WIDTH / 2.0 + 0.71 * GROVE_EXIT_CELL_FT + 1.0)
    path = dry_exit(start, walls, lines, float(plan.W), float(plan.H), cell=GROVE_EXIT_CELL_FT if bands else EXIT_CELL_FT)
    if path is None:
        raise NoDryExit(f"no dry way out of the frame from the gateway at ({start[0]:.0f}, {start[1]:.0f})")
    return path
