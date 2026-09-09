# Tasks - 221 the gate's fixed costs

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL; research R1 (the profile before, the audit)
      research: rendering
      verify: DONE. FAITHFUL at round 2 of 5; R1 the profile before (phases, the suite three ways, the audit)
- [x] T02 workers: time and peak-memory the test phase at 6/8/10/12 on a quiet box; set the cap by the rule; record at the point of change and in R2 (FR-001)
      research: rendering
      verify: DONE. 6/8/10/12 workers timed (49/45/40/45 s), footprints 0.95-1.52 GiB, two gates 5.9 GiB under 8; the rule picks 10; cap min(10, nproc) with the reasoning at the point of change; R2
- [x] T03 contexts: the full tree with and without per-test contexts, three runs each; the merge's needs read; the arrangement the number supports; R3 (FR-002)
      research: rendering
      verify: DONE. contexts ~2 s (48.6/45.3 vs 44.3/45.6), under the 10 s bar; left; the merge's needs recorded; R3
- [x] T04 one coverage table: addopts, the Makefile note, the tooling test; the saving measured; R4 (FR-003)
      research: rendering
      verify: DONE. --cov-report= in addopts (pytest-cov defaults to term with none), the Makefile note corrected, the hamlet floor's table only on a miss, tooling tests; one TOTAL on a passing run (measured); R4
- [x] T05 the rolls: the water-index line as a unit test; the determinism test to tests/soak/; `make roll-audit` after; R5 (FR-004)
      research: rendering
      verify: DONE. the determinism roll to tests/soak/test_village_determinism.py, water_index.py:49 as a unit test, the soak index row; roll-audit after lists 10 contexts; R5
- [x] T06 `make done` green; R6 the gate after beside R1; spec IMPLEMENTED; land (FR-005, FR-006)
      research: rendering
      verify: DONE. make done green 55 s (pytest 37 s at 10 workers), test-full 43 s with one table (pytest 31.8 s); R6; spec IMPLEMENTED; landing
