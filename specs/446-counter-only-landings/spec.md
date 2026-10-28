# Feature Specification: lighter landings for counter-only changes

**Feature Branch**: `446-counter-only-landings` (no branch; work on `main` in the clone)

**Created**: 2026-10-28

**Status**: Draft

**Affects**: tooling

**Approved**: the GM, 2026-10-28, "Yes, those two changes seem good. So please make them. Thank you."

**Input**: `request.md` (the GM's words, verbatim, and the two changes he accepted).

## Why

A landing of engine code runs the full suite, the 48-seed landing cohort and, after the push, a fresh 48-seed block. For a change
that only adds work counters (443's), the cohorts re-roll maps the change cannot move: a counter block as FR-001 restricts it reads names and
writes `work_counts.OPS`, calling nothing but `len` and `max`, so it cannot change what a roll decides (and `make counters-inert` checks that on a real roll). The claims triage
likewise dispatches an agent per landing: of the 455 claims it triaged on 2026-10-28 (observed 2026-10-28, method: the
`make claims-triaged` lines of 443 T01, T09-T12 and T02 in this session), it sent two on, neither counter-only (a mixin added to
`FieldsMixin`; `FabricIndex.fouled` binding its candidates to a name).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A counter-only landing rolls no cohort (Priority: P1)

1. **Given** a landing whose engine delta is counter-only (FR-001: with every counter block removed from both sides, every engine
   file's semantic id unchanged), **When** `make land` runs, **Then** it runs the full suite and skips `make cohort-landing` and the fresh
   block, printing why; **Given** any other engine delta, **Then** both run as today.

### User Story 2 - A counter-only claim is cleared without an agent (Priority: P1)

1. **Given** a claim owed a code triage whose unit only gained counter blocks since its recorded version, **When**
   `make claims-owed` or `make claims-triage` runs, **Then** the claim is recorded cleared ("counter-only") with its new
   fingerprint and sent to no agent; **Given** any other change to the unit, **Then** it is owed as today.

## Requirements *(mandatory)*

- **FR-001**: One definition of a COUNTER BLOCK and of "counter-only", in `scripts/gates/codeid.py`. A counter block is an `if
  __debug__:` statement with no `else` whose body is nothing but augmented assignments (`+=`, `-=`) to `OPS[<string constant>]`,
  each value one of the forms FR-001 itself defines: a literal; a name; `len(<name or attribute chain on a name>)`;
  `<name>.size`; `max(len(<name or chain>) - <literal>, <literal>)`; or a product (`*`) of these. The only calls a value may make
  are `len` and `max`, and `len`'s argument is read, never computed - no call, subscript or operator inside it - so a counter
  block can do nothing but add to a counter. Any other `if __debug__:` statement, or an `if __debug__ and ...:`, is code (the
  driver's per-stage attribution, which writes `BY_STAGE`, among them: a landing touching it rolls the cohorts). `debug_free_bytes(data, name)` is a `.py` file's
  semantic bytes (as `semantic_bytes`) with every counter block removed; two versions of a `.py` file are counter-only-equal when
  these are equal; a non-`.py` file compares its bytes; an added or deleted file is never counter-only-equal.
- **FR-002**: A delta is counter-only when every engine path it changes (`land.py`'s `ENGINE`) is counter-only-equal to its base,
  the merge base with origin/main. `make land` then skips `make cohort-landing` and the fresh block, and says so. The cohort's
  same-engine test (`cohort_known.same_key`, read by `cohort_gate`'s `pick`, `needs_baseline` and `baselines`) treats two commits
  whose engine differs only so as the same engine, so the record before a counter-only landing stays main's baseline and the
  next landing's cohort is not pushed onto it. `l7r.diagram.ci.delta.engine_key`, which keys the gate's own selection, is
  untouched. Any other engine delta runs both cohorts as today.
- **FR-003**: The claims triage (the code-triage owing, `claims_owed` and `claims_triage`) records a claim cleared, with its new code
  fingerprint and the note "counter-only (feature 446)", and sends it to no bundle, when: its unit's source at the merge base with
  origin/main fingerprints to the claim's recorded `code` (so the recorded version is the base's), and the current unit is that
  version with counter blocks only added - every counter block of the base version standing unchanged. A claim whose recorded
  version is not the base's, or whose counter blocks were removed or rewritten, is owed as today.
- **FR-004**: Unchanged: the full suite on every engine landing, the claims switch's refusal of an owed claim, `make counters-inert`
  in `make done`, every review and checklist.
- **FR-005**: Each skip has a test that a non-counter change still runs it, proven to fire with the skip's condition deleted; the
  guards table and `make land`'s help name the skip.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001): tests find two versions differing only by a counter block equal; versions differing by any other statement,
  by an `if __debug__:` with an `else`, by an `if __debug__:` whose body does anything but count, by a counter whose value calls
  anything but `len` or `max` or computes `len`'s argument (`len(f(x))`), or by an added or deleted file, unequal.
- **SC-002** (FR-002, FR-004): a test of `land.py` skips the cohorts on a counter-only delta and runs them on another, and runs the
  full suite on both; a test of `cohort_known.same_key` finds a commit and its counter-only successor the same engine.
- **SC-003** (FR-003): a test records a claim whose unit only gained a counter block cleared without a bundle, and owes one whose
  code changed otherwise, one whose counter block was removed, and one whose recorded version is not the base's.
- **SC-004** (FR-005): each skip's test goes red with its condition deleted; the docs name it.

## Edge Cases

- An `if __debug__:` block with an `else` branch: not counter-only (the `else` runs under `-O`), so it counts as a change.
- A new or a deleted engine file: not counter-only.
- `if __debug__ and held is not None:` (`overlap/registry.py`): not a counter block - a landing that touches it counts as a change,
  the safe direction; do not widen the definition to catch it.

## Review history

- 2026-10-28, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED, 7 items - a counter block defined by its form (FR-001); the
  recorded side of the claims comparison named, and only added counter blocks cleared (FR-003); the cohort's same-engine test made
  counter-blind so the skip does not push the roll onto the next landing (FR-002); deleted and non-`.py` files defined; SC-002 names
  FR-004; the Why's triage figure measured and its two flagged claims shown not counter-only.
- 2026-10-28, round 2 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 1 item - six of round 1 resolved; FR-001 now restricts a
  counter's value to the forms it lists, `len`'s argument read and never computed, the only calls `len` and `max`; the Why rests on
  that restriction; SC-001 adds `len(f(x))`.
- 2026-10-28, the round cap: the round arbiter ACCEPT (ask:446-spec-round-3), standing as the spec's verdict; round 3 waived.
