"""The runtime ratchets: a target that gets slower FAILS (feature 171).

The spec is `specs/171-runtime-ratchets/spec.md`, written and reviewed by the `diagram-testing`
session and handed to this one. What these tests protect is not the numbers but the SHAPE: a
mechanism that sits under the GM's figures, a baseline that only a human moves, and a comparison that
differs by regime.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[5] / "scripts"
_spec = importlib.util.spec_from_file_location("_ratchet", SCRIPTS / "_ratchet.py")
assert _spec and _spec.loader
ratchet = importlib.util.module_from_spec(_spec)
# REGISTER BEFORE EXEC. `_ratchet` uses `from __future__ import annotations`, so its dataclass fields
# are string annotations that `dataclasses` resolves through `sys.modules[cls.__module__]` - which is
# None for a module loaded by importlib and never registered, and the failure surfaces as a baffling
# `AttributeError: 'NoneType' object has no attribute '__dict__'` from inside the stdlib.
sys.modules["_ratchet"] = ratchet
_spec.loader.exec_module(ratchet)


# ---------------------------------------------------------------------------------------------
# FR-004 - the derivation, and the ONLY evidence it is trustworthy
# ---------------------------------------------------------------------------------------------
def test_the_derivation_reproduces_the_gm_s_own_numbers() -> None:
    """THIS TEST IS A TWO-POINT FIT, AND THAT IS THE WHOLE ARGUMENT FOR THE FORMULA.

    The GM stated two ceilings, each against a baseline they were reasoning from: 15 s given `quick`'s
    11 s, and 45 s given a `done` of 35 s. The derivation is trusted on targets the GM never named
    ONLY because it reproduces both. There is no third point, and no independent justification.

    So if a future target's derived bar ever looks wrong, this is the test that tells you why: the
    formula was never validated anywhere except at these two places. Do not read agreement here as
    evidence that it generalizes - read it as the reason it is allowed to be used at all.
    (Recorded at the handoff author's request; it is their point and it is a good one.)
    """
    assert ratchet.derive_ceiling(11, hard=15) == 15, "the GM's quick figure"
    assert ratchet.derive_ceiling(35, hard=45) == 45, "the GM's done figure"


@pytest.mark.parametrize("baseline", [11, 12, 20, 35, 100, 155, 310])
def test_the_derivation_never_computes_a_ceiling_above_the_gm_s_number(baseline: int) -> None:
    """The `min()` is load-bearing and is not to be removed.

    An early draft of the handoff spec derived `max(baseline + 4, int(baseline * 1.3))` with no cap, so
    the ceiling LOOSENED as the baseline drifted: a `quick` baseline of 12 s bought a 16 s ceiling,
    past the figure the GM stated. That is the mechanism relaxing exactly when the thing it guards
    starts happening - caught by round 2 of the handoff's own review.
    """
    assert ratchet.derive_ceiling(baseline, hard=15) <= 15


# ---------------------------------------------------------------------------------------------
# FR-002 - one rule per regime
# ---------------------------------------------------------------------------------------------
def test_quick_is_judged_on_the_run_itself_at_the_gm_s_fifteen_seconds() -> None:
    ok, _ = ratchet.verdict("quick", seconds=14)
    assert ok, "14 s is under the bar"
    ok15, msg = ratchet.verdict("quick", seconds=15)
    assert not ok15, "the GM said 'even as much as fifteen seconds' should fail - so 15 fails, not 16"
    assert "15s ceiling" in msg


def test_done_uses_the_median_while_its_baseline_is_above_the_gm_s_thirty_five() -> None:
    """Today's regime. A per-run bar at the interim ceiling would fire on 28% of normal runs, which is
    the handoff author's decision D2 - recorded as theirs, and the GM's to overturn."""
    _c, mode = ratchet.ceiling_for(ratchet.RATCHETS["done"])
    assert mode == "median"
    ceiling, _m = ratchet.ceiling_for(ratchet.RATCHETS["done"])
    ok, _ = ratchet.verdict("done", seconds=ceiling * 2, median=ceiling - 1)
    assert ok, "a single slow run is not evidence in this regime - the median is"
    over, msg = ratchet.verdict("done", seconds=10, median=ceiling)
    assert not over and f"{ceiling}s ceiling" in msg, msg


def test_done_switches_to_the_run_and_the_gm_s_forty_five_once_the_baseline_reaches_thirty_five() -> None:
    """The regime the efficiency work will bring about by pinning a smaller baseline.

    The case the handoff flagged explicitly: a single 45 s run against a 35 s baseline must FAIL. An
    earlier draft compared an unbounded median here and that run would have passed - silently
    overturning the GM's own worked example.
    """
    pinned = ratchet.Ratchet(target="done", baseline=35, reason="the efficiency work landed", hard_ceiling=45, hard_at_or_below=35, compare="median")
    ceiling, mode = ratchet.ceiling_for(pinned)
    assert (ceiling, mode) == (45, "run"), "at or below 35 the GM's 45 is fixed AND the run is judged"


def test_the_ceiling_does_not_auto_tighten_below_a_number_the_gm_stated() -> None:
    """At a 25 s baseline the derivation would give 32 s. The GM stated 45. A mechanism that tightened
    past their figure without being asked is the same overreach as one that loosens past it."""
    pinned = ratchet.Ratchet(target="done", baseline=25, reason="hypothetical", hard_ceiling=45, hard_at_or_below=35, compare="median")
    assert ratchet.ceiling_for(pinned)[0] == 45


# ---------------------------------------------------------------------------------------------
# FR-003 / FR-005 / FR-006 / FR-010 - the table
# ---------------------------------------------------------------------------------------------
def test_every_pinned_baseline_carries_a_written_reason() -> None:
    """FR-010: a baseline moves in EITHER direction only with a reason at the point of change. A row
    with no reason is how a pinned number quietly becomes a rolling one."""
    for name, r in ratchet.RATCHETS.items():
        assert len(r.reason.split()) >= 5, f"{name}'s baseline has no real reason: {r.reason!r}"


def test_the_aws_row_is_present_and_not_armed() -> None:
    """FR-006: wired, and off. The GM: 'I am not interested in running the lengthy tests at this time,
    especially given that they run on AWS.'"""
    assert "test-full" in ratchet.RATCHETS
    assert not ratchet.RATCHETS["test-full"].armed
    ok, _ = ratchet.verdict("test-full", seconds=99999)
    assert ok, "an unarmed row judges nothing"


def test_an_unknown_target_and_a_missing_measurement_never_fail() -> None:
    """A target with no row, and a row with nothing measured, are silent. A ratchet that fails for
    lack of evidence teaches sessions to route around it."""
    assert ratchet.verdict("no-such-target", seconds=9999)[0]
    assert ratchet.verdict("done", seconds=None, median=None)[0]


def test_a_failure_says_what_to_do() -> None:
    """FR-008. `QUICK_BUDGET`'s message is the model: it names the number, the ceiling, and the next
    command. A bar that fails without a route is a bar that gets raised."""
    _ok, msg = ratchet.verdict("quick", seconds=99)
    for expected in ("make audit", "make durations", "pinned baseline", "written reason"):
        assert expected in msg, f"the failure message does not mention {expected!r}"


# ---------------------------------------------------------------------------------------------
# FR-009 - only runs that DID THE WORK, and like with like
# ---------------------------------------------------------------------------------------------
def test_the_median_ignores_short_circuits_failures_and_other_scopes(tmp_path) -> None:
    """A log full of `already-verified` rows must not lower anybody's bar.

    Those rows carry `seconds: 0` - the gate short-circuits on unchanged engine content - so a naive
    median over every row is dragged toward zero, and the ratchet would then fire on a perfectly
    normal run. The handoff author raised this; it is why FR-009's exclusion is load-bearing rather
    than tidy. Failures are excluded for the same reason in reverse: a run that died at 4 s is not
    evidence that the gate is fast.
    """
    gc_spec = importlib.util.spec_from_file_location("_gatecost", SCRIPTS / "_gatecost.py")
    assert gc_spec and gc_spec.loader
    gatecost = importlib.util.module_from_spec(gc_spec)
    sys.modules["_gatecost"] = gatecost
    gc_spec.loader.exec_module(gatecost)

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)  # so the toplevel resolves HERE
    log = tmp_path / ".claude/skills/diagram/dev/run-log"
    log.mkdir(parents=True)
    rows = (
        [("green", "reference", 100)] * 3  # the only evidence about duration
        + [("already-verified", "reference", 0)] * 9  # short-circuits: no work done
        + [("failed:test", "reference", 4)] * 3  # died early: not evidence of speed
        + [("green", "full", 900)] * 3  # a different scope entirely
        + [("green", "reference", 30)] * 5  # INCREMENTAL runs (feature 207): a selection, not the target - excluded below
    )
    for i, (result, scope, secs) in enumerate(rows):
        entry = {"utc": f"2026-08-30T{i:02d}:00:00Z", "target": "done", "scope": scope, "seconds": secs, "result": result, "commit": "abc1234"}
        if secs == 30:
            entry["mode"] = "incremental"
        (log / f"2026083{i // 10}T{i:06d}-{i}.json").write_text(json.dumps(entry))

    got = gatecost.median_seconds("done", "reference", cwd=str(tmp_path))
    assert got == 100, f"the median took the excluded rows into account: {got}"


# ---------------------------------------------------------------------------------------------
# FEATURE 196: warm and cold are separate populations. A median over both described neither, and
# it blocked two landings in one day on a finding of "no regression".
def test_a_cold_run_is_judged_against_the_cold_ceiling_not_the_warm_one() -> None:
    r = ratchet.RATCHETS["done"]
    assert ratchet.ceiling_for_class(r, "cold")[0] == ratchet.derive_ceiling(r.baseline_cold)
    assert ratchet.ceiling_for_class(r, "warm")[0] == ratchet.derive_ceiling(r.baseline)
    assert ratchet.ceiling_for_class(r, "cold")[0] > ratchet.ceiling_for_class(r, "warm")[0]


def test_below_sample_the_RUN_is_judged_and_never_waved_through() -> None:
    """SC-002, and the path that would have disarmed this ratchet entirely.

    The round-1 draft passed an unjudgeable run. Measured at the time: 0 of 507 run-log entries
    carried a cache field, so BOTH classes started empty and `make done` would have been unjudged for
    hours to over a week - the guard whose motivating failure was a 4x slowdown going unnoticed."""
    over = ratchet.derive_ceiling(ratchet.RATCHETS["done"].baseline_cold) + 1
    ok, msg = ratchet.verdict("done", over, None, "cold", "reference", 0)
    assert not ok and "cold roll cache" in msg, "a below-sample run over its class ceiling must FAIL"
    under = ratchet.derive_ceiling(ratchet.RATCHETS["done"].baseline_cold) - 1
    assert ratchet.verdict("done", under, None, "cold", "reference", 0)[0]


def test_an_unknown_class_takes_the_STRICTER_warm_ceiling() -> None:
    """`REF_OK` skips the reference roll, so no verdict exists and no marker is written. An unknown
    class with no rule is how this feature nearly re-introduced its own defect through a side door."""
    warm_ceiling = ratchet.derive_ceiling(ratchet.RATCHETS["done"].baseline)
    assert not ratchet.verdict("done", warm_ceiling + 1, None, None, "reference", 0)[0]


def test_full_scope_stays_UNJUDGED_below_sample() -> None:
    """`done` has zero green full-scope runs, so FULL is unjudged today. Arming a per-run bar on a
    PAID, prompted target against ceilings derived wholly from reference runs would fail a completed
    cold FULL run by construction - and would split populations on one axis while merging on another."""
    way_over = ratchet.derive_ceiling(ratchet.RATCHETS["done"].baseline_cold) + 500
    assert ratchet.verdict("done", way_over, None, "cold", "full", 0)[0], "FULL must stay unjudged"


def test_each_baseline_carries_its_OWN_written_reason() -> None:
    """171 FR-010 per CLASS, not per row. The existing per-row check passes while a second baseline
    inherits a reason that is not about it - the property gone, the test still green."""
    for name, r in ratchet.RATCHETS.items():
        if getattr(r, "baseline_cold", None) is not None:
            assert len(r.reason_cold.split()) >= 5, f"{name}'s cold baseline has no written reason"


def test_the_dry_run_floor_still_reads_baseline() -> None:
    """SC-004. `check-run-plausible.py` derives its floor from `RATCHETS[target].baseline` via
    getattr and treats a missing value as NO FLOOR - so renaming that field would silently restore
    the 2026-09-05 defect where `make -n done` minted a push credential."""
    spec = importlib.util.spec_from_file_location("crp", SCRIPTS / "check-run-plausible.py")
    crp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(crp)
    assert crp.floor_for("done") == max(crp.ABSOLUTE_MIN, int(ratchet.RATCHETS["done"].baseline * crp.FRACTION))


def test_a_class_median_EXCLUDES_entries_that_carry_no_class(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """SC-003. Every entry written before feature 196 lacks a cache field, and DEFAULTING them would
    put cold runs in the warm population - the exact defect this feature removes. Excluding costs a
    slow start (the below-sample rule covers it) and cannot lie."""
    spec = importlib.util.spec_from_file_location("gc", SCRIPTS / "_gatecost.py")
    gc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gc)
    logs = tmp_path / ".claude/skills/diagram/dev/run-log"
    logs.mkdir(parents=True)
    rows = [
        {"target": "done", "scope": "reference", "result": "green", "seconds": 900, "utc": "2026-01-01T00:00:00Z"},
        {"target": "done", "scope": "reference", "result": "green", "seconds": 100, "utc": "2026-01-02T00:00:00Z", "cache": "warm"},
        {"target": "done", "scope": "reference", "result": "green", "seconds": 700, "utc": "2026-01-03T00:00:00Z", "cache": "cold"},
    ]
    for i, r in enumerate(rows):
        (logs / f"{i}.json").write_text(json.dumps(r))
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    cwd = str(tmp_path)
    assert gc.median_seconds("done", "reference", cwd, "warm") == 100, "the classless 900 must not count"
    assert gc.median_seconds("done", "reference", cwd, "cold") == 700
    assert gc.class_count("done", "reference", cwd, "warm") == 1
    assert gc.median_seconds("done", "reference", cwd) == 700, "classless still sees all three"
