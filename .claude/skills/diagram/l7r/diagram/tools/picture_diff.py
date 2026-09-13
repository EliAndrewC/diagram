"""Two renders of a map compared: how many pixels differ, by how much, where, and on which class's ink.

WHY THIS EXISTS (feature 231, GM 2026-09-12). The other half of what a settlement-review of a rendering
change does by hand: on feature 228 the reviewer rendered main's SVG and the clone's at full size,
diffed them, and measured how far every differing pixel lay from a pond outline - eight of its eighteen
minutes. The measurement is general: two renders (a PNG, or an SVG rendered here by the engine's own
rasterizer at the other's width), the share of differing pixels, the largest channel delta, the bounding
box, and - when the map's PAGE is given - the share of differing pixels lying on each class's ink, read
from the id map the page already carries (`interactive/raster.id_map`, decoded by `page_lit`). "Every differing pixel is on
the fish pond's ink" is one line here instead of a mask pipeline.

MEASUREMENT, NEVER VERDICT (feature 193): the reviewer decides whether 0.14% at the pond's edge is
antialiasing or a defect.

Run from the skill root:

    python3 -m l7r.diagram.tools.picture_diff main.png clone.png [--page clone.html] [--threshold 6]
    make picture-diff A=main.png B=pool/hamlets/kuwabata/kuwabata.svg PAGE=pool/hamlets/kuwabata/kuwabata.html
"""

from __future__ import annotations

import argparse
import io
import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # the names for the type checker; `_load_arrays` binds the runtime ones
    import numpy as np
    from PIL import Image

from l7r.diagram.interactive import raster
from l7r.diagram.tools import page_lit

_ARRAYS_LOADED = False


def _load_arrays() -> None:
    """Bind `numpy` and `PIL.Image` into this module, on first use rather than at import (feature 237).

    WHY. `numpy` costs 17.9 MiB of resident memory and `PIL` another 2.3, and a module-level import here
    made every one of the ten gate workers pay both merely to COLLECT this tool - a diagnostic that one
    worker runs, from `make page-lit` or `make picture-diff`
    (`specs/237-lean-test-collection/research.md` R9 and R10). It is the same deferral FR-010 made for
    `shapely`, and the GM asked for it in the same terms on 2026-09-13; the marginal figure is the larger
    half of the two, because `shapely` pulls `numpy` in anyway wherever this tool is already loaded.

    The names are bound into this module's globals ONCE, so every call site afterwards is the plain global
    lookup it was before (spec D6); the sentinel makes a repeat call two bytecodes. The per-call cost is
    irrelevant here in any case - nothing in this file runs per plot - but the form is the one the engine
    already uses, and a second form would be a second thing to learn.
    """
    global _ARRAYS_LOADED, np, Image  # binding this module's own names is the point
    if _ARRAYS_LOADED:
        return
    import numpy as np
    from PIL import Image

    _ARRAYS_LOADED = True


#: a channel must move by MORE than this for a pixel to count as differing (see page_lit.THRESHOLD)
THRESHOLD = 6
OFF_CLASS = "off any class"


def load_from_text(svg_text: str, width: int | None = None) -> Image.Image:
    """An SVG already in memory, rendered by resvg - `load`'s body for a document that is not on disk."""
    _load_arrays()
    size = ["--width", str(width)] if width else ["--zoom", "1"]
    png = raster.resvg_png(svg_text, *size, *raster.RESVG_FONT_ARGS)
    if png is None:
        raise SystemExit("resvg is not installed (sudo apt-get install -y resvg fonts-dejavu-extra) - an SVG cannot be rendered")
    return Image.open(io.BytesIO(png)).convert("RGB")


def load(path: str, width: int | None = None) -> Image.Image:
    """A render as an RGB image: a PNG as it is; an SVG rendered by resvg at `width` px (at 1 px per
    map px when no width is given), with the page's font mapping so text renders as on the page."""
    _load_arrays()
    if not path.endswith(".svg"):
        return Image.open(path).convert("RGB")
    with open(path, encoding="utf-8") as fh:
        return load_from_text(fh.read(), width)


def diff_stats(a: Image.Image, b: Image.Image, threshold: int = THRESHOLD) -> dict[str, Any]:
    """pixels, differing, share, max_delta, bbox (x0, y0, x1, y1 inclusive, or None) and the boolean mask."""
    _load_arrays()
    if a.size != b.size:
        raise ValueError(f"the renders differ in size: {a.size} against {b.size} - render the SVG at the other's width")
    a_ = np.asarray(a.convert("RGB")).astype(np.int64)
    b_ = np.asarray(b.convert("RGB")).astype(np.int64)
    delta = np.abs(a_ - b_).max(axis=2)
    mask = delta > threshold
    differing = int(mask.sum())
    bbox = None
    if differing:
        ys, xs = np.nonzero(mask)
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    return {"pixels": int(mask.size), "differing": differing, "share": differing / mask.size, "max_delta": int(delta.max()), "bbox": bbox, "mask": mask}


def id_map_of(svg_text: str) -> tuple[np.ndarray, dict[int, str]] | None:
    """(the red channel of the SVG's class id map at 1 px per map px, {red: class key}), or None without
    resvg - or when the document carries no class groups at all.

    A MAP'S `.svg` IS NOT THE PAGE'S SVG. The class groups (`<g class="f f-..." data-k="...">`) are emitted
    by the HTML target only - the drawn SVG is byte-identical to what it was before feature 134, on purpose
    - so handing this the map's own `.svg` yields an empty palette and attributes every differing pixel to
    nothing. That is what the first run against Kuwabata did. Use `id_map_of_page` for a rendered page."""
    _load_arrays()
    keys = raster.class_keys(svg_text)
    if not keys:
        return None
    png, palette = raster.id_map(svg_text, keys)
    if png is None:
        return None
    red = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))[:, :, 0].astype(np.int64)
    return red, {int(k): v for k, v in palette.items()}


def id_map_of_page(html: str) -> tuple[np.ndarray, dict[int, str]] | None:
    """The id map a rendered PAGE already carries, decoded - no second render. `None` when it carries none."""
    _load_arrays()
    decoded = page_lit.decode_idmap(html)
    if decoded is None:
        return None
    red, palette, _step = decoded
    return red, palette


def by_class(mask: np.ndarray, red: np.ndarray, palette: dict[int, str], scale: float) -> dict[str, int]:
    """{class key: differing pixels on its ink}, plus OFF_CLASS for the rest. `scale` is picture px per
    map px (the render's width over the id map's), so a picture pixel is read at its map coordinate."""
    _load_arrays()
    ys, xs = np.nonzero(mask)
    mx = np.floor(xs / scale).astype(np.int64)
    my = np.floor(ys / scale).astype(np.int64)
    rows, cols = red.shape
    inside = (mx < cols) & (my < rows)
    keys = sorted(palette)
    lut = np.full(256, -1, dtype=np.int64)
    for i, v in enumerate(keys):
        lut[max(0, v - 1) : min(256, v + 2)] = i
    cls = np.full(len(xs), -1, dtype=np.int64)
    cls[inside] = lut[red[my[inside], mx[inside]]]
    out = {palette[v]: int((cls == i).sum()) for i, v in enumerate(keys)}
    out = {k: n for k, n in out.items() if n}
    out[OFF_CLASS] = int((cls == -1).sum())
    return out


def report(stats: dict[str, Any], classes: dict[str, int] | None = None) -> str:
    lines = [
        f"differing: {stats['differing']} of {stats['pixels']} px = {100 * stats['share']:.3f}%   max channel delta: {stats['max_delta']}/255",
        f"bbox: {stats['bbox'] if stats['bbox'] else 'none (identical)'}",
    ]
    if classes:
        total = max(1, stats["differing"])
        lines.append("on the ink of:")
        for k, n in sorted(classes.items(), key=lambda kv: -kv[1]):
            lines.append(f"{100 * n / total:7.1f}%  {n:>9}  {k}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("a", help="the first render (.png or .svg) - main's, by convention")
    ap.add_argument("b", help="the second render (.png or .svg) - the clone's")
    ap.add_argument("--svg", default=None, help="a document CARRYING class groups (a page's SVG), for the per-class attribution")
    ap.add_argument("--page", default=None, help="the map's rendered .html - its own id map answers which class each differing pixel lies on")
    ap.add_argument("--threshold", type=int, default=THRESHOLD)
    args = ap.parse_args(argv)
    # a PNG fixes the size; an SVG is rendered at the other's width, or at 1 px per map px when both are SVGs
    first, second = (args.a, args.b) if not args.a.endswith(".svg") else (args.b, args.a)
    a = load(first)
    b = load(second, width=a.size[0] if second.endswith(".svg") else None)
    stats = diff_stats(a, b, args.threshold)
    classes = None
    source = args.page or args.svg
    if source and stats["differing"]:
        with open(source, encoding="utf-8") as fh:
            text = fh.read()
        ids = id_map_of_page(text) if args.page else id_map_of(text)
        if ids is not None:
            red, palette = ids
            classes = by_class(stats["mask"], red, palette, a.size[0] / red.shape[1])
    print(report(stats, classes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
