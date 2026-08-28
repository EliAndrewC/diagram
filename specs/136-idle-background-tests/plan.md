# Implementation Plan: Idle Sessions Run the Expensive Tests in the Background (136)

**Input**: `spec.md` (approved by `spec-fidelity` - see its Status line). **Constitution**: v2.12.0.

## Summary

Two hook events and one guard script. The session's Stop hook arms a detached timer; the
UserPromptSubmit hook disarms it and prints the last idle verdict. The timer waits the session's
staggered 60-120 minutes of AWAKE time (a suspend restarts it), takes the host-wide lock, runs
`make idle-tests` (= the tripwire and tier sweep, `maps`) in the clone, and records the verdict in
`dev/idle-log/`.

## Technical Context

- Hooks: `.claude/settings.json` gains a `Stop` entry and extends `UserPromptSubmit`; both call
  `scripts/idle-tests-hooks.sh <event>`. The script is a guard by this repo's definition (it runs on
  every turn) and gets its companion `scripts/test-idle-tests-hooks.sh`, run by the hooks-test target.
- The timer: `scripts/idle-tests-hooks.sh timer <clone> <session>` run under `setsid nohup`;
  loops `sleep $IDLE_TICK` (60 s) counting awake seconds; wall delta - awake > 300 s = suspend
  -> restart; the state file `<clone>/.git/idle-tests.json` is the arm/disarm channel (the disarm
  deletes it; the timer exits when it is gone or its `armed_at` changed).
- Session identity: the clone name (`basename` of the clone dir) - the same kebab of the session
  name the clone-sync hooks derive; `cksum` of it gives the stagger.
- The lock: `flock -n ~/.claude/idle-tests.lock`; on failure the timer defers `5 + (h mod 11)` min
  and retries until `IDLE_GIVE_UP` (6 h) after arming.
- Injection for tests: `IDLE_TICK`, `IDLE_WAIT_MIN`/`IDLE_WAIT_SPAN` (band), `IDLE_SUSPEND_S`,
  `IDLE_CLOCK` (a command printing the wall clock), `IDLE_RUN` (the command run in place of the
  idle-tests target), `IDLE_HOME` (the lock's directory). Only the test companion sets them, and
  the hook refuses them outside a fixture (the same seams-only-in-a-fixture rule
  `test-sync-with-main.sh` proves for the procedure).
- Never in main: the script exits at once when the cwd's git root is `/diagram` (or has no
  `.clones/` parent) - the same test `clone-sync-hooks.sh` makes.

## Constitution Check

- I/II n/a. VI: verification is the hooks-test target + the quick target; the timer's own run is
  the maps target, whose verdict the gate's rules already own. X: pure shell + a small Python state
  helper under 100% (`tests/tools/test_idle_state.py`). XII (research): none - a procedure. XIII:
  no engine change. XVI: spec reviewed before this plan. XVIII: the guard has a companion test.

## Decisions made in the GM's place (User Story 4 - for the GM's review at the end)

| # | decision | why | alternative declined |
|---|---|---|---|
| D1 | RULED BY THE GM 2026-08-28: the whole `done` gate (never FULL); the scope lock relaxed for the timer's process tree only (`switches.idle_context`); records as `idle-done`; one run per idle and none on unchanged content (D10). The first proposal was the maps target, through one Makefile target `idle-tests` | it is exactly what the scope lock deferred and what surfaced at unlock; ~5 min; the unlocked full gate is 21 min and rolls the whole suite, which an idle run can afford but which also writes the verification stamp - a stamp a session did not watch being earned | the full gate (heavier; stamps); the 48-seed cohort (2+ min more, no pool sweep) |
| D2 | wait = 60 + (cksum(session) mod 61) min of AWAKE time; suspend threshold 5 min of wall drift | the GM's band; the tick-vs-wall method needs no OS resume signal | a random draw per arming (not reproducible; two sessions can collide) |
| D3 | a suspend restarts the FULL wait | the GM: "we wait an additional hour" - read as the whole wait again, since the stagger is the point | credit awake time before the suspend |
| D4 | the lock is host-wide in `~/.claude/` (shared by every container of this host); a loser defers 5-15 min and retries up to 6 h after arming | one runner at a time is the herd rule; a loser should still run later that night | a queue file; or losers skipping the night |
| D5 | the verdict surfaces in the NEXT prompt's hook output, one line, and in `dev/idle-log/` (committed, append-only, like `dev/run-log/`) | the session must ACT on a red; a line at the next prompt is where every other guard speaks | a push notification to the GM (noisy at night); a file the session must remember to read |
| D6 | the timer runs in the clone's tree, never main's; it never re-arms itself - only a Stop arms | main is not a workspace; "once per idle" is the GM's shape | a nightly cron independent of sessions (would run in main or need its own clone) |
| D7 | a session that ends leaves its timer to notice (`~/.claude/sessions/<pid>.json` gone) and exit | no orphan runs after the GM closes a terminal | killing the timer from a SessionEnd hook (not always delivered) |

## Project Structure

- `scripts/idle-tests-hooks.sh` (the guard: `stop`, `prompt`, `timer`), `scripts/test-idle-tests-hooks.sh`
- `.claude/settings.json` (Stop + UserPromptSubmit wiring)
- `.claude/skills/diagram/Makefile` `idle-tests` target; `dev/idle-log/CLAUDE.md`
- docs: root `CLAUDE.md` guard table + iteration-loop bullet; `docs/iteration-loop.md`; `dev/switches.md`
