"""Every drawn element of a Mode A sheet with its KIND, the kinds it is a part of, and its inherited paint (feature 294).

WHY A SECOND READER. `parse.py` classifies rects by fill and keys each one's kind by its byte offset, which is enough
for a check that asks "is there a latrine" or "how big is the kitchen". The program checks of feature 294 (B16-B23) ask
what a mark BELONGS to: a door drawn inside the karo's house's group is that house's entrance, a privy tagged
`data-part-of="residence"` is the house's own, a road is a stroked path whose width is inherited from nothing but its
own attributes. So this walks the tree `interactive.sheet.parse` builds - the one reader that already knows `data-kind`
and `data-part-of` - and hands each element over with its lineage and the presentation attributes it inherits.

A `translate(...)` on an ancestor is applied (a glyph authored in local coordinates is ink where its group puts it,
the same walk as `shared.ink_bounds`); any other transform is not, as `parse.py` applies none.
"""

from __future__ import annotations

# LOCKSTEP (feature 449 T170, `ask:449-engine-order` condition 3): this module is ported to `rust/mode_a/src/tagged.rs`, which `make notes-census`
# runs; an edit here makes the same change there in the same commit, and `make rust-test CRATE=rust/mode_a` fails until it does
# (`parse/lockstep.rs` holds the two equal on every pool sheet).

import re
from dataclasses import dataclass, field
from functools import lru_cache

from ...interactive.sheet import DEFS, Node, parse

#: An attribute and its value, in either quote (feature 449 T182: a single-quoted attribute read as absent).
_ATTR = re.compile(r"""([\w:-]+)\s*=\s*(["'])([^<]*?)\2""")
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_TRANSLATE = re.compile(r"translate\(\s*(-?[\d.]+)[\s,]*(-?[\d.]+)?\s*\)")
_PATH_CMD = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")
_INNER_TAG = re.compile(r"<[^>]*>")
#: the presentation attributes a child inherits from its group (SVG's own inheritance)
#: (feature 449 T182: "stroke-dasharray" too, SVG's own inheritance, so a check tells a dashed sliding partition from a solid wall)
INHERITED: tuple[str, ...] = ("fill", "stroke", "stroke-width", "font-size", "font-weight", "font-style", "stroke-dasharray")
_SKIP = {DEFS, "pattern", "symbol", "clipPath", "mask", "marker"}


@dataclass(frozen=True)
class Mark:
    """One drawn element: its tag, its kind (its own `data-kind`, else its nearest tagged ancestor's), every kind and
    `data-part-of` above and on it (outermost first), its paint, its box (px) and, for a path or a line, its points."""

    tag: str
    kind: str | None
    lineage: tuple[str, ...]
    x: float
    y: float
    w: float
    h: float
    pos: int
    paint: dict[str, str] = field(default_factory=dict, hash=False, compare=False)
    pts: tuple[tuple[float, float], ...] = ()
    text: str = ""
    ident: str = ""
    placed: bool = True  # False for a caption DECLARED without `x` - the render pipeline places it (feature 286)

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def fill(self) -> str:
        return self.paint.get("fill", "")

    @property
    def stroke_width(self) -> float:
        m = _NUM.match(self.paint.get("stroke-width", "") or "")
        return float(m.group(0)) if m else 0.0

    @property
    def font_size(self) -> float:
        m = _NUM.match(self.paint.get("font-size", "") or "")
        return float(m.group(0)) if m else 0.0

    def belongs_to(self, kind: str) -> bool:
        """The mark is `kind` or a part of it - drawn inside its group, or tagged `data-part-of` it."""
        return self.kind == kind or kind in self.lineage


#: A path's number: a sign, digits with or without a point, an exponent (feature 449 T182: `-?\d+(?:\.\d+)?` read `1e1` as two
#: numbers and `.5` as `5`).
_PATH_NUM = re.compile(r"[-+]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?")
#: How many numbers one segment of each command takes.
_PATH_STEP = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7}


def path_walk(d: str) -> list[tuple[str, list[tuple[float, float]]]]:
    """Each segment of a path, in order, as its command (upper case) and its points made ABSOLUTE - every coordinate pair it gives
    (a curve's control points and its end), an arc its end alone, a horizontal or vertical step the point it reaches. A relative
    command's pairs are offsets from the segment's start, a `Z` returns to its subpath's start, and a command's numbers repeat it
    segment by segment (feature 449 T182: the relative commands were skipped, and a repeated curve kept only its last end).

    Research:
        its salts, guards and sentinels - NONE: they decide nothing about the place - 7 (SVG arc arguments); 6 (SVG curve arguments)
    """
    out: list[tuple[str, list[tuple[float, float]]]] = []
    x = y = sx = sy = 0.0
    for cmd, body in _PATH_CMD.findall(d):
        up, rel = cmd.upper(), cmd.islower()
        if up == "Z":
            x, y = sx, sy
            continue
        nums = [float(n) for n in _PATH_NUM.findall(body)]
        step = _PATH_STEP[up]
        for i in range(0, len(nums) - step + 1, step):
            v = nums[i : i + step]
            if up == "H":
                x = x + v[0] if rel else v[0]
                pts = [(x, y)]
            elif up == "V":
                y = y + v[0] if rel else v[0]
                pts = [(x, y)]
            elif up == "A":
                pts = [(x + v[5], y + v[6]) if rel else (v[5], v[6])]
            else:
                pts = [(x + v[k], y + v[k + 1]) if rel else (v[k], v[k + 1]) for k in range(0, step, 2)]
            x, y = pts[-1]
            if up == "M" and i == 0:
                sx, sy = x, y
            out.append((up, pts))
    return out


def path_points(d: str) -> tuple[tuple[float, float], ...]:
    """The points a path visits, in order: each segment's end, made absolute (`path_walk`)."""
    return tuple(pts[-1] for _cmd, pts in path_walk(d))


def _num(attrs: dict[str, str], key: str) -> float:
    m = _NUM.match(attrs.get(key, "") or "")
    return float(m.group(0)) if m else 0.0


def _box(name: str, a: dict[str, str], dx: float, dy: float) -> tuple[float, float, float, float, tuple[tuple[float, float], ...]] | None:
    """(x, y, w, h, points) of one element, or None for an element that draws nothing a check measures."""
    if name == "rect":
        return _num(a, "x") + dx, _num(a, "y") + dy, _num(a, "width"), _num(a, "height"), ()
    if name in ("circle", "ellipse"):
        rx, ry = (_num(a, "r"), _num(a, "r")) if name == "circle" else (_num(a, "rx"), _num(a, "ry"))
        return _num(a, "cx") + dx - rx, _num(a, "cy") + dy - ry, 2 * rx, 2 * ry, ()
    if name in ("line", "path", "polyline", "polygon"):
        if name == "line":
            pts: tuple[tuple[float, float], ...] = ((_num(a, "x1"), _num(a, "y1")), (_num(a, "x2"), _num(a, "y2")))
        elif name == "path":
            pts = path_points(a.get("d", ""))
        else:
            nums = [float(n) for n in _NUM.findall(a.get("points", ""))]
            pts = tuple(zip(nums[0::2], nums[1::2], strict=False))
        if not pts:
            return None
        pts = tuple((px + dx, py + dy) for px, py in pts)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), pts
    if name == "text":
        return _num(a, "x") + dx, _num(a, "y") + dy, 0.0, 0.0, ()
    return None


@lru_cache(maxsize=16)
def marks(svg: str) -> tuple[Mark, ...]:
    """Every drawn element of the sheet in document order (definitions skipped), each with its kind and lineage.

    Research:
        its cache size - NONE: a memo's size, which decides nothing about the place - 16
    """
    out: list[Mark] = []

    def visit(node: Node, kind: str | None, lineage: tuple[str, ...], paint: dict[str, str], dx: float, dy: float) -> None:
        if not node.name or node.name in _SKIP:
            return
        a = {k: v for k, _q, v in _ATTR.findall(node.open)}
        own = node.kind if node.kind is not None else kind
        lineage = lineage + tuple(k for k in (node.part_of, node.kind) if k is not None)
        paint = {**paint, **{k: a[k] for k in INHERITED if k in a}}
        m = _TRANSLATE.search(a.get("transform", ""))
        if m:
            dx, dy = dx + float(m.group(1)), dy + float(m.group(2) or 0.0)
        box = _box(node.name, a, dx, dy)
        if box is not None:
            x, y, w, h, pts = box
            text = " ".join(_INNER_TAG.sub(" ", node.source()).split()) if node.name == "text" else ""
            placed = node.name != "text" or "x" in a
            out.append(Mark(node.name, own, lineage, x, y, w, h, node.start, paint, pts, text, a.get("id", ""), placed))
        if node.name != "text":
            for child in node.children:
                visit(child, own, lineage, paint, dx, dy)

    try:
        root = parse(svg)
    except ValueError:
        return ()  # a fragment with no balanced <svg> root (the report's tests feed `parse_svg` such snippets): nothing tagged
    for child in root.children:
        visit(child, None, (), {}, 0.0, 0.0)
    return tuple(out)


def gap(a: Mark, b: Mark) -> float:
    """The clear distance between two boxes, px (zero when they touch or overlap)."""
    dx = max(b.x - a.x2, a.x - b.x2, 0.0)
    dy = max(b.y - a.y2, a.y - b.y2, 0.0)
    return float((dx * dx + dy * dy) ** 0.5)
