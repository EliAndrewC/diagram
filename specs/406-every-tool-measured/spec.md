# Feature 406 - every tool measured by what it does

**Feature Branch**: none (worked on `main` in a session clone)

**Created**: 2026-10-19

**Status**: In progress

**Approved**: the GM, 2026-10-19, "Yes, go ahead and do this as a process feature. So go ahead and file it and then fully implement it. And let me know when it is landed on main. Thanks."
**Approved**: the GM, 2026-10-26, "Sounds great. I approve all of that. So please do it end to end. Thanks."

Reopened 2026-10-26 for T09, the fix-yield re-run a retired session memory carried.

**Affects**: tooling, review process

**Request**: `request.md` (the GM's words and the proposal he approved, verbatim)

## Why

`make fix-yield` (feature 385 T119) judged each tooling fix by how often a command its measure names ran per session hour,
before and after the fix - measures assigned after the fact, and a rate that rises when a fix is used and moves with the hour's
mix of work. The GM: "Whether or not it's doing something for us should be a measurable question", for "basically ... every
tool", with "a way that it is notionally possible for us to see how often a tool is used ... Or how often it makes a difference".

## User Story 1 - how often each tool is used, and how often it changes the outcome (P1)

The GM, or a step-back, runs one command and sees, for every tool of the project, its uses per week, its interventions (the times
it changed what happened), its likely misfires, and when it was first seen - or that it is too new to say.

**Independent Test**: `make tool-yield` prints every wired hook, refusing check, make target, review check and logged automatic
step, listed from the code - a tool that never fired reads 0 - each with those columns or "no outcome record".

## User Story 2 - no tool without a signal (P1)

A tool added later is measurable from the day it lands, because the tooling refuses one that records nothing.

**Independent Test**: a wired hook or a refusing check that records nothing (unless it names the record that sees it), or a
usage-log call the registry does not list, fails the check `make hooks-test` runs.

## User Story 3 - the 22 fixes judged on evidence (P2)

The tooling fixes `fix-yield` read as "saves nothing" are judged on what their tools did since they landed.

**Independent Test**: `make fix-yield` reports, per made fix, the tools it changed and their numbers since it was made, and each
of the 22 carries a recorded judgment - doing something, doing nothing, or too new to say - in a file the GM's review reads.

## Requirements

- **FR-001 (the report)**: `make tool-yield` reports every tool, listed from the code, not from what has fired - every hook wired
  in `.claude/settings.json`; every gate or check script that can refuse work (what `make done`, `make quick`, the push and `make
  tick` run, `scripts/gates/` and the `scripts/` checks among them); every make target in the Makefile; every review check (a
  `.claude/agents/` type); every logged automatic step. For each: first seen, uses in the last 7 days and in all, interventions,
  likely misfires, and "too new" only where it was first seen under 7 days ago (an older tool reports its numbers, however
  small). A tool that has never fired reads 0 uses; a tool whose record cannot show an outcome reads "no outcome record", never 0.
  By kind:
  - a guard or check: interventions are its blocks, refusals, rewrites, reminders and warnings; likely misfires its escapes;
  - a make target: interventions are its runs that failed or refused; likely misfires its runs refused and then escaped (an
    escape token on the next run of the same target);
  - a review check: interventions are its passes with a finding acted on (the review ledger's `acted on`); likely misfires its
    findings declined and its `MISSED-BY-REVIEWER` rows; a check with no ledger rows reads its dispatches and "no outcome record";
  - an automatic step: interventions are its runs that changed something; likely misfires its runs undone afterward where the
    step records that, else "no outcome record".
- **FR-002 (no trace, no tool)**: every automatic step that changes an outcome without a guard's firing or a target's run of its
  own, and every refusing check that logs no firing, records each run through one shared usage-log helper
  (`<git common dir>/tool-usage.jsonl`: utc, tool, kind, outcome), and every tool that records through the helper - each automatic
  step and each refusing check - is listed in one registry with what it does.
- **FR-003 (target outcomes)**: a make target's run records its outcome: the event log records a failed tool call (the hook
  event a failure fires) beside a succeeded one, so every target run in a session reads succeeded or failed; runs the event log
  cannot see - a target run by a timer outside any session (`make idle-tests`) or from inside another script - record through
  FR-002's helper, and the report names any it still cannot see.
- **FR-004 (the rule)**: a check run by `make hooks-test` refuses a wired hook, or a refusing gate or check script, that records
  nothing (no `guard_log` and no usage-log call) unless its exemption names the record where its runs and outcomes can be seen
  (the event-log hook is its own record); a usage-log call naming a tool the registry lacks; and a registry entry no code calls.
- **FR-005 (the fixes, judged)**: `make fix-yield` reports each tooling fix the round arbiter named by the tools its change
  touched and their FR-001 numbers since the fix was made, replacing the command-rate measure, and the step-back bundle reads
  the same. As the report's first use, each of the 22 fixes that read "saves nothing" gets a recorded judgment - doing something,
  doing nothing, or too new to say - citing its numbers, delivered to the GM.

## Success Criteria

- **SC-001** (FR-001, FR-003): `make tool-yield` lists every wired hook, refusing check, make target, review check and logged
  step, with numbers, "too new" or "no outcome record", and a test red without each kind's reading; a target's failed run reads
  failed.
- **SC-002** (FR-002, FR-004): the rule's check fails on a hook or check that records nothing and on an unregistered tool, with
  tests red without it; every hook and check the inventory finds recording nothing either records or names its record.
- **SC-003** (FR-005): each of the 22 fixes carries a judgment citing its tools' numbers since it was made, in a file the GM's
  review reads.

## Review history

- **spec-fidelity round 1 (2026-10-19): CHANGES REQUIRED, 6 items.** The structure followed the approved four-item proposal,
  but six points did not do what it said; all six applied.
- **spec-fidelity round 2 (2026-10-19, verify): CHANGES REQUIRED, 1 item.** Round 1's six fixed; the rewrite set FR-002 against
  FR-004. Applied.
- **spec-fidelity round 3 (2026-10-19, verify): FAITHFUL.** Round 2's item fixed, no contradiction introduced.
- **Plan review (MODE 4), rounds 1-3 (2026-10-20): BLOCKED.** D161 (counting runs and matching outcomes), D163/D164's reach and
  the target-body exemption, and D165/D166 (the fix's tools; the judgment order), each answered in the plan. The round arbiter
  ruled `continue` at round 3 and `accept` for round 4 (round:spec-fidelity|plan:406-every-tool-measured#T01@4): the rounds
  converged, and a fourth would re-read its own prescriptions.
