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
    assert len(rings) == 3 and not holes, "the hem strip, the marsh and the pond are the others' outline; the paddy alone gives the chains"
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
