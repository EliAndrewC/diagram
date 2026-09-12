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
import math
import pickle
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

#: Px per map px of the picture. Feature 200 chose 3 (Kuwabata 3210 x 5784 = 18.6 Mpx, 74 MB decoded) over 2
#: because 2 puts a DPR-2 screen's opening view of Kuwabata (screen scale 1.31 x 2 = 2.62) past the switch, so such
#: a reader's first view is the vector page and the picture serves them only zoomed out from it; 4 would double the
#: decoded image (specs/200 R4). FEATURE 223 SET IT TO 2 (GM 2026-09-11: the fourth item of the list they approved,
#: on feature 222's pattern for a visible change to this picture - make it, look, reverse it in one line if bad):
#: 44% of the pixels (Inashiro 3402 x 3424 = 11.6 Mpx against 26.2), so the render, the decode, the JPEG and the
#: page's bytes all fall by about that - the numbers are specs/223 research R2. The DPR-2 reader's opening view is
#: the priced cost (spec D3). To REVERSE: `RASTER_R = 3.0` - this line is the whole of the decision.
RASTER_R = 2.0
#: THE PICTURE IS A LOSSY JPEG (feature 222, GM 2026-09-11: "I am willing to at least try the lossy JPEG compression
#: for the final image if that seems like it will gain us about four seconds ... if the lossy nature means that it
#: becomes blurry or otherwise bad, then we can always reverse it"). Measured on Inashiro's 5103 x 5136 picture
#: (specs/222 research R1): lossless WebP method 0 4.12 s / 3.87 MB - the single most expensive step of a whole
#: regeneration, paid on every map; JPEG q90 4:4:4 0.15 s / 4.56 MB; JPEG q90 4:2:0 0.10 s / 3.58 MB; lossy WebP q90
#: 0.93 s / 2.32 MB. 4:4:4 (`subsampling=0`) keeps full chroma resolution on the map's thin colored strokes - a
#: 0.8 px blade is 2.4 px here and 4:2:0 would halve its color resolution - for one megabyte more page. This
#: supersedes specs/200 D2 ("lossy WebP rings on line art and was declined") by the GM's words above. To REVERSE:
#: `PICTURE_FORMAT = "WEBP"` with `lossless=True, quality=100, method=0` in `_PICTURE_CHILD` and the mime back to
#: image/webp - these three lines are the whole of the decision.
PICTURE_FORMAT = "JPEG"
PICTURE_QUALITY = 90
PICTURE_SUBSAMPLING = 0  # 4:4:4
PICTURE_MIME = "image/jpeg"
#: THE PICTURE IS RENDERED IN TILES, IN PARALLEL (feature 223, GM 2026-09-11: "is there anything that we can do
#: about that SVG render time?"). resvg is single-threaded and the picture's cost is its pixel count, not its ink
#: (Inashiro at zoom 3 with every blade removed still took 2.4 s of 26 megapixels - specs/223 research R1), so the
#: picture is split into an n x n grid of PIXEL-ALIGNED tiles, each rendered by its own resvg process from the same
#: document with the tile's viewBox and the same `--zoom`, all at once, and the encode child pastes them into one
#: image. A tile's viewBox origin is the picture's origin plus a whole number of MAP pixels, and its size a whole
#: number of map pixels, so at an integer zoom every tile pixel is a whole number of picture pixels from the origin
#: and resvg rasterizes it from the same geometry-to-pixel mapping the single render used: the stitched picture is
#: the single render pixel for pixel (`test_a_tiled_picture_is_the_single_render`; the pool's diffed by review).
#: `n` is the smallest count putting each tile under TILE_MPX megapixels - every resvg process parses the whole
#: document (~0.3 s), so tiles cost parse time in proportion; 8 puts a hamlet at 2 x 2 and a city at 3 x 3.
TILE_MPX = 8.0
_VIEWBOX_ATTR = re.compile(r'viewBox="[^"]*"')
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
#: THE WRITER'S OWN ATTRIBUTE ORDER, matched directly (feature 224): every shape the engine emits leads with its
#: coordinates in one fixed order, so one anchored regex per tag reads them without building an attribute dict per
#: element; an element in any other order falls back to the general parse below, so the verdict is the same.
_FAST = {
    "circle": re.compile(r'\s*cx="(-?[\d.]+)" cy="(-?[\d.]+)" r="(-?[\d.]+)"'),
    "ellipse": re.compile(r'\s*cx="(-?[\d.]+)" cy="(-?[\d.]+)" rx="(-?[\d.]+)" ry="(-?[\d.]+)"'),
    "line": re.compile(r'\s*x1="(-?[\d.]+)" y1="(-?[\d.]+)" x2="(-?[\d.]+)" y2="(-?[\d.]+)"'),
    "rect": re.compile(r'\s*x="(-?[\d.]+)" y="(-?[\d.]+)" width="(-?[\d.]+)" height="(-?[\d.]+)"'),
}
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
        tag, attrs = m.group(1), m.group(2)
        fast = _FAST.get(tag)
        fm = fast.match(attrs) if fast else None
        if fm is not None:  # the writer's order: the numbers straight from the match
            g = [float(v) for v in fm.groups()]
            if tag == "circle":
                xs, ys = [g[0] - g[2], g[0] + g[2]], [g[1] - g[2], g[1] + g[2]]
            elif tag == "ellipse":
                xs, ys = [g[0] - g[2], g[0] + g[2]], [g[1] - g[3], g[1] + g[3]]
            elif tag == "line":
                xs, ys = [g[0], g[2]], [g[1], g[3]]
            else:
                xs, ys = [g[0], g[0] + g[2]], [g[1], g[1] + g[3]]
            return "" if outside(xs, ys) else m.group(0)
        at = dict(_ATTRS.findall(attrs))
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
    from l7r.diagram import _census  # noqa: PLC0415 - render-time only

    # THE SAME REFUSAL AS `render_png`'s, at the page's own renderer (GM 2026-09-12): a test that reaches here
    # is about to spend a resvg and a PIL child on an image nothing will look at.
    # the size asked for is whatever `--zoom`/`--width` the caller passed, times the document's own width for a
    # zoom; a probe's 40x40 lands far below the bar and a real page's raster far above it
    _px = 0.0
    for _i, _a in enumerate(args):
        if _a == "--width" and _i + 1 < len(args):
            _px = max(_px, float(args[_i + 1]))
        elif _a == "--zoom" and _i + 1 < len(args):
            _m = re.search(r'width="([\d.]+)"', doc[:400])
            _px = max(_px, float(args[_i + 1]) * (float(_m.group(1)) if _m else 1.0))
    _census.refuse_render_in_a_test("the page's raster picture", _px)
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


def tile_count(vb: Viewbox, r: float) -> int:
    """The tiles per axis for a picture of `vb` at `r` px per map px - the smallest n with each tile under TILE_MPX."""
    return max(1, math.ceil(math.sqrt(vb[2] * r * vb[3] * r / (TILE_MPX * 1e6))))


def tile_boxes(vb: Viewbox, n: int) -> list[tuple[int, int, Viewbox]]:
    """(column, row, viewBox) for an n x n split of `vb` on whole map pixels - every tile but the last in each
    axis is `ceil(size / n)` map px wide, the last takes the remainder - so an integer zoom lands every tile on
    the picture's own pixel grid."""
    mw, mh = math.ceil(vb[2] / n), math.ceil(vb[3] / n)
    xs = [min(i * mw, vb[2]) for i in range(n + 1)]
    ys = [min(j * mh, vb[3]) for j in range(n + 1)]
    return [(i, j, (vb[0] + xs[i], vb[1] + ys[j], xs[i + 1] - xs[i], ys[j + 1] - ys[j])) for j in range(n) for i in range(n) if xs[i + 1] > xs[i] and ys[j + 1] > ys[j]]


def picture(svg_text: str, r: float = RASTER_R, tiles: int | None = None) -> bytes | None:
    """The whole picture at `r` px per map px, encoded as `PICTURE_FORMAT` (a JPEG since feature 222 - the
    note at `PICTURE_FORMAT`), rendered as `tiles` x `tiles` pixel-aligned tiles in parallel (feature 223, the
    note at `TILE_MPX`; None picks the count from the pixel area). The same SVG text the page carries, so the
    same picture."""
    from l7r.diagram import _census

    _census.record("render", what="raster")  # the gate refuses a render from a test not marked as one of rendering (feature 213)
    vb = viewbox_of(svg_text[: svg_text.find(">") + 1])
    n = tiles if tiles else (tile_count(vb, r) if vb is not None else 1)
    if not float(r).is_integer():
        n = 1  # the tiles are pixel-aligned only at a whole-number zoom (the note at TILE_MPX): a fractional `r` renders single, never with a seam
    if vb is None or n <= 1:
        png = resvg_png(svg_text, "--zoom", f"{r:g}", *RESVG_FONT_ARGS)
        return None if png is None else encode_picture([(0, 0, png)])
    boxes = tile_boxes(vb, n)
    with ThreadPoolExecutor(max_workers=len(boxes)) as pool:
        jobs = [
            (i, j, pool.submit(resvg_png, _VIEWBOX_ATTR.sub(f'viewBox="{tx:g} {ty:g} {tw:g} {th:g}"', svg_text, count=1), "--zoom", f"{r:g}", *RESVG_FONT_ARGS)) for i, j, (tx, ty, tw, th) in boxes
        ]
    rendered = [(i, j, job.result()) for i, j, job in jobs]
    if any(png is None for _i, _j, png in rendered):
        return None
    return encode_picture([(i, j, png) for i, j, png in rendered if png is not None])


# THE ENCODE RUNS IN A CHILD PROCESS (feature 208, GM 2026-09-07: "write the picture in a subprocess"). PIL's
# decode of the 18.6-megapixel PNG (70 MB of RGBA) and the encoder's working memory are C allocations the Python
# process never returns to the OS: measured on one worker with the lossless WebP encode, the page write went
# 146 -> 598 -> 173 MB and the worker then RESTED at 250 MB where the roll itself had ended at 121 - eight such
# workers under the gate was the 3 GiB the GM asked about (specs/208 research.md R1). In a child the spike lives
# and dies with it; the parent holds the 6 MB PNG and the picture. The child imports only PIL - no engine module,
# so the make-only guard has nothing to say and coverage nothing to measure (the snippet is data here).
# The picture is opaque (its alpha channel is 255 everywhere - the sheet is drawn), so the RGB conversion JPEG
# needs loses nothing. (Feature 203's lossless method 0 over method 4 - 2.2 s vs 9.6 s - is history since 222.)
_PICTURE_CHILD = (
    "import io, pickle, sys\n"
    "from PIL import Image\n"
    "tiles = pickle.load(sys.stdin.buffer)\n"
    "ims = {(c, r): Image.open(io.BytesIO(b)) for c, r, b in tiles}\n"
    "cols, rows = sorted({c for c, _r in ims}), sorted({r for _c, r in ims})\n"
    "ws, hs = [ims[(c, rows[0])].width for c in cols], [ims[(cols[0], r)].height for r in rows]\n"
    "out = Image.new('RGB', (sum(ws), sum(hs)))\n"
    "y = 0\n"
    "for r, h in zip(rows, hs):\n"
    "    x = 0\n"
    "    for c, w in zip(cols, ws):\n"
    "        out.paste(ims[(c, r)].convert('RGB'), (x, y))\n"
    "        x += w\n"
    "    y += h\n"
    "buf = io.BytesIO()\n"
    f"out.save(buf, {PICTURE_FORMAT!r}, quality={PICTURE_QUALITY}, subsampling={PICTURE_SUBSAMPLING})\n"
    "sys.stdout.buffer.write(buf.getvalue())\n"
)


def encode_picture(tiles: Sequence[tuple[int, int, bytes]]) -> bytes:
    """The rendered tiles - `(column, row, PNG bytes)`, one tile for a single render - pasted into one image and
    encoded as the page's picture (`PICTURE_FORMAT`) by a child Python that imports only PIL: the same bytes an
    in-process paste-and-save would produce, without the decode and encode buffers ever living in this process.
    A child that fails raises, with its stderr, rather than returning a picture that is not one."""
    proc = subprocess.run([sys.executable, "-c", _PICTURE_CHILD], input=pickle.dumps(list(tiles)), capture_output=True, check=False)
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError(f"the picture child failed (rc={proc.returncode}): {proc.stderr.decode('utf-8', 'replace').strip()[-400:]}")
    return proc.stdout


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
