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
) -> DispatchDecision:
    conds: list[Condition] = []
    conds.append(Condition("route-is-gated", delta.route == "GATED", delta.reason))
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
    if operation:
        verified = None
    if verified is not None and verified.satisfies(scope):
        conds.append(Condition("tree-not-already-verified", False, f"this exact tree was verified {verified.scope}-scope by {verified.build_id} - no second build (SKIP-VERIFIED)"))
    elif verified is not None:
        conds.append(Condition("tree-not-already-verified", True, f"verified only at {verified.scope} scope by {verified.build_id}; a {scope} run is still owed"))
    else:
        conds.append(Condition("tree-not-already-verified", True, "no verified record for the tree this would land"))
    conds.append(Condition("breaker-not-tripped", breaker is None, breaker or "the monthly hard stop has not tripped"))

    est = estimate(scope, month_to_date_usd, operation)
    failing = [c for c in conds if not c.passed and c.name != "tree-not-already-verified"]
    if failing:
        verdict = f"REFUSE({failing[0].name})"
    elif verified is not None and verified.satisfies(scope):
        verdict = "SKIP-VERIFIED"
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
