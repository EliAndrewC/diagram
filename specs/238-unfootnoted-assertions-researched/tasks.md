# Tasks - feature 238

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research notes: [`research.md`](research.md).

## Phase 1 - the inventory (FR-001, FR-002)

- [x] T01 the census that sizes the pass, from the pages rather than by hand
      research: procedure
      verify: DONE. DONE. research.md R1: every paragraph inside <main> on all 19 pages counted, and counted again for those carrying no footnote - 1,200 paragraphs, 864 with no footnote, 285 inline unsourced-class markers, per page. Derived from the pages, not by hand.
- [x] T02 `quote-check` batch A - `religion-and-death`, `vegetation`, `urban-features`: per section, every assertion carrying no footnote; report kept under `reader-reports/`
      research: procedure
      verify: DONE. DONE. Report kept verbatim at reader-reports/religion-vegetation-and-urban-features.md - 53 sections, 171 items, 34 with an inline marker. It also found that feature 232 named the right pages and not the worst sections on them.
- [x] T03 `quote-check` batch B - `cities/capitals`, `cities/fabric`, `cities/government`, `cities/defenses`
      research: procedure
      verify: DONE. DONE. reader-reports/the-city-pages.md - 72 sections, 203 items, 59 inline markers and 12 roster-only. Confirms the nine-claim run in the capitals class-scaling bullets that 232 flagged.
- [x] T04 `quote-check` batch C - `water`, `fields`, `cities/river-cities`, `cities/hinterland`, `cities/sizing`
      research: procedure
      verify: DONE. DONE. reader-reports/water-fields-and-the-river-cities.md - 57 sections, 153 items, 51 with a marker. Named the wharf section (12 items, one footnote) as the thinnest-sourced on those pages.
- [x] T05 `quote-check` batch D - `homesteads`, `archetypes`, `buildings`, `settlements`, `towns`, `ways`, `presentation`
      research: procedure
      verify: DONE. DONE. reader-reports/homesteads-buildings-and-the-hamlet-pages.md - 100 sections, 168 items, 67 with a marker. presentation.html returned ZERO and settlements.html one, both as R1 predicted.
- [ ] T06 the inventory built from those reports: every named sentence given one of the four dispositions, in `research.md` R3
      research: procedure
      verify:

## Phase 2 - page by page (FR-003, FR-004, FR-005, FR-006)

Each task: the page's `CITE` entries read by `source-reader`, its notes written in the three forms, its
inline `(unsourced)` markers retired where a note replaces them, its new keys registered with both
write-ups, any unreadable document appended to `TO-DOWNLOAD.md` Part 4.

- [ ] T07 `religion-and-death.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T08 `vegetation.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T09 `urban-features.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T10 `cities/capitals.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T11 `buildings.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T12 `archetypes.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T13 `homesteads.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T14 `water.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T15 `fields.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T16 `cities/fabric.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T17 `cities/government.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T18 `cities/defenses.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T19 `cities/river-cities.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T20 `ways.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T21 `towns.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T22 `cities/hinterland.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T23 `cities/sizing.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T24 `settlements.html`
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T25 `presentation.html`
      research: rendering
      verify:

## Phase 3 - the checks the changed material owes (FR-007, FR-008)

- [ ] T26 `record-format` over every changed page; findings applied
      research: rendering
      verify:
- [ ] T27 `source-applicability` over every new registry key; findings applied
      research: rendering
      verify:
- [ ] T28 every `entry-drift` pair `scripts/_entry_owed.py` names answered - the agent run and the modal rewritten, or one recorded sweep reason
      research: rendering
      verify:

## Phase 4 - the caravan inn (FR-011)

- [ ] T29 the reader's verdict on Japanese post-station inn story counts recorded in `research.md` R2, whichever way it came back
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:
- [ ] T30 the `inn()` glyph loses its second story and its docstring says so; `towns.html` states a single-story caravan inn with no deviation label
      research: physical
      - [ ] research pass  - [ ] source-reader confirmed  - [ ] quote-check confirmed  - [ ] source-applicability confirmed  - [ ] recorded and cited
      verify:

## Phase 5 - closing (FR-005, FR-010)

- [ ] T31 `TO-DOWNLOAD.md` Part 4 carries every document this pass could not read, appended at the end, each with a clickable link
      research: rendering
      verify:
- [ ] T32 the closing report: what the inventory came to, the contradictions corrected, and what is left open with the searches that failed
      research: rendering
      verify:
- [ ] T33 `make page-check` green, `make done` green, the push clean
      research: rendering
      verify:
