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

import re
from dataclasses import dataclass, field
from functools import lru_cache

from ...interactive.sheet import DEFS, Node, parse

_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_TRANSLATE = re.compile(r"translate\(\s*(-?[\d.]+)[\s,]*(-?[\d.]+)?\s*\)")
_PATH_CMD = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")
_INNER_TAG = re.compile(r"<[^>]*>")
#: the presentation attributes a child inherits from its group (SVG's own inheritance)
INHERITED: tuple[str, ...] = ("fill", "stroke", "stroke-width", "font-size", "font-weight", "font-style")
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


def path_points(d: str) -> tuple[tuple[float, float], ...]:
    """The ABSOLUTE points a path visits, in order (M, L, H, V, and the end point of every curve or arc); a relative
    command's offsets are skipped, as `shared._path_points` skips them."""
    out: list[tuple[float, float]] = []
    x = y = 0.0
    for cmd, body in _PATH_CMD.findall(d):
        nums = [float(n) for n in _NUM.findall(body)]
        if cmd == "H" and nums:
            x = nums[-1]
            out.append((x, y))
        elif cmd == "V" and nums:
            y = nums[-1]
            out.append((x, y))
        elif cmd in "ML":
            for i in range(0, len(nums) - 1, 2):
                x, y = nums[i], nums[i + 1]
                out.append((x, y))
        elif cmd in "CSQTA" and len(nums) >= 2:
            x, y = nums[-2], nums[-1]
            out.append((x, y))
    return tuple(out)


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
    """Every drawn element of the sheet in document order (definitions skipped), each with its kind and lineage."""
    out: list[Mark] = []

    def visit(node: Node, kind: str | None, lineage: tuple[str, ...], paint: dict[str, str], dx: float, dy: float) -> None:
        if not node.name or node.name in _SKIP:
            return
        a = dict(_ATTR.findall(node.open))
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
