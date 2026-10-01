"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, cast

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._geom import CanopyArea
from l7r.diagram.settlement.homestead_parts.belt_law import wind_unit
from l7r.diagram.settlement.homestead_parts.wood_goal import copse_goal

from ..consts import COPSE_BELT_REACH_FT, COPSE_HOUSE_REACH_FT
from ..homesteads import farmstead_fixtures, household_bamboo
from ..plan import SitePlan
from .bamboo import bamboo_seats
from .belt import belt_polygon
from .frame import belt_page, frame_bounds, frame_for, scatter_frame, title_pocket
from .parcels import CROP_MARGIN, open_ground_patches

# ---- STAGE 7: the ground between everything ------------------------------------------------------


LEE_BAND_FT = 40.0  # ft: the width across the wind of one band of the belt, about a crown and a half
LEE_DEPTH_FT = 30.0  # ft: a crown's depth, the lee face's thickness in each band


def reserved_seats(s: Settlement) -> list[tuple[float, float]]:
    """Every household's reserved share of the wood floor, as the seats its record carries (`wood_share`, feature 287,
    woods W25; plan D9), in the houses' order."""
    return [(float(p[0]), float(p[1])) for h in s.M.get("houses") or [] for p in (h.get("wood_share") or {}).get("seats") or ()]


def lee_face(clumps: Sequence[tuple[float, float]], wind: tuple[float, float]) -> list[tuple[float, float]]:
    """The belt crowns on its LEE face - in each `LEE_BAND_FT` band across the wind, those within `LEE_DEPTH_FT` of the
    band's most leeward crown (settlement-review of Mizuguchi, feature 261).

    The against-the-belt copse is "tucked against the back grove" (`COPSE_SITINGS`): the fruit and bamboo a household
    keeps stand in the belt's shelter, on the houses' side. Anchored on every belt crown, it could stand anywhere within
    reach of one, and once the belt kept its depth where its fringe turns, 31 of Mizuguchi's 75 copse crowns stood beyond
    its windward face, farther from every house than the belt beside them - one wood 250 ft deep. `wind` points toward
    where the wind comes from."""
    wx, wy = wind
    bands: dict[int, list[tuple[float, tuple[float, float]]]] = {}
    for c in clumps:
        bands.setdefault(int((c[0] * -wy + c[1] * wx) // LEE_BAND_FT), []).append((c[0] * wx + c[1] * wy, c))
    return [c for band in bands.values() for u, c in band if u <= min(v for v, _ in band) + LEE_DEPTH_FT]


_COMPASS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def woodland_offsheet(plan: SitePlan) -> dict[str, Any]:
    """The record a roll carries when its worked wood stands OFF the sheet (feature 287, plan D11 - a DEPARTURE, raised with
    the GM): the wood's bearing from the settlement - up the fall, the nearest hill beyond the fields where
    research/vegetation/220 puts a village's fuel wood ("houses, then fields, then the hill and wild land beyond") - as a
    compass point and in degrees, and the parcels rolled.

    WHY A RECORD AND NOT A PARCEL. Where no legal ground for a parcel lies inside the sheet (Sawada and Kashikawa rolled
    none), the ways to draw one ON it all change what the feature is: a parcel that sets the frame (against the GM's frame
    rule - the commons never set it), a parcel under the legibility floor, or one on the crop's set-back. The wood is not
    missing - the record says it is beyond the sheet's edge, and which way. The alternative forms were priced in the woods
    design (`specs/287-placer-guarantees/design/design-woods.json`, `impossible`); the GM chooses between them."""
    ux, uy = -plan.fall[0], -plan.fall[1]
    deg = math.degrees(math.atan2(ux, -uy)) % 360.0  # compass: 0 = north, screen y points down
    return {"bearing": _COMPASS[int((deg + 22.5) // 45.0) % 8], "bearing_deg": round(deg, 1), "parcels": plan.woodland_patches}


def woodland_on_the_sheet(s: Settlement, plan: SitePlan, polys: list[Any]) -> list[Any]:
    """The parcels the scan found, as they are - and where it found none of the parcels the plan rolled, the wood recorded
    beyond the sheet with its bearing (`meta.woodland_offsheet`, plan D11), so a roll either draws a wood or says where
    it stands."""
    if plan.woodland_patches and not polys:
        s.M["meta"]["woodland_offsheet"] = woodland_offsheet(plan)
    return polys


def against_the_belt(dented: Sequence[tuple[float, float]], groves: Sequence[Any], wind: tuple[float, float], half: float) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """The against-the-belt copse's box and anchors (lifted from `stage_hinterland`, feature 291: no pool map rolls the
    siting once Mizuguchi rolls linear, so its lines are tested here with plain inputs).

    The box is the belt's own footprint (`dented`), stood off the houses so the two stands read as one wood at its back.
    The anchors are on its LEE side of that face: the reach is centered `half` of it leeward of each lee crown, so a copse
    crown stands 0 to `COPSE_BELT_REACH_FT` leeward and never windward of the face - at the belt's thin end a band's one or
    two crowns are its lee face, and a copse anchored round them stood beyond its windward side (Mizuguchi, two crowns)."""
    bx = [q[0] for q in dented]
    by = [q[1] for q in dented]
    box = [(min(bx), min(by)), (max(bx), min(by)), (max(bx), max(by)), (min(bx), max(by))]
    belt = [(float(c[0]), float(c[1])) for g in groves if g.get("role") == "windbreak" for c in g.get("clumps") or []]
    return box, [(x - wind[0] * half, y - wind[1] * half) for x, y in lee_face(belt, wind)]


def copse_seat(
    siting: str, dented: Sequence[tuple[float, float]], groves: Sequence[Any], wind: tuple[float, float], half: float, box: Any, near: tuple[Any, ...], brook: Any
) -> tuple[Any, tuple[Any, ...]]:
    """The copse's box and its reach: the dooryard copse's as given, or - sited against the belt, where it has one - the
    belt's box and its lee anchors at `half` (`against_the_belt`). Lifted from `stage_hinterland` (feature 291)."""
    if siting == "against_the_belt" and dented:
        box, anchors = against_the_belt(dented, groves, wind, half)
        return box, (anchors, half, brook)
    return box, near


def stage_hinterland(s: Settlement, plan: SitePlan) -> None:
    """The marsh, then scrub and rough grazing.

    Ground cover fills what is left, so it runs after everything it must avoid; it reads the drawn features as
    obstacles rather than reserving anything from them. Three moves, in order: the reed marsh at the wet toe,
    its inner edge following the fan's foot along the collector (T30); then the coppice patches are SCANNED (not
    yet drawn) and the shelter belt is computed, both from the houses as they stand; then the scrub is scattered
    with every wood as a soft keep-out - brush and pine stop at a wood's line and at the marsh, grass grades
    into them over one shared feather (T12, T34, T35). The floor of a worked village wood was kept clear, so no
    scrub stands under its crowns.

    The non-arable ground: reed marsh at the wet toe, cut-over scrub everywhere else.

    One engine call, because the engine already knows the doctrine (China-first: the south-China rice
    hills were stripped for fuel and timber over centuries, so the DOMINANT cover past the fields is
    scrub, not forest). It runs after the structures so the scatter skips them, and before the woods
    so the woodland patches draw on top of the scrub they stand in.

    Steps:
        l7r.diagram.hamletgen.hinterland.belt.belt_polygon
        l7r.diagram.hamletgen.hinterland.frame.scatter_frame
        l7r.diagram.settlement.Settlement.hinterland
        l7r.diagram.hamletgen.homesteads.fixtures.farmstead_fixtures
        l7r.diagram.hamletgen.homesteads.bamboo.household_bamboo
        l7r.diagram.hamletgen.hinterland.bamboo.bamboo_seats
        l7r.diagram.hamletgen.hinterland.stages.plant_the_belt
        l7r.diagram.hamletgen.hinterland.frame.frame_for
    """
    # THE BELT IS COMPUTED HERE, two stages before it is drawn, so the scrub can keep out of it
    # (T34): the belt derives from the houses alone, which are final by now, and `stage_woodland`
    # recomputes the same polygon. Woody scatter stops at the belt's line; grass grades into it.
    # EVERY WOOD, not only the belt (T35, GM 2026-08-27: "Did you only make it not overlap with the
    # windbreak forest and then keep it overlapping with the other forests or something?"). The
    # coppice patches are scanned here too - the scan keeps off the marsh, so the marsh is drawn
    # first, then the patches are found, then the scrub is scattered with every wood as a soft
    # keep-out. `stage_woodland` draws the patches from `plan.woodland_polys`.
    plan.belt = belt_polygon(s, plan)
    # THE SCATTER THROWS ONLY INSIDE A PREDICTED FRAME (feature 224): set before each scatter from what is known then -
    # the marsh before the coppice and the pocket exist, the commons after them - and kept for finish()'s breach record.
    s._scatter_frame = scatter_frame(s, plan)
    s.hinterland(commons=False)
    plan.woodland_polys = woodland_on_the_sheet(s, plan, open_ground_patches(s, plan, plan.woodland_patches))
    # ...and the bamboo stands (T47), seated now for the same reason: a stand is a wood, and the
    # scrub keeps out of it. Drawn by `stage_bamboo`, after the belt.
    farmstead_fixtures(s, plan, s.M.get("houses", []))  # T53-T59: the privies, woodpiles, heaps, baths, coops, shrines, persimmons - before the bamboo, which keeps off them
    plan.bamboo_polys += household_bamboo(s, plan, s.M.get("houses", []))  # T49: after the web and the board, before the scrub
    plan.bamboo_polys += bamboo_seats(s, plan)
    # THE BELT IS PLANTED, AND THEN THE VIEW IS DECIDED - ONCE (feature 287, M6). The belt's inner face is the last thing
    # that sets the frame (`crop_boxes`, GM 2026-08-26), and nothing after this line sets it, so the view the crop will
    # take is known here: `frame_for` - the crop's own body over the crop's own boxes and the ground it reserves - into
    # `plan.view`, which `stage_frame` sets exactly. The scrub below throws within that view (not a prediction of it), and
    # the woods' rules that read the picture read it. The polygon is recomputed first, as `stage_woodland` used to: the
    # marsh is laid now, and the band keeps off it.
    plan.belt = belt_polygon(s, plan)
    plant_the_belt(s, plan)
    plan.view = frame_for(s, plan)
    s._scatter_frame = scatter_frame(s, plan)

    s.hinterland(marsh=False, soft_extra=[*([plan.belt] if plan.belt else []), *plan.woodland_polys, *plan.bamboo_polys])
    # ...AND NO HOLES IN THE COUNTRYSIDE (feature 287, woods W11): over the decided view, the ground nothing covers - the
    # parcels and the bamboo still to be drawn counted as cover - is clothed as rough grazing until it is at most the rule's
    # share (`fill_the_holes`, asking `bare_cells`, the rule's one predicate). The stages after this only add cover.
    s.fill_the_holes(plan.view, [*plan.woodland_polys, *plan.bamboo_polys])
    s._scatter_frame = None  # the later scatters (a stand's understory, a hand call) throw whole


def stage_bamboo(s: Settlement, plan: SitePlan) -> None:
    """The bamboo stands.

    A take-yabu is a clonal thicket with a hard edge - a stand, not a seasoning - and a culm is inches across,
    so at this scale bamboo is drawn as a STAND-LEVEL glyph: the stand's position and extent to scale, the marks
    inside symbolic (the convention of Japan's own topographic legend, which gives bamboo its own symbol beside
    broadleaf and conifer). Seated by the previous stage in the farmsteads or at the settlement's edge behind its
    back row (feature 280 M49: not at the field margin), per the `bamboo` knob; drawn here, after the belt, over scrub that already kept out of it. Before
    this stage existed bamboo was 20% of the belt's crowns, one six-foot culm at a time, and invisible.

    The bamboo stands, drawn on the seats `stage_hinterland` scanned (T47). After the belt, so the
    stand-level glyph lies over the scrub that already kept out of it; `meta.bamboo` records the roll
    so the gate can hold "declared and drawn".

    Steps:
        l7r.diagram.settlement.Settlement.bamboo_stand
    """
    s.M["meta"]["bamboo"] = plan.bamboo
    s.M["bamboo_stands"] = []  # the pending seat-time records (T49) are replaced by the drawn ones
    for k, (role, ring) in enumerate(zip(plan.bamboo_roles, plan.bamboo_polys, strict=True)):
        # ...A HOMESTEAD STRIP NAMES ITS HOUSE (feature 287, homes H01): the owner `household_bamboo` recorded at seating
        # (`plan.bamboo_of`, by the stand's index) goes on the drawn record as `of`, as every other farmstead part's does
        if s.bamboo_stand(ring, role=role) and k in plan.bamboo_of:
            s.M["bamboo_stands"][-1]["of"] = [round(float(plan.bamboo_of[k][0]), 1), round(float(plan.bamboo_of[k][1]), 1)]


def stage_woodland(s: Settlement, plan: SitePlan) -> None:
    """The woodland commons.

    Managed coppice on ground nothing else wanted, drawn on the parcels the previous stage scanned - so the
    scrub has already kept out of them. Each parcel is an irregular ring inside the reach its keep-outs were
    tested at, never a rectangle (T36): an iriai wood's edge was a line the villages agreed or were given, bent to
    the ground, and the wood was governed by rules rather than parcel lines (research/vegetation/140). That the line
    followed ridge, stream and path is a GUESS - no page read says so.

    A few managed-woodland patches on the high, far ground - the green EXCEPTION to the scrub.

    The windbreak belt was COMPUTED before the scan, so the two woods do not merge (`woodland_clear_of_grove` requires a
    coppice patch to keep off every clump of the fengshui grove, or the two read as one indistinct green mass), and is
    planted by `stage_hinterland` before the view is decided (feature 287, M6).

    Steps:
        l7r.diagram.settlement.Settlement.commons
    """

    # The patches were SCANNED in `stage_hinterland` (T35) - before the scrub, so the scrub kept out
    # of them; the scan needs the marsh drawn and nothing this stage adds. Drawn here, over open ground.
    for patch in plan.woodland_polys:
        stock_woodland(s, patch)


def stock_woodland(s: Settlement, patch: Sequence[Any]) -> None:
    """One woodland parcel, NEVER UNDER-STOCKED (feature 287, woods W13). The scan offered the parcel on its room
    (`woodland_room` at `WOODLAND_MIN_CROWNS`), and the farmstead fixtures, the bamboo, the belt and the scrub are laid
    between the scan and this draw - so the room is asked again HERE, on the ground as it now stands, immediately before
    `commons` stocks the parcel: nothing is recorded between the two, so where the throws seat short, the room `commons`
    stocks from is this one. A parcel whose room the later fixtures have taken under the floor is not drawn as a wood of
    a few trees on grass: its ground is clothed as rough grazing, as `fill_the_holes` clothes bare ground, and the map
    records it (`meta.woodland_regraded`). Measured over cohort seeds 1-60 on 2026-09-29: no parcel's room was re-read
    at the draw and the fewest crowns a wood recorded was 134, so the refusal is a guarantee, not a path any map takes."""
    from l7r.diagram.settlement.land.cover import WOODLAND_MIN_CROWNS  # noqa: PLC0415 - kept beside its one use

    if len(s.woodland_room(patch)) < WOODLAND_MIN_CROWNS:
        s.M["meta"].setdefault("woodland_regraded", []).append([round(float(v), 1) for v in ring_box(patch)])
        s.commons(patch, role="grazing")
        return
    s.commons(patch, role="woodland")


def ring_box(ring: Sequence[Any]) -> tuple[float, float, float, float]:
    """A ring's (x0, y0, x1, y1)."""
    xs, ys = [float(q[0]) for q in ring], [float(q[1]) for q in ring]
    return (min(xs), min(ys), max(xs), max(ys))


def dent_around(belt: Sequence[tuple[float, float]], pocket: tuple[float, float, float, float]) -> list[tuple[float, float]]:
    """The belt's outline with every vertex inside the title's `pocket` pushed 6 px out of it, to the nearest side - the
    dent `plant_the_belt` plants and the against-the-belt copse is boxed by (one body, so the two cannot differ)."""
    out: list[tuple[float, float]] = []
    for bx, by in belt:
        if pocket[0] <= bx <= pocket[2] and pocket[1] <= by <= pocket[3]:
            cands = ((pocket[0] - 6.0, by), (pocket[2] + 6.0, by), (bx, pocket[1] - 6.0), (bx, pocket[3] + 6.0))
            bx, by = min(cands, key=lambda q, _x=bx, _y=by: (q[0] - _x) ** 2 + (q[1] - _y) ** 2)
        out.append((bx, by))
    return out


def plant_the_belt(s: Settlement, plan: SitePlan) -> None:
    """The shelter belt, planted - the LAST frame-setting feature, so `stage_hinterland` plants it just before it decides
    the view (feature 287, M6): the belt's inner face sets the frame (GM 2026-08-26, `crop_boxes`), so the view cannot be
    decided before the belt stands, and every rule that reads the view is placed after it.

    Sited from the wind and the cluster it shelters, so it needs the cluster finished. Its canopy is deferred to
    the flush at the end - drawn here it would be painted over by nothing - and its crowns are filtered against every
    structure the belt keeps off (`village_grove`'s keep-outs: the houses, yards, gardens, byres, sheds, wells, shrines,
    ponds, the crops, the water, the lanes), every one of which is standing when this runs. Nothing seated after it - the
    woodland parcels drawn, the scrub, the bamboo stands, the copse, the decks - is in that list, so planting it here
    rather than in `stage_windbreak` changes what it is filtered against not at all.

    The communal fengshui belt behind the cluster, shaped to the houses that actually landed.

    A nucleated settlement shelters behind ONE grove rather than per-house belts, and the belt must
    do two things the gate measures: stand on the WINDWARD side of the house centroid, and EMBRACE
    the cluster (a substantial belt within 150 px of a farmhouse - "far corner masses alone are
    decoration"). Both fall out of deriving it from the houses: the belt is a band offset into the
    wind from the cluster's own centroid, spanning the cluster's width across the wind, ragged along
    its edges because a grove hugs the land and is not a ruled wall.
    """
    if not plan.belt:
        return
    # ...DENTED AROUND THE TITLE'S POCKET. `stage_woodland` reserves blank ground for the map's name
    # (`title_pocket`) and keeps the woods out of it, but the BELT is drawn later and honors
    # nothing - `village_grove` takes only a polygon, with no keep-out list - so on a tightly framed
    # map the belt simply covered the reservation and `title()` had nowhere clear to sit (seed 8's
    # polder, 3 of 4 falls). Pushing the belt's vertices out of that rectangle costs the band a
    # local dent where a hamlet's own name goes, which is cheaper than the alternative of moving a
    # windbreak that is correct on every other count.
    # ...AND CLAMPED TO THE FRAME THE CROP WILL SET (settlement-review, Mizuguchi 2026-08-17). Soft
    # cover clips at the map edge on purpose - the commons and the marsh trail off as "more wild
    # ground this way" - but a settlement's own PLANTED windbreak is not wild ground: it is a belt of
    # finite depth that the hamlet made, and a belt sliced by the page edge along its whole length
    # reads as woodland running off-map instead. On Mizuguchi the re-pack pulled the crop's bottom up
    # 37 px while the belt's canopy still reached 62 px below it, so 58 of 217 clumps touched the
    # edge and 23 were drawn WHOLLY outside the viewBox - ink emitted where nothing can ever see it,
    # which is a record-vs-drawing mismatch as much as a composition one.
    #
    # The clamp can be exact rather than a guess, because every HARD feature that sets the crop is
    # already placed by the time this stage runs: ask `_crop_boxes` - the very source
    # `crop_to_content` reads - and hold the belt inside that box. Same-source doctrine, and the same
    # move the title-pocket dent above already makes: push the vertices, keep the belt.
    #
    # SINCE FEATURE 287 (M6) the frame is `frame_bounds` - the one function the view is decided by, asked just before the
    # decision this belt is the last input to: the crop's own boxes AND the ground the frame reserves as content (an
    # outside title pocket, the confluence, the brook beside the field), which the old `_crop_boxes` clamp did not know.
    _fx0, _fy0, _fx1, _fy1 = frame_bounds(s, plan)
    _tp = title_pocket(s, plan)
    _dented = dent_around(plan.belt, _tp)
    # THE BELT ITSELF IS NOT MOVED - the CLUMPS are held inside the frame instead, via
    # `village_grove(within=...)`. Clamping the polygon was tried first and is wrong, recorded so it
    # is not retried: the outline's bbox center is what `village_grove` records as the grove's `x`,`y`
    # and what `village_windbreak_on_windward_side` judges, so pulling vertices inward walks that
    # center toward the cluster - cohort seeds 19 and 28 crossed to the LEE side, and a guard on the
    # polygon's centroid did not catch it because the centroid is not the point the check reads. The
    # belt's position is its meaning; only its leaves needed containing.
    # The frame ITSELF, with no inset: `village_grove` skips only a clump lying WHOLLY outside it, so
    # the belt still clips at the page edge the way every other soft cover does (and the way
    # `research/presentation.html` requires) and only ink nobody can see is dropped. An inset was
    # tried first and cost Sawada 46% of its canopy - see the comment at the skip.
    # ...AND THE WINDWARD EDGE FOLLOWS THE BELT'S OWN FACE (GM 2026-08-26, feature 133 T10). The
    # frame now includes the belt's inner face plus CROP_MARGIN (`crop_boxes`, "windbreak face"),
    # so on the wind axis the `within` window is opened to the whole band and `face_margin` does the
    # precise trim from the face the clumps actually form - the other three edges keep the hard
    # frame exactly as before. Without this the belt was clamped to a frame set by the houses, and
    # a belt standing off the plots for their sun fell outside it (85% of Inashiro's clumps).
    _bxs = [q[0] for q in _dented]
    _bys = [q[1] for q in _dented]
    _wx, _wy = plan.wind
    # ...ON EVERY AXIS THE WIND HAS A SHARE OF (settlement-review of Inashiro, feature 261): a diagonal wind wraps the belt
    # round two sides, and opening only the dominant axis - the x axis, on the tie a northwest wind makes - left the north
    # arm clamped to the frame the houses set, 28 ft deep behind the northernmost farmhouse
    if abs(_wx) > 1e-6:
        _fx0, _fx1 = (min(_fx0, min(_bxs) - 30.0), _fx1) if _wx < 0 else (_fx0, max(_fx1, max(_bxs) + 30.0))
    if abs(_wy) > 1e-6:
        _fy0, _fy1 = (min(_fy0, min(_bys) - 30.0), _fy1) if _wy < 0 else (_fy0, max(_fy1, max(_bys) + 30.0))
    # ...ON THE PAGE IT WILL BE DRAWN ON, DEEP, WHOLE AND WITHIN REACH OF THE HOUSES (feature 287, woods W16-W19; plan D8):
    # `belt_page` answers the view `frame_for` decides from the crowns the belt keeps, so the planter judges the depth, the
    # holes and the hook on that page; and every crown stands within the band's reach of a farmhouse (`meta.belt_reach`)
    _reach = s.M["meta"].get("belt_reach")
    _near = ([(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []], float(_reach)) if _reach else None
    s.village_grove(
        _dented,
        role="windbreak",
        within=(_fx0, _fy0, _fx1, _fy1),
        face_margin=CROP_MARGIN,
        reserved=_tp,
        near=_near,
        wind=wind_unit(plan.windward),
        page=belt_page(s, plan, round(14.0 * s.bscale, 1)),
        reach=float(_reach) if _reach else None,
        keep_off=reserved_seats(s),  # every household's share of the wood floor stands free for the copse (woods W25)
    )


def stage_windbreak(s: Settlement, plan: SitePlan) -> None:
    """The copse among the homes - the shelter belt's companion wood.

    The belt itself is planted by `stage_hinterland` (`plant_the_belt`), before the view is decided, because its inner
    face sets the frame (feature 287, M6). What is left here is the copse, which sets no frame: seated after the woods
    and the ground cover, against the belt's recorded crowns, so the two stands read as two.

    Steps:
        l7r.diagram.hamletgen.hinterland.frame.title_pocket
        l7r.diagram.settlement.Settlement.village_grove
    """
    _seats = reserved_seats(s)
    if not plan.belt and not _seats:
        return
    _dented = dent_around(plan.belt or [], title_pocket(s, plan))
    # The COPSE fills the leafy gaps AMONG the homes, over the house cloud. That is only reasonable
    # ground because `stage_homesteads` now bounds every seat to the cluster band: over a cloud with
    # a strewn farmstead in it, this became a scatter across 1,446 x 1,244 px - a wood over the whole
    # settlement rather than a copse among the houses, and every clump an obstacle the map's own
    # title could then find no room around (`title_clear_of_features`).
    houses = s.M.get("houses", [])
    xs = [h["x"] for h in houses]
    ys = [h["y"] for h in houses]
    pad = 16.0
    # WHERE THE COPSE SITS IS A KNOB (feature 152 T20, constitution XII). Both forms are what a
    # back-village planting is: trees threading the homesteads, or a stand tucked against the shelter
    # belt at the settlement's back. A settlement-review named the pair as a knob candidate while
    # reporting Sawada's copse drawn INSIDE the belt - which is the second form happening by accident,
    # unrecorded, on a map that had rolled the first. Rolled per settlement from the map's own seed, so
    # two hamlets differ at a glance, which is the point of a knob rather than a house style.
    # THE CLUSTER'S OWN FOOTPRINT, NOT ITS BOUNDING BOX (feature 230, settlement-review pass 6). A hamlet
    # seated on a diagonal margin is a RIBBON - Inashiro's is 969 x 231 ft - and its axis-aligned box is
    # 617 x 875, most of which is the empty bay beside it. Scattering "among the houses" over that box put 86%
    # of the copse's clumps more than 90 ft from any house and tripled the wood to 12.4 acres, so the sheet read
    # as a house row with a wood tucked against its side rather than as houses threaded through trees. The seat
    # already carries the frame the cluster was laid in; measure the cloud in THAT frame and the ground is the
    # settlement's own shape. (The windbreak beside it has always used its oriented footprint.)
    _al = cast("tuple[float, float]", plan.seat.get("along", (1.0, 0.0))) if plan.seat else (1.0, 0.0)
    _ou = cast("tuple[float, float]", plan.seat.get("out", (0.0, 1.0))) if plan.seat else (0.0, 1.0)
    _as = [x * _al[0] + y * _al[1] for x, y in zip(xs, ys, strict=False)]
    _os = [x * _ou[0] + y * _ou[1] for x, y in zip(xs, ys, strict=False)]
    _a0, _a1, _o0, _o1 = min(_as) - pad, max(_as) + pad, min(_os) - pad, max(_os) + pad
    _box = [
        (_a0 * _al[0] + _o0 * _ou[0], _a0 * _al[1] + _o0 * _ou[1]),
        (_a1 * _al[0] + _o0 * _ou[0], _a1 * _al[1] + _o0 * _ou[1]),
        (_a1 * _al[0] + _o1 * _ou[0], _a1 * _al[1] + _o1 * _ou[1]),
        (_a0 * _al[0] + _o1 * _ou[0], _a0 * _al[1] + _o1 * _ou[1]),
    ]
    # ...AND WITHIN REACH OF WHAT IT STANDS AMONG (feature 261, settlement-review of Kashikawa, Inashiro and Mizuguchi).
    # The oriented box above is the cluster's extent, not its ground: a crescent or a cloud seat leaves an empty bay
    # inside the box, and the copse filled it as a wood 500 x 450 ft across that hid the belt behind it. So a dooryard
    # copse clump stands within `COPSE_HOUSE_REACH_FT` of a house, and an against-the-belt one within
    # `COPSE_BELT_REACH_FT` of a belt crown - scattered over the belt's axis-aligned box it spread across the whole
    # cluster wherever the belt wrapped a diagonal ribbon.
    # ...AND ON ITS OWN BANK: a clump near a house across the brook is not among the houses (settlement-review of Kashikawa,
    # feature 261: three clumps stood across the water from every farmhouse, within reach only as the crow flies)
    _brook = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for f in s.M.get("streams") or [] for a, b in zip(f.get("poly") or [], (f.get("poly") or [])[1:], strict=False)]
    # ...AT THE REACH ITSELF (feature 287, woods W01): the manifest records a clump to 0.1 px, and Kashikawa's clump at
    # (1069.3, 1011.6) stood 89.99 ft from its house as placed and 90.01 as recorded (269 E2), which a 0.1 px margin here
    # covered. `village_grove` now decides every seat at the record's grain, so the point it asks the reach of is the point
    # the manifest carries, and no margin stands in for the rounding.
    _copse_near: tuple[Any, ...] = ([(float(x), float(y)) for x, y in zip(xs, ys, strict=False)], s.px(COPSE_HOUSE_REACH_FT), _brook)
    _dooryard = _copse_near  # a household's reserved seat is its dooryard's on either siting (woods W25), asked of it as planted
    # the belt's own footprint and its lee anchors, where the copse is sited against the belt (`copse_seat`)
    _box, _copse_near = copse_seat(plan.copse_siting, _dented, s.M.get("village_groves") or [], plan.wind, s.px(COPSE_BELT_REACH_FT) / 2.0, _box, _copse_near, _brook)
    # THE COPSE IS THE HOMESTEADS' WOODS, SIZED BY THEM (269 B26; research/vegetation/210): each homestead's wood - its
    # windward grove and its share of the copse together, which the record knows as one - is rolled within the 1684
    # register's range, and the copse is filled to what the belt leaves of their sum. It used to be whatever one grid's
    # gaps gave: 750-1,700 sq ft a homestead beside a belt share of 3,700-9,200, so four of five maps drew less wood
    # than the register's smallest household.
    # ...WITHIN WHAT THIS GROUND CAN HOLD (feature 294 B9, `wood_goal`): the copse is filled to its capacity, each homestead's
    # wood rolled within the part of the register's range between what the belt and the groves give and what the ground holds,
    # and the copse trimmed back to the roll - so the size recorded as rolled is the size drawn (Sawada drew 60% of its roll).
    _rolls = [s._hjit(float(h["x"]), float(h["y"]), 210.0) for h in houses]
    _ft2 = s.px(1.0) ** 2  # px^2 per sq ft
    # ...AND WHAT EACH FARM'S OWN GROVE ALREADY HOLDS (feature 291): where the farms carry their own groves the record's one
    # wood is that grove and its share of the copse, so the copse is filled to what the groves leave (settlement-review of
    # Kashikawa: filled to the belt's remainder alone, the drawn wood ran ~17,400 sq ft a house against 14,872 rolled)
    _given = wood_canopy(s, ("windbreak",)) + farm_grove_area(s)
    _rolled: list[float] = [copse_goal(_rolls, _given, 0.0, 0.0, _ft2)[1]]  # the mean rolled wood a homestead, set again at the fill

    def _goal_for(capacity: float, kept: float) -> float:
        goal, _rolled[0] = copse_goal(_rolls, _given, kept, capacity, _ft2)
        return goal

    # ...EVERY HOUSEHOLD'S RESERVED SHARE FIRST (feature 287, woods W25; plan D9): the seats the seating reserved for each
    # household's share of the floor (`wood_share`) are planted before any other clump, on either siting - each within its
    # own house's dooryard reach, not the siting's `near` - and the goal counts them, so the grid fills only the rest.
    # ...AND OFF THE SEATED BAMBOO (feature 280, `bamboo_rings`): every stand was seated clear of the reserved seats
    # (`stand_spares_seats`), so the keep-out refuses only the grid's own clumps.
    s.village_grove(
        _box,
        role="copse",
        dense=False,
        reserved=title_pocket(s, plan),
        near=_copse_near,
        area_from=_goal_for,
        seats=_seats,
        seat_near=_dooryard,
        bamboo_rings=plan.bamboo_polys,
    )  # the map's name has ground reserved; the copse honors it like the belt does
    s.standing.reserved.release_seats()  # planted: the seats stand as the copse's clumps now (feature 287 M8, `overlap/reserved.py`)
    # ...AND NEVER UNDER THE REGISTER'S FLOOR (feature 287, woods W25; plan D9), BY CONSTRUCTION: each household is seated only
    # with copse seats reserved that cover `HOMESTEAD_WOOD_FT2`'s floor (`wood_share`), and since the registry of what
    # stands (plan M8, `overlap/reserved.py`) keeps the web's lanes, the title's pocket, the shared byres and the parts laid
    # after the seating off them, every seat is planted where it was reserved (cohort 1-60 and the pool: 0 of 20,454 seats
    # lost, against 17% before; the lowest drawn wood 9,401 sq ft a homestead). The lee top-up that made up a short floor
    # here - it fired on none of cohort 1-60 once the seats were planted first - is retired with the check that triggered
    # it (R8).
    # RECORD WHAT THE GROUND GAVE, beside what the knob asked for (settlement-review, feature 230 pass 12; the same
    # move `place_kosatsuba` makes with `kosatsuba_well_ft`, and for the same reason). `copse_siting` says
    # `among_the_houses` on four of the five pool maps, and what that produces depends entirely on whether the
    # settlement HAS interior gaps: Inashiro seats 10 clumps with every one inside the house cloud, while Kuwabata's
    # single row on a dike head has no interior at all and gets 3. A reader - or a later check - reading the knob
    # alone is told five maps did the same thing. These two numbers say what each one actually drew, and they
    # claim nothing: a count and a distance, not a second label.
    _cop = [c for g in s.M.get("village_groves") or [] if g.get("role") == "copse" for c in g.get("clumps") or []]
    _hs = [(float(h["x"]), float(h["y"])) for h in s.M.get("houses") or []]
    if _cop and _hs:
        _near = sorted(min(math.dist((float(c[0]), float(c[1])), h) for h in _hs) for c in _cop)
        s.M["meta"]["copse_clumps"] = len(_near)
        s.M["meta"]["copse_house_ft"] = round(_near[len(_near) // 2] * float(s.M["meta"].get("ftpx") or 1), 1)
    # ...and what the woods came to beside what was rolled, so a copse the ground could not hold is a number, not a silence
    if _hs:
        s.M["meta"]["homestead_wood_ft2"] = {"rolled": round(_rolled[0]), "drawn": round(homestead_wood_drawn(s))}


def wood_canopy(s: Settlement, roles: Sequence[str]) -> float:
    """The ground (px^2) the village groves of `roles` cover - each role's crowns unioned at its clumps' radius, on the page
    and off it (the belt's trees stand whether the page shows them or not), the roles summed."""
    total = 0.0
    for role in roles:
        area = CanopyArea(2.0 * s.bscale)
        for g in s.M.get("village_groves") or []:
            if g.get("role") == role:
                for c in (g.get("clumps") or []) + (g.get("clumps_offpage") or []):
                    area.add(float(c[0]), float(c[1]), float(g.get("r") or 0.0))
        total += area.area
    return total


def homestead_wood_drawn(s: Settlement) -> float:
    """THE ONE PREDICATE of the homesteads' wood floor (feature 287, woods W25; research/vegetation/210): the wood each
    homestead keeps, in sq ft - the belt, the copse and each farm's own grove (feature 291) together, shared among the
    houses - which the register puts at no less than `HOMESTEAD_WOOD_FT2[0]`. `meta.homestead_wood_ft2.drawn` records it."""
    houses = s.M.get("houses") or []
    return (wood_canopy(s, ("windbreak", "copse")) + farm_grove_area(s)) / s.px(1.0) ** 2 / len(houses) if houses else 0.0


def farm_grove_area(s: Settlement) -> float:
    """The ground (px^2) the farms' own grove bands cover (feature 291): each band's box, as recorded."""
    return sum(float(g["w"]) * float(g["h"]) for g in s.M.get("groves") or [] if g.get("w") and g.get("h"))
