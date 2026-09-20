"""A sheet on a map matches the map (feature 257, spec FR-004; the GM, 2026-09-20: "we shold make the
diagram view match what is shown on the larger map ... we shouldn't put any trees or graveyard on the
shrine diagram if those are not in correspnding places on the village map").

The sheet declares the map (`onmap.py`); this module reads the map's RECORDED manifest, maps the sheet's
frame and every feature of a corresponding class into map coordinates through the subject's position and
the two scales, and reports disagreement in three directions:

  (b) a sheet feature of a class with no map feature of that class within the grain;
  (c) a map feature of a class inside the sheet's frame with no sheet feature of that class within the grain;
  (d) the subject's footprint against the map's, per side.

THE GRAIN IS MEASURED (research.md R1, `m:map-grain`): the village map places a set-apart feature on rings
whose steps are 12-16 px (median 15) and marches a torii avenue at 15 px, so a sheet cannot be held
tighter than 15 map px - stated in MAP px so a hamlet map (1 ft per px) and a city map (3 ft per px)
get the same rule. A class the map cannot record (a fence, a sanctuary, a garden bed, a privy, a tub) is
not in the table, and the map's silence about it is not evidence.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from .grids import FTPX
from .onmap import OnMap
from .parse import ParsedPlan, Rect

MAP_GRAIN_PX: float = 15.0  # m:map-grain (research.md R1)
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_VIEWBOX_RE = re.compile(r'viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*"')

# THE CORRESPONDENCE CLASSES (contracts/on-map.md): a sheet class, the manifest keys it corresponds to.
CLASSES: dict[str, tuple[str, ...]] = {
    "tree": ("tree_crowns", "village_groves", "forest_patches"),
    "burial_ground": ("cemeteries",),
    "water_point": ("wells",),  # a well or a purification basin: the map's shrine well IS the shrine's ablution water
    "arch": ("torii",),
    "water": ("streams", "channels", "pond", "crescent_ponds"),
    "lane": ("lanes",),
    "building": ("houses", "byres", "farm_sheds", "storehouses", "buildings"),
}
# How the sheet marks each class, by element id (trees are known by their drawing - `parse.TREE_FILL`).
SHEET_IDS: dict[str, str] = {"burial_ground": "burial_ground", "well": "water_point", "basin": "water_point", "arch": "arch", "water": "water", "lane": "lane", "building": "building"}
_ALL_KEYS = frozenset(k for keys in CLASSES.values() for k in keys)


@dataclass(frozen=True)
class MapFeature:
    """One recorded map feature in map px: a point (`r` = 0), a circle, a rect (`w`, `h`) or a line (`pts`)."""

    cls: str
    x: float
    y: float
    w: float = 0.0
    h: float = 0.0
    r: float = 0.0
    pts: tuple[tuple[float, float], ...] = ()

    def distance(self, px: float, py: float) -> float:
        """How far (px, py) is from the feature's edge - zero inside a rect or a circle, on a line."""
        if self.pts:
            return min(_seg_distance(px, py, a, b) for a, b in zip(self.pts, self.pts[1:], strict=False)) if len(self.pts) > 1 else math.hypot(px - self.pts[0][0], py - self.pts[0][1])
        if self.w or self.h:
            dx = max(self.x - self.w / 2 - px, 0.0, px - self.x - self.w / 2)
            dy = max(self.y - self.h / 2 - py, 0.0, py - self.y - self.h / 2)
            return math.hypot(dx, dy)
        return max(0.0, math.hypot(px - self.x, py - self.y) - self.r)

    def in_frame(self, frame: tuple[float, float, float, float]) -> bool:
        """Any part of the feature lies inside the frame (x0, y0, x1, y1)."""
        x0, y0, x1, y1 = frame
        if self.pts:
            return any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in self.pts) or any(_seg_crosses(a, b, frame) for a, b in zip(self.pts, self.pts[1:], strict=False))
        if self.w or self.h:
            return self.x + self.w / 2 >= x0 and self.x - self.w / 2 <= x1 and self.y + self.h / 2 >= y0 and self.y - self.h / 2 <= y1
        cx = min(max(self.x, x0), x1)
        cy = min(max(self.y, y0), y1)
        return math.hypot(cx - self.x, cy - self.y) <= self.r


def _seg_distance(px: float, py: float, a: tuple[float, float], b: tuple[float, float]) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _seg_crosses(a: tuple[float, float], b: tuple[float, float], frame: tuple[float, float, float, float]) -> bool:
    """A segment with both ends outside the frame still crosses it when it passes within the frame's box."""
    x0, y0, x1, y1 = frame
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # the closest point of the segment to the frame's center lies inside the frame iff the segment enters it
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return False
    t = max(0.0, min(1.0, ((cx - ax) * dx + (cy - ay) * dy) / (dx * dx + dy * dy)))
    qx, qy = ax + t * dx, ay + t * dy
    return x0 <= qx <= x1 and y0 <= qy <= y1


def _pairs(seq: Iterable[Any]) -> tuple[tuple[float, float], ...]:
    return tuple((float(p[0]), float(p[1])) for p in seq if isinstance(p, (list, tuple)) and len(p) >= 2)


def _features(key: str, cls: str, recs: Any) -> list[MapFeature]:
    """The manifest list `key` as features of class `cls` (the shapes of research.md R2)."""
    out: list[MapFeature] = []
    if not isinstance(recs, list):
        return out
    if key == "tree_crowns":  # a flat list of x, y, r triplets
        for i in range(0, len(recs) - 2, 3):
            out.append(MapFeature(cls, float(recs[i]), float(recs[i + 1]), r=float(recs[i + 2])))
    elif key == "village_groves":
        for g in recs:
            if isinstance(g, Mapping):
                out += [MapFeature(cls, cx, cy, r=float(g.get("r", 0.0))) for cx, cy in _pairs(g.get("clumps", ()))]
    elif key == "torii":
        out += [MapFeature(cls, x, y) for x, y in _pairs(recs)]
    elif key == "pond" and recs and not isinstance(recs[0], (list, tuple, Mapping)):  # one rect: x, y, w, h
        if len(recs) >= 4:
            x, y, w, h = (float(v) for v in recs[:4])
            out.append(MapFeature(cls, x + w / 2, y + h / 2, w, h))
    else:
        for rec in recs:
            if not isinstance(rec, Mapping):
                continue
            pts = _pairs(rec.get("poly") or rec.get("pts") or ())
            if pts:
                out.append(MapFeature(cls, pts[0][0], pts[0][1], pts=pts))
            elif "cx" in rec:
                out.append(MapFeature(cls, float(rec["cx"]), float(rec["cy"]), r=float(rec.get("r", 0.0))))
            elif "x" in rec and "y" in rec:
                out.append(MapFeature(cls, float(rec["x"]), float(rec["y"]), float(rec.get("w", 0.0)), float(rec.get("h", 0.0)), float(rec.get("r", 0.0))))
    return out


@lru_cache(maxsize=8)
def load_map(path: str) -> dict[str, Any]:
    """The map's recorded manifest, read once per path (the sweep asks for the same map per sheet)."""
    with open(path, encoding="utf-8") as fh:
        loaded: dict[str, Any] = json.load(fh)
    return loaded


def manifest_path(on_map: OnMap) -> str:
    return on_map.manifest if os.path.isabs(on_map.manifest) else os.path.join(SKILL_ROOT, on_map.manifest)


@dataclass(frozen=True)
class Transform:
    """Sheet px to map px: sheet px / FTPX = ft; ft / the map's ftpx = map px; origin at the subject's center."""

    ftpx: float
    sheet_ox: float
    sheet_oy: float
    map_ox: float
    map_oy: float

    def to_map(self, sx: float, sy: float) -> tuple[float, float]:
        k = 1.0 / (FTPX * self.ftpx)
        return self.map_ox + (sx - self.sheet_ox) * k, self.map_oy + (sy - self.sheet_oy) * k

    def frame(self, text: str) -> tuple[float, float, float, float] | None:
        m = _VIEWBOX_RE.search(text)
        if not m:
            return None
        x, y, w, h = (float(m.group(i)) for i in range(1, 5))
        x0, y0 = self.to_map(x, y)
        x1, y1 = self.to_map(x + w, y + h)
        return x0, y0, x1, y1


def _center(r: Rect) -> tuple[float, float]:
    return r.x + r.w / 2, r.y + r.h / 2


def sheet_features(plan: ParsedPlan) -> list[tuple[str, Rect]]:
    """Every sheet feature of a corresponding class: trees by their drawing, the rest by their declared id."""
    out: list[tuple[str, Rect]] = [("tree", t) for t in plan.trees]
    for ident, cls in SHEET_IDS.items():
        out += [(cls, r) for r in plan.by_id(ident)]
    return out


def inventory(on_map: OnMap, frame: tuple[float, float, float, float]) -> dict[str, list[MapFeature]]:
    """The map's features of every class that lie inside the frame (map px)."""
    m = load_map(manifest_path(on_map))
    out: dict[str, list[MapFeature]] = {}
    for cls, keys in CLASSES.items():
        out[cls] = [f for key in keys for f in _features(key, cls, m.get(key)) if f.in_frame(frame)]
    return out


def matches_map(plan: ParsedPlan, text: str, on_map: OnMap | None, grain: float = MAP_GRAIN_PX) -> list[str]:
    """Spec FR-004's three directions and FR-005's refusals; an empty list on a sheet with no declaration
    (the report says "on no map" for it - `skipped`)."""
    if on_map is None:
        return []
    path = manifest_path(on_map)
    if not os.path.isfile(path):
        return [f"the declared manifest {on_map.manifest} cannot be read (no file at {path})"]
    m = load_map(path)
    ftpx = float(m.get("meta", {}).get("ftpx", 0) or 0)
    if ftpx <= 0:
        return [f"the manifest {on_map.manifest} records no scale (meta.ftpx)"]
    subject_map = [f for f in _features(on_map.key, "subject", m.get(on_map.key)) if math.hypot(f.x - on_map.x, f.y - on_map.y) <= grain]
    if not subject_map:
        return [f"no `{on_map.key}` feature within {grain:.0f} map px of ({on_map.x:.0f}, {on_map.y:.0f}) in {on_map.manifest}"]
    subject = plan.by_id(on_map.sheet_id)
    if not subject:
        return [f'no element marked id="{on_map.sheet_id}" on the sheet - the declaration names it as the subject']
    out: list[str] = []
    for ident in sorted(plan.ids & _ALL_KEYS):
        out.append(f'the sheet marks id="{ident}", a manifest key, not a class the check knows - the classes are {", ".join(SHEET_IDS)}')
    sx, sy = _center(subject[0])
    tf = Transform(ftpx, sx, sy, subject_map[0].x, subject_map[0].y)
    frame = tf.frame(text)
    if frame is None:
        return out + ["the sheet has no viewBox, so its frame cannot be laid on the map"]
    inv = inventory(on_map, frame)
    all_of: dict[str, list[MapFeature]] = {cls: [f for key in keys for f in _features(key, cls, m.get(key))] for cls, keys in CLASSES.items()}
    sheet = sheet_features(plan)
    # (b) every sheet feature has its map counterpart within the grain
    for cls, r in sheet:
        cx, cy = _center(r)
        mx, my = tf.to_map(cx, cy)
        near = min((f.distance(mx, my) for f in all_of[cls]), default=math.inf)
        if near > grain:
            out.append(f"{cls.replace('_', ' ')} at svg({cx:.0f},{cy:.0f}) has no {cls.replace('_', ' ')} on the map within {grain:.0f} map px (map ({mx:.0f},{my:.0f}))")
    # (c) every map feature inside the frame has its sheet counterpart within the grain
    for cls, feats in inv.items():
        mine = [tf.to_map(*_center(r)) for c, r in sheet if c == cls]
        for f in feats:
            if not any(f.distance(mx, my) <= grain for mx, my in mine):
                sxy = tf.to_map(0, 0)  # only for the message: the feature's place in sheet px
                px = tf.sheet_ox + (f.x - tf.map_ox) * FTPX * ftpx
                py = tf.sheet_oy + (f.y - tf.map_oy) * FTPX * ftpx
                del sxy
                out.append(f"the map's {cls.replace('_', ' ')} at map ({f.x:.0f},{f.y:.0f}) = svg({px:.0f},{py:.0f}) is inside the frame and not on the sheet")
    # (d) the subject's footprint, per side
    sw, sh = subject[0].w / FTPX, subject[0].h / FTPX
    mw, mh = subject_map[0].w * ftpx, subject_map[0].h * ftpx
    if abs(sw - mw) > grain * ftpx or abs(sh - mh) > grain * ftpx:
        out.append(f"the subject is {sw:.0f} x {sh:.0f} ft on the sheet; the map draws it {mw:.0f} x {mh:.0f} ft")
    return out


def skipped(on_map: OnMap | None) -> str | None:
    """Why the check did not run: the report's line for a sheet on no map."""
    return None if on_map is not None else "on no map (no `**On map**:` line in the notes)"
