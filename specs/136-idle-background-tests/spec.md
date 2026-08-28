# Feature Specification: Idle Sessions Run the Expensive Tests in the Background

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=136-idle-background-tests`)

**Created**: 2026-08-28

**Status**: APPROVED by `spec-fidelity` - round 3 verdict **FAITHFUL** (2026-08-28), after round 1 returned five changes (decisions embedded as requirements; the lock an unrequested addition; `make maps` under the lock; two suspend rules; nothing carried "never interrupts the merge") and round 2 one (a run in progress blocked the merge route - D9). Reviewer asides for the GM at acceptance: D9 throws away a nearly-finished run; whether such a run may finish detached is the GM's call.

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

**Acceptance**: **Given** the container was suspended (a wall-clock jump past the timer's own
awake count, threshold D2), **When** it resumes, **Then** no session starts the tests
immediately; each waits its own FULL wait again from the resume - the one rule, whatever the
suspend's length (the GM: "we wait an additional hour"; "long" is the detection threshold, D2).

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
- A prompt arrives DURING a run: the run is aborted at once and recorded as `aborted-on-prompt`
  (FR-006b d) - the GM never waits on a test they did not ask for.
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
  compares it with the wall clock; a wall-clock jump beyond the awake time larger than the
  threshold (D2: 5 minutes) is a suspend, and on a suspend the wait RESTARTS in full from the
  resume, whatever the suspend's length (the GM: "we wait an additional hour"). The threshold is a
  constant in one place.
- **FR-004** (a session DECISION beyond the request, D4 - the GM named the stagger as the herd
  fix; this adds a backstop): at most one idle run at a time across every session on the host - a
  lock in a location every session shares (`~/.claude/`); a session that finds it held defers by a
  further stagger (5-15 minutes, from the same hash) and retries until the GIVE-UP (6 hours after
  the arming, D4), after which that arming lapses without a run.
- **FR-005**: "This kind of test" is taken to be the tests the scope lock deferred and that
  surfaced at the unlock - the tripwire seeds and the tier sweep - and, by the GM's second quote,
  the other hamlet types' gates. The run is one Makefile target, `make idle-tests` (D1: `maps`,
  which under an UNLOCKED scope rolls the reference map, the tripwire seeds and every tier map),
  in the session's clone, launched fully detached (`setsid`), its output logged, its verdict
  appended to the clone's `dev/idle-log/` (an append-only directory of records, like
  `dev/run-log/`), and the last verdict printed to the session by the next UserPromptSubmit hook
  ("idle-tests: ran ... clean" / "FAILED: ...") so the session acts on it next turn. UNDER THE
  SCOPE LOCK the target rolls the reference map alone, because the lock admits no override by any
  variable, flag or environment (feature 132, the GM's own ruling) - so a locked period gets no
  nightly look at the tier, and that limitation is put before the GM as D1b rather than worked
  around.
- **FR-006**: The mechanism never runs in main's tree, arms only at a Stop (the end of a turn),
  and never runs more than once per arming.
- **FR-006b** (the GM: "I do not want to implement this in a way which interrupts the merge back
  into main"): an armed or running idle test never blocks, delays or invalidates the stop-work
  ritual or the merge route. Concretely: (a) the timer's state lives in `.git/`, outside the tree
  the ritual commits and the gate keys; (b) the timer does not START while any `make` is running
  in the clone (a gate or a sweep the session launched and detached) - it defers like a lock loss;
  (c) the idle run records its verification state under its own target name (`idle-tests`), which
  the push guard never reads as a green `done`, so it neither grants nor revokes a push; (d) a new
  prompt disarms the timer AND terminates any idle run in progress (the detached process group is
  killed; an `aborted-on-prompt` record is appended to `dev/idle-log/` and surfaced like any other),
  so no session-issued `make` target ever waits on an idle run and the ritual and the merge route
  are never blocked, delayed or refused because of one (D9).
- **FR-007**: Every rule has a test in `scripts/test-idle-tests-hooks.sh` run by `make hooks-test`
  (constitution XVIII): arm/disarm, the stagger band and its determinism, resume detection, the
  lock's exclusion and deferral, the record and its surfacing, the never-in-main rule, the abort of
  a run in progress on a prompt - with the
  clocks, the sleeps and the command injected so the tests run in seconds.
- **FR-008**: The doctrine is recorded: root `CLAUDE.md` (the guard table and the iteration-loop
  section), `docs/iteration-loop.md`, and the skill's `dev/switches.md` (an UNLOCKED scope now has
  a nightly look at the tier; a locked one still does not - D1b).
- **FR-009** (the GM: "the final task of the feature is me taking acceptance of those decisions"):
  the feature's last task is the GM's acceptance of the decisions listed below, tickable only on
  the GM's explicit word, recorded verbatim.

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

## Decisions for the GM (User Story 4, FR-009) - every choice made in the GM's place

| # | decision (where it binds) | why | alternative declined |
|---|---|---|---|
| D1 | "this kind of test" = `make idle-tests` = the `maps` target: the reference map, the tripwire seeds, the tier sweep (FR-005) | exactly what the lock deferred and what surfaced at the unlock; ~5-10 min unlocked; the full gate (21 min) also writes the verification stamp, which an idle run must not | the full gate; the 48-seed cohort (no pool sweep) |
| D1b | under a LOCKED scope the idle run rolls the reference map alone - the mechanism is silent about the tier during a locked period (FR-005) | the lock admits no override (feature 132, the GM's ruling: "we literally cannot"); an exemption for the idle run would be a flag the lock forbids | a lock exemption for idle runs (would need the GM to amend the lock's doctrine) |
| D2 | wait = 60 + (cksum(session name) mod 61) minutes of AWAKE time (FR-002); suspend = a wall-clock jump > 5 minutes beyond the ticks (FR-003) | the GM's band; tick-vs-wall needs no OS resume signal; 5 minutes is far above scheduler jitter and far below a nap | a random draw per arming (two sessions can collide) |
| D3 | any detected suspend restarts the FULL wait (FR-003) | "we wait an additional hour" read as the whole wait, since the stagger is the point | credit the awake time before the suspend |
| D4 | one runner at a time host-wide via `~/.claude/idle-tests.lock`; a loser defers 5-15 min (same hash) and retries; an arming lapses 6 h after it was set (FR-004) - an ADDITION beyond the stagger the GM named | the stagger makes collisions unlikely, not impossible; a lock makes "never two at once" true rather than probable; a loser still runs later that night | the stagger alone; a queue |
| D5 | the verdict surfaces as one line at the NEXT prompt (the UserPromptSubmit hook) and as a committed record in `dev/idle-log/` (FR-005) | the session must ACT on a red, and the next prompt is where every guard speaks | a push notification (noisy at night) |
| D6 | arm at every Stop; never in main; never self re-arming; timer state in `.git/` (FR-001, FR-006) | one idle = at most one run, the GM's shape; main is not a workspace | a nightly cron independent of sessions |
| D7 | the timer exits when its session is gone (`~/.claude/sessions/<pid>.json` and the process); it defers while a `make` runs in the clone; the idle verification record is its own target, never a `done` (FR-006b) | no orphan runs; the merge route untouched | a SessionEnd hook (not always delivered) |
| D9 | a prompt aborts an idle run in progress (kill the process group; an `aborted-on-prompt` record) (FR-006b d) | "I do not want to implement this in a way which interrupts the merge back into main" - the session's next `make done` or push must never wait on, or be refused because of, an idle run | let the run finish and refuse the session's makes meanwhile (round-2 finding: that blocks the merge route) |
| D8 | arming point = the Stop hook (the end of an assistant turn). If a Stop turns out to fire mid-task (a turn that ends awaiting a tool), the arming would be premature - to be MEASURED on this session (T06) before the timer design is fixed | it is the only "finished the round" signal the harness gives | a manual `make idle-arm` |

## Assumptions

- The Stop and UserPromptSubmit hook events are available to a session's `.claude/settings.json`
  (UserPromptSubmit already carries `clone-sync-hooks.sh`); a Stop hook fires at the end of every
  assistant turn.
- A `sleep`-based timer does not advance during a host suspend (nanosleep on CLOCK_MONOTONIC), so
  awake time versus wall time detects a suspend; the container's clock follows the host's.
- The host has `flock` (verified) and `setsid`.
