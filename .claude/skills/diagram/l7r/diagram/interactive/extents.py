"""What the page's merge asks of an element's painted area: whether two areas touch, and whether a bucket may take one.

Moved out of `page.py` by feature 278, when the bucket grids (`_BoxGrid`, FR-011) took that file past the 1,000-line
bar; `page.py` imports every name back, so nothing that reads them moved.
"""

from __future__ import annotations

from typing import Any

#: What one element paints inside: a disc (cx, cy, r) for a circle, a box (x0, y0, x1, y1) for anything
#: else, None for a shape whose area cannot be read - which counts as being in the way everywhere.
Extent = tuple[float, float, float] | tuple[float, float, float, float] | None


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
    # FROM EACH LIST'S GRID (feature 278, FR-011): the lists were walked whole per element - up to `_SKIP_CAP` skipped
    # extents and every member's - 896,436 `_hits` over Sawada's two finishes. `_hits` is true only of two extents whose
    # boxes touch (a disc pair is judged as discs, and two discs that touch have touching boxes), so a grid of the boxes
    # returns every extent the test could find, and `_hits` decides as before. An unreadable extent is judged as before:
    # it touches everything, so the answer is whether the list holds anything.
    if (b["translucent"] or b["outlined"]) and (ext is None or b["ext_none"] or any(_hits(ext, e) for e in b["ext_grid"].near(ext))):
        return True
    if ext is None:
        return bool(b["skip"])
    return any(_hits(ext, e) for e in b["skip_grid"].near(ext))


class _BoxGrid:
    """Extents filed by their boxes in square cells, for `_refused` (feature 278). `near(ext)` returns every filed extent
    whose box shares a cell with `ext`'s box - a superset of those whose boxes touch it, since touching boxes share a
    cell. A box wider than `_BIG` cells is kept aside and always returned."""

    __slots__ = ("big", "cells")
    _CELL = 64.0
    _BIG = 24

    def __init__(self) -> None:
        self.cells: dict[tuple[int, int], list[tuple[float, ...]]] = {}
        self.big: list[tuple[float, ...]] = []

    def _span(self, e: tuple[float, ...]) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = _box(e)
        c = self._CELL
        return int(x0 // c), int(y0 // c), int(x1 // c), int(y1 // c)

    def add(self, e: tuple[float, ...]) -> None:
        i0, j0, i1, j1 = self._span(e)
        if i1 - i0 > self._BIG or j1 - j0 > self._BIG:
            self.big.append(e)
            return
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                self.cells.setdefault((i, j), []).append(e)

    def near(self, e: tuple[float, ...]) -> list[tuple[float, ...]]:
        i0, j0, i1, j1 = self._span(e)
        out = list(self.big)
        if i1 - i0 > self._BIG or j1 - j0 > self._BIG:  # a query this wide reads everything filed
            for bucket in self.cells.values():
                out.extend(bucket)
            return out
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                out.extend(self.cells.get((i, j), ()))
        return out


def _file_extent(b: dict[str, Any], ext: Extent) -> None:
    """A member's extent into its bucket's grid, or the flag that an unreadable one is among them."""
    if ext is None:
        b["ext_none"] = True
    else:
        b["ext_grid"].add(ext)
