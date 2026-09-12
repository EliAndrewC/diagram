# Tasks - 226 the site boundary, and the seats proposed from it

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL; research R1
      research: rendering
      verify: DONE. spec-fidelity rounds 1-4 CHANGES REQUIRED, round 5 FAITHFUL (2026-09-12); rounds 6-7 on the post-implementation amendments applied, round 8 pending at the tick of T05; research R1 from dev/performance.md's per-house counts
- [x] T02 FR-001 the site boundary built once and recorded, with its test
      research: rendering
      verify: DONE. hamletgen/homesteads/boundary.py: site_boundary (the paddy's facing chains, one holed union outline, two corridor sets, the toe band registered as hard ground), install_site_boundary records site_boundary in the manifest; tests/hamletgen/test_site_boundary.py 9 tests green; the pool's boundaries 7-10 chords, 1-3 rings, 0-5 water and 0-3 corridor segments (R2)
- [x] T03 FR-002 the fit test on the boundary; `make map` Inashiro; the counts
      research: rendering
      verify: DONE. _rect_blocked takes _site_blocks_rect (nine points; chains by side, outline by containment, corridors) when a boundary is set; make map Inashiro: stage_homesteads 1.0 -> 0.25 s, positions per house 419 -> 55, rectangles 1,090 -> 194 (R2); make done green 2026-09-12 (72 s)
- [x] T04 FR-003 seats from the chains, the pre-test, the bounded spiral, `meta.seat_search`
      research: rendering
      verify: DONE. front_row from the chains at the pitch (the envelope walk retired), the pre-test before try_place, the six-ring spiral with three rescue rounds while the quota is short, the re-roll's salted lattice, meta.seat_search with rounds; candidates per house 1.6-7.0 and placer calls 1.1-1.8 on the pool against 3-10 proposals per house before; Kuwabata 157 proposals -> 112 pre-tested candidates for 16 houses
- [ ] T05 FR-004/FR-005: the pool, the cohort, R2, `make done`, the settlement-review, spec IMPLEMENTED, land
      research: rendering
