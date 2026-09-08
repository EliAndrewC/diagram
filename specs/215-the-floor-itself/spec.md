# Feature 215 - the floor itself

**Status**: DRAFT - `spec-fidelity` round 1 pending (constitution XVI).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) R1 - the audit, per roll,
of the lines nothing else reaches; the count after.
**Predecessors**: 213 (the census), 214 (the first packing, 21 -> 13 specs, 24 -> 16 rolls); the packing
record of 2026-08-31 (`dev/loop.md`, "THE PACKING QUESTION": floor about 8-9).

## Summary

The GM, on 16 rolls of 13 specs: *"are you really, truly not able to combine ... so that the same checks are
being made in those unit tests, but with three fewer rolls?"* and *"are you really not able to find different
hamlets, which could be combined into a single hamlet spec?"* The audit (R1) says: the three duplicates need
no roll at all, two of the thirteen specs are the pool's own maps rolled again, one exists only to be
perturbed, two exercise a loop that holds on stand-in stages, and one may pack if its defect reproduces
synthetically. This feature takes all of that: **9 rolls of 9 specs on a warm gate** (8 of 8 if seed 43
packs) - the record's floor - with every assertion kept where it was.

## Functional requirements

- **FR-001 The gate reads the pool's Inashiro and Kuwabata.** Every reader of the reference and of Kuwabata
  (the gate modules' `rolled` fixtures, the ratchet, the lane rules, the hamlet floor's fixed subjects) reads
  the pool sweep's map: the generator obtained through `gate_obtain` (served warm, rolled cold in its coverage
  child) and its manifest from disk, the plan from `plan_site`. The reference spec used by the tests is the
  pool's brief (`fixtures_min={'shrine': 1}`), per the GM. The ratchet's verdict (the roll's failures, the
  attempt) is carried in the manifest's meta by `generate()` so it can be read back; `rollcache`'s `roll:`
  subjects for these two go, and `rollcache.hamlet()`/`report()` serve the other rostered specs unchanged.
- **FR-002 The three duplicates go.** The fan-out test runs `roll_pool` with a stub producer (module-level,
  picklable) and asserts the pool branch's ordering and results; the child-equality proof is RETIRED - every
  roll is a child now and the shipped maps are children's work, so the property that matters, child == child,
  is the immune test's, and the toy-level child tests in `tests/pipeline/test_rollcache.py` keep the mechanism
  covered; the cache round trip runs on the sweep's entry (its artifacts and its recorded dependencies) - store
  into a scratch cache, wipe, load, bytes match - and rolls nothing.
- **FR-003 The immune test perturbs the reference.** A child roll of the reference with one extra draw at
  every `meta()` (a module-level target) against the pool's committed manifest; Kashikawa's `Roll` row goes,
  its `PoolGen` row stays.
- **FR-004 The re-roll loop on stand-in stages.** `generate()`'s loop is exercised with `driver.STAGES`
  replaced by stand-ins and `unreached_houses` patched as today: the attempt count, the forbidden ground handed
  to the second build, the re-roll that helps nothing not kept, the artifacts written - the same assertions,
  no map. Retry and NoHelp leave the roster.
- **FR-005 Seed 43: its lines as unit tests, its kink reproduced or kept.** The eight lines only it reaches
  (`ways/touch.py`, `waterfields/carve.py`) become direct unit tests. The kink itself is attempted as a synthetic
  reproduction on a stub (a house corner and a lattice step through the router): if it reproduces, the strict
  xfail moves there and the seed leaves the roster; if it does not within this feature, the seed stays and R2
  records what was tried - measured, not assumed.
- **FR-006 Nothing asserted is dropped; the further cuts are recorded, not taken.** Every assertion of the
  sixteen sites is kept on a map that exists or on the stand-in that holds it. The audit's further cuts
  (Woodland-shrink, Clamped, Polder 19, the three seatings on one partial roll) each trade a behavior asserted
  on a real map for a unit test and are listed in R1 with their cost for the GM to take or leave.
- **FR-007 The roster, the census, the record.** `tests/rolls.py` at 9 rows (8 if seed 43 packs); a warm
  gate's census reads 9 rolls of 9 specs (8 of 8); `make done` green; R2 the census line and the gate's time;
  `dev/loop.md`'s packing section extended; `tests/CLAUDE.md`.

## Success criteria

- **SC-001** A warm full gate's census reads 9 rolls of 9 specs, or 8 of 8, with no stated duplicates.
- **SC-002** `make done` green at 100% on both floors; no test's assertion removed (FR-006).
- **SC-003** The gate's pytest phase shorter than 214's 204 s.

## Decisions Recorded

- **D1 - the reference's brief is the pool's.** The tests' `Inashiro 4` gains `fixtures_min={'shrine': 1}`
  so the map the gate asserts on IS the shipped map. The GM's words: *"I don't care whether the Inashiro
  reference has a different fixture from the brief, so that's fine."*
- **D2 - the child-equality proof is retired, not moved.** Its claim (a child's environment does not change
  the map) protected the transition of feature 210; with every roll a child and the shipped maps children's
  work, the claim that matters is determinism between children, which the immune test asserts every gate.
- **D3 - the ratchet reads the manifest.** `generate()` records the roll's failures and attempt in the
  manifest's meta, so a map read from disk carries its own verdict; a small engine change, re-keying every
  roll once.
- **D4 - the further cuts are the GM's.** Four more rolls could go (R1) by trading a real-site assertion for
  a unit test; the audit prices them and this feature stops at the record's floor.
