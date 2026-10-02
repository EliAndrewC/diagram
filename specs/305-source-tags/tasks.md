# Tasks - feature 305, source tags

Every task is tooling over the record and its registry: nothing a map draws or asserts changes, so each is
`research: rendering`. The classification reads the registry's own write-ups; no source is newly cited and no claim
reaches a map.

## Occasions

- none: no map, glyph or placement changes; the record site's labels and grouping are checked by tests and by eye (T09)

## Phase 1 - Setup

- [x] T01 Baseline: `make done` on unmodified main in a detached worktree (`/tmp/base305`); `make record` timed before any edit (constitution XIII, plan Performance bookends)
      research: rendering
      verify: DONE. Baseline make done green on unmodified main (291fa9433, specs only ahead of origin) in detached worktree /tmp/base305; make record before any edit 4.6-5.2 s over 3 runs, 2,687 pages (2026-10-02, wall clock)

## Phase 2 - Foundational

- [x] T02 The data: `research/source-tags.json` (FR-001, FR-002, FR-003: every region's cut-off and its logic in the period explanations, plan D3) and `research/source-sections.json` (FR-006, FR-007, plan D4)
      research: rendering
      verify: DONE. research/source-tags.json: 4 periods, 7 regions, 5 kinds + canon; every period explanation states every region's cut-off and why (test_the_real_vocabulary... asserts 1868/1895/1876/Ryukyu/Vietnam/Taiwan/1800/elsewhere/General); research/source-sections.json: FR-007's 8 sections, every vocabulary combination homed (test_every_combination...)
- [x] T03 `l7r/diagram/interactive/record/source_tags.py`: loaders, marker parse, homing, labels, the `Catalog`; every FR-010 refusal and every file refusal a failing test first in `tests/interactive/test_source_tags.py` (plan D1, D2, D6)
      research: rendering
      verify: DONE. record/source_tags.py: loaders, parse, home, labels, Catalog; 33 tests in test_source_tags.py incl. every FR-010 and file refusal; two refusals mutated off turned 2 tests red (written after the code, so the fire was proven by mutation)

## Phase 3 - User Stories 1 and 2: labels and sections (P1)

- [x] T04 [US1] [US2] The build: `citations.works_html` groups by section with labels (`l7r/diagram/interactive/citations.py`); `record/site.py` - entry pages with labels and the marker stripped, the registry index and the one-page Sources part grouped, the pager in grouped order, section ids claimed; the fixture record (`tests/_flat_record.py`) tagged; tests in `tests/interactive/test_record_site.py` (FR-008, FR-009; plan D5)
      research: rendering
      verify: DONE. works_html grouped by section with labels (h3 section, h4 work); site.py entry pages labeled, marker stripped, registry index and all.html grouped, pager in grouped order, section ids claimed; fixture record tagged; 3 new tests in test_record_site.py pass (fixture); real-record tests await T07
- [x] T05 [US1] The hover: `research/assets/record.js` gives `span.srctag[data-def]` the tooltip box; `research/assets/site.css` styles the chips and the section headings (FR-009; plan D5)
      research: rendering
      verify: DONE. record.js: span.srctag[data-def] gets the #fntip hover/focus, title dropped under scripts (kept as the no-script tooltip); site.css chips and section headings; looked at in T09

## Phase 4 - User Story 3: tags cannot go missing or drift (P2)

- [x] T06 [US3] `make reserve KIND=registry ... TAGS=` in `scripts/reserve-prefix.py` and `.claude/skills/diagram/Makefile`, the placeholder marker without it, with tests; the `source-applicability` contract's Tags rule and its derived vocabulary block, `make source-tags-contract`, and the test that fails while the block is stale; the docs (`research/CLAUDE.md`, `docs/research-doctrine.md`, `container-scripts/page-session-rules.md`, root `CLAUDE.md`) (FR-011, FR-012, FR-013; plan D7, D8, D9)
      research: rendering
      verify: DONE. reserve-prefix.py --tags (engine parser loaded by path), placeholder marker without it, Makefile TAGS= and source-tags-contract; test_reserve_prefix 9 passed incl. the new tags test; contract Tags rule + derived block, test holds it current; docs: research CLAUDE.md, research-doctrine, page-session-rules, root CLAUDE.md

## Phase 5 - User Story 4: every work tagged, the write-ups trimmed (P2)

- [x] T07 [US4] The migration under `specs/305-source-tags/migrate/`: `extract.py` batches, the 22 Sonnet classifications (rules: research R5 and plan D3), `apply.py` with R4's trim checks and R3's consistency lists, the lists worked by hand, every unsettled source settled by the vocabulary first; the build check passing with no exemption (FR-014, FR-015; SC-001; plan D10)
      research: rendering
      verify: DONE. extract.py 2,110 non-canon entries in 22 batches; 22 Sonnet classifications; apply.py: 0 bad tags, 0 unclassified, 910 trims passed R4, 1 refused (suido-ishizue-minuma, done by hand: deleted only 'without footnotes'); 35 unsettled + 98 late-date flags adjudicated by two Opus agents (41 changed); vocabulary gained fiction/rokugan and the undated/straddling rules (FR-002, FR-003); make record builds with no exemption (SC-001); report.md and results/ committed
- [ ] T08 [US4] The check: a stratified sample of at least 60 entries bundled (`make check-bundle KEY=`) and judged by `source-applicability`; every wrong tag and every repeated or lost limit fixed; any pattern swept across the registry (SC-004, SC-005; plan D11)
      research: rendering

## Phase 6 - Polish and landing

- [ ] T09 The site looked at in a browser - a question page's grouped works and a label's hover, the registry index, the single page - and SC-003 checked by a script over the built site; SC-006's figure (the total limits-paragraph length before and after)
      research: rendering
- [ ] T10 Verify and land: SC-002 as tests; `make record CHECK=1`; `make record` timed against T01; `make done` compared with T01's baseline; closing notes in `plan.md`; pushed
      research: rendering

## Dependencies

T01 -> T02 -> T03 -> T04 -> T05; T06 after T03; T07 after T02 and T04 (the build check judges the migration); T08 after
T07; T09 and T10 last. T05 and T06 can run in parallel with the classification batches of T07.
