"""The DispatchDecision: every condition, evaluated and printed even after one fails (pure).

Order (plan, design note 1): route -> feature-complete (merge only) -> green-local-since-edit ->
tree-not-already-verified -> breaker. The breaker is last because it is the only one that costs an
AWS call; the caller supplies its answer. Verdict = the FIRST failing condition, or SKIP-VERIFIED,
or DISPATCH - but every row is reported, because the project's rule is that failures are reported
together so the session sees the whole picture in one turn.

FR-027: a verified record carries its SCOPE. A `reference` record does not satisfy a FULL merge; a
`full` record satisfies either.
"""

from __future__ import annotations

from dataclasses import dataclass

from l7r.diagram.ci import config
from l7r.diagram.ci.delta import Delta
from l7r.diagram.ci.features import FeatureStatus
from l7r.diagram.ci.state import GREEN, VerificationState

MERGE = "merge"
CHECK = "check"
# The measurement route (feature 177). A THIRD mode rather than a flag on `check`, because it needs a
# buildspec of its own - `buildspec/measure.yml`, whose `MODE` makes `run.sh` write no `verified/`
# record and never push. That is FR-009 enforced where it can be READ IN A DIFF, which is the bar
# `door.py` set for this package: what a paid run may do is not something the dispatcher promises.
MEASURE = "measure"


@dataclass(frozen=True)
class Condition:
    name: str
    passed: bool
    why: str


@dataclass(frozen=True)
class VerifiedRecord:
    tree: str
    build_id: str
    scope: str  # reference | full
    utc: str = ""

    def satisfies(self, scope: str) -> bool:
        return self.scope == "full" or scope == "reference"


@dataclass(frozen=True)
class Estimate:
    minutes: float
    cost_usd: float
    month_to_date_usd: float


@dataclass(frozen=True)
class DispatchDecision:
    conditions: tuple[Condition, ...]
    estimate: Estimate
    verdict: str  # DISPATCH | SKIP-VERIFIED | REFUSE(<condition>)

    @property
    def dispatches(self) -> bool:
        return self.verdict == "DISPATCH"

    @property
    def skip_verified(self) -> bool:
        return self.verdict == "SKIP-VERIFIED"


def estimate(scope: str, month_to_date_usd: float, operation: str | None = None) -> Estimate:
    minutes = config.ESTIMATE_MINUTES["operation" if operation else scope]
    return Estimate(minutes=minutes, cost_usd=round(minutes * config.RATE_PER_MIN, 2), month_to_date_usd=round(month_to_date_usd, 2))


def decide(
    delta: Delta,
    state: VerificationState | None,
    now_hash: str,
    verified: VerifiedRecord | None,
    breaker: str | None,
    mode: str,
    feature: FeatureStatus | None,
    scope: str = "reference",
    month_to_date_usd: float = 0.0,
    operation: str | None = None,
    remote_off: str | None = None,
    measure: bool = False,
) -> DispatchDecision:
    conds: list[Condition] = []
    # REMOTE OFF IS THE FIRST ROW (feature 132). The GM's reusable switch: *"if it is disabled, then
    # we do not use it as a gate. and we do not dispatch to it."* It is reported first because it
    # is the one fact that makes every other row moot for DISPATCH - and it is NOT the first
    # refusal: with remote off, a merge whose engine content a green local `make done` vouches for
    # still lands (SKIP-VERIFIED, the LOCAL-GATED route), so the other conditions are judged first
    # and remote-off only decides between "push on the local verdict" and "nothing happens".
    conds.append(Condition("remote-enabled", remote_off is None, remote_off or "remote is on (dev/switches.json)"))
    # THE MEASUREMENT ROUTE BYPASSES THIS CONDITION AND ONLY THIS ONE (feature 177, FR-009a).
    # A measurement of what the remote gate COSTS has, by construction, no engine delta to point at:
    # feature 175 owed a FULL-scope cache timing, could not take it because `ci-check` requires one,
    # wrote *"it rides on the next real engine change"* - and four features later it had not been
    # taken. A debt that can only be paid by waiting for unrelated work is not a debt anyone pays.
    # The row is still PRINTED, with the bypass named in it, because this package's rule is that
    # every condition is reported even when it does not decide anything.
    conds.append(Condition("route-is-gated", delta.route == "GATED" or measure, delta.reason if not measure else f"{delta.reason} - BYPASSED: a measurement has no engine delta to point at (FR-009a)"))
    if mode == MERGE:
        f = feature or FeatureStatus(name=None)
        conds.append(Condition("feature-complete", f.complete, f.why))
    if state is None:
        conds.append(Condition("green-local-since-edit", False, "no local check recorded - run `make quick` (or reference / test-file / a local done) first"))
    elif state.event != GREEN:
        conds.append(
            Condition("green-local-since-edit", False, f"the last gate FAILED (`make {state.target}` at {state.utc}) - run `make quick` (or reference / test-file) green before dispatching again")
        )
    elif state.hash != now_hash:
        conds.append(
            Condition("green-local-since-edit", False, f"`make {state.target}` was green at {state.utc}, but the code changed since - that run vouched for different code; run `make quick` again")
        )
    else:
        conds.append(Condition("green-local-since-edit", True, f"`make {state.target}` green at {state.utc} against exactly this code"))
    # AN OPERATION IS NEVER SHORT-CIRCUITED: a verified record says a GATE passed on this tree; it says
    # nothing about a cohort or a cache audit (the first cohort dispatch, 2026-08-25, was skipped by
    # the reference record the same tree had just earned).
    if operation or measure:
        verified = None  # a measurement must actually RUN; a record says a gate passed, not what it cost
    if verified is not None and verified.satisfies(scope):
        who = "a green local `make done` on exactly this engine content (main adds none)" if verified.build_id.startswith("local:") else f"{verified.build_id}"
        conds.append(Condition("tree-not-already-verified", False, f"this engine content was verified {verified.scope}-scope by {who} - no second build (SKIP-VERIFIED)"))
    elif verified is not None:
        conds.append(Condition("tree-not-already-verified", True, f"verified only at {verified.scope} scope by {verified.build_id}; a {scope} run is still owed"))
    else:
        conds.append(Condition("tree-not-already-verified", True, "no verified record for the tree this would land"))
    conds.append(Condition("breaker-not-tripped", breaker is None, breaker or "the monthly hard stop has not tripped"))

    est = estimate(scope, month_to_date_usd, operation)
    failing = [c for c in conds if not c.passed and c.name not in ("tree-not-already-verified", "remote-enabled")]
    if failing:
        verdict = f"REFUSE({failing[0].name})"
    elif verified is not None and verified.satisfies(scope):
        verdict = "SKIP-VERIFIED"
    elif remote_off is not None:
        verdict = "REFUSE(remote-enabled)"  # LOCAL-GATED with nothing local to vouch for it: nothing dispatches
    else:
        verdict = "DISPATCH"
    return DispatchDecision(conditions=tuple(conds), estimate=est, verdict=verdict)


def render(d: DispatchDecision, mode: str, scope: str) -> str:
    """FR-014: the whole picture, before a cent is spent."""
    lines = [f"ci-{mode} ({scope} scope) - dispatch conditions:"]
    for c in d.conditions:
        lines.append(f"  [{'ok' if c.passed else '--'}] {c.name:<26} {c.why}")
    e = d.estimate
    lines.append(f"  estimate: ~{e.minutes:.0f} build-min at ${config.RATE_PER_MIN:.2f}/min = ~${e.cost_usd:.2f}; month-to-date remote spend ${e.month_to_date_usd:.2f}")
    lines.append(f"  verdict: {d.verdict}")
    return "\n".join(lines)
