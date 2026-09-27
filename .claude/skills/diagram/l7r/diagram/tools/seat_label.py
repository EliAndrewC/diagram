"""`make seat-label` - the ONE placer (feature 266) run on a hand-drawn Mode A sheet.

A hand-drawn sheet's SVG is its source: a session writes every caption by hand. This tool reads the sheet's drawn
shapes, classifies each by its `data-kind` tag (feature 262 tagged every drawn element), finds each caption's subject
- the non-text shapes of the caption's own kind - and asks `l7r.diagram.labels.place` where the caption goes. With
`--check` it lists every caption not at its standard seat, and every leader that is missing, stray or misplaced; with
`--write` it rewrites them in place. The rule for hand-drawn sheets (buildings.md, and the building-review contract):
every caption is seated with this tool, and revising a sheet re-seats all of its captions.

The classification (spec plan P4): the way kinds are ways (500 a way crossed), the ground kinds are free space, the
one `-` shape covering the whole view is the background (free), and everything else - every other `-` shape, every
`<text>` whatever its tag, `court divider`, `weighing floor` - is an obstacle (1,000).

Feature 267 weighed ink as a reader meets it (`classify`): another caption 10,000, dark ink 2,000, anything painted
after a caption as much as a caption (it hides it), ink inside what a caption names in full (`Obstacle.inner`) - except
ground nested in the ground it names and ink the sheet marks `data-texture="1"` (a feature's surface, a wing's shutter
marks), both light (250) - a ground's drawn border, and an area's own outline; the building holding a named room is
waived. A caption's own seat is kept only where it covers strictly less than the standard's pick.

    make seat-label SHEET=pool/<tier>/<map>/<map>.svg
"""

from __future__ import annotations

import argparse
import hashlib
import html
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, replace
from pathlib import Path

from l7r.diagram.labels import Obstacle, ObstacleIndex, Placement, Subject, Way, place
from l7r.diagram.labels.geom import Poly, Pt, bbox, inside, rect
from l7r.diagram.labels.standard import CENTER_ABOVE_BASELINE_EM, CHAR_W_EM, CLEAR_EM, PITCH_EM, WEIGHT_OBSTACLE, WEIGHT_WAY, block_half
from l7r.diagram.labels.svg import caption_svg, leader_svg

SVG = "{http://www.w3.org/2000/svg}"

WAY_KINDS = frozenset({"road", "river", "revetment"})
"""The kinds a caption may cross at a way's weight (plan P4, observed 2026-09-27, method: the tag census of the six
sheets - roads are stroked paths 18 to 40 px wide)."""

GROUND_KINDS = frozenset({"outer court", "inner court", "border court", "practice ground", "garden", "vegetable garden", "garden pines", "cart yard", "shrine grove", "river landing"})
"""The sheets' open ground - free space to a caption (plan P4). An explicit list: a name that merely CONTAINS "court"
is not ground (`court divider` is a wall), and a roofed floor on posts (`weighing floor`) is built - as the hearing court
is since feature 267 roofed it (research buildings 450), so another caption no longer takes its floor as open ground."""

WEIGHT_INNER = WEIGHT_OBSTACLE / 4
"""What ground nested inside the ground a caption names costs (feature 267): a court's name takes the court's own open
earth before a garden inside it, and a garden before a building."""

WEIGHT_DARK = 2 * WEIGHT_OBSTACLE
"""What covering dark ink costs - a wall, a post, a dark roof (feature 267): black caption ink cannot be read on it,
where on light ink it can, so a caption with no free seat takes light ink first. At one weight Hayakawa's practice
ground's name, with no free seat in its ground, lay across the compound wall."""

DARK = 0.3
"""Ink this dark (0-1 luma) or darker is dark to a caption."""

WEIGHT_TEXT = 10 * WEIGHT_OBSTACLE


"""What covering another caption costs: ten drawn obstacles (feature 267). A caption with no free seat falls back to the
least cost, and at one weight for all ink it chose a seat on Ubame's border name over one on the parley room's own
mats - words on words are the one overlap a reader cannot see past."""

ELONGATED = 3.0

"""How much taller than wide an area is before its name runs along it (a calibration: the river band is ~7x)."""

TOLERANCE = 1.0

"""How far a caption may stand from its standard seat and still be at it, in px - rounding in a hand-written sheet
(spec D4a, a calibration)."""

Affine = tuple[float, float, float, float, float, float]
IDENTITY: Affine = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _mul(m: Affine, n: Affine) -> Affine:
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2, a * e2 + c * f2 + e, b * e2 + d * f2 + f)


def parse_transform(t: str | None) -> Affine:
    """An SVG `transform` list as one affine matrix: translate, rotate (about a point too), scale and matrix."""
    m = IDENTITY
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", t or ""):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "translate":
            m = _mul(m, (1.0, 0.0, 0.0, 1.0, v[0], v[1] if len(v) > 1 else 0.0))
        elif name == "scale":
            m = _mul(m, (v[0], 0.0, 0.0, v[1] if len(v) > 1 else v[0], 0.0, 0.0))
        elif name == "rotate":
            a = math.radians(v[0])
            r: Affine = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0.0, 0.0)
            if len(v) == 3:
                r = _mul(_mul((1.0, 0.0, 0.0, 1.0, v[1], v[2]), r), (1.0, 0.0, 0.0, 1.0, -v[1], -v[2]))
            m = _mul(m, r)
        elif name == "matrix":
            m = _mul(m, (v[0], v[1], v[2], v[3], v[4], v[5]))
    return m


def _inverse(m: Affine) -> Affine:
    """The matrix that undoes `m` (an SVG transform is always invertible when anything is drawn through it)."""
    a, b, c, d, e, f = m
    det = a * d - b * c
    return (d / det, -b / det, -c / det, a / det, (c * f - d * e) / det, (b * e - a * f) / det)


def _apply(m: Affine, p: Pt) -> Pt:
    return m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]


def _angle(m: Affine) -> float:
    return math.degrees(math.atan2(m[1], m[0]))


def _f(el: ET.Element, name: str, default: float = 0.0) -> float:
    v = el.get(name)
    try:
        return float(v) if v is not None else default
    except ValueError:
        return default


@dataclass
class Shape:
    """One drawn element, in sheet coordinates: its kind, its outline (or its polyline and stroke half-width), and for a
    `<text>` the caption it carries."""

    tag: str
    kind: str
    poly: Poly
    half: float = 0.0
    line: bool = False
    text: str = ""
    size: float = 0.0
    angle: float = 0.0
    element: ET.Element | None = None
    leader: bool = False
    center: Pt = (0.0, 0.0)
    lines: list[str] = field(default_factory=list)
    group: int = 0
    frame: Affine = IDENTITY  # a text's PARENT matrix (its groups' transforms, not its own) - the frame a rewrite writes in
    within: frozenset[int] = frozenset()  # every tagged group the element sits inside, its own included
    edge: float = 0.0  # a closed shape's drawn outline half-width (0 when it has none)
    texture: bool = False  # marked `data-texture` on the sheet: ink that is a feature's surface (a wing's shutter marks), not its parts
    filled: bool = False  # a closed shape painted with a fill (SVG's default fill is black), which hides what is under it
    dark: bool = False  # drawn in dark ink - a line's stroke, a shape's fill - which black caption ink cannot be read on


def _path_points(d: str) -> list[Pt]:
    """A path's vertices - absolute and relative move, line, horizontal and vertical steps, and the end points of
    curves; enough for the handful of paths the sheets draw (roads and banks)."""
    pts: list[Pt] = []
    x = y = 0.0
    for cmd, args in re.findall(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)", d):
        v = [float(n) for n in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        step = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7}.get(cmd.upper(), 0)
        for i in range(0, len(v) - step + 1, step) if step else ():
            chunk = v[i : i + step]
            rel = cmd.islower()
            if cmd.upper() == "H":
                x = x + chunk[0] if rel else chunk[0]
            elif cmd.upper() == "V":
                y = y + chunk[0] if rel else chunk[0]
            else:
                ex, ey = chunk[-2], chunk[-1]
                x, y = (x + ex, y + ey) if rel else (ex, ey)
            pts.append((x, y))
    return pts


def read_sheet(src: str) -> tuple[list[Shape], tuple[float, float, float, float]]:
    """Every drawn element of a sheet as a Shape, and the sheet's view (x0, y0, x1, y1)."""
    root = ET.fromstring(src)
    vb = [float(v) for v in re.split(r"[\s,]+", (root.get("viewBox") or "0 0 0 0").strip())]
    view = (vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3])
    shapes: list[Shape] = []

    def walk(el: ET.Element, m: Affine, kind: str, stroke_w: float, stroked: bool, group: int, within: frozenset[int] = frozenset(), ink: tuple[str, str] = ("", ""), texture: bool = False) -> None:
        parent = m
        m = _mul(m, parse_transform(el.get("transform")))
        if el.get("data-kind") is not None:
            kind, group = el.get("data-kind", kind), id(el)  # the tagged element a caption and its subject share
            within = within | {group}
        stroke_w = _f(el, "stroke-width", stroke_w)
        if el.get("stroke") is not None:
            stroked = el.get("stroke") != "none"
        ink = (el.get("stroke", ink[0]), el.get("fill", ink[1]))  # (stroke, fill), inherited as SVG inherits them
        texture = texture or el.get("data-texture") == "1"

        tag = el.tag.replace(SVG, "")
        pts: list[Pt] = []
        line = False
        if tag == "rect":
            x, y, w, h = _f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height")
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        elif tag in ("circle", "ellipse"):
            cx, cy = _f(el, "cx"), _f(el, "cy")
            rx, ry = (_f(el, "r"), _f(el, "r")) if tag == "circle" else (_f(el, "rx"), _f(el, "ry"))
            pts = [(cx - rx, cy - ry), (cx + rx, cy - ry), (cx + rx, cy + ry), (cx - rx, cy + ry)]
        elif tag in ("polygon", "polyline"):
            v = [float(n) for n in re.findall(r"-?\d*\.?\d+", el.get("points", ""))]
            pts = list(zip(v[0::2], v[1::2], strict=False))
            line = tag == "polyline" and el.get("fill", "none") == "none"
        elif tag == "line":
            pts = [(_f(el, "x1"), _f(el, "y1")), (_f(el, "x2"), _f(el, "y2"))]
            line = True
        elif tag == "path":
            pts = _path_points(el.get("d", ""))
            line = stroked and el.get("fill", "") == "none"
        elif tag == "text":
            t = _text_shape(el, m, kind)
            t.frame = parent
            t.group = group
            t.within = within
            shapes.append(t)
            return
        if len(pts) >= 2:
            tp = [_apply(m, p) for p in pts]
            if line:
                shapes.append(Shape(tag, kind, tp, stroke_w / 2, True, element=el, leader=el.get("data-leader") == "1", group=group, within=within, dark=_luma(ink[0]) < DARK, texture=texture))
            else:
                x0, y0, x1, y1 = bbox(tp)
                edge = stroke_w / 2 if stroked else 0.0

                shapes.append(
                    Shape(
                        tag,
                        kind,
                        tp if len(tp) >= 3 else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                        element=el,
                        group=group,
                        within=within,
                        edge=edge,
                        filled=ink[1] != "none",
                        dark=_luma(ink[1]) < DARK,
                        texture=texture,
                    )
                )
        for c in el:
            walk(c, m, kind, stroke_w, stroked, group, within, ink, texture)

    for c in root:
        walk(c, IDENTITY, "", 1.0, False, 0)
    return shapes, view


def _text_shape(el: ET.Element, m: Affine, kind: str) -> Shape:
    size = _f(el, "font-size", 12.0)
    spans = [t for t in el.iter(f"{SVG}tspan")]
    lines = [(t.text or "").strip() for t in spans] if spans else [(el.text or "").strip()]
    lines = [ln for ln in lines if ln] or [""]
    x, y = _f(el, "x"), _f(el, "y")
    anchor = el.get("text-anchor", "start")
    bw, bh = block_half(lines, size, char_w_of(el, " ".join(lines), size))
    pitch = PITCH_EM * size
    cx = x if anchor == "middle" else (x - bw if anchor == "end" else x + bw)
    cy = y + (len(lines) - 1) * pitch / 2 - CENTER_ABOVE_BASELINE_EM * size
    c = _apply(m, (cx, cy))
    ang = _angle(m)
    return Shape("text", kind, rect(c[0], c[1], bw, bh, ang), text=" ".join(lines), size=size, angle=ang, element=el, center=c, lines=lines)


def _is_background(s: Shape, view: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = bbox(s.poly)
    return s.kind == "-" and s.tag == "rect" and x0 <= view[0] and y0 <= view[1] and x1 >= view[2] and y1 >= view[3]


def classify(
    shapes: list[Shape],
    view: tuple[float, float, float, float],
    skip: set[int] = frozenset(),
    after: int | None = None,
    group: int = 0,
    kind: str = "",
    subject: Poly | None = None,
    area: bool = False,
) -> ObstacleIndex:  # type: ignore[assignment]
    """The sheet as the placer sees it (plan P4). `skip` holds the captions being placed, which are not obstacles to
    themselves. With `after` (a caption's own index), a GROUND shape drawn LATER in the document - outside the caption's
    own `group` - is an obstacle too: a hand sheet keeps each caption where it stands in the document, so ground painted
    after it covers it (feature 267: the Inari shrine's name seated on the vegetable garden showed only its last letter)."""
    obstacles: list[Obstacle] = []
    ways: list[Way] = []
    for i, s in enumerate(shapes):
        if i in skip or s.leader:
            continue
        # ink INSIDE what the caption names is ink it must avoid (`Obstacle.inner`): the placer's standard waives a
        # subject's own parts, and on a hand sheet those are partitions, mats, stepping stones and a court's buildings -
        # a name was seated through a bay partition and under a mat drawn after it (feature 267). The caption's own
        # feature's ink drawn BEFORE it weighs light (a shuttered wing's name has nowhere else to go); anything drawn
        # after it, or of another kind, weighs in full
        within = subject is not None and s.tag != "text" and _box_within(s.poly, subject) and not _same_box(s.poly, subject)
        if within and not _is_background(s, view):
            # ground nested in the ground it names weighs light (a garden in a court: Ubame's INNER COURT went to the
            # kitchen garden, open ground inside the court), and so does ink the sheet marks `data-texture` - a
            # feature's surface, a wing's shutter marks, which a name may lie on; everything else in full - the caption's
            # own partitions too, which at a light weight lost to its building's outline and put Ubame's servants'
            # quarters on one (round 4)
            light = (s.kind in GROUND_KINDS and s.kind != kind) or s.texture

            weight = WEIGHT_INNER if light else WEIGHT_TEXT if after is not None and i > after and s.filled and not s.line else WEIGHT_OBSTACLE
            bands = [_band(a, b, max(s.half, 0.5)) for a, b in zip(s.poly, s.poly[1:], strict=False)] if s.line else [s.poly]
            obstacles += [Obstacle(tuple(b), weight, inner=True) for b in bands]
            continue
        if area and subject is not None and s.tag != "text" and not s.line and _box_within(subject, s.poly) and not (after is not None and i > after and s.filled):
            # the area itself, or the building that holds the room an `area` caption names: the name is inside it by
            # necessity (a guardroom's in its range) - but not on its drawn outline, which a name set against it runs
            # into (Hayakawa's HEARING COURT and Hajime's quarters against their walls, feature 267 round 4)
            if s.edge:
                ring = [*s.poly, s.poly[0]]
                obstacles += [Obstacle(tuple(_band(a, b, s.edge)), WEIGHT_OBSTACLE, inner=True) for a, b in zip(ring, ring[1:], strict=False)]
            continue

        if s.tag == "text":
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_TEXT))
        elif after is not None and i > after and s.filled and not s.line and not _is_background(s, view):
            # painted OVER the caption, which a hand sheet keeps where it stands in the document: it hides the name as
            # surely as another name would (Hayakawa's weapon rack under the granary, feature 267)
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_TEXT))

        elif s.kind in GROUND_KINDS or _is_background(s, view):
            # a ground's drawn border is ink even where its floor is free space (Ochiba's RESIDENCE on the vegetable
            # garden's dashed edge, feature 267); the border of the ground a caption names is its own, and waived
            if s.edge and not _is_background(s, view) and not (subject is not None and _same_box(s.poly, subject)):
                ring = [*s.poly, s.poly[0]]
                obstacles += [Obstacle(tuple(_band(a, b, s.edge)), WEIGHT_OBSTACLE) for a, b in zip(ring, ring[1:], strict=False)]
            continue
        elif s.kind in WAY_KINDS:
            if s.line:
                ways.append(Way(tuple(s.poly), max(s.half, 0.5)))
            else:
                obstacles.append(Obstacle(tuple(s.poly), WEIGHT_WAY))
        elif s.line:
            for a, b in zip(s.poly, s.poly[1:], strict=False):
                obstacles.append(Obstacle(tuple(_band(a, b, max(s.half, 0.5))), WEIGHT_DARK if s.dark else WEIGHT_OBSTACLE))
        else:
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_DARK if s.dark else WEIGHT_OBSTACLE))
    return ObstacleIndex(obstacles, ways)


def _same_box(a: Poly, b: Poly, tol: float = 1.0) -> bool:
    """Do two outlines share a box (within `tol`) - a shape that IS the subject rather than a part inside it."""
    return all(abs(p - q) <= tol for p, q in zip(bbox(a), bbox(b), strict=True))


def _band(a: Pt, b: Pt, half: float) -> Poly:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / n * half, dx / n * half
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def subject_of(caption: Shape, shapes: list[Shape]) -> Subject | None:
    """A caption's subject: the non-text shapes of the tagged element it sits in (its `<g data-kind>`) - or, for a
    caption tagged on its own, the nearest drawn shape of its kind - as a point subject beside which it stands; an
    area subject when the caption already lies inside it. None when there is nothing drawn for it to name."""
    if not caption.kind or caption.kind == "-":
        return None
    own = [s for s in shapes if s.group == caption.group and s.group and s.tag != "text" and not s.leader]
    # a group naming several things (two clerks' seats, each with its label) gives a caption the shape it lies in, not
    # the group's whole extent - which set each label beside the group's middle (feature 267)
    holding = [s for s in own if s.tag == "rect" and inside(caption.center[0], caption.center[1], s.poly)]
    if len(own) > 1 and len([s for s in shapes if s.tag == "text" and s.group == caption.group]) > 1:
        # the room it names, inside the building that holds it - or, outside every shape, the drawn thing nearest it:
        # Ubame's residence privies are one group of two rects at its two ends, and both names were seated beside the
        # span between them (feature 267)
        near = min(own, key=lambda s: math.dist(_mid(s.poly), caption.center))
        own = [min(holding, key=lambda s: _area(s.poly))] if holding else cluster_of(near, own, 2 * caption.size)
    if not own:
        same = [s for s in shapes if s.kind == caption.kind and s.tag != "text" and not s.leader]
        if not same:
            return None
        # the shape of its kind the caption lies in (Ubame's shuttered wing: its name sits in the wing's rect, and the
        # nearest shape of the kind was a shutter line, which read the name as a point caption far off - feature 267)
        held = [s for s in same if s.tag == "rect" and inside(caption.center[0], caption.center[1], s.poly)]
        own = [min(held, key=lambda s: _area(s.poly))] if held else cluster_of(min(same, key=lambda s: math.dist(_mid(s.poly), caption.center)), same, 2 * caption.size)
    if len(own) == 1 and own[0].tag == "rect":
        poly = own[0].poly
    else:
        x0, y0, x1, y1 = bbox([p for s in own for p in s.poly])
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    ang = math.degrees(math.atan2(poly[1][1] - poly[0][1], poly[1][0] - poly[0][0])) if len(poly) == 4 else 0.0
    area = inside(caption.center[0], caption.center[1], poly)
    # an elongated area is named ALONG its length, as a map names a river band (feature 267: Hayakawa's river, a tall
    # rect, had its rotated names turned level across a band too narrow for them)
    x0, y0, x1, y1 = bbox(poly)
    along = 90.0 if area and (y1 - y0) > ELONGATED * max(x1 - x0, 1e-9) else 0.0
    return Subject("area" if area else "point", tuple(poly), angle=along if area else ang)


def cluster_of(seed: Shape, same: list[Shape], reach: float) -> list[Shape]:
    """`seed` and every shape of `same` joined to it through shapes within `reach` of each other - the whole drawn thing
    a caption names. The nearest shape alone depends on where the caption stands, so a genkan drawn as two shapes had its
    caption flip between them on every pass (feature 267)."""
    out = [seed]
    grew = True
    while grew:
        grew = False
        for s in same:
            if s not in out and any(_box_gap(s.poly, o.poly) <= reach for o in out):
                out.append(s)
                grew = True
    return out


def _box_within(a: Poly, b: Poly) -> bool:
    ax0, ay0, ax1, ay1 = bbox(a)
    bx0, by0, bx1, by1 = bbox(b)
    return ax0 >= bx0 and ay0 >= by0 and ax1 <= bx1 and ay1 <= by1


def _box_gap(a: Poly, b: Poly) -> float:
    ax0, ay0, ax1, ay1 = bbox(a)
    bx0, by0, bx1, by1 = bbox(b)
    return math.hypot(max(0.0, max(ax0, bx0) - min(ax1, bx1)), max(0.0, max(ay0, by0) - min(ay1, by1)))


def _area(poly: Poly) -> float:
    x0, y0, x1, y1 = bbox(poly)
    return (x1 - x0) * (y1 - y0)


def _mid(poly: Poly) -> Pt:
    x0, y0, x1, y1 = bbox(poly)
    return (x0 + x1) / 2, (y0 + y1) / 2


@dataclass(frozen=True)
class Finding:
    """One caption not at its standard seat, or with its leader wrong."""

    kind: str
    text: str
    what: str
    placement: Placement


def captions_of(shapes: list[Shape], kinds: set[str] | None) -> list[list[int]]:
    """The sheet's captions, each the list of its `<text>` indices: the texts of one tagged group that STACK - each the
    next line under the last - are one caption, its lines in document order (a board's name with the bill posted under
    it is one caption of two lines). A group's texts that do not stack are separate captions: an office hall names its
    three rooms and a gate range its rooms side by side, and read as one block they were piled into one (feature 267)."""
    groups: dict[int, list[list[int]]] = {}
    order: list[int] = []
    for i, s in enumerate(shapes):
        if s.tag == "text" and s.text and s.kind and s.kind != "-" and (kinds is None or s.kind in kinds):
            key = s.group or -i - 1
            if key not in groups:
                groups[key] = []
                order.append(key)
            runs = groups[key]
            if runs and stacks_under(shapes[runs[-1][-1]], s):
                runs[-1].append(i)
            else:
                runs.append([i])
    return [run for k in order for run in groups[k]]


def stacks_under(above: Shape, below: Shape) -> bool:
    """Is `below` the next line of `above`'s caption: under it by at most two line pitches, and sharing at least half the
    narrower block's width with it - centered, left- or right-aligned alike; two room names side by side share none."""
    ay, by = above.center[1], below.center[1]
    pitch = PITCH_EM * max(above.size, below.size)
    ax0, _ay0, ax1, _ay1 = bbox(above.poly)
    bx0, _by0, bx1, _by1 = bbox(below.poly)
    shared = min(ax1, bx1) - max(ax0, bx0)
    return 0 < by - ay <= 2 * pitch and shared >= 0.5 * min(ax1 - ax0, bx1 - bx0)


def seat(src: str, kinds: set[str] | None = None) -> tuple[list[Finding], list[tuple[list[Shape], Placement]]]:
    """Every caption on a sheet (of `kinds`, or all), placed in document order; the findings, and each caption's texts
    with its standard placement."""
    shapes, view = read_sheet(src)
    pairs = [(idx, subject_of(shapes[idx[0]], shapes)) for idx in captions_of(shapes, kinds)]
    pairs = [(idx, sub) for idx, sub in pairs if sub is not None]
    skip = {i for idx, _ in pairs for i in idx}
    findings: list[Finding] = []
    placed: list[tuple[list[Shape], Placement]] = []
    leaders = [s for s in shapes if s.leader]
    per_group: dict[int, int] = {}
    for idx, _sub in pairs:
        per_group[shapes[idx[0]].group] = per_group.get(shapes[idx[0]].group, 0) + 1
    for idx, sub in pairs:
        caps = [shapes[i] for i in idx]
        head = caps[0]
        lines = [ln for c in caps for ln in c.lines]
        # each caption's own index: the ground drawn after it is an obstacle to IT (see `classify`), and every caption
        # placed before it is one
        index = classify(shapes, view, skip, after=idx[0], group=head.group, kind=head.kind, subject=list(sub.poly), area=sub.kind == "area")
        for _caps, done in placed:
            index.add(Obstacle(done.block, WEIGHT_TEXT))
        cw = char_w_of(head.element, head.text, head.size)
        p = place(" ".join(lines), head.size, sub, index, view, lines=_as_head(caps, cw) if len(caps) > 1 else None, char_w=cw)
        p = hand_seat_if_no_better(p, caps, sub, index)
        if p.position == HAND:
            placed.append((caps, p))
            continue  # at its seat as it stands: the hand's own seat won, so nothing is rewritten or reported

        placed.append((caps, p))
        want = _line_centers(p, [c.size for c in caps], [len(c.lines) for c in caps])
        off = any(math.dist(w, c.center) > TOLERANCE for w, c in zip(want, caps, strict=True))
        if off or abs(((head.angle - p.angle + 90) % 180) - 90) > 0.5 or (len(caps) == 1 and tuple(head.lines) != p.lines):
            findings.append(Finding(head.kind, head.text, "off its standard seat", p))
        have = leader_of(head, leaders, alone=per_group[head.group] == 1)

        if p.leader is None and have is not None:
            findings.append(Finding(head.kind, head.text, "a stray leader", p))
        elif p.leader is not None and (have is None or max(math.dist(have.poly[0], p.leader[0]), math.dist(have.poly[-1], p.leader[1])) > TOLERANCE):
            findings.append(Finding(head.kind, head.text, "a missing or misplaced leader", p))
    return findings, placed


#: Width per character, in ems, of a hand sheet's captions by their face (feature 267). The standard's 0.55 holds for the
#: engine's own regular lowercase captions; a hand sheet's ALL-CAPS court names run ~0.70 (the pack audit's own
#: CHAR_W_BOLD for bold caps is 0.72), bold adds ~0.04, and letter-spacing adds its own width per character - the Inari
#: shrine's bold, spaced name was seated a third too narrow, its first letter under the karo's house.
CAPS_W_EM = 0.70
BOLD_W_EM = 0.04


def _as_head(caps: list[Shape], cw: float) -> list[str]:
    """A caption's lines as the placer measures them - all at the head's size and face - each line standing in for its
    own width: a sub-line in 8 px italic under a 12 px bold name is that much narrower. Measured at the head's face, a
    guest house's note ran 156 px for a 90 px house and its name was seated across the wall (feature 267 round 4)."""
    head = caps[0]
    return [ln if c is head else "x" * max(1, round(len(ln) * c.size * char_w_of(c.element, ln, c.size) / (head.size * cw))) for c in caps for ln in c.lines]


def char_w_of(el: ET.Element | None, text: str, size: float) -> float:
    """How wide a text's characters run, in ems, from its element's face - for a caption being seated and for every
    text read as an obstacle."""
    letters = [c for c in text if c.isalpha()]
    w = CAPS_W_EM if letters and all(c.isupper() for c in letters) else CHAR_W_EM
    if el is not None and el.get("font-weight") == "bold":
        w += BOLD_W_EM
    if el is not None and size:
        w += _f(el, "letter-spacing") / size
    return w


HAND = "hand"
"""The position of a caption kept at the seat it already has (`hand_seat_if_no_better`)."""


def hand_seat_if_no_better(p: Placement, caps: list[Shape], sub: Subject, index: ObstacleIndex) -> Placement:
    """The standard's choice, unless it found no free seat and the caption's own seat costs LESS: the standard takes
    the first free candidate, else the least cost, and on a hand sheet the seat the caption already has is a candidate
    too (feature 267). Where nothing is free - a crowded corner, a name wider than its room - the placer's fallback moved
    a caption onto its neighbors' ink while the hand's seat covered less; kept, the caption is at its standard seat. A tie is not kept: the standard
    breaks ties by ring and rank (266 FR-007), and keeping the hand's seat on one excused 26 captions the standard moves."""
    if p.cost == 0.0:
        return p
    head = caps[0]
    x0, y0, x1, y1 = bbox([pt for c in caps for pt in c.poly])
    block = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    own = list(sub.poly) if sub.kind != "line" else None
    cost = index.cost(block, CLEAR_EM * head.size, own, " ".join(ln for c in caps for ln in c.lines), sub.civic)
    if sub.kind == "area" and not all(inside(q[0], q[1], sub.poly) for q in block):
        cost += WEIGHT_OBSTACLE
    if cost >= p.cost:
        return p  # a tie goes to the standard's own order - the nearer ring, then rank (266 FR-007)
    anchor_y = head.center[1] + CENTER_ABOVE_BASELINE_EM * head.size - (sum(len(c.lines) for c in caps) - 1) * PITCH_EM * head.size / 2
    return replace(p, x=head.center[0], y=anchor_y, angle=head.angle, lines=tuple(ln for c in caps for ln in c.lines), block=block, cost=cost, leader=None, position=HAND)


def _self_tagged(head: Shape) -> bool:
    """Does the caption's text carry its own `data-kind` (so it is its own group) rather than take one from a group?"""
    return head.element is not None and head.element.get("data-kind") is not None


def leader_of(head: Shape, leaders: list[Shape], alone: bool = False) -> Shape | None:
    """The leader a caption has now. A caption in a tagged group finds it in its group; a self-tagged caption is its own
    group, so its leader - written beside it, carrying its kind - is the nearest leader of its kind that reaches its
    block (feature 267: matched by group alone it was never found, and read as missing on one pass, stray on the next).
    Either way the leader must reach THIS caption: a gate range's name, written outside with a leader, lent it to the
    three room names in the same group, each then reported as carrying a stray one. A caption `alone` in its group owns
    any leader in it, wherever it runs: that is its stray or misplaced one."""
    reach = math.inf if alone and head.group and not _self_tagged(head) else max(math.dist(p, head.center) for p in head.poly) + head.size
    mine = (lambda s: s.group == head.group) if head.group and not _self_tagged(head) else (lambda s: s.kind == head.kind)
    near = [s for s in leaders if mine(s) and min(math.dist(p, head.center) for p in s.poly) <= reach]
    return min(near, key=lambda s: min(math.dist(p, head.center) for p in s.poly)) if near else None


def _line_centers(p: Placement, sizes: list[float], counts: list[int]) -> list[Pt]:
    """Where the center of each of a caption's `<text>` blocks stands in a placement: the texts stacked in order about
    the block's middle, each taking its own lines at its OWN size's pitch (a note box's title over its smaller lines -
    spaced at the title's pitch they ran out of the box, feature 267), all turned with the caption. At one size it is
    the even split it always was."""
    heights = [PITCH_EM * s * c for s, c in zip(sizes, counts, strict=True)]
    a = math.radians(p.angle)
    cx, cy = p.x, p.y - CENTER_ABOVE_BASELINE_EM * sizes[0]
    top = -sum(heights) / 2
    out: list[Pt] = []
    for h in heights:
        dy = top + h / 2
        out.append((cx - dy * math.sin(a), cy + dy * math.cos(a)))
        top += h
    return out


def rewrite(src: str, kinds: set[str] | None = None) -> str:
    """The sheet with every caption (of `kinds`) at its standard seat: one seating pass repeated until nothing moves
    (feature 267's measurement: two passes settle the three magistracy sheets - a caption kept at its own seat in one pass
    frees or blocks a neighbor's seat for the next). At most `SETTLE` passes; what is still off after them is reported."""
    out = src
    for _ in range(SETTLE):
        nxt = _rewrite_once(out, kinds)
        if nxt == out:
            break
        out = nxt
    return out


SETTLE = 5


def _rewrite_once(src: str, kinds: set[str] | None = None) -> str:
    """The sheet with every caption (of `kinds`) moved to its standard seat and its leader written, moved or removed."""
    _findings, placed = seat(src, kinds)
    ground, _view = read_sheet(src)
    out = src

    for caps, p in placed:
        if p.position == HAND:
            continue  # kept where it stands (`hand_seat_if_no_better`)

        head = caps[0]
        fill = (head.element.get("fill") if head.element is not None else None) or "#3A2E1C"
        centers = _line_centers(p, [c.size for c in caps], [len(c.lines) for c in caps])
        news: list[str] = []
        for cap, (cx, cy) in zip(caps, centers, strict=True):
            el = cap.element
            assert el is not None
            style = "".join(f' {a}="{el.get(a)}"' for a in ("font-style", "font-weight", "letter-spacing", "paint-order", "stroke", "stroke-width") if el.get(a))
            # a one-text caption takes the placement's LINES too - the standard may wrap it, and writing its old lines
            # left it off its seat on every pass (feature 267)
            lines = tuple(p.lines) if len(caps) == 1 else tuple(cap.lines)
            # written in the text's PARENT frame: a caption inside a translated group (Hayakawa's salt-wards box) was
            # written in sheet coordinates and moved twice (feature 267)
            inv = _inverse(cap.frame)
            lx, ly = _apply(inv, (cx, cy))
            sub = Placement(lx, ly + CENTER_ABOVE_BASELINE_EM * cap.size, p.angle - _angle(cap.frame), lines, p.block, p.ring, p.rank, p.position, p.cost, None)
            # a text carrying its OWN tag keeps it - such a text is its own group, and writing it untagged left untagged
            # ink the page refuses (feature 267); a text taking its tag from a group around it stays untagged
            ink = el.get("fill", fill)
            if _luma(ink) > LIGHT and not _on_dark((cx, cy), ground):
                ink = DARK_INK  # a light name chosen for a dark roof, set down on light ground (Ochiba's `(rice)`, feature 267)
            new = caption_svg(sub, cap.size, style, ink, cap.kind if el.get("data-kind") or not head.group else "")
            old = _element_source(out, el)
            if old:
                out = out.replace(old, new, 1)
                news.append(new)
        out = re.sub(rf'\s*<line[^>]*data-kind="{re.escape(head.kind)}"[^>]*data-leader="1"[^>]*/>', "", out) if not head.group else _drop_group_leader(out, news)
        if p.leader is not None and news:
            # a self-tagged caption's leader carries its kind, which is how `leader_of` finds it again
            inv = _inverse(head.frame)
            local = replace(p, leader=(_apply(inv, p.leader[0]), _apply(inv, p.leader[1])))
            out = out.replace(news[-1], news[-1] + "\n    " + leader_svg(local, head.size, fill, head.kind if _self_tagged(head) else "", mark=True), 1)
    return out


LIGHT = 0.75
"""A fill this light (0-1 luma) is a caption chosen to read on dark ink; it reads on nothing else."""

DARK_INK = "#3A2E1C"
"""The sheets' caption ink."""


def _luma(fill: str | None) -> float:
    """A `#rgb` or `#rrggbb` fill's luma (0 black, 1 white); anything else - none, a pattern - reads as 0.5."""
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", (fill or "").strip())
    if not m:
        return 0.5
    h = m.group(1)
    h = "".join(c * 2 for c in h) if len(h) == 3 else h
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def _on_dark(pt: Pt, shapes: list[Shape]) -> bool:
    """Is the innermost filled shape under a point dark?"""
    under = [s for s in shapes if s.tag != "text" and not s.line and s.element is not None and s.element.get("fill") and inside(pt[0], pt[1], s.poly)]
    return bool(under) and _luma(min(under, key=lambda s: _area(s.poly)).element.get("fill")) < 1 - LIGHT  # type: ignore[union-attr]


def _drop_group_leader(src: str, news: list[str]) -> str:
    """Remove the leader line that follows a caption's last text, if it has one."""
    if not news:
        return src
    return re.sub(re.escape(news[-1]) + r'\s*<line[^>]*data-leader="1"[^>]*/>', lambda m: news[-1], src, count=1)


def _element_source(src: str, el: ET.Element) -> str:
    """The `<text ...>...</text>` in the source that `el` was parsed from - found by its text and its x and y."""
    # the text as the SOURCE spells it: `& pantries` is `&amp; pantries` there, and matching the parsed text missed it,
    # leaving that line of a caption unmoved (feature 267)
    body = re.escape(html.escape((el.text or "").strip(), quote=False))
    for m in re.finditer(r"<text\b[^>]*>.*?</text>", src, re.S):
        s = m.group(0)
        if re.search(rf'\bx="{re.escape(el.get("x", ""))}"', s) and re.search(rf'\by="{re.escape(el.get("y", ""))}"', s) and (not body or re.search(body, s)):
            return s
    return ""


def ledger_entry(src: str) -> dict[str, object]:
    """What the exemption ledger records for a sheet as it stands: its content hash and every caption finding, each as
    [kind, text, what] (spec FR-013)."""
    findings, _placed = seat(src)
    return {"sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(), "exempt": sorted([f.kind, f.text, f.what] for f in findings)}


def judge(src: str, entry: dict[str, object] | None) -> list[str]:
    """The ledger rule (spec FR-013, D9): what is wrong with a hand-drawn sheet's captions. A finding is excused only
    while the ledger holds it AND the sheet is unchanged since it was recorded; a changed or new sheet is held to the
    standard in full, and must tag every `<text>` - on the element or a group around it - so the tool can see it."""
    findings, _placed = seat(src)
    unchanged = entry is not None and entry.get("sha256") == hashlib.sha256(src.encode("utf-8")).hexdigest()
    exempt = {tuple(e) for e in entry.get("exempt", ())} if unchanged and entry is not None else set()  # type: ignore[union-attr]
    out = [f"{f.kind!r} {f.text!r}: {f.what}" for f in findings if (f.kind, f.text, f.what) not in exempt]
    if not unchanged:
        shapes, _view = read_sheet(src)
        out += [f"untagged caption {s.text!r}: tag it (or its group) with its data-kind, or `-` for a title" for s in shapes if s.tag == "text" and s.text and not s.kind]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Seat a hand-drawn sheet's captions by the one placer (feature 266).")
    ap.add_argument("sheet")
    ap.add_argument("--kind", action="append", help="only captions of this data-kind (repeatable)")
    ap.add_argument("--write", action="store_true", help="rewrite the captions and leaders in place")
    args = ap.parse_args(argv)
    path = Path(args.sheet)
    src = path.read_text(encoding="utf-8")
    kinds = set(args.kind) if args.kind else None
    if args.write:
        path.write_text(rewrite(src, kinds), encoding="utf-8")
    findings, placed = seat(path.read_text(encoding="utf-8"), kinds)
    for f in findings:
        print(f"{f.kind!r} {f.text!r}: {f.what} - standard seat {f.placement.position}, ring {f.placement.ring}")
    print(f"seat-label: {len(placed)} caption(s), {len(findings)} not at the standard seat")
    return 1 if findings else 0


if __name__ == "__main__":  # pragma: no cover - the make target's entry
    sys.exit(main())
