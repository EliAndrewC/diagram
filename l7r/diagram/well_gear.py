"""A well's lifting gear and its roof on a Mode A sheet (feature 374 wave 135): the rolls and the glyph.

research/questions/0196-communal-wells-ido.drawing.html: "The lifting gear is a knob, weighted by how deep the water lies. On
shallow water about three wells in four take a sweep ... on deeper water about three in four take a pulley frame"; "Our maps
take a valley floor or river plain to hold shallow water, an upland or terrace deep water"; "A roof is drawn over about one
well in three." A sheet whose notes record its landform takes the depth that landform gives; one whose notes record none
rolls it from its seed (its name). Each well's gear and roof are rolled from the seed by the well's order on the sheet.
The generated drafts call these; a hand sheet records the same recipes in its notes and draws what they give.
"""

from __future__ import annotations

import math
import random
import zlib

WATER_DEPTHS: tuple[str, str] = ("shallow", "deep")
GEARS: tuple[str, str] = ("sweep", "pulley frame")
GEAR_SHARE: float = 0.75  # the depth's own gear on about three wells in four: a GUESS on the drawing page
"""Research: well gear share - GUESS research/questions/0196-communal-wells-ido.drawing.html: the depth's own lifting gear (sweep on shallow, pulley frame on deep water) is drawn on about three wells in four; the gears are attested, the three-in-four split is the page's guess."""
ROOF_SHARE: float = 1.0 / 3.0  # a roof over about one well in three: a GUESS on the drawing page

GEAR_INK = "#5A3F1E"
ROOF_STROKE = "#6B5836"


def _draw(sheet: str, what: str) -> float:
    return random.Random(zlib.crc32(f"{sheet}:{what}".encode())).random()


def water_depth(sheet: str) -> str:
    """A sheet's water depth where its notes record no landform: rolled from its name, in the drawing page's order.

    Research:
        water depth from the ground - research/questions/0196-communal-wells-ido.drawing.html: a valley floor or river plain shallow, an upland or terrace deep (the page's GUESS); a sheet recording no landform rolls between the two"""
    return random.Random(zlib.crc32(f"{sheet}:water depth".encode())).choice(WATER_DEPTHS)


def well_gear(sheet: str, i: int, depth: str) -> str:
    """The `i`-th well's lifting gear: the depth's own gear on about three wells in four, the other on the rest.

    Research:
        gear by depth - research/questions/0196-communal-wells-ido.drawing.html: a sweep on shallow water, a pulley frame on deep, about three in four (the share a GUESS)"""
    common = GEARS[0] if depth == "shallow" else GEARS[1]
    other = GEARS[1] if common == GEARS[0] else GEARS[0]
    return common if _draw(sheet, f"well gear {i}") < GEAR_SHARE else other


def well_roofed(sheet: str, i: int) -> bool:
    """Whether the `i`-th well has a roof on posts: about one well in three.

    Research:
        a roof on some wells - research/questions/0196-communal-wells-ido.drawing.html: about one well in three (a GUESS)"""
    return _draw(sheet, f"well roof {i}") < ROOF_SHARE


def gear_svg(cx: float, cy: float, half: float, gear: str, roofed: bool, indoor: bool = False) -> str:
    """The roof and the gear of a well whose curb is centered at (`cx`, `cy`) px, `half` px from center to side, drawn
    over the curb, each a group tagged a part of the well (its posts small circles, never a door's small dark rect) with
    the well's center (`data-at`), which the pack audit's `well_gear` reads. An `indoor` well (its curb inside a
    building) draws neither its rolled gear nor a roof: its pulley hangs from the building's beams (plan W135-2). The
    generated drafts seat every well in the open, so they never pass it; the hand sheets draw the same glyph by hand.

    Research:
        sweep glyph - research/questions/0196-communal-wells-ido.drawing.html: a pole about as long as the marker is wide crossing the curb from a post outside it
        pulley frame glyph - research/questions/0196-communal-wells-ido.drawing.html: two posts and a beam across the curb; the drawn proportions a GUESS
        beam pulley glyph - GUESS research/questions/0196-communal-wells-ido.drawing.html: an indoor well's pulley hung from its building's beams, drawn as the beam across the curb and the wheel at its middle, no posts and no roof; no page names an indoor well's gear
        roof glyph - CONVENTION: an unfilled outline (a path, so it buries nothing) 4 px outside the curb on four corner posts, drawn over the curb, so it reads as a roof standing over the well and not as the paved apron the same page draws
        its drawn proportions - GUESS research/questions/0196-communal-wells-ido.drawing.html: 3.5 (pulley frame's left post offset); 1.5 (crossbar end offset)
        its right post - GUESS research/questions/0196-communal-wells-ido.drawing.html: 0.5 (pulley frame's right post offset)
        its glyph sizes - CONVENTION: sizes on the sheet, not in the world - 2 (sweep post off the curb's corner); 1.6 (post radius); 2.2 (wheel radius); 1.2 (stroke); 1.1 (stroke); 3 (roof dash)
    """
    at = f'data-at="{cx:g},{cy:g}"'
    if indoor:
        return (
            f'<g data-kind="well" data-gear="beam pulley" {at}><line x1="{cx - half:g}" y1="{cy:g}" x2="{cx + half:g}" y2="{cy:g}" '
            f'stroke="{GEAR_INK}" stroke-width="2"/><circle cx="{cx:g}" cy="{cy:g}" r="2.2" fill="none" stroke="{GEAR_INK}" stroke-width="1.2"/></g>'
        )
    roof = ""
    if roofed:
        r = half + 4.0
        posts = "".join(f'<circle cx="{cx + dx:g}" cy="{cy + dy:g}" r="1.6" fill="{ROOF_STROKE}"/>' for dx in (-r, r) for dy in (-r, r))
        roof = (
            f'<g data-kind="well" data-roof="1" {at}><path d="M {cx - r:g} {cy - r:g} h {2 * r:g} v {2 * r:g} h {-2 * r:g} z" '
            f'fill="none" stroke="{ROOF_STROKE}" stroke-width="1.1" stroke-dasharray="3 2"/>{posts}</g>'
        )
    if gear == "sweep":
        # the pole as long as the marker is wide (2 * half), running from its post off the curb's corner in across it
        px, py = cx + half + 2.0, cy + half + 2.0
        ex, ey = round(px - half * math.sqrt(2.0), 2), round(py - half * math.sqrt(2.0), 2)
        return roof + (
            f'<g data-kind="well" data-gear="sweep" {at}><circle cx="{px:g}" cy="{py:g}" r="1.6" fill="{GEAR_INK}"/>'
            f'<line x1="{px:g}" y1="{py:g}" x2="{ex:g}" y2="{ey:g}" stroke="{GEAR_INK}" stroke-width="1.6"/></g>'
        )
    lx, rx = cx - half - 3.5, cx + half + 0.5
    return roof + (
        f'<g data-kind="well" data-gear="pulley frame" {at}><circle cx="{lx + 1.5:g}" cy="{cy:g}" r="1.6" fill="{GEAR_INK}"/>'
        f'<circle cx="{rx + 1.5:g}" cy="{cy:g}" r="1.6" fill="{GEAR_INK}"/>'
        f'<line x1="{lx + 1.5:g}" y1="{cy:g}" x2="{rx + 1.5:g}" y2="{cy:g}" stroke="{GEAR_INK}" stroke-width="2"/></g>'
    )
