"""A grid over every watercourse segment, with each segment's keep-out half-width (feature 138).

Built for `fixture_clear_of_water`, which was measuring a probe against every segment of every stream,
channel, ditch and drawn channel - 12.5 million segment distances for one notice board on a polder.
Cached on the settlement and rebuilt when any source list changes length, exactly as
`rolling/fit.py::_water_obstacles` decides staleness; the probe's own `half` is added at query time, so
the filing inflates each segment by its half-width plus `SLACK`, the largest probe the engine makes
(a fixture's half-diagonal - the kosatsuba's is ~20 px). A probe larger than the slack falls back to
the full scan, so the answer is never wrong, only slower.
"""

from __future__ import annotations

from typing import Any

from l7r.diagram.settlement._geom.base import Pt
from l7r.diagram.settlement._geom.primitives import seg_dist

SLACK = 64.0
_SOURCES = (("streams", 9.0), ("channels", 2.5), ("field_ditches", 4.2), ("drawn_channels", 2.5))


class WaterIndex:
    __slots__ = ("cell", "grid", "segs")

    def __init__(self, M: dict[str, Any], cell: float = 128.0) -> None:
        self.segs: list[tuple[Pt, Pt, float]] = []
        for key, default in _SOURCES:
            for rec in M.get(key) or []:
                pts = rec.get("poly") or rec.get("pts") or []
                need = float(rec.get("w") or default) / 2
                for i in range(len(pts) - 1):
                    self.segs.append(((float(pts[i][0]), float(pts[i][1])), (float(pts[i + 1][0]), float(pts[i + 1][1])), need))
        self.cell = cell
        self.grid: dict[tuple[int, int], list[int]] = {}
        for idx, (a, b, need) in enumerate(self.segs):
            m = need + SLACK
            for cx in range(int((min(a[0], b[0]) - m) // cell), int((max(a[0], b[0]) + m) // cell) + 1):
                for cy in range(int((min(a[1], b[1]) - m) // cell), int((max(a[1], b[1]) + m) // cell) + 1):
                    self.grid.setdefault((cx, cy), []).append(idx)

    def clear(self, x: float, y: float, half: float) -> bool:
        """Does a point fixture of half-diagonal `half` at (x, y) stand clear of every watercourse?"""
        if half > SLACK:
            return all(seg_dist(x, y, a, b) >= need + half for a, b, need in self.segs)
        for idx in self.grid.get((int(x // self.cell), int(y // self.cell)), ()):
            a, b, need = self.segs[idx]
            if seg_dist(x, y, a, b) < need + half:
                return False
        return True


def water_index(s: Any) -> WaterIndex:
    """The settlement's cached index, rebuilt when a source list's length changed."""
    key = tuple(len(s.M.get(k) or []) for k, _d in _SOURCES)
    cached = getattr(s, "_water_index_cache", None)
    if cached is None or cached[0] != key:
        cached = (key, WaterIndex(s.M))
        s._water_index_cache = cached
    return cached[1]
