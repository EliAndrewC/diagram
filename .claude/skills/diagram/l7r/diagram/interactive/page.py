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
import math
import os
import re
from collections.abc import Iterator, Sequence
from typing import Any

from .classes import CLASSES, NOT_HIGHLIGHTED, PLACE, lead_sentence, slug
from .glossary import GLOSSARY
from .notes import EMPTY, MapNotes, read_map_notes
from .place import LANE, lane_default, place_card
from .sources import research_questions
from .tags import ClsTag, Planted, Split

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

#: What introduces a feature class's caveat. The place card's basis gets its OWN lead-in
#: (`place.BASIS_LEAD`) because it is not about the drawing - see `explanations`.
CAVEAT_LEAD = "On the drawing: "

#: The one line above the references list (feature 180, spec FR-008 / D8). A bare list of research
#: headings under the word "References" does not tell a casual reader what the lines are, or that each
#: is a link to a written answer with its sources. "Questions" is the GM's own word for them.
REFERENCES_LEAD = "The questions we asked while working out this feature - each is answered in our research notes, with the sources it rests on:"


_LINE = re.compile(r'<line ((?:[a-z0-9-]+="[^"]*"\s*)+)/>')
_CIRCLE = re.compile(r'<circle ((?:[a-z0-9-]+="[^"]*"\s*)+)/>')
_ATTR = re.compile(r'([a-z0-9-]+)="([^"]*)"')
_RUN = re.compile(r"(?:<(?:line|circle) (?:[a-z0-9-]+=\"[^\"]*\"\s*)+/>){2,}")
#: Every element the merge has to reason about: the three it can MERGE, and the rest, which it only has
#: to locate well enough to know whether something may be moved past them.
_ELEM = re.compile(r'<(line|circle|ellipse|path|polygon|polyline|rect)\s((?:[a-z0-9-]+="[^"]*"\s*)+)/?>')
_NUM = re.compile(r"-?\d+(?:\.\d+)?")
#: Coordinates, per tag - everything else is the STYLE, and two elements sharing a style draw the same
#: ink in either order, which is what makes reordering thinkable at all.
_COORDS: dict[str, tuple[str, ...]] = {
    "line": ("x1", "y1", "x2", "y2"),
    "circle": ("cx", "cy", "r"),
    "ellipse": ("cx", "cy", "rx", "ry"),
}
#: What one element paints inside: a disc (cx, cy, r) for a circle, a box (x0, y0, x1, y1) for anything
#: else, None for a shape whose area cannot be read - which counts as being in the way everywhere.
Extent = tuple[float, float, float] | tuple[float, float, float, float] | None
#: How many skipped extents one bucket will hold before it gives up and starts a new run. A bound on the
#: work, not a rule about the map: past this the bucket is almost certainly blocked anyway.
_SKIP_CAP = 400


def _extent(tag: str, at: dict[str, str], raw: str) -> Extent:
    """The area this element paints inside - a disc `(cx, cy, r)` for a circle, otherwise a box
    `(x0, y0, x1, y1)` - or None when that cannot be known cheaply.

    A SUPERSET IS SAFE AND AN UNDERSET IS NOT. For a path the box is taken over every number in `d`,
    which for a curve is its control points - always a superset of the curve itself, so the overlap test
    below can only ever be too careful. None means "assume it is in the way"."""
    try:
        if tag == "line":
            xs = (float(at["x1"]), float(at["x2"]))
            ys = (float(at["y1"]), float(at["y2"]))
        elif tag == "circle":
            cx, cy, r = float(at["cx"]), float(at["cy"]), float(at["r"])
            return (cx, cy, r + float(at.get("stroke-width") or 0.0) / 2.0)
        elif tag == "ellipse":
            cx, cy, rx, ry = float(at["cx"]), float(at["cy"]), float(at["rx"]), float(at["ry"])
            xs, ys = (cx - rx, cx + rx), (cy - ry, cy + ry)
        elif tag == "rect":
            x, y, w, h = float(at["x"]), float(at["y"]), float(at["width"]), float(at["height"])
            xs, ys = (x, x + w), (y, y + h)
        else:  # path, polygon, polyline - every number in the geometry attribute
            nums = [float(v) for v in _NUM.findall(at.get("d") or at.get("points") or "")]
            if len(nums) < 4:
                return None
            xs, ys = tuple(nums[0::2]), tuple(nums[1::2])
            return (min(xs), min(ys), max(xs), max(ys))
    except KeyError, ValueError:  # pragma: no cover - an attribute shape the writer does not emit
        return None
    pad = float(at.get("stroke-width") or 0.0) / 2.0
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def _hits(a: Extent, b: Extent) -> bool:
    """Do these two painted areas touch? An unknown one is treated as touching everything.

    A CIRCLE IS TESTED AS A CIRCLE (feature 153). Boxes are what every other shape gets, but a scatter
    of round blobs is exactly where a box lies most: two crowns whose boxes overlap in a corner do not
    touch at all, and under the box test they refuse to merge for nothing. Measured on Kuwabata's
    woodland, where the difference is thousands of elements."""
    if a is None or b is None:
        return True
    if len(a) == 3 and len(b) == 3:
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 <= (a[2] + b[2]) ** 2
    ba, bb = _box(a), _box(b)
    return not (ba[2] < bb[0] or bb[2] < ba[0] or ba[3] < bb[1] or bb[3] < ba[1])


def _box(e: tuple[float, ...]) -> tuple[float, float, float, float]:
    """A disc's bounding box, or a box unchanged."""
    if len(e) == 3:
        x, y, r = e
        return (x - r, y - r, x + r, y + r)
    return (e[0], e[1], e[2], e[3])


def _refused(b: dict[str, Any], ext: Extent) -> bool:
    """May this bucket NOT take an element painting inside `ext`? Three ways it may not.

    A TRANSLUCENT SHAPE MAY NOT MERGE WITH ONE IT OVERLAPS (feature 148, measured). Two blobs at
    opacity 0.85 stack darker where they cross; the same two as subpaths of ONE path are a single 0.85
    fill and the crossing goes light. Small - 0.0025% of the reference hamlet's pixels - and still the
    picture changing, which feature 134's FR-002 forbids.

    NOR MAY AN OUTLINED ONE (feature 153, measured on Kuwabata). A path paints ALL its subpath fills and
    only THEN its stroke, so an earlier crown's outline that a later crown's fill used to hide comes back
    over it: the dike-pond map's woodland read as a heap of glass rings, and the page sat 0.255% of
    pixels from its own PNG against the reference hamlet's 0.015%.

    And nothing may move BACKWARD past a different element it overlaps - the `skip` extents gathered
    since this bucket's last member, or `blocked` when one of them could not be read at all."""
    if b["blocked"]:
        return True
    if (b["translucent"] or b["outlined"]) and any(_hits(ext, e) for e in b["extents"]):
        return True
    return any(_hits(ext, e) for e in b["skip"])


def _outlined(tag: str, at: dict[str, str]) -> bool:
    """Does this element paint a fill AND a stroke? Those two are painted in different PASSES once the
    element is a subpath of a merged path - every fill, then the one stroke - so where two of them
    overlap the merge changes which is on top. A fill-only or stroke-only shape has no such order to
    lose. An absent `fill` is black in SVG, which is why the default here is a visible fill.

    A LINE HAS NO FILL, whatever its attributes say. Reading one as outlined cost 4,336 elements on
    Kuwabata's scrub alone - 5,536 unmerged blades where 1,200 paths had been - because the scatter is
    one <line> per blade, drawn with no `fill` attribute at all."""
    if tag == "line":
        return False
    if at.get("fill", "black") == "none":
        return False
    if at.get("stroke", "none") == "none":
        return False
    try:
        return float(at.get("stroke-width", "1")) > 0.0
    except ValueError:  # pragma: no cover - a stroke-width shape the writer does not emit
        return True


def _sub(tag: str, at: dict[str, str]) -> str:
    """One element as a subpath of the merged `d`."""
    if tag == "line":
        return f"M{at['x1']},{at['y1']}L{at['x2']},{at['y2']}"
    if tag == "circle":
        r = float(at["r"])
        return f"M{float(at['cx']) - r:g},{at['cy']}a{r:g},{r:g} 0 1 0 {2 * r:g},0a{r:g},{r:g} 0 1 0 {-2 * r:g},0"
    rx, ry = float(at["rx"]), float(at["ry"])
    return f"M{float(at['cx']) - rx:g},{at['cy']}a{rx:g},{ry:g} 0 1 0 {2 * rx:g},0a{rx:g},{ry:g} 0 1 0 {-2 * rx:g},0"


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

    # SEPARATED IS NOT THE SAME AS UNMERGEABLE (feature 148, GM 2026-08-29: "please re aim the feature at
    # element count since that seems to be the cause of the ball performance"). The first cut merged only
    # CONSECUTIVE runs, which is nearly nothing on a map whose glyphs interleave: Kuwabata's mulberry dike
    # draws a trunk, a shadow and its foliage per tree, a mean run of 2.4 elements, so 2,975 circles
    # carrying THREE styles collapsed to almost none of them. Gathering them instead takes that page's
    # groups from 10,462 elements toward 4,140 (research R2).
    #
    # WHAT MAKES THE REORDER LEGAL. Two elements of the same style paint the same ink in either order, so
    # they may always be gathered. Moving one BACKWARD past a different element is only invisible when the
    # two do not overlap - so each bucket remembers the extents it has skipped since its last member, and
    # an element joins only if it touches none of them. An extent that cannot be computed counts as
    # touching everything, which makes the test too careful rather than wrong. That is why the trees
    # gather at all: a crown's own blobs overlap and keep their order, while tree 40's foliage never
    # reaches tree 12's.
    elems: list[tuple[int, int, str, dict[str, str]]] = []
    for m in _ELEM.finditer(s):
        elems.append((m.start(), m.end(), m.group(1), _attrs(m.group(2))))
    if len(elems) < 2:
        return s

    # ONE OPEN BUCKET PER STYLE, and a refused element opens a new one. Keeping SEVERAL open and trying
    # each was implemented and measured (feature 153) on the map that stresses this hardest: Kuwabata
    # came out at 9,726 elements either way, byte for byte. It bought nothing, so it is not here.
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    order: list[dict[str, Any]] = []
    for idx, (_a, _b, tag, at) in enumerate(elems):
        ext = _extent(tag, at, s)
        coords = _COORDS.get(tag)
        key = (tag, " ".join(f"{k}={v}" for k, v in sorted(at.items()) if k not in coords)) if coords else None
        joined = None
        if key is not None:
            got = buckets.get(key)
            if got is not None and _refused(got, ext):
                got = None
            if got is not None:
                got["members"].append(idx)
                got["extents"].append(ext)
                joined = got
            else:
                _st = dict(at)
                _translucent = any(float(_st.get(k, 1) or 1) < 1.0 for k in ("opacity", "fill-opacity", "stroke-opacity"))
                joined = {"first": idx, "members": [idx], "extents": [ext], "skip": [], "blocked": False, "tag": tag, "translucent": _translucent, "outlined": _outlined(tag, _st)}
                buckets[key] = joined
                order.append(joined)
        for other in buckets.values():
            if other is joined:
                continue
            other["skip"].append(ext)
            if ext is None or len(other["skip"]) > _SKIP_CAP:
                other["blocked"] = True

    #: what each element becomes: its own text, nothing (it was gathered into an earlier one), or the path
    repl: dict[int, str] = {}
    for b in order:
        if len(b["members"]) < 2:
            continue
        tag = b["tag"]
        at0 = elems[b["members"][0]][3]
        style = {k: v for k, v in at0.items() if k not in _COORDS[tag]}
        d = "".join(_sub(tag, elems[k][3]) for k in b["members"])
        attrs = " ".join(f'{k}="{v}"' for k, v in style.items())
        tail = ' fill="none"' if tag == "line" and "fill" not in style else ""
        repl[b["members"][0]] = f'<path d="{d}"' + (" " + attrs if attrs else "") + tail + "/>"
        for k in b["members"][1:]:
            repl[k] = ""

    if not repl:
        return s
    out: list[str] = []
    at_pos = 0
    for idx, (a, b2, _t, _at) in enumerate(elems):
        out.append(s[at_pos:a])
        out.append(repl.get(idx, s[a:b2]))
        at_pos = b2
    out.append(s[at_pos:])
    return "".join(out)


#: Thin classes whose marks get a FAT INVISIBLE HIT COPY (GM 2026-08-28: "very thin and hard for me to
#: move my mouse over very precisely" - the bunds, the beans on them, the ditches, the lanes). The
#: copy repeats the mark's geometry with `pointer-events: stroke` (a line, path or outline) or a
#: tripled radius with `pointer-events: fill` (a bead), no paint, HIT_WIDEN_FACTOR times the drawn
#: width with a floor of HIT_WIDEN_MIN px - the GM's "three or four times the width". It sits right
#: after the mark inside its class group: above the paddy fill beneath a bund, below anything drawn
#: later.
#: Per class: (stroke factor, stroke floor px, bead radius factor). The GM, testing the first cut
#: (2026-08-28): the bund and bean boxes "about twice as wide"; the channels and the stream could
#: "stand to widen"; the lanes "seem fine".
HIT_WIDEN: dict[str, tuple[float, float, float]] = {
    "bund": (8.0, 12.0, 6.0),
    "bund beans": (8.0, 12.0, 6.0),
    "field ditch": (6.0, 9.0, 4.5),
    #: the GM, 2026-08-29: "the pond sluices are really hard to click on ... a larger highlight box,
    #: similar to what we are doing with the field ditches". It is a 2.4 px line - thinner than a ditch -
    #: so the ditch's own factors give it a 14 px box, which is what "similar" buys at that width.
    "pond sluice": (6.0, 9.0, 4.5),
    "stream": (1.5, 12.0, 4.5),
    "village lane": (4.0, 6.0, 3.0),
}
#: WHOSE BOX RIDES ABOVE THE INK instead of inside its own class group (feature 153). Everything else
#: keeps the arrangement the GM tuned on 2026-08-28 - a box just above its own class's ink, buried by
#: whatever is drawn later - and only a mark that CANNOT be hit any other way is lifted out.
#:
#: A pond sluice is the case: 49 of Kuwabata's 52 are drawn ON a field ditch (median centerline
#: separation 0.03 px - a sluice IS a gate in a watercourse), the ditch group comes later, and its box
#: took the pointer from the sluice's own 2.4 px line. Measured by `settlement-review`: the sluice won
#: 42.4% of its own widened box, median 40%, worst 10.3%, seven sluices under 25% - so the GM's "really
#: hard to click on" was still true after the widening meant to fix it. Lifted out: 88.6%, median 91.7%,
#: worst 75.8%, none under 25%.
#:
#: LIFTING EVERY BOX WAS TRIED FIRST AND IS WRONG. Above the ink, the bund's 12 px box (8x a 1.4 px
#: mark) stops being buried and blankets the map: +5,112 sample points for the bund, -2,802 for the
#: mulberry dike, -1,472 for the vegetable ground, -914 for the paddy - hovering a dike would have
#: given "bund". A box may beat empty ground; it may not beat another feature's drawn ink.
HIT_ON_TOP: frozenset[str] = frozenset({"pond sluice"})
#: Among the lifted ones, hardest-to-hit last (it wins). One member today; the order is here so the
#: second one is a decision rather than a coincidence of dict order. A lifted class this list forgets
#: sorts LAST rather than first - a class is lifted precisely because it must win, and the earlier
#: version's `-1` fallback silently gave it the weakest place, the opposite of the rule stated here.
HIT_PRIORITY: tuple[str, ...] = ("stream", "village lane", "bund", "bund beans", "field ditch", "pond sluice")
#: THE STRUCTURES A LIFTED BOX MUST NOT SWALLOW. `HIT_ON_TOP` puts a box above the ink, and the rule it
#: is allowed under is that a box may beat empty ground and area fills but never another feature's drawn
#: glyph. It broke that rule the moment it shipped: the sluice box took 88.4% of one pig sty's own
#: footprint and 42.8% of a duck pen's (settlement-review, 2026-08-29, 0.25 px grid) - the sty's center
#: is 4.67 px from a lifted line whose half-width is 7.2, so the box simply contained it, and the GM's
#: "really hard to click on" moved from the sluice onto a farm building. Every one of these is a rect in
#: the manifest, so the layer is clipped against them: the box keeps the open ground and gives up the
#: glyph. Ground records (gardens, threshing yards) are deliberately NOT here - they are area fills, and
#: a box over one is the case the widening exists for.
#: EVERY KEY LISTED MUST RECORD `x/y/w/h`: a key whose records carry some other shape (a well's `x,y,r`,
#: a footbridge's `span`, a sluice gate's bare `x,y,rot`) makes no hole and no error, so
#: `test_every_keep_clear_key_makes_its_holes` counts holes against records on a real manifest.
HIT_KEEP_CLEAR: tuple[str, ...] = ("houses", "byres", "farm_sheds", "farm_fixtures", "duck_pens", "pig_sties", "kosatsuba")
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


def hit_copies(s: str, factor: float = HIT_WIDEN_FACTOR, floor: float = HIT_WIDEN_MIN, bead: float = 3.0) -> str:
    """The fat invisible copies of every stroked mark and every bead in one classed string."""

    def _hit_width(w: float) -> float:
        return max(factor * w, floor)

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
        out.append(f'<circle cx="{m.group(1)}" cy="{m.group(2)}" r="{max(bead * r, floor / 2):.1f}" fill="none" class="hit" style="pointer-events: fill"/>')
    return "".join(out)


def _in_any(x: float, y: float, polys: Sequence[Sequence[Sequence[float]]]) -> bool:
    for poly in polys:
        n = len(poly)
        inside = False
        for i in range(n):
            x1, y1 = poly[i][0], poly[i][1]
            x2, y2 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
        if inside:
            return True
    return False


def marks_region(strings: Sequence[str], cell: float = HIT_CELL, grow: int = 1, within: Sequence[Sequence[Sequence[float]]] = ()) -> str:
    """Rects over the grid cells that hold a mark of the given strings - the scrub's real extent -
    GROWN by `grow` cells around every mark and kept inside the recorded footprints `within`. The
    growth is what makes a bare patch INSIDE the scrub count as scrub (the GM, 2026-08-28: "patches
    of dirt with nothing growing there ... should still be counted as part of the scrub land") while
    the village's deliberate clearing, wider than two cells, stays clear; the footprint stops the
    growth spilling past the scrub's own edge. The rects carry fill="none" so the highlight never
    paints them - the first cut left the attribute off and the grid showed as gold steps."""
    marked: set[tuple[int, int]] = set()
    for s in strings:
        for m in _MARK_XY.finditer(s):
            x, y = (m.group(1), m.group(2)) if m.group(1) is not None else (m.group(3), m.group(4))
            marked.add((int(float(x) // cell), int(float(y) // cell)))
    cells: set[tuple[int, int]] = set()
    for gx, gy in marked:
        for dx in range(-grow, grow + 1):
            for dy in range(-grow, grow + 1):
                c = (gx + dx, gy + dy)
                if (dx == 0 and dy == 0) or not within or _in_any((c[0] + 0.5) * cell, (c[1] + 0.5) * cell, within):
                    cells.add(c)
    out: list[str] = []
    for gy in sorted({c[1] for c in cells}):
        xs = sorted(c[0] for c in cells if c[1] == gy)
        start = prev = xs[0]
        for gx in xs[1:]:
            if gx == prev + 1:
                prev = gx
                continue
            out.append(f'<rect x="{start * cell:.0f}" y="{gy * cell:.0f}" width="{(prev - start + 1) * cell:.0f}" height="{cell:.0f}" fill="none"/>')
            start = prev = gx
        out.append(f'<rect x="{start * cell:.0f}" y="{gy * cell:.0f}" width="{(prev - start + 1) * cell:.0f}" height="{cell:.0f}" fill="none"/>')
    return "".join(out)


def _open(key: str, planted: bool = False) -> str:
    #: `planted` adds the token the stylesheet needs to keep a feature's greenery legible while the
    #: feature is lit - see `tags.Planted`. The key, and so the hover and the modal, are unchanged.
    mark = " planted" if planted else ""
    return f'<g class="f f-{slug(key)}{mark}" data-k="{html.escape(key, quote=True)}">'


def _inline_hits(s: str, key: str) -> str:
    """The widened copies that stay INSIDE their class group - every widened class but the lifted ones."""
    return hit_copies(s, *HIT_WIDEN[key]) if key in HIT_WIDEN and key not in HIT_ON_TOP else ""


def wrap(s: str, tag: ClsTag) -> str:
    """The HTML form of one record-stream string: unchanged when unclassed or ruled out; wrapped in its
    class group when classed; two copies for a `Split` (fill-only under the fill class, stroke-only under
    the stroke class - the paddy body and the bund from one polygon); piece by piece for `Parts`."""
    if tag is None or tag == NOT_HIGHLIGHTED or not s:
        return s
    if isinstance(tag, str):
        return _open(tag, isinstance(tag, Planted)) + merge_primitives(s) + _inline_hits(s, tag) + "</g>"
    if isinstance(tag, Split):
        fill_copy = _ATTR_STROKE.sub(' stroke="none"', s)
        stroke_copy = _ATTR_FILL.sub(' fill="none"', s)
        return _open(tag.fill) + fill_copy + "</g>" + _open(tag.stroke) + stroke_copy + _inline_hits(stroke_copy, tag.stroke) + "</g>"
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
    return sorted(k for k in counts if k not in (NOT_HIGHLIGHTED, PLACE) and k not in CLASSES)


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


def explanations(present: set[str], notes: MapNotes = EMPTY) -> dict[str, dict[str, Any]]:
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
            # `lead` is empty for an `accurate` class (feature 156) - see `classes.lead_sentence`.
            # `caveat` is the liberty its record discloses, shown after the why; `label` stays so the
            # classification is still readable on the page (`data-label`), per constitution XII.
            "label": fc.label,
            "lead": lead_sentence(fc.label, fc.label_note),
            # THE LEAD-IN IS PART OF THE ENTRY (settlement-review, 2026-08-29). It used to be
            # prepended by `page.js`, which meant one renderer put "On the drawing:" in front of
            # every caveat - including the place card's, which is about where the card's claims come
            # from and not about the drawing at all. A renderer cannot tell those apart; the writer of
            # the string can.
            "caveat": (CAVEAT_LEAD + fc.caveat) if fc.caveat else "",
            # THE REFERENCES ARE QUESTIONS, READ FROM THE RECORD (feature 180, GM 2026-09-05): the
            # research sections the class's entry names, each linking to its anchor on GitHub. The
            # sources those sections cite no longer ride on the page - a reader reaches them through
            # the question's own page - and neither does the entry pointer, which the modal used to
            # print as a "Record:" footer. Both stay in the registry as the record (constitution XII).
            "questions": research_questions(fc.entry),
            # siblings are LINKS now (hover lights the other class, click opens its modal); the
            # distinguishing texts stay in the registry as the record, not on the page
            "siblings": [other for other in fc.siblings if other in present],
            # WHAT IS TRUE OF THIS MAP ONLY (feature 156, the GM's general capability: "This is, in
            # general, the kind of thing that we want to be able to do for any kind of map feature").
            # Kept in its own key rather than appended to `why`, so a reader is never led to take a
            # local fact for a general one - and absent for every class the notes do not annotate,
            # which is nearly all of them on nearly every map.
            "on_this_map": notes.features.get(key, ""),
        }
    for key in sorted(present - CLASSES.keys() - {PLACE}):
        out[key] = {
            "name": key,
            "what": "This kind of feature has no entry in the class registry yet (interactive/classes.py).",
            "why": "",
            "label": "guess",
            # the stub follows the same contract as a real entry, so its announcement survives
            # (settlement-review nitpick, 2026-08-29: it still carried the pre-154 keys, which
            # nothing reads, and had silently lost its lead)
            "lead": lead_sentence("guess", "unregistered class - the gate reports it"),
            "caveat": "",
            "questions": [],
            "siblings": [],
            "on_this_map": "",
        }
    return out


def glossary_for(data: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """The glossary entries whose terms occur in the present explanations - variants and definition,
    longest variants first so "head race" wins over "head". The page wraps each occurrence.

    IT READS WHAT THE PAGE RENDERS, and nothing else. That used to include `label_note`; since
    feature 156 the note itself is not rendered - only the `lead` built from it for a liberty, and
    the `caveat` split out of it for an accurate class - so those two are what is scanned. Scanning
    a string the reader never sees would define terms that never appear, which the companion test
    in `test_page.py` catches from the other direction."""
    text = " ".join(" ".join(str(d.get(k, "")) for k in ("what", "why", "lead", "caveat", "on_this_map")) for d in data.values()).lower()
    out: list[dict[str, Any]] = []
    for term, (variants, definition) in GLOSSARY.items():
        if any(re.search(r"\b" + re.escape(v.lower()) + r"\b", text) for v in variants):
            out.append({"term": term, "variants": sorted(variants, key=len, reverse=True), "def": definition})
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


def _hit_pieces(s: str, tag: ClsTag) -> Iterator[tuple[str, str]]:
    """(class, the ink a widened copy would be taken from) for one record string. A `Split` widens its
    STROKE class only - the bund, not the paddy body it bounds."""
    if isinstance(tag, str):
        yield tag, s
    elif isinstance(tag, Split):
        yield tag.stroke, _ATTR_FILL.sub(' fill="none"', s)
    elif tag is not None and tag != NOT_HIGHLIGHTED:
        for c, piece in tag:
            if c is not None:
                yield from _hit_pieces(piece, c)


def hit_layer(strings: Sequence[str], tags: Sequence[ClsTag], manifest: dict[str, Any] | None = None) -> str:
    """Every widened hit copy on the page, in ONE layer, THINNEST-DRAWN CLASS LAST.

    THE COPIES USED TO RIDE INSIDE THEIR OWN CLASS GROUP, and a group drawn later then buried them:
    49 of Kuwabata's 52 pond sluices are drawn ON a field ditch (median centerline separation 0.03 px,
    which is correct engineering - a sluice IS a gate in a watercourse), the ditch group comes later,
    and its 14.4 px invisible box therefore took the pointer from the sluice's own drawn line. Measured
    at 83,690 sample points by `settlement-review` on the first cut of this feature: the sluice won
    44.2% of its own widened box and 47.3% of its own 2.4 px stroke, and 28 of those lost points went
    to an invisible box rather than to any visible ink - so the GM's "really hard to click on" was
    still true of most sluices after the widening that was meant to fix it.

    One layer, ordered by `HIT_PRIORITY`, puts the decision on HOW HARD THE MARK IS TO HIT rather than
    on draw order. Each class keeps its own `data-k` group, so hover, highlight and the modal are
    unchanged - `page.js` already collects every `g.f` carrying a key."""
    per: dict[str, list[str]] = {}
    for s, tag in zip(strings, tags, strict=True):
        for key, piece in _hit_pieces(s, tag):
            if key not in HIT_ON_TOP or key not in HIT_WIDEN:
                continue
            copies = hit_copies(piece, *HIT_WIDEN[key])
            if copies:
                per.setdefault(key, []).append(copies)
    order = sorted(per, key=lambda k: (HIT_PRIORITY.index(k) if k in HIT_PRIORITY else len(HIT_PRIORITY), k))
    clip, attr = _keep_clear_clip(manifest)
    return clip + "".join(_open(k)[:-1] + attr + ">" + "".join(per[k]) + "</g>" for k in order)


def _keep_clear_clip(manifest: dict[str, Any] | None) -> tuple[str, str]:
    """(the clipPath, the attribute that applies it) - the map minus every recorded structure footprint.

    An even-odd path of one huge rectangle plus one rectangle per structure, so the structures are HOLES:
    a lifted box hit-tests everywhere except over a drawn building. Clipping is part of hit-testing in
    SVG, which masking is not, so this is the mechanism that actually moves the pointer."""
    holes: list[str] = []
    for key in HIT_KEEP_CLEAR:
        for rec in (manifest or {}).get(key) or []:
            if not isinstance(rec, dict):
                continue
            try:
                x, y, w, h = (float(rec[k]) for k in ("x", "y", "w", "h"))
                rot = math.radians(float(rec.get("rot") or 0.0))
            except KeyError, TypeError, ValueError:
                continue
            # the AXIS-ALIGNED BOX OF THE ROTATED FOOTPRINT, plus the tenth of a pixel the coordinates
            # are rounded to - without that pad the "never smaller than the glyph" claim is false by up
            # to 0.0919 px (measured, settlement-review round 3; with it, 0.0000). The margin is exactly
            # adequate rather than generous: 0.1 px a side against a worst case of 0.05 on the origin
            # plus 0.05 on the width. It holds because the pad is added BEFORE the `:.1f` rounding - a
            # format that ever drops a decimal breaks the claim silently.
            bw = abs(w * math.cos(rot)) + abs(h * math.sin(rot)) + 0.2
            bh = abs(w * math.sin(rot)) + abs(h * math.cos(rot)) + 0.2
            holes.append(f"M{x - bw / 2:.1f},{y - bh / 2:.1f}h{bw:.1f}v{bh:.1f}h{-bw:.1f}Z")
            # ...AND THE APRON A GLYPH IS DRAWN OUTSIDE ITS OWN BOX. A duck pen's `wet` reaches 6-7 px
            # past its `w` x `h`, and the lifted box was taking 10.17% of one apron (settlement-review
            # rounds 3-4). Any auxiliary polygon on the record is held clear too - which is a BBOX with
            # no size bound, so a record that ever carries a large `poly` (a pond ring, a compound
            # outline) would punch a correspondingly large hole, and the count test would not see it.
            for extra in ("wet", "poly"):
                pts = rec.get(extra)
                if isinstance(pts, list) and len(pts) > 2:
                    xs, ys = [float(q[0]) for q in pts], [float(q[1]) for q in pts]
                    ew, eh = max(xs) - min(xs) + 0.2, max(ys) - min(ys) + 0.2
                    holes.append(f"M{min(xs) - 0.1:.1f},{min(ys) - 0.1:.1f}h{ew:.1f}v{eh:.1f}h{-ew:.1f}Z")
    if not holes:
        return "", ""
    d = "M-99999,-99999h199998v199998h-199998Z" + "".join(holes)
    return f'<clipPath id="hit-keep-clear"><path clip-rule="evenodd" d="{d}"/></clipPath>', ' clip-path="url(#hit-keep-clear)"'


def render_page(strings: Sequence[str], tags: Sequence[ClsTag], name: str, meta: dict[str, Any] | None = None, manifest: dict[str, Any] | None = None, notes: MapNotes = EMPTY) -> str:
    """The whole page as one string - `write_html` writes it; tests read it.

    `notes` is the map's own `.notes.md` "Map notes" block, and is EMPTY for most maps and for every
    caller that does not have one. Nothing here fails on its absence: the place card falls back to
    what the map itself knows, and a class with no annotation simply carries none."""
    present = present_classes(tags)
    wrapped = [wrap(s, t) for s, t in zip(strings, tags, strict=True)]
    # the hit regions go right after the SHEET (the first "-"-tagged string), under everything drawn
    sheet = next((i for i, t in enumerate(tags) if t == NOT_HIGHLIGHTED), 0)
    regions = hit_regions(manifest, present - HIT_FROM_MARKS)
    for key in sorted(HIT_FROM_MARKS & present):
        polys = [
            rec["poly"]
            for mk, roles in HIT_REGIONS
            for rec in (manifest or {}).get(mk) or []
            if isinstance(rec, dict) and rec.get("poly") and roles.get(str(rec.get("role", "*")), roles.get("*")) == key
        ]
        rects = marks_region([s for s, t in zip(strings, tags, strict=True) if t == key], within=polys)
        if rects:
            regions += _open(key) + f'<g class="hit" fill="none" style="pointer-events: fill">{rects}</g></g>'
    wrapped.insert(sheet + 1, regions)
    # the widened boxes ride ABOVE the ink, in one layer of their own - see `hit_layer`
    close = next((i for i in range(len(wrapped) - 1, -1, -1) if "</svg>" in wrapped[i]), len(wrapped))
    wrapped.insert(close, hit_layer(strings, tags, manifest))
    svg = "\n".join(wrapped)
    svg = svg.replace("<svg ", '<svg id="map" ', 1)
    data = explanations(present, notes)
    # THE PLACE CARD rides in the same map, under the placard's own reserved key, so the page opens it
    # through the one modal every other feature uses (feature 156). None for a tier the vocabulary does
    # not describe - and then the placard simply has nothing to open, exactly as before.
    card = place_card(meta or {}, present, notes, manifest or {})
    if card is not None:
        data[PLACE] = card
    # THE LANE'S DEFAULT DESTINATION (spec FR-021). An explicit annotation always wins - this only
    # fills in where the notes named a district but said nothing about the lanes, which is the case
    # on every hamlet in the pool.
    if LANE in data and not data[LANE]["on_this_map"]:
        data[LANE]["on_this_map"] = lane_default(str((meta or {}).get("scale") or ""), notes.place)
    blob = json.dumps({"classes": data, "glossary": glossary_for(data)}, ensure_ascii=False).replace("</", "<\\/")
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
        '<section id="x-what"></section><section id="x-why"></section>'
        '<section id="x-onmap" class="onmap" hidden></section><section id="x-caveat" class="caveat" hidden></section>'
        '<section id="x-siblings"></section>'
        # NO "Record:" LINE (feature 180, GM 2026-09-05: "I don't think we need lines like [Record: ...]
        # on our main modal") - the entry pointer is bookkeeping a reader of the map does not need; the
        # references modal below carries what it pointed at, as questions.
        '<footer><p><a id="x-refs" href="#references">See references</a></p><button id="x-close" type="button">Close</button></footer>'
        "</article></dialog>\n"
        # THE REFERENCES MODAL lists the QUESTIONS the research asked, linked to their answers (feature
        # 180); its button says where it goes ("Return to <Name> writeup", set by page.js), because a bare
        # "Close" could be read as closing every modal at once.
        f'<dialog id="references" aria-labelledby="r-name"><article><header><h2 id="r-name"></h2><p id="r-intro" class="intro">{REFERENCES_LEAD}</p></header><section id="r-list"></section>'
        '<footer><button id="r-close" type="button">Return to writeup</button></footer></article></dialog>\n'
        f'<script id="classes" type="application/json">{blob}</script>\n'
        f"<script>\n{_asset('page.js')}</script>\n</body>\n</html>\n"
    )


def write_html(path: str, strings: Sequence[str], tags: Sequence[ClsTag], name: str, meta: dict[str, Any] | None = None, manifest: dict[str, Any] | None = None) -> None:
    """`<base>.html`, beside the map's other outputs. The map's `<base>.notes.md` is read here if it
    exists - one place, derived from the output path rather than searched for, so a stale or foreign
    notes file in the same directory can never be picked up (spec, Edge Cases)."""
    notes = read_map_notes(path[: -len(".html")] + ".notes.md") if path.endswith(".html") else EMPTY
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(render_page(strings, tags, name, meta, manifest, notes))
