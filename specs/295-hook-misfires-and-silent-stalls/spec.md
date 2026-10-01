# Feature Specification: Hook misfires and silent stalls

**Feature Branch**: `295-hook-misfires-and-silent-stalls` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-30

**Status**: Draft (taken up 2026-09-30 by the Diagram tooling session, at the GM's word: *"Does feature 295 have all the
information you need to make the tooling fixes? If so then please do so, thanks."*)

**Input**: the GM's request and the five problems, verbatim in [`request.md`](request.md); the GM's two answers on item 4
under Clarifications below.

## Clarifications

### Session 2026-09-30

The session judged items 1, 2, 3 and 5 specified by the request plus measurement (each defect's cause is in
`research.md`), and item 4 short of two decisions only the GM could make. Asked, the GM chose:

- Q: when the outside watchdog finds a session idle over an hour with unfinished work, how does it reach the GM? ->
  A: **"Tab title + bell"** - retitle the stalled session's tmux tab and ring the bell, reusing the tab-title mechanism.
- Q: may the watchdog also nudge a stalled interactive session by typing a short prompt into its tmux pane? ->
  A: **"Nudge if prompt empty"** - type the nudge only when the pane's input line is empty and the session has been
  idle over an hour, at most once per stall.

## The defects, measured

The causes below are measured in `research.md` (R1-R7), each against the incident the request names.

1. **The finished-run hook's false alarm** (`scripts/finished-run-hooks.sh`, Stop). The hook calls a detached make
   WATCHED only when a waiter loop's command line contains the make's stdout path literally. Two shapes in feature 291's
   landing defeat that: a waiter naming its log through a variable (`S=<dir>; until grep -q X $S/maps.log`), and a chain
   whose waiter watches the chain's final marker file while an earlier make in it writes a different log
   (`bash -c "make a > a.log; make b > b.log; echo DONE >> b.log"`, waiting on `b.log` while `make a` runs). The session's
   guard log holds 28 `run-still-going` refusals on 2026-09-30; these two shapes are the ones the request names.
2. **The review-round hook's misroute** (`scripts/review-round-hooks.sh`, `_hm_review_round.classify_mode`). The
   classifier knows an exception check only as `MODE 1` or `EXCEPTION CHECK`; the dispatch said `MODE: a proposed
   EXCEPTION during implementation (constitution XVI)`, matched neither, fell to the default (a spec review), and was
   rewritten into a MODE 3 round and routed to `spec-fidelity-verify`.
3. **A headless page session never wakes for its own background agents** (`scripts/_page_session_runner.py`). A
   `claude -p` session is never re-invoked by background work (feature 293's measurement); the runner waits on the
   process, which never ends, so the queue sits until someone kills it.
4. **Nothing outside a session sees a stall.** An in-session `CronCreate` check dies with its session.
5. **A periodic report kept as a backgrounded one-shot watcher** loses its schedule across a usage-limit window. The
   real shape was `POLL_OK='hourly progress report on ...' bash watch.sh 3600` - the loop inside a script file.

Found by this feature while measuring (constitution XIV: fixed in the same work):

6. **The no-poll ceiling rewrite breaks a loop inside a double-quoted string.** `bash -c "until grep -q X \$L; do ...;
   done"` gets the ceiling clause with bare `"` and `$SECONDS` inserted inside the quotes, and the command no longer
   parses (reproduced 2026-09-30). The proof-of-life clause has the same defect.
7. **The no-poll busy-wait rule fires on a `sleep` that is outside every loop.** A command with a `for` loop and an
   unrelated `sleep 1` before it was refused as a busy-wait (reproduced 2026-09-30).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A covered run is not called abandoned (Priority: P1)

A session starts a detached chain of makes and arms a backgrounded waiter on the chain's own marker, naming its file
through a variable or naming the last file the chain writes. The turn ends quietly: the hook says the run is watched.

**Independent Test**: start a detached make in a clone in each of the two shapes with a waiter armed, run the hook's
`judge` mode; it reports `watched`.

**Acceptance Scenarios**:

1. **Given** a waiter `S=<dir>; until grep -q X $S/run.log ...` and a detached make writing `<dir>/run.log`, **When** the
   turn ends, **Then** the run is judged watched and the turn is not refused.
2. **Given** a detached `bash -c "make a > a.log; make b > b.log; echo DONE >> b.log"` and a waiter on `b.log`, **When**
   the turn ends while `make a` runs, **Then** it is judged watched.
3. **Given** a detached make with no waiter at all, **When** the turn ends, **Then** it is still refused once, as today.

### User Story 2 - An exception check reaches the agent it was sent to (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a `spec-fidelity` dispatch whose mode line says `MODE: a proposed EXCEPTION ...` for a feature with a review
   snapshot, **When** it is dispatched, **Then** it passes untouched to `spec-fidelity` (not rewritten, not routed).
2. **Given** a mode line naming a plan review, **Then** it passes untouched; **given** `MODE 2`/`MODE 3` anywhere, or no
   mode named at all, **Then** it is treated as a spec review round exactly as today.

### User Story 3 - A headless session that went quiet is resumed (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a queued `claude -p` session whose transcript and every subagent transcript of it have been silent past the
   stall threshold while its process lives, **When** the runner checks it, **Then** the runner ends that process, logs
   `stalled <sid> - idle <N> min, resuming it`, and resumes the same session at once (no usage-limit backoff).
2. **Given** a session still writing its transcript, or whose subagents still write theirs, **Then** nothing is done.
3. **Given** a session that has been resumed for stalls the maximum number of times, **Then** the runner stops resuming
   it, logs that, and moves to the next brief.

### User Story 4 - A stall outside any session is seen, and nudged when safe (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a live interactive session whose transcripts have been silent over an hour, which is not waiting on the GM
   (a pending question or permission), and whose clone holds unfinished work (uncommitted changes, commits not on
   GitHub `main`, or a live make), **When** the watchdog runs, **Then** it retitles that session's tmux tab with a stall
   mark and the idle time, and rings the bell.
2. **And** when that pane's input line is empty, **Then** it types one nudge prompt into the pane and presses Enter -
   once per stall; a stall that continues after the nudge is not nudged again until the session has been active and
   gone quiet again.
3. **Given** a session whose clone has no unfinished work, or a page-session queue in its usage-limit retry wait
   (`failed ... waiting ... then resuming it` as its run log's last line), **Then** it is not called stalled.
4. **Given** a headless (`claude -p`) session whose runner is gone, or that no runner started, silent over an hour with
   unfinished work, **When** the watchdog runs, **Then** the stall mark and bell land on the tab of the session that
   dispatched it (its `L7R_DISPATCHER`), else on the tab of a live interactive session in the same clone, and the nudge
   typed there (input line empty, once per stall) names the stalled session and the command that resumes it; with no
   such tab the stall is only logged.
5. **Given** a background (`kind: bg`) session, **Then** its tab is the interactive session that parked it, as
   `tab-title.sh` finds it, and the same rules apply.
6. **Given** the watchdog is not running, **When** any session submits a prompt, **Then** one instance is started,
   detached; a second never runs beside it.

### User Story 5 - A periodic report is steered to a cron (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a backgrounded Bash command whose `POLL_OK` reason names a periodic report (hourly, every N minutes, a
   progress or status report), or whose loop - inline or in the script file it runs - exits on elapsed time alone,
   **When** it is dispatched, **Then** it is refused with the exact `CronCreate` call for the same period (an off-minute
   hourly cron, or `*/N` for a period that divides the hour).
2. **Given** an event-driven wait (a file watch, with or without the hook's own ceiling), **Then** it is untouched.
3. **Given** `CRON_OK="<reason>"` in the command, **Then** it passes, logged.

### User Story 6 - The no-poll rewrites keep a command runnable, and a stray sleep is not a busy-wait (Priority: P2)

**Acceptance Scenarios**:

1. **Given** a wait loop inside a double-quoted `bash -c "..."`, **When** the ceiling and the proof-of-life clauses are
   added, **Then** they are escaped for that quoting and the command still parses (`bash -n`); inside single quotes they
   are added as they are today.
2. **Given** a command whose only `sleep` is outside every loop body, **Then** it is not refused as a busy-wait; a `sleep`
   inside a `do ... done` body still is.

## Requirements *(mandatory)*

- **FR-001** (item 1): a waiter's watched files are the paths in its command line after expanding the simple shell
  assignments it makes (`NAME=value`, quoted or not) into their `$NAME`/`${NAME}` uses, and resolving a relative path
  against the waiter's working directory.
- **FR-002** (item 1): a live make is WATCHED when a waiter watches its stdout file, or the stdout file of any of its
  ancestors up to the first that is the harness, or a file named in any such ancestor's command line.
- **FR-003** (item 2): the mode is read first from a line beginning `MODE`: one naming EXCEPTION is an exception check,
  one naming PLAN a plan review; a `MODE 2`/`MODE 3` marker anywhere still wins over everything; without either, today's
  rules apply unchanged.
- **FR-004** (item 3): the runner watches each running session; silence past the stall threshold across the session's
  transcript and its subagent transcripts, with the process alive, ends the process and resumes the session at once;
  stall resumes are capped per session (eight: two hours of quiet at the outside) and logged. The threshold and the cap
  are recorded with their reasons beside them.
- **FR-005** (item 4): a watchdog runs outside every session, one instance, started by the prompt hook when absent; on
  each pass it judges EVERY live session - interactive, headless and background - by FR-005a and acts by FR-005b on the
  tab FR-005c names. (A runner-managed headless session is resumed by FR-004 at 15 minutes, so it reaches the hour only
  when its runner has failed or never existed - which is item 4's case.)
  - **FR-005a**: stalled = silent over an hour (its transcripts), not waiting on the GM, and with unfinished work in its
    clone (uncommitted changes, commits not on `origin/main`, or a live make); a page-session queue's retry wait is not
    a stall.
  - **FR-005b**: the stalled session's tab is retitled with a stall mark and the idle time and the bell rung; when the
    pane's input line is empty the nudge is typed once per stall.
  - **FR-005c**: the tab is the session's own tmux pane; for a session with none, the pane of the session that
    dispatched it (`L7R_DISPATCHER` in its environment), else of the interactive session that parked it (a `bg` job), else
    of a live interactive session in the same clone; with none, the stall is logged only. A nudge typed into another
    session's tab names the stalled session and how to resume it.
- **FR-006** (item 5): a backgrounded Bash command that is a periodic report by the definition in Story 5 is refused
  with the exact `CronCreate` call; `CRON_OK="<reason>"` escapes it; an event-driven wait is never caught.
- **FR-007** (item 6): every clause the no-poll hook inserts is escaped for the quoting it lands in.
- **FR-008** (item 7): the busy-wait rule requires the `sleep` inside a loop body.
- **FR-009**: every changed or new guard has its cases in its `scripts/test-*-hooks.sh` suite, each new rule shown red
  with the rule deleted; the runner's watchdog and the watchdog's judgment have unit tests; the guard tables in
  `CLAUDE.md` and `docs/guards.md` carry the changes.

## Success Criteria *(mandatory)*

- **SC-001**: the two item-1 shapes, replayed live, are judged watched; the unwatched shape is still refused.
- **SC-002**: the 2026-09-30 exception dispatch's prompt, replayed through the judge, passes untouched.
- **SC-003**: a fake headless session that goes silent is ended and resumed by the runner within the threshold plus
  one check interval.
- **SC-004**: the watchdog, run once against fixtures, retitles, rings and nudges exactly the stalled fixtures (an
  interactive one in its own pane, a headless one in its dispatcher's), and nudges each once.
- **SC-005**: the 292 watcher command, replayed, is refused with a `CronCreate` call; the 291 waiters pass.
- **SC-006**: the reproduced item-6 command parses after the rewrite; the item-7 command passes.
- **SC-007**: `make hooks-test` and `make done` green.

## Assumptions

- The tmux pane of an interactive session is the one its registry entry (`~/.claude/sessions/<pid>.json`) names, as
  `~/.claude/hooks/tab-title.sh` reads it; the watchdog writes the title the same way, and the session's own next hook
  restores its usual title.
- "Waiting on the GM" is the registry's `waiting` status or a pending `AskUserQuestion`; an idle session whose last
  message ended in a prose question is not distinguishable and may be nudged - the nudge's text tells it to say so in
  one line and stop.
