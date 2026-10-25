"""The persimmon a household could not keep, given to one that has room (feature 315).

A rolled knob is honored by what is drawn (the GM, 2026-08-24): the hamlet's persimmon share is rolled as a count and spread
over its households before any is seated, and a household whose dooryard has no seat for its tree out of every yard's and
bed's sun (`fixture_seats.PERSIMMON_DOORYARD_FT`, `fit._settle_persimmon`) keeps none - which left Sawada one short (15
drawn of 16 rolled, B10). Here each tree short of the count is offered, in turn, to a household that rolled none: laid in
that household's own dooryard by the same seat search (`fixture_seats._persimmon`), judged at the rake its house is drawn at,
clear of its parts, its own and its neighbors' plots' sun, every grove's conifers (B5b: the groves are drawn by now) and every
neighbor's grove.

Research: plumbing - NONE
"""

from __future__ import annotations

import math
import re
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
    """A persimmon fixture record for household `h`, laid in its dooryard at its house's rake where the rules allow one, or None.

    Research:
        persimmon in the dooryard - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: by the seat search every persimmon takes, front or behind
        out of the plots' sun - research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html: its own plots' and its neighbors', `CANOPY_SHADE_FT`
        its own grove gives way - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: its own grove's bands open to it, its own grove's crowns no bar (taken out after, `give_way`)
        under no other stand's conifer - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); a persimmon is refused under the crown of any other stand's conifer; the page records nothing for other stands
        in no other farm's grove - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: a neighbor's grove refuses the tree"""
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
    # ITS OWN GROVE OPEN TO IT, AS THE SEATING'S `fruit` ARE (feature 374 wave 152, 0046: "its own grove, no other farm's"):
    # the bands are not taken ground, and the grove's conifers are no bar - the grove gives way round the tree (`give_way`)
    taken = [*roofs, *ground, *(frame(r) for r in (g.get("fixtures") or {}).values())]
    sunlit = _sunlit(ground, s.px(CANOPY_SHADE_FT), (turn,))
    own = [tuple(float(v) for v in b) for b in g.get("groves") or ()]
    cones = [c for c in getattr(s, "_conifer_crowns", None) or [] if not in_bands(c[0], c[1], own)]

    crown, shade = s.px(PERSIMMON_CROWN_FT + 1.0), s.px(CANOPY_SHADE_FT)

    def clear(lx: float, ly: float, r: float) -> bool:
        wx, wy, _w, _d = _turned((hx + lx, hy + ly, 0.0, 0.0), hx, hy, turn)
        # ...and out of every neighbor's plots' sun, asked of each seat the search tries (feature 317): asked only of the seat it
        # chose, the search stopped at the first and the household gave the tree up, where a later seat shaded no one (Inashiro,
        # moved by the feature, kept 11 of 12 rolled)
        return sunlit(lx, ly, r) and not any(over_a_conifer(cx, cy, cr, [(wx, wy, r)]) for cx, cy, cr in cones) and not s._persimmon_shades_a_neighbor(g, (wx, wy, 0.0, 0.0), crown, shade)

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


def in_bands(x: float, y: float, bands: Sequence[Sequence[float]]) -> bool:
    """Is (x, y) inside one of `bands`, each a world box (center x, center y, w, h)?

    Research: plumbing - NONE: a point in a box"""
    return any(abs(x - b[0]) <= b[2] / 2 and abs(y - b[1]) <= b[3] / 2 for b in bands)


_CIRCLE = re.compile(r'<circle cx="(-?[0-9.]+)" cy="(-?[0-9.]+)" r="([0-9.]+)"[^>]*/>')
_TRANSLATE = re.compile(r'^<g transform="translate\((-?[0-9.]+),(-?[0-9.]+)\)">')


def give_way(s: Settlement, x: float, y: float, r: float, bands: Sequence[Sequence[float]]) -> int:
    """Take out every crown of the farm's own grove (centered in `bands`) that lies under a persimmon's crown at (x, y) of radius
    `r`: from the drawing (its clump's circle), from the record of crowns (`tree_crowns`) and from the conifers' list; the
    number taken out.

    Research: the grove gives way round it - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the grove's trees give way round the farm's persimmon, wholly - no crown's edge under its disc, as the seating's grove gives way
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.2 (float tolerance, matching an SVG circle)
    """

    def under(cx: float, cy: float, cr: float) -> bool:
        return in_bands(cx, cy, bands) and math.hypot(cx - x, cy - y) < cr + r + 0.2

    flat = s.M.get("tree_crowns") or []
    keep: list[float] = []
    gone: list[tuple[float, float]] = []
    for i in range(0, len(flat) - 2, 3):
        cx, cy, cr = float(flat[i]), float(flat[i + 1]), float(flat[i + 2])
        if under(cx, cy, cr):
            gone.append((cx, cy))
        else:
            keep += [flat[i], flat[i + 1], flat[i + 2]]
    if not gone:
        return 0
    s.M["tree_crowns"] = keep
    s._conifer_crowns = [c for c in getattr(s, "_conifer_crowns", None) or [] if not under(*c)]  # type: ignore[attr-defined]

    def drop(text: str) -> str:
        t = _TRANSLATE.match(text)
        if t is None:
            return text
        tx, ty = float(t.group(1)), float(t.group(2))
        return _CIRCLE.sub(lambda m: "" if any(abs(tx + float(m.group(1)) - gx) < 0.2 and abs(ty + float(m.group(2)) - gy) < 0.2 for gx, gy in gone) else m.group(0), text)

    s.out[:] = [drop(o) for o in s.out]
    return len(gone)


def reseat_persimmons(s: Settlement, houses: Sequence[dict[str, Any]], target: int, forms: FixtureForms) -> int:
    """Lay, for each tree the hamlet's rolled `target` is short of, a persimmon at the next household without one that has a
    seat for it (`persimmon_for`), in the houses' own order; the trees laid. Only on the map that keeps the sun corridor.

    Research:
        the rolled count honored - research/questions/0046-fruit-trees-in-the-farmyard-persimmon-chestnut-and-plum-kaki.drawing.html: the per-hamlet 80 to 95 in 100 share; each tree short of the hamlet's rolled count offered to a household without one
        which household takes it - GUESS: no source could speak to it, a value of ours (feature 417 T29 pass C, 2026-10-25); the next in the houses' own order that has a seat"""
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
        gave = give_way(s, rec["x"], rec["y"], rec["w"] / 2.0, [tuple(float(v) for v in b) for b in g.get("groves") or ()])
        s.M["meta"]["persimmon_grove_gave_way"] = int(s.M["meta"].get("persimmon_grove_gave_way", 0)) + gave
        g["fixtures"] = {**(g.get("fixtures") or {}), "persimmon": (rec["x"], rec["y"], rec["w"], rec["h"])}
        laid += 1
    return laid
