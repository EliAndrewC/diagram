# Tasks - 224 clip the throw, the glossary scan, and the drop's last pass

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL; research R1
      research: rendering
      verify: DONE. FAITHFUL at round 1 of 5; R1 from 223's R2 and the glossary profile
- [x] T02 FR-003 the glossary prefilter, held to the regex form on a fixture; FR-004 the direct parse, held to the general form
      research: rendering
      verify: DONE. `glossary_for` tests `v in text` before the boundary regex, held to the regex scan on a fixture over the real GLOSSARY; `fix_shape` reads the writer's order from a per-tag anchored regex with the general parse as the fallback, held to it on writer-order and shuffled fixtures
- [x] T03 FR-001/FR-002 `scatter_frame`, the stage, the two throw loops, the breach record, the pool test; `make map` Inashiro; the pool
      research: rendering
      verify: DONE. `scatter_frame` (crop boxes + belt + woodland + bamboo + pocket, + 48 + 120) set before each scatter in `stage_hinterland`, the two loops skip an outside throw before the keep-out test, `finish()` records `scatter_frame`/`_overhang`/`_breach`, the cohort reports a breach as a FAIL, `tests/gate/test_scatter_frame.py` over the pool; Inashiro hinterland 1.3 -> 0.6 s, SVG 3.9 -> 2.5 MB; the pool: no breach, the tightest side exactly the 120 px pad on every map, manifests differ only in `ink_classes` and the two meta keys
- [ ] T04 FR-005/FR-006: R2 with the cohort's overhangs; `make done`; the settlement-review; spec IMPLEMENTED; land
      research: rendering
