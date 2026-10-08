"""Feature 177 FR-008/FR-009/FR-009a - the measurement route, and everything it may still NOT do.

This route is the only one that may spend money with no engine delta, so its envelope is the whole of
its safety and every edge of it is asserted here rather than described in the spec. The GM's rule for
this package is that *"all of the situations in which we absolutely, positively do not want to run
anything on AWS"* come first and the speedup second; a new route is a change to that list, and the
tests are where the change is pinned.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from l7r.diagram.ci import decision
from tests.tooling.ci.test_cache import FRESHNESS_PATHS, _cache_paths
from tests.tooling.ci.test_decision import DIRECT, GATED, NOW, failed, green

pytestmark = pytest.mark.tooling

HERE = Path(__file__).resolve().parents[3]
REPO = HERE.parents[2]
BUILDSPEC = REPO / "buildspec"


def measure(delta=DIRECT, state=None, verified=None, breaker=None, remote_off=None):
    return decision.decide(delta, state or green(), NOW, verified, breaker, decision.CHECK, None, "reference", 0.0, None, remote_off, measure=True)


def test_the_ONE_bypass_is_route_is_gated() -> None:
    """FR-008. A DIRECT delta refuses every other route and dispatches this one - which is the entire
    reason the route exists: feature 175 owed a FULL-scope timing, could not take it because
    `ci-check` requires an engine delta, and four features later still had not."""
    assert decision.decide(DIRECT, green(), NOW, None, None, decision.CHECK, None).verdict == "REFUSE(route-is-gated)"
    assert measure().verdict == "DISPATCH"


def test_the_bypassed_condition_is_still_PRINTED_and_says_so() -> None:
    """This package reports every condition even when one has already decided the verdict. A bypass
    that vanished from the printout would be the one thing a reader could not audit."""
    row = next(c for c in measure().conditions if c.name == "route-is-gated")
    assert row.passed and "BYPASSED" in row.why and "FR-009a" in row.why
    assert "route-is-gated" in decision.render(measure(), "measure", "reference")


def test_a_RED_local_gate_still_refuses_it() -> None:
    """FR-009a, and the condition rests on the GM's own words: *"make done could check whether the
    last thing that was run was an unsuccessful make done, in which case it should just short circuit
    immediately and refuse to run without even dispatching to AWS."* A measurement is not a reason to
    lose that."""
    assert measure(state=failed()).verdict == "REFUSE(green-local-since-edit)"
    assert measure(state=green("a-different-hash")).verdict == "REFUSE(green-local-since-edit)"
    assert decision.decide(DIRECT, None, NOW, None, None, decision.CHECK, None, "reference", 0.0, None, None, measure=True).verdict == "REFUSE(green-local-since-edit)"


def test_the_breaker_and_the_remote_switch_still_refuse_it() -> None:
    """The monthly hard stop and feature 132's switch: *"if it is disabled, then we do not use it as a
    gate. and we do not dispatch to it while we are doing iteration."*"""
    assert measure(breaker="the monthly hard stop has tripped").verdict == "REFUSE(breaker-not-tripped)"
    assert measure(remote_off="remote is OFF since ...").verdict == "REFUSE(remote-enabled)"


def test_a_verified_record_does_not_short_circuit_a_measurement() -> None:
    """A record says a GATE passed on this content. It says nothing about what the gate COST, which is
    the only thing this route is for - so the measurement runs."""
    rec = decision.VerifiedRecord(tree="t", build_id="gm-assistant-check:abc", scope="full")
    assert decision.decide(GATED, green(), NOW, rec, None, decision.CHECK, None).verdict == "SKIP-VERIFIED"
    assert measure(delta=GATED, verified=rec).verdict == "DISPATCH"


def test_the_route_cannot_mint_a_push_credential() -> None:
    """FR-009, asserted where it is ENFORCED - in the tree the build runs, not in the dispatcher.

    This is the only route that may dispatch without an engine delta, so it is the only one that could
    be used to buy a merge credential cheaply: run a "measurement", have it write a `verified/`
    record, and let the next push read that record as proof a gate passed. `run.sh` returns before the
    record is written, which also puts it before the push."""
    run_sh = (BUILDSPEC / "run.sh").read_text(encoding="utf-8")
    assert '"$MODE" = measure' in run_sh, "the build side must know the mode"
    guard = run_sh.index('if [ "$MODE" = measure ]')
    assert guard < run_sh.index('aws s3 cp --quiet /tmp/verified.json'), "the measure branch must return BEFORE the verified record is written"
    assert guard < run_sh.index("git push origin HEAD:main"), "...and therefore before the push"
    assert re.search(r'if \[ "\$MODE" = measure \];.*?\n(.*\n)*?\s*exit 0\n', run_sh), "the branch must exit, not fall through"


def test_the_measure_buildspec_matches_check_in_everything_but_MODE() -> None:
    """A measurement that ran cold while the gate runs warm, or checked out a different tree, would
    measure something other than the gate. The cache block and the install phase are therefore
    identical to check.yml's, and `test_cache.py`'s drift test covers the other two."""
    check, meas = ((BUILDSPEC / n).read_text(encoding="utf-8") for n in ("check.yml", "measure.yml"))
    assert "MODE: measure" in meas and "MODE: check" not in meas
    assert _cache_paths(meas) == _cache_paths(check), "a measurement must be cached exactly as the gate is"
    assert FRESHNESS_PATHS[0] in meas, "including the hooks-test freshness state"
    assert "--no-checkout" in meas and "buildspec/sparse-excludes.txt" in meas, "and it must check out exactly what the gate checks out"


def test_the_cli_and_the_make_target_agree_that_it_is_paid_and_prompted() -> None:
    """FR-010: the same class as `make ci-image` - it prompts, it cancels by default, and it logs. A
    session may answer under the GM's 2026-08-25 authorization, and the logged reason is how the audit
    tells a session's answer from theirs."""
    makefile = (HERE / "Makefile").read_text(encoding="utf-8")
    body = makefile.split("\nci-measure:")[1].split("\nci-image:")[0]
    assert "$(REMOTE_OK)" in body, "remote off refuses it before any AWS call"
    assert "Enter cancels" in body and "$(LOGBYPASS) cancelled" in body and "$(LOGBYPASS) permitted" in body
    assert "-t 0" in body, "a paid prompt needs a terminal"
    main = (HERE / "l7r" / "diagram" / "ci" / "__main__.py").read_text(encoding="utf-8")
    assert '"measure"' in main and "no verified record, no push" in main
