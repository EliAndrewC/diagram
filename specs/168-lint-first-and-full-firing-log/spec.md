# Feature Specification: Lint First, and a Firing Log Worth Reading

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=168-lint-first-and-full-firing-log`)

**Created**: 2026-08-30

**Status**: Draft - awaiting `spec-fidelity`

**Input**: [`request.md`](request.md), verbatim and unedited.

## The feature, in one sentence

Two things the GM picked off a list of three: the gate runs its 1.8 s of static checks before its
29 s map roll, on principle rather than for a saving, and every guard BRANCH that refuses, corrects
or teaches records what it did - naming the RULE that fired, not merely the script - so that the next
question of the form *"is this guard worth what it costs"* is answered from the record instead of
from a transcript replay.

## Why this exists (the GM's words - `request.md` is the authority)

- *"On general principle, we should probably make linting go first. So you can go ahead and do that
  reorder, but I don't think that it will yield an efficiency improvement."*
- *"It also sounds like the firing log should record more data for us to be able to use to make
  improvements in the future. So please add that."*

And, equally binding, what this feature does NOT do:

- *"I agree that the gate getting slower is the most important thing, but I will hand that off to a
  different session."* The 35 s -> 148 s rise is out of scope here, and the findings are already with
  the GM.

## What was measured before specifying

| | |
|---|---|
| the gate's `lint` phase | `ruff check --fix` - **autocorrects**, as the GM said |
| the gate's `format` phase | `ruff format` (not `--check`) - **autocorrects** |
| gate runs that failed on a static phase ALONE | **8 of 317** (3 format, 2 lint, 2 typecheck, 1 lint+typecheck) |
| what the reorder therefore recovers | ~29 s x 8 = **about 4 minutes, across the whole recorded history** |
| `batching` firings in six days, recording nothing | **119** - more than every other guard combined |

The first three lines are the GM's premise, confirmed. This spec claims no efficiency improvement
from FR-001 and says why in the requirement itself, so that a later reader does not credit it with
one.

## Scope, stated exactly

**IN scope**: the phase order of `make done`; `scripts/_guardlog.sh` and every guard BRANCH that acts
without recording (FR-002 derives the set); the rule breakdown in the census; the companion suites of
every guard touched.

**OUT of scope**: what any guard FORBIDS or CORRECTS - not one refusal changes; which phases the gate
runs, or what any of them do; the gate's rising median, which the GM has handed to another session;
`make quick`, whose own lint already runs first.

## Requirements

### FR-001 - the static phases run before the map roll

`make done` runs `lint`, `format` and `typecheck` before `reference`, instead of after it. Every
phase, and everything each one does, is unchanged; only the order moves.

**This is done on principle and buys almost nothing, which the GM said plainly and the record
confirms**: both static phases autocorrect, so they rarely fail at all, and only 8 of 317 recorded
gate runs failed on one without also failing the suite. It remains right that the cheapest check
runs first - a session that has broken something ruff cannot fix hears about it in 1.8 s rather than
31 s - and this requirement is not to be defended later with a saving it does not deliver.

It does not weaken the rule that the reference settlement gates everything expensive: the phases
moved ahead of it are cheaper than it by a factor of 16, and everything expensive still stands
behind it.

### FR-002 - the criterion, not a hand-list: every branch that acts records

**Every branch of every guard that BLOCKS, REWRITES, REMINDS, PERMITS or IS ESCAPED records one
entry**, and the
in-scope set is DERIVED from `scripts/*-hooks.sh` plus `review-gate.sh` at implementation time rather
than copied from a list in this document.

`spec-fidelity` round 1 caught the first draft asserting "two guards out of twelve" and naming ten
that "do not yet write to the firing log" - a census that predates this session's own feature 164,
which added recording to five more. Measured in this tree now:

| already records | on which branches | still uncovered |
|---|---|---|
| `measure` | blocked, escaped, reminded | - |
| `no-poll` | blocked, permitted, rewrote | - |
| `house-style` | blocked, rewrote | - |
| `gate` | rewrote | its `-k` subset BLOCK |
| `make-only` | rewrote | its five refusal verdicts |
| `pair` | rewrote | its two blocks and the stop branch |
| `guard-file` | reminded | its block |
| `batching`, `discard`, `no-branch`, `readme`, `repo-safety`, `source-block`, `clone-sync`, `agent-stall`, `review-gate` | nothing | every branch |

**`idle-tests` is OUT OF CLASS, and the reason is stated rather than assumed**: it never refuses,
rewrites or corrects a session's command - it is a RUNNER, whose branches (the host-wide lock, the
one-run-per-idle rule, the suspend restart) decide what an unattended process does with its own time.
Nothing it does costs a session a round trip, which is the cost this log exists to measure, and it
already keeps its own record in `dev/idle-log/`. `agent-stall` IS in class: its stall report is a
remind-shaped branch aimed at the session.

So the work is mostly BRANCHES inside guards that already record, plus TEN scripts recording nothing
at all - including `agent-stall`, `idle-tests` and `review-gate`, which the first draft did not
mention (`spec-fidelity` rounds 1 and 2 found each of those omissions in a hand-written census, which
is why the set is derived rather than listed).

**AN ESCAPE IS A BRANCH, and it is the one that matters most.** `measure` records `escaped` for
`MEASURE_OK`; nothing else records its escape at all, so the escape RATE - the number this project
has actually acted on, and the reason feature 162 retired a refusal that was escaped 62% of the
time - is computable for exactly one guard today. A branch that lets a command through on
`GATE_OK`, `PAIR_OK`, `DISCARD_OK`, `NO_BRANCH_OK`, `REVIEW_GATE_OK`, `SOURCE_EDIT_OK`,
`GUARD_EDIT_OK` or `POLL_OK` records like any other.

`batching` remains the reason this is worth doing: **119 firings in six days**, more than every other
guard combined, none of them recorded.

### FR-003 - an entry names the RULE that fired

Every entry written under FR-002 carries a short rule slug naming the branch, because several guards
enforce more than one thing and *"no-poll fired 32 times"* cannot say which of its three rules is
carrying the cost. `no-poll` distinguishes busy-wait, disguised-sleep and process-match; `repo-safety`
force-push, history-rewrite and host-repo; `make-only` its five verdicts; `clone-sync` its five
refusals. A guard with a single branch records that one slug.

This is the GM's *"record more data for us to be able to use to make improvements in the future"*: the
unit a future improvement acts on is a RULE, not a script.

### FR-004 - the census gains the rule breakdown, and nothing else

`make audit` ALREADY prints, per guard, firings by event and the escape rate (feature 162) - so the
delta is one line, not a new report: the rules that fired most, for any guard with more than one. A
single-rule guard prints exactly as it does today, and an empty log prints as it does today.
`spec-fidelity` round 1 caught this requirement re-specifying work that is already done.

### FR-005 - no suite writes fixture events into the real log

Every companion suite of every newly-recording guard isolates `GUARD_LOG_DIR` for the whole file and
asserts it was never dropped, exactly as features 162 and 164 established. A census polluted by its
own tests answers nothing, and that has already happened once (24 entries).

## Success Criteria

- **SC-001**: `make done` runs lint, format and typecheck before rolling the reference settlement, and a failure in any of them is reported without the roll.
- **SC-002**: the gate's phases and their contents are otherwise unchanged, and `make done` is green.
- **SC-003**: every branch that blocks, rewrites, reminds, permits or is escaped writes an entry when it fires, with the rule slug set - proved by driving each guard's own suite and counting entries by rule, not by reading the source. In particular each escape token (`GATE_OK`, `PAIR_OK`, `DISCARD_OK`, `NO_BRANCH_OK`, `REVIEW_GATE_OK`, `SOURCE_EDIT_OK`, `GUARD_EDIT_OK`, `POLL_OK`, `MEASURE_OK`) produces an `escaped` entry.
- **SC-004**: `make audit` prints the per-rule breakdown, and prints sensibly when the log is empty.
- **SC-005**: running every guard suite leaves the real firing log with zero new entries.
- **SC-006**: not one guard refuses, permits or corrects anything it did not before - every companion suite is green with its existing vectors unchanged apart from the log isolation.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| static phases before the map roll | GM ruling, taken on principle with the measured saving (~4 min historically) stated rather than inflated | FR-001 |
| the in-scope set is a CRITERION, derived at implementation time | a hand-list went stale inside one session - the first draft described the tree as it was before feature 164 | FR-002 |
| an entry names the RULE, not just the guard | the GM's "record more data ... to make improvements"; a future fix acts on a rule | FR-003 |
| the gate's rising median is NOT touched here | the GM handed it to another session | Scope |

## Review history

Constitution XVI: reviewed against the GM's request AS WRITTEN (`request.md`), by an independent
`spec-fidelity` subagent, before implementation - three rounds.

| round | verdict | what it found |
|---|---|---|
| 1 | CHANGES REQUIRED | the census of which guards already record described the tree as it was BEFORE this same session's feature 164, which had added recording to five more; and FR-004 re-specified a census line feature 162 had already built. Fixed: the in-scope set became a derived CRITERION, and FR-004 shrank to the actual delta |
| 2 | CHANGES REQUIRED | the list of recording verbs omitted ESCAPED - the escape RATE is the lever this project has actually acted on (feature 162 retired a refusal escaped 62% of the time) - and `idle-tests` and `review-gate` were missing from the scope discussion. Fixed: the escape branch runs throughout, and `idle-tests` is ruled out of class with its reason |
| 3 | **FAITHFUL** | final round, verdict FAITHFUL: clause-by-clause against the request, both directions. It independently checked the one carve-out rather than accepting the argument - reading `scripts/idle-tests-hooks.sh` for an `exit 2`, an `updatedInput` or an `additionalContext`, finding none, and confirming `idle-tests` is a runner rather than an exception to the rule |

**One note from round 3, recorded because it is a real tension rather than a fidelity defect.**
SC-001 says a static failure is *"reported without the roll"*, which reads as fail-fast, while FR-001
says *"only the order moves"* and this repository's standing rule is that `make done` reports all
failures together. The implementation satisfies both, and deliberately: the three static phases run
as a group and are collected together, so a run that breaks two of them reports both; the gate then
stops before the reference roll rather than continuing. If the two are ever read against each other,
FR-001 is the binding one.
