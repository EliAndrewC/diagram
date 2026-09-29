"""Feature 226 (GM 2026-09-12): the site boundary - one outline separating the homestead ground from everything the
map holds at seat time - and the fit test and the proposer that read it."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.homesteads.boundary import SiteCorridors, site_boundary
from l7r.diagram.settlement import Settlement

SQUARE_FIELD = [(300.0, 300.0), (700.0, 300.0), (700.0, 700.0), (300.0, 700.0)]


def _site() -> Settlement:
    """A field with a hem plot on its north side, a marsh at its east toe, a pond, a stream running north from the
    field's head and a registered corridor - everything the fit test used to scan, one of each."""
    s = Settlement(W=1000, H=1000, seed=7)
    s.field_polys.append(SQUARE_FIELD)
    s.M["dry_plots"] = [{"poly": [[300, 280], [700, 280], [700, 300], [300, 300]]}]  # the hem, a 20 px strip north of the paddy
    s.wet_polys.append([(700.0, 400.0), (760.0, 400.0), (760.0, 600.0), (700.0, 600.0)])  # the marsh at the east toe
    s.ellipses.append((500.0, 760.0, 40.0, 25.0))  # the pond below the field
    s.M["streams"] = [{"poly": [[500, 0], [500, 300]], "w": 6}]  # the stream from the high ground to the field's head
    s.corridors.append(([(100.0, 100.0), (100.0, 900.0)], 30.0))  # a registered corridor down the west
    return s


def test_the_boundary_is_a_few_chords_facing_the_seat_and_two_corridor_sets() -> None:
    s = _site()
    chains, (water, registered), (rings, holes) = site_boundary(s, (500.0, 150.0))  # the seat is north of the field
    assert len(rings) == 3 and not holes, "the hem strip, the marsh, and the pond with the toe band it lies in are the others' outline; the paddy alone gives the chains"
    chords = [c for ch in chains for c in ch]
    assert 1 <= len(chords) <= 30, len(chords)
    assert all(n[1] < 0 for _a, _b, n in chords if abs(n[1]) > 0.7), "the chords facing a northern seat have northward normals"
    assert len(water) == 1 and water[0][2] == 6 / 2 + 5, "the stream at its half-width plus 5, as _rect_on_water"
    assert len(registered) == 1 and registered[0][2] == 30.0, "the registered corridor at its registered clearance"
    assert any(min(p[1] for p in r) <= 280.0 - 2.0 + 0.5 for r in rings), "the hem's north edge, grown by the tilt allowance, is in the others' outline"


def test_the_boundary_path_refuses_the_hem_the_marsh_the_pond_the_stream_and_admits_open_ground() -> None:
    from l7r.diagram.hamletgen.homesteads.boundary import install_site_boundary

    s = _site()
    plan = type("P", (), {"seat": {"cx": 500.0, "cy": 150.0}})()
    install_site_boundary(s, plan)  # type: ignore[arg-type]
    assert s._site_chains is not None and "site_boundary" in s.M and s.M["site_boundary"]["chords"]
    assert s._site_blocks_rect((500.0, 290.0, 40.0, 28.0)), "a house on the hem strip"
    assert s._site_blocks_rect((730.0, 500.0, 40.0, 28.0)), "a house in the marsh"
    assert s._site_blocks_rect((500.0, 760.0, 40.0, 28.0)), "a house on the pond (a free-standing ring, asked by containment)"
    assert s._site_blocks_rect((560.0, 750.0, 60.0, 28.0)), "...and one whose corners straddle the pond: a ring vertex inside the rectangle"
    assert s._site_blocks_rect((500.0, 200.0, 40.0, 28.0)), "a house over the stream (its corners reach the corridor)"
    assert s._site_blocks_rect((100.0, 500.0, 40.0, 28.0)), "a house centered in the registered corridor"
    assert not s._site_blocks_rect((110.0 + 30.0 + 25.0, 500.0, 40.0, 28.0)), "...but one whose CENTER is clear of its clearance, as _near_corridor asked"
    assert not s._site_blocks_rect((300.0, 150.0, 40.0, 28.0)), "open ground north of the hem, west of the stream"
    assert not s._rect_blocked((300.0, 150.0, 40.0, 28.0), fields=True) and s._rect_blocked((500.0, 290.0, 40.0, 28.0), fields=True), "_rect_blocked takes the boundary path"
    assert s._seat_search["rects"] >= 9


def test_the_reed_marsh_toe_is_in_the_boundary_before_it_is_drawn() -> None:
    """The settlement-review of this feature found three pool maps whose manifest put a farmhouse, a threshing floor and a
    byre inside the toe-marsh polygon: `hinterland()` draws the toe after the houses, so `wet_polys` did not hold it at
    seat time. The boundary asks `toe_band()` as the ways do. A seat WEST of a field whose fall is south: the ground west
    of the paddy is on the house side of its chains, but the band below the crop's lowest point (its pad above it) is
    the reeds' and is refused."""
    from l7r.diagram.hamletgen.homesteads.boundary import install_site_boundary

    s = Settlement(W=1000, H=1000, seed=3)
    s.field_polys.append(SQUARE_FIELD)
    s.M["meta"]["down_deg"] = 90  # downhill is +y, so the toe lies below the paddy
    toe = s.toe_band()
    assert toe and min(p[1] for p in toe) == 700.0 - 90.0, "the band's inner edge is the pad above the crop's lowest point"
    plan = type("P", (), {"seat": {"cx": 150.0, "cy": 500.0}})()
    install_site_boundary(s, plan)  # type: ignore[arg-type]
    assert not s._site_blocks_rect((250.0, 500.0, 40.0, 28.0)), "open ground beside the paddy, uphill of the toe"
    assert s._site_blocks_rect((250.0, 660.0, 40.0, 28.0)), "the same column in the toe band (the band is as wide as the crop plus its pad): refused before the reeds are drawn"
    assert s._site_blocks_rect((250.0, 604.0, 40.0, 28.0)), "...and a house whose lower edge reaches the band's inner edge, grown by the tilt allowance"


def test_a_member_thinner_than_half_a_side_is_still_caught_by_the_nine_points() -> None:
    s = Settlement(W=1000, H=1000, seed=1)
    s.block_polys.append([(495.0, 100.0), (505.0, 100.0), (505.0, 900.0), (495.0, 900.0)])  # a 10 px no-build strip
    chains, corr, outline = site_boundary(s, (200.0, 500.0))
    s._site_chains, s._site_corridors = chains, SiteCorridors(corr, outline)
    assert s._site_blocks_rect((500.0, 500.0, 60.0, 28.0)), "the strip passes between the corners; the edge midpoints see it"


def test_site_corridors_hit_the_water_at_every_point_and_the_registered_set_at_the_center_only() -> None:
    sc = SiteCorridors(([((0.0, 0.0), (100.0, 0.0), 8.0)], [((0.0, 50.0), (100.0, 50.0), 20.0)]))
    assert sc.hit_points([(50.0, 7.0)]) and not sc.hit_points([(50.0, 9.0)])
    assert sc.hit_center(50.0, 60.0) and not sc.hit_center(50.0, 71.0)
    assert not sc.hit_points([(50.0, 60.0)]), "the registered set is never asked at a corner"


def test_a_settlement_with_no_boundary_runs_the_old_fit_path() -> None:
    s = Settlement(W=1000, H=1000, seed=1)
    s.block_polys.append(SQUARE_FIELD)
    assert s._site_chains is None and s._rect_blocked((500.0, 500.0, 40.0, 28.0), fields=True) and not s._rect_blocked((100.0, 100.0, 40.0, 28.0), fields=True)


def test_front_row_from_the_chains_stands_off_the_whole_blob_at_the_pitch() -> None:
    from l7r.diagram.hamletgen.consts import BUNDLE_PITCH
    from l7r.diagram.hamletgen.homesteads.seats import front_row

    s = _site()
    chains, _corr, _outline = site_boundary(s, (500.0, 150.0))
    plan = type("P", (), {"seat": {"cx": 500.0, "cy": 150.0, "along": (1.0, 0.0), "anchor": (500.0, 280.0), "lat": 300.0}, "cluster_shape": "crescent", "envelope": SQUARE_FIELD})()
    row = front_row(plan, 12, standoff=46.0, chains=chains)  # type: ignore[arg-type]
    front = [(x, y) for x, y in row if 300.0 <= x <= 700.0 and y < 300.0]
    assert front and all(y <= 300.0 - 46.0 + 4.0 for _x, y in front), "every seat fronting the paddy stands the standoff north of its chords (the hem is the others' outline, which the pre-test asks)"
    xs = sorted(x for x, _y in front)
    assert all(b - a >= BUNDLE_PITCH - 1.0 for a, b in zip(xs, xs[1:], strict=False)), "one bundle pitch apart along the front"
    assert row[0] == min(row, key=lambda q: math.hypot(q[0] - 500.0, q[1] - 150.0)), "ordered center-out"


def test_the_ground_between_two_ponds_is_buildable_because_the_others_outline_keeps_its_holes() -> None:
    """The mosaic case (Kuwabata): four ponds around a courtyard. The first cut's one facing blob refused the ground
    behind its front; the others' outline is asked by containment, and the courtyard is a hole in it - buildable."""
    s = Settlement(W=1000, H=1000, seed=3)
    s.field_polys.append([(100.0, 700.0), (900.0, 700.0), (900.0, 900.0), (100.0, 900.0)])  # the field to the south
    for cx, cy in ((400.0, 400.0), (600.0, 400.0), (400.0, 600.0), (600.0, 600.0), (500.0, 360.0), (500.0, 640.0), (360.0, 500.0), (640.0, 500.0)):
        s.block_polys.append([(cx - 70, cy - 70), (cx + 70, cy - 70), (cx + 70, cy + 70), (cx - 70, cy + 70)])  # eight overlapping ponds enclosing a 60 px courtyard
    chains, corr, outline = site_boundary(s, (500.0, 200.0))
    s._site_chains, s._site_corridors = chains, SiteCorridors(corr, outline)
    assert outline[1], "the courtyard is a hole of the ponds' union"
    assert not s._site_blocks_rect((500.0, 500.0, 40.0, 28.0)), "a house in the courtyard among the ponds"
    assert s._site_blocks_rect((400.0, 400.0, 40.0, 28.0)), "a house on a pond"
    assert s._site_blocks_rect((500.0, 780.0, 40.0, 28.0)), "a house on the field, by the paddy's own chains"


def test_the_chain_walk_skips_a_zero_length_chord_and_caps_the_row_at_64() -> None:
    """Two edges of the walk the pool never reaches: a chord whose ends coincide (a facing chain can carry one at a
    corner) is stepped over, and a very long chain - here 9,000 px, 91 seats at the pitch - is thinned to 64 so a huge
    fan cannot make the row unbounded (the old envelope walk's own cap, kept)."""
    from l7r.diagram.hamletgen.consts import BUNDLE_PITCH
    from l7r.diagram.hamletgen.homesteads.seats import front_row

    plan = type("P", (), {"seat": {"cx": 4500.0, "cy": 100.0, "anchor": (4500.0, 300.0), "along": (1.0, 0.0), "lat": 10000.0}, "cluster_shape": "elongated"})()
    chain = [((0.0, 300.0), (0.0, 300.0), (0.0, -1.0)), ((0.0, 300.0), (9000.0, 300.0), (0.0, -1.0))]
    row = front_row(plan, 12, standoff=46.0, chains=[chain])  # type: ignore[arg-type]
    assert len(row) == 64 and all(abs(y - (300.0 - 46.0)) < 1e-6 for _x, y in row)
    xs = sorted(x for x, _y in row)
    assert xs[0] == 0.0 and xs[-1] > 9000.0 - 2 * BUNDLE_PITCH, "the thinning keeps the whole span, not the first 64"


def test_a_block_polygon_with_fewer_than_three_points_is_no_member() -> None:
    s = Settlement(W=1000, H=1000, seed=2)
    s.block_polys.append([(100.0, 100.0), (200.0, 100.0)])  # a degenerate registration
    s.block_polys.append(SQUARE_FIELD)
    _chains, _corr, (rings, holes) = site_boundary(s, (500.0, 150.0))
    assert len(rings) == 1 and not holes, "the two-point polygon contributes nothing; the square is the outline"


def test_the_computed_standoff_without_an_envelope_is_the_house_alone() -> None:
    """`standoff=None` with no envelope: the wall rule, the tilt's slack and the house's own half-extent along the
    chord's normal (a caller that seats a bare house)."""
    from l7r.diagram.hamletgen.homesteads.seats import DEFAULT_HOUSE, STANDOFF_SLACK_PX, front_row
    from l7r.diagram.settlement.houses import HOUSE_PADDY_GAP_FT

    plan = type("P", (), {"seat": {"cx": 500.0, "cy": 100.0, "anchor": (500.0, 300.0), "along": (1.0, 0.0), "lat": 1000.0}, "cluster_shape": "round"})()
    chain = [((300.0, 300.0), (700.0, 300.0), (0.0, -1.0))]
    row = front_row(plan, 12, standoff=None, chains=[chain])  # type: ignore[arg-type]
    assert row and all(abs(y - (300.0 - (HOUSE_PADDY_GAP_FT + 1.0 + STANDOFF_SLACK_PX + DEFAULT_HOUSE[1] / 2))) < 1e-6 for _x, y in row)


def test_the_indexed_hit_points_answer_as_the_linear_scan_did() -> None:
    """Feature 276 (plan D8): the vertex grids, the hole grid and the one lookup per rectangle answer every rectangle
    exactly as the linear form - every water segment, every ring, every vertex, every hole - over random rings with
    holes and random water, including rectangles that hold a ring vertex without a sample point inside it."""
    import math
    import random

    from l7r.diagram.hamletgen.homesteads.boundary import SiteCorridors
    from l7r.diagram.settlement._geom.indexes import RingIndex
    from l7r.diagram.settlement._geom.primitives import seg_dist

    r = random.Random(276)

    def blob(cx, cy, rad, n):  # type: ignore[no-untyped-def]
        return [(cx + rad * (0.7 + 0.3 * r.random()) * math.cos(2 * math.pi * k / n), cy + rad * (0.7 + 0.3 * r.random()) * math.sin(2 * math.pi * k / n)) for k in range(n)]

    for _ in range(6):
        rings = [blob(r.uniform(100, 900), r.uniform(100, 900), r.uniform(40, 160), r.randint(6, 40)) for _ in range(5)]
        holes = [blob(ring[0][0] - 20, ring[0][1], 15, 8) for ring in rings[:2]]
        water = []
        for _ in range(40):
            x, y = r.uniform(0, 1000), r.uniform(0, 1000)
            water.append(((x, y), (x + r.uniform(-80, 80), y + r.uniform(-80, 80)), r.uniform(2, 12)))
        corr = SiteCorridors((water, []), (rings, holes))
        ring_ix = [RingIndex(g) for g in rings]
        hole_ix = [RingIndex(h) for h in holes]

        def linear(pts, water=water, rings=rings, ring_ix=ring_ix, hole_ix=hole_ix):  # type: ignore[no-untyped-def]
            if any(seg_dist(x, y, a, b) < clr for x, y in pts for a, b, clr in water):
                return True
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            rx0, ry0, rx1, ry1 = min(xs), min(ys), max(xs), max(ys)
            for g, ix in zip(rings, ring_ix, strict=True):
                if max(p[0] for p in g) < rx0 or min(p[0] for p in g) > rx1 or max(p[1] for p in g) < ry0 or min(p[1] for p in g) > ry1:
                    continue
                if any(ix.inside(px, py) and not any(h.inside(px, py) for h in hole_ix) for px, py in pts) or any(rx0 <= vx <= rx1 and ry0 <= vy <= ry1 for vx, vy in g):
                    return True
            return False

        hits = 0
        for _ in range(300):
            cx, cy, w, h = r.uniform(0, 1000), r.uniform(0, 1000), r.uniform(4, 90), r.uniform(4, 90)
            x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
            pts = ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (cx, y0), (x1, cy), (cx, y1), (x0, cy), (cx, cy))
            got = corr.hit_points(pts)
            assert got == linear(pts)
            hits += got
        assert 20 < hits < 280, "non-vacuity: both answers occur"


def test_free_ground_with_nothing_to_claim_claims_no_cell() -> None:
    """Feature 276 (D9): a zero-length chord contributes nothing, no ground at all leaves the raster empty, and ground
    thinner than the half-pixel shrink leaves it empty too - so a seat there is never pruned."""
    from l7r.diagram.hamletgen.homesteads.boundary import FreeGround

    none = FreeGround([[((10.0, 10.0), (10.0, 10.0), (0.0, 1.0))]], ([], []), None, (0.0, 0.0, 100.0, 100.0))
    assert none.taken == set() and not none.rect_refused((10.0, 10.0, 4.0, 4.0))
    thin = FreeGround([], ([((0.0, 50.0), (100.0, 50.0), 0.3)], []), None, (0.0, 0.0, 100.0, 100.0))
    assert thin.taken == set() and not thin.rect_refused((50.0, 50.0, 4.0, 4.0))


def test_a_seat_deeper_than_any_ways_reach_is_refused_and_one_within_reach_is_not() -> None:
    """Feature 278 (FR-005): a way is never drawn on the web's hard ground nor within `WEB_HARD_GAP` of it, so a house
    whose center stands more than `WEB_REACH_FT` inside that inflated ground is one `unreached_houses` must fail. A
    500 px field: its middle is refused; a point 60 px in (a way on the margin 68 px off - within reach) is not, nor is
    one outside; and with no ground installed the settlement refuses nothing."""
    from l7r.diagram.hamletgen.consts import WEB_HARD_GAP, WEB_REACH_FT
    from l7r.diagram.hamletgen.homesteads.boundary import UnreachableGround
    from l7r.diagram.settlement import Settlement

    field = [(100.0, 100.0), (600.0, 100.0), (600.0, 600.0), (100.0, 600.0)]
    ground = UnreachableGround([field])
    assert ground.refuses(350.0, 350.0), "the middle of the field, 258 px from any ground a way may stand on"
    assert not ground.refuses(160.0, 350.0), "60 px in: a way at the margin stands 68 px off, within reach"
    assert not ground.refuses(60.0, 350.0), "outside the field"
    edge = WEB_REACH_FT - WEB_HARD_GAP  # the depth at which a margin way stands exactly at the reach
    assert not ground.refuses(100.0 + edge - 1.0, 350.0) and ground.refuses(100.0 + edge + 3.0, 350.0), "the line sits at the reach"
    assert UnreachableGround([]).deep is None and not UnreachableGround([]).refuses(0.0, 0.0)
    s = Settlement(800, 800, seed=1)
    assert s._house_unreachable((350.0, 350.0, 40.0, 26.0)) is False
    s._unreachable = ground
    assert s._house_unreachable((350.0, 350.0, 40.0, 26.0)) is True


def test_free_ground_asks_blocks_of_cells_first_and_claims_what_asking_every_cell_claims() -> None:
    """Feature 287: the raster is built block by block - a block the grown ground misses is all clear, one the shrunk ground
    holds all taken, and only the cells of the rest are asked - and claims exactly the cells asking each one claims. Ground
    lying wholly off the grid leaves every block missed and no cell to ask; no line asked is no answer."""
    import shapely
    from shapely.geometry import LineString, Polygon
    from shapely.ops import unary_union

    from l7r.diagram.hamletgen.homesteads.boundary import FreeGround

    water = ([((0.0, 130.0), (400.0, 170.0), 12.0)], [])
    ring = ([[(200.0, 220.0), (330.0, 220.0), (330.0, 330.0), (200.0, 330.0)]], [])
    fg = FreeGround([], water, ring, (0.0, 0.0, 400.0, 400.0))
    union = unary_union([Polygon(ring[0][0]), LineString([(0.0, 130.0), (400.0, 170.0)]).buffer(12.0)])
    keys = [(i, j) for i in range(fg.nx) for j in range(fg.ny)]
    cells = shapely.box([i * 8.0 for i, _ in keys], [j * 8.0 for _, j in keys], [(i + 1) * 8.0 for i, _ in keys], [(j + 1) * 8.0 for _, j in keys])
    assert fg.clear == {k for k, t in zip(keys, shapely.disjoint(union.buffer(0.5), cells).tolist(), strict=True) if t}
    assert fg.taken == {k for k, t in zip(keys, shapely.contains(union.buffer(-0.5), cells).tolist(), strict=True) if t}
    assert len(fg.taken) > 50 and len(fg.clear) > 500, "non-vacuity: both kinds of block and edge cells"
    away = FreeGround([], ([((900.0, 900.0), (950.0, 950.0), 5.0)], []), None, (0.0, 0.0, 100.0, 100.0))
    assert away.taken == set() and len(away.clear) == away.nx * away.ny
    assert away.lines_edge_points([]) == []


def test_the_lines_asked_together_answer_as_each_sample_asked_alone() -> None:
    """`FreeGround.lines_edge_points` asks many lines of the raster in one array: a line is refused where one of its
    samples stands in a taken cell, and otherwise hands back exactly its samples in neither a taken nor a clear cell - the
    samples asked one by one, off the grid included."""
    import random

    from l7r.diagram.hamletgen.homesteads.boundary import FreeGround

    fg = FreeGround([], ([((0.0, 130.0), (400.0, 170.0), 12.0)], []), ([[(200.0, 220.0), (330.0, 220.0), (330.0, 330.0), (200.0, 330.0)]], []), (0.0, 0.0, 400.0, 400.0))
    rng = random.Random(6)
    lines = []
    for _ in range(300):
        a = (rng.uniform(-50, 450), rng.uniform(-50, 450))
        b = (a[0] + rng.uniform(-200, 200), a[1] + rng.uniform(-200, 200))
        lines.append((a, b, max(1, int(((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 / 8))))
    got = fg.lines_edge_points(lines)
    refused = 0
    for (a, b, n), edge in zip(lines, got, strict=True):
        pts = [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n + 1)]
        cells = [(int((x - fg.x0) // fg.cell), int((y - fg.y0) // fg.cell)) for x, y in pts]
        if any(c in fg.taken for c in cells):
            assert edge is None
            refused += 1
            continue
        want = [p for p, c in zip(pts, cells, strict=True) if c not in fg.clear]
        assert edge is not None and list(edge) == want and len(edge) == len(want)
    assert 30 < refused < 270
