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
- [x] T07a The GM's review of the pilot (2026-09-29): lead-line bullets (statement or question, readable from what came before) and metric-to-feet - the guide, the check's contract, `make style-prepass` with its tests and its bundle part, and the grove section revised (FR-012, FR-013, SC-009, SC-010). research: rendering
  - [x] guide, contract, prepass, tests, section revised
  - [x] the updated check run on the section before (named the 1868 lead line, the lead lines in the wrong form, all four metric figures) and after the revision (5 FAIL, applied) (SC-009)
      verify: DONE. its sub-items done; the lead-line and metric rules held by the style prepass and record-style across the sweep
- [x] T07b No visible GM ruling (GM 2026-09-29): the guide, the rules file, `record-format` and `record-style` contracts, the prepass's GM list with its test; the grove section's ruling moved to a comment and its sides bullet rewritten as the project's choice; the HomesteadGrove modal's two "the GM's ruling" made "this project's choice" (FR-014). research: rendering
- [x] T07c The GM's own examples are fixed points in the check's contract (two seeded-run findings contradicted them). research: rendering
- [x] T07d Number follows the map (GM 2026-09-29): the guide, `record-style` rule 9a; the grove section's map bullets and lead lines made plural (FR-015). research: rendering
- [x] T07e The rendering collection and its automatic cross-links (FR-017): `sources.COLLECTIONS` read by every page lister, `record/xref.py` and its hook in the assembly, the `xref` style, `rendering/homesteads` with its first section (the groves) and its rule as a nested list; the HomesteadGrove modal's `Entry:` names both. research: rendering
- [x] T07f Paragraphs over 150 words - the style prepass's fourth list, seeded on the old rule paragraph (364 words, flagged) (FR-018). research: rendering
- [x] T07g Tests for `xref.py` (100% of it) and the collection plumbing; the page-listing test helpers read `collection_pages`, so the rendering page is under every record test (which found it missing its Evidence field). research: rendering
- [x] T07h The size cap counts prose only; quote-check notes in 12,000-byte batches; no notes to record-style (but for a merge audit) or entry-drift (FR-019). research: rendering
- [x] T07i Originals stored apart: `record/originals.py`, `make record` moves inline originals (6,171 runs in 618 notes files moved; 165 assembled files identical but for the wrapper), the hover and the citations page collapse them (`record.js`, browser-tested), the file filters of every record reader, `translation-check` and `make translation-owed`, the contracts and rules (FR-020). research: rendering
- [x] T07j translation-check run on the owed pairs (7 today: feature 291's and an earlier landing's). research: rendering
  - [x] the grove section's 4 (2026-09-29): FAITHFUL 4 - the first run of the check
  - [x] archetypes/110's 3 (not this feature's section; owed by the change that added them)
      verify: DONE. archetypes/110's pairs checked with the record-wide translation-check of 2026-10-01 (394 pairs, 380 faithful, the rest fixed)
- [x] T07k The GM's footnote review (2026-09-29): the heading link on the heading's row, "How it's drawn" (FR-021); the retired forms swept from 1,946 files - "(the source's own English)" and "translated from the <language> by this project" - with the test that holds them out (FR-022); "1868" a glossary term, the skimmer rule in the guide, `record-style` rule 5c and the prepass's years list (FR-023); multi-passage notes as lists, 908 notes, the pages' text proved unchanged (FR-024). research: rendering
- [x] T07l Absence notes (GM 2026-09-29): the one opening sentence in `record/absence.py`, rendered by the assembly; the search as a comment; findings as lists; the grove topic's six converted ("and on no page found" written out: the bulletin is not online; 屋敷林 translated); the prepass's two new lists, the contracts and rules (FR-025). research: rendering
- [x] T08 The size cap for a topic section - the GM's choice: prose only, notes bounded in the quote-check's batches (FR-019). research: rendering
- [x] T07m Second pilot topic (GM 2026-09-29: "take the next section ... figure out whether there are one or more other sections which should fold into this one"): homesteads 020 + 025 + 030 + 490 + 700 folded into "Threshing and drying yards at farmhouses (niwa)", the map half into rendering/homesteads "How our maps draw threshing and drying yards (niwa)"; checks: record-style x2 (with the merge audit: LOST 6, all restored), record-format x2, quote-check x3 (9 PARTIAL/unfootnoted, applied - the Hakka and the Tiangong Kaiwu's author newly sourced from pages already cited), entry-drift (DRIFTED, 3 fixed); a prepass defect found and fixed (the heading's rendering link read as its text); two guide rules added. research: rendering
  - [x] translation-check on the 3 owed pairs: FAITHFUL 3
- [x] T07n The GM's review of the work-yard topic (2026-09-30): the three unread-page claims traced to feature 134's pass of 2026-08-28 and removed, the minimum yard stated as this project's choice, Kodaira on the download list (FR-026); the kanji gloss form, the prepass's check of it and `translation-owed`'s gloss pairs, 垣根 glossed (FR-027); "are" dropped from the glossary and the common-English-word test (FR-028). research: rendering
  - [x] translation-check on the grove's owed pairs, the new gloss 垣根 (kakine, "hedge") among them: FAITHFUL 5
- [x] T07o Third pilot topic (GM 2026-09-30: *"a section not specifically about garden sun, but about shade in general"*): homesteads 040 + 043 + 044 + 046 and vegetation 610 folded into "Sunlight and shade on the farm", the map rules into rendering/homesteads "How our maps keep yards and gardens in the sun"; checks: record-style x2 (with the merge audit: LOST 11, restored or kept in comments), quote-check x3 (7 PARTIAL applied; the minami-2022 full text read and made the key's link), record-format x2, entry-drift x4 (3 DRIFTED fixed), translation-check (FAITHFUL 1); two guide rules added (a topic can be a condition; a lead line states no more than its sources). research: rendering
- [x] T09 **The GM signs off on the guide and the check** - after as many pilot topics as the GM asks for; only then are the sweep's tasks written (FR-011, SC-008). research: rendering
  - [x] signed off 2026-09-30, after three pilot topics: *"What you have done so far seems good enough to roll out to the rest of our research Sections. So please update the feature to mark my acceptance of our current process and checks and whatnot."* (request.md)

## The sweep (plan D6-D10)

- [x] T11 The sweep's machinery: a topic plan for every page (`sweep/plan-<page>.md`, D6), reviewed by the session; the brief generator `sweep/make_briefs.py` and its two templates (D7); the plan's sweep decisions reviewed by `spec-fidelity`. research: rendering
      verify: DONE. the 19 page topic plans and 2 additions plans in sweep/, the brief templates and generator, the merge tools in sweep/tools/; the plan's sweep decisions reviewed by spec-fidelity, CLEAR at round 3 (2026-10-01)
- [x] T12 buildings: every section in a topic, each group written and checked (D7); the page's checks report. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 54 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T13 religion-and-death, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 42 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T14 urban-features, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 51 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T15 towns, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 36 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T16 archetypes, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 21 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T17 fields, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 23 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T18 water, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 35 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T19 settlements, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 4 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T20 presentation, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 3 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T21 the cities collection, as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 87 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T22 vegetation, after feature 291's latest work is merged in (D8), as T12. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 22 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T23 ways, as T22. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 16 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [x] T24 homesteads (beyond the three pilot topics), as T22. research: rendering
      verify: DONE. every group written and checked (record-style with the merge audit, quote-check, record-format, entry-drift, translation-check where owed); 38 section lines in the page's checks report; merged into this clone and the record tests green, 2026-10-01
- [ ] T25 The record as a whole: a test that no section keeps a `Sources:` roster and every section's sources are its footnotes' (the sweep's completion, held); `make translation-owed` empty; `make done`; 291 landed, main merged, the feature landed (D10). research: rendering
  - [x] the three clones merged into this one and main merged (features 287 and 291 landed): 239 sections, every one carrying the sweep's mark; interactive tests 1555 passed (2026-10-01)
- [x] T26 The closing pass: what the sweep's checks left (the 26 items "for the GM" put to `escalation-check` on 2026-10-01 - 1 kept and answered, 24 cut as the session's own; the open-questions file that carried them is deleted, its content here and in request.md). research: rendering
  - [x] the GM's answer to the one kept question (request.md, 2026-10-01: "(b) the earlier ruling was never intended to be a deviation from historical norms"): a senior samurai house inside a provincial city's wall is enclosed by rank, as `rendering/cities/government` 280 says; 030's "deliberate deviation" is dropped, and the capital-versus-provincial contrast in `rendering/cities/capitals` 390 is rewritten around what the record shows actually differed
  - [x] the ministry office's size at a capital against a provincial seat, as RESEARCH (the GM, 2026-10-01: "whatever our research shows should be the driving force ... the offices of the six ministries in Imperial China or differences between smaller and larger cities in Edo period Japan"); the "recorded feature 018 decision (GM 2026-08-09)" in `rendering/cities/government` 230 is corrected - it is feature 018's research note (`specs/018-capital-space-budget/research.md` line 62), not a ruling of the GM's; the drawn sizes (the capital's 224 x 148 ft, the provincial 114 x 78 to 140 x 95 ft, citybudget's "roughly 2x" comment) follow what the research finds, a judgment between the Japanese and the Chinese evidence labeled as one
  - [x] the `l7r-budgets` registry link stands (the GM's notes are canon and keep their registry link); the two PARTIAL quotes and the grounds note at cities/capitals 010 get their stored originals and a citation or an absence note
  - [x] BenchNoticeBoard relabeled guess, matching its rendering section
  - [x] the town-framing spec heading in presentation reads "for a provincial city" (presentation 010 already says a town map is as much about its surroundings)
  - [x] the Takayama survey's figure (site 9,807 m², total floor 3,018 m², about 31%, floor area not footprint) written in as a citation; the 37-42% built-cover guess revisited against it
  - [x] the byre's drawn share calibrated or labeled; the StorageShed modal narrowed to its sections and labeled as its rendering section is; the Privy and HenCoop modal fixes applied
  - [x] the Garden modal relabeled guess, matching its rewritten section
  - [x] the road at a compound gate is the road the compound stands on, at that road's width (ways 070); Ochiba's 13.3 ft approach checked against the Imperial road's 30 ft
  - [x] the paddy's shoot-scatter rule moved to the rendering section
  - [x] the dike band past the Echizen 18 ft bound brought under it or labeled a convention with its reason; the PerimeterDike modal's "6-10 m" (the pond dikes' figure) corrected
  - [x] the county-yamen encyclopedia and the fujita-2007 PDF on the GM's download list
  - [x] the small practice ground inside the wall (attested at Chongming) a knob
  - [x] the T-shaped town plan (ways 180) joins the town-plan knob in rendering/towns 230; the crank at a town's ends noted as future work
  - [x] the day-office and official-study bullet moved to the office-hall rendering section, the DayOffice and OfficialStudy modals following it
  - [x] the retitles the checks proposed made where the style guide calls for them, their links re-aimed
  - [x] the note gating a seventeenth-century date by period dropped (it is inside the record's pre-1868 window)
  - [x] the town's inn count reconciled (a calibration); a walled town's inn stands in its gate market (towns 080)
  - [x] the downstream intake side, attested only in modern practice, dropped under the GM's ruling of 2026-09-28
  - [x] the KarosHouse modal gives the guess for the hand-drawn house and "accurate" for the county-town bay
  - [x] the cross-topic moves the checks deferred to a later group (the yamen bullet and the rectangular-compound bullet to cities/government's compound topic; the granary siting-knob link; the caravan and post-station bullets to towns 340; the dispersed-farm bullet of the row-village rendering), each where the topic it belongs to now stands
      verify: DONE. closing briefs C1-C4 (sweep/closing/, report in sweep/closing-checks.md) and the session: the GM's answer (b) applied in rendering/cities/government 030, 080, 280 and capitals 390; the office size researched in both traditions (capital ministry at most half again a provincial one, a labeled judgment); the 24 cut items and the deferred moves done; the 394 owed translations checked (380 faithful, 14 fixed or confirmed), 2026-10-01
- [x] T10 **Not to be confused with** (FR-016) - AFTER the sweep, when every section has its final title: the pairs as data (from `confusables.md`, two-way by construction), rendered at the top of each section by `make record`, a test that every pair resolves to a real section and every rendered list matches the data, and `record-style` checking a section that a reader could confuse with another has its list. research: rendering
      verify: DONE. record/confusables.py writes the list under both sections of each pair in research/confusables.json (224 pairs from the sweep's 282 collected lines; 58 duplicates or merged-away dropped); make record refuses a pair naming no section; tests/interactive/test_confusables.py; STYLE.md section 5 and record-style rule 12, 2026-10-01
