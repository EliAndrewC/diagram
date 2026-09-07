"""The low-zoom RASTER of the page, and the CLASS ID MAP that answers the pointer while it shows (feature 200).

THE GM, 2026-09-07, after feature 199 tiled the merged scatter paths: "that is better but still slow ...
I'm using google chrome, and all of the above feel slow, so please proceed with the hybrid approach" -
hovering, scrolling, zooming and the first load. A Chrome DevTools trace of the tiled page said what was
left (specs/200 research.md R1): every hover on a map-spanning class, every wheel turn and every zoom
step re-rasterizes ALL the visible ink - 100-250 ms of rasterizer CPU per action on Kuwabata's opening
view - and it is not the scrub: 96% of the scrub's blades lie outside the viewBox (R2), and a prototype
that pre-rendered only the ground cover left a wheel turn at 152-157 ms against 163-178 shipped.

So below a screen scale the page shows ONE IMAGE of the whole picture - this module renders it with resvg,
the map's own PNG renderer, at `RASTER_R` px per map px - and the hovered class alone is drawn lit as
vector above it. Hidden groups cannot answer the pointer, so a second render, the ID MAP, paints every
class one flat color (its hit geometry included, every opacity stripped, no anti-aliasing) and the page
reads the class under the pointer from a canvas. Measured on the prototype (R4): hover the scrub 221-251
-> 32-38 ms of raster CPU, hover off 109-123 -> 9, a wheel turn 163-178 -> 12-14, a zoom step 62-69 ->
10-12; the id map agrees with the DOM's own hit-testing on 98.2% of a grid of points, the rest single-pixel
boundaries. Above the scale the page is feature 199's, unchanged.

And the OFF-MAP INK is dropped (R2): 286,058 subpaths and 2,250 elements on Kuwabata that the viewBox
clips. Invisible by construction, and it is what keeps the first load near today's once the image's decode
is added: 0.36 s today, 0.83 with the ink kept, 0.58 dropped.

Every number here is a rendering decision (constitution XII), recorded in specs/200 with its measurement.
"""

from __future__ import annotations

import base64
import io
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence

#: Px per map px of the picture. 2 puts a DPR-2 screen's opening view of Kuwabata (screen scale 1.31 x 2)
#: past the switch, so such a reader would see no change; 4 doubles the decoded image (Kuwabata 33 Mpx,
#: 132 MB). At 3: Kuwabata 3210 x 5784 = 18.6 Mpx, 74 MB decoded, 2.95 MB on the page (specs/200 R4).
RASTER_R = 3.0
#: How far past the viewBox an element may lie and still be kept - wider than any stroke width or blob
#: radius the writer emits, so a mark reaching in by a pixel is never lost (spec D6).
OFFMAP_MARGIN = 24.0
#: The id map's palette: class i (1-based) paints red = i * PALETTE_STEP; 4 admits 63 classes, and a value
#: one off the grid (a PNG round trip through a canvas) snaps back. The page's vocabulary is 51 classes
#: and the placard; `id_map` refuses a page past the palette rather than aliasing two classes.
PALETTE_STEP = 4
#: resvg names MS fonts for the generic families; 'serif' must be DejaVu Serif or every label changes face
#: (settlement/finish.py `render_png`, where this was learned; ONE definition, both renders use it).
RESVG_FONT_ARGS: tuple[str, ...] = ("--serif-family", "DejaVu Serif")

_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_VIEWBOX = re.compile(r'viewBox="\s*(-?[\d.]+)[ ,]+(-?[\d.]+)[ ,]+(-?[\d.]+)[ ,]+(-?[\d.]+)\s*"')
_PATH = re.compile(r'(<path [^>]*?d=")([^"]*)("[^>]*/>)')
_SHAPE = re.compile(r"<(circle|ellipse|line|rect|polygon|polyline)\b([^>]*)/>")
#: the merge's own grammar (page.py `_sub`): a line is `M x,y L x,y`, a disc `M x-r,y a r,r 0 1 0 2r,0 a ...`
_MERGE_GRAMMAR = re.compile(r"(M-?[\d.]+,-?[\d.]+(L-?[\d.]+,-?[\d.]+|a[^Mm]*))+")
_SUBPATH = re.compile(r"[Mm][^Mm]*")
_ATTRS = re.compile(r'([a-z0-9-]+)="([^"]*)"')
_GROUP = re.compile(r'<g class="f f-[a-z0-9-]+(?: planted)?" data-k="([^"]*)"[^>]*>')
_GTAG = re.compile(r"<g\b|</g>")
_OPACITY = re.compile(r'\s(?:fill-opacity|stroke-opacity|opacity)="[^"]*"')

Viewbox = tuple[float, float, float, float]


def viewbox_of(svg_open: str) -> Viewbox | None:
    """(x, y, w, h) from the page's `<svg>` open tag, or None when it carries none - and then nothing here runs."""
    m = _VIEWBOX.search(svg_open)
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))) if m else None


def drop_offmap(s: str, vb: Viewbox) -> str:
    """One record string less every element or merged subpath that lies wholly outside the viewBox plus
    OFFMAP_MARGIN. A string carrying a `transform` is returned untouched - its coordinates are local - and
    so is any path outside the merge's own M/L and M/a grammar, whose extent is not a matter of reading
    numbers. Invisible by construction: the viewBox clips what is dropped (spec FR-001)."""
    if "transform=" in s:
        return s
    x0, y0 = vb[0] - OFFMAP_MARGIN, vb[1] - OFFMAP_MARGIN
    x1, y1 = vb[0] + vb[2] + OFFMAP_MARGIN, vb[1] + vb[3] + OFFMAP_MARGIN

    def outside(xs: Sequence[float], ys: Sequence[float]) -> bool:
        return max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1

    def fix_path(m: re.Match[str]) -> str:
        d = m.group(2)
        if not _MERGE_GRAMMAR.fullmatch(d):
            return m.group(0)
        keep = []
        for sp in _SUBPATH.findall(d):
            nums = [float(v) for v in _NUM.findall(sp)]
            xs, ys = nums[0::2], nums[1::2]
            if "a" in sp:  # an arc subpath starts a radius left of its center: its box is the disc
                r = float(_NUM.findall(sp.split("a", 1)[1])[0])
                xs, ys = [xs[0], xs[0] + 2 * r], [ys[0] - r, ys[0] + r]
            if not outside(xs, ys):
                keep.append(sp)
        if not keep:
            return ""
        return m.group(1) + "".join(keep) + m.group(3)

    def fix_shape(m: re.Match[str]) -> str:
        tag, at = m.group(1), dict(_ATTRS.findall(m.group(2)))
        try:
            if tag == "circle":
                cx, cy, r = float(at["cx"]), float(at["cy"]), float(at["r"])
                xs, ys = [cx - r, cx + r], [cy - r, cy + r]
            elif tag == "ellipse":
                cx, cy, rx, ry = float(at["cx"]), float(at["cy"]), float(at["rx"]), float(at["ry"])
                xs, ys = [cx - rx, cx + rx], [cy - ry, cy + ry]
            elif tag == "line":
                xs, ys = [float(at["x1"]), float(at["x2"])], [float(at["y1"]), float(at["y2"])]
            elif tag == "rect":
                x, y, w, h = float(at["x"]), float(at["y"]), float(at["width"]), float(at["height"])
                xs, ys = [x, x + w], [y, y + h]
            else:
                nums = [float(v) for v in _NUM.findall(at["points"])]
                xs, ys = nums[0::2], nums[1::2]
            if not xs or not ys:
                return m.group(0)
        except KeyError, ValueError:  # a shape the writer does not emit: not judged
            return m.group(0)
        return "" if outside(xs, ys) else m.group(0)

    return _SHAPE.sub(fix_shape, _PATH.sub(fix_path, s))


def resvg_png(doc: str, *args: str) -> bytes | None:
    """`doc` rendered by resvg with `args`, as PNG bytes - or None when resvg is not on the host (the
    engine already refuses to render a map without it; here the page simply carries no raster)."""
    exe = shutil.which("resvg")
    if not exe:
        sys.stderr.write("warning: resvg not found (sudo apt-get install -y resvg fonts-dejavu-extra); the page carries no raster\n")
        return None
    if "xmlns=" not in doc[: doc.find(">") + 1]:  # a test page's bare `<svg viewBox=...>`: resvg needs the namespace
        doc = doc.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    with tempfile.TemporaryDirectory() as d:
        src, out = f"{d}/r.svg", f"{d}/r.png"
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(doc)
        subprocess.run([exe, *args, src, out], check=True, capture_output=True)  # its font warnings are noise here
        with open(out, "rb") as fh:
            return fh.read()


def picture(svg_text: str, r: float = RASTER_R) -> bytes | None:
    """The whole picture at `r` px per map px, as lossless WebP (half the bytes of PNG; lossy WebP rings on
    line art and was declined - spec D2). The same SVG text the page carries, so the same picture."""
    png = resvg_png(svg_text, "--zoom", f"{r:g}", *RESVG_FONT_ARGS)
    if png is None:
        return None
    from PIL import Image

    buf = io.BytesIO()
    # ENCODE METHOD 0, NOT 4 (feature 203, found by the gate's duration ratchet): still lossless, and measured on
    # Kuwabata at 18.6 Mpx - method 4 took 9.6 s for 2.97 MB, method 0 2.2 s for 3.20 MB (+8%). The gate writes a
    # page for every map it rolls, so the slow setting cost it 7 s per roll for a quarter-megabyte saving.
    Image.open(io.BytesIO(png)).save(buf, "WEBP", lossless=True, quality=100, method=0)
    return buf.getvalue()


_TEXT = re.compile(r"<text\b[^>]*>.*?</text>", re.S)


def without_text(svg_text: str) -> str:
    """The SVG less every `<text>` - what the PICTURE is rendered from (feature 201, FR-001). Text is never in
    the image and always the browser's: feature 200's picture carried resvg's DejaVu Serif rendering of the
    scale and the placard, and the page drew Chrome's own text over it - two fonts on top of each other on
    the scale (the GM: "two different lines of text are overlapped on each other"), and a placard whose
    lit name was one font and whose unlit name was another. The id map keeps its text: a caption is hit as
    its class."""
    return _TEXT.sub("", svg_text)


def class_keys(svg_text: str) -> list[str]:
    """Every class key on the page, in order of first appearance - derived from the groups, never listed."""
    keys: list[str] = []
    for m in _GROUP.finditer(svg_text):
        if m.group(1) not in keys:
            keys.append(m.group(1))
    return keys


def _recolor_group(text: str, c: str) -> str:
    """One class group painted flat in `c`, its HIT GEOMETRY painted as the DOM would hit it: the marks-region
    rectangles (each carrying its own `fill="none"`) and the region polygons as fills, the widened copies as
    strokes of their hit width, the widened beads as discs. Then every fill and stroke the group draws with,
    a pattern fill included, and a fill on the group for anything that draws with the default."""
    text = re.sub(r'<g class="hit" fill="none" style="pointer-events: fill">(.*?)</g>', lambda m: f'<g fill="{c}">' + m.group(1).replace(' fill="none"', "") + "</g>", text, flags=re.S)
    text = text.replace('fill="none" style="pointer-events: fill"', f'fill="{c}"')
    text = re.sub(r'fill="none" class="hit" style="pointer-events: stroke; stroke-width: ([\d.]+)px"', lambda m: f'stroke="{c}" stroke-width="{m.group(1)}" fill="none"', text)
    text = re.sub(r'r="([\d.]+)" fill="none" class="hit" style="pointer-events: fill"', lambda m: f'r="{m.group(1)}" fill="{c}"', text)
    text = re.sub(r'fill="(?:#[0-9A-Fa-f]{3,8}|url\([^)]*\))"', f'fill="{c}"', text)
    text = re.sub(r'stroke="#[0-9A-Fa-f]{3,8}"', f'stroke="{c}"', text)
    return text.replace(">", f' fill="{c}">', 1)


def id_map(svg_text: str, keys: Sequence[str]) -> tuple[bytes | None, dict[str, str]]:
    """(the id map as PNG at 1 px per map px, {red value: class key}). Anti-aliasing OFF, because a blended
    edge is a wrong class; every opacity stripped, inside and outside the class groups, because a
    translucent wrapper moved every value off the palette (spec R4). Ink outside the class groups - the
    sheet, the scale bar - is painted none, so nothing but a class can answer."""
    if len(keys) * PALETTE_STEP > 255:
        raise ValueError(f"{len(keys)} classes on one page - past the id map's {255 // PALETTE_STEP}-class palette")
    palette = {str((i + 1) * PALETTE_STEP): k for i, k in enumerate(keys)}
    color = {k: f"#{(i + 1) * PALETTE_STEP:02X}0000" for i, k in enumerate(keys)}
    out: list[str] = []
    pos = 0
    for m in _GROUP.finditer(svg_text):
        if m.start() < pos:
            continue
        depth, i = 1, m.end()
        while depth:
            mm = _GTAG.search(svg_text, i)
            assert mm is not None, "an unclosed class group"
            depth += -1 if mm.group(0) == "</g>" else 1
            i = mm.end()
        out.append(_unpaint(svg_text[pos : m.start()]))
        out.append(_recolor_group(svg_text[m.start() : i], color[m.group(1)]))
        pos = i
    out.append(_unpaint(svg_text[pos:]))
    doc = _OPACITY.sub("", "".join(out))
    doc = doc.replace("<svg ", '<svg shape-rendering="crispEdges" ', 1)
    # THE FONT MAPPING TOO (feature 201): without it resvg finds no 'serif' and draws no text at all, so a
    # caption was unhittable in raster mode - a feature-200 defect the picture never showed, because the
    # picture passed the mapping and the id map did not
    return resvg_png(doc, "--zoom", "1", "--shape-rendering", "crispEdges", *RESVG_FONT_ARGS), palette


def _unpaint(text: str) -> str:
    """Text OUTSIDE every class group with its paints removed: nothing there may answer the pointer."""
    text = re.sub(r'fill="(?:#[0-9A-Fa-f]{3,8}|url\([^)]*\))"', 'fill="none"', text)
    return re.sub(r'stroke="#[0-9A-Fa-f]{3,8}"', 'stroke="none"', text)


def data_uri(mime: str, data: bytes) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
