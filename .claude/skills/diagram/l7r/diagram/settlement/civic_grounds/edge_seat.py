"""A SEAT AT THE SETTLEMENT'S EDGE for a ground that must stand apart from the houses (feature 273).

Two grounds are placed this way: a hamlet's own burial ground (the scripted hamlet generator) and a village's
cremation ground (the roller's village tier). Each stands beyond the last house, clear of the houses and wells by its
own distance, set back from water by the record's drawn bands, as near the houses as those allow and, among equally
near seats, nearest the fall line - below the houses where it can. The machinery is shared so the two cannot drift
(the tiers' rule: MOVE, never copy). Research: research/religion-and-death.html "Where do a hamlet's dead lie?",
"Does a village burn its own dead, and where is its cremation ground?", "How far from water does a burial ground lie?".

NEAREST FIRST, NOT FALL LINE FIRST. A scan that followed the fall line out to its reach before turning put a hamlet's
ground across its paddies from its houses, 700 ft off, where a side bearing had room 200 ft away (found by the
stage's own test, feature 273).

Everything a candidate is measured against is built ONCE, before the first candidate (constitution X clause 15): the
houses' and wells' footprints, the watercourses in a `PointGrid`, the paddy and marsh rings and the dry plots in
`PointGrid`s of ring indexes.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING

from .._geom import PointGrid, boxed_grid, boxed_ring_hit, boxed_rings, boxed_segs, seg_dist

if TYPE_CHECKING:
    from ..core import Settlement

Pt = tuple[float, float]
Rect = tuple[float, float, float, float]  # (cx, cy, w, h)

ANGLES = (0, 30, -30, 60, -60, 90, -90, 120, -120, 150, -150, 180)  # off the fall line, nearest first
STEP_FT = 10.0


def rect_gap(a: Rect, b: Rect) -> float:
    """The clear distance between two axis-aligned rects given as (cx, cy, w, h); 0 when they touch or overlap."""
    dx = max(0.0, abs(a[0] - b[0]) - (a[2] + b[2]) / 2)
    dy = max(0.0, abs(a[1] - b[1]) - (a[3] + b[3]) / 2)
    return math.hypot(dx, dy)


def rect_samples(cx: float, cy: float, w: float, h: float) -> list[Pt]:
    """The rect's corners, edge midpoints and center - where a set-back or a ring test is asked."""
    return [(cx + fx * w / 2, cy + fy * h / 2) for fx in (-1, 0, 1) for fy in (-1, 0, 1)]


class EdgeGround:
    """What a ground at the edge must stand clear of, measured in px.

    `clear_px` from every house and well footprint; `stream_px` beyond a stream's half-width; `ditch_px` beyond an
    irrigation course's; `field_px` from a paddy or marsh edge (0: the ring's inside only); `avoid` extra polylines
    with their own clearance (a shrine's approach)."""

    def __init__(self, s: Settlement, clear_px: float, stream_px: float, ditch_px: float, field_px: float, avoid: Sequence[tuple[Sequence[Pt], float]] = ()) -> None:
        self.clear_px, self.field_px = clear_px, field_px
        self.homes: list[Rect] = []
        for h in s.M.get("houses", []):
            b = (h.get("geom") or {}).get("bbox")
            self.homes.append((float(b[0]), float(b[1]), float(b[2]), float(b[3])) if b else (float(h["x"]), float(h["y"]), float(h["w"]), float(h["h"])))
        self.homes += [(float(w["x"]), float(w["y"]), 2 * float(w.get("r", 8)), 2 * float(w.get("r", 8))) for w in s.M.get("wells", [])]
        streams = [(st["poly"], float(st.get("w", 6)) / 2 + stream_px) for st in s.M.get("streams", []) if len(st.get("poly") or []) >= 2]
        # every drawn watercourse keeps the ditch margin; a stream's own entry above carries the larger set-back
        courses = [(pl, half + ditch_px) for pl, half in s._watercourse_segs(0.0)]
        self.water: PointGrid = boxed_grid(boxed_segs(streams + courses + [(pl, pad) for pl, pad in avoid]))
        rings = [f["outline"] for f in s.M.get("fields", []) if len(f.get("outline") or []) >= 3]
        rings += [m["poly"] for m in s.M.get("marshes", []) if len(m.get("poly") or []) >= 3]
        self.fields: PointGrid = boxed_grid(boxed_rings(rings, field_px))
        self.dry: PointGrid = boxed_grid(boxed_rings([d["poly"] for d in s.M.get("dry_plots", []) if len(d.get("poly") or []) >= 3], 3.0))

    def clear(self, s: Settlement, cx: float, cy: float, w: float, h: float) -> bool:
        """May a w x h ground stand at (cx, cy)? The engine's own fit, then the ground's distances."""
        if not (s._fits(cx, cy, w, h) and s._footprint_clear(cx, cy, w, h)):
            return False
        if any(rect_gap((cx, cy, w, h), home) < self.clear_px for home in self.homes):
            return False
        for px, py in rect_samples(cx, cy, w, h):
            if any(seg_dist(px, py, a, b) < half for a, b, half, *_ in self.water.near(px, py)):
                return False
            if boxed_ring_hit(px, py, self.fields.near(px, py), self.field_px) or boxed_ring_hit(px, py, self.dry.near(px, py), 3.0):
                return False
        return True


def edge_seat(s: Settlement, down_deg: float, w: float, h: float, ground: EdgeGround, reach_px: float, step_px: float) -> Pt | None:
    """The nearest seat out from the middle of the houses that `ground` clears, and among seats equally near the one
    nearest the fall line. None when nothing within `reach_px` clears."""
    houses = s.M.get("houses") or []
    if not houses:
        return None
    mx = sum(float(q["x"]) for q in houses) / len(houses)
    my = sum(float(q["y"]) for q in houses) / len(houses)
    bearings = [(math.cos(math.radians(down_deg + off)), math.sin(math.radians(down_deg + off))) for off in ANGLES]
    r = step_px
    while r <= reach_px:
        for dx, dy in bearings:
            cx, cy = mx + dx * r, my + dy * r
            if ground.clear(s, cx, cy, w, h):
                return (cx, cy)
        r += step_px
    return None

