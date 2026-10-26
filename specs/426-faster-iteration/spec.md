# Feature Specification: Faster iteration - no wasted waits, no re-rolled seeds

**Feature Branch**: `426-faster-iteration` (no branch; work on `main` in the clone)

**Created**: 2026-10-26

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-26, "Yes please.  I want your first 3 proposed fixes from your previous message plus this improvement.  I also thought we were already omitting docstrings when hashing code, so please look for any other places where we're failing to strip docstrings when we should and fix those too as part of this."

**Input**: `request.md` (the GM's three messages, verbatim, and which proposals "your first 3" and "this improvement" name).

## Why

Feature 417's conversions took 40 minutes to nearly 2 hours each (measured from commit times, 2026-10-26: T48 ~1.5 h, T49
~40 min, T50 ~1 h 50 min). The engine work in each was minutes. The rest was, by the session's step-back:

- `make land` waiting the full 20 minutes twice for a claims round no agent was running (T50, about 40 minutes);
- seed rolls repeated after edits that changed no behavior: the roll cache keys a seed on the raw source of the functions it
  ran, docstrings and comments included, so a research-claim relabel or a comment fix re-rolled every seed through that
  function (the cohort log records 21 full 54-seed runs between T50's first probe and its landing);
- every probe rolling every seed even when the first new failure already rejected it (`settle_network`'s probe rolled all 54
  to find 18 failures), and HEAD's fresh block rolled again for each comparison;
- plan reviews blocking on the same two omissions (the red exit's wording, a step-by-step alone-off table) on T48 and T50.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A landing that cannot finish says so at once (Priority: P1)

The session runs `make land` on a task whose claims gate refuses for a reason only the session can cure (a finding the delta
introduced, a carry, a known drift awaiting a ruling). Today the landing runs the gate and the cohort, then waits 20 minutes
for a claims round that nothing is running. It should stop as soon as the gate has spoken, name the refusal and the command
that cures it, and land nothing.

**Why this priority**: the largest single measured waste (about 40 minutes on one task), for the smallest change.

**Independent Test**: on a fixture repository whose claims gate refuses with an introduced finding and no claims check in
flight, `make land` exits non-zero within a minute of its gates finishing, its message naming the finding.

**Acceptance Scenarios**:

1. **Given** the claims gate refuses with an INTRODUCED finding and no claims round is in flight, **When** `make land` runs,
   **Then** it does not wait; it exits naming the finding and the cure, nothing pushed or ticked.
2. **Given** a claims round IS in flight (a claims agent dispatched for this delta, its reply not yet recorded), **When**
   `make land` runs, **Then** it waits for it as today.
3. **Given** the claims gate passes, **When** `make land` runs, **Then** it lands as today.

---

### User Story 2 - A docs-only edit re-rolls nothing (Priority: P1)

The session rolls the cohort, then edits only docstrings, comments or research claims in the engine, then rolls again (or
runs `make land`). Every seed is served from the roll cache. The same holds for the render cache and every other place that
keys work on code, except where a docstring is the artifact's own content (the interactive class registry's docstrings are
modal text), which keeps keying on its bytes.

**Why this priority**: it removes most of the repeated rolls; the GM believed this already held.

**Independent Test**: roll a seed, add a docstring line and a comment to a function it executes, roll again: served from the
cache. Change a number in that function: rolled again. Edit a registry class's docstring: the page artifacts that show it are
rebuilt.

**Acceptance Scenarios**:

1. **Given** a cached roll, **When** only docstrings, comments, blank lines or formatting change in the functions it ran,
   **Then** the roll is served, not re-rolled.
2. **Given** a cached roll, **When** any executable token of a function it ran changes, **Then** it rolls again.
3. **Given** a docstring that IS artifact content (modal text, page text), **When** it changes, **Then** what shows it is
   rebuilt.
4. **Given** every place in the repository that hashes code to decide whether work is stale, **When** the audit is done,
   **Then** each one either ignores docstrings and comments or is recorded, at the point of change, as keying on them because
   they are content.

---

### User Story 3 - Iterate on failing seeds, stop at the first failure (Priority: P1)

While fixing or probing, the session rolls only what can change its answer: the seeds that failed or changed verdict last time
first, or only those; and stops at the first new failure when that alone settles the question. The landing check still rolls
every seed (most served from the cache).

**Why this priority**: it is the GM's explicit "pytest" request, and it turns a rejected probe from minutes into seconds.

**Independent Test**: with a recorded last run in which seeds 7 and 19 failed, `FAILED_FIRST=1` rolls 7 and 19 before the
others; `LAST_FAILED=1` rolls only them; `EXITFIRST=1` stops at the first seed whose verdict is a new failure and reports how
many seeds it did not roll.

**Acceptance Scenarios**:

1. **Given** a last run, **When** `make cohort FAILED_FIRST=1`, **Then** the failing and changed-verdict seeds roll first, then
   the rest.
2. **Given** a last run, **When** `make cohort LAST_FAILED=1`, **Then** only those seeds roll; with none recorded it says so
   and rolls all.
3. **Given** `EXITFIRST=1`, **When** a seed fails that did not fail in the baseline, **Then** the run stops, prints that seed's
   failure and the count left unrolled, and exits non-zero.
4. **Given** the landing (`make cohort-landing`, `make land`), **Then** every seed is judged, none of these modes applies.

---

### User Story 4 - One probe command compares against HEAD (Priority: P2)

To probe a change (a step off, a placer changed), the session applies the edit in a detached worktree and runs one command. It
rolls the landing cohort, the fresh block and the pool maps there, and prints each seed's verdict against HEAD's (new failure,
fixed, changed failure, same) and each pool manifest's changed fields. HEAD's verdicts per block are read from the stored
record for HEAD's engine, rolled only when none is stored. It supports `EXITFIRST=1`.

**Why this priority**: it replaces the hand-written probe scripts that cost time and caused a measurement mistake (T48 compared
failing seed sets, not verdicts).

**Independent Test**: in a worktree with a known regression, the probe prints the regressed seed as a new failure and the
moved pool fields; at HEAD's own tree it prints no differences and rolls HEAD's block at most once across two runs.

**Acceptance Scenarios**:

1. **Given** an edit that worsens one fresh seed's verdict, **When** the probe runs, **Then** that seed is listed as changed
   with both verdicts, even though the set of failing seeds is the same.
2. **Given** HEAD's verdicts for a block already stored, **When** the probe runs, **Then** HEAD's block is not re-rolled.
3. **Given** an edit that moves a pool manifest, **When** the probe runs, **Then** each changed field is listed by path, with
   lanes compared as drawn.

---

### User Story 5 - A plan section is born with what its review asks (Priority: P3)

`make task-add` writes a plan section that already holds the D35 red exit (the failing seeds recorded, the task set down, a
claim that it cannot be placed correctly ruled through `make arbiter-ask`) and, for a task that removes or converts steps, a
table of each step measured alone (verdicts, pool manifests moved, what the last resort did).

**Why this priority**: removes the plan-review rounds T48 and T50 each spent on these two items.

**Independent Test**: `make task-add F=<n> TITLE=...` writes a section whose checklist item 6 carries the D35 wording and whose
body carries the alone-off table's header.

**Acceptance Scenarios**:

1. **Given** a new task, **When** `make task-add` writes its section, **Then** item 6 states the D35 red exit.
2. **Given** a section passed in with `SECTION=`, **When** it lacks the red exit, **Then** `task-add` says so and names the
   wording.

### Edge Cases

- A claims round dispatched in another session for the same delta: the landing waits for it (scenario 1.2), not fail fast.
- A docstring edit to a function whose docstring a check reads (the claims gate reads claims from docstrings): the claims
  machinery keeps keying on the text - this feature changes what decides re-ROLLING, not what decides re-CHECKING claims.
- A function changed in a way only a decorator or default argument shows: still a code change (it is in the AST).
- `LAST_FAILED=1` with no prior run, or a prior run on a different seed block: rolls everything and says why.
- `EXITFIRST=1` at a seed that failed in the baseline too: not a new failure, the run goes on.
- The cache key change itself invalidates every stored roll once; the first run after landing re-rolls everything.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `make land` MUST NOT wait for a claims round when the claims gate's refusal is one no in-flight check can cure;
  it MUST exit non-zero naming each refusal and its cure, landing and ticking nothing.
- **FR-002**: `make land` MUST still wait (as today) when a claims check for the delta is in flight.
- **FR-003**: The roll cache's key MUST be blind to docstrings, comments, blank lines and formatting in the functions a roll
  executed, and MUST move on any other change to them (including module top level and class bodies as today).
- **FR-004**: Every code-hashing site that decides whether work is stale MUST be audited; each MUST ignore docstrings and
  comments unless a docstring is content of what it produces, recorded at the point of change with the reason. The audit's
  list of sites and rulings MUST be in the plan.
- **FR-005**: The render cache's engine fingerprint MUST follow FR-004 (docstring-blind except the content areas).
- **FR-006**: `make cache-audit` MUST pass after the key changes.
- **FR-007**: `make cohort` MUST offer `FAILED_FIRST=1`, `LAST_FAILED=1` and `EXITFIRST=1` as User Story 3 describes, reading
  "last run" from the cohort's own records for the same seed block.
- **FR-008**: The landing cohort and `make land` MUST judge every seed regardless of these modes.
- **FR-009**: A `make probe` command MUST roll the landing cohort, the fresh block and the pool in a given worktree and print
  per-seed verdict comparisons and per-manifest field changes against HEAD, reading HEAD's verdicts from a stored record per
  engine key and rolling them only when absent; it MUST accept `EXITFIRST=1`.
- **FR-010**: `make task-add` MUST write the D35 red exit into a new section's checklist item 6 and an alone-off table header,
  and MUST warn when a `SECTION=` file lacks the red exit.
- **FR-011**: Each new mode, target and refusal MUST carry its fix in its own output (tips live in error output) and a test
  that pins it; each fix MUST be shown to fire by a test that fails without it.

### Key Entities

- **Roll key**: the hash deciding whether a seed's stored roll still stands - its spec plus the executed functions' code.
- **Cohort record**: a run's per-seed verdicts, its seed block and its engine key (`dev/cohort-log/`).
- **HEAD baseline**: the cohort record for HEAD's engine key and a seed block, read instead of re-rolled.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a full cohort run, a docstring-, comment- or claims-only edit to engine code followed by the same cohort
  run re-rolls zero seeds.
- **SC-002**: A landing whose claims gate refuses with nothing in flight ends within 1 minute of its gates, never 20.
- **SC-003**: A probe whose change regresses a seed reports it after rolling only the seeds up to that seed under `EXITFIRST=1`.
- **SC-004**: Two probes in a row at the same HEAD roll HEAD's fresh block at most once.
- **SC-005**: A plan section written by `make task-add` carries the D35 red exit with no hand edit.
- **SC-006**: `make cache-audit` passes; no stored map or roll is served stale (an executable edit always re-rolls).

## Assumptions

- Tooling only: no engine behavior and no map changes (the cache key change re-rolls once, producing identical maps).
- "Content" docstrings are those the build reads to write an artifact: the interactive class registry (`gate-stamp`'s
  `RAW_AREAS`) and any docstring a page writer quotes; the plan's audit names each.
- The claims machinery's own fingerprints (which must see claim text in docstrings) are out of FR-003's scope and recorded so in
  the audit.
