# Tasks - 214 pack the roster

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. DONE. FAITHFUL at round 3 of 5. Round 1: FR-007 restated site by site naming the two sites that prove less; the target in the record's unit (11 measured, NINE after its merges) with the delivery itemized; the immune test kept on Kashikawa per the reviewer's aside (its clean side is already the sweep's shared entry). Round 2: D2 in the record's unit and count; the research aligned. Round 3's aside (the delivery in the Summary) applied
- [x] T02 the ratchet and the lane rules over the roster's coverage rolls; the floor's fixed subjects; seed 43 kept (FR-001)
      research: rendering
      verify: DONE. DONE. the ratchet over rolls.COVERAGE (tests/gate/hamletgen/test_driver.py), the lane rules over COVERAGE + KINK (test_cohort_lane_rules.py), the floor's fixed subjects the same five; the probe (research R1) showed every assertion holds; the green gate's census shows the four coverage rolls read by 34 served requests and seed 43 rolled once
- [x] T03 the fan-out over `roll_pool` on the reference (FR-002)
      research: rendering
      verify: DONE. DONE. driver.roll_pool(specs, jobs) with cohort() delegating; the fan-out pool-rolls rolls.REFERENCE and compares with rollcache.report(REFERENCE) - a stated Duplicate of the reference in the census
- [x] T04 the child-equality proof and the immune test on the reference; `perturb` retired from `run_gen_child` (FR-003)
      research: rendering
      verify: DONE. DONE. the child-equality proof compares an in-process _roll_payload(REFERENCE) with the shared hamlet()/report()/report_deps(); the immune test left on Kashikawa (its clean side already the sweep's entry, reviewer's aside); Childroll gone from the roster
- [x] T05 the CLI test with `generate` patched (FR-004)
      research: rendering
      verify: DONE. DONE. the CLI test patches hg.driver.generate to serve the shared roll and write the artifacts from its manifest; asserts main built exactly the reference spec; rolls nothing (0 rolls attributed to it in the census)
- [x] T06 the perf tests on stand-in stages (FR-005)
      research: rendering
      verify: DONE. DONE. measure() and profile_stage() on stand-in stages under a counter clock (a fixed tick list landed on roll_scope's and the census's own clock reads - measured: every stage 0.0); the perf modules stub=True in the roster; 23 tests green
- [x] T07 the roster, the record, `make done` green, SC-001 read off the census, land (FR-006, FR-007)
      research: rendering
      verify: DONE. DONE. tests/rolls.py at 13 rows (COVERAGE, REFERENCE, KINK named), 4 duplicates, 5 pool gens; dev/loop.md packing addendum, tests/CLAUDE.md, 213's pointer; make done green 2026-09-08 (3446 passed, 100% both floors); the census: 16 rolls of 13 specs, 34 served - SC-001 exactly; whole gate 222 s (pytest 204 s) against 333-418 s; the two found defects fixed (D5); landing LOCAL-GATED
