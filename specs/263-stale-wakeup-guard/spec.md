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

A session outside `/loop` calls `ScheduleWakeup` to guard a background run. The call is refused with the reason: the
harness wakes the session when background work finishes, `agent-stall-hooks.sh` reports a stall, and a reminder the
GM asked for is `CronCreate`'s job.

**Independent Test**: drive the hook with a `ScheduleWakeup` payload whose transcript has no `/loop`; it refuses.

**Acceptance Scenarios**:

1. **Given** a session whose transcript shows no `/loop`, **When** it calls `ScheduleWakeup`, **Then** the call is
   refused (exit 2) with the reason and the alternatives.
2. **Given** a session running `/loop`, **When** it calls `ScheduleWakeup`, **Then** the call passes.
3. **Given** a `ScheduleWakeup` whose `reason` or `prompt` carries `WAKEUP_OK` with a reason of two words or more,
   **When** it is called, **Then** it passes and the escape is recorded like every other escape.

### User Story 2 - A turn cannot end with a stale wakeup pending (Priority: P1)

However a wakeup came to exist (before this guard, through the escape, in a `/loop` that has since stopped), a turn
that would end with it pending is stopped, naming the exact `CronDelete <id>` to run.

**Independent Test**: drive the Stop hook with a payload carrying a cron whose prompt matches a `ScheduleWakeup` in
the transcript and no `/loop`; it blocks, naming the id.

**Acceptance Scenarios**:

1. **Given** a pending cron whose prompt is a `ScheduleWakeup` prompt from this transcript, no `/loop`, **When** the
   turn ends, **Then** the Stop hook blocks and names `CronDelete <id>`.
2. **Given** a pending cron made by `CronCreate` (its prompt matches no `ScheduleWakeup` call), **When** the turn ends,
   **Then** the hook does not block - a reminder the GM asked for is never cancelled by this guard.
3. **Given** a session running `/loop`, **When** a turn ends with its wakeup pending, **Then** the hook does not block.
4. **Given** a wakeup whose prompt carries `WAKEUP_OK` with a reason, **When** the turn ends, **Then** it does not block.
5. **Given** the hook has already blocked once for a given cron id, **When** the next turn end sees the same id,
   **Then** it does not block again - once per wakeup, never a loop (the `escalation-hooks.sh` rule).

### Edge Cases

- A payload with no `transcript_path`, an unreadable transcript, or malformed JSON: the hook exits 0 (a guard that
  cannot read its inputs does not refuse on a guess), and the Stop layer still sees no wakeup to name.
- A background session (`kind: "bg"`) continuing a parked tab has its own transcript and session id; the rule reads
  that transcript, so it holds there as well.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A PreToolUse hook on `ScheduleWakeup` MUST refuse the call unless the session's transcript shows a
  `/loop` invocation or the call carries `WAKEUP_OK` with a reason; the refusal MUST name the alternatives.
- **FR-002**: A Stop hook MUST block the turn from ending when a pending session cron's prompt equals the `prompt` of a
  `ScheduleWakeup` call in the session's transcript, unless the session shows `/loop` or that prompt carries
  `WAKEUP_OK` with a reason; the block MUST name `CronDelete <id>` for each such cron.
- **FR-003**: A cron that no `ScheduleWakeup` call made MUST never be blocked or named.
- **FR-004**: The Stop hook MUST block at most once per cron id.
- **FR-005**: Both layers MUST record every firing and escape through `_guardlog.sh`, and the escape MUST state a reason
  (the feature-170 floor).
- **FR-006**: The guard MUST have a companion suite that `make hooks-test` runs, proving each refusal and each pass
  above against real payloads, and each layer MUST be shown to go red when its rule is removed.
- **FR-007**: The guard MUST appear in `CLAUDE.md`'s "What is enforced" table and in `docs/guards.md`.

### Key Entities

- **Wakeup**: a session cron whose prompt equals a `ScheduleWakeup` call's `prompt` in the same transcript.
- **Loop session**: a session whose transcript shows `/loop` invoked (the command, or the `loop` skill).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-001, FR-005): the suite proves a `ScheduleWakeup` outside `/loop` refused, inside `/loop` passed, and
  escaped with a reason passed and logged.
- **SC-002** (FR-002, FR-003, FR-004): the suite proves a stale wakeup blocks once naming its id, a `CronCreate`
  reminder never blocks, a `/loop` wakeup never blocks.
- **SC-003** (FR-006, FR-007): `make hooks-test` green with the new suite; deleting either rule turns a case red; the
  guard is in both tables.

## Decisions Recorded

**N/A - no map drawn or stated.** This is tooling; it changes nothing a map draws or a modal says.

## Assumptions

- The tab-title hook (`~/.claude/hooks/tab-title.sh`, outside this repository) was fixed directly on 2026-09-26: a
  session is found by the hook payload's `session_id` in Claude Code's session registry, and a background
  continuation titles the tab that parked it, under that tab's name - which removes the "(2)" and restores the
  research tab's icon. It is not part of this repository and so not of this feature's code.
- `/loop` is detected from the transcript, where its invocation is recorded; a `/loop` session keeps that marker for
  its life, which errs toward passing (the Stop layer's `/loop` exemption can let a wakeup outlive a stopped loop -
  priced: `/loop` ends by `ScheduleWakeup(stop: true)`, which removes its wakeup, so the case needs a loop abandoned
  without stopping).
