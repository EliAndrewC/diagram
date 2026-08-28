"""gate tests split out of `tests.hamletgen.test_driver` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import re

import pytest

from l7r.diagram import check_village
from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache
from tests._scope import FULL


@pytest.mark.rolls_map
def test_a_rolled_cohort_passes_the_whole_gate() -> None:
    """The experiment's actual claim, in miniature, and a RATCHET on it.

    Hamlets rolled from seeds nobody looked at come out correct. The honest figure is still a pass
    RATE rather than a guarantee - a cohort of two dozen turns up the odd siting collision - so this
    pins the rate: a change that drops it fails here by name.

    The two things that hold WITHOUT exception, on every map whether it passes the gate or not, are
    asserted for all of them: the declared households are seated, and the paddy acreage lands on the
    figure the household count implies. Those are the derivations this module exists to get right.

    (The four demo maps in `pool/hamlets/` carry the full-size version of the gate check, in
    `tests/test_villages.py`; four members here keep the suite's runtime honest.)"""
    # SERIAL ON PURPOSE (2026-08-16), for two reasons that point the same way. An in-gate caller
    # wants `jobs=1` - a pytest worker that spawns its own pool competes with the other 21 - and
    # these four rolls are also this suite's only in-process walk of the seed-dependent generator
    # branches, because a fanned-out roll executes in a worker where this run's coverage cannot see
    # it. Leaving it on the default parallel path silently uncovered `hinterland.py`'s
    # no-house-column fringe fallback. The fan-out is a CLI win, not a gate win; the parallel branch
    # is held by `test_the_fan_out_agrees_with_the_serial_path` below.
    # ONE REPRESENTATIVE SEED AT THE GATE, FOUR IN THE FULL RUN (feature 135, GM 2026-08-27: *"running tests
    # against many random seeds on the same map ... is something either more suited to a EXAUSTIVE=1 Test run or
    # better yet best farmed out to the AWS tests"*) - and each member through the roll cache, so an unchanged
    # engine serves the report and a changed one rolls it. The full run (`make done FULL=1`, `L7R_TESTS_FULL=1`)
    # bypasses the cache and rolls all four. Last exhaustive green: 2026-08-27 (this feature's baseline).
    specs = hg.driver.cohort_specs(4 if FULL else 1, first_seed=41)  # FULL, not EXHAUSTIVE: the gate is always EXHAUSTIVE, and a seed sweep is the full run's
    reports = [rollcache.report(spec)[0] for spec in specs]
    assert len(reports) == len(specs)
    for report in reports:
        assert report.plan.placed >= round(0.85 * report.plan.spec.households), f"{report.plan.spec.name} seated {report.plan.placed}/{report.plan.spec.households}"
        assert abs(report.plan.acres - report.plan.target_acres) / report.plan.target_acres < 0.15, (
            f"{report.plan.spec.name}: {report.plan.acres:.1f} acres against a {report.plan.target_acres:.1f} target"
        )
    # MEASURED 2026-08-12: 24 of 24 over the first two dozen seeds, and 4 of 4 here
    # (`python3 -m l7r.diagram.tools.cohort_audit --count 24` reproduces the sweep and reports any residue by check).
    # It was 7 of 12 when the experiment was first reported. Keep this at 4 of 4: a change that drops
    # a single rolled hamlet now fails here by name, which is the whole point of a ratchet.
    passed = [r for r in reports if r.ok]
    assert len(passed) == len(reports), f"only {len(passed)}/{len(reports)} rolled hamlets pass the whole gate: " + "; ".join(f"{r.plan.spec.name}: {r.failures}" for r in reports if not r.ok)


@pytest.mark.rolls_map
def test_a_map_that_strands_a_farmhouse_is_re_rolled_with_that_ground_forbidden(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`generate` re-rolls a map whose FINISHED manifest strands a farmhouse, forbidding the ground
    those houses stood on. Three seat-time tests were built before this and all three failed, because
    whether a way can reach a steading depends on fabric that does not exist when seats are chosen;
    observing it on the finished map does not have that problem.

    The gate is the oracle at every step - the seats are read off its own FAIL line rather than
    recomputed, because a hand-rolled reach measure was tried and over-counted on five of six seeds.
    So this drives the loop by faking the ORACLE, not by faking geometry."""

    def produce():  # type: ignore[no-untyped-def]
        calls: list[int] = []

        def fake_gate(M, verbose=True, only=None):  # type: ignore[no-untyped-def]
            calls.append(1)
            if len(calls) == 1:  # the first roll strands two houses; the gate names them
                print("FAIL farmhouses_reach_a_way  -> 2 farmhouse(s) at [(1262, 848, 211), (1397, 890, 287)] - omission")
                return ["farmhouses_reach_a_way"]
            return []

        # PATCH THE SOURCE MODULE, not `hg.driver`: `generate` imports `gate` INSIDE the function, so
        # the name is re-fetched from `check_village` on every call and a package-level patch is
        # invisible to it.
        monkeypatch.setattr(check_village, "gate", fake_gate)
        seen: list[list[tuple[float, float]]] = []
        real_build = hg.driver.build

        def spy_build(plan, avoid=()):  # type: ignore[no-untyped-def]
            seen.append(list(avoid))
            return real_build(plan, avoid=avoid)

        monkeypatch.setattr(hg.driver, "build", spy_build)
        rep = hg.generate(hg.HamletSpec(name="Retry", seed=4, households=10), out_base=None, render=False)
        return rep.failures, seen

    # served from the roll cache keyed to this test's source (feature 135): two 10-household rolls, ~36 s fresh
    failures, seen = rollcache.keyed_to(test_a_map_that_strands_a_farmhouse_is_re_rolled_with_that_ground_forbidden, produce)[0]
    assert failures == []  # the re-roll's verdict is the one reported
    assert len(seen) == 2  # one roll, then exactly one re-roll
    assert seen[0] == []  # the first roll forbids nothing
    assert (1262.0, 848.0) in seen[1]  # the re-roll forbids what the GATE named
    assert (1397.0, 890.0) in seen[1]


@pytest.mark.rolls_map
def test_a_re_roll_that_does_not_help_is_not_kept(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The retry is self-limiting: a re-roll is kept only if the gate's verdict is no longer than the
    one it replaces. Without that a map could be re-rolled into a WORSE state and shipped, which is
    the opposite of the point."""

    def produce():  # type: ignore[no-untyped-def]
        rolls: list[int] = []

        def fake_gate(M, verbose=True, only=None):  # type: ignore[no-untyped-def]
            rolls.append(1)
            print("FAIL farmhouses_reach_a_way  -> 1 farmhouse(s) at [(100, 100, 200)] - omission")
            # the RE-ROLL comes back worse than the roll it would replace
            return ["farmhouses_reach_a_way"] if len(rolls) == 1 else ["farmhouses_reach_a_way", "another_rule"]

        monkeypatch.setattr(check_village, "gate", fake_gate)
        # WITH AN OUT PATH, because rejecting a re-roll leaves THAT roll's files on disk - the keeper has
        # to be re-emitted, and it cannot be done by finishing the kept Settlement a second time (that
        # splices the water block twice and its `</g>` closes the <svg> root early; see `_roll`). So the
        # rejected-re-roll path only exists when there is somewhere to write.
        out = str(tmp_path / "nohelp")
        rep = hg.generate(hg.HamletSpec(name="NoHelp", seed=4, households=10), out_base=out, render=False)
        return rep.failures, len(rolls), rep.fail_lines, (tmp_path / "nohelp.svg").read_text()

    # served from the roll cache keyed to this test's source (feature 135): three 10-household rolls, ~57 s fresh
    failures, n_rolls, fail_lines, svg = rollcache.keyed_to(test_a_re_roll_that_does_not_help_is_not_kept, produce)[0]
    assert failures == ["farmhouses_reach_a_way"]  # the FIRST roll's verdict is kept, not the worse one
    assert n_rolls == 3  # roll, rejected re-roll, then the keeper re-emitted
    assert fail_lines and "farmhouses_reach_a_way" in fail_lines[0]
    assert svg.count("<svg") == 1 and svg.count("</svg>") == 1  # finished exactly once...
    assert len(re.findall(r"<g[\s>]", svg)) == svg.count("</g>")  # ...so its groups balance
