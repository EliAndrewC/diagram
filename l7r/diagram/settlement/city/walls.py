"""The city's defensive shell: the wall, its towers and walk, and the patrol road inside it.

Split from settlement/city.py by feature 113 - see settlement/city/CLAUDE.md for the index.

Research: plumbing - NONE
"""

import math
from typing import TYPE_CHECKING, Any

from .._geom import (
    Pt,
)

if TYPE_CHECKING:
    from ..core import Settlement


"""Research: set on the patrol road - research/questions/0147-city-and-town-gates-the-opening-the-gate-tower-and-the-crossing-of-the-moat-chengmen.drawing.html: the drawing page's GUESS, about 105 to 135 ft inside the opening"""


class WallsMixin:
    def _gapped_ring(self: Settlement, ring: Any, gates: Any, gap: float = 38, closed: bool = True, water_gates: Any = (), water_gap: float = 24) -> str:  # type: ignore[misc]
        """An SVG path for a wall (closed ring or open arc) with a genuine OPENING (~2*gap wide) at each
        gate, so the rampart can render OVER the ground lanes yet still let the road show THROUGH the gate
        - rather than painting a land rect over the wall (which would erase the road too, once on top).
        `water_gates` open NARROWER gaps (~2*water_gap) where a cargo canal passes the rampart under
        a water-gate arch (the Suzhou shuimen; the canal shows through exactly like a road at a gate)."""
        gpts = [(g[0], g[1]) for g in gates]
        wpts = [(g[0], g[1]) for g in water_gates]

        def isg(p: Any) -> bool:
            return any(math.hypot(p[0] - x, p[1] - y) < 6 for x, y in gpts) or any(math.hypot(p[0] - x, p[1] - y) < 6 for x, y in wpts)

        def gapof(p: Any) -> float:
            return water_gap if any(math.hypot(p[0] - x, p[1] - y) < 6 for x, y in wpts) else gap

        def lerp(a: Any, b: Any, d: float) -> Pt:
            length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            return (a[0] + (b[0] - a[0]) * d / length, a[1] + (b[1] - a[1]) * d / length)

        subs: list[Any] = []
        cur: list[Any] = []
        for i in range(len(ring) - 1):
            a, b = ring[i], ring[i + 1]
            s = lerp(a, b, gapof(a)) if isg(a) else a
            e = lerp(b, a, gapof(b)) if isg(b) else b
            if not cur:  # start a fresh run (the first edge, or just after a gate)
                cur = [s]
            cur.append(e)
            if isg(b):  # this edge ends at a gate - close the run (a gap follows)
                subs.append(cur)
                cur = []
        if cur:
            subs.append(cur)
        if closed and len(subs) >= 2 and not isg(ring[0]):  # closed ring, ring[0] not a gate: last run continues into the first
            subs[0] = subs[-1] + subs[0][1:]
            subs.pop()
        return ' '.join('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in sp) for sp in subs)
