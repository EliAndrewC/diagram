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
from l7r.diagram.waterfields.palette import _RICE_GREEN, AZE, FLOODED, RIPE_GOLD, aze_w

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
STATE_FILL = {"green": _RICE_GREEN, "wet": FLOODED, "flooded": FLOODED, "gold": RIPE_GOLD}
"""Research: the plots' paint - research/questions/0007-wet-paddies-that-never-drain-shitsuden.drawing.html: the wet paddy tinted blue-green where other plots are green; research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.html: one in sixteen still flooded, one in twenty gold"""


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
