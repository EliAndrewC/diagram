"""What a caption may and may not cover, indexed once (feature 266, FR-006, FR-009, FR-014).

Built ONCE per label phase (or tool run) and asked per candidate - the engine's standing rule for a keep-out that
does not change during a search (constitution X clause 15). Each placed caption is added as it lands, so the next
caption sees it. The index prunes; the exact polygon tests decide.

Research: obstacle index - NONE: indexing and exact geometry
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

from .geom import Poly, Pt, bbox, centroid, inside, poly_gap, poly_seg_gap, seg_dist
from .standard import WAY_NOTCH, WEIGHT_WAY

CIVIC_GROUPS = frozenset({"ministry", "governor", "temple"})
"""The civic groups (research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html, the city rule, GM 2026-07-21): "a named civic building's caption ...
additionally may not touch any other named civic building", because the group rule alone "would permit one ministry's
name to sit on the next ministry". So when a caption's SUBJECT is a named civic building, every other NAMED civic
building keeps its full weight; a caption whose subject is not - a district's, even a "temple neighborhood" - is waived
onto its group like any other (FR-014).

Research: named civic buildings - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: ministry, governor and temple keep full weight against another civic caption
"""

GROUP_WORDS = {"funerary": ("funerary", "cemetery", "graveyard", "cremation", "mausoleum", "ossuary"), "estate": ("estate", "samurai")}
"""The words that name a caption group, where a group is named by more than its own word (feature 328 wave 5): a caption
naming a graveyard, a cremation ground, a mausoleum or an ossuary may cover any of the funerary structures; a samurai caption
may cover the samurai houses and estates (0243).

Research: a funerary caption covers the funerary structures - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: a graveyard, cremation, mausoleum or ossuary caption may cover any of the funerary structures, and a samurai caption the samurai houses and estates"""


def names_group(group: str | None, words: str) -> bool:
    """Does a caption's lower-cased text `words` name the caption `group` (its own word, or one of `GROUP_WORDS`)?

    Research: plumbing - NONE"""
    return bool(group) and any(w in words for w in GROUP_WORDS.get(group or "", (group or "",)))


ASSOCIATION_TIE = 1e-6
"""How much farther than a caption's own subject a neighbor may stand and still claim the caption (labels L6, the
ASSOCIATION): a tie counts, and this is float slack on the tie only - it decides no seat a rounding-free measure would
not. The search's term (`ObstacleIndex.score`) and the measured rule (`stands_nearest`) read it alike."""

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
    such ink, so none of its obstacles sets it. `keep` is a gap the obstacle asks for itself, when larger than the
    caption's own: a placed caption keeps its OWN clearance from the next one, so a small name set beside a large one
    keeps the large one's gap (feature 286 - by the small name's gap alone, Hayakawa's RESIDENCE stood 4.3 px from
    `family privy`, inside its own 5.5). `soft` marks ink a caption may be set on when no seat is free - a hand sheet's
    light roofs and nested ground (standard.py, "WHAT IS AN OVERLAP"); every other obstacle is an overlap the placer
    never draws (feature 287, D10). `circle` (x, y, r) says the obstacle is that disc - a tree crown - measured as a
    disc; `poly` is then its box (feature 287, labels L7)."""

    poly: tuple[Pt, ...]
    weight: float
    group: str | None = None
    named: bool = False
    inner: bool = False
    keep: float = 0.0
    soft: bool = False
    circle: tuple[float, float, float] | None = None


@dataclass(frozen=True)
class Way:
    """A lane, road, stream or ditch: a polyline a caption may cross at `WEIGHT_WAY`, with its drawn half-width. A `soft`
    way may be crossed when no seat is free (a hand sheet's road); crossing any other is an overlap (feature 287, D10)."""

    pts: tuple[Pt, ...]
    half_width: float
    soft: bool = False


def _cells(box: tuple[float, float, float, float]) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    return [(i, j) for i in range(math.floor(x0 / CELL), math.floor(x1 / CELL) + 1) for j in range(math.floor(y0 / CELL), math.floor(y1 / CELL) + 1)]


class ObstacleIndex:
    """Obstacles and ways bucketed by grid cell."""

    def __init__(self, obstacles: list[Obstacle] | None = None, ways: list[Way] | None = None) -> None:
        self.obstacles: list[Obstacle] = []
        self._boxes: list[tuple[float, float, float, float]] = []
        self._level: list[bool] = []
        self.ways: list[Way] = []
        self._ob: dict[tuple[int, int], list[int]] = defaultdict(list)
        self._segs: dict[tuple[int, int], list[tuple[int, int, Pt, Pt]]] = defaultdict(list)
        self._seg_boxes: list[tuple[float, float, float, float]] = []  # each way segment's own box, by its id
        for o in obstacles or []:
            self.add(o)
        for w in ways or []:
            self.add_way(w)

    def add(self, o: Obstacle) -> None:
        i = len(self.obstacles)
        self.obstacles.append(o)
        self._boxes.append(bbox(o.poly))
        self._level.append(level_rect(o.poly))
        bx0, by0, bx1, by1 = self._boxes[i]
        for c in _cells((bx0 - o.keep, by0 - o.keep, bx1 + o.keep, by1 + o.keep)):
            self._ob[c].append(i)

    def add_way(self, w: Way) -> None:
        wid = len(self.ways)
        self.ways.append(w)
        reach = w.half_width + WAY_NOTCH
        for a, b in zip(w.pts, w.pts[1:], strict=False):
            sid = len(self._seg_boxes)
            self._seg_boxes.append((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])))
            box = (min(a[0], b[0]) - reach, min(a[1], b[1]) - reach, max(a[0], b[0]) + reach, max(a[1], b[1]) + reach)
            for c in _cells(box):
                self._segs[c].append((wid, sid, a, b))

    def cost(self, block: Poly, clear: float, subject: Poly | None = None, text: str = "", civic: bool = False, own_gap: float | None = None) -> float:
        """The weight a caption set on `block` covers (`score`'s first half)."""
        return self.score(block, clear, subject, text, civic, own_gap)[0]

    def score(self, block: Poly, clear: float, subject: Poly | None = None, text: str = "", civic: bool = False, own_gap: float | None = None) -> tuple[float, bool]:
        """The weight a caption set on `block` covers - every obstacle it comes within `clear` of, except its own subject
        and any built feature of a group its `text` names (FR-014), plus `WEIGHT_WAY` per way it crosses - and whether
        any of it is an OVERLAP (an obstacle or way not `soft`; feature 287, D10). `civic` says the caption's SUBJECT is
        a named civic building, which keeps every other named civic building at full weight.

        `own_gap` is the block's gap to its own POINT subject (feature 287, labels L6: the standard's ASSOCIATION). An
        obstacle outside the subject standing as near the block as the subject does, or nearer, counts too: a caption
        as close to a neighbor as to what it names is not plainly its subject's. At the preferred offset this closes the
        tie (a neighbor exactly one offset off). The placer passes it for a seat with no leader (`placer._score`).

        Research:
            what a caption may cover - research/questions/0243-what-labels-may-cover-and-how-districts-are-named-on-town-and-city-maps.drawing.html: its own subject and the buildings of a group its words name, never a named
                civic building when its subject is one
            association - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a neighbor as near as the subject, or nearer, counts as covered
            ways crossed - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: each way crossed adds its weight
        """
        x0, y0, x1, y1 = bbox(block)
        level = level_rect(block)
        own_lim = own_gap + ASSOCIATION_TIE if own_gap is not None else -math.inf
        reach = max(clear, own_lim)
        cells = _cells((x0 - reach, y0 - reach, x1 + reach, y1 + reach))
        seen: set[int] = set()
        words = text.lower()
        total = 0.0
        hard = False
        for c in cells:
            for i in self._ob.get(c, ()):
                if i in seen:
                    continue
                seen.add(i)
                o = self.obstacles[i]
                need = max(clear, o.keep)
                bx0, by0, bx1, by1 = self._boxes[i]
                box_gap = math.hypot(max(0.0, bx0 - x1, x0 - bx1), max(0.0, by0 - y1, y0 - by1))
                if box_gap >= need - 1e-6 and box_gap > own_lim:
                    continue  # the boxes' gap bounds the outlines' from below: clear by the boxes, clear (feature 286)
                if not o.weight or (names_group(o.group, words) and not (civic and o.named and o.group in CIVIC_GROUPS)) or (subject is not None and not o.inner and part_of(o.poly, subject)):
                    continue
                # a disc is measured as a disc; two level rectangles are their boxes, so the boxes' gap is theirs (feature
                # 286: the outline test was nine tenths of placing a hand sheet's captions)
                gap = circle_gap(block, o.circle) if o.circle is not None else (box_gap if level and self._level[i] else poly_gap(block, list(o.poly)))
                near = gap < need - 1e-6  # strict: a seat exactly one offset off is clear (plan P6)...
                if not near and gap <= own_lim and subject is not None:
                    cx, cy = centroid(o.poly)
                    near = not inside(cx, cy, subject)  # ...unless its own subject stands no nearer (the association)
                if near:
                    total += o.weight
                    hard = hard or not o.soft
        # EACH SEGMENT MEASURED ONCE (feature 287, the board's 216 s siting): a long segment is filed in every cell it
        # crosses, and one block's cells met it again in each, measuring the same outline gap up to nine times; and the
        # boxes' gap, a lower bound on the outline gap, clears a segment before the outline is measured. Same verdict.
        crossed: set[int] = set()
        measured: set[int] = set()
        for c in cells:
            for wid, sid, a, b in self._segs.get(c, ()):
                if wid in crossed or sid in measured:
                    continue
                measured.add(sid)
                need = self.ways[wid].half_width + WAY_NOTCH
                sx0, sy0, sx1, sy1 = self._seg_boxes[sid]
                if math.hypot(max(0.0, sx0 - x1, x0 - sx1), max(0.0, sy0 - y1, y0 - sy1)) >= need:
                    continue
                if poly_seg_gap(block, a, b) < need:
                    crossed.add(wid)
                    hard = hard or not self.ways[wid].soft
        return total + WEIGHT_WAY * len(crossed), hard

    def nearer_than(self, block: Poly, gap: float, subject: Poly) -> bool:
        """Does any obstacle outside `subject` stand within `gap` of `block` - as near as the subject or nearer, a tie
        counting (`ASSOCIATION_TIE`)? The association term of `score` asked alone, of EVERY obstacle whatever its group
        (a caption beside a neighbor it may lie on still reads as that neighbor's), measured as `score` measures (a disc
        as a disc, else the outline); the subject is its own record (`part_of`) or ink whose center lies inside it."""
        x0, y0, x1, y1 = bbox(block)
        lim = gap + ASSOCIATION_TIE
        seen: set[int] = set()
        for c in _cells((x0 - lim, y0 - lim, x1 + lim, y1 + lim)):
            for i in self._ob.get(c, ()):
                if i in seen:
                    continue
                seen.add(i)
                bx0, by0, bx1, by1 = self._boxes[i]
                if math.hypot(max(0.0, bx0 - x1, x0 - bx1), max(0.0, by0 - y1, y0 - by1)) > lim:
                    continue  # the boxes' gap bounds the outlines' from below
                o = self.obstacles[i]
                if part_of(o.poly, subject) or inside(*centroid(o.poly), subject):
                    continue
                if (circle_gap(block, o.circle) if o.circle is not None else poly_gap(block, list(o.poly))) <= lim:
                    return True
        return False

    def blocked(self, block: Poly, clear: float, slack: float, subject: Poly | None = None, text: str = "", civic: bool = False) -> bool:
        """Does `score` count something against `block` that stays counted however the block is moved by up to `slack` -
        an obstacle or way nearer it than its own clearance less `slack`? Then no seat within `slack` of this one is free
        (a gap moves no more than the block does), and a strict search need not measure it or nudge it (feature 287: the
        board's siting, which proved every seat under one wide canopy seat by seat, 216 s). Asks the first such thing and
        stops; the association term only adds weight, so it is not asked.

        A gap bounds a moved block's gap only from above by gap + `slack`, which says nothing where the clearance is under
        `slack`; so an OVERLAP is judged by its depth instead: the block's center inside an obstacle by more than `slack`,
        a disc reaching more than `slack` past the block, or a way through the disc the block's rectangle holds about its
        center by more than `slack` - each still an overlap however the block moves by `slack`."""
        x0, y0, x1, y1 = bbox(block)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2  # a rectangle's center is its box's
        inner = min(math.dist(block[0], block[1]), math.dist(block[1], block[2])) / 2  # the block is a rectangle (`rect`)
        cells = _cells((x0 - clear, y0 - clear, x1 + clear, y1 + clear))
        words = text.lower()
        for c in cells:
            for i in self._ob.get(c, ()):
                o = self.obstacles[i]
                need = max(clear, o.keep) - 1e-6
                bx0, by0, bx1, by1 = self._boxes[i]
                box_gap = math.hypot(max(0.0, bx0 - x1, x0 - bx1), max(0.0, by0 - y1, y0 - by1))
                if box_gap > 0.0 and box_gap >= need - slack:
                    continue  # apart by more than a moved block could close
                if not o.weight or (names_group(o.group, words) and not (civic and o.named and o.group in CIVIC_GROUPS)):
                    continue
                if subject is not None and not o.inner and part_of(o.poly, subject):
                    continue
                if o.circle is not None:
                    ox, oy, r = o.circle
                    reach = 0.0 if inside(ox, oy, block) else min(seg_dist((ox, oy), a, b) for a, b in zip(block, [*block[1:], block[0]], strict=True))
                    if reach - r < need - slack:
                        return True
                    continue
                gap = box_gap if self._level[i] and level_rect(block) else poly_gap(block, list(o.poly))
                if gap < need - slack:
                    return True
                if gap == 0.0 and inside(cx, cy, o.poly):
                    ring = list(o.poly)
                    if min(seg_dist((cx, cy), a, b) for a, b in zip(ring, [*ring[1:], ring[0]], strict=True)) > slack:
                        return True
            for wid, sid, a, b in self._segs.get(c, ()):
                need = self.ways[wid].half_width + WAY_NOTCH
                sx0, sy0, sx1, sy1 = self._seg_boxes[sid]
                if math.hypot(max(0.0, sx0 - x1, x0 - sx1), max(0.0, sy0 - y1, y0 - sy1)) >= need:
                    continue
                if poly_seg_gap(block, a, b) < need - slack or seg_dist((cx, cy), a, b) + slack < inner:
                    return True
        return False


def stands_nearest(block: Poly, subject: Poly, index: ObstacleIndex) -> bool:
    """THE ONE PREDICATE of the association as the reader meets it (labels L6): does the caption on `block` stand nearer
    its own `subject` than any obstacle `index` holds - strictly, a tie being the neighbor's? The search's term decides a
    seat on its exact geometry; a map is judged on its RECORD, rounded to 0.1 unit, which moves each gap by up to a tenth
    of a unit - enough to turn a neighbor a hair farther than the subject into one a hair nearer (Kuwabata, feature 287:
    the board's caption 4.008 ft off a threshing yard and 4.056 ft off its board as recorded). So the notice board's
    siter asks this of the geometry AS IT WILL BE RECORDED, and the pool test asks it of the record.

    Research: association - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: nearer its own subject than any other drawn thing, strictly
    """
    return not index.nearer_than(block, poly_gap(block, list(subject)), subject)


def circle_gap(block: Poly, circle: tuple[float, float, float]) -> float:
    """The gap between a caption's block and a disc (x, y, r): 0 when they meet."""
    x, y, r = circle
    if inside(x, y, block):
        return 0.0
    edge = min(seg_dist((x, y), a, b) for a, b in zip(block, [*block[1:], block[0]], strict=True))
    return max(0.0, edge - r)


def circle_obstacle(x: float, y: float, r: float, weight: float, group: str | None = None) -> Obstacle:
    """A disc as an obstacle - a tree crown (feature 287, labels L7): its box files it, the disc measures it."""
    return Obstacle(((x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)), weight, group, circle=(x, y, r))


def level_rect(poly: tuple[Pt, ...] | Poly) -> bool:
    """Is this outline a level rectangle - four corners, every edge along an axis - so that its box is itself?"""
    return len(poly) == 4 and all(abs(a[0] - b[0]) < 1e-9 or abs(a[1] - b[1]) < 1e-9 for a, b in zip(poly, [*poly[1:], poly[0]], strict=True))


def part_of(poly: tuple[Pt, ...] | Poly, subject: Poly) -> bool:
    """Is this obstacle the subject itself? Its center lies inside the subject, its box inside the subject's box (1 unit
    of slack), and it spans at least half the subject's box: a board's own record, a building's own rect. A well in a
    court or a post in a hall lies inside its area and is NOT the area - an area caption must still keep off it. Neither
    mode needs to carry an identity for this, which is what lets one index serve the settlement engine, the compound
    composer and a hand-drawn sheet."""
    sx0, sy0, sx1, sy1 = bbox(subject)
    ox0, oy0, ox1, oy1 = bbox(poly)
    if not (ox0 >= sx0 - 1 and oy0 >= sy0 - 1 and ox1 <= sx1 + 1 and oy1 <= sy1 + 1):
        return False  # the cheap box test first: an obstacle not within the subject's box is not the subject
    cx, cy = centroid(poly)
    return inside(cx, cy, subject) and (ox1 - ox0) * (oy1 - oy0) >= 0.5 * (sx1 - sx0) * (sy1 - sy0)
