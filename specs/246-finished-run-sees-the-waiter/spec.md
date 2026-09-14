# Feature 246 - the finished-run guard sees the waiter

**Status**: IMPLEMENTED - FAITHFUL (`spec-fidelity`, round 1 of 5, 2026-09-13); the plan CLEAR at round 1. SC-003's live observation is taken after landing, because a session's hooks run from the mirror's copy (tasks.md T04).
**Request**: [`request.md`](request.md) - the GM's words verbatim, and the assessment they approved.
**Research**: [`research.md`](research.md) - the firing census, what a tracked run looks like in `/proc`, the double wakeup, the timer priced.
**Predecessors**: 170 (the finished-run rule), the still-going rule of 2026-09-12 (the same script), 227 (the proof-of-life clause on a waiter), 212 (a guard does the right thing and tells the session).

## Summary

The still-going rule of `finished-run-hooks.sh` refuses a turn that would close over a live `make` in the
session's clone. It asks one question - is a make alive - and cannot ask the second, is anyone waiting for
it, so it refuses a run the harness tracks and will wake the session for, a detached run with a live waiter
loop on its log, and a detached run nobody watches, all alike; and its "once per run" marker holds every
live make pid, so a four-phase gate is refused up to four times (R1: 18 refusals in its first day, 5 of them
repeats on a run already refused, every one in this session landing on a state that was already correct).
The GM asked what to do about it and approved this: the guard answers the second question mechanically,
lets a tracked run and a watched run through with one line of context, keys the refusal on the root make so
it truly fires once, and keeps the refusal for the one shape that can go unread - a detached run with no
watcher. The prescribed remedy also tells a tracked run apart, so it no longer produces a second wakeup for
an event the harness already reports. A periodic timer is priced and declined (R4).

## Functional requirements

- **FR-001 A harness-tracked run is let through.** A live make is TRACKED when one of its ancestors is the
  `claude` process (the harness), which is what a command run through the Bash tool's background mode
  looks like (R2). At Stop, a tracked run does not refuse the turn: the guard prints one line naming the
  run and saying the harness will wake the session when it finishes, exits 0, and records `permitted` with
  the rule `tracked-run`.
- **FR-002 A watched run is let through.** A live make is WATCHED when some process outside the hook's
  own ancestry is a file-watching loop (the `until`/`while` ... `grep` ... `sleep` shape the guard's stale
  census already recognizes) whose command names the file the make's stdout is written to. At Stop, a
  watched run does not refuse the turn: one line naming the run and its waiter, exit 0, `permitted` with the
  rule `waiter-armed`.
- **FR-003 An unwatched detached run is refused, once per run.** A live make that is neither tracked nor
  watched refuses the turn as today (exit 2, the message, `blocked` with `run-still-going`), keyed on the
  ROOT make of each run - the live make with no live make ancestor - so a phase child appearing does not
  refuse again. The second attempt on the same root still closes the turn (the release valve stands), and
  the marker is cleared when nothing is live.
- **FR-004 The message prescribes the loop for the shape that needs it.** The refusal's remedy names the
  detached run's own log (the target of its stdout) in the loop it prescribes, and says that a run started
  through the harness's background mode needs no loop because the harness wakes the session and this guard
  sees that.
- **FR-005 Mixed states.** With several live runs, any unwatched detached root refuses (listing every live
  run and marking each unwatched root); with none, every run is reported on one line each and the turn is
  let through.
- **FR-006 The suite proves each branch on real processes.** A make whose ancestor is a process named
  `claude` writing to a `tasks/*.output` file is permitted and recorded `tracked-run`; a detached make with a
  loop watching its log is permitted and recorded `waiter-armed`; a detached make with no watcher is refused
  once and then let through; a two-phase make (a target that runs `$(MAKE)` twice in sequence) is refused
  once and NOT again when its second phase is the live child - the R1 shape; a detached make whose only
  watcher names a different file is refused. `make hooks-test` stays green and the guard's rules are named
  in the firing log.
- **FR-007 The record.** The hook's header and the root CLAUDE.md row say the new rule and why; R1-R4 in
  `research.md`; the periodic-timer alternative is recorded as declined with the one case that would
  reopen it (R4), and the lost-notification fallback is filed in `future-work/cross-cutting.md`.

## Success criteria

- **SC-001** (FR-001, FR-002, FR-003, FR-005, FR-006): `scripts/test-finished-run-hooks.sh` green with the
  new cases, and `make hooks-test` green.
- **SC-002** (FR-003, FR-006): the two-phase case in the suite - one refusal, then exit 0 on the same run
  with a different live child.
- **SC-003** (FR-001): a `make done` started through the Bash tool's background mode in this session, and a
  turn ended while it runs, is not refused, and the context line appears - observed on the feature's own
  gate and recorded in tasks.md.
- **SC-004** (FR-004, FR-007): the message, the header, the CLAUDE.md row and the future-work entry say what
  the FRs say.
- **SC-005** (spec-wide): no engine code in the delta; lands DIRECT on a green `make hooks-test`.

## Decisions recorded

- **D1 - tracked is "an ancestor named `claude`", not a path pattern on the task file.** The harness's task
  file path is an implementation detail of the tool that could move; the harness process in the ancestry is
  what "the harness will notify" actually rests on. The task file is still read off that ancestor's stdout
  for the message. Read from `/proc` by pid, so nothing here can match its own command line (the 2026-07-25
  trap).
- **D2 - a waiter is recognized by the file it names, not by its pid or age**, exactly as the stale census
  does: at any instant the loop's visible process is its `sleep`. The file is the make's own stdout target,
  so a loop on some other file is not a wait on this run (FR-006's last case).
- **D3 - the refusal stays a refusal**, not a rewrite: a Stop payload carries no command, so there is
  nothing to rewrite and no token escape (the finding of the rule's own suite); the once-per-root release
  is the valve.
- **D4 - the timer is declined** (R4): polling with a period at a turn per tick, where the event wakeup
  exists twice over and did not fail. The one form that adds something - a single fallback for a LOST
  notification - waits for a lost notification to be observed.
- **D5 - a foreground make cannot be live at Stop**, so the guard need not consider it: a turn cannot end
  while the Bash tool is running a foreground command.

## Out of scope

- The finished-run (first) rule and the dead-producer (third) rule, unchanged.
- Any change to `no-poll-hooks.sh` or the proof-of-life clause.
- The fallback wakeup for a lost harness notification (D4, filed).

## Review history

- **Round 1 (2026-09-13, MODE 2): FAITHFUL.** Every clause of the approved assessment carried; D4's
  declined timer and FR-007's future-work line judged within (a priced alternative owes its record);
  nothing unrequested; scope not larger. One aside, not a finding: the dead-producer rule runs only when
  nothing is live, so a watched run killed mid-turn is reported at the next Stop rather than at once -
  the existing script's ordering, untouched here.
