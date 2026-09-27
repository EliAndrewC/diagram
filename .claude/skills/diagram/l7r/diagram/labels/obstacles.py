"""What a caption may and may not cover, indexed once (feature 266, FR-006, FR-009, FR-014).

Built ONCE per label phase (or tool run) and asked per candidate - the engine's standing rule for a keep-out that
does not change during a search (constitution X clause 15). Each placed caption is added as it lands, so the next
caption sees it. The index prunes; the exact polygon tests decide.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

from .geom import Poly, Pt, bbox, centroid, inside, poly_gap, poly_seg_gap
from .standard import WAY_NOTCH, WEIGHT_WAY

CIVIC_GROUPS = frozenset({"ministry", "governor", "temple"})
"""The civic groups (research/presentation 070, the city rule, GM 2026-07-21): "a named civic building's caption ...
additionally may not touch any other named civic building", because the group rule alone "would permit one ministry's
name to sit on the next ministry". So when a caption's SUBJECT is a named civic building, every other NAMED civic
building keeps its full weight; a caption whose subject is not - a district's, even a "temple neighborhood" - is waived
onto its group like any other (FR-014)."""

CELL = 32.0
"""The grid's cell, in drawing units. A pruning grain, not a rule: it decides nothing a smaller or larger cell would
decide differently."""


@dataclass(frozen=True)
class Obstacle:
    """A drawn thing a caption is scored against. `weight` is on Esri's 0-1,000 scale; `group` is the caption word that
    may cover it (the overlap taxonomy's caption group, FR-014), or None; `named` marks a civic building that carries a
    name of its own (a ministry, the governor's yamen, a temple by name), which no other caption may lie on. `inner`
    marks ink INSIDE a subject that its caption must still avoid - a hand sheet draws a building's partitions, a court's
    mats, a garden's stepping stones, and a name set on them could not be read (feature 267); a generated map draws no
    such ink, so none of its obstacles sets it."""

    poly: tuple[Pt, ...]
    weight: float
    group: str | None = None
    named: bool = False
    inner: bool = False


@dataclass(frozen=True)
class Way:
    """A lane, road, stream or ditch: a polyline a caption may cross at `WEIGHT_WAY`, with its drawn half-width."""

    pts: tuple[Pt, ...]
    half_width: float


def _cells(box: tuple[float, float, float, float]) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    return [(i, j) for i in range(math.floor(x0 / CELL), math.floor(x1 / CELL) + 1) for j in range(math.floor(y0 / CELL), math.floor(y1 / CELL) + 1)]


class ObstacleIndex:
    """Obstacles and ways bucketed by grid cell."""

    def __init__(self, obstacles: list[Obstacle] | None = None, ways: list[Way] | None = None) -> None:
        self.obstacles: list[Obstacle] = []
        self.ways: list[Way] = []
        self._ob: dict[tuple[int, int], list[int]] = defaultdict(list)
        self._segs: dict[tuple[int, int], list[tuple[int, Pt, Pt]]] = defaultdict(list)
        for o in obstacles or []:
            self.add(o)
        for w in ways or []:
            self.add_way(w)

    def add(self, o: Obstacle) -> None:
        i = len(self.obstacles)
        self.obstacles.append(o)
        for c in _cells(bbox(o.poly)):
            self._ob[c].append(i)

    def add_way(self, w: Way) -> None:
        wid = len(self.ways)
        self.ways.append(w)
        reach = w.half_width + WAY_NOTCH
        for a, b in zip(w.pts, w.pts[1:], strict=False):
            box = (min(a[0], b[0]) - reach, min(a[1], b[1]) - reach, max(a[0], b[0]) + reach, max(a[1], b[1]) + reach)
            for c in _cells(box):
                self._segs[c].append((wid, a, b))

    def cost(self, block: Poly, clear: float, subject: Poly | None = None, text: str = "", civic: bool = False) -> float:
        """The weight a caption set on `block` covers: every obstacle it comes within `clear` of, except its own subject
        and any built feature of a group its `text` names (FR-014), plus `WEIGHT_WAY` per way it crosses. `civic` says
        the caption's SUBJECT is a named civic building, which keeps every other named civic building at full weight."""
        x0, y0, x1, y1 = bbox(block)
        cells = _cells((x0 - clear, y0 - clear, x1 + clear, y1 + clear))
        seen: set[int] = set()
        words = text.lower()
        total = 0.0
        for c in cells:
            for i in self._ob.get(c, ()):
                if i in seen:
                    continue
                seen.add(i)
                o = self.obstacles[i]
                if not o.weight or (o.group and o.group in words and not (civic and o.named and o.group in CIVIC_GROUPS)) or (subject is not None and not o.inner and part_of(o.poly, subject)):
                    continue
                if poly_gap(block, list(o.poly)) < clear - 1e-6:  # strict: a seat exactly one offset off is clear (plan P6)
                    total += o.weight
        crossed: set[int] = set()
        for c in cells:
            for wid, a, b in self._segs.get(c, ()):
                if wid not in crossed and poly_seg_gap(block, a, b) < self.ways[wid].half_width + WAY_NOTCH:
                    crossed.add(wid)
        return total + WEIGHT_WAY * len(crossed)


def part_of(poly: tuple[Pt, ...] | Poly, subject: Poly) -> bool:
    """Is this obstacle the subject itself? Its center lies inside the subject, its box inside the subject's box (1 unit
    of slack), and it spans at least half the subject's box: a board's own record, a building's own rect. A well in a
    court or a post in a hall lies inside its area and is NOT the area - an area caption must still keep off it. Neither
    mode needs to carry an identity for this, which is what lets one index serve the settlement engine, the compound
    composer and a hand-drawn sheet."""
    cx, cy = centroid(poly)
    sx0, sy0, sx1, sy1 = bbox(subject)
    ox0, oy0, ox1, oy1 = bbox(poly)
    within = ox0 >= sx0 - 1 and oy0 >= sy0 - 1 and ox1 <= sx1 + 1 and oy1 <= sy1 + 1
    return inside(cx, cy, subject) and within and (ox1 - ox0) * (oy1 - oy0) >= 0.5 * (sx1 - sx0) * (sy1 - sy0)
