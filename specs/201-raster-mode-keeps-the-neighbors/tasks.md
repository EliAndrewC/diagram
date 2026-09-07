# Tasks - 201 Raster mode keeps the neighbors

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the inexact
      route (the wash) put to it against the GM's own allowance
      research: rendering
      verify: DONE. FAITHFUL at round 1: the wash graded a faithful reading of the GM's conditional (both exact routes measured, R2/R3), the sheet-level hiding implied by the scale complaint
- [x] T02 `raster.without_text`; `page.py` renders the picture without text (FR-001); `page.css` the leaf
      rule and the wash (FR-002, FR-003); the why at each point of change
      research: rendering
      verify: DONE. raster.without_text; page.py renders the picture from it; page.css: one leaf-hiding selector (`:not(g.f.on *):not(g.raster *):not(defs *)`) and the 0.45 wash on the lit class's filled shapes; the id map now rendered WITH the font mapping (its text was not being painted - found by T03's unit test, a defect of feature 200 fixed here)
- [x] T03 unit tests (FR-005); the browser test on the Kuwabata fixture (FR-006); SC-003 shown once
      research: rendering
      verify: DONE. Unit: without_text, the picture without text vs the id map with it (17 in test_raster.py); browser: text displayed, no leaf outside a lit group, the placard's font equal lit and unlit, the wash 0.45, a lit stream's ink shown. SC-003: with feature 200's group rule restored the leaf assertion failed (8,335 displayed) - the test file then crossed the 1,000-line bar and was split into tests/full/interactive/page_browser/ (conftest, _driver, test_synthetic, test_reference, test_speed; the page-check target and test_page_check repointed)
- [x] T04 documents: `interactive/CLAUDE.md`, feature 200's D4 amended, memory (FR-007); the crops kept
      research: rendering
      verify: DONE. interactive/CLAUDE.md raster.py row; feature 200's D4 revised; memory; crops kept in research.md R5 after the gate's regeneration
- [x] T05 `make done` green; the page opened with the paddy and the placard lit (SC-004); land GATED
      research: rendering
      verify: DONE. make done green (3,027 passed, coverage 100%, 498 s) after the browser test file was split into a package for the file-size gate; the regenerated Kuwabata page opened in raster mode with the paddy, a well, a bund and the placard lit (R5 crops); landing GATED (LOCAL-GATED, remote off)
