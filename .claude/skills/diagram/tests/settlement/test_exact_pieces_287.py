"""Feature 287's perf pass, its exact pieces, each against a copy of the scan it replaced: the hem's watercourses filed once
(`WetLines`), the wild middle's rings boxed once (`BoxedRings`), the copse's brook barriers filed once (`BankNear`), the site corridors' box test before the
distance (`SiteCorridors.hit_points`) and the seat's back asked each plot's y-span first (`back_fouled`). Each index PRUNES; the old test DECIDES (`dev/performance.md`)."""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.homesteads.boundary import SiteCorridors
from l7r.diagram.settlement._geom import point_quad_dist, quad_hits_seg, seg_dist, segments_cross
from l7r.diagram.settlement.fields.comb import WetLines, hem_on_water
from l7r.diagram.settlement.homestead_parts.stands import BankNear
from l7r.diagram.waterfields.hem import BoxedRings, overlaps_any


def _quad(rng: random.Random, span: float = 600.0) -> list[tuple[float, float]]:
    cx, cy, w, h, t = rng.uniform(0, span), rng.uniform(0, span), rng.uniform(4, 60), rng.uniform(4, 60), rng.uniform(0, math.pi)
    c, s = math.cos(t), math.sin(t)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]


def _polyline(rng: random.Random, span: float = 600.0) -> list[tuple[float, float]]:
    return [(rng.uniform(0, span), rng.uniform(0, span)) for _ in range(rng.randint(2, 6))]


def _old_hem_on_water(poly, wet, pond) -> bool:
    if any(quad_hits_seg(poly, pl_[i], pl_[i + 1], hw_) for pl_, hw_ in wet for i in range(len(pl_) - 1)):
        return True
    return bool(pond is not None and point_quad_dist(pond[0], pond[1], poly) < max(pond[2], pond[3]))


def test_the_hems_filed_watercourses_are_the_whole_scan() -> None:
    """A plot lies across a watercourse by the index exactly when the scan over every segment says so - strokes of every
    half-width, through, beside and far from the plot, one index asked of many plots, and a pond beside."""
    rng = random.Random(2871)
    hits = 0
    for _ in range(80):
        wet = [(_polyline(rng), rng.choice((1.25, 4.5, 7.5, 7.0))) for _ in range(rng.randint(0, 6))]
        lines = WetLines(wet)
        pond = None if rng.random() < 0.5 else (rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(10, 60), rng.uniform(10, 60))
        for _k in range(25):
            plot = _quad(rng)
            want = _old_hem_on_water(plot, wet, pond)
            hits += want
            assert hem_on_water(plot, lines, pond) is want
            assert hem_on_water(plot, wet, pond) is want
    assert 100 < hits < 1900, "the sample holds plots on the water and off it"


def _old_overlaps_any(poly, rings) -> bool:
    from shapely.geometry import Polygon

    a = Polygon(poly).buffer(0)
    x0, y0, x1, y1 = a.bounds
    for r in rings:
        if max(q[0] for q in r) < x0 or min(q[0] for q in r) > x1 or max(q[1] for q in r) < y0 or min(q[1] for q in r) > y1:
            continue
        if a.intersection(Polygon(r).buffer(0)).area > 1.0:
            return True
    return False


def test_the_boxed_rings_overlap_as_the_rings_did() -> None:
    """A plot overlaps the taken ground through the boxed rings exactly when it overlaps the rings themselves - one boxed
    set asked of many plots, the plot beside, across and far from the rings."""
    rng = random.Random(2872)
    seen = 0
    for _ in range(40):
        rings = [_quad(rng, 300.0) for _ in range(rng.randint(0, 8))]
        boxed = BoxedRings(rings)
        for _k in range(20):
            plot = _quad(rng, 300.0)
            want = _old_overlaps_any(plot, rings)
            seen += want
            assert overlaps_any(plot, boxed) is want
            assert overlaps_any(plot, rings) is want
    assert 50 < seen < 750, "the sample holds plots on the taken ground and off it"


def _old_too_near(points, reach, barriers, x, y) -> bool:
    return any(math.dist((x, y), p) <= reach and not any(segments_cross((x, y), p, a, b) for a, b in barriers) for p in points)


def test_the_copses_filed_brook_is_every_brook_segment() -> None:
    """A clump is near a house on its own bank by the filed barriers exactly when the scan over every barrier says so -
    brooks crossing the reach, lying beside it and far off, houses inside and beyond it."""
    rng = random.Random(2873)
    near = 0
    for _ in range(60):
        points = [(rng.uniform(0, 500), rng.uniform(0, 500)) for _ in range(rng.randint(0, 8))]
        brook = _polyline(rng, 500.0)
        barriers = list(zip(brook, brook[1:], strict=False))
        reach = rng.choice((40.0, 90.0, 150.0))
        index = BankNear(points, reach, barriers)
        for _k in range(40):
            x, y = rng.uniform(-20, 520), rng.uniform(-20, 520)
            want = _old_too_near(points, reach, barriers, x, y)
            near += want
            assert index.too_near(x, y) is want
    assert 100 < near < 2300, "the sample holds clumps near a house on its bank, and not"


def test_the_site_corridors_box_test_is_the_distance() -> None:
    """A point on the water corridors by `hit_points` exactly when the distance to some corridor segment is under its
    clearance - a rectangle's nine points and single points, corridors of every clearance."""
    rng = random.Random(2875)
    hits = 0
    for _ in range(60):
        water = [(a, b, rng.choice((6.0, 12.0, 20.0))) for pl in (_polyline(rng) for _ in range(rng.randint(0, 5))) for a, b in zip(pl, pl[1:], strict=False)]
        corridors = SiteCorridors((water, []))
        for _k in range(30):
            cx, cy, w, h = rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(0, 50), rng.uniform(0, 50)
            pts = [(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h), (cx, cy)] if rng.random() < 0.5 else [(cx, cy)]
            want = any(seg_dist(x, y, a, b) < clr for a, b, clr in water for x, y in pts)
            hits += want
            assert corridors.hit_points(pts) is want
    assert 100 < hits < 1700, "the sample holds points on the corridors and off them"


def _old_back_fouled(anchor, out, dep, dry_plots, reach=2.6, samples=7):
    from l7r.diagram.settlement._geom import point_in_poly

    if not dry_plots:
        return 0.0
    ax, ay = -out[1], out[0]
    hit = total = 0
    for i in range(samples):
        t = (i + 0.5) / samples
        for lat in (-0.5, 0.0, 0.5):
            px = anchor[0] + out[0] * dep * reach * t + ax * dep * lat
            py = anchor[1] + out[1] * dep * reach * t + ay * dep * lat
            total += 1
            hit += any(point_in_poly(px, py, list(poly)) for poly in dry_plots)
    return hit / total


def test_the_seats_back_is_fouled_as_the_whole_ray_test_said() -> None:
    """`back_fouled` with each plot's y-span asked first answers as the ray test over every plot did - backs under the hem,
    beside it and clear of it, and a plot with no ring."""
    from l7r.diagram.hamletgen.cluster import back_fouled

    rng = random.Random(2876)
    fouled = 0
    for _ in range(300):
        plots = [_quad(rng, 400.0) for _ in range(rng.randint(0, 12))] + ([[]] if rng.random() < 0.1 else [])
        anchor, t = (rng.uniform(0, 400), rng.uniform(0, 400)), rng.uniform(0, 2 * math.pi)
        out, dep = (math.cos(t), math.sin(t)), rng.uniform(10, 60)
        want = _old_back_fouled(anchor, out, dep, plots)
        fouled += want > 0
        assert back_fouled(anchor, out, dep, plots) == want
    assert 20 < fouled < 280, "the sample holds fouled backs and clear ones"


def test_a_house_box_refused_on_growing_grounds_refuses_every_box_that_holds_it() -> None:
    """`_house_box_refused` (the nucleated placer's first question): past the canvas margin, over a reserved corridor, on two
    placed homesteads - each refuses every box holding the house's box (`_envelope_blocked` returns True, never the one box
    a move is made from); one placed homestead alone does not refuse it (the placer's move may clear it)."""
    from l7r.diagram.settlement import Settlement
    from l7r.diagram.settlement.rolling.access import start_tree

    s = Settlement(1400, 1400, seed=3)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    s._nucleated = True
    hw, hh = 46.0, 28.0
    box = s._house_box(700.0, 700.0, hw, hh)
    assert box[:2] == (700.0, 700.0) and box[2] >= hw - 1e-9
    assert not s._house_box_refused(box)
    assert s._house_box_refused(s._house_box(20.0, 700.0, hw, hh)), "past the canvas margin"
    s.placed.append((720.0, 700.0, 40.0, 40.0))
    assert not s._house_box_refused(box), "one placed homestead: the move may clear it"
    s.placed.append((680.0, 700.0, 40.0, 40.0))
    assert s._house_box_refused(box), "two placed homesteads"
    rng = random.Random(2878)
    for _ in range(50):  # every box holding a refused house box is refused by the envelope test
        grown = (box[0] + rng.uniform(-5, 5), box[1] + rng.uniform(-5, 5), box[2] + rng.uniform(10, 80), box[3] + rng.uniform(10, 80))
        assert s._envelope_blocked(grown) is True
    t = Settlement(1400, 1400, seed=3)
    t.meta(name="V", scale="hamlet", ftpx=1, toscale=True, households=10, down_deg=90, water_flow=90, nucleated=True)
    start_tree(t, (700.0, 600.0), (0.0, 1.0), 300.0)
    assert t._house_box_refused(t._house_box(700.0, 700.0, hw, hh)), "over a reserved corridor"
