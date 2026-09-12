# Tasks - 229 the rule files retire into the research pages

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Rulebook: [`migration-rules.md`](migration-rules.md).
A task is `research: procedure` (how the work is done), `research: rendering` (the record's form, a convention),
or `research: physical` (a claim about how a place was built, farmed or lived in that moves onto a page without a
footnote - it carries the five boxes and is not ticked until they are).

## Phase 0-1 - the spec, the baseline, the contradictions

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any page is edited (up to five rounds)
      research: procedure
      verify: DONE. FAITHFUL at round 5 of 5. Each round found something new and smaller: 1 (six: FR-004's bound, FR-009's additions, the README, the exhibits' prose, the derived surface, the order), 2 (FR-002a; `specs/` exemption), 3 (FR-001 derived), 4 (bare-basename references; a test path), 5 (FAITHFUL; two R1 rows from its aside). Not the persistent-misunderstanding pattern the cap exists to end - the same shape as feature 169's round 3
- [ ] T03 FR-001 on the existing pages: rows 1 and 2 of R1 are owned by the writers of `water.html` (T08) and `urban-features.html` (T13); R1 opened with 32 rows, each with its owner
      research: rendering
- [x] T02 baseline: `make page-check` green on the unmodified clone; the last green `make done` on main noted (XIII)
      research: procedure
      verify: DONE. `make page-check` on the clone at f4c0da29 (main b87b88aa + the claim commit): 684 passed, 3 warnings, 8.0 s, "page-check green"; the finished-run hook reported main's last `make done` green 6 h before the feature began

## Phase 2 - the writers (FR-002, FR-003, FR-004, FR-006), one per target page, each followed by the session's spot check

- [ ] T04 `homesteads.html` <- `homesteads.md`
      research: rendering
- [ ] T05 `fields.html` <- `fields.md`
      research: rendering
- [ ] T06 `archetypes.html` <- `archetypes.md` (FR-001: the Shunde claim, the density label)
      research: rendering
- [ ] T07 `vegetation.html` <- `vegetation.md` (FR-001: bamboo 14 ft; the belt's three roles heading)
      research: rendering
- [ ] T08 `water.html` <- `water.md` + the swept-bend entry from `presentation.md`
      research: rendering
- [ ] T09 NEW `ways.html` + `citations/ways.html` <- `ways.md`
      research: rendering
- [ ] T10 NEW `presentation.html` + `citations/presentation.html` <- `presentation.md`
      research: rendering
- [ ] T11 `religion-and-death.html` <- `religion-and-death.md`
      research: rendering
- [ ] T12 `towns.html` <- `towns.md`
      research: rendering
- [ ] T13 `urban-features.html` <- `urban-features.md`
      research: rendering
- [ ] T14 `cities/defenses.html` + `cities/government.html` <- the two rule files (FR-001: the page's GUESS labels win)
      research: rendering
- [ ] T15 `cities/fabric.html` <- `fabric.md` (FR-001: the frontage-tax rationale does not move)
      research: rendering
- [ ] T16 `cities/hinterland.html` + `cities/river-cities.html` <- the two rule files + `cities.md`'s farmland rulings (FR-001: the junction hydrology reaches river-cities)
      research: rendering
- [ ] T17 NEW `cities/sizing.html` + `citations/cities/sizing.html`; `cities/capitals.html` <- `sizing.md`, `capitals.md`, `cities.md`'s population rule (FR-001: the extramural share, the settled constants)
      research: rendering
- [ ] T18 NEW `settlements.html` + `citations/settlements.html` <- `settlements.md` + `cities.md`'s tier definition and intake questions (FR-001: houses per household 0.85-1.05)
      research: rendering
- [ ] T19 `research.md` R2 (decision map), R3 (specification map), R7 (dropped stale content) written from the writers' reports; every audit D item accounted for; `make page-check` green over all pages
      research: procedure

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

- [ ] T28 re-point every file the SC-001 grep finds - docs, agent, pool and legacy notes and gens, `wip/`, tests' docstrings; `buildings.md` and `programs.md` incl. the three stale Mode A pointers (XIV); `research/CLAUDE.md`'s new section; `research.md` R6
      research: procedure
- [ ] T29 engine comments and docstrings re-pointed (comment-only; the `Entry:` tag in `greenery.py` to the vegetation heading); the stale `urban_fixtures.py:74` figure (XIV)
      research: procedure
- [ ] T30 delete `settlements.md`, `settlements/`, `settlements/cities/`; `test_record.py` gains the retired-file rule with its self-test; `test_docs_match_the_mechanism.py`'s list; `make test-file` on both; `make page-check`; `make quick`
      research: procedure

## Phase 5 - verification and landing (FR-010)

- [ ] T31 `quote-check` + `record-format` on every changed and new page (one pair per page, background); findings resolved; verdicts recorded here per page
      research: procedure
- [ ] T32 the four new pages opened in a browser from disk: glossary hover, citations hover, links (SC-006)
      research: rendering
- [ ] T33 `make done` green (detached); commit; `sync-with-main.sh done`; the closing report with the README correction text, the Mode A rulings question, and any claim left a guess
      research: procedure
