"""Light one class on a map's page and report which classes' pixels change - the reviewer's page measurement.

WHY THIS EXISTS (feature 231, GM 2026-09-12: *"there's no reason to need to write a scratch script to do
pixel checks every single time ... think about what that reviewer pass is actually doing and what tools it
needs, and then give it those tools"*). On feature 228 the session wrote a pixel check four times and the
settlement-review then wrote a better one: for a class lit on the page, what share of every OTHER class's
pixels changes? The page already knows which class every map pixel belongs to - its class id map
(`interactive/raster.id_map`: one red value per class at 1 px per map px, carried in the page's payload
with its palette) - and it exposes `window.l7rMap.highlight`, so the measurement is a screenshot before and
after lighting, each screen pixel attributed through the SVG's screen transform to the class the id map
answers there. No manifest polygons, any class, any map.

MEASUREMENT, NEVER VERDICT (feature 193): this prints shares; the reviewer judges them.

Run from the skill root:

    python3 -m l7r.diagram.tools.page_lit pool/hamlets/kuwabata/kuwabata.html "mulberry dike" [--vector] [--out lit.png]
    make page-lit MAP=pool/hamlets/kuwabata/kuwabata.html CLASS="mulberry dike" [VECTOR=1] [OUT=lit.png]

Raster mode at the page's opening view by default (the view a reader meets); `--vector` zooms past the
raster switch first, so the vector page is measured instead.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import io
import json
import os
import re
import sys
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # the names for the type checker; `_load_arrays` binds the runtime ones
    import numpy as np
    from PIL import Image

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


_IDMAP = re.compile(r'"idmap":\s*"data:image/png;base64,([A-Za-z0-9+/=]+)"')
_PALETTE = re.compile(r'"palette":\s*(\{[^{}]*\})')
_STEP = re.compile(r'"step":\s*(\d+)')
#: a channel must move by MORE than this for a pixel to count as changed - the page's own antialiasing
#: at a lit edge moves a fringe pixel by a few units and is not a lit feature
THRESHOLD = 6
#: the opening viewport, the browser tests' size
VIEWPORT = (1400, 1000)
#: how many wheel steps `--vector` may take before giving up on reaching the vector page
ZOOM_STEPS = 24


def decode_idmap(html: str) -> tuple[np.ndarray, dict[int, str], int] | None:
    """(the id map's red channel as an array, {red value: class key}, the palette step) from a page's
    text, or None when the page carries no id map (rendered without resvg)."""
    _load_arrays()
    m, p, s = _IDMAP.search(html), _PALETTE.search(html), _STEP.search(html)
    if not (m and p and s):
        return None
    im = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")
    red = np.asarray(im)[:, :, 0].astype(np.int64)
    palette = {int(k): v for k, v in json.loads(p.group(1)).items()}
    return red, palette, int(s.group(1))


def attribute(
    before: Image.Image,
    after: Image.Image,
    red: np.ndarray,
    palette: dict[int, str],
    ctm: Sequence[float],
    threshold: int = THRESHOLD,
    viewbox: Sequence[float] | None = None,
) -> dict[str, tuple[int, int]]:
    """{class key: (changed pixels, on-screen pixels)} for a screenshot pair. Each screen pixel's center is
    carried to map coordinates through the inverse of `ctm` (the SVG's `getScreenCTM`, as a, b, c, d, e, f)
    and answered by the id map exactly as the page answers the pointer: a red value within 1 of a palette
    entry is that class (`page.js keyAtPoint`). Pixels off the map or on no class are dropped.

    THE ID MAP IS THE VIEWBOX, NOT THE MAP (feature 200 drops the off-map ink and crops the viewBox, so
    Kuwabata's page opens on `viewBox="1792 326 955 1954"`). `viewbox` is that rectangle: a map coordinate
    is shifted by its origin and scaled by the image's pixels per user unit before the id map is asked.
    Without it every sample lands outside the image and every class measures zero - which is exactly what
    the first cut reported on the first real page it was pointed at. `None` means the id map IS the map."""
    _load_arrays()
    a_ = np.asarray(before.convert("RGB")).astype(np.int64)
    b_ = np.asarray(after.convert("RGB")).astype(np.int64)
    changed = np.abs(a_ - b_).max(axis=2) > threshold
    h, w = changed.shape
    a, b, c, d, e, f = (float(v) for v in ctm)
    det = a * d - b * c
    sx, sy = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    ux = ((sx - e) * d - (sy - f) * c) / det
    uy = ((sy - f) * a - (sx - e) * b) / det
    rows, cols = red.shape
    vx, vy, vw, vh = viewbox if viewbox is not None else (0.0, 0.0, float(cols), float(rows))
    mx = np.floor((ux - vx) * (cols / vw)).astype(np.int64)
    my = np.floor((uy - vy) * (rows / vh)).astype(np.int64)
    inside = (mx >= 0) & (my >= 0) & (mx < cols) & (my < rows)
    keys = sorted(palette)
    lut = np.full(256, -1, dtype=np.int64)
    for i, v in enumerate(keys):
        lut[max(0, v - 1) : min(256, v + 2)] = i
    cls = np.full((h, w), -1, dtype=np.int64)
    cls[inside] = lut[red[my[inside], mx[inside]]]
    out: dict[str, tuple[int, int]] = {}
    for i, v in enumerate(keys):
        on = cls == i
        out[palette[v]] = (int((on & changed).sum()), int(on.sum()))
    return out


def _painted(page: Any) -> None:
    """Return once the browser has PAINTED what the page has been told to show.

    A wall-clock wait is not a paint: measured on a two-class synthetic page, a fixed 300 ms gave a
    before-shot of a map that had not drawn yet (every pixel then "changed") in one run and an
    after-shot the highlight had not reached in another - the same instrument reporting 100% and 0% on
    the same page. Two animation frames is the browser telling us instead of us guessing."""
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


@contextlib.contextmanager
def _chromium() -> Iterator[Any]:
    """A Chromium of the tool's own, when the caller has none to lend (the browser tests lend theirs)."""
    from playwright.sync_api import sync_playwright  # here, so the module imports where Playwright is absent

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            yield browser
        finally:
            browser.close()


def measure(html_path: str, key: str, vector: bool = False, browser: Any = None, out: str | None = None, viewport: tuple[int, int] = VIEWPORT) -> dict[str, Any]:
    """Open the page, light `key`, and attribute what changed. `browser` is a Playwright browser to reuse;
    without one the tool launches its own. `out` saves the lit screenshot."""
    _load_arrays()
    with open(html_path, encoding="utf-8") as fh:
        decoded = decode_idmap(fh.read())
    if decoded is None:
        raise SystemExit(f"{html_path} carries no class id map (rendered without resvg?) - nothing to attribute pixels to")
    red, palette, _step = decoded
    if browser is None:
        with _chromium() as own:
            return measure(html_path, key, vector, own, out, viewport)
    page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]}, device_scale_factor=1)
    try:
        page.goto("file://" + os.path.abspath(html_path))
        page.wait_for_function("window.l7rMap && window.l7rMap.rasterReady()", timeout=60000)
        if vector:
            for _ in range(ZOOM_STEPS):
                if page.evaluate("window.l7rMap.mode()") == "vector":
                    break
                page.mouse.move(viewport[0] / 2, viewport[1] / 2)
                page.mouse.wheel(0, -300)
                page.wait_for_timeout(120)
        mode = page.evaluate("window.l7rMap.mode()")
        zoom = float(page.evaluate("window.l7rMap.zoom()"))
        ctm = page.evaluate("(() => { var m = document.getElementById('map').getScreenCTM(); return [m.a, m.b, m.c, m.d, m.e, m.f]; })()")
        vb = page.evaluate("(() => { var v = document.getElementById('map').getAttribute('viewBox'); return v ? v.trim().split(/[\\s,]+/).map(Number) : null; })()")
        # NOTHING IS LIT IN THE `before` SHOT. The browser's pointer starts at (0, 0), which is ON the map,
        # so the page lights whatever class lies under that corner - measured on a two-class synthetic page,
        # the before-shot arrived with the left class already gold, and the diff then reported BOTH classes
        # as fully changed. The zoom path moves the pointer as well, so the clear belongs here, last.
        page.evaluate("() => window.l7rMap.highlight(null)")
        _painted(page)
        before = Image.open(io.BytesIO(page.screenshot()))
        page.evaluate("k => window.l7rMap.highlight(k)", key)
        _painted(page)
        after = Image.open(io.BytesIO(page.screenshot()))
    finally:
        page.close()
    if out:
        after.save(out)
    shares = attribute(before, after, red, palette, ctm, viewbox=vb)
    return {"key": key, "mode": mode, "zoom": zoom, "classes": shares}


def report(result: dict[str, Any]) -> str:
    """The shares, largest first; the lit class is what should sit at the top."""
    lines = [f"lit: {result['key']}  mode: {result['mode']}  zoom: {result['zoom']:.2f}x of fit"]
    classes: dict[str, tuple[int, int]] = result["classes"]
    if result["key"] not in classes:
        lines.append(f"  (no pixels of '{result['key']}' are on screen in this view)")
    rows = sorted(((c / t if t else 0.0, c, t, k) for k, (c, t) in classes.items() if t), reverse=True)
    lines.append(f"{'changed':>8}  {'changed':>9}/{'on screen':<9}  class")
    for share, c, t, k in rows:
        lines.append(f"{100 * share:7.1f}%  {c:>9}/{t:<9}  {k}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("page", help="the map's .html")
    ap.add_argument("key", help="the class to light, e.g. 'mulberry dike'")
    ap.add_argument("--vector", action="store_true", help="zoom past the raster switch first")
    ap.add_argument("--out", default=None, help="save the lit screenshot here")
    args = ap.parse_args(argv)
    print(report(measure(args.page, args.key, vector=args.vector, out=args.out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
