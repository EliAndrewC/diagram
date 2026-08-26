"""tier city tests split out of `tests.test_citybudget` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import json
import math
import os

import pytest

from l7r.diagram import check_village, citybudget
from l7r.diagram.citybudget import BudgetLine, budget_to_manifest, plan_capital, plan_city
from tests.test_citybudget import HERE, _cap, _line, _prog


@pytest.mark.parametrize("pop", [1999, 4001, 0, 12000])
@pytest.mark.tiers("city")
def test_population_outside_the_provincial_band_is_rejected(pop):
    with pytest.raises(ValueError, match="2000"):
        plan_city(_prog(population=pop))


@pytest.mark.tiers("city")
def test_circulation_is_the_declared_fraction_of_the_required_interior():
    b = plan_city(_prog())
    circ = next(ln for ln in b.lines if "circulation" in ln.label)
    assert math.isclose(circ.area_px2, citybudget.CIRC_FRAC * b.required_interior_px2, rel_tol=1e-9)
    assert circ.count is None


@pytest.mark.tiers("city")
def test_extras_are_itemized_and_priced_into_the_total():
    plain = plan_city(_prog())
    extra = plan_city(_prog(extras=(BudgetLine("drill ground", None, 12000.0, "GM program"),)))
    assert any(ln.label == "drill ground" for ln in extra.lines)
    # the extra inflates the pre-circulation subtotal, so the required interior grows by extra/(1-f)
    assert math.isclose(extra.required_interior_px2 - plain.required_interior_px2, 12000.0 / (1 - citybudget.CIRC_FRAC), rel_tol=1e-9)


@pytest.mark.parametrize("pop", [2000, 3000, 4000])
@pytest.mark.tiers("city")
def test_agri_toggle_adds_exactly_its_itemized_line_and_grows_the_wall(pop):
    off = plan_city(_prog(population=pop))
    on = plan_city(_prog(population=pop, agricultural_district=True))
    agri = next(ln for ln in on.lines if "agricultural" in ln.label)
    assert not any("agricultural" in ln.label for ln in off.lines)
    assert math.isclose(agri.area_px2, citybudget.AGRI_FRAC * on.required_interior_px2, rel_tol=1e-9)
    # same program otherwise: the non-agri, non-circulation lines are identical
    fixed_off = sum(ln.area_px2 for ln in off.lines if "circulation" not in ln.label)
    fixed_on = sum(ln.area_px2 for ln in on.lines if "circulation" not in ln.label and "agricultural" not in ln.label)
    assert math.isclose(fixed_off, fixed_on, rel_tol=1e-9)
    assert on.wall.rx > off.wall.rx and on.wall.ry > off.wall.ry


@pytest.mark.tiers("city")
def test_canvas_with_room_is_accepted():
    b = plan_city(_prog(), canvas=(3200.0, 2700.0))
    assert 2 * (b.wall.rx + citybudget.WALL_MARGIN_PX) <= 3200


@pytest.mark.tiers("city")
def test_pre_feature_nagahara_is_priced_as_over_enclosed():
    # The pinned GM-rejected map: its program (pop 3000, river city, NO agricultural district)
    # must price a required interior that its actual wall over-encloses beyond the check tolerance.
    with open(os.path.join(HERE, "pool", "regressions", "city_budget_fires_on_the_too_empty_nagahara.json")) as fh:
        M = json.load(fh)
    measured = check_village.poly_area(M["wall"])
    b = plan_city(_prog(river=True, aspect=460 / 494, nring=20))
    assert measured > b.required_interior_px2 * (1 + check_village.BUDGET_TOL_OVER)


@pytest.mark.tiers("city")
def test_the_temple_line_keeps_its_place_in_the_civic_sequence():
    """Line ORDER is manifest bytes: the knob-driven temple row must land exactly where the
    hard-coded CIVIC_PROGRAM row sat, directly after the ministries."""
    labels = [ln.label for ln in plan_city(_prog()).lines]
    assert labels.index("temple precincts") == labels.index(citybudget.MINISTRIES_LABEL) + 1


@pytest.mark.tiers("city")
def test_a_fox_eight_precinct_program_prices_eight_precincts_and_scales_the_clergy_line():
    """Minami's program: eight modest precincts, each well under the 8,125 px^2 default, with
    hereditary temple families living OUT (research/religion-and-death.md finding 3)."""
    b = plan_city(_prog(population=2360, river=True, temple_precincts=8, temple_precinct_px2=3_400.0, monk_houses_per_precinct=6.0))
    temple = _line(b, "temple precincts")
    assert temple.count == 8
    assert temple.area_px2 == pytest.approx(8 * 3_400.0)
    assert temple.area_px2 / 8 < citybudget.TEMPLE_PRECINCT_PX2  # every precinct smaller than a normal complex
    monks = _line(b, "adept-monk houses by the temple precincts")
    assert monks.count == 48  # 8 precincts x 6 households, NOT the retired constant 5
    assert monks.area_px2 == pytest.approx(48 * citybudget.C_PACKED)


@pytest.mark.tiers("city")
def test_cli_plan_prints_the_report(capsys):
    rc = citybudget.main(["--plan", "--population", "3000", "--river", "--canvas", "3200x2700"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "required" in out.lower() and "canal" in out


@pytest.mark.tiers("city")
def test_cli_agri_flag_adds_the_district_line(capsys):
    rc = citybudget.main(["--plan", "--population", "3000", "--agri"])
    assert rc == 0
    assert "agricultural" in capsys.readouterr().out


@pytest.mark.tiers("city")
def test_cli_reports_errors_on_stderr_with_exit_1(capsys):
    rc = citybudget.main(["--plan", "--population", "99"])
    assert rc == 1
    assert "2000" in capsys.readouterr().err


@pytest.mark.tiers("city")
def test_the_new_ground_costs_sit_in_their_documented_ranges_and_order():
    """A walled compound costs more ground than a detached house, which costs more than a terrace.

    The one relationship that looks wrong and is not: C_TERRACE sits just BELOW C_PACKED. That is
    because C_PACKED is the caste-WEIGHTED average of the packed castes and is pulled up by
    merchant houses (~200 px^2 footprint, against a laborer's ~99), so a bare laborer row house is
    only ~550 gross. A retainer terrace is roomier than a laborer's row and tighter than the
    merchant-inflated average - and it is already generous against the historical anchor, since
    Shibata's ashigaru-nagaya gave each household 378 sq ft to our laborer row's 891.
    """
    assert 3_500.0 <= citybudget.C_YASHIKI <= 5_000.0
    assert 500.0 <= citybudget.C_TERRACE <= 900.0
    assert citybudget.C_YASHIKI > citybudget.C_SPACED > citybudget.C_TERRACE
    assert 500.0 < citybudget.C_TERRACE < citybudget.C_PACKED


@pytest.mark.tiers("capital", "city")
def test_the_capital_caste_table_matches_budgets_md_and_sums_to_the_declared_population():
    fam = citybudget.CAPITAL_FAMILIES
    assert fam == {"servants": 480, "laborers": 960, "merchants": 600, "burakumin": 120, "samurai": 312}
    assert "farmers" not in fam  # a capital walls its farmland out
    assert sum(fam.values()) * citybudget.HOUSEHOLD == citybudget.CAPITAL_POP


@pytest.mark.tiers("capital", "city")
def test_the_rank_bands_sum_to_the_working_cohort_and_invert_the_provincial_mix():
    """budgets.md's capital column is 70% senior / 30% junior - the INVERSE of a provincial
    city's 27/73 - so walled compounds are the majority texture, not a minority."""
    bands = citybudget.CAPITAL_RANK_BANDS
    working = sum(sum(v) for v in bands.values())
    assert working == 800
    senior = (sum(bands["yashiki"]) + sum(bands["detached"])) / working
    assert senior == pytest.approx(0.70, abs=0.01)
    assert sum(bands["terrace"]) / working == pytest.approx(0.30, abs=0.01)


@pytest.mark.tiers("capital", "city")
def test_a_capital_houses_more_of_its_samurai_in_wall_than_a_provincial_city():
    assert citybudget.CAPITAL_SAMURAI_INWALL_FRAC > citybudget.SAMURAI_INWALL_FRAC


@pytest.mark.parametrize("pop", [8_999, 16_001, 3_000, 40_000])
@pytest.mark.tiers("capital")
def test_population_outside_the_capital_band_is_rejected(pop):
    with pytest.raises(ValueError, match="domain-capital band"):
        _cap(population=pop)


@pytest.mark.tiers("capital", "city")
def test_the_samurai_cohort_splits_in_wall_then_by_rank_band_and_the_three_sum_exactly():
    b = plan_capital(_cap())
    t = b.dwelling_target
    assert t["samurai_inwall"] == round(citybudget.CAPITAL_FAMILIES["samurai"] * citybudget.CAPITAL_SAMURAI_INWALL_FRAC)
    assert t["samurai_yashiki"] + t["samurai_detached"] + t["samurai_terrace"] == t["samurai_inwall"]
    assert t["dwellings"] == citybudget.CAPITAL_POP / citybudget.HOUSEHOLD


@pytest.mark.tiers("city")
def test_capital_circulation_is_the_declared_fraction_of_the_interior_not_of_the_subtotal():
    b = plan_capital(_cap())
    circ = _line(b, "circulation (trunk + ring road + streets + alleys)")
    assert circ.area_px2 == pytest.approx(b.required_interior_px2 * citybudget.CIRC_FRAC_CAPITAL, abs=1e-6)  # the CAPITAL fraction (021): measured trunk fabric ~20%, not the provincial 7%


@pytest.mark.tiers("city")
def test_the_canonical_capital_fits_the_standard_canvas():
    """SC-002: adopting the tier forces no canvas change."""
    b = plan_capital(_cap(river=True), canvas=(3200, 2700))
    assert 2 * (b.wall.rx + citybudget.WALL_MARGIN_PX) <= 3200
    assert 2 * (b.wall.ry + citybudget.WALL_MARGIN_PX) <= 2700


@pytest.mark.tiers("capital", "city")
def test_the_capital_civic_rows_are_row_totals_not_per_unit_costs():
    """The six domain ministries are one row TOTAL for all six, exactly as the provincial six are."""
    row = next(r for r in citybudget.CAPITAL_CIVIC_PROGRAM if r[0].startswith("six domain ministries"))
    assert row[1] == 6
    ministries = _line(plan_capital(_cap()), row[0])
    assert ministries.area_px2 == pytest.approx(row[2], abs=1e-6)


@pytest.mark.tiers("city")
def test_a_declared_castle_reprices_the_wall_and_records_its_hectares_in_the_basis():
    small = plan_capital(_cap(castle_px2=citybudget.CASTLE_PX2))
    grand = plan_capital(_cap(castle_px2=citybudget.CASTLE_PX2 * 3))
    assert grand.wall.rx > small.wall.rx
    assert "ha" in _line(grand, "the castle (enceinte: baileys + moats; interior implied)").basis


@pytest.mark.tiers("city")
def test_the_capital_manifest_round_trips_as_plain_json_and_adds_no_new_top_level_keys():
    """budget_to_manifest's SHAPE is manifest bytes - a new key would dirty every shipped city."""
    cap = json.loads(json.dumps(budget_to_manifest(plan_capital(_cap(river=True)))))
    prov = json.loads(json.dumps(budget_to_manifest(plan_city(_prog()))))
    assert set(cap) == set(prov)
    assert cap["dwelling_target"]["samurai_yashiki"] == 53


@pytest.mark.tiers("capital", "city")
def test_cli_plans_a_capital_when_asked(capsys):
    assert citybudget.main(["--plan", "--tier", "capital", "--population", "12360", "--river"]) == 0
    out = capsys.readouterr().out
    assert "the castle" in out and "retainer terraces" in out


@pytest.mark.tiers("city")
def test_cli_defaults_to_the_provincial_tier(capsys):
    assert citybudget.main(["--plan", "--population", "3000"]) == 0
    assert "governor's mansion" in capsys.readouterr().out


@pytest.mark.tiers("capital", "city")
def test_cli_refuses_an_agricultural_district_at_capital_tier_rather_than_ignoring_it(capsys):
    assert citybudget.main(["--plan", "--tier", "capital", "--population", "12360", "--agri"]) == 1
    assert "walls its farms out" in capsys.readouterr().err


@pytest.mark.tiers("capital", "city")
def test_cli_reports_a_capital_band_error_on_stderr(capsys):
    assert citybudget.main(["--plan", "--tier", "capital", "--population", "3000"]) == 1
    assert "domain-capital band" in capsys.readouterr().err


@pytest.mark.tiers("capital", "city")
def test_cli_accepts_the_capital_knobs(capsys):
    assert citybudget.main(["--plan", "--tier", "capital", "--population", "12360", "--river", "--castle-seat", "edge", "--granary-seat", "wharf"]) == 0
    assert "seat=edge" in capsys.readouterr().out
