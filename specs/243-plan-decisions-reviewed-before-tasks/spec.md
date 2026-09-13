# Feature 243 - plan decisions are reviewed before tasks are ticked

**Created**: 2026-09-13
**Status**: DRAFT (round 2 CHANGES REQUIRED applied; round 3 next)
**Input**: the GM's request, verbatim, in `request.md`

## Summary

Constitution Principle XVI requires an independent `spec-fidelity` check before an exception to an
accepted rule reaches the GM. A spec is checked at push by `review-gate.sh`; a PLAN is written after the
spec's verdict and nothing reads it, so a plan decision that narrows the spec can reach implementation,
every ticked task and main without the check. Feature 239 shipped two narrowings of its accepted spec
without that check: one was a decision in its plan (P2), the other was written only in code. Catching and
removing both after landing was the avoidable part of that feature's time (`research.md` R1). The GM
approved a plan-stage gate: tasks are not ticked while a plan's decisions lack a recorded independent
verdict.

## Functional requirements

**FR-001** `make tick` MUST refuse to tick a task in a feature that has no CURRENT plan review recorded,
naming what is owed and how to get it. A feature with a `tasks.md` and no `plan.md` is refused the same
way: the plan stage of the spec-kit flow is owed before its review can be (D5).

**FR-002** The plan review MUST be performed by the independent reviewer reading the WHOLE plan, not by
the author labeling which decisions narrow what was asked (D1). The reviewer lists every decision the plan
makes that the spec does not already settle, classifies each as within what was asked or narrowing what
was asked - the GM's request as written and the accepted spec - and for each narrowing decision gives the
MODE 1 ruling, LEGITIMATE or NOT LEGITIMATE.

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

**FR-007** The push MUST refuse, from `sync-with-main.sh` beside `review-gate.sh`, any feature whose
`specs/NNN-*/` directory the delta touches - the set `review-gate.sh` check 1 judges - that has at least
one ticked task while its plan review is not CURRENT and CLEAR, a feature with ticked tasks and no
`plan.md` included. A tick made by a hand edit of `tasks.md` rather than through `make tick` is refused
here (D4). A feature with no ticked task - a plan still being drafted - passes (D3).

**FR-008** Both refusals MUST carry an escape, `PLAN_REVIEW_OK="<reason>"`, whose reason is required and
logged in the manner of every escape since feature 170.

**FR-009** `.claude/agents/spec-fidelity.md` MUST document the plan review as its own mode: that it is
given the GM's `request.md` verbatim together with `spec.md` and `plan.md`, that it lists the decisions
itself, how it classifies and rules them, and the make target that records the result.

**FR-010** `.specify/templates/tasks-template.md` MUST carry the plan review as the first task of a
feature, so the checklist states the step the gate enforces (D6). That task is ticked after the record
exists, so FR-001 does not refuse it.

## Success criteria

**SC-001** (FR-001, FR-003, FR-004) `make tick` refuses with no `plan-review.json`, refuses with one whose
digest does not match `plan.md`, refuses a feature with a `tasks.md` and no `plan.md`, and ticks with a
current CLEAR review.
**SC-002** (FR-002, FR-009) The agent file documents the plan review mode, is given `request.md` verbatim
beside the spec and the plan, and has the reviewer list decisions itself rather than read a list the
author supplies.
**SC-003** (FR-005) A current BLOCKED review refuses ticking.
**SC-004** (FR-006) The recording target declines without the reviewer's declaration and writes the
record with it.
**SC-005** (FR-007) A push touching a feature with a ticked task and no current CLEAR review is refused,
including one ticked by a hand edit and one with no `plan.md`; a push of a feature with no ticked task
passes.
**SC-006** (FR-008) The escape permits the tick and the push, and is refused without a reason.
**SC-007** (FR-010) The tasks template's first task is the plan review.
**SC-008** (spec-wide) Every refusal is proven to fire by breaking it and watching a test go red.
**SC-009** (spec-wide) `make hooks-test`, `make quick` and `make done` are green, and this feature's own
tasks were ticked under the gate it adds, after its own plan was reviewed.

## Decisions recorded

**D1 - the reviewer finds the decisions; the author does not label them.** The proposal read literally
is a gate over the decisions the author marks as narrowing. Feature 239's plan, as first committed,
framed P2 as a question the spec left open, not as a narrowing: *"check 5 applies to features numbered
239 and later. The spec says a figure with a unit must carry a key; it does not say whether that reaches
the 238 specs written before the rule existed."* A gate over author-marked decisions would have passed
that plan untouched, so the literal reading defeats the purpose it was approved for (`research.md` R1).
That no existing plan labels its decisions in a common form is supporting detail only (R2).

**D2 - the review is keyed on the whole plan's digest.** A digest of only the decisions would need the
decisions to be found by a script, which D1 rules out. The cost is that any edit to `plan.md` owes a new
review before the next tick; that is accepted because the plan edit is the moment a narrowing decision
arrives.

**D3 - a draft plan pushes; an implemented one does not.** The push gate applies once a task is ticked.
Refusing every push of an unreviewed plan would refuse the milestone push of a plan still being written.

**D4 - the push refusal is required, not optional.** `make tick` is not the only way a box gets ticked:
no hook refuses a hand edit of `tasks.md` (`research.md` R3). A gate only at tick time can be walked
around by the edit the tick command replaced, so FR-007 is where the gate holds.

**D5 - a feature with tasks and no plan is refused, not passed.** Letting it pass would make skipping the
plan the way around the gate, which is an exception to the rule. Reviewing `tasks.md` in the plan's place
was priced and declined: every tick rewrites `tasks.md`, so its digest cannot key a review without
normalizing away the text a tick writes, and the spec-kit flow this project runs puts a feature's
decisions in its plan (specify, plan, tasks, implement). The cost is that a small feature writes a short
`plan.md`.

**D6 - the template task follows the project's practice of review steps as tasks.** The tasks template
already carries the spec review as a task, and the GM's approved item 6 of feature 236 (2026-09-12)
encodes a re-review as a `tasks.md` shape rather than a constitution sentence (`specs/236-*/request.md`).
The plan review is written the same way.

## Out of scope

- A narrowing made only in code, never written into the plan, is not reached by this gate: the reviewer
  reads the plan. The second of feature 239's two narrowings was of that kind.
- Older features. A push that touches an older feature with ticked tasks - all of them lack a
  `plan-review.json`, and many lack a `plan.md` - is refused until it is reviewed or escaped with a
  reason. No feature-number cutoff is made: that scoping was ruled NOT LEGITIMATE on feature 239
  (`specs/239-*/tasks.md` T17). No exemption for a fully ticked feature is made either, on its own
  ground: Principle XVI presumes an exception wrong, and feature 239 was fully ticked when its narrowings
  were pushed, so that exemption would let through the incident this gate exists for (`research.md` R1).
  The GM accepted this kind of cost for older specs on 2026-09-13:
  *"I'm not worried about older specs; we don't usually edit older specs so that's fine."*
  (`specs/239-*/request.md`).
- Judging whether the plan is GOOD. The review rules on fidelity to what was asked, not on design quality.

## Review history

- Round 1 (MODE 2, initial review): CHANGES REQUIRED, 8 items. All three departures were judged LEGITIMATE
  on corrected grounds. Applied: the Summary's account of 239; D1 rebuilt on P2's original wording; the
  R2 count restated with its command; R3's claim about `make tick` corrected, with D4 added; FR-007's
  scope defined and the older-features consequence stated; a feature with no `plan.md` (D5); the
  reviewer given `request.md` verbatim; the ground for FR-010 (D6).
- Round 2 (MODE 3 VERIFY): CHANGES REQUIRED, 2 items. Applied: the R2 counts pinned to a commit so they
  reproduce; the fully ticked exemption declined on its own ground rather than on 239's ruling, which
  covered only the feature-number cutoff.
