# Tasks - 229 the rule files retire into the research pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Rulebook: [`migration-rules.md`](migration-rules.md).
A task is `research: procedure` (how the work is done), `research: rendering` (the record's form, a convention),
or `research: physical` (a claim about how a place was built, farmed or lived in that moves onto a page without a
footnote - it carries the five boxes and is not ticked until they are).

## Phase 0-1 - the spec, the baseline, the contradictions

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any page is edited (up to five rounds)
      research: procedure
      verify: DONE. FAITHFUL at round 5 of 5. Each round found something new and smaller: 1 (six: FR-004's bound, FR-009's additions, the README, the exhibits' prose, the derived surface, the order), 2 (FR-002a; `specs/` exemption), 3 (FR-001 derived), 4 (bare-basename references; a test path), 5 (FAITHFUL; two R1 rows from its aside). Not the persistent-misunderstanding pattern the cap exists to end - the same shape as feature 169's round 3
- [x] T03 FR-001 on the existing pages: rows 1 and 2 of R1 are owned by the writers of `water.html` (T08) and `urban-features.html` (T13); R1 opened with 32 rows, each with its owner
      research: rendering
      verify: DONE. R1 opened with 32 rows (30 from the audits + 2 from the round-5 aside), each with the truth it resolves to and its owner; rows 1 and 2 handed to the water and urban-features writers so no page had two editors.
- [x] T02 baseline: `make page-check` green on the unmodified clone; the last green `make done` on main noted (XIII)
      research: procedure
      verify: DONE. `make page-check` on the clone at f4c0da29 (main b87b88aa + the claim commit): 684 passed, 3 warnings, 8.0 s, "page-check green"; the finished-run hook reported main's last `make done` green 6 h before the feature began

## Phase 2 - the writers (FR-002, FR-003, FR-004, FR-006), one per target page, each followed by the session's spot check

- [x] T04 `homesteads.html` <- `homesteads.md`
      research: rendering
      verify: DONE. 12 decisions mapped (name-informed siting, the legacy-pool shading exemption, the headman's kura, the geomantic pond, the byre forms, the phantom tail, the compactness limit, the twin calibration, the position-seeded kura, the east nudge, the garden-size ruling, the big-glyph wing), 9 specifications, 7 FN-PENDING. Found and resolved two internal contradictions the audit had not: the rule file said both that the headman always has a kura and that he carries none (the engine forces it), and its byre footprint arithmetic was impossible (31x21 ft is not 16 m2 - a 1 px = 2 ft residue; the engine draws 16 by 11 ft).
- [x] T05 `fields.html` <- `fields.md`
      research: rendering
      verify: DONE. 12 decisions, 6 specifications, 10 FN-PENDING; R1 21 closed by separating the leveled cell (~0.05 acre) from the older parcel grain (0.10 / 0.19), all inside the page's own 0.02-0.25 acre band.
- [x] T06 `archetypes.html` <- `archetypes.md` (FR-001: the Shunde claim, the density label)
      research: rendering
      verify: DONE. 8 decisions (the withdrawn clustering check, the perpendicular junction measure, the mosaic no-check record, the crown density, edge grazing, additive-vs-subtractive, the sixth pass, split_gap), 2 specifications for the two unscripted archetypes, 5 FN-PENDING; the struck Shunde figure not revived, the density left the page's GUESS.
- [x] T07 `vegetation.html` <- `vegetation.md` (FR-001: bamboo 14 ft; the belt's three roles heading)
      research: rendering
      verify: DONE. 9 decisions - the four prose sections became two new entries carrying the GM's 2026-08-29 hook ruling and the belt-continuity limitation - 7 specifications, 11 FN-PENDING; the three-groves heading written for the map's copse class; bamboo 14 ft.
- [x] T08 `water.html` <- `water.md` + the swept-bend entry from `presentation.md`
      research: rendering
      verify: DONE. 15 decisions across four new entries (the drainage bearing, the moat's current, the discharge end, the swept bend from presentation.md), 7 specifications, 4 FN-PENDING; the head-race states 6.0 ft with the engine's reason.
- [x] T09 NEW `ways.html` + `citations/ways.html` <- `ways.md`
      research: rendering
      verify: DONE. research/ways.html and its citations page created: 5 decisions (solve a crossing, the itabashi correction, the useless-plank census, the Rokugan canal canon, the lane-width absence), 7 specifications, 10 FN-PENDING.
- [x] T10 NEW `presentation.html` + `citations/presentation.html` <- `presentation.md`
      research: rendering
      verify: DONE. research/presentation.html and its citations page created: 11 decisions, 14 specifications, 0 FN-PENDING (the page is conventions and says so; its one physical claim went to water.html). The crop advisory was dropped with its reason - a generation-time diagnostic that prints a hint and never fails.
- [x] T11 `religion-and-death.html` <- `religion-and-death.md`
      research: rendering
      verify: DONE. 11 decisions - the district catchment first, since research/archetypes.html cites it - 12 specifications including ONE tier schedule replacing four near-duplicates, 24 FN-PENDING. Found: the page asserted a 76-120 ft arch gradient the GM's 2026-07-27 threshold ruling had overturned; resolved to the ruling.
- [x] T12 `towns.html` <- `towns.md`
      research: rendering
      verify: DONE. 8 decisions (the manor-glyph ruling first), 16 specifications - the town tier's whole composition, which no generator encodes - 4 FN-PENDING; the retired scale factor and the wrong canvas did not move.
- [x] T13 `urban-features.html` <- `urban-features.md`
      research: rendering
      verify: DONE. 15 decisions, 10 specifications, 3 FN-PENDING; the bell-and-drum tower's DECISION corrected to 36 / 30 ft (the page had stated the retired 70 / 60 beside the corrected finding), the seam's 60 ft moved with no identifier.
- [x] T14 `cities/defenses.html` + `cities/government.html` <- the two rule files (FR-001: the page's GUESS labels win)
      research: rendering
      verify: DONE. 6 decisions, 20 specifications across the two pages, 9 FN-PENDING; R1 5 applied in full - every contested figure carries the page's own GUESS or unsourced label rather than the rule file's confidence. Found: the ring-road corridor is width/2 + 21 px in the engine, not the rule file's +17.
- [x] T15 `cities/fabric.html` <- `fabric.md` (FR-001: the frontage-tax rationale does not move)
      research: rendering
      verify: DONE. 5 decisions, 17 specifications - the largest specification load in the sweep - and the fire-watch narrative written as a finding with 8 FN-PENDING; the frontage-tax rationale did not move (R1 6) and the terrace specification carries the page's 18 ft departure (R1 32).
- [x] T16 `cities/hinterland.html` + `cities/river-cities.html` <- the two rule files + `cities.md`'s farmland rulings (FR-001: the junction hydrology reaches river-cities)
      research: rendering
      verify: DONE. 7 decisions, 13 specifications across the two pages, 9 FN-PENDING; R1 12 closed - the junction hydrology now exists on the page whose title advertises it. Found: the two rule files used the sediment argument in opposite directions; resolved toward the ruled reading.
- [x] T17 NEW `cities/sizing.html` + `citations/cities/sizing.html`; `cities/capitals.html` <- `sizing.md`, `capitals.md`, `cities.md`'s population rule (FR-001: the extramural share, the settled constants)
      research: rendering
      verify: DONE. research/cities/sizing.html created; capitals edited. 6 decisions, 13 specifications, 2 FN-PENDING; R1 8, 9, 20 and the capitals half of 30 applied. Found: the Tango dead-ground pocket's three figures did not reconcile - resolved toward the pixel figures at 3 ft/px.
- [x] T18 NEW `settlements.html` + `citations/settlements.html` <- `settlements.md` + `cities.md`'s tier definition and intake questions (FR-001: houses per household 0.85-1.05)
      research: rendering
      verify: DONE. research/settlements.html created: 6 decisions, 9 specifications, 0 FN-PENDING (setting canon, GM rulings and this project's measurements). R1 7 closed - the page states the engine's 0.85-1.05 band and the 16-of-17-at-1.00 measurement, and the GM's 'at least 50 houses' reads as the floor it was.
- [x] T19 `research.md` R2 (decision map), R3 (specification map), R7 (dropped stale content) written from the writers' reports; every audit D item accounted for; `make page-check` green over all pages
      research: procedure
      verify: DONE. research.md R2/R3 written from all fourteen writer reports; every audit D item accounted for, every dropped B item carries its reason.

## Phase 3 - the research pass on physical claims that move (FR-005)

- [ ] T20 Chinese settlement form: Knapp; North vs South China village sizes; villages per 100 km² (from `homesteads.md`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T21 the degraded south-China commons past the grove (from `vegetation.md`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T22 the swept-bend channel radius, Leopold and Wolman (from `presentation.md`, landing on `water.html`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T23 bridges and lanes: the deck's landing (scour, bearing length), the lane vehicle (wheelbarrow, porter; the 2026-08-27 reads), the plank bridge's name (from `ways.md`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T24 funerary: the district catchment (Buck; danka; ryobosei), the swept ground (keidai, sando), the size memo's five named works, the temple neighborhood's economy, the village shrine at the water-mouth (from `religion-and-death.md`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T25 the fire-watch narrative (hinomi-yagura, Meireki, the jin'ya case, wanghuolou) and the guan-xiang suburb's 10-40 structures (from `fabric.md`, `towns.md`, `hinterland.md`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T26 the junction hydrology (an offtake and bedload; a confluence's merging angle) and the sizing model's civic and circulation shares (from `river-cities.md`, `sizing.md`)
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
- [ ] T27 every `FN-PENDING` resolved to a footnote or an absence note; new keys' write-ups in `SOURCES.html`; `make citations`; `make glossary` with the writers' terms; `research.md` R4, R5
      research: rendering

## Phase 4 - the tree (FR-007, FR-008, FR-009)

- [x] T28 re-point every file the SC-001 grep finds - docs, agent, pool and legacy notes and gens, `wip/`, tests' docstrings; `buildings.md` and `programs.md` incl. the three stale Mode A pointers (XIV); `research/CLAUDE.md`'s new section; `research.md` R6
      research: procedure
      verify: DONE. DONE. Every pointer the SC-001 grep finds re-pointed - docs, the agent files, pool and legacy notes and gens, wip/, test docstrings, buildings.md and programs.md. research/CLAUDE.md carries the new 'ONE home per topic' section; research.md R6 written. Verified: tests/interactive/test_record.py green (47 passed with test_docs_match_the_mechanism.py), which is the grep as a gated rule - by path and by bare basename, with its own self-test.
- [x] T29 engine comments and docstrings re-pointed (comment-only; the `Entry:` tag in `greenery.py` to the vegetation heading); the stale `urban_fixtures.py:74` figure (XIV)
      research: procedure
      verify: DONE. DONE. Engine comments and docstrings re-pointed, comment-only so the route stays DIRECT; greenery.py's Entry tags name research/vegetation.html and research/homesteads.html headings; urban_fixtures.py's drum-tower figure now cites the record's 30-45 ft band at research/urban-features.html; boards.py points at cities/fabric.html and urban-features.html. Verified: every research/*.html path in l7r/ resolves to a file on disk (zero missing).
- [ ] T30 delete `settlements.md`, `settlements/`, `settlements/cities/`; `test_record.py` gains the retired-file rule with its self-test; `test_docs_match_the_mechanism.py`'s list; `make test-file` on both; `make page-check`; `make quick`
      research: procedure

## Phase 5 - verification and landing (FR-010)

- [ ] T31 `quote-check` + `record-format` on every changed and new page (one pair per page, background); findings resolved; verdicts recorded here per page
      research: procedure
- [ ] T32 the four new pages opened in a browser from disk: glossary hover, citations hover, links (SC-006)
      research: rendering
- [ ] T33 `make done` green (detached); commit; `sync-with-main.sh done`; the closing report with the README correction text, the Mode A rulings question, and any claim left a guess
      research: procedure
