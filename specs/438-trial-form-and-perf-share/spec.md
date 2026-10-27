# Feature Specification: the trial form and perf-share

**Feature Branch**: `438-trial-form-and-perf-share` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling, performance

**Approved**: the GM, 2026-10-27, "I agree, we should build the trial form and perf-share first since these kinds of tooling changes make everything fgaster."

**Input**: `request.md` (the GM's words, verbatim, and the two improvements of feature 437's report he chose).

## Why

Feature 437 (`specs/437-array-geometry-trial/report-trial.md`) took about 17 minutes from request to report; its spec took
three review rounds and a round-arbiter ruling - about 12 minutes of reviewer time - because the spec was reviewed while the
trial's evidence files changed beside it, and reading where the time was took two ad-hoc profile scripts. The two cheapest
fixes it named: a trial form (measure first, review once on fixed evidence) and a command that reads a module's share of the
stages' time.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Where a module's time is, in one command (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a module path and stages, **When** `make perf-share MODULE=<path> STAGES=<a,b>` runs, **Then** it reads the
   kept raw profile of each stage of the 40-household roll (seed 25 by default; `dev/perf-raw/`), and prints, per stage, the stage's profiled total, the module's own
   time and its share, the largest self-time functions of the stage, and the callers of the module's functions ranked by the
   module's time under them.
2. **Given** no `MODULE`, **Then** it reads `l7r/diagram/settlement/_geom/primitives.py`; given no `STAGES`, the four
   stages feature 437 read (homesteads, web, field, hinterland).

### User Story 2 - A trial measured first and reviewed once (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a question to trial, **When** `make trial SLUG=<slug>` runs, **Then** it claims a feature number and writes a
   trial brief (`spec.md` with `**Form**: trial`) - the question, the GM's words, the measurement, the rule that decides it,
   the evidence, the time - and `request.md` to fill.
2. **Given** a trial brief with no fidelity verdict, **Then** its pushes go through while the trial runs and its delta changes
   no engine code on net, so its evidence is committed and pushed as it is measured; **Given** the trial closed (its status
   `Done`), or a delta that changes the engine (`l7r/`) on net, **Then** the push needs its one fidelity verdict, taken on the
   brief with its evidence fixed, as any spec's.
3. **Given** a trial done, **Then** its time is reported as feature 437's was: `make feature-report F=<n>`'s split (the
   session's work, its waits, the agents' time) and a per-step breakdown.

## Requirements *(mandatory)*

- **FR-001**: `make perf-share [MODULE=<path>] [STAGES=<a,b,...>] [SEED=25] [HOUSEHOLDS=40] [PROFILES=<files>]` reads, per
  stage, a KEPT raw profile from `dev/perf-raw/`: the files `PROFILES` names, else the newest
  `*-seed<SEED>-hh<HOUSEHOLDS>-<stage>.prof`; a stage with neither is profiled then (`perf_profile.profile_stage`) and the
  output says so. `make perf-profile` names its raw profile with the household count from this feature on
  (`-seed<S>-hh<H>-<stage>.prof`), which is what lets a kept profile be matched to a size; an older profile, whose name holds
  no size, is read only when `PROFILES` names it. It prints per stage its profiled total, the module's own (self) time and share, the stage's
  largest self-time functions, and the callers of the module's functions ranked by the module's time under them; it ends
  with the module's share across all the stages read. It gates nothing.
- **FR-002**: Its defaults: `MODULE` `l7r/diagram/settlement/_geom/primitives.py`; `STAGES` homesteads, web, field,
  hinterland.
- **FR-003**: `make trial SLUG=<slug>` claims a number as `make claim` does and writes the trial brief from a template
  (`.specify/templates/trial-template.md`): `**Form**: trial`, the question, the `**Approved**:` line, the measurement, the
  trial's own decision rule (filled in per trial; feature 437's - land where the evidence shows time saved beyond the quick
  form's floor, otherwise set down - as the worked example), the evidence, and the time (`make feature-report`'s split and a
  per-step breakdown).
- **FR-004**: The review gate passes a trial brief with no verdict while its status is not `Done` and the push's delta changes
  the engine (`l7r/`) on net by nothing; a trial whose status opens `Done`, or whose push changes the engine, owes one fidelity
  verdict on the brief, as any spec does.
- **FR-006**: `docs/spec-kit-and-reviews.md` gains the trial form (when to use it - a question answered by measurement,
  before any decision to build - and its rules), the root `CLAUDE.md`'s development-workflow list one line pointing at it,
  and `docs/guards.md` the review gate's trial rule.
- **FR-007**: Nothing added refuses on a time (feature 435 FR-006 stands).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): `make perf-share PROFILES=<feature 437's four kept profiles>` prints their stages' shares of
  `primitives.py` and its callers table; a test reads a synthetic profile and checks every column, and a stage with no kept
  profile is profiled and named so.
- **SC-002** (FR-003): `make trial SLUG=x` (in a test fixture) writes `spec.md` with `**Form**: trial` and the template's
  sections.
- **SC-003** (FR-004): The review gate's tests pass a verdict-less trial not `Done` whose delta leaves the engine unchanged,
  and refuse it `Done` or with a net engine change.
- **SC-004** (FR-006): The three docs name the trial form and its gate rule.
- **SC-005** (FR-007): Nothing added refuses on a time.

## Edge Cases

- A trial whose spike is committed and reverted inside one push: the net engine change is empty, so it passes.
- A stage with no kept profile, profiled then, whose roll refuses before the stage is reached: perf-share names the refusal
  and goes on to the next stage.

## Review history

- 2026-10-27, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED - perf-share reads the kept profiles (matched by seed,
  size and stage); the separate engine refusal dropped, the verdict-less pass limited to no net engine change; each trial's
  own rule; the per-step time kept.
- 2026-10-27, round 2 (spec-fidelity-verify): FAITHFUL.

## Assumptions

- A trial is a feature like any other (its number, `request.md`, `report.md`, `make feature-report`, its landing when a spike
  wins); only its spec's form and its review's timing differ.
