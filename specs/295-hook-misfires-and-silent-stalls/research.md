# Research - feature 295

Tooling only: nothing here is asserted about the world, so no task is `research: physical`. Each entry is the
measurement behind one defect's cause.

## R1 - why the finished-run hook called covered runs abandoned (item 1)

Feature 291's session (`diagram-readability`, transcript `99e044f9-...jsonl`) has 28 `run-still-going` refusals in the
guard log on 2026-09-30. The commands around them, read from the transcript:

- 02:26:43 launch: `setsid --fork nohup bash -c "make maps SCOPE=all > $S/maps.log 2>&1; echo MAPS-EXIT \$? >> $S/maps.log"`;
  02:26:50 waiter (backgrounded): `S=<scratchpad>; until grep -q "^MAPS-EXIT" $S/maps.log || { _writer-alive.sh ...; }; do sleep 20; done`.
  The make's stdout IS `<scratchpad>/maps.log`; the waiter's command line holds `S=<scratchpad>` and `$S/maps.log` but never
  the joined path, so `log in cmd` (`judge_runs`) is false.
- 19:06:50 launch: `bash -c "make map GEN=...kashikawa... > $S/kas3.log 2>&1; make map GEN=...mizuguchi... > $S/miz6.log 2>&1; echo PAIR-DONE >> $S/miz6.log"`;
  waiter on `$S/miz6.log`. While the first make runs its stdout is `kas3.log`, which no waiter names - but the chain
  (its parent `bash -c`, whose command line the outer shell expanded) will write `miz6.log`, which the waiter does name.

Reproduced 2026-09-30 in this clone with a dummy `make -f <scratch>/mk slow`: a waiter whose command line holds the literal
path is judged `watched` both as a plain process and as a harness-backgrounded one (whose command line is the harness's
`eval '...'` wrapper, still holding the text). So the matching rule, not the process walk, is what fails.

## R2 - why the exception check was routed as a review round (item 2)

The 19:53:20 dispatch (same transcript) began `MODE: a proposed EXCEPTION during implementation (constitution XVI),
feature 291 (...)`. `classify_mode` tests `\bMODE\s*[23]\b`, then `\bMODE\s*4\b|\bPLAN REVIEW\b`, then
`\bMODE\s*1\b|\bEXCEPTION CHECK\b`, else `spec`: none matched, so it was a spec round (guard log 19:53:21
`rewrote mode-3-preamble ... round 3`). The re-dispatch at 19:55:22 passed only because its `REVIEW_ROUND_OK` reason text
happened to contain "an exception check".

## R3 - why a headless page session sits idle (item 3)

Feature 293 measured that a `claude -p` session is never re-invoked by background work (backgrounded Bash, a detached
make, background agents); the request records R12's check session sitting about two and a half hours after its five
re-checks returned, until it was killed and the runner's retry path resumed it. `_page_session_runner.work` waits on the
process with `subprocess.run`, so nothing in the runner can see the silence. The resume path already exists (`resume_command`,
used for usage-limit failures). A session's transcript is `<projects>/<sid>.jsonl`; its subagents write
`<projects>/<sid>/subagents/agent-*.jsonl` (measured on this host).

The longest silence a working session can show is one foreground tool call: the Bash tool's own ceiling is 10 minutes
(600000 ms; observed 2026-09-30, method: the maximum `timeout` the Bash tool's own description states). A stall threshold of 15 minutes is therefore past any legitimate silence, and costs at most 15 minutes plus
one check interval against the 2.5 hours measured.

## R4 - what the outside watchdog can read and write (item 4)

- Every live session has `~/.claude/sessions/<pid>.json` with `sessionId`, `name`, `kind` (`interactive` | `bg`),
  `status` (`busy` | `idle` | `waiting` | `shell` observed), `cwd`, and, inside tmux, a `tmux` field naming the pane;
  dead pids leave stale files (liveness is `kill -0 <pid>`).
- `~/.claude/hooks/tab-title.sh` titles a tab by writing `ESC ] 0 ; <title> BEL` to the pane's tty
  (`tmux display -p -t <pane> '#{pane_tty}'`); the session's next hook event rewrites its own title, so a stall title
  clears itself when the session moves.
- `tmux capture-pane -p -t <pane>` gives the pane's visible text, from which the input line is read; `tmux send-keys`
  types into it.
- There is no `crontab` in the container; the watchdog is a detached loop with a lock file, started by the prompt hook
  when absent (the pattern `idle-tests-hooks.sh` and `tab-title.sh`'s watcher already use).

## R5 - the periodic-report shape (item 5)

The 292 session (`d9a6b720-...`) armed its report 13 times on 2026-09-30 as
`POLL_OK='hourly progress report on two|three detached page-session queues' bash <scratch>/sweep/watch4.sh 3600`,
backgrounded: the loop is inside the script file, and the period is its argument. The no-poll guard permitted it on the
escape. The 293 session's backgrounded stall watcher - `until [ -s result ] || [ $(( $(date +%s) - $(stat ...) )) -gt 1200 ]`
- is event-driven (it ends on a result file) and must not be caught.

## R6 - the ceiling rewrite inside double quotes (item 6, found here)

`setsid --fork bash -c "L=$S/c.log; until grep -q X \$L; do sleep 5; done"`, sent with `POLL_OK`, was rewritten to
`... until grep -q X \$L || { [ "$SECONDS" -ge 5400 ] && { echo "WAIT TIMED OUT ..."; exit 4; }; }; do ...` - the inserted
`"` closed the outer quote and the command failed `syntax error near unexpected token '('` (2026-09-30, this session).
`proof_of_life` inserts `"<path>"` the same way.

## R7 - the busy-wait rule on a sleep outside the loop (item 7, found here)

`pkill -f '<pattern>' ; sleep 1; cd <clone>; scripts/finished-run-hooks.sh judge <clone>; for p in $(pgrep -f X); do echo ...; done`
was refused as "a busy-wait loop (a loop containing `sleep`)" (2026-09-30, this session): the rule tests for a loop
keyword anywhere and a `sleep` anywhere, not a `sleep` inside the loop.
