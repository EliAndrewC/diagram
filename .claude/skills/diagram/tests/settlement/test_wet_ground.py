"""Feature 150 T50 (GM 2026-08-28): marsh is HARD ground - no house, garden or yard footprint may stand on it.

The reed fringe round a reservoir was drawn but registered nowhere a placer reads, so `_hard_clear`
passed footprints on it and two of Kuwabata's farmhouses stood in the reeds. `marsh()` now records its
polygon in `wet_polys`, which `_hard_ground` folds in beside the crop, the bog and the ditches."""

from __future__ import annotations

import re

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.land.wet import _clipped_to_open_ground

_FRINGE = [(300.0, 300.0), (500.0, 300.0), (500.0, 500.0), (300.0, 500.0)]


def _s() -> Settlement:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="village")
    s.marsh(_FRINGE, role="pond_fringe")
    return s


def test_a_marsh_registers_as_wet_ground() -> None:
    s = _s()
    assert s.wet_polys == [_FRINGE]
    assert any(len(p) == 4 and p[0] == (300.0, 300.0) for p in s._hard_ground()), "the fringe is in the hard set"


def test_a_footprint_on_the_marsh_is_refused_and_one_beside_it_is_not() -> None:
    s = _s()
    assert s._hard_clear(400, 400, 46, 28) is False  # on the reeds
    assert s._hard_clear(400, 560, 46, 28) is True  # 40 ft south of them
    assert s._rect_blocked((400, 400, 46, 28), fields=True) is True


def test_the_hard_ground_cache_re_keys_when_a_marsh_is_added() -> None:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="V", scale="village")
    assert s._hard_clear(400, 400, 46, 28) is True  # cached: nothing wet yet
    s.marsh(_FRINGE, role="pond_fringe")
    assert s._hard_clear(400, 400, 46, 28) is False  # the key includes the wet count, so the cache does not lie


# ---- feature 150 T54: reeds keep OFF the earthen mounds ------------------------------------------
def _ring(x0: float, y0: float, x1: float, y1: float, n: int = 30) -> list[list[float]]:
    """A rectangle's perimeter, sampled - the shape a drawn band records (a dense closed ribbon)."""
    return (
        [[x0 + (x1 - x0) * i / n, y0] for i in range(n)]
        + [[x1, y0 + (y1 - y0) * i / n] for i in range(n)]
        + [[x1 - (x1 - x0) * i / n, y1] for i in range(n)]
        + [[x0, y1 - (y1 - y0) * i / n] for i in range(n)]
    )


_BAND = _ring(600.0, 200.0, 640.0, 800.0)  # a 40 ft dike band, N-S...
_CREST = [
    [620.0, 200.0 + 30.0 * i] for i in range(21)
]  # ...and its centerline, which every drawn band records and the keep-out reads (it tests the crest + half of w_max, not the 360-point ribbon: feature 150 T55 perf)
_WIDE = [(300.0, 200.0), (900.0, 200.0), (900.0, 800.0), (300.0, 800.0)]  # a marsh polygon straight over it


def _marks(s: Settlement) -> list[tuple[float, float]]:
    """Every reed blade start, wet-tint center and glint the marsh drew, from the ink itself."""
    s.flush_blade_groups()  # the reed bucket is written at finish since feature 223
    svg = "".join(s.out)
    out = [(float(a), float(b)) for a, b in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="[\d.]+" fill="#9FBBAE"', svg)]
    out += [(float(a), float(b)) for a, b in re.findall(r'<ellipse cx="([-\d.]+)" cy="([-\d.]+)"[^>]*fill="#C2D6CE"', svg)]
    for g in re.findall(r'<g stroke="#6E9377" stroke-width="0.8">(.*?)</g>', svg, re.S):
        out += [(float(a), float(b)) for a, b in re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)"', g)]
        out += [(float(a), float(b)) for a, b in re.findall(r'M([-\d.]+),([-\d.]+)L', g)]  # the merged form (feature 222)
    return out


def _on_band(x: float, y: float) -> bool:
    return 600.0 <= x <= 640.0 and 200.0 <= y <= 800.0


def test_a_marsh_over_a_dike_band_draws_no_reed_on_it_and_would_without_the_dike() -> None:
    """The rule FIRES: the same marsh polygon over the same ground reeds the band when no dike is
    recorded and leaves it bare when one is (feature 150 T54, GM 2026-08-28: "the hazy blue that
    denotes the marsh is clearly overlaid on top of the greenery of the earthen mounds")."""
    bare = Settlement(1200, 1000, seed=2)
    bare.meta(name="V", scale="village")
    bare.marsh(_WIDE, role="waterside")
    assert sum(1 for x, y in _marks(bare) if _on_band(x, y)) > 20, "the un-guarded marsh reeds the band - the test's own premise"

    diked = Settlement(1200, 1000, seed=2)
    diked.meta(name="V", scale="village")
    diked.M["dikes"] = [{"outline": _BAND, "crest": _CREST, "w_min": 40.0, "w_max": 40.0}]
    diked.marsh(_WIDE, role="waterside")
    assert [1 for x, y in _marks(diked) if _on_band(x, y)] == []


def test_a_wet_tint_circle_keeps_its_whole_body_off_the_mound() -> None:
    """The tint is a 15-28 ft haze circle: its CENTER standing off the band is not enough, the body
    is what laps the greenery. Centers stand at least the widest radius clear."""
    s = Settlement(1200, 1000, seed=5)
    s.meta(name="V", scale="village")
    s.M["dikes"] = [{"outline": _BAND, "crest": _CREST, "w_min": 40.0, "w_max": 40.0}]
    s.marsh(_WIDE, role="waterside")
    s.flush_blade_groups()  # the scatter's marks are written at finish since feature 225
    svg = "".join(s.out)
    tints = [(float(a), float(b), float(r)) for a, b, r in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)" fill="#9FBBAE"', svg)]
    assert tints, "no tint drawn at all - the test would pass vacuously"
    for x, y, r in tints:
        if 200.0 <= y <= 800.0:
            assert x + r <= 600.0 or x - r >= 640.0, f"a tint circle laps the mound: {(x, y, r)}"


def test_a_pond_bank_keeps_the_reeds_off_the_same_way() -> None:
    """A fish pond's mulberry bank is the same planted earth as the perimeter dike (feature 150 T54)."""
    s = Settlement(1200, 1000, seed=3)
    s.meta(name="V", scale="village")
    s.M["dikeponds"] = [{"bank": _ring(600.0, 300.0, 700.0, 500.0)}]
    s.marsh(_WIDE, role="toe")
    assert [1 for x, y in _marks(s) if 600.0 <= x <= 700.0 and 300.0 <= y <= 500.0] == []


# ---------------------------------------------------------------------------
# The degenerate-geometry guards (feature 155: the hamlet-path floor).
#
# Every one of these is a `return` taken when Shapely is handed something that is
# not a polygon - a two-point ring, a collinear sliver, a clip that removes
# everything. They are cheap to reach directly and impossible to reach from a
# rolled map, which is exactly why they sat uncovered: a real settlement never
# produces them, and the guard exists for the day one does.


def test_a_band_half_width_of_a_degenerate_ring_is_zero_not_a_crash() -> None:
    """Under three points there is no polygon to measure, and a collinear sliver has area 0 with a
    non-zero perimeter - `buffer(0)` returns an EMPTY geometry for it rather than raising."""
    from l7r.diagram.settlement.land.wet import _band_half_width

    assert _band_half_width([(0.0, 0.0), (10.0, 0.0)], None, "toe") == 0.0
    collinear = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (10.0, 0.0)]
    assert _band_half_width(collinear, None, "toe") == 0.0


def test_an_unbuildable_band_measures_zero_rather_than_propagating(monkeypatch) -> None:
    """The `except` here is NOT reachable through the argument, and that is worth stating: Shapely 2
    tolerates NaN, infinite and self-crossing rings, returning a geometry rather than raising, and the
    `len(pts) < 3` guard above already excludes the one constructor error a caller could provoke. What
    raises is the geometry ENGINE, on invalid topology inside `buffer` or `difference` - a GEOSException
    from library internals, which no input reliably reproduces across versions. So the handler's
    CONTRACT is what is pinned: whatever the engine throws, an unmeasurable band is zero, not a
    traceback out of a draw call."""
    from l7r.diagram.settlement.land import wet

    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]

    def _boom(*_a, **_k):
        raise ValueError("invalid topology")

    wet._load_shapely()  # feature 237: the name is bound on FIRST USE, so a module-global patch needs the loader to have run
    monkeypatch.setattr(wet, "ShapelyPolygon", _boom)
    assert wet._band_half_width(square, None, "toe") == 0.0


def test_a_clip_that_would_remove_everything_returns_the_polygon_unchanged() -> None:
    """A marsh polygon wholly inside the dikes has nothing left after the subtraction. Handing back
    an empty record would erase the feature from the manifest; handing back the original leaves it
    visible and lets the checks report it, which is this engine's standing trade."""
    from l7r.diagram.settlement.land.wet import _clipped_to_open_ground

    poly = [(10.0, 10.0), (20.0, 10.0), (20.0, 20.0), (10.0, 20.0)]
    swallowing = [{"outline": [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]}]
    assert _clipped_to_open_ground(poly, swallowing) == poly
    # a dike record with no usable outline contributes no ring, and with nothing to cut the outline
    # comes straight back rather than being run through shapely for nothing
    assert _clipped_to_open_ground(poly, [{"outline": [(0.0, 0.0), (1.0, 1.0)]}]) == poly


def test_an_unbuildable_clip_hands_the_polygon_straight_back(monkeypatch) -> None:
    """Same contract, same reason (see above): the marsh keeps the shape it came in with rather than
    vanishing from the manifest, because a feature the reader can see and the checks can report beats
    a silent deletion."""
    from l7r.diagram.settlement.land import wet

    poly = [(10.0, 10.0), (20.0, 10.0), (20.0, 20.0), (10.0, 20.0)]

    def _boom(*_a, **_k):
        raise ValueError("invalid topology")

    wet._load_shapely()  # feature 237: the name is bound on FIRST USE, so a module-global patch needs the loader to have run
    monkeypatch.setattr(wet, "ShapelyPolygon", _boom)
    assert wet._clipped_to_open_ground(poly, []) == poly


def test_keyholing_skips_a_hole_too_small_to_walk() -> None:
    """A keyhole seam needs a ring on both sides. A degenerate interior - fewer than three points -
    is skipped rather than spliced, because there is no loop to walk and the seam would double back
    on itself. The OUTER ring still comes back whole, which is the point: the guard must not cost
    the polygon its own boundary."""
    from shapely.geometry import Polygon as ShapelyPolygon

    from l7r.diagram.settlement.land.wet import _keyholed

    square = ShapelyPolygon([(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)])
    holed = ShapelyPolygon(
        [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)],
        [[(40.0, 40.0), (60.0, 40.0), (60.0, 60.0), (40.0, 60.0)]],
    )
    spliced = _keyholed(holed)
    assert len(spliced) > len(_keyholed(square)), "a real hole is spliced in on a seam"

    # a hole walked as a two-point degenerate: skipped, outer ring intact
    class _Degenerate:
        exterior = square.exterior

        class _H:
            coords = [(40.0, 40.0), (60.0, 40.0), (40.0, 40.0)]

        interiors = [_H()]

    assert _keyholed(_Degenerate()) == [(0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)]


def test_an_outline_shapely_cannot_build_is_returned_unclipped() -> None:
    """Feature 174: the `except (ValueError, GEOSException)` path - refuse to clip rather than fail.

    A two-point ring is not a polygon, so `ShapelyPolygon` raises before any difference is taken. The
    contract is that the caller gets its own outline back untouched, not an exception and not an
    empty result - a marsh that cannot be clipped is still a marsh.
    """
    poly = [(0.0, 0.0), (10.0, 0.0)]
    dikes = [{"outline": [(0.0, 0.0), (5.0, 0.0), (5.0, 5.0)]}]
    assert _clipped_to_open_ground(poly, dikes) == poly, "the outline is handed back as it came in"


def test_the_hard_ground_sweep_SKIPS_a_ditch_that_carries_no_path() -> None:
    """`_hard_ground` sweeps every recorded watercourse, and a record carrying neither `poly` nor
    `pts` has no line for a placer to keep clear of. Production always writes one - which is why the
    skip was excluded from coverage - but the sweep is what would raise, and it would take the whole
    placement pass down with it."""
    s = _s()
    s.M["field_ditches"] = [{"w": 3.0}, {"poly": [[100.0, 100.0], [200.0, 100.0]], "w": 3.0}]
    s._hard_cache = None if hasattr(s, "_hard_cache") else None
    hard = s._hard_ground()
    assert hard, "the ditch that HAS a path is still folded in; the pathless one is simply skipped"


def test_the_vectorized_marsh_keeps_every_keep_out_and_its_density() -> None:
    """Feature 281 (FR-009): the marsh's tints and tufts are thrown and tested as arrays. Every mark stands where the
    per-point test would have let it - inside the outline, off every keep-out at its kind's pads, off the pond at its
    lateral reach and (a tuft) with its blade top off the water, inside the frame; a tuft's glint or blades stand at its
    base - and the share of throws kept matches a per-point scatter of the old form over many throws (the density), for
    both kinds. The same seed throws the same marks."""
    import math
    import random

    from l7r.diagram.settlement._geom import KeepoutGrid, RingIndex
    from l7r.diagram.settlement.land.wet import marsh_scatter

    outline = [(0.0, 0.0), (700.0, 0.0), (720.0, 520.0), (320.0, 580.0), (0.0, 500.0)]
    ring = RingIndex(outline)
    keep = KeepoutGrid()
    keep.rings([[(100.0, 100.0), (220.0, 90.0), (230.0, 200.0), (110.0, 210.0)]], pad=10.0)
    keep.segs([([(0.0, 330.0), (700.0, 360.0)], 3.0)])
    keep.segs([([(400.0, 420.0), (650.0, 440.0)], 2.0)], slot=3, reach=30.0)
    pond = (480.0, 180.0, 60.0, 40.0)
    frame = (0.0, 0.0, 690.0, 570.0)
    extras = ((0.0, 28.0, 28.0, 30.0), (0.0, 7.0, 7.0, 9.0))
    pads, tip, feather = (28.0, 1.5), 7.0, 46.0
    args = ((6000, 14000), (0.0, 0.0, 720.0, 580.0), frame, ring, keep, extras, None, (30.0, 9.0), pond, pads, tip, feather, 28.0, 1.0, 281)
    blades, marks = marsh_scatter(*args)
    tints = [((m[0] + m[2]) / 2, (m[1] + m[3]) / 2) for m in marks if "<circle" in m[4]]
    glints = [((m[0] + m[2]) / 2, (m[1] + m[3]) / 2) for m in marks if "<ellipse" in m[4]]
    tufts = {(float(b[0]), float(b[1])) for b in blades}
    assert tints and glints and tufts, "non-vacuity: every kind of mark"
    near = [(dx, dy) for dx in (-0.05, 0.0, 0.05) for dy in (-0.05, 0.0, 0.05)]  # a mark is recorded to 0.1 px

    def ok(x, y, extra, lat, up):
        def one(px, py):
            if not ring.inside(px, py) or keep.hit(px, py, extra):
                return False
            if ((px - pond[0]) / (pond[2] + lat)) ** 2 + ((py - pond[1]) / (pond[3] + lat)) ** 2 < 1.0:
                return False
            return not (up and ((px - pond[0]) / pond[2]) ** 2 + ((py - up - pond[1]) / pond[3]) ** 2 < 1.0)

        return any(one(x + dx, y + dy) for dx, dy in near)

    for x, y in tints:
        assert ok(x, y, extras[0], pads[0], 0.0), (x, y)
    for x, y in [*tufts, *glints]:
        assert frame[0] - 0.05 <= x <= frame[2] + 0.05 and frame[1] - 0.05 <= y <= frame[3] + 0.05
        assert ok(x, y, extras[1], pads[1], tip), (x, y)

    def old_kept(n, extra, lat, up, drop, seed):  # the per-point form: `_sparse`, one throw at a time
        rnd = random.Random(seed)
        kept = 0
        for _ in range(n):
            px, py = rnd.uniform(0.0, 720.0), rnd.uniform(0.0, 580.0)
            if not (frame[0] <= px <= frame[2] and frame[1] <= py <= frame[3]) or not ok(px, py, extra, lat, up):
                continue
            ed = ring.edge_within(px, py, feather)
            if ed is not None and rnd.random() > (ed / feather) ** drop:
                continue
            kept += 1
        return kept

    for got, n, extra, lat, up, drop in ((len(tints), 6000, extras[0], pads[0], 0.0, 0.9), (len(glints) + len(tufts), 14000, extras[1], pads[1], tip, 0.7)):
        want = sum(old_kept(n, extra, lat, up, drop, s) for s in range(3)) / 3
        assert abs(got - want) <= 4 * math.sqrt(want) + 0.02 * want, (got, want)
    assert marsh_scatter(*args) == (blades, marks)
    assert marsh_scatter((0, 0), *args[1:]) == ([], [])
    # a crescent pond keeps both kinds off its water at each kind's pad, point for point
    moon = (200.0, 450.0, 50.0)

    def crescent(x, y, pad):
        return math.hypot(x - moon[0], y - moon[1]) < moon[2] + pad

    cb, cm = marsh_scatter(*args[:6], crescent, *args[7:])
    kept = [((m[0] + m[2]) / 2, (m[1] + m[3]) / 2, 30.0) for m in cm if "<circle" in m[4]] + [(float(b[0]), float(b[1]), 9.0) for b in cb]
    assert kept and all(math.hypot(x - moon[0], y - moon[1]) >= moon[2] + pad - 0.1 for x, y, pad in kept)
    assert len(cm) + len(cb) < len(marks) + len(blades), "the crescent refused some throws"
