"""THE VILLAGE GROVE'S FILL, in four parts lifted out of `stands.py`'s `village_grove` by feature 370 (the 100-statement
cap; `stands.py` stood at 960 lines, so the parts take a module of their own): the keep-outs indexed once (`grove_blocks`),
the re-seat search (`reseat_clump`), the windbreak's gap fill (`close_belt_gaps`) and the ink and the record
(`ink_and_record_grove`). The same code in the same order - `self` is the settlement `s` - so no grove moves.

Research: plumbing - NONE"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from .._geom import point_in_poly
from ..land.wet import MARSH_FEATHER_BS, marsh_ground
from ._helpers import _BELT_GAP_FT, _belt_axis
from .bamboo_keepout import copse_bamboo_reach, grown_ring
from .grove_blocks import BankNear, GroveBlocks, Seats
from .grove_rules import EAST_REACH_FT
from .groves import RANK_JITTER_FT, crown_lift
from .stocking import crown_cover, grove_extent, record_box, stocked_box
from .tree_shade import CANOPY_SHADE_FT

if TYPE_CHECKING:
    from ..core import Settlement


def grove_blocks(
    s: Settlement,
    poly: Any,
    role: str,
    clump: float,
    keep_off: Any,
    reserved: tuple[float, float, float, float] | None,
    bamboo_rings: Any,
) -> GroveBlocks:
    """Every keep-out a grove's clumps are asked of, indexed once (`GroveBlocks`, feature 218) - the why of each is at
    its line.

    Research:
        clump off buildings - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: half the diagonal plus the clump's radius and 2 px
        wellhead canopy keep-out - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a wellhead kept its drawn half-size plus 1.05 clumps and 1 px off
        copse off the whole marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: woody cover on the dry ground above the marsh, so the copse is kept off all of it
        off the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: the south strip, the west lane and every crown's sun ground
        belt off the deep marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: based in the reed margin at most
        copse off the bamboo - research/questions/0075-bamboo-groves-chikurin.drawing.html: each stand grown by `copse_bamboo_reach` (two crowns)
        canopy kept 0.9 clump off shrines, torii and ponds - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25)
        clumps kept 12 px plus a crown off paddies and 12 px off dry plots - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: the crops stay open; the 12 px and the crown UNRESEARCHED
        clumps off streams, channels and the moat - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); clumps kept a crown off streams, channels and the moat
        clumps off the road - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: the copse and the groves kept off the main road
        clumps off lanes - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: where a lane crosses the belt the planting resumes on both sides
        clump crown-reach margin off a way - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); the crown reach kept clear of lanes, streets and the road, the margin's width
        clumps off the gardens' east - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: no crown within 50 ft (`EAST_REACH_FT`) east of a yard or bed, from its north edge down to 50 ft below its south edge
        one grove off another's - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); one grove's clumps kept off another's by the sum of their canopy reaches
        groves off the households' wood seats - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); every grove but the copse kept off each household's reserved copse seat (`reserved_seat_keepouts`)
        clumps off a dike bank - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); no clump based on a dike's bank
        the title's pocket kept clear - CONVENTION: clumps kept a crown off the pocket reserved for the map's name
    """
    from .stands import crown_reach, deep_marsh, reserved_seat_keepouts  # noqa: PLC0415 - `stands` imports this module

    bs = s.bscale
    # never draw a clump ON a home/yard/garden/byre/kura: keep the clump CENTER clear by the footprint's
    # circumscribing radius PLUS the clump's own drawn radius (clump/2) and a hair - so the tree blob settles
    # BESIDE the building, touching at most (grove_clumps_clear_of_structures gates it). (A grove may still hug
    # the eaves visually; the blob edge just may not cross the wall.) Was 0.35*clump - too small by ~0.15*clump,
    # which let a blob corner clip a small house.
    occ = [(o["x"], o["y"], 0.5 * math.hypot(o["w"], o["h"]) + clump * 0.5 + 2) for k in ("houses", "threshing_yards", "gardens", "byres", "farm_sheds", "retirement_houses") for o in s.M.get(k, [])]
    # a WELL is a clean draw-point: no tree CANOPY may reach the wellhead (a well lost under the grove reads
    # wrong - wells_clear_of_trees gates it). Keep-out = the well's DRAWN half-size (vr) + the canopy reach
    # (~0.9*clump, as for a shrine), NOT the tight 0.35*clump a homestead eave gets. (o["r"] is the recorded
    # clearance radius; the DRAWN wellhead is vr, which is what a crown must not overhang.)
    occ += [
        (o["x"], o["y"], o.get("vr", o["r"]) + clump * 1.05 + 1.0) for o in s.M.get("wells", [])
    ]  # 1.05, not 0.90 (feature 145): a DRAWN crown runs to ~1.03 x clump (Kashikawa: 14.4 on a 14 clump reached a well 25.4 px away, vr 12.4), and the check measures the drawn crown
    # ...and NOT the notice board, which no longer exists when this runs (GM 2026-08-29). This
    # list used to give the kosatsuba a `30.0 + clump * 0.90` keep-out - about 55 ft, larger than
    # a well's and larger than a shrine's - so that a clump could not swallow the board or pierce
    # its caption. Two things retired it. The board is now the LAST thing placed on a hamlet, so
    # `M["kosatsuba"]` is empty here and the entry could only ever have matched nothing; and the
    # GM has ruled the clearing itself wrong: "it would be very easy to put the notice board at
    # the edge of the forest. We could even display it as being underneath the canopy because I
    # think in many cases it would be ... humans would not need to clear any amount of space in
    # order to put up a notice board at the side of a path." A village drives a plank in beside a
    # way; it does not fell 9,500 sq ft of its own shelter wood to do it. What protects the board
    # now is that it is sited last and can see the trees, not that the trees were kept off it.
    # A SHRINE and its TORII sit in a CLEAN clearing: no tree CANOPY may reach them (a hall/arch lost in the
    # wood reads wrong - shrine_clear_of_grove_trees / torii_clear_of_grove_trees gate it). The DRAWN canopy
    # overhangs the nominal clump radius (crowns spill past clump/2), reaching ~0.85*clump from the clump
    # center - so the keep-out uses that reach + a hair (0.90*clump), NOT the 0.35*clump a homestead uses
    # (there a grove may hug the eaves). A torii is recorded as [x, y, z]; glyph spans x +/-19, y -10..+18.
    occ += [(o["x"], o["y"], 0.5 * math.hypot(o["w"], o["h"]) + clump * 0.90) for k in ("religious", "shrines") for o in s.M.get(k, [])]
    occ += [(t[0], t[1] + 4, math.hypot(19, 14) + clump * 0.90) for t in s.M.get("torii", [])]
    # ... and OFF the fengshui CRESCENT POND (GM 2026-07-21): no tree canopy may cross the half-moon
    # pond's water (trees_clear_of_fengshui_ponds gates it). The keep-out circle spans the FULL disk
    # (radius r + canopy reach) even though the water is only the away-facing half - the flat side toward
    # the village is the pond's open FORECOURT (the banyuetang fronted the settlement's ceremony/work
    # ground), so keeping the copse fringe off that band too is the historically right reading, not slack.
    occ += [(cp["cx"], cp["cy"], cp["r"] + clump * 0.90) for cp in s.M.get("crescent_ponds", [])]
    # ... and OFF THE POND - the tameike or a polder's header reservoir (feature 150: the first
    # scripted dike-pond seated its village at the block's head, so the windbreak's band ran
    # over the reservoir and 15 clumps stood in open water; nothing in this list knew the pond).
    # `M["pond"]` is [cx, cy, rx, ry]; the keep-out is the longer semi-axis + the canopy reach,
    # the same reading as the crescent pond above. `trees_clear_of_water` gates it.
    _pnd = s.M.get("pond")
    if _pnd:
        occ.append((float(_pnd[0]), float(_pnd[1]), max(float(_pnd[2]), float(_pnd[3])) + clump * 0.90))
    # ... and OFF A GROVE THAT IS ALREADY PLANTED (settlement-review x1, 2026-08-19). Nothing here
    # kept one grove out of another, and the copse is seated AFTER the windbreak, so it simply
    # planted itself in the belt: measured on Inashiro, clump-to-nearest-belt-clump distances of
    # 9, 8, 6, 4, 6, 4, 11, 9, 26, 30 and 83 ft against a belt clump radius of 14 - **10 of 11
    # copse clumps inside the belt's own canopy**, spanning x 1096-1188 while the houses span
    # 1108-1331. So the dooryards east of the front rank got no greenery at all and a whole
    # feature was invisible, while `research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html`
    # says outright that "the copse, not the back grove, fills the gaps between the houses".
    #
    # Sum of the two canopy reaches, so neither stand's ink laps the other. This also protects the
    # reverse order (a belt seated after a copse) without needing to know which ran first, and it
    # is why the keep-out is built from the RECORDED clumps rather than the grove's bbox - a belt's
    # bbox is a long rectangle whose corners are open ground the copse may legitimately use.
    # (the radius lives on the GROVE record, not the clump - a clump is a bare [x, y] pair)
    # Kept in its OWN list, not folded into `occ`, because `_reseat` has to tell this blocker
    # apart from the others - see the note there. (the radius lives on the GROVE record, not the
    # clump - a clump is a bare [x, y] pair)
    occ_grove = [(cl[0], cl[1], float(g.get("r") or 0.0) + clump * 0.90) for g in s.M.get("village_groves", []) for cl in (g.get("clumps") or [])]
    occ += occ_grove
    # ...AND OFF EVERY HOUSEHOLD'S RESERVED SHARE OF THE WOOD FLOOR (feature 287, woods W25; plan D9): another grove's
    # clump stands where the copse's crown at a reserved seat would not be displaced by it, so the seat stands when the
    # copse is planted. A local keep-out: the belt flows round it as round a shed. (The copse's own clumps keep half a
    # crown off the seats instead - `held` below - since the seats are its own.)
    if keep_off and role != "copse":
        occ += reserved_seat_keepouts(keep_off, clump, bs)
    # ... and keep trees OFF the lanes / streets / road - and every TRUNK the clump will draw off the tread, not only its seat
    # (feature 287, woods W21 and homes H43): a crown is thrown anywhere in the clump's box and a belt's row conifer a few
    # feet past it (`crown_reach`), so the seat keeps at least that reach beyond the tread, and no trunk the clump draws
    # can stand on it (`trunk_on_tread`). 0.45 x clump + 4 fell 0.4 px short of the belt's own crowns at the box corner
    corr = s._corridor_buffers(max(clump * 0.45 + 4, crown_reach(clump, s.px(RANK_JITTER_FT) if role == "windbreak" else 0.0, lift=crown_lift(bs))))
    cr = clump / 2
    # ... and OUT of the SOUTHERN sun-corridor of every threshing yard + garden (a tree just south of them
    # blocks the drying/growing sun - +y is south). A touch wider than the check so it stays strictly clear.
    sun = [(o["x"], o["y"] + o["h"] / 2, o["w"] / 2 + cr + 2) for k in ("threshing_yards", "gardens") for o in s.M.get(k, [])]
    # HOW DEEP THE SOUTHERN STRIP IS follows the generator's own sun corridor when it declares one (`_sun_corridor_ft`,
    # 39 ft on the scripted hamlets - the depth a FARMHOUSE owes the same bed), else the 22 px this strip always was.
    # The settlement-review of feature 226 (2026-09-12) measured the contradiction: the belt is the tallest thing on
    # the map, the west lane it keeps is 50 ft, a house keeps 39 ft south, and this strip kept 22 - so 7 of
    # Kashikawa's 22 beds had a 10 m clump 24-38 ft south of them with no rule firing.
    # ...AND SINCE FEATURE 328 (wave 56, 0038: "50 ft east, west and south of a plot" for a tree), the tree's own 50 ft
    # (`CANOPY_SHADE_FT`), not the 39 ft a farmhouse owes a bed: the crowns were held to 50 ft (`_sun_keepouts`) while
    # the seats kept 39, so a seat in the strip between was reserved and never planted
    _sun_depth = s.px(CANOPY_SHADE_FT)
    # ... and OUT of the EASTERN sun-lane of every kitchen GARDEN: a tree just east blocks the MORNING sun
    # (the sun rises in the E; +x is east), so a garden on a house's lee/E side keeps clear sky to its east.
    # Entry = (garden east edge, garden cy, half-height + reach). See gardens_unshaded_from_east.
    east = [(o["x"] + o["w"] / 2, o["y"], o["h"] / 2 + cr + 2) for k in ("threshing_yards", "gardens") for o in s.M.get(k, [])]  # every plot (0038), the yard too
    # ... and OUT of the WESTERN / SOUTHWESTERN sun-lane of every yard and garden - the AFTERNOON
    # sun (feature 133 T10, GM 2026-08-25). A belt is the tallest thing on the map: a working
    # igune measures ~10 m, and at 3pm in the shoulder month (sun at 28 deg, azimuth ~232) a
    # 33 ft belt throws ~63 ft of shadow to the NORTHEAST - ~50 ft of it eastward. So a
    # belt clump within `_west_sun_ft` of a plot's west edge, from the plot's north edge down to
    # `_west_sun_ft` below its south edge (the southwest, where the 3pm shadow starts), takes the
    # afternoon. Measured as a SQUARE, not a solar wedge, the same knowing departure the yard's
    # south corridor takes. EVERY MIX (feature 310, GM 2026-10-02: "no canopy trees should be exempt"): the copse was
    # exempt on a passage the record did not hold; every crown is now held to the full sun ground at the crown too
    # (`_sun_keepouts`), and this lane keeps the copse's clump SEATS out of it as the belt's are. Opt-in via
    # `west_sun_lane` (off on the frozen pool). Derivation: research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html.
    wl = float(getattr(s, "_west_sun_ft", 0.0))
    west = [(o["x"] - o["w"] / 2, o["y"] - o["h"] / 2, o["y"] + o["h"] / 2) for k in ("threshing_yards", "gardens") for o in s.M.get(k, [])] if wl else []
    water_lines = [(st_["poly"], st_.get("w", 9) / 2) for st_ in s.M.get("streams", [])]
    water_lines += [(c_["poly"], c_.get("w", 2.5) / 2) for c_ in s.M.get("channels", [])]
    if s.M.get("moat"):
        water_lines.append((s.M["moat"], s.M.get("moat_width", 22) / 2))

    # EVERY KEEP-OUT ABOVE IS INDEXED ONCE, HERE, AND ASKED PER CANDIDATE (feature 218, GM
    # 2026-09-08). Three closures used to answer these questions by walking the whole registry
    # per candidate - `_hard_blocked` ran `edge_dist` over every crop polygon and `seg_dist` over
    # every watercourse segment, `_lane_blocked` over every corridor segment - and the re-seat
    # search re-asked all of it eight times per ring: 7.19 million `seg_dist` calls and 77% of
    # the stage on the reference hamlet, to keep 150 clumps (specs/218 research R1). The split
    # the closures encoded is kept on the index's methods: `hard` (the crop, open water, the dike
    # bank - the edges a belt STOPS at, so a refusal drops the clump), `lane` (a lane that ends at
    # the belt is an edge, one that runs through it is an obstacle - interior-vs-rim separates
    # them below), `local` (a house, a yard, a wellhead's wide keep-out, a sun corridor, a light
    # lane - obstacles a real planted belt is planted AROUND, so an interior refusal re-seats).
    # The index prunes; the same expressions decide; the maps are byte-identical.
    blocks = GroveBlocks(
        outline=poly,
        crops=s.field_polys,
        crop_pad=12 + cr,
        dry=s.dry_polys,
        dry_pad=12,
        # ...AND THE MARSH, INSIDE ONLY, as a dike bank is: woody cover "stands on the dry ground above it"
        # (research/contents.json#vegetation, Reed beds and the marsh's edge), so no clump is BASED in the marsh - a Kashikawa copse clump
        # stood 3-21 ft inside the toe (settlement-review, feature 261) - while a crown may reach over its edge.
        # The COPSE only: applied to every grove it took Sawada's windward belt from 179 crowns to 104, and 20-34 of the
        # 68 crowns it refused stood on ground DRAWN dry - the toe marsh's recorded outline runs under the settlement's
        # cleared ground there, so the outline is not the drawn marsh. The crops' padded keep-out was tried before that
        # and was worse still. The copse is the grove the review measured, and the parcels' own marsh keep-out is the
        # precedent it asked for.
        # ...AND EVERY OTHER GROVE KEEPS OUT OF THE MARSH DEEPER THAN ITS REED MARGIN (feature 287, woods W06): the outline
        # that took Sawada's belt from 179 crowns to 104 was the wrong one - it ran under ground drawn dry - and since M7 the
        # record IS the drawn marsh, so the belt is held to it too, with the margin (`MARSH_FEATHER_BS`, the reeds' own
        # thinning band) left to it: a belt clump based in the margin is drawn as alder, one deeper is not seated
        dikes=[dk["outline"] for dk in s.M.get("dikes", [])]
        + (marsh_ground(s.M) if role == "copse" else deep_marsh(marsh_ground(s.M), MARSH_FEATHER_BS * bs))
        # ...AND OFF THE BAMBOO, grown by a crown: a take-yabu is a clonal near single-species stand (research/questions/0075-bamboo-groves-chikurin.html),
        # and once feature 280 seated the thicket behind the back row the copse's crowns stood inside it (settlement-reviews
        # of Kashikawa and Mizuguchi: four crowns centered inside, culms drawn over them)
        # The rings come from the CALLER (`bamboo_rings`, the plan's seated stands): the stands are drawn by a later stage, so
        # `M['bamboo_stands']` is still empty when the copse is seeded - reading it made the keep-out a no-op (round 3)
        # grown by TWO crowns: a clump draws its crowns scattered about its seat, so a seat one crown off the stand still
        # drew a crown centered inside it (measured on the round-3 fix: one to two a map). `copse_bamboo_reach` is that
        # margin, and every bamboo placer keeps the reserved copse seats outside it (`stand_spares_seats`, feature 287
        # woods W25), so no household's reserved share is refused here
        + ([grown_ring(b, copse_bamboo_reach(bs)) for b in bamboo_rings if len(b) >= 3] if role == "copse" else []),
        water=[(wl, whw + cr) for wl, whw in water_lines],
        corridors=corr,
        circles=occ,
        displacers=occ_grove,
        rects=[(sx - shw, se - cr - 2, sx + shw, se + _sun_depth + 2 + cr) for sx, se, shw in sun]
        + [
            (ex - cr - 2, ey - ehh, ex + s.px(EAST_REACH_FT) + cr, ey + ehh + s.px(EAST_REACH_FT)) for ex, ey, ehh in east
        ]  # down past the south edge too: the southeast corner (0038, "from the plot's north edge down")
        + [(wx0 - wl - cr - 3, wy0 - cr - 1, wx0 + cr + 1, wy1 + wl + cr + 1) for wx0, wy0, wy1 in west]
        # ...AND OFF GROUND SOMETHING ELSE HAS RESERVED (settlement-review, feature 230 pass 12). `reserved`
        # is a rectangle a later stage is holding - today the pocket the map's own NAME will stand in. The
        # caller used to defend it by pushing the grove's polygon VERTICES out of the rectangle, which cannot
        # work at the clump scale: an edge between two vertices outside the pocket still crosses it, and a
        # crown is drawn 14 ft round a center that is itself outside. Measured on Kuwabata: 35 of 87 belt
        # clumps had canopy inside the reserved pocket, the title's own search rejected the pocket it had
        # reserved, and the placard fell to the cover rung and printed over 174 ft of the belt's windward
        # end - the stretch sheltering the westernmost homesteads - hiding 28 of its clumps.
        + ([(reserved[0] - cr, reserved[1] - cr, reserved[2] + cr, reserved[3] + cr)] if reserved else []),
    )
    return blocks


def reseat_clump(
    blocks: GroveBlocks,
    near_clumps: Seats,
    dense: bool,
    step: float,
    clump: float,
    within: tuple[float, float, float, float] | None,
    qx: float,
    qy: float,
    require_interior: bool,
    reach_of: Seats | BankNear | None,
    exact: bool = False,
) -> tuple[float, float] | None:
    """A DENSE belt flows around a local obstacle instead of losing the column.

    Which obstacles, and why this is not "re-seat around everything": a clump refused by the
    CROP, by open WATER or by a lane it merely abuts is refused for a reason that moving it a
    few feet does not change, and those are the edges where a belt is supposed to stop. What
    it DOES flow around is a local keep-out standing IN its line - a house, a yard, a
    wellhead (whose keep-out is the widest of the lot), a lane that CROSSES rather than
    abuts, and a threshing yard's southern sun corridor.

    The sun corridor is the case that motivated folding these three ad-hoc nudges into one
    helper (cohort seed 10, 2026-08-19). A yard's no-tree strip ran straight through the
    belt and left a 40 ft hole with a farmhouse directly downwind of it - the wall breached
    at the one place it was sheltering someone. It is not a crop edge and not a page edge;
    it is a local obstacle, and a real planted belt is planted around it. NOTE the earlier
    ledger entry blamed a pinch in `belt_polygon`; that was wrong - the band is a
    constant-depth ribbon, and the clumps were being filtered out, not left outside.

    Interior-only: a clump blocked near the polygon's own rim is at the belt's edge, where
    stopping is correct.

    Research:
        a belt plants round a local obstacle - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: a lane through the belt and a wellhead in it are planted round, the wall resuming
        a seat refused for the sun set deeper - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: a crown refused in a plot's sun is set deeper in the stand rather than dropped
        the re-seat's reach - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a refused belt clump is offered up to 2.2 grid steps away, eight bearings a ring
        the copse re-seats only when displaced - GUESS: no source could speak to it, a value of ours (feature 417 T36 pass P1, 2026-10-25); a sparse grove re-seats only where another grove's canopy displaced it; any other refusal leaves the gap
        the belt stops at a lane it abuts - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.html: at Fangkeng the flagstone path goes round the grove, not through it; the one-clump rim margin is a GUESS; a clump blocked by a lane within a clump of the belt's rim is dropped
        the edges a stand stops at - research/questions/0071-groves-around-a-southern-chinese-village-the-fengshui-woods-fengshuilin-and-the-dooryard-copse.drawing.html: the paddies, the drying yards and the main road stay open; open water and the dike bank are a GUESS; a clump refused by the crop, open water or a dike bank is dropped, not re-seated"""
    # INTERIOR ONLY FOR A LANE, and this cost seed 10 a round. The rule reads "a clump blocked
    # near the polygon's own rim is at the belt's edge, where stopping is correct" - true of a
    # lane, false of everything else. A belt is 110 px deep and a clump is 28, so demanding
    # `edge_dist > clump` leaves only the middle 54 px eligible: measured on seed 10, every
    # sun-corridor clump sat 2-27 px from a face and the search never ran. A yard's sun
    # corridor crosses the whole depth of the belt; where in that depth a given clump sits
    # says nothing about whether the belt should plant around it.
    # A SPARSE GROVE RE-SEATS TOO (settlement-review, Inashiro 2026-08-20). This used to read
    # `if not dense or (...)`, so only a belt flowed around an obstacle and a scatter's blocked
    # clump was dropped. That guard was written FOR the belt - the docstring above says so, "a
    # DENSE belt flows around a local obstacle instead of losing the column" - and the sparse
    # case was never considered. It is also backwards for what a copse is: the copse fills the
    # open gaps among the houses, so a clump refused because a house is there should try the
    # next gap. Finding the next gap IS the job; dropping the clump is the one response that
    # defeats the feature.
    #
    # Measured cost of the old behavior: Inashiro's copse collapsed to ONE clump inside a
    # declared 255 x 741 ft footprint once gate 0616 reserved ground around the belt's 227
    # clumps, and Mizuguchi's went 11 -> 4 earlier for the same reason (homesteads.py:248).
    # `village_groves_visibly_stocked` now fails a grove in that state.
    #
    # ONLY local obstacles reach here. `_hard_blocked` (crop, open water, the dike bank) still
    # drops the clump outright and must - those are the edges a stand is supposed to stop at,
    # and moving a few feet does not change them.
    # A SPARSE GROVE RE-SEATS ONLY WHEN ANOTHER STAND DISPLACED IT, and the narrowness is the
    # point. Blanket `not dense` re-seating was tried first and OVERSHOT badly: Inashiro's
    # copse went 1 -> 55 clumps and density across the four hamlets jumped to 10-15 per 100k
    # against a historical 3.9-4.4, which turns a dooryard scatter into a stand and defeats
    # the `dense` flag's whole purpose. A scatter is SUPPOSED to leave gaps; a clump refused
    # because a house is there has found one of them.
    #
    # What is NOT a gap is ground another grove's canopy is standing on. That blocker did not
    # exist until gate 0616's keep-out added it, and it deletes clumps for a reason that has
    # nothing to do with the settlement's own texture - measured, it cost Inashiro 10 of its
    # 11 copse clumps. So exactly that class relocates, and every other refusal still drops.
    # This repairs the harm the keep-out did without redesigning the scatter.
    if not dense and not blocks.displaced(qx, qy):
        return None
    if require_interior and blocks.rim_within(qx, qy, clump):
        return None
    # THE RADII REACH PAST THE WIDEST LOCAL OBSTACLE, which is the sun corridor: a yard's
    # no-tree strip is ~25 px half-width across and ~31 px deep, so a search capped at
    # step*1.4 = 28 px could not clear one and seed 10 kept its hole. step*2.2 = 44 px can.
    # A DEAD END, MEASURED AND REVERTED (feature 134 T50, 2026-08-28). When T49's rolled yard
    # sizes opened a 197 ft hole in cohort seed 8's wind wall, the obvious suspect was this
    # ladder: its top rung `step * 2.2` = 44 px is a number measured against the widest local
    # obstacle OF ITS DAY, and a rolled 52 x 36 ft yard stands in `occ` with a keep-out near
    # 57 px, so no rung could clear one. Deriving the top rung from the blocker actually
    # standing at the point (`rr - dist`, capped at `step * 5`) was implemented and rolled:
    # seed 8 came back with the SAME 65 clumps and the SAME 197 ft gap, and seeds 32 and 40
    # were unchanged too. Instrumenting the seating loop's rejections said why - of the grid
    # points in the hole, 166 were refused by `point_in_poly` and 39 by `within`, and NOT ONE
    # reached `_reseat`. The belt's eastern arm had swung north OFF THE PAGE as the cluster
    # repacked, so there was nothing there to re-seat around; the lone clump at (1423, 324) is
    # the only column of that arm the frame still shows. Do not re-derive this radius to chase
    # a belt hole - measure the rejection reasons first, because a hole in the ink and a hole
    # in the ribbon look identical from the manifest.
    for _nr in (step * 0.6, step * 1.0, step * 1.4, step * 1.8, step * 2.2):
        for _na in range(0, 360, 45):
            ax, ay = qx + _nr * math.cos(math.radians(_na)), qy + _nr * math.sin(math.radians(_na))
            if not blocks.inside(ax, ay):
                continue
            if within is not None and (ax + clump * 0.9 < within[0] or ax - clump * 0.9 > within[2] or ay + clump * 0.9 < within[1] or ay - clump * 0.9 > within[3]):
                continue
            if not (blocks.exact_clear if exact else blocks.static_clear)(ax, ay):  # the fill's regions; a reserved seat's exactly (R16)
                continue
            if near_clumps.too_near(ax, ay):
                continue
            if reach_of is not None and not reach_of.too_near(ax, ay):
                continue  # a re-seat is a clump like any other: it stays within its reach (feature 261; a reserved seat's, W25)
            return (ax, ay)
    return None


def close_belt_gaps(
    s: Settlement,
    poly: Any,
    role: str,
    seated: list[tuple[float, float]],
    clumps: list[Any],
    near_seats: Seats,
    near_clumps: Seats,
    blocks: GroveBlocks,
    within: tuple[float, float, float, float] | None,
    clump: float,
    _near: Seats | BankNear | None,
    memory: bool,
) -> None:
    """Close the windbreak's interior holes: each gap over `_BELT_GAP_FT` along the belt's own axis is offered seats across
    its span and depth, re-asking every test the fill asks (the why is at its lines). `seated`, `clumps` and the two seat
    indexes take what lands. `memory` is `stands._GAP_MEMORY`.

    Research:
        belt deep and whole - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: interior gaps over `_BELT_GAP_FT`, 30 ft at every grain, filled
        clumps off lanes - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: where a lane crosses the belt the planting resumes on both sides
    """
    if role == "windbreak" and len(seated) >= 2:
        _wv = _belt_axis(seated)
        # A GAP THAT SEATED NOTHING IS NOT OFFERED AGAIN (feature 281, FR-008). The depth search offers a gap the same
        # points every round - they depend only on its two clumps, `_wv` and the outline - and every test they face is
        # fixed during the fill but the spacing test against clumps already down, whose refusals only grow as clumps
        # land. So a gap that took no seat in a round takes none in a later one: re-offering it was 5 fractions x 33
        # depths of refusals per round, most of the 253,704 outline tests on Sawada's belts. A gap whose clumps change
        # (one lands between them) is a new pair, offered its own points.
        _barren: set[tuple[tuple[float, float], tuple[float, float]]] = set()
        for _ in range(6):  # a 94 ft gap needs three rounds; six is headroom, and it stops when nothing lands
            _order = sorted(range(len(seated)), key=lambda _k: seated[_k][0] * _wv[0] + seated[_k][1] * _wv[1])
            _added = 0
            # A DEAD END, MEASURED AND REVERTED (2026-08-29, the acceptance re-check's ERROR 2; the
            # record: research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html).
            # The review read Kuwabata's belt as stopping before its polygon did, and the obvious
            # repair was to bracket this run by the polygon's own across-wind extent so the END
            # stretches were offered seats like any interior gap. Implemented and rolled: it bought
            # ONE clump, on ONE map, at (2273.9, 393.6) on the page edge - because the unplanted
            # tail is off the page. Kuwabata's belt polygon runs 693..1440 along its own axis, the
            # view holds only 790..1327 of that, and the planting already covers 734..1330. The
            # honest fix was in the CHECK, which was demanding canopy on ground no reader can see;
            # `_column_in_belt` now clips its columns to the view. Do not re-add the end bracket to
            # chase a belt that "stops short" - measure whether the short end is on the page first.
            for _a, _b in zip(_order, _order[1:], strict=False):
                _pa, _pb = seated[_a], seated[_b]
                if math.dist(_pa, _pb) <= s.px(_BELT_GAP_FT) or (memory and (_pa, _pb) in _barren):
                    continue
                # FILL UP TO THE OBSTACLE FROM BOTH SIDES, not only at the midpoint. Where a lane
                # crosses the belt the midpoint IS the lane, so a midpoint-only fill gives up and
                # leaves the whole 40-50 ft hole - when what the record and the agronomy both want is
                # the wall resuming on each side of the crossing. The agroforestry manual, on a windbreak that
                # must be crossed: a gap funnels the wind and the air downwind of it often moves FASTER
                # than over the open field, so a bare opening is a defect. (The record used to give the
                # remedy as rebuilding the crossing to the belt's own height and porosity, which is on no
                # page and would close the access; the attested remedy is to ANGLE the opening to the
                # prevailing wind. What this code does - resuming the wall each side of the crossing -
                # is unaffected.) So the gap is offered
                # seats across its span and takes whichever the ground allows.
                # ...AND ACROSS THE BELT'S DEPTH, not only along the straight line between the two
                # clumps. `village_windbreak_is_continuous` walks COLUMNS of the belt's own span and
                # asks whether each has canopy; a belt that bows around a plot has columns whose
                # midpoint-between-neighbors lies outside its own polygon, so a fill that only tried
                # that line refused every seat and left the column bare - measured on Kuwabata, where
                # the run leaves the polygon after 14 of its 40 ft. So each fraction along the gap is
                # also tried at several depths across the band, which is where the belt actually is.
                # ...AT THE BELT'S OWN DEPTH FOR THAT COLUMN. The continuity check walks COLUMNS
                # across the wind and asks whether each carries canopy, so a fill has to answer in
                # the same terms: find where the belt's polygon actually lies at the bare column and
                # seat there. Offsetting from the straight chord between two clumps does not do it -
                # a belt that bows leaves that chord entirely, and measured on Kuwabata the polygon's
                # depth at the bare columns sits in a band the chord never reaches.
                _took = False
                _perp = (-_wv[1], _wv[0])
                _pd = [(q[0] * _perp[0] + q[1] * _perp[1]) for q in poly]
                _d0, _d1 = min(_pd), max(_pd)
                for _f in (0.5, 0.34, 0.66, 0.22, 0.78):
                    _col = (_pa[0] * _wv[0] + _pa[1] * _wv[1]) + ((_pb[0] * _wv[0] + _pb[1] * _wv[1]) - (_pa[0] * _wv[0] + _pa[1] * _wv[1])) * _f
                    _inside = []
                    for _k in range(33):
                        _d = _d0 + (_d1 - _d0) * _k / 32
                        _qx, _qy = round(_col * _wv[0] + _d * _perp[0], 1), round(_col * _wv[1] + _d * _perp[1], 1)  # the record's grain (W01)
                        if blocks.inside(_qx, _qy):
                            _inside.append((_qx, _qy))
                    for _qx, _qy in _inside[len(_inside) // 2 :] + _inside[: len(_inside) // 2]:  # the band's middle outward
                        if within is not None and (_qx + clump * 0.9 < within[0] or _qx - clump * 0.9 > within[2] or _qy + clump * 0.9 < within[1] or _qy - clump * 0.9 > within[3]):
                            continue
                        if not blocks.static_clear(_qx, _qy) or (_near is not None and not _near.too_near(_qx, _qy)):
                            continue
                        # ...AND NEVER ON TOP OF A CLUMP THAT IS ALREADY THERE (settlement-review
                        # 2026-08-29, acceptance re-check). The depth search is deterministic, so a gap
                        # that survives one round is offered the SAME point on the next and the fill
                        # piled crowns instead of converging. Measured by rolling Kuwabata with this
                        # clause disabled: 246 recorded windbreak clumps at 211 distinct positions,
                        # five of them at (1695.8, 576.9) alone, and 46 off-page clumps at 41
                        # positions. Refusing a seat within half a crown of one already taken brings
                        # the same belt in at 101 on-page clumps with nothing stacked. A stacked crown
                        # is invisible in ink and inflates every count taken off the record - including
                        # the one I first quoted for this feature.
                        if near_seats.too_near(_qx, _qy):
                            continue
                        seated.append((_qx, _qy))
                        clumps.append([round(_qx, 1), round(_qy, 1)])
                        near_seats.add(_qx, _qy)
                        near_clumps.add(round(_qx, 1), round(_qy, 1))
                        _took = True
                        break
                    if _took:
                        break
                if _took:
                    _added += 1
                else:
                    _barren.add((_pa, _pb))
            if not _added:
                break


def ink_and_record_grove(s: Settlement, seated: list[tuple[float, float]], poly: Any, bbox: tuple[float, float, float, float], role: str, mix: str, clump: float) -> int:
    """Ink a grove's clumps - alder in the marsh, the belt's rolled form - and record it in `village_groves` at an extent its
    clumps stock; returns the clumps recorded.

    Research:
        the belt's rolled form - research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html: the village belt drawn conifer-led (its conifer ranks laid along it and painted over the clumps) or mixed broadleaf, rolled per map (`_windbreak_belt`)
        belt alder in the marsh - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: belt clumps standing in the toe or waterside marsh drawn as alder
        the belt's hit region - CONVENTION: the page lights the crowns drawn - each windbreak clump's seat out to its crown reach plus 0.3 of a clump for a crown's spread, the conifer ranks at their drawn radius, the alder clumps (their own class) left out
    """
    from .stands import crown_reach  # noqa: PLC0415 - `stands` imports this module

    x0, y0, x1, y1 = bbox
    bs = s.bscale
    clumps = [[x, y] for x, y in seated]  # the seats are at the record's grain (W01), so the record is the ink
    # A BELT CROWN IN THE MARSH IS ALDER (feature 261, Sawada's belt on its toe's reed edge): the record's woody stage at
    # a reed margin is alder or willow (research/contents.json#vegetation, Reed beds and the marsh's edge), and alder is the tree of a
    # wetland's fertile edge, so where the windbreak's ground runs into the recorded marsh its trees are drawn as one
    _wet = marsh_ground(s.M, only=("toe", "waterside")) if role == "windbreak" else []
    alder = 0
    alder_clumps: list[list[float]] = []  # which seats are drawn as alder, so a recount after the page is known reads them (woods W05)
    bamboo = 0  # the bamboo marks inked low under the windbreak's crowns (269 B29, `_draw_grove`)
    # THE VILLAGE BELT IS DRAWN IN ITS ROLLED FORM (269 B30, `windbreak_belt`; research/questions/0072-shelter-belts-on-a-villages-windward-side-bofurin.drawing.html): conifer-led, its
    # rows of conifers laid along the belt as drawn and seated before the clumps' lesser crowns, then painted over them
    # (`_belt_ranks`), or mixed broadleaf. The water-mouth grove keeps the older mix.
    form = s._windbreak_belt() if role == "windbreak" and seated else None
    crowns: dict[str, int] = {}
    rows_ink = ""
    _rows: list[Any] = []  # the conifer-led belt's rank crowns (x, y, r), for its hit region below
    if form == "conifer_led":
        _rows, rows_ink = s._belt_ranks(seated, clump, _wet)
        crowns["conifer"] = len(_rows)
        # ...AND KNOWN TO EVERY LATER STAND (feature 315): a stand drawn after the belt keeps its broadleaf off a conifer it
        # knows of (`_draw_grove`'s `_cones`), and the belt's rows were never told it - a re-seated Inashiro drew a copse crown
        # over a belt cedar (B5b)
        s._conifer_crowns = [*(getattr(s, "_conifer_crowns", None) or []), *((float(x), float(y), float(r)) for x, y, r in _rows)]
    for jx, jy in seated:
        # feature 150: the belt and the copse are two highlight classes; a water_mouth grove has no
        # class in the vocabulary yet and stays unclassed so the census reports it
        if any(point_in_poly(jx, jy, w) for w in _wet):
            alder += 1
            alder_clumps.append([jx, jy])
            s._draw_grove(jx, jy, clump, clump, face=(0, -1), mix="alder", cls="alder")
            continue
        bamboo += s._draw_grove(jx, jy, clump, clump, face=(0, -1), mix=form or mix, cls={"windbreak": "windbreak", "copse": "copse"}.get(role), tally=crowns)
    if rows_ink:
        s.add(rows_ink, cls="windbreak")
    if clumps:
        # A COPSE IS RECORDED AT THE SIZE IT WAS DRAWN, not at the size it was asked for.
        #
        # The copse's requested footprint is the bounding box of the whole house cloud, and the
        # clumps inside it are skipped wherever they would land on a house, yard, garden or
        # crop - so the DECLARED area and the PLANTED area are two different things, and the
        # gap between them widens whenever the cluster spreads. Feature 126 spread it (houses
        # are no longer seated against pre-laid lanes), and `village_groves_visibly_stocked`
        # started firing: "copse 307x443px holds 1 clump (0.73/100k), floor 1.5". The trees had
        # not gone anywhere; the box around them had grown.
        #
        # The check is right and the record was wrong - a map that declares a feature it did not
        # draw is the defect, which is the same rule `M["lane"]` breaks when it keeps an untrimmed
        # spine. So a COPSE reports the extent of its own clumps. The WINDBREAK deliberately does
        # not: its position IS its meaning (`village_windbreak_on_windward_side` judges the
        # recorded center) and shrinking it to the leaves would walk that center off the windward
        # side - a defect this file already records having caused on cohort seeds 19 and 28.
        _pad = clump / 2 + 4.0
        if role == "copse":
            x0, y0, x1, y1 = grove_extent(clumps, _pad)
            poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        # ...AND EVERY GROVE IS RECORDED AT AN EXTENT ITS CLUMPS STOCK (feature 287, woods W15): the band's box where they
        # stock it (the windbreak's position is its meaning, above), else the extent they are drawn at, else their main
        # stand's (`stocked_box`) - no role is left to a density nothing decided
        _rec: dict[str, Any] = {}
        record_box(_rec, stocked_box(clumps, (x0, y0, x1, y1), _pad))
        s.M["village_groves"].append(
            {
                **_rec,
                "rot": 0,
                "role": role,
                "r": round(clump / 2, 1),
                "clumps": clumps,
                "clumps_offpage": [],  # filled by `set_view`'s partition, the first moment the page is known
                "alder": alder,  # of the clumps, those standing in the marsh and drawn as alder (feature 261)
                "alder_clumps": alder_clumps,  # ...and which they are, for the recount once the page is known (feature 287, woods W05)
                "bamboo": bamboo,  # bamboo marks inked in the gaps and along the edge (269 B29; 0 outside the windbreak mix)
                "form": form,  # the village belt's rolled form (269 B30, meta.windbreak_belt); None off the belt
                "crowns": crowns,  # the crowns drawn, by kind (conifer / broadleaf; the alder clumps are not counted)
                "poly": [[round(px, 1), round(py, 1)] for px, py in poly],
                # THE BELT'S HIT REGION IS ITS DRAWN CROWNS (feature 328 wave 71): each windbreak clump's crowns reach
                # `crown_reach` from its seat plus a crown's own spread, and a conifer-led belt's ranks their drawn radius
                # - the page lit the belt's whole box, an empty arm included (Inashiro's glyph check, batch 3's close)
                **(
                    {
                        "cover": crown_cover(
                            [(jx, jy, crown_reach(clump, s.px(RANK_JITTER_FT), crown_lift(bs)) + clump * 0.3) for jx, jy in seated if [jx, jy] not in alder_clumps]
                            + [(float(x), float(y), float(r)) for x, y, r in _rows]
                        )
                    }
                    if role == "windbreak"
                    else {}
                ),
            }
        )
    return len(clumps)
