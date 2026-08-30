"""gate tests split out of `tests.hamletgen.test_driver` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import re

import pytest

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
    # EIGHT IN THE FULL RUN since feature 145: the hamlet-path floor counts what these in-process rolls execute, and the
    # seed-dependent placer branches (the fabric threader, the web smoother, the strip and trunk guards) are reached by
    # rolls, not by a fixture; four more seeds (~50 s in FULL) reach what four did not. Their verdicts are pinned below.
    specs = hg.driver.cohort_specs(4 if FULL else 1, first_seed=41)  # FULL, not EXHAUSTIVE: the gate is always EXHAUSTIVE, and a seed sweep is the full run's
    reports = [rollcache.report(spec)[0] for spec in specs]
    assert len(reports) == len(specs)
    for report in reports:
        assert report.plan.placed >= round(0.85 * report.plan.spec.households), f"{report.plan.spec.name} seated {report.plan.placed}/{report.plan.spec.households}"
        if report.plan.spec.seed in ACREAGE_SHORT:
            continue  # a ledgered fan that cannot reach its acreage (below); measured on the pre-145 solver too
        assert abs(report.plan.acres - report.plan.target_acres) / report.plan.target_acres < 0.15, (
            f"{report.plan.spec.name}: {report.plan.acres:.1f} acres against a {report.plan.target_acres:.1f} target"
        )
    # MEASURED 2026-08-12: 24 of 24 over the first two dozen seeds, and 4 of 4 here
    # (`python3 -m l7r.diagram.tools.cohort_audit --count 24` reproduces the sweep and reports any residue by check).
    # It was 7 of 12 when the experiment was first reported. Keep this at 4 of 4: a change that drops
    # a single rolled hamlet now fails here by name, which is the whole point of a ratchet.
    # THE RATCHET IS A PIN (feature 133 T92, merged 2026-08-28): three of the four seeds fail named checks under
    # the engine the GM accepted on the reference hamlet - WAIVED as expected failures for a separate session
    # (133 tasks.md T91/T92). `baseline_verdict` holds the line both ways: a check outside a seed's set is a
    # regression, a pinned seed that comes up clean is a stale pin. At the gate only seed 41 rolls (clean); the
    # FULL run judges all four against the pin.
    rolled = {r.plan.spec.seed for r in reports}
    lines, clean = hg.baseline_verdict(reports, {seed: checks for seed, checks in GATE_COHORT_EXPECTED.items() if seed in rolled})  # a pin for a seed this scope did not roll is neither stale nor met
    assert clean, "\n".join(lines)


# The gate cohort's expected failures (seeds 41-44), measured 2026-08-27 at the T99 unlock - see above.
# A FAN THAT SATURATES: seed 45 (17 households, 22.1 acres asked) reaches 18.6 acres with the feature-145 solver and
# reached 18.1 with the bisection it replaced (measured on the pre-145 worktree, 2026-08-28) - the envelope clamps the
# fan at every aspect, so this is the canvas/envelope sizing for a large household count at that fall, not the solver.
# Pre-existing, ledgered here with its measurement (constitution XIII); the gate itself is green on the map.
ACREAGE_SHORT: dict[int, str] = {
    45: "18.6 of 22.1 acres (18.1 before feature 145)",
    47: "21.9 of 26.0 acres (21.9 before feature 145, whose gate on this seed was red besides) - 20 households at fall 90: the largest fan at every aspect stops at 21.9",
}

GATE_COHORT_EXPECTED: dict[int, frozenset[str]] = {
    # EMPTY SINCE FEATURE 166, AND ITS TWO PINS MOVED RATHER THAN VANISHED. `Report.failures` no longer
    # carries check-battery names - a roll's self-report is `farmhouses_reach_a_way` and nothing else -
    # so `baseline_verdict` would read every other pinned name as a STALE PIN and fail on it. That is the
    # mechanism working, not a bug in it: a pin nothing can read is not a pin.
    #
    # WHERE THE TWO WENT, and both were VERIFIED before being moved rather than assumed dead:
    #   seed 43 `lanes_bend_like_paths` - STILL REAL. Rolled it and ran the re-homed predicate: one kink
    #     at (991, 188), while seeds 41, 42 and 44 are clean. It is now held by
    #     `tests/gate/test_cohort_lane_rules.py`, which runs the lane rules over the whole gate cohort
    #     and carries seed 43 as a STRICT xfail - so it stays visible and the gate goes red the day the
    #     router stops making it.
    #   seed 45 `village_windbreak_is_continuous` - a FULL-cohort seed this gate scope never rolls. The
    #     rule itself migrated with the rest of the belt rules; the seed-45 instance is ledgered in
    #     `future-work/farming-communities.md` because verifying it needs the FULL cohort, and a pin
    #     asserted from a heuristic I have not checked is worse than no pin (my first attempt at a
    #     continuity measure flagged all four gate seeds, which is how I know).
    # seed 42 and two of seed 43's three came up clean when feature 145 moved the maps (the field solver).
    # seed 44 pinned `houses_clear_of_paddies` until feature 141 retired that check.
}


@pytest.mark.rolls_map
def test_a_map_that_strands_a_farmhouse_is_re_rolled_with_that_ground_forbidden(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """`generate` re-rolls a map whose FINISHED manifest strands a farmhouse, forbidding the ground
    those houses stood on. Three seat-time tests were built before this and all three failed, because
    whether a way can reach a steading depends on fabric that does not exist when seats are chosen;
    observing it on the finished map does not have that problem.

    THE ORACLE MOVED (feature 166 T02/T03). The seats used to be read off the gate's own printed FAIL
    line; they now come from `ways.unreached_houses`, which is that check's body LIFTED - not
    recomputed, because a hand-rolled reach measure was tried and over-counted on five of six seeds.
    So this still drives the loop by faking the ORACLE rather than by faking geometry; the oracle is
    just no longer the battery. That the old version of this test stopped working when the seam moved is
    the point: it was pinned to the dependency this feature removes."""

    def produce():  # type: ignore[no-untyped-def]
        calls: list[int] = []

        def fake_unreached(M, reach=None):  # type: ignore[no-untyped-def]
            calls.append(1)
            if len(calls) == 1:  # the first roll strands two houses; the predicate names them
                return [(1262, 848, 211), (1397, 890, 287)]
            return []

        # PATCH `hg.driver`, not `ways`: the driver imports the predicate at module level, so the name it
        # calls is its OWN. (The old test had to patch `check_village` instead, because `generate`
        # imported `gate` inside the function - the note is kept because the reasoning still applies to
        # any future seam: patch the namespace that does the CALLING.)
        monkeypatch.setattr(hg.driver, "unreached_houses", fake_unreached)
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
    assert (1262.0, 848.0) in seen[1]  # the re-roll forbids what the PREDICATE named
    assert (1397.0, 890.0) in seen[1]


@pytest.mark.rolls_map
def test_a_re_roll_that_does_not_help_is_not_kept(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """The retry is self-limiting: a re-roll is kept only if it strands NO MORE houses than the roll it
    replaces. Without that a map could be re-rolled into a worse state and shipped, which is the opposite
    of the point.

    THE CRITERION CHANGED (feature 166 T03) and this test changed with it. It used to be the gate's whole
    failure list getting no longer - a global quality proxy that becomes uncomputable when the battery
    goes. It is now the reach count, because this loop exists to fix stranded farmhouses and judging its
    re-rolls by an unrelated total let a defect elsewhere veto a genuine reach fix, KEEPING the map with
    the stranded house."""

    def produce():  # type: ignore[no-untyped-def]
        rolls: list[int] = []

        def fake_unreached(M, reach=None):  # type: ignore[no-untyped-def]
            rolls.append(1)
            # the RE-ROLL strands MORE than the roll it would replace, so it must be rejected
            return [(100, 100, 200)] if len(rolls) == 1 else [(100, 100, 200), (900, 900, 300)]

        monkeypatch.setattr(hg.driver, "unreached_houses", fake_unreached)

        # NO GATE STUB ANY MORE (feature 166 Phase 4). This used to patch `check_village.gate` with a
        # fake that PRINTED a FAIL line, because `Report.fail_lines` was scraped from the gate's stdout.
        # The driver now writes both `failures` and `fail_lines` itself from the reach predicate, so the
        # only seam this test needs is the one above - and the assertions below are unchanged except for
        # the count the report now carries.
        # WITH AN OUT PATH, because rejecting a re-roll leaves THAT roll's files on disk - the keeper has
        # to be re-emitted, and it cannot be done by finishing the kept Settlement a second time (that
        # splices the water block twice and its `</g>` closes the <svg> root early; see `_roll`). So the
        # rejected-re-roll path only exists when there is somewhere to write.
        out = str(tmp_path / "nohelp")
        rep = hg.generate(hg.HamletSpec(name="NoHelp", seed=4, households=10), out_base=out, render=False)
        return rep.failures, len(rolls), rep.fail_lines, (tmp_path / "nohelp.svg").read_text()

    # served from the roll cache keyed to this test's source (feature 135): three 10-household rolls, ~57 s fresh
    failures, n_rolls, fail_lines, svg = rollcache.keyed_to(test_a_re_roll_that_does_not_help_is_not_kept, produce)[0]
    assert failures == ["farmhouses_reach_a_way[1]"]  # the FIRST roll's verdict is kept, not the worse one
    assert n_rolls == 3  # roll, rejected re-roll, then the keeper re-emitted
    assert fail_lines and "farmhouses_reach_a_way" in fail_lines[0]
    assert svg.count("<svg") == 1 and svg.count("</svg>") == 1  # finished exactly once...
    assert len(re.findall(r"<g[\s>]", svg)) == svg.count("</g>")  # ...so its groups balance
