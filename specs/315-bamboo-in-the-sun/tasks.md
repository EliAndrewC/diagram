# Tasks - feature 315, bamboo held out of a yard's or bed's sun

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- placement-changed: persimmon - on a grove farm the persimmon may stand in its own grove behind the house (Kashikawa)
Bamboo: no occasion - its rule refuses a mark or stand only in a plot's sun, and the regenerated pool draws none there (the gate test); its marks moved only with the farms re-seated round them (one-shot, observed 2026-10-02; method: `bamboo_marks` and `bamboo_stands` counted on the pool - Inashiro 25 marks, Kashikawa 64 and a stand, Kuwabata 50, Mizuguchi a stand, Sawada 52; Kuwabata's one household strip found every seat in a garden's sun and is no longer drawn).

## Phase 0 - baselines (constitution VI, XIII)

- [x] T01 `315-start` bookend on the unmodified engine; the 24-seed cohort baseline in a detached worktree at the same commit
      research: rendering
      verify: DONE. DONE (bookend). 315-start dev/perf-log 20261002T220503Z-315-start-diagram-inashiro; the cohort baseline follows in a detached worktree

## Phase 1 - the check, red (US1; FR-004, FR-005)

- [x] T10 [US1] D5: `tree_shade.bamboo_shading_plots` over `bamboo_marks` and `bamboo_stands`, unit tests; the gate test counts it with
      non-vacuity and the record-equals-drawn check (SC-002); red on a planted mark (SC-003); the cohort audit reads it; the new key
      classified in the overlap taxonomy and `_BARE_SKIP`
      research: rendering
      verify: DONE. DONE. bamboo_shading_plots over bamboo_marks and bamboo_stands (tests/settlement/test_tree_shade.py: a planted mark and stand found, SC-003); tests/gate/test_canopy_sun.py counts it with non-vacuity and recorded marks == drawn culm marks outside patterns (SC-002), green on the five; the cohort audit reads it; bamboo_marks classified in taxonomy and _BARE_SKIP

## Phase 2 - the rule at every bamboo site (US1; FR-001 to FR-004)

- [x] T20 [US1] D1: `tree_shade.BAMBOO_SHADE_FT` with its derivation; D2: `_sun_keepouts(bbox, reach)`; unit tests
      research: rendering
      verify: DONE. DONE. BAMBOO_SHADE_FT = 50 in tree_shade.py with its derivation (research R0/R2); _sun_keepouts(bbox, reach_ft) tested at a second reach (test_keepouts)
- [x] T21 [US1] D3: the culm marks take the sun boxes at bamboo's reach and are recorded in `bamboo_marks`; a unit test that a mark in a
      plot's sun is refused and one outside it drawn and recorded
      research: rendering
      verify: DONE. DONE. culm marks tested against krect + bamboo-reach sun boxes, every inked mark in bamboo_marks; test_homestead_woods: marks in a yard's sun refused, the rest recorded; pool regenerated, recorded == drawn on all five (gate test)
- [x] T22 [US1] D4: `household_bamboo` and `bamboo_seats` refuse a seat in a plot's sun at bamboo's reach; a unit test each
      research: rendering
      verify: DONE. DONE. household_bamboo refuses a strip in_the_sun (test_homesteads_287), bamboo_seats takes the sun boxes as rects; pool regenerated: Kuwabata's one strip refused at all six seats (0.3 ft from a garden's sun ground), every other stand unchanged

## Phase 2b - the regressions feature 310 shipped (amendment; constitution XIII, XIV)

- [x] T23 D7: `beds_sun_clear` on the south nudge; the grove farm's bed south of the front wall; `clear_east_of_beds`; unit tests
      research: rendering
      verify: DONE. cohort315j: 29/30, seeds 14, 15 and 906 pass
- [x] T24 D8: the persimmon's dooryard, grove seat, seat rake and settle-in-geometry; unit tests
      research: physical
      verify: DONE. cohort315j: seed 23 passes; pool persimmons match their rolls; sendai-igune-modelplan READ, quote-check and applicability answered
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
- [x] T25 D9 and D10: the walled-in gateway's fallbacks; the shared wells off the street's bends, the row street unjogged; unit tests
      research: rendering
      verify: DONE. cohort315j: seeds 19 and 903 pass, 29 of 30, seed 22 the one failure (failing on main before)

## Phase 3 - the record (US2; FR-002, FR-006)

- [x] T30 [US2] D6: the sun page's bamboo bullet rewritten - held at its own reach, the heights footnoted (new registry entries), yadake
      placed; `tree_shade.py`'s docstring and the `ksun` comment; the ThreshingYard and Garden modals; the record checks the gate owes
      research: physical
      verify: DONE. make record-owed UNANSWERED=1: no record check is owed; grep finds no page or modal calling bamboo exempt
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed

## Phase 4 - close

- [x] T40 `make done` green; `315-end` and `make perf-report AGAINST=315-start`, any band explained; the cohort at zero new failures;
      the closing re-read of the rendered Kuwabata and Kashikawa bamboo against R0
      research: rendering
      verify: DONE. make done green (incremental, 5 workers); perf band 1 (seed 47 +5.0% at 15 hh, total -16.7%) explained and confirmed consistent by perf-audit; cohort 54/54; Kuwabata and Kashikawa re-read at fit zoom against R0: bamboo north of its grove, every yard and bed clear
- [x] T41 Report to the GM through escalation-check: the finding (bamboo held, 50 ft, from the timber bamboos' height) and what moved
      research: rendering
      verify: DONE. escalation-check on the closing report: 3 KEEP, 1 REWRITE (seed 28 cut as process narrative), 1 CUT (the persimmon seat's regularity, no norm, left in the ledger); reported to the GM
