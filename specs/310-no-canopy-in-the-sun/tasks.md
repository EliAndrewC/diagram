# Tasks - feature 310, no canopy tree in a yard's or bed's sun

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).

## Occasions

- placement-changed: copse - every copse crown now keeps out of a yard's or bed's sun ground (Inashiro)
- placement-changed: homestead grove - a farm grove's band crowns now keep out of every plot's sun ground (Kashikawa)
- gm-fix: inashiro - no canopy tree is exempt from the sun calculations; only bamboo may stand closer

## Phase 0 - baselines (SC-002, SC-004; constitution VI, XIII)

- [ ] T01 `310-start` bookend on the unmodified engine; the 24-seed cohort baseline in a detached worktree on the same commit
      research: rendering
      verify: the perf-log entry and the cohort count, recorded in research R3

## Phase 1 - the check, red (US1; FR-005)

- [ ] T10 [US1] D6: `tree_shade.trees_shading_plots` over every recorded tree (crowns, pines, willows) (the persimmon function retired into it), unit
      tests; `tests/gate/test_canopy_sun.py` over the five hamlets replaces `test_persimmon_sun.py` and is RED on today's pool
      (95, 78, 98, 10, 143); the cohort audit reads it
      research: rendering
      verify: the gate test's red run on the unmodified maps, quoted

## Phase 2 - the rule at every crown (US1; FR-001 to FR-004, FR-006)

- [ ] T20 [US1] D1: `CANOPY_SHADE_FT` in `tree_shade.py`, `PERSIMMON_SHADE_FT` renamed everywhere it is read
      research: rendering
      verify: `make quick` green; no `PERSIMMON_SHADE_FT` left (grep)
- [ ] T21 [US1] D2: `_sun_keepouts(bbox)` - the drawn plots and every placed bundle's, on a map keeping the sun corridor; unit
      tests (on, off, a bundle's plot before its record)
      research: rendering
      verify: `make test-file` on the keep-outs tests
- [ ] T22 [US1] D3: the belt's ranks, the clump crowns, the woods' stand and fringe, the woodland commons (throws and room grid),
      the scrub pines (recorded as `scrub_pines`) and the dike willows and the fruit dike's trees (thinned once the plots stand, `planted_trees`) take it;
      the culm marks, the coppiced mulberry and the tea dike's clipped hedge do not; a unit test
      per site and one that a culm mark may stand in a plot's sun
      research: rendering
      verify: `make test-file` on the groves and woods tests
- [ ] T23 [US1] D4: the copse's west lane applies to every mix; the unsupported comment removed. D5: the farm grove's strips
      recorded as seating preferences at `fit._yard_sun_conflict` / `_garden_sun_conflict`
      research: rendering
      verify: `make test-file` on the stands tests; the comments read
- [ ] T24 [US1] Inashiro regenerated (the copse), then Kashikawa (the farm groves): the gate test green on each; SC-004's figures
      after, against R2
      research: rendering
      verify: `make map` on each; the counts in research R3
- [ ] T25 [US1] The pool (`make maps`) and the cohort (`make cohort N=24`): the gate test green on all five, zero crowns in a
      plot's sun on every seed, no seed lost against T01's baseline
      research: rendering
      verify: the cohort's count against the baseline, in research R3

## Phase 3 - the record (US2; FR-007)

- [ ] T30 [US2] D7: the sun page states the one rule for every canopy tree, bamboo as the GM's tentative allowance with the
      bamboo page's tall madake, each decision's class; the persimmon bullet folded in; quote-check and record-format on it;
      entry-drift on the modals written from it
      research: rendering
      verify: `make record CHECK=1`; the agents' verdicts

## Closing

- [ ] T40 `make done` green; the owed reviews (`make verify`); `310-end` bookend and `make perf-report AGAINST=310-start`, any band
      explained; the closing bookend - the rendered Inashiro and Kashikawa re-read against research R0
      research: rendering
      verify: the gate, the review verdicts, the perf band
- [ ] T41 Raise with the GM: the bamboo allowance (the stands counted, the culm marks uncounted, the bamboo page's madake height)
      and SC-004's wood figures
      research: rendering
      verify: the closing report, through escalation-check
