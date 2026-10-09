"""THE COVER TILES (feature 298): a ground cover that stands for an AREA, not for objects, drawn as one repeating tile.

The scrub's grass, the marsh's reeds and a bamboo stand's culms were thrown glyph by glyph - 55-68% of four pool hamlets' SVGs, and
every throw tested against the keep-outs and culled at the finish one at a time (specs/298). The GM (2026-10-01): "drawing
individual blades of grass and lines for marshland and scrubland" serves no purpose that individual trees do, so "instead of then
drawing individual glyphs within that ... some tiled pattern where a relatively small block of background is then repeated".
Each tile here lays the scatter's own glyphs - their shapes, colors, strokes and density per area - ONCE, from a fixed seed, and
the zone is filled with it (`Settlement.flush_covers`). A MAP DRAWING CONVENTION, recorded as such (research/contents.json#vegetation, the
spec's Decisions Recorded); the GM does not mind the repetition.

SEAMLESS: a glyph whose extent crosses the tile's edge is laid again at the opposite edge, so the tiles meet without a cut. No
background: the land shows between the glyphs, as it did between the thrown ones.

Research: cover tiles - CONVENTION: an area cover drawn as one repeating tile of its scatter's glyphs, sizes and densities"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

#: The grass and reed tile's side in feet (x the map's `bscale`): wide enough that a zone shows few repeats, small enough that
#: the tile is a few hundred glyphs. The bamboo tile is the stand's own grid (`bamboo_tile`).
COVER_TILE_FT = 64.0
#: The reed tile's side (feature 299): its wide pale tint patches made a 64 ft lattice that read as a grid on Inashiro's toe at
#: full size (2026-10-01); twice the side holds four times the glyphs, once, in the <defs>, and costs a map nothing else.
REED_TILE_FT = 128.0

#: One throw per this many square feet (x bscale^2) - the scatters' own densities: `commons` threw `area / 74` (14% of the kept
#: throws brush dots, the rest three-bladed tufts), the marsh a tint per 360 and a tuft per 150 (12% of them glints).
GRASS_SQFT_PER_THROW = 74.0
GRASS_DOT_SHARE = 0.14
REED_SQFT_PER_TINT = 360.0
REED_SQFT_PER_TUFT = 150.0
REED_GLINT_SHARE = 0.12

#: A fixed seed per kind: the tile is the same on every map (the GM does not mind the repetition), so a re-roll moves nothing.
_SEED = {"grass": 2981, "reed": 2982, "bamboo": 2983, "grass-clumps": 2991, "reed-clumps": 2992, "fringe": 2993, "reed-bank": 2994}
"""Research: tile seeds - NONE: fixed seeds"""


@dataclass
class Cover:
    """One zone a tile fills (`Settlement._covers`, drawn by `flush_covers`): its `kind` (a key of `TILES`), the class its shape
    is ruled under on the page (`cls`, the zone's), its `ring`, and the ground its scatter kept bare as shapely geometries
    (`bare` - a clearing swept later is added here, `_cull_cover_in`). `rec` is the zone's manifest record, which is given the
    drawn shape (`cover`) for the page's hit region.

    Research: cover record - NONE: a zone and its bare ground"""

    kind: str
    cls: str | None
    ring: list[tuple[float, float]]
    bare: list[Any] = field(default_factory=list)
    rec: dict[str, Any] | None = None


def pattern_id(kind: str, bs: float) -> str:
    """The `<pattern>` id of `kind` at scale `bs` - one per kind and scale on a map.

    Research: plumbing - NONE: pattern and path assembly"""
    return f"cover-{kind}-{bs:g}".replace(".", "_")


def _wrapped(side_w: float, side_h: float, glyph: Callable[[float, float], str], x: float, y: float, reach: float) -> str:
    """`glyph` drawn at (x, y) and again at each opposite edge its `reach` crosses, so the tile is seamless.

    Research: plumbing - NONE: pattern and path assembly"""
    out = []
    for dx in (-side_w, 0.0, side_w):
        for dy in (-side_h, 0.0, side_h):
            px, py = x + dx, y + dy
            if px + reach >= 0 and px - reach <= side_w and py + reach >= 0 and py - reach <= side_h:
                out.append(glyph(px, py))
    return "".join(out)


def grass_tile(bs: float, brush: bool = True, keep: float = 1.0, name: str | None = None) -> str:
    """The scrub's tile: brush dots and three-bladed tufts of grass at the commons' density (`commons`, `grass_scatter` as it
    was): a dot `#94A063` r 1.5-2.4, a tuft three `#A7A860` blades 2.4-4.2 long within 0.45 rad of upright. `brush=False` is
    the grass under a wood's edge: the same tufts, no brush dot (0077: no brush in a wood; feature 328 wave 57); `keep` the share
    of the tufts kept (the inner half of that band, where the grass thins), `name` the pattern's kind."""
    import numpy as np

    side = COVER_TILE_FT * bs
    n = round(side * side / (GRASS_SQFT_PER_THROW * bs * bs))
    rng = np.random.default_rng(_SEED["grass"])
    xs, ys, kind = rng.uniform(0, side, n), rng.uniform(0, side, n), rng.random(n)
    r_dot = rng.uniform(1.5, 2.4, n) * bs
    ang, blen = rng.uniform(-0.45, 0.45, (n, 3)), rng.uniform(2.4, 4.2, (n, 3)) * bs
    kept = rng.random(n) < keep  # drawn after the tufts' own draws, so the full tile is unchanged
    dots, blades = [], []
    for i in range(n):
        x, y = float(xs[i]), float(ys[i])
        if not kept[i]:
            continue
        if kind[i] < GRASS_DOT_SHARE:
            if not brush:
                continue
            r = float(r_dot[i])
            dots.append(_wrapped(side, side, lambda px, py, r=r: f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}"/>', x, y, r))
            continue
        tips = [(math.sin(float(ang[i, k])) * float(blen[i, k]), -math.cos(float(ang[i, k])) * float(blen[i, k])) for k in range(3)]
        blades.append(_wrapped(side, side, lambda px, py, tips=tips: "".join(f"M{px:.1f},{py:.1f}l{tx:.1f},{ty:.1f}" for tx, ty in tips), x, y, 4.2 * bs))
    return (
        f'<pattern id="{pattern_id(name or ("grass" if brush else "wood-fringe"), bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<g fill="#94A063" fill-opacity="0.85">{"".join(dots)}</g>'
        f'<path d="{"".join(blades)}" stroke="#A7A860" stroke-width="0.8" fill="none"/></pattern>'
    )


def wood_fringe_tile(bs: float) -> str:
    """The grass a few paces in under a wood's edge (`land.cover.WOOD_FRINGE_FT`): the scrub's tufts without its brush.

    Research: grass under a wood's edge - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: grass only, no brush in a wood"""
    return grass_tile(bs, brush=False)


WOOD_FRINGE_THIN_KEEP = 0.5
"""Research: grass thinning under a wood - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: thinning out over the first few paces; the half density of the inner half a CONVENTION"""


def wood_fringe_thin_tile(bs: float) -> str:
    """The inner half of the band under a wood's edge: the grass-only tile at `WOOD_FRINGE_THIN_KEEP` of its tufts, where the
    grass thins out under the crowns (0077, feature 328 wave 57's impl-drift: a uniform band stopped on a hard line).

    Research: grass thinning under a wood - research/questions/0077-village-fuel-woods-and-their-coppice-satoyama.drawing.html: the grass thins over the first few paces"""
    return grass_tile(bs, brush=False, keep=WOOD_FRINGE_THIN_KEEP, name="wood-fringe-thin")


def reed_tile(bs: float) -> str:
    """The marsh's tile: the pale wet tint (`#9FBBAE` at 0.14, r 15-28), the standing-water glints (`#C2D6CE` ellipses) and the
    reed tufts - four near-vertical `#6E9377` blades 4-7 long within 0.2 rad of upright - at the marsh's densities (`marsh`).

    Research: reed tile - CONVENTION: tint, glints and reed tufts at the marsh's densities"""
    import numpy as np

    from .wet import MARSH_TINT_R

    side = REED_TILE_FT * bs
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
        # THE WET HAZE IS EVEN, ITS PATCHES FAINT (feature 299): the scatter's tint circles at 0.14 overlapped at random over
        # a whole marsh, and repeated in a tile their gaps made a sawtooth of bare ground at fit zoom (Inashiro, 2026-10-01)
        f'<rect width="{side:g}" height="{side:g}" fill="#9FBBAE" fill-opacity="0.12"/>'
        f'<g fill="#9FBBAE" fill-opacity="0.06">{"".join(tints)}</g>'
        f'<g fill="#C2D6CE" fill-opacity="0.85">{"".join(glints)}</g>'
        f'<path d="{"".join(reeds)}" stroke="#6E9377" stroke-width="0.8" fill="none"/></pattern>'
    )


#: The bamboo stand's grid (`bamboo_stand` as it was): a mark per 7 ft, rows 0.86 of that apart and every other row offset
#: half a step, each mark jittered within 0.3 of a step. Four marks by four rows make the tile, so it repeats the grid exactly.
BAMBOO_STEP_FT = 7.0
BAMBOO_ROW = 0.86
BAMBOO_TILE_MARKS = 4
#: The stand's ground shade under its marks: its culm green at this opacity (a map drawing convention).
BAMBOO_SHADE = 0.18


def bamboo_tile(bs: float) -> str:
    """A bamboo stand's tile: `bamboo_mark` (two culms and a leafy fork, 5-8 ft tall) on the stand's own jittered grid.

    Research: bamboo mark - research/questions/0075-bamboo-groves-chikurin.drawing.html: the modern map's bamboo symbol on a 7 ft grid over the thicket's shade"""
    import numpy as np

    from ..homestead_parts.groves import BAMBOO_CULM, bamboo_mark

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
    # ...ON THE THICKET'S OWN SHADE (`BAMBOO_SHADE`): a stand shades out almost everything under it (research/vegetation/150), and
    # marks alone over the scrub's ground read as a tuft of grass (the glyph check of Sawada's homestead bamboo, feature 302)
    shade = f'<rect width="{w:g}" height="{h:g}" fill="{BAMBOO_CULM}" fill-opacity="{BAMBOO_SHADE}"/>'
    return f'<pattern id="{pattern_id("bamboo", bs)}" width="{w:g}" height="{h:g}" patternUnits="userSpaceOnUse">{shade}{"".join(marks)}</pattern>'


#: THE OVERLAY'S REPEAT (feature 299, the GM 2026-10-01 of the marsh: "Could you do the same thing" - the scrub's varied look):
#: a second, sparse tile drawn over the base tile at a repeat that shares no small common multiple with the base's 64 ft, so the
#: two together do not visibly repeat at either's period.
OVERLAY_TILE_FT = 97.0
#: ...and the reed overlay's, larger than the reed base tile's own 128 ft (`REED_TILE_FT`) and sharing no small multiple with
#: it; it carries the clumps per area the 97 ft tile does.
REED_OVERLAY_TILE_FT = 197.0
#: Clumps per overlay tile, and the tufts in each, kept within `CLUMP_RADIUS_FT` of its center.
OVERLAY_CLUMPS = 3
CLUMP_TUFTS = (6, 10)
CLUMP_RADIUS_FT = 6.0


def _tufts(side: float, xs: Any, ys: Any, ang: Any, length: Any) -> str:
    """Tufts of blades rooted at (xs[i], ys[i]), blade k at angle ang[i, k] off upright and length[i, k] long, as one path's `d`,
    each tuft laid again past any edge it crosses (`_wrapped`).

    Research: plumbing - NONE: pattern and path assembly"""
    out = []
    for i in range(len(xs)):
        tips = [(math.sin(float(ang[i, k])) * float(length[i, k]), -math.cos(float(ang[i, k])) * float(length[i, k])) for k in range(ang.shape[1])]
        reach = max(float(v) for v in length[i])
        out.append(_wrapped(side, side, lambda px, py, tips=tips: "".join(f"M{px:.1f},{py:.1f}l{tx:.1f},{ty:.1f}" for tx, ty in tips), float(xs[i]), float(ys[i]), reach))
    return "".join(out)


def _clump_centers(rng: Any, side: float, n: int, spread: float) -> tuple[Any, Any]:
    """`n` clumps' tuft roots: clump centers anywhere on the tile, each with 8-14 roots within `spread` of it.

    Research: plumbing - NONE: pattern and path assembly"""
    import numpy as np

    xs, ys = [], []
    for cx, cy in zip(rng.uniform(0, side, n), rng.uniform(0, side, n), strict=True):
        m = int(rng.integers(CLUMP_TUFTS[0], CLUMP_TUFTS[1] + 1))
        r, a = spread * np.sqrt(rng.random(m)), rng.uniform(0.0, 2.0 * math.pi, m)
        xs += (cx + r * np.cos(a)).tolist()
        ys += (cy + r * np.sin(a)).tolist()
    return np.array(xs) % side, np.array(ys) % side


def reed_overlay_tile(bs: float) -> str:
    """The marsh's overlay (feature 299): a few dense reed clumps and small open-water patches, sparse, at `REED_OVERLAY_TILE_FT`."""
    import numpy as np

    side = REED_OVERLAY_TILE_FT * bs
    rng = np.random.default_rng(_SEED["reed-clumps"])
    xs, ys = _clump_centers(rng, side, round(OVERLAY_CLUMPS * (REED_OVERLAY_TILE_FT / OVERLAY_TILE_FT) ** 2), CLUMP_RADIUS_FT * bs)
    n = len(xs)
    reeds = _tufts(side, xs, ys, rng.uniform(-0.2, 0.2, (n, 4)), rng.uniform(5.0, 8.0, (n, 4)) * bs)
    pools = []
    for x, y, a, b in zip(rng.uniform(0, side, 8), rng.uniform(0, side, 8), rng.uniform(6.0, 10.0, 8) * bs, rng.uniform(3.0, 4.5, 8) * bs, strict=True):
        pools.append(_wrapped(side, side, lambda px, py, a=float(a), b=float(b): f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{a:.1f}" ry="{b:.1f}"/>', float(x), float(y), float(a)))
    return (
        f'<pattern id="{pattern_id("reed-clumps", bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<g fill="#C2D6CE" fill-opacity="0.7">{"".join(pools)}</g>'
        f'<path d="{reeds}" stroke="#6E9377" stroke-width="0.8" fill="none"/></pattern>'
    )


def grass_overlay_tile(bs: float) -> str:
    """The scrub's overlay (feature 299): a few dense clumps of grass with a brush dot or two, sparse, at `OVERLAY_TILE_FT`."""
    import numpy as np

    side = OVERLAY_TILE_FT * bs
    rng = np.random.default_rng(_SEED["grass-clumps"])
    xs, ys = _clump_centers(rng, side, OVERLAY_CLUMPS, CLUMP_RADIUS_FT * bs)
    n = len(xs)
    blades = _tufts(side, xs, ys, rng.uniform(-0.45, 0.45, (n, 3)), rng.uniform(2.8, 4.6, (n, 3)) * bs)
    dots = []
    for x, y, r in zip(rng.uniform(0, side, 2), rng.uniform(0, side, 2), rng.uniform(1.8, 2.6, 2) * bs, strict=True):
        dots.append(_wrapped(side, side, lambda px, py, r=float(r): f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}"/>', float(x), float(y), float(r)))
    return (
        f'<pattern id="{pattern_id("grass-clumps", bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<g fill="#94A063" fill-opacity="0.85">{"".join(dots)}</g>'
        f'<path d="{blades}" stroke="#A7A860" stroke-width="0.8" fill="none"/></pattern>'
    )


#: THE FRINGE (feature 299, the GM 2026-10-01: "a more gradual transition ... between the two"): where scrub meets marsh, a band
#: `FRINGE_FT` wide straddling the boundary is drawn with a tile of both - grass tufts and reed tufts at about half their own
#: densities, with a little of the wet tint - so the change is a grading, as the margin itself grades (research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.html:
#: reed, then sedge and grass, then dry ground). A MAP DRAWING CONVENTION; the width is calibrated by eye.
FRINGE_FT = 30.0
"""Research: scrub-marsh fringe - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: a 30 ft mixed band of grass and reed straddling the edge"""


def fringe_tile(bs: float) -> str:
    """The scrub-marsh fringe's tile: grass and reed tufts at half density each, a few pale tint patches, at the base repeat.

    Research: fringe tile - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: grass and reed tufts at half density each"""
    import numpy as np

    side = COVER_TILE_FT * bs
    rng = np.random.default_rng(_SEED["fringe"])
    ng, nr, nt = round(side * side / (2 * GRASS_SQFT_PER_THROW * bs * bs)), round(side * side / (2 * REED_SQFT_PER_TUFT * bs * bs)), 4
    grass = _tufts(side, rng.uniform(0, side, ng), rng.uniform(0, side, ng), rng.uniform(-0.45, 0.45, (ng, 3)), rng.uniform(2.4, 4.2, (ng, 3)) * bs)
    reeds = _tufts(side, rng.uniform(0, side, nr), rng.uniform(0, side, nr), rng.uniform(-0.2, 0.2, (nr, 4)), rng.uniform(4.0, 7.0, (nr, 4)) * bs)
    tints = []
    for x, y, r in zip(rng.uniform(0, side, nt), rng.uniform(0, side, nt), rng.uniform(10.0, 18.0, nt) * bs, strict=True):
        tints.append(_wrapped(side, side, lambda px, py, r=float(r): f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}"/>', float(x), float(y), float(r)))
    return (
        f'<pattern id="{pattern_id("fringe", bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<g fill="#9FBBAE" fill-opacity="0.08">{"".join(tints)}</g>'
        f'<path d="{grass}" stroke="#A7A860" stroke-width="0.8" fill="none"/>'
        f'<path d="{reeds}" stroke="#6E9377" stroke-width="0.8" fill="none"/></pattern>'
    )


#: THE BANK BAND (feature 300, the GM 2026-10-01: the stream's banks through the marsh looked "cleared of marsh"): the reeds run
#: to the water's drawn edge, and a band `BANK_FT` wide along each bank inside the marsh is drawn with a tighter, darker reed
#: tile, so the stream stays framed where a bare strip framed it. A MAP DRAWING CONVENTION; the width is calibrated by eye.
BANK_FT = 6.0
"""Research: reed bank band - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: 6 ft of denser, darker reeds along each bank in the marsh"""


def reed_bank_tile(bs: float) -> str:
    """The bank band's tile: reed tufts at about three times the marsh's density, a shade darker, at the base repeat.

    Research: bank tile - research/questions/0074-reed-beds-and-the-marshs-edge-yoshihara.drawing.html: reeds at three times the marsh's density, a shade darker"""
    import numpy as np

    side = COVER_TILE_FT * bs
    rng = np.random.default_rng(_SEED["reed-bank"])
    n = round(3 * side * side / (REED_SQFT_PER_TUFT * bs * bs))
    reeds = _tufts(side, rng.uniform(0, side, n), rng.uniform(0, side, n), rng.uniform(-0.2, 0.2, (n, 4)), rng.uniform(4.5, 7.5, (n, 4)) * bs)
    return (
        f'<pattern id="{pattern_id("reed-bank", bs)}" width="{side:g}" height="{side:g}" patternUnits="userSpaceOnUse">'
        f'<rect width="{side:g}" height="{side:g}" fill="#9FBBAE" fill-opacity="0.16"/>'
        f'<path d="{reeds}" stroke="#56785F" stroke-width="0.9" fill="none"/></pattern>'
    )


#: The overlay drawn over each base kind (feature 299); bamboo has none.
OVERLAYS: dict[str, str] = {"grass": "grass-clumps", "reed": "reed-clumps"}
"""Research: overlay table - NONE: which overlay draws over which base"""

TILES: dict[str, Callable[[float], str]] = {
    "grass": grass_tile,
    "wood-fringe": wood_fringe_tile,
    "wood-fringe-thin": wood_fringe_thin_tile,
    "reed": reed_tile,
    "bamboo": bamboo_tile,
    "grass-clumps": grass_overlay_tile,
    "reed-clumps": reed_overlay_tile,
    "fringe": fringe_tile,
    "reed-bank": reed_bank_tile,
}


def cover_defs(kinds: set[tuple[str, float]]) -> str:
    """The `<defs>` of every tile a map uses, `(kind, bscale)` each - empty when it uses none.

    Research: plumbing - NONE: pattern and path assembly"""
    if not kinds:
        return ""
    return "<defs>" + "".join(TILES[k](bs) for k, bs in sorted(kinds)) + "</defs>"


def cover_rings(shape: Any, tolerance: float = 0.25) -> list[list[tuple[float, float]]]:
    """Every ring of `shape` (a polygon, a multipolygon or a collection) - each outline and each hole - simplified within
    `tolerance` (a quarter foot: a buffered keep-out's arcs carry eight points a quarter-circle the fill cannot show) and at the
    record's grain, 0.1. Drawn as one even-odd path, the holes are bare.

    Research: plumbing - NONE: pattern and path assembly"""
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


def cover_path(shape: Any, kind: str, bs: float) -> str:
    """One even-odd `<path>` of `shape`'s rings (`cover_rings`) filled with `kind`'s tile at scale `bs`, taking no pointer (the
    page's hit regions take it, `interactive.page.hit_regions`).

    Research: plumbing - NONE: pattern and path assembly"""
    d = "".join("M" + "L".join(f"{x},{y}" for x, y in r) + "Z" for r in cover_rings(shape))
    return f'<path d="{d}" fill="url(#{pattern_id(kind, bs)})" fill-rule="evenodd" style="pointer-events: none"/>'
