"""Unit tests for the pipeline and the CLI that drives it (`hamletgen/driver.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

from l7r.diagram import hamletgen as hg

from ._builders import a_plan


def test_the_report_line_names_the_map_and_its_verdict() -> None:
    plan = a_plan()
    assert "OK" in hg.Report(plan=plan, failures=[]).line()
    bad = hg.Report(plan=plan, failures=["a_check", "another"])
    assert not bad.ok and "FAIL" in bad.line() and "a_check" in bad.line()


_PIN = {22: frozenset({"field_ringed"}), 24: frozenset({"paddy_bunds_clear_the_supply_channels"})}


def _cohort(**seeds: list[str]) -> list[hg.Report]:
    """Reports keyed `s<seed>`, each failing whatever the caller names (empty = it passed)."""
    return [hg.Report(plan=hg.plan_site(hg.HamletSpec(name="T", seed=int(s[1:]), households=12, down_deg=90.0, windward="N")), failures=f) for s, f in sorted(seeds.items())]


def test_a_cohort_matching_its_pinned_baseline_is_clean() -> None:
    """The pin is what makes `22/24 passed` mean something: the RATE is identical whether the two
    failures are the expected ones or two fresh regressions."""
    lines, clean = hg.baseline_verdict(_cohort(s21=[], s22=["field_ringed[cohort-22-paddies]"], s23=[], s24=["paddy_bunds_clear_the_supply_channels"]), _PIN)
    assert clean and "NO NEW REGRESSIONS" in lines[0]


def test_the_instance_suffix_is_not_part_of_a_check_identity() -> None:
    # `field_ringed[cohort-22-paddies]` and `field_ringed[whatever]` are the same rule; the suffix
    # carries the map's own feature ids and would make the pin unmatchable
    _, clean = hg.baseline_verdict(_cohort(s22=["field_ringed[some-other-field]"], s24=["paddy_bunds_clear_the_supply_channels"]), _PIN)
    assert clean


def test_a_failure_on_an_unpinned_seed_is_a_regression() -> None:
    lines, clean = hg.baseline_verdict(_cohort(s9=["paddy_plot_seams_shared"], s22=["field_ringed"], s24=["paddy_bunds_clear_the_supply_channels"]), _PIN)
    assert not clean
    assert any("REGRESSION seed 9" in line and "paddy_plot_seams_shared" in line for line in lines)
    assert any("Principle XIII" in line for line in lines), "the message must name the rule that blocks the merge"


def test_a_NEW_check_on_an_ALREADY_failing_seed_is_still_a_regression() -> None:
    """The subtle one: seed 22 was already failing, so the pass RATE does not move at all."""
    lines, clean = hg.baseline_verdict(_cohort(s22=["field_ringed", "paddy_plot_seams_shared"], s24=["paddy_bunds_clear_the_supply_channels"]), _PIN)
    assert not clean
    assert any("REGRESSION seed 22" in line and "paddy_plot_seams_shared" in line for line in lines)


def test_a_pinned_failure_that_starts_PASSING_fails_too_so_the_pin_ratchets_down() -> None:
    """Same discipline as `waivers_are_live`: a baseline nobody maintains stops being a baseline,
    and a pin that only ever loosens hides the next real regression on that seed."""
    lines, clean = hg.baseline_verdict(_cohort(s24=["paddy_bunds_clear_the_supply_channels"]), _PIN)
    assert not clean
    assert any("STALE PIN seed 22" in line and "COHORT_BASELINE" in line for line in lines), "it must name the edit to make"


def _as_pinned() -> list[hg.Report]:
    """Reports reproducing exactly today's `COHORT_BASELINE` - built FROM the pin, so this test
    keeps testing the WIRING rather than freezing whatever the baseline happens to be."""
    return [
        hg.Report(plan=hg.plan_site(hg.HamletSpec(name="T", seed=seed, households=12, down_deg=90.0, windward="N")), failures=sorted(checks))
        for seed, checks in sorted(hg.driver.COHORT_BASELINE.items())
    ]
