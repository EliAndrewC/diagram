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

### T01 part B (2026-10-20T04:51Z)

Owed by the round arbiter's ruling on hour:406-every-tool-measured@1 (continue), taken while T01 was the active task.

1. **What is refusing?** Nothing in T01: the helper, the registry and their tests are green, and `make hooks-test` holds them in step. The two reds of the hour were outside it: the push fixtures read a new import's `__pycache__` as uncommitted work (fixed: no bytecode written), and a fixture's script list lacked the helper (added).
2. **A3 again.** Unchanged: FR-002 (O, from the spec) and the GM's "a tool, never a reminder" (G).
3. **A4 again.** Unchanged.
4. **Moving something earlier for something later?** No.
5. **Tuning or changing?** Neither: D160 stands as reviewed.
6. **The one-sentence test.** "Every silent tool writes one line per run to one log, and a registry names each" - true by the code and `check-tool-signals`.
7. **The next step is a measurement.** The ticks of T01-T07 on their tests, then `make done` before the landing.
8. **Every route measured before offering one?** No route is offered.
9. **After a ruling: the step it names?** Yes - the ruling says go on to T07 and T08; its point for the GM (which 22 were judged) goes to 406's GM review.

<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-20 (feature 375 FR-044) -->
<!-- plan-archive: T09 to T07 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T09 Approach (checklist part A)

1. **The goal, in the world.** each of the 22 arbiter fixes judged on what its tools did since it was made.
2. **The constraints.** FR-005, SC-003.
3. **Where each comes from.** O: `make fix-yield F=385`.
4. **Do they describe the world here?** n/a - a reading, not a placement.
5. **The order.** after 2026-10-26, when every fix has a week of use.
6. **The exits.** done when no row reads "too new to say"; a fix still unread after a week is recorded as "no use since".
7. **The search smell.** none.
8. **The budget.** One landing.
9. **Done, measured.** `grep -c "too new" fix-judgments.md` is 0.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

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
