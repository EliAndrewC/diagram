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

from l7r.diagram.buildings.types import load_types

from .checks import _main_gate_passage, main_gate_passage_ft
from .grids import FTPX
from .onmap import OnMap
from .parse import ParsedPlan, Rect
from .tagged import marks

MAP_GRAIN_PX: float = 15.0  # m:map-grain (research.md R1): a POSITION is the same feature within this
SIZE_GRAIN_PX: float = 1.0  # a SIDE matches within the map's own resolution: the map records a footprint to the px and a sheet draws it exactly
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # pack_audit -> tools -> diagram -> l7r -> the skill
_VIEWBOX_RE = re.compile(r'viewBox="\s*([\-\d.]+)\s+([\-\d.]+)\s+([\d.]+)\s+([\d.]+)\s*"')

# THE CORRESPONDENCE CLASSES (contracts/on-map.md): a sheet class, the manifest keys it corresponds to.
CLASSES: dict[str, tuple[str, ...]] = {
    "tree": ("tree_crowns", "village_groves", "forest_patches"),
    "burial_ground": ("cemeteries",),
    "water_point": ("wells",),  # a well or a purification basin: the map's shrine well IS the shrine's ablution water
    "arch": ("torii",),
    "water": ("streams", "channels", "pond", "crescent_ponds"),
    # every key a map records a way under (feature 294 B24): `lanes` and `roads` are lists of ways, `lane`, `road` and a
    # city's `ring_road` ONE way as a flat point list - the town map records four, and reading `lanes` alone never checked a road
    "lane": ("lanes", "lane", "roads", "road", "ring_road"),
    "building": ("houses", "byres", "farm_sheds", "retirement_houses", "storehouses", "buildings"),
}
#: The keys whose value is one polyline, a flat list of points, rather than a list of records.
POLYLINE_KEYS: frozenset[str] = frozenset({"lane", "road", "ring_road"})
#: The kinds a sheet draws a way under that a map can record: a tagged road IS a lane-class feature, sampled along its
#: line. A `footpath` is not among them - no map in either pool records a footpath under any key (measured 2026-10-01:
#: the ways are the five keys above), so the map's silence about one is not evidence.
SHEET_WAY_KINDS: frozenset[str] = frozenset({"road"})
# How the sheet marks each class, by element id (trees are known by their drawing - `parse.TREE_FILL`).
SHEET_IDS: dict[str, str] = {"burial_ground": "burial_ground", "well": "water_point", "basin": "water_point", "arch": "arch", "water": "water", "lane": "lane", "building": "building"}
# a manifest key a sheet might mistake for a class id - less the ids that ARE the class marks (`lane` is both since B24)
_ALL_KEYS = frozenset(k for keys in CLASSES.values() for k in keys) - set(SHEET_IDS)


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
    elif key in POLYLINE_KEYS:  # ONE way as a flat list of points (the town's `road`, a village's `lane`)
        pts = _pairs(recs)
        if pts:
            out.append(MapFeature(cls, pts[0][0], pts[0][1], pts=pts))
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


def subject_box(plan: ParsedPlan, sheet_id: str) -> Rect | None:
    """The subject's footprint on the sheet: the UNION of every rect marked with its id (feature 294 B24) - a walled
    compound marks each court `precinct`, and its first rect alone was the inner court, half the compound."""
    rects = plan.by_id(sheet_id)
    if not rects:
        return None
    x0, y0 = min(r.x for r in rects), min(r.y for r in rects)
    return Rect(x0, y0, max(r.x2 for r in rects) - x0, max(r.y2 for r in rects) - y0, rects[0].fill, rects[0].pos, sheet_id)


def _inside(px: float, py: float, r: Rect) -> bool:
    return r.x <= px <= r.x2 and r.y <= py <= r.y2


def sheet_ways(text: str) -> list[tuple[tuple[float, float], ...]]:
    """Every way the sheet draws (a path or line tagged road or footpath), as its points in sheet px, each once."""
    out: list[tuple[tuple[float, float], ...]] = []
    for mk in marks(text):
        if mk.tag in ("path", "line") and mk.kind in SHEET_WAY_KINDS and len(mk.pts) >= 2 and mk.pts not in out:
            out.append(mk.pts)
    return out


def densify(pts: tuple[tuple[float, float], ...], step: float) -> list[tuple[float, float]]:
    """The polyline's points with more set between them, none farther apart than `step`."""
    out = [pts[0]]
    for (ax, ay), (bx, by) in zip(pts, pts[1:], strict=False):
        n = max(1, math.ceil(math.hypot(bx - ax, by - ay) / step))
        out += [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(1, n + 1)]
    return out


_SIDES: dict[str, str] = {"north": "N", "south": "S", "east": "E", "west": "W", "n": "N", "s": "S", "e": "E", "w": "W"}


def side_of(px: float, py: float, box: Rect) -> str:
    """The side (N, S, E, W) of `box` nearest the point."""
    return min((("N", abs(py - box.y)), ("S", abs(py - box.y2)), ("W", abs(px - box.x)), ("E", abs(px - box.x2))), key=lambda s: s[1])[0]


def subject_record(m: Mapping[str, Any], on_map: OnMap, grain: float) -> Mapping[str, Any] | None:
    """The subject's raw record in the manifest (the one whose center lies within the grain of the declaration)."""
    for rec in m.get(on_map.key) or []:
        if isinstance(rec, Mapping) and "x" in rec and "y" in rec and math.hypot(float(rec["x"]) - on_map.x, float(rec["y"]) - on_map.y) <= grain:
            return rec
    return None


def gate_agrees(plan: ParsedPlan, rec: Mapping[str, Any], tf: Transform, box: Rect, grain: float) -> list[str]:
    """(e) Where the subject's record carries its gate (`gate`, `gate_dir`, `gate_w` - a town's manor records all three),
    the sheet's main-gate passage stands at it within the grain, on the side it names, and as wide within the map's
    resolution (`SIZE_GRAIN_PX`). A record with none of the three asks nothing."""
    if not any(k in rec for k in ("gate", "gate_dir", "gate_w")):
        return []
    passage = _main_gate_passage(plan)
    if not passage:
        return ["the map records the subject's gate, and the sheet draws no `main gate` (tag its posts data-kind=\"main gate\")"]
    px, py = passage[0]
    out: list[str] = []
    gate = rec.get("gate")
    if isinstance(gate, (list, tuple)) and len(gate) >= 2:
        mx, my = tf.to_map(px, py)
        off = math.hypot(mx - float(gate[0]), my - float(gate[1]))
        if off > grain:
            out.append(f"the main gate at svg({px:.0f},{py:.0f}) = map ({mx:.0f},{my:.0f}) is {off:.0f} map px from the map's gate at ({float(gate[0]):.0f},{float(gate[1]):.0f})")
    want = _SIDES.get(str(rec.get("gate_dir", "")).lower())
    have = side_of(px, py, box)
    if want is not None and want != have:
        out.append(f"the main gate is on the sheet's {have} side; the map faces it {rec['gate_dir']}")
    ft = main_gate_passage_ft(plan)
    if "gate_w" in rec and ft is not None and abs(ft - float(rec["gate_w"]) * tf.ftpx) > SIZE_GRAIN_PX * tf.ftpx:
        out.append(f"the main gate's passage is {ft:.1f} ft on the sheet; the map records it {float(rec['gate_w']) * tf.ftpx:.1f} ft")
    return out


def matches_map(plan: ParsedPlan, text: str, on_map: OnMap | None, grain: float = MAP_GRAIN_PX) -> list[str]:
    """Spec FR-004's three directions and FR-005's refusals, and (feature 294 B24) the subject's gate; an empty list on a
    sheet with no declaration (the report says "on no map" for it - `skipped`).

    THE SUBJECT IS A GLYPH ON THE MAP (GM 2026-07-27, recorded in feature 257 and the settlement-review contract): a
    compound on a settlement map is one mark that contains everything the sheet draws inside it. So what stands INSIDE
    the subject's footprint - the garden's trees, a well in a court - is the sheet's own and is not compared, on either
    side; what is compared is the subject's relationship to the map (its place, its footprint, its gate, its approach)
    and the SITE outside it."""
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
    box = subject_box(plan, on_map.sheet_id)
    if box is None:
        return [f'no element marked id="{on_map.sheet_id}" on the sheet - the declaration names it as the subject']
    out: list[str] = []
    for ident in sorted(plan.ids & _ALL_KEYS):
        out.append(f'the sheet marks id="{ident}", a manifest key, not a class the check knows - the classes are {", ".join(SHEET_IDS)}')
    sx, sy = _center(box)
    tf = Transform(ftpx, sx, sy, subject_map[0].x, subject_map[0].y)
    frame = tf.frame(text)
    if frame is None:
        return out + ["the sheet has no viewBox, so its frame cannot be laid on the map"]
    home = subject_map[0]
    # a map feature standing inside the subject's own map footprint is the glyph's, as a sheet feature inside it is
    inv = {cls: [f for f in feats if f.pts or home.distance(f.x, f.y) > 0.0] for cls, feats in inventory(on_map, frame).items()}
    all_of: dict[str, list[MapFeature]] = {cls: [f for key in keys for f in _features(key, cls, m.get(key))] for cls, keys in CLASSES.items()}
    sheet = [(cls, r) for cls, r in sheet_features(plan) if not _inside(*_center(r), box)]
    step = grain * FTPX * ftpx  # a way is sampled at the map's grain, in sheet px
    ways = [[p for p in densify(pts, step) if not _inside(*p, box)] for pts in sheet_ways(text)]
    # (b) every sheet feature has its map counterpart within the grain
    for cls, r in sheet:
        cx, cy = _center(r)
        mx, my = tf.to_map(cx, cy)
        near = min((f.distance(mx, my) for f in all_of[cls]), default=math.inf)
        if near > grain:
            out.append(f"{cls.replace('_', ' ')} at svg({cx:.0f},{cy:.0f}) has no {cls.replace('_', ' ')} on the map within {grain:.0f} map px (map ({mx:.0f},{my:.0f}))")
    for samples in ways:
        offs = [(min((f.distance(*tf.to_map(px, py)) for f in all_of["lane"]), default=math.inf), px, py) for px, py in samples]
        worst = max(offs, default=None)
        if worst is not None and worst[0] > grain:
            out.append(f"the road at svg({worst[1]:.0f},{worst[2]:.0f}) runs {worst[0]:.0f} map px from every way on the map (the grain is {grain:.0f})")
    # (c) every map feature inside the frame has its sheet counterpart within the grain
    for cls, feats in inv.items():
        mine = [tf.to_map(*_center(r)) for c, r in sheet if c == cls]
        if cls == "lane":
            mine += [tf.to_map(px, py) for samples in ways for px, py in samples]
        for f in feats:
            if not any(f.distance(mx, my) <= grain for mx, my in mine):
                px = tf.sheet_ox + (f.x - tf.map_ox) * FTPX * ftpx
                py = tf.sheet_oy + (f.y - tf.map_oy) * FTPX * ftpx
                out.append(f"the map's {cls.replace('_', ' ')} at map ({f.x:.0f},{f.y:.0f}) = svg({px:.0f},{py:.0f}) is inside the frame and not on the sheet")
    # (d) the subject's footprint, per side
    sw, sh = box.w / FTPX, box.h / FTPX
    mw, mh = home.w * ftpx, home.h * ftpx
    if abs(sw - mw) > SIZE_GRAIN_PX * ftpx or abs(sh - mh) > SIZE_GRAIN_PX * ftpx:
        out.append(f"the subject is {sw:.0f} x {sh:.0f} ft on the sheet; the map draws it {mw:.0f} x {mh:.0f} ft")
    # (e) the subject's gate, where the map records one
    rec = subject_record(m, on_map, grain)
    if rec is not None:
        out += gate_agrees(plan, rec, tf, box, grain)
    return out


def site_classes(plan: ParsedPlan, text: str, on_map: OnMap | None) -> dict[str, bool] | None:
    """Which correspondence classes the declared map shows inside the sheet's frame - what the program check
    asks a SITE item against; None when the sheet declares no map or the declaration cannot be laid on it
    (then `matches_map` names why and every site item is asked for)."""
    if on_map is None:
        return None
    path = manifest_path(on_map)
    if not os.path.isfile(path):
        return None
    m = load_map(path)
    ftpx = float(m.get("meta", {}).get("ftpx", 0) or 0)
    subject_map = [f for f in _features(on_map.key, "subject", m.get(on_map.key)) if math.hypot(f.x - on_map.x, f.y - on_map.y) <= MAP_GRAIN_PX]
    subject = subject_box(plan, on_map.sheet_id)
    if ftpx <= 0 or not subject_map or subject is None:
        return None
    sx, sy = _center(subject)
    frame = Transform(ftpx, sx, sy, subject_map[0].x, subject_map[0].y).frame(text)
    if frame is None:
        return None
    return {cls: bool(feats) for cls, feats in inventory(on_map, frame).items()}


#: Where a map records a subject of each Mode A tier: the top-level keys of a settlement manifest (feature 294 B24).
TIER_KEYS: dict[str, tuple[str, ...]] = {t.tier: t.map_keys for t in load_types()}  # derived from types.json (map_keys)
#: The trees a settlement manifest lives in, from the skill root.
MAP_TREES: tuple[str, ...] = ("pool", "legacy-hand-authored-pool")


def maps_recording(stem: str, tier: str, root: str = SKILL_ROOT) -> list[str]:
    """The manifests (paths from `root`) that record a subject of the sheet's tier at the sheet's PLACE - the name
    convention `<place>-<type>` (`ubame-magistracy` -> `ubame`), matched to a map folder `<tree>/<tier>/<place>/<place>.json`
    whose tier key is a non-empty list. The name convention is a GUESS (the scout's, feature 294): a sheet named for
    another place than its map's is not found, and the explicit `**On map**: none - <why>` opt-out covers the rest."""
    place = stem.split("-")[0]
    out: list[str] = []
    for tree in MAP_TREES:
        base = os.path.join(root, tree)
        if not os.path.isdir(base):
            continue
        for map_tier in sorted(os.listdir(base)):
            rel = os.path.join(tree, map_tier, place, place + ".json")
            path = os.path.join(root, rel)
            if os.path.isfile(path) and any(isinstance(load_map(path).get(k), list) and load_map(path).get(k) for k in TIER_KEYS.get(tier, ())):
                out.append(rel)
    return out


def skipped(on_map: OnMap | None) -> str | None:
    """Why the check did not run: the report's line for a sheet on no map."""
    return None if on_map is not None else "on no map (no `**On map**:` line in the notes)"
