# Feature 406 - every tool measured by what it does

**Feature Branch**: none (worked on `main` in a session clone)

**Created**: 2026-10-19

**Status**: In progress

**Approved**: the GM, 2026-10-19, "Yes, go ahead and do this as a process feature. So go ahead and file it and then fully implement it. And let me know when it is landed on main. Thanks."

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

**Independent Test**: `make tool-yield` prints every guard, make target, review check and logged automatic step, each with those
columns, read from the records the project keeps.

## User Story 2 - no tool without a signal (P1)

A tool added later is measurable from the day it lands, because the tooling refuses one that records nothing.

**Independent Test**: a hook script that logs no firing, or a usage-log step the registry does not list, fails the check that
`make hooks-test` (or the gate) runs.

## User Story 3 - the 22 fixes judged on evidence (P2)

The tooling fixes `fix-yield` read as "saves nothing" are judged on what their tools did since they landed.

**Independent Test**: `make fix-yield` reports, per made fix, the tools it changed and their uses and interventions since it
was made, and the GM's review gets the list.

## Requirements

- **FR-001 (the report)**: `make tool-yield` reports every tool of four kinds - a guard (a `*-hooks.sh` or gate logging through
  `guardlog.sh`), a make target, a review check (a `.claude/agents/` type), an automatic step (a usage-log step) - each with: first
  seen, uses in the last 7 days and in all, interventions, likely misfires, and "too new" where it has under 7 days of record or
  under 5 uses. Interventions and misfires by kind: a guard's blocks, refusals and rewrites, and its escapes (a likely misfire);
  a make target's runs that failed or refused, and their share; a review check's passes with a finding acted on (the review
  ledger's `acted on`) against its clean passes; an automatic step's runs that changed something.
- **FR-002 (no trace, no tool)**: every automatic step that changes an outcome without a guard's firing or a target's run of its
  own records each run through one shared usage-log helper (`<git common dir>/tool-usage.jsonl`: utc, step, changed), and the
  steps are listed in one registry with what each does.
- **FR-003 (the rule)**: a check, run by `make hooks-test`, refuses a hook script under `scripts/hooks/` that logs no firing
  (exempting, with its reason, a hook that refuses nothing), a usage-log call naming a step the registry lacks, and a registry
  step no code calls. Make targets and review checks are measured from records every run already leaves.
- **FR-004 (the fixes)**: `make fix-yield` reports each tooling fix the round arbiter named by the tools its change touched (the
  guards, targets and steps of its landed files) and their FR-001 numbers since the fix was made, replacing the command-rate
  measure; the step-back bundle reads the same.

## Success Criteria

- **SC-001** (FR-001): `make tool-yield` lists every one of the 46 guards in the guard log and every target in the Makefile, with
  numbers or "too new", and a test red without each kind's reading.
- **SC-002** (FR-002, FR-003): the rule's check fails on a hook that logs nothing and on an unregistered step, with tests red
  without it; the hooks the inventory finds logging nothing either log or carry their reason.
- **SC-003** (FR-004): the 22 fixes read "saves nothing" are reported by their tools' interventions since each was made, and
  the list goes to the GM's review.
