"""The comb field's ink, written from the Rust stage's records (feature 444 T16 D12).

WHY: the field's placement is Rust's (`rust/phases/src/field/`); its SVG stays Python's and reads only the records the stage
returns. The MIXED methods' ink is written here new from those records - the classes and paint of the classification table
(`specs/444-work-budget-program/phases/field.md`, "Who draws the field") - and never lifted from the old bodies; the five DRAWING
functions (`comb_base_fill`, `_comb_draw_beads`, `_draw_furrows`, `pond`, `_field_feature_ink`) are called as they are.

Research:
    the field's ink - NONE: drawing; each record's claims are at the Rust that places it
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from l7r.diagram.interactive.tags import Split
from l7r.diagram.settlement.water_ways.water import ditch_style
from l7r.diagram.waterfields.palette import _RICE_GREEN, AZE, BEAN_GREEN, FLOODED, aze_w

if TYPE_CHECKING:
    from ..core import Settlement

Pt = tuple[float, float]

DRY_STROKE = "#A98C58"
"""Research: the dry plot's outline - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: a thin tan-brown line, about 1.4 ft wide on a hamlet map, a map drawing convention"""
DRY_STROKE_FT = 1.4
"""Research: the dry plot's outline width - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: about 1.4 ft wide on a hamlet or town map"""
CROP_FILL = {"barley": "#C9B57A", "millet": "#C29A55", "buckwheat": "#D9CFC0", "soy": "#8DAA6A"}
"""Research: the dry crops' colors - research/questions/0006-dry-fields-and-their-crops-hatake.drawing.html: barley tan-gold, millet ochre, buckwheat pale with reddish stems, soybean green, each at its ripest"""
CROP_FURROW = {"barley": "#9C8650", "millet": "#8E6E36", "buckwheat": "#A8574A", "soy": "#5E7A44"}
"""Research: the furrows' colors - CONVENTION: each crop's own color, darkened so its rows read"""
POND_WATER, POND_RIM, POND_SHEEN, REED = "#9CB4C8", "#5C7488", "#B6CAD8", "#7FA040"
"""Research: the pocket pond's ink - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: an earthen bank round its edge, the wet ground where the reeds stand, open water in the middle"""
MOUND, MOUND_EDGE, STONE, STONE_EDGE = "#CFC6B4", "#8C8470", "#9AA1A4", "#5A584F"
"""Research: the grave's ink - research/questions/0008-ponds-rocks-and-graves-in-the-middle-of-the-fields.drawing.html: an island inside a plot, or a corner grave against the bunds"""


def _pts(ring: Sequence[Pt]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ring)


def paddies(s: Settlement, net: dict[str, Any], name: str) -> None:
    """Each basin by its state: a resting one through `rest_basin`, the rest a polygon in its paint with the bund round it -
    `wet paddy` for the wet low row, `paddy` otherwise (the classification's `_comb_draw_paddies` classes)."""
    bund = aze_w(s.ftpx)
    for p in net["plots"]:
        if p["rest"]:
            s.rest_basin(p["poly"], bund, name)
            continue
        cls = "wet paddy" if p["state"] == "wet" else "paddy"
        s.add_paddy(f'<polygon points="{_pts(p["poly"])}" fill="{p["fill"]}" stroke="{AZE}" stroke-width="{bund:.2f}" stroke-linejoin="round"/>', cls=Split(cls, "bund"))


def ditches(s: Settlement, net: dict[str, Any], archetype: str) -> None:
    """Each of the field's channels a tapered stroke in the late water block, its paint and class by its role."""
    for c in net["channels"]:
        col, cls = ditch_style(c["role"], archetype)
        s.field_channel(c["pts"], col, c["w"], c["w_tail"], late=True, cls=cls)


def dry_plots(s: Settlement, net: dict[str, Any]) -> None:
    """Each dry plot in its crop's paint with its thin outline, and its furrows (`_draw_furrows`)."""
    w = DRY_STROKE_FT / s.ftpx
    for d in net["dry_plots"]:
        s.add_paddy(f'<polygon points="{_pts(d["poly"])}" fill="{d["fill"]}" stroke="{DRY_STROKE}" stroke-width="{w:.2f}" stroke-linejoin="round"/>', cls=d["crop"])
        s._draw_furrows(d["poly"], d["furrow"], d["theta"], d["crop"])


def pocket_pond(s: Settlement, pond: dict[str, float]) -> None:
    """The pocket pond: its bank, its water, its sheen and a ring of reeds, class `field pond`."""
    x, y, rx, ry = pond["x"], pond["y"], pond["rx"], pond["ry"]
    s._field_feature_ink(None, f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx + 2.5:.1f}" ry="{ry + 2.5:.1f}" fill="{FLOODED}" stroke="{AZE}" stroke-width="2.2"/>', "field pond")
    s._field_feature_ink(None, f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{POND_WATER}" stroke="{POND_RIM}" stroke-width="1.2"/>', "field pond")
    s._field_feature_ink(None, f'<ellipse cx="{x - rx * 0.2:.1f}" cy="{y - ry * 0.2:.1f}" rx="{rx * 0.5:.1f}" ry="{ry * 0.4:.1f}" fill="none" stroke="{POND_SHEEN}" stroke-width="0.9"/>', "field pond")
    reeds = []
    for k in range(8):
        a = k / 8 * math.tau
        cx, cy = x + (rx + 1.2) * math.cos(a), y + (ry + 1.2) * math.sin(a)
        reeds.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy - 2.4:.1f}"/>')
    s._field_feature_ink(None, f'<g opacity="0.9" stroke="{REED}" stroke-width="1.1">{"".join(reeds)}</g>', "field pond")


def grave(s: Settlement, g: dict[str, Any]) -> None:
    """The grave: its mound and its stones, class `field grave`."""
    x, y = g["x"], g["y"]
    s._field_feature_ink(None, f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6.5" ry="4.5" fill="{MOUND}" stroke="{MOUND_EDGE}" stroke-width="1.2"/>', "field grave")
    stones = "".join(f'<rect x="{x - 3 + 3 * k:.1f}" y="{y - 2.5:.1f}" width="1.8" height="3" fill="{STONE}" stroke="{STONE_EDGE}" stroke-width="0.5"/>' for k in range(2))
    s._field_feature_ink(None, f"<g>{stones}</g>", "field grave")


def weir(s: Settlement, w: dict[str, Any]) -> None:
    """The weir across the brook at the intake, its bar in its form's thickness, class `weir`."""
    s.add(f'<polygon points="{_pts(w["poly"])}" fill="#7A6A52" stroke="#4E4232" stroke-width="0.6"/>', cls="weir")


def draw(s: Settlement, net: dict[str, Any], name: str, archetype: str) -> None:
    """The field's ink in its order: the floor under the plots (`comb_base_fill`), the plots, the dry hem, the channels, the
    beans (`_comb_draw_beads`), then the features."""
    s.comb_base_fill(net, name)
    paddies(s, net, name)
    dry_plots(s, net)
    ditches(s, net, archetype)
    s._comb_draw_beads(net)
    for pond in net.get("pocket_ponds", []):
        pocket_pond(s, pond)
    for g in net.get("grave_records", []):
        grave(s, g)


def settle(s: Settlement) -> None:
    """The beans settled after the last water (feature 287 W33, at `finish`): each field's bead slot rewritten from the runs that
    survive the map's final water - its ditches, channels and streams, the pond and the field ponds - in Rust (`settle_runs`),
    its record's `bund_beans` with it."""
    from l7r.diagram.hamletgen.phases_ext import phases

    if not s._bead_slots:
        return
    segs: list[tuple[tuple[float, float], tuple[float, float], float]] = []
    for key in ("field_ditches", "channels", "streams"):
        for rec in s.M.get(key) or []:
            pts = rec.get("poly") or []
            w = float(max(rec.get("w") or 1.5, rec.get("w_tail") or 0.0))
            segs += [((float(a[0]), float(a[1])), (float(b[0]), float(b[1])), w) for a, b in zip(pts, pts[1:], strict=False)]
    ponds = [tuple(float(v) for v in s.M["pond"][:4])] if s.M.get("pond") else []
    ponds += [(float(p["x"]), float(p["y"]), float(p["rx"]), float(p["ry"])) for p in s.M.get("field_ponds") or []]
    for z, runs, rec, own in s._bead_slots:
        kept = phases().settle_runs([[(float(x), float(y)) for x, y in r] for r in runs], segs, ponds + [tuple(float(v) for v in p) for p in own])
        rec["bund_beans"] = [[x, y] for r in kept for x, y in r]
        beads = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{BEAN_GREEN}"/>' for r in kept for x, y in r)
        s.out[z] = f'<g opacity="0.85">{beads}</g>'


DIKE_EARTH, DIKE_EDGE = "#B79B68", "#9C8150"
"""Research: the dike's band - CONVENTION: the shared dike drawing's earth and its edge"""
CROWN_FILL = {"willow": "#6E8B4A", "mulberry": "#87A45C", "fruit": "#7C9A54", "tea": "#5E7C40"}
"""Research: the crowns' greens - CONVENTION: the shared dike drawing's willow and mulberry, the banks' fruit and tea"""
BANK_FILL, POND_WATER_FRY = "#A9AE7C", "#A7B3AE"
"""Research: a pond's bank and a nursery's water - research/questions/0024-fish-fry-and-nursery-ponds-yumiao.drawing.html: its fry ponds drawn in grayer, muddier water than the clear ponds; the bank's earth a CONVENTION"""


def dike(s: Settlement, dk: dict[str, Any]) -> None:
    """The polder's dike as the Rust placed it: the band between its faces, its two rows of crowns, and a gate at each sluice."""
    outer, inner = _pts(dk["outer"]), _pts(dk["inner"])
    s.add(f'<path d="M {outer} Z M {inner} Z" fill="{DIKE_EARTH}" fill-rule="evenodd" stroke="{DIKE_EDGE}" stroke-width="1.0"/>', cls="perimeter dike")
    for kind, crowns in dk["trees"]:
        dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in crowns)
        s.add(f'<g fill="{CROWN_FILL.get(kind, "#6E8B4A")}" opacity="0.92">{dots}</g>', cls="perimeter dike")
    for x, y in dk["gaps"]:
        s.add(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" fill="#8C7A5A" stroke="#5A4A32" stroke-width="0.8"/>', cls="sluice gate")


def dikeponds(s: Settlement, parcels: Sequence[Any], crops: Any, bund: float) -> None:
    """The dike-pond block as the Rust converted it: each pond's bank and water (a nursery's grayer), each rice parcel, and the
    banks' crop."""
    for kind, parcel, bank, water in parcels:
        if kind == "rice":
            s.add_paddy(f'<polygon points="{_pts(parcel)}" fill="{_RICE_GREEN}" stroke="{AZE}" stroke-width="{bund:.2f}" stroke-linejoin="round"/>', cls=Split("paddy", "bund"))
            continue
        cls = "fry pond" if kind == "fry" else "fish pond"
        s.add_paddy(f'<path d="{bank[0]}" fill="{BANK_FILL}" stroke="{AZE}" stroke-width="{bund:.2f}"/>', cls=cls)
        s.add(f'<path d="{water[0]}" fill="{POND_WATER_FRY if kind == "fry" else POND_WATER}" stroke="{POND_RIM}" stroke-width="1.0"/>', cls=cls)
    crop, crowns, hedges = crops
    cls = f"{crop} dike" if crop in ("mulberry", "fruit", "tea") else "mulberry dike"
    if crowns:
        dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in crowns)
        s.add(f'<g fill="{CROWN_FILL.get(crop, "#87A45C")}" opacity="0.9">{dots}</g>', cls=cls)
    for h in hedges:
        s.add(f'<polyline points="{_pts(h)}" fill="none" stroke="{CROWN_FILL["tea"]}" stroke-width="3" stroke-linecap="butt"/>', cls=cls)
