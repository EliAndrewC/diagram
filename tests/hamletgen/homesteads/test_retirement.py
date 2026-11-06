"""`hamletgen/homesteads/retirement.py` on stub settlements - the retirement house and its knob (269 E8, B42; 0004)."""

from __future__ import annotations

import math

import pytest

import l7r.diagram.settlement.rolling.access as access_mod
from l7r.diagram.hamletgen.homesteads.retirement import (
    FAMILY_FORMS,
    RETIREMENT_SHARE,
    retirement_glyph,
    retirement_houses,
    turned_box,
)
from l7r.diagram.settlement._knobs import KNOBS
from tests.settlement._builders import _byre_village


def test_the_family_form_knob_rolls_between_the_two_attested_forms() -> None:
    knob = KNOBS["family_form"]
    assert tuple(knob.value_space) == FAMILY_FORMS == ("one_roof", "retirement_house") and knob.default == "one_roof"
    assert {knob.roll(seed, {}) for seed in range(40)} == set(FAMILY_FORMS), "both forms are reachable from a seed"


def test_one_roof_draws_no_retirement_house_and_declares_its_form() -> None:
    s, _hs = _byre_village()
    s.pin_knob("family_form", "one_roof")
    assert retirement_houses(s, None) == 0  # type: ignore[arg-type]
    assert s.M["meta"]["family_form"] == "one_roof" and s.M["retirement_houses"] == []
    assert "retirement_target" not in s.M["meta"]


def test_the_box_turns_and_the_glyph_draws_a_door() -> None:
    assert all(abs(a - b) < 1e-9 for a, b in zip(turned_box(18.0, 15.0, 180.0), (18.0, 15.0), strict=True))
    w, h = turned_box(18.0, 15.0, 90.0)
    assert abs(w - 15.0) < 1e-9 and abs(h - 18.0) < 1e-9
    g = retirement_glyph(10.0, 20.0, 18.0, 15.0, 90.0)
    assert g.startswith('<g transform="translate(10.0,20.0) rotate(90.00)">') and g.endswith("</g>") and g.count("<rect") == 4


def test_a_seated_hamlet_draws_every_retirement_house_its_lots_laid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes H32 and plan D9: on the retirement form the house is a household's part, laid in its bundle off
    the back wall or a flank - every one drawn where it was laid, the count the lots' quota, never short."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads.retirement import retirement_quota, retirement_share
    from tests.hamletgen.test_homesteads import _no_tree, _toy_hamlet

    # the toy's bundles lay a bed or the well pocket where a flank door stands, and a corridor over its own parts is refused
    # since feature 287 M8 (`access.parts_clear`); the seating's count, not the parts, is under test here - nor the tree's
    monkeypatch.setattr(access_mod, "parts_clear", lambda *a: True)
    _no_tree(monkeypatch)
    s, plan = _toy_hamlet(12)
    s.pin_knob("family_form", "retirement_house")
    assert retirement_quota(s, 12) == {"retirement": retirement_share(s.seed)}
    stage_homesteads(s, plan)
    laid = [(h, f) for h in s.M["houses"] for f in h.get("fixtures") or () if f["kind"] == "retirement"]
    assert len(laid) == math.floor(12 * retirement_share(s.seed) + 0.5)
    n = retirement_houses(s, plan)
    assert n == len(laid) == s.M["meta"]["retirement_target"] == len(s.M["retirement_houses"])
    for r in s.M["retirement_houses"]:
        h = next(h for h in s.M["houses"] if [round(h["x"], 1), round(h["y"], 1)] == r["of"])
        assert math.hypot(r["x"] - h["x"], r["y"] - h["y"]) > h["h"] / 2 + r["h"] / 2, "a roof of its own"
    one = _toy_hamlet(10)[0]
    one.pin_knob("family_form", "one_roof")
    assert retirement_quota(one, 10) == {}


def test_a_laid_retirement_house_faces_off_the_wall_it_stands_by() -> None:
    from l7r.diagram.hamletgen.homesteads.retirement import retirement_face

    h = {"x": 100.0, "y": 100.0, "w": 40.0, "h": 28.0, "rot": 0.0}
    assert retirement_face(h, 100.0, 70.0) == 180.0 and retirement_face(h, 135.0, 100.0) == -90.0 and retirement_face(h, 65.0, 100.0) == 90.0


def test_a_seating_that_laid_no_retirement_house_draws_none() -> None:
    """Feature 444 T33 D7c: the seating's lots decide every retirement house - the search for a settlement seated without lots
    went, and a seating that laid none draws none (the lots' quota keeps at least one keeper where it can seat it)."""
    s, hs = _byre_village()
    s.pin_knob("family_form", "retirement_house")
    assert not any("fixtures" in h for h in hs)
    assert retirement_houses(s, None) == 0 and s.M["retirement_houses"] == []  # type: ignore[arg-type]
    assert s.M["meta"]["retirement_target"] == 0 and RETIREMENT_SHARE[0] <= s.M["meta"]["retirement_share"] <= RETIREMENT_SHARE[1]
