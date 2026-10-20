# Implementation Plan: every tool measured by what it does (feature 406)

**Spec**: `spec.md` | **Request**: `request.md`

**Lands open**: T01, T02, T03, T04, T05, T06, T07, T08

## Summary

One report over the records the project keeps - the guard log (`~/.claude/guard-log/`, every guard's firing), each clone's
event log (`<git dir>/l7r-events/*.jsonl`, every tool call with its make target), the review ledger (`dev/review-ledger.md`,
every check pass and whether it was acted on) - plus one new record, `<git common dir>/tool-usage.jsonl`, for the tools that
leave none. The tool list comes from the code: `.claude/settings.json`'s wired hooks, the Makefile's targets, the refusing
checks (what `make done`, `make quick`, the push and `make tick` run - `scripts/gates/` and the `scripts/` checks those entry points name), `.claude/agents/`, and the registry `scripts/tool-registry.json`.

## Measured before planning (2026-10-19)

- The guard log: 58,602 entries over 46 guard names; two hooks that call `guard_log` (`download-copy`, `repo-safety`) never
  fired. 41 hook scripts are wired; three record nothing (`checks-hooks.sh`, `event-log-hooks.sh`, `idle-tests-hooks.sh`).
- `scripts/gates/`: 35 files; 7 log through `guardlog`; of the rest, about twenty are refusing checks with a command line, the
  others libraries.
- The event log: 6,442 lines with a `make` target; no outcome field; PostToolUse fires only on success, so a failed call leaves
  a PreToolUse with no PostToolUse; `PostToolUseFailure` is the hook event a failure fires (`docs/guards.md`).
- The transcripts: 17 GB under `~/.claude/projects/` - too large for a report to read; the report reads the logs above only.

## Constitution Check

Tooling only (no engine path): lands by `make land-tooling`, its tests under `tests/tooling/` and `tests/hooks/`; no map moves.

## T01 - the usage-log helper and the tool registry

### T01 Approach (checklist part A)

1. **The goal, in the world.** A tool that leaves no record of its own records each run in one place, and one registry says which tools do and what each does.
2. **The constraints.** FR-002: one shared helper, `<git common dir>/tool-usage.jsonl` (utc, tool, kind, outcome); every tool recording through it listed in one registry with what it does. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the inventory in the plan's Summary: three silent hooks, about twenty silent refusing checks, the automatic steps of `make tick` and `land-tooling` and the rest leaving no record).
5. **The order.** the helper (a Python function and a command line for shell callers); the registry file; their tests.
6. **The exits.** (c) - one helper, one registry; a log line per tool in its own format was weighed and refused (the report would read N formats).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `scripts/hooks/lib/usage_log.py` records a line through `record(root, tool, kind, outcome)` and `usage_log.py record --tool --kind --outcome`, never raising into its caller; `scripts/tool-registry.json` holds each tool's kind and what it does; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T01 Decisions

**D160 - one helper, one registry.** `usage_log.record` appends `{utc, tool, kind, outcome, session}` to `<git common dir>/tool-usage.jsonl` under a lock, swallowing any error (a record must never fail its tool); `exited(tool, code)` records `passed` or `refused` from a check's exit code and returns it. `scripts/tool-registry.json` maps each tool to `{kind: step|check|hook|target, what}`.

## T02 - a make target's outcome recorded

### T02 Approach (checklist part A)

1. **The goal, in the world.** Every make target run in a session reads succeeded or failed, and the runs the event log cannot see are recorded.
2. **The constraints.** FR-003: the event log records a failed tool call beside a succeeded one; a run outside any session (`make idle-tests` by its timer) or from inside another script records through the helper; the report names what it still cannot see. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the event log's 6,442 make lines carry no outcome; PostToolUse fires only on success; `PostToolUseFailure` fires on a failure (`docs/guards.md`)).
5. **The order.** `event_log` records a `PostToolUseFailure` line; the hook wired on it; `make idle-tests` records its run through the helper; the tests.
6. **The exits.** (c) - record the failure event; inferring a failure from a PreToolUse with no PostToolUse was weighed and refused as the only reading (a call still running looks the same), kept as the fallback for lines before this lands.
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: a failed Bash call's event line reads `ev: PostToolUseFailure` with its make target; `make idle-tests` writes a helper line with its outcome; every make invocation, from a session, a recipe, a script or the timer, records a `ran` line; `make tool-yield` counts a target's runs from those lines and its outcomes from the event log, and names beside each target how many of its runs have no outcome record; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T02 Decisions

**D161 - the failure recorded.** `event-log-hooks.sh` is wired on `PostToolUseFailure`; `event_log.line` keeps the event name, so a failed call's line carries `ev: PostToolUseFailure`, its tool, id and make target. `make idle-tests` (the timer's target) records `idle-tests` through the helper with `passed` or `failed`, registered as a target that records. A target run from another target's recipe or from a script is not a tool call, so the event log cannot see it: every make invocation records its run through the helper as the Makefile is read (one `$(shell ...)` line naming `$(MAKECMDGOALS)`, or the default goal's name when there is none, kind `target`, outcome `ran`; skipped for `make -n` and `make -q`, which run nothing), so `tool_yield` counts every run of every target from the usage log alone - never adding the event log's runs, so a session run is counted once - and reads its outcome from the event log's line for the same target in the same minute; the outcome of a run no session made is what it still cannot see, and the report says so beside each target.

## T03 - the silent tools record

### T03 Approach (checklist part A)

1. **The goal, in the world.** Every refusing check, the two silent hooks that refuse or run work, and the automatic steps leave a record of each run.
2. **The constraints.** FR-002 and FR-004: each refusing check and automatic step records through the helper and is in the registry; a hook that records nothing names the record where it is seen (the event-log hook is its own record). The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the plan's inventory: `checks-hooks.sh` and `idle-tests-hooks.sh` record nothing; about twenty refusing checks under `scripts/gates/` log nothing; automatic steps - `make tick`'s plan archive, `land-tooling`'s `make docs` and stale-base merge, `ledger-owed`'s rows, clone-sync's merge, the plan hold's write-back - leave no trace).
5. **The order.** the refusing checks wrapped at their exit; `hm_checks`' refusals and the idle-tests hook recorded; each automatic step recorded where it acts; the registry entries; the test.
6. **The exits.** (c) - one call at each tool's own exit or action; a wrapper in the Makefile around each check was weighed and refused (a check run from a hook or another script would miss it).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: every refusing check's command line and each listed automatic step records a helper line, each in the registry; `checks-hooks` and `idle-tests-hooks` record or name their record; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T03 Decisions

**D162 - each silent tool records.** Each refusing check script with a command line returns through `usage_log.exited(<its name>, code)`; `hm_checks` records each refusal it makes (`checks-hooks`, outcome `refused`); `idle-tests-hooks.sh` records each run it starts; the automatic steps record at their action with outcome `changed` or `unchanged` - `tick-archive`, `land-tooling-docs`, `land-tooling-merge`, `ledger-owed-write`, `clone-sync-merge`, `planhold-restore`. Every name is in `scripts/tool-registry.json`. The six steps are the inventory's; an automatic step written later that calls neither the helper nor `guard_log` is one FR-004's check cannot see (it has no file of its own to read), a limit `tool-yield`'s footer states.

## T04 - `make tool-yield`

### T04 Approach (checklist part A)

1. **The goal, in the world.** One command shows, for every tool, how often it is used and how often it changed the outcome.
2. **The constraints.** FR-001: every tool listed from the code - wired hooks, refusing checks, make targets, review checks, logged steps; first seen, uses in 7 days and in all, interventions, likely misfires per kind; too new only under 7 days since first seen; no outcome record, never 0, where the record cannot show one. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the guard log, the event logs and the review ledger read; their fields as the spec's FR-001 names them).
5. **The order.** the tool inventory from the code; each kind's reader; the table; the make target; the tests.
6. **The exits.** (c) - one report over the existing records and the new one; reading the transcripts was weighed and refused (17 GB).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `make tool-yield` prints every wired hook, refusing check, make target, review check and registered tool, each with its columns or `too new` / `no outcome record`; a hook that never fired reads 0; `tests/tooling/` red without each kind's reading.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T04 Decisions

**D163 - one report.** `scripts/measure/tool_yield.py` lists tools from `.claude/settings.json` (hook scripts and the guard names their firings carry), every refusing check - each `.py` with a `__main__` and each `.sh` under `scripts/gates/`, and each script under `scripts/` that the entry points name, found at run time by reading them - the Makefile recipes of `done`, `quick` and `tick` and the text of `scripts/sync-with-main.sh`, `scripts/gates/push_checks.py` and `scripts/gates/preflight.py`, every `scripts/...` path they name - never a hand-kept list - an exempt one included, read through the record its `# TOOL_RECORD:` names, or as its own make target where it is a target's body, or as "no outcome record"; the Makefile, `scripts/tool-registry.json` and `.claude/agents/`; reads the guard log (interventions: blocked, refused, rewrote, reminded, warned; misfires: escaped), every clone's event logs (a target's runs; failures its `PostToolUseFailure` lines, or before T02 a PreToolUse with no PostToolUse; misfires a failed run followed by the same target with an `*_OK=` escape), the review ledger (acted-on passes; misfires declined and `MISSED-BY-REVIEWER`; a check with no ledger rows reads its dispatches from the event logs' `SubagentStart` lines and "no outcome record"), and the usage log (a target's runs; interventions `refused`, `changed`, `failed`; an automatic step's misfires "no outcome record", no step recording an undo). `make tool-yield [KIND=] [SINCE=]`.

## T05 - the rule

### T05 Approach (checklist part A)

1. **The goal, in the world.** A tool added later cannot land recording nothing.
2. **The constraints.** FR-004: `make hooks-test` refuses a wired hook or a refusing check script that records nothing unless its exemption names its record; a usage-log call naming a tool the registry lacks; a registry entry no code calls. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the plan's inventory; `make hooks-test` runs every guard's suite).
5. **The order.** the check script; its suite under `tests/hooks/`; its place in `make hooks-test`.
6. **The exits.** (c) - a check in the suite run that already gates hooks; a reminder in CLAUDE.md was weighed and refused (the GM's rule).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `scripts/gates/check-tool-signals.py`, run by `make hooks-test`, refuses each case FR-004 names, naming the file and the fix; its suite red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T05 Decisions

**D164 - no tool without its record.** `check-tool-signals.py` reads the wired hooks and the refusing check scripts (the same set `tool_yield` lists: every `.py` with a `__main__` and every `.sh` under `scripts/gates/`, and every script under `scripts/` the entry points name; a script that is a make target's own body is measured as that target - its runs in the usage log's `ran` lines, its outcomes in the event log - and the check names that record in its pass line); each must call `guard_log` or the helper, or carry `# TOOL_RECORD: <where its runs are seen>`; every helper call's tool name must be in the registry, and every registry entry called somewhere. Its suite `tests/hooks/test-tool-signals.sh` (a guard's companion) runs in `make hooks-test`.

## T06 - `make fix-yield` on the new numbers

### T06 Approach (checklist part A)

1. **The goal, in the world.** Each tooling fix the round arbiter named is read by what its tools did since it was made.
2. **The constraints.** FR-005: each fix by the tools its change touched and their FR-001 numbers since the fix was made, replacing the command-rate measure; the step-back bundle reads the same. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (`fix_yield.py` (385 T119) compares a command rate per session hour; the 45 fixes made before T119 carry measures assigned after the fact (`fix-measures.json`)).
5. **The order.** each fix's tools found from the files its settling commit or landing named; the report rebuilt on `tool_yield`; the step-back's table; the tests.
6. **The exits.** (c) - the fix's own tools; keeping the command rate beside it was weighed and refused (the spec replaces it).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `make fix-yield F=<n>` prints each fix with its tools and their first seen, uses, interventions, likely misfires (or "no outcome record") since it was made; the step-back's `fix-yield.md` the same; `tests/tooling/` red without it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T06 Decisions

**D165 - a fix by its tools.** A fix's tools are the guards, checks, targets and registered steps in the files of the commit that settled it (`make arbiter-fix-done`'s land-tooling run, or the clone commit naming its trigger), mapped by `tool_yield`'s inventory; `fix_yield.verdict` reports, per fix, each tool's first seen, uses, interventions and likely misfires since the settling, FR-001's "no outcome record" where its record cannot show one, and `too new` under 7 days. `fix-measures.json` and the command-rate reading are retired.

## T07 - the 22 fixes judged

### T07 Approach (checklist part A)

1. **The goal, in the world.** Each of the 22 fixes that read "saves nothing" has a judgment the GM can read, on its tools' evidence.
2. **The constraints.** FR-005 and SC-003: each a recorded judgment - doing something, doing nothing, or too new to say - citing its numbers, delivered to the GM. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (`make fix-yield F=385` printed "saves nothing" on 22 rows (the spec review re-counted it)).
5. **The order.** T06's report run over 385; each of the 22 judged from its tools' numbers; the file; a row in the GM's review.
6. **The exits.** (c) - a judgment per fix from its numbers; retiring any here was weighed and refused (the GM decides; the judgment informs).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `specs/406-every-tool-measured/fix-judgments.md` holds the 22, each with its tools, numbers and judgment; a row in 406's GM review points to it.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T07 Decisions

**D166 - the 22 judged.** Doing something: a tool of the fix has interventions net of its likely misfires since it was made. Doing nothing: its tools have outcome records, 7 days or more of them since, and no intervention net of misfires. Too new to say: under 7 days since. No outcome record: a tool whose record cannot show an outcome is never judged doing nothing - the line says the record is missing. Record too new: a fix older than 7 days whose tools began recording under 7 days ago (this feature's new records) reads that, never doing nothing. Each fix takes the first that holds, in this order, so none falls through: too new to say (the fix under 7 days old); no outcome record; record too new; doing something; doing nothing. Each line cites the numbers; the file is written by hand from T06's output and reviewed with the feature.

## T08 - the close

### T08 Approach (checklist part A)

1. **The goal, in the world.** 406 closes with its report.
2. **The constraints.** Feature-report and retro rows, as 385's tasks closed. The GM's rule: a tool, never a reminder. A test red without it.
3. **Where each comes from.** The GM and the approved proposal (G, `request.md`); the spec (O).
4. **Do they describe the world here?** Yes - measured 2026-10-19 (the feature's tasks and records).
5. **The order.** the feature report; the retro rows.
6. **The exits.** (c).
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** One goal: `make feature-report F=406 WRITE=1` written; every task's retro row.
10. **Before moving a constant.** n/a - no constant moves in this task.
11. **Before fitting things into room.** n/a - nothing is fitted in this task.

### T08 Decisions

**Wording only.** The report and the retro rows.
