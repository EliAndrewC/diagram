"""Where a hamlet's coarse grain grows (feature 287, water W36; `settlement/fields/grain.py`, research/contents.json#fields
0011): the placer's guarantee - the drawn dry band holds the need the winter-crop form leaves, or every plot the
ground offers is drawn - tested on constructed inputs that include the violating cases (a reserve plot on the brook, a
wet paddy that cannot carry barley, a need the ground cannot hold)."""

from __future__ import annotations

from typing import Any

import pytest

from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement._knobs import KNOBS
from l7r.diagram.settlement.fields.grain import COARSE_GRAIN_ACRES_PER_HOUSEHOLD, dry_need_acres, poly_area, top_up
from l7r.diagram.waterfields import FLOODED


def _sq(x: float, y: float, side: float = 200.0) -> list[tuple[float, float]]:
    return [(x, y), (x + side, y), (x + side, y + side), (x, y + side)]


def _plot(x: float, y: float, side: float = 200.0) -> dict[str, Any]:
    return {"poly": _sq(x, y, side), "fill": "#DCCFA6", "furrow": 6.0, "theta": 0.0, "crop": "barley"}


def test_the_winter_crop_is_a_knob_over_the_two_attested_forms() -> None:
    knob = KNOBS["winter_crop"]
    assert knob.value_space == ["barley", "none"]
    assert {knob.roll(seed, {}) for seed in range(40)} == {"barley", "none"}, "both forms are rolled across seeds"


def test_the_need_is_the_households_share_less_what_the_drained_paddy_carries_over_the_winter() -> None:
    assert dry_need_acres(10, 30.0, "none") == 10 * COARSE_GRAIN_ACRES_PER_HOUSEHOLD, "bare over the winter: the whole need is dry field"
    assert dry_need_acres(10, 30.0, "barley") == 0.0, "the drained paddy's barley covers it"
    assert abs(dry_need_acres(10, 5.0, "barley") - (10 * COARSE_GRAIN_ACRES_PER_HOUSEHOLD - 5.0)) < 1e-9, "a short winter crop leaves the rest"


def test_top_up_takes_the_reserve_in_order_skips_a_refused_plot_and_stops_at_the_need() -> None:
    on_water = _plot(0.0, 0.0)
    a, b, c = _plot(0.0, 300.0), _plot(0.0, 600.0), _plot(0.0, 900.0)
    got = top_up(10_000.0, [on_water, a, b, c], 90_000.0, lambda poly: poly is on_water["poly"])
    assert got == [a, b], "the first plot is refused; 10,000 + 40,000 + 40,000 reaches the need at b"
    assert top_up(90_000.0, [a], 90_000.0, lambda poly: False) == [], "a band that already holds the need takes nothing"
    assert top_up(0.0, [on_water, a], 1e9, lambda poly: poly is on_water["poly"]) == [a], "an unmeetable need takes every plot the ground offers"


def _hamlet(households: int, form: str) -> Settlement:
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, generated_by="hamletgen", households=households, fan_middle="wild")
    s.pin_knob("winter_crop", form)
    return s


def _net(paddy_fill: str) -> tuple[dict[str, Any], dict[str, Any]]:
    toe = _plot(1000.0, 1000.0)
    on_brook = _plot(100.0, 100.0)  # nearest the toe, and across the brook - the violating case
    net = {
        "dry_plots": [toe],
        "dry_reserve": [on_brook, _plot(400.0, 100.0), _plot(700.0, 100.0), _plot(1000.0, 100.0)],
        "plots": [{"poly": _sq(1300.0, 1300.0, 300.0), "fill": paddy_fill}],  # 90,000 sq ft: 2.07 acres of paddy
    }
    return net, {"kind": "stream", "stream": [(200.0, 0.0), (200.0, 400.0)]}


def _drawn(s: Settlement) -> set[tuple[float, float]]:
    return {(p["poly"][0][0], p["poly"][0][1]) for p in s.M["dry_plots"]}


def test_a_single_cropped_wild_fan_tops_its_dry_band_up_to_the_need_off_the_brook() -> None:
    s = _hamlet(2, "none")  # need 1.7 acres = 74,052 sq ft; the toe holds 40,000
    net, source = _net("#7FA35A")
    s._comb_draw_hem(net, source)
    assert _drawn(s) == {(1000.0, 1000.0), (400.0, 100.0)}, "the brook plot is skipped, and one reserve plot meets the need"
    meta = s.M["meta"]
    assert meta["winter_crop"] == "none"
    assert meta["coarse_grain_dry_acres"] >= meta["coarse_grain_dry_need_acres"] == round(2 * COARSE_GRAIN_ACRES_PER_HOUSEHOLD, 2)


def test_a_double_cropped_wild_fan_grows_its_grain_on_the_drained_paddy_and_draws_only_the_toe() -> None:
    s = _hamlet(2, "barley")
    net, source = _net("#7FA35A")
    s._comb_draw_hem(net, source)
    assert _drawn(s) == {(1000.0, 1000.0)}
    assert s.M["meta"]["coarse_grain_dry_need_acres"] == 0.0


def test_a_wet_paddy_carries_no_winter_barley_so_the_band_is_topped_up_all_the_same() -> None:
    s = _hamlet(2, "barley")
    net, source = _net(FLOODED)
    s._comb_draw_hem(net, source)
    assert (400.0, 100.0) in _drawn(s), "the blue plot is shitsuden, too wet for barley"


def test_a_green_plot_of_the_drain_side_row_carries_no_winter_barley_either() -> None:
    """Feature 328 (0007: the lowest row's green plots are as wet as its blue ones): a plot of the drain-side row counts as
    wet whatever its tint, so the band is topped up as for a blue one."""
    s = _hamlet(2, "barley")
    net, source = _net("#7FA35A")
    net["plots"][0]["low"] = True
    s._comb_draw_hem(net, source)
    assert (400.0, 100.0) in _drawn(s), "the low row's green plot is not drained"


def test_the_knob_offers_only_the_forms_this_ground_can_feed() -> None:
    """The violating case: ten households need 8.5 acres of dry field, and the toe and the middle offered hold 3.7. Bare
    over the winter is never rolled there; with the drained paddy's barley the need left is nil and the band holds it."""
    knob = KNOBS["winter_crop"]
    ctx = {"grain_households": 10, "grain_drained_acres": 20.0, "grain_room_acres": 3.7}
    assert knob.allowed(ctx) == ["barley"]
    assert knob.allowed({**ctx, "grain_drained_acres": 1.0}) == [], "neither form: the roll is a loud error, never a short band"
    assert knob.allowed({**ctx, "grain_room_acres": 9.0}) == ["barley", "none"]
    assert knob.allowed({}) == ["barley", "none"], "a context without the site's figures offers both"


def test_a_hamlet_whose_ground_cannot_feed_it_unwatered_rolls_the_winter_crop() -> None:
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True, generated_by="hamletgen", households=10, fan_middle="wild")
    net, source = _net("#7FA35A")
    net["plots"] = [{"poly": _sq(1300.0, 1300.0, 700.0), "fill": "#7FA35A"}]  # 11.2 acres drained: covers 8.5
    s._comb_draw_hem(net, source)
    assert s.M["meta"]["winter_crop"] == "barley" and s.M["meta"]["coarse_grain_dry_need_acres"] == 0.0


def test_pinning_a_form_the_ground_cannot_feed_is_refused_loudly() -> None:
    s = _hamlet(10, "none")
    net, source = _net("#7FA35A")
    with pytest.raises(ValueError, match="typing rule"):
        s._comb_draw_hem(net, source)


def test_a_map_the_generator_did_not_make_is_not_topped_up() -> None:
    s = Settlement(2000, 2000, seed=1)
    s.meta(name="V", scale="hamlet", ftpx=1, toscale=True)
    net, source = _net("#7FA35A")
    s._comb_draw_hem(net, source)
    assert _drawn(s) == {(1000.0, 1000.0)} and "winter_crop" not in s.M["meta"]


def test_poly_area_is_the_shoelace() -> None:
    assert poly_area(_sq(0.0, 0.0, 10.0)) == 100.0
