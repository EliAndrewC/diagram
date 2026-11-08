# Feature Specification: A Rust codebase

**Feature Branch**: none - this project stays on `main` (`SPECIFY_FEATURE=449-rust-codebase`)

**Created**: 2026-11-07

**Status**: Draft

**Approved**: the GM, 2026-11-07, "I think what we're finding is that our Python code is just to inefficient and should probably all be ported to Rust, so I think I want to just move forward with that, making this a Rust codebase instead of a Python codebase."

Filed without an approval round under the GM's standing rule: "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future" (GM 2026-10-18).

**Affects**: tooling, performance, interactive page, research record, research process, review process, magistracy, country shrine

**Input**: the GM's words, verbatim in `request.md`; the measurements of feature 444 T36 (2026-11-07) that led to them.

## Why

Feature 444 moved the hamlet engine to Rust. Everything else is still Python: the gate, the hooks that run on every tool call, the
research and review tooling, the Mode A building planner, the interactive page writer. Each figure below is recorded with its command
in `measurements.json` (feature 444 T36's runs of 2026-11-07):

- a one-line Rust code edit's `make done`, against a fresh baseline, took 30.2 s of wall time, 24 s by its own record, of which the
  preflight's 4 s and the Python test phase's 19 s - 11 test modules picked because they read a `.rs` file - were Python
  (`m:done-rust-edit`);
- this repository's 26 guards run before every Bash call, in parallel: the slowest 175 ms, 1,045 ms summed per call
  (`m:hooks-bash`); a
  `pair-hooks.sh` run averaged 441 ms inside its own suite, 90 runs and 39.7 s summed, most of it work rather than start-up
  (`m:pair-hooks-suite`);
- a Python interpreter starts in 15-16 ms with nothing to run (`m:python-start`); the Rust crate's 91 tests run in 0.11 s
  (`m:rust-tests`); every test of the gate's trees, summed, is 632 s (`m:suite-cpu`).

Limits a port does not change, recorded so the plan does not promise them: git operations and the push path, the I/O of a scan of the
whole repository, subprocess-heavy fixtures. And the day's largest wins were design fixes - a claims test 6.7 s -> 0.5 s, a
mutation test 20.7 s -> 1.1 s, a check bundle 3.3 s -> 1.55 s (`m:design-fixes`) - which a port must carry over, never repeat.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every tool call answers at once (Priority: P1)

The GM works with a session; before each tool call the project's guards run. Today that is 26 processes, each a shell that starts
Python (`m:hooks-bash`). After this story they answer as one process, with the same verdicts.

**Why this priority**: the GM asked of the hooks first - "Wouldn't the hooks being in Rust also make the hook tests run faster?" -
before deciding on the whole codebase. Their cost is paid on every tool call of every session, and its CPU competes with any gate running beside it on a laptop measured at its thermal limit (`m:done-rust-edit`).

**Independent Test**: time the guards for a Bash, an Edit and an Agent call before and after; replay every guard suite's cases
(`tests/hooks/`) against the replacement and compare each verdict.

**Acceptance Scenarios**:

1. **Given** a Bash call, **When** the guards run, **Then** they decide it in under a tenth of today's slowest guard, and in under a
   twentieth of today's summed CPU (`m:hooks-bash`).
2. **Given** each case a guard suite holds today, **When** it runs against the replacement, **Then** the verdict - allowed, refused,
   rewritten, its message - is the one the Python guard gives.
3. **Given** a guard suite, **When** it runs, **Then** it takes under a tenth of its measured time today where the guard's own run
   was its cost (`m:pair-hooks-suite`).

---

### User Story 2 - The gate is Rust (Priority: P2)

`make done`, `make quick`, `make land` and the push's checks are driven by Rust: the test planner, the stamps and verification state,
the run records, the claims and coverage reports. A one-line Rust edit's gate runs only what that edit can change.

**Why this priority**: the gate is the loop the GM waits on; its Python path is most of the time measured above (`m:done-rust-edit`).

**Independent Test**: a one-line Rust edit, a one-line edit of a ported tool, a comment-only edit and no edit, each timed through
`make done` before and after, every verdict compared.

**Acceptance Scenarios**:

1. **Given** a one-line change to Rust code, **When** `make done` runs, **Then** it finishes in under half today's wall time, its Python steps gone (`m:done-rust-edit`).
2. **Given** a comment-only change, or none, **When** `make done` runs, **Then** it reuses the last green result and runs no test.
3. **Given** a defect a check catches today, **When** the gate runs on the Rust path, **Then** it is caught, by the same rule.

---

### User Story 3 - The tooling is Rust (Priority: P3)

The research-record, review, measurement and page-session tooling under `scripts/` runs as Rust, each command through make as today.

**Why this priority**: the largest body of Python; slow where it parses, walks and starts processes.

**Independent Test**: each command's output on the real repository compared before and after; its tests run as Rust tests.

**Acceptance Scenarios**:

1. **Given** any make target that runs a tool, **When** it runs, **Then** its output and exit status are those of the Python tool.
2. **Given** a tool's tests, **When** they run, **Then** none takes a tenth of a second or more unless it is that tool's one end-to-end test.

---

### User Story 4 - Mode A and the page writer are Rust (Priority: P4)

The Mode A building planner (compound plans, captions, buildings), the caption placer, the interactive page writer and the map
pipeline are Rust. With them gone, no Python remains in the repository.

**Why this priority**: last, as the least often run on the iteration loop.

**Independent Test**: every Mode A sheet and every interactive page regenerated before and after and checked by the same checks;
`make done` with no Python interpreter on the path.

**Acceptance Scenarios**:

1. **Given** a Mode A sheet, **When** it is regenerated, **Then** every check that passed on it passes.
2. **Given** the repository after this story, **When** it is searched, **Then** it holds no Python file outside git history.

### Edge Cases

- A piece half ported: its Python stays the one that runs until its replacement passes every case; the two never both decide.
- A Python test that tests a tool's real behavior over the whole repository: kept as that tool's one end-to-end test, ported.
- A guard that refuses on correct work today: fixed in the port, its suite case recording the fix (constitution XIV).
- A behavior only the Python tests' coverage revealed: the Rust replacement carries a test for it before the Python is deleted.
- A design fault found while porting (work repeated, a scan run twice): fixed in the port, not carried over.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every Python file the repository tracks MUST be replaced by Rust, in four phases in this order: the hooks (Story 1),
  the gate (Story 2), the tooling (Story 3), Mode A and the page writer (Story 4). THE CENSUS is `git ls-files '*.py'` (872 files on
  2026-11-07, `m:python-census`), and every file it returns is in a phase: `scripts/hooks/` and the libraries its guards call -
  phase 1; `l7r/diagram/ci/`, the gate's scripts under `scripts/gates/` and `scripts/measure/`, `l7r/diagram/_invocation.py` (the
  make-only refusal) and `l7r/diagram/switches.py` - phase 2; the rest of `scripts/`, `l7r/diagram/tools/`, `l7r/diagram/pipeline/`,
  `l7r/diagram/_census.py`, `l7r/diagram/_memory.py`, `l7r/diagram/work_counts.py` and every file under `specs/` (a past feature's
  harness, measurement or prototype, ported like any other: `make figures` re-runs the measurements) - phase 3; `l7r/diagram/` Mode A
  (`compound*`, `labels/`, `buildings/`, `dwellings.py`, `well_gear.py`), `l7r/diagram/interactive/`, the Mode A sheets' generators
  under `pool/` (6, the magistracies and the country shrine) and `l7r/diagram/__init__.py` last - phase 4; each `tests/` file with the
  piece it tests. A SECOND CENSUS counts the Python run inline in the Makefile and the shell scripts - `git grep -nE "python3
  (-c|-[[:space:]]|-$|<<)" -- Makefile '*.mk' '*.sh'` (300 sites in 93 files on 2026-11-07, `m:inline-python-census`) - and every site
  it returns is in a phase: `scripts/hooks/` and `tests/hooks/` - phase 1; the Makefile's gate recipes, `scripts/gates/*.sh`,
  `scripts/sync-with-main.sh`, `scripts/land-tooling.sh` and `buildspec/run.sh` - phase 2; the Makefile's other recipes,
  `.specify/scripts/bash/` and the shell scripts under `specs/` - phase 3; `scripts/container/setup-dev-env.sh` and `Dockerfile.ci`, their Python checks and the Python
  they install, with every `requirements*.txt` and its `.in` source (four pairs on 2026-11-07, `m:lockfiles`: the runtime, dev, CI and semantic
  lockfiles) and
  `pyproject.toml`'s Python tables - phase 4,
  once nothing runs Python. Both censuses are run again at each phase's end and at the feature's close. EVERY RECORDED MEASUREMENT THAT RUNS PYTHON - a `command` in a
  `specs/*/measurements*.json` that runs a `.py` file, runs `python3 -c` or `-m`, or describes a run under `python3` in prose (4,473 on
  2026-11-07: 4,465 run a `.py`, 8 inline or prose, `m:recorded-python-commands`) - is rewritten in the commit that ports what it runs:
  to the port, where it names a ported file; to an equivalent command through make, where it is inline or prose. The rewritten entry
  is re-run as the proof: a figure is re-run, never read.
- **FR-002**: Each replaced piece MUST give the same verdicts and outputs as the Python it replaces, on every case its tests and its
  suites hold, before that Python is deleted; maps MAY change where a check or a research claim allows it (the GM, 2026-10-18). The
  one other exception: a guard or check that refuses correct work today is fixed in its port (constitution XIV), its case's expected
  verdict changed in the same commit, the change named in the commit and in the phase's record.
- **FR-003**: Until a piece's replacement passes, its Python MUST remain the one that runs; no piece runs both.
- **FR-004**: Every replacement MUST hold the coverage floor the Rust crate holds today: every line and every function reached by a
  test, read strictly.
- **FR-005**: make MUST remain the one entry point; the make-only guard MUST cover the replacements' binaries as it covers the
  Python and cargo today.
- **FR-006**: The design fixes measured in feature 444 T36 MUST be carried over, not rebuilt as they were: the import graph kept per
  process, semantic file ids read from the kept cache, a fixture built once.
- **FR-007**: The guards MUST run as one process for a tool call, not one per guard.
- **FR-008**: A tool's tests MUST each take under a tenth of a second, but its one end-to-end test against the real command.
- **FR-009**: The JavaScript and CSS of the interactive page and the research record's HTML fragments are not Python and are out of
  this feature's scope; the two containers - the dev container's `scripts/container/setup-dev-env.sh` and the CI image's
  `Dockerfile.ci` - are in it only for the Python they run and install (FR-001, phase 4). The guards' shell wrappers (`scripts/hooks/*-hooks.sh`) are
  in it: Story 1 replaces them. The GM's own hooks in `~/.claude/` are not this repository's and are out of it.
- **FR-010**: Each phase MUST end with its timings measured against this spec's figures and recorded in `dev/`.

### Key Entities

- **A piece**: one hook, one tool or one engine package, with its tests and the make targets that run it; the unit replaced.
- **A verdict replay**: a piece's recorded cases (inputs, expected verdicts and outputs) run against the Python and the Rust.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The guards before a Bash call decide it in under a tenth of today's slowest guard's time (`m:hooks-bash`).
- **SC-002**: A one-line Rust edit's `make done` finishes in under half today's wall time (`m:done-rust-edit`); an unchanged tree's
  runs no test.
- **SC-003**: The test suites, every tree together, run in under a tenth of today's summed time (`m:suite-cpu`).
- **SC-004**: Every guard suite case and every tool's recorded output gives the same verdict after its piece is ported.
- **SC-005**: When the feature closes, both censuses (FR-001) return nothing, `m:recorded-python-commands`' command returns none, and
  `make done` and `make figures` run with no Python interpreter. Its one entry here, this feature's own `m:python-start` (the before
  figure of the interpreter the close removes), is retired in the closing commit - git history keeps it - the only exemption.

## Decisions Recorded *(mandatory for any feature that changes what a map draws or states)*

None: this feature changes how the tooling runs, and no map draws or states anything new; a Mode A sheet or page that changes under
the port is held to its checks and its research claims, as FR-002 states.

## Assumptions

- The interactive page's JavaScript and CSS and the research record's HTML fragments stay as they are: they are not Python.
- Mode A's building planner is in this feature, its last phase, since the GM asked for the whole codebase.
- Each piece's Python tests are rewritten as Rust tests when the piece is ported; during a phase, a Python test may drive a Rust binary
  black-box only until that piece's Rust tests replace it.
- The research archive, the record's build (`make record`) and the claims switch keep their rules; only their implementation moves.
- The work-budget program (feature 444) and its Rust stages continue unchanged; the stages past the cut are ported there, not here.
- The 100% coverage floor's exemption for engine code the Rust port replaces (feature 448) ends piece by piece as each is ported.
