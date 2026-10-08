"""THE caption placer (feature 266): one for every caption, in both modes and on a hand-drawn sheet.

The GM, 2026-09-27: *"I also agree with one placer for all labels"*, adopting the cartographic standard
(research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html). `place()` takes what a caption NAMES - a point feature's
drawn footprint, a line, or an area - and returns where the words go, at what angle, on how many lines, and whether a
leader line ties them back. The standard, in the order it decides:

1. NEARER FIRST (QGIS's default, "Prefer closer labels"): every candidate at the preferred offset - every ranked
   position, every line layout - is tried before any seat a ring further out.
2. Within a ring, the RANKED POSITIONS (`standard.POSITIONS`: the user-tested order of Bobák, Čmolík and Čadík 2024 -
   above, below, right, then the corners on the right, left, the corners on the left; feature 290), then fewer lines
   before more (the GM's wrap rule).
3. FREE SPACE WINS: the first candidate that covers nothing is taken. When nothing in reach is free, the fallback
   slides and then the leader rings out to the hug are searched; a caption is never dropped (the GM: "we'll treat
   labels as mandatory"), and with no free seat it goes down where it covers the least (0242) - never in a key (0241).
4. A caption not at the preferred offset is no longer directly beside its feature, so a LEADER line joins it back
   (QGIS callouts, Esri's leader, PSU: "labels that do not fit on or directly adjacent to their respective feature").

Research: caption search plumbing - NONE: candidate bookkeeping, geometry and search bounds
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from typing import Literal, overload

from .geom import Poly, Pt, area_centroid, bbox, centroid, inside, nearest_points, poly_gap, rect, seg_closest
from .layout import layouts
from .obstacles import ObstacleIndex, Way
from .standard import (
    CENTER_ABOVE_BASELINE_EM,
    CHAR_W_EM,
    CLEAR_EM,
    HUG_PX,
    LINE_H_EM,
    PITCH_EM,
    POSITIONS,
    PREFERRED_OFFSET_EM,
    REACH_EM,
    RING_STEP_EM,
    WEIGHT_OBSTACLE,
    block_half,
    upright,
)

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


NUDGE_PX = 3
"""How far, in whole pixels each way, the least-cost seat is nudged for a cheaper one (feature 286): a free band exactly as
tall as a caption and its clearance - Hayakawa's guardroom - lies between any grid's points."""

HUG_RING = HUG_PX - NUDGE_PX * math.sqrt(2.0)
"""The farthest ring any seat stands on (feature 287, labels L10): the hug less the farthest a nudge can carry a seat."""


def rings(size: float) -> list[float]:
    """The ring distances for a caption of `size`: the preferred offset, then a step at a time out to the reach - never
    past the hug (`HUG_RING`), whatever the caption's size.

    Research: nearer first - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the preferred offset, then a half em a ring out to the reach, never past the hug
    """
    n = int(round((REACH_EM - PREFERRED_OFFSET_EM) / RING_STEP_EM)) + 1
    return [min((PREFERRED_OFFSET_EM + k * RING_STEP_EM) * size, HUG_RING) for k in range(n) if k == 0 or (PREFERRED_OFFSET_EM + k * RING_STEP_EM) * size <= HUG_RING]


def outer_rings(size: float) -> list[tuple[int, float]]:
    """The LEADER rings (feature 287, D10): past the standard's reach, a step at a time out to the hug, each with its ring
    number - where a caption with no free seat in reach looks next, tied back by its leader, before it goes in the key.

    Research: leader rings - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: past the reach out to the hug, each seat tied back by a leader
    """
    k = len(rings(size))
    out: list[tuple[int, float]] = []
    while (PREFERRED_OFFSET_EM + k * RING_STEP_EM) * size <= HUG_RING:
        out.append((k, (PREFERRED_OFFSET_EM + k * RING_STEP_EM) * size))
        k += 1
    return out


def _frame_of(angle: float) -> tuple[Pt, Pt]:
    a = math.radians(angle)
    return (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def _ringed(size: float, ring_gaps: list[tuple[int, float]] | None) -> list[tuple[int, float]]:
    return list(enumerate(rings(size))) if ring_gaps is None else ring_gaps


def _box_frame(subject: Subject, ang: float) -> tuple[Pt, Pt, Pt, float, float]:
    """The subject's box in the frame turned by `ang`: its center, the frame's two axes and its half-extents."""
    u, v = _frame_of(ang)
    c = centroid(subject.poly)
    pu = [(p[0] - c[0]) * u[0] + (p[1] - c[1]) * u[1] for p in subject.poly]
    pv = [(p[0] - c[0]) * v[0] + (p[1] - c[1]) * v[1] for p in subject.poly]
    cu, cv = (min(pu) + max(pu)) / 2, (min(pv) + max(pv)) / 2
    c = (c[0] + cu * u[0] + cv * v[0], c[1] + cu * u[1] + cv * v[1])  # the center of the subject's box in its frame
    return c, u, v, (max(pu) - min(pu)) / 2, (max(pv) - min(pv)) / 2


def _point_cands(
    text: str, size: float, subject: Subject, lays: list[list[str]], char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None, ring_gaps: list[tuple[int, float]] | None = None
) -> Iterator[_Cand]:
    """Research: seats round a point - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the ranked positions in the feature's own turned frame, the gap from its drawn edge"""
    ang = upright(subject.angle)
    c, u, v, su, sv = _box_frame(subject, ang)
    for ring, g in _ringed(size, ring_gaps):
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


def _line_cands(
    text: str, size: float, subject: Subject, lays: list[list[str]], char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None, ring_gaps: list[tuple[int, float]] | None = None
) -> Iterator[_Cand]:
    """Seats along a line.

    Research:
        a line's caption - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: along the line at its bearing, above before below, never upside down
        stations along the line - NONE: two ems apart from the hint, a search bound
    """
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

    for ring, g in _ringed(size, ring_gaps):
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
    """Research: an area's caption - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: inside the area, its centroid first"""
    ang = upright(subject.angle)
    c = area_centroid(subject.poly)
    x0, y0, x1, y1 = bbox(subject.poly)
    grid = [(x0 + i * size, y0 + j * size) for i in range(int((x1 - x0) / size) + 1) for j in range(int((y1 - y0) / size) + 1)]
    seats = [c] + sorted((p for p in grid if inside(p[0], p[1], subject.poly)), key=lambda p: math.dist(p, c))[: AREA_SEATS - 1]
    for rank, p in enumerate(seats):
        for lines in lays:
            yield _Cand(0, rank, "inside", p, ang, tuple(lines), sized_half(lines, size, char_w, line_sizes), size)


def _extended_cands(
    text: str, size: float, subject: Subject, lines: list[str] | None = None, char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None, ring_gaps: list[tuple[int, float]] | None = None
) -> Iterator[_Cand]:
    """THE FALLBACK SEARCH (feature 286), tried only when the standard's candidates found no free seat: an area's inside
    sampled over its whole extent, the step set by its size rather than one em (a large court's free ground lay beyond
    the 400 seats nearest its centroid); round a point subject, the block slid along each side between the ranked
    positions, ring by ring. A line subject's stations already walk its length, so it adds nothing.

    Research: fallback seats - CONVENTION: slides between the ranked seats, and a finer grid inside an area, when none is free
    """
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
    c, u, v, su, sv = _box_frame(subject, ang)
    slides = [-1.0 + 2.0 * k / EXTENDED_SLIDES for k in range(EXTENDED_SLIDES + 1)]
    for ring, g in _ringed(size, ring_gaps):
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


def _cands(
    text: str, size: float, subject: Subject, lines: list[str] | None = None, char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None, ring_gaps: list[tuple[int, float]] | None = None
) -> Iterator[_Cand]:
    lays = [lines] if lines else layouts(text)
    sizes = line_sizes if lines else None  # per-line sizes hold only for fixed lines
    if subject.kind == "point":
        return _point_cands(text, size, subject, lays, char_w, sizes, ring_gaps)
    if subject.kind == "line":
        return _line_cands(text, size, subject, lays, char_w, sizes, ring_gaps)
    if subject.kind == "area":
        return _area_cands(text, size, subject, lays, char_w, sizes)
    raise ValueError(f"a caption's subject is a point, a line or an area, not {subject.kind!r}")


def _leader_cands(text: str, size: float, subject: Subject, lines: list[str] | None = None, char_w: float = CHAR_W_EM, line_sizes: list[float] | None = None) -> Iterator[_Cand]:
    """THE LEADER SEARCH (feature 287, D10), tried only when nothing in the standard's reach is free: the standard's
    positions and the fallback's slides on the rings past the reach, out to the hug (`outer_rings`), every seat tied back
    by its leader. An area's name lies inside it, so it adds nothing for an area.

    Research: leader search - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a displaced caption tied to its feature by a leader line
    """
    outer = outer_rings(size)
    if not outer or subject.kind == "area":
        return
    lays = [lines] if lines else layouts(text)
    sizes = line_sizes if lines else None
    if subject.kind == "line":
        yield from _line_cands(text, size, subject, lays, char_w, sizes, outer)
        return
    yield from _point_cands(text, size, subject, lays, char_w, sizes, outer)
    yield from _extended_cands(text, size, subject, lines, char_w, line_sizes, outer)


def referent_box(subject: Subject, block: Poly | tuple[Pt, ...]) -> tuple[float, float, float, float]:
    """The box of what a caption names, as its record carries it (element [6]): a point subject's UNROTATED box - its
    extents in its own frame, about its center (`_record_label`'s note: it keeps the hug conservative) - an area's box,
    or for a LINE the drawn way's width across from where the caption landed."""
    if subject.kind == "point":
        a = math.radians(subject.angle)
        u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        c = centroid(subject.poly)
        su = max(abs((q[0] - c[0]) * u[0] + (q[1] - c[1]) * u[1]) for q in subject.poly)
        sv = max(abs((q[0] - c[0]) * v[0] + (q[1] - c[1]) * v[1]) for q in subject.poly)
        return (c[0] - su, c[1] - sv, c[0] + su, c[1] + sv)
    if subject.kind == "area":
        return bbox(subject.poly)
    cx, cy = centroid(block)
    pts = list(subject.poly)
    q = min((seg_closest((cx, cy), a, b) for a, b in zip(pts, pts[1:], strict=False)), key=lambda c: math.dist(c, (cx, cy)))
    h = subject.half_width
    return (q[0] - h, q[1] - h, q[0] + h, q[1] + h)


def record_box(block: Poly | tuple[Pt, ...]) -> tuple[float, float, float, float]:
    """A drawn block's record box - the block unturned about its own center, as `_record_label` writes elements [0:4]."""
    cx, cy = centroid(block)
    hw, hh = math.dist(block[0], block[1]) / 2, math.dist(block[1], block[2]) / 2
    return (cx - hw, cy - hh, cx + hw, cy + hh)


def hug_gap(block: Poly | tuple[Pt, ...], ref: tuple[float, float, float, float]) -> float:
    """THE ONE PREDICATE of `label_hugs_its_referent` (feature 287, labels L10): the box-to-box gap between a caption's
    record box and the box of what it names. The placer never offers a seat past `HUG_PX` by it."""
    a = record_box(block)
    return math.hypot(max(a[0] - ref[2], ref[0] - a[2], 0.0), max(a[1] - ref[3], ref[1] - a[3], 0.0))


def caption_clears_ways(block: Poly | tuple[Pt, ...], ways: list[Way]) -> bool:
    """THE ONE PREDICATE of `captions_clear_the_ways_they_stand_on` (feature 287, labels L5): no way comes within its drawn
    half-width plus `WAY_NOTCH` of the block, segment against polygon - the index's own way term, so a curved tread's
    middle crossing an edge between the block's corners is not missed."""
    return ObstacleIndex(ways=ways).cost(list(block), 0.0) == 0.0


Frame = tuple[float, float, float, float]


@overload
def place(
    text: str,
    size: float,
    subject: Subject,
    index: ObstacleIndex,
    frame: Frame | None = None,
    lines: list[str] | None = None,
    char_w: float = CHAR_W_EM,
    leader_index: ObstacleIndex | None = None,
    line_sizes: list[float] | None = None,
    extended: bool = True,
    *,
    strict: Literal[False] = False,
    max_ring: int | None = None,
    accept: Callable[[Placement], bool] | None = None,
) -> Placement: ...


@overload
def place(
    text: str,
    size: float,
    subject: Subject,
    index: ObstacleIndex,
    frame: Frame | None = None,
    lines: list[str] | None = None,
    char_w: float = CHAR_W_EM,
    leader_index: ObstacleIndex | None = None,
    line_sizes: list[float] | None = None,
    extended: bool = True,
    *,
    strict: Literal[True],
    max_ring: int | None = None,
    accept: Callable[[Placement], bool] | None = None,
) -> Placement | None: ...


def place(
    text: str,
    size: float,
    subject: Subject,
    index: ObstacleIndex,
    frame: Frame | None = None,
    lines: list[str] | None = None,
    char_w: float = CHAR_W_EM,
    leader_index: ObstacleIndex | None = None,
    line_sizes: list[float] | None = None,
    extended: bool = True,
    *,
    strict: bool = False,
    max_ring: int | None = None,
    accept: Callable[[Placement], bool] | None = None,
) -> Placement | None:
    """Seat one caption by the standard (the module docstring). `frame` is the finished picture's (x0, y0, x1, y1); a
    block that leaves it is never a candidate, because a clipped caption cannot be read. `lines` fixes the caption's
    lines (a hand-drawn caption with a line of its own under it) instead of the wrap rule's layouts. `char_w` is the
    caption's width per character in ems - the standard's for the engine's own captions; a hand sheet's bold, capital or
    letter-spaced caption runs wider (feature 267: `labels/hand_sheet.py` measures it). `line_sizes` gives each fixed
    line its own size (a name over a smaller gloss). `leader_index` holds what a seat's leader line may not pass over or
    end against - the other captions and the small glyphs, which a hand sheet supplies (feature 283).

    WHEN NO STANDARD SEAT IS FREE (features 286, 287): the fallback search (`_extended_cands`), then the leader rings past
    the reach out to the hug (`_leader_cands`). A seat covering only `soft` ink (a hand sheet's) is then taken at the
    least cost; a caption whose every seat overlaps goes down where it covers the least (0242), and one with no seat in the
    frame at all takes the first seat beside it past the frame's edge. Never dropped, never in a key (0241), never past the hug
    (`HUG_PX`).

    `strict=True` returns None instead of anything but a free seat (feature 287: the notice board's siter and the
    generated Mode A sheets ask it, and choose the SUBJECT or the program instead). The retired least-cost seat's last
    caller, the board with no clean verge (D12, a preference since the GM's 2026-09-30 ruling), takes this non-strict path. `max_ring` keeps
    only the seats on rings up to it (0: directly beside the subject, no leader - the notice board's caption).

    `accept` is asked of every free candidate before it is returned, and of the strict search's nudged seat - a strict
    search's every answer, so only a strict caller passes it - and a seat it refuses is passed over as if it were not
    free (feature 287, labels L6: the board's siter asks whether the caption stands nearest its board AS IT WILL BE
    RECORDED, `board_seat.board_caption_seat`). The search then goes on to the next seat, so a refused seat costs the
    caption no seat another would have given it.

    Research:
        free space wins - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: the first seat covering nothing is taken
        never clipped - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a seat leaving the picture is never a candidate
        never left off - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: with no free seat, the seat covering the least - soft ink first, then whatever it covers
        no key - research/questions/0241-the-map-sheet-its-title-legend-frame-and-margins.drawing.html: there is no key box; a caption with no seat in the frame takes the first seat beside it past the frame's edge
        the hug - CONVENTION: no seat past the hug from what it names
    """
    clear = CLEAR_EM * size
    own: Poly | None = list(subject.poly) if subject.kind != "line" else None
    point = subject.kind == "point"
    ref = referent_box(subject, subject.poly) if point else None
    best: tuple[float, int, _Cand, Poly] | None = None
    soft: tuple[float, int, _Cand, Poly] | None = None
    # the standard's candidates, then - reached only when none was free, the chain being lazy - the fallback search
    # (feature 286) and the leader rings (feature 287)
    # `max_ring` generates only the rings up to it - the rings past it are never offered, so they are never built
    near = None if max_ring is None else list(enumerate(rings(size)))[: max_ring + 1]
    leaders = _leader_cands(text, size, subject, lines, char_w, line_sizes) if max_ring is None else iter(())
    more = itertools.chain(_extended_cands(text, size, subject, lines, char_w, line_sizes, near), leaders) if extended else iter(())
    deep: list[tuple[int, _Cand, Poly]] = []  # strict: the seats no nudge can free, measured only if one might be the best
    outside: tuple[_Cand, Poly] | None = None  # the first seat beside the subject that leaves the frame, for a frame that holds none
    for order, cand in enumerate(itertools.chain(_cands(text, size, subject, lines, char_w, line_sizes, near), more)):
        block = rect(cand.center[0], cand.center[1], cand.half[0], cand.half[1], cand.angle)
        # the hug is held with the nudge's room to spare, so no nudge can carry a seat past it (labels L10)
        if subject.kind != "area" and hug_gap(block, ref or referent_box(subject, block)) > HUG_RING:
            continue
        if not _in_frame(block, frame):
            outside = outside or (cand, block)
            continue
        if strict and index.blocked(block, clear, NUDGE_REACH, own, text, subject.civic):
            deep.append((order, cand, block))
            continue
        cost, hard = _score(cand, block, subject, index, clear, own, text, leader_index)
        if cost == 0.0:
            free = _placement(cand, block, cost, subject)
            if accept is None or accept(free):
                return free
            continue
        if best is None or cost < best[0]:
            best = (cost, order, cand, block)
        if not hard and (soft is None or cost < soft[0]):
            soft = (cost, order, cand, block)
    if strict:
        got = _strict_seat(best, deep, subject, index, clear, own, text, frame, leader_index)
        return got if got is None or accept is None or accept(got) else None
    if best is not None:
        # a nudge may yet free the least-cost seat, or carry it off every overlap (feature 286's band between grid points)
        cost, cand, block = nudge(best[0], best[2], best[3], subject, index, clear, own, text, frame, leader_index)
        if (cost == 0.0 or not _score(cand, block, subject, index, clear, own, text, leader_index)[1]) and (soft is None or cost <= soft[0]):
            return _placement(cand, block, cost, subject)
    if soft is not None:
        cost, cand, block = nudge(soft[0], soft[2], soft[3], subject, index, clear, own, text, frame, leader_index, soft_only=True)
        return _placement(cand, block, cost, subject)
    if best is not None:
        # ...AND WITH NO FREE GROUND AT ALL, THE SEAT COVERING THE LEAST, whatever it covers (feature 328 wave 49, 0242's
        # drawing page: "On a sheet with no free ground at all, the caption still goes down, where it covers the least"; an
        # exception keeping feature 287's key for an all-hard seat ruled NOT LEGITIMATE - 0241: "There is no key box")
        cost, cand, block = nudge(best[0], best[2], best[3], subject, index, clear, own, text, frame, leader_index)
        return _placement(cand, block, cost, subject)
    # ...AND WITH NO SEAT INSIDE THE FRAME AT ALL, the first seat beside it past the frame's edge: never left off (0242)
    assert outside is not None, "the standard offers a seat beside every subject"
    return _placement(outside[0], outside[1], _score(outside[0], outside[1], subject, index, clear, own, text, leader_index)[0], subject)


NUDGE_REACH = NUDGE_PX * math.sqrt(2.0) + 1e-3
"""The farthest a nudge carries a seat, with a margin over rounding: a seat blocked by more than this stays blocked
under every nudge (`ObstacleIndex.blocked`)."""


def _strict_seat(
    best: tuple[float, int, _Cand, Poly] | None,
    deep: list[tuple[int, _Cand, Poly]],
    subject: Subject,
    index: ObstacleIndex,
    clear: float,
    own: Poly | None,
    text: str,
    frame: Frame | None,
    leader_index: ObstacleIndex | None,
) -> Placement | None:
    """A strict search's answer once no candidate was free: the least-cost seat nudged free, or None. THE SAME ANSWER AS
    MEASURING EVERY SEAT (feature 287, the board's siting): a seat `blocked` beyond a nudge's reach can be neither free nor
    nudged free, so where every seat is, the answer is None unmeasured; otherwise those seats are measured now, since
    one may still be the least-cost seat the nudge starts from (the first in order among the cheapest)."""
    if best is None:
        return None
    for order, cand, block in deep:
        cost = _score(cand, block, subject, index, clear, own, text, leader_index)[0]
        if (cost, order) < best[:2]:
            best = (cost, order, cand, block)
    if any(best[1] == order for order, _c, _b in deep):
        return None
    cost, cand, block = nudge(best[0], best[2], best[3], subject, index, clear, own, text, frame, leader_index)
    return _placement(cand, block, cost, subject) if cost == 0.0 else None


def _in_frame(block: Poly, frame: tuple[float, float, float, float] | None) -> bool:
    if frame is None:
        return True
    bx0, by0, bx1, by1 = bbox(block)
    return not (bx0 < frame[0] or by0 < frame[1] or bx1 > frame[2] or by1 > frame[3])


def _score(c: _Cand, block: Poly, subject: Subject, index: ObstacleIndex, clear: float, own: Poly | None, text: str, leader_index: ObstacleIndex | None) -> tuple[float, bool]:
    """A seat's weight and whether it overlaps: what the block covers (with the association term for a point subject's
    seat beside it), an area's name spilling out of the area, and what its leader passes over.

    THE ASSOCIATION TERM IS ASKED OF A SEAT WITH NO LEADER (feature 287, labels L6). The design asked it of every ring,
    and it cannot be: a ring-k block in a position whose ring-0 block an obstacle blocked stands within that obstacle's
    gap plus the ring's step of it - under `clear + (g_k - g_0) = g_k`, its own gap - so every leader seat would be
    refused and a caption with a leader could only go in the key. A leader carries the association itself (QGIS's
    callouts, Esri's leaders: the line ties the words to their feature), so the term holds where the words alone must.

    Research:
        association beside a point - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: asked of a seat with no leader
        an area's name inside it - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: spilling out costs an obstacle
    """
    og = poly_gap(block, list(subject.poly)) if subject.kind == "point" and c.ring == 0 else None
    cost, hard = index.score(block, clear, own, text, subject.civic, og)
    if subject.kind == "area" and not all(inside(p[0], p[1], subject.poly) for p in block):
        cost, hard = cost + WEIGHT_OBSTACLE, True  # an area's name lies inside the area; spilling out is covering what is outside it
    if leader_index is not None:
        lc, lh = leader_score(c, block, subject, leader_index, clear, own, text)
        cost, hard = cost + lc, hard or lh
    return cost, hard


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
    soft_only: bool = False,
) -> tuple[float, _Cand, Poly]:
    """The least-cost seat, or the cheapest one within `NUDGE_PX` of it in the caption's own frame - never a seat off
    the frame, never one that spills an area's name outside the area, and with `soft_only` never one that overlaps."""
    best = (cost, cand, block)
    for dx in range(-NUDGE_PX, NUDGE_PX + 1):
        for dy in range(-NUDGE_PX, NUDGE_PX + 1):
            if best[0] == 0.0:
                return best
            c = replace(cand, center=(cand.center[0] + dx, cand.center[1] + dy))
            b = rect(c.center[0], c.center[1], c.half[0], c.half[1], c.angle)
            if not _in_frame(b, frame):
                continue
            if subject.kind == "area" and not all(inside(p[0], p[1], subject.poly) for p in b):
                continue
            k, hard = _score(c, b, subject, index, clear, own, text, leader_index)
            if k < best[0] and not (soft_only and hard):
                best = (k, c, b)
    return best


LEADERLESS_RINGS = int(round((2 * PREFERRED_OFFSET_EM - PREFERRED_OFFSET_EM) / RING_STEP_EM)) + 1
"""The rings a caption takes with no leader: the preferred offset and each step out to twice it (rings 0 and 1, 1 em).

Research: no leader within twice the usual gap - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: it may go as far as twice the usual gap with nothing more"""


def leader_of(ring: int, block: Poly, subject: Subject) -> tuple[Pt, Pt] | None:
    """The leader a seat past twice the usual gap draws: from the caption's block to the nearest point of what it names,
    trimmed a little at each end. None within `LEADERLESS_RINGS` (the preferred offset and the step out from it, out to twice
    the usual gap) and for an area, whose name lies inside it.

    Research: when a leader is drawn - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption more than twice the usual gap from its feature is tied to it by a thin leader line, to the nearest point of the feature
    """
    if ring < LEADERLESS_RINGS or subject.kind == "area":
        return None
    a, b = nearest_points(block, list(subject.poly), closed=subject.kind != "line")
    d = math.dist(a, b)
    trim = min(1.0, d / 4)
    ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
    return ((a[0] + ux * trim, a[1] + uy * trim), (b[0] - ux * trim, b[1] - uy * trim))


def leader_cost(c: _Cand, block: Poly, subject: Subject, index: ObstacleIndex, clear: float, own: Poly | None, text: str) -> float:
    """What a seat's leader line passes over or ends against (`leader_score`'s weight)."""
    return leader_score(c, block, subject, index, clear, own, text)[0]


def leader_score(c: _Cand, block: Poly, subject: Subject, index: ObstacleIndex, clear: float, own: Poly | None, text: str) -> tuple[float, bool]:
    """What a seat's leader line passes over or ends against, of the things `index` holds, and whether that is an
    overlap: a leader through another caption, or ending on a tub beside the feature it names, reads as naming the wrong
    thing (feature 283: Ochiba's RESIDENCE led through INNER COURT to a tub at the house's corner).

    Research: leader keeps clear - CONVENTION: a leader through a caption or ending on a small glyph counts as covering it
    """
    seg = leader_of(c.ring, block, subject)
    if seg is None or math.dist(*seg) < 1e-6:
        return 0.0, False
    (ax, ay), (bx, by) = seg
    band = rect((ax + bx) / 2, (ay + by) / 2, math.dist(*seg) / 2, 0.5, math.degrees(math.atan2(by - ay, bx - ax)))
    return index.score(band, clear, own, text, subject.civic)


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
