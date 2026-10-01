"""THE COVER TILES (feature 298): a ground cover that stands for an AREA, not for objects, drawn as one repeating tile.

The scrub's grass, the marsh's reeds and a bamboo stand's culms were thrown glyph by glyph - 55-68% of four pool hamlets' SVGs, and
every throw tested against the keep-outs and culled at the finish one at a time (specs/298). The GM (2026-10-01): "drawing
individual blades of grass and lines for marshland and scrubland" serves no purpose that individual trees do, so "instead of then
drawing individual glyphs within that ... some tiled pattern where a relatively small block of background is then repeated".
Each tile here lays the scatter's own glyphs - their shapes, colors, strokes and density per area - ONCE, from a fixed seed, and
the zone is filled with it (`Settlement.flush_covers`). A MAP DRAWING CONVENTION, recorded as such (research/vegetation, the
spec's Decisions Recorded); the GM does not mind the repetition.

SEAMLESS: a glyph whose extent crosses the tile's edge is laid again at the opposite edge, so the tiles meet without a cut. No
background: the land shows between the glyphs, as it did between the thrown ones."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

#: The grass and reed tile's side in feet (x the map's `bscale`): wide enough that a zone shows few repeats, small enough that
#: the tile is a few hundred glyphs. The bamboo tile is the stand's own grid (`bamboo_tile`).
COVER_TILE_FT = 64.0

#: One throw per this many square feet (x bscale^2) - the scatters' own densities: `commons` threw `area / 74` (14% of the kept
#: throws brush dots, the rest three-bladed tufts), the marsh a tint per 360 and a tuft per 150 (12% of them glints).
GRASS_SQFT_PER_THROW = 74.0
GRASS_DOT_SHARE = 0.14
REED_SQFT_PER_TINT = 360.0
REED_SQFT_PER_TUFT = 150.0
REED_GLINT_SHARE = 0.12

#: A fixed seed per kind: the tile is the same on every map (the GM does not mind the repetition), so a re-roll moves nothing.
_SEED = {"grass": 2981, "reed": 2982, "bamboo": 2983}


@dataclass
class Cover:
    """One zone a tile fills (`Settlement._covers`, drawn by `flush_covers`): its `kind` (a key of `TILES`), the class its shape
    is ruled under on the page (`cls`, the zone's), its `ring`, and the ground its scatter kept bare as shapely geometries
    (`bare` - a clearing swept later is added here, `_cull_cover_in`). `rec` is the zone's manifest record, which is given the
    drawn shape (`cover`) for the page's hit region."""

    kind: str
    cls: str | None
    ring: list[tuple[float, float]]
    bare: list[Any] = field(default_factory=list)
    rec: dict[str, Any] | None = None


def pattern_id(kind: str, bs: float) -> str:
    """The `<pattern>` id of `kind` at scale `bs` - one per kind and scale on a map."""
    return f"cover-{kind}-{bs:g}".replace(".", "_")


def _wrapped(side_w: float, side_h: float, glyph: Callable[[float, float], str], x: float, y: float, reach: float) -> str:
    """`glyph` drawn at (x, y) and again at each opposite edge its `reach` crosses, so the tile is seamless."""
    out = []
    for dx in (-side_w, 0.0, side_w):
        for dy in (-side_h, 0.0, side_h):
            px, py = x + dx, y + dy
            if px + reach >= 0 and px - reach <= side_w and py + reach >= 0 and py - reach <= side_h:
                out.append(glyph(px, py))
    return "".join(out)


def grass_tile(bs: float) -> str:
    """The scrub's tile: brush dots and three-bladed tufts of grass at the commons' density (`commons`, `grass_scatter` as it
    was): a dot `#94A063` r 1.5-2.4, a tuft three `#A7A860` blades 2.4-4.2 long within 0.45 rad of upright."""
    import numpy as np

    side = COVER_TILE_FT * bs
    n = round(side * side / (GRASS_SQFT_PER_THROW * bs * bs))
    rng = np.random.default_rng(_SEED["grass"])
    xs, ys, kind = rng.uniform(0, side, n), rng.uniform(0, side, n), rng.random(n)
    r_dot = rng.uniform(1.5, 2.4, n) * bs
    ang, blen = rng.uniform(-0.45, 0.45, (n, 3)), rng.uniform(2.4, 4.2, (n, 3)) * bs
    dots, blades = [], []
    for i in range(n):
        x, y = float(xs[i]), float(ys[i])
        if kind[i] < GRASS_DOT_SHARE:
            r = float(r_dot[i])
            dots.append(_wrapped(side, side, lambda px, py, r=r: f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}"/>', x, y, r))
            continue
        tips = [(math.sin(float(ang[i, k])) * float(blen[i, k]), -math.cos(float(ang[i, k])) * float(blen[i, k])) for k in range(3)]
        blades.append(_wrapped(side, side, lambda px, py, tips=tips: "".join(f"M{px:.1f},{py:.1f}l{tx:.1f},{ty:.1f}" for tx, ty in tips), x, y, 4.2 * bs))
    return (
        f'<pattern id="{pattern_id("grass", bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<g fill="#94A063" fill-opacity="0.85">{"".join(dots)}</g>'
        f'<path d="{"".join(blades)}" stroke="#A7A860" stroke-width="0.8" fill="none"/></pattern>'
    )


def reed_tile(bs: float) -> str:
    """The marsh's tile: the pale wet tint (`#9FBBAE` at 0.14, r 15-28), the standing-water glints (`#C2D6CE` ellipses) and the
    reed tufts - four near-vertical `#6E9377` blades 4-7 long within 0.2 rad of upright - at the marsh's densities (`marsh`)."""
    import numpy as np

    from .wet import MARSH_TINT_R

    side = COVER_TILE_FT * bs
    rng = np.random.default_rng(_SEED["reed"])
    tints, glints, reeds = [], [], []
    n_tint = round(side * side / (REED_SQFT_PER_TINT * bs * bs))
    for x, y, r in zip(rng.uniform(0, side, n_tint), rng.uniform(0, side, n_tint), rng.uniform(min(15.0, MARSH_TINT_R * 0.6), MARSH_TINT_R, n_tint) * bs, strict=True):
        rr = float(r)
        tints.append(_wrapped(side, side, lambda px, py, rr=rr: f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rr:.1f}"/>', float(x), float(y), rr))
    n = round(side * side / (REED_SQFT_PER_TUFT * bs * bs))
    xs, ys, glint = rng.uniform(0, side, n), rng.uniform(0, side, n), rng.random(n) < REED_GLINT_SHARE
    rx, ry = rng.uniform(2.6, 4.6, n) * bs, rng.uniform(1.2, 2.0, n) * bs
    ang, bl = rng.uniform(-0.2, 0.2, (n, 4)), rng.uniform(4.0, 7.0, (n, 4)) * bs
    for i in range(n):
        x, y = float(xs[i]), float(ys[i])
        if glint[i]:
            a, b = float(rx[i]), float(ry[i])
            glints.append(_wrapped(side, side, lambda px, py, a=a, b=b: f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{a:.1f}" ry="{b:.1f}"/>', x, y, a))
            continue
        tips = [(math.sin(float(ang[i, k])) * float(bl[i, k]), -math.cos(float(ang[i, k])) * float(bl[i, k])) for k in range(4)]
        reeds.append(_wrapped(side, side, lambda px, py, tips=tips: "".join(f"M{px:.1f},{py:.1f}l{tx:.1f},{ty:.1f}" for tx, ty in tips), x, y, 7.0 * bs))
    return (
        f'<pattern id="{pattern_id("reed", bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<g fill="#9FBBAE" fill-opacity="0.14">{"".join(tints)}</g>'
        f'<g fill="#C2D6CE" fill-opacity="0.85">{"".join(glints)}</g>'
        f'<path d="{"".join(reeds)}" stroke="#6E9377" stroke-width="0.8" fill="none"/></pattern>'
    )


#: The bamboo stand's grid (`bamboo_stand` as it was): a mark per 7 ft, rows 0.86 of that apart and every other row offset
#: half a step, each mark jittered within 0.3 of a step. Four marks by four rows make the tile, so it repeats the grid exactly.
BAMBOO_STEP_FT = 7.0
BAMBOO_ROW = 0.86
BAMBOO_TILE_MARKS = 4


def bamboo_tile(bs: float) -> str:
    """A bamboo stand's tile: `bamboo_mark` (two culms and a leafy fork, 5-8 ft tall) on the stand's own jittered grid."""
    import numpy as np

    from ..homestead_parts.groves import bamboo_mark

    step = BAMBOO_STEP_FT * bs
    w, h = BAMBOO_TILE_MARKS * step, BAMBOO_TILE_MARKS * step * BAMBOO_ROW
    rng = np.random.default_rng(_SEED["bamboo"])
    marks = []
    for row in range(BAMBOO_TILE_MARKS):
        for col in range(BAMBOO_TILE_MARKS):
            x = step * (col + (0.5 if row % 2 == 0 else 1.0)) + (float(rng.random()) - 0.5) * step * 0.6
            y = step * BAMBOO_ROW * (row + 0.5) + (float(rng.random()) - 0.5) * step * 0.6
            tall, lean = float(rng.random()), float(rng.random())
            marks.append(_wrapped(w, h, lambda px, py, tall=tall, lean=lean: bamboo_mark(px, py, bs, tall, lean), x % w, y, 11.0 * bs))
    return f'<pattern id="{pattern_id("bamboo", bs)}" width="{w:g}" height="{h:g}" patternUnits="userSpaceOnUse">{"".join(marks)}</pattern>'


TILES: dict[str, Callable[[float], str]] = {"grass": grass_tile, "reed": reed_tile, "bamboo": bamboo_tile}


def cover_defs(kinds: set[tuple[str, float]]) -> str:
    """The `<defs>` of every tile a map uses, `(kind, bscale)` each - empty when it uses none."""
    if not kinds:
        return ""
    return "<defs>" + "".join(TILES[k](bs) for k, bs in sorted(kinds)) + "</defs>"


def cover_rings(shape: Any, tolerance: float = 0.25) -> list[list[tuple[float, float]]]:
    """Every ring of `shape` (a polygon, a multipolygon or a collection) - each outline and each hole - simplified within
    `tolerance` (a quarter foot: a buffered keep-out's arcs carry eight points a quarter-circle the fill cannot show) and at the
    record's grain, 0.1. Drawn as one even-odd path, the holes are bare."""
    out: list[list[tuple[float, float]]] = []
    for g in getattr(shape, "geoms", [shape]):
        if g.geom_type == "Polygon":
            g = g.simplify(tolerance, preserve_topology=True)
            for r in (g.exterior, *g.interiors):
                pts = [(round(x, 1), round(y, 1)) for x, y in list(r.coords)[:-1]]
                if len(pts) >= 3:
                    out.append(pts)
        elif hasattr(g, "geoms"):
            out += cover_rings(g, tolerance)
    return out
