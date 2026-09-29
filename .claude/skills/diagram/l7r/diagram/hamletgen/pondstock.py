"""STAGE 6b (feature 150, GM 2026-08-28 choosing audits A3 and A4): the stock a dike-pond hamlet keeps ON its ponds.

The dike-pond loop fed its fish with more than silkworm waste: "pigs, chickens and ducks are reared on
the dykes, to provide manure to fertilise the fishponds" (Ruddle & Zhong via `isis-dykepond`), the
pig shed "constructed on the pond dyke or over the water surface" so the excreta run straight in. The
premodern SHARE of households keeping a sty is not in anything read - the band below is a GUESS and the
class entry says so - so it is rolled from the hamlet's seed like every other share, and each sty takes
a pond of its own nearest the houses, on the bank between the parcel's edge and its water. Research:
research/archetypes.html "What stands on a dike-pond hamlet that a paddy hamlet lacks - the audit".

NO DUCK PEN (269 B32, the GM 2026-09-28: "We should eliminate anything which is only modern, and this
includes the duck pen"). The fenced dry-and-wet-run pen is read only in a modern fish-cum-duck manual
(FAO/NACA, `fao-ac264e`); the premodern delta's ducks were herded in the rice fields, not penned at the
fish ponds (research/archetypes/210), so the stage draws sties only.
"""

from __future__ import annotations

import math
from typing import Any

from l7r.diagram.settlement import Settlement, knob_rng
from l7r.diagram.settlement.fields.landuse import DIKEPOND_WATER_INSET

from .consts import Pt
from .plan import SitePlan

# The per-hamlet share band, as a fraction of households - a GUESS (see the module docstring).
STY_SHARE = (0.25, 0.50)
BANK_INSET_FT = DIKEPOND_WATER_INSET / 2  # half the bank between the parcel edge (the canal) and the water inset (feature 280 M58)


def _centroid(poly: list[Any]) -> Pt:
    return (sum(float(p[0]) for p in poly) / len(poly), sum(float(p[1]) for p in poly) / len(poly))


def _bank_seats(parcel: list[Any], toward: Pt) -> list[tuple[Pt, float]]:
    """EVERY seat on a parcel's bank, ranked by distance to `toward`: each the midpoint of a parcel
    edge, pulled in by half the bank so the fixture stands on the planted band, not on the canal at the
    edge. Each is (center, rotation along the edge in degrees).

    RANKED, not just the nearest (feature 233). It used to return the single nearest edge, and the
    caller skipped the whole pond when that seat did not fit - so adding the sluice clearance would
    have moved fixtures between ponds, or lost them, rather than along the bank they belong on. The
    caller walks this list and takes the first seat that fits, and BOUNDS how far down it it may go -
    see `stage_pond_stock`. This function ranks; it does not decide what is acceptable.
    """
    cx, cy = _centroid(parcel)
    seats: list[tuple[Pt, float]] = []
    n = len(parcel)
    for i in range(n):
        a, b = parcel[i], parcel[(i + 1) % n]
        mx, my = (float(a[0]) + float(b[0])) / 2, (float(a[1]) + float(b[1])) / 2
        rot = math.degrees(math.atan2(float(b[1]) - float(a[1]), float(b[0]) - float(a[0])))
        vx, vy = cx - mx, cy - my
        vl = math.hypot(vx, vy) or 1.0
        seats.append(((mx + vx / vl * BANK_INSET_FT, my + vy / vl * BANK_INSET_FT), rot))
    seats.sort(key=lambda s: math.dist(s[0], toward))
    return seats


STY_HOUSE_REACH_FT = 320.0
"""How far from a farmhouse a sty may stand: the farthest main drew (feature 233's sties, 155-320 ft). A sty is a household's,
and once feature 280's fry village took the smaller ponds the grow-out ponds left lay out to the block's far end - sties
480-1,235 ft from any house (settlement-review of Kuwabata); a household with no grow-out pond in reach keeps none."""


def stage_pond_stock(s: Settlement, plan: SitePlan) -> None:
    """Pig sties on the ponds.

    A dike-pond hamlet's livestock fixture (feature 150 A3): pig sties on the dikes of the grow-out ponds nearest
    the houses. It runs after the appurtenances because each sty is sited relative to the houses as placed, and
    before the lane web because it reserves ground the web must thread around, like the byres and wells before it.
    Nothing on a valley hamlet, hence the card. The duck pen this stage once drew is retired (269 B32; the module
    docstring).

    Pig sties on the dikes of the ponds nearest the houses (dike-pond only).

    Steps:
        l7r.diagram.hamletgen.pondstock._bank_seats
        l7r.diagram.settlement.Settlement.pond_fixture_fits
        l7r.diagram.settlement.Settlement.pig_sty
    """
    ponds = s.M.get("dikeponds") or []
    houses = s.M.get("houses") or []
    if plan.field_archetype != "mulberry_dike_fishpond" or not ponds or not houses:
        return
    rng = knob_rng(s.seed, "pond_stock")
    n_sty = round(len(houses) * (STY_SHARE[0] + rng.random() * (STY_SHARE[1] - STY_SHARE[0])))
    s.M["meta"]["pond_stock"] = {"sties": n_sty}
    hc = (sum(float(h["x"]) for h in houses) / len(houses), sum(float(h["y"]) for h in houses) / len(houses))
    # grow-out ponds only, nearest the houses first; each pond takes at most one sty
    order = sorted((i for i, p in enumerate(ponds) if p.get("kind") != "fry"), key=lambda i: math.dist(_centroid(ponds[i]["parcel"]), hc))
    done = 0
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
        reach = math.dist(_centroid(ponds[i]["parcel"]), hc)
        seat = next((((x, y), rot) for (x, y), rot in _bank_seats(ponds[i]["parcel"], hc) if math.dist((x, y), hc) <= reach and s.pond_fixture_fits(x, y, rot)), None)
        if seat is None:
            continue
        (x, y), rot = seat
        if min(math.dist((x, y), (float(h["x"]), float(h["y"]))) for h in houses) > s.px(STY_HOUSE_REACH_FT):
            continue
        s.pig_sty(x, y, rot=rot, pond=i)
        done += 1
    s.M["meta"]["pond_stock"]["drawn"] = done
