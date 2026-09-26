# Implementation Plan: A wakeup cannot outlive its purpose

**Feature**: `263-stale-wakeup-guard` | **Date**: 2026-09-26 | **Spec**: [spec.md](spec.md)

## Summary

One guard script with two modes, its companion suite, two hook registrations and two table rows. No engine code.

## Technical Context

Bash + an embedded Python decision (the repo's guard idiom); `_guardlog.sh` for every firing. Tested by
`scripts/test-wakeup-hooks.sh` under `make hooks-test`. No performance bookends: no generator change.

## Constitution Check

- I, II, III, VII, VIII, IX, XI, XII: N/A - no UI in this repository, no map, no pool content, no setting detail.
- IV, V: PASS - no SOURCE block touched; `request.md` holds the GM's words.
- VI: PASS - each task names its verification; the suite drives the real hook with measured payload shapes.
- X: PASS - no Python module added to the engine; the guard's decision is tested case by case in its suite.
- XIII: PASS - the suite is new; `make hooks-test` is the regression bed and ran green.
- XVI: PASS - no exception: both layers, no escape, no once-only valve (spec-fidelity round 1).

## The design

### D1 - A wakeup is identified through the transcript

The Stop payload cannot tell a `ScheduleWakeup` from a `CronCreate` reminder (research.md R1), so a pending cron is a
wakeup when its prompt equals a `ScheduleWakeup` call's `prompt` in the transcript the hook is handed. A reminder
the GM asked for can never match, so FR-003 holds by construction.

### D2 - A loop is live, not merely once run

research.md R3: the latest loop event in the transcript - an invocation (the command entry or a `loop` skill call)
against a `ScheduleWakeup(stop: true)` - decides whether a loop is live; only a wakeup whose prompt is the loop's
(`/loop <input>` or the autonomous sentinel) is exempt, and only while the loop is live.

### D3 - The Stop layer blocks at every turn end

Exit 2 with the `CronDelete <id>` lines on stderr, every time a stale wakeup is pending - there is no once-only
state, because the block is always satisfiable by one call (spec-fidelity round 1).

### D4 - Closed on the call, open on the turn end

- **ScheduleWakeup layer: fails CLOSED.** An unreadable payload, a missing or unparsable transcript, an empty verdict (the
  decision crashed) or anything unforeseen is a refusal: the matcher already says the call is a `ScheduleWakeup`, one
  that cannot be shown to belong to a live loop is refused, and failing open would let the incident through whole
  (plan review 2026-09-26). `stop: true` still passes; a non-`ScheduleWakeup` tool is decided before the transcript is
  read, so failing closed never touches another tool.
- **Stop layer: fails OPEN** on an unreadable payload or transcript: without the transcript a wakeup cannot be told from
  a `CronCreate` reminder (R1), and blocking the GM's own reminder is what FR-003 forbids.

### D5 - The payload reaches the decision through a file

The decision's program is a heredoc, which IS python's stdin; a piped payload would be silently replaced - the first
cut judged an empty payload every time. Recorded at the point of change.

### D6 - Wired as the repo's other guards are

`.claude/settings.json`: a PreToolUse matcher `ScheduleWakeup` and a Stop entry, each commented with GUARD_EDIT_OK and
the reason. Rows in `CLAUDE.md` "What is enforced" and `docs/guards.md`.
