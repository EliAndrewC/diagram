# Tasks - feature 310, no canopy tree in a yard's or bed's sun

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- placement-changed: copse - every copse crown now keeps out of a yard's or bed's sun ground (Inashiro)
- placement-changed: homestead grove - a farm grove's band crowns now keep out of every plot's sun ground (Kashikawa)
- gm-fix: inashiro - no canopy tree is exempt from the sun calculations; only bamboo may stand closer

## Phase 0 - baselines (SC-002, SC-004; constitution VI, XIII)

- [x] T01 `310-start` bookend on the unmodified engine; the 24-seed cohort baseline in a detached worktree on the same commit
      research: rendering
      verify: DONE. 310-start dev/perf-log 20261002T134028Z-310-start; cohort base 28/30 on main (seeds 5 and 903, both traced to the persimmon push and fixed here)

## Phase 1 - the check, red (US1; FR-005)

- [x] T10 [US1] D6: `tree_shade.trees_shading_plots` over every recorded tree (crowns, pines, willows) (the persimmon function retired into it), unit
      tests; `tests/gate/test_canopy_sun.py` over the five hamlets replaces `test_persimmon_sun.py` and is RED on today's pool
      (95, 78, 98, 10, 143); the cohort audit reads it
      research: rendering
      verify: DONE. tests/gate/test_canopy_sun.py red on all five (95, 78, 98, 10, 143), green after; trees_shading_plots in the cohort audit

## Phase 2 - the rule at every crown (US1; FR-001 to FR-004, FR-006)

- [x] T20 [US1] D1: `CANOPY_SHADE_FT` in `tree_shade.py`, `PERSIMMON_SHADE_FT` renamed everywhere it is read
      research: rendering
      verify: DONE. CANOPY_SHADE_FT in tree_shade.py; no PERSIMMON_SHADE_FT left (grep)
- [x] T21 [US1] D2: `_sun_keepouts(bbox)` - the drawn plots and every placed bundle's, on a map keeping the sun corridor; unit
      tests (on, off, a bundle's plot before its record)
      research: rendering
      verify: DONE. _sun_keepouts with tests (off, drawn plots, bundles, bbox) in tests/settlement/test_keepouts.py
- [x] T22 [US1] D3: the belt's ranks, the clump crowns, the woods' stand and fringe, the woodland commons (throws and room grid),
      the scrub pines (recorded as `scrub_pines`) and the dike willows and the fruit dike's trees (thinned once the plots stand, `planted_trees`) take it;
      the culm marks, the coppiced mulberry and the tea dike's clipped hedge do not; a unit test
      per site and one that a culm mark may stand in a plot's sun
      research: rendering
      verify: DONE. belt ranks, clump crowns (not the culm marks), woods, commons, scrub_pines, planted_trees thinned; tests in test_keepouts, test_homestead_woods
- [x] T23 [US1] D4: the copse's west lane applies to every mix; the unsupported comment removed. D5: the farm grove's strips
      recorded as seating preferences at `fit._yard_sun_conflict` / `_garden_sun_conflict`
      research: rendering
      verify: DONE. copse west lane for every mix; grove strips recorded as seating preferences (fit docstrings, dispersed, consts)
- [x] T24 [US1] Inashiro regenerated (the copse), then Kashikawa (the farm groves): the gate test green on each; SC-004's figures
      after, against R2
      research: rendering
      verify: DONE. Inashiro and Kashikawa regenerated, gate test green; SC-004: copse clumps fell (the figures current at the close are research.md R2a), wood drawn = rolled, belts unchanged
- [x] T25 [US1] The pool (`make maps`) and the cohort (`make cohort N=24`): the gate test green on all five, zero crowns in a
      plot's sun on every seed, no seed lost against T01's baseline
      research: rendering
      verify: DONE. make maps (five regenerated, gate test green); make cohort N=24 30/30 (903 and 5 fixed)

## Phase 3 - the record (US2; FR-007)

- [x] T30 [US2] D7: the sun page states the one rule for every canopy tree, bamboo as the GM's tentative allowance with the
      bamboo page's tall madake, each decision's class; the persimmon bullet folded in; quote-check and record-format on it;
      entry-drift on the modals written from it
      research: rendering
      verify: DONE. sun page rewritten; quote-check, record-format and entry-drift applied (Garden, ThreshingYard, Windbreak, Persimmon, HomesteadGrove)

## Closing

- [ ] T40 `make done` green; the owed reviews (`make verify`); `310-end` bookend and `make perf-report AGAINST=310-start`, any band
      explained; the closing bookend - the rendered Inashiro and Kashikawa re-read against research R0
      research: rendering
      verify: the gate, the review verdicts, the perf band
- [ ] T41 Raise with the GM: the bamboo allowance (the stands counted, the culm marks uncounted, the bamboo page's madake height)
      and SC-004's wood figures
      research: rendering
      verify: the closing report, through escalation-check
