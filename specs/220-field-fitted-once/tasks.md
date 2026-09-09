# Tasks - 220 the field fitted once

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL; `220-start` bookend on unmodified code; research R1 (the profile before)
      research: rendering
      verify: DONE. FAITHFUL at round 2 of 5 (round 1: FR-005 over any moving step, STRtree required, the whole-roll yardstick); 220-start bookend 49.1 s over four seeds; R1 the profile before
- [x] T02 step 1: `carve_comb` / `finish_comb`, `fit_field` finishes the winner once; tests; reference hamlet measured (R2) (FR-001, FR-006)
      research: rendering
      verify: DONE. carve_comb/finish_comb (one body); fit_field scores CombCarve.planted_area (within 0.05% of the finish; the bare carve overshot 12% - R2) and finishes the winner once; tests incl. one finish per roll; field 5.25 -> 2.43 s, roll 9.9 -> 7.2 s
- [x] T03 step 1, the pool: `make maps`; every moved hamlet reviewed by `settlement-review` beside the gate; findings fixed (FR-005)
      research: rendering
      verify: DONE. make maps clean; four hamlets moved and reviewed (R2b, R4c): the reviews found two defects fixed at the source (the doubled-remnant sweep splitting the web on three maps; a planted basin keeping a 4 ft collar) plus two needles repaired at the seam pass's end; second-pass reviews pass; the stream coupling recorded for the GM
- [x] T04 step 2: the stroke index for the three supply-bank callers; equivalence test; no map moves; measured (R3) (FR-002, FR-006)
      research: rendering
      verify: DONE. StrokeIndex (banks.py) with one shared body; the two hot callers read BEYOND as clear, the hem's caller keeps the exact fallback; equivalence tests on random strokes; no map moved; field 2.43 -> 2.09 s (R3)
- [x] T05 step 3: one geometry per plot in the seam passes, a prefilter for the neighbor searches; measured (R4) (FR-003)
      research: rendering
      verify: DONE. PlotGeoms (one geometry per ring object, STRtree neighbors) and GeomTree (changed set, never rebuilt in a round - the rebuild was a measured dead end); no map moved; field 2.09 -> 1.71 s (R4)
- [x] T06 `make done` green; `220-end` bookend and `perf-report`; the rendered roll; R5; spec IMPLEMENTED; land (FR-004, SC-001..003)
      research: rendering
      verify: DONE. make done green 65 s (warm, one roll of one spec, 100% both floors); 220-end bookend total 49.1 -> 32.5 s (-33.8%, band 0); rendered roll 19.7 s (was 22.7); R5; eight second-pass review findings acted on or recorded; spec IMPLEMENTED; landing
