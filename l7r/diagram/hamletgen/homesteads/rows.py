"""THE ROW VILLAGE'S HOLDINGS DRAWN (feature 291 amendment 3; research/questions/0033-row-villages-resson.html): each far-row
farm's holding behind its lot, as dry-field plots cut across its depth. The rows themselves - the streets, the frames along them,
the holdings reserved and the farms seated - are the Rust's since feature 444 T30 (`rust/phases/src/homesteads/rows.rs`,
`row_seat.rs`); `rust_seating.rust_rows` records what they return, and this module draws the holdings it recorded.

Research: row geometry - NONE: the holding's plots cut and drawn; the units that decide carry their own claims
"""

from __future__ import annotations

import math
from typing import Any

from l7r.diagram.settlement import Settlement

from ..consts import Pt

HOLDING_CELL_FT = 150.0
"""The holding's plots, cut across its depth at the near ring's cell (`near_ring_dry`'s 150 ft) - a map drawing convention.

Research: holding plot depth - research/questions/0033-row-villages-resson.drawing.html: 150 ft
"""


def holding_quad(center: Pt, t: Pt, n: Pt, along: float, depth: float) -> list[Pt]:
    """A holding's rectangle, `along` wide on the tangent `t` and `depth` deep on the normal `n`, about `center`."""
    ax, ay = t[0] * along / 2, t[1] * along / 2
    nx, ny = n[0] * depth / 2, n[1] * depth / 2
    cx, cy = center
    return [(cx - ax - nx, cy - ay - ny), (cx + ax - nx, cy + ay - ny), (cx + ax + nx, cy + ay + ny), (cx - ax + nx, cy - ay + ny)]


def largest_ring(geom: Any) -> list[Pt]:
    """The exterior of a polygon - or of a multi-polygon's largest part - as a point list without the closing repeat."""
    part = geom if geom.geom_type == "Polygon" else max(geom.geoms, key=lambda g: g.area)
    return [(float(x), float(y)) for x, y in list(part.exterior.coords)[:-1]]


def draw_holdings(s: Settlement) -> int:
    """Draw each reserved holding (`s._row_holdings`) as dry-field plots cut across its depth at `HOLDING_CELL_FT`, furrowed,
    recorded in `dry_plots` and registered in `dry_polys` (feature 291 plan D16). A cell on water or a lane is left undrawn;
    the rest of the holding stands. Returns the plots drawn.

    Research:
        holding drawn as dry field - research/questions/0033-row-villages-resson.drawing.html: every cell a dry crop, none paddy
        furrows down the strip - CONVENTION: across the street, the crops cycled from the dry palette
        holding plot depth - research/questions/0033-row-villages-resson.drawing.html: each holding cut across its depth into `HOLDING_CELL_FT` (150 ft) plots, as many as round(depth / 150 ft), at least one
        crop cells kept back from lanes and streams - GUESS: a holding cell within 2 px of a lane's drawn edge (half its width + 2.0) or within 6 px of a stream's outline is left unplanted, margins in pixels at the map's scale; no page says how near a lane or stream a dry-field strip was planted (searched 0033, 0081, 0014)
        cell on a lane or stream left undrawn - GUESS: a holding cell a lane or stream crosses or touches is left unplanted and the rest of the holding stands, so no lane runs through row crops (research/questions/0081-village-lanes.drawing.html: a lane never crosses row crops); no page says how a lane or stream crossing a farm's dry-field strip was laid out (searched 0033, 0081, 0014)
        its salts, guards and sentinels - NONE: they decide nothing about the place - 100000 (sentinel band length, clipped)
    """
    from shapely.geometry import LineString, Polygon

    from l7r.diagram.waterfields import DRY_CROPS

    pal = list(DRY_CROPS.items())
    lanes = [LineString(ln["pts"]).buffer(float(ln.get("w", 3)) / 2 + 2.0) for ln in s.M.get("lanes", []) if len(ln.get("pts") or []) >= 2]
    water = [LineString(st["poly"]).buffer(6.0) for st in s.M.get("streams", []) if len(st.get("poly") or []) >= 2]
    n = 0
    for k, (quad, t, nrm, depth) in enumerate(getattr(s, "_row_holdings", None) or []):
        cells = max(1, round(depth / s.px(HOLDING_CELL_FT)))
        poly = Polygon(quad)
        crop, (fill, fur) = pal[k % len(pal)]
        mx = sum(p[0] for p in quad) / len(quad)
        my = sum(p[1] for p in quad) / len(quad)
        for c in range(cells):
            lo, hi = -depth / 2 + depth * c / cells, -depth / 2 + depth * (c + 1) / cells
            band = Polygon(holding_quad((mx + nrm[0] * (lo + hi) / 2, my + nrm[1] * (lo + hi) / 2), t, nrm, 1e5, hi - lo)).intersection(poly)
            if band.is_empty or band.area < 1.0 or any(band.intersects(g) for g in lanes + water):
                continue
            cell = largest_ring(band)
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in cell)
            s.add(f'<polygon points="{pts}" fill="{fill}" stroke="#A98C58" stroke-width="1.4" stroke-linejoin="round"/>', cls="farm holding")
            theta = math.atan2(nrm[1], nrm[0]) % math.pi  # the furrows run down the strip, across the street
            s._draw_furrows(cell, fur, theta, cls="farm holding")
            # `holding`: a farm's own holding, not the field's hem - the reed toe is measured below the FIELD'S lowest crop
            # (`toe_band`), and read as field crop a holding moved the toe 220 ft onto three Kashikawa farms' doors
            s.M["dry_plots"].append({"poly": [[round(x, 1), round(y, 1)] for x, y in cell], "crop": crop, "theta": round(theta, 3), "holding": k})
            s.dry_polys.append(cell)
            n += 1
    return n
