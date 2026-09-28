"""Feature 284's exact pieces, each against a copy of the form it replaced: the board's lazy caption choice (A3), the bamboo
search walked outward (A4), the fabric crossing's box prefilters and the ring test (A5), and the grove draw's crown grid
(A6). Each index or ordering PRUNES; the old test DECIDES (`dev/performance.md`)."""

from __future__ import annotations

import math
import random

from l7r.diagram.hamletgen.hinterland.bamboo import nearest_fitting
from l7r.diagram.hamletgen.ways.fabric import _crosses_fabric
from l7r.diagram.hamletgen.ways.geom import ring_within
from l7r.diagram.settlement._geom import edge_dist, seg_dist, segments_cross
from l7r.diagram.settlement.shrines_wells.woods import CrownIndex, TreeStandsMixin
from l7r.diagram.settlement.structures.fixtures.siting import BOARD_CAPTION_TOP, board_choice


def _old_choice(seats, level):
    fits = {id(c): level(c) for c in seats}
    fitting = [c for c in seats if fits[id(c)] == max(fits.values())]
    in_the_open = [c for c in fitting if not c[7]] or fitting
    return max(in_the_open, key=lambda c: (fits[id(c)], c[5] is not None, c[1]))


def test_the_lazy_board_choice_is_the_full_choice() -> None:
    """A3: over random candidate sets - ties on score, shaded and open seats, caption levels 0 to the top - the lazy walk
    picks the very seat (the same object) the full evaluation picks, and asks fewer levels when a top seat is open."""
    rng = random.Random(2843)
    asked_less = 0
    for _ in range(400):
        seats = [(0, rng.choice((1.0, 2.0, 3.0, rng.uniform(0, 5))), 0.0, 0.0, 0.0, rng.choice((None, 0, 1)), 0.0, rng.random() < 0.4) for _ in range(rng.randint(1, 14))]
        levels = {id(c): rng.choice((0, 1, 1, BOARD_CAPTION_TOP, BOARD_CAPTION_TOP)) for c in seats}
        calls: list[int] = []

        def level(c, calls=calls, levels=levels):
            calls.append(1)
            return levels[id(c)]

        assert board_choice(seats, level) is _old_choice(seats, lambda c, levels=levels: levels[id(c)])
        asked_less += len(calls) < len(seats)
    assert asked_less, "non-vacuity: the walk stopped early somewhere"


def test_the_bamboo_walk_outward_finds_the_scans_seat() -> None:
    """A4: the nearest fitting position, ties in row order, exactly as the whole-square scan kept it - obstacles of every
    kind, no fit at all, and a fit exactly on a tie."""
    rng = random.Random(2844)
    for _ in range(60):
        target, reach, step = (rng.uniform(100, 300), rng.uniform(100, 300)), rng.uniform(40, 90), rng.choice((4.0, 8.0))
        holes = [(rng.uniform(0, 400), rng.uniform(0, 400), rng.uniform(5, 70)) for _ in range(rng.randint(0, 8))]

        def fits(x, y, holes=holes):
            return all(math.hypot(x - hx, y - hy) > hr for hx, hy, hr in holes)

        best = None
        y = target[1] - reach
        while y <= target[1] + reach:
            x = target[0] - reach
            while x <= target[0] + reach:
                if fits(x, y):
                    d = math.hypot(x - target[0], y - target[1])
                    if best is None or d < best[0]:
                        best = (d, x, y)
                x += step
            y += step
        assert nearest_fitting(target, reach, step, fits) == best
    assert nearest_fitting((0.0, 0.0), 10.0, 5.0, lambda x, y: False) is None


def _old_crosses(run, fabric, gap):
    for poly in fabric:
        for k in range(len(run) - 1):
            a, b = run[k], run[k + 1]
            for j in range(len(poly)):
                c, d = poly[j], poly[(j + 1) % len(poly)]
                if segments_cross(a, b, c, d) or seg_dist(c[0], c[1], a, b) < gap:
                    return True
            if edge_dist(a[0], a[1], poly) < gap or edge_dist(b[0], b[1], poly) < gap:
                return True
    return False


def _box(rng):
    cx, cy, w, h = rng.uniform(0, 600), rng.uniform(0, 600), rng.uniform(8, 60), rng.uniform(8, 60)
    return [(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h)]


def test_the_fabric_crossing_with_box_prefilters_is_the_old_scan() -> None:
    """A5: `_crosses_fabric` answers as the full scan did - runs through, beside and exactly `gap` off a steading."""
    rng = random.Random(2845)
    for _ in range(500):
        fabric = [_box(rng) for _ in range(rng.randint(0, 9))]
        run = [(rng.uniform(0, 600), rng.uniform(0, 600)) for _ in range(rng.randint(2, 5))]
        gap = rng.choice((3.0, 7.0, 12.0))
        assert _crosses_fabric(run, fabric, gap) == _old_crosses(run, fabric, gap)
    square = [(100.0, 100.0), (200.0, 100.0), (200.0, 200.0), (100.0, 200.0)]
    at = [(0.0, 93.0), (300.0, 93.0)]  # exactly 7 off the square's edge: not under a 7 gap, under an 8
    assert _crosses_fabric(at, [square], 7.0) is _old_crosses(at, [square], 7.0) is False
    assert _crosses_fabric(at, [square], 8.0) is _old_crosses(at, [square], 8.0) is True


def test_the_ring_test_from_the_shared_index_is_edge_dist() -> None:
    """A5: `ring_within` is `edge_dist <= limit` (closed) and `< limit` (open) - points inside, outside, and exactly at the
    limit."""
    rng = random.Random(2846)
    for _ in range(300):
        poly = _box(rng)
        limit = rng.choice((4.0, 10.0, 25.0))
        for _k in range(20):
            x, y = rng.uniform(-50, 650), rng.uniform(-50, 650)
            d = edge_dist(x, y, poly)
            assert ring_within(x, y, poly, limit) == (d <= limit)
            assert ring_within(x, y, poly, limit, closed=False) == (d < limit)
    sq = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert ring_within(5.0, -4.0, sq, 4.0) is True and ring_within(5.0, -4.0, sq, 4.0, closed=False) is False


def test_the_crown_grid_is_the_crown_scan() -> None:
    """A6: a crown seat is clear by the grid exactly when the scan over every crown says so - crowns of every size, a seat
    inside a bigger crown, a crown center inside a bigger seat, and crowns added as they land."""
    rng = random.Random(2847)
    for _ in range(100):
        crowns = [(rng.uniform(0, 300), rng.uniform(0, 300), rng.uniform(3, 20)) for _ in range(rng.randint(0, 40))]
        index = CrownIndex(crowns[: len(crowns) // 2])
        index.add(crowns[len(crowns) // 2 :])
        for _k in range(60):
            x, y, r = rng.uniform(-20, 320), rng.uniform(-20, 320), rng.uniform(3, 20)
            assert index.clear(x, y, r) == TreeStandsMixin._crown_seat_clear(x, y, r, crowns)
    assert CrownIndex().clear(1.0, 1.0, 5.0) is True


def _hamlet_with_a_board_to_seat(rng: random.Random, blocked_verge: bool):
    from l7r.diagram.settlement import Settlement

    s = Settlement(1400, 1000, seed=rng.randint(1, 99))
    s.meta(name="Board", scale="hamlet", ftpx=1)
    y0 = rng.uniform(350, 650)
    s.M["lanes"] = [{"pts": [(150.0, y0), (rng.uniform(600, 800), y0 + rng.uniform(-80, 80)), (1250.0, y0 + rng.uniform(-120, 120))], "w": 5.0}]
    s.M["houses"] = [{"x": rng.uniform(200, 1200), "y": y0 + rng.choice((-1, 1)) * rng.uniform(40, 200), "w": 46.0, "h": 28.0, "rot": 0.0} for _ in range(rng.randint(3, 9))]
    if blocked_verge:  # a band of taken ground down the whole lane: every verge seat fails and the far band decides
        pts = s.M["lanes"][0]["pts"]
        for (ax, ay), (bx, by) in zip(pts, pts[1:], strict=False):
            n = int(math.hypot(bx - ax, by - ay) // 20) + 1
            for i in range(n + 1):
                s.placed.append((ax + (bx - ax) * i / n, ay + (by - ay) * i / n, 40.0, 30.0))
    return s


def test_the_board_sampled_verge_first_is_the_board_sampled_whole() -> None:
    """FR-007: sampling the verge band first seats the same board, with the same record, as sampling the whole band - on
    hamlets whose verge holds a seat and on hamlets whose verge is taken, so the far band decides."""
    import copy

    from l7r.diagram.settlement.structures.fixtures import siting

    rng = random.Random(2848)
    seated = off_the_verge = 0
    for k in range(24):
        s = _hamlet_with_a_board_to_seat(rng, blocked_verge=k % 3 == 0)
        whole = copy.deepcopy(s)
        siting.VERGE_FIRST = False
        try:
            want = whole.place_kosatsuba()
        finally:
            siting.VERGE_FIRST = True
        assert s.place_kosatsuba() == want
        assert s.M.get("kosatsuba") == whole.M.get("kosatsuba")
        if want is not None:
            seated += 1
            lane = s.M["lanes"][0]["pts"]
            off_the_verge += min(seg_dist(want[0], want[1], a, b) for a, b in zip(lane, lane[1:], strict=False)) > 12.0
    assert seated >= 20 and off_the_verge, f"non-vacuity: boards seated {seated}, of them off the verge {off_the_verge}"


def test_the_fabric_push_with_box_prefilters_is_the_old_walk() -> None:
    """FR-009: `push_clear_of_fabric` lands where the walk over every polygon's ring landed - clear ground, crowded
    ground, and a step landing exactly `gap` off a steading."""
    from l7r.diagram.hamletgen.ways.geom import push_clear_of_fabric

    def old(base, unit, edge, fabric, gap):
        for _ in range(24):
            gx, gy = base[0] + unit[0] * edge, base[1] + unit[1] * edge
            if not any(edge_dist(gx, gy, poly) < gap for poly in fabric):
                return (gx, gy)
            edge += 6.0
        return (base[0] + unit[0] * edge, base[1] + unit[1] * edge)

    rng = random.Random(2849)
    for _ in range(300):
        fabric = [_box(rng) for _ in range(rng.randint(0, 12))]
        a = rng.uniform(0, 2 * math.pi)
        base, unit, edge, gap = (rng.uniform(100, 500), rng.uniform(100, 500)), (math.cos(a), math.sin(a)), rng.uniform(0, 30), rng.choice((4.0, 9.0))
        assert push_clear_of_fabric(base, unit, edge, fabric, gap) == old(base, unit, edge, fabric, gap)
    square = [(100.0, 100.0), (200.0, 100.0), (200.0, 200.0), (100.0, 200.0)]
    assert push_clear_of_fabric((150.0, 91.0), (0.0, -1.0), 0.0, [square], 9.0) == old((150.0, 91.0), (0.0, -1.0), 0.0, [square], 9.0) == (150.0, 91.0)


def test_the_comb_bead_test_through_the_segment_index_is_the_whole_scan() -> None:
    """A5 (the comb's `_dry`): a bead is kept off the water exactly when every ditch and channel segment stands `half` or
    more from it - through `seg_reach_index`, as by the scan over every segment of every line; points exactly at `half`
    included."""
    from l7r.diagram.settlement._geom import seg_reach_index

    rng = random.Random(2850)
    for _ in range(200):
        water = [([(rng.uniform(0, 400), rng.uniform(0, 400)) for _ in range(rng.randint(2, 6))], rng.choice((1.5, 2.75, 4.0))) for _ in range(rng.randint(0, 6))]
        idx = seg_reach_index(water, 0.0)
        for _k in range(40):
            q = (rng.uniform(-20, 420), rng.uniform(-20, 420))
            old = all(min(seg_dist(q[0], q[1], poly[i], poly[i + 1]) for i in range(len(poly) - 1)) >= half for poly, half in water)
            new = not any(x0 <= q[0] <= x1 and y0 <= q[1] <= y1 and seg_dist(q[0], q[1], a, b) < half for a, b, half, x0, y0, x1, y1 in idx.near(q[0], q[1]))
            assert new == old
    line = [([(0.0, 0.0), (100.0, 0.0)], 2.0)]
    idx = seg_reach_index(line, 0.0)
    at = (50.0, 2.0)  # exactly `half` off the line: dry
    assert not any(x0 <= at[0] <= x1 and y0 <= at[1] <= y1 and seg_dist(at[0], at[1], a, b) < half for a, b, half, x0, y0, x1, y1 in idx.near(*at))


def test_the_page_reads_a_blade_slot_as_it_would_have_parsed_it() -> None:
    """A2: a blade slot the finish wrote - culled, merged by `merge_lines`, its roots handed over - gives the page it gave
    when the page culled, merged and read the roots out of the text itself: the whole page byte-identical through both
    routes, over a slot that tiles, a slot too small to tile, and a lone blade."""
    from l7r.diagram.interactive import page
    from l7r.diagram.interactive.page import HIT_FROM_MARKS, NOT_HIGHLIGHTED, merge_lines, render_page

    key = next(iter(HIT_FROM_MARKS))
    rng = random.Random(2851)
    for n in (1, 5, page.TILE_MIN + 40):
        blades = []
        for _ in range(n):
            x, y = rng.uniform(10, 590), rng.uniform(10, 390)
            blades.append((f"{x:.1f}", f"{y:.1f}", f"{x + rng.uniform(-3, 3):.1f}", f"{y - rng.uniform(2, 5):.1f}"))
        slot = f'<g stroke="#7a8a4a" stroke-width="0.8">{merge_lines(blades)}</g>'
        strings = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400"><rect x="0" y="0" width="600" height="400" fill="#eee"/>', slot, "</svg>"]
        tags = [NOT_HIGHLIGHTED, key, None]
        parsed = render_page(strings, tags, "T", with_raster=False)
        handed = render_page(strings, tags, "T", with_raster=False, blade_starts={1: [(b[0], b[1]) for b in blades]})
        assert handed == parsed, f"{n} blades"
        assert page.marks_region([slot]) == page.marks_region([], points=[(b[0], b[1]) for b in blades])
