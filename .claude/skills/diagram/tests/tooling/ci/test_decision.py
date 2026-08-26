"""One case per row of the VerificationState transition table, per route, SKIP-VERIFIED, the breaker,
merge-vs-check (FR-011 is merge only), FR-027's scope rule, and the FR-014 printout (T010, T045, T061)."""

from __future__ import annotations

from l7r.diagram.ci import config, decision
from l7r.diagram.ci.delta import Delta
from l7r.diagram.ci.features import FeatureStatus
from l7r.diagram.ci.state import FAILED, GREEN, VerificationState

S = ".claude/skills/diagram/"
GATED = Delta("b", (S + "l7r/diagram/m.py",), (S + "l7r/diagram/m.py",))
DIRECT = Delta("b", ("docs/x.md",), ())
COMPLETE = FeatureStatus(name="130-x", exists=True, faithful=True, open_tasks=())
OPEN = FeatureStatus(name="130-x", exists=True, faithful=True, open_tasks=("T005 open",))
NOW = "h1"


def green(h: str = NOW) -> VerificationState:
    return VerificationState(GREEN, "quick", "2026-08-25T00:00:00Z", h, "abc")


def failed() -> VerificationState:
    return VerificationState(FAILED, "done", "2026-08-25T00:00:00Z", NOW, "abc")


def names_failing(d: decision.DispatchDecision) -> list[str]:
    return [c.name for c in d.conditions if not c.passed]


def test_dispatch_when_everything_passes_on_merge() -> None:
    d = decision.decide(GATED, green(), NOW, None, None, decision.MERGE, COMPLETE)
    assert d.verdict == "DISPATCH" and d.dispatches and names_failing(d) == []


def test_direct_route_refuses_first() -> None:
    d = decision.decide(DIRECT, green(), NOW, None, None, decision.MERGE, COMPLETE)
    assert d.verdict == "REFUSE(route-is-gated)"


def test_feature_incomplete_refuses_merge_but_not_check() -> None:
    m = decision.decide(GATED, green(), NOW, None, None, decision.MERGE, OPEN)
    assert m.verdict == "REFUSE(feature-complete)" and "T005 open" in next(c.why for c in m.conditions if c.name == "feature-complete")
    c = decision.decide(GATED, green(), NOW, None, None, decision.CHECK, OPEN)
    assert c.verdict == "DISPATCH" and all(cond.name != "feature-complete" for cond in c.conditions)
    n = decision.decide(GATED, green(), NOW, None, None, decision.MERGE, None)
    assert n.verdict == "REFUSE(feature-complete)"


def test_transition_table_rows() -> None:
    absent = decision.decide(GATED, None, NOW, None, None, decision.CHECK, None)
    assert absent.verdict == "REFUSE(green-local-since-edit)" and "no local check recorded" in absent.conditions[2].why
    red = decision.decide(GATED, failed(), NOW, None, None, decision.CHECK, None)
    assert red.verdict == "REFUSE(green-local-since-edit)" and "last gate FAILED" in red.conditions[2].why and "make quick" in red.conditions[2].why
    stale = decision.decide(GATED, green("older"), NOW, None, None, decision.CHECK, None)
    assert stale.verdict == "REFUSE(green-local-since-edit)" and "different code" in stale.conditions[2].why
    fresh = decision.decide(GATED, green(), NOW, None, None, decision.CHECK, None)
    assert fresh.verdict == "DISPATCH"


def test_every_condition_is_reported_even_after_the_first_failure() -> None:
    d = decision.decide(DIRECT, None, NOW, None, "tripped", decision.MERGE, None)
    assert names_failing(d) == ["route-is-gated", "feature-complete", "green-local-since-edit", "breaker-not-tripped"]
    assert d.verdict == "REFUSE(route-is-gated)"


def test_skip_verified_and_scope_rule() -> None:
    ref = decision.VerifiedRecord("t", "gm-assistant-check:1", "reference")
    full = decision.VerifiedRecord("t", "gm-assistant-check:2", "full")
    assert decision.decide(GATED, green(), NOW, ref, None, decision.CHECK, None, "reference").verdict == "SKIP-VERIFIED"
    d = decision.decide(GATED, green(), NOW, ref, None, decision.CHECK, None, "full")
    assert d.verdict == "DISPATCH" and "still owed" in next(c.why for c in d.conditions if c.name == "tree-not-already-verified")
    assert decision.decide(GATED, green(), NOW, full, None, decision.CHECK, None, "full").verdict == "SKIP-VERIFIED"
    assert decision.decide(GATED, green(), NOW, full, None, decision.CHECK, None, "reference").verdict == "SKIP-VERIFIED"
    assert decision.decide(GATED, green(), NOW, ref, None, decision.CHECK, None, "reference").skip_verified


def test_an_operation_is_never_skip_verified() -> None:
    full = decision.VerifiedRecord("t", "gm-assistant-check:2", "full")
    d = decision.decide(GATED, green(), NOW, full, None, decision.CHECK, None, "reference", 0.0, "cohort N=48")
    assert d.verdict == "DISPATCH" and "no verified record" in next(c.why for c in d.conditions if c.name == "tree-not-already-verified")


def test_a_verified_tree_does_not_rescue_a_refusal() -> None:
    ref = decision.VerifiedRecord("t", "b", "reference")
    assert decision.decide(GATED, failed(), NOW, ref, None, decision.CHECK, None).verdict == "REFUSE(green-local-since-edit)"


def test_breaker_is_last_and_refuses() -> None:
    d = decision.decide(GATED, green(), NOW, None, "the monthly hard stop tripped", decision.CHECK, None)
    assert d.verdict == "REFUSE(breaker-not-tripped)" and d.conditions[-1].why == "the monthly hard stop tripped"


def test_estimate_and_render_golden() -> None:
    d = decision.decide(GATED, green(), NOW, None, None, decision.CHECK, None, "reference", 1.234)
    assert d.estimate == decision.Estimate(minutes=5.0, cost_usd=0.4, month_to_date_usd=1.23)
    text = decision.render(d, "check", "reference")
    assert text.splitlines()[0] == "ci-check (reference scope) - dispatch conditions:"
    assert "[ok] route-is-gated" in text and "[ok] green-local-since-edit" in text
    assert f"~5 build-min at ${config.RATE_PER_MIN:.2f}/min = ~$0.40; month-to-date remote spend $1.23" in text
    assert text.splitlines()[-1] == "  verdict: DISPATCH"
    op = decision.estimate("reference", 0.0, "cohort N=48")
    assert op.minutes == config.ESTIMATE_MINUTES["operation"]
    assert decision.estimate("full", 0.0).minutes == config.ESTIMATE_MINUTES["full"]
    refused = decision.render(decision.decide(DIRECT, None, NOW, None, None, decision.MERGE, None), "merge", "reference")
    assert "[--] route-is-gated" in refused and refused.endswith("verdict: REFUSE(route-is-gated)")


# ---- REMOTE OFF (feature 132): the first row, and the LOCAL-GATED verdict table ----------------


def test_remote_on_is_the_first_row_and_passes() -> None:
    d = decision.decide(GATED, green(), NOW, None, None, decision.MERGE, COMPLETE)
    assert d.conditions[0].name == "remote-enabled" and d.conditions[0].passed and d.verdict == "DISPATCH"


def test_remote_off_never_dispatches() -> None:
    d = decision.decide(GATED, green(), NOW, None, None, decision.MERGE, COMPLETE, remote_off="remote is OFF since T by GM: iterating")
    assert d.verdict == "REFUSE(remote-enabled)" and not d.dispatches
    assert d.conditions[0].name == "remote-enabled" and not d.conditions[0].passed and "iterating" in d.conditions[0].why
    assert "[--] remote-enabled" in decision.render(d, "merge", "reference")


def test_remote_off_with_a_local_green_done_is_skip_verified() -> None:
    local = decision.VerifiedRecord("t", "local:make-done@abc", "reference")
    d = decision.decide(GATED, green(), NOW, local, None, decision.MERGE, COMPLETE, remote_off="off")
    assert d.verdict == "SKIP-VERIFIED" and d.skip_verified  # LOCAL-GATED: the caller pushes, nothing dispatches


def test_remote_off_still_reports_the_other_failing_condition_first() -> None:
    d = decision.decide(GATED, green(), NOW, None, None, decision.MERGE, OPEN, remote_off="off")
    assert d.verdict == "REFUSE(feature-complete)"  # an incomplete feature does not land locally either
    d2 = decision.decide(DIRECT, green(), NOW, None, None, decision.CHECK, None, remote_off="off")
    assert d2.verdict == "REFUSE(route-is-gated)"


def test_remote_off_does_not_short_circuit_a_full_scope_on_a_reference_record() -> None:
    local = decision.VerifiedRecord("t", "local:make-done@abc", "reference")
    d = decision.decide(GATED, green(), NOW, local, None, decision.MERGE, COMPLETE, scope="full", remote_off="off")
    assert d.verdict == "REFUSE(remote-enabled)"
