"""THE caption placer (feature 266): one for every caption, in both modes and on a hand-drawn sheet.

The GM, 2026-09-27: *"I also agree with one placer for all labels"*, adopting the cartographic standard
(research/presentation.html, "Where does a caption sit"). `place()` takes what a caption NAMES - a point feature's
drawn footprint, a line, or an area - and returns where the words go, at what angle, on how many lines, and whether a
leader line ties them back. The standard, in the order it decides:

1. NEARER FIRST (QGIS's default, "Prefer closer labels"): every candidate at the preferred offset - every ranked
   position, every line layout - is tried before any seat a ring further out.
2. Within a ring, the RANKED POSITIONS (`standard.POSITIONS`: the user-tested order of Bobák, Čmolík and Čadík 2024 -
   above, below, right, then the corners on the right, left, the corners on the left; feature 290), then fewer lines
   before more (the GM's wrap rule).
3. FREE SPACE WINS: the first candidate that covers nothing is taken. Only when nothing in reach is free does the
   caption go where it covers the least weight - it is never dropped (the GM: "we'll treat labels as mandatory").
4. A caption not at the preferred offset is no longer directly beside its feature, so a LEADER line joins it back
   (QGIS callouts, Esri's leader, PSU: "labels that do not fit on or directly adjacent to their respective feature").
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Iterator
from dataclasses import dataclass, replace

from .geom import Poly, Pt, area_centroid, bbox, centroid, inside, nearest_points, rect, seg_closest
from .layout import layouts
from .obstacles import ObstacleIndex
from .standard import CENTER_ABOVE_BASELINE_EM, CHAR_W_EM, CLEAR_EM, LINE_H_EM, PITCH_EM, POSITIONS, PREFERRED_OFFSET_EM, REACH_EM, RING_STEP_EM, WEIGHT_OBSTACLE, block_half, upright

AREA_SEATS = 400
"""How many interior seats an area caption tries, nearest the centroid first - a search bound, not a rule."""

LINE_STATIONS = 13
"""How many stations along a line a line caption tries, nearest its hint first - a search bound, not a rule."""


@dataclass(frozen=True)
class Subject:
    """What a caption names. `kind` is "point" (a feature beside which the caption stands - its drawn outline and its
    rotation), "line" (a polyline with its drawn half-width, the caption running along it near `hint`) or "area" (an
    outline the caption lies inside). `civic` marks a subject that is itself a named civic building (FR-014)."""

    kind: str
    poly: tuple[Pt, ...]
    angle: float = 0.0
    half_width: float = 0.0
    hint: Pt | None = None
    civic: bool = False


@dataclass(frozen=True)
class Placement:
    """Where a caption goes. (`x`, `y`) is the anchor `label()` takes - the middle of the first line's baseline, the
    block turned by `angle` about its own center; `block` is that drawn block; `ring` 0 is the preferred offset."""

    x: float
    y: float
    angle: float
    lines: tuple[str, ...]
    block: tuple[Pt, ...]
    ring: int
    rank: int
    position: str
    cost: float
    leader: tuple[Pt, Pt] | None


@dataclass(frozen=True)
class _Cand:
    ring: int
    rank: int
    position: str
    center: Pt
    angle: float
    lines: tuple[str, ...]
    half: tuple[float, float]
    size: float


EXTENDED_SLIDES = 8
"""How many steps the extended search slides a caption along each side of a point subject, between the ranked corner
and edge seats (feature 286): the ranked positions alone missed free seats a person found beside small subjects."""


EXTENDED_AREA_FACTOR = 5
"""How many times the standard's inside seats the fallback samples an area with, spread over its whole extent, at no
coarser than a quarter em (feature 286: Hayakawa's guardroom and HEARING COURT had free seats in bands narrower than
the standard's one-em grid)."""


def sized_half(lines: list[str] | tuple[str, ...], size: float, char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> tuple[float, float]:
    """A caption block's half-extents, each line at its own size when `line_sizes` gives them (a name over a smaller
    gloss): measured at the head's size, Hayakawa's bath and HEARING COURT were too tall for any seat (feature 286)."""
    bw, bh = block_half(lines, size, char_w)
    if line_sizes:
        bh = (line_sizes[0] * LINE_H_EM + sum(PITCH_EM * s for s in line_sizes[1:])) / 2.0
    return bw, bh


def rings(size: float) -> list[float]:
    """The ring distances for a caption of `size`: the preferred offset, then a step at a time out to the reach."""
    n = int(round((REACH_EM - PREFERRED_OFFSET_EM) / RING_STEP_EM)) + 1
    return [(PREFERRED_OFFSET_EM + k * RING_STEP_EM) * size for k in range(n)]


def _frame_of(angle: float) -> tuple[Pt, Pt]:
    a = math.radians(angle)
    return (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def _point_cands(text: str, size: float, subject: Subject, lays: list[list[str]], char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> Iterator[_Cand]:
    ang = upright(subject.angle)
    u, v = _frame_of(ang)
    c = centroid(subject.poly)
    pu = [(p[0] - c[0]) * u[0] + (p[1] - c[1]) * u[1] for p in subject.poly]
    pv = [(p[0] - c[0]) * v[0] + (p[1] - c[1]) * v[1] for p in subject.poly]
    cu, cv = (min(pu) + max(pu)) / 2, (min(pv) + max(pv)) / 2
    c = (c[0] + cu * u[0] + cv * v[0], c[1] + cu * u[1] + cv * v[1])  # the center of the subject's box in its frame
    su, sv = (max(pu) - min(pu)) / 2, (max(pv) - min(pv)) / 2
    for ring, g in enumerate(rings(size)):
        for rank, (name, sx, sy) in enumerate(POSITIONS):
            for lines in lays:
                bw, bh = sized_half(lines, size, char_w, line_sizes)
                if abs(sx) == 1.0 and sy:
                    # A CORNER: the block's near corner stands `g` from the subject's corner, along the diagonal.
                    du, dv = sx * (su + bw + g / math.sqrt(2)), sy * (sv + bh + g / math.sqrt(2))
                elif not sy:
                    du, dv = sx * (su + bw + g), 0.0
                else:
                    du, dv = sx * 2.0 * bw, sy * (sv + bh + g)
                yield _Cand(ring, rank, name, (c[0] + du * u[0] + dv * v[0], c[1] + du * u[1] + dv * v[1]), ang, tuple(lines), (bw, bh), size)


def _line_cands(text: str, size: float, subject: Subject, lays: list[list[str]], char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> Iterator[_Cand]:
    pts = list(subject.poly)
    segs = list(zip(pts, pts[1:], strict=False))
    lengths = [math.dist(a, b) for a, b in segs]
    total = sum(lengths)
    if subject.hint is not None:
        best = min(range(len(segs)), key=lambda i: math.dist(subject.hint, seg_closest(subject.hint, *segs[i])))  # type: ignore[arg-type]
        q = seg_closest(subject.hint, *segs[best])
        s0 = sum(lengths[:best]) + math.dist(segs[best][0], q)
    else:
        s0 = total / 2
    step = 2.0 * size
    stations = [s0]
    for j in range(1, LINE_STATIONS):
        for s in (s0 + j * step, s0 - j * step):
            if 0.0 <= s <= total:
                stations.append(s)
    stations = stations[:LINE_STATIONS]

    def at(s: float) -> tuple[Pt, float]:
        for (a, b), ln in zip(segs, lengths, strict=True):
            if s <= ln or (a, b) == segs[-1]:
                t = 0.0 if ln == 0 else min(1.0, s / ln)
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            s -= ln
        raise AssertionError("unreachable: the last segment returns")  # pragma: no cover - the loop's last pass returns

    for ring, g in enumerate(rings(size)):
        for j, s in enumerate(stations):
            p, bearing = at(s)
            ang = upright(bearing)
            _u, v = _frame_of(ang)
            for side, name in ((-1.0, "above"), (1.0, "below")):  # above the line before below (psu-geog486-point-labels)
                for lines in lays:
                    bw, bh = sized_half(lines, size, char_w, line_sizes)
                    d = subject.half_width + g + bh
                    yield _Cand(ring, j * 2 + (side > 0), name, (p[0] + side * d * v[0], p[1] + side * d * v[1]), ang, tuple(lines), (bw, bh), size)


def _area_cands(text: str, size: float, subject: Subject, lays: list[list[str]], char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> Iterator[_Cand]:
    ang = upright(subject.angle)
    c = area_centroid(subject.poly)
    x0, y0, x1, y1 = bbox(subject.poly)
    grid = [(x0 + i * size, y0 + j * size) for i in range(int((x1 - x0) / size) + 1) for j in range(int((y1 - y0) / size) + 1)]
    seats = [c] + sorted((p for p in grid if inside(p[0], p[1], subject.poly)), key=lambda p: math.dist(p, c))[: AREA_SEATS - 1]
    for rank, p in enumerate(seats):
        for lines in lays:
            yield _Cand(0, rank, "inside", p, ang, tuple(lines), sized_half(lines, size, char_w, line_sizes), size)


def _extended_cands(text: str, size: float, subject: Subject, lines: list[str] | None = None, char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> Iterator[_Cand]:
    """THE FALLBACK SEARCH (feature 286), tried only when the standard's candidates found no free seat: an area's inside
    sampled over its whole extent, the step set by its size rather than one em (a large court's free ground lay beyond
    the 400 seats nearest its centroid); round a point subject, the block slid along each side between the ranked
    positions, ring by ring. A line subject's stations already walk its length, so it adds nothing."""
    lays = [lines] if lines else layouts(text)
    sizes = line_sizes if lines else None
    ang = upright(subject.angle)
    if subject.kind == "area":
        x0, y0, x1, y1 = bbox(subject.poly)
        step = max(size / 4.0, math.sqrt(max((x1 - x0) * (y1 - y0), 1e-9) / (EXTENDED_AREA_FACTOR * AREA_SEATS)))
        c = area_centroid(subject.poly)
        grid = [(x0 + i * step, y0 + j * step) for i in range(int((x1 - x0) / step) + 1) for j in range(int((y1 - y0) / step) + 1)]
        for rank, p in enumerate(sorted((q for q in grid if inside(q[0], q[1], subject.poly)), key=lambda q: math.dist(q, c))):
            for ln in lays:
                yield _Cand(0, rank, "inside", p, ang, tuple(ln), sized_half(ln, size, char_w, sizes), size)
        return
    if subject.kind != "point":
        return
    u, v = _frame_of(ang)
    c = centroid(subject.poly)
    pu = [(p[0] - c[0]) * u[0] + (p[1] - c[1]) * u[1] for p in subject.poly]
    pv = [(p[0] - c[0]) * v[0] + (p[1] - c[1]) * v[1] for p in subject.poly]
    cu, cv = (min(pu) + max(pu)) / 2, (min(pv) + max(pv)) / 2
    c = (c[0] + cu * u[0] + cv * v[0], c[1] + cu * u[1] + cv * v[1])
    su, sv = (max(pu) - min(pu)) / 2, (max(pv) - min(pv)) / 2
    slides = [-1.0 + 2.0 * k / EXTENDED_SLIDES for k in range(EXTENDED_SLIDES + 1)]
    for ring, g in enumerate(rings(size)):
        for ln in lays:
            bw, bh = sized_half(ln, size, char_w, sizes)
            rank = 0
            for name, side in (("above", -1.0), ("below", 1.0)):
                for s in slides:
                    yield _Cand(
                        ring, rank, name, (c[0] + s * (su + bw) * u[0] + side * (sv + bh + g) * v[0], c[1] + s * (su + bw) * u[1] + side * (sv + bh + g) * v[1]), ang, tuple(ln), (bw, bh), size
                    )
                    rank += 1
            for name, side in (("right", 1.0), ("left", -1.0)):  # right before left, as in `POSITIONS` (feature 290)
                for s in slides:
                    yield _Cand(
                        ring, rank, name, (c[0] + side * (su + bw + g) * u[0] + s * (sv + bh) * v[0], c[1] + side * (su + bw + g) * u[1] + s * (sv + bh) * v[1]), ang, tuple(ln), (bw, bh), size
                    )
                    rank += 1


def _cands(text: str, size: float, subject: Subject, lines: list[str] | None = None, char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> Iterator[_Cand]:
    lays = [lines] if lines else layouts(text)
    sizes = line_sizes if lines else None  # per-line sizes hold only for fixed lines
    if subject.kind == "point":
        return _point_cands(text, size, subject, lays, char_w, sizes)
    if subject.kind == "line":
        return _line_cands(text, size, subject, lays, char_w, sizes)
    if subject.kind == "area":
        return _area_cands(text, size, subject, lays, char_w, sizes)
    raise ValueError(f"a caption's subject is a point, a line or an area, not {subject.kind!r}")


def place(
    text: str,
    size: float,
    subject: Subject,
    index: ObstacleIndex,
    frame: tuple[float, float, float, float] | None = None,
    lines: list[str] | None = None,
    char_w: float = CHAR_W_EM,
    leader_index: ObstacleIndex | None = None,
    line_sizes: list[float] | None = None,
    extended: bool = True,
) -> Placement:
    """Seat one caption by the standard (the module docstring). `frame` is the finished picture's (x0, y0, x1, y1); a
    block that leaves it is never a candidate, because a clipped caption cannot be read. `lines` fixes the caption's
    lines (a hand-drawn caption with a line of its own under it) instead of the wrap rule's layouts. Never returns
    nothing. `char_w` is the caption's width per character in ems - the standard's for the engine's own captions; a
    hand sheet's bold, capital or letter-spaced caption runs wider (feature 267: `labels/hand_sheet.py` measures it).
    `line_sizes` gives each fixed line its own size (a name over a smaller gloss). When no standard candidate is free, a
    fallback search (`_extended_cands`) runs before the least-cost seat is taken.
    `leader_index` holds what a seat's leader line may not pass over or end against - the other captions and the small
    glyphs, which a hand sheet supplies (feature 283); the engine passes none, and its leaders are weighed as before."""
    clear = CLEAR_EM * size
    own: Poly | None = list(subject.poly) if subject.kind != "line" else None
    best: tuple[float, int, _Cand, Poly] | None = None
    first: tuple[_Cand, Poly] | None = None
    # the standard's candidates, then - reached only when none was free, the chain being lazy - the fallback search
    # (feature 286), before the least cost is taken
    more = _extended_cands(text, size, subject, lines, char_w, line_sizes) if extended else iter(())
    for order, cand in enumerate(itertools.chain(_cands(text, size, subject, lines, char_w, line_sizes), more)):
        block = rect(cand.center[0], cand.center[1], cand.half[0], cand.half[1], cand.angle)
        if first is None:
            first = (cand, block)
        bx0, by0, bx1, by1 = bbox(block)
        if frame is not None and (bx0 < frame[0] or by0 < frame[1] or bx1 > frame[2] or by1 > frame[3]):
            continue
        cost = index.cost(block, clear, own, text, subject.civic)
        if subject.kind == "area" and not all(inside(p[0], p[1], subject.poly) for p in block):
            cost += WEIGHT_OBSTACLE  # an area's name lies inside the area; spilling out is covering what is outside it
        if leader_index is not None:
            cost += leader_cost(cand, block, subject, leader_index, clear, own, text)
        if cost == 0.0:
            return _placement(cand, block, cost, subject)
        if best is None or cost < best[0]:
            best = (cost, order, cand, block)
    if best is None:  # every candidate left the frame: the caption still goes down (never dropped), at the first seat
        assert first is not None  # every subject kind yields at least one candidate
        return _placement(first[0], first[1], index.cost(first[1], clear, own, text, subject.civic), subject)
    cost, cand, block = nudge(best[0], best[2], best[3], subject, index, clear, own, text, frame, leader_index)
    return _placement(cand, block, cost, subject)


NUDGE_PX = 3
"""How far, in whole pixels each way, the least-cost seat is nudged for a cheaper one (feature 286): a free band exactly as
tall as a caption and its clearance - Hayakawa's guardroom - lies between any grid's points."""


def nudge(
    cost: float,
    cand: _Cand,
    block: Poly,
    subject: Subject,
    index: ObstacleIndex,
    clear: float,
    own: Poly | None,
    text: str,
    frame: tuple[float, float, float, float] | None,
    leader_index: ObstacleIndex | None,
) -> tuple[float, _Cand, Poly]:
    """The least-cost seat, or the cheapest one within `NUDGE_PX` of it in the caption's own frame - never a seat off
    the frame, never one that spills an area's name outside the area."""
    best = (cost, cand, block)
    for dx in range(-NUDGE_PX, NUDGE_PX + 1):
        for dy in range(-NUDGE_PX, NUDGE_PX + 1):
            if best[0] == 0.0:
                return best
            c = replace(cand, center=(cand.center[0] + dx, cand.center[1] + dy))
            b = rect(c.center[0], c.center[1], c.half[0], c.half[1], c.angle)
            bx0, by0, bx1, by1 = bbox(b)
            if frame is not None and (bx0 < frame[0] or by0 < frame[1] or bx1 > frame[2] or by1 > frame[3]):
                continue
            if subject.kind == "area" and not all(inside(p[0], p[1], subject.poly) for p in b):
                continue
            k = index.cost(b, clear, own, text, subject.civic)
            if leader_index is not None:
                k += leader_cost(c, b, subject, leader_index, clear, own, text)
            if k < best[0]:
                best = (k, c, b)
    return best


def leader_of(ring: int, block: Poly, subject: Subject) -> tuple[Pt, Pt] | None:
    """The leader a seat off the preferred offset draws: from the caption's block to the nearest point of what it names,
    trimmed a little at each end. None at ring 0 and for an area, whose name lies inside it."""
    if ring == 0 or subject.kind == "area":
        return None
    a, b = nearest_points(block, list(subject.poly), closed=subject.kind != "line")
    d = math.dist(a, b)
    trim = min(1.0, d / 4)
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return ((a[0] + ux * trim, a[1] + uy * trim), (b[0] - ux * trim, b[1] - uy * trim))


def leader_cost(c: _Cand, block: Poly, subject: Subject, index: ObstacleIndex, clear: float, own: Poly | None, text: str) -> float:
    """What a seat's leader line passes over or ends against, of the things `index` holds: a leader through another
    caption, or ending on a tub beside the feature it names, reads as naming the wrong thing (feature 283: Ochiba's
    RESIDENCE led through INNER COURT to a tub at the house's corner)."""
    seg = leader_of(c.ring, block, subject)
    if seg is None or math.dist(*seg) < 1e-6:
        return 0.0
    (ax, ay), (bx, by) = seg
    band = rect((ax + bx) / 2, (ay + by) / 2, math.dist(*seg) / 2, 0.5, math.degrees(math.atan2(by - ay, bx - ax)))
    return index.cost(band, clear, own, text, subject.civic)


def _placement(c: _Cand, block: Poly, cost: float, subject: Subject) -> Placement:
    leader = leader_of(c.ring, block, subject)
    return Placement(
        x=c.center[0],
        y=c.center[1] + CENTER_ABOVE_BASELINE_EM * c.size,
        angle=c.angle,
        lines=c.lines,
        block=tuple(block),
        ring=c.ring,
        rank=c.rank,
        position=c.position,
        cost=cost,
        leader=leader,
    )
