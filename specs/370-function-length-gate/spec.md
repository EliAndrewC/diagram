# Feature Specification: a mechanical cap on function length, held at the gate

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-08 (filed); specified 2026-10-10

**Status**: Draft

**Affects**: tooling

**Input**: `request.md` (the GM, verbatim). Closing feature 111 the GM said the project had *"replaced 'decompose for
readability' with a mechanical cap on function length and file length"*; only the file cap existed. On 2026-10-10, after a
survey of what projects set (research.md R1): *"Please go with 100. And we can document why 100 is the number that we went
with, like that it is the second most common value on GitHub from our initial survey."* And on where it lives: *"I do like
the idea of just doing that in our linter"*.

## Summary

The constitution (Principle X clause 12) caps a function's size in logic units but nothing enforces it; its Sync Impact
Report carries the gate check as a deferred TODO. This feature makes the cap real: the linter the gate already runs counts
every function's statements and fails one over **100**, the number the GM chose from the survey (research.md R1: the second
most common value on GitHub, and the most common one a project chose over the default 50). The ten engine functions and two
script functions over it today (research.md R2) are split, or - where a body must stay one - carry an inline justification
the gate reads. Splitting changes no map.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A function past the cap fails the gate (Priority: P1)

A session writes or grows a function past 100 statements; `make lint` (and so `make done` and the push) fails and names
the function, its count and the cap, with the two ways out: split it, or justify it inline.

**Why this priority**: it is the whole of the GM's ruling - a cap that is held, not a sentence in the constitution.

**Independent Test**: a fixture function of 101 statements fails the lint step; one of 100 passes.

**Acceptance Scenarios**:

1. **Given** a function with 101 statements in the engine, tests or scripts, **When** the lint step runs, **Then** it
   fails naming the file, the line, the count and the cap of 100.
2. **Given** the same function carrying the justification marker with a reason, **When** the lint step runs, **Then** it
   passes.
3. **Given** the marker with no reason, **When** the gate runs, **Then** it fails and says a reason is owed.

### User Story 2 - Today's code is under the cap (Priority: P1)

Every function now over 100 statements (research.md R2: ten in the engine, two in `scripts/`) is split into named parts, or
kept whole with a justification, so the gate is green the day the cap lands.

**Why this priority**: a cap switched on over a red tree is either bypassed or blocks every session.

**Independent Test**: the lint step reports no function over 100 on the landing commit; every map in the pool is
byte-identical to HEAD's after a reroll.

**Acceptance Scenarios**:

1. **Given** the landing commit, **When** the cap's check runs over the whole project, **Then** it reports nothing.
2. **Given** the pool rerolled on the landing commit, **When** its manifests are compared with HEAD's, **Then** none moved.

### User Story 3 - Why 100 is written where the cap is (Priority: P2)

A later reader who wonders why 100 and not the default 50 finds the answer beside the setting and in the constitution: the
survey, its date and its numbers.

**Independent Test**: the setting's comment and clause 12 both name the survey and research.md R1.

### Edge Cases

- A function under 100 statements but long in raw lines (wrapped strings, a long literal): passes - the measure is
  statements, never lines (clause 12).
- A nested function: counted as its own function, and its statements are not counted again in its parent (ruff's count).
- The frozen and excluded trees (`pool/`, `legacy-hand-authored-pool/`, `specs/`, `tests/hooks/`): not held - they are
  outside the lint fence for their own reasons (pyproject's `extend-exclude`), and a frozen exhibit is never edited.
- `scripts/` is outside the lint fence too (feature 329 kept it there), but it is the project's own working code, so the
  cap - this rule alone - is held over it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The lint step the gate already runs MUST fail any function over 100 statements, counted by the linter's
  statement rule (ruff `PLR0915`, `max-statements = 100`), over every tree it lints (research.md R3).
- **FR-002**: The same rule, alone, MUST be held over `scripts/`, which the lint fence otherwise excludes.
- **FR-003**: Every function over the cap at the start of the work (research.md R2) MUST be split into named parts or
  carry the justification marker; splitting MUST NOT change any map (the pool's manifests identical to HEAD's).
- **FR-004**: The justification is the linter's own inline suppression for that rule followed by a reason in words;
  a suppression with no reason MUST fail the gate, with a message that names the line and says a reason is owed.
- **FR-005**: The setting MUST carry, beside it, why 100: the survey's date, its sample and its finding (research.md R1).
- **FR-006**: Constitution Principle X clause 12 MUST be amended to name the measure (the statement count), the cap (100),
  the escape (the reasoned suppression) and the survey, and its Sync Impact Report's deferred TODO MUST be closed.
- **FR-007**: Every unit split under FR-003 MUST keep its research claims, and every new part MUST carry the claims its
  code holds (the claims coverage the gate already enforces).
- **FR-008**: The failure message MUST name the two ways out (split, or the reasoned suppression).

### Key Entities

- **The cap**: 100 statements per function, ruff's count.
- **The justification**: an inline suppression of the statement rule with a reason, read by the gate.

## Success Criteria *(mandatory)*

- **SC-001**: A fixture function of 101 statements fails the lint step and one of 100 passes (FR-001, FR-002, FR-008;
  research.md R3).
- **SC-002**: On the landing commit the cap's check over the whole project reports zero functions over 100 (FR-001,
  FR-002, FR-003).
- **SC-003**: The pool rerolled on the landing commit leaves every manifest identical to HEAD's (FR-003).
- **SC-004**: A suppression with no reason fails the gate; one with a reason passes (FR-004).
- **SC-005**: The setting's comment and clause 12 both cite research.md R1 (FR-005, FR-006).
- **SC-006**: The claims gate passes at the push with every split unit's claims carried and checked (FR-007).

## Assumptions

- Ruff's statement count is the measure (research.md R3); the constitution's "logic units" wording is amended to say so.
- The splits are behavior-preserving refactors; a map that moves is a defect in the split, not an accepted change.
- No review check (`glyph-check`, `settlement-review`, ...) is owed: no map changes (`## Occasions`: none).
- The claims gate will owe `impl-drift` on the split units (their code fingerprints change); that is this feature's
  expected review cost, run once over all of them.

## Out of Scope

- Bringing `scripts/` under the rest of the lint rules (the fence stays as feature 329 left it).
- A cyclomatic-complexity cap or any other size measure.
- Lowering the cap later; the survey's numbers stay in research.md for whoever reconsiders it.

## Decisions Recorded

- **D1 - 100 statements** (the GM, 2026-10-10, from research.md R1). Class: deliberate choice on measured evidence.
- **D2 - ruff's count, in the linter** (the GM: *"I do like the idea of just doing that in our linter"*). Class: tooling
  convention.
- **D3 - `scripts/` held by this rule alone** (FR-002): the GM asked for a cap on function length, and `scripts/` is the
  project's own code; the rest of its lint stays out of scope. Class: scope decision.
