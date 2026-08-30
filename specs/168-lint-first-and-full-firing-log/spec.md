# Feature Specification: Lint First, and a Firing Log Worth Reading

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=168-lint-first-and-full-firing-log`)

**Created**: 2026-08-30

**Status**: Draft - awaiting `spec-fidelity`

**Input**: [`request.md`](request.md), verbatim and unedited.

## The feature, in one sentence

Two things the GM picked off a list of three: the gate runs its 1.8 s of static checks before its
29 s map roll, on principle rather than for a saving, and the firing log stops covering two guards
out of twelve so that the next question of the form *"is this guard worth what it costs"* can be
answered from the record instead of from a transcript replay.

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

**IN scope**: the phase order of `make done`; `scripts/_guardlog.sh` and the ten guards that do not
yet record; the census `make audit` prints; the companion suites of every guard touched.

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

### FR-002 - every guard that refuses or corrects records what it did

The ten guards that do not yet write to the firing log do so: `batching`, `no-branch`, `discard`,
`guard-file`, `repo-safety`, `source-block`, `readme`, `clone-sync`, `review-gate` and the
`pair` stop branch. Each records the same shape the two existing ones do - guard, event, session,
and the command or path it fired on.

`batching` is the reason this is worth doing: 119 firings in six days, more than every other guard
combined, and not one of them recorded.

### FR-003 - a firing says WHICH RULE fired, not only which guard

Each entry carries a short rule slug naming the branch that fired, because several guards enforce
more than one thing and "no-poll fired 32 times" cannot tell anybody which of its three rules is
carrying the cost. `no-poll` distinguishes its busy-wait, disguised-sleep and process-match rules;
`repo-safety` its force-push, history-rewrite and host-repo rules; `make-only` its five verdicts;
and so on for any guard with more than one branch.

This is the GM's *"record more data for us to be able to use to make improvements in the future"*: the
unit a future improvement acts on is a RULE, not a script.

### FR-004 - the census reports it

`make audit` reports, per guard: firings by event, the escape rate, and the rules that fired most.
A guard with one rule prints as it does today.

### FR-005 - no suite writes fixture events into the real log

Every companion suite of every newly-recording guard isolates `GUARD_LOG_DIR` for the whole file and
asserts it was never dropped, exactly as features 162 and 164 established. A census polluted by its
own tests answers nothing, and that has already happened once (24 entries).

## Success Criteria

- **SC-001**: `make done` runs lint, format and typecheck before rolling the reference settlement, and a failure in any of them is reported without the roll.
- **SC-002**: the gate's phases and their contents are otherwise unchanged, and `make done` is green.
- **SC-003**: each of the ten guards writes an entry when it fires, with the rule slug set.
- **SC-004**: `make audit` prints the per-rule breakdown, and prints sensibly when the log is empty.
- **SC-005**: running every guard suite leaves the real firing log with zero new entries.
- **SC-006**: not one guard refuses, permits or corrects anything it did not before - every companion suite is green with its existing vectors unchanged apart from the log isolation.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| static phases before the map roll | GM ruling, taken on principle with the measured saving (~4 min historically) stated rather than inflated | FR-001 |
| all twelve guards record | GM ruling; `batching` alone fired 119 times unrecorded | FR-002 |
| an entry names the RULE, not just the guard | the GM's "record more data ... to make improvements"; a future fix acts on a rule | FR-003 |
| the gate's rising median is NOT touched here | the GM handed it to another session | Scope |
