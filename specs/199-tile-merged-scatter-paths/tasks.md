# Tasks - 199 Tile the merged scatter paths

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - how a browser
paints a page, nothing about how a place was built.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. Round 1 CHANGES REQUIRED (FR-007 failed on a correct implementation; FR-008's cap on Inashiro could never fail); round 2 FAITHFUL after both were rewritten - the reviewer measured the reference page itself (39 paths of 200+ subpaths, every one merge grammar)
- [x] T02 `merge_primitives` tiles a bucket of `TILE_MIN`+ members into one path per `TILE` cell
      (FR-001, FR-002, FR-005); `_cell` at module level; the why at the point of change
      research: rendering
      verify: DONE. `TILE`/`TILE_MIN`, `_cell`, `_tiles` in page.py; the emit loop writes one path per cell; the why at the point of change (R1-R4 in one paragraph)
- [x] T03 unit tests for the tiling (FR-006); the structural guard on the real reference page (FR-007)
      research: rendering
      verify: DONE. Four unit tests in tests/interactive/test_page.py (73 passed); the structural guard in tests/full/interactive/test_page_browser.py - with the split off it fails on 39 paths spanning up to 22 cells
- [x] T04 the browser test: a Kuwabata fixture, the pointer sweep at the opening view capped at 40 ms
      on the median; the reference sweep recorded (FR-008); both guards shown to FAIL with the tiling
      reverted (SC-005)
      research: rendering
      verify: DONE. `kuwabata` fixture + `test_kuwabata_pointer_moves_are_cheap_at_the_opening_view`, cap 40 ms on the MEAN (R6: untiled mean 59.5 / median 21.0 - a median cap PASSED the reversion, so the statistic was changed and re-reviewed, round 3 FAITHFUL); reference sweep recorded uncapped; SC-005 shown on both guards
- [x] T05 measurement on the implementation: the R2 move-cost table and the R4 pixel comparison over
      the pool pages, written to `research.md` R6 (FR-004, SC-001..003)
      research: rendering
      verify: DONE. R7: every page 16.6-18.8 ms at every view (Kuwabata opening 57.7 -> 17.4, Kashikawa 4x 133 -> 18); pixels 0-17 of 1.4 M; SC-001/002 hold, SC-003 MISSED on Sawada (+14.4%), reported
- [x] T06 documents: `interactive/CLAUDE.md` row; `.specify` pointer; memory note (FR-009)
      research: rendering
      verify: DONE. interactive/CLAUDE.md merge_primitives row; .specify/feature.json points at 199; memory note project_page_paint_cost_giant_paths.md
- [x] T07 `make done` green, `make page-check` green, the Kuwabata page opened and hovered at the
      opening view (SC-004); land on the GATED route
      research: rendering
      verify: DONE. make done green (3,005 passed, coverage 100%, 406 s); the gate's test phase includes the interactive tests and the browser test, and the page stamp; Kuwabata opened and hovered at the opening view by T05's sweep; landing GATED (LOCAL-GATED, remote off)
