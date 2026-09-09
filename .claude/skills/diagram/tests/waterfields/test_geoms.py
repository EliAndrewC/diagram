"""`PlotGeoms` and `GeomTree` answer what the seam passes' scans answered (feature 220): one geometry per
ring object, dropped when the ring is reassigned; neighbors from a tree equal to the vertex-extent
gate the passes compared by hand, including a basin the pass has replaced since the tree was built."""

from __future__ import annotations

import random

from shapely.geometry import Polygon

from l7r.diagram.waterfields.seams.geoms import GeomTree, PlotGeoms


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
