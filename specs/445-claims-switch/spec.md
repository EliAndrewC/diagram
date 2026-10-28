# Feature Specification: the claims switch

**Feature Branch**: `445-claims-switch` (no branch; work on `main` in the clone)

**Created**: 2026-10-28

**Status**: Draft

**Affects**: tooling, review process

**Approved**: the GM, 2026-10-28, "So maybe the answer is actually just building the check that we want, but then disabling it?"

**Input**: `request.md` (the GM's words, verbatim, and the recommendation he accepted).

## Why

Until the open claims are closed out, the GM wants claims "basically ignore[d] so long as they are properly marked and show up in
the claims report"; in the long run he wants "claims issues fixed within the task where they are noticed, so that every time a
feature lands, there are no open clams". Today's claims gate does neither: it refuses a finding a change introduces, and files a
finding on unchanged code as a task holding the landing's feature open (385 FR-013, its 2026-10-26 amendment routing them to 405).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Claims recorded, not refused, for now (Priority: P1)

1. **Given** the switch at `report`, **When** a landing carries a claims finding - introduced on code it touched, or found on
   code it left unchanged - **Then** the landing goes ahead and files no task; the finding stays a row of the claims index that
   `make claims-report` lists, and the landing prints it as a warning.
2. **Given** the switch at `report`, **When** a claim is owed a check, **Then** the push refuses as today (and `make land` waits
   for a check in flight, as today), so every finding is checked and recorded ("properly marked").

### User Story 2 - The long-run check, built and switched off (Priority: P1)

1. **Given** the switch at `clean`, **When** a landing runs while `make claims-report` lists any open finding, **Then** it
   refuses, naming the findings and the command that bundles them, so a finding is fixed in the task that notices it.

### User Story 3 - The switch thrown on record (Priority: P2)

1. **Given** `make claims-report-only REASON=` or `make claims-clean REASON=`, **Then** `dev/switches.json`'s `claims` entry
   changes with the reason, who and when, and the change is committed, as the remote switch is.

## Requirements *(mandatory)*

- **FR-001**: `dev/switches.json` holds a `claims` switch, `report` or `clean`, written only by `make claims-report-only` and
  `make claims-clean`, each demanding a reason and committing (feature 132's rules: one tracked file, no override, a malformed
  file failing closed - to `clean`). Absent, it reads `report`.
- **FR-002**: At `report`, the claims gate (`scripts/record/claims_carry.gate`) refuses an owed claim, as today, and a
  claims-grammar form problem (`claims.py gate`'s `delta_form_problems`); introduced, carried and known findings are warnings.
  `make land`'s claims route and wait (`land.py` `claims_route`, `claims_cure`, feature 440) are unchanged, and so meet only an
  owed claim or a form problem. The gate's other consumers, found by `grep -rn "gate(\|claims_cure\|claims_route\|record_known\|file_known\|file_carries"
  scripts/ l7r/` (2026-10-28): `land.py` `file_carries` files no carried finding as a task, and `make claims-carry` says the
  switch is at `report`; `claims_carry.record_known` (run by `land.py` `file_known` and `make claims-known`) writes no known-drift
  row to `gm-review.jsonl` - a known drift is a row of the claims report like any finding, and the GM's "basically ignore claims"
  asks no row for his review. At `clean` both behave as today.
- **FR-003**: At `clean`, the gate refuses as at `report` and also refuses every open finding `make claims-report` lists
  (drifted, needs research, mislabeled, unclaimed, undecided, cannot-tell; DEFERRED findings and UNRESEARCHED claims excepted),
  naming each and `make claims-bundle`.
- **FR-004**: The switch ships at `report` (the GM: "building the check that we want, but then disabling it").
- **FR-005**: Feature 405 closes: its status line opens `Withdrawn` with the evidence (the GM's 2026-10-28 ruling; its claims
  work deferred to a claims feature after the rewrite); its open engine fixes (T98, T101, T104, T106, T111) and drawing-page notes
  (T165) are recorded in `specs/444-work-budget-program/phase-inputs.md`, each under the stage whose rebuild settles it.
- **FR-006**: `docs/guards.md`, the claims gate's message and the root `CLAUDE.md`'s claims line name the switch and its current
  state; every refusal added has its test, proven to fire with it deleted.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-004): `dev/switches.json` reads `claims: report`; a test throws it both ways through the targets and
  reads a malformed file as `clean`.
- **SC-002** (FR-002): at `report`, a test lands a fixture carrying an introduced, a carried and a known finding with no task
  filed and no `gm-review.jsonl` row written, and still refuses one with a claim owed a check.
- **SC-003** (FR-003): at `clean`, a test refuses a fixture whose report lists an open finding and passes one whose report lists
  only DEFERRED findings.
- **SC-004** (FR-005): 405's status line opens `Withdrawn`; `phase-inputs.md` names each of the six tasks under its stage.
- **SC-005** (FR-006): each refusal's test goes red with it deleted; the docs name the switch.

## Assumptions

- 444's phase acceptance (its US2: the phase's claims round IN-STEP) is the phase checklist's own requirement and is not this
  switch's to relax.

## Review history

- 2026-10-28, round 1 (spec-fidelity, MODE 2): CHANGES REQUIRED, 2 items - FR-002 names the gate's consumers from a stated search
  and what each does at `report` (no known-drift row written); the owed-claim refusal kept as today, the route and wait unchanged.
  FR-002's reading of "basically ignore claims" (introduced findings warn) ruled the request's.
- 2026-10-28, round 2 (spec-fidelity-verify, MODE 3): CHANGES REQUIRED, 1 item - both of round 1 resolved; the route and wait
  meet an owed claim or a form problem, not an owed claim alone.
- 2026-10-28, the round cap: the round arbiter ACCEPT (ask:445-spec-round-3), standing as the spec's verdict; round 2's fix made
  as written.
