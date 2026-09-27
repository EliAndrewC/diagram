"""THE caption placer (feature 266): one for every caption, in both modes and on a hand-drawn sheet.

The GM, 2026-09-27: *"I also agree with one placer for all labels"*, adopting the cartographic standard
(research/presentation.html, "Where does a caption sit"). `place()` takes what a caption NAMES - a point feature's
drawn footprint, a line, or an area - and returns where the words go, at what angle, on how many lines, and whether a
leader line ties them back. The standard, in the order it decides:

1. NEARER FIRST (QGIS's default, "Prefer closer labels"): every candidate at the preferred offset - every ranked
   position, every line layout - is tried before any seat a ring further out.
2. Within a ring, the RANKED POSITIONS in the standard's order (upper right first; `standard.POSITIONS`), then fewer
   lines before more (the GM's wrap rule).
3. FREE SPACE WINS: the first candidate that covers nothing is taken. Only when nothing in reach is free does the
   caption go where it covers the least weight - it is never dropped (the GM: "we'll treat labels as mandatory").
4. A caption not at the preferred offset is no longer directly beside its feature, so a LEADER line joins it back
   (QGIS callouts, Esri's leader, PSU: "labels that do not fit on or directly adjacent to their respective feature").
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass

from .geom import Poly, Pt, area_centroid, bbox, centroid, inside, nearest_points, rect, seg_closest
from .layout import layouts
from .obstacles import ObstacleIndex
from .standard import CENTER_ABOVE_BASELINE_EM, CLEAR_EM, POSITIONS, PREFERRED_OFFSET_EM, REACH_EM, RING_STEP_EM, WEIGHT_OBSTACLE, block_half, upright

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


def rings(size: float) -> list[float]:
    """The ring distances for a caption of `size`: the preferred offset, then a step at a time out to the reach."""
    n = int(round((REACH_EM - PREFERRED_OFFSET_EM) / RING_STEP_EM)) + 1
    return [(PREFERRED_OFFSET_EM + k * RING_STEP_EM) * size for k in range(n)]


def _frame_of(angle: float) -> tuple[Pt, Pt]:
    a = math.radians(angle)
    return (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def _point_cands(text: str, size: float, subject: Subject, lays: list[list[str]]) -> Iterator[_Cand]:
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
                bw, bh = block_half(lines, size)
                if abs(sx) == 1.0 and sy:
                    # A CORNER: the block's near corner stands `g` from the subject's corner, along the diagonal.
                    du, dv = sx * (su + bw + g / math.sqrt(2)), sy * (sv + bh + g / math.sqrt(2))
                elif not sy:
                    du, dv = sx * (su + bw + g), 0.0
                else:
                    du, dv = sx * 2.0 * bw, sy * (sv + bh + g)
                yield _Cand(ring, rank, name, (c[0] + du * u[0] + dv * v[0], c[1] + du * u[1] + dv * v[1]), ang, tuple(lines), (bw, bh), size)


def _line_cands(text: str, size: float, subject: Subject, lays: list[list[str]]) -> Iterator[_Cand]:
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
                    bw, bh = block_half(lines, size)
                    d = subject.half_width + g + bh
                    yield _Cand(ring, j * 2 + (side > 0), name, (p[0] + side * d * v[0], p[1] + side * d * v[1]), ang, tuple(lines), (bw, bh), size)


def _area_cands(text: str, size: float, subject: Subject, lays: list[list[str]]) -> Iterator[_Cand]:
    ang = upright(subject.angle)
    c = area_centroid(subject.poly)
    x0, y0, x1, y1 = bbox(subject.poly)
    grid = [(x0 + i * size, y0 + j * size) for i in range(int((x1 - x0) / size) + 1) for j in range(int((y1 - y0) / size) + 1)]
    seats = [c] + sorted((p for p in grid if inside(p[0], p[1], subject.poly)), key=lambda p: math.dist(p, c))[: AREA_SEATS - 1]
    for rank, p in enumerate(seats):
        for lines in lays:
            yield _Cand(0, rank, "inside", p, ang, tuple(lines), block_half(lines, size), size)


def _cands(text: str, size: float, subject: Subject, lines: list[str] | None = None) -> Iterator[_Cand]:
    lays = [lines] if lines else layouts(text)
    if subject.kind == "point":
        return _point_cands(text, size, subject, lays)
    if subject.kind == "line":
        return _line_cands(text, size, subject, lays)
    if subject.kind == "area":
        return _area_cands(text, size, subject, lays)
    raise ValueError(f"a caption's subject is a point, a line or an area, not {subject.kind!r}")


def place(text: str, size: float, subject: Subject, index: ObstacleIndex, frame: tuple[float, float, float, float] | None = None, lines: list[str] | None = None) -> Placement:
    """Seat one caption by the standard (the module docstring). `frame` is the finished picture's (x0, y0, x1, y1); a
    block that leaves it is never a candidate, because a clipped caption cannot be read. `lines` fixes the caption's
    lines (a hand-drawn caption with a line of its own under it) instead of the wrap rule's layouts. Never returns
    nothing."""
    clear = CLEAR_EM * size
    own: Poly | None = list(subject.poly) if subject.kind != "line" else None
    best: tuple[float, int, _Cand, Poly] | None = None
    first: tuple[_Cand, Poly] | None = None
    for order, cand in enumerate(_cands(text, size, subject, lines)):
        block = rect(cand.center[0], cand.center[1], cand.half[0], cand.half[1], cand.angle)
        if first is None:
            first = (cand, block)
        bx0, by0, bx1, by1 = bbox(block)
        if frame is not None and (bx0 < frame[0] or by0 < frame[1] or bx1 > frame[2] or by1 > frame[3]):
            continue
        cost = index.cost(block, clear, own, text, subject.civic)
        if subject.kind == "area" and not all(inside(p[0], p[1], subject.poly) for p in block):
            cost += WEIGHT_OBSTACLE  # an area's name lies inside the area; spilling out is covering what is outside it
        if cost == 0.0:
            return _placement(cand, block, cost, subject)
        if best is None or cost < best[0]:
            best = (cost, order, cand, block)
    if best is None:  # every candidate left the frame: the caption still goes down (never dropped), at the first seat
        assert first is not None  # every subject kind yields at least one candidate
        return _placement(first[0], first[1], index.cost(first[1], clear, own, text, subject.civic), subject)
    return _placement(best[2], best[3], best[0], subject)


def _placement(c: _Cand, block: Poly, cost: float, subject: Subject) -> Placement:
    leader = None
    if c.ring > 0 and subject.kind != "area":
        a, b = nearest_points(block, list(subject.poly), closed=subject.kind != "line")
        d = math.dist(a, b)
        trim = min(1.0, d / 4)
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        leader = ((a[0] + ux * trim, a[1] + uy * trim), (b[0] - ux * trim, b[1] - uy * trim))
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
