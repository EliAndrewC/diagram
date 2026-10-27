# Feature Specification: perf-ab quick first

**Feature Branch**: `436-perf-ab-quick-first` (no branch; work on `main` in the clone)

**Created**: 2026-10-27

**Status**: Draft

**Affects**: tooling, performance

**Approved**: the GM, 2026-10-27, "That sounds good. Please implement that. Thank you."

**Input**: `request.md` (the GM's words, verbatim, and the proposal he approved).

## Why

`make perf-ab` (feature 435) always runs the whole snapshot - the reference hamlet on four seeds and the 10-, 20- and
40-household legs, 15 rolls a run, three runs a version - so one comparison took 8.2 minutes each time it ran on
2026-10-27 (measured 2026-10-27, the file times of feature 435's T04 and T08 A/B logs). Most of that time goes to sizes and
seeds a change is not aimed at, which makes iterating on a performance change expensive. An A/A run of one engine against
itself swung -9% to +8% (specs/435-speed-aims-at-time/report-numbers.md), and the arms always ran A first.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A quick comparison to iterate on (Priority: P1)

A session changing the 40-household roll compares its engine against the parent on one seed at one size, six runs a
version, in a couple of minutes, and iterates on that.

**Acceptance Scenarios**:

1. **Given** two commits, **When** `make perf-ab A=<commit>` runs with nothing else set, **Then** it times seed 25 at 40
   households, 6 runs a version, and prints each version's best wall time and spread, best CPU time and spread, and calls.
2. **Given** `SEEDS=` and `HOUSEHOLDS=` naming one seed and one size, **Then** the quick form times that seed at that size
   instead.

### User Story 2 - Quick first, enforced (Priority: P1)

A larger comparison - a chosen subset of seeds and sizes, or the full sweep - is refused unless a quick comparison of the same
two engines is on record, the way `make done` will not run before `make quick` has.

**Acceptance Scenarios**:

1. **Given** no quick comparison of these two engines on record, **When** `make perf-ab A=... SEEDS=25,39 HOUSEHOLDS=20,40`
   or `make perf-ab A=... FULL=1` runs, **Then** it refuses before any roll and prints the quick command that would satisfy
   it.
2. **Given** a quick comparison of the same two engines on record (the engines judged by their code, so a commit that
   changes only docs or comments, or a rebuilt commit of the same code, still matches), **Then** the larger comparison runs.
3. **Given** a stated reason (`PERF_AB_QUICK_OK="<reason>"`, two words or more), **Then** it runs and the reason is
   recorded.
4. The refusal is for a skipped step, never on a timing: nothing in this feature refuses because of a time.

### User Story 3 - A fairer comparison (Priority: P2)

**Acceptance Scenarios**:

1. **Given** any form, **Then** the versions alternate A then B, then B then A, so neither always runs first.
2. **Given** a quick comparison, **Then** the noise floor of that quick form - an A/A run of one engine against itself at
   that seed, size and run count - is printed beside the result, with when it was taken; where none is on record the line
   says how to take it (`make perf-ab AA=1`), and a floor once taken is reused.

## Requirements *(mandatory)*

- **FR-001**: The form is decided by what is compared, never by which variable is spelled how: `SEEDS=` and `HOUSEHOLDS=`
  are lists (defaults `25` and `40`); exactly one seed at exactly one size is the QUICK form (`N` default 6); more than one
  seed or more than one size is the SUBSET form (`N` default 3); `FULL=1` is the FULL form, the present sweep (`make perf
  SCALING=1`'s legs, `N` default 3). `make perf-ab A=<commit> [B=<commit>]` with nothing else set is the quick form, seed 25
  at 40 households.
- **FR-002**: The subset form times every seed listed at every size listed.
- **FR-003**: Every form alternates the order A B, B A, A B, ...; prints, per seed and size, each version's best wall time
  and spread, best CPU time and spread, and calls, and the change between versions in each; and exits 0 whatever the times.
- **FR-004**: A quick comparison is recorded (local to the clone, never pushed) under both engines' code keys, the keys
  ignoring docstrings and comments as the project's other engine keys do.
- **FR-005**: Every run that is not the quick form refuses, before any roll, unless that record holds a quick comparison of
  the same two engine keys; the refusal names the quick command; `PERF_AB_QUICK_OK="<reason>"` overrides it, the reason recorded where
  the project's escapes are recorded.
- **FR-006**: `make perf-ab AA=1 [SEEDS=<one seed>] [HOUSEHOLDS=<one size>] [N=]` takes the noise floor of a quick form: one engine (default
  HEAD) against itself, recorded per seed, size and run count; a quick comparison prints the latest floor of its form beside
  its result.
- **FR-007**: No requirement, test or exit of this feature refuses on a time (feature 435 FR-006 stands).
- **FR-008**: `docs/performance-checklist.md` (question 5, and its tools table) says: the quick form while iterating, then a
  subset or the full sweep once before landing; `docs/guards.md` lists the new refusal and its escape.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): The quick form's wall time is a few minutes or less at 40 households (measured, not gated).
- **SC-002** (FR-005): A subset or full comparison with no quick record refuses before rolling; with one, or with the stated
  reason, it runs.
- **SC-003** (FR-003, FR-006): The output shows wall and CPU time with spreads, the alternating order, and the floor line.
- **SC-004** (FR-007): No test or exit added refuses on a time.

## Edge Cases

- A seed the generator refuses at a size prints "refused" for both versions, as today.
- An older commit as A: the quick and subset forms roll through code the older commit already has (the reference hamlet's
  roll and the per-stage timing), so any engine since feature 435 can be compared.

## Review history

- 2026-10-27, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED - nothing decided which form a run is, so `HOUSEHOLDS=20,40`
  read as quick and skipped the refusal; the form is now decided by the count of seeds and sizes compared (FR-001, FR-005).
- 2026-10-27, round 2 (spec-fidelity-verify): FAITHFUL.

## Assumptions

- The default seed is 25, the seed the 435 profiles used; seed 4 is refused at 40 households.
