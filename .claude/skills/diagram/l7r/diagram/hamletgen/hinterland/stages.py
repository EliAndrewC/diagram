"""Split from hamletgen/hinterland.py by feature 173 - see this package's CLAUDE.md for the index."""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

from ..homesteads import farmstead_fixtures, household_bamboo
from ..plan import SitePlan
from .bamboo import bamboo_seats
from .belt import belt_polygon
from .frame import title_pocket
from .parcels import CROP_MARGIN, open_ground_patches

# ---- STAGE 7: the ground between everything ------------------------------------------------------


def stage_hinterland(s: Settlement, plan: SitePlan) -> None:
    """The non-arable ground: reed marsh at the wet toe, cut-over scrub everywhere else.

    One engine call, because the engine already knows the doctrine (China-first: the south-China rice
    hills were stripped for fuel and timber over centuries, so the DOMINANT cover past the fields is
    scrub, not forest). It runs after the structures so the scatter skips them, and before the woods
    so the woodland patches draw on top of the scrub they stand in."""
    # THE BELT IS COMPUTED HERE, two stages before it is drawn, so the scrub can keep out of it
    # (T34): the belt derives from the houses alone, which are final by now, and `stage_woodland`
    # recomputes the same polygon. Woody scatter stops at the belt's line; grass grades into it.
    # EVERY WOOD, not only the belt (T35, GM 2026-08-27: "Did you only make it not overlap with the
    # windbreak forest and then keep it overlapping with the other forests or something?"). The
    # coppice patches are scanned here too - the scan keeps off the marsh, so the marsh is drawn
    # first, then the patches are found, then the scrub is scattered with every wood as a soft
    # keep-out. `stage_woodland` draws the patches from `plan.woodland_polys`.
    plan.belt = belt_polygon(s, plan)
    s.hinterland(commons=False)
    plan.woodland_polys = open_ground_patches(s, plan, plan.woodland_patches)
    # ...and the bamboo stands (T47), seated now for the same reason: a stand is a wood, and the
    # scrub keeps out of it. Drawn by `stage_bamboo`, after the belt.
    farmstead_fixtures(s, plan, s.M.get("houses", []))  # T53-T59: the privies, woodpiles, heaps, baths, coops, shrines, persimmons - before the bamboo, which keeps off them
    plan.bamboo_polys += household_bamboo(s, plan, s.M.get("houses", []))  # T49: after the web and the board, before the scrub
    plan.bamboo_polys += bamboo_seats(s, plan)
    s.hinterland(marsh=False, soft_extra=[*([plan.belt] if plan.belt else []), *plan.woodland_polys, *plan.bamboo_polys])


def stage_bamboo(s: Settlement, plan: SitePlan) -> None:
    """The bamboo stands, drawn on the seats `stage_hinterland` scanned (T47). After the belt, so the
    stand-level glyph lies over the scrub that already kept out of it; `meta.bamboo` records the roll
    so the gate can hold "declared and drawn"."""
    s.M["meta"]["bamboo"] = plan.bamboo
    s.M["bamboo_stands"] = []  # the pending seat-time records (T49) are replaced by the drawn ones
    for role, ring in zip(plan.bamboo_roles, plan.bamboo_polys, strict=True):
        s.bamboo_stand(ring, role=role)


def stage_woodland(s: Settlement, plan: SitePlan) -> None:
    """A few managed-woodland patches on the high, far ground - the green EXCEPTION to the scrub.

    The windbreak belt is COMPUTED here, before the scan, and only DRAWN in the next stage. That
    split exists because the two woods must not merge: `woodland_clear_of_grove` requires a coppice
    patch to keep off every clump of the fengshui grove, or the two read as one indistinct green
    mass. The scan therefore has to know where the belt is going, but the belt has to be DRAWN late
    so its per-crown filter sees every structure already standing (the engine's DRAW ORDER rule).
    Computing early and drawing late satisfies both."""
    plan.belt = belt_polygon(s, plan)
    # The patches were SCANNED in `stage_hinterland` (T35) - before the scrub, so the scrub kept out
    # of them; the scan needs the marsh drawn and nothing this stage adds. Drawn here, over open ground.
    for patch in plan.woodland_polys:
        s.commons(patch, role="woodland")


def stage_windbreak(s: Settlement, plan: SitePlan) -> None:
    """The communal fengshui belt behind the cluster, shaped to the houses that actually landed.

    A nucleated settlement shelters behind ONE grove rather than per-house belts, and the belt must
    do two things the gate measures: stand on the WINDWARD side of the house centroid, and EMBRACE
    the cluster (a substantial belt within 150 px of a farmhouse - "far corner masses alone are
    decoration"). Both fall out of deriving it from the houses: the belt is a band offset into the
    wind from the cluster's own centroid, spanning the cluster's width across the wind, ragged along
    its edges because a grove hugs the land and is not a ruled wall. A copse scatter then fills the
    leafy gaps among the homes.

    Drawn LATE, after the ground cover and the woods, so its per-crown filter sees every structure
    already standing and no tree is drawn on a roof."""
    if not plan.belt:  # pragma: no cover - stage_woodland always computes it first
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
    # move the title-pocket dent above already makes: push the vertices, keep the belt. (Only
    # `stage_crossings` follows, and a footbridge sits on water well inside the frame, so it cannot
    # pull the box back out from under this.)
    _boxes = s._crop_boxes(city=False)
    _fx0 = min((b[0] for b in _boxes), default=0.0) - CROP_MARGIN
    _fx1 = max((b[1] for b in _boxes), default=float(s.W)) + CROP_MARGIN
    _fy0 = min((b[2] for b in _boxes), default=0.0) - CROP_MARGIN
    _fy1 = max((b[3] for b in _boxes), default=float(s.H)) + CROP_MARGIN
    _tp = title_pocket(s, plan)
    _dented = []
    for _bx, _by in plan.belt:
        if _tp[0] <= _bx <= _tp[2] and _tp[1] <= _by <= _tp[3]:
            _cands = ((_tp[0] - 6.0, _by), (_tp[2] + 6.0, _by), (_bx, _tp[1] - 6.0), (_bx, _tp[3] + 6.0))
            _bx, _by = min(_cands, key=lambda q: (q[0] - _bx) ** 2 + (q[1] - _by) ** 2)
        _dented.append((_bx, _by))
    # THE BELT ITSELF IS NOT MOVED - the CLUMPS are held inside the frame instead, via
    # `village_grove(within=...)`. Clamping the polygon was tried first and is wrong, recorded so it
    # is not retried: the outline's bbox center is what `village_grove` records as the grove's `x`,`y`
    # and what `village_windbreak_on_windward_side` judges, so pulling vertices inward walks that
    # center toward the cluster - cohort seeds 19 and 28 crossed to the LEE side, and a guard on the
    # polygon's centroid did not catch it because the centroid is not the point the check reads. The
    # belt's position is its meaning; only its leaves needed containing.
    # The frame ITSELF, with no inset: `village_grove` skips only a clump lying WHOLLY outside it, so
    # the belt still clips at the page edge the way every other soft cover does (and the way
    # `settlements/presentation.md` requires) and only ink nobody can see is dropped. An inset was
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
    if abs(_wx) >= abs(_wy):
        _fx0, _fx1 = (min(_fx0, min(_bxs) - 30.0), _fx1) if _wx < 0 else (_fx0, max(_fx1, max(_bxs) + 30.0))
    else:
        _fy0, _fy1 = (min(_fy0, min(_bys) - 30.0), _fy1) if _wy < 0 else (_fy0, max(_fy1, max(_bys) + 30.0))
    s.village_grove(_dented, role="windbreak", within=(_fx0, _fy0, _fx1, _fy1), face_margin=CROP_MARGIN)
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
    _box = [(min(xs) - pad, min(ys) - pad), (max(xs) + pad, min(ys) - pad), (max(xs) + pad, max(ys) + pad), (min(xs) - pad, max(ys) + pad)]
    if plan.copse_siting == "against_the_belt" and _dented:
        # the belt's own footprint, stood off the houses so the two stands read as one wood at its back
        _bx = [q[0] for q in _dented]
        _by = [q[1] for q in _dented]
        _box = [(min(_bx), min(_by)), (max(_bx), min(_by)), (max(_bx), max(_by)), (min(_bx), max(_by))]
    s.village_grove(_box, role="copse", dense=False)
