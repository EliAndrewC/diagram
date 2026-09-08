"""`KeepoutGrid` answers exactly what the family-by-family scans answered (feature 218).

One grid holds every keep-out of a scatter; a point reads its cell once. The verdict must equal the
per-family linear tests the scatters ran before - rings inside or within a pad, segments within a
reach, closed and open rectangles, closed and open circles - including the per-query extras a slot
carries and the `None` that exempts a family for one query. Plain lists and tuples, no settlement."""

from __future__ import annotations

import itertools

from l7r.diagram.settlement._geom import KeepoutGrid, edge_dist, point_in_poly, seg_dist

RINGS_A = [[(100.0, 100.0), (200.0, 110.0), (190.0, 200.0), (110.0, 190.0)]]
RINGS_B = [[(400.0, 300.0), (480.0, 300.0), (480.0, 380.0), (400.0, 380.0)]]
SEGS = [([(0.0, 250.0), (300.0, 260.0), (600.0, 240.0)], 6.0)]
CRESTS = [([(350.0, 0.0), (360.0, 400.0)], 4.0)]
RECTS = [(150.0, 300.0, 210.0, 340.0)]
CIRCLES = [(500.0, 100.0, 30.0)]
LATTICE = [(float(x), float(y)) for x, y in itertools.product(range(-10, 620, 9), range(-10, 420, 9))]


def _grid() -> KeepoutGrid:
    k = KeepoutGrid()
    k.rings(RINGS_A, pad=10.0, slot=1, reach=20.0)  # grows by the query's slot-1 extra
    k.rings(RINGS_B)  # inside only
    k.segs(SEGS)
    k.segs(CRESTS, slot=2, reach=25.0)  # grows by slot 2, or is skipped when slot 2 is None
    k.rects(RECTS, closed=True)
    k.circles(CIRCLES, closed=True)
    return k


def _linear(px: float, py: float, extra_a: float, extra_c: float | None) -> bool:
    return (
        any(point_in_poly(px, py, r) or edge_dist(px, py, r) < 10.0 + extra_a for r in RINGS_A)
        or any(point_in_poly(px, py, r) for r in RINGS_B)
        or any(seg_dist(px, py, pl[i], pl[i + 1]) < hw for pl, hw in SEGS for i in range(len(pl) - 1))
        or (extra_c is not None and any(seg_dist(px, py, pl[i], pl[i + 1]) < hw + extra_c for pl, hw in CRESTS for i in range(len(pl) - 1)))
        or any(x0 <= px <= x1 and y0 <= py <= y1 for x0, y0, x1, y1 in RECTS)
        or any((px - cx) ** 2 + (py - cy) ** 2 <= r * r for cx, cy, r in CIRCLES)
    )


def test_one_grid_equals_every_family_scan_for_every_query_shape() -> None:
    k = _grid()
    for extra_a, extra_c in ((0.0, 0.0), (15.0, 20.0), (5.0, None)):
        hits = 0
        for x, y in LATTICE:
            got = k.hit(x, y, (0.0, extra_a, extra_c))
            assert got == _linear(x, y, extra_a, extra_c), (x, y, extra_a, extra_c)
            hits += got
        assert 0 < hits < len(LATTICE)


def test_each_family_fires_on_its_own_class_and_a_none_slot_exempts_it() -> None:
    k = _grid()
    assert k.hit(150.0, 150.0, (0.0, 0.0, 0.0))  # inside ring A
    assert k.hit(204.0, 150.0, (0.0, 0.0, 0.0)) and not k.hit(215.0, 150.0, (0.0, 0.0, 0.0))  # within A's 10 px pad (the edge is at x ~195.6), then beyond it
    assert k.hit(215.0, 150.0, (0.0, 15.0, 0.0))  # ... unless the query widens the pad
    assert k.hit(440.0, 340.0, (0.0, 0.0, 0.0)) and not k.hit(440.0, 385.0, (0.0, 0.0, 0.0))  # ring B is inside-only
    assert k.hit(100.0, 256.0, (0.0, 0.0, 0.0))  # on the segment
    assert k.hit(357.0, 200.0, (0.0, 0.0, 0.0)) and not k.hit(370.0, 200.0, (0.0, 0.0, 0.0))  # the crest at its base reach
    assert k.hit(370.0, 200.0, (0.0, 0.0, 20.0))  # ... widened by slot 2
    assert not k.hit(357.0, 200.0, (0.0, 0.0, None))  # ... and exempt when slot 2 is None
    assert not k.hit(150.0, 150.0, (0.0, None, 0.0))  # a None slot exempts a RING family the same way, even from its interior
    assert k.hit(150.0, 300.0, (0.0, 0.0, 0.0)) and not k.hit(149.0, 300.0, (0.0, 0.0, 0.0))  # the closed rect counts its edge
    assert k.hit(530.0, 100.0, (0.0, 0.0, 0.0)) and not k.hit(531.0, 100.0, (0.0, 0.0, 0.0))  # the closed circle counts its rim


def test_open_rects_and_circles_exclude_their_boundary() -> None:
    k = KeepoutGrid()
    k.rects(RECTS)
    k.circles(CIRCLES)
    assert not k.hit(150.0, 300.0) and k.hit(151.0, 301.0)
    assert not k.hit(530.0, 100.0) and k.hit(529.0, 100.0)


def test_a_ring_with_no_pad_and_no_extra_is_inside_only() -> None:
    k = KeepoutGrid()
    k.rings(RINGS_A, reach=12.0)  # the box must carry the widest extra a query may add - the grid's contract
    assert k.hit(150.0, 150.0) and not k.hit(205.0, 150.0)  # ~9 px off the edge is clear with pad 0
    assert k.hit(205.0, 150.0, (12.0,))  # ... and refused once the query's extra reaches it
