# Tasks: The blue paddy plot is its own kind

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Every task carries `research: rendering | physical | procedure` (constitution v2.12.0). A `physical`
task - one about how a place was built, farmed or lived in - carries the three research boxes, and
`tests/test_task_research_boxes.py` fails the gate if a ticked one is missing them.

## Phase 0 - research

- [x] T1 The `source-reader` pass on what a blue plot depicts: the shitsuden / kanden category, its
  penalties, the valley-bottom terms, and what the drain-foot siting actually rests on.
  research: physical
  - [x] research pass - dispatched 2026-08-29; five claims put to `source-reader` with pointers
  - [x] source-reader confirmed - A and B READ with verbatim quotes; C NOT-FOUND / SUMMARY-ONLY;
    D an inference from an attested cascade; E READ for yatsuda and fukada, the identity NOT confirmed
  - [x] recorded and cited - `research/fields.md` 'The wettest plots are their own kind of ground';
    five keys in `research/SOURCES.md`; the three failures written into the re-sourcing queue

- [x] T2 Record the two defects the pass turned up (constitution XIV): the unsourced "four to six
  inches" in the shipped `paddy` modal, and "Kishu-school" as the name for the comb layout. Both
  queued in `research/SOURCES.md`, the second also noted at the claim in `research/fields.md`;
  both reported to the GM rather than silently changed.
  research: procedure

## Phase 1 - the reference settlement

- [x] T3 RED: the tests, before the implementation. `tests/interactive/test_classes.py` - add
  `wet paddy` to `SPEC_CLASSES` (with the comment recording it as added at implementation, like
  `field pond` and the dike-pond rows). `tests/interactive/test_page.py` - a page whose plots carry
  both classes reports both in the census and emits both explanations, and a page with no blue plot
  emits neither the class nor the sibling paragraph (spec Edge Cases). Run them and watch them fail.
  research: rendering

- [x] T4 GREEN: the registry row and the emit site. `classes.py` - the `wet paddy` row (key, name,
  covers, what, why, `accurate` + `label_note` + `caveat`, sources, entry) and the symmetric
  `("paddy", "wet paddy")` sibling text in `_PAIRS`. `comb.py` `_comb_draw_paddies` - the class
  chosen from the fill, with the comment recording why it is decided there (spec FR-002).
  research: rendering

- [x] T5 Regenerate the reference hamlet (`make map GEN=pool/hamlets/inashiro.gen.py`) and assert
  the drawn output did not move. MEASURED: `.svg` and `.png` byte-identical; `.json` moves in
  `ink_classes` alone (`paddy` 575 -> 573, `wet paddy` 2), which is the census recording the new
  class and is not a drawing. SC-004 said "`.json` byte-identical" through three review rounds and
  was corrected to what the artifact does.
  research: rendering

- [x] T6 Open `pool/hamlets/inashiro.html` in the browser test and drive the GM's own scenario:
  hover a blue plot and see only the blue plots light; hover a green one and see no blue one light;
  click a blue plot and read a modal that is about the blue plot. Add it to
  `tests/full/interactive/test_page_browser.py` and prove it FIRES by reverting T4's emit-site
  expression and watching it go red.
  research: rendering

## Phase 2 - the pool

- [x] T7 `make done` - GREEN, 2,589 tests. Run twice: once after the implementation, and again
  after the pool sweep rewrote three manifests (pool manifests are part of the gate's engine key,
  so the sweep re-opened it). `classes.py` and `comb.py` both at 100% line coverage.
  research: procedure

- [x] T8 `make maps` - MAPS CLEAN. Tripwire seeds 27/33/37/41 ok (37 had been red on the previous
  run, before this work) and 47 the GM's waived expected failure; then kashikawa, kuwabata,
  mizuguchi and sawada rolled OK. MEASURED: kuwabata `wet paddy` 5 / `paddy` 51 against low 5,
  blue 5 - the tint-all rule carries the class, `unclassed_ink` empty, `unregistered_classes`
  empty. CORRECTION to the plan: of the four tint-all maps only KUWABATA is live;
  `poolmaps.classify` puts enokida, tanada and yatsuda in the frozen legacy pool, which is never
  regenerated, so they keep the pages they have. Five scripted maps exist in total (inashiro,
  kashikawa, mizuguchi, sawada, kuwabata) and all five are covered.
  research: rendering

- [x] T9 The perf bookend and its review. BAND 0 - no increase on the total or on any seed, so no
  `perf-audit` dispatch and no records owed. The reported -59.2% is CONTENTION, not a gain: the
  baseline ran beside another session's 48-seed cohort audit, the closing run on an idle box. Noted
  in plan.md so the perf log is not mined for a speedup this change cannot produce.
  research: procedure

- [x] T10 Update `l7r/diagram/interactive/CLAUDE.md` so the next reader learns the class exists and
  that the tint has two rules, and add the review-ledger rows for the three `spec-fidelity` rounds
  (`docs/review-ledger.md`).
  research: procedure

- [x] T11 Stop-work: commit, `scripts/sync-with-main.sh done`. The route is GATED (engine `.py`
  changes), and with `remote off` that means LOCAL-GATED - a green local `make done` on the merged
  engine content pushes. Every task above must be ticked first, or the push refuses.
  research: procedure
