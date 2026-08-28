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


def _open(key: str) -> str:
    return f'<g class="f f-{slug(key)}" data-k="{html.escape(key, quote=True)}">'


def wrap(s: str, tag: ClsTag) -> str:
    """The HTML form of one record-stream string: unchanged when unclassed or ruled out; wrapped in its
    class group when classed; two copies for a `Split` (fill-only under the fill class, stroke-only under
    the stroke class - the paddy body and the bund from one polygon); piece by piece for `Parts`."""
    if tag is None or tag == NOT_HIGHLIGHTED or not s:
        return s
    if isinstance(tag, str):
        return _open(tag) + s + "</g>"
    if isinstance(tag, Split):
        fill_copy = _ATTR_STROKE.sub(' stroke="none"', s)
        stroke_copy = _ATTR_FILL.sub(' fill="none"', s)
        return _open(tag.fill) + fill_copy + "</g>" + _open(tag.stroke) + stroke_copy + "</g>"
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


def render_page(strings: Sequence[str], tags: Sequence[ClsTag], name: str, meta: dict[str, Any] | None = None) -> str:
    """The whole page as one string - `write_html` writes it; tests read it."""
    svg = "\n".join(wrap(s, t) for s, t in zip(strings, tags, strict=True))
    svg = svg.replace("<svg ", '<svg id="map" ', 1)
    data = explanations(present_classes(tags))
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


def write_html(path: str, strings: Sequence[str], tags: Sequence[ClsTag], name: str, meta: dict[str, Any] | None = None) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(render_page(strings, tags, name, meta))
