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
- [x] T06 the inventory built from those reports: every named sentence given one of the four dispositions, in `research.md` R3
      research: procedure
      verify: DONE. DONE. research.md R6: a disposition for every one of the 695 items - a rule (the readers' brief already excluded conventions and decisions, so the default is CITE) plus 51 individually triaged LOW items, enumerated by class. R6a records that the table's numbers are the readers' own stated splits, not a parse, after a peer found a hook had silently altered a counting command.

## Phase 2 - the items that need no new reading (FR-012)

The amendment of 2026-09-13 cut this phase by ITEM rather than by page: every item needing no new
`source-reader` pass is worked here, on all nineteen pages, and the per-page tasks for the `CITE` items
that DO need a reading were moved to the successor and removed from this file.

- [x] T07 every bare inline unsourced-class marker in body prose converted to a note at its own assertion, on every page
      research: rendering
      verify: DONE. DONE. 142 bare inline markers converted across sixteen pages. Where the marker recorded a reason the note carries it verbatim; where it recorded none the note says no query of its own was run, rather than claiming a search nobody made. page-check green, 776 passed.
- [x] T08 the roster-disclosure sections worked - where a section's `Sources:` line records a dated search while the body sentence stands bare
      research: rendering
      verify: DONE. DONE. A scan found 61 sections whose Sources roster records a dated search while the body stood bare. The 142 marker conversions covered most; the six sections left carrying a disclosure with NO footnote anywhere in them were worked individually - the lotus share, the yamen predecessor-veneration practice, the sluice duty cycle, the sluice mechanism, Edo's moats blooming green, and the no-subsumed-crown rule (a grounds note: it describes what the MAP removes, not how a stand grows).
- [x] T09 every defect the readings of 2026-09-12 and 2026-09-13 surfaced, corrected or recorded as declined
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. Every defect from both readings corrected: the Wagner workforce misread and the two-site argument built on it, a quotation readable on no page the note points at, a hearth called open that the source calls insulated, a truncation with no ellipsis, a quotation of a damaged text layer (twice - the degree signs and then the rl the first fix defended), an inference presented as a quotation's content, the mis-scoped Korean mean, the missing Japan-comparability limit, and a claim that did not survive its source swap. research.md R4-R5g.
- [x] T24 `settlements.html` closed - the inventory found one item, and it restates footnoted canon
      research: rendering
      verify: DONE. DONE. The reader found one item and said it restates footnoted setting canon from the section above it - NOT AN ASSERTION in R6, nothing owed, no edit needed.
- [x] T25 `presentation.html` closed - the inventory found none, the page being about how the sheet is drawn
      research: rendering
      verify: DONE. DONE. The reader read all six sections and found ZERO items: every one is about how the sheet is drawn. R1 predicted it (42 paragraphs, none with a footnote, none owing one) and the reading confirmed it.

## Phase 3 - the checks the changed material owes (FR-007, FR-008)

- [ ] T26 `record-format` over every changed page; findings applied
      research: rendering
      verify:
- [x] T27 `source-applicability` over every new registry key; findings applied
      research: rendering
      verify: DONE. DONE. Three new registry keys this feature: okabe-hatago-jawiki, lai-2003-daoism-today, lagerwey-1988-taoist-lineages. All three judged APPLICABLE-WITH-LIMITS; ten write-up corrections applied, including a palanquin claim that was the session's own inference stated as fact, and a mirror link now disclosed as one with its DOI recorded.
- [x] T28 every `entry-drift` pair `scripts/_entry_owed.py` names answered - the agent run and the modal rewritten, or one recorded sweep reason
      research: rendering
      verify: DONE. DONE. 27 pairs, every one a label-only conversion: a marker left the prose and a note arrived at the assertion, with no finding moved in any of them. None touches the sections where a finding DID move (the Wagner iron work, the Daoism swap, the inn) because no modal is written from those. Discharged with one recorded ENTRY_DRIFT_OK sweep reason at push, which is the case feature 234 provides it for.

## Phase 4 - the caravan inn (FR-011)

- [x] T29 the reader's verdict on Japanese post-station inn story counts recorded in `research.md` R2, whichever way it came back
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. research.md R2a records the verdict whichever way it fell: a two-story Japanese post-station inn IS attested (Okabe-juku, c.1836), but a hatago has no cart yard and no long stable, so it does not touch the analogue the GM's condition named. quote-check on fn-26 returned PARTIAL and the date and post-station identity are now quoted rather than glossed.
- [x] T30 the `inn()` glyph loses its second story and its docstring says so; `towns.html` states a single-story caravan inn with no deviation label
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] quote-check confirmed  - [x] source-applicability confirmed  - [x] recorded and cited
      verify: DONE. DONE. The inn() glyph lost its lower-eave band and upper-story lattice windows; the three windows moved to mid-wall as the openings of the one wall it has. Docstring says single-story and names where the confusion came from. towns.html asserts a single-story caravan inn with no deviation label. No live map moves - the only callers are the frozen legacy towns.

## Phase 5 - closing (FR-005, FR-010)

- [x] T31 `TO-DOWNLOAD.md` Part 4 carries every document this pass could not read, appended at the end, each with a clickable link
      research: rendering
      verify: DONE. DONE. Part 4 carries the honest result: nothing to add. Every item 238 worked was the no-new-reading class, so none of it needed a document the GM lacks - the searches were already done and what was missing was the label's position. The note points at feature 242 as where documents will start appearing.
- [x] T32 the closing report: what the inventory came to, the contradictions corrected, and what is left open with the searches that failed
      research: rendering
      verify: DONE. DONE. closing-report.md: what shipped, the numbers, the two findings that changed an argument, the three defects the checks caught in this session's own work, what spec-fidelity refused and why, and what is left open - about 600 CITE items that were never searched rather than searched and failed, fifty-one redundant roster lines deferred by volume, and the two items only the GM can settle.
- [ ] T33 `make page-check` green, `make done` green, the push clean
      research: rendering
      verify:
