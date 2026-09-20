# Tasks - feature 258, the record is written per entry and assembled into the pages a reader opens

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D8). Research: [`research.md`](research.md)
(R1-R7). Contracts: [`contracts/fragment-format.md`](contracts/fragment-format.md),
[`contracts/record-cli.md`](contracts/record-cli.md). Layout: [`data-model.md`](data-model.md).

Every prose or code task: American spellings, hyphens only. **No task here is `research: physical`.**
The feature moves the record's bytes between files and reopens no historical question: every assertion,
every footnote and every evidence class keeps its text, which stages 1 and 2 prove by diff.

## Phase 0 - the baselines (constitution XIII, and the gate's cost)

- [ ] T01 The regression baseline: `git worktree add --detach /tmp/base258 HEAD`; there, `make quick ALL=1`
      and `make hooks-test`; the counts recorded in `measurements.json` as `m:baseline-quick`; every later
      failure checked against the clone before it is called new
      research: rendering
      measure: the worktree's own `make quick ALL=1` output
      verify:
- [ ] T02 The gate-cost bookend, before: `make done` phase timings on unmodified code, recorded in
      `research.md` as R7-before. The assembly check joins the gate in T13; this is what it is judged
      against
      research: rendering
      verify:

## Phase 1 - the registry, one file per source (FR-007 to FR-010; D1, D2)

- [ ] T03 RED: `tests/interactive/test_record_assembly.py` asserts `assemble(split(page)) == page` over
      `research/SOURCES.html` and fails for want of `l7r.diagram.interactive.record`
      research: rendering
      verify:
- [ ] T04 `interactive/record/fragments.py` - the layout as `data-model.md` states it: what a fragment is
      named, what its prefix means, where a page's directory is, which names are legal in one, and the
      gapped allocation (three digits a question, four a registry entry, counting by ten). Tests over
      names alone, no filesystem
      research: rendering
      verify:
- [ ] T05 `interactive/record/split.py` and `assemble.py` for the section shape: front, sections in prefix
      order, a section's own entries in prefix order, tail. Byte-for-byte concatenation, no normalization
      (FR-006, FR-013)
      research: rendering
      verify:
- [ ] T06 `tools/record_asset.py` and `make record` with `CHECK=1`, `PAGE=`, `SPLIT=`, exactly as
      `contracts/record-cli.md` states, including the message shapes
      research: rendering
      verify:
- [ ] T07 **The registry is split**: `research/sources/` - front, the five group files, 920 entries under
      `030-works-cited/`, tail. `make record CHECK=1` reports in sync and `git diff --stat
      research/SOURCES.html` is empty (FR-009, SC-003)
      research: rendering
      measure: the byte diff of the assembled registry against the file it replaced
      verify:
- [ ] T08 Every refusal in `contracts/fragment-format.md` that applies to a section page - duplicate
      prefix, stray file, missing front or tail, a registry key that differs from its filename, an
      exhausted gap - each with a test that fails without it and a message that names the file
      research: rendering
      verify:

## Phase 2 - the questions (FR-011 to FR-015; D2, D3)

- [ ] T09 **`research/ways.html` is split** (the reference artifact): `_front`, 5 questions, `_tail`.
      Byte-identical, proven by an empty diff
      research: rendering
      measure: `git diff --stat research/ways.html`
      verify:
- [ ] T10 **`research/cities/defenses.html` is split** - the one-level-down case, whose references carry
      `../citations/cities/...`. Byte-identical
      research: rendering
      verify:
- [ ] T11 **The sweep**: the other seventeen research pages, in one commit, each byte-identical. This is
      the second of the two steps, with its own verification (plan, "every step is two steps")
      research: rendering
      measure: `git diff --stat research/` - every page 0 changed
      verify:
- [ ] T12 `test_record_assembly.py` parametrizes over the REAL record - every page, every round trip -
      rather than over a fixture, so the test cannot drift from the thing it checks
      research: rendering
      verify:
- [ ] T13 The staleness check in both places (FR-003, FR-004, D6): the test at the gate, `make record
      CHECK=1` in `sync-with-main.sh` before either route. A record-only delta takes DIRECT, where the
      gate never runs - so a check in one place only has a hole exactly where this feature's commits land
      research: rendering
      verify:
- [ ] T14 The guard (FR-028, D7): `scripts/record-edit-hooks.sh` rewrites an `Edit` aimed at an assembled
      page to the one fragment holding its `old_string`, refuses where none or several do and names them,
      and always refuses a `Write`. `tests/tooling/test_record_edit_hooks.py` and a `make hooks-test` row;
      proved by deleting the guard and watching the test go red
      research: rendering
      verify:

## Phase 3 - the notes, and the numbers nobody types (FR-016 to FR-022; D4, D5)

- [ ] T15 `interactive/record/notes.py`: keys, allocation in document order, the back link, and the
      document-unique id per reference (`fnref-N`, `fnref-N-2`). Tests on plain strings first
      research: rendering
      verify:
- [ ] T16 The splitter derives the 1,850 keys by R5's rule (the leading source key, an ordinal where a page
      repeats one, the question's slug and an ordinal for the 326 that lead with none); `citations.py`
      reads notes from the fragments and `make citations` writes `_citations-works.html` instead of
      writing between markers in the page
      research: rendering
      verify:
- [ ] T17 **`ways` notes split** (the reference artifact again): the diff of `research/citations/ways.html`
      is inspected line by line and declared - footnote numbers, the ids that carry them, and nothing else
      research: rendering
      measure: the diff, classified
      verify:
- [ ] T18 **The sweep**: the other eighteen citations pages. The whole renumbering diff is checked by the
      contract's own test - strip the numbers from both sides and require equality, and require the
      multiset of (question, note body) pairs to be unchanged (SC-003)
      research: rendering
      verify:
- [ ] T19 The two defects, fixed by construction (FR-021, R4, R5): the 4 references that carry no id and
      the 2 pages with a duplicated one. A test that fails on the pre-split record and passes after, so
      the fix is proven rather than asserted
      research: rendering
      verify:
- [ ] T20 FR-027: `test_footnotes.py`, `test_citations.py`, `test_record.py`, `test_sources.py`,
      `test_record_format.py`, `test_classes.py`, `test_place.py` and `test_page.py` pass UNCHANGED - not
      one of them edited to accommodate this feature. An edit to any of them is a finding, and the reason
      goes here
      research: rendering
      verify:

## Phase 4 - collecting the saving (FR-023 to FR-026; D8)

- [ ] T21 `scripts/_record_prepass.py` addresses one question - a fragment path, or `PAGE=` with
      `SECTION=` - and prints the fragment paths a check should read
      research: rendering
      verify:
- [ ] T22 `scripts/_quote_verbatim.py` grows `--section`; `scripts/_entry_owed.py` reports the fragment
      path for a drifted pair, so the drift report names what to open
      research: rendering
      verify:
- [ ] T23 The four contracts (FR-024): `record-format`, `quote-check`, `entry-drift` and
      `source-applicability` are told to read the fragment they are given and not the assembled page.
      This is the only place the rule can reach them - a defined agent launches with `omitClaudeMd: true`
      (feature 256). `test_agent_models.py` still passes: no tier moves
      research: rendering
      verify:
- [ ] T24 `research/CLAUDE.md` (FR-025): how to find an entry without reading a page - the glob by key,
      the grep over a page directory - and that an assembled page is never hand-edited. The root
      `CLAUDE.md`'s research bullet and the guards table get the one-line versions
      research: rendering
      verify:
- [ ] T25 **FR-026, the re-run that says whether this worked**: `record-format` and `quote-check` over a
      fragment, against their recorded whole-page runs on the same entries (`seeded-format-clean`,
      `255-qc-capitals`). Report the record bytes read, the whole input, and whether the findings are the
      same. A check that reads less and finds less has not been improved (feature 255). Recorded as R8
      research: rendering
      measure: the two runs' own transcripts, by `measure.py R3`'s method
      verify:

## Phase 5 - landing

- [ ] T26 `make done` green, backgrounded, acted on by its notification; every failure checked against
      T01's baseline before it is called new (constitution XIII)
      research: rendering
      verify:
- [ ] T27 The gate-cost bookend, after (R7): `make record CHECK=1` over the whole record, and `make done`'s
      phase timings against T02. Over 2 s for the check, or a visible move in the gate, is diagnosed here
      in writing with the number
      research: rendering
      verify:
- [ ] T28 `docs/research-doctrine.md` and `docs/efficiency-tooling.md` carry the new shape and the reason
      for it - the measurement, not the preference
      research: rendering
      verify:
- [ ] T29 Stop-work: commit, `scripts/sync-with-main.sh done`. The delta touches engine code, so the route
      is GATED on T26's green gate
      research: rendering
      verify:
