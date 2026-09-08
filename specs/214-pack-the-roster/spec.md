# Feature 214 - pack the roster

**Status**: DRAFT - `spec-fidelity` round 1 required three changes, all applied (FR-007 restated site by site; the
target number established in the record's own unit and the delivery itemized against it; the immune test kept on
Kashikawa per the reviewer's aside, so its `Roll` and `PoolGen` rows both stay). Round 2 pending (constitution XVI).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - the ten rolls adjudicated
one by one, the probe over the coverage rolls, the count after.
**Predecessor**: 213 (the roll census and the roster it enforces); the packing record of 2026-08-31
(`dev/loop.md`, "THE PACKING QUESTION": 11 rolled, floor 8-9).

## Summary

The GM, on being told half the roster exists because "a test's behavior needs a roll of its own": *"is it
ACTUALLY the case ... and not just some assertions we could add onto the existing tests where that same
hamlet was already rolled elsewhere?!"* It is not. Seven of the ten read a shared roll or run on stand-in
stages; three genuinely roll (the perturbed roll, the in-process half of the child-equality proof, the
seed-43 kink). This feature makes every test that can read a shared roll read one - *"back down to the number
it was at before, especially if we do the 'shared roll' thing for most or all of these."* The number before, in
the packing record's own unit (DISTINCT SPECS a gate rolls): 11 measured on 2026-08-31, NINE after the two merges
that section then made; the feature is judged against the nine, which is the coverage set unchanged today.

## Functional requirements

- **FR-001 The ratchet population is the roster's own coverage rolls.** The cohort gate test and the
  lane-rule cohort tests read the plain shared rolls (Inashiro 4, Kuwabata 21, Polder 12, Polder 19) through
  `rollcache.report()` / `hamlet()`; the seated-households, acreage and gate-verdict assertions are
  unchanged and hold on them (research R1). The pin `GATE_COHORT_EXPECTED` is re-keyed to those specs
  (empty, as it has been since feature 166). The hamlet floor's fixed subjects follow the same list. Seeds
  41, 42 and 44 leave the roster; seed 43 STAYS as a rostered emergent condition, because the probe shows no
  coverage map carries its kink and the strict xfail is the only reader of an open defect.
- **FR-002 The fan-out compares the pool child against the shared roll of the reference.** `driver.cohort()`
  delegates to a `roll_pool(specs, jobs)` that takes explicit specs, so the test pool-rolls Inashiro 4 and
  compares it with `rollcache.report(Inashiro 4)`; the pool child is a stated duplicate of the reference.
- **FR-003 The child-equality proof uses the reference; the immune test is already a shared roll and stays
  on Kashikawa.** The in-process half rolls Inashiro 4 in the worker and compares with the shared roll (a
  stated duplicate of the reference); Childroll leaves the roster. The immune test's clean side is the pool
  sweep's own gen-cache entry and only its perturbed roll is real - the shared-roll form already - and its
  subject stays the largest hamlet (20 households, fall 315, the off-map sink: stages the reference does not
  run), so Kashikawa's `Roll` row (the perturbed roll) and its `PoolGen` row (the sweep) both stay, and the
  `Duplicate` for its clean side rolled cold stays with them.
- **FR-004 The CLI test rolls nothing.** `generate` is patched for the test to a function that asserts the
  spec `main()` built is the reference spec, writes the `.json` and `.svg` artifacts from the shared roll's
  manifest, and returns the shared roll's Report; the test's assertions (artifacts written, the name reported)
  stand. Clitest leaves the roster.
- **FR-005 The perf tests run on stand-in stages.** `measure()` and `profile_stage()` are exercised with
  `driver.STAGES` monkeypatched to stand-in stages named so the profiled stage resolves, under a
  deterministic clock, exactly as the stage-profile tests do; both modules become `stub=True` exceptions in
  the roster and Inashiro 5, 6 and 7 leave it. The real seeds stay with `make perf-gate`.
- **FR-006 The roster and the record, in the record's unit.** `tests/rolls.py` lists 13 `Roll` rows: the
  packing record's NINE coverage specs unchanged (Inashiro 4, Kuwabata 21, Polder 12, Polder 19, CloudOnly,
  LaneOnly, OneHouse, Clamped, Woodland-shrink), the two re-roll-loop rolls added after the record (Retry,
  NoHelp - the loop's own lines), Cohort-43 (the open defect's only carrier) and Kashikawa 3 (the immune
  experiment's perturbed roll, which cannot be served); the `Duplicate`s are the fan-out's pool child, the
  child-equality proof's in-process half and the cache round trip, all of the reference, plus Kashikawa's
  clean side rolled cold. A warm full gate therefore rolls **16 times for 13 specs**, against 24 for 21 before
  and 37 for 14 at the start of feature 213. Against the record's nine: +2 the re-roll tests, +1 seed 43, +1
  the immune experiment - each named, none of them a coverage roll the packing could remove. The census
  verdict is green on a full run; `dev/loop.md`'s packing section and 213's research point at the new count;
  research R2 records the census line and the gate's time.
- **FR-007 Every site adjudicated, what each proves after.** No test is deleted. After the change: the
  cohort ratchet proves seating, acreage and the gate verdict on the roster's coverage rolls (the same
  assertions, a different population - D1); the lane rules prove bending on the same rolls and the seed-43
  xfail keeps the kink visible; the fan-out proves the pool child equals the shared roll of the reference;
  the child-equality proof compares an in-process roll of the reference with its shared roll; the immune
  test is unchanged. TWO SITES PROVE LESS, stated: the CLI test proves `main`'s wiring (arguments to spec,
  the artifacts written, the report line) and no longer runs `generate` - proven by every other roll (D4);
  the perf-snapshot and perf-profile tests prove the tools' behavior on stand-in stages under a
  deterministic clock and no longer time a real map - the real seeds stay with `make perf-gate`.

## Success criteria

- **SC-001** A warm full gate's census reads 16 rolls of 13 specs (FR-006's itemization), the duplicates all of the reference but Kashikawa's clean side.
- **SC-002** `make done` green, 100% on both floors, no test removed.
- **SC-003** The cohort seed 42's three-attempt roll no longer appears in any gate.

## Decisions Recorded

- **D1 - the ratchet population is no longer "seeds nobody looked at".** The cohort test's docstring made
  that claim; of the new population only Inashiro was tuned by hand, and the polders and Kuwabata were chosen
  for their archetypes, not looked at as maps. The property pinned (seating, acreage, the gate) is the same.
- **D2 - seed 43 stays.** The GM's number is 11; this is 12, because the probe found no other carrier for
  the one open defect and hiding it is worse than one roll of 21 s. Raised with the GM at landing.
- **D3 - the immune subject stays the largest hamlet.** The draft moved it to the reference to drop a
  distinct spec; the reviewer (round 1) pointed out the clean side is ALREADY the pool sweep's shared entry, so
  the move would save no roll and would lose the off-map sink and the fall-315 stages the reference never
  runs. The immune test is left as it is.
- **D4 - the CLI's `generate` is patched.** The CLI test proved `main` and `generate` end to end; `generate`
  is proven by every roll in the suite, so the CLI test proves `main`'s wiring alone, for no roll.
