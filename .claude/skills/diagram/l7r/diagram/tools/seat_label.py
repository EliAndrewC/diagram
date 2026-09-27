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

    python3 -m l7r.diagram.tools.seat_label pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg --check
"""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from l7r.diagram.labels import Obstacle, ObstacleIndex, Placement, Subject, Way, place
from l7r.diagram.labels.geom import Poly, Pt, bbox, inside, rect
from l7r.diagram.labels.standard import CENTER_ABOVE_BASELINE_EM, PITCH_EM, WEIGHT_OBSTACLE, WEIGHT_WAY, block_half
from l7r.diagram.labels.svg import caption_svg, leader_svg

SVG = "{http://www.w3.org/2000/svg}"

WAY_KINDS = frozenset({"road", "river", "revetment"})
"""The kinds a caption may cross at a way's weight (plan P4, observed 2026-09-27, method: the tag census of the six
sheets - roads are stroked paths 18 to 40 px wide)."""

GROUND_KINDS = frozenset(
    {"outer court", "inner court", "hearing court", "border court", "practice ground", "garden", "vegetable garden", "garden pines", "cart yard", "shrine grove", "river landing"}
)
"""The sheets' open ground - free space to a caption (plan P4). An explicit list: a name that merely CONTAINS "court"
is not ground (`court divider` is a wall), and a roofed floor on posts (`weighing floor`) is built."""

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

    def walk(el: ET.Element, m: Affine, kind: str, stroke_w: float, stroked: bool, group: int) -> None:
        m = _mul(m, parse_transform(el.get("transform")))
        if el.get("data-kind") is not None:
            kind, group = el.get("data-kind", kind), id(el)  # the tagged element a caption and its subject share
        stroke_w = _f(el, "stroke-width", stroke_w)
        if el.get("stroke") is not None:
            stroked = el.get("stroke") != "none"
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
            t.group = group
            shapes.append(t)
            return
        if len(pts) >= 2:
            tp = [_apply(m, p) for p in pts]
            if line:
                shapes.append(Shape(tag, kind, tp, stroke_w / 2, True, element=el, leader=el.get("data-leader") == "1", group=group))
            else:
                x0, y0, x1, y1 = bbox(tp)
                shapes.append(Shape(tag, kind, tp if len(tp) >= 3 else [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], element=el, group=group))
        for c in el:
            walk(c, m, kind, stroke_w, stroked, group)

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
    bw, bh = block_half(lines, size)
    pitch = PITCH_EM * size
    cx = x if anchor == "middle" else (x - bw if anchor == "end" else x + bw)
    cy = y + (len(lines) - 1) * pitch / 2 - CENTER_ABOVE_BASELINE_EM * size
    c = _apply(m, (cx, cy))
    ang = _angle(m)
    return Shape("text", kind, rect(c[0], c[1], bw, bh, ang), text=" ".join(lines), size=size, angle=ang, element=el, center=c, lines=lines)


def _is_background(s: Shape, view: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = bbox(s.poly)
    return s.kind == "-" and s.tag == "rect" and x0 <= view[0] and y0 <= view[1] and x1 >= view[2] and y1 >= view[3]


def classify(shapes: list[Shape], view: tuple[float, float, float, float], skip: set[int] = frozenset()) -> ObstacleIndex:  # type: ignore[assignment]
    """The sheet as the placer sees it (plan P4). `skip` holds the captions being placed, which are not obstacles to
    themselves."""
    obstacles: list[Obstacle] = []
    ways: list[Way] = []
    for i, s in enumerate(shapes):
        if i in skip or s.leader:
            continue
        if s.tag == "text":
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_OBSTACLE))
        elif s.kind in GROUND_KINDS or _is_background(s, view):
            continue
        elif s.kind in WAY_KINDS:
            if s.line:
                ways.append(Way(tuple(s.poly), max(s.half, 0.5)))
            else:
                obstacles.append(Obstacle(tuple(s.poly), WEIGHT_WAY))
        elif s.line:
            for a, b in zip(s.poly, s.poly[1:], strict=False):
                obstacles.append(Obstacle(tuple(_band(a, b, max(s.half, 0.5))), WEIGHT_OBSTACLE))
        else:
            obstacles.append(Obstacle(tuple(s.poly), WEIGHT_OBSTACLE))
    return ObstacleIndex(obstacles, ways)


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
    if not own:
        same = [s for s in shapes if s.kind == caption.kind and s.tag != "text" and not s.leader]
        if not same:
            return None
        own = [min(same, key=lambda s: math.dist(_mid(s.poly), caption.center))]
    if len(own) == 1 and own[0].tag == "rect":
        poly = own[0].poly
    else:
        x0, y0, x1, y1 = bbox([p for s in own for p in s.poly])
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    ang = math.degrees(math.atan2(poly[1][1] - poly[0][1], poly[1][0] - poly[0][0])) if len(poly) == 4 else 0.0
    area = inside(caption.center[0], caption.center[1], poly)
    return Subject("area" if area else "point", tuple(poly), angle=0.0 if area else ang)


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
    """The sheet's captions, each the list of its `<text>` indices: every text of one tagged group is one caption, its
    lines in document order (a board's name with the bill posted under it is one caption of two lines)."""
    groups: dict[int, list[int]] = {}
    order: list[int] = []
    for i, s in enumerate(shapes):
        if s.tag == "text" and s.text and s.kind and s.kind != "-" and (kinds is None or s.kind in kinds):
            key = s.group or -i - 1
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(i)
    return [groups[k] for k in order]


def seat(src: str, kinds: set[str] | None = None) -> tuple[list[Finding], list[tuple[list[Shape], Placement]]]:
    """Every caption on a sheet (of `kinds`, or all), placed in document order; the findings, and each caption's texts
    with its standard placement."""
    shapes, view = read_sheet(src)
    pairs = [(idx, subject_of(shapes[idx[0]], shapes)) for idx in captions_of(shapes, kinds)]
    pairs = [(idx, sub) for idx, sub in pairs if sub is not None]
    index = classify(shapes, view, {i for idx, _ in pairs for i in idx})
    findings: list[Finding] = []
    placed: list[tuple[list[Shape], Placement]] = []
    leaders = {s.group: s for s in shapes if s.leader}
    for idx, sub in pairs:
        caps = [shapes[i] for i in idx]
        head = caps[0]
        lines = [ln for c in caps for ln in c.lines]
        p = place(" ".join(lines), head.size, sub, index, view, lines=lines if len(caps) > 1 else None)
        index.add(Obstacle(p.block, WEIGHT_OBSTACLE))
        placed.append((caps, p))
        want = _line_centers(p, head.size, [len(c.lines) for c in caps])
        off = any(math.dist(w, c.center) > TOLERANCE for w, c in zip(want, caps, strict=True))
        if off or abs(((head.angle - p.angle + 90) % 180) - 90) > 0.5 or (len(caps) == 1 and tuple(head.lines) != p.lines):
            findings.append(Finding(head.kind, head.text, "off its standard seat", p))
        have = leaders.get(head.group) if head.group else None
        if p.leader is None and have is not None:
            findings.append(Finding(head.kind, head.text, "a stray leader", p))
        elif p.leader is not None and (have is None or max(math.dist(have.poly[0], p.leader[0]), math.dist(have.poly[-1], p.leader[1])) > TOLERANCE):
            findings.append(Finding(head.kind, head.text, "a missing or misplaced leader", p))
    return findings, placed


def _line_centers(p: Placement, size: float, counts: list[int]) -> list[Pt]:
    """Where the center of each of a caption's `<text>` blocks stands in a placement: the block's lines split among
    the texts in order, each text's block centered on its own lines, all turned with the caption."""
    n = sum(counts)
    pitch = PITCH_EM * size
    a = math.radians(p.angle)
    cx, cy = p.x, p.y - CENTER_ABOVE_BASELINE_EM * size
    out: list[Pt] = []
    k = 0
    for c in counts:
        mid = (k + (c - 1) / 2) - (n - 1) / 2  # this text's middle line, in lines from the block's middle
        dy = mid * pitch
        out.append((cx - dy * math.sin(a), cy + dy * math.cos(a)))
        k += c
    return out


def rewrite(src: str, kinds: set[str] | None = None) -> str:
    """The sheet with every caption (of `kinds`) moved to its standard seat and its leader written, moved or removed."""
    _findings, placed = seat(src, kinds)
    out = src
    for caps, p in placed:
        head = caps[0]
        fill = (head.element.get("fill") if head.element is not None else None) or "#3A2E1C"
        centers = _line_centers(p, head.size, [len(c.lines) for c in caps])
        news: list[str] = []
        for cap, (cx, cy) in zip(caps, centers, strict=True):
            el = cap.element
            assert el is not None
            style = "".join(f' {a}="{el.get(a)}"' for a in ("font-style", "font-weight", "paint-order", "stroke", "stroke-width") if el.get(a))
            sub = Placement(cx, cy + CENTER_ABOVE_BASELINE_EM * cap.size, p.angle, tuple(cap.lines), p.block, p.ring, p.rank, p.position, p.cost, None)
            new = caption_svg(sub, cap.size, style, el.get("fill", fill), "" if head.group else cap.kind)
            old = _element_source(out, el)
            if old:
                out = out.replace(old, new, 1)
                news.append(new)
        out = re.sub(rf'\s*<line[^>]*data-kind="{re.escape(head.kind)}"[^>]*data-leader="1"[^>]*/>', "", out) if not head.group else _drop_group_leader(out, news)
        if p.leader is not None and news:
            out = out.replace(news[-1], news[-1] + "\n    " + leader_svg(p, head.size, fill, "", mark=True), 1)
    return out


def _drop_group_leader(src: str, news: list[str]) -> str:
    """Remove the leader line that follows a caption's last text, if it has one."""
    if not news:
        return src
    return re.sub(re.escape(news[-1]) + r'\s*<line[^>]*data-leader="1"[^>]*/>', lambda m: news[-1], src, count=1)


def _element_source(src: str, el: ET.Element) -> str:
    """The `<text ...>...</text>` in the source that `el` was parsed from - found by its text and its x and y."""
    body = re.escape((el.text or "").strip())
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
