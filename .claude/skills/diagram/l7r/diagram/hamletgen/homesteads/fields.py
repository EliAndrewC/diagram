"""THE HOMESTEAD FIELD (feature 261) - each household's own dry plot, laid against its homestead.

A household's dry ground lay first of all on the raised ground its house stood on: the settlement and its dry fields
share the natural levee, and the paddy takes the back marsh (research/fields.html, "Where dry (hatake) crops go"). The
comb's hem along the supply canal is the other attested form - patches beside the paddy and on the banks - and it stays;
this stage adds the first. Until it did, every dry plot on a hamlet lay out along the canal, and on a map whose houses
face the wind from across the rice that was all of them: Inashiro's median walk from a house to its dry plots was 658 ft
(settlement-review, feature 261).

Laid after the lanes, so a plot is fitted to the ways rather than the ways routed round a plot, and before the cover, the
woods and the belt, which all keep off `dry_polys`. A plot runs along one side of the homestead's reserved box, never the
windward side (the belt's ground), and is refused anywhere a homestead part would be - crop, water, a lane's tread and
verge, another steading, a well, a fixture, the marsh - or across the brook from its house.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from l7r.diagram.settlement import Settlement, knob_rng, point_in_poly, seg_dist, segments_cross
from l7r.diagram.waterfields.palette import DRY_CROPS

from ..consts import Pt
from ..plan import SitePlan

# THE PLOT'S SIZE IS A GUESS, labeled as one (specs/261 research R10): no readable page gives the area of a homestead
# field. It is as long as the side of the steading it lies against (so it reads as that household's), and one hem row
# deep - the comb's dry rows are ~36 ft deep (`waterfields/carve.py`), so the two forms draw at the same grain.
HOMESTEAD_FIELD_DEPTH_FT = (30.0, 44.0)
HOMESTEAD_FIELD_LEN_FT = (50.0, 120.0)  # the side's length, clamped to this
HOMESTEAD_FIELD_GAP_FT = 4.0  # between the steading's box and the plot: a bund's width
HOMESTEAD_FIELD_LANE_GAP_FT = 4.0  # past a lane's drawn tread
HOMESTEAD_FIELD_WINDWARD_DOT = 0.5  # a side facing the wind closer than 60 degrees is the belt's ground


def homestead_box(placed: Sequence[Any], x: float, y: float) -> tuple[float, float, float, float] | None:
    """The largest reserved box (`cx, cy, w, h`) holding the house center - the steading's whole footprint."""
    boxes = [(float(b[0]), float(b[1]), float(b[2]), float(b[3])) for b in placed if abs(x - b[0]) <= b[2] / 2 and abs(y - b[1]) <= b[3] / 2]
    return max(boxes, key=lambda b: b[2] * b[3]) if boxes else None


def side_plots(box: tuple[float, float, float, float], depth: float, wind: Pt) -> list[tuple[Pt, list[Pt]]]:
    """The four candidate plots against `box`'s sides as (outward normal, corner ring), the lee side first and the
    windward side (normal within `HOMESTEAD_FIELD_WINDWARD_DOT` of the wind) left out."""
    cx, cy, w, h = box
    g = HOMESTEAD_FIELD_GAP_FT
    out: list[tuple[Pt, list[Pt]]] = []
    for nx, ny in ((0.0, -1.0), (0.0, 1.0), (-1.0, 0.0), (1.0, 0.0)):
        if nx * wind[0] + ny * wind[1] > HOMESTEAD_FIELD_WINDWARD_DOT:
            continue
        side = w if nx == 0.0 else h
        length = min(HOMESTEAD_FIELD_LEN_FT[1], max(HOMESTEAD_FIELD_LEN_FT[0], side))
        near = (h / 2 if nx == 0.0 else w / 2) + g
        mx, my = cx + nx * (near + depth / 2), cy + ny * (near + depth / 2)
        hx, hy = (length / 2, depth / 2) if nx == 0.0 else (depth / 2, length / 2)
        out.append(((nx, ny), [(mx - hx, my - hy), (mx + hx, my - hy), (mx + hx, my + hy), (mx - hx, my + hy)]))
    out.sort(key=lambda t: t[0][0] * wind[0] + t[0][1] * wind[1])
    return out


def ring_clear_of_lines(ring: Sequence[Pt], lines: Sequence[tuple[Sequence[Pt], float]]) -> bool:
    """Whether no polyline (`pts`, clearance) comes within its clearance of the ring - a point of the line inside the ring,
    or a ring edge nearer a line segment than the clearance."""
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    for pts, clr in lines:
        for a, b in zip(pts, pts[1:], strict=False):
            if max(a[0], b[0]) < x0 - clr or min(a[0], b[0]) > x1 + clr or max(a[1], b[1]) < y0 - clr or min(a[1], b[1]) > y1 + clr:
                continue
            if point_in_poly(a[0], a[1], list(ring)) or point_in_poly(b[0], b[1], list(ring)):
                return False
            for p, q in zip(ring, list(ring[1:]) + [ring[0]], strict=False):
                if segments_cross(p, q, a, b) or min(seg_dist(p[0], p[1], a, b), seg_dist(q[0], q[1], a, b), seg_dist(a[0], a[1], p, q), seg_dist(b[0], b[1], p, q)) < clr:
                    return False
    return True


def ring_clear_of_items(ring: Sequence[Pt], items: Sequence[tuple[float, float, float]]) -> bool:
    """Whether no item (`x, y, radius`) stands within its radius of the ring's box."""
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    return all(math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1)) >= r for x, y, r in items)


def stage_homestead_fields(s: Settlement, plan: SitePlan) -> None:
    """The homestead fields.

    One dry plot against each homestead that has room for one, on its lee or flank side, fitted to the lanes already
    drawn (module docstring); the count is recorded.

    Steps:
        l7r.diagram.hamletgen.homesteads.fields.homestead_field_fits
        l7r.diagram.hamletgen.homesteads.fields.draw_homestead_field
    """
    rng = knob_rng(plan.spec.seed, "homestead_fields")
    lanes = [([(float(p[0]), float(p[1])) for p in ln["pts"]], float(ln.get("w") or 6) / 2 + HOMESTEAD_FIELD_LANE_GAP_FT) for ln in s.M.get("lanes") or [] if len(ln.get("pts") or []) >= 2]
    streams = [[(float(p[0]), float(p[1])) for p in st["poly"]] for st in s.M.get("streams") or [] if len(st.get("poly") or []) >= 2]
    items = [(float(w["x"]), float(w["y"]), 12.0) for w in s.M.get("wells") or [] if "x" in w]
    for key in ("farm_fixtures", "byres", "farm_sheds", "persimmons"):
        items += [(float(r["x"]), float(r["y"]), max(float(r.get("w") or 6.0), float(r.get("h") or 6.0)) / 2 + 3.0) for r in s.M.get(key) or [] if "x" in r]
    wet = [list(p) for p in s.hard_polys] + [[(float(a), float(b)) for a, b in m["poly"]] for m in s.M.get("marshes") or [] if m.get("poly")]
    laid = 0
    for house in s.M.get("houses") or []:
        box = homestead_box(s.placed, float(house["x"]), float(house["y"]))
        if box is None:
            continue
        depth = rng.uniform(*HOMESTEAD_FIELD_DEPTH_FT)
        crop = rng.choice(sorted(DRY_CROPS))
        for normal, ring in side_plots(box, depth, plan.wind):
            if not homestead_field_fits(s, ring, (float(house["x"]), float(house["y"])), lanes, streams, items, wet):
                continue
            along = 0.0 if normal[0] == 0.0 else math.pi / 2
            theta = along + rng.uniform(-0.6, 0.6)
            draw_homestead_field(s, ring, crop, theta)
            laid += 1
            break
    s.M["meta"]["homestead_fields"] = laid


def homestead_field_fits(
    s: Settlement, ring: Sequence[Pt], house: Pt, lanes: Sequence[tuple[Sequence[Pt], float]], streams: Sequence[Sequence[Pt]], items: Sequence[tuple[float, float, float]], wet: Sequence[Sequence[Pt]]
) -> bool:
    """Whether a plot may stand at `ring`: on the ground a homestead may take, clear of the lanes, the wells and fixtures,
    the marsh, and on its house's bank of every stream."""
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    rect = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys))
    if s._envelope_blocked(rect) is not None:
        return False
    if not ring_clear_of_lines(ring, lanes) or not ring_clear_of_items(ring, items):
        return False
    if any(point_in_poly(p[0], p[1], list(w)) for w in wet if len(w) >= 3 for p in [*ring, (rect[0], rect[1])]):
        return False
    return not any(segments_cross(house, (rect[0], rect[1]), a, b) for st in streams for a, b in zip(st, st[1:], strict=False))


def draw_homestead_field(s: Settlement, ring: Sequence[Pt], crop: str, theta: float) -> None:
    """Draw and register one homestead field, as the comb draws a hem plot (`_comb_draw_hem`)."""
    fill, furrow = DRY_CROPS[crop]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in ring)
    s.add(f'<polygon points="{pts}" fill="{fill}" stroke="#A98C58" stroke-width="1.4" stroke-linejoin="round"/>', cls=crop)
    s._draw_furrows(list(ring), furrow, theta, cls=crop)
    s.M.setdefault("dry_plots", []).append({"poly": [[round(x, 1), round(y, 1)] for x, y in ring], "crop": crop, "theta": round(theta, 3), "homestead": True})
    s.block_polys.append(list(ring))
    s.dry_polys.append(list(ring))
    s.placed.append(
        (
            (min(p[0] for p in ring) + max(p[0] for p in ring)) / 2,
            (min(p[1] for p in ring) + max(p[1] for p in ring)) / 2,
            max(p[0] for p in ring) - min(p[0] for p in ring),
            max(p[1] for p in ring) - min(p[1] for p in ring),
        )
    )
