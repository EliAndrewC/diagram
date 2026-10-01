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

GROW = 1.5
"""How far every painted shape is grown, in cells. A cell is painted when PIL's fill covers its center; any point of the cell
lies within 0.71 cells of that center, and PIL places a vertex to within half a cell - so 1.5 cells keeps every point of the
true shape on painted ground (the property `tests/settlement/test_region.py` samples)."""


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

    def _fill(self, geom: Any) -> None:
        """Paint a shapely geometry, grown by `GROW` cells: its exterior rings filled (a hole filled too only takes more ground)."""
        g = geom.buffer(GROW * self.cell, quad_segs=4)
        for part in getattr(g, "geoms", [g]):
            if part.is_empty:
                continue
            ring = [((x - self.x0) / self.cell, (y - self.y0) / self.cell) for x, y in part.exterior.coords]
            if len(ring) >= 3:
                self._draw.polygon(ring, fill=1)
        self._sat = None

    def rect(self, x0: float, y0: float, x1: float, y1: float, pad: float = 0.0) -> None:
        """An axis-aligned box, grown by `pad`."""
        from shapely.geometry import box

        self._fill(box(min(x0, x1) - pad, min(y0, y1) - pad, max(x0, x1) + pad, max(y0, y1) + pad))

    def circle(self, x: float, y: float, r: float) -> None:
        """A disc of radius `r`."""
        from shapely.geometry import Point

        self._fill(Point(x, y).buffer(max(r, 0.0), quad_segs=8))

    def poly(self, ring: Sequence[Pt], pad: float = 0.0) -> None:
        """A filled polygon, grown by `pad`."""
        from shapely.geometry import Polygon

        if len(ring) < 3:
            return
        g = Polygon([(float(q[0]), float(q[1])) for q in ring])
        if not g.is_valid:
            g = g.buffer(0)
        self._fill(g.buffer(pad, quad_segs=4) if pad > 0 else g)

    def line(self, pts: Sequence[Pt], half: float) -> None:
        """A polyline of half-width `half`, round-capped and round-joined."""
        from shapely.geometry import LineString, Point

        if not pts:
            return
        q = [(float(p[0]), float(p[1])) for p in pts]
        self._fill((LineString(q) if len(q) >= 2 else Point(q[0])).buffer(max(half, 0.0), quad_segs=4))

    def cells(self, taken: Iterable[tuple[int, int]], cell: float, x0: float, y0: float) -> None:
        """Another raster's taken cells (`(i, j)` of `cell` px from `(x0, y0)`, e.g. `FreeGround.taken`), each painted whole."""
        for i, j in taken:
            self.rect(x0 + i * cell, y0 + j * cell, x0 + (i + 1) * cell, y0 + (j + 1) * cell)

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
