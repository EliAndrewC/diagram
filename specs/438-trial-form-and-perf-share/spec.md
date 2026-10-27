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

1. **Given** a module path and stages, **When** `make perf-share MODULE=<path> STAGES=<a,b>` runs, **Then** it profiles each
   stage of the 40-household roll (seed 25 by default) and prints, per stage, the stage's profiled total, the module's own
   time and its share, the largest self-time functions of the stage, and the callers of the module's functions ranked by the
   module's time under them.
2. **Given** no `MODULE`, **Then** it reads `l7r/diagram/settlement/_geom/primitives.py`; given no `STAGES`, the four
   stages feature 437 read (homesteads, web, field, hinterland).

### User Story 2 - A trial measured first and reviewed once (Priority: P1)

**Acceptance Scenarios**:

1. **Given** a question to trial, **When** `make trial SLUG=<slug>` runs, **Then** it claims a feature number and writes a
   trial brief (`spec.md` with `**Form**: trial`) - the question, the GM's words, the measurement, the rule that decides it,
   the evidence, the time - and `request.md` to fill.
2. **Given** a trial brief with no fidelity verdict, **Then** its pushes go through while the trial runs, so its evidence is
   committed and pushed as it is measured; **Given** the trial closed (its status `Done`), **Then** the push needs its one
   fidelity verdict, taken on the brief with its evidence fixed.
3. **Given** a trial's pushes, **Then** a net change to the engine (`l7r/`) is refused: a trial lands no engine code - a spike
   is measured and reverted, and a trial that wins becomes an ordinary feature whose spec cites the trial's evidence.
4. **Given** a trial done, **Then** its time is `make feature-report F=<n>`'s split (the session's work, its waits, the agents'
   time), with no hand-kept clock.

## Requirements *(mandatory)*

- **FR-001**: `make perf-share [MODULE=<path>] [STAGES=<a,b,...>] [SEED=25] [HOUSEHOLDS=40]` profiles each stage
  (`perf_profile.profile_stage`), and prints per stage its profiled total, the module's own (self) time and share, the stage's
  largest self-time functions, and the callers of the module's functions ranked by the module's time under them; it ends
  with the module's share across all the stages read. It gates nothing.
- **FR-002**: Its defaults: `MODULE` `l7r/diagram/settlement/_geom/primitives.py`; `STAGES` homesteads, web, field,
  hinterland.
- **FR-003**: `make trial SLUG=<slug>` claims a number as `make claim` does and writes the trial brief from a template
  (`.specify/templates/trial-template.md`): `**Form**: trial`, the question, the `**Approved**:` line, the measurement (the
  commands: `make perf-share`, `make perf-ab`, `make perf-fanout STAGES=`), the rule (a trial lands no engine code; it
  recommends promotion where the evidence shows time saved beyond the quick form's floor, otherwise it is set down), the
  evidence, and the time (`make feature-report`).
- **FR-004**: The review gate passes a trial brief with no verdict while its status is not `Done`; a trial whose status opens
  `Done` owes one fidelity verdict on the brief, as any spec does.
- **FR-005**: The push refuses a trial's delta that changes the engine (`l7r/`) on net - the delta's `git diff` of `l7r/`
  non-empty - naming the rule and the promotion route; `TRIAL_ENGINE_OK="<reason>"` overrides, recorded.
- **FR-006**: `docs/spec-kit-and-reviews.md` gains the trial form (when to use it - a question answered by measurement,
  before any decision to build - and its rules), the root `CLAUDE.md`'s development-workflow list one line pointing at it,
  and `docs/guards.md` the two gate rules with their escapes.
- **FR-007**: Nothing added refuses on a time (feature 435 FR-006 stands).

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002): `make perf-share` with no arguments prints feature 437's four stages' shares of
  `primitives.py` and its callers table; a test reads a synthetic profile and checks every column.
- **SC-002** (FR-003): `make trial SLUG=x` (in a test fixture) writes `spec.md` with `**Form**: trial` and the template's
  sections.
- **SC-003** (FR-004, FR-005): The review gate's tests pass a verdict-less trial not `Done`, refuse it `Done`, and refuse a
  trial delta with a net engine change (and pass it with the escape).
- **SC-004** (FR-006): The three docs name the trial form and its gate rules.
- **SC-005** (FR-007): Nothing added refuses on a time.

## Edge Cases

- A trial whose spike is committed and reverted inside one push: the net engine change is empty, so it passes.
- A stage the roll refuses before it is reached: perf-share names the refusal and goes on to the next stage.

## Assumptions

- A trial is a feature like any other (its number, `request.md`, `report.md`, `make feature-report`); only its spec's form,
  its review's timing and its no-engine rule differ.
