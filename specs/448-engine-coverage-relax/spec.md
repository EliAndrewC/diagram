# Feature Specification: relax the coverage floor for the engine code the Rust port replaces

**Feature Branch**: `448-engine-coverage-relax` (no branch; work on `main` in the clone)

**Created**: 2026-11-02

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-11-02, "We can relax that for the engine code at this pooint since that's going away, so long as we maintain it for our other Python code not currently slated to be removed (tools, automated checks for hand-drawn maps, etc)."

**Input**: `request.md` (the GM's words, verbatim).

## Why

Every gate holds every Python module to 100% line coverage, the engine included. Feature 444 is replacing the engine's stages with
Rust one phase at a time, and each Python stage it replaces is deleted at its landing. Until then, any change near that code - a
deletion, a seam, a review fix - has to keep every line of it covered, and keeping a doomed module at 100% costs session time
the GM no longer wants spent. The code that STAYS - the tools, the gate's checks (including the automated checks for the
hand-drawn maps), the pipeline, the interactive page, ci and scripts - keeps the floor.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - a change to engine code slated for the Rust port is not held to 100% (Priority: P1)

A session changes or deletes Python in a package the Rust port replaces and leaves some of its lines unrun. The gate reports
those lines but does not fail on them.

**Independent Test**: In a fixture, leave one line of a slated engine module unrun; the coverage step passes and names the line.

**Acceptance Scenarios**:

1. **Given** a module on the slated list under 100%, **When** the gate runs, **Then** it passes and lists the module's unrun lines
   as information.
2. **Given** the same, **When** `make cover-changed` runs, **Then** it does not refuse.

### User Story 2 - the code that stays keeps the floor (Priority: P1)

**Independent Test**: In a fixture, leave one line of a tool, a gate check, the pipeline or a script unrun; the gate fails as today.

**Acceptance Scenarios**:

1. **Given** a module NOT on the slated list under 100%, **When** the gate runs, **Then** it fails, naming the module and lines, as
   today.
2. **Given** a module new to the tree, **When** nothing names it slated, **Then** it is held to the floor (the list is opt-out, not
   opt-in for the floor).

### User Story 3 - the slated list is one record, read by every coverage check (Priority: P2)

The list of what is slated is kept once, with why each entry is on it, and every coverage reader (the gate, `make cover-changed`,
the derived hamlet floor, `make land`'s cover step) reads that one record.

**Independent Test**: Removing an entry from the record makes every coverage reader hold that module to 100% again.

## Requirements *(mandatory)*

- **FR-001**: One record names the Python engine code slated for removal by the Rust port, each entry with its reason (the 444
  phase that replaces it, or the program's whole-engine replacement).
- **FR-002**: Every coverage floor - the gate's floored report, the derived hamlet floor, `make cover-changed` (which `make land`
  runs) and `make preflight`'s coverage step, the readers that a search of the tree before this feature finds (`git grep -l -E
  "fail-under|fail_under|missing_lines|CoverageData|analysis2|Coverage\(" 69982e1ee -- scripts l7r Makefile`, each hit read for a
  refusal on unrun lines; the hits that only gather coverage data or measure the Rust crate's - `pipeline/gencache.py`,
  `ci/incremental.py`, `scripts/gates/rust_checks.py`, `scripts/measure/uncovered-in-diff.py` - refuse nothing of the Python's;
  and, outside the search, `tools/cache_audit.py` runs coverage only to pick mutation sites) - exempts the entries of that record and only them; their unrun lines are still reported, as information.
- **FR-003**: Everything else keeps the 100% floor unchanged - in particular `l7r/diagram/tools/`, `ci/`, `pipeline/`,
  `interactive/`, the gate's checks under `tests/gate/` and the automated checks of the hand-drawn maps, and `scripts/`.
- **FR-004**: A module is held to the floor unless the record names it (a new module defaults to the floor).
- **FR-005**: An entry is stale when its path is gone, when every 444 phase it names is accepted (its Rust landed; what is left is
  the stage's thin door, which stays Python), or, for a whole-engine entry, when code that stays Python now reaches it by import; a
  stale entry is no longer exempt and fails the gate and `make land` with the command that removes it, so the list shrinks as the
  port proceeds.
- **FR-006**: Every operative doc that states the single 100% floor says the exemption, with the GM's words - those a search finds
  (`git grep -n -E "100% (coverage|line|over)|100%.*floor|fail-under=100"` over the docs, templates and engine docstrings, less the
  specs, the research record and the run logs): `l7r/diagram/CLAUDE.md`, `settlement/CLAUDE.md`'s Coverage, `tools/CLAUDE.md`'s
  hamlet-floor row, `tests/CLAUDE.md`'s tree table, `tests/soak/CLAUDE.md`'s gate row and membership rule, the root `CLAUDE.md`'s Python line, `docs/efficiency-tooling.md`,
  `docs/guards.md`'s coverage row, `docs/migration-plan.md`, `ci/incremental.py`'s docstring, `pyproject.toml`'s coverage note,
  `.specify/templates/plan-template.md`'s Principle X gate, and the constitution's Principle X clause 5 as a dated amendment; the tests that pin "no `--omit` on the floored report"
  pin instead that its only omission is the record's.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-002, FR-004, FR-005): A fixture with an unrun line in a slated module passes every coverage reader; the same line in a kept module fails
  each of them.
- **SC-002** (FR-003): Every module outside the record is fully covered at the landing (the floor did not loosen anywhere else).
- **SC-003** (FR-002, FR-006): After landing, no coverage reader FR-002 names refuses a slated module's unrun line, and each prints
  that line as information; the docs FR-006 names each carry the exemption and the GM's words.

## Edge Cases

- A module half slated (one stage's code inside a package that otherwise stays): the record names files, not packages, so only the
  slated files are exempt.
- A stage's slated module also imported by kept code: its exemption covers only its own lines; the kept caller's lines stay at
  100%. A whole-engine entry that kept code starts to import is stale (FR-005) and its floor returns.
- A Rust phase that is withdrawn: its Python's entries leave the record and the floor returns.

## Review history

- 2026-11-02, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED, 5 items - FR-002 adds preflight's coverage step and its search;
  FR-006 states its search and adds the docs it finds; FR-005 defines stale as the plan's D4 does; the Assumption names both
  classes; SC-003 restated as an observable outcome.
- 2026-11-02, round 2 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 3 items - FR-002's search widened so it finds the hamlet
  floor, the non-refusing hits named; FR-006 adds `tests/soak/CLAUDE.md`; the edge case on kept importers split by class.
- 2026-11-02, round 3 (spec-fidelity-verify, MODE 3): FAITHFUL - round 2's three items resolved; its note applied (`cache_audit.py`
  moved outside FR-002's search hits, where it is not one).

## Decisions Recorded

Tooling only: this feature draws and states nothing on any map.

## Assumptions

- "The engine code ... that's going away" is, in two classes: a 444 stage's own Python while its phase is not accepted, and the
  engine modules unreached from what 444 FR-010 and FR-003 keep in Python once those stages' Python is gone (the program's
  whole-engine replacement). Nothing else is slated.
- Lint, format and type checks are unchanged for slated modules; only the coverage floor is relaxed.
