# Retros - feature 406

One row per closed task.

## T01 - the retro row

About 20 min. One helper (`scripts/hooks/lib/usage_log.py`) that every silent tool records through, and one registry
(`scripts/tool-registry.json`) of what records. A record never fails its tool: every error is swallowed. A late fix came from
the push fixtures, which copy `scripts/` without ignoring `__pycache__` and read the helper's bytecode as uncommitted work, so
the importers now write none. **The habit it changes:** a tool that refuses or changes something now says so in one log.

## T02 - the retro row

About 25 min. The event-log hook now runs on PostToolUseFailure too, so a failed `make` call is told apart from a succeeded
one by its call id. A parse-time Makefile line records every goal (a session's, a recipe's, a script's or a timer's), and
`make -n`/`-q` record nothing. Runs no session made keep their count but not their outcome, which the report names beside each
target. **The habit it changes:** none; the records are written where they already ran.

## T03 - the retro row

About 40 min. 18 gate checks plus `speckit-todo`, `ratchet` and `one-gate` record passed or refused. The six automatic steps
(plan-hold restore, tick archive, land-tooling's docs and merge, clone-sync's merge, ledger-owed's write) record what they did.
The tools whose runs are already seen elsewhere carry `# TOOL_RECORD:` saying where. **The habit it changes:** none.

## T04 - the retro row

About 60 min, the longest task: three plan-review rounds and one arbiter ruling. Round 4 was accepted rather than run,
because each round had closed what the one before raised. `make tool-yield` lists every guard, check, target, review and step
with its uses, interventions and likely misfires, marked "too new" or "no outcome record" where that is all the record can
say, in about 2.5 s. The checks are found by following `done`, `quick` and `tick` through their prerequisites and `$(MAKE)`
calls, not by a list. **The habit it changes:** "is this tool doing anything" is a command now, not a reading of its source.

## T05 - the retro row

About 25 min. `check-tool-signals.py` runs in `make hooks-test` twice: as a roster companion on fixtures, and live on the
repository. It refuses a hook or check that records nothing without naming its record, a usage-log call the registry lacks,
and an entry nothing calls. Its suite goes red (6 of 10) on a copy without the refusal. **The habit it changes:** a new tool
cannot land silent.

## T06 - the retro row

About 45 min. `make fix-yield` reads each fix by its tools since it was made. Each fix's settling commit is found by its
note's hash, then by the exact trigger (`@2` is not `@29`, and the clone's own commit comes before a landing's), then by its
test file between ruling and settling. A commit holding only records is passed over. Engine code that belongs to no tool reads
as "no tool found", never as an older commit's tools. Four rules were added in turn as the live run over 385 showed wrong
mappings, and each is pinned by a test. `fix_measure` and the command rate are retired; `fix_minutes` stays. **The habit it
changes:** the step-back's "does a fix do anything" reads tool numbers, not a regex's rate.

## T07 - the retro row

About 20 min. The 22 fixes the GM counted, taken from the hour-37 table, are judged in `fix-judgments.md`. Today's retired
reading finds 21, because one now reads "saving" on the same rate. All 22 read "too new to say": they were made between
2026-10-17 and 2026-10-19 and become readable from 2026-10-24 to 2026-10-26. **The habit it changes:** none; the GM decides.

## T08 - the retro row

About 15 min, the close: the feature report and these rows.
