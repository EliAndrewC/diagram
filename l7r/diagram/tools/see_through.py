"""Which classes a page draws see-through, and how faintly (feature 294 B5; the declared table is `settlement/see_through.py`).

Walks the page's map SVG once, carrying each element's EFFECTIVE opacity - its own `opacity`, `fill-opacity` and
`stroke-opacity` times every enclosing group's - and the class group it lies in. Hit geometry (`pointer-events`) is not a mark;
`<defs>` (the patterns, read only through a fill) are not walked. It measures and never judges."""

from __future__ import annotations

import re

from l7r.diagram.settlement.see_through import SOLID

_TAG = re.compile(r"<(/?)([a-zA-Z]+)([^>]*?)(/?)>")
_OPACITY = re.compile(r'\s(?:opacity|fill-opacity|stroke-opacity)="([\d.]+)"')
_GROUP = re.compile(r'class="f f-[a-z0-9-]+(?: planted)?" data-k="([^"]*)"')
_DEFS = re.compile(r"<defs>.*?</defs>", re.S)


def translucent_marks(svg_text: str) -> dict[str, float]:
    """{class key: the faintest effective opacity any of its marks is drawn at}, for every class with a mark under `SOLID`;
    a mark outside every class group is keyed "(no class)"."""
    stack: list[tuple[float, str | None]] = []
    out: dict[str, float] = {}
    for m in _TAG.finditer(_DEFS.sub("", svg_text)):
        close, tag, attrs, selfclose = m.groups()
        if close:
            if stack:
                stack.pop()
            continue
        own = 1.0
        for v in _OPACITY.findall(attrs):
            own *= float(v)
        parent, cls = stack[-1] if stack else (1.0, None)
        g = _GROUP.search(attrs)
        cls = g.group(1) if g else cls
        eff = parent * own
        if tag != "g" and eff < SOLID and "pointer-events" not in attrs:
            key = cls or "(no class)"
            out[key] = min(out.get(key, 1.0), round(eff, 3))
        if not selfclose:
            stack.append((eff, cls))
    return out


_PAINT = re.compile(r"<(/?)(g|circle)\b([^>]*?)(/?)>")
_TRANSLATE = re.compile(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)")
_FILL = re.compile(r'fill="(#[0-9A-Fa-f]{6})"')
_CIRC = re.compile(r'cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"')
#: the conifer's own fills - the grove's cedar and the hill wood's (`homestead_parts/groves.py`, `shrines_wells/woods.py`)
CONIFER_FILLS = frozenset({"#496733", "#4A6733"})
#: a crown is a disc at least this wide in radius (px); smaller circles are wells, beads, culm tops
CROWN_MIN_R = 3.0


def crowns_in_paint_order(svg_text: str) -> list[tuple[float, float, float, bool]]:
    """(x, y, r, is a conifer) of every tree crown the SVG paints, in the order it paints them - the document order - with each
    group's `translate` carried to the absolute map position (feature 294 B5b: what is drawn over what is read off the ink)."""
    stack = [(0.0, 0.0)]
    out = []
    for m in _PAINT.finditer(_DEFS.sub("", svg_text)):
        close, tag, attrs, selfclose = m.groups()
        if tag == "g":
            if close:
                if len(stack) > 1:
                    stack.pop()
            elif not selfclose:
                t = _TRANSLATE.search(attrs)
                dx, dy = stack[-1]
                stack.append((dx + float(t.group(1)), dy + float(t.group(2))) if t else (dx, dy))
            continue
        c, f = _CIRC.search(attrs), _FILL.search(attrs)
        if c and f and float(c.group(3)) >= CROWN_MIN_R and "stroke=" in attrs:
            dx, dy = stack[-1]
            out.append((float(c.group(1)) + dx, float(c.group(2)) + dy, float(c.group(3)), f.group(1).upper() in {k.upper() for k in CONIFER_FILLS}))
    return out


def broadleaf_over_conifer(crowns: list[tuple[float, float, float, bool]]) -> list[tuple[int, int]]:
    """(the conifer's index, the lesser crown's index) for every lesser crown painted after a conifer it lies over, by the
    placer's own predicate (`groves.over_a_conifer`, at the ink's own rounding: no slack)."""
    from shapely.geometry import Point
    from shapely.strtree import STRtree

    from l7r.diagram.settlement.homestead_parts.groves import over_a_conifer

    cones = [(i, c) for i, c in enumerate(crowns) if c[3]]
    if not cones:
        return []
    tree = STRtree([Point(c[0], c[1]) for _, c in cones])
    reach = max(c[2] for _, c in cones)
    out = []
    for j, b in enumerate(crowns):
        if b[3]:
            continue
        for k in tree.query(Point(b[0], b[1]).buffer(b[2] + reach)):
            i, c = cones[int(k)]
            if i < j and over_a_conifer(b[0], b[1], b[2], [c[:3]], slack=0.0):
                out.append((i, j))
                break
    return out
