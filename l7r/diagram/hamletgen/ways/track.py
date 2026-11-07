"""Split from hamletgen/ways.py by feature 173 - see this package's CLAUDE.md for the index.

Research: track plumbing - NONE"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import ring_offset
from l7r.diagram.work_counts import OPS

from ..consts import (
    LANE_CLEARANCE,
    POLDER_ARCHETYPES,
    Poly,
)
from ..plan import SitePlan
from .thread import (
    CONNECTOR_BAND_GAP_FT as CONNECTOR_BAND_GAP_FT,
)
from .thread import (
    CONNECTOR_WIDTH as CONNECTOR_WIDTH,
)
from .thread import (  # noqa: F401 - lifted out at the 1,000-line bar (405 T09); re-exported so every importer and test still reaches them here
    _inner as _inner,
)


def recorded_track(s: Settlement) -> Poly | None:
    """The track out the homesteads stage chose once the last house stood (`choose_track_out`, feature 320 FR-008) - the
    track every household's way was laid to, drawn here as chosen - None on a form that records none.

    Research: the track out decided once - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out"""
    r = s.M.get("way_out_track")
    return [(float(q[0]), float(q[1])) for q in r] if r and len(r) >= 2 else None


def the_track_out(s: Settlement, plan: SitePlan) -> Poly:
    """The track out the homesteads recorded (`recorded_track`) - or, on a form that records none (a dispersed hamlet, whose
    seating builds no access tree), the track out chosen now in Rust as the homesteads choose theirs (`household_ways.chose_the_track`,
    `l7r_phases.track_out`), `NoDryExit` by name where no way leaves the frame. The Python choice went with T32 (feature 444).

    Research: the track out decided once - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way joins the track out"""
    track = recorded_track(s)
    if track is not None:
        return track
    from ..homesteads.household_ways import chose_the_track  # the homesteads' layer: its Rust chooser, asked once the houses stand

    return chose_the_track(s, plan)


def stage_track(s: Settlement, plan: SitePlan) -> None:
    """The connector (the field spur it also laid went in feature 417 T50: laid before anything it could join, it was dropped whole).

    The track out to the off-map road - drawn NOW, after the farmhouses, because a lane drawn earlier takes ground the houses
    then cannot have. That is true whatever the lane represents: a road may well predate a settlement in the world, but this
    generator does not inherit a road, it DRAWS one, and drawing it first reserves a no-build corridor the placer then refuses
    seats against. It starts from the settlement as it actually stands rather than from where it was predicted to go.

    THE GM, stating the whole feature (2026-08-24): *"We are reordering the procedural layout of the
    hamlet generation so that farmhouses are rendered after the fields and water, but before any
    village lanes. That is what the feature is. Full stop."*

    ANY. There is no exogenous class and no connector exception. A road can predate a settlement in
    the world, but this generator does not import one - it DRAWS one, and a lane drawn before the
    houses registers a no-build corridor (`settlement/water_ways/lanes.py`, `Settlement.lane`) that the seating then
    refuses seats against. It takes ground the houses cannot have, which is
    exactly what the GM reported: *"the lanes being there was the thing that was making it difficult
    to lay out the farmhouses."* That reasoning - ground reservation - is true of every lane whatever it represents.

    **Both branches.** The polder path returns early with its own connector; a fix applied only to
    the valley path would leave polder hamlets reserving ground, and the reference hamlet is a valley
    map so it would not notice.

    Steps:
        l7r.diagram.hamletgen.ways.track.the_track_out
        l7r.diagram.hamletgen.ways.track.recorded_track
        l7r.diagram.hamletgen.ways.clearance.route_around
        l7r.diagram.settlement.Settlement.lane

    Research:
        square at the water, as laid - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html, research/questions/0084-plank-bridges-over-farm-ditches-itabashi.drawing.html: a way crosses the brook or a ditch square - the row road squared here as laid (`square_run`, feature 417 T49); the valley and polder connector as chosen and threaded (`choose_track_out`, `_connector_through`, which square it)
        track out and field way one through-route - research/questions/0081-village-lanes.drawing.html: the spur to the fields and the track out are one through-route - the track lays no spur (feature 417 T50) and the field is reached by the web's way onto the bund or the settle's field way, neither laid as the connector's other end, a departure the code keeps until feature 417 T32
        lanes after the farmhouses - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: the connector drawn after every house
        row road - research/questions/0033-row-villages-resson.drawing.html: the street carried on off the map, over a ford
        row road width - research/questions/0033-row-villages-resson.drawing.html: 6 ft
        row road over the brook at a ford - research/questions/0035-villages-beside-their-stream-one-bank-or-both.drawing.html: the ford that makes the walk shortest, each leg threaded to its landing (`thread_over_the_ford`)
        track off the map - research/questions/0081-village-lanes.drawing.html: from the gateway, out of the field, to the frame
        track off the wet - research/questions/0081-village-lanes.drawing.html: the toe band and every drawn marsh are wet
        connector width - research/questions/0081-village-lanes.drawing.html: the track out 6 ft (`CONNECTOR_WIDTH`), valley and polder alike
        lane clearance - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: a lane's middle keeps 7 ft clear of a garden fence; the connector keeps `LANE_CLEARANCE`, 7 ft from the lane's middle, a footprint held to it at its corners
    """
    # The steadings, read ONCE for the whole stage: the bearing sweep ranks against them and
    # `_thread_the_fabric` re-reads them for the clip. They cannot change during this stage -
    # nothing here draws a homestead - so a second walk would only be a second chance to disagree.
    # ...WITH THE BUILDINGS' BOXES AS THE LANE LAW READS THEM (`law.solid_quads`, ways: break-mid-run): the sweep and the
    # dry exit keep `TRACK_FABRIC_GAP` off the very boxes `law.breaks_through` asks a connector leg's midpoint to stay out
    # of, so the connector they hand back cannot run through a building by the rule's own reading (a turned house's box
    # is not its drawn quad)
    # (the grove bands the dry exit reads are set where a track out is chosen, `choose_track_out` - never on a recorded track, the
    # common path, where reading every homestead's polygons was the stage's one uncounted loop: T32's second audit)

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
    # THE TRACK LAYS NO FIELD SPUR (feature 417 T50): laid here, before the connector and two stages before the web, it joined
    # nothing it could reach, and on 28 of 54 maps the settle's one-network step dropped it whole - laid only to be dropped. The
    # field is reached by the web's own way onto the bund (`bund.a_way_onto_the_bund`: run on, branch) or the settle's field way
    # (`reach.settle_field`), each laid joined to the ways it serves.
    # A POLDER'S CONNECTOR is its recorded track out (feature 150), over the dike at its sluice gaps
    if plan.field_archetype in POLDER_ARCHETYPES:  # both polder archetypes (feature 150)
        s.M["meta"]["lane_skeleton"] = plan.lane_skeleton
        s.lane(the_track_out(s, plan), width=CONNECTOR_WIDTH, clearance=LANE_CLEARANCE, worn=True, connector=True)
        return

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
        # ...THE ROAD IN RUST (feature 444 T32, `rust/phases/src/track.rs`): the street as drawn, run on off the sheet at both ends
        # along each end's last leg, the nearer first, each over the brook at a ford, threaded and squared; drawn here
        from ..homesteads.household_ways import track_inputs
        from ..phases_ext import phases

        pt = lambda q: (float(q[0]), float(q[1]))  # noqa: E731
        houses = s.M.get("houses") or []
        own = getattr(s, "_row_street_farms", None) or []
        inputs = track_inputs(s, plan)
        inputs.update(
            {
                "street": [pt(q) for q in _row],
                "farms": [pt(q) for q in own[0]] if own else [(float(h["x"]), float(h["y"])) for h in houses],
                "frames": [max(float(b[2]), float(b[3])) for b in ((h.get("geom") or {}).get("bbox") for h in houses) if b],
                "brook": [pt(q) for q in plan.brook or []],
                "fords": [pt(f) for f in getattr(s, "brook_fords", ()) or ()],
            }
        )
        OPS["write@row_road_inputs"] += 2 * len(houses)  # each house read for its farm and its frame (T32's third audit)
        got = phases().row_road_runs(inputs)
        for k, n in got["counts"].items():  # the Rust's counted work on the stage's (feature 444 D5)
            OPS[k] += n
        for k, run in enumerate(got["runs"]):
            s.lane([pt(q) for q in run], width=CONNECTOR_WIDTH, clearance=LANE_CLEARANCE, worn=True, connector=True)
            if k:  # ...the far end's run is the road running on, not the way in: the board stands at the entrance (`run_on`)
                s.M["lanes"][-1]["run_on"] = True
        return
    # THE TRACK OUT AS CHOSEN ONCE THE LAST HOUSE STOOD (feature 320, FR-008), the households' ways already laid to it; chosen
    # here only on a form that records none
    s.lane(the_track_out(s, plan), width=CONNECTOR_WIDTH, clearance=LANE_CLEARANCE, worn=True, connector=True)


def wet_grown_by_the_lane(w: Poly) -> Poly:
    """A wet polygon grown 8 px along its own outward normals (`ring_offset`) - 8 ft on a hamlet's sheet (1 ft a px),
    the web's own bar off wet ground (`WEB_HARD_GAP`), so the sweep scores the tread the gate measures (`connector_track`).

    Research:
        its unstated figures - GUESS: searched, the record silent (feature 417 T38 pass N4, 2026-10-25) - 8 (wet ground grown 8 ft (`WEB_HARD_GAP` written as a literal))
    """
    return list(ring_offset(w, 8.0, 0.0)[: len(w)])


class NoDryExit(ValueError):
    """The cluster's gateway has no dry way out of the frame: every route crosses marsh, a steading, the field or the brook.
    That is a property of the seat (`seat_cluster` must refuse such an anchor - the homesteads area's rule), raised here
    rather than drawn as a track through the wet (feature 287, ways W23)."""
