# Tasks - 228 The crop dike lights as a ring

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 1: every clause of the request carried by FR-001; FR-002 judged a consequence of the one emit line, not a widening; FR-003's preservation of the crown clip named as the real hazard
- [x] T02 `landuse.py`: the bank emitted as a ring (FR-001/FR-002), the why at the point of change and
      in the operative doc (FR-004)
      research: rendering
      verify: DONE. landuse.py: the bank emitted as `<path d="{bd} {wd}" fill-rule="evenodd" ...>` after both outlines are computed in their original order, the why at the point of change; archetypes.md 'The bank is a ring' records the convention and the three declined alternatives; Kuwabata's page carries 26 mulberry-dike groups, all even-odd rings
- [x] T03 the unit test on the emitted bank and pond paths (FR-004); SC-002 shown once
      research: rendering
      verify: DONE. tests/settlement/test_fields.py::test_a_dike_pond_bank_is_a_ring_around_its_water - the bank path holds both outlines and the rule, its hole is the pond's own outline, the pond path is unchanged, the records untouched; SC-002 shown once: 1 failed, 45 passed on the old emit, then 46 passed
- [x] T04 Kuwabata regenerated, the page opened with the dike lit (SC-001); `make verify` green with
      `settlement-review` recorded (SC-003); notes entry; land GATED
      research: rendering
      verify: DONE. Kuwabata regenerated (26 dike groups, all even-odd rings); the page opened headless in raster mode with the dike lit - every sampled pond-center pixel unchanged, every bank pixel lit (SC-001); make verify: gate green in 151 s on commit a9140fe7 (dev/run-log/20260912T130118518661-561726.json) with settlement-review pass beside it (water pixels lighting 100% -> 6.2%, all at the rim; picture diff 0.144% of pixels, all within the pond stroke band); notes entry and ledger rows written; landing GATED (LOCAL-GATED)
