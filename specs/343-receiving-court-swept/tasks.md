# Tasks - feature 343, is the receiving court "swept"?

The record write is `research: physical` with its five boxes; the rest are `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The record (D1, FR-001): 0104's absence note on the court's surface, Morse's Sakai drawing named, 'the one drawing' sentences in line
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. 0104 states the Edo gravel and the silence elsewhere - swept, raked, sanded or bare earth - with its absence note and the Morse search; Sakai drawing named; the one-drawing sentences in line - M1 write and check, M1b, M1c (briefs/m1-checks.md; the review ledger's rows): source-reader READ, quote-check SUPPORTS (round 3 accepted by the round arbiter), source-applicability honest limits; make record-owed UNANSWERED=1 lists nothing
- [x] T02 The modal and the sheet's comments (D2, D3, FR-002, FR-005)
      research: rendering
      verify: DONE. the ubame sheet's comments carry no 'swept' (grep: 0); border-court.md never calls the court swept - its one 'swept' is the Guesses line naming swept earth among the surfaces not known outside Edo; the modal's research, form and depiction rounds answered (M1, M1b, M1c; record-owed lists nothing)
- [x] T03 Implementation check (feature 378): make impl-check F=343 reports nothing missing (D4, FR-004)
      research: rendering
      verify: DONE. make impl-check F=343: nothing missing (2026-10-11)
- [x] T04 Close: the tooling tests green; report; landed
      research: rendering
      verify: DONE. tooling tests green (make hooks-test, tests/tooling 1,616 passed, the arbiter suites 106); report.md written (make feature-report F=343 WRITE=1, 2026-10-11); lands with sync-with-main.sh done
- [x] GM review (make gm-reviewed F=343) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
