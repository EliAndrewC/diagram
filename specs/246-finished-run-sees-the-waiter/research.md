# Research - 246 The finished-run guard sees the waiter

## R1. What the guard's own firing log says

(Observed 2026-09-13; method: `make guard-log GUARD=finished-run`, the still-going refusals counted by
their recorded make pid.) The still-going rule is one day old.

| still-going refusals, 2026-09-13 | count |
|---|---|
| refusals | 18 |
| distinct gate runs | 13 |
| repeats on a run already refused | 5 |

Two runs were refused three times each within about half a minute - feature 245's second gate in this
session and one in the Kuwabata session - and every refusal in this session landed after a waiter loop had
been armed on the gate's log and the harness's own completion notification was on its way. The CLAUDE.md
row says "once per run, keyed on the make PIDs"; the marker holds the whole set of live make pids, a gate
is four phases (`static`, `_reference`, `test-full`, `test`), and each phase is a new child pid, so the set
changes at every phase boundary and the refusal fires again. Each refusal is a model round trip.

## R2. What a harness-tracked run looks like from `/proc`

(Observed 2026-09-13; method: a command run through the Bash tool's `run_in_background`, printing each
ancestor's `comm` and the target of its stdout descriptor.) The command's own shell writes to a pipe (the
`| tail` of the pipeline); its parent shell's stdout is the harness's task file,
`/tmp/claude-1000/<project>/<session>/tasks/<task>.output`; that shell's parent is the `claude` process
itself. The harness notifies the session when that task exits - it did so on all three of feature 245's
gates. A run detached with `setsid nohup ... > log &` re-parents to init: no ancestor is `claude`, its
stdout is the log it was given, and nothing notifies anyone - which is the shape of the 2026-09-12 run the
rule was written for (a detached `make done INCREMENTAL=0`, unread for 52 minutes). A foreground command
cannot be live when a turn ends, so every live make at Stop time is one of these two.

## R3. Two wakeups for one event

(Observed 2026-09-13; method: the task notifications this session received.) On each of feature 245's
three gates the session was woken twice - once by the harness for the backgrounded `make done`, once by the
waiter loop the refusal had prescribed - because the prescription does not distinguish a tracked run from a
detached one. The loop is the right instrument for a detached run only.

## R4. The timer alternative, priced

A prompt every N minutes until the run finishes is polling with a period in place of an event: each tick is
a turn, and a gate of a few minutes at a two-minute period is several turns of "still running". The event
wakeup already exists in two forms - the harness notification for a tracked run, the file watcher with its
proof-of-life clause for a detached one - and neither failed on any of this session's gates. A single long
fallback wakeup for a LOST notification is the one shape of timer that would add something, and how often
a tracked run's notification is actually lost is unmeasured (zero of three here); it is recorded rather
than built, as `future-work` material, until a lost notification is observed.
