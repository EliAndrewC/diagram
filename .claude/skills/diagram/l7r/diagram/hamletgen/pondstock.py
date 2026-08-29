"""STAGE 6b (feature 150, GM 2026-08-28 choosing audits A3 and A4): the stock a dike-pond hamlet keeps ON its ponds.

The dike-pond loop fed its fish with more than silkworm waste: "pigs, chickens and ducks are reared on
the dykes, to provide manure to fertilise the fishponds" (Ruddle & Zhong via `isis-dykepond`), the
pig shed "constructed on the pond dyke or over the water surface" so the excreta run straight in, and
fish-cum-duck ponds fence a DRY RUN on the dike and a WET RUN in a corner of the water (FAO/NACA,
`fao-ac264e`). The premodern SHARE of households keeping either is not in anything read - the bands
below are GUESSES and the class entries say so - so they are rolled from the hamlet's seed like every
other share, and each fixture takes a pond of its own nearest the houses: the sty sits on the bank
between the parcel's edge and its water, the pen's dry run on the same bank with its wet run fenced
into the pond. Research: research/archetypes.md "What stands on a dike-pond hamlet that a paddy
hamlet lacks - the audit".
"""

from __future__ import annotations

import math
from typing import Any

from l7r.diagram.settlement import Settlement, knob_rng

from .consts import Pt
from .plan import SitePlan

# The per-hamlet share bands, as a fraction of households - GUESSES (see the module docstring).
STY_SHARE = (0.25, 0.50)
PEN_SHARE = (0.10, 0.30)
BANK_INSET_FT = 5.5  # half the ~11 ft bank between the parcel edge (the canal) and the water inset


def _centroid(poly: list[Any]) -> Pt:
    return (sum(float(p[0]) for p in poly) / len(poly), sum(float(p[1]) for p in poly) / len(poly))


def _bank_seat(parcel: list[Any], toward: Pt) -> tuple[Pt, float]:
    """The seat on a parcel's bank nearest `toward`: the midpoint of the parcel edge facing it, pulled
    in by half the bank so the fixture stands on the planted band, not on the canal at the edge.
    Returns (center, rotation along the edge in degrees)."""
    cx, cy = _centroid(parcel)
    best: tuple[float, Pt, float] | None = None
    n = len(parcel)
    for i in range(n):
        a, b = parcel[i], parcel[(i + 1) % n]
        mx, my = (float(a[0]) + float(b[0])) / 2, (float(a[1]) + float(b[1])) / 2
        d = math.dist((mx, my), toward)
        if best is None or d < best[0]:
            rot = math.degrees(math.atan2(float(b[1]) - float(a[1]), float(b[0]) - float(a[0])))
            best = (d, (mx, my), rot)
    assert best is not None
    (mx, my), rot = best[1], best[2]
    vx, vy = cx - mx, cy - my
    vl = math.hypot(vx, vy) or 1.0
    return (mx + vx / vl * BANK_INSET_FT, my + vy / vl * BANK_INSET_FT), rot


def stage_pond_stock(s: Settlement, plan: SitePlan) -> None:
    """Pig sties on the dikes and duck pens at the pond corners nearest the houses (dike-pond only)."""
    ponds = s.M.get("dikeponds") or []
    houses = s.M.get("houses") or []
    if plan.field_archetype != "mulberry_dike_fishpond" or not ponds or not houses:
        return
    rng = knob_rng(s.seed, "pond_stock")
    n_sty = round(len(houses) * (STY_SHARE[0] + rng.random() * (STY_SHARE[1] - STY_SHARE[0])))
    n_pen = round(len(houses) * (PEN_SHARE[0] + rng.random() * (PEN_SHARE[1] - PEN_SHARE[0])))
    s.M["meta"]["pond_stock"] = {"sties": n_sty, "pens": n_pen}
    hc = (sum(float(h["x"]) for h in houses) / len(houses), sum(float(h["y"]) for h in houses) / len(houses))
    # grow-out ponds only, nearest the houses first; each pond takes at most one fixture
    order = sorted((i for i, p in enumerate(ponds) if p.get("kind") != "fry"), key=lambda i: math.dist(_centroid(ponds[i]["parcel"]), hc))
    taken: set[int] = set()
    # PENS FIRST: ducks are driven out to the water and penned back every day, pigs are fed where they stand -
    # so the pens take the nearest ponds and the sties the next (settlement-review: sties on the seven nearest,
    # pens on the ninth and tenth read as a placement order, not a household's walk). The record ranks neither.
    for kind, want in (("pen", n_pen), ("sty", n_sty)):
        done = 0
        for i in order:
            if done >= want:
                break
            if i in taken:
                continue
            (x, y), rot = _bank_seat(ponds[i]["parcel"], hc)
            if not s.pond_fixture_fits(x, y, rot, kind):
                continue
            taken.add(i)
            if kind == "sty":
                s.pig_sty(x, y, rot=rot, pond=i)
            else:
                s.duck_pen(x, y, rot=rot, pond=i, water=[(float(q[0]), float(q[1])) for q in ponds[i]["water"]])
            done += 1
