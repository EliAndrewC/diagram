# Tasks - feature 191

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Part 1 and Part 3 are `research: rendering` (a citation form and a page form). Part 2's backfill is
`research: physical` in the constitution's sense - it reads sources about how places were built - and each
backfill task carries the three boxes.

- [ ] T01 FR-001/FR-004: the footnote form and the mechanical test (`tests/interactive/test_footnotes.py`); a worked section converted by hand as the exemplar (the farmstead fixtures entry: the coop's two sources, two footnotes)
      research: rendering
      verify: the test is red on a footnote without a quote and on a roster key without a footnote; green on the exemplar
- [ ] T02 FR-003: the `quote-check` agent; run it on the exemplar section and record its verdicts
      research: rendering
      verify: the agent returns VERBATIM/SUPPORTS for the exemplar and names an unfootnoted assertion when one is planted
- [ ] T03 FR-005: the rule in `research/CLAUDE.md`, root `CLAUDE.md`, the constitution (XII, v2.17.0); README reported
      research: rendering
      verify: read back
- [ ] T04 FR-009/FR-010/FR-011: the one-time conversion of the 15 record files and the registry to hand-authored HTML (scripted, checked, `git mv`; the `.md` deleted); `research/assets/record.css` + `record.js` (the hover); README and CLAUDE.md not converted, the README's link table reported
      research: rendering
      verify: every heading, table, list, link, quote and SOURCE block present in the page; ids equal `github_anchor` for all 183 sections and the registry keys; a hover shows the quote (browser test)
- [ ] T05 FR-012/FR-013/FR-014: `sources.py` reads the HTML; `_ENTRY_FILE` and the 51 class entries name `.html`; the maps link locally; feature 190's link test and the roster tests on the HTML surface; the guards' scope checked; docs
      research: rendering
      verify: every class entry's file and every anchor a pool map emits exist on disk; `make done` green at 100%
- [ ] T06 FR-006/FR-007: the backfill, file by file (15 record files, one agent each), then `quote-check` over every file, then the fixes
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      verify: every section's roster keys are quoted (the test); the checker's verdicts per file recorded here; the residue listed with what was tried
- [ ] T07 FR-008: the answer to the GM - contradictions found, the residue, D2's ruling; push (GATED: engine code)
      research: rendering
      verify: landed; a map's "See references" opens the local page and a footnote hovers
