"""Feature 299 - the marsh's natural outline, the scrub-marsh fringe and the overlay tiles."""

from __future__ import annotations

import math
import re

from shapely.geometry import LineString, Polygon, box

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.land import outline, tiles
from l7r.diagram.settlement.land.tiles import Cover


def _laid_runs(shaped: list[tuple[float, float]], laid: Polygon, tol: float = 0.5) -> float:
    """The longest run of `shaped`'s edge lying along `laid`'s boundary, in feet."""
    edge = laid.exterior.buffer(tol)
    best = 0.0
    for a, b in zip(shaped, [*shaped[1:], shaped[0]], strict=True):
        seg = LineString([a, b])
        best = max(best, seg.intersection(edge).length if seg.length else 0.0)
    return best


def test_a_laid_rectangle_is_rounded_and_waved_within_itself() -> None:
    """FR-001/FR-002: the shaped outline lies within the laid one, its corners are curves, and no stretch of it runs along the
    laid straight line for longer than a quarter of the wave's shortest length."""
    laid = [(0.0, 0.0), (1200.0, 0.0), (1200.0, 500.0), (0.0, 500.0)]
    shaped = outline.natural_outline(laid, seed=299)
    poly, laid_poly = Polygon(shaped), Polygon(laid)
    assert poly.is_valid and laid_poly.buffer(0.2).contains(poly), "the shaping only takes ground away"
    assert poly.area > 0.85 * laid_poly.area, "...and only a little of it"
    assert not any(math.hypot(x - cx, y - cy) < 1.0 for x, y in shaped for cx, cy in laid), "no laid corner survives"
    assert _laid_runs(shaped, laid_poly) < outline.WAVE_LENGTH_FT[0] / 4, "no straight run along the laid line"
    assert outline.natural_outline(laid, seed=299) == shaped, "the same seed shapes the same outline"
    assert outline.natural_outline(laid, seed=300) != shaped


def test_a_narrow_band_keeps_what_rounding_it_can_and_a_degenerate_ring_is_returned_as_it_is() -> None:
    narrow = [(0.0, 0.0), (800.0, 0.0), (800.0, 40.0), (0.0, 40.0)]
    shaped = Polygon(outline.natural_outline(narrow, seed=1))
    assert shaped.area > 0.4 * 800 * 40, "a band narrower than the rounding still draws"
    assert outline.natural_outline([(0.0, 0.0), (5.0, 0.0)], seed=1) == [(0.0, 0.0), (5.0, 0.0)]
    assert outline._largest(LineString([(0, 0), (1, 1)])) is None


def test_the_marsh_records_its_shaped_outline_and_a_pond_fringe_is_left_as_laid() -> None:
    """FR-005: the record is the shaped outline; a toe laid as a right-angled block comes out with no laid corner."""
    s = Settlement(W=2000, H=1600, seed=4)
    s.meta(name="T", scale="hamlet", ftpx=1)
    laid = [(200.0, 800.0), (1800.0, 800.0), (1800.0, 1500.0), (200.0, 1500.0)]
    s.marsh(laid, role="toe")
    rec = [tuple(q) for q in s.M["marshes"][-1]["poly"]]
    assert Polygon(laid).buffer(0.5).contains(Polygon(rec))
    assert not any(math.hypot(x - cx, y - cy) < 1.0 for x, y in rec for cx, cy in laid)
    from l7r.diagram.settlement.land import wet

    calls = []
    real = wet.natural_outline
    wet.natural_outline = lambda *a, **k: calls.append(a) or real(*a, **k)  # type: ignore[assignment]
    try:
        s.marsh([(300.0, 200.0), (500.0, 200.0), (500.0, 300.0), (300.0, 300.0)], role="pond_fringe")
    finally:
        wet.natural_outline = real  # type: ignore[assignment]
    assert calls == [], "a pond's fringe is not shaped"


def _slot(s: Settlement, key: tuple[str, str | None]) -> str:
    return s.out[s._cover_slots[key]]


def test_the_fringe_is_drawn_only_where_scrub_meets_marsh_and_every_base_has_its_overlay() -> None:
    """FR-003/FR-004: a scrub square beside a marsh square - a fringe band on both sides of their shared edge, in each side's
    slot; a marsh with no scrub beside it gets none; every base path carries its overlay."""
    s = Settlement(W=1000, H=1000, seed=1)
    s._covers += [
        Cover("grass", "scrub and rough grazing", [(0.0, 0.0), (400.0, 0.0), (400.0, 400.0), (0.0, 400.0)]),
        Cover("reed", "marsh", [(400.0, 0.0), (800.0, 0.0), (800.0, 400.0), (400.0, 400.0)]),
        Cover("reed", "marsh", [(0.0, 700.0), (300.0, 700.0), (300.0, 950.0), (0.0, 950.0)]),  # no scrub beside it
    ]
    s.flush_covers()
    scrub, marsh = _slot(s, ("grass", "scrub and rough grazing")), _slot(s, ("reed", "marsh"))
    pid = tiles.pattern_id
    assert scrub.count(f"url(#{pid('fringe', 1.0)})") == 1 and marsh.count(f"url(#{pid('fringe', 1.0)})") == 1
    assert scrub.count(f"url(#{pid('grass-clumps', 1.0)})") == scrub.count(f"url(#{pid('grass', 1.0)})") == 1
    assert marsh.count(f"url(#{pid('reed-clumps', 1.0)})") == marsh.count(f"url(#{pid('reed', 1.0)})") == 2
    fringe = re.search(r'<path d="([^"]+)" fill="url\(#cover-fringe-1\)"', marsh)
    assert fringe is not None
    xs = [float(v) for v in re.findall(r"[ML](-?[\d.]+),", fringe.group(1))]
    assert min(xs) >= 399.0 and max(xs) <= 400.0 + tiles.FRINGE_FT / 2 + 1.0, "the marsh's half of the band, at the shared edge"
    defs = s.out[s._cover_slots["defs"]]
    assert all(pid(k, 1.0) in defs for k in ("grass", "reed", "fringe", "grass-clumps", "reed-clumps"))


def test_the_overlay_and_fringe_tiles_are_patterns_at_their_repeats() -> None:
    for kind, side in (("grass-clumps", tiles.OVERLAY_TILE_FT), ("reed-clumps", tiles.REED_OVERLAY_TILE_FT), ("fringe", tiles.COVER_TILE_FT), ("reed", tiles.REED_TILE_FT)):
        svg = tiles.TILES[kind](1.0)
        assert svg.startswith(f'<pattern id="{tiles.pattern_id(kind, 1.0)}" width="{side:g}"'), kind
    fringe = tiles.fringe_tile(1.0)
    assert 'stroke="#A7A860"' in fringe and 'stroke="#6E9377"' in fringe, "grass and reeds both"


def test_the_scrub_meets_a_recorded_marsh_without_a_gap() -> None:
    """FR-003's meeting (plan B): once a marsh is recorded, the scrub is handed no laid toe band, so the ground the marsh's
    shaping gives up is scrub."""
    from tests.settlement._builders import _covered

    s = Settlement(W=2000, H=1600, seed=4)
    s.meta(name="T", scale="hamlet", ftpx=1)
    laid = [(200.0, 800.0), (1800.0, 800.0), (1800.0, 1500.0), (200.0, 1500.0)]
    s.marsh(laid, role="toe")
    marsh = Polygon(s.M["marshes"][-1]["poly"])
    s.commons([(100.0, 600.0), (1900.0, 600.0), (1900.0, 1550.0), (100.0, 1550.0)], role="grazing")
    grass = _covered(s)
    given_up = Polygon(laid).difference(marsh)
    assert given_up.area > 1000.0, "non-vacuity: the shaping gave ground up"
    assert grass.intersection(given_up).area > 0.6 * given_up.area, "the scrub takes what the marsh gave up"
    assert box(0, 0, 1, 1).area == 1.0


def test_the_pond_cuts_a_marsh_as_its_ellipse_not_its_building_box() -> None:
    """Plan review (feature 299): the pond's no-build box keeps buildings off the water; the marsh is cut by the water itself."""
    from l7r.diagram.settlement.land.wet import pond_cut

    pond = [500.0, 400.0, 100.0, 60.0]
    pond_box = [(390.0, 330.0), (610.0, 330.0), (610.0, 470.0), (390.0, 470.0)]
    other = [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0)]
    cut = pond_cut([pond_box, other], pond)
    assert other in cut and pond_box not in cut and len(cut) == 2
    assert Polygon(cut[-1]).area < 0.8 * Polygon(pond_box).area, "the ellipse, not the box"
    far_box = [(100.0, 100.0), (900.0, 100.0), (900.0, 900.0), (100.0, 900.0)]  # holds the pond but is not its box
    assert pond_cut([far_box], pond) == [far_box] and pond_cut([pond_box], None) == [pond_box]


def test_a_scrub_sliver_wholly_inside_the_fringe_is_drawn_as_fringe_alone() -> None:
    s = Settlement(W=1000, H=1000, seed=1)
    s._covers += [
        Cover("grass", "scrub and rough grazing", [(400.0, 0.0), (405.0, 0.0), (405.0, 400.0), (400.0, 400.0)]),  # 5 ft wide
        Cover("reed", "marsh", [(405.0, 0.0), (800.0, 0.0), (800.0, 400.0), (405.0, 400.0)]),
    ]
    s.flush_covers()
    scrub = _slot(s, ("grass", "scrub and rough grazing"))
    assert scrub.count("<path") == 1 and "cover-fringe" in scrub, "only the fringe: no base or overlay left"


def test_the_reeds_reach_a_streams_edge_and_a_bank_band_lines_it() -> None:
    """Feature 300 (SC-001): a stream across a marsh - the reed shapes reach the water's drawn edge, the bank band is drawn in
    the marsh's slot, and a scrub zone the stream crosses keeps its grass to the bank as before (no band in its slot)."""
    from shapely.geometry import Point

    from tests.settlement._builders import _covered

    s = Settlement(W=1200, H=1200, seed=2)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["streams"] = [{"poly": [[600.0, 0.0], [600.0, 1200.0]], "w": 8}]
    s.marsh([(300.0, 600.0), (900.0, 600.0), (900.0, 1100.0), (300.0, 1100.0)], role="waterside")
    reeded = _covered(s)
    marsh = _slot(s, ("reed", "marsh"))
    assert f"url(#{tiles.pattern_id('reed-bank', 1.0)})" in marsh, "the bank band is drawn in the marsh's slot"
    assert reeded.contains(Point(605.0, 850.0)) and not reeded.contains(Point(601.0, 850.0)), "reeds to the drawn edge, not on the water"
    t = Settlement(W=1200, H=1200, seed=2)
    t.meta(name="T", scale="hamlet", ftpx=1)
    t.M["streams"] = [{"poly": [[600.0, 0.0], [600.0, 1200.0]], "w": 8}]
    t.commons([(300.0, 100.0), (900.0, 100.0), (900.0, 500.0), (300.0, 500.0)], role="pasture")
    t.flush_covers()
    assert "reed-bank" not in _slot(t, ("grass", None)), "no bank band in the scrub"
