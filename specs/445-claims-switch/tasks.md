# Tasks - feature 445, the claims switch

## Occasions

- none: tooling only - no map feature, glyph or placement rule

## Tasks

- [x] T01 The `claims` switch in `l7r/diagram/switches.py` and `dev/switches.json` (shipped at `report`), `make claims-report-only` and `make claims-clean`, the other axis kept on a throw (D1; FR-001, FR-004, SC-001)
      research: rendering
      verify: DONE. landed: the claims switch in switches.py, thrown to report on record with the GM's words; remote kept on a claims throw; a malformed claims entry closes to clean alone
- [x] T02 The claims gate at `report` (only owed claims and form problems refuse; no carry filed, no known-drift row) and at `clean` (every open finding the report lists refuses, `open_findings` shared with the report) (D2, D3; FR-002, FR-003, SC-002, SC-003)
      research: rendering
      verify: DONE. landed: the gate at report and clean, each refusal proven red with it deleted; the companion suite at both states; _key_of fixed for a finding with no note
- [x] T03 Feature 405 closed Withdrawn with its evidence; its engine fixes and notes recorded in `specs/444-work-budget-program/phase-inputs.md` under their stages (D4; FR-005, SC-004)
      research: rendering
      verify: DONE. landed: 405 closed Withdrawn with its evidence; T98, T101, T104, T106, T111 and T165 in specs/444-work-budget-program/phase-inputs.md under web, homesteads, lane_wells, notice and track, today's counts marked
- [ ] T04 `docs/guards.md`, the gate's message and the root CLAUDE.md name the switch; the refusal proven to fire with it deleted; `make feature-report F=445 WRITE=1` (D5; FR-006, SC-005)
      research: rendering
