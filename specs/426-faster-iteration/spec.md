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

- `make land` waiting its full claims wait (`CLAIMS_WAIT_S`, `scripts/land.py`) twice for a claims round no agent was running
  (T50; measured 2026-10-26 UTC, method: the two landing logs each ending "the claims round did not finish in 20 min");
- seed rolls repeated after edits that changed no behavior: the roll cache keys a seed on the raw source of the functions it
  ran, docstrings and comments included, so a research-claim relabel or a comment fix re-rolled every seed through that
  function (measured 2026-10-26 UTC, method: counting `dev/cohort-log/` records of 54 seeds between T50's first probe and its
  landing: 21);
- every probe rolling every seed even when the first new failure already rejected it (`settle_network`'s probe rolled every
  landing seed though its first new failure already rejected it; measured 2026-10-26 UTC, method: the probe's cohort log), and HEAD's fresh block rolled again for each comparison;
- plan reviews blocking on the same two omissions (the red exit's wording, a step-by-step alone-off table) on T48 and T50.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A landing that cannot finish says so at once (Priority: P1)

The session runs `make land` on a task whose claims gate refuses for a reason only the session can cure (a finding the delta
introduced, a carry, a known drift awaiting a ruling). Today the landing runs the gate and the cohort, then waits its full claims wait (`CLAIMS_WAIT_S`)
for a claims round that nothing is running. It should stop as soon as the gate has spoken, name the refusal and the command
that cures it, and land nothing.

**Why this priority**: the largest single measured waste (two full claims waits on one task, the Why section's first bullet),
for the smallest change.

**Independent Test**: on a fixture repository whose claims gate refuses with an introduced finding and no claims check in
flight, `make land` exits non-zero without entering the claims wait, its message naming the finding.

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

While fixing or probing, the session rolls only what can change its answer: the seeds that failed last time first, or only
those; and stops at the first failing seed when that alone settles the question. The landing check still judges every seed, and
a seed whose stored roll still stands (FR-012) is served, not rolled.

**Why this priority**: it is the GM's explicit "pytest" request, and it turns a rejected probe from minutes into seconds.

**Independent Test**: with a recorded last run on the same seed block in which seeds 7 and 19 failed, `FAILED_FIRST=1` rolls 7
and 19 before the others; `LAST_FAILED=1` rolls only them; `EXITFIRST=1` stops at the first seed that fails and reports how many
seeds it did not roll.

**Acceptance Scenarios**:

1. **Given** a last run, **When** `make cohort FAILED_FIRST=1`, **Then** the seeds that failed in it roll first, then the rest.
2. **Given** a last run, **When** `make cohort LAST_FAILED=1`, **Then** only the seeds that failed in it roll; with no last run
   on that seed block it says so and rolls all.
3. **Given** `EXITFIRST=1`, **When** any seed fails, **Then** the run stops, prints that seed's failure and the count left
   unrolled, and exits non-zero.
4. **Given** the landing (`make cohort-landing`, `make land`), **Then** every seed is judged, none of these modes applies.

---

### User Story 3b - A passing seed is not rolled again for the landing (Priority: P1)

The session rolls the seeds while developing (in the clone or a detached worktree), then runs `make cohort-landing` or `make
land` with no change to the code those seeds execute. Every seed is served from the rolls already stored; none is rolled again.

**Why this priority**: the GM's own example ("run the seeds locally and then do a `make landing`").

**Independent Test**: `make cohort N=48 FRESH=0` in a clone, then `make cohort-landing` with no engine change: it reports every
seed served and rolls none; the same after a docstring-only edit (User Story 2).

**Acceptance Scenarios**:

1. **Given** a full cohort run in the clone and no code change, **When** `make cohort-landing` runs, **Then** it rolls no seed.
2. **Given** the same seeds rolled in a detached worktree of the clone, **When** the clone's landing runs at the same code,
   **Then** it rolls no seed.
3. **Given** a change to a function some seeds execute, **When** the landing runs, **Then** only those seeds roll.

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
claim that it cannot be placed correctly ruled through `make arbiter-ask`) and a
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
- `make probe EXITFIRST=1` at a seed that failed the same way at HEAD (its baseline: HEAD's stored verdicts for that seed
  block): not a new failure, the probe goes on; `make cohort EXITFIRST=1` stops at any failing seed.
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
- **FR-007**: `make cohort` MUST offer `FAILED_FIRST=1` and `LAST_FAILED=1` (the seeds that FAILED in the last run, read from
  the cohort's own records for the same seed block) and `EXITFIRST=1` (stop at the first seed that fails, whatever it did
  before), as User Story 3 describes.
- **FR-008**: The landing cohort and `make land` MUST judge every seed regardless of these modes.
- **FR-009**: A `make probe` command MUST roll the landing cohort, the fresh block and the pool in a given worktree and print
  per-seed verdict comparisons and per-manifest field changes against HEAD, reading HEAD's verdicts from a stored record per
  engine key and rolling them only when absent; it MUST accept `EXITFIRST=1`, which stops the probe at the first seed whose
  verdict is worse than HEAD's for that seed (a new or changed failure; HEAD's stored verdicts are its baseline).
- **FR-010**: `make task-add` MUST write the D35 red exit into a new section's checklist item 6 and an alone-off table header,
  and MUST warn when a `SECTION=` file lacks the red exit.
- **FR-011**: Each new mode, target and refusal MUST carry its fix in its own output (tips live in error output) and a test
  that pins it; each fix MUST be shown to fire by a test that fails without it.
- **FR-012**: `make cohort-landing` and `make land` MUST serve every seed whose stored roll still stands under FR-003's key,
  wherever it was rolled (the clone or a worktree of it), and roll only the rest; a test pins that a landing right after a
  full cohort run at the same code rolls no seed.

### Key Entities

- **Roll key**: the hash deciding whether a seed's stored roll still stands - its spec plus the executed functions' code.
- **Cohort record**: a run's per-seed verdicts, its seed block and its engine key (`dev/cohort-log/`).
- **HEAD baseline**: the cohort record for HEAD's engine key and a seed block, read instead of re-rolled.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a full cohort run, a docstring-, comment- or claims-only edit to engine code followed by the same cohort run or
  the landing cohort re-rolls zero seeds.
- **SC-002**: A landing whose claims gate refuses with nothing in flight never enters the claims wait: it ends once its gates
  have run (a target, not a measurement).
- **SC-003**: A probe whose change regresses a seed reports it after rolling only the seeds up to that seed under `EXITFIRST=1`.
- **SC-004**: Two probes in a row at the same HEAD roll HEAD's fresh block at most once.
- **SC-005**: A plan section written by `make task-add` carries the D35 red exit with no hand edit.
- **SC-006**: `make cache-audit` passes; no stored map or roll is served stale (an executable edit always re-rolls).

## Assumptions

- "Omitting docstrings" is read as the GM's "if the code didn't change": comments, blank lines and formatting are ignored
  too - none changes what a roll does.

- Tooling only: no engine behavior and no map changes (the cache key change re-rolls once, producing identical maps).
- "Content" docstrings are those the build reads to write an artifact: the interactive class registry (`gate-stamp`'s
  `RAW_AREAS`) and any docstring a page writer quotes; the plan's audit names each.
- The claims machinery's own fingerprints (which must see claim text in docstrings) are out of FR-003's scope and recorded so in
  the audit.

## Review history

- 2026-10-26, first reading, NOT-REVIEWABLE (not a round; substance not read). Figures with a unit carry no `m:<key>`,
  one-shot label (date and method) or round label: (1) Success Criteria SC-002, its time threshold and the "never" figure
  beside it (spec-lint check 5 reports this one); (2) User Story 1's Independent Test, the same time threshold; (3) User
  Story 1's "Why this priority", the measured waste on one task; (4) Why, first bullet, the length of each wait, the count of
  waits and the T50 total (if the wait length is the configured timeout, point at the constant); (5) Why, second bullet, the
  count of full runs and the seeds per run, sourced to the cohort log but undated; (6) Why, third bullet, the seeds
  `settle_network`'s probe rolled and the failures it found. The opening line of Why (T48-T50 durations, from commit
  times, dated) is labeled and stands. A threshold that is a target rather than an observation should say so. Record or
  label these and re-dispatch as a first reading.
- 2026-10-26, round 1 (first reading of substance; the NOT-REVIEWABLE return above was not a round), spec-fidelity MODE 2:
  **CHANGES REQUIRED**. Figures: spec-lint passes, and every Why figure carries a dated method. One bare figure remains
  (item 4). It is the configured wait that the Why already names by its constant, so it is listed here rather than returned
  NOT-REVIEWABLE a second time. Clause walk: fix 1 is carried by FR-001/FR-002; fix 2 by FR-009 (generalized from "switch a
  step off" to any edit applied in a worktree, which is acceptable); fix 3 by FR-010 (the `SECTION=` warning enforces the
  template and is not new behavior); the docstring audit by FR-004/FR-005/FR-006. The content-docstring and
  claims-machinery carve-outs follow from the GM's own "when we should". FR-008 and FR-011 are enforcement. The approval
  line quotes the GM approving this feature.
  1. **FR-007, User Story 3 scenario 3, and the Edge Case "`EXITFIRST=1` at a seed that failed in the baseline too: not a
     new failure, the run goes on"** narrow the GM's "stop after the first failing seed without running the others" to
     "first NEW failure against a baseline". On the loop the GM described ("if we're trying to fix failing seeds ... if
     those are still failing then only run them"), a seed that failed last time and still fails is never a new failure.
     So no combination of `FAILED_FIRST`, `LAST_FAILED` and `EXITFIRST` stops on it, and the mode does not serve the
     purpose he gave it. NOT LEGITIMATE for `make cohort`. Fix: in `make cohort`, `EXITFIRST=1` MUST stop at the first
     seed that fails, whatever the baseline. The new-failure-against-HEAD rule belongs only to the probe (FR-009), whose
     stated purpose is comparison against HEAD. Either delete the edge case or limit it to `make probe`, and define "the
     baseline", which the spec uses without defining.
  2. **User Story 3 scenarios 1-2 / FR-007, "failing and changed-verdict seeds".** The GM said "start with the failing
     seeds and if those are still failing then only run them". If "changed-verdict" can include a seed that PASSED last
     run, `LAST_FAILED=1` re-rolls passing seeds, which is what he asked to stop. Define the set as seeds that failed in
     the last run (a seed failing differently is still failing), or drop "changed-verdict".
  3. **MISSING: the GM's clause "if we run the seeds locally and then do a `make landing` then we don't want to rerun
     them if the code didn't change since last time"** (and, in his first message, the "confirmation in the clone" and
     "the landing itself" re-runs). No FR carries it. FR-003 changes the key but does not require the landing to read the
     cache an earlier run filled, and SC-001 covers only "the same cohort run". User Story 3's "most served from the
     cache" is an unmeasured premise. Add an FR: `make cohort-landing` and `make land`, wherever they run, MUST serve
     every seed whose roll key is unchanged since an earlier `make cohort` run, and a test MUST pin it. If the cache
     already does this, the FR plus its test is enforcement. If the cache is per-tree, it is the work.
  4. **User Story 1, its claims-wait figure (now pointed at `CLAIMS_WAIT_S`)**, is a figure with a unit and no label. Point it at `CLAIMS_WAIT_S`, as the
     Why's first bullet does.
  Not numbered: FR-003 and FR-004 widen "docstrings" (the GM's word) to comments, blank lines and formatting. This serves
  his "if the code doesn't change" and is free with an AST hash, but the plan should say so where the GM can see it. User
  Story 5 makes the alone-off table conditional ("for a task that removes or converts steps"), while FR-010 writes it
  unconditionally. Make them agree with FR-010.
- 2026-10-26, round 2, spec-fidelity-verify MODE 3: **FAITHFUL**. Item 1 RESOLVED: FR-007 and User Story 3 scenario 3 make
  `make cohort EXITFIRST=1` stop at any failing seed; the new-failure rule is confined to `make probe` (FR-009, the edge case),
  its baseline defined as HEAD's stored verdicts for the seed block, consistent with SC-003 and the HEAD baseline entity.
  Item 2 RESOLVED: "changed-verdict" is gone; FR-007 and scenarios 1-2 name the seeds that FAILED in the last run. Item 3
  RESOLVED: FR-012 and User Story 3b carry the GM's "run the seeds locally and then do a `make landing` ... don't rerun them"
  with a pinning test; serving a stored roll is still judging the seed, so FR-008 and scenario 4 stand; SC-001 now covers the
  landing cohort; the Independent Test's `N=48 FRESH=0` is what `make cohort-landing` rolls (Makefile). Item 4 RESOLVED: User
  Story 1 points at `CLAIMS_WAIT_S`. Both notes acted on (Assumptions; User Story 5 now unconditional, agreeing with FR-010).
  No contradiction introduced; spec-lint passes. Read in full: the diff, and the grep hits for FR-003/007/008/009/012,
  SC-001/003, EXITFIRST, LAST_FAILED, FAILED_FIRST, baseline, cohort-landing and CLAIMS_WAIT_S (spec.md lines 20, 35, 82-120,
  125-133, 150-155, 167-171, 181-218, 231), plus request.md.
