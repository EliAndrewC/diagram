"""Feature 139 T50 (GM 2026-08-28): marsh is HARD ground - no house, garden or yard footprint may stand on it.

The reed fringe round a reservoir was drawn but registered nowhere a placer reads, so `_hard_clear`
passed footprints on it and two of Kuwabata's farmhouses stood in the reeds. `marsh()` now records its
polygon in `wet_polys`, which `_hard_ground` folds in beside the crop, the bog and the ditches."""

from __future__ import annotations

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
