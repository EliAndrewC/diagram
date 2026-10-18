# Tasks - feature 386, the landing cohort

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The fresh block on every `make cohort`, the landing cohort, its push gate and the fresh rate (plan T01, D1-D9; FR-001 to FR-010): `cohort_audit --fresh`, `make cohort-landing` (main's baseline first), `cohort-gate.sh` on the GATED and GATED-LOCAL routes with `COHORT_OK`, `cohort_seeds`' fresh rate, the docs; tests red without each rule
      research: rendering
      verify: DONE. DONE. cohort_audit --fresh (block in the same pool and record, outside pass count and exit; test_cohort_audit); make cohort FRESH default 4 measured (m:fresh-block-cost: 16 maps 57.2 s, 20 maps 56.7 s); make cohort-landing (baseline first) rolled on this engine: 54/54 pass, fresh 9 of 48; cohort-gate.sh on GATED/GATED-LOCAL with COHORT_OK (test-cohort-gate.sh 13, sync-with-main case 27 red without the call); cohort-seeds fresh rate; docs; make done green, hooks-test green
- [x] T02 The close: this feature's own landing through `make cohort-landing` (SC-004), the feature report, the six failing fresh seeds and the measured fresh rates reported to the GM
      research: rendering
      verify: DONE. DONE. landing cohort rolled on this feature's engine (dev/cohort-log/20261018T044901Z, 54/54 pass, fresh 9 of 48) and the gate takes it; report.md written; the six fresh failures and the fresh rates go to the GM in the landing message
