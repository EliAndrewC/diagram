"""THE POLDER ARCHETYPES - the reclaimed block, its dike, its flanks and the reed fringe outside them.

Split from `hamletgen/water.py` by feature 230 (constitution X clause 13); bodies verbatim.
See `CLAUDE.md` in this directory.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, knob_rng, point_in_poly, seg_intersect, segments_cross
from l7r.diagram.settlement.land.dikes import CREST_REACH, DIKE_GAP_HW, GAP_REACH, course_breaches, dike_band, dike_crest
from l7r.diagram.sitegen.geom import net_acres, poly_area
from l7r.diagram.waterfields import build_polder, clean_polder_parcels

from ..consts import (
    DIKEPOND_CONVERSION,
    POLDER_ARCHETYPES,
    POLDER_FABRIC,
    POND_LAYOUT_MOSAIC,
    WATERWARD_DEPTH,
    Poly,
    Pt,
)
from ..plan import SitePlan
from ..pondstock import reserve_sty_seat


def reservoir_clear_of_crop(pond: tuple[float, float, float, float], envelope: Sequence[Pt]) -> bool:
    """THE RULE (feature 287, water W46): no part of the reservoir's rim lies on the crop - its ellipse, as a polygon drawn
    just OUTSIDE the true ellipse, shares no ground with the envelope. Sixteen rim samples let a spike of the envelope
    through between two of them; a polygon does not. The seat below and its test read this one predicate."""
    from shapely.geometry import Polygon

    n = 96
    grow = 1.0 / math.cos(math.pi / n)  # the polygon's edges run outside the ellipse, so it covers every rim point
    ring = [(pond[0] + pond[2] * grow * math.cos(math.tau * k / n), pond[1] + pond[3] * grow * math.sin(math.tau * k / n)) for k in range(n)]
    return not Polygon(ring).intersects(Polygon([(float(p[0]), float(p[1])) for p in envelope]).buffer(0))


def reservoir_uphill_of_field(pond: tuple[float, float, float, float], envelope: Sequence[Pt], fall: Pt) -> bool:
    """THE RULE (feature 287, water W46): the source sits ABOVE what it waters - the reservoir's center is further up the
    fall than the field's highest point (research/archetypes polder siting; the soak test's own reading)."""
    return pond[0] * fall[0] + pond[1] * fall[1] < min(float(p[0]) * fall[0] + float(p[1]) * fall[1] for p in envelope)


def walk_pond_uphill(pond: tuple[float, float, float, float], envelope: list[Any], ux: float, uy: float, step: float = 12.0) -> tuple[float, float, float, float]:
    """The header reservoir SEATED uphill (against the fall) at the first step where it is clear of the crop AND above it.

    Lifted out of `stage_polder` by feature 219 so the walk is a unit test on a rectangle rather than a roll of a
    polder that needs it (seed 12 did; seeds 3, 8, 19 and 22 cleared first try). `pond` is (cx, cy, rx, ry).

    A SOLVED SEAT, NOT A BOUNDED WALK (feature 287, water W46). The walk used to stop after 60 steps with whatever it had,
    which on an envelope that needed more left the rim on the crop; and it tested 16 rim points, which a spike between
    two of them slipped through. Both predicates are asked at each step, and the steps are bounded by geometry rather
    than a count: once the rim's LOWEST point stands above the field's HIGHEST, the ellipse cannot meet the envelope and
    the center is uphill of it, so the seat is found at or before that step. `(ux, uy)` is the unit uphill direction."""
    fall = (-ux, -uy)
    top = min(float(p[0]) * fall[0] + float(p[1]) * fall[1] for p in envelope)
    reach = math.hypot(pond[2] * fall[0], pond[3] * fall[1])  # the ellipse's half extent along the fall
    last = max(0, math.ceil((pond[0] * fall[0] + pond[1] * fall[1] + reach - top) / step) + 1)
    for k in range(last + 1):
        seat = (pond[0] + ux * step * k, pond[1] + uy * step * k, pond[2], pond[3])
        if reservoir_clear_of_crop(seat, envelope) and reservoir_uphill_of_field(seat, envelope, fall):
            return seat
    raise AssertionError("unreachable: the last step stands the whole rim above the field")  # pragma: no cover - `last` is past the geometric bound


def dike_gaps_at_channels(ring: list[Any], channels: Any, sluices: Any) -> list[Any]:
    """The perimeter dike's gaps: the two sluices `build_polder` names, plus a gap WHEREVER a channel actually
    crosses the ring - a dug gap is what lets water through an earthwork, and a dike drawn straight over a running
    channel is the defect `polder_dike_gapped_at_sluices` named. A crossing within 30 ft of a gap already listed
    is that gap. Lifted out of `stage_polder` by feature 219 (a unit test on a square and two channels)."""
    gaps = list(sluices)
    for ch in channels:
        pts = ch["pts"]
        for i in range(len(pts) - 1):
            for k in range(len(ring)):
                a, b = ring[k], ring[(k + 1) % len(ring)]
                if segments_cross(tuple(pts[i]), tuple(pts[i + 1]), a, b):
                    hit = seg_intersect(tuple(pts[i]), tuple(pts[i + 1]), a, b)
                    if hit is not None and not any(math.hypot(hit[0] - g[0], hit[1] - g[1]) < 30 for g in gaps):
                        gaps.append(hit)
    return gaps


def inlet_to_rim(pts: list[Any], pond: tuple[float, float, float, float], envelope: Sequence[Pt]) -> list[Any]:
    """The feeder's points with its inlet ended ON the reservoir's rim, 2 ft inside it (feature 150 T51 - see `stage_polder`).

    ONLY THE STUB'S END MOVES (feature 287, water W44). Where `_polder_close` trimmed the stub away as an acute tail (a
    warped corner), the feeder's last point is a RING vertex inside the crop - and moving it to the rim dragged the ring
    off the corner the west toe had been snapped onto (Polder 12: the toe's end left 15.5 ft from any trunk). A last
    point inside the crop is kept, and the run to the rim is added after it."""
    sx, sy = float(pts[-1][0]), float(pts[-1][1])
    vx, vy = pond[0] - sx, pond[1] - sy
    lo, hi = 0.0, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        qx, qy = sx + vx * m, sy + vy * m
        if ((qx - pond[0]) / pond[2]) ** 2 + ((qy - pond[1]) / pond[3]) ** 2 > 1.0:
            lo = m
        else:
            hi = m
    vl = math.hypot(vx, vy) or 1.0
    rim = (round(sx + vx * hi + vx / vl * 2.0, 1), round(sy + vy * hi + vy / vl * 2.0, 1))
    return [*pts, rim] if point_in_poly(sx, sy, list(envelope)) else [*pts[:-1], rim]


def gaps_for_courses(gaps: Sequence[Any], courses: Sequence[Sequence[Pt]], crest: Sequence[Pt]) -> list[Any]:
    """`gaps` with one more wherever a course still breaches the crest (`course_breaches`) - each at the breach itself, and
    the course asked again until it breaches nowhere, so every course recorded when the dike is drawn crosses it only at
    a gap (feature 287, water W42). Asked half a foot stricter on both reaches than the rule, since the dike records its
    crest and gaps rounded to 0.1 px."""
    out = list(gaps)
    for course in courses:
        while hits := course_breaches(list(course), list(crest), [(float(g[0]), float(g[1])) for g in out], CREST_REACH + 0.5, GAP_REACH - 0.5):
            out.append(hits[0])
    return out


def stage_polder(s: Settlement, plan: SitePlan) -> None:
    """The POLDER field: a surveyed orthogonal grid diked out of standing water on flat ground.

    Not a variation on the comb - the opposite of it. A comb is grown around a head-race running down
    a slope and its shape follows the water; a polder is a planned block whose water enters at a
    corner, rings the module in a perimeter feeder, and drains to the low corner. `build_polder`
    returns `build_comb`-compatible keys on purpose, so `draw_comb_field` draws either.

    The SOURCE is a header reservoir OUTSIDE the dike above the high corner, charged through a sluice
    in the dike - not a brook running in over the crop, which is what a valley hamlet has.

    Steps:
        l7r.diagram.hamletgen.water.polder.fit_polder
        l7r.diagram.sitegen.geom.net_acres
        l7r.diagram.hamletgen.water.polder.walk_pond_uphill
        l7r.diagram.settlement.Settlement.draw_comb_field
        l7r.diagram.hamletgen.water.polder.dike_gaps_at_channels
        l7r.diagram.settlement.Settlement.perimeter_dike
        l7r.diagram.settlement.Settlement.apply_land_use
    """
    # BOTH polder archetypes come through here (feature 150): the fabric table sets the module and
    # the parcel mix, the knob sets the arrangement, and the dike-pond's overlay is applied once the
    # grid is drawn - see `POLDER_ARCHETYPES` in consts.py for why the dike-pond is a polder.
    fabric = POLDER_FABRIC[plan.field_archetype]
    mosaic = POND_LAYOUT_MOSAIC if plan.pond_layout == "mosaic" else 0.0
    net = fit_polder(plan, plan.spec.seed, fabric=fabric, mosaic=mosaic)
    plan.net = net
    plan.acres = net_acres(net, plan.ftpx)
    plan.envelope = [(round(x, 1), round(y, 1)) for x, y in net["envelope"]]
    s.field_polys.append(list(plan.envelope))
    s.meta(dry_furrows_vary=False)
    s.M["meta"]["field_archetype"] = plan.field_archetype
    s.M["meta"]["pond_layout"] = plan.pond_layout
    s.M["meta"]["water_source"] = "reservoir"
    s.M["meta"]["water_source_position"] = "corner_high"
    # THE HEADER RESERVOIR sits OUTSIDE the dike, above the block's high end, on the fall axis -
    # derived from the drawn envelope rather than offset from a corner, because which corner is
    # "high" depends on the bearing. It is the wild water the inlet sluice draws from.
    env = plan.envelope
    prx, pry = 82.0, 54.0
    # SEATED AT THE DIKE'S OWN INLET SLUICE, pushed straight out from the block. `build_polder` says
    # where the dike is cut for water (`dike_sluices`), and the reservoir is the body that sluice
    # draws from - so the link between them is the short square one Enokida draws, not a diagonal
    # across the block's whole head. Two earlier tries measured only in the fall frame: one blended
    # the high corner with the centroid and put the pond INSIDE the crop; the next centered it across
    # the block's head, and the inlet channel then ran so far that its field end dangled short of
    # the envelope (`watercourse_ends_reach_water`). The sluice is the anchor both ends agree on.
    # SEATED ON THE LINE THROUGH THE RING'S HEAD. `draw_comb_field` runs the inlet channel from the
    # pond to `net["sluice"]`, and `build_polder` puts the perimeter feeder's own head up to 70 px
    # away from that sluice, just outside the planted extent - so the ring's head dangled in bare
    # ground with the inlet water stopping short of it (`watercourse_ends_reach_water`, which is
    # right: an on-map main end outside the crop must JOIN a watercourse). Snapping the sluice onto
    # the head was tried and is worse - it drags the channel's mouth across the grid and puts a
    # farmstead on it. Placing the POND on the far side of the head, along the head->sluice line,
    # leaves the channel running straight THROUGH the head on its way in: the ring is charged where
    # it begins, which is what the sluice gate does, and nothing else moves.
    # THE RESERVOIR ANSWERS THREE RULES AT ONCE, and seating it against fewer than three is what
    # made this oscillate. It must sit OUTSIDE the crop (`pond_clear_of_field`), close enough to the
    # ring canal's head that the inlet channel is a short square run rather than a diagonal across
    # the block, and UPHILL of the field, because the source of an irrigation system has to be above
    # what it waters (`channels_flow_downhill`). Earlier versions had two of the three: seating it on
    # the head-to-sluice line satisfied the first two and let the fall push it downhill; backing it
    # off along that same line to clear the crop then dragged it further from the head.
    #
    # So: start at the ring's head and walk UPHILL - straight against the fall, which is the one
    # direction that cannot make the feed run backwards - until the rim is clear of the envelope.
    sluice = net.get("sluice")
    main = next((ch for ch in net.get("channels", []) if ch.get("role") == "main" and len(ch.get("pts") or []) >= 2), None)
    # THE ANCHOR IS THE MAIN'S LAST POINT, because that is the one `draw_comb_field` draws the inlet
    # from (`fork = net["channels"][0]["pts"][-1]`). Choosing the end nearest the SLUICE instead put
    # the reservoir uphill of one end of the ring while the channel was drawn from the other, so the
    # inlet ran diagonally across the head and the far end dangled with nothing joining it
    # (`watercourse_ends_reach_water`, 5 cohort maps). Same point, or the two disagree.
    if main is not None and sluice is not None:
        anchor: Pt = (float(main["pts"][-1][0]), float(main["pts"][-1][1]))
    else:
        anchor = (net.get("dike_sluices") or [(min(p[0] for p in env), sum(p[1] for p in env) / len(env))])[
            0
        ]  # pragma: no cover - build_polder always returns a main feeder and a sluice [174: KEPT, not deletable - an else branch that binds `anchor`]
    ux, uy = -plan.fall[0], -plan.fall[1]  # uphill
    pond = walk_pond_uphill((anchor[0] + ux * (pry + 30.0), anchor[1] + uy * (pry + 30.0), prx, pry), list(plan.envelope), ux, uy)
    # THE STUB REACHES THE RIM (feature 150 T51, GM 2026-08-28: "the irrigated channel which feeds into the water
    # for everything stops short of actually being connected to the feeder pond"). `build_polder` ends the
    # feeder's inlet stub a fixed 52 ft past the ring's corner, and the reservoir is walked uphill until its
    # rim clears the crop - so the stub stopped a measured 30 ft short of the water. The stub's last point is
    # moved onto the rim, 2 ft inside it, so `_clip_to_pond` snaps the drawn bed onto the rim and its bed
    # covers the rim stroke at the mouth: one continuous water.
    if main is not None:
        main["pts"] = inlet_to_rim(main["pts"], pond, env)
    # A polder's ring canal ENDS on the block's corner, outside the planted extent; the feed's record traces the drawn stub
    # to that corner (`comb.feed_stub`, feature 294), so the inlet meets the ring by construction.
    s.draw_comb_field(net, f"{plan.spec.name.lower()}-polder", {"kind": "pond", "pond": pond})
    plan.sink_pond = None
    # THE DIKE-POND SYSTEM (桑基魚塘): convert (almost) every cell to a fish pond rimmed by a
    # mulberry dike. `eligible="all"` is the archetype's named opt-out of the topographic filter -
    # this map IS the wholesale-conversion end state, the rare case where a whole district went
    # over to ponds and bought its grain in (research/archetypes/030-cash-crops-on-rice-land-dike-ponds-lotus-fields-and-tea-rows.html).
    # Applied right after the grid is drawn and BEFORE the perimeter dike, so the ponds' banks and
    # the repainted leftovers are field ground the dike band and the houses draw over. Its RNG is
    # positional (`knob_rng`), so adding it re-rolls nothing else on the map.
    if plan.field_archetype == "mulberry_dike_fishpond":
        # ...with the hamlet's dike crop and its leftover form (feature 150 A6/B2): a `pond` leftover means the
        # whole block converted, so the fraction goes to 1.0 and no parcel is left to repaint.
        s.apply_land_use(
            net,
            "mulberry_fishpond",
            knob_rng(plan.spec.seed, "mulberry_fishpond"),
            fraction=1.0 if plan.leftover == "pond" else DIKEPOND_CONVERSION,
            eligible="all",
            dike_crop=plan.dike_crop,
            leftover=plan.leftover,
            fry_form=plan.fry_form,
        )
    # THE PERIMETER DIKE - the defining polder feature, and the reason a polder is a polder: an
    # irregular hand-piled earthwork band following the water edge in organic bends (fish-scale
    # polder, 鱼鳞圩). Drawn HERE, before the village, so it sits UNDER the houses that line it.
    # ...gapped WHEREVER a channel actually crosses it, not only at the two sluices `build_polder`
    # names. A dug gap is what lets water through an earthwork; anywhere else the dike would be
    # drawn straight over a running channel (`polder_dike_gapped_at_sluices`).
    ring = list(plan.envelope)
    gaps = dike_gaps_at_channels(ring, net.get("channels", []), net.get("dike_sluices") or [])
    # ...AND WHEREVER ANY RECORDED COURSE RUNS ON THE CREST (feature 287, water W42). The ring test above sees only the
    # net's own channels crossing the INNER face; the inlet hairline and the topology channel `draw_comb_field` records
    # in `M["channels"]` cross the band too, and a course can lie on the crest without crossing the inner face at all.
    # The band is a pure function of the ring and the seed (`dike_band`), so its crest is known before it is drawn, and
    # every course is gapped where it breaches it - the rule's own predicate, `course_breaches`.
    _dseed = plan.spec.seed ^ 0x6D
    _crest = dike_crest(*dike_band(ring, _dseed)[1:3])
    courses = [[(float(v[0]), float(v[1])) for v in d["poly"]] for d in list(s.M.get("field_ditches", [])) + list(s.M.get("channels", [])) if d.get("poly")]
    gaps = gaps_for_courses(gaps, courses, _crest)
    # ...and UNLABELED on this tier. `perimeter_dike` captions itself 8 px above the band it picks,
    # and the band is not in the crop's hard set (`_CROP_HARD`), so on some bearings that caption
    # lands outside the frame (`labels_within_image`, seen at down_deg=270). Adding `dikes` to the
    # crop set was tried: the band then holds the frame open past the content and every bearing
    # fails `crop_hugs_content` instead, and Enokida and Kuwabata both move. A perimeter dike is not
    # a feature a reader needs named - it is the most legible thing on a polder sheet - so the
    # scripted tier draws it without a caption rather than framing slack around a word.
    s.perimeter_dike(ring, seed=_dseed, gaps=gaps, label="")
    # ...and the ditch runs OUTSIDE the crop become no-build corridors, exactly as on the valley
    # path. `field_channel` registers none of its own because inside the envelope the crop already
    # blocks building - but a polder's RING CANAL hugs the envelope's edge and its outer stretches
    # lie on the open margin where the village stands, so a farmstead landed squarely on the water
    # (`no_structure_on_channel`, 1 of 12 cardinal polders). The same loop the valley path runs, and
    # like that one it must come AFTER the field is drawn, since `M["field_ditches"]` is written
    # there - placed before it, the loop iterates nothing and reserves nothing, silently.
    # A SEGMENT IS RESERVED UNLESS IT LIES WHOLLY INSIDE THE CROP - tested at both ENDS, not at the
    # midpoint. A ditch segment that straddles the envelope has its midpoint inside, so a midpoint
    # test reserves nothing while half the segment runs out onto the margin where the village is;
    # that is where the last byre came to rest, with the ring canal's vertex landing inside its
    # drawn quad (measured: channel vertex (2301.0, 1864.6) inside a byre spanning 2294-2310 x
    # 1862-1873). The crop already blocks building for the part that IS inside, so reserving a
    # straddling segment costs nothing and closes the gap the midpoint left open.
    # ...over `channels` AS WELL as `field_ditches`. The polder's ring and laterals are field
    # ditches, but the inlet link and the topology hairline `draw_comb_field` records live in
    # `M["channels"]` - and it was one of THOSE that the last byre sat on, its vertex 3.4 px from
    # the byre's center. Reserving one list and not the other is the same shape as a check that
    # reads one manifest key and not its sibling: the ground does not care which list the water
    # was written to.
    for ditch in list(s.M.get("field_ditches", [])) + list(s.M.get("channels", [])):
        run = [(float(v[0]), float(v[1])) for v in ditch["poly"]]
        for a, b in zip(run, run[1:], strict=False):
            if not (point_in_poly(a[0], a[1], plan.envelope) and point_in_poly(b[0], b[1], plan.envelope)):
                s.corridors.append(([a, b], 30.0))


def fit_polder(plan: SitePlan, seed: int, tolerance: float = 0.06, rounds: int = 9, fabric: Mapping[str, Any] | None = None, mosaic: float = 0.0) -> dict[str, Any]:
    """SOLVE the polder grid for the acreage the household count demands - the flat-ground sibling of
    `fit_field`, and it bisects the same way for the same reason.

    What it scales is the GRID (how many modules), never the module: `build_polder`'s cell size is
    calibrated so a whole bay is ~1.9 mu, a half ~0.9 and a third ~0.6, which is the attested parcel
    range, and stretching the cell to hit an acreage would silently move every parcel out of it. A
    polder grows by taking in more of the marsh, not by drawing bigger fields.

    The block keeps a ~1.8:1 tall aspect (Enokida's 15x8 is 1.9), which is what a wei-tian module
    looks like when it is diked out along a shore rather than around a bay."""
    # THE ORIGIN IS DERIVED, NOT PINNED. `build_polder` grows its grid from the HIGH corner along the
    # fall and across it, so a fixed corner only works for one fall bearing - at down_deg=0 the same
    # corner sends the block off the top of the canvas, which is exactly what the first version did
    # (bunds at y=-124, the drain outfall at y=-407, water running visibly backwards). Centring the
    # block and stepping back half its extent along each axis puts it on the canvas at any bearing,
    # and it has to be recomputed per candidate because the bisection changes the extent.
    fab = fabric if fabric is not None else POLDER_FABRIC["polder_grid"]
    cellpx = float(fab["cell"]) / plan.ftpx
    tried: dict[tuple[int, int], tuple[float, dict[str, Any]]] = {}

    def grid(rows: int, cols: int) -> tuple[float, dict[str, Any]]:
        if (rows, cols) not in tried:
            net = _polder_candidate(plan, seed, rows, cols, cellpx, fab, mosaic)
            tried[(rows, cols)] = (net_acres(net, plan.ftpx), net)
        return tried[(rows, cols)]

    def miss(acres: float) -> float:
        return abs(acres - plan.target_acres) / plan.target_acres

    lo, hi = 6, 44
    for _ in range(rounds):
        rows = (lo + hi) // 2
        got, _net = grid(rows, max(4, int(round(rows * 0.55))))
        if miss(got) <= tolerance:
            break
        if got < plan.target_acres:
            lo = rows + 1
        else:
            hi = rows - 1
        if lo > hi:
            break
    # THE ACREAGE IS SOLVED, NOT THE CLOSEST MISS KEPT (feature 287, water W47). The bisection walks ROWS with the columns
    # tied to them, so its candidates jump in coarse steps (a row and a half-column at once) and it used to keep whatever
    # it ended on - on some targets 15% short. When it misses, the search goes on over the (rows, cols) pairs of the
    # archetype's aspect band, each predicted from the acres per module cell measured so far, until one lands inside
    # the tolerance; the drawn block is the tried candidate nearest the target.
    for _ in range(PAIR_ROUNDS):
        if min(miss(a) for a, _n in tried.values()) <= tolerance:
            break
        grid(*_nearest_pair(tried, sum(a / (r * c) for (r, c), (a, _n) in tried.items()) / len(tried), miss))
    # THE BAND IS MEASURED ON THE BLOCK AS DRAWN. The parcel cleanup runs on the WINNER only (feature 150 T55 - see
    # `clean_polder_parcels` for the 15 s -> 41 s it costs on all 45 candidates), and it and the apex pass trim ground
    # after the choice; so the winner is cleaned and measured, and while the trim has taken it out of the band the next
    # candidate is chosen with the trim's measured share carried into its prediction.
    kept = 1.0
    cleaned: set[tuple[int, int]] = set()
    for _ in range(PAIR_ROUNDS):
        (r, c), (_raw, best) = min(((rc, an) for rc, an in tried.items() if rc not in cleaned), key=lambda t: miss(t[1][0] * kept))
        raw = net_acres(best, plan.ftpx)
        clean_polder_parcels(best)
        cleaned.add((r, c))
        final = net_acres(best, plan.ftpx)
        if polder_acres_in_band(final, plan.target_acres):
            return best
        kept = final / raw if raw > 0 else 1.0
        grid(*_nearest_pair(tried, raw / (r * c) * kept, miss))
    # a site no grid of the archetype's module can honor is refused naming it, never drawn short (FR-005)
    raise ValueError(f"no polder grid of {cellpx:.0f} px modules lands {plan.target_acres:.1f} acres within {POLDER_ACRE_BAND:.0%}")


PAIR_ROUNDS = 12  # the (rows, cols) refinement's builds after the bisection: each lands on the pair its measured acres per cell predicts nearest the target, and the pairs of a 1.5-2.2:1 block are dense enough that measured cohorts land in two or three
POLDER_ACRE_BAND = 0.12  # a polder's drawn acreage is within this fraction of the households' target (feature 287, water W47): the soak's clause, with the fit's own 6% tolerance inside it


def _nearest_pair(tried: Mapping[tuple[int, int], Any], per_cell: float, miss: Any) -> tuple[int, int]:
    """The untried (rows, cols) block of the archetype's aspect band (cols 0.45-0.65 of rows, Enokida's 15x8 at 0.53)
    whose acreage `per_cell` predicts nearest the target, the nearer to the 0.55 aspect on a tie."""
    return min(
        ((r, c) for r in range(6, 45) for c in range(max(4, round(r * 0.45)), max(4, round(r * 0.65)) + 1) if (r, c) not in tried),
        key=lambda rc: (round(miss(per_cell * rc[0] * rc[1]), 3), abs(rc[1] / rc[0] - 0.55)),
    )


def polder_acres_in_band(acres: float, target: float, band: float = POLDER_ACRE_BAND) -> bool:
    """THE RULE (feature 287, water W47): the polder's drawn acreage lands within `band` of its target. The fit and its
    test read this one predicate."""
    return abs(acres - target) / target < band


def _polder_candidate(plan: SitePlan, seed: int, rows: int, cols: int, cellpx: float, fab: Mapping[str, Any], mosaic: float) -> dict[str, Any]:
    """One candidate block of `rows` x `cols` modules, centered on the canvas, its edge wander walked down until it reads
    as surveyed (see `fit_polder`)."""
    dx, dy = plan.fall
    ux, uy = -dy, dx  # across the fall
    along, across = rows * cellpx, cols * cellpx
    cx, cy = plan.W / 2.0, plan.H / 2.0
    origin = (cx - dx * along / 2 - ux * across / 2, cy - dy * along / 2 - uy * across / 2)
    # EDGE WANDER IS FITTED TO THE BLOCK, not fixed at Enokida's 0.5. `polder_fills_its_bbox`
    # wants the outline to cover >= 82% of its bbox - the archetype's teeth, since a polder
    # reads as a SURVEYED rectangle rather than an organic field - and the wander's wobble is a
    # fixed size in cells, so on a small block it eats a much larger share of the bbox: measured,
    # a 9x5 grid fills 79% at wander 0.5 where Enokida's 15x8 clears the bar comfortably. So the
    # wander is walked down until the block reads as surveyed, keeping as much of the
    # hand-piled, fish-scale irregularity as the archetype can carry at that size.
    net: dict[str, Any] = {}
    for wander in (0.5, 0.4, 0.3, 0.2, 0.12):
        net = build_polder(
            plan.W,
            plan.H,
            origin,
            seed,
            down_deg=plan.down_deg,
            rows=rows,
            cols=cols,
            cell=cellpx,
            parcel_mix=tuple(fab["parcel_mix"]),
            gap=tuple(fab["gap"]),
            edge_wander=wander,
            mosaic=mosaic,
            clean_parcels=False,
        )
        _env = [(float(a), float(b)) for a, b in net["envelope"]]
        _xs = [q[0] for q in _env]
        _ys = [q[1] for q in _env]
        _bb = max(1.0, (max(_xs) - min(_xs)) * (max(_ys) - min(_ys)))
        if poly_area(_env) / _bb >= 0.86:  # 0.82 is the rule; the margin absorbs the drawn outline's rounding
            break
    return net


# ---- the polder's flanks (feature 150) --------------------------------------------------------------


def _compass(v: Pt) -> str:
    """The compass letter a screen-space vector points to (screen y grows DOWN, so +y is S)."""
    return ("E" if v[0] > 0 else "W") if abs(v[0]) >= abs(v[1]) else ("S" if v[1] > 0 else "N")


def polder_flanks(plan: SitePlan) -> dict[str, str]:
    """The four flanks of a polder block as compass letters, in the roles the composition uses.

    `head` is where the water comes in (uphill), `foot` where it leaves, `plus` the +cross side -
    the one `build_polder` names the settlement side and gives the `e_toe` collector - and `minus`
    the other; `cluster` is the flank the seated village actually stands on (from `plan.seat`,
    empty before `stage_seat`). Polders are laid to cardinal falls, so every letter is exact."""
    dx, dy = plan.fall
    out = plan.seat.get("out") if plan.seat else None
    return {
        "head": _compass((-dx, -dy)),
        "foot": _compass((dx, dy)),
        "plus": _compass((dy, -dx)),
        "minus": _compass((-dy, dx)),
        "cluster": _compass((float(out[0]), float(out[1]))) if out else "",
    }


def waterward_flanks(plan: SitePlan) -> list[str]:
    """Which flanks of the dike face the fluctuating water it was reclaimed from.

    research/archetypes/160-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html: outside the dike is the lake, creek, reed marsh or
    mudflat the block was dug out of - EXCEPT on the landward flank where the polder abuts the
    natural shore, which is where the village stands (nobody lives on a flood-fighting earthwork
    when dry ground is a few steps away), and the head flank, where the header reservoir already
    stands as the wild water. So: the foot (the outfall side, already wet) and the cross flank(s)
    the cluster does not occupy. This is the hand-authored Kuwabata's and Enokida's `["W", "S"]`
    derived rather than declared."""
    f = polder_flanks(plan)
    return [q for q in (f["minus"], f["plus"], f["foot"]) if q != f["cluster"]]


def dike_face(pts: Sequence[Pt], flank: str, lo: float, hi: float, bins: int = 32, cut: float = 0.0, cuts: Sequence[Pt] = (), cut_hw: float = DIKE_GAP_HW) -> Poly:
    """The dike's OUTER FACE along one flank, as a polyline spanning [lo, hi] (feature 150 T54).

    The waterward reed strip has to end exactly where the embankment starts: on the mound is the GM's
    defect, short of it is a dry apron in front of the water. A rectangle can do neither, because the
    ring wanders - Kuwabata's west face stands up to 40 px inside its own outermost point. So the face
    is read off the dike's drawn outline: bin the outline's points along the flank's axis and take the
    OUTERMOST one in each bin (`min` on the W/N sides, `max` on the E/S). Outermost, not average, is
    what keeps the strip off the band - within a bin the face can only be at or outside the value
    taken. A bin the ring does not reach (the strip runs a little past the dike's extent, and the ring
    is CUT by its crossing gaps) keeps its neighbor's face, so the polyline stays continuous to the
    frame. Only the ring's own half counts, split at its center: measured, a gap in the west face let
    the east face win those bins and the west strip came out 2,422 px wide - the whole map wet.

    `cut` is how far the face steps INWARD at a NOTCH - a sluice cut or a crossing, where the
    earthwork is cut through and the water passes - and `cuts` are the notch centers the dike itself
    records (`M['dikes'][*]['gaps']`), already assigned to this flank by the caller. Holding the
    neighbor's face across one left a ~50 ft dry pocket in front of the south outfall
    (settlement-review 2026-08-28), which is backwards: an outfall notch is the wettest ground on the
    flank. The step is keyed on the RECORD and applies UNCONDITIONALLY to the bins the notch covers -
    the first cut made it an `elif` on an empty bucket, on the assumption that a cut empties its bin,
    and the next review measured 14 outline points in the notch bin and 0 steps on all four flanks:
    the ring's cut ENDS fill it. A rule that cannot fire looks exactly like a rule that passes, so the
    step now reads the record alone (bins beyond the ring's own span still keep the extreme - the
    strip runs a little past the dike's ends, and there is no cut there)."""
    horiz = flank in ("W", "E")
    ai, fi = (1, 0) if horiz else (0, 1)  # bin ALONG `ai`; the face is the extreme on `fi`
    outward_min = flank in ("W", "N")
    fs = [p[fi] for p in pts]
    mid = (min(fs) + max(fs)) / 2  # the ring's center on the face axis: only its own half counts
    step = (hi - lo) / bins
    buckets: list[list[float]] = [[] for _ in range(bins)]
    for p in pts:
        k = int((p[ai] - lo) / step)
        if 0 <= k < bins and ((p[fi] <= mid) if outward_min else (p[fi] >= mid)):
            buckets[k].append(p[fi])
    filled = [k for k in range(bins) if buckets[k]]
    first, final = (filled[0], filled[-1]) if filled else (bins, -1)
    last = min(fs) if outward_min else max(fs)  # the extreme, for the bins beyond the ring's own extent
    vals: list[float] = []
    for k in range(bins):
        if buckets[k]:
            last = min(buckets[k]) if outward_min else max(buckets[k])
        v = last
        c = lo + (k + 0.5) * step
        if first <= k <= final and any(abs(g[ai] - c) <= cut_hw + step / 2 for g in cuts):
            v = last + (cut if outward_min else -cut)  # a NOTCH on this flank: the water passes through the cut
        vals.append(v)
    # THINNED, BUT IN SQUARE STEPS. Every point of this polyline is paid for again by `marsh()`'s
    # per-scatter-point `point_in_poly` - 64 bins turned a 4-point rectangle into a 66-point ring in the
    # hottest test on the map - so a run of bins at one face value emits its FIRST and LAST point only.
    # Keeping just the first was tried and is wrong: the run then slants to the next value across its
    # whole length, and a slant cuts back INSIDE the band it was measured to stay outside of (5.5 px on
    # the unit fixture). The step is square; only the one bin where the face actually changes slants.
    out: Poly = []
    for k, v in enumerate(vals):
        if k in (0, bins - 1) or v != vals[k - 1] or v != vals[k + 1]:
            c = lo + (k + 0.5) * step
            out.append((round(v, 1), round(c, 1)) if horiz else (round(c, 1), round(v, 1)))
    return out


def stage_waterward(s: Settlement, plan: SitePlan) -> None:
    """The reed fringe along every water-facing flank of a polder dike, and its declaration.

    Its own stage since feature 150 - `STAGES` position 5, after the seat and BEFORE the houses and the
    track, because the strip RESERVES wet ground both must avoid (laid in the hinterland it was drawn
    over a connector already routed through it; `driver.py` records the move). The hinterland's own toe
    marsh and scrub come later and keep out of it. Each strip hugs the dike's outer face (reeds auto-skip the band and the ponds via the
    keep-outs) and runs off the frame - it is wild ground continuing, not a feature with an edge,
    so `crop_to_content` ignores it. `meta.waterward` declares the flanks for
    `polder_waterward_flanks_wet`, which samples 28 px outside the dike's extreme on each and wants
    14 of 20 points wet - so a strip ENDING at that extreme still satisfies it. A polder that declares
    nothing skips the check silently - the 'check that never runs' shape - which is why the scripted
    tier declares.

    THE STRIP STOPS AT THE MOUND (feature 150 T54, GM 2026-08-28: "the marshland overlaps with the
    earthen mounds ... In some cases, it seems to even extend past them"). Each strip used to lap 60 px
    INWARD from the dike's outer extreme - past a band 11-38 px wide, so the reeds and their wet tint
    were drawn over the mound and out the other side, and the recorded polygon claimed the mound as wet
    ground (which since T50 is no-build ground too). The lap is gone: the strip's inner edge FOLLOWS the
    dike's outer face (`dike_face`), so record and ink both stop where the embankment starts and neither
    leaves a dry apron in front of it - clipping the rectangle to the dike's extreme instead was tried
    and showed one up to 40 px wide wherever the ring wanders inward from its outermost point. `marsh()`
    keeps the scatter off the band itself and off every pond bank in the same change: the strip is the
    REGION, the keep-out is the guarantee - the two halves of one rule.

    Steps:
        l7r.diagram.hamletgen.water.polder.waterward_flanks
        l7r.diagram.hamletgen.water.polder.dike_face
        l7r.diagram.settlement.Settlement.marsh
        l7r.diagram.hamletgen.pondstock.reserve_sty_seat
    """
    if plan.field_archetype not in POLDER_ARCHETYPES or not s.M.get("dikes"):
        return
    pts = [p for dk in s.M["dikes"] for p in dk.get("outline", [])]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    W, H = float(s.W), float(s.H)
    ylo, yhi = y0 - 30.0, y1 + 20.0
    xlo, xhi = x0 - 30.0, x1 + 20.0
    cut = max(float(dk.get("w_max", 0.0)) for dk in s.M["dikes"])  # a notch is cut through the whole band
    # EACH NOTCH BELONGS TO ONE FLANK - the one whose face it stands nearest. A cut near a corner is
    # otherwise stepped into on both, which bites the strip's edge where the band is whole.
    by_flank: dict[str, list[Pt]] = {"W": [], "E": [], "N": [], "S": []}
    for dk in s.M["dikes"]:
        for g in dk.get("gaps") or []:
            gx, gy = float(g[0]), float(g[1])
            by_flank[min((("W", gx - x0), ("E", x1 - gx), ("N", gy - y0), ("S", y1 - gy)), key=lambda t: t[1])[0]].append((gx, gy))
    # THE STRIP IS A BAND, NOT A HALF-CANVAS (feature 150 T55). It used to run from the dike's face to the
    # edge of the canvas, and the crop then threw nearly all of it away - on Kuwabata the view keeps ~74 px
    # of open water west of the dike out of the 1,880 px drawn. Every one of those reeds and tint circles
    # was scattered, tested against every keep-out and discarded: `stage_waterward` cost 18-24 s of a 40 s
    # gen. `WATERWARD_DEPTH` outlasts any crop this tier produces while cutting the scatter ~4x; the strip
    # still runs off the frame, so it is still wild ground continuing rather than a feature with an edge.
    d = WATERWARD_DEPTH
    strips: dict[str, Poly] = {
        "W": [(max(-20.0, x0 - d), ylo), *dike_face(pts, "W", ylo, yhi, cut=cut, cuts=by_flank["W"]), (max(-20.0, x0 - d), yhi)],
        "E": [(min(W + 20.0, x1 + d), ylo), *dike_face(pts, "E", ylo, yhi, cut=cut, cuts=by_flank["E"]), (min(W + 20.0, x1 + d), yhi)],
        "N": [(xlo, max(-20.0, y0 - d)), *dike_face(pts, "N", xlo, xhi, cut=cut, cuts=by_flank["N"]), (xhi, max(-20.0, y0 - d))],
        "S": [(xlo, min(H + 20.0, y1 + d)), *dike_face(pts, "S", xlo, xhi, cut=cut, cuts=by_flank["S"]), (xhi, min(H + 20.0, y1 + d))],
    }
    flanks = waterward_flanks(plan)
    for q in flanks:
        s.marsh(strips[q], role="waterside")
    s.meta(waterward=flanks)
    # ...AND THE STY'S SEAT, the other ground a dike-pond hamlet decides once the flank is known and before the houses stand
    # (feature 287, water W50). A re-seat by `seat_every_household` keeps to this flank (`margin_ladder`), so neither the
    # strips, their declaration nor this reservation has to be redrawn for it (`waterward_flanks` reads the flank alone).
    reserve_sty_seat(s, plan)


def polder_crossing_caps(plan: SitePlan) -> dict[str, int]:
    """Where plank crossings go on a polder's ring canal (research 2026-07-22, research/archetypes/160-polders-fields-diked-against-the-fluctuating-water-weitian-waju.html): people cross to the fields where they LIVE and then walk the bund network,
    so crossings CLUSTER on the settlement-side toe collector, are sparse on the interior laterals,
    and there are NONE on the unsettled feeder, the far toe or the drain. `build_polder` names the
    +cross collector `e_toe` and the other `w_toe`; which is the settlement side is read off the
    seat, not assumed."""
    f = polder_flanks(plan)
    if f["cluster"] == f["plus"]:
        return {"feeder": 0, "w_toe": 0, "drain": 0, "e_toe": 3, "lateral": 1}
    if f["cluster"] == f["minus"]:
        return {"feeder": 0, "e_toe": 0, "drain": 0, "w_toe": 3, "lateral": 1}
    # The village at the HEAD or the FOOT: its own collector is the one it abuts - the feeder at the
    # head, the drain at the foot - and THAT carries the crossings, with one plank on each toe. The
    # first cut here gave both toes two and the feeder none, which satisfied
    # `long_ditches_have_a_footbridge` and put every plank 350-1,100 ft from the houses while the
    # canal directly behind the north dike had none (settlement-review, Kuwabata 2026-08-28: "the
    # crossings are where the CHECK wanted them, not where the feet are"). The research the rule
    # rests on - people cross where they LIVE - applies to whichever collector that is.
    if f["cluster"] == f["head"]:
        return {"feeder": 3, "drain": 0, "e_toe": 1, "w_toe": 1, "lateral": 1}
    # ...EXCEPT THAT A DRAIN TAKES NO PLANK (feature 287, ways W14 and the WAYS law's `plank_on_supply`: a footplank stands on
    # a supply ditch - research ways/030, archetypes/110). The village at the FOOT abuts the drain, which the law refuses a
    # plank, so its crossings go on the supply ditches that reach it - the two toe collectors (role `lateral`) run down to
    # the foot, two a side - and none is asked of the drain that `channel_footbridges` would refuse.
    return {"feeder": 0, "drain": 0, "e_toe": 2, "w_toe": 2, "lateral": 1}
