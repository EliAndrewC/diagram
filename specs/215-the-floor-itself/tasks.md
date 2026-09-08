# Tasks - 215 the floor itself

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. DONE. FAITHFUL at round 5 of 5 - every round found a new, smaller item: FR-006 itemized (round 1), D5 facing 214's D3 (1), the fourth site that proves less (2), the fifth if seed 43 packs (3), the make roll-audit target dropped as unrequested (4). The synthetic kink probe ran during the review and did not reproduce the kink (R2), so FR-005 keeps seed 43: 9 of 9
- [x] T02 the reference brief aligned; the manifest carries the roll's verdict; the gate reads the pool's Inashiro and Kuwabata (FR-001, D1, D3)
      research: rendering
      verify: DONE. DONE. rolls.REFERENCE carries the pool's brief; generate() writes roll_failures/roll_placed/roll_acres into the meta before the finish (the probe showed a roll-cache roll of that brief identical to the committed pool manifest); tests/gate/_pool.py rolled_map/rolled_report read the sweep's entry under a per-gen lock; the fifteen gate modules, the ratchet, the lane rules and the floor's subjects read it; verified by the green gate: no roll of Inashiro but the immune experiment's, none of Kuwabata
- [x] T03 the three duplicates gone: the fan-out on a stub producer, the child-equality proof retired, the round trip on the sweep's entry (FR-002)
      research: rendering
      verify: DONE. DONE. the fan-out runs roll_pool(specs, jobs=2, produce=stub_produce) against the serial path (the pool branch, ordering, pickling); test_rollcache_child.py retired (D2); the round trip stores/wipes/restores the sweep's own entry with its recorded deps; verified: 0 rolls by all three in the census
- [x] T04 the immune test perturbs the reference (FR-003)
      research: rendering
      verify: DONE. DONE. rollcache.extra_draws + _perturbed_manifest: a child roll of the reference with one extra draw per meta() against the pool's committed manifest; Kashikawa's Roll row gone, its PoolGen row kept; verified: Inashiro rolled once, by the immune test, and equal
- [x] T05 the re-roll loop on stand-in stages (FR-004)
      research: rendering
      verify: DONE. DONE. the re-roll loop on stand-in stages in the worker (tests/gate/hamletgen/test_driver.py, a stub InProcess module): attempt count, forbidden ground, the re-roll that helps nothing not kept, the artifacts written; Retry and NoHelp gone from the roster; verified green
- [x] T06 seed 43's eight lines as unit tests; the synthetic kink attempted and its outcome recorded (FR-005)
      research: rendering
      verify: DONE. DONE. seed 43's eight lines: the detour rung, the rung-3 join, the fold refusal from either end (a post sets the piece's clearance so the fold rule decides), the hem pass - all direct unit tests reached (cov-file); the synthetic kink attempted from the seed's own geometry and NOT reproduced (R2), so the seed stays: 9 of 9
- [x] T07 the roster, `make done` green, the census read (SC-001), R2, the record, land (FR-006, FR-007)
      research: rendering
      verify: DONE. DONE. the roster at 9 rows, no duplicates; make done green 2026-09-08 (3437 passed, 100% both floors) with the census 9 rolls of 9 specs, 11 served - SC-001; pytest 147 s / gate 165 s against 204 / 222 s (SC-003); the record in tests/CLAUDE.md, dev/loop.md, the pipeline index; R2; the verdict's --full defect found and fixed; landing LOCAL-GATED
