# Tasks - feature 259, the glossary is written one word per file

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5). Research: [`research.md`](research.md)
(R1-R4). Every prose or code task: American spellings, hyphens only.

**No task here is `research: physical`.** The feature moves the glossary's bytes between files and
reopens no historical question; the two tooltips it changes are each showing another term's definition
today because of a file order nobody chose (R2), which is a presentation decision, not a finding.

## Phase 0 - the baseline

- [ ] T01 The regression baseline: `make done` on unmodified code in the clone at `d7cbe8a8`, recorded
      in `measurements.json` as `m:baseline-done`; every later failure checked against it before it is
      called new
      research: rendering
      measure: the run's own output
      verify:
- [ ] T02 The gate-cost bookend, before (R4): the test phase's time and count from T01
      research: rendering
      verify:

## Phase 1 - the split (FR-001 to FR-005; D1, D2)

- [ ] T03 RED: `tests/interactive/test_glossary_source.py` asserts `assemble(split(glossary.json)) ==
      glossary.json` over the real file and fails for want of the module
      research: rendering
      verify:
- [ ] T04 `interactive/glossary_source.py`: the filename rule (the term, percent-encoded where a
      filename cannot carry it, behind a gapped prefix), `split`, `assemble`, `check`. The assembly
      reproduces `json.dumps(..., ensure_ascii=False, indent=1) + "\n"` exactly, and reads each term
      from its file's CONTENT, never from its name
      research: rendering
      verify:
- [ ] T05 `make glossary` assembles before it derives, `CHECK=1` reports either file stale, and the
      order is stated in the Makefile rather than left to the caller; `SPLIT=1` performs the one-time
      split. The reference case first: one term round-trips
      research: rendering
      verify:
- [ ] T06 **The split**: all 720 terms written to `interactive/assets/glossary/`. `git diff --stat` over
      `glossary.json` and `research/assets/glossary.js` is empty (SC-003)
      research: rendering
      measure: the byte diff of both assembled files
      verify:
- [ ] T07 The refusals, each with a test that fails without it: a term file whose name and content
      disagree, two files claiming one prefix, a stray file in the directory, a missing directory, and
      a committed `glossary.json` that differs from its term files (FR-005, FR-006)
      research: rendering
      verify:

## Phase 2 - what the split is for (FR-007 to FR-009, FR-011; D3, D4, D5)

- [ ] T08 FR-011, the clashes: the resolving rule applied to the 7, the `bettō` duplicate removed, and a
      test that fails while any variant is claimed twice or listed twice. The two tooltips that change
      are named in the commit and in the spec's Decisions Recorded
      research: rendering
      measure: `measure.py R2` before and after
      verify:
- [ ] T09 FR-007: `scripts/_hm_record.py` learns `glossary.json` as an assembled file whose fragments
      are the term directory - a case in the same function, not a second guard - with its cases in
      `scripts/test-record-edit-hooks.sh` and the proof that deleting the branch turns them red
      research: rendering
      verify:
- [ ] T10 FR-008, FR-009: the VOCABULARY checks' contracts say to list the directory, grep it for a
      variant, and read a term file only for a definition they name; `research/CLAUDE.md` and the
      interactive index say where a term lives
      research: rendering
      verify:

## Phase 3 - landing

- [ ] T11 **FR-010, the re-run that says whether this worked**: `record-format` over the same entry
      feature 258 measured (`ways` 010), reporting the bytes read under the glossary and whether the
      findings are the same. A check that reads less and finds less has not been improved. Recorded as R5
      research: rendering
      measure: the dispatch's own transcript, by `specs/258-*/measure.py R3`'s method
      verify:
- [ ] T12 The gate-cost bookend, after (R4), and `make done` green; every failure checked against T01
      research: rendering
      verify:
- [ ] T13 `docs/efficiency-tooling.md` carries the new shape and the measurement
      research: rendering
      verify:
- [ ] T14 Stop-work: commit, `scripts/sync-with-main.sh done`. The delta touches engine code, so the
      route is GATED on T12's green gate
      research: rendering
      verify:
