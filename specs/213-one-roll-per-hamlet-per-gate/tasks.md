# Tasks - 213 One roll per hamlet per gate

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` (tooling; nothing physical).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. FAITHFUL at round 2 of 5 (round 2's first attempt died on an API limit before reading; relaunched). Round 1 required five changes, all applied: FR-007's surface derived from the callers of generate/build/STAGES with a census check; FR-003 on a second ROLL not a second request; the exceptions adjudicated (perf tests roll their own rostered seeds; the fan-out's pool half a stated duplicate; gate_obtain the rule); the record at the chokepoint roll_scope() (D5); FR-005's pin named exactly with its cost. The relayed D14 request (FR-001, SC-004, T10) reviewed in the same round
- [x] T02 the census plugin, its verdict and the roster (FR-003, FR-004); the Makefile loads it; each
      refusal proved (FR-013)
      research: rendering
      verify: DONE. DONE. l7r/diagram/_census.py writes at driver.roll_scope (and at finish.render_png / raster.picture for renders); ci/rollcensus.py is the -p shim, ci/rollverdict.py the attribution and the verdict, tests/rolls.py the roster (21 rows, 4 Duplicates, 5 PoolGens, 5 InProcess); the Makefile's test recipe loads the plugin, clears the census per run and runs the verdict before the floors; make roll-census re-reads it. Each refusal proved in tests/tooling/ci/test_rollverdict.py (16 cases) and the ci route in test_main.py. Verified on the full run of 2026-09-08 (t08-w4-s4): roll census green, 25 rolls of 21 specs, 28 requests served
- [x] T03 one roll per spec: the unified child roll, `Report.manifest`, `hamlet()`/`report()` read it (FR-001)
      research: rendering
      verify: DONE. DONE. rollcache._roll = one child roll under roll:<spec> via _roll_payload (generate; plan, kept manifest, Report); hamlet()/report() are views, report_deps reads the same subject; Report.manifest carried by generate(). Verified by the census of the green full run: every cohort seed once (41 twice only by the stated fan-out duplicate), 28 requests served from shared rolls
- [x] T04 the first-wave lock and the roll cap (FR-002, FR-010's cap); proved with two producers
      research: rendering
      verify: DONE. DONE. rollcache._share_lock (flock in the run share dir, LOCK_WAIT_S=600, a dead holder lets the next waiter roll) and _roll_slot (L7R_ROLL_SLOTS, default 4). Proved in tests/pipeline/test_rollcache.py (two producers one roll, a wedged holder, the slot bound). Verified on the green full run: Inashiro 4, Kuwabata 21, Polder 12/19 each rolled once, whatever the workers' start order (the first census had Inashiro rolled by 4 workers)
- [x] T05 the child roll-out: the five closures lifted and run by name, the immune and CLI tests, the
      fan-out's serial half, the regen child (FR-007); child equality per closure
      research: rendering
      verify: DONE. DONE. rollcache._in_child(target, arg) runs a module-level function by name; keyed_to(child=) for the lifted closures (roll_cloud_only, roll_lane_only, roll_one_house, roll_clamped, roll_woodland_shrink, roll_retry, roll_no_help), gencache.run_gen_child for the immune test and the regen site, the CLI test's roll through generate, the fan-out's serial half served from the shared roll, the cache round trip's gen in one child (D6). Verified by the census verdict: no in-worker roll outside the roster's InProcess exceptions on the green full run
- [x] T06 tests do not render: the default, the opt-outs, the census's render refusal (FR-006)
      research: rendering
      verify: DONE. DONE. tests/conftest.py sets DIAGRAM_SKIP_RENDER=1 by default; the renders marker (registered in pyproject) on test_finish (2), test_core (1), test_raster, test_page, page_browser/test_synthetic, test_placement_stages; the census records every PNG and page-raster render and the verdict fails one from an unmarked test (proved in test_rollverdict; the first census caught the placement-stages plates, now marked). Verified: the green full run's verdict lists no stray render
- [x] T07 first-attempt seeds (FR-005); collection order (FR-010)
      research: rendering
      verify: DONE. DONE. The CLI test rolls Clitest seed 9 (seed 8 took two attempts); the perf-snapshot test seed 6 and the perf-profile tests seeds 5 and 7, each rostered; the cohort seeds 41-44 stay with seed 42's three attempts recorded (FR-005). rollverdict.rolls_first moves the rolls_map tests to the front of collection (proved in test_rollverdict). Verified on the green full run: seed 42 reported as 1 roll, attempts 3
- [ ] T08 measurements: the pool-sweep child profile (FR-008); 4/6/8 workers (FR-009); the cap count;
      research R4
      research: rendering
- [ ] T09 the record (FR-013); `make done` green; SC-001 read off the census; land GATED
      research: rendering
- [x] T11 the first gated census read and acted on (D6, D7): the process in the roll key, the three sites
      that roll again by their nature stated, the stub modules bounded, the pool gens their own kind, the
      perf-profile seed; a second full run green on the census
      research: rendering
      verify: DONE. DONE. D6 and D7 in spec.md: the roll key carries the pid; Kashikawa's perturbed roll and the cache round trip are stated Duplicates; the five pool gens are PoolGen rows (allowed once, from the sweep, never stale); the stub modules are InProcess(stub=True), bounded by STUB_MAX_S; the first-stage perf-profile test rolls seed 7. Verified: the full run of 2026-09-08 (t08-w4-s4) green on the census after the first two runs had failed it
- [ ] T10 feature 207's D14 confirmed closed (FR-001, SC-004): the polder-only incremental run measured
      with the census - the floor phase rolls nothing, the gate's time recorded against 219 s; ticked with
      the numbers whether or not a change beyond FR-001 was needed (the GM's request, relayed 2026-09-07)
      research: rendering
