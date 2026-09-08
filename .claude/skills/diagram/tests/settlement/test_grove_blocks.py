"""The grove's indexed keep-outs answer exactly what the linear scans answered (feature 218).

The index PRUNES and the same expressions DECIDE, so on any layout the verdict must equal the
per-candidate walk `village_grove` used to run. This proves it on a synthetic layout that exercises
every keep-out class at least once - a crop edge inside its pad, a dry plot, a dike interior, a
watercourse within reach, a corridor, an occupancy circle, each open rectangle, the outline's rim,
and a seated neighbor - over a lattice of sample points, with plain lists and tuples (feature 146:
no settlement is rolled to ask a yes/no question)."""

from __future__ import annotations

import itertools

from l7r.diagram.settlement._geom import edge_dist, point_in_poly, seg_dist
from l7r.diagram.settlement.homestead_parts.grove_blocks import GroveBlocks, Seats

OUTLINE = [(0.0, 0.0), (400.0, 20.0), (420.0, 300.0), (10.0, 280.0)]
CROPS = [[(50.0, 50.0), (150.0, 55.0), (140.0, 150.0), (60.0, 140.0)]]
DRY = [[(300.0, 200.0), (380.0, 200.0), (380.0, 260.0), (300.0, 260.0)]]
DIKES = [[(200.0, 60.0), (260.0, 60.0), (260.0, 120.0), (200.0, 120.0)]]
WATER = [([(0.0, 200.0), (200.0, 210.0), (400.0, 190.0)], 9.0)]
CORRIDORS = [([(220.0, 0.0), (230.0, 300.0)], 7.0)]
CIRCLES = [(100.0, 220.0, 30.0), (350.0, 80.0, 25.0)]
DISPLACERS = [(350.0, 80.0, 25.0)]
RECTS = [(120.0, 160.0, 180.0, 200.0), (280.0, 20.0, 330.0, 60.0)]
CROP_PAD, DRY_PAD, CLUMP = 26.0, 12.0, 28.0
LATTICE = [(float(x), float(y)) for x, y in itertools.product(range(-20, 440, 7), range(-20, 320, 7))]


def _linear_hard(x: float, y: float) -> bool:
    return (
        any(point_in_poly(x, y, f) or edge_dist(x, y, f) < CROP_PAD for f in CROPS)
        or any(point_in_poly(x, y, d) or edge_dist(x, y, d) < DRY_PAD for d in DRY)
        or any(point_in_poly(x, y, dk) for dk in DIKES)
        or any(seg_dist(x, y, wl[k], wl[k + 1]) < hw for wl, hw in WATER for k in range(len(wl) - 1))
    )


def _linear_lane(x: float, y: float) -> bool:
    return any(seg_dist(x, y, lp[k], lp[k + 1]) < buf for lp, buf in CORRIDORS for k in range(len(lp) - 1))


def _linear_local(x: float, y: float) -> bool:
    return any((x - ox) ** 2 + (y - oy) ** 2 < rr * rr for ox, oy, rr in CIRCLES) or any(x0 < x < x1 and y0 < y < y1 for x0, y0, x1, y1 in RECTS)


def _blocks() -> GroveBlocks:
    return GroveBlocks(outline=OUTLINE, crops=CROPS, crop_pad=CROP_PAD, dry=DRY, dry_pad=DRY_PAD, dikes=DIKES, water=WATER, corridors=CORRIDORS, circles=CIRCLES, displacers=DISPLACERS, rects=RECTS)


def test_every_indexed_verdict_equals_the_linear_scan_on_a_lattice() -> None:
    b = _blocks()
    fired = {"hard": 0, "lane": 0, "local": 0, "displaced": 0, "inside": 0, "rim": 0}
    for x, y in LATTICE:
        assert b.hard(x, y) == _linear_hard(x, y), (x, y)
        assert b.lane(x, y) == _linear_lane(x, y), (x, y)
        assert b.local(x, y) == _linear_local(x, y), (x, y)
        assert b.displaced(x, y) == any((x - ox) ** 2 + (y - oy) ** 2 < rr * rr for ox, oy, rr in DISPLACERS), (x, y)
        assert b.inside(x, y) == point_in_poly(x, y, OUTLINE), (x, y)
        assert b.rim_within(x, y, CLUMP) == (edge_dist(x, y, OUTLINE) <= CLUMP), (x, y)
        for key, hit in (("hard", b.hard(x, y)), ("lane", b.lane(x, y)), ("local", b.local(x, y)), ("displaced", b.displaced(x, y)), ("inside", b.inside(x, y)), ("rim", b.rim_within(x, y, CLUMP))):
            fired[key] += hit
    assert all(fired.values()), fired  # every class fired at least once, or the lattice proved nothing


def test_each_hard_term_fires_on_its_own_class() -> None:
    b = _blocks()
    assert b.hard(100.0, 100.0)  # inside the crop
    assert b.hard(160.0, 100.0) and not b.hard(200.0, 40.0)  # 10 ft off the crop edge is inside the 26 ft pad; the open ground is not
    assert b.hard(290.0, 230.0) and not b.hard(280.0, 230.0)  # the dry plot's 12 ft pad, and the point 20 ft off it
    assert b.hard(230.0, 90.0)  # inside the dike outline
    assert b.hard(100.0, 210.0) and not b.hard(100.0, 240.0)  # within the stream's reach; 35 ft off it


def test_rim_within_is_the_closed_inequality() -> None:
    b = _blocks()
    # a point exactly `limit` from the bottom edge (y = 0 between x 0 and 400 is not an edge; use the
    # left edge x = 0..10 - simpler: the top edge from (0, 0) to (400, 20) has a point at exact distance)
    x, y = 200.0, 10.0 + 30.0  # 30 ft below the top edge's midpoint region, roughly
    d = edge_dist(x, y, OUTLINE)
    assert b.rim_within(x, y, d) is True  # `<=`: the exact distance itself counts
    assert b.rim_within(x, y, d - 1e-6) is False


def test_seats_files_incrementally_and_matches_the_linear_test() -> None:
    s = Seats(11.0)
    placed: list[tuple[float, float]] = []
    for i, (x, y) in enumerate([(10.0, 10.0), (300.0, 40.0), (18.0, 12.0), (600.0, 600.0)]):
        for qx, qy in LATTICE[:: max(1, i + 1)]:
            assert s.too_near(qx, qy) == any((qx - sx) ** 2 + (qy - sy) ** 2 < 11.0**2 for sx, sy in placed), (qx, qy, placed)
        s.add(x, y)
        placed.append((x, y))
    assert s.too_near(10.5, 10.5) and s.too_near(299.0, 41.0) and not s.too_near(150.0, 150.0)
