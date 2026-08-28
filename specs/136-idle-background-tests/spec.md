# Feature Specification: Idle Sessions Run the Expensive Tests in the Background

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=136-idle-background-tests`)

**Created**: 2026-08-28

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI)

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

When a session has finished its round of work and the GM has given it nothing new for a while, it
kicks off the expensive deferred tests in the background - after a wait of one to two hours that
is staggered per session, restarted when the laptop resumes from a suspend, and never taken by two
sessions at once - so an expensive test costs the GM no waiting at all.

## Why this exists (the GM's words)

- *"a test which is relatively expensive in terms of me having to wait for it time becomes very
  cheap because it is largely going to run unattended"*
- *"I would not want to open my laptop and then suddenly have every session fire off the
  expensive tests. That would be bad."*
- *"if we are able to detect when the laptop has resumed after a long suspend, then we don't just
  immediately kick things off ... Instead, we wait an additional hour"*
- *"between one and two hours with a randomly selected time ... based on the hash of the session
  name ... And that solves the thundering herd problem"*

The motivating measurement: the reference-hamlet period (feature 133) locked the scope for two
days; at the unlock four tripwire regressions surfaced and cost a 20-minute bisect to attribute,
where a nightly look would have named each on the day it was made.

## User Scenarios & Testing

### User Story 1 - the idle session runs the tests (Priority: P1)

The session finishes a turn (the GM's last request is done, or the session is waiting on the GM).
Nothing arrives for the session's wait (60-120 minutes, fixed per session). The session's clone
then runs the expensive tests in the background and records the result where the session sees it
on its next turn.

**Acceptance**: **Given** a session whose last turn ended at T with nothing since, **When** T +
wait passes with no new prompt and no suspend, **Then** the tests start in that session's clone,
detached from the session's own tools, and their verdict is written to the clone's idle-test log.
**Given** a new prompt arrives before the wait ends, **Then** nothing starts and the wait is
cancelled (it re-arms at the end of that turn).

### User Story 2 - the laptop resumes (Priority: P1)

The GM closes the laptop for the night. Every session has been idle far longer than its wait.

**Acceptance**: **Given** the container was suspended for longer than the session's wait,
**When** it resumes, **Then** no session starts the tests immediately; each waits its own full
wait again from the resume. **Given** a suspend shorter than the wait, **Then** the wait is simply
extended by the time suspended (no test starts within the wait's span of awake time).

### User Story 3 - many sessions, one runner (Priority: P1)

The GM runs several sessions at once; all go idle together.

**Acceptance**: **Given** N idle sessions, **When** their waits end, **Then** they end at
different minutes (the per-session stagger from the session name), **and** at most one session's
tests run at a time - a session whose wait ends while another's tests are running defers and tries
again later rather than starting a second run.

### User Story 4 - the GM reviews the decisions (Priority: P2)

**Acceptance**: the spec's "Decisions for the GM" section lists every design choice the session
made in the GM's place (what is run, the thresholds, where results surface, what counts as idle);
the feature's last task is the GM's acceptance of those decisions, in their words.

### Edge Cases

- A session that was never named has no stagger seed: it uses the clone's directory name; a
  session outside any clone (main's tree) never arms - main is not a workspace.
- The tests are already red when they start (a red reference map): the run records the red and
  stops at the first problem, like `make maps`.
- The laptop resumes DURING a run: the run continues (the detached process survives the suspend);
  the next arming starts from the next Stop.
- The `scope` switch is locked: the idle run rolls what the lock allows (`make maps` under the
  lock is the reference map alone) and says so in its record - it never widens the scope.
- The session ends (the terminal closes) with a wait armed: the timer notices its session is gone
  (the transcript stops growing / the sessions record is gone) and exits without running.

## Requirements

### Functional Requirements

- **FR-001**: A session ARMS an idle wait at the end of every turn (the Stop hook) and DISARMS it
  when a new prompt arrives (the UserPromptSubmit hook). Arming when a wait is already armed is a
  no-op; disarming when none is armed is a no-op.
- **FR-002**: The wait is 60 + (h mod 61) minutes, where h is a stable hash of the session's name
  (the same source the clone name derives from), so a session's wait is fixed and two sessions
  differ unless their names hash alike. The band is a constant in one place.
- **FR-003**: Resume detection: the timer counts its own awake time (a loop of short sleeps) and
  compares it with the wall clock; a wall-clock jump of more than 5 minutes beyond the awake time
  is a suspend. On a suspend the wait RESTARTS in full from the resume (the GM: "we wait an
  additional hour"). The threshold is a constant in one place.
- **FR-004**: At most one idle run at a time across every session on the host: a lock in a
  location every session shares (`~/.claude/`); a session that finds it held defers by a further
  stagger (5-15 minutes, from the same hash) and retries, up to the end of the day's window.
- **FR-005**: The run is `make maps` in the session's clone - the tripwire and the tier sweep the
  scope lock defers - launched fully detached (`setsid`), its output logged, its verdict appended to
  the clone's `dev/idle-log/` (an append-only directory of records, like `dev/run-log/`), and the
  last verdict printed to the session by the next UserPromptSubmit hook ("idle tests ran at HH:MM:
  clean" / "FAILED: ...") so the session acts on it next turn. What is run is a single Makefile
  target the GM can change.
- **FR-006**: The mechanism never runs in main's tree, never runs while the session's own Bash is
  mid-command (a Stop marks the end of a turn, which is the only arming point), and never runs
  more than once per arming.
- **FR-007**: Every rule has a test in `scripts/test-idle-tests-hooks.sh` run by `make hooks-test`
  (constitution XVIII): arm/disarm, the stagger band and its determinism, resume detection, the
  lock's exclusion and deferral, the record and its surfacing, the never-in-main rule - with the
  clocks, the sleeps and the command injected so the tests run in seconds.
- **FR-008**: The doctrine is recorded: root `CLAUDE.md` (the guard table and the iteration-loop
  section), `docs/iteration-loop.md`, and the skill's `dev/switches.md` (the lock's accepted cost
  now has a nightly look).

### Key Entities

- **Idle wait**: per session; state in the clone's `.git/idle-tests.json` (armed-at, wait minutes,
  session name, timer pid).
- **Idle-log record**: `dev/idle-log/<utc>-<session>.json`: when, clone commit, target, verdict,
  failures, wall time, whether a suspend restarted the wait and how many deferrals the lock cost.
- **Host lock**: `~/.claude/idle-tests.lock` held for the run's duration.

## Success Criteria

- **SC-001**: An idle session's tests run without any GM wait: measured as a record in
  `dev/idle-log/` whose start time is ≥ 60 minutes after the session's last Stop.
- **SC-002**: After a simulated suspend longer than the wait, no run starts within the full wait
  of awake time (the test proves it with injected clocks).
- **SC-003**: With three sessions armed at the same instant, three distinct waits and never two
  concurrent runs (the test proves it with the lock).
- **SC-004**: `make hooks-test` green with the new guard and its companion; `make quick` green.

## Decisions for the GM (User Story 4)

Listed in `plan.md` "Decisions made in the GM's place" as they are made; copied here at the end.

## Assumptions

- The Stop and UserPromptSubmit hook events are available to a session's `.claude/settings.json`
  (UserPromptSubmit already carries `clone-sync-hooks.sh`); a Stop hook fires at the end of every
  assistant turn.
- A `sleep`-based timer does not advance during a host suspend (nanosleep on CLOCK_MONOTONIC), so
  awake time versus wall time detects a suspend; the container's clock follows the host's.
- The host has `flock` (verified) and `setsid`.
