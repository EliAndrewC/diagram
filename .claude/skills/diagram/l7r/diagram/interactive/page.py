"""The HTML target: wrap each classed primitive, take the ink census, assemble and write the page.

Feature 134. `finish()` hands this module the finished record streams (the same strings that were
just written to the SVG) and their class side-list, and gets back `<base>.html`: the map inlined as
SVG with every classed string wrapped in `<g class="f f-<class>" data-k="<class>">`, the page's CSS
and script inlined (a plain `file://` open, no network, no asset - spec FR-001), and the
explanations of the classes PRESENT on this map embedded as JSON. Nothing here touches the SVG or
the PNG (FR-010).

The census (`ink_census`) is what the FR-009 gate check reads: it counts drawn elements per class
and lists the ones that carry NO class - ink nobody has ruled on. Ink that draws nothing (`<defs>`,
`<pattern>`, `<clipPath>`, a bare `<g>` wrapper) is exempt; a `"-"` tag is a RULING and is counted
under its own key, never reported.
"""

from __future__ import annotations

import html
import json
import os
import re
from collections.abc import Iterator, Sequence
from typing import Any

from .classes import CLASSES, NOT_HIGHLIGHTED, label_phrase, slug
from .tags import ClsTag, Split

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_HERE, "assets")

#: The elements that put ink on the sheet. A `<g>` or `<clipPath>` draws nothing by itself.
_INK = re.compile(r"<(rect|circle|ellipse|line|polyline|polygon|path|text|image)\b")
#: Definitions whose children never paint: stripped before an element is counted.
_NOT_INK = re.compile(r"<(clipPath|pattern|defs)\b.*?</\1>", re.S)
_ATTR_STROKE = re.compile(r'\sstroke="[^"]*"')
_ATTR_FILL = re.compile(r'\sfill="[^"]*"')

#: How many unclassed snippets the manifest keeps - enough to find the emit site, not the whole map.
UNCLASSED_CAP = 20


_LINE = re.compile(r'<line ((?:[a-z0-9-]+="[^"]*"\s*)+)/>')
_CIRCLE = re.compile(r'<circle ((?:[a-z0-9-]+="[^"]*"\s*)+)/>')
_ATTR = re.compile(r'([a-z0-9-]+)="([^"]*)"')
_RUN = re.compile(r"(?:<(?:line|circle) (?:[a-z0-9-]+=\"[^\"]*\"\s*)+/>){2,}")


def _attrs(body: str) -> dict[str, str]:
    return dict(_ATTR.findall(body))


def merge_primitives(s: str) -> str:
    """MANY SAME-STYLED LINES OR CIRCLES BECOME ONE <path> (feature 134, GM 2026-08-28 on performance).
    The scrub scatter and the marsh alone are 282,000 of Inashiro's 289,000 drawn elements - one <line>
    per blade - and every one is a DOM node the browser styles, lays out and hit-tests: measured
    200-270 ms per scroll frame, 100-300 ms per zoom step, ~550 ms to highlight the scrub. A run of
    consecutive <line>s (or <circle>s) whose attributes other than their coordinates are identical
    draws the same ink as one <path> carrying those attributes and a `d` of M/L (or arc) segments.
    Applied to the HTML target only; the SVG and PNG never see it (FR-010). Vector, so the 16x zoom
    stays crisp and the class groups keep their hit-testing - which is what a raster layer per class
    would have cost (at 16x a full-map raster is ~46,000 px square; see research.md R5)."""

    def _merge_run(m: re.Match[str]) -> str:
        items = [(t, _attrs(a)) for t, a in re.findall(r'<(line|circle) ((?:[a-z0-9-]+="[^"]*"\s*)+)/>', m.group(0))]
        out: list[str] = []
        i = 0
        while i < len(items):
            tag, at = items[i]
            coord = ("x1", "y1", "x2", "y2") if tag == "line" else ("cx", "cy", "r")
            style = {k: v for k, v in at.items() if k not in coord}
            j = i
            d: list[str] = []
            while j < len(items) and items[j][0] == tag and {k: v for k, v in items[j][1].items() if k not in coord} == style:
                a = items[j][1]
                if tag == "line":
                    d.append(f"M{a['x1']},{a['y1']}L{a['x2']},{a['y2']}")
                else:
                    r = float(a["r"])
                    d.append(f"M{float(a['cx']) - r:g},{a['cy']}a{r:g},{r:g} 0 1 0 {2 * r:g},0a{r:g},{r:g} 0 1 0 {-2 * r:g},0")
                j += 1
            if j - i == 1:
                out.append(m.group(0)[0:0] + (f"<{tag} " + " ".join(f'{k}="{v}"' for k, v in at.items()) + "/>"))
            else:
                if tag == "circle" and "fill" not in style:
                    style = {**style}  # a circle's default fill is black; an arc path's is too - nothing to add
                attrs = " ".join(f'{k}="{v}"' for k, v in style.items())
                out.append(f'<path d="{"".join(d)}"' + (" " + attrs if attrs else "") + ("" if tag == "circle" else ' fill="none"' if "fill" not in style else "") + "/>")
            i = j
        return "".join(out)

    return _RUN.sub(_merge_run, s)


#: Thin classes whose marks get a FAT INVISIBLE HIT COPY (GM 2026-08-28: "very thin and hard for me to
#: move my mouse over very precisely" - the bunds, the beans on them, the ditches, the lanes). The
#: copy repeats the mark's geometry with `pointer-events: stroke` (a line, path or outline) or a
#: tripled radius with `pointer-events: fill` (a bead), no paint, HIT_WIDEN_FACTOR times the drawn
#: width with a floor of HIT_WIDEN_MIN px - the GM's "three or four times the width". It sits right
#: after the mark inside its class group: above the paddy fill beneath a bund, below anything drawn
#: later.
HIT_WIDEN: frozenset[str] = frozenset({"bund", "bund beans", "field ditch", "village lane"})
HIT_WIDEN_FACTOR = 4.0
HIT_WIDEN_MIN = 6.0
#: The scrub's hit region is where its MARKS are, not its recorded polygon (the polygon is the whole
#: hinterland, including the ground the scatter deliberately keeps clear - the GM: "if my mouse is just
#: in the middle of the village, over blank space where there is deliberately no scrubland, then I
#: don't think that the scrubland should be highlighted"). A grid of HIT_CELL px cells; a cell with a
#: mark in it is part of the region; runs of cells become one rect each.
HIT_FROM_MARKS: frozenset[str] = frozenset({"scrub and rough grazing"})
HIT_CELL = 24.0

_STROKE_W = re.compile(r'stroke-width="([\d.]+)"')
_GROUP_W = re.compile(r'<g [^>]*stroke-width="([\d.]+)"')
_MARK_XY = re.compile(r'(?:x1|cx)="([-\d.]+)" (?:y1|cy)="([-\d.]+)"|[Mm]([-\d.]+),([-\d.]+)')


def _hit_width(w: float) -> float:
    return max(HIT_WIDEN_FACTOR * w, HIT_WIDEN_MIN)


def hit_copies(s: str) -> str:
    """The fat invisible copies of every stroked mark and every bead in one classed string."""
    out: list[str] = []
    gm = _GROUP_W.search(s)
    default_w = float(gm.group(1)) if gm else 1.0
    for m in re.finditer(r'<(line|path|polygon|polyline) ([^>]*?)/>', s):
        tag, attrs = m.group(1), m.group(2)
        if tag in ("polygon", "polyline", "path") and 'fill="none"' not in attrs and tag != "path":
            continue  # a filled shape already takes the pointer over its whole body
        if tag == "path" and 'fill="none"' not in attrs and "stroke" not in attrs:
            continue
        wm = _STROKE_W.search(attrs)
        w = float(wm.group(1)) if wm else default_w
        geom = " ".join(a for a in re.findall(r'(?:points|d|x1|y1|x2|y2)="[^"]*"', attrs))
        out.append(f'<{tag} {geom} fill="none" class="hit" style="pointer-events: stroke; stroke-width: {_hit_width(w):.1f}px"/>')
    for m in re.finditer(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([-\d.]+)"[^>]*/>', s):
        r = float(m.group(3))
        out.append(f'<circle cx="{m.group(1)}" cy="{m.group(2)}" r="{max(3 * r, HIT_WIDEN_MIN / 2):.1f}" fill="none" class="hit" style="pointer-events: fill"/>')
    return "".join(out)


def marks_region(strings: Sequence[str], cell: float = HIT_CELL) -> str:
    """Rects over the grid cells that hold a mark of the given strings - the scrub's real extent."""
    cells: set[tuple[int, int]] = set()
    for s in strings:
        for m in _MARK_XY.finditer(s):
            x, y = (m.group(1), m.group(2)) if m.group(1) is not None else (m.group(3), m.group(4))
            cells.add((int(float(x) // cell), int(float(y) // cell)))
    out: list[str] = []
    for gy in sorted({c[1] for c in cells}):
        xs = sorted(c[0] for c in cells if c[1] == gy)
        start = prev = xs[0]
        for gx in xs[1:]:
            if gx == prev + 1:
                prev = gx
                continue
            out.append(f'<rect x="{start * cell:.0f}" y="{gy * cell:.0f}" width="{(prev - start + 1) * cell:.0f}" height="{cell:.0f}"/>')
            start = prev = gx
        out.append(f'<rect x="{start * cell:.0f}" y="{gy * cell:.0f}" width="{(prev - start + 1) * cell:.0f}" height="{cell:.0f}"/>')
    return "".join(out)


def _open(key: str) -> str:
    return f'<g class="f f-{slug(key)}" data-k="{html.escape(key, quote=True)}">'


def wrap(s: str, tag: ClsTag) -> str:
    """The HTML form of one record-stream string: unchanged when unclassed or ruled out; wrapped in its
    class group when classed; two copies for a `Split` (fill-only under the fill class, stroke-only under
    the stroke class - the paddy body and the bund from one polygon); piece by piece for `Parts`."""
    if tag is None or tag == NOT_HIGHLIGHTED or not s:
        return s
    if isinstance(tag, str):
        return _open(tag) + merge_primitives(s) + (hit_copies(s) if tag in HIT_WIDEN else "") + "</g>"
    if isinstance(tag, Split):
        fill_copy = _ATTR_STROKE.sub(' stroke="none"', s)
        stroke_copy = _ATTR_FILL.sub(' fill="none"', s)
        return _open(tag.fill) + fill_copy + "</g>" + _open(tag.stroke) + stroke_copy + (hit_copies(stroke_copy) if tag.stroke in HIT_WIDEN else "") + "</g>"
    return "".join(wrap(piece, c) for c, piece in tag)


def _pieces(s: str, tag: ClsTag) -> Iterator[tuple[str | None, str]]:
    """(class, text) for every separately-classed piece of one stream string - a Split counts once,
    under its fill class, because both copies are the same ink."""
    if tag is None or isinstance(tag, str):
        yield tag, s
    elif isinstance(tag, Split):
        yield tag.fill, s
    else:
        yield from tag


def _snippet(piece: str) -> str:
    m = _INK.search(piece)
    name = m.group(1) if m else "?"
    return f"<{name}> {piece[:80]!s}"


def ink_census(strings: Sequence[str], tags: Sequence[ClsTag]) -> tuple[dict[str, int], list[str]]:
    """Count drawn elements per class, and list the ones with no class at all (capped, with a final
    "... and N more" entry so the count is never lost). `"-"` is counted under its own key."""
    counts: dict[str, int] = {}
    unclassed: list[str] = []
    more = 0
    for s, tag in zip(strings, tags, strict=True):
        for key, piece in _pieces(s, tag):
            n = len(_INK.findall(_NOT_INK.sub("", piece)))
            if n == 0:
                continue
            if key is None:
                if len(unclassed) < UNCLASSED_CAP:
                    unclassed.append(_snippet(piece))
                else:
                    more += 1
                continue
            counts[key] = counts.get(key, 0) + n
    if more:
        unclassed.append(f"... and {more} more")
    return counts, unclassed


def unregistered_classes(counts: dict[str, int]) -> list[str]:
    """Class keys the engine tagged that `classes.py` has no entry for - a typo, or a class the
    vocabulary does not name yet. The gate fails on either (FR-009 reads this beside the census)."""
    return sorted(k for k in counts if k != NOT_HIGHLIGHTED and k not in CLASSES)


def present_classes(tags: Sequence[ClsTag]) -> set[str]:
    keys: set[str] = set()
    for tag in tags:
        if isinstance(tag, str):
            keys.add(tag)
        elif isinstance(tag, Split):
            keys.add(tag.fill)
            keys.add(tag.stroke)
        elif tag is not None:
            keys.update(c for c, _s in tag if c is not None)
    keys.discard(NOT_HIGHLIGHTED)
    return keys


def explanations(present: set[str]) -> dict[str, dict[str, Any]]:
    """The embedded data: one entry per present class, in vocabulary order, with only the sibling
    paragraphs whose OTHER class is also present (spec US4 scenario 4 - an absent sibling is never
    claimed). A present key the registry does not know gets a stub that says so, never silence."""
    out: dict[str, dict[str, Any]] = {}
    for key, fc in CLASSES.items():
        if key not in present:
            continue
        out[key] = {
            "name": fc.name,
            "what": fc.what,
            "why": fc.why,
            "label": fc.label,
            "label_phrase": label_phrase(fc.label),
            "label_note": fc.label_note,
            "sources": list(fc.sources),
            "entry": fc.entry,
            "siblings": {other: text for other, text in fc.siblings.items() if other in present},
        }
    for key in sorted(present - CLASSES.keys()):
        out[key] = {
            "name": key,
            "what": "This kind of feature has no entry in the class registry yet (interactive/classes.py).",
            "why": "",
            "label": "guess",
            "label_phrase": label_phrase("guess"),
            "label_note": "unregistered class - the gate reports it",
            "sources": ["not recorded"],
            "entry": "",
            "siblings": {},
        }
    return out


def _asset(name: str) -> str:
    with open(os.path.join(_ASSETS, name), encoding="utf-8") as fh:
        return fh.read()


#: Which recorded footprints become HIT REGIONS, by class: (manifest key, role -> class). A scatter
#: feature is mostly empty ground between its marks - the GM (2026-08-28): "moving my mouse over the
#: scrublands is surprisingly difficult because I need my mouse to be over one of these specific trees
#: or little lines" - so the page adds an invisible polygon of the feature's recorded footprint that
#: takes the pointer wherever nothing drawn above it does.
HIT_REGIONS: tuple[tuple[str, dict[str, str]], ...] = (
    ("commons", {"grazing": "scrub and rough grazing", "commons": "scrub and rough grazing", "woodland": "woodland commons"}),
    ("marshes", {"*": "marsh"}),
    ("village_groves", {"windbreak": "windbreak", "copse": "copse"}),
    ("bamboo_stands", {"homestead": "homestead bamboo", "*": "shared bamboo grove"}),
)


def hit_regions(manifest: dict[str, Any] | None, present: set[str]) -> str:
    """Invisible footprint polygons for the scatter classes present on this map. `fill="none"` with
    `pointer-events: fill` hit-tests the area without painting it, and the highlight rules skip a
    fill-less, stroke-less element, so a region never lights up itself. Placed at the BOTTOM of the
    stack (just above the sheet): everything drawn later - a house, a lane, a paddy - is above it and
    keeps the pointer; only bare ground inside the footprint falls through to the class."""
    if not manifest:
        return ""
    out: list[str] = []
    for key, roles in HIT_REGIONS:
        for rec in manifest.get(key) or []:
            if not isinstance(rec, dict) or not rec.get("poly"):
                continue
            cls = roles.get(str(rec.get("role", "*")), roles.get("*"))
            if cls is None or cls not in present:
                continue
            pts = " ".join(f"{float(x):.1f},{float(y):.1f}" for x, y in rec["poly"])
            out.append(_open(cls) + f'<polygon class="hit" points="{pts}" fill="none" style="pointer-events: fill"/></g>')
    return "".join(out)


def render_page(strings: Sequence[str], tags: Sequence[ClsTag], name: str, meta: dict[str, Any] | None = None, manifest: dict[str, Any] | None = None) -> str:
    """The whole page as one string - `write_html` writes it; tests read it."""
    present = present_classes(tags)
    wrapped = [wrap(s, t) for s, t in zip(strings, tags, strict=True)]
    # the hit regions go right after the SHEET (the first "-"-tagged string), under everything drawn
    sheet = next((i for i, t in enumerate(tags) if t == NOT_HIGHLIGHTED), 0)
    regions = hit_regions(manifest, present - HIT_FROM_MARKS)
    for key in sorted(HIT_FROM_MARKS & present):
        rects = marks_region([s for s, t in zip(strings, tags, strict=True) if t == key])
        if rects:
            regions += _open(key) + f'<g class="hit" fill="none" style="pointer-events: fill">{rects}</g></g>'
    wrapped.insert(sheet + 1, regions)
    svg = "\n".join(wrapped)
    svg = svg.replace("<svg ", '<svg id="map" ', 1)
    data = explanations(present)
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(name)
    # NO HEADER ON THE PAGE (GM 2026-08-28: "we can get rid of the entire header") - the map already
    # carries its own title placard and scale bar; the page is the map and nothing else.
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title} - interactive map</title>\n<style>\n{_asset('page.css')}</style>\n</head>\n<body>\n"
        # The STAGE (FR-013, GM 2026-08-28): the map fills the viewport; page.js fits it whole at
        # load (the minimum zoom) and zooms about the pointer up to MAX_ZOOM times that.
        f'<main id="stage">\n{svg}\n</main>\n'
        '<nav id="zoom" aria-label="zoom"><button type="button" data-z="in" title="zoom in (+)">+</button>'
        '<button type="button" data-z="out" title="zoom out (-)">-</button>'
        '<button type="button" data-z="fit" title="fit the whole map (0)">fit</button></nav>\n'
        '<div id="shade" hidden></div>\n'
        '<dialog id="explain" aria-labelledby="x-name"><article>'
        '<header><h2 id="x-name"></h2><p id="x-label" class="label"></p></header>'
        '<section id="x-what"></section><section id="x-why"></section><section id="x-siblings"></section>'
        '<footer><p id="x-sources"></p><p id="x-entry"></p><button id="x-close" type="button">Close</button></footer>'
        "</article></dialog>\n"
        f'<script id="classes" type="application/json">{blob}</script>\n'
        f"<script>\n{_asset('page.js')}</script>\n</body>\n</html>\n"
    )


def write_html(path: str, strings: Sequence[str], tags: Sequence[ClsTag], name: str, meta: dict[str, Any] | None = None, manifest: dict[str, Any] | None = None) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(render_page(strings, tags, name, meta, manifest))
