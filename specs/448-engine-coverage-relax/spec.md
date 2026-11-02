# Feature Specification: relax the coverage floor for the engine code the Rust port replaces

**Feature Branch**: `448-engine-coverage-relax` (no branch; work on `main` in the clone)

**Created**: 2026-11-02

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-11-02, "We can relax that for the engine code at this pooint since that's going away, so long as we maintain it for our other Python code not currently slated to be removed (tools, automated checks for hand-drawn maps, etc)." - and *"you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future"* (GM 2026-10-18)

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
- **FR-002**: Every coverage floor the gate, `make cover-changed`, `make land` and the derived hamlet floor enforce exempts the
  entries of that record and only them; their unrun lines are still reported, as information.
- **FR-003**: Everything else keeps the 100% floor unchanged - in particular `l7r/diagram/tools/`, `ci/`, `pipeline/`,
  `interactive/`, the gate's checks under `tests/gate/` and the automated checks of the hand-drawn maps, and `scripts/`.
- **FR-004**: A module is held to the floor unless the record names it (a new module defaults to the floor).
- **FR-005**: The record's entries are checked to exist; a stale entry (a path deleted by a Rust landing) fails the gate with the
  command that removes it, so the list shrinks as the port proceeds.
- **FR-006**: The docs that state the single 100% floor (`l7r/diagram/CLAUDE.md`, `settlement/CLAUDE.md`'s Coverage, the root
  `CLAUDE.md`'s Python line, `docs/efficiency-tooling.md`) say the exemption, with the GM's words.

## Success Criteria *(mandatory)*

- **SC-001**: A fixture with an unrun line in a slated module passes every coverage reader; the same line in a kept module fails
  each of them.
- **SC-002**: No module outside the record is below 100% at the landing (the floor did not loosen anywhere else).
- **SC-003**: Coverage-driven work on slated modules stops: after landing, no task of feature 444 adds a test only to cover a slated
  module's line.

## Edge Cases

- A module half slated (one stage's code inside a package that otherwise stays): the record names files, not packages, so only the
  slated files are exempt.
- A slated module also imported by kept code: its exemption covers only its own lines; the kept caller's lines stay at 100%.
- A Rust phase that is withdrawn: its Python's entries leave the record and the floor returns.

## Decisions Recorded

Tooling only: this feature draws and states nothing on any map.

## Assumptions

- "The engine code ... that's going away" is the Python that feature 444's phases replace; where the plan names a stage's Python
  as replaced, it is slated, and nothing else is.
- Lint, format and type checks are unchanged for slated modules; only the coverage floor is relaxed.
