# Tasks: Retire the post-placement check battery

**Input**: [`spec.md`](spec.md), [`plan.md`](plan.md) | **Feature**: 166-retire-the-check-battery

Every task carries `research: rendering | physical | procedure` (constitution v2.12.0). Most of this feature
is code movement and is `procedure`. The FR-005 confirmations are `physical` - they are about whether a
historical finding still has a home - and carry the three boxes.

## Phase 0 - baseline (blocking)

- [ ] **T01** Baseline on UNMODIFIED code: `git worktree add --detach /tmp/base166 HEAD`, `make done` there,
      record in `research.md`. Check each worktree failure against the clone before calling it pre-existing.
      Then `make perf LABEL=166-start` and fill the plan's bookend table.
      research: procedure

## Phase 1 - cut the generator's dependency (US1, P1) - THE ONLY PART THAT CAN MOVE A MAP

- [x] **T02** Lift `farmhouses_reach_a_way`'s reach measure out of the check into a predicate `hamletgen`
      owns, with unit tests. Do NOT re-derive it: `driver.py` records that a hand-rolled reach measure was
      wrong on five of six seeds and never read zero. Lift the check's own body.
      verify: `make quick`
      research: procedure
- [x] **T03** Replace the ladder's accept criterion (`len(f2) <= len(failures)` over the gate's whole
      failure list). State what replaces it AND its reasoning at the point of change - a global quality
      proxy is being exchanged for a local one, and that is a decision, not a refactor.
      research: procedure
- [ ] **T04** `hamletgen` imports nothing from `check_village`. Prove it: a test that the module graph is
      clean, not a grep in a commit message.
      **MOVED TO PHASE 4** (discovered at T03 by reading the consumers, which is what the ordering is for):
      the ladder no longer NEEDS the gate, but `generate()` still calls it to populate `Report.failures`
      and `Report.fail_lines`, and those have live consumers - `tools/mapcheck.py`'s tripwire and
      `tools/cohort_audit.py`. Both are battery apparatus and die with it, so cutting the import is part of
      the Phase 4 deletion rather than a Phase 1 task. Recorded rather than silently reordered.
      verify: `make quick`
      research: procedure
- [ ] **T05** Re-roll all five live hamlets; compare each manifest byte-for-byte against before. DIAGNOSE
      any difference in writing before Phase 2 starts. If a map moved, a `settlement-review` is owed and
      this is the task that owes it.
      measure: `make maps`
      research: procedure

## Phase 2 - classify all 147 (US2, P1)

- [ ] **T06** Build the destination ledger: one row per check - owning placer (from feature 163's
      `surviving-checks.md`), destination (placer unit test / seed-sweep / static code test / drop), and for
      a drop the covering test or the reason. Zero unaccounted for. Nothing is deleted in this task.
      research: procedure

## Phase 3 - migrate by owning placer (US2, P1). The battery KEEPS RUNNING throughout

Each task below: write the replacement, PROVE IT FIRES against the unfixed placer, then delete the checks in
that batch. A batch is not done until its replacements have each been seen red.

- [ ] **T07** Batch `water_frame` + `field` + `sink` - the water and field engine's checks.
      verify: `make quick`
      research: procedure
- [ ] **T08** Batch `seat` + `homesteads` - the cluster and farmhouse placers.
      verify: `make quick`
      research: procedure
- [ ] **T09** Batch `track` + `web` - the way network.
      verify: `make quick`
      research: procedure
- [ ] **T10** Batch `appurtenances` + `notice` - yards, gardens, wells, the board.
      verify: `make quick`
      research: procedure
- [ ] **T11** Batch `hinterland` + `woodland` + `windbreak` + `bamboo` - ground cover and the belts.
      verify: `make quick`
      research: procedure
- [ ] **T12** Batch `crossings` + `frame` - bridges, and the frame the crop holds open.
      verify: `make quick`
      research: procedure
- [ ] **T13** Batch `finish` - the terminal stage, which feature 163 measured as the last-changer for 75%
      of the battery. Expect this to be the batch that reveals whether `finish` genuinely MOVES features or
      merely writes them out; record which, because it is the open question from 163's R10b.
      verify: `make quick`
      research: procedure
- [ ] **T14** The 17 completeness ratchets (they read no manifest key) become STATIC tests over the code -
      a new feature type added without a registry entry must still turn something red.
      verify: `make quick`
      research: procedure
- [ ] **T15** The whole-map properties become ONE seed-sweep test over a documented seed set, in
      `tests/full/`. Say in its docstring which properties it carries and why a seed sweep is the right
      home for them.
      research: procedure
- [ ] **T16** The URBAN checks (39 segments carrying an `if URBAN:` branch): no placer exists to migrate
      them into, so each is deleted after its rule is confirmed to have a documented home (T18).
      research: procedure

## Phase 4 - delete the apparatus (US3, P2)

- [ ] **T17** Delete `check_village/`, `tests/check_village/`, `tests/gate/`, the 105 frozen fixtures, the
      Makefile targets, the `_invocation` row and the pool sweep. Then prove no file in the tree references
      any of it. Decide and record what happens to the corpus's two non-fixture files
      (`city_density_broken_nagahara.notes.md`, `mode-a-forbidden-apparatus.svg`).
      verify: `make quick`
      research: procedure

## Phase 5 - the record and the docs (P2)

- [ ] **T18** Per-rule confirmation that every research finding whose only operative statement was a check
      body now has a documented home (FR-005). The urban rules bind hardest - they have no placer. Record
      the confirmation per rule; a class-level assumption is what this task exists to prevent.
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
- [ ] **T19** Rewrite `dev/gate.md` to carry the successor doctrine in the GM's own words (FR-010): when
      towns, provincial cities and capitals are scripted, their rules are written directly as tests of the
      placer that owns them, and a post-placement battery is not rebuilt. A session looking up "how do I
      add a check" must meet this, not instructions for writing a segment.
      research: procedure
- [ ] **T20** The doc sweep, per MENTION (FR-011): Mode B battery doctrine goes; **Mode A's stays**.
      `pack_audit`, `scatter_audit` and the 8 frozen red SVG fixtures are untouched and still documented -
      Mode A compounds are placed by a person, so a check on them is doing what checks are for. Verify by
      confirming Mode A's apparatus and its doctrine are intact, not by counting deletions.
      research: procedure
- [ ] **T21** Record where each of the 147 rules now lives (FR-009), so "what happened to rule X" is
      answerable after the code is gone.
      research: procedure

## Phase 6 - verify

- [ ] **T22** Coverage floors RE-DERIVED, not lowered. A drop is a coverage loss on code that is STAYING
      and is a sentence to the GM, never a quiet reduction.
      measure: `make hamlet-floor`
      research: procedure
- [ ] **T23** `make verify` (gate + its paired review). Fix everything it lists, then re-run once. Then
      `make maps` - reference, then the tier.
      research: procedure
- [ ] **T24** `make perf LABEL=166-end` and `make perf-report AGAINST=166-start`. A decrease is expected
      (the battery ran inside every roll); any seed that got SLOWER is diagnosed in writing with the number.
      research: procedure
- [ ] **T25** Report to the GM: what was deleted, where each rule went, what moved and why, and what the
      generator costs now.
      research: procedure
