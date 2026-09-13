# Tasks - 245 Lit beads at low zoom

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - a map convention of
the HTML target, nothing physical behind it.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
      verify: DONE. spec-fidelity FAITHFUL at round 1 (three asides taken in the round); plan review MODE 4 BLOCKED at round 1 on P7 (the plan named page-lit as SC-002's check where the spec names the contact sheet) and CLEAR at round 2 on the amended plan, plan-review.json recorded by the subagent
- [x] T02 the stylesheet rule and its comment (FR-001, FR-002, FR-003); the synthetic map's bead and the
      raster-mode browser test (FR-005)
      research: rendering
      verify: DONE. page.css: the lit bund-beans class keeps full fill opacity in raster mode, one rule after the wash with the FR-003 comment; _driver.py's synthetic map gains one bead; test_synthetic.py reaches raster mode in a 100-unit viewport and reads the lit paddy at 0.45 and the lit beads at 1, both 1 on the vector page; make page-check green (778 passed, page and browser stamps written)
- [x] T03 `page_lit.measure` zooms by key (FR-004); the stub tests and the browser test on a page that
      opens in raster mode (FR-005)
      research: rendering
      verify: DONE. page_lit.measure presses Control+= (the page's own zoom key) instead of turning the wheel; stub tests assert the presses and the step cap; the browser test measures the halves page in a 300-unit viewport that opens in raster mode - a 100-unit one put the zoom buttons over most of the lit half (43% changed) - asserts raster measured, then vector reached with zoom above the opening view; on the shipped Inashiro page VECTOR=1 now reports mode: vector at 6.31x of fit; 39 passed across tests/tools/test_page_lit.py and the browser package
- [x] T04 the record (FR-006): research R1, the two index rows; SC-002 decided by the R1 contact sheet
      re-taken on the shipped Inashiro page with the shipped stylesheet (page-lit only confirming no other
      class moved) and SC-003 by `make page-lit ... VECTOR=1` on it reporting vector mode; `make page-check`
      and `make done` green; land GATED
      research: rendering
      verify: DONE. research R1 (the measurement) and R2 (the shipped stylesheet replayed on the shipped Inashiro page: the contact sheet shows the beads gold where they were olive, page-lit reports no other class moved and VECTOR=1 reports mode: vector); the interactive and tools index rows; make page-check green (778 passed); make done green (test-full, 100% over 25,517 statements, roll census green) after one red run whose single error was a pre-existing race - tests/full/pipeline/test_gencache.py deleting the pool's own Inashiro manifest under other workers' fixtures - fixed under Principle XIV to round-trip a copy; landing GATED (LOCAL-GATED)
