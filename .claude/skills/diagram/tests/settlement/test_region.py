"""The region (feature 297, plan A): a painted shape is never read clear, the box query is the brute-force sum's answer,
and ground off the window is taken."""

import math
import random

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from l7r.diagram.settlement._geom.region import Region

WINDOW = (100.0, 50.0, 900.0, 650.0)


def _samples(geom, rng, n=400):
    """Points inside a shapely geometry (its box sampled, the points it covers kept), and points on its boundary."""
    x0, y0, x1, y1 = geom.bounds
    out = []
    while len(out) < n:
        p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if geom.covers(Point(p)):
            out.append(p)
    edge = geom.boundary
    out += [edge.interpolate(t, normalized=True).coords[0] for t in np.linspace(0, 1, 200)]
    return out


def test_no_painted_shape_is_read_clear():
    rng = random.Random(7)
    for cell in (2.0, 3.0, 8.0):
        for _ in range(6):
            r = Region(WINDOW, cell)
            cx, cy = rng.uniform(250, 750), rng.uniform(200, 500)
            ring = [(cx + rng.uniform(40, 120) * math.cos(a), cy + rng.uniform(40, 120) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
            pad = rng.choice([0.0, 3.5, 11.0])
            r.poly(ring, pad=pad)
            pts = [(rng.uniform(150, 850), rng.uniform(100, 600)) for _ in range(5)]
            half = rng.uniform(1.0, 9.0)
            r.line(pts, half)
            ccx, ccy, rad = rng.uniform(200, 800), rng.uniform(150, 550), rng.uniform(2.0, 40.0)
            r.circle(ccx, ccy, rad)
            bx, by = rng.uniform(150, 700), rng.uniform(100, 500)
            r.rect(bx, by, bx + rng.uniform(1, 90), by + rng.uniform(1, 60), pad=rng.choice([0.0, 2.0]))
            shapes = [Polygon(ring).buffer(pad) if pad else Polygon(ring), LineString(pts).buffer(half), Point(ccx, ccy).buffer(rad)]
            for g in shapes:
                for x, y in _samples(g, rng):
                    assert r.taken(x, y), (cell, x, y)
            many = [p for g in shapes for p in _samples(g, rng, 50)]
            assert r.taken_many([p[0] for p in many], [p[1] for p in many]).all()


def test_the_box_query_is_the_brute_force_sum():
    rng = random.Random(3)
    r = Region(WINDOW, 4.0)
    for _ in range(25):
        x, y = rng.uniform(100, 880), rng.uniform(50, 630)
        r.rect(x, y, x + rng.uniform(1, 40), y + rng.uniform(1, 40))
    a = r.array()
    for _ in range(400):
        x0, y0 = rng.uniform(80, 900), rng.uniform(30, 650)
        x1, y1 = x0 + rng.uniform(0.5, 120), y0 + rng.uniform(0.5, 120)
        i0, j0 = math.floor((x0 - 100) / 4), math.floor((y0 - 50) / 4)
        i1, j1 = math.floor((x1 - 100) / 4) + 1, math.floor((y1 - 50) / 4) + 1
        inside = i0 >= 0 and j0 >= 0 and i1 <= r.nx and j1 <= r.ny
        want = inside and a[j0:j1, i0:i1].sum() == 0
        assert r.box_clear(x0, y0, x1, y1) == want
    r.rect(500, 300, 510, 310)  # a paint after a query rebuilds the table
    assert not r.box_clear(495, 295, 515, 315)


def test_ground_off_the_window_is_taken_and_cells_paint_whole():
    r = Region(WINDOW, 8.0)
    assert r.taken(99.0, 300.0) and r.taken(500.0, 651.0)
    assert not r.taken(500.0, 300.0)
    assert list(r.taken_many([50.0, 500.0], [300.0, 300.0])) == [True, False]
    assert not r.box_clear(90.0, 300.0, 120.0, 320.0)
    r.cells([(3, 4)], 8.0, 100.0, 50.0)
    assert r.taken(100.0 + 3 * 8 + 4, 50.0 + 4 * 8 + 4)
    r.poly([(1.0, 1.0), (2.0, 2.0)])  # fewer than three points: nothing to fill
    r.line([], 3.0)  # no points: nothing to draw
    r.line([(300.0, 300.0)], 2.0)  # one point: a dot
    assert r.taken(300.0, 300.0)


def test_many_geometries_paint_each_by_its_kind_and_an_empty_one_paints_nothing() -> None:
    from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon, box

    r = Region(WINDOW, 4.0)
    r.fill_many([Point(200.0, 200.0), LineString([(300.0, 100.0), (400.0, 100.0)]), MultiPolygon([box(600, 400, 650, 450)]), GeometryCollection(), Polygon()], [10.0, 3.0, 0.0, 5.0, 5.0])
    assert r.taken(208.0, 200.0) and r.taken(350.0, 102.0) and r.taken(625.0, 425.0)
    assert not r.taken(500.0, 300.0)
