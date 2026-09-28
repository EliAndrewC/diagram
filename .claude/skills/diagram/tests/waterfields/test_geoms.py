"""`PlotGeoms` and `GeomTree` answer what the seam passes' scans answered (feature 220): one geometry per
ring object, dropped when the ring is reassigned; neighbors from a tree equal to the vertex-extent
gate the passes compared by hand, including a basin the pass has replaced since the tree was built."""

from __future__ import annotations

import random
from typing import Any

from l7r.diagram.waterfields.seams.geoms import GeomTree, PlotGeoms


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


def test_plot_geoms_caches_per_ring_object_and_drops_a_reassigned_ring() -> None:
    plots = [{"poly": r} for r in _rings(random.Random(1), 5)]
    plots.append({"poly": [(0.0, 0.0), (1.0, 0.0)]})  # under three vertices: never a candidate
    g = PlotGeoms(plots)
    a = g.geom(2)
    assert g.geom(2) is a  # the same ring object, the same geometry
    plots[2]["poly"] = [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0)]
    b = g.geom(2)
    assert b is not a and abs(b.area - 2500.0) < 1e-6
    assert 5 not in g.near((0.0, 0.0, 1000.0, 1000.0))


def test_plot_geoms_near_equals_the_vertex_gate_before_and_after_rings_change() -> None:
    rng = random.Random(220)
    plots = [{"poly": r} for r in _rings(rng, 60)]
    g = PlotGeoms(plots)
    for _ in range(40):
        bx = (rng.uniform(0, 900), rng.uniform(0, 900))
        bounds = (bx[0], bx[1], bx[0] + rng.uniform(5, 120), bx[1] + rng.uniform(5, 120))
        ex = rng.randrange(60)
        assert g.near(bounds, exclude=ex) == _gate(plots, bounds, ex)
        if rng.random() < 0.3:  # a trade reassigns a ring; the tree must see the new extent
            k = rng.randrange(60)
            x, y = rng.uniform(0, 900), rng.uniform(0, 900)
            plots[k]["poly"] = [(x, y), (x + 40.0, y), (x + 40.0, y + 30.0), (x, y + 30.0)]


def test_plot_geoms_answers_a_changed_ring_directly_and_rebuilds_only_past_the_stale_bar(monkeypatch: Any) -> None:
    """Feature 276: a reassigned ring is tested against its CURRENT extent while the tree stands - including a ring
    that drops under three vertices or climbs back over - and the tree is rebuilt when the list grows or the stale
    set passes the bar. Every answer equals the passes' own gate."""
    from l7r.diagram.waterfields.seams import geoms as geoms_mod

    monkeypatch.setattr(geoms_mod, "_STALE_REBUILD", 3)
    rng = random.Random(276)
    plots = [{"poly": r} for r in _rings(rng, 30)]
    plots.append({"poly": [(0.0, 0.0), (1.0, 0.0)]})
    g = PlotGeoms(plots)
    q = (100.0, 100.0, 400.0, 400.0)
    assert g.near(q) == _gate(plots, q, -1)
    tree = g._tree
    plots[4]["poly"] = [(0.0, 0.0), (1.0, 1.0)]  # under three: leaves the answer
    plots[30]["poly"] = [(150.0, 150.0), (160.0, 150.0), (160.0, 160.0)]  # climbs over: joins it
    plots[7]["poly"] = [(200.0, 200.0), (220.0, 200.0), (220.0, 220.0), (200.0, 220.0)]
    got = g.near(q)
    assert got == _gate(plots, q, -1) and 30 in got and 4 not in got and 7 in got
    assert g._tree is tree, "three stale rings are answered directly, not by a rebuild"
    plots[9]["poly"] = [(900.0, 900.0), (910.0, 900.0), (910.0, 910.0)]  # the fourth: past the bar
    assert g.near(q) == _gate(plots, q, -1) and g._tree is not tree
    tree = g._tree
    plots.append({"poly": [(300.0, 300.0), (310.0, 300.0), (310.0, 310.0)]})  # the list grew
    assert g.near(q) == _gate(plots, q, -1) and g._tree is not tree


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
