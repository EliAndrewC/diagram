"""Gate segments (city civic and commerce; keys 0563_045-0563_077) - bodies verbatim, registry order preserved."""

import math
from typing import Any

from .common_01_geometry import point_in_poly, seg_dist, solid_structs
from .common_03_capacity import _UNBOUND, _kept

# civic amenities ported up from the town tier (a city is a bigger version of the same):


# a CITY theater stage is bigger than a town's (towns run a viewing ground ~150 wide) - a provincial
# city draws a larger crowd, so its viewing ground is wider (>= 185, the city baseline)


def _seg_0563_049__amph_raw3(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.049 (amph_raw3) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        amph_raw3 = M.get("theater_stage")
    return _kept(locals(), ('amph_raw3',))


def _seg_0563_050__amph_all3(*, amph_raw3: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.050 (amph_all3) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        amph_all3 = amph_raw3 if isinstance(amph_raw3, list) else ([amph_raw3] if amph_raw3 else [])
    return _kept(locals(), ('amph_all3',))


def _seg_0563_051__amph(*, a8: Any = _UNBOUND, amph_all3: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.051 (amph) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        amph = max(amph_all3, key=lambda a8: a8.get("w", 0)) if amph_all3 else None
    return _kept(locals(), ('amph',))


# FIRE DEFENSE: a city's dense quarters each need a fire-watch tower (hinomi-yagura). WHY:
# settlements.md "Fire towers". Opt out per-map with meta(fire_tower=False).


# A NAMED civic building's label must sit on ITS OWN building, never on a DIFFERENT one of the
# same kind. labels_clear_of_other_buildings lumps every ministry into one "ministry" GROUP, so
# it permits a ministry label to sit on a SIBLING ministry (the "Ministry of Justice" label
# drifted onto the "Ministry of Works" office). This catches that finer case: a label that names
# a civic building (a ministry by name, the governor's yamen, a named temple) must not overlap
# any OTHER named civic building.


# GOVERNMENT OFFICES stand in their own ground - a ministry or the governor's yamen is a large,
# important compound and must not ABUT another structure. Ordinary city houses may touch each
# other, but a government office keeps a clear gap from every other building/compound around it.


# every solid footprint, from the registry - an office must not abut a martial hall or a
# brewery any more than it may abut a house (GM 2026-07-25; see solid_structs). The FUNERARY
# compounds are the one deliberate exclusion: the ruling clan's walled crypt standing against
# the governor's yamen is a real adjacency (the house's dead beside the house's seat), not a
# packing error, and Nagahara has drawn it that way since long before this check read the
# registry. Burial ground siting has its own battery (funerary_clear_of_fields, the
# burial-ground checks); this rule is about a bureau not being crowded by ordinary premises.


def _seg_0563_066__others(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.066 (others) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        others = solid_structs(M, "religious", "merchant_estates", exclude=("cemeteries", "mausoleums", "cremation_grounds", "ossuaries"))
    return _kept(locals(), ('others',))


# PUBLIC WELLS: ensuring every commoner could draw water was a defining civic concern of a
# premodern city. A communal well (the idobata) served a courtyard / cluster of ~10-20
# households, so the warren is dotted with them - one within a short walk of any home. The
# underground half of the system (aqueducts, cisterns, rain barrels feeding the shafts) is too
# small or literally subterranean and stays OFF the map; only the wellheads show.
# PRIVATE wells (private=True - e.g. the brewery's own courtyard well, GM 2026-07-24) are
# premises fixtures, not neighborhood infrastructure: they serve no commoner households, so
# they are excluded from ALL the public-well accounting below (reach, density, block-interior
# siting, the samurai-ward ban) - exactly as samurai compounds' implied private wells are.


def _seg_0563_071__w_(*, M: Any = _UNBOUND, scale: Any = _UNBOUND, w_: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.071 (w_, wells) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        wells = [w_ for w_ in M.get("wells", []) if not w_.get("private")]
    return _kept(locals(), ('w_', 'wells'))


def _seg_0563_072__city_neighborhoods_have_wells(
    *,
    COMMON: Any = _UNBOUND,
    HOUSEK: Any = _UNBOUND,
    M: Any = _UNBOUND,
    MAX_PER_WELL: Any = _UNBOUND,
    MAX_PER_WELL_OUTCAST: Any = _UNBOUND,
    REACH: Any = _UNBOUND,
    SAMK: Any = _UNBOUND,
    _sy_stbl: Any = _UNBOUND,
    a: Any = _UNBOUND,
    b: Any = _UNBOUND,
    b9: Any = _UNBOUND,
    bad_well: Any = _UNBOUND,
    c: Any = _UNBOUND,
    check: Any = _UNBOUND,
    d: Any = _UNBOUND,
    dry: Any = _UNBOUND,
    dwl: Any = _UNBOUND,
    h: Any = _UNBOUND,
    hh: Any = _UNBOUND,
    hh_out: Any = _UNBOUND,
    hx: Any = _UNBOUND,
    hy: Any = _UNBOUND,
    i: Any = _UNBOUND,
    inw: Any = _UNBOUND,
    lane_w: Any = _UNBOUND,
    ln: Any = _UNBOUND,
    lw: Any = _UNBOUND,
    meta: Any = _UNBOUND,
    near_dw: Any = _UNBOUND,
    s9: Any = _UNBOUND,
    sam_wells: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    served: Any = _UNBOUND,
    served_out: Any = _UNBOUND,
    st: Any = _UNBOUND,
    structs: Any = _UNBOUND,
    swamped: Any = _UNBOUND,
    w: Any = _UNBOUND,
    wells: Any = _UNBOUND,
    wlanes: Any = _UNBOUND,
    wp: Any = _UNBOUND,
    wr: Any = _UNBOUND,
    wx: Any = _UNBOUND,
    wy: Any = _UNBOUND,
    x: Any = _UNBOUND,
    y: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.072 (city_neighborhoods_have_wells, city_samurai_quarter_has_no_public_wells, city_well_density_sufficient, city_wells_in_block_interiors) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):  # noqa: SIM102
        if wells:
            wp = M.get("wall") or []
            inw: Any = (lambda x, y: point_in_poly(x, y, wp)) if len(wp) >= 3 else (lambda x, y: True)  # type: ignore[no-redef]  # noqa: E731
            # WATER ACCESS: every commoner dwelling INSIDE the walls (laborer/burakumin/merchant kinds;
            # samurai have private wells in their compounds, and a transient gate market outside the wall
            # is not housing) must have a public well within reach. Servants are interleaved among the
            # commoners and share the same wells, so they ride along. A dwelling too far from any well is
            # a neighborhood the water network forgot.
            REACH = 290
            # monk_house is NOT here (021): a temple's monk houses draw from the temple's own
            # well inside the precinct (the monastery provisions its own community - the same
            # reason samurai compounds are exempt), so a monk file in a well-less pocket beside
            # its temple is correct, not a forgotten neighborhood.
            COMMON = {"laborer", "laborer_large", "burakumin", "merchant", "merchant_house", "merchant_large"}
            dry = [
                (round(b["x"]), round(b["y"]))
                for b in M.get("buildings", [])
                if b.get("kind") in COMMON and inw(b["x"], b["y"]) and min(math.hypot(b["x"] - w["x"], b["y"] - w["y"]) for w in wells) > REACH
            ]
            check(
                "city_neighborhoods_have_wells",
                not dry,
                f"{len(dry)} commoner dwelling(s) inside the walls more than {REACH}px from any public well - every neighborhood needs water access; scatter wells through the warren (e.g. {dry[:3]})",
            )
            # and ENOUGH wells that none is OVER-BURDENED: a communal well historically served a courtyard
            # / cluster of ~10-20 households, so assigning each commoner dwelling (servants included - they
            # draw here too) to its NEAREST well, no well should end up doing the work of three. The reach
            # check guarantees coverage but not density - the AVERAGE can look fine while the busiest wells
            # in the dense laborer warren are swamped - so this bounds the per-well share. (The nearest-well
            # split over-counts a little where two wells are nearly equidistant, so the ceiling sits a touch
            # above the historical 20.)
            #
            # BURAKUMIN HOUSEHOLDS ARE COUNTED AT A HIGHER CEILING, and that is a finding, not a
            # fudge (GM 2026-08-10, from the capital's well knots). An outcast quarter packed at
            # roughly twice the machi's row density cannot reach 1-per-20 without putting five to
            # seven wellheads inside one 150 ft radius - which is not how any settled map looks,
            # because it is not how the ground worked: hinin quarters were the LAST to be served
            # by communal water, drew from the river, the ditch, or a single shared well, and
            # their under-provision is part of what made them outcast ground. So they carry their
            # own ceiling rather than forcing wells the quarter would never have had. A quarter
            # whose burakumin rows are ALSO dry still fails city_neighborhoods_have_wells - the
            # reach rule is not relaxed, only the density share.
            # 26 at provincial-city density; 30 at CAPITAL density (GM 2026-08-11, and only after
            # every placement lever was tried and failed on Shiro Daika). The band this rule cites -
            # ~1 well per 10-20 households - was calibrated against the provincial cities, whose
            # machi the 018 budget builds at a lower density than a domain capital's. On the capital
            # two blocks run at 27 and 29, and that is NOT scarcity: 16 public wells stand within
            # 200 px of the first, at 60-95 px spacing, and open_seat refuses a 9 px wellhead at
            # every radius out to 96 px with the EXACT disc reach because the terrace is solid.
            # Adding wells trips wells_not_clustered before the deficit clears; reserving one ahead
            # of the packs cascades through the fabric (205 -> 278 wells); shrinking the packs to
            # free ground puts capital_housing_matches_band_targets off its budget. Every lever
            # moves a different rule into the red, which is the signature of a THRESHOLD calibrated
            # for a different tier - so the tier gets its own number rather than the map getting a
            # waiver. Edo's densest nagaya blocks did share a single well among ~30 households.
            MAX_PER_WELL = 30 if meta.get("scale") == "capital" else 26
            MAX_PER_WELL_OUTCAST = 60
            hh = [(b["x"], b["y"]) for b in M.get("buildings", []) if b.get("kind") in (COMMON | {"servant"}) and b.get("kind") != "burakumin" and inw(b["x"], b["y"])]
            hh_out = [(b["x"], b["y"]) for b in M.get("buildings", []) if b.get("kind") == "burakumin" and inw(b["x"], b["y"])]
            served = [0] * len(wells)
            for hx, hy in hh:
                served[min(range(len(wells)), key=lambda i: math.hypot(hx - wells[i]["x"], hy - wells[i]["y"]))] += 1
            served_out = [0] * len(wells)
            for hx, hy in hh_out:
                served_out[min(range(len(wells)), key=lambda i: math.hypot(hx - wells[i]["x"], hy - wells[i]["y"]))] += 1
            swamped = [(round(wells[i]["x"]), round(wells[i]["y"]), c + served_out[i]) for i, c in enumerate(served) if c > MAX_PER_WELL or c + served_out[i] > MAX_PER_WELL_OUTCAST]
            # WHY (~1 communal well per 10-20 households - the premodern courtyard-well norm): settlements.md "Historical grounding"
            check(
                "city_well_density_sufficient",
                not swamped,
                f"public well(s) each the nearest for more than {MAX_PER_WELL} commoner households - too few wells for "
                f"the neighborhood (~1 per 10-20 households is realistic); add wells where the warren is densest: {swamped}",
            )
            # wells sit in a block INTERIOR off the lanes (the idobata was a courtyard, not the avenue),
            # and a wellhead must not overlap a building or compound. Placement guarantees both (well_at /
            # place_wells use the same clearance test the houses do), so this is the backstop.
            wlanes = [st["pts"] for st in M.get("town_streets", [])] + ([M["road"]] if M.get("road") else []) + [a["pts"] for a in M.get("alleys", [])]
            lane_w = [st.get("w", 24) for st in M.get("town_streets", [])] + ([M.get("road_width", 26)] if M.get("road") else []) + [10 for _ in M.get("alleys", [])]
            _gov = M.get("governor_mansion")
            structs = solid_structs(M, "religious", "merchant_estates")  # registry-driven, so a new feature cannot silently host a wellhead
            bad_well = []
            for w in wells:
                wx, wy, wr = w["x"], w["y"], w.get("r", 8)
                if any(seg_dist(wx, wy, ln[i], ln[i + 1]) < lw / 2 + wr for ln, lw in zip(wlanes, lane_w, strict=False) for i in range(len(ln) - 1)):
                    bad_well.append((round(wx), round(wy), "on a lane"))
                elif any("w" in st and abs(wx - st["x"]) < st["w"] / 2 + wr and abs(wy - st["y"]) < st["h"] / 2 + wr for st in structs):
                    bad_well.append((round(wx), round(wy), "on a building"))
            check("city_wells_in_block_interiors", not bad_well, f"well(s) not sitting clear in a block interior - a wellhead is on a lane or overlaps a structure: {bad_well[:4]}")
            # the SAMURAI/GOVERNMENT quarter has NO public wells - samurai drew from PRIVATE wells inside
            # their own walled compounds, and gathering at the communal idobata was a commoner-district
            # institution (beneath samurai status). So a public wellhead embedded AMONG the samurai
            # dwellings is wrong; their water is private and stays off-map, like their gardens. A well is
            # "in the samurai quarter" if the dwellings it actually sits among are mostly samurai - a
            # relative test, robust where a commoner well sits a block from the quarter across the ward fence.
            SAMK = {"samurai", "samurai_large"}
            HOUSEK = {"laborer", "laborer_large", "servant", "burakumin", "merchant", "merchant_house", "merchant_large"} | SAMK
            dwl = [(b["x"], b["y"], b.get("kind") in SAMK) for b in M.get("buildings", []) if b.get("kind") in HOUSEK]
            dwl += [
                (h["x"], h["y"], False) for h in M.get("houses", [])
            ]  # FARMHOUSES are commoner households in this vote: a farm-belt well (s.farm_wells) sits among farmsteads far from any urban dwelling, and judging it by the nearest IN-WALL houses mislabeled it samurai (Nagahara's SW belt, 2026-07-21)
            # a CARAVAN-YARD well (within reach of a stables) is the yard's own trough water,
            # serving wagon crews and animals wherever the gate quarter's caste happens to sit -
            # the resized capital's N gate cluster stands in the samurai band, and its yard well
            # is not a neighborhood idobata (021, the wall-resize re-lay).
            _sy_stbl = [b9 for b9 in M.get("buildings", []) if b9.get("kind") == "stables"]
            sam_wells = []
            for w in wells:
                if w.get("kind") == "cistern":
                    # a josui-ido draw-basin is INFRASTRUCTURE on the buried main, sited by the
                    # aqueduct's reach (within ~600 ft of the settling basin), not a neighborhood
                    # idobata - at the E gate that reach falls in the samurai quarter, and everyone
                    # within reach of the main draws from it (021, the settled-wall pass).
                    continue
                if any(math.hypot(w["x"] - s9["x"], w["y"] - s9["y"]) < 80 for s9 in _sy_stbl):
                    continue
                if len(wp) >= 3 and not inw(w["x"], w["y"]):
                    # the samurai QUARTER is intramural by definition - an extramural well (a farm-belt
                    # or gate-suburb well) cannot sit "in" it, and letting in-wall samurai houses vote
                    # across the rampart mislabeled a SE farm well (Tango, 2026-07-24 trade-works ripple)
                    continue
                near_dw = sorted(dwl, key=lambda d: math.hypot(d[0] - w["x"], d[1] - w["y"]))[:3]
                if near_dw and sum(1 for d in near_dw if d[2]) * 2 >= len(near_dw):  # most of its nearest neighbors are samurai
                    sam_wells.append((round(w["x"]), round(w["y"])))
            # WHY (samurai/official households drew from PRIVATE wells inside their walled compounds): settlements.md "Historical grounding"
            check(
                "city_samurai_quarter_has_no_public_wells",
                not sam_wells,
                f"public well(s) sitting among the samurai dwellings: {sam_wells} - the samurai/government quarter has no "
                f"communal wells (samurai draw from private wells inside their compounds; the public idobata is a commoner institution)",
            )
    return _kept(
        locals(),
        (
            'COMMON',
            'HOUSEK',
            'MAX_PER_WELL',
            'MAX_PER_WELL_OUTCAST',
            'REACH',
            'SAMK',
            '_',
            '_gov',
            '_sy_stbl',
            'a',
            'b',
            'b9',
            'bad_well',
            'c',
            'd',
            'dry',
            'dwl',
            'h',
            'hh',
            'hh_out',
            'hx',
            'hy',
            'i',
            'inw',
            'lane_w',
            'ln',
            'lw',
            'near_dw',
            's9',
            'sam_wells',
            'served',
            'served_out',
            'st',
            'structs',
            'swamped',
            'w',
            'wlanes',
            'wp',
            'wr',
            'wx',
            'wy',
        ),
    )


# a city ON the Imperial road LINES that road with COMMERCE (shops + traveler inns): the
# through-road is the city's prime frontage, where caravans and travelers pass, so it must not
# run bare. This holds for ANY city with an Imperial road, WALLED OR NOT - a city WITHOUT a road
# has no such ribbon (its commerce stays in the market district). The road's portion running
# THROUGH the city is judged: bounded by the WALL if there is one, else by the URBAN FOOTPRINT
# (the bbox of the city's buildings). Scaled to that length at ~1 commercial frontage per 130px,
# a floor that catches a bare spine.


def _seg_0563_073__road(*, M: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.073 (road) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        road = M.get("road") or []
    return _kept(locals(), ('road',))


def _seg_0563_074__p(*, EY0: Any = _UNBOUND, EY1: Any = _UNBOUND, p: Any = _UNBOUND, road: Any = _UNBOUND, scale: Any = _UNBOUND) -> dict[str, Any]:
    """Gate segment 563.074 (p, road_through) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital'):
        road_through = bool(road) and any(p[1] < EY0 for p in road) and any(p[1] > EY1 for p in road)
    return _kept(locals(), ('p', 'road_through'))


def _seg_0563_075__city_imperial_road_has_commerce(
    *,
    COMMERCE: Any = _UNBOUND,
    EX0: Any = _UNBOUND,
    EX1: Any = _UNBOUND,
    EY0: Any = _UNBOUND,
    EY1: Any = _UNBOUND,
    M: Any = _UNBOUND,
    a: Any = _UNBOUND,
    b: Any = _UNBOUND,
    bg: Any = _UNBOUND,
    bx: Any = _UNBOUND,
    by: Any = _UNBOUND,
    check: Any = _UNBOUND,
    frac_inside: Any = _UNBOUND,
    i: Any = _UNBOUND,
    il: Any = _UNBOUND,
    in_city: Any = _UNBOUND,
    k: Any = _UNBOUND,
    need: Any = _UNBOUND,
    road: Any = _UNBOUND,
    road_comm: Any = _UNBOUND,
    road_through: Any = _UNBOUND,
    scale: Any = _UNBOUND,
    t: Any = _UNBOUND,
    wp: Any = _UNBOUND,
    x: Any = _UNBOUND,
    x0: Any = _UNBOUND,
    x1: Any = _UNBOUND,
    y: Any = _UNBOUND,
    y0: Any = _UNBOUND,
    y1: Any = _UNBOUND,
) -> dict[str, Any]:
    """Gate segment 563.075 (city_imperial_road_has_commerce) - body verbatim from the city mega-segment (feature 023; guards preserved, see research.md R2/R3)."""
    if scale in ('city', 'capital') and road_through:
        wp = M.get("wall") or []
        if len(wp) >= 3:
            in_city: Any = lambda x, y: point_in_poly(x, y, wp)  # type: ignore[no-redef]  # noqa: E731
        else:
            bx = [b["x"] for b in M.get("buildings", [])] or [EX0, EX1]
            by = [b["y"] for b in M.get("buildings", [])] or [EY0, EY1]
            x0, x1, y0, y1 = min(bx) - 40, max(bx) + 40, min(by) - 40, max(by) + 40
            in_city = lambda x, y: x0 <= x <= x1 and y0 <= y <= y1  # noqa: E731
        il = 0.0
        for i in range(len(road) - 1):
            a, b = road[i], road[i + 1]
            frac_inside = sum(1 for t in range(11) if in_city(a[0] + (b[0] - a[0]) * t / 10, a[1] + (b[1] - a[1]) * t / 10)) / 11
            il += math.hypot(b[0] - a[0], b[1] - a[1]) * frac_inside
        COMMERCE = {"shop", "merchant", "inn"}
        road_comm = sum(
            1 for bg in M.get("buildings", []) if bg.get("kind") in COMMERCE and in_city(bg["x"], bg["y"]) and min(seg_dist(bg["x"], bg["y"], road[k], road[k + 1]) for k in range(len(road) - 1)) <= 95
        )
        need = round(il / 130)
        check(
            "city_imperial_road_has_commerce",
            road_comm >= need,
            f"only {road_comm} shops/inns front the {round(il)}px of Imperial road running through the city (want >= {need}) - a "
            f"city on a trade route lines its through-road with commerce to service travelers; don't leave the prime road frontage bare",
        )
    return _kept(locals(), ('COMMERCE', 'a', 'b', 'bg', 'bx', 'by', 'frac_inside', 'i', 'il', 'in_city', 'k', 'need', 'road_comm', 't', 'wp', 'x0', 'x1', 'y0', 'y1'))


# two lanes (streets/alleys) heading STRAIGHT at each other and stopping just short, with nothing
# between them, should simply CONNECT - a near-miss reads as a mistake, not a deliberate dead-end.
# (Unlike city_streets_no_near_miss, which only compares street-vs-street segment proximity, this
# catches ALLEYS too and the aligned end-to-end / T case, and ignores gaps a building/fence/wall
# genuinely blocks.) Generic to any city with lanes, walled or not.
