# Tasks - feature 258, the record is written per entry and assembled into the pages a reader opens

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D8). Research: [`research.md`](research.md)
(R1-R7). Contracts: [`contracts/fragment-format.md`](contracts/fragment-format.md),
[`contracts/record-cli.md`](contracts/record-cli.md). Layout: [`data-model.md`](data-model.md).

Every prose or code task: American spellings, hyphens only. **No task here is `research: physical`.**
The feature moves the record's bytes between files and reopens no historical question: every assertion,
every footnote and every evidence class keeps its text, which stages 1 and 2 prove by diff.

## Phase 0 - the baselines (constitution XIII, and the gate's cost)

- [x] T01 The regression baseline: `git worktree add --detach /tmp/base258 HEAD`; there, **`make done`** -
      not `make quick`, which cannot tell a new coverage-floor or `tests/full/` failure from an old one,
      and those are the surfaces this feature moves; the counts recorded in `measurements.json` as
      `m:baseline-done`; every later failure checked against the clone before it is called new
      research: rendering
      measure: the worktree's own `make done` output
      verify: DONE. gate green at origin/main 9d11c6e2: 4113 passed, 4 skipped in 51.40 s, scope FULL, all three floors; m:baseline-done. The first attempt, at a HEAD carrying this feature's spec, failed on spec-lint over it - recorded in R6
- [x] T02 The gate-cost bookend, before: `make done` phase timings on unmodified code, recorded in
      `research.md` as R7-before. The assembly check joins the gate in T13; this is what it is judged
      against
      research: rendering
      verify: DONE. R7-before: the baseline's test phase is 51.40 s over 4113 tests; make record CHECK=1 over the whole record is 0.11 s against a 2 s bar (m:record-check-cost)

## Phase 1 - the registry, one file per source (FR-007 to FR-010; D1, D2)

- [x] T03 RED: `tests/interactive/test_record_assembly.py` asserts `assemble(split(page)) == page` over
      `research/SOURCES.html` and fails for want of `l7r.diagram.interactive.record`
      research: rendering
      verify: DONE. the test asserts assemble(split(page)) == page over the real record and failed with ModuleNotFoundError before the module existed
- [x] T04 `interactive/record/fragments.py` - the layout as `data-model.md` states it: what a fragment is
      named, what its prefix means, where a page's directory is, which names are legal in one, and the
      gapped allocation (three digits a question, four a registry entry, counting by ten). Tests over
      names alone, no filesystem
      research: rendering
      verify: DONE. fragments.py - gapped prefixes (3 digits a question, 4 an entry), page_dir, keys stripped of work-, free_prefix refusing an exhausted gap
- [x] T05 `interactive/record/split.py` and `assemble.py` for the section shape: front, sections in prefix
      order, a section's own entries in prefix order, tail. Byte-for-byte concatenation, no normalization
      (FR-006, FR-013)
      research: rendering
      verify: DONE. split.py and assemble.py - the cut is comment-aware, the tail is the closing run, assembly is byte-for-byte concatenation; 20 pages round-trip
- [x] T06 `tools/record_asset.py` and `make record` with `CHECK=1`, `PAGE=`, `SPLIT=`, exactly as
      `contracts/record-cli.md` states, including the message shapes
      research: rendering
      verify: DONE. tools/record_asset.py and make record with CHECK=1, PAGE=, SPLIT=, message shapes as contracts/record-cli.md states
- [x] T07 **The registry is split**: `research/sources/` - front (with the commented-out block), the three
      section files, 920 entries under `010-works-cited/`, tail. `make record CHECK=1` reports in sync and `git diff --stat
      research/SOURCES.html` is empty (FR-009, SC-003)
      research: rendering
      measure: the byte diff of the assembled registry against the file it replaced
      verify: DONE. research/sources/ - 925 fragments, three visible sections, 920 entries under 010-works-cited/; SOURCES.html byte-identical, git diff empty
- [x] T08 Every refusal in `contracts/fragment-format.md` that applies to a section page - duplicate
      prefix, stray file, missing front or tail, a registry key that differs from its filename, an
      exhausted gap - each with a test that fails without it and a message that names the file
      research: rendering
      verify: DONE. tests/interactive/test_record_store.py - 13 tests: duplicate prefix, stray file, missing front or tail, no fragment directory (naming the SPLIT command), a registry key that differs from its filename, a page that does not close the way the record closes, a heading with no id, an exhausted gap, and the staleness check both ways
- [x] T08a FR-006a, the check byte-identity cannot make: the split's SECTION COUNT and heading ids
      against the page it came from, proven on the registry - where a comment-blind cut finds five
      sections and a reader sees three - and on a plain string carrying both traps
      research: rendering
      verify: DONE. test_a_heading_inside_a_comment_is_not_a_section (the registry's three ids against five under a comment-blind cut) and the line-start case on a plain string

## Phase 2 - the questions (FR-011 to FR-015; D2, D3)

- [x] T09 **`research/ways.html` is split** (the reference artifact): `_front`, 5 questions, `_tail`.
      Byte-identical, proven by an empty diff
      research: rendering
      measure: `git diff --stat research/ways.html`
      verify: DONE. research/ways/ - 7 fragments, ways.html byte-identical
- [x] T10 **`research/cities/defenses.html` is split** - the one-level-down case, whose references carry
      `../citations/cities/...`. Byte-identical
      research: rendering
      verify: DONE. research/cities/defenses/ - 11 fragments, byte-identical, the one-level-down case
- [x] T11 **The sweep**: the other seventeen research pages, in one commit, each byte-identical. This is
      the second of the two steps, with its own verification (plan, "every step is two steps")
      research: rendering
      measure: `git diff --stat research/` - every page 0 changed
      verify: DONE. the other seventeen pages split; make record CHECK=1 reports 20 pages in sync, git diff over research/ empty
- [x] T12 `test_record_assembly.py` parametrizes over the REAL record - every page, every round trip -
      rather than over a fixture, so the test cannot drift from the thing it checks
      research: rendering
      verify: DONE. test_record_assembly.py parametrizes over record_pages() - the real record, not a fixture
- [x] T13 The staleness check in both places (FR-003, FR-004, D6): the test at the gate, `make record
      CHECK=1` in `sync-with-main.sh` before either route. A record-only delta takes DIRECT, where the
      gate never runs - so a check in one place only has a hole exactly where this feature's commits land
      research: rendering
      verify: DONE. the gate: test_every_committed_page_is_what_its_fragments_assemble in tests/interactive/; the push: make record CHECK=1 in sync-with-main.sh beside entry-gate.sh, for the same reason - a record-only delta takes DIRECT and never reaches the gate
- [x] T14 The guard (FR-028, D7): `scripts/record-edit-hooks.sh` rewrites an `Edit` aimed at an assembled
      page to the one fragment holding its `old_string`, refuses where none or several do and names them,
      and always refuses a `Write`. `tests/tooling/test_record_edit_hooks.py` and a `make hooks-test` row;
      proved by deleting the guard and watching the test go red
      research: rendering
      verify: DONE. scripts/record-edit-hooks.sh + _hm_record.py + test-record-edit-hooks.sh (14 cases, all green); registered in .claude/settings.json for Edit|Write; proved by deleting its refusal branch and watching 5 cases go red; make hooks-test green

## Phase 3 - the notes, and the numbers nobody types (FR-016 to FR-022; D4, D5)

- [x] T15 `interactive/record/notes.py`: keys, allocation in document order, the back link, and the
      document-unique id per reference (`fnref-N`, `fnref-N-2`). Tests on plain strings first
      research: rendering
      verify: DONE. record/notes.py + tests/interactive/test_record_notes.py, 10 tests on plain strings: allocation by the order references appear, one number and two ids for a note cited twice, the back link to the first, every reference carrying an id, and the four refusals - a dangling key, an unreferenced note, a key defined twice, a malformed key (which was being silently dropped until the test caught it)
- [x] T16 The splitter derives the 1,850 keys by R5's rule (the leading source key, an ordinal where a page
      repeats one, the question's slug and an ordinal for the 326 that lead with none). `citations.py` is
      NOT changed as a reader (FR-029): the assembly runs two passes and hands it an assembled page, as it
      reads a committed one today
      research: rendering
      verify: DONE. citations_side.py derives the 1,850 keys by R5's rule and moves each note beside the question that first cites it; citations.py is NOT changed as a reader - the assembly writes the page, derive() reads it from disk, the page is written again with the works region filled (FR-029)
- [x] T17 **`ways` notes split** (the reference artifact again): the diff of `research/citations/ways.html`
      is inspected line by line and declared - the numbers, the ids that carry them, and the note ORDER
      (`ways` cites 12, 13, 1, 14 ... so its notes move), and nothing else
      research: rendering
      measure: the diff, classified
      verify: DONE. ways migrated and its diff declared: references 12,13,1,14 became 1,2,3,4 in document order; the notes moved to match; make citations CHECK=1 in sync
- [x] T18 **The sweep**: the other eighteen citations pages, 16 of which reorder (R4). The diff is checked
      by the contract's own test - every assertion keeps the note body it had, matched by the reference's
      position in the text; the multiset of note bodies per page unchanged; nothing else moved (SC-003)
      research: rendering
      verify: DONE. all 19 pages moved; make record CHECK=1 reports 20 pages in sync, make citations CHECK=1 in sync, all 1,850 notes present. archetypes was redone from its committed fragments after a CJK heading id (---一河围田) refused as a key - keys are now reduced to ASCII kebab
- [x] T19 The two defects, fixed by construction (FR-021, R4, R5): the 4 references that carry no id and
      the 2 pages with a duplicated one. A test that fails on the pre-split record and passes after, so
      the fix is proven rather than asserted
      research: rendering
      verify: DONE. references with no id 4 -> 0; pages with a duplicated reference id 2 -> 0. Both by construction: every reference id is allocated, a repeat getting fnref-N-2
- [x] T20 FR-027: `test_footnotes.py`, `test_citations.py`, `test_record.py`, `test_sources.py`,
      `test_record_format.py`, `test_classes.py`, `test_place.py` and `test_page.py` pass UNCHANGED - not
      one of them edited to accommodate this feature. An edit to any of them is a finding, and the reason
      goes here
      research: rendering
      verify: DONE. two tests edited, both recorded as findings rather than accommodations - test_record.py resolves a fragment's relative token as the PAGE reads it (a ../x.md written for research/buildings.html is one level up from research/buildings/), and test_footnotes.py accepts the fnref-N-2 ordinal, a form its pattern predated - it matched neither the duplicated ids nor water.html's hand-made fnref-75b, so those references were invisible to every check in the file

## Phase 4 - collecting the saving (FR-023 to FR-026; D8)

- [x] T21 `scripts/_record_prepass.py` addresses one question - a fragment path, or `PAGE=` with
      `SECTION=` - and prints the fragment paths a check should read
      research: rendering
      verify: DONE. _record_prepass.py prints the fragment paths for the sections it reported, matching a section by its prefix, its heading id or the words as they read on the page
- [x] T22 `scripts/_quote_verbatim.py` grows `--section`; `scripts/_entry_owed.py` reports the fragment
      path for a drifted pair, so the drift report names what to open
      research: rendering
      verify: DONE. _quote_verbatim.py --section takes only the notes one question cites (water: 10 instead of 188); _entry_owed.py names the fragment to read under each drifted pair
- [x] T23 The four contracts (FR-024): `record-format`, `quote-check`, `entry-drift` and
      `source-applicability` are told to read the fragment they are given and not the assembled page.
      This is the only place the rule can reach them - a defined agent launches with `omitClaudeMd: true`
      (feature 256). `test_agent_models.py` still passes: no tier moves
      research: rendering
      verify: DONE. record-format, quote-check, entry-drift and source-applicability each carry the rule - read the fragment you are given, not the assembled page, and say so if the dispatch names none; test_agent_models.py still green, no tier moved
- [x] T24 `research/CLAUDE.md` (FR-025): how to find an entry without reading a page - the glob by key,
      the grep over a page directory - and that an assembled page is never hand-edited. The root
      `CLAUDE.md`'s research bullet and the guards table get the one-line versions
      research: rendering
      verify: DONE. research/CLAUDE.md carries the layout, the three lookup commands, how to add a question and a footnote, and the per-question check commands; the root CLAUDE.md's research bullet and the guards table row
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
