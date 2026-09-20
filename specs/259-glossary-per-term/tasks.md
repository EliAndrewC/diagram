# Tasks - feature 259, the glossary is written one word per file

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5). Research: [`research.md`](research.md)
(R1-R4). Every prose or code task: American spellings, hyphens only.

**No task here is `research: physical`.** The feature moves the glossary's bytes between files and
reopens no historical question; the two tooltips it changes are each showing another term's definition
today because of a file order nobody chose (R2), which is a presentation decision, not a finding.

## Phase 0 - the baseline

- [x] T01 The regression baseline: `make done` on unmodified code in the clone at `d7cbe8a8`, recorded
      in `measurements.json` as `m:baseline-done`; every later failure checked against it before it is
      called new
      research: rendering
      measure: the run's own output
      verify: DONE. make done on unmodified code at d7cbe8a8 short-circuited green - nothing the gate exercises had changed since feature 258's landing run, which is therefore this feature's baseline: 4,179 passed, 4 skipped, all three floors, 92 s (m:baseline-done)
- [x] T02 The gate-cost bookend, before (R4): the test phase's time and count from T01
      research: rendering
      verify: DONE. R4-before: the baseline's test phase, 46.65 s over 4,179 tests - feature 258's landing run (m:baseline-done). 51.40 s was 258's OWN baseline in a detached worktree, over 4,113 tests, and is a different run

## Phase 1 - the split (FR-001 to FR-005; D1, D2)

- [x] T03 RED: `tests/interactive/test_glossary_source.py` asserts `assemble(split(glossary.json)) ==
      glossary.json` over the real file and fails for want of the module
      research: rendering
      verify: DONE. the round trip over the real glossary, red with ModuleNotFoundError before the module existed
- [x] T04 `interactive/glossary_source.py`: the filename rule (the term, percent-encoded where a
      filename cannot carry it, behind a gapped prefix), `split`, `assemble`, `check`. The assembly
      reproduces `json.dumps(..., ensure_ascii=False, indent=1) + "\n"` exactly, and reads each term
      from its file's CONTENT, never from its name
      research: rendering
      verify: DONE. glossary_source.py - the filename rule (the term, percent-encoded only where a filename cannot carry it, behind a gapped prefix), split, assemble, check, and the index; the assembly reproduces json.dumps(ensure_ascii=False, indent=1) + newline exactly and reads each term from its file's content
- [x] T05 `make glossary` assembles before it derives, `CHECK=1` reports either file stale, and the
      order is stated in the Makefile rather than left to the caller; `SPLIT=1` performs the one-time
      split. The reference case first: one term round-trips
      research: rendering
      verify: DONE. make glossary assembles before it derives (the engine builds GLOSSARY at import, so the other order derives from the file as it stood one edit ago), CHECK=1 reports either stale, SPLIT=1 did the one-time split
- [x] T06 **The split**: all 720 terms written to `interactive/assets/glossary/`. `git diff --stat` over
      `glossary.json` and `research/assets/glossary.js` is empty (SC-003)
      research: rendering
      measure: the byte diff of both assembled files
      verify: DONE. 720 term files written; git diff over glossary.json and glossary.js empty - committed as its own diff before any content correction
- [x] T07 The refusals, each with a test that fails without it: a term file whose name and content
      disagree, two files claiming one prefix, a stray file in the directory, a missing directory, and
      a committed `glossary.json` that differs from its term files (FR-005, FR-006)
      research: rendering
      verify: DONE. eleven refusal cases - duplicate prefix, stray file, name and content disagreeing (checked in the ENCODE direction, since decoding stops being injective the moment a term carries a %), missing directory, a split that would not rebuild - plus make glossary CHECK=1 in sync-with-main.sh beside make record CHECK=1

## Phase 2 - what the split is for (FR-007 to FR-009, FR-011; D3, D4, D5)

- [x] T08 FR-011, the clashes: the resolving rule applied to the 7, the `bettō` duplicate removed, and a
      test that fails while any variant is claimed twice or listed twice. The two tooltips that change
      are named in the commit and in the spec's Decisions Recorded
      research: rendering
      measure: `measure.py R2` before and after
      verify: DONE. the 7 clashes resolved by the rule (the term whose name is the variant keeps it, comparing with case, spaces and hyphens folded) and the betto duplicate removed; two tooltips change, each of which was showing another term's definition; a test fails if it happens again
- [x] T09 FR-007: `scripts/_hm_record.py` learns `glossary.json` as an assembled file whose fragments
      are the term directory - a case in the same function, not a second guard - with its cases in
      `scripts/test-record-edit-hooks.sh` and the proof that deleting the branch turns them red
      research: rendering
      verify: DONE. _hm_record.py learns glossary.json as an assembled file whose fragments are the term directory, with its own refusal wording; 14 cases green, and deleting the refusal branch still turns 5 red
- [x] T10 FR-008, FR-009: the VOCABULARY checks' contracts say to list the directory, grep it for a
      variant, and read a term file only for a definition they name; `research/CLAUDE.md` and the
      interactive index say where a term lives
      research: rendering
      verify: DONE. record-format's contract carries the three-row table (the variant index for a word, the listing for a term, one file for a definition) and why a grep will not do; research/CLAUDE.md carries the same

## Phase 3 - landing

- [x] T11 **FR-010, the re-run that says whether this worked**: `record-format` over the same entry
      feature 258 measured (`ways` 010), reporting the bytes read under the glossary and whether the
      findings are the same. A check that reads less and finds less has not been improved. Recorded as R5
      research: rendering
      measure: the dispatch's own transcript, by `specs/258-*/measure.py R3`'s method
      verify: DONE. R5 records THREE runs of the same check on the same entry. The bytes: 45,921 against 62,720, and glossary.js never opened. The findings: eight terms proposed by every run - the stable core - and a tail that varies in BOTH directions, the whole-glossary run missing `embankment` that a scoped run found, the scoped runs missing `NRCS` and `out-to-out` that it found. SC-002 is met by no single run in either condition and is NOT reworded: it is recorded unmet and put to the GM
- [x] T12 The gate-cost bookend, after (R4), and `make done` green; every failure checked against T01
      research: rendering
      verify: DONE. gate green in 124 s: 4,191 passed, 4 skipped, 100% over 27,113 statements; twelve more tests than the baseline and zero new failures
- [x] T13 `docs/efficiency-tooling.md` carries the new shape and the measurement
      research: rendering
      verify: DONE. docs/efficiency-tooling.md carries the three questions and what answers each, why the index is not a convenience, and why the filename carries a prefix
- [x] T14 Stop-work: commit, `scripts/sync-with-main.sh done`. The delta touches engine code, so the
      route is GATED on T12's green gate
      research: rendering
      verify: DONE. everything the push is gated on is verified at this tick: make done green (4,191 passed, 4 skipped, 100% over 27,113 statements), make glossary CHECK=1 in sync, make record CHECK=1 in sync, make hooks-test green, spec-lint --delta clean, the tree committed. The delta touches engine code so the route is GATED on that green gate
