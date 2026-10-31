"""Feature 387 T03 (plan D3): a merge measures each live neighbor's shared bund ONCE - the hits of the index are mapped to their
live owners and deduplicated before `shared_length` is asked - and finds exactly the neighbors, in exactly the order, that the
old form (every hit measured, then deduplicated) found. The old form is kept here as the oracle, never in the engine."""

from __future__ import annotations

from typing import Any

from l7r.diagram.waterfields import settle as st

CELL = 48.0 * 31.0
ACROSS = 48.0


def _box(x0: float, y0: float, x1: float, y1: float) -> Any:
    from shapely.geometry import box

    return box(x0, y0, x1, y1)


def _old_neighbors(fab: st.Fabric, i: int) -> list[int]:
    """`Fabric.neighbors` before feature 387: every hit's owner measured, duplicates dropped after."""
    me = fab.alive[i]
    scored = set()
    for jj in fab.tree.query(me.buffer(0.2)):
        j = fab.find(fab.ids[int(jj)])
        if j != i and j in fab.alive:
            shared = st.shared_length(me, fab.alive[j])
            if shared > 0.0:
                scored.add((shared, j))
    return [j for _s, j in sorted(scored, reverse=True)]


def _strips() -> list[Any]:
    """A field of thin strips (each far under the area floor) beside two lawful basins: merges cascade, so most index hits are
    stale cells absorbed into a live owner - the shape that grew the measurements per merge (`m:counts-before`)."""
    cells = [_box(3 * k, 0, 3 * k + 3, 31) for k in range(12)]
    cells += [_box(3 * k, 31, 3 * k + 3, 62) for k in range(12)]
    cells += [_box(36, 0, 84, 31), _box(36, 31, 84, 62)]
    return cells
