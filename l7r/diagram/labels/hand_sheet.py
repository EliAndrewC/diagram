"""A hand-drawn Mode A sheet's captions, placed by the ONE placer (feature 266) in the render pipeline (feature 286).

A hand-drawn sheet's SVG is the drawing and, for each caption, its declaration - its text, its face and what it names -
never where it stands (feature 286, the GM: *"There is no point in having an automated check run against an automated
process"*). `placed(svg)` reads the sheet's drawn shapes, classifies each by its `data-kind` tag (feature 262 tagged
every drawn element), finds each caption's subject from its declaration (`declared_parts`) and asks
`l7r.diagram.labels.place` where it goes - inside its subject first, then beside it (`subjects`) - and returns the sheet
with every caption written there and its leader drawn. Each sheet's gen renders its picture and its page from that
text; `make sheet-render` renders one for a session or a review agent to look at. A caption's placement is a function
of the drawing and the declarations alone, and the placer's unit tests are what hold it correct.

The classification (feature 266 plan P4): the way kinds are ways (500 a way crossed), the ground kinds are free space,
the one `-` shape covering the whole view is the background (free), and everything else - every other `-` shape, every
`<text>` whatever its tag, `court divider`, `weighing floor` - is an obstacle (1,000).

Feature 267 weighed ink as a reader meets it (`classify`): another caption 10,000, dark ink 2,000, anything painted
after a caption as much as a caption (it hides it), ink inside what a caption names in full (`Obstacle.inner`) - except
ground nested in the ground it names and ink the sheet marks `data-texture="1"` (a feature's surface, a wing's shutter
marks), both light (250) - a ground's drawn border, and an area's own outline; the building holding a named room is
waived.

    make sheet-render SHEET=pool/<tier>/<map>/<map>.svg OUT=<png>
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
from typing import Any
from dataclasses import dataclass, field, replace
from pathlib import Path

from l7r.diagram.labels import InkPart, Obstacle, ObstacleIndex, Placement, Subject, Way, place
from l7r.diagram.labels.geom import Poly, Pt, bbox, inside, rect
from l7r.diagram.labels.layout import layouts
from l7r.diagram.labels.placer import _nearest_ink
from l7r.diagram.labels.standard import CENTER_ABOVE_BASELINE_EM, CHAR_W_EM, CLEAR_EM, PITCH_EM, REACH_EM, WEIGHT_OBSTACLE, WEIGHT_WAY, block_half
from l7r.diagram.labels.svg import caption_svg, leader_svg

SVG = "{http://www.w3.org/2000/svg}"
JOINS = ("miter", "round", "bevel", "miter-clip", "arcs")
"""The `stroke-linejoin` values SVG knows (SVG 2 adds the last two, which draw a miter within the limit); any other is ignored."""

WAY_KINDS = frozenset({"road", "river", "revetment"})
"""The kinds a caption may cross at a way's weight (plan P4, observed 2026-09-27, method: the tag census of the six
sheets - roads are stroked paths 18 to 40 px wide)."""

GROUND_KINDS = frozenset({"outer court", "inner court", "border court", "practice ground", "garden", "vegetable garden", "garden pines", "cart yard", "rear yard", "shrine grove", "river landing"})
"""The sheets' open ground - free space to a caption (plan P4). An explicit list: a name that merely CONTAINS "court"
is not ground (`court divider` is a wall), and a roofed floor on posts (`weighing floor`) is built - as the hearing court
is since feature 267 roofed it (research 0099), so another caption no longer takes its floor as open ground. The `rear
yard` (feature 283's open working ground behind a house) was missed when it was added: its outline weighed as a drawn
obstacle, and on Ubame, once the yard reached down to the reception privy (feature 335), the privy's name was led out
across the yard into the shrine grove."""

WEIGHT_INNER = WEIGHT_OBSTACLE / 4
"""What ground nested inside the ground a caption names costs (feature 267): a court's name takes the court's own open
earth before a garden inside it, and a garden before a building."""

WEIGHT_DARK = 2 * WEIGHT_OBSTACLE
"""What covering dark ink costs - a wall, a post, a dark roof (feature 267): black caption ink cannot be read on it,
where on light ink it can, so a caption with no free seat takes light ink first. At one weight Hayakawa's practice
ground's name, with no free seat in its ground, lay across the compound wall."""
BUSY_FILLS: frozenset[str] = frozenset({"url(#vegetable-rows)"})
"""Fills a name cannot be read on even as nested ground: a worked bed's rows run through the letters (feature 283 - Ubame's
INNER COURT, its seat above the house taken by the storehouses, went onto the kitchen garden's furrows)."""

DARK = 0.3
"""Ink this dark (0-1 luma) or darker is dark to a caption.

Research: dark ink threshold - CONVENTION: ink of luma 0.3 or darker counts as dark to a caption, so a caption reads against it."""

WEIGHT_TEXT = 10 * WEIGHT_OBSTACLE


"""What covering another caption costs: ten drawn obstacles (feature 267). A caption with no free seat falls back to the
least cost, and at one weight for all ink it chose a seat on Ubame's border name over one on the parley room's own
mats - words on words are the one overlap a reader cannot see past."""

Affine = tuple[float, float, float, float, float, float]
IDENTITY: Affine = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
"""Research: identity transform - NONE: the identity affine matrix."""


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
    busy: bool = False  # painted in a banded fill (a worked bed's rows) that crosses a name's letters, however light its ground
    dark: bool = False  # drawn in dark ink - a line's stroke, a shape's fill - which black caption ink cannot be read on
    at: int = -1  # the element's place in the document (`root.iter()` order), which is how `placed` finds it to write
    ids: frozenset[str] = frozenset()  # the element's `data-id` and every one around it - what a caption's `data-names` names
    names: tuple[str, ...] = ()  # a caption's `data-names`: the `data-id`s of the drawn things it names (feature 286)
    cont: bool = False  # a caption line marked `data-cont="1"`: the next line of the caption before it (feature 286)
    cap: str = "butt"  # a stroke's `stroke-linecap`, inherited as SVG inherits it: "butt" (SVG's default), "square" or "round" (feature 449 T193)
    join: str = "miter"  # a stroke's `stroke-linejoin`, inherited: "miter" (SVG's default, and its SVG 2 forms), "round" or "bevel" (T194)
    miter: float = 4.0  # a stroke's `stroke-miterlimit`, inherited (SVG's default 4): a sharper corner's miter is drawn as a bevel (T194)
    closed: bool = False  # a stroke a path's `Z` closed: drawn with a join at its start, no caps (T194)
    dash: tuple[float, ...] = ()  # a stroke's `stroke-dasharray` in sheet px, an even count (empty: solid), inherited (T194)
    offset: float = 0.0  # a stroke's `stroke-dashoffset` in sheet px, inherited (T194)


def _path_points(d: str, tol: float) -> list[tuple[list[Pt], bool]]:
    """A path's subpaths as SVG draws them, each its points and whether a `Z` closed it: absolute and relative move, line, horizontal
    and vertical steps, and every curve - cubic and quadratic Beziers, their smooth forms reflecting the control point before, and
    elliptical arcs - flattened finely enough that no chord stands more than `tol` inside it. A move starts a new subpath, and a step
    after a `Z` starts one at the closed subpath's start (feature 449 T194: a curve was kept by its end points alone, so Hoshigaoka's
    sacred-tree rope, a ring drawn in two arcs, was read as a 10 px line doubled back, and a second move was joined to the first by a
    segment nobody drew).

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 6 (SVG C-command argument count); 7 (SVG A-command argument count)
    """
    subs: list[tuple[list[Pt], bool]] = []
    pts: list[Pt] = []
    closed = False
    x = y = sx = sy = 0.0
    ctrl: Pt | None = None  # the last cubic's second control point, or the last quadratic's control point, which S and T reflect
    last = ""
    for cmd, args in re.findall(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)", d):
        up, rel = cmd.upper(), cmd.islower()
        if up == "Z":
            if pts:
                closed = True
            x, y, last = sx, sy, "Z"
            continue
        v = [float(n) for n in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        step = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7}[up]
        for i in range(0, len(v) - step + 1, step):
            c = v[i : i + step]
            ox, oy = (x, y) if rel else (0.0, 0.0)
            if (up == "M" and i == 0) or closed:
                # a move, or a step after a `Z`, starts a new subpath (at the closed one's start)
                if pts:
                    subs.append((pts, closed))
                pts, closed = [], False
                if up == "M" and i == 0:
                    x, y = ox + c[0], oy + c[1]
                    sx, sy, pts, last = x, y, [(x, y)], "M"
                    continue
                pts = [(x, y)]
            if not pts:
                pts = [(x, y)]
            p0 = (x, y)
            if up == "H":
                x = ox + c[0]
                pts.append((x, y))
            elif up == "V":
                y = oy + c[0]
                pts.append((x, y))
            elif up in ("M", "L"):
                x, y = ox + c[0], oy + c[1]
                pts.append((x, y))
            elif up in ("C", "S"):
                c1 = (ox + c[0], oy + c[1]) if up == "C" else (2 * x - ctrl[0], 2 * y - ctrl[1]) if ctrl is not None and last in ("C", "S") else p0
                c2, e = (ox + c[-4], oy + c[-3]), (ox + c[-2], oy + c[-1])
                pts.extend(_bezier((p0, c1, c2, e), tol))
                (x, y), ctrl = e, c2
            elif up in ("Q", "T"):
                q = (ox + c[0], oy + c[1]) if up == "Q" else (2 * x - ctrl[0], 2 * y - ctrl[1]) if ctrl is not None and last in ("Q", "T") else p0
                e = (ox + c[-2], oy + c[-1])
                pts.extend(_bezier((p0, q, e), tol))
                (x, y), ctrl = e, q
            else:
                e = (ox + c[5], oy + c[6])
                pts.extend(_arc(p0, c[0], c[1], c[2], c[3] != 0.0, c[4] != 0.0, e, tol))
                x, y = e
            last = up
    if pts:
        subs.append((pts, closed))
    return subs


def _dasharray(v: str | None, up: tuple[float, ...]) -> tuple[float, ...]:
    """A `stroke-dasharray` as SVG reads it: `none`, or lengths of no sum, solid (empty); an odd count repeated to an even one; a value
    SVG does not read - a negative or no number, a percentage - ignored, so the inherited pattern `up` stands."""
    if v is None:
        return up
    if v.strip() == "none":
        return ()
    try:
        vals = [float(x) for x in re.split(r"[\s,]+", v.strip()) if x]
    except ValueError:
        return up
    if not vals or any(x < 0 for x in vals):
        return up
    if sum(vals) == 0.0:
        return ()
    return tuple(vals * 2 if len(vals) % 2 else vals)


def _bezier(cp: tuple[Pt, ...], tol: float) -> list[Pt]:
    """A cubic or quadratic Bezier's points after its start, in the fewest equal steps of its parameter whose chords stand within `tol`
    of the curve: Wang's bound, n(n - 1) / 8 times the largest second difference of the control points, over the square of the steps."""
    deg = len(cp) - 1
    dd = max(math.hypot(cp[k][0] - 2 * cp[k + 1][0] + cp[k + 2][0], cp[k][1] - 2 * cp[k + 1][1] + cp[k + 2][1]) for k in range(deg - 1))
    n = max(1, math.ceil(math.sqrt(deg * (deg - 1) / 8 * dd / tol)))
    out: list[Pt] = []
    for k in range(1, n + 1):
        t = k / n
        w = [math.comb(deg, j) * t**j * (1 - t) ** (deg - j) for j in range(deg + 1)]
        out.append((sum(wj * p[0] for wj, p in zip(w, cp, strict=True)), sum(wj * p[1] for wj, p in zip(w, cp, strict=True))))
    out[-1] = cp[-1]
    return out


def _arc(p0: Pt, rx: float, ry: float, rot: float, large: bool, sweep: bool, e: Pt, tol: float) -> list[Pt]:
    """An elliptical arc's points after its start, as SVG draws it (SVG 1.1 appendix F.6): none where it ends where it starts, a
    straight step where a radius is 0, its radii scaled up where they cannot reach the end, and its center found from its flags;
    flattened in equal steps of its angle whose chords stand within `tol` of the curve, R(1 - cos(half a step)), R its larger radius."""
    if p0 == e:
        return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0.0 or ry == 0.0:
        return [e]
    phi = math.radians(rot)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - e[0]) / 2, (p0[1] - e[1]) / 2
    x1, y1 = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1.0:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / (rx * rx * y1 * y1 + ry * ry * x1 * x1)))
    if large == sweep:
        co = -co
    cx1, cy1 = co * rx * y1 / ry, -co * ry * x1 / rx
    cx, cy = cp * cx1 - sp * cy1 + (p0[0] + e[0]) / 2, sp * cx1 + cp * cy1 + (p0[1] + e[1]) / 2
    ux, uy, vx, vy = (x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry
    t1 = math.atan2(uy, ux)
    dt = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    if sweep and dt < 0:
        dt += 2 * math.pi
    elif not sweep and dt > 0:
        dt -= 2 * math.pi
    r = max(rx, ry)
    n = max(1, math.ceil(abs(dt) / (2 * math.acos(max(-1.0, 1 - tol / r)))))
    out = []
    for k in range(1, n + 1):
        t = t1 + dt * k / n
        out.append((cx + rx * math.cos(t) * cp - ry * math.sin(t) * sp, cy + rx * math.cos(t) * sp + ry * math.sin(t) * cp))
    out[-1] = e
    return out


def _stretch(m: Affine) -> float:
    """How far `m` stretches a unit length at most - its linear part's largest singular value."""
    a, b, c, dd = m[0], m[1], m[2], m[3]
    s = a * a + b * b + c * c + dd * dd
    return math.sqrt((s + math.sqrt(max(0.0, s * s - 4 * (a * dd - b * c) ** 2))) / 2)


def read_sheet(src: str) -> tuple[list[Shape], tuple[float, float, float, float]]:
    """Every drawn element of a sheet as a Shape, and the sheet's view (x0, y0, x1, y1)."""
    root = ET.fromstring(src)
    vb = [float(v) for v in re.split(r"[\s,]+", (root.get("viewBox") or "0 0 0 0").strip())]
    view = (vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3])
    shapes: list[Shape] = []
    order = {id(e): k for k, e in enumerate(root.iter())}

    def walk(
        el: ET.Element,
        m: Affine,
        kind: str,
        stroke_w: float,
        stroked: bool,
        group: int,
        within: frozenset[int] = frozenset(),
        ink: tuple[str, str] = ("", ""),
        texture: bool = False,
        ids: frozenset[str] = frozenset(),
        cap: str = "butt",
        join: str = "miter",
        miter: float = 4.0,
        dash: tuple[float, ...] = (),
        offset: float = 0.0,
    ) -> None:
        parent = m
        if el.get("data-id"):
            ids = ids | {el.get("data-id", "")}
        m = _mul(m, parse_transform(el.get("transform")))
        if el.get("data-kind") is not None:
            kind, group = el.get("data-kind", kind), id(el)  # the tagged element a caption and its subject share
            within = within | {group}
        stroke_w = _f(el, "stroke-width", stroke_w)
        if el.get("stroke") is not None:
            stroked = el.get("stroke") != "none"
        ink = (el.get("stroke", ink[0]), el.get("fill", ink[1]))  # (stroke, fill), inherited as SVG inherits them
        texture = texture or el.get("data-texture") == "1"
        # a stroke's cap, join and miter limit, inherited as SVG inherits them, a value SVG does not know ignored, as SVG ignores it, so the
        # one inherited stands (feature 449 T193, T194)
        cap = el.get("stroke-linecap", cap) if el.get("stroke-linecap") in ("butt", "square", "round") else cap
        join = el.get("stroke-linejoin", join) if el.get("stroke-linejoin") in JOINS else join
        limit = _f(el, "stroke-miterlimit", 0.0)
        miter = limit if limit >= 1.0 else miter
        dash = _dasharray(el.get("stroke-dasharray"), dash)
        offset = _f(el, "stroke-dashoffset", offset)

        tag = el.tag.replace(SVG, "")
        pts: list[Pt] = []
        subs: list[tuple[list[Pt], bool]] | None = None
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
            # a polyline is a stroke unless a fill is set on it or inherited, as SVG fills it (feature 449 T194)
            line = tag == "polyline" and ink[1] in ("", "none")
        elif tag == "line":
            pts = [(_f(el, "x1"), _f(el, "y1")), (_f(el, "x2"), _f(el, "y2"))]
            line = True
        elif tag == "path":
            # each subpath its own shape, as SVG strokes each alone, flattened within the drawn sag on the sheet (feature 449 T194)
            subs = _path_points(el.get("d", ""), DISC_SAG_PX / max(_stretch(m), 1e-9))
            # a stroke where its fill, its own or inherited, is none (feature 449 T194: a group's `fill="none"` was not read, and its
            # strokes read as boxes)
            line = stroked and ink[1] == "none"
        elif tag == "text":
            t = _text_shape(el, m, kind)
            t.frame = parent
            t.group = group
            t.within = within
            t.at, t.ids = order[id(el)], ids
            t.names, t.cont = tuple((el.get("data-names") or "").split()), el.get("data-cont") == "1"
            shapes.append(t)
            return
        for pts, closed in subs if subs is not None else [(pts, False)]:
            if len(pts) < 2:
                continue
            tp = [_apply(m, p) for p in pts]
            if line:
                shapes.append(
                    Shape(
                        tag,
                        kind,
                        tp + [tp[0]] if closed and tp[-1] != tp[0] else tp,
                        stroke_w / 2,
                        True,
                        element=el,
                        leader=el.get("data-leader") == "1",
                        group=group,
                        within=within,
                        dark=_luma(ink[0]) < DARK,
                        texture=texture,
                        at=order[id(el)],
                        ids=ids,
                        cap=cap,
                        join="round" if join == "round" else "bevel" if join == "bevel" else "miter",
                        miter=miter,
                        closed=closed,
                        # the pattern in sheet px: its lengths scaled as the element's own are (exact for a turn and an even scale)
                        dash=tuple(v * math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) for v in dash),
                        offset=offset * math.sqrt(abs(m[0] * m[3] - m[1] * m[2])),
                    )
                )
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
                        busy=ink[1] in BUSY_FILLS,
                        at=order[id(el)],
                        ids=ids,
                        join="round" if join == "round" else "bevel" if join == "bevel" else "miter",
                        miter=miter,
                    )
                )
        for c in el:
            walk(c, m, kind, stroke_w, stroked, group, within, ink, texture, ids, cap, join, miter, dash, offset)

    for c in root:
        walk(c, IDENTITY, "", 1.0, False, 0)
    # a coordinate that is no finite number is refused here, as the Rust port refuses it: the placer's grid cannot file it (feature 449
    # T184 - an infinity overflowed and a NaN raised later, in other words)
    if any(not (math.isfinite(x) and math.isfinite(y)) for s in shapes for x, y in s.poly):
        raise ValueError("a drawn coordinate is no finite number")
    return shapes, view


def _text_shape(el: ET.Element, m: Affine, kind: str) -> Shape:
    """Research:
    its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 12 (default font size)
    """
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
    skip: set[int] | frozenset[int] = frozenset(),
    after: int | None = None,
    group: int = 0,
    kind: str = "",
    subject: Poly | None = None,
    area: bool = False,
    dark_inside: bool = False,
    named: frozenset[str] = frozenset(),
) -> ObstacleIndex:  # type: ignore[assignment]
    """The sheet as the placer sees it (plan P4). `skip` holds the captions being placed, which are not obstacles to
    themselves. With `after` (a caption's own index), a GROUND shape drawn LATER in the document - outside the caption's
    own `group` - is an obstacle too: a placed caption is written where it stands in the document, so ground painted
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
            # quarters on one (round 4). Ground painted AFTER the caption is not light: it hides the name however open it
            # is (Hayakawa's vegetable bed cut from the inner garden's corner took the garden's name, feature 283)
            over = after is not None and i > after and s.filled and not s.line
            light = (s.kind in GROUND_KINDS and s.kind != kind and not over and not s.busy) or s.texture
            # ink inside it that carries a name of its own (`named` - a named room, a named ground) weighs as that name:
            # a caption set on it reads as naming it (feature 286 - Ubame's RESIDENCE was set in the guest room, and its
            # OUTER COURT on the practice ground, whose own name it pushed out)
            own_name = s.kind in named and s.kind != kind and not s.texture

            weight = WEIGHT_TEXT if own_name or over else WEIGHT_INNER if light else WEIGHT_OBSTACLE
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
            if dark_inside and s.dark and s.filled and _same_box(s.poly, subject):
                # its own dark fill (a well's shaft, a tub, a dark roof) takes no name in the sheet's dark ink: the
                # caption goes beside it (feature 286, plan D2)
                obstacles.append(Obstacle(tuple(s.poly), WEIGHT_DARK, inner=True))
            continue

        if s.tag == "text":
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_TEXT))
        elif after is not None and i > after and s.filled and not s.line and not _is_background(s, view):
            # painted OVER the caption, which a hand sheet keeps where it stands in the document: it hides the name as
            # surely as another name would (Hayakawa's weapon rack under the granary, feature 267)
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_TEXT))

        elif s.busy and s.kind != kind:
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_OBSTACLE))  # ground in rows no other name can be read on
        elif s.kind in GROUND_KINDS or _is_background(s, view):
            # a ground's drawn border is ink even where its floor is free space (Ochiba's RESIDENCE on the vegetable
            # garden's dashed edge, feature 267); the border of the ground a caption names is its own, and waived
            if s.edge and not _is_background(s, view) and not (subject is not None and _same_box(s.poly, subject)):
                ring = [*s.poly, s.poly[0]]
                obstacles += [Obstacle(tuple(_band(a, b, s.edge)), WEIGHT_OBSTACLE) for a, b in zip(ring, ring[1:], strict=False)]
            # a ground's name set on another ground that carries a name of its own reads as naming it (feature 286 -
            # Ubame's OUTER COURT on the practice ground); a thing's name beside it on open ground is free as ever
            if kind in GROUND_KINDS and s.kind in named and s.kind != kind and not _is_background(s, view):
                obstacles.append(Obstacle(tuple(s.poly), WEIGHT_TEXT))
            continue
        elif s.kind in WAY_KINDS:
            if s.line:
                ways.append(Way(tuple(s.poly), max(s.half, 0.5)))
            else:
                obstacles.append(Obstacle(tuple(s.poly), WEIGHT_WAY))
        elif s.line:
            for a, b in zip(s.poly, s.poly[1:], strict=False):
                obstacles.append(Obstacle(tuple(_band(a, b, max(s.half, 0.5))), WEIGHT_DARK if s.dark else WEIGHT_OBSTACLE))
        elif s.filled and s.kind in named and s.kind != kind and not s.texture:
            # a thing that carries a name of its own: a caption set on it reads as naming it (feature 286 - Ubame's
            # OUTER COURT, with no free seat on its apron, was set on the gate range's roof)
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_TEXT))
        else:
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_DARK if s.dark else WEIGHT_OBSTACLE))
    return soft_index(obstacles, ways)


def soft_index(obstacles: list[Obstacle], ways: list[Way]) -> ObstacleIndex:
    """A hand sheet's index with what a caption may be set on when nothing is free marked `soft` (feature 287, D10): light
    ink, nested ground and the ways. What stays hard is what the sheet's own checks call an overlap - another caption or
    ink painted over one (`WEIGHT_TEXT`: overlapping, occluded) and dark ink under dark words (`WEIGHT_DARK`) - which the
    placer never draws: with no other seat, such a caption goes in the sheet's key."""
    return ObstacleIndex([replace(o, soft=o.weight < WEIGHT_DARK) for o in obstacles], [replace(w, soft=True) for w in ways])


def _same_box(a: Poly, b: Poly, tol: float = 1.0) -> bool:
    """Do two outlines share a box (within `tol`) - a shape that IS the subject rather than a part inside it."""
    return all(abs(p - q) <= tol for p, q in zip(bbox(a), bbox(b), strict=True))


def _band(a: Pt, b: Pt, half: float) -> Poly:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / n * half, dx / n * half
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def leader_to_ink(p: Placement, parts: list[Shape]) -> Placement:
    """A leader ends on the drawn thing it names, not on the box around its parts: a barge moored by lines and three
    pines are boxed with empty water or ground in the box's corner, and a leader to the corner named nothing (feature
    283 - the tax barge's and the old pines' leaders ended 5-6 ft short). A disc's ink is its drawn curve (`drawn_ink`), not the box
    the reader keeps as its outline (feature 449 T192: three pool leaders ended 1.75 to 4.45 px off the curve); a stroke's is its band as
    the sheet draws it, its `stroke-linecap` read, and a closed part's its outline drawn out by its own stroke (feature 449 T193: a leader
    past a butt end stopped up to the half-width short of the ink, and one to a stroked building inside its stroke), their corners joined
    as the sheet joins them (T194). The tip is the placer's own (`_nearest_ink` from the leader's start, its exact measure where shapely
    drew each round end and corner as chords, feature 449 T194), so this leaves every leader a hand sheet's subject scores as it was
    scored (`Subject.ink`, feature 449 T192). A leader whose start already lies on the ink it names ties nothing back - the caption
    touches its subject - so it is dropped (feature 449 T184: it divided by the zero distance there); one to parts that draw no ink is
    left as it was scored.

    Research:
        its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 1.5 (leader already touching ink, left alone)
        leader end trim - CONVENTION: a leader stops short of the ink it ends on by a quarter of its length, at most 1 px, so its end does not touch the ink; a drawn size on the sheet, not in the world
    """
    if p.leader is None or not parts:
        return p
    ink = tuple(drawn_ink(s) for s in parts if len(s.poly) >= (2 if s.line else 3))
    at_end = _nearest_ink([p.leader[1]], ink)
    if at_end is None or math.dist(*at_end) < 1.5:
        return p
    a, tip = _nearest_ink([p.leader[0]], ink) or at_end
    d = math.dist(a, tip)
    if d == 0.0:
        return replace(p, leader=None)
    trim = min(1.0, d / 4)
    ux, uy = (tip[0] - a[0]) / d, (tip[1] - a[1]) / d
    return replace(p, leader=(p.leader[0], (tip[0] - ux * trim, tip[1] - uy * trim)))


DISC_SAG_PX = 0.05
"""How far a disc's drawn curve, sampled as a polygon, may stand inside the true curve (px): a leader's end on it lands within its
1 px trim and this of the curve (feature 449 T192).

Research: a disc's sampled curve - CONVENTION: a disc's drawn curve sampled finely enough that no chord stands more than 0.05 px inside it - a drawn size on the sheet, not in the world; the sample count is the least whose chord sag R(1 - cos(pi / n)) is within it, R bounding the curve's half-axes (the pool's largest disc half-axis is 45 px, 80 samples at the bound)"""


def _drawn_as(part: Shape, own: list[Shape]) -> tuple[InkPart, ...]:
    """The drawn ink of one closed part as the sheet draws it: its own and that of every other closed part of `own` sharing its box -
    a fill and the outline stroked over it as two elements (Hayakawa's RESIDENCE's blocks), which draw one block (feature 449 T193: a
    leader read off the fill alone ended inside the outline's stroke)."""
    return tuple(drawn_ink(s) for s in own if s is part or (not s.line and len(s.poly) >= 3 and _same_box(s.poly, part.poly)))


def drawn_ink(s: Shape) -> InkPart:
    """A drawn part as a leader ends on it (feature 449 T192, T193): a stroke's polyline at its half-width, at least half a pixel, and its
    cap (the band `leader_to_ink` buffers); a disc's drawn curve - the image of the unit circle in the drawn box the reader keeps as its
    outline, its center plus cos t of one half-side plus sin t of the other, so a turned or unequally scaled disc is drawn as it is -
    sampled in `_disc_samples` points; any other shape its outline; a closed part with the half-width of the stroke drawn on it (`edge`).

    Research: its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.5 (a stroke's least half-width, the band `leader_to_ink` buffers)
    """
    if s.line:
        return InkPart(tuple(s.poly), line=True, half=max(s.half, 0.5), cap=s.cap, join=s.join, miter=s.miter, closed=s.closed, dash=s.dash, offset=s.offset)
    if s.tag not in ("circle", "ellipse") or len(s.poly) != 4:
        return InkPart(tuple(s.poly), half=s.edge, join=s.join, miter=s.miter)
    p0, p1, p2, p3 = s.poly
    c = ((p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2)
    u, v = ((p1[0] - p0[0]) / 2, (p1[1] - p0[1]) / 2), ((p3[0] - p0[0]) / 2, (p3[1] - p0[1]) / 2)
    n = _disc_samples(math.hypot(math.hypot(*u), math.hypot(*v)))
    ts = [2 * math.pi * k / n for k in range(n)]
    return InkPart(tuple((c[0] + math.cos(t) * u[0] + math.sin(t) * v[0], c[1] + math.cos(t) * u[1] + math.sin(t) * v[1]) for t in ts), half=s.edge, join=s.join, miter=s.miter)


def _disc_samples(r: float) -> int:
    """The least number of points sampling a curve whose half-axes `r` bounds with no chord more than `DISC_SAG_PX` inside it -
    R(1 - cos(pi / n)) - at least 8 (a disc smaller than the sag).

    Research: its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 8 (the least samples of a disc's curve)
    """
    return 8 if r <= DISC_SAG_PX else max(8, math.ceil(math.pi / math.acos(1 - DISC_SAG_PX / r)))


BLOCK_PX = 2000.0
"""A part big enough to be a block of a building (about 220 sq ft): a notice board's legs, a sanctuary's steps or a mat
are parts of one thing, not blocks that can stand in echelon.

Research: block part size - CONVENTION: a part of 2000 px2 (about 220 sq ft) or more counts as a block of a building to the caption placer, not a sub-part - a calibration of the placer, which changes where a caption is seated"""
STEPPED = 0.85
"""How much of its box a multi-part subject must fill to be named against the box: under it the parts leave an empty
corner (Hayakawa's residence, two blocks in echelon), and a caption and its leader set against the box land in that
corner, on nothing (feature 283 - RESIDENCE's leader ended 4 ft short of the house, under INNER COURT).

Research: stepped subject fill - CONVENTION: a multi-part subject filling under 0.85 of its box is named against its parts, not the box - a calibration of the placer, which changes where a caption is seated"""


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


GLYPH_MAX_PX = 600.0
"""The largest drawn thing a leader may not end against, in px (a well's curb is 24 x 24): a tub, a stone, a basin -
beside the feature a leader names, the tip would name it instead. A building is larger and is what leaders point at.

Research: leader-end glyph size - CONVENTION: a drawn thing up to 600 px2 (a well curb is 24 x 24) is a glyph a leader may not end against, so a caption's leader names the building."""


def leader_blockers(shapes: list[Shape], skip: set[int], placed: list[tuple[list[Shape], Placement]], sub: Subject, own_parts: list[Shape] | None = None) -> ObstacleIndex:
    """What a caption's leader may not pass over or end against (feature 283): every other caption - the sheet's own
    drawn texts and those already placed - every small glyph that is not part of what the caption names, and every wall
    (feature 286: with no hand seat to fall back on, the bath's and the granary's names were led across the court
    divider and the compound wall from ground on the far side, a caption naming a building it is walled off from), and
    every building it would cross - except
    a wall the caption names (Ubame's east wall is the Fox border), which `own_parts` holds; a wall merely inside the
    subject's box is a wall (Ubame's INNER COURT was led over the compound wall from above the sheet)."""
    own = list(sub.poly)
    out = [Obstacle(tuple(s.poly), WEIGHT_TEXT) for i, s in enumerate(shapes) if s.tag == "text" and i not in skip]
    out += [Obstacle(done.block, WEIGHT_TEXT) for _caps, done in placed]
    out += [
        Obstacle(tuple(s.poly), WEIGHT_OBSTACLE)
        for s in shapes
        if s.tag != "text" and s.filled and not s.line and not s.leader and s.kind != "door" and 0 < _area(s.poly) <= GLYPH_MAX_PX and not _box_within(s.poly, own)
    ]
    out += [
        Obstacle(tuple(_band(a, b, s.half)), WEIGHT_TEXT)
        for s in shapes
        if s.line and s.dark and s.half >= WALL_HALF_PX and not s.leader and not any(s is o for o in own_parts or ())
        for a, b in zip(s.poly, s.poly[1:], strict=False)
    ]
    # and every building it would cross to reach its subject - not the one it names, nor one holding what it names (a
    # room's own range): Ochiba's inner garden was led across the kitchen
    out += [
        Obstacle(tuple(s.poly), WEIGHT_OBSTACLE)
        for s in shapes
        if s.tag != "text"
        and s.filled
        and not s.line
        and not s.leader
        and s.kind not in GROUND_KINDS
        and s.kind != "-"
        and _area(s.poly) > GLYPH_MAX_PX
        and not any(s is o for o in own_parts or ())
        and not _box_within(s.poly, own)
        and not _box_within(own, s.poly)
    ]
    return soft_index(out, [])


WALL_HALF_PX = 2.0
"""A dark stroke this wide (half-width, px) or wider is a wall to a leader: the sheets' walls and court dividers are 6-9
px strokes; a partition, a rope or a hatching line is 1 px or less.

Research: wall stroke test - CONVENTION: a dark stroke 2 px or more in half-width is a wall a leader may not cross; sheet walls are 6-9 px, partitions 1 px or less - a calibration of the placer, which changes how a leader is drawn"""


#: Width per character, in ems, of a hand sheet's captions by their face (feature 267). The standard's 0.55 holds for the
#: engine's own regular lowercase captions; a hand sheet's ALL-CAPS court names run ~0.70 (the pack audit's own
#: CHAR_W_BOLD for bold caps is 0.72), bold adds ~0.04, and letter-spacing adds its own width per character - the Inari
#: shrine's bold, spaced name was seated a third too narrow, its first letter under the karo's house.
CAPS_W_EM = 0.70
"""Research: caps caption width - NONE: a hand sheet's all-caps captions run about 0.70 em per character, a text-measuring figure."""
BOLD_W_EM = 0.04
"""Research: bold caption width - NONE: bold adds about 0.04 em per character to a caption's width, a text-measuring figure."""


def _as_head(caps: list[Shape], cw: float, per: list[list[str]]) -> list[str]:
    """A caption's lines as the placer measures them - all at the head's size and face - each line standing in for its
    own width: a sub-line in 8 px italic under a 12 px bold name is that much narrower. Measured at the head's face, a
    guest house's note ran 156 px for a 90 px house and its name was seated across the wall (feature 267 round 4)."""
    head = caps[0]
    return [ln if c is head else "x" * max(1, round(len(ln) * c.size * char_w_of(c.element, ln, c.size) / (head.size * cw))) for c, lines in zip(caps, per, strict=True) for ln in lines]


def wraps(caps: list[Shape]) -> list[list[list[str]]]:
    """The layouts a caption of several texts may take, each its texts' lines: as declared, then each one-line text
    wrapped by the standard's own rule (`layouts`) to two lines, then three - one line before two, as the placer tries a
    one-text caption (feature 286: the granary's `staging store - tax grain` and the tally office's `barge manifests
    & seals` fit inside their buildings only wrapped, and unwrapped their names went onto the hearing court). A text the
    sheet already breaks into lines keeps its breaks."""
    out: list[list[list[str]]] = []
    for depth in range(3):
        per = [list(c.lines) if len(c.lines) > 1 else layouts(c.lines[0])[min(depth, len(layouts(c.lines[0])) - 1)] for c in caps]
        if per not in out:
            out.append(per)
    return out


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


def _self_tagged(head: Shape) -> bool:
    """Does the caption's text carry its own `data-kind` (so it is its own group) rather than take one from a group?"""
    return head.element is not None and head.element.get("data-kind") is not None


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


LIGHT = 0.75
"""A fill this light (0-1 luma) is a caption chosen to read on dark ink; it reads on nothing else.

Research: light fill threshold - CONVENTION: a fill of luma 0.75 or lighter is a caption chosen to read on dark ink."""

DARK_INK = "#3A2E1C"
"""The sheets' caption ink."""


def _luma(fill: str | None) -> float:
    """A `#rgb` or `#rrggbb` fill's luma (0 black, 1 white); anything else - none, a pattern - reads as 0.5.

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 0.114 (Rec.601 luma weight (blue)); 16 (hex base); 0.299 (Rec.601 luma weight (red)); 0.587 (Rec.601 luma weight (green))
    """
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


_START_TOKEN = re.compile(r"""<!--.*?-->|<!\[CDATA\[.*?\]\]>|<\?.*?\?>|<!(?:[^\[>]|\[[^\]]*\])*>|<(?:"[^"]*"|'[^']*'|[^'">])*>|[^<]+""", re.S)


# LOCKSTEP (feature 449 T174, `ask:449-engine-order` condition 3): `start_tags` is ported to `rust/mode_a/src/hand_sheet.rs`, which `make size-table`
# runs; an edit of it makes the same change there in the same commit (`parse/lockstep_audit.rs` holds the two equal on every pool sheet).
def start_tags(src: str) -> list[tuple[int, int]]:
    """Where each element's start tag lies in the source, in document order - the order `ET` iterates in, so a Shape's
    `at` is its index here. Comments, declarations and end tags are not elements."""
    # FEATURE 449 T182: the sheet reader's own tokens (`interactive.sheet._TOKEN`), so a CDATA section's tag-like run is no element,
    # an element named outside [A-Za-z] is one, and a `>` in a quoted attribute value does not end its tag - each had shifted the
    # index every later element is paired by
    return [m.span() for m in _START_TOKEN.finditer(src) if m.group(0).startswith("<") and src[m.start() + 1] not in "!?/"]


def captions_of(shapes: list[Shape]) -> list[list[int]]:
    """The sheet's captions, each the list of its `<text>` indices in document order: every text tagged with a kind
    (on itself or a group around it) is a caption, and a text marked `data-cont="1"` is the next line of the caption
    before it (a building's name over its gloss, a note's lines). Untagged and `-` texts are the sheet's own drawing -
    its title and its scale - and are not placed."""
    out: list[list[int]] = []
    for i, s in enumerate(shapes):
        if s.tag != "text" or not s.text or not s.kind or s.kind == "-":
            continue
        if s.cont:
            if not out:
                raise ValueError(f"caption line {s.text!r} is marked data-cont but no caption comes before it")
            out[-1].append(i)
        else:
            out.append([i])
    return out


def declared_parts(head: Shape, shapes: list[Shape], alone: bool) -> list[Shape]:
    """What a caption names, from its declaration alone (feature 286, plan D1): the shapes its `data-names` mark by
    their `data-id` (one on a group marks everything in it; not the SVG `id`, which a sheet shares among shapes on
    purpose - the courts' `precinct`, which the pack audit reads), else - for the one caption of a tagged group - the group's own drawn
    shapes. Where it stands is never read. A caption that declares nothing it can name is refused: it cannot be placed,
    and a caption is never dropped (feature 266)."""
    if head.names:
        want = set(head.names)
        own = [s for s in shapes if s.tag != "text" and not s.leader and s.ids & want]
        missing = want - {i for s in own for i in s.ids}
        if missing:
            raise ValueError(f"caption {head.text!r}: data-names {sorted(missing)} mark no drawn shape")
        return own
    if alone and head.group and not _self_tagged(head):
        own = [s for s in shapes if s.group == head.group and s.tag != "text" and not s.leader]
        if own:
            return own
    raise ValueError(f"caption {head.text!r} ({head.kind}) names nothing: stand it alone in the tagged group it names, or give it data-names")


def _covers(own: list[Shape], box: Poly) -> bool:
    """Do the closed parts fill `box` (STEPPED of it) - one thing whose box is its outline, not blocks in echelon?"""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    closed = [Polygon(s.poly) for s in own if not s.line and len(s.poly) >= 3]
    return bool(closed) and unary_union(closed).area >= STEPPED * _area(box)


def subjects(own: list[Shape], size: float = 0.0) -> list[Subject]:
    """The subjects a caption is tried against, in order (feature 286, plan D2): INSIDE first, the standard's seat for
    an area's name - the one closed shape it names, or the box of parts that fill it, or each block of a stepped
    building, largest first - then BESIDE: the box, or each block of a stepped building, largest first (Hayakawa's
    RESIDENCE had no free seat within reach of its larger block while the other had one). A scatter of glyphs and lines
    (three pines, a moored barge) has no inside, and is named beside the group, else beside any one of its glyphs - only
    beside a glyph where the group spreads wider than the standard's reach at the caption's `size`. An area with no direction
    of its own - a box of parts, an irregular outline - is named level, however long and narrow (feature 449 T184: an area three
    times taller than wide was named along its length, where 0242 keeps an area's caption level); a feature with a direction of its
    own (`_squared`: a drawn rect, an outline whose every corner is square, an ellipse of unequal radii) is turned with the sheet,
    and its name inside it, like a caption beside a turned feature, takes its outline's first edge's angle (feature 449 T188: a
    turned building's roof name was set level), a quarter, half or three-quarter turn keeping it level; beside it, the caption is
    seated off the box of what it names read in that feature's own frame (`_framed`; feature 449 T189: a turned garden holding its
    lantern and a lone turned block among its parts were named level beside, off the upright box). Each subject beside carries the
    drawn ink of what it is read off as its `ink` (`drawn_ink`), which its leader ends on: a subject read off one part - a lone shape,
    a scatter's member, a block of a stepped building - that part's and that of every closed part drawn with its box (`_drawn_as`; T193: a fill and its stroked outline drawn as two elements), and a subject read off a box of several parts every part's
    (feature 449 T191: a leader to a lone L-shaped house was scored to its box's corner over the empty ground of its notch; T192: a
    leader to a disc ended on its drawn box, and one to several parts was scored to their box while `leader_to_ink` drew it to their ink).

    Research:
        a caption's subjects - CONVENTION: inside what it names first, then beside it; a stepped building by its blocks, largest first; a scatter beside its glyphs (feature 286, plan D2)
        an area's caption level - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption naming an area with no direction of its own (a box of parts, an outline with a corner off square, a disc drawn round) is level; the name inside a feature that has a direction of its own - a drawn rect, an outline whose every corner is square (a rectangle, an L-shaped house) or an ellipse of unequal radii, which a turned group turns - takes the feature's own angle, as a turned feature's caption does
        a turned subject's angle - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption naming a turned feature, beside it or inside it, takes its own angle, read off its outline's first edge, and beside it is seated off its turned edge, not off an upright box around it - a lone shape's box, a holder's box of what it holds or a lone block's box of its parts, each read in the feature's own frame, and a scatter's member by its own outline, which the placer's seats read in that member's frame; a feature turned a quarter, a half or three quarters of a turn keeps a level caption
        a lone block's beside box - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a lone block among smaller parts is named beside the box of all its parts read in the block's own frame, not off the block alone - the page's map drawing convention (a block named among loose parts "is seated beside the smallest box holding them all"); the caption names every part, and at level this box is the upright box the caption had (feature 449 T189)
        which subjects carry ink - CONVENTION: every subject beside carries the drawn parts it is read off as the ink its leader ends on - a subject read off one part (a lone shape, a scatter's member, a block of a stepped building) that part and every closed part drawn with its box (a fill and its stroked outline drawn as two elements draw one block), a subject read off a box of several parts every part - so the leader the placer weighs is the one `leader_to_ink` draws; an inside subject carries none, an area's name taking no leader; 0242 has the leader end at the nearest drawn point, and the ink is where that point is read (feature 449 T191, T192, T193)
    """
    x0, y0, x1, y1 = bbox([p for s in own for p in s.poly])
    box = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    closed = [s for s in own if not s.line and len(s.poly) >= 3]
    blocks = sorted((s for s in own if s.tag == "rect" and _area(s.poly) >= BLOCK_PX), key=lambda q: -_area(q.poly))
    holder = max(closed, key=lambda s: _area(s.poly), default=None)
    # every part's drawn ink, which the leader of a subject read off a box of several parts ends on (feature 449 T192)
    every = tuple(drawn_ink(s) for s in own)
    # each inside seat with whether it has a direction of its own - a drawn rect, an outline whose every corner is square, an ellipse
    # of unequal radii (feature 449 T188, T189) - and each beside seat with the same and the drawn ink its leader ends on: only such a
    # feature's caption is turned with it
    inner: list[tuple[Poly, bool]]
    beside: list[tuple[Poly, bool, tuple[InkPart, ...]]]
    if len(own) == 1 and closed:
        squared = _squared(own[0])
        # beside its box in its own frame - a rectangle's own outline, an L-shaped house's turned box (feature 449 T189); its leader to
        # its own drawn outline, not to that box's corner over the empty ground of an L's notch (feature 449 T191) or beside a disc's
        # curve (T192)
        inner, beside = [(own[0].poly, squared)], [(_framed(own[0].poly, _turned(own[0].poly)), True, every) if squared else (box, False, every)]
    elif holder is not None and all(_box_within(s.poly, holder.poly) for s in own):
        # one outline holding the rest - a garden and the lantern in it (Ochiba's inner garden, read as a scatter, was
        # named from outside with a leader across the kitchen) - named beside the box of them all read in the holder's own
        # frame where it has a direction of its own (feature 449 T189: a turned garden was named level beside, off the upright box)
        squared = _squared(holder)
        frame = _turned(holder.poly) if squared else 0.0
        inner, beside = [(holder.poly, squared)], [(_framed([p for s in own for p in s.poly], frame), squared, every)]
    elif _covers(own, box):
        inner, beside = [(box, False)], [(box, False, every)]
    elif blocks:
        # a lone block among small parts is named beside the box of them all read in the block's own frame (feature 449 T189: a
        # lone turned block was named level beside, off the upright box)
        lone = [(_framed([p for s in own for p in s.poly], _turned(blocks[0].poly)), True, every)]
        inner, beside = [(b.poly, True) for b in blocks], [(b.poly, True, _drawn_as(b, own)) for b in blocks] if len(blocks) >= 2 else lone
    else:
        # a scatter of like glyphs - three pines, the fire-water tubs: beside the group, else beside any one of them,
        # largest first (Ochiba's tubs stand all over the compound, and round the box of them all no seat was free).
        # A group wider than the standard's reach at the caption's size has no "beside": a seat by its box is by none
        # of its glyphs (Hayakawa's tubs were named outside the compound's corner)
        # A member with a direction of its own (a turned L-shaped house) goes as its own outline at its angle: the placer's seats
        # read its box in that frame already (placer `_box_frame`), so its `_framed` box would give the same seats, while the
        # association gap and a leader's end, read off the outline, stay on the member's ink (feature 449 T190, measured 2026-11-18)
        members = [(s.poly, _squared(s), _drawn_as(s, own)) for s in sorted(closed, key=lambda s: -_area(s.poly))]
        spread = size > 0 and max(x1 - x0, y1 - y0) > REACH_EM * size
        inner, beside = [], ([] if spread else [(box, False, every)]) + members if len(closed) > 1 else [(box, False, every)]
    out: list[Subject] = []
    for poly, squared in inner:
        # a rectangle's name inside it takes the rectangle's own angle; an area with no direction of its own - a box of parts, an
        # irregular outline - is level
        out.append(Subject("area", tuple(poly), angle=_turned(poly) if squared else 0.0))
    for poly, squared, ink in beside:
        out.append(Subject("point", tuple(poly), angle=_turned(poly) if squared else 0.0, ink=ink))
    return out


def _squared(s: Shape) -> bool:
    """Has this drawn shape a direction of its own, its first edge's: a `<rect>`, an outline `_square_cornered` passes, or an ellipse of
    unequal radii, whose axes a turned group turns - a circle alike, which an unequal scale draws as an ellipse - never a disc drawn
    round, whose turned square box has no direction (the T188 claims round: a disc in a turned group, and a scatter's four-point kite, were
    named at an angle; the plan review's round 3: an ellipse of unequal radii in a turned group was named level, and a circle scaled
    unequally too). The radii are the drawn box's sides, which the reader keeps as the disc's outline. An outline of more corners, each
    square (an L-shaped house), has its edges' direction too (feature 449 T189: a turned L-shaped house drawn as one outline was named
    level, where the same house drawn as two rects took its angle).

    Research:
        a direction of its own - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a caption naming a turned feature is drawn at that feature's own angle and seated off its turned edge, and everything with no direction of its own is labeled level; a drawn rect and an outline of four square corners turn with their group, and an ellipse of unequal radii has its axes turned with it; a disc drawn round, an outline with a corner off square and a four-point kite have no direction
        an outline of square corners - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: an outline of more than four corners, each square (an L-shaped house), has its edges' direction as a rectangle has - the page's map drawing convention ("A turned outline whose every corner is square has a direction of its own"), read so because the same house drawn as two rects takes its angle through its blocks, and naming it level drawn as one outline would repeat the rect-against-outline defect T188 fixed, and because 0242 gives a quarter-turned feature its direction by its edges ("it has a level edge of its own"); the simpler route, an L kept level, was priced and not taken for that inconsistency (feature 449 T189)
    """
    if s.tag == "rect":
        return True
    if s.tag in ("circle", "ellipse"):
        if not _rectangular(s.poly):
            return False
        across, down = math.dist(s.poly[0], s.poly[1]), math.dist(s.poly[1], s.poly[2])
        return abs(across - down) > 1e-6 * max(across, down)  # equal radii, within a turned outline's float slack, are a circle
    return _square_cornered(s.poly)


def _framed(pts: Poly, angle: float) -> list[Pt]:
    """The box of `pts` read in the frame turned `angle` degrees, its first edge along the frame's first axis - the upright box
    itself where the angle is level - so that a caption beside a turned feature is seated off its turned edge (feature 449 T189)."""
    if angle == 0.0:
        x0, y0, x1, y1 = bbox(pts)
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    s, c = math.sin(math.radians(angle)), math.cos(math.radians(angle))
    along = [p[0] * c + p[1] * s for p in pts]
    across = [p[1] * c - p[0] * s for p in pts]
    u0, u1, v0, v1 = min(along), max(along), min(across), max(across)
    return [(u * c - v * s, u * s + v * c) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]


SQUARE_TOL = math.sin(math.radians(1.0))
"""How far from square a corner may stand and the outline still be a rectangle: within a degree, the cosine of the corner's angle under
the sine of one degree (feature 449 T188).

Research: a square corner - CONVENTION: a corner within 1 degree of square, so a turned rectangle drawn by hand to a tenth of a pixel is one"""


def _rectangular(poly: Poly) -> bool:
    """Is this outline a rectangle - four corners, each square within `SQUARE_TOL`, a closing point repeating the first dropped - so
    that it has a direction of its own, its first edge's, however it was drawn (feature 449 T188: a turned rectangle drawn as a polygon
    was named level where the same `<rect>` took its angle)?"""
    return len(poly) - (len(poly) > 1 and poly[0] == poly[-1]) == 4 and _square_cornered(poly)


def _square_cornered(poly: Poly) -> bool:
    """Is every corner of this outline square within `SQUARE_TOL` - four corners or more, a closing point repeating the first dropped -
    a rectangle or an L- or T-shaped house, whose edges all run along one turned frame and give it a direction of its own (feature 449
    T189: a turned L-shaped house drawn as one outline was named level, where the same house drawn as two rects took its angle)?"""
    pts = list(poly[:-1]) if len(poly) > 1 and poly[0] == poly[-1] else list(poly)
    n = len(pts)
    if n < 4:
        return False
    for k in range(n):
        a, b, c = pts[k - 1], pts[k], pts[(k + 1) % n]
        u, v = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        nu, nv = math.hypot(*u), math.hypot(*v)
        if not nu or not nv or abs(u[0] * v[0] + u[1] * v[1]) / (nu * nv) > SQUARE_TOL:
            return False
    return True


def _turned(poly: Poly) -> float:
    """A turned feature's angle as its caption takes it: its outline's first edge's, level where the turn is a quarter, a half or three
    quarters (within a millionth of a degree, the float slack of a turned outline's edge).

    Research:
        a quarter turn keeps a level caption - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a feature turned a quarter, a half or three quarters of a turn keeps a level caption
        which edge gives the angle - CONVENTION: the outline's first edge, where a square-cornered outline has two perpendicular edges and 0242 does not say which a caption runs along (feature 449 T189)
    """
    ang = math.degrees(math.atan2(poly[1][1] - poly[0][1], poly[1][0] - poly[0][0]))
    return 0.0 if abs(ang - 90.0 * round(ang / 90.0)) < 1e-6 else ang


def seat(src: str) -> list[tuple[list[Shape], Placement, list[list[str]]]]:
    """Every caption on a sheet placed by the one placer, each avoiding the others: the caption's texts, its placement
    and its texts' lines as placed, in document order. A caption is tried against each of its `subjects` in turn, the
    first free seat winning, else the least cost; a name in light ink (chosen for a dark roof) may sit on its subject's
    dark fill, and a name in the sheet's dark ink may not.

    The ORDER (feature 286): open ground's names first, as a cartographer sets the major area names before the small
    ones fill in around them (a court's name placed after them found its open ground taken, and was led out past the
    wall - Ubame's OUTER COURT); then, points before areas, the names that must stand BESIDE their subject, then those
    that fit inside it, then the glyphs standing in a named ground; each tier in document order. In document order
    alone Ochiba's garrison latrine found its one free seat taken by a building's name placed before it; smallest subject
    first, Hayakawa's RESIDENCE, placed last, found every seat taken; and a glyph named before the ground it stands in
    took the ground's inside (Hayakawa's weapon rack and striking posts, whose practice ground's name went into the
    empty tally office beside it). Then `repair`: a greedy order still strands a caption now and then, so each caption
    left covering ink is tried with one neighbor lifted, and the pair is kept where the two together cover less. A caption
    of several texts is tried in each of its `wraps`, the first free one winning; where none clears it goes back to its
    declared lines, the cheapest seat of those (feature 449 T184: it kept the cheapest of all its wraps). A ground's name stays in its
    ground unless every seat there covers another name; an inside seat that covers a building gives way to a seat beside that covers
    no building - free, or on soft ink or a lane alone - and to nothing else (feature 449 T188: the break kept it over a free seat, and
    then over a seat on a lane alone).

    Research:
        a stranded several-text caption's wrap - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a wrap is taken only where it clears; if nothing clears, the caption goes back to its declared lines
        a ground's name stays in its ground - research/questions/0242-labels-on-maps-cartographic-label-placement.drawing.html: a ground's name is set inside the ground it names, as an area caption is, unless every seat there covers another name; an inside seat covering a building - read off its cost, a drawn obstacle's or more, the placement carrying no more - is kept only while no seat beside covers no building - a free seat, or one on soft ink or a lane alone, under a drawn obstacle's cost - as a building is never covered while any other choice exists
        the order captions are set - CONVENTION: open ground's names first, then the names that must stand beside their subject, then those that fit inside it, then the glyphs standing in a named ground, each tier in document order - the major area names before the small ones fill in around them, as a cartographer sets them (feature 286)
    """
    shapes, view = read_sheet(src)
    caps_of = captions_of(shapes)
    skip = {i for idx in caps_of for i in idx}
    per_group: dict[int, int] = {}
    for idx in caps_of:
        per_group[shapes[idx[0]].group] = per_group.get(shapes[idx[0]].group, 0) + 1
    owns = {idx[0]: declared_parts(shapes[idx[0]], shapes, alone=per_group[shapes[idx[0]].group] == 1) for idx in caps_of}
    named = frozenset(shapes[idx[0]].kind for idx in caps_of)
    grounds = [bbox([p for s in owns[idx[0]] for p in s.poly]) for idx in caps_of if shapes[idx[0]].kind in GROUND_KINDS]

    def order(idx: list[int]) -> tuple[int, float]:
        # a scatter's box has no inside, however large (Ochiba's tubs span the compound)
        x0, y0, x1, y1 = bbox([p for s in owns[idx[0]] for p in s.poly])
        if any(s.kind == "area" for s in subjects(owns[idx[0]], shapes[idx[0]].size)) and fits_inside([shapes[i] for i in idx], owns[idx[0]]):
            # open ground's names first (see the docstring); a named ground in them weighs as a name (`classify`), so a
            # court's name placed first no longer takes the practice ground
            return (-1, 0.0) if shapes[idx[0]].kind in GROUND_KINDS else (1, 0.0)
        return (3, 0.0) if any(g[0] <= x0 and g[1] <= y0 and x1 <= g[2] and y1 <= g[3] and (x1 - x0) * (y1 - y0) < (g[2] - g[0]) * (g[3] - g[1]) for g in grounds) else (0, 0.0)

    bases: dict[tuple[int, int], ObstacleIndex] = {}

    def one(idx: list[int], others: list[tuple[Placement, float]], quick: bool = False) -> tuple[Placement, list[list[str]]]:
        caps = [shapes[i] for i in idx]
        head = caps[0]
        own = owns[idx[0]]
        text = " ".join(ln for c in caps for ln in c.lines)
        cw = char_w_of(head.element, head.text, head.size)
        light = _luma(head.element.get("fill") if head.element is not None else None) > LIGHT
        best: Placement | None = None
        best_per = [list(c.lines) for c in caps]
        held = [(caps, p) for p, _size in others]
        kept_inside = False  # a ground's name holding an inside seat that covers a building, which only a seat covering no building may replace
        for k, sub in enumerate(subjects(own, head.size)):
            # each caption's own index: the ground drawn after it is an obstacle to IT (see `classify`), and every
            # caption placed is one, with its leader
            if (idx[0], k) not in bases:
                bases[idx[0], k] = classify(shapes, view, skip, after=idx[0], group=head.group, kind=head.kind, subject=list(sub.poly), area=sub.kind == "area", dark_inside=not light, named=named)
            base = bases[idx[0], k]
            index = ObstacleIndex(list(base.obstacles), list(base.ways))
            for done, size in others:
                # each placed caption keeps its own clearance too (`Obstacle.keep`)
                index.add(Obstacle(done.block, WEIGHT_TEXT, keep=CLEAR_EM * size))
                if done.leader is not None:
                    index.add(Obstacle(tuple(_band(done.leader[0], done.leader[1], 1.0)), WEIGHT_TEXT))
            lead = leader_blockers(shapes, skip, held, sub, own)
            # a one-text caption is wrapped by the placer itself; a caption of several texts is tried in each of its
            # `wraps`, each line measured at its own size
            for w, per in enumerate(wraps(caps) if len(caps) > 1 else [best_per]):
                lines = _as_head(caps, cw, per) if len(caps) > 1 else None
                sizes = [c.size for c, ls in zip(caps, per, strict=True) for _ in ls] if len(caps) > 1 else None
                p = place(text, head.size, sub, index, view, lines=lines, char_w=cw, leader_index=lead, line_sizes=sizes, extended=not quick)
                # a wrap is taken only where it clears; with none clearing, the caption goes back to its declared lines (0242,
                # feature 449 T184: it kept the cheapest of all its wraps)
                if (p.cost == 0.0 or (w == 0 and (not kept_inside or p.cost < WEIGHT_OBSTACLE))) and (best is None or p.cost < best.cost):
                    best, best_per = p, per
                if p.cost == 0.0:
                    break
            if best is not None and best.cost == 0.0:
                break
            if head.kind in GROUND_KINDS and sub.kind == "area" and best is not None and best.position == "inside" and best.cost < WEIGHT_TEXT:
                # a ground's name stays in its ground unless every seat there covers another name: led out from beyond
                # the wall, Ubame's OUTER COURT named the gate range it crossed (feature 286; Imhof - an area is named
                # inside it). A building too small for its name still goes beside it. An inside seat covering a building (a
                # cost of a drawn obstacle or more) is kept only while no seat beside covers no building: 0242 covers a building
                # only where no other choice exists (feature 449 T188: the break kept it over a free seat on a later subject)
                if best.cost < WEIGHT_OBSTACLE:
                    break
                kept_inside = True
        assert best is not None
        return leader_to_ink(best, own), best_per

    done: dict[int, tuple[Placement, list[list[str]]]] = {}
    for idx in sorted(caps_of, key=order):
        done[idx[0]] = one(idx, [(p, shapes[k].size) for k, (p, _) in done.items()])
    by_head = {idx[0]: idx for idx in caps_of}
    boxes = {k: bbox([p for s in owns[k] for p in s.poly]) for k in done}
    repair(done, boxes, {k: shapes[k].size for k in done}, lambda k, rest, quick=False: one(by_head[k], rest, quick))
    return [([shapes[i] for i in idx], *done[idx[0]]) for idx in caps_of]


Seated = tuple[Placement, list[list[str]]]


def repair(done: dict[int, Seated], boxes: dict[int, tuple[float, float, float, float]], sizes: dict[int, float], one: Callable[..., Seated]) -> None:
    """The greedy pass's repair (feature 286): each caption left covering ink is re-placed with one neighbor lifted - a
    caption whose block lies within `REPAIR` ems plus its own length of the subject's box - and the neighbor re-placed
    after it; the pair is kept where the two together cover less (a neighbor may move to a seat covering a little so a
    stranded caption covers nothing). `one(key, others, quick)` places a caption against the others' placements, each
    with its caption's size; `quick`
    tries the standard's seats only - a lift that frees a caption frees one of them, and the fallback search is the
    expensive half of a stranded caption's search (a full search per lift ran past ten minutes on Hayakawa). A chain of
    three lifts was tried for Ochiba's tubs and freed nothing more; it was taken out (2026-09-28)."""
    for a in list(done):
        if done[a][0].cost == 0.0:
            continue
        block = done[a][0].block
        reach = REPAIR * sizes[a] + max(math.dist(block[0], block[1]), math.dist(block[1], block[2]))
        x0, y0, x1, y1 = boxes[a]
        near = [b for b in done if b != a and _box_gap(list(done[b][0].block), [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]) <= reach]
        for b in near:
            rest = [(p, sizes[k]) for k, (p, _) in done.items() if k not in (a, b)]
            pa = one(a, rest, True)
            if pa[0].cost >= done[a][0].cost:
                continue
            pb = one(b, [*rest, (pa[0], sizes[a])])
            if pa[0].cost + pb[0].cost < done[a][0].cost + done[b][0].cost:
                done[a], done[b] = pa, pb
                break


REPAIR = 2.0
"""How far from a stranded caption's subject a neighbor is lifted to free a seat for it: this many ems of its size, plus
the caption's own length - the near rings, where the standard's preferred seats lie (a calibration: at the standard's
whole reach, eight ems, a lift was tried for every caption in a court).

Research: caption repair reach - CONVENTION: a neighbor within 2 ems of a stranded caption's subject (plus the caption's length) is lifted to free a seat; a calibration of the placer."""


def fits_inside(caps: list[Shape], own: list[Shape]) -> bool:
    """Could a caption's block stand inside the box of what it names - its widest line and its lines' height, at their
    own sizes and faces, within the box less the standard's gap on every side? The ORDER's test, not a seat's: a caption
    that cannot is placed before those that can."""
    x0, y0, x1, y1 = bbox([p for s in own for p in s.poly])
    w = max(len(ln) * c.size * char_w_of(c.element, ln, c.size) for c in caps for ln in c.lines)
    h = sum(PITCH_EM * c.size * len(c.lines) for c in caps)
    gap = 2 * CLEAR_EM * caps[0].size
    return w + gap <= x1 - x0 and h + gap <= y1 - y0


def element_end(src: str, a: int, b: int) -> int:
    """Where the element whose start tag spans `a:b` ends: past its own end tag, found by the start tag's own name - `</text>`,
    or `</s:text>` for a caption written with a prefix bound to the SVG namespace (feature 449 T184: `src.index("</text>")`
    refused a prefixed caption, or wrote it over through the next caption's end). A sheet the XML reader read whole never
    lacks the end tag; its absence is refused by name."""
    name = _tag_name(src, a, b)
    m = re.compile(rf"</{re.escape(name)}[ \t\r\n]*>").search(src, b)
    if m is None:
        raise ValueError(f"the caption's <{name}> has no end tag")
    return m.end()


def _tag_name(src: str, a: int, b: int) -> str:
    """The name the start tag spanning `a:b` is written under - `text`, or `s:text` with a prefix."""
    return re.match(r"[^\s/>]*", src[a + 1 : b]).group(0)  # type: ignore[union-attr]


def _prefix(src: str, a: int, b: int) -> str:
    """The namespace prefix the start tag spanning `a:b` is written with, its colon kept (`s:`), or the empty string."""
    name = _tag_name(src, a, b)
    return name[: name.index(":") + 1] if ":" in name else ""


def in_prefix(svg: str, prefix: str) -> str:
    """A written caption or leader (`caption_svg`, `leader_svg`) under the prefix its own element was written with: a caption declared as
    `<s:text>` on a sheet binding SVG only to `s` is written back as `<s:text>`, its lines `<s:tspan>` and its leader `<s:line>` (feature
    449 T188: written as a plain `<text>`, it fell into no namespace and was drawn by no renderer). The writer's own text escapes every
    `<` it carries, so each `<` opens one of its three elements."""
    return re.sub(r"<(/?)(text|tspan|line)\b", rf"<\g<1>{prefix}\g<2>", svg) if prefix else svg


_STYLE = ("font-style", "font-weight", "letter-spacing", "paint-order", "stroke", "stroke-width")


def placed(src: str) -> str:
    """The sheet with every caption written where the placer put it, and its leader drawn after it (feature 286, plan
    D5): what a sheet's picture and page are rendered from. The tracked sheet is the drawing and the declarations; this
    is a function of them alone."""
    ground, view = read_sheet(src)
    tags = start_tags(src)
    # FEATURE 449 T182: a caption is paired with its start tag by its index, so the two lists must be one length - an entity that
    # expands to markup draws an element the source writes no tag for, and every later caption would be written at the wrong tag
    if len(tags) != sum(1 for _ in ET.fromstring(src).iter()):
        raise ValueError("the sheet's elements and its start tags disagree - an entity that expands to markup draws an element the source does not write; write the element out")
    edits: list[tuple[int, int, str]] = []
    for caps, p, per in seat(src):
        head = caps[0]
        fill = (head.element.get("fill") if head.element is not None else None) or DARK_INK
        centers = _line_centers(p, [c.size for c in caps], [len(ls) for ls in per])
        news: list[tuple[int, int, str]] = []
        for cap, cap_lines, (cx, cy) in zip(caps, per, centers, strict=True):
            el = cap.element
            assert el is not None
            style = "".join(f' {a}="{el.get(a)}"' for a in _STYLE if el.get(a))
            # a one-text caption takes the placement's LINES - the standard may wrap it
            lines = tuple(p.lines) if len(caps) == 1 else tuple(cap_lines)
            # written in the text's PARENT frame: a caption inside a translated group is written in that group's
            # coordinates (feature 267)
            lx, ly = _apply(_inverse(cap.frame), (cx, cy))
            at = Placement(lx, ly + CENTER_ABOVE_BASELINE_EM * cap.size, p.angle - _angle(cap.frame), lines, p.block, p.ring, p.rank, p.position, p.cost, None)
            ink = el.get("fill", fill)
            if _luma(ink) > LIGHT and not _on_dark((cx, cy), ground):
                ink = DARK_INK  # a light name chosen for a dark roof, set down on light ground (feature 267)
            # a text carrying its OWN tag keeps it (it is its own group); one taking its tag from a group stays untagged
            a, b = tags[cap.at]
            end = element_end(src, a, b)
            prefix = _prefix(src, a, b)
            news.append((a, end, in_prefix(caption_svg(at, cap.size, style, ink, cap.kind if el.get("data-kind") else ""), prefix)))
        if p.leader is not None:
            inv = _inverse(head.frame)
            local = replace(p, leader=(_apply(inv, p.leader[0]), _apply(inv, p.leader[1])))
            a, end, new = news[-1]
            news[-1] = (a, end, new + "\n    " + in_prefix(leader_svg(local, head.size, fill, head.kind if _self_tagged(head) else "", mark=True), prefix))
        edits += news
    out = src
    for a, end, new in sorted(edits, reverse=True):
        out = out[:a] + new + out[end:]
    return out


def render(src: str, png: str) -> None:
    """Render a sheet's placed text to `png` with resvg, as every sheet's gen does - from a temporary file beside the
    picture, removed after.

    Research: the sheets' face and width - CONVENTION: every sheet's picture is drawn 2400 px wide, its serif lettering in `DejaVu Serif` - a display choice of the sheets, not of the world
    """
    import subprocess
    import tempfile

    fd, tmp = tempfile.mkstemp(suffix=".svg", dir=str(Path(png).parent))
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write(src)
        subprocess.run(["resvg", "--width", "2400", "--serif-family", "DejaVu Serif", tmp, png], check=True)
    finally:
        Path(tmp).unlink()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render a hand-drawn sheet with its captions placed by the one placer (feature 286).")
    ap.add_argument("sheet")
    ap.add_argument("out", help="the PNG to write")
    args = ap.parse_args(argv)
    render(placed(Path(args.sheet).read_text(encoding="utf-8")), args.out)
    print(f"sheet-render: {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover - the make target's entry
    sys.exit(main())
