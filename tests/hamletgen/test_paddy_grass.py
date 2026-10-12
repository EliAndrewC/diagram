"""The paddy's own grass hill (feature 374 wave 148, `hamletgen/hinterland/paddy_grass.py`): rolled now and then on a grass-hill
map, seated on the open ground just upslope of a plot at the field's top, drawn as open grass."""

from __future__ import annotations

import types

from l7r.diagram.hamletgen.hinterland import paddy_grass as pg
from l7r.diagram.settlement import Settlement

SQUARE = [[0.0, 0.0], [40.0, 0.0], [40.0, 40.0], [0.0, 40.0]]


def _shifted(dx: float, dy: float) -> list[list[float]]:
    return [[x + dx, y + dy] for x, y in SQUARE]


def _plan(flood: bool = False, seed: int = 1) -> types.SimpleNamespace:
    return types.SimpleNamespace(flood_ground=flood, spec=types.SimpleNamespace(seed=seed), fall=(0.0, 1.0))


def test_the_upslope_plots_are_the_field_s_top_nearest_first() -> None:
    plots = [_shifted(0, 200), _shifted(0, 100), [[1.0, 1.0]], _shifted(0, 300)]
    got = pg.upslope_plots(plots, (0.0, 1.0), n=2)
    assert got == [_shifted(0, 100), _shifted(0, 200)], "against the fall first; a ring of under three points is no plot"


def test_a_floodplain_map_rolls_none_and_a_grass_hill_map_one_in_three() -> None:
    assert not any(pg.paddy_grass_hill(_plan(flood=True, seed=s)) for s in range(30)), "no slope above a river flat's paddies"
    rolled = sum(pg.paddy_grass_hill(_plan(seed=s)) for s in range(300))
    assert 60 < rolled < 140, "about one hamlet in three"


def test_the_grass_hill_is_seated_above_its_plot_and_recorded(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["fields"] = [{"plot_rings": [_shifted(280, 300), [[0.0, 0.0], [0.5, 0.0], [0.0, 0.5]]]}]
    monkeypatch.setattr(pg, "paddy_grass_hill", lambda plan: True)
    square = pg.lay_paddy_grass(s, _plan())
    assert square is not None and s.M["meta"]["paddy_grass_hill"] == "drawn" and square in s.block_polys
    assert max(y for _x, y in square) <= 300.0 - pg.GRASS_GAP_FT + 1.0, "above the plot's top edge, its gap kept"
    side = square[1][0] - square[0][0]
    assert abs(side - 40.0) < 0.5, "about the plot's own size"
    pg.draw_paddy_grass(s, square)
    assert s.M["commons"][-1]["role"] == "paddy_grass"


def test_none_rolled_or_no_seat_is_recorded(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["fields"] = [{"plot_rings": [_shifted(280, 300)]}]
    monkeypatch.setattr(pg, "paddy_grass_hill", lambda plan: False)
    assert pg.lay_paddy_grass(s, _plan()) is None and s.M["meta"]["paddy_grass_hill"] == "none"
    monkeypatch.setattr(pg, "paddy_grass_hill", lambda plan: True)
    monkeypatch.setattr(s, "open_seat", lambda *a, **k: None)
    assert pg.lay_paddy_grass(s, _plan()) is None and s.M["meta"]["paddy_grass_hill"] == "no seat"


def test_the_grass_hill_keeps_its_gap_off_the_plot_on_a_turned_fall(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """impl-drift on wave 148: on a diagonal fall an unturned square's corner reaches further along the fall than its half side,
    and the seat search may slide it - the gap is held as seated, and a seat that falls short is passed over."""
    s = Settlement(W=600, H=600, seed=1)
    s.meta(name="T", scale="hamlet", ftpx=1)
    s.M["fields"] = [{"plot_rings": [_shifted(280, 300)]}]
    k = 2**-0.5
    plan = types.SimpleNamespace(flood_ground=False, spec=types.SimpleNamespace(seed=1), fall=(k, k))
    square = pg.seat_paddy_grass(s, plan)
    assert square is not None and pg.clear_of_plot(square, _shifted(280, 300), pg.GRASS_GAP_FT)
    monkeypatch.setattr(s, "open_seat", lambda *a, **k: (300.0, 290.0))  # slid onto the plot
    assert pg.seat_paddy_grass(s, plan) is None


def test_a_square_slid_off_the_paddy_s_flank_is_not_above_it() -> None:
    """impl-drift on wave 148: the gap is not enough - the square must stand upslope of its paddy, not beside it."""
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert pg.above(square, 20.0, (0.0, 1.0), 6.0), "its lowest edge 10 above the plot's top"
    assert not pg.above(square, 14.0, (0.0, 1.0), 6.0), "within the gap of the top"
    assert not pg.above([(x + 0.0, y + 30.0) for x, y in square], 20.0, (0.0, 1.0), 6.0), "below the top - off the flank"
