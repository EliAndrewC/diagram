"""THE REGION: the ground a thing may not take, painted ONCE, then read per candidate as array lookups (feature 297).

The GM, 2026-09-30, on the hinterland's lookups: *"we're doing a bunch of math before putting down each individual blade of
grass or marsh glyph instead of drawing a box and then filling it in with a much simpler algorithm"*. This is the box: a
raster over one consumer's WINDOW (a seat band, a grove's footprint, the woodland search's window - never the whole canvas,
whose summed-area table alone costs 0.40 s, specs/297 plan Technical Context) into which every keep-out the consumer reads is
painted once - PIL draws rects, circles, polygons and wide polylines in C - and then a point is one array read and a box four
(a summed-area table, built lazily on the first box query and again only after a later paint).

CONSERVATIVE BY CONSTRUCTION: every painter grows its shape by one cell (and a cell is taken when any part of the grown shape
touches it), so a point or a box the region calls CLEAR is clear of every painted shape. A consumer may therefore lose a seat
or a glyph at a margin it would once have kept, and never gains one a keep-out forbids - the rules hold, the map may move
(constitution X clause 15, v2.27.0: a placer may decide by a faster form; the GM: maps "do NOT need to remain identical in
output"). Ground outside the window is taken.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any

from .base import Pt

GROW = 2.0
"""How far every painted shape is grown, in cells. A cell is painted when PIL's fill covers its center; any point of the cell
lies within 0.71 cells of that center, and PIL places a wide line's edge to within a cell (measured: a pixel 5.85 cells from a
segment drawn 14 cells wide came out unpainted) - so two cells keep every point of the true shape on painted ground (the
property `tests/settlement/test_region.py` samples). Painted with PIL's own primitives, in C: buffering each shape with shapely
first was most of a region's cost (feature 297, the hinterland's sample)."""


class Region:
    """A raster of TAKEN ground over `window` = (x0, y0, x1, y1) at `cell` px. See the module docstring."""

    __slots__ = ("_draw", "_im", "_sat", "cell", "nx", "ny", "x0", "y0")

    def __init__(self, window: tuple[float, float, float, float], cell: float) -> None:
        from PIL import Image, ImageDraw  # bound on first use: no heavy library at import time (feature 237)

        x0, y0, x1, y1 = window
        self.cell, self.x0, self.y0 = float(cell), float(x0), float(y0)
        self.nx = max(1, math.ceil((x1 - x0) / cell))
        self.ny = max(1, math.ceil((y1 - y0) / cell))
        self._im = Image.new("L", (self.nx, self.ny), 0)
        self._draw = ImageDraw.Draw(self._im)
        self._sat: Any = None

    # ---- painting (every shape grown by GROW cells: conservative) ------------------------------------------------------

    def _p(self, x: float, y: float) -> tuple[float, float]:
        """A map point in raster units (pixel (i, j) covers [i, i+1) x [j, j+1) in them)."""
        return ((x - self.x0) / self.cell, (y - self.y0) / self.cell)

    def fill_many(self, geoms: Any, pads: Any) -> None:
        """Many shapely geometries, each grown by its pad: points as discs, lines as strokes, polygons filled and stroked."""
        for g, pad in zip(geoms, pads, strict=True):
            for part in getattr(g, "geoms", [g]):
                if part.is_empty:
                    continue
                kind = part.geom_type
                if kind == "Point":
                    self.circle(part.x, part.y, float(pad))
                elif kind == "LineString":
                    self.line(list(part.coords), float(pad))
                elif kind == "Polygon":
                    self.poly(list(part.exterior.coords)[:-1], float(pad))

    def _stroke(self, pts: list[tuple[float, float]], r: float) -> None:
        """A polyline in raster units, `r` cells either side and `GROW` cells more, round-capped and round-joined: PIL's wide
        line, made conservative by the margin (its edge is placed to within a cell), with a disc at every vertex."""
        rr = r + GROW
        w = max(1, math.ceil(2 * rr))
        if len(pts) >= 2:
            self._draw.line(pts, fill=1, width=w)
        for px, py in pts:
            self._draw.ellipse([px - rr, py - rr, px + rr, py + rr], fill=1)

    def rect(self, x0: float, y0: float, x1: float, y1: float, pad: float = 0.0) -> None:
        """An axis-aligned box, grown by `pad`."""
        g = GROW
        a = self._p(min(x0, x1) - pad, min(y0, y1) - pad)
        b = self._p(max(x0, x1) + pad, max(y0, y1) + pad)
        self._draw.rectangle([math.floor(a[0] - g), math.floor(a[1] - g), math.ceil(b[0] + g), math.ceil(b[1] + g)], fill=1)
        self._sat = None

    def circle(self, x: float, y: float, r: float) -> None:
        """A disc of radius `r`."""
        cx, cy = self._p(x, y)
        rr = max(r, 0.0) / self.cell + GROW
        self._draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=1)
        self._sat = None

    def poly(self, ring: Sequence[Pt], pad: float = 0.0) -> None:
        """A filled polygon, grown by `pad`: the polygon filled and its outline stroked `pad` either side."""
        if len(ring) < 3:
            return
        pts = [self._p(float(q[0]), float(q[1])) for q in ring]
        self._draw.polygon(pts, fill=1)
        self._stroke(pts + [pts[0]], max(pad, 0.0) / self.cell)
        self._sat = None

    def line(self, pts: Sequence[Pt], half: float) -> None:
        """A polyline of half-width `half`, round-capped and round-joined."""
        if not pts:
            return
        self._stroke([self._p(float(p[0]), float(p[1])) for p in pts], max(half, 0.0) / self.cell)
        self._sat = None

    def cells(self, taken: Iterable[tuple[int, int]], cell: float, x0: float, y0: float) -> None:
        """Another raster's taken cells (`(i, j)` of `cell` px from `(x0, y0)`, e.g. `FreeGround.taken`), each painted whole and
        NOT grown - such a cell is already taken at every point. On the same grid (this region's cell and origin are that
        raster's) each is exactly one cell here; otherwise every cell of this region it touches."""
        for i, j in taken:
            ax, ay = x0 + i * cell, y0 + j * cell
            i0, j0 = math.floor((ax - self.x0) / self.cell + 1e-9), math.floor((ay - self.y0) / self.cell + 1e-9)
            i1, j1 = math.ceil((ax + cell - self.x0) / self.cell - 1e-9) - 1, math.ceil((ay + cell - self.y0) / self.cell - 1e-9) - 1
            self._draw.rectangle([i0, j0, i1, j1], fill=1)
        self._sat = None

    # ---- reading -------------------------------------------------------------------------------------------------------

    def array(self) -> Any:
        """The raster as a numpy array, rows = y: 1 where taken."""
        import numpy as np

        return np.asarray(self._im, dtype=np.uint8)

    def taken(self, x: float, y: float) -> bool:
        """Is the point (x, y) on taken ground (or off the window)?"""
        i, j = math.floor((x - self.x0) / self.cell), math.floor((y - self.y0) / self.cell)
        if not (0 <= i < self.nx and 0 <= j < self.ny):
            return True
        return bool(self._im.getpixel((i, j)))

    def taken_many(self, xs: Any, ys: Any) -> Any:
        """`taken` for numpy arrays of points: a boolean array."""
        import numpy as np

        a = self.array()
        i = np.floor((np.asarray(xs, dtype=float) - self.x0) / self.cell).astype(np.int64)
        j = np.floor((np.asarray(ys, dtype=float) - self.y0) / self.cell).astype(np.int64)
        inside = (i >= 0) & (i < self.nx) & (j >= 0) & (j < self.ny)
        out = np.ones(i.shape, dtype=bool)
        out[inside] = a[j[inside], i[inside]] > 0
        return out

    def _table(self) -> Any:
        import numpy as np

        if self._sat is None:
            sat = np.zeros((self.ny + 1, self.nx + 1), dtype=np.int32)
            sat[1:, 1:] = self.array().astype(np.int32).cumsum(0).cumsum(1)
            self._sat = sat
        return self._sat

    def box_clear(self, x0: float, y0: float, x1: float, y1: float) -> bool:
        """Is every cell the box (x0, y0)-(x1, y1) touches clear? A box reaching off the window is not."""
        return bool(self.box_clear_many([x0], [y0], [x1], [y1])[0])

    def box_clear_many(self, x0s: Any, y0s: Any, x1s: Any, y1s: Any) -> Any:
        """`box_clear` for numpy arrays of boxes: a boolean array."""
        import numpy as np

        sat = self._table()
        i0 = np.floor((np.asarray(x0s, dtype=float) - self.x0) / self.cell).astype(np.int64)
        j0 = np.floor((np.asarray(y0s, dtype=float) - self.y0) / self.cell).astype(np.int64)
        i1 = np.floor((np.asarray(x1s, dtype=float) - self.x0) / self.cell).astype(np.int64) + 1
        j1 = np.floor((np.asarray(y1s, dtype=float) - self.y0) / self.cell).astype(np.int64) + 1
        inside = (i0 >= 0) & (j0 >= 0) & (i1 <= self.nx) & (j1 <= self.ny) & (i1 > i0) & (j1 > j0)
        out = np.zeros(i0.shape, dtype=bool)
        a, b, c, d = i0[inside], j0[inside], i1[inside], j1[inside]
        out[inside] = (sat[d, c] - sat[b, c] - sat[d, a] + sat[b, a]) == 0
        return out
