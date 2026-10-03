"""The persimmon a household could not keep, given to one that has room (feature 315).

A rolled knob is honored by what is drawn (the GM, 2026-08-24): the hamlet's persimmon share is rolled as a count and spread
over its households before any is seated, and a household whose dooryard has no seat for its tree out of every yard's and
bed's sun (`fixture_seats.PERSIMMON_DOORYARD_FT`, `fit._settle_persimmon`) keeps none - which left Sawada one short (15
drawn of 16 rolled, B10). Here each tree short of the count is offered, in turn, to a household that rolled none: laid in
that household's own dooryard by the same seat search (`fixture_seats._persimmon`), judged at the rake its house is drawn at,
clear of its parts, its own and its neighbors' plots' sun, every grove's conifers (B5b: the groves are drawn by now) and every
neighbor's grove.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.farm_fixtures import PERSIMMON_CROWN_FT
from l7r.diagram.settlement.homestead_parts.fixture_seats import SALT, FixtureForms, _persimmon, _sunlit
from l7r.diagram.settlement.homestead_parts.groves import over_a_conifer
from l7r.diagram.settlement.homestead_parts.tree_shade import CANOPY_SHADE_FT


def _turned(r: Sequence[float], hx: float, hy: float, deg: float) -> tuple[float, float, float, float]:
    """`r` (center x, center y, w, h) carried about (`hx`, `hy`) by `deg`, its size kept."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    dx, dy = float(r[0]) - hx, float(r[1]) - hy
    return (hx + dx * c - dy * s, hy + dx * s + dy * c, float(r[2]), float(r[3]))


def persimmon_for(s: Settlement, h: Mapping[str, Any], forms: FixtureForms) -> dict[str, Any] | None:
    """A persimmon fixture record for household `h`, laid in its dooryard at its house's rake where the rules allow one, or None."""
    g = h.get("geom") or {}
    if not g.get("house"):
        return None
    hx, hy, hw, hh = (float(v) for v in g["house"])
    turn = float(g.get("turn") or 0.0)

    def frame(r: Sequence[float]) -> tuple[float, float, float, float]:  # world -> the house's unturned frame
        x, y, w, d = _turned(r, hx, hy, -turn)
        return (x - hx, y - hy, w, d)

    roofs = [(0.0, 0.0, hw, hh), *(frame(g[k]) for k in ("shed", "byre", "well") if g.get(k) is not None)]
    ground = [frame(r) for r in ([g["yard"]] if g.get("yard") is not None else []) + list(g.get("gardens") or ())]
    taken = [*roofs, *ground, *(frame(r) for r in (g.get("fixtures") or {}).values()), *(frame(b) for b in g.get("groves") or ())]
    sunlit = _sunlit(ground, s.px(CANOPY_SHADE_FT), (turn,))
    cones = getattr(s, "_conifer_crowns", None) or []

    crown, shade = s.px(PERSIMMON_CROWN_FT + 1.0), s.px(CANOPY_SHADE_FT)

    def clear(lx: float, ly: float, r: float) -> bool:
        wx, wy, _w, _d = _turned((hx + lx, hy + ly, 0.0, 0.0), hx, hy, turn)
        # ...and out of every neighbor's plots' sun, asked of each seat the search tries (feature 317): asked only of the seat it
        # chose, the search stopped at the first and the household gave the tree up, where a later seat shaded no one (Inashiro,
        # moved by the feature, kept 11 of 12 rolled)
        return (
            sunlit(lx, ly, r)
            and not any(over_a_conifer(cx, cy, cr, [(wx, wy, r)]) for cx, cy, cr in cones)
            and not s._persimmon_shades_a_neighbor(g, (wx, wy, 0.0, 0.0), crown, shade)
        )

    front = s._hjit(hx, hy, SALT["persimmon"] + 0.5) < forms.persimmon_front
    # ...ITS ROLLED SIDE OF THE HOUSE FIRST, THEN THE OTHER (feature 317): the tree is the hamlet's rolled count's, given here to
    # a household that rolled none, so the side is this household's preference and not a rule; with feature 317's tight seats
    # and moved maps, Inashiro's four households without a tree each had no seat on their rolled side and the count fell short
    # (11 drawn of 12 rolled, B10)
    for side in (front, not front):
        seat = _persimmon(hw, hh, taken, roofs, side, s.px, clear)
        if seat is None:
            continue
        x, y, w, d = _turned((hx + seat[0], hy + seat[1], seat[2], seat[3]), hx, hy, turn)
        # ...nor in a neighbor's grove (a neighbor's sun is the search's own test, `clear`)
        if any(rec is not h and any(abs(x - b[0]) < (w + b[2]) / 2 and abs(y - b[1]) < (d + b[3]) / 2 for b in (rec.get("geom") or {}).get("groves") or ()) for rec in s.M.get("houses") or ()):
            continue
        c, sn = abs(math.cos(math.radians(turn))), abs(math.sin(math.radians(turn)))
        return {"kind": "persimmon", "x": x, "y": y, "w": w, "h": d, "box": [x, y, w * c + d * sn, w * sn + d * c], "ft": [PERSIMMON_CROWN_FT * 2.0, PERSIMMON_CROWN_FT * 2.0]}
    return None


def reseat_persimmons(s: Settlement, houses: Sequence[dict[str, Any]], target: int, forms: FixtureForms) -> int:
    """Lay, for each tree the hamlet's rolled `target` is short of, a persimmon at the next household without one that has a
    seat for it (`persimmon_for`), in the houses' own order; the trees laid. Only on the map that keeps the sun corridor."""
    if not getattr(s, "_sun_corridor_ft", 0.0):
        return 0
    short = target - sum(1 for h in houses for f in h.get("fixtures") or () if f.get("kind") == "persimmon")
    laid = 0
    for h in houses:
        if laid >= short:
            break
        if any(f.get("kind") == "persimmon" for f in h.get("fixtures") or ()):
            continue
        rec = persimmon_for(s, h, forms)
        if rec is None:
            continue
        h.setdefault("fixtures", []).append(rec)
        g = h.get("geom") or {}
        g["fixtures"] = {**(g.get("fixtures") or {}), "persimmon": (rec["x"], rec["y"], rec["w"], rec["h"])}
        laid += 1
    return laid
