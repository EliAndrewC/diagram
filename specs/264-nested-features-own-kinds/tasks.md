# Tasks - feature 264, a feature inside a feature is its own kind

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D9). Inventory: [`inventory.md`](inventory.md). Coverage:
[`coverage.md`](coverage.md).

**No task here is `research: physical`.** No research pass is run (GM 2026-09-26); every write-up is carried from the
existing record, and what it does not cover is recorded as owed.

- [x] T01 The reader and the page: `sheet.pieces` with each fragment's part-of kinds, `data-part-of`, `render_page(within=)`, `page.js` indexing (D2, D3)
      research: rendering
      verify: DONE. DONE. sheet.pieces gives each fragment its part-of kinds (lineage + data-part-of); render_page(within=) writes data-in after data-k; page.js files a part under its parents - test_sheet.py, research.md R4-R5
- [x] T02 Tag every inventoried part on Ochiba, Hayakawa and Ubame; rooms as their own floors; each PNG 0 px changed (D1, D4)
      research: rendering
      verify: DONE. DONE. every inventoried part tagged on the three hand sheets, rooms as their own floors; make picture-diff 0 px on all five PNGs (research.md R2)
- [x] T03 The placer's emitter draws the rack and posts as parts; the two generated sheets regenerated (D6)
      research: rendering
      verify: DONE. DONE. compound.emit_svg draws the rack and posts as parts inside a practice-ground group; both placer sheets 0 px changed
- [x] T04 The pack audit folds rooms into buildings; audit output identical on every sheet (D5)
      research: rendering
      verify: DONE. DONE. pack_audit rooms_folded; audit output identical before/after on all three hand sheets, old sheets unchanged by the fold (research.md R3, plan review re-measured six)
- [x] T05 Measure the record's coverage of every new kind (`coverage.md`)
      research: rendering
      verify: DONE. DONE. coverage.md - 32 rows plus inner rooms and nakamon added after review
- [x] T06 Write every new kind from `coverage.md`; trim each parent's `Covers:` and prose; split the court divider and the nakamon (D7)
      research: rendering
      verify: DONE. DONE. the new kinds written from coverage.md, parents trimmed, the court divider split from the nakamon; three building reviews x2 rounds applied (docs/review-ledger.md)
- [x] T07 Research owed and contradictions into `future-work/compounds.md` (D8)
      research: rendering
      verify: DONE. DONE. future-work/compounds.md 'Opened by feature 264': guesses, thin rows, contradictions, review questions, drawing defects, canon found on Obsidian Portal
- [x] T08 Unit tests: the reader's part-of, the page's `data-in`, the audit's fold, the registry closure and completeness over the five sheets
      research: rendering
      verify: DONE. DONE. test_sheet (part-of, data-in), test_pack_audit (rooms folded), test_raster (palette rows, crisp text only when asked), test_compound_kinds (every part and parent; no lead repeated)
- [x] T09 The browser probe over the five pages (SC-001, SC-002), result in `research.md` (D9)
      research: rendering
      verify: DONE. DONE. probe264.py over five pages, both modes: every part answers as itself, every parent pointable and opens its write-up, parent lights parts, no part lights a parent (research.md R5)
- [x] T10 `make done` green; the review ledger row; land
      research: rendering
      verify: DONE. DONE. make done green (131s); review ledger rows for the six building-review passes; landing
