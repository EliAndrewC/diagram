"""Feature 306's indexed checks (the GM: an overlap check against many things means a box or a line was not drawn): the
road-over-water crossings, the footplank's keep-outs, the drain hem's reach, and the conifer belt's half-depth and marsh test each ask an
index built once, and the index PRUNES while the old test DECIDES. Each is compared here against a copy of the old scan
(the oracle `dev/performance.md` prescribes), and each comparison is shown to FAIL when the index drops a candidate - so
the equality is a test of the index, not of two scans that agree because both see nothing."""

from __future__ import annotations

import math
import random

import pytest

from l7r.diagram.settlement._geom import (
    PointGrid,
    boxed_grid,
    boxed_polys,
    boxes_meeting,
    nearest_seg_dist,
    point_in_poly,
    quad_hits_poly,
    seg_dist,
    seg_reach_index,
    segments_cross,
    within_reach,
)
from l7r.diagram.settlement.city import bridges as B

Pt = tuple[float, float]


def _walk(rng: random.Random, n: int, span: float = 600.0, step: float = 90.0) -> list[Pt]:
    out = [(rng.uniform(0, span), rng.uniform(0, span))]
    for _ in range(n - 1):
        out.append((out[-1][0] + rng.uniform(-step, step), out[-1][1] + rng.uniform(-step, step)))
    return out


def _ring(rng: random.Random, span: float = 600.0) -> list[Pt]:
    cx, cy, r = rng.uniform(0, span), rng.uniform(0, span), rng.uniform(4, 90)
    k = rng.randint(3, 8)
    return [(cx + r * rng.uniform(0.5, 1.0) * math.cos(math.tau * i / k), cy + r * rng.uniform(0.5, 1.0) * math.sin(math.tau * i / k)) for i in range(k)]


# ---- bridges(): the way-over-water crossings ---------------------------------------------------------------------------


def _old_crossings(carried, waters):
    """The scan `bridges()` made before feature 306: every way segment against every water segment, in that order."""
    out = []
    for rpts, rw in carried:
        for i in range(len(rpts) - 1):
            ra, rb = tuple(rpts[i]), tuple(rpts[i + 1])
            for wpts, ww in waters:
                for j in range(len(wpts) - 1):
                    wa, wb = tuple(wpts[j]), tuple(wpts[j + 1])
                    if segments_cross(ra, rb, wa, wb):
                        out.append((ra, rb, rw, wa, wb, ww, wpts))
    return out


def _crossing_beds(seed: int, n: int = 150):
    rng = random.Random(seed)
    for _ in range(n):
        carried = [(_walk(rng, rng.randint(2, 7)), rng.uniform(4, 30)) for _ in range(rng.randint(1, 4))]
        waters = [(_walk(rng, rng.randint(0, 9)), rng.uniform(2, 12)) for _ in range(rng.randint(1, 5))]
        # a way that meets water exactly at a vertex, and a way lying along a water segment: the degenerate ends
        if waters[0][0]:
            w0 = waters[0][0]
            carried.append(([(w0[0][0] - 30, w0[0][1] - 30), w0[0]], 6.0))
            if len(w0) > 1:
                carried.append(([w0[0], w0[1]], 6.0))
        yield carried, waters


def test_the_crossings_from_the_index_are_the_old_scan_in_its_order() -> None:
    """`way_water_crossings` yields every crossing the full scan finds, in the scan's own order (`bridges()` lays decks as
    it meets them, so the order is part of the answer), and nothing else."""
    found = 0
    for carried, waters in _crossing_beds(3061):
        new = list(B.way_water_crossings(carried, waters))
        assert new == _old_crossings(carried, waters)
        found += len(new)
    assert found > 200  # non-vacuous: the beds cross


def test_the_crossing_comparison_fails_when_the_index_drops_a_segment(monkeypatch: pytest.MonkeyPatch) -> None:
    """The comparison above has teeth: an index that loses the first segment it files misses crossings the scan finds."""
    keep = B.water_segment_index

    def lossy(water):
        grid = keep(water)
        for bucket in grid.buckets.values():
            if bucket:
                drop = bucket[0]
                break
        for bucket in grid.buckets.values():
            while drop in bucket:
                bucket.remove(drop)
        return grid

    monkeypatch.setattr(B, "water_segment_index", lossy)
    assert any(list(B.way_water_crossings(c, w)) != _old_crossings(c, w) for c, w in _crossing_beds(3061))


# ---- channel_footbridges(): a plank's keep-outs, and _belt_ranks(): the marsh under a rank point -------------------------


def _quad(rng: random.Random) -> list[Pt]:
    return B._deck_quad(rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(4, 40), rng.uniform(2, 6), rng.uniform(0, 180))


def _hits(quad, grid):
    return any(quad_hits_poly(quad, it[0]) for it in boxes_meeting(grid, *_box(quad)))


def _box(pts):
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def test_a_planks_keepouts_from_the_index_are_the_old_scan() -> None:
    """`quad_hits_poly` over the polygons whose box meets the deck's box is `quad_hits_poly` over every polygon - the deck's
    landing on a dry plot, a garden or a grove (`channel_footbridges`), on random decks, rings and decks lying on rings."""
    rng = random.Random(3062)
    hit = 0
    for _ in range(300):
        polys = [_ring(rng) for _ in range(rng.randint(0, 12))] + [_quad(rng) for _ in range(rng.randint(0, 6))]
        grid = boxed_grid(boxed_polys(polys, 1.0))
        for _ in range(20):
            q = _quad(rng)
            old = any(quad_hits_poly(q, p) for p in polys)
            assert _hits(q, grid) == old
            hit += old
    assert hit > 300


def test_a_point_on_the_marsh_from_the_index_is_the_old_scan() -> None:
    """`point_in_poly` over the rings whose box holds the point is `point_in_poly` over every ring (`_belt_ranks`' marsh
    test), points on a ring's vertices and edges included."""
    rng = random.Random(3063)
    inside = 0
    for _ in range(200):
        wet = [_ring(rng) for _ in range(rng.randint(0, 8))]
        grid = boxed_grid(boxed_polys(wet, 1.0))
        pts = [(rng.uniform(0, 600), rng.uniform(0, 600)) for _ in range(40)] + [v for w in wet for v in w]
        pts += [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for w in wet for a, b in zip(w, w[1:], strict=False)]
        for x, y in pts:
            old = any(point_in_poly(x, y, w) for w in wet)
            assert any(point_in_poly(x, y, it[0]) for it in boxes_meeting(grid, x, y, x, y)) == old
            inside += old
    assert inside > 300


def test_the_box_comparisons_fail_when_the_index_drops_a_polygon() -> None:
    """The two comparisons above have teeth: a grid missing one filed polygon gives a different answer somewhere."""
    rng = random.Random(3064)
    differs_q = differs_p = False
    for _ in range(200):
        polys = [_ring(rng) for _ in range(rng.randint(1, 8))]
        lossy = boxed_grid(boxed_polys(polys[1:], 1.0))
        for _ in range(20):
            q = _quad(rng)
            differs_q |= _hits(q, lossy) != any(quad_hits_poly(q, p) for p in polys)
            x, y = rng.uniform(0, 600), rng.uniform(0, 600)
            differs_p |= any(point_in_poly(x, y, it[0]) for it in boxes_meeting(lossy, x, y, x, y)) != any(point_in_poly(x, y, w) for w in polys)
    assert differs_q and differs_p


def test_boxes_meeting_returns_each_item_once() -> None:
    """An item filed in several cells is returned once, however many of the queried cells hold it."""
    grid = PointGrid(10.0)
    grid.extend([("long", 0.0, 0.0, 95.0, 5.0), ("far", 200.0, 200.0, 210.0, 210.0)])
    assert boxes_meeting(grid, 0.0, 0.0, 100.0, 10.0) == [("long", 0.0, 0.0, 95.0, 5.0)]


# ---- _comb_record_field(): the plots bordering the drain ---------------------------------------------------------------


def test_the_drain_hems_reach_from_the_index_is_the_old_scan() -> None:
    """`within_reach` over a `seg_reach_index` of the drain is `min(seg_dist over every segment) <= band` - the test
    `_comb_record_field` asks of each plot vertex - including points exactly `band` from the line."""
    rng = random.Random(3065)
    near = 0
    for _ in range(200):
        line = _walk(rng, rng.randint(2, 30), step=40.0)
        band = rng.uniform(31, 40)
        grid = seg_reach_index([(line, 1.0)], band)
        pts = [(rng.uniform(-50, 650), rng.uniform(-50, 650)) for _ in range(60)]
        pts += [(a[0], a[1] + band) for a in line] + [(a[0] + band, a[1]) for a in line]
        for x, y in pts:
            old = min(seg_dist(x, y, line[i], line[i + 1]) for i in range(len(line) - 1)) <= band
            assert within_reach(grid, x, y, band) == old
            near += old
    assert near > 1000


def test_the_drain_hem_comparison_fails_when_the_index_drops_a_segment() -> None:
    """The comparison above has teeth: an index missing one of the drain's segments misses a point only it reaches."""
    rng = random.Random(3066)
    differs = False
    for _ in range(100):
        line = _walk(rng, rng.randint(3, 20), step=40.0)
        band = 35.0
        lossy = seg_reach_index([(line[1:], 1.0)], band)
        for _ in range(40):
            x, y = rng.uniform(0, 600), rng.uniform(0, 600)
            differs |= within_reach(lossy, x, y, band) != (min(seg_dist(x, y, line[i], line[i + 1]) for i in range(len(line) - 1)) <= band)
    assert differs


# ---- _belt_ranks(): the belt's half-depth, each seat's distance to the centerline -----------------------------------------


def test_the_nearest_centerline_distance_from_the_index_is_the_old_scan() -> None:
    """`nearest_seg_dist` is `min(seg_dist over every segment)` - the same float - for seats on the line, near it and a
    canvas away (the outward search doubling many times), whatever radius the search starts from."""
    rng = random.Random(3067)
    for _ in range(200):
        line = _walk(rng, rng.randint(2, 25), step=40.0)
        grid = seg_reach_index([(line, 0.0)], 0.0)
        pts = [(rng.uniform(-900, 1500), rng.uniform(-900, 1500)) for _ in range(30)] + list(line)
        pts += [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(line, line[1:], strict=False)]
        for x, y in pts:
            old = min(seg_dist(x, y, line[i], line[i + 1]) for i in range(len(line) - 1))
            assert nearest_seg_dist(grid, x, y, rng.choice((0.5, 8.0, 60.0))) == old


def test_the_nearest_distance_comparison_fails_when_the_index_drops_a_segment() -> None:
    """The comparison above has teeth: an index missing one centerline segment gives a farther distance somewhere."""
    rng = random.Random(3068)
    differs = False
    for _ in range(100):
        line = _walk(rng, rng.randint(3, 20), step=40.0)
        lossy = seg_reach_index([(line[1:], 0.0)], 0.0)
        for _ in range(20):
            x, y = rng.uniform(0, 600), rng.uniform(0, 600)
            differs |= nearest_seg_dist(lossy, x, y, 30.0) != min(seg_dist(x, y, line[i], line[i + 1]) for i in range(len(line) - 1))
    assert differs


def test_the_nearest_distance_of_no_segments_raises_as_min_does() -> None:
    """An empty index raises, as `min` over no segments did, rather than searching outward forever."""
    with pytest.raises(ValueError, match="empty"):
        nearest_seg_dist(seg_reach_index([], 0.0), 0.0, 0.0, 10.0)
