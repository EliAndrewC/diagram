"""Who answers the pointer over each class's visible ink? (feature 294 B6, the review's "page hit regions" class)

The reviews caught a class whose hover region took another's ink three times - the pond sluice's box winning 42% of its own
area, a lifted layer taking 88% of a pig sty, lighting that repainted structures (features 153 and 230) - each by a
measurement made by hand. This makes it one measurement: the page's class ID MAP (`interactive/raster.id_map`, what the
pointer reads in raster mode, hit geometry and all) against its VISIBLE-INK map (the same render with the hit geometry taken
out, so each pixel carries the class whose ink is on top there), pixel for pixel. A class's share is the part of its own
visible ink where the pointer answers with that class; its thief, the class that answers instead over most of the rest.

Two renders a map with resvg at 1 px per map px, no browser. It measures and never judges: the bar and the declared overlaps
are the gate test's (`tests/gate/test_review_rules_294.py`)."""

from __future__ import annotations

import io
import re
from typing import Any

from l7r.diagram.interactive import raster

_HIT_GROUP = re.compile(r'<g class="hit"[^>]*>.*?</g>', re.S)
_HIT_ELEMENT = re.compile(r"<[^<>]*pointer-events:[^<>]*/>")
_PAGE_SVG = re.compile(r'<svg id="map".*?</svg>', re.S)


def page_svg(html: str) -> str | None:
    """The page's map SVG - the one carrying the class groups - or None."""
    m = _PAGE_SVG.search(html)
    return m.group(0) if m else None


def without_hits(svg_text: str) -> str:
    """The page's SVG less every piece of hit geometry: the widened copies, the marks-region boxes, the region polygons."""
    return _HIT_ELEMENT.sub("", _HIT_GROUP.sub("", svg_text))


def _red(png: bytes) -> Any:
    import numpy as np
    from PIL import Image

    return np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))[:, :, 0].astype(np.int64)


def shares(svg_text: str) -> dict[str, tuple[float, str | None, int]] | None:
    """{class key: (its share of its own visible ink the pointer answers with it, the class answering over most of the rest,
    its visible pixels)}, or None without resvg or class groups. Red-channel palette: a hamlet page's classes fit one row."""
    import numpy as np

    keys = raster.class_keys(svg_text)
    if not keys:
        return None
    # TEXT CRISP IN BOTH RENDERS: a hamlet page's id map blends a caption's glyph edges (feature 264 keeps it so), and a blend
    # over a hit box reads as no class at all - Sawada's notice-board caption, laid on the connector, lost 27% of its own ink to
    # its own antialiasing. The pointer over a glyph answers by its outline, which the crisp render is.
    hit_png, palette = raster.id_map(svg_text, keys, crisp_text=True)
    ink_png, _ = raster.id_map(without_hits(svg_text), keys, crisp_text=True)
    if hit_png is None or ink_png is None:
        return None
    hit, ink = _red(hit_png), _red(ink_png)
    key_of = {int(k): v for k, v in palette.items() if "," not in k}
    out: dict[str, tuple[float, str | None, int]] = {}
    for red, key in key_of.items():
        mask = ink == red
        n = int(mask.sum())
        if not n:
            continue
        answered = hit[mask]
        won = int((answered == red).sum())
        others = answered[answered != red]
        thief = None
        if others.size:
            values, counts = np.unique(others, return_counts=True)
            thief = key_of.get(int(values[int(counts.argmax())]))
        out[key] = (won / n, thief, n)
    return out
