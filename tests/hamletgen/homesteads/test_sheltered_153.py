"""A row village's leeward farm sheltered by the grove row across its street (feature 374 wave 153, 0033's second form): its
windward grove one tree deep, its bamboo a band along its south side past its plots' sun."""

from __future__ import annotations

import math
import types

import pytest

from l7r.diagram.hamletgen.homesteads import bamboo as bm
from l7r.diagram.hamletgen.homesteads.rows import ACROSS_THE_WIND_COS, sheltered_by_the_row_across
from l7r.diagram.hamletgen.plan import HamletSpec


def test_a_farm_is_sheltered_only_with_its_street_across_the_wind_on_its_windward_side() -> None:
    # a street running east-west, the far side (+1) north of it under a north wind: the street is south of the farm, to its lee
    assert not sheltered_by_the_row_across(1, (0.0, -1.0), "N")
    assert sheltered_by_the_row_across(-1, (0.0, -1.0), "N"), "the near row south of the street: the street and the row beyond to its north"
    assert not sheltered_by_the_row_across(-1, (1.0, 0.0), "N"), "a street running with the wind shelters no one"
    assert 0.38 < ACROSS_THE_WIND_COS < 0.39 and sheltered_by_the_row_across(-1, (0.0, -1.0), "XX"), "an unknown wind reads as the default NW"


def test_a_sheltered_farm_s_windward_band_is_drawn_one_tree_deep_against_its_house() -> None:
    from l7r.diagram.settlement.rolling.farmsteads import thinned

    # a north band (face (0, -1)) 40 deep, its inner edge at y = 20: cut to 17, the inner edge kept
    assert thinned(0.0, 0.0, 100.0, 40.0, (0, -1), 17.0) == (0.0, 11.5, 100.0, 17.0)
    assert thinned(0.0, 0.0, 40.0, 100.0, (-1, 0), 17.0) == (11.5, 0.0, 17.0, 100.0), "a west band, its east edge kept"
    assert thinned(0.0, 0.0, 100.0, 10.0, (0, 1), 17.0) == (0.0, 0.0, 100.0, 10.0), "already thinner: as it stood"


def test_the_south_band_runs_the_whole_farmstead_across_past_its_plots_sun() -> None:
    h = {"geom": {"house": (100.0, 100.0, 46.0, 28.0), "yard": (100.0, 132.0, 40.0, 30.0), "gardens": [(140.0, 132.0, 20.0, 24.0)]}}
    seats = list(bm.south_band(h, lambda v: v))
    assert len(seats) == bm.BAND_STEPS_OUT + 1, "no frame: the house, yard and beds across alone"
    cx, cy, w, d = seats[0]
    assert (cx - w / 2, cx + w / 2) == (77.0, 150.0), "the house, yard and beds across"
    assert cy - d / 2 == pytest.approx(147.0 + bm.BAMBOO_SHADE_FT + 1.0) and d == bm.HOUSEHOLD_BAMBOO_FT[1]
    assert seats[1][1] - seats[0][1] == d, "stepped south a strip's depth at a time"
    assert list(bm.south_band({"geom": {}}, lambda v: v)) == []
    framed = {"geom": {**h["geom"], "bbox": (110.0, 150.0, 240.0, 200.0), "groves": [(110.0, 58.0, 240.0, 17.0), (-1.5, 150.0, 17.0, 200.0)], "grove_faces": [([0, -1], "deep"), ([-1, 0], "deep")]}}
    offers = list(bm.south_band(framed, lambda v: v))
    spans = [(round(c - w / 2, 1), round(c + w / 2, 1)) for c, _y, w, _d in offers]
    n = bm.BAND_STEPS_OUT + 1
    assert spans == [(-10.0, 230.0)] * n + [(7.0, 230.0)] * n, "the frame whole stepped all the way south, then between its side groves"
    assert offers[1][1] - offers[0][1] == bm.HOUSEHOLD_BAMBOO_FT[1]
    assert bm.band_spans({"bbox": (0.0, 0.0, 10.0, 10.0), "groves": [(0.0, 0.0, 10.0, 2.0)], "grove_faces": [([0, -1], "deep")]}, [(0.0, 0.0, 10.0, 4.0)]) == [(-5.0, 5.0)], "each span once"


def test_every_sheltered_farm_wants_its_bamboo_where_the_farmsteads_keep_it() -> None:
    s = types.SimpleNamespace(_hjit=lambda x, y, salt: 0.99)  # a roll that keeps no strip of its own
    houses = [{"x": 1.0, "y": 1.0, "sheltered": True, "geom": {}}, {"x": 2.0, "y": 2.0, "geom": {}}]
    assert bm.household_bamboo_wanted(s, types.SimpleNamespace(bamboo="homestead"), houses) == 1, "always, not three in five"
    assert bm.household_bamboo_wanted(s, types.SimpleNamespace(bamboo="none"), houses) == 0, "none where the knob gave the farmsteads none"
    assert bm.household_bamboo_wanted(s, types.SimpleNamespace(bamboo="thicket"), houses) == 0
    assert bm.household_bamboo_wanted(s, types.SimpleNamespace(bamboo="homestead"), houses[1:]) == 0


def test_the_spec_takes_the_two_forms_and_refuses_another() -> None:
    assert HamletSpec(name="T", seed=1, row_shelter="sheltered").row_shelter == "sheltered"
    with pytest.raises(ValueError, match="row_shelter"):
        HamletSpec(name="T", seed=1, row_shelter="hedge")
    assert math.isclose(math.cos(math.radians(67.5)), ACROSS_THE_WIND_COS)


def test_its_own_door_path_does_not_part_a_farm_from_its_band() -> None:
    ground = bm.StripGround(
        fields=[], marsh=[], pond=None, lanes=[([(0.0, 0.0), (10.0, 0.0)], 4.0), ([(0.0, 5.0), (9.0, 5.0)], 4.0)], footing=None, seats=[], sun=[], belt=None, skip=frozenset(), near=None
    )  # type: ignore[arg-type]
    lanes = [{"pts": [[0, 0], [10, 0]], "serves": [100.0, 100.0]}, {"pts": [[0, 5], [9, 5]]}, {"pts": [[1, 1]]}]
    mine = bm.own_ground(ground, lanes, (100.0, 100.0))
    assert mine.lanes == [ground.lanes[1]], "its own path out, a public lane kept"
    assert bm.own_ground(ground, lanes, (5.0, 5.0)).lanes == ground.lanes
