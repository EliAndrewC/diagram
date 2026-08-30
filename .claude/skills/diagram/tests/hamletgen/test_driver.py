"""Unit tests for the pipeline and the CLI that drives it (`hamletgen/driver.py`).

Split from test_hamletgen.py by feature 111; test bodies verbatim. See hamletgen/CLAUDE.md.
"""

import pytest

from l7r.diagram import hamletgen as hg

from ._builders import a_plan


def test_the_report_line_names_the_map_and_its_verdict() -> None:
    plan = a_plan()
    assert "OK" in hg.Report(plan=plan, failures=[]).line()
    bad = hg.Report(plan=plan, failures=["a_check", "another"])
    assert not bad.ok and "FAIL" in bad.line() and "a_check" in bad.line()


def test_the_report_line_attributes_the_map_to_its_roll() -> None:
    """Feature 133 T33 (GM 2026-08-27): a re-rolled map says so - attempt four shipped with a reversed
    connector on T31 and nothing on the sheet or in the report attributed it."""
    plan = a_plan()
    first = hg.Report(plan=plan, failures=[]).line()
    assert "attempt 1" in first and "re-rolled" not in first
    fourth = hg.Report(plan=plan, failures=[], attempt=4, rerolled_after=["farmhouses_reach_a_way"] * 3).line()
    assert "attempt 4 (re-rolled after: farmhouses_reach_a_way)" in fourth


_PIN = {24: frozenset({"paddy_bunds_clear_the_supply_channels"})}


def _cohort(**seeds: list[str]) -> list[hg.Report]:
    """Reports keyed `s<seed>`, each failing whatever the caller names (empty = it passed)."""
    return [hg.Report(plan=hg.plan_site(hg.HamletSpec(name="T", seed=int(s[1:]), households=12, down_deg=90.0, windward="N")), failures=f) for s, f in sorted(seeds.items())]


def test_a_pinned_failure_that_starts_PASSING_fails_too_so_the_pin_ratchets_down() -> None:
    """Same discipline as `waivers_are_live`: a baseline nobody maintains stops being a baseline,
    and a pin that only ever loosens hides the next real regression on that seed."""
    pin = {22: frozenset({"some_check"}), 24: frozenset({"paddy_bunds_clear_the_supply_channels"})}  # a synthetic two-seed pin: the LOGIC under test, not today's baseline
    lines, clean = hg.baseline_verdict(_cohort(s24=["paddy_bunds_clear_the_supply_channels"]), pin)
    assert not clean
    assert any("STALE PIN seed 22" in line and "COHORT_BASELINE" in line for line in lines), "it must name the edit to make"


def _as_pinned() -> list[hg.Report]:
    """Reports reproducing exactly today's `COHORT_BASELINE` - built FROM the pin, so this test
    keeps testing the WIRING rather than freezing whatever the baseline happens to be."""
    return [
        hg.Report(plan=hg.plan_site(hg.HamletSpec(name="T", seed=seed, households=12, down_deg=90.0, windward="N")), failures=sorted(checks))
        for seed, checks in sorted(hg.driver.COHORT_BASELINE.items())
    ]


# THE STUBBED CLI TESTS (feature 135 T11, GM 2026-08-27). These carried `rolls_map` and lived in the gate tree
# because the marker guard matches the CALL (`hg.main`, `hg.cohort`) - but every one of them stubs `cohort` or
# `generate` first and rolls nothing; measured at milliseconds. The guard now reads the stub, so they are quick.


def test_the_cli_batch_mode_returns_nonzero_when_a_member_fails(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    """The batch exit code is the experiment's pass/fail signal, so it has to be real."""
    monkeypatch.setattr(hg.driver, "cohort", lambda n, first_seed=1, jobs=None: [hg.Report(plan=a_plan(), failures=["boom"])])
    assert hg.main(["--batch", "1"]) == 1
    assert "0/1 passed" in capsys.readouterr().out


def test_the_cli_batch_mode_returns_zero_when_every_member_passes(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(hg.driver, "cohort", lambda n, first_seed=1, jobs=None: [hg.Report(plan=a_plan(), failures=[])])
    assert hg.main(["--batch", "1"]) == 0
    assert "1/1 passed" in capsys.readouterr().out


def test_the_canonical_cohort_is_judged_against_the_pin_not_the_rate(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    """`--batch 24` from seed 1 exits ZERO on its known failures - the steady state is success, and
    only a change from it is a failure. Before the pin this exact run exited 1, which meant the
    signal everyone read was a rate that cannot distinguish two expected failures from two new ones."""
    monkeypatch.setattr(hg.driver, "cohort", lambda n, first_seed=1, jobs=None: _as_pinned())
    assert hg.main(["--batch", str(hg.driver.COHORT_BASELINE_SIZE)]) == 0
    assert "NO NEW REGRESSIONS" in capsys.readouterr().out


def test_the_canonical_cohort_fails_on_a_seed_the_pin_does_not_cover(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    extra = hg.Report(plan=hg.plan_site(hg.HamletSpec(name="T", seed=999, households=12, down_deg=90.0, windward="N")), failures=["something_new"])
    monkeypatch.setattr(hg.driver, "cohort", lambda n, first_seed=1, jobs=None: [*_as_pinned(), extra])
    assert hg.main(["--batch", str(hg.driver.COHORT_BASELINE_SIZE)]) == 1
    assert "REGRESSION seed 999" in capsys.readouterr().out


def test_a_non_canonical_range_says_it_has_no_pin(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    """A held-out or ad-hoc range must NOT be judged against the fitted cohort's baseline, and must
    say so rather than implying it was checked."""
    monkeypatch.setattr(hg.driver, "cohort", lambda n, first_seed=1, jobs=None: [hg.Report(plan=a_plan(), failures=[])])
    assert hg.main(["--batch", "1"]) == 0
    assert "no pinned baseline for this range" in capsys.readouterr().out


def test_the_cli_returns_nonzero_for_a_failing_single_map(monkeypatch, capsys) -> None:
    monkeypatch.setattr(hg.driver, "generate", lambda spec, out_base=None, render=True: hg.Report(plan=a_plan(), failures=["boom"]))
    assert hg.main(["--name", "X"]) == 1
    assert "boom" in capsys.readouterr().out


def test_cohort_derives_each_spec_and_can_be_forced_serial(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`jobs=1` is the path an in-gate caller wants (a pytest worker that spawns its own pool
    competes with the other 21), and the spec derivation is the same on either path: consecutive
    seeds, zero-padded names, and the household ladder unless a count is given."""
    seen: list[hg.HamletSpec] = []

    def fake(spec, out_base=None, render=True):  # type: ignore[no-untyped-def]
        seen.append(spec)
        return hg.Report(plan=a_plan(), failures=[])

    monkeypatch.setattr(hg.driver, "generate", fake)
    assert len(hg.cohort(3, first_seed=5, jobs=1)) == 3
    assert [s.seed for s in seen] == [5, 6, 7]
    assert [s.name for s in seen] == ["Cohort-05", "Cohort-06", "Cohort-07"]
    assert [s.households for s in seen] == [10 + (n * 7) % 11 for n in (5, 6, 7)]
    seen.clear()
    hg.cohort(2, first_seed=9, households=14, jobs=1)  # an explicit count overrides the ladder
    assert [s.households for s in seen] == [14, 14]


# ---- feature 151 US4: the stage profile prints, and changes nothing -------------------------------
@pytest.mark.rolls_map  # it builds a Settlement (two stand-in stages, no render) - the marker keeps `make quick` honest about what it runs
def test_the_stage_profile_prints_only_when_asked_and_rolls_the_same_map(monkeypatch, capfd) -> None:
    """`PROFILE=1` is an environment variable, which feature 132 forbids for a SWITCH - no variable may
    change what a map rolls. This one changes what is PRINTED, and this is the test that says so: the same
    stages run in the same order with it set and unset, and the settlement they build is identical."""
    from l7r.diagram.hamletgen import driver

    seen: list[str] = []

    def stage_alpha(s, plan) -> None:  # noqa: ANN001 - a stand-in stage
        seen.append("alpha")
        s.M.setdefault("probe", []).append("alpha")

    def stage_beta(s, plan) -> None:  # noqa: ANN001
        seen.append("beta")
        s.M.setdefault("probe", []).append("beta")

    plan = hg.plan_site(hg.HamletSpec(name="Prof", seed=3, households=10))
    monkeypatch.setattr(driver, "STAGES", (stage_alpha, stage_beta))

    # A DETERMINISTIC CLOCK, because the tie was decided by machine noise (feature 164, found when it
    # failed the gate). Both stub stages do nothing measurable, so `max(timings)` picked whichever
    # happened to record a larger float - and under a loaded parallel gate run that was `stage_beta`,
    # while every isolated run gave `stage_alpha`. The test then asserted a coin flip: 5 of 5 passing
    # locally, one failure at the gate, one whole gate cycle spent on it. The clock below makes alpha
    # 0.10 s and beta 0.01 s, which is what the assertions have always MEANT - one stage over the
    # 0.05 s floor and one under it - and it costs no wall time at all.
    ticks = iter([0.0, 0.10, 0.10, 0.11])
    monkeypatch.setattr(driver.time, "time", lambda: next(ticks, 0.11))

    monkeypatch.delenv(driver.STAGE_PROFILE_ENV, raising=False)
    quiet = driver.build(plan)
    assert capfd.readouterr().err == "", "an unasked-for profile is noise in every roll"

    seen.clear()
    monkeypatch.setenv(driver.STAGE_PROFILE_ENV, "1")
    loud = driver.build(plan)
    err = capfd.readouterr().err
    assert "stage profile" in err and "Prof seed 3" in err  # the header: the roll's total and its slowest stage
    assert "stage_alpha" in err  # ...which is named
    assert "stage_beta" not in err, "a stage under the 0.05 s floor stays out of the table - the point is the SLOW one"
    assert seen == ["alpha", "beta"], "the stages run in the same order either way"
    assert loud.M["probe"] == quiet.M["probe"] == ["alpha", "beta"]

    # ...AND A STAGE OVER THE FLOOR GETS ITS ROW. The assertions above prove only the negative - a
    # fast stage stays out of the table - so the table itself was never printed by any test, and the
    # line that prints it could have been deleted silently. Stand-in stages are instant by design, so
    # the CLOCK is what gets stood in for here rather than the work: each `time.time()` call advances
    # a tenth of a second, which puts both stages over the 0.05 s floor without the test sleeping.
    ticks = iter(0.1 * i for i in range(1000))
    monkeypatch.setattr(driver.time, "time", lambda: next(ticks))
    seen.clear()
    driver.build(plan)
    table = capfd.readouterr().err
    assert "stage profile" in table
    for row in ("stage_alpha", "stage_beta"):
        assert row in table, f"{row} took 0.1 s and owes a row"
    assert "%" in table and "s  " in table, "the row carries its duration and its share of the roll"
