"""Feature 150 T50 (GM 2026-08-28): marsh is HARD ground - no house, garden or yard footprint may stand on it.

The reed fringe round a reservoir was drawn but registered nowhere a placer reads, so `_hard_clear`
passed footprints on it and two of Kuwabata's farmhouses stood in the reeds. `marsh()` now records its
polygon in `wet_polys`, which `_hard_ground` folds in beside the crop, the bog and the ditches."""

from __future__ import annotations

import re

from l7r.diagram.settlement import Settlement

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
    svg = "".join(s.out)
    out = [(float(a), float(b)) for a, b in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="[\d.]+" fill="#9FBBAE"', svg)]
    out += [(float(a), float(b)) for a, b in re.findall(r'<ellipse cx="([-\d.]+)" cy="([-\d.]+)"[^>]*fill="#C2D6CE"', svg)]
    for g in re.findall(r'<g stroke="#6E9377" stroke-width="0.8">(.*?)</g>', svg, re.S):
        out += [(float(a), float(b)) for a, b in re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)"', g)]
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
