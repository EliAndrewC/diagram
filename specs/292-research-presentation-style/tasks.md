# Tasks - feature 292, how a research section is presented

Pilot phase. The sweep's tasks are added only after T09 is ticked (FR-011).

- [x] T01 The GM's request verbatim, the spec, spec-fidelity round 1 applied (FR-001 - FR-011). research: rendering
- [x] T02 The style guide `research/STYLE.md`, each rule marked GM or inferred; the rules file points at it (FR-001, FR-006, SC-001). research: rendering
- [x] T03 The hover's key link leads to the work's entry on the citations page, with its test (FR-005, SC-005). research: rendering
- [x] T03a Links to the citations page open in a new tab - the hover's key link (derived script) and the footnote number (record.js); unit test and the record-page browser test (FR-005). research: rendering
- [x] T04 A roster-less section's sources are read from its footnotes, with its test (FR-004, SC-004). research: rendering
- [x] T05 Glossary: `knob` redefined, `canopy-tree` added, `appurtenance` retired as unused (FR-007, SC-006). research: rendering
- [x] T06 The `record-style` agent, its tier, its bundle part and its guard entry (FR-008). research: rendering
- [ ] T07 The grove topic: 010 + 710 + 715 folded into one section, links and `Entry:` re-aimed, no citation lost (FR-002, FR-003, FR-009, FR-010, SC-002, SC-003). research: rendering
  - [x] the section written and assembled
  - [x] record-style on the old section (seeded against the GM's objections - it named every one) and on the new, with the merge audit (LOST 0; 7 FAIL applied) (SC-007)
  - [x] quote-check (4 PARTIAL, 2 unfootnoted - all applied) and record-format (clean) on the new section
  - [x] entry-drift on the HomesteadGrove modal: IN-STEP; its pre-existing gap fixed (its Note called the count read; its Why kept the cut 'largest thing' and the unsourced early-Edo date)
  - [ ] at the first `make done`: `PAIR_OK="292 moves no map layout - the maps whose layout moved (inashiro, kashikawa, kuwabata, mizuguchi, sawada) moved in feature 291's merged work in progress, whose review 291's session owes"` - `_review_owed.py` names them against origin/main; nothing in 292 touches a generator
  - [ ] at push: the copse modal's section (vegetation/210) moved only by a re-aimed link - `ENTRY_DRIFT_OK` with that reason
- [ ] T07a The GM's review of the pilot (2026-09-29): lead-line bullets (statement or question, readable from what came before) and metric-to-feet - the guide, the check's contract, `make style-prepass` with its tests and its bundle part, and the grove section revised (FR-012, FR-013, SC-009, SC-010). research: rendering
  - [x] guide, contract, prepass, tests, section revised
  - [x] the updated check run on the section before (named the 1868 lead line, the lead lines in the wrong form, all four metric figures) and after the revision (5 FAIL, applied) (SC-009)
- [x] T07b No visible GM ruling (GM 2026-09-29): the guide, the rules file, `record-format` and `record-style` contracts, the prepass's GM list with its test; the grove section's ruling moved to a comment and its sides bullet rewritten as the project's choice; the HomesteadGrove modal's two "the GM's ruling" made "this project's choice" (FR-014). research: rendering
- [x] T07c The GM's own examples are fixed points in the check's contract (two seeded-run findings contradicted them). research: rendering
- [x] T07d Number follows the map (GM 2026-09-29): the guide, `record-style` rule 9a; the grove section's map bullets and lead lines made plural (FR-015). research: rendering
- [x] T07e The rendering collection and its automatic cross-links (FR-017): `sources.COLLECTIONS` read by every page lister, `record/xref.py` and its hook in the assembly, the `xref` style, `rendering/homesteads` with its first section (the groves) and its rule as a nested list; the HomesteadGrove modal's `Entry:` names both. research: rendering
- [x] T07f Paragraphs over 150 words - the style prepass's fourth list, seeded on the old rule paragraph (364 words, flagged) (FR-018). research: rendering
- [x] T07g Tests for `xref.py` (100% of it) and the collection plumbing; the page-listing test helpers read `collection_pages`, so the rendering page is under every record test (which found it missing its Evidence field). research: rendering
- [ ] T08 The size cap for a topic section - the GM's choice (spec Decisions; plan D3). research: rendering
- [ ] T09 **The GM signs off on the guide and the check** - after as many pilot topics as the GM asks for; only then are the sweep's tasks written (FR-011, SC-008). research: rendering
- [ ] T10 **Not to be confused with** (FR-016) - AFTER the sweep, when every section has its final title: the pairs as data (from `confusables.md`, two-way by construction), rendered at the top of each section by `make record`, a test that every pair resolves to a real section and every rendered list matches the data, and `record-style` checking a section that a reader could confuse with another has its list. research: rendering
