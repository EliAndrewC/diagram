"""`PlotGeoms` and `GeomTree` answer what the seam passes' scans answered (feature 220): one geometry per
ring object, dropped when the ring is reassigned; neighbors from a tree equal to the vertex-extent
gate the passes compared by hand, including a basin the pass has replaced since the tree was built."""

from __future__ import annotations

import random
from typing import Any

from l7r.diagram.waterfields.seams.geoms import GeomTree


def Polygon(*args: Any, **kwargs: Any) -> Any:
    """`shapely.geometry.Polygon`, imported on FIRST USE rather than at collection (feature 237, FR-007).

    A module-level import here cost EVERY one of the ten gate workers 16.3 MiB - shapely plus the numpy it
    drags in (`specs/237-lean-test-collection/research.md` R9) - to collect a file whose tests one worker
    runs. The name is kept so no call site changes, and a test is not a per-plot path, so the import lookup
    this adds per call is free in practice.
    """
    from shapely.geometry import Polygon as _Polygon

    return _Polygon(*args, **kwargs)


def _rings(rng: random.Random, n: int) -> list[list[tuple[float, float]]]:
    out = []
    for _ in range(n):
        x, y, w, h = rng.uniform(0, 900), rng.uniform(0, 900), rng.uniform(10, 80), rng.uniform(10, 80)
        out.append([(x, y), (x + w, y + rng.uniform(-5, 5)), (x + w, y + h), (x, y + h)])
    return out


def _gate(plots: list[dict], bounds: tuple[float, float, float, float], exclude: int) -> list[int]:
    """The passes' own vertex-extent gate, verbatim (strictly outside is refused)."""
    x0, y0, x1, y1 = bounds
    out = []
    for k, q in enumerate(plots):
        if k == exclude or len(q["poly"]) < 3:
            continue
        if max(v[0] for v in q["poly"]) < x0 or min(v[0] for v in q["poly"]) > x1 or max(v[1] for v in q["poly"]) < y0 or min(v[1] for v in q["poly"]) > y1:
            continue
        out.append(k)
    return out


def test_geom_tree_reads_a_replaced_basins_current_envelope_without_rebuilding() -> None:
    rng = random.Random(7)
    into = [Polygon(r) for r in _rings(rng, 50)]
    t = GeomTree(into)
    q = (100.0, 100.0, 140.0, 140.0)

    def gate(pad: float) -> list[int]:
        x0, y0, x1, y1 = q[0] - pad, q[1] - pad, q[2] + pad, q[3] + pad
        return [j for j, g in enumerate(into) if not (g.bounds[2] < x0 or g.bounds[0] > x1 or g.bounds[3] < y0 or g.bounds[1] > y1)]

    assert t.near(q, pad=1.0) == gate(1.0)
    tree_before = t._tree
    into[3] = Polygon([(90.0, 90.0), (150.0, 90.0), (150.0, 150.0), (90.0, 150.0)])  # grown onto the query
    t.replaced(3)
    assert 3 in t.near(q, pad=1.0) and t.near(q, pad=1.0) == gate(1.0)
    assert t._tree is tree_before  # answered from the changed set, not a rebuild
    into.append(Polygon([(120.0, 120.0), (130.0, 120.0), (130.0, 130.0), (120.0, 130.0)]))  # the list grew: a rebuild
    assert t.near(q) == gate(0.0) and t._tree is not tree_before


def test_ring_polygons_answers_per_ring_empty_or_batched(monkeypatch: Any) -> None:
    """Feature 276: rings under three vertices come back None (all of them, when none qualifies), and a batch GEOS
    refuses is rebuilt ring by ring into the same polygons."""
    import shapely

    from l7r.diagram.waterfields.seams.geoms import ring_polygons

    assert ring_polygons([[(0.0, 0.0)], []]) == [None, None]
    rings = [[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], [(0.0, 0.0), (1.0, 1.0)], [(20.0, 0.0), (30.0, 0.0), (30.0, 5.0), (20.0, 5.0)]]
    batched = ring_polygons(rings)

    real = shapely.linearrings

    def refuse(*a: Any, **k: Any) -> Any:
        if "indices" in k:  # the batched call only - `Polygon()` builds its own ring through the same function
            raise ValueError("refused")
        return real(*a, **k)

    monkeypatch.setattr(shapely, "linearrings", refuse)
    one_by_one = ring_polygons(rings)
    assert batched[1] is None and one_by_one[1] is None
    assert all(a.equals(b) for a, b in zip([batched[0], batched[2]], [one_by_one[0], one_by_one[2]], strict=True))
