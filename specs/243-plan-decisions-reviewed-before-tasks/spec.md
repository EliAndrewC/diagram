# Feature 243 - plan decisions are reviewed before tasks are ticked

**Created**: 2026-09-13
**Status**: DRAFT (awaiting `spec-fidelity`)
**Input**: the GM's request, verbatim, in `request.md`

## Summary

Constitution Principle XVI requires an independent `spec-fidelity` check before an exception to an
accepted rule reaches the GM. A spec is checked at push by `review-gate.sh`; a PLAN is written after the
spec's verdict and nothing reads it, so a plan decision that narrows the spec can reach implementation,
every ticked task and main without the check. Feature 239 did exactly that twice, and the loop of
catching and removing it after landing was the avoidable part of that feature's time (`research.md` R1).
The GM approved a plan-stage gate: tasks are not ticked while a plan's decisions lack a recorded
independent verdict.

## Functional requirements

**FR-001** `make tick` MUST refuse to tick a task in a feature whose `plan.md` has no CURRENT plan review
recorded, naming what is owed and how to get it.

**FR-002** The plan review MUST be performed by the independent reviewer reading the WHOLE plan, not by
the author labeling which decisions narrow the spec: plans label decisions in no common form, and the
failure this gate exists for is an author not seeing that a decision narrows the spec (`research.md` R2).
The reviewer lists every decision the plan makes that the spec does not already settle, classifies each
as within the spec or narrowing it, and for each narrowing decision gives the MODE 1 ruling - LEGITIMATE
or NOT LEGITIMATE.

**FR-003** The review MUST be recorded in `specs/NNN-*/plan-review.json` with the digest of the `plan.md`
it read, the date, each decision with its class and ruling, and an overall verdict: CLEAR when no
narrowing decision stands ruled NOT LEGITIMATE, BLOCKED otherwise.

**FR-004** A plan review is CURRENT only while `plan.md` is byte-identical to what it read. A plan edited
after its review owes a new one before the next tick: an edit is how a narrowing decision can arrive
after a review has already cleared the plan, and a review that went on counting would wave it through.

**FR-005** A BLOCKED verdict MUST refuse ticking exactly as a missing review does. The way out is to
change the plan - withdraw or overrule the decision - which makes the review stale and owes a new one.

**FR-006** The record MUST be written through a make target that declines unless the reviewer declares
itself, on the pattern `make perf-confirm ... AS=perf-audit` already uses; the limit that nothing
distinguishes the shells is stated where the target is, as it is there (`research.md` R3).

**FR-007** The push MUST refuse a feature that has at least one ticked task while its plan review is not
CURRENT and CLEAR, from `sync-with-main.sh` beside `review-gate.sh`, so a tick made around `make tick`
does not land. A plan pushed before any task is ticked - a draft - passes.

**FR-008** Both refusals MUST carry an escape, `PLAN_REVIEW_OK="<reason>"`, whose reason is required and
logged in the manner of every escape since feature 170.

**FR-009** `.claude/agents/spec-fidelity.md` MUST document the plan review as its own mode: what it is
given, what it lists, how it classifies and rules, and the make target that records the result.

**FR-010** `.specify/templates/tasks-template.md` MUST carry the plan review as the first task of a
feature, so the checklist states the step the gate enforces.

## Success criteria

**SC-001** (FR-001, FR-003, FR-004) `make tick` refuses with no `plan-review.json`, refuses with one whose
digest does not match `plan.md`, and ticks with a current CLEAR one.
**SC-002** (FR-002, FR-009) The agent file documents the plan review mode, and its instructions have the
reviewer list decisions itself rather than read a list the author supplies.
**SC-003** (FR-005) A current BLOCKED review refuses ticking.
**SC-004** (FR-006) The recording target declines without the reviewer's declaration and writes the
record with it.
**SC-005** (FR-007) A push of a feature with a ticked task and no current CLEAR review is refused; a push
of a plan with no ticked task passes.
**SC-006** (FR-008) The escape permits the tick and the push, and is refused without a reason.
**SC-007** (FR-010) The tasks template's first task is the plan review.
**SC-008** (spec-wide) Every refusal is proven to fire by breaking it and watching a test go red.
**SC-009** (spec-wide) `make hooks-test`, `make quick` and `make done` are green, and this feature's own
tasks were ticked under the gate it adds, after its own plan was reviewed.

## Decisions recorded

**D1 - the reviewer finds the decisions; the author does not label them.** Labeling was priced first -
the author tags each decision and only tagged ones are reviewed - and rejected on the census: one plan
in 112 labels its decisions, and a gate that trusts the author's classification cannot catch the author
missing a narrowing decision, which is the whole incident (`research.md` R1, R2).

**D2 - the review is keyed on the whole plan's digest.** A digest of only the decisions would need the
decisions to be found by a script, which D1 rules out. The cost is that any edit to `plan.md` owes a new
review before the next tick; that is accepted because the plan edit is the moment a narrowing decision
arrives.

**D3 - a draft plan pushes; an implemented one does not.** The push gate applies once a task is ticked.
Refusing every push of an unreviewed plan would refuse the milestone push of a plan still being written.

## Out of scope

- Plans of features whose tasks are already all ticked: they are not ticked again, so the gate never
  reaches them; the GM ruled edits to older specs are rare (feature 239 `request.md`).
- Judging whether the plan is GOOD. The review rules on fidelity to the spec, not on design quality.
