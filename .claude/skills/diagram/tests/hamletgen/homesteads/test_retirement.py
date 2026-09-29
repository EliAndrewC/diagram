"""`hamletgen/homesteads/retirement.py` on stub settlements - the retirement house and its knob (269 E8, B42; settlements/035)."""

from __future__ import annotations

import math

from l7r.diagram.hamletgen.homesteads.retirement import (
    FAMILY_FORMS,
    RETIREMENT_FT,
    RETIREMENT_SHARE,
    retirement_glyph,
    retirement_houses,
    retirement_seats,
    turned_box,
)
from l7r.diagram.settlement._knobs import KNOBS
from tests.settlement._builders import _byre_village, _crop_settlement


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


def test_a_retirement_settlement_seats_its_share_each_house_off_its_own_farmhouse() -> None:
    s, hs = _byre_village()
    s.pin_knob("family_form", "retirement_house")
    n = retirement_houses(s, None)  # type: ignore[arg-type]
    meta = s.M["meta"]
    assert RETIREMENT_SHARE[0] <= meta["retirement_share"] <= RETIREMENT_SHARE[1]
    assert n == meta["retirement_houses"] == meta["retirement_target"] == max(1, round(5 * meta["retirement_share"])) == len(s.M["retirement_houses"])
    owners = {(h["x"], h["y"]): h for h in hs}
    for r in s.M["retirement_houses"]:
        assert {"x", "y", "w", "h", "rot", "of"} <= set(r), "the geometry is complete when appended"
        h = owners[tuple(r["of"])]
        assert (r["w"], r["h"]) == (s.px(RETIREMENT_FT[0]), s.px(RETIREMENT_FT[1]))
        gap = math.hypot(r["x"] - h["x"], r["y"] - h["y"])
        assert gap > h["h"] / 2 + r["h"] / 2, "a roof of its own, off the farmhouse wall"
        assert r["y"] < h["y"] or abs(r["y"] - h["y"]) < 1.0, "behind the house or on a flank - never in the front yard"
    assert len(s.M["houses"]) == 5, "not a household: the houses registry is untouched"
    assert sum(1 for c in s.out_cls if c == "retirement house") == n
    assert len(s.placed) == 5 + n, "each one reserves its ground for the placers after it"


def test_a_homestead_with_no_room_passes_its_turn_and_a_hamlet_with_no_houses_asks_for_none() -> None:
    s, _hs = _byre_village()
    s.field_polys.append([(0.0, 0.0), (2000.0, 0.0), (2000.0, 1500.0), (0.0, 1500.0)])  # every seat is basin
    s.pin_knob("family_form", "retirement_house")
    assert retirement_houses(s, None) == 0 and s.M["meta"]["retirement_target"] >= 1  # type: ignore[arg-type]
    empty = _crop_settlement()
    empty.pin_knob("family_form", "retirement_house")
    assert retirement_houses(empty, None) == 0 and empty.M["meta"]["retirement_target"] == 0  # type: ignore[arg-type]


def test_the_seats_ring_the_back_and_flanks_turned_with_the_house() -> None:
    h = {"x": 100.0, "y": 100.0, "w": 40.0, "h": 28.0, "rot": 0.0}
    seats = retirement_seats(h, 18.0, 15.0, (6.0, 12.0), 0)
    assert len(seats) == 6
    back, east, west = seats[:3]
    assert back == (100.0, 100.0 - (14.0 + 6.0 + 7.5), 180.0)
    assert east == (100.0 + (20.0 + 6.0 + 7.5), 100.0, -90.0) and west == (100.0 - (20.0 + 6.0 + 7.5), 100.0, 90.0)
    assert retirement_seats(h, 18.0, 15.0, (6.0,), 1)[0] == east, "the turn starts the ring on another side"
    turned = retirement_seats({**h, "rot": 90.0}, 18.0, 15.0, (6.0,), 0)[0]
    assert abs(turned[0] - (100.0 + 27.5)) < 1e-9 and abs(turned[1] - 100.0) < 1e-9 and turned[2] == 270.0
    for x, y, rot in seats:  # the door (local +y) opens away from the farmhouse
        dx, dy = -math.sin(math.radians(rot)), math.cos(math.radians(rot))
        assert dx * (x - 100.0) + dy * (y - 100.0) > 0


def test_the_box_turns_and_the_glyph_draws_a_door() -> None:
    assert all(abs(a - b) < 1e-9 for a, b in zip(turned_box(18.0, 15.0, 180.0), (18.0, 15.0), strict=True))
    w, h = turned_box(18.0, 15.0, 90.0)
    assert abs(w - 15.0) < 1e-9 and abs(h - 18.0) < 1e-9
    g = retirement_glyph(10.0, 20.0, 18.0, 15.0, 90.0)
    assert g.startswith('<g transform="translate(10.0,20.0) rotate(90.00)">') and g.endswith("</g>") and g.count("<rect") == 4


def test_a_seated_hamlet_draws_every_retirement_house_its_lots_laid() -> None:
    """Feature 287, homes H32 and plan D9: on the retirement form the house is a household's part, laid in its bundle off
    the back wall or a flank - every one drawn where it was laid, the count the lots' quota, never short."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads.retirement import retirement_quota, retirement_share
    from tests.hamletgen.test_homesteads import _toy_hamlet

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
