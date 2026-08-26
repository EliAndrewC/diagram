#!/usr/bin/env python3
"""Unit tests for citybudget.py - the budget-first city wall sizer (feature 009).

The two calibration anchors are the heart of the suite:
  - Tango (GM-accepted): its program must BACK-PREDICT the shipped wall within tolerance.
  - pre-feature Nagahara (GM-rejected, pinned in pool/regressions/): its program must price the
    city's required interior far enough below the fixture's measured enclosure to breach the
    over-enclosure tolerance - the empty-space defect must be arithmetic, not opinion.
"""

import json
import math
import os

import pytest

from l7r.diagram import citybudget
from l7r.diagram.citybudget import BudgetLine, CityProgram, budget_to_manifest, derive_wall, format_budget, plan_capital, plan_city

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the skill root; the tests live one level down in tests/


def _prog(**kw):
    kw.setdefault("population", 3000)
    return CityProgram(**kw)


# ---- inventory derivation (budgets.md Provincial city caste table) ------------------------


def test_inventory_splits_600_families_per_the_caste_table_at_pop_3000():
    b = plan_city(_prog())
    assert b.dwelling_target["families"] == {"servants": 120, "laborers": 240, "merchants": 150, "burakumin": 30, "samurai": 60}
    assert b.dwelling_target["packed"] == 540  # servants + laborers + merchants + burakumin
    assert b.dwelling_target["samurai_inwall"] == 40  # 2/3 of 60 (the rest live in extramural estates)


@pytest.mark.parametrize(
    "pop,families,packed,samurai_inwall",
    [
        (2000, 400, 360, 27),
        (3000, 600, 540, 40),
        (4000, 800, 720, 53),
    ],
)
def test_inventory_scales_linearly_across_the_canonical_band(pop, families, packed, samurai_inwall):
    b = plan_city(_prog(population=pop))
    assert sum(b.dwelling_target["families"].values()) == families
    assert b.dwelling_target["packed"] == packed
    assert b.dwelling_target["samurai_inwall"] == samurai_inwall


# ---- the budget lines sum to the required interior ----------------------------------------


@pytest.mark.parametrize("agri", [False, True])
@pytest.mark.parametrize("pop", [2000, 3000, 4000])
def test_lines_sum_exactly_to_required_interior(pop, agri):
    b = plan_city(_prog(population=pop, agricultural_district=agri))
    assert math.isclose(sum(ln.area_px2 for ln in b.lines), b.required_interior_px2, rel_tol=1e-9)


def test_every_line_carries_a_basis_and_a_label():
    b = plan_city(_prog(river=True, agricultural_district=True))
    for ln in b.lines:
        assert ln.label and ln.basis, ln


def test_water_line_is_labeled_for_the_program_kind():
    assert any("pond" in ln.label for ln in plan_city(_prog()).lines)
    assert any("canal" in ln.label for ln in plan_city(_prog(river=True)).lines)


# ---- the agricultural-district toggle (US3) ------------------------------------------------


# ---- wall derivation (N-gon geometry, not the smooth ellipse) ------------------------------


@pytest.mark.parametrize("nring", [20, 22])
@pytest.mark.parametrize("required", [400_000.0, 690_000.0])
def test_derived_wall_ngon_encloses_the_required_area(required, nring):
    w = derive_wall(required, aspect=0.93, nring=nring)
    ngon = 0.5 * nring * math.sin(2 * math.pi / nring) * w.rx * w.ry
    assert math.isclose(ngon, required, rel_tol=1e-9)
    assert math.isclose(w.interior_px2, required, rel_tol=1e-9)
    assert math.isclose(w.ry / w.rx, 0.93, rel_tol=1e-9)


def test_derived_wall_reports_a_real_perimeter():
    w = derive_wall(690_000.0, aspect=0.93, nring=20)
    # 20-gon perimeter of a ~487x453 ring is ~2,950 px = ~8,900 ft at 3 ft/px
    assert 8_000 < w.perimeter_px * 3 < 10_000


@pytest.mark.parametrize("aspect", [0.0, -1.0, 1.5])
def test_implausible_aspect_is_rejected(aspect):
    with pytest.raises(ValueError, match="aspect"):
        derive_wall(500_000.0, aspect=aspect)


def test_wall_that_cannot_fit_the_canvas_fails_loudly_with_the_numbers():
    with pytest.raises(ValueError) as ei:
        plan_city(_prog(agricultural_district=True), canvas=(900.0, 900.0))
    msg = str(ei.value)
    assert "900" in msg and "canvas" in msg.lower()


# ---- calibration anchors -------------------------------------------------------------------


def test_tango_program_back_predicts_the_shipped_wall():
    # Shipped Tango: RX,RY = 487,457 (22-vertex ring), agricultural district ON, pop 3000.
    b = plan_city(_prog(agricultural_district=True, aspect=457 / 487, nring=22))
    assert abs(b.wall.rx - 487) / 487 < 0.06
    assert abs(b.wall.ry - 457) / 457 < 0.06
    shipped_interior = 0.5 * 22 * math.sin(2 * math.pi / 22) * 487 * 457
    assert abs(b.required_interior_px2 - shipped_interior) / shipped_interior < 0.06


# ---- the shipped programs are PINNED (feature 016 regression net) ---------------------------
#
# Feature 016 moved the temple program out of the static CIVIC_PROGRAM tuple and onto CityProgram
# knobs so a Fox city can declare eight small precincts instead of two great ones. The knobs
# default to the values the tuple carried, so BOTH shipped cities must reprice bit-for-bit. These
# literals were captured from the pre-refactor code and are deliberately hard-coded rather than
# recomputed: a test that derives its expectation from the code it guards cannot catch a drift.

#: (label, count, area_px2) for every line plan_city emitted for the shipped programs, pre-016.
_TANGO_LINES_PRE_016 = [
    ("packed row housing (laborer/servant/merchant/burakumin)", 540, 372_600.0),
    ("samurai houses in-wall", 40, 99_200.0),
    ("governor's mansion (yamen)", 1, 17_730.0),
    ("six provincial ministries", 6, 7_980.0),
    ("temple precincts", 2, 16_250.0),
    ("minor civic (theater, flophouses, funerary, inspection, kura)", None, 17_440.0),
    ("shops, inns, stables", 21, 4_700.0),
    ("bell-and-drum tower", 1, 250.0),
    ("provincial martial hall + 1-2 private dojos", None, 2_200.0),
    ("brewery compound", 1, 800.0),
    ("trade works (dye yard, oil press, pawn court, 1-2 bathhouses, farrier)", None, 1_500.0),
    ("adept-monk houses by the temple precincts", 5, 3_450.0),
    ("pond", 1, 2_900.0),
    ("circulation (trunk + ring road + streets + alleys)", None, 49_089.743590),
    ("agricultural district (in-wall farms, declared reserve)", None, 105_192.307692),
]

_NAGAHARA_LINES_PRE_016 = [
    *[ln for ln in _TANGO_LINES_PRE_016 if ln[0] not in ("pond", "circulation (trunk + ring road + streets + alleys)", "agricultural district (in-wall farms, declared reserve)")],
    ("cargo canal + dock basin", 1, 2_900.0),
    ("circulation (trunk + ring road + streets + alleys)", None, 41_172.043011),
]


def _tango_program(**kw):
    """Tango's shipped program - pop 3000, agricultural district, 22-vertex ring."""
    return CityProgram(population=3000, agricultural_district=True, aspect=457 / 487, nring=22, **kw)


def _nagahara_program(**kw):
    """Nagahara's shipped program - pop 3000, river city, no agricultural district."""
    return CityProgram(population=3000, river=True, aspect=460 / 494, nring=20, **kw)


@pytest.mark.parametrize(
    "program,expected_lines,expected_rx,expected_ry,expected_required",
    [
        (_tango_program(), _TANGO_LINES_PRE_016, 491.063756, 460.813422, 701_282.051282),
        (_nagahara_program(), _NAGAHARA_LINES_PRE_016, 452.111512, 420.994525, 588_172.043011),
    ],
    ids=["tango", "nagahara"],
)
def test_shipped_city_programs_price_exactly_as_they_did_before_the_temple_knobs(program, expected_lines, expected_rx, expected_ry, expected_required):
    b = plan_city(program, canvas=(3200, 2700))
    assert [(ln.label, ln.count, pytest.approx(ln.area_px2, abs=1e-6)) for ln in b.lines] == expected_lines
    assert b.wall.rx == pytest.approx(expected_rx, abs=1e-6)
    assert b.wall.ry == pytest.approx(expected_ry, abs=1e-6)
    assert b.required_interior_px2 == pytest.approx(expected_required, abs=1e-6)


# ---- the temple program as declared knobs (feature 016) -------------------------------------


def _line(budget, label):
    return next(ln for ln in budget.lines if ln.label == label)


def test_the_default_temple_knobs_reproduce_the_retired_hard_coded_row():
    b = plan_city(_prog())
    temple = _line(b, "temple precincts")
    assert (temple.count, temple.area_px2) == (2, 16_250.0)  # the row CIVIC_PROGRAM used to carry
    assert _line(b, "adept-monk houses by the temple precincts").count == 5


def test_the_clergy_line_basis_records_the_derivation_not_just_the_total():
    monks = _line(plan_city(_prog(temple_precincts=8, monk_houses_per_precinct=6.0)), "adept-monk houses by the temple precincts")
    assert "8 temple precinct(s)" in monks.basis and "6 adept-monk households" in monks.basis


def test_an_extras_line_such_as_the_inari_uplift_survives_into_the_budget():
    uplift = BudgetLine("Inari precinct uplift", 1, 1_600.0, "the Fox Inari precinct stands slightly larger than its seven siblings")
    b = plan_city(_prog(temple_precincts=8, extras=(uplift,)))
    assert _line(b, "Inari precinct uplift") == uplift


def test_a_smaller_population_derives_a_smaller_ring():
    small = plan_city(_prog(population=2360, river=True))
    standard = plan_city(_prog(population=3000, river=True))
    assert small.wall.rx < standard.wall.rx and small.required_interior_px2 < standard.required_interior_px2


# ---- scale conversion ----------------------------------------------------------------------


def test_costs_convert_from_the_3ftpx_calibration_to_other_scales():
    at3 = plan_city(_prog())
    at1 = plan_city(_prog(ftpx=1))
    assert math.isclose(at1.required_interior_px2, at3.required_interior_px2 * 9, rel_tol=1e-9)
    assert math.isclose(at1.wall.rx, at3.wall.rx * 3, rel_tol=1e-9)


# ---- manifest + report surfaces ------------------------------------------------------------


def test_manifest_round_trips_as_plain_json():
    b = plan_city(_prog(river=True, agricultural_district=True))
    d = budget_to_manifest(b)
    j = json.loads(json.dumps(d))
    assert j["required_interior_px2"] == pytest.approx(b.required_interior_px2)
    assert j["interior_px2"] == pytest.approx(b.wall.interior_px2)
    assert j["flags"] == {"river": True, "agricultural_district": True}
    assert j["wall"]["rx"] == pytest.approx(b.wall.rx)
    assert len(j["lines"]) == len(b.lines) and all(ln["basis"] for ln in j["lines"])
    assert j["dwelling_target"]["packed"] == 540


def test_report_prints_every_line_with_its_basis_and_the_wall():
    b = plan_city(_prog(agricultural_district=True))
    rep = format_budget(b)
    for ln in b.lines:
        assert ln.label in rep
    assert "basis" in rep or all(ln.basis in rep for ln in b.lines)
    assert f"{b.wall.rx:.0f}" in rep and "required" in rep.lower()


# ---- CLI -----------------------------------------------------------------------------------


# ---- THE DOMAIN-CAPITAL TIER (feature 018) ---------------------------------------------------
#
# A capital gets a PARALLEL entry point, not a widened band, so the provincial path above runs no
# new branches. These tests therefore also guard a negative: nothing here may move a shipped city.


def _cap(**kw):
    return citybudget.CapitalProgram(**kw)


def test_capital_lines_sum_exactly_to_the_required_interior():
    b = plan_capital(_cap(river=True))
    assert sum(ln.area_px2 for ln in b.lines) == pytest.approx(b.required_interior_px2, abs=1e-6)


def test_every_capital_line_carries_a_label_and_a_basis():
    for ln in plan_capital(_cap(river=True)).lines:
        assert ln.label.strip()
        assert ln.basis.strip()


def test_the_castle_is_its_own_line_and_the_samurai_are_three_separate_housing_lines():
    """US2 AS-2: the report must not hide the castle in a civic total, nor flatten the rank bands."""
    labels = [ln.label for ln in plan_capital(_cap()).lines]
    assert any(lb.startswith("the castle") for lb in labels)
    assert sum(1 for lb in labels if "in-wall (Rank" in lb) == 3


def test_a_capital_wall_too_large_for_its_canvas_fails_loudly_with_the_numbers():
    with pytest.raises(ValueError, match="never clamp the wall"):
        plan_capital(_cap(river=True), canvas=(1200, 1000))


# ---- the shipped capital program is PINNED the day it lands ---------------------------------
#
# Same discipline the provincial tier earned the hard way: CAPITAL_CIVIC_PROGRAM's third field is
# a ROW TOTAL, not a per-unit cost, and reading it the other way is how feature 016 nearly doubled
# every city's temple ground. These literals are deliberately hard-coded - a test that derives its
# expectation from the code it guards cannot catch a drift - and they also pin LINE ORDER, which
# is manifest bytes.

_CAPITAL_LINES_AS_SHIPPED = [
    ('packed row housing IN-WALL (laborer/servant/merchant/burakumin)', 2100, pytest.approx(1995000.0, abs=1e-6)),
    ('packed row housing SUBURBAN (kashi wharf belt + guan-xiang gate wards)', 60, pytest.approx(0.0, abs=1e-6)),
    ('the castle (enceinte: baileys + moats; interior implied)', 1, pytest.approx(598000.0, abs=1e-6)),
    ('samurai walled yashiki in-wall (Ranks 8-12)', 53, pytest.approx(219950.0, abs=1e-6)),
    ('samurai detached houses in-wall (Ranks 5-7)', 133, pytest.approx(329840.0, abs=1e-6)),
    ('retainer terraces in-wall (Ranks 1-4)', 79, pytest.approx(52140.0, abs=1e-6)),
    ('six domain ministries + government ward', 6, pytest.approx(16000.0, abs=1e-6)),
    ("House Chancellery (the domain's 5-10 lineage representatives)", 1, pytest.approx(2000.0, abs=1e-6)),
    ("Imperial Magistrate's compound (foreign; houses its own 12 households)", 1, pytest.approx(8000.0, abs=1e-6)),
    ("the Emperor's granaries", 1, pytest.approx(3000.0, abs=1e-6)),
    ('domain school (hanko)', 1, pytest.approx(4000.0, abs=1e-6)),
    ("domain granary + wharf brokers' row", None, pytest.approx(12000.0, abs=1e-6)),
    ('domain martial hall + rolled private dojos', None, pytest.approx(4400.0, abs=1e-6)),
    ('aqueduct in-wall works (the conduit itself is buried)', None, pytest.approx(500.0, abs=1e-6)),
    ('minor civic (theaters, flophouses, funerary, inspection, kura)', None, pytest.approx(30000.0, abs=1e-6)),
    ('shops, inns, stables', 60, pytest.approx(13400.0, abs=1e-6)),
    ('bell-and-drum tower (sounds the kido curfew)', 1, pytest.approx(250.0, abs=1e-6)),
    ('brewery compounds', 2, pytest.approx(1600.0, abs=1e-6)),
    ('trade works (dye yards, oil presses, pawn courts, bathhouses, farriers)', None, pytest.approx(3000.0, abs=1e-6)),
    ('sovereign temple precincts', 2, pytest.approx(32500.0, abs=1e-6)),
    ('adept-monk houses by the temple precincts', 5, pytest.approx(3450.0, abs=1e-6)),
    ('cargo canal + dock basin', 1, pytest.approx(5800.0, abs=1e-6)),
    ('circulation (trunk + ring road + streets + alleys)', None, pytest.approx(588499.4117647059, abs=1e-6)),
]


def test_the_shipped_capital_program_prices_and_orders_exactly_as_recorded():
    b = plan_capital(_cap(river=True), canvas=(3200, 2700))
    assert [(ln.label, ln.count, pytest.approx(ln.area_px2, abs=1e-6)) for ln in b.lines] == _CAPITAL_LINES_AS_SHIPPED
    assert b.required_interior_px2 == pytest.approx(3923329.411764706, abs=1e-6)  # packed-tight capital: C 950, CIRC 0.15, wharf-hamlet extramural (GM 2026-08-10)
    assert b.wall.rx == pytest.approx(1168.408561745735, abs=1e-6)  # model minimum; the drawn 1110x1150 at (1400,1313) stands within tolerance
    assert b.wall.ry == pytest.approx(1086.6199624235335, abs=1e-6)


# ---- the variant knobs are validated at DECLARATION time (US3) --------------------------------


@pytest.mark.parametrize(
    "kw,match",
    [
        ({"castle_seat": "edge"}, "requires river=True"),
        ({"castle_seat": "keep"}, "is not one of"),
        ({"imperial_granary_seat": "castle"}, "is not one of"),
        ({"castle_px2": 40_000.0}, "outside the documented band"),
        ({"castle_px2": 9_000_000.0}, "outside the documented band"),
        ({"agricultural_district": True}, "no agricultural district"),
        ({"aspect": 0.0}, "aspect must be in"),
        ({"suburb_packed_frac": 0.9}, "outside"),
    ],
)
def test_an_illegal_capital_declaration_is_refused_when_it_is_constructed(kw, match):
    with pytest.raises(ValueError, match=match):
        _cap(**kw)


@pytest.mark.parametrize(
    "kw",
    [
        {"castle_seat": "edge", "river": True},
        {"castle_seat": "ring"},
        {"castle_seat": "ring", "river": True},
        {"imperial_granary_seat": "wharf"},
        {"imperial_granary_seat": "magistrate"},
    ],
)
def test_a_legal_capital_declaration_is_accepted(kw):
    assert plan_capital(_cap(**kw)).wall.rx > 0


def test_capital_costs_convert_from_the_3ftpx_calibration_to_other_scales():
    at3 = plan_capital(_cap()).required_interior_px2
    at6 = plan_capital(_cap(ftpx=6)).required_interior_px2
    assert at6 == pytest.approx(at3 / 4, rel=1e-9)


def test_the_capital_report_prints_every_line_with_its_basis_and_the_wall():
    text = format_budget(plan_capital(_cap(river=True)))
    assert "SPACE BUDGET - population 12360" in text
    for ln in plan_capital(_cap(river=True)).lines:
        assert ln.label in text
    assert "derived wall" in text


# ---- the CLI grows a --tier, and the provincial default is untouched -------------------------
