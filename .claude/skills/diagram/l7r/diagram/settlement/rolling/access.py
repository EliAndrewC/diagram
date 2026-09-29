"""The access-corridor tree reserved at seating (feature 287, plan M3's seat half; homes H16, ways W01).

A farmhouse the lane web cannot reach was found only on the finished map, and the map was re-rolled with that ground
forbidden (`hamletgen/driver.py`). Eighteen seat-time reach tests failed before this because they ran while the
neighbors' fabric was still to be laid. The corridor is reserved AGAINST that fabric instead: the first corridor is an
EXIT STRIP from the cluster's center outward, and each house is admitted only with a clear corridor from its door to
the tree - a straight strip a footpath wide, clear of every other homestead's box and of the ground the boundary
refuses. Every later envelope refuses to cover a corridor, so no household seated after can hem a house in.

The corridor is a RESERVATION, not a way: the web draws a way along it where its lanes do not reach the house
(WAYS' `settle_the_web`). The tree is recorded on the manifest (`access_corridors`) for the stages that follow.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from .._geom import PointGrid, Pt, seg_closest, seg_dist, segments_cross
from .._geom.primitives import chain_violated

if TYPE_CHECKING:
    from ..core import Settlement

#: Half the corridor's width, in feet: `WEB_FABRIC_GAP` (7 ft) either side of the tread's line - a footpath's room between
#: two steadings, the gap the web's own fabric keeps (homes H16: "a footpath-width strip (WEB_FABRIC_GAP x 2)").
ACCESS_HALF_FT = 7.0

#: How far along a corridor its ground is sampled against the site boundary, in px: finer than the thinnest member the
#: boundary holds a corridor off (a ditch's half-width plus its clearance).
SAMPLE_PX = 8.0

#: How many of the tree's points a door tries before its seat is refused, nearest first: each corridor's nearest point and
#: its points every `TARGET_STEP_PX` along it. A straight corridor to the nearest point is the common case; a point further
#: along the same corridor is the way round a neighbor standing square across the direct run.
TARGETS_TRIED = 12

#: The spacing of the points along a corridor a door may aim at, in px: half a bundle pitch (`BUNDLE_PITCH`, 100 ft), so a
#: neighbor's homestead standing across the direct run leaves an aim point on either side of it.
TARGET_STEP_PX = 50.0


def _seg_box_gap(a: Pt, b: Pt, box: Any) -> float:
    """The least distance from the segment a-b to the axis-aligned box `(cx, cy, w, h)`; 0 where they meet."""
    cx, cy, w, h = box
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in (a, b)):
        return 0.0
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if any(segments_cross(a, b, corners[k], corners[(k + 1) % 4]) for k in range(4)):
        return 0.0
    return min(
        min(seg_dist(c[0], c[1], a, b) for c in corners),
        min(seg_dist(p[0], p[1], corners[k], corners[(k + 1) % 4]) for p in (a, b) for k in range(4)),
    )


class AccessTree:
    """The reserved corridors: segments `(a, b)` a footpath wide (`half` either side), indexed by their widened boxes."""

    __slots__ = ("grid", "half", "segs")

    def __init__(self, half: float) -> None:
        self.half = half
        self.segs: list[tuple[Pt, Pt]] = []
        self.grid = PointGrid(128.0)

    def add(self, a: Pt, b: Pt) -> None:
        self.segs.append((a, b))
        h = self.half
        self.grid.extend([(a, b, min(a[0], b[0]) - h, min(a[1], b[1]) - h, max(a[0], b[0]) + h, max(a[1], b[1]) + h)])

    def covers_box(self, box: Any) -> bool:
        """Does any corridor's strip meet the box `(cx, cy, w, h)`? The ONE test an envelope asks (plan M3: every later
        placement refuses to cover a corridor)."""
        cx, cy, w, h = box
        for a, b, x0, y0, x1, y1 in self.grid.near(cx, cy, max(w, h) / 2 + self.half):
            if x1 < cx - w / 2 or x0 > cx + w / 2 or y1 < cy - h / 2 or y0 > cy + h / 2:
                continue
            if _seg_box_gap(a, b, box) < self.half:
                return True
        return False

    def targets(self, p: Pt) -> list[Pt]:
        """The nearest point of each corridor and its points every `TARGET_STEP_PX`, nearest first, at most
        `TARGETS_TRIED`."""
        pts: list[Pt] = []
        for a, b in self.segs:
            pts.append(seg_closest(p[0], p[1], a, b))
            n = int(math.dist(a, b) // TARGET_STEP_PX)
            pts += [(a[0] + (b[0] - a[0]) * k / max(1, n), a[1] + (b[1] - a[1]) * k / max(1, n)) for k in range(n + 1)]
        pts.sort(key=lambda q: math.dist(p, q))
        return pts[:TARGETS_TRIED]


def doors_of(geom: Any) -> list[Pt]:
    """Where a homestead's corridor may start, in preference order: its forecourt (the yard's center, before the door),
    then a step off each of the house's four walls - a farmhouse is entered from more than one side (the doma's front
    and back doors), and a corridor that had to cross its own house to leave by the front is taken out the back."""
    boxes = geom.get("boxes") or {}
    yard = boxes.get("yard") or geom.get("yard")
    hx, hy, hw, hh = boxes.get("house") or geom["house"]
    step = 2.0
    walls = [(hx, hy + hh / 2 + step), (hx, hy - hh / 2 - step), (hx + hw / 2 + step, hy), (hx - hw / 2 - step, hy)]
    return ([(float(yard[0]), float(yard[1]))] if yard is not None else []) + [(float(x), float(y)) for x, y in walls]


def start_tree(s: Settlement, center: Pt, out: Pt, length: float) -> AccessTree:
    """The tree's first corridor, the EXIT STRIP: from the cluster's center outward along `out` for `length` px (the
    connector starts at its outer end). Installed on the settlement for the seat pass and recorded on the manifest."""
    tree = AccessTree(s.px(ACCESS_HALF_FT))
    end = (center[0] + out[0] * length, center[1] + out[1] * length)
    tree.add(center, end)
    s._access = tree
    s.M["access_corridors"] = []
    s.M["access_exit"] = [[round(center[0], 1), round(center[1], 1)], [round(end[0], 1), round(end[1], 1)]]
    return tree


def corridor_clear(s: Settlement, a: Pt, b: Pt, own: Any) -> bool:
    """May a corridor run a-b? Its strip clears every placed homestead box but its own (`own`, the candidate's bbox, whose
    house it may not cross either), and its line stands on ground the site boundary admits - not on the field's side of a
    chord, not within a water course's clearance, not inside the outline of the other ground."""
    tree = s._access
    half = tree.half
    house = own.get("boxes", {}).get("house") or own["house"]
    if _seg_box_gap(a, b, house) < 0.5:
        return False
    x0, y0, x1, y1 = min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])
    seen: set[int] = set()
    for it in s._reach_index(s.placed, "placed_reach").near((x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0) / 2 + half):
        if id(it) in seen:
            continue
        seen.add(id(it))
        if _seg_box_gap(a, b, (it[0], it[1], it[2], it[3])) < half:
            return False
    n = max(1, int(math.dist(a, b) / SAMPLE_PX))
    pts = [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
    chains, corr = getattr(s, "_site_chains", None), getattr(s, "_site_corridors", None)
    if chains and any(chain_violated(px, py, chains, 0.0) for px, py in pts):
        return False
    return not (corr is not None and any(corr.hit_points([p]) for p in pts))


def access_corridor(s: Settlement, geom: Any) -> tuple[Pt, Pt] | None:
    """The corridor this homestead would be admitted with: from its door to the first of the tree's nearest points that a
    clear strip reaches (`corridor_clear`). None when no target is clear - the seat is refused (the ONE predicate the
    placer reads and its test reads)."""
    tree = getattr(s, "_access", None)
    if tree is None:
        return None
    for door in doors_of(geom):
        for q in tree.targets(door):
            if math.dist(door, q) < 1e-6 or corridor_clear(s, door, q, geom):
                return (door, q)
    return None


def reserve(s: Settlement, corridor: tuple[Pt, Pt], of: Pt | None = None) -> None:
    """Add an admitted house's corridor to the tree and to the manifest's record, naming the house it serves (`of`, its
    center) - the record the web reads to draw a way along the corridor of a house its lanes do not reach."""
    a, b = corridor
    s._access.add(a, b)
    rec: dict[str, Any] = {"pts": [[round(a[0], 1), round(a[1], 1)], [round(b[0], 1), round(b[1], 1)]]}
    if of is not None:
        rec["of"] = [round(of[0], 1), round(of[1], 1)]
    s.M.setdefault("access_corridors", []).append(rec)
