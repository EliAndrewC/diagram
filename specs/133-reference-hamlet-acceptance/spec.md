# Feature Specification: The Reference Hamlet Is Accepted by the GM

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=133-reference-hamlet-acceptance`)

**Created**: 2026-08-25

**Status**: APPROVED by `spec-fidelity` - round 2 verdict **FAITHFUL** (2026-08-25), after round 1 returned one change. The skeleton may be built.

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

Inashiro (seed 4), the reference hamlet, is brought to the state where **the GM accepts it as the
developer** - one task at a time, each task named by the GM, each task timed - and the period is
itself a **dry run of the iteration workflow**, measuring whether the tooling lets a simple change
cost a simple amount of time.

## Why this exists (the GM's words)

- *"for the current period, I would like to focus on getting our reference hamlet to be exactly
  right. and address all known issues with it"*
- *"I would like to provide the tasks one at a time. Part of my reasoning for this is that I am
  going to use the length of time which each task takes to implement in order to measure the
  effectiveness of our tooling and our approach."*
- *"this is the dry run for how we will do this kind of feature iteration in the future."*
- *"iterations are expensive in terms of wall clock time. And if me asking for a simple change
  results in half an hour of work being done when it should have only taken five minutes, then
  that limits the number of changes that I can make in a single day."*

## The shape of the feature

This is **deliberately a skeleton**. Its task list holds the tooling the GM asked for at the very
beginning, then one open slot per task the GM will name, then the acceptance task. The GM's own
instruction: *"I don't want these results thrown off by the time that it will take to generate the
skeleton"* - so the skeleton phase (this spec, the tracker, the doctrine text) is NOT a measured
task, and every task the GM names afterwards IS.

The feature **stays in the clone until the GM accepts**: its last task cannot be ticked by a
session, so the gated route's feature-complete condition refuses to land engine work (feature 130
FR-011). The skeleton itself is pushed to main once, as the spec-number claim the project requires
and so a fresh session's clone carries it; after that, the route for any further push is decided
by the delta as always (`ci/delta.py` `is_engine`), never by this spec: any delta touching engine
paths - including `l7r/diagram/switches.py` - is GATED and is refused while T99 is open, which is
precisely the behavior SC-003 exists to observe. (Round 1 of the fidelity review struck a sentence
here that had pre-judged the route.)

## User Scenarios & Testing

### User Story 1 - A task, timed (Priority: P1)

The GM opens a fresh session and names one defect on the map. The session records when the task
was given, does the work, verifies it on Inashiro alone, records when it was done and what ran,
and reports the elapsed time with the result.

**Independent Test**: `tasks.md` carries, for the task, the GM's words, the given-at and done-at
timestamps, the elapsed minutes, and the list of gate/map runs the run-log shows in that window.

**Acceptance Scenarios**:

1. **Given** the GM names a task, **When** the session starts it, **Then** the task is appended to
   `tasks.md` with the GM's words verbatim and a `given` timestamp (UTC) before any work starts.
2. **Given** the task is done and verified, **Then** the entry gains `done`, the elapsed minutes,
   and the run-log entries in that window (every `make done`, `make reference`, `make map`), so
   the GM can ask *"why did that take so long?"* against a record rather than a memory.
3. **Given** a task took longer than its shape suggested, **Then** the entry says why, in one of
   the GM's three categories: more complicated than expected; ran lengthier tests than needed;
   more cycles than needed (small change, long test, repeat) - and, where it is the tooling, a
   follow-up task is proposed.

### User Story 2 - What AWS would have done (Priority: P1)

Remote is off for the whole period. Every time a paid run WOULD have started - a gated push that
would have dispatched, a `ci-check`, a `ci-image`, a `FULL=1` - the tooling records it, with the
estimate, so the period can be audited afterwards: *"were we about to spend many hours and many
dollars of tests?"*

**Independent Test**: throw remote off in a fixture; attempt each paid target; each attempt
leaves an auditable entry that no spend figure counts; `make ci-status` reports the count.

**Acceptance Scenarios**:

1. **Given** remote is off, **When** any paid target is attempted, or the gated route would have
   dispatched, **Then** a run-log entry with `where: would-have-dispatched` is written carrying
   the target, scope, estimated minutes and cost, the reason, and the commit - and it is NOT
   summed into month-to-date spend.
2. **Given** such entries exist, **When** `make ci-status` or `make audit` runs, **Then** a "Would
   have dispatched (remote off)" block lists them with a total estimated cost.
3. **Given** the period ends, **Then** the acceptance task's record includes the audit: how many
   times a paid run would have started, and for each whether it should have - a "no" is a tooling
   defect to fix, per the GM: *"if the answer turns out to be no, then that means that we need to
   make more tooling changes in order to be smarter about when we run the longer tests."*

### User Story 3 - The feature cannot reach main incomplete (Priority: P1)

The GM: *"our automated tooling should stop it from going back into main. Right? ... this will
also be a good test for seeing whether working on a feature through speckit triggers those gates
successfully. To be honest, I'm not sure how the tooling can know whether we're working on a
feature or not."*

**What exists today (the answer to the GM's question)**: the tooling knows the active feature from
`.specify/feature.json` in the clone (or `SPECIFY_FEATURE`), and the GATED route refuses to land
engine work unless that feature has no open task and a FAITHFUL spec (feature 130 FR-011). The
DIRECT route (docs, tests, ci/, config) does not consult the feature at all - which is the *"ways
to get things into main outside the context of features"* the GM suspected.

**Acceptance Scenarios**:

1. **Given** 133 has an open task and the clone's delta touches engine code, **When** the procedure
   runs, **Then** the push is refused - since FR-006 the in-progress check fires first and names
   `IN PROGRESS` (the gated route's `feature-complete` condition sits behind it). OBSERVED on this
   feature on 2026-08-25: the procedure refused this clone's own T05 push, naming
   `scripts/sync-with-main.sh` as outside the spec directory.
2. **Given** a feature has an open task, **When** any push is attempted from a clone whose delta
   touches its spec directory or whose pointer names it, **Then** the push is refused on BOTH
   routes unless the delta is that spec directory alone (FR-006, the GM's ruling).

### Edge Cases

- **The GM names a task the tooling cannot do in reference scope** (a knob wanting three maps): the
  session says so in the task entry and does the reference-map half; the rest is a task for after
  unlock.
- **A task turns up a defect elsewhere**: fixed in that task (constitution XIV), its time counted
  in that task and called out in the entry, so the measurement is honest about where time went.
- **A task's fix wants a pool map re-rolled**: refused by the lock; the entry says so; it waits.

## Requirements

- **FR-001**: The feature's final task is *"the GM accepts the current state of Inashiro"* and
  MUST be tickable only on the GM's explicit word, recorded verbatim in `tasks.md`.
- **FR-002**: Tasks are added ONE AT A TIME, on the GM's word, verbatim; the skeleton adds none
  of the GM's map tasks in advance.
- **FR-003**: Each GM task MUST carry the given/done UTC timestamps, the elapsed minutes, the
  run-log entries in that window, and - if the time was out of proportion - which of the GM's three
  causes applied and what follows from it.
- **FR-004**: With remote off, every attempt that would have started a paid run MUST be recorded
  as a `would-have-dispatched` run-log entry (target, scope, estimated minutes and cost, reason,
  commit), excluded from spend, and reported by `make ci-status` and `make audit`. This is built
  in the skeleton phase - *"part of this feature should, at the very beginning, involve modifying
  our tooling so that when AWS testing is turned off, we still track when it would have run."*
- **FR-005**: The acceptance task's record MUST include the audit of those entries: for each,
  should it have run? Every "no" names the tooling change it implies.
- **FR-006 (the GM's ruling, 2026-08-25)**: the DIRECT-route gap was put to the GM after the
  skeleton itself was pushed to main against their intent (*"even though we are literally working
  on a feature and that feature is not yet done, you still pushed back to main anyway"*). Ruled:
  **a feature in progress lands nothing, on either route.** The active feature is DERIVED - any
  `specs/NNN-*/tasks.md` with an open task that the delta touches or that `.specify/feature.json`
  names - so it cannot be evaded by not setting the pointer; there is no flag; the ONE exception,
  which the GM kept, is a delta consisting solely of that feature's own `specs/` directory (the
  spec-number claim). Enforced in `scripts/sync-with-main.sh` at push time, proven both ways in
  `scripts/test-sync-with-main.sh` (7d). Recorded cost: while a feature is open in a clone, that
  clone lands nothing else either - an unrelated fix goes through another clone.
- **FR-007**: The motivation - iteration wall-clock is the cost that limits how many changes the
  GM can make in a day; every command chosen, every tooling improvement, every interaction with
  the tooling is judged against it - MUST be written into the constitution, the root `CLAUDE.md`
  and the skill's `SKILL.md`/`CLAUDE.md` where it is not already, in the skeleton phase, as a
  project goal for every future session.

## Success Criteria

- **SC-001**: Every GM task in `tasks.md` has a measured elapsed time and a run-log window.
- **SC-002**: With remote off, zero paid runs happen and every would-have-run is on record.
- **SC-003**: The feature cannot land engine work while any task is open - observed, not assumed.
- **SC-004**: The GM ticks the acceptance task.

## Assumptions

- Feature 132's switches stay thrown for the whole period (remote off, scope reference).
- The skeleton phase is not measured; every GM-named task is.
- "Accepted by the GM as the developer" is the GM's judgment of the rendered map
  (`pool/hamlets/inashiro.png`), not a check passing.

## Review history (constitution XVI)

- **Round 1 (2026-08-25): CHANGES REQUIRED** - one: the spec had asserted that the Phase 0 tooling
  "lands DIRECT" when `switches.py` is engine code and would be GATED. Removed; the route is the
  delta's to decide and this feature's to observe. FR-006 (the DIRECT-route gap as a QUESTION) and
  pushing the skeleton to main were both judged faithful.
- **Round 2 (2026-08-25): FAITHFUL.** The change applied without new scope. Aside: the spec names
  `T99` by id; if the task ids change, that sentence goes stale.
- **FR-006 amendment (2026-08-25): FAITHFUL** at round 1. Reviewer's aside applied: User Story 3
  scenario 1 now names `IN PROGRESS` as the observed refusal, and records the live observation.

## Decisions Recorded (constitution XII - the reader who will click on it)

| feature | class | where |
|---|---|---|
| the farm privy as an independent outbuilding at the back door / gate / naya (T53) | ACCURATE (READ) | research/homesteads.md "The farmstead's fixtures"; settlements/homesteads.md "Farmstead fixtures" |
| the privy's 6 x 6 ft, the heap's 8 x 6, the bath's 6 x 6, the coop's 5 x 5, the stack's 10 x 3.5, the crown's 18 ft, every share band | GUESS (labeled) | same |
| the manure heap beyond the privy (T55) | ACCURATE in China (the Han pigsty-privy, READ); SUMMARY-ONLY in Japan | same |
| only the bath SHED share drawn, the in-house baths undrawn (T56) | ACCURATE (Sugiura's two forms) | same |
| the chicken coop in imperial China's proportions (T59) | ACCURATE that it existed and was widespread (READ); the share a GUESS | same |
| the household shrine rare (T58) - the GM chose between two attested patterns; the every-house pattern declined | DEVIATION by ruling, recorded with the alternative | same |
| the hokora drawn at the 6 ft small-shed module where the one measured stone is 1.3 ft; the vermilion, the ridge and the torii before it (T58, T62) | DEVIATION (legibility; the GM's glyph convention, ruled 2026-08-27) | same |
| the persimmon's four fruit dots | DEVIATION (a naming convention, not a season) | same |
| the straw rick and the hasa frames not drawn (T60) | DEFERRED (seasonal maps) | future-work/farming-communities.md |
