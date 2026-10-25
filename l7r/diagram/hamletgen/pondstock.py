"""STAGE 6b (feature 150, GM 2026-08-28 choosing audits A3 and A4): the stock a dike-pond hamlet keeps ON its ponds.

The dike-pond loop fed its fish with more than silkworm waste: "pigs, chickens and ducks are reared on
the dykes, to provide manure to fertilise the fishponds" (Ruddle & Zhong via `isis-dykepond`), the
pig shed "constructed on the pond dyke or over the water surface" so the excreta run straight in. The
premodern SHARE of households keeping a sty is not in anything read - the band below is a GUESS and the
class entry says so - so it is rolled from the hamlet's seed like every other share, and each sty takes
a pond of its own nearest the houses, on the bank between the parcel's edge and its water. Research:
research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.html and research/questions/0023-the-dike-pond-hamlet-its-houses-boats-and-manure-jars.drawing.html.

NO DUCK PEN (269 B32, the GM 2026-09-28: "We should eliminate anything which is only modern, and this
includes the duck pen"). The fenced dry-and-wet-run pen is read only in a modern fish-cum-duck manual
(FAO/NACA, `fao-ac264e`); the premodern delta's ducks were herded in the rice fields, not penned at the
fish ponds (research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.html), so the stage draws sties only.

Research: pond-bank geometry - NONE: centroids and bank seat ranking
"""

from __future__ import annotations

import math
from typing import Any

from l7r.diagram.settlement import Settlement, knob_rng
from l7r.diagram.settlement.farm_fixtures import STY_FT
from l7r.diagram.settlement.fields.landuse import DIKEPOND_WATER_INSET

from .consts import Pt
from .plan import SitePlan

# The per-hamlet share band, as a fraction of households - a GUESS (see the module docstring).
STY_SHARE = (0.25, 0.50)
"""Research: share of households keeping a sty - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: a quarter to a half, rolled per hamlet"""
BANK_INSET_FT = DIKEPOND_WATER_INSET / 2  # half the bank between the parcel edge (the canal) and the water inset (feature 280 M58)
"""Research: sty on the bank - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: halfway between the parcel edge and the water"""


def _centroid(poly: list[Any]) -> Pt:
    return (sum(float(p[0]) for p in poly) / len(poly), sum(float(p[1]) for p in poly) / len(poly))


def _bank_seats(parcel: list[Any], toward: Pt, inset: float = BANK_INSET_FT) -> list[tuple[Pt, float]]:
    """EVERY seat on a parcel's bank, ranked by distance to `toward`: each the midpoint of a parcel
    edge, pulled in by half the bank so the fixture stands on the planted band, not on the canal at the
    edge. Each is (center, rotation along the edge in degrees).

    RANKED, not just the nearest (feature 233). It used to return the single nearest edge, and the
    caller skipped the whole pond when that seat did not fit - so adding the sluice clearance would
    have moved fixtures between ponds, or lost them, rather than along the bank they belong on. The
    caller walks this list and takes the first seat that fits, and BOUNDS how far down it it may go -
    see `stage_pond_stock`. This function ranks; it does not decide what is acceptable.

    Research:
        bank seats by distance - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: ranked nearest the houses, every seat of the bank - its midpoints and its eighths - in one ranking
        sty seat on the bank - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: each bank seat set in from the parcel's edge by half the bank's width - the map's own inset since feature 385 T10 (`BANK_INSET_FT` the fallback) - so the sty stands on the bank and not out by the canal
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25) - 0.125 (candidate seats at each eighth of a bank edge (the record gives the rule, not the fractions)); 0.25 (candidate seats at each eighth of a bank edge (the record gives the rule, not the fractions)); 0.375 (candidate seats at each eighth of a bank edge (the record gives the rule, not the fractions)); 0.625 (candidate seats at each eighth of a bank edge (the record gives the rule, not the fractions)); 0.75 (candidate seats at each eighth of a bank edge (the record gives the rule, not the fractions)); 0.875 (a search step or candidate the pass ruled with its row)
    """
    cx, cy = _centroid(parcel)
    n = len(parcel)

    def ranked(fracs: tuple[float, ...]) -> list[tuple[Pt, float]]:
        seats: list[tuple[Pt, float]] = []
        for i in range(n):
            a, b = parcel[i], parcel[(i + 1) % n]
            rot = math.degrees(math.atan2(float(b[1]) - float(a[1]), float(b[0]) - float(a[0])))
            for f in fracs:
                mx, my = float(a[0]) + (float(b[0]) - float(a[0])) * f, float(a[1]) + (float(b[1]) - float(a[1])) * f
                vx, vy = cx - mx, cy - my
                vl = math.hypot(vx, vy) or 1.0
                seats.append(((mx + vx / vl * inset, my + vy / vl * inset), rot))
        seats.sort(key=lambda s: math.dist(s[0], toward))
        return seats

    # ...EVERY SEAT OF THE BANK, IN ONE RANKING (feature 287, water W50: a sty whose every edge midpoint was taken by a
    # sluice or another shed lost its pond, so the bank's eighths are seats too; feature 328: the midpoints no longer rank
    # ahead of a nearer eighth - the sty takes the seat nearest the houses that has room, 0025)
    return ranked((0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875))


def sty_on_near_half(seat: Pt, parcel: list[Any], hc: Pt, margin: float = 0.0) -> bool:
    """THE RULE (feature 287, water W51; specs/233 research R7): a pig sty stands no further from the house cluster's
    centroid `hc` than its pond's own parcel center - on the side of the water the households are on. The placer and
    its test read this one predicate; the placer asks it `margin` stricter, since the sty is recorded rounded to 0.1.

    Research: sty on the near half - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: no farther from the houses than the pond's middle"""
    return math.dist(seat, hc) + margin <= math.dist(_centroid(parcel), hc)


def sty_in_reach(s: Settlement, seat: Pt, houses: list[Any], reach_ft: float = 0.0) -> bool:
    """THE RULE (feature 280, settlement-review of Kuwabata; carried into feature 287's placer): a sty stands within
    `STY_HOUSE_REACH_FT` of a farmhouse - it is a household's. The placer and its test read this one predicate; the
    reservation asks it of the seat's center, before the houses stand.

    Research: sty within a household's reach - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: 320 ft of a farmhouse"""
    return any(math.dist(seat, (float(h["x"]), float(h["y"]))) <= s.px(reach_ft or STY_HOUSE_REACH_FT) for h in houses)


STY_RESERVE_REACH_FT = (
    24.0  # the largest footprint's half-diagonal a reserved sty seat is held clear of - a farmhouse of about 40 x 28 ft; a GUESS at the envelope, not a researched figure (feature 287, water W50)
)
"""Research: reserved sty disc - GUESS: 24 ft, the largest footprint's half-diagonal"""


def reserve_sty_seat(s: Settlement, plan: SitePlan) -> tuple[Pt, float, int] | None:
    """THE STY'S SEAT, RESERVED BEFORE THE HOUSES (feature 287, water W50): the
    homesteads seated before `stage_pond_stock` could take every near bank seat. Once `stage_seat` has decided the flank,
    the grow-out ponds are walked nearest the seat's center first, and the first with a bank seat on its near half
    (`sty_on_near_half`) that clears the sluices (`pond_fixture_fits`) and stands within reach of the seat (`sty_in_reach`)
    gives it; a disc about it - the sty's own reach plus the largest footprint's
    half-diagonal (`STY_RESERVE_REACH_FT`) - goes into `block_polys`, which every homestead placer refuses. Recorded on
    the settlement for `stage_pond_stock`; returns (seat, rotation, pond), or None where the hamlet keeps no grow-out pond
    (no sty is owed) or where no grow-out pond has a seat within reach of it: a household with no pond within reach keeps
    none (feature 374 wave 140; until then such a hamlet was refused, a floor of one sty that no page gives).

    Research:
        no seat in reach, no sty - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: a household with no pond within that reach keeps none
        nearest pond first - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: grow-out ponds walked nearest the seat
        seat reserved before the houses - NONE: placement order, the sty's rules unchanged
        the reserved seat on the near half - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: on the half of its pond's bank facing the seat (`sty_on_near_half`)
        the reserved seat clear of the sluices - GUESS research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: `pond_fixture_fits` keeps the sty off a drawn sluice only; the record is silent on a sluice beside a sty
        the reserved seat's disc - GUESS: no homestead within the sty's half-diagonal, 2 ft and `STY_RESERVE_REACH_FT` (24 ft) of it
        its search steps and tolerances - GUESS: no source could speak to it, a value of ours (feature 417 T38 pass N5, 2026-10-25) - 16 (reserved disc drawn as a 16-gon)
    """
    ponds = s.M.get("dikeponds") or []
    if plan.field_archetype != "mulberry_dike_fishpond" or not ponds or not plan.seat:
        return None
    toward = (float(plan.seat["cx"]), float(plan.seat["cy"]))
    order = sorted((i for i, p in enumerate(ponds) if p.get("kind") != "fry"), key=lambda i: math.dist(_centroid(ponds[i]["parcel"]), toward))
    if not order:
        return None
    for i in order:
        par = ponds[i]["parcel"]
        seat = next(
            (
                ((x, y), rot)
                for (x, y), rot in _bank_seats(par, toward, getattr(s, "dikepond_inset", DIKEPOND_WATER_INSET) / 2)
                if sty_on_near_half((x, y), par, toward, 0.5) and sty_in_reach(s, (x, y), [{"x": toward[0], "y": toward[1]}]) and s.pond_fixture_fits(x, y, rot)
            ),
            None,
        )
        if seat is None:
            continue
        (x, y), rot = seat
        reach = math.hypot(s.px(STY_FT[0]), s.px(STY_FT[1])) / 2 + s.px(2.0) + s.px(STY_RESERVE_REACH_FT)
        s.block_polys.append([(x + reach * math.cos(math.tau * k / 16), y + reach * math.sin(math.tau * k / 16)) for k in range(16)])
        s.__dict__["_sty_seat"] = ((x, y), rot, i)
        return (x, y), rot, i
    return None


STY_HOUSE_REACH_FT = 320.0
"""How far from a farmhouse a sty may stand: the farthest main drew (feature 233's sties, 155-320 ft). A sty is a household's,
and once feature 280's fry village took the smaller ponds the grow-out ponds left lay out to the block's far end - sties
480-1,235 ft from any house (settlement-review of Kuwabata); a household with no grow-out pond in reach keeps none.

Research: sty reach - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: 320 ft"""


def stage_pond_stock(s: Settlement, plan: SitePlan) -> None:
    """Pig sties on the ponds.

    A dike-pond hamlet's livestock fixture (feature 150 A3): pig sties on the dikes of the grow-out ponds nearest
    the houses. It runs after the appurtenances because each sty is sited relative to the houses as placed - the first
    taking the seat reserved for it before the houses (`reserve_sty_seat`) wherever that still qualifies - and
    before the lane web because it reserves ground the web must thread around, like the byres and wells before it.
    Nothing on a valley hamlet, hence the card. The duck pen this stage once drew is retired (269 B32; the module
    docstring).

    Pig sties on the dikes of the ponds nearest the houses (dike-pond only).

    Steps:
        l7r.diagram.hamletgen.pondstock._bank_seats
        l7r.diagram.settlement.Settlement.pond_fixture_fits
        l7r.diagram.settlement.Settlement.pig_sty

    Research:
        sties at the dike-pond only - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.html, research/questions/0049-pigs-and-ducks-in-south-china-rice-villages.drawing.html: the pig as the dike-pond district's animal; a sty AT A POND only on a dike-pond hamlet (a paddy hamlet's sties are its farmsteads', not the ponds')
        privy over the sty - research/questions/0047-farm-privies-and-their-night-soil-benjo.drawing.html: the sty drawn alone, never
            with a privy built over it
        no duck pen - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.html: ducks herded in the rice, the pen modern
        sty count - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: a quarter to a half of households
        at least one sty where one fits - GUESS: searched, the record silent (feature 417 T36 pass P7, 2026-10-25); the share rounded up to one, the floor of one not on the page
        no seat in reach, no sty - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: a household with no pond within that reach keeps none; the hamlet is drawn with none and says why (`meta.pond_stock.none_why`)
        one sty per pond, nursery ponds none - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: nearest the houses first
        sty on the near half - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html
        sty within reach - research/questions/0025-pigs-and-ducks-at-a-dike-pond-the-sty-on-the-pond-dike.drawing.html: 320 ft of a farmhouse
    """
    # A FIX HELD (feature 328 wave 86, 2026-10-09): the pig toilet (0048, 0047) puts the household's privy over its sty. A
    # glyph-only form - the privy's mark on the shed, the farmsteads keeping their own privies - was built and its plan
    # BLOCKED (the household's privy left where it was), then reverted. The whole fix needs a sty-to-household mapping and a
    # privy off its farmstead under `undrawn_rolls` and 0047's seat rules: E3 (m:wave86-privy-over-the-sty-held; the patch
    # is in the spec's audit/reverted/).
    ponds = s.M.get("dikeponds") or []
    houses = s.M.get("houses") or []
    if plan.field_archetype != "mulberry_dike_fishpond" or not ponds or not houses:
        return
    rng = knob_rng(s.seed, "pond_stock")
    # AT LEAST ONE WHERE ONE FITS (feature 287, water W50; feature 150 A3): the dike-pond loop fed its fish from the sties on
    # its dikes, so the share rounds up to one, however few households it rounds to - where a seat is in reach (wave 140).
    n_sty = max(1, round(len(houses) * (STY_SHARE[0] + rng.random() * (STY_SHARE[1] - STY_SHARE[0]))))
    stock: dict[str, Any] = {"sties": n_sty}
    s.M["meta"]["pond_stock"] = stock
    hc = (sum(float(h["x"]) for h in houses) / len(houses), sum(float(h["y"]) for h in houses) / len(houses))
    # grow-out ponds only, nearest the houses first; each pond takes at most one sty
    order = sorted((i for i, p in enumerate(ponds) if p.get("kind") != "fry"), key=lambda i: math.dist(_centroid(ponds[i]["parcel"]), hc))
    done = 0
    # THE RESERVED SEAT FIRST (water W50, `reserve_sty_seat`): held clear of the homesteads, and taken wherever it stands on
    # the near half of its pond for the houses as seated; else the walk below, which it only ever adds to
    reserved = s.__dict__.get("_sty_seat")
    if reserved is not None:
        (rx, ry), rrot, ri = reserved
        if sty_on_near_half((rx, ry), ponds[ri]["parcel"], hc, 0.5) and sty_in_reach(s, (rx, ry), houses) and s.pond_fixture_fits(rx, ry, rrot):
            s.pig_sty(rx, ry, rot=rrot, pond=ri)
            done += 1
            order = [i for i in order if i != ri]
    for i in order:
        if done >= n_sty:
            break
        # the nearest seat to the houses that FITS - not the nearest seat, take it or leave the
        # pond (feature 233): a refused seat used to cost the pond its sty entirely.
        #
        # BOUNDED TO THE NEAR HALF OF THE POND (feature 233, settlement-review). Ranking alone
        # leaves the accept set the WHOLE perimeter, and on the ponds that carry a sty the far bank
        # runs 155.6 to 320.0 ft further from the houses than the first choice - a shed that took one
        # would read as belonging to no household, and nothing in the placer or the gate would say so.
        # The bound is geometric rather than a tuned distance: a seat may not be further from the house
        # cluster than the pond's own PARCEL center is (`_centroid(parcel)` below), which keeps the sty on
        # the side of the water the households are on. Figures: specs/233-pigsty-clear-of-the-sluice/research.md R7.
        par = ponds[i]["parcel"]
        # ...AND WITHIN A HOUSEHOLD'S REACH (feature 280, `sty_in_reach`): a seat past every farmhouse's reach is no seat
        seat = next(
            (
                ((x, y), rot)
                for (x, y), rot in _bank_seats(par, hc, getattr(s, "dikepond_inset", DIKEPOND_WATER_INSET) / 2)
                if sty_on_near_half((x, y), par, hc, 0.5) and sty_in_reach(s, (x, y), houses) and s.pond_fixture_fits(x, y, rot)
            ),
            None,
        )
        if seat is None:
            continue
        (x, y), rot = seat
        s.pig_sty(x, y, rot=rot, pond=i)
        done += 1
    s.M["meta"]["pond_stock"]["drawn"] = done
    # NONE IN REACH, NONE DRAWN (feature 374 wave 140; 0025: "a household with no pond within that reach keeps none"): the
    # hamlet keeps no sty, and its record says which of the three rules the reserved seat failed, or that none was reserved.
    if done == 0 and any(p.get("kind") != "fry" for p in ponds):
        why = "the reserved seat failed " + ", ".join(seat_faults(s, reserved, ponds, hc, houses)) if reserved is not None else "no grow-out pond had a seat within reach"
        stock["none_why"] = why


def seat_faults(s: Settlement, reserved: tuple[Pt, float, int], ponds: list[Any], hc: Pt, houses: list[Any]) -> list[str]:
    """Which of the sty's three rules the seat reserved before the houses fails for the houses as seated - named in the
    hamlet's record, so a hamlet drawn with no sty says why without a probe (feature 374 wave 140)."""
    (rx, ry), rrot, ri = reserved
    nearest_ft = min(math.dist((rx, ry), (float(h["x"]), float(h["y"]))) for h in houses) * s.ftpx
    faults = [
        name
        for name, ok in (
            ("the near half (the houses' middle moved)", sty_on_near_half((rx, ry), ponds[ri]["parcel"], hc, 0.5)),
            (f"a household's reach (nearest farmhouse {nearest_ft:.0f} ft, reach {STY_HOUSE_REACH_FT:.0f})", sty_in_reach(s, (rx, ry), houses)),
            ("the fit (a sluice or a shed took it)", s.pond_fixture_fits(rx, ry, rrot)),
        )
        if not ok
    ]
    return faults or ["none (the seat qualifies; the pond loop found no other)"]
