"""The copse's keep-out round a bamboo stand, and the one predicate every bamboo placer reads to leave the households'
reserved copse seats outside it (feature 280, the copse off the bamboo; feature 287 woods W25, every reserved seat
planted where it was reserved). Split out of `stands.py` at the 1,000-line bar.

Research: plumbing - NONE
"""

import math
from collections.abc import Sequence
from typing import Any


def grown_ring(ring: Any, by: float) -> list[tuple[float, float]]:
    """`ring` pushed `by` outward from its centroid, vertex by vertex - a keep-out a crown of radius `by` centered outside
    it cannot reach into, for the near-convex outlines of a bamboo stand."""
    pts = [(float(q[0]), float(q[1])) for q in ring]
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    out = []
    for x, y in pts:
        d = math.hypot(x - cx, y - cy) or 1.0
        out.append((x + (x - cx) / d * by, y + (y - cy) / d * by))
    return out


def copse_bamboo_reach(bs: float) -> float:
    """How far the copse keeps its seats off a bamboo stand (feature 280, round 4): TWO of its crowns' radii
    (`COPSE_CLUMP_BS`, the sparse copse's clump), the margin `village_grove` grows each stand's ring by.

    Research: copse off the bamboo - research/questions/0075-bamboo-groves-chikurin.drawing.html: kept two crown radii off a stand
    """
    from .wood_share import COPSE_CLUMP_BS

    return 2.0 * (COPSE_CLUMP_BS * bs / 2.0)


def stand_spares_seats(cx: float, cy: float, w: float, h: float, seats: Sequence[tuple[float, float]], bs: float) -> bool:
    """THE ONE PREDICATE of a bamboo stand leaving the reserved copse seats free (feature 287 woods W25, with feature 280's
    copse-off-the-bamboo rule): a stand whose rect is centered (cx, cy), `w` x `h`, keeps every seat outside the rect grown
    by `copse_bamboo_reach` and `BAR_MARGIN_PX` - the square that holds any ring inside the rect grown as `grown_ring`
    grows it (each vertex moved at most the reach) - so the copse never finds a household's reserved seat in a stand's
    keep-out. The thicket's seat scan, the household strips and their tests read this one predicate."""
    from .wood_share import BAR_MARGIN_PX

    rx, ry = w / 2 + copse_bamboo_reach(bs) + BAR_MARGIN_PX, h / 2 + copse_bamboo_reach(bs) + BAR_MARGIN_PX
    return not any(abs(x - cx) <= rx and abs(y - cy) <= ry for x, y in seats)
