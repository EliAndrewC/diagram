# Implementation Plan: Hook misfires and silent stalls

**Feature**: `295-hook-misfires-and-silent-stalls` | **Date**: 2026-09-30 | **Spec**: [spec.md](spec.md)

## Summary

Five guard and runner fixes plus one new outside watchdog, each with its suite. No engine code, so the landing is
DIRECT. Every rule below is a decision of this plan; none narrows the spec.

## Technical Context

Bash guards with embedded or sibling Python decisions (the repo's guard idiom); `_guardlog.sh` for every firing. Tested
by the `scripts/test-*-hooks.sh` suites under `make hooks-test`, and the runner by
`.claude/skills/diagram/tests/tooling/test_page_session.py`. No performance bookends: no generator change.

## Constitution Check

- I, II, III, VII, VIII, IX, XI, XII: N/A - no map, no pool content, no setting detail, nothing asserted about the world.
- IV, V: PASS - no SOURCE block touched; `request.md` holds the GM's words; the GM's two answers are in spec.md.
- VI: PASS - each task names its verification; every guard case drives the real hook with a measured shape.
- X: PASS - no engine module added; the new Python is in `scripts/` with its tests.
- XIII: PASS - `make hooks-test` and `make done` are the regression bed.
- XIV: PASS - items 6 and 7 were found while measuring and are fixed here.
- XVI: PASS - spec-fidelity FAITHFUL at round 3; no exception taken.

## The design

### D1 - Item 1: a command line names files after expanding its own variables (FR-001, FR-002)

`finished-run-hooks.sh` `judge_runs`: `files_named(cmd, cwd)` expands the simple assignments a command line makes into
their `$NAME`/`${NAME}` uses (three passes, for `S=..; L=$S/x; $L`), resolves relative tokens against the process's cwd,
and keeps paths that are not directories and not executables, whether the file exists yet or not (a chain's last log is
not there while its first make runs; research R1). A run's files are its stdout plus, for every ancestor up to the
harness, that ancestor's stdout and `files_named` of its command line. Watched = any waiter loop's `files_named`
intersects them. The loop recognizer itself is unchanged.

### D2 - Item 2: the dispatch's own MODE line decides, after MODE 2/3 (FR-003)

`_hm_review_round.classify_mode`: after the `MODE 2/3` test, a line BEGINNING with `MODE` (case-sensitive, so a relayed
sentence does not count) is read: EXCEPTION in it is an exception check, PLAN a plan review; otherwise today's rules.

### D3 - Item 3: a watch thread beside each headless session (FR-004)

`_page_session_runner.StallWatch` runs beside the `subprocess.run` of each session (so the existing call and its tests
stand), reads the newest mtime of `<projects>/<sid>.jsonl` and `<projects>/<sid>/subagents/*.jsonl`, measures silence
from the later of that and the watch's own start (a resumed session's transcript is as old as the wait before it), and
past `STALL_AFTER` = 15 min (research R3) sends SIGTERM to the session's `claude` process, found in `/proc` by its
`--session-id`/`--resume <sid>` arguments. The loop then resumes the session at once, logging
`stalled <sid> - idle <N> min, resuming it (k of 8)`; past `STALL_RESUMES` = 8 it logs and moves to the next brief.
Checked every 60 s.

### D4 - Item 4: one watchdog loop outside every session (FR-005)

`scripts/stall-watchdog-hooks.sh`: `prompt` (UserPromptSubmit) starts the loop detached (`setsid`) when its pid file names
no live process; `run` is the loop - `flock -n` on `~/.claude/stall-watchdog/lock` so a second never runs beside it,
then one pass every 5 minutes, each pass a fresh `python3 scripts/_stall_watchdog.py pass` so an update to the decision
takes effect without restarting the loop; `once` runs one pass (the suite). Every action is a line in
`~/.claude/stall-watchdog/log`. Five minutes: the threshold is an hour, so a pass every five puts the mark within 5 min
of it at a cost of one short Python run.

### D5 - Item 4: what is a stall (FR-005a)

For every registry entry `~/.claude/sessions/<pid>.json` whose pid lives: the transcript is the
`~/.claude/projects/*/<sessionId>.jsonl` found by glob, with its subagents. Stalled when ALL hold:
- silent 60 minutes or more (newest mtime);
- not waiting on the GM: status is not `waiting`, and the transcript's last record is not an `AskUserQuestion` tool use
  without its result;
- the session's clone (from `/diagram/.clones/.session-clones/<sessionId>`, else the git toplevel of its cwd; the mirror
  `/diagram` itself never counts, as it is not a workspace) holds unfinished work: `git status --porcelain` non-empty,
  `git rev-list origin/main..HEAD` non-empty, or a live make there (`finished-run-hooks.sh live`);
- the clone has no page-session run log whose last line is the runner's retry wait (`failed ... waiting ... then
  resuming it`), which is the 292 watcher's misfire.

### D6 - Item 4: where it lands and what it types (FR-005b, FR-005c)

The tab: the session's own `tmux` pane (`@w.%p` -> `%p`); else the pane of the live session whose `sessionId` is the
`L7R_DISPATCHER` in `/proc/<pid>/environ`; else the interactive session whose `parkedJobId` is its `jobId`; else a live
interactive session with a pane whose clone is the same; else none (logged only). The mark: the title
`⚠ STALLED <idle> - <stalled session's name>` written to the pane's tty (`#{pane_tty}`) and a bell, every pass while the
stall lasts (the idle time moves), the bell once per stall. The nudge: only in the session's OWN pane, only when
`tmux capture-pane` shows exactly one line between the last two rule lines (`────`) and it is `❯` with nothing after
it, once per stall: `tmux send-keys -l` with the text, then Enter. A stall is identified by its last-activity time, kept
in `~/.claude/stall-watchdog/<sessionId>.json`; activity after it starts a new stall. The text:
`watchdog (feature 295): this session has been idle <N> min with unfinished work in <clone> (<what>). If you are
waiting on the GM, say so in one line and stop; otherwise check your background work and carry on.`

### D7 - Item 5: a periodic report is refused with its CronCreate (FR-006)

`no-poll-hooks.sh`, before the POLL_OK escape (a periodic report is exactly what that escape let through): with
`run_in_background` set and no `CRON_OK="<reason>"`, `_hm_shape.py periodic` judges the command periodic when its
POLL_OK reason names a period or a report (hourly, every N minutes/hours, periodic, progress/status report, heartbeat),
or a loop in it - inline, or in the script file it runs (`bash|sh <file>`, `./<file>`) - has a condition made only of
elapsed-time tests (`$SECONDS`, `date +%s`) or is `while true`/`while :` with a `sleep` in it. The hook's own ceiling
clause is set aside first, so an event-driven wait is never periodic. The period: the reason's words, else the elapsed
limit in the condition, else the largest `sleep`, else an hour. The cron: under an hour, `*/m` with m the nearest
divisor of 60; an hour or more, the current minute (moved 7 off :00 and :30) every h hours. The refusal prints the
`CronCreate` call with `recurring: true` and a prompt seeded from the reason.

### D8 - Item 6: an inserted clause is escaped for the quoting it lands in (FR-007)

`_hm_shape`: `_quote_state(cmd, pos)` walks the command to the insertion point (backslash, single and double quotes);
inside double quotes the clause's `"` and `$` are escaped; single quotes need nothing (no clause contains one).
`add_ceiling` and `proof_of_life` both use it.

### D9 - Item 7: the sleep must be inside the loop (FR-008)

`_hm_shape.sleep_in_loop(scan)`: for each `while|until|for`, the span from the keyword to its matching `done` (counting
nested `do`/`done`) must contain the `sleep`; the no-poll rule 2 asks it instead of "a loop keyword anywhere and a sleep
anywhere".

### D10 - Wiring and tables (FR-009)

`.claude/settings.json`: `stall-watchdog-hooks.sh prompt` on UserPromptSubmit. Rows in `CLAUDE.md` "What is enforced"
and `docs/guards.md` for the new watchdog and the changed no-poll, finished-run and review-round behavior.
