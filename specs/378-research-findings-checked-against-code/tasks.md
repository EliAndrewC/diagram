# Tasks - feature 378, a research feature ends with its findings checked against the code

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The reader (plan D1-D3, FR-001, FR-003): `scripts/record/impl_check.py` + `make impl-check F=<n>`
      research: rendering
      verify: DONE. impl_check.py + make impl-check: changed questions from non-merge commits whose subject opens with the number (pre-329 prefix accepted); a claim cites a question by its findings page only; owed for any claims.owed reason; (b) needs searched:; test_impl_check.py 7/7; real features read (317 0081, 315 0046, 310 0038)
- [x] T02 Held at every close (plan D4, FR-004): close_check.reasons asks it
      research: rendering
      verify: DONE. close_check.reasons appends impl_check.missing for the repository holding the feature; the closing-check test in test_impl_check.py and test_close_check.py green
- [x] T03 The text (plan D5, FR-005, FR-006, FR-007): the template task, CLAUDE.md, research/CLAUDE.md, every spec `make speckit-todo AFFECTS="research record"` lists open at landing
      research: rendering
      verify: DONE. tasks template's implementation-check task; CLAUDE.md and research/CLAUDE.md state the rule; every spec make speckit-todo AFFECTS='research record' lists open (336 337 338 343 352 368 374) carries the feature 378 line
- [x] T05 Claimed units outside the hamlet scope (plan D6, FR-009): `tools/claims.py:claimed_outside` in `all_units`; the four claims it brings in checked by impl-drift
      research: rendering
      verify: DONE. claimed_outside in all_units (own claims only; coverage unchanged); tests/tools/test_claims.py 38 passed incl. SC-005; the 4 claims checked by impl-drift and recorded (barracks DRIFTED, 3 IN-STEP, 22 UNCLAIMED); make claims-owed: none
- [x] T04 Close: make done green (an engine file changed); the tooling tests and make hooks-test green; report; landed
      research: rendering
      verify: DONE. make done green alone in the foreground (the arbiter's ruling on the two overlapping red gates); tooling tests and hooks-test inside it; report written; landed by the push carrying this tick
- [x] GM review (make gm-reviewed F=378) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
