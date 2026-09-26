# Feature Specification: A wakeup cannot outlive its purpose

**Feature Branch**: `263-stale-wakeup-guard` (no branch - `main`, per CLAUDE.md)

**Created**: 2026-09-26

**Status**: Draft

**Input**: the GM's request, verbatim in [`request.md`](request.md): these things *"need to be mechanical. It needs to
be literally impossible for them to do the wrong thing. Or else we will just end up doing the wrong thing a lot"* -
and, on the two layers the session proposed, *"Yes, please go ahead and implement that as a new feature."*

## The defect, measured

On 2026-09-26 a session scheduled a `ScheduleWakeup` as a fallback while a background agent ran. The agent reported
back and the work landed; the wakeup stayed pending, so every later turn ended with a session cron, and the GM's
tab (whose title hook reads `session_crons` from the Stop payload) showed the hourglass instead of the idle mark.
`ScheduleWakeup`'s own contract is `/loop`-only, and the harness already wakes a session when background work
finishes (and `agent-stall-hooks.sh` reports a stalled agent), so the fallback was never needed. The session's first
remedy was a memory note - which the GM rejected as a remedy: a rule that depends on being remembered is the rule
that gets broken.

A pending cron in the Stop payload is `{id, schedule, recurring, prompt}` - a `ScheduleWakeup` and a `CronCreate`
reminder are indistinguishable there (measured 2026-09-26 with one of each; `research.md` R1). The transcript tells
them apart: a wakeup's prompt is the `prompt` of a `ScheduleWakeup` call in the session's own transcript, and the
Stop hook is handed `transcript_path`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A fallback wakeup is refused before it exists (Priority: P1)

A session outside a live `/loop` calls `ScheduleWakeup` to guard a background run. The call is refused with the reason: the
harness wakes the session when background work finishes, `agent-stall-hooks.sh` reports a stall, and a reminder the
GM asked for is `CronCreate`'s job.

**Independent Test**: drive the hook with a `ScheduleWakeup` payload whose transcript has no live loop; it refuses.

**Acceptance Scenarios**:

1. **Given** a session with no live loop, **When** it calls `ScheduleWakeup`, **Then** the call is refused (exit 2)
   with the reason and the alternatives - and there is no escape token.
2. **Given** a live loop, **When** it calls `ScheduleWakeup` with the loop's own prompt (`/loop <input>`), **Then** the
   call passes; **When** it calls it with any other prompt (a fallback riding on the loop), **Then** it is refused.
3. **Given** a loop that was ended with `ScheduleWakeup(stop: true)`, **When** a later `ScheduleWakeup` is called,
   **Then** it is refused - a loop once run is not a loop live.

### User Story 2 - A turn cannot end with a stale wakeup pending (Priority: P1)

However a wakeup came to exist (before this guard, or in a `/loop` that has since stopped), a turn that would end with
it pending is stopped, naming the exact `CronDelete <id>` to run - at every turn end until it is cancelled.

**Independent Test**: drive the Stop hook with a payload carrying a cron whose prompt matches a `ScheduleWakeup` in
the transcript and no live loop; it blocks, naming the id.

**Acceptance Scenarios**:

1. **Given** a pending cron whose prompt is a `ScheduleWakeup` prompt from this transcript and no live loop, **When**
   the turn ends, **Then** the Stop hook blocks and names `CronDelete <id>`.
2. **Given** a pending cron made by `CronCreate` (its prompt matches no `ScheduleWakeup` call), **When** the turn ends,
   **Then** the hook does not block - a reminder the GM asked for is never cancelled by this guard.
3. **Given** a live loop, **When** a turn ends with the loop's own wakeup pending, **Then** the hook does not block.
4. **Given** the hook has already blocked for a cron id, **When** the next turn end still has it pending, **Then** it
   blocks again - there is no once-only valve, because one `CronDelete <id>` always satisfies it.

### Edge Cases

- An unreadable payload, a missing or unparsable transcript, or a failure of the check itself: the ScheduleWakeup layer
  REFUSES the call (it cannot show the call belongs to a live loop, and failing open would let the incident through
  whole); `stop: true` still passes. The Stop layer exits 0, because without the transcript it cannot tell a wakeup
  from a reminder the GM asked for, and must never block the latter.
- A background session (`kind: "bg"`) continuing a parked tab has its own transcript and session id; the rule reads
  that transcript, so it holds there as well.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A PreToolUse hook on `ScheduleWakeup` MUST refuse the call unless it is a live loop's own wakeup (a live
  loop, and a prompt that is the loop's: `/loop <input>` or the autonomous sentinel) or `stop: true`; the refusal MUST
  name the alternatives. There is no escape.
- **FR-002**: A Stop hook MUST block the turn from ending when a pending session cron's prompt equals the `prompt` of a
  `ScheduleWakeup` call in the session's transcript, unless it is a live loop's own wakeup; the block MUST name
  `CronDelete <id>` for each such cron. There is no escape.
- **FR-003**: A cron that no `ScheduleWakeup` call made MUST never be blocked or named.
- **FR-004**: The Stop hook MUST block at EVERY turn end at which a stale wakeup is pending - no once-only valve.
- **FR-005**: Both layers MUST record every firing through `_guardlog.sh`.
- **FR-006**: The guard MUST have a companion suite that `make hooks-test` runs, proving each refusal and each pass
  above against real payloads, and each layer MUST be shown to go red when its rule is removed.
- **FR-007**: The guard MUST appear in `CLAUDE.md`'s "What is enforced" table and in `docs/guards.md`.

### Key Entities

- **Wakeup**: a session cron whose prompt equals a `ScheduleWakeup` call's `prompt` in the same transcript.
- **Live loop**: the transcript's latest loop event is a `/loop` invocation (the command entry
  `<command-name>/loop</command-name>`, or a `loop` skill call) rather than a `ScheduleWakeup(stop: true)` (measured,
  `research.md` R3). A loop's own wakeup carries the prompt `/loop <input>` (or the autonomous sentinel).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-005): the suite proves a `ScheduleWakeup` outside a live loop refused (a `WAKEUP_OK` token
  changing nothing), a live loop's own wakeup passed, a fallback inside a live loop refused, a stopped loop not live,
  and every firing logged.
- **SC-002** (FR-002, FR-003, FR-004): the suite proves a stale wakeup blocks at every turn end naming its id, a
  `CronCreate` reminder never blocks, a live loop's own wakeup never blocks, a fallback after the loop stopped blocks.
- **SC-003** (FR-006, FR-007): `make hooks-test` green with the new suite; deleting either rule turns a case red; the
  guard is in both tables.

## Decisions Recorded

**N/A - no map drawn or stated.** This is tooling; it changes nothing a map draws or a modal says.

## Assumptions

- The tab-title hook (`~/.claude/hooks/tab-title.sh`, outside this repository) was fixed directly on 2026-09-26: a
  session is found by the hook payload's `session_id` in Claude Code's session registry, and a background
  continuation titles the tab that parked it, under that tab's name - which removes the "(2)" and restores the
  research tab's icon. It is not part of this repository and so not of this feature's code. Seen: after the fix every
  tab carried its icon (tmux pane titles read 2026-09-26 20:52: `⏳ Diagram research`, not `Diagram research (2)`).
- A loop abandoned without `stop: true` stays "live" to this guard, and its own `/loop` wakeup is exempt: that wakeup
  is the loop continuing, which is what `/loop` is for, and it fires and re-enters the loop rather than lingering.

## Review history

- Round 1 (2026-09-26, `spec-fidelity`, Opus): CHANGES REQUIRED, four items, all applied. (1) and (2) the `WAKEUP_OK`
  escape removed from both layers - no out-of-loop case needs one, and on the Stop layer it would let the incident
  itself through. (3) the `/loop` exemption scoped to a LIVE loop's own wakeup and measured (`research.md` R3). (4) the
  once-per-id valve removed: the Stop layer blocks at every turn end, since one `CronDelete` always satisfies it.
- Round 2 (2026-09-26, `spec-fidelity-verify`, Opus): FAITHFUL - all four round-1 items resolved.
- Amendment after acceptance (plan review, 2026-09-26, BLOCKED on D4): the fail-open edge case is scoped to the Stop
  layer; the ScheduleWakeup layer fails closed.
- Amendment review (2026-09-26, `spec-fidelity`, Opus): FAITHFUL; plan re-review CLEAR.
