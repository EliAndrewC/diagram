# Feature 214 - pack the roster

**Status**: DRAFT - `spec-fidelity` round 1 pending (constitution XVI).
**Request**: [`request.md`](request.md). **Research**: [`research.md`](research.md) - the ten rolls adjudicated
one by one, the probe over the coverage rolls, the count after.
**Predecessor**: 213 (the roll census and the roster it enforces); the packing record of 2026-08-31
(`dev/loop.md`, "THE PACKING QUESTION": 11 rolled, floor 8-9).

## Summary

The GM, on being told half the roster exists because "a test's behavior needs a roll of its own": *"is it
ACTUALLY the case ... and not just some assertions we could add onto the existing tests where that same
hamlet was already rolled elsewhere?!"* It is not. Seven of the ten read a shared roll or run on stand-in
stages; three genuinely roll (the perturbed roll, the in-process half of the child-equality proof, the
seed-43 kink). This feature makes every test that can read a shared roll read one, so the roster returns to
the packing record's number - *"back down to the number it was at before, especially if we do the 'shared
roll' thing for most or all of these."*

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
- **FR-003 The child-equality proof and the immune test use the reference.** The in-process half rolls
  Inashiro 4 in the worker and compares with the shared roll; the immune test's perturbed roll is a child of
  the reference spec (a module-level target that applies the one-extra-draw perturbation and calls
  `_roll_payload`) compared with the shared roll's manifest - no gen files, no pool entry touched. Both are
  stated duplicates of the reference; Kashikawa and Childroll leave the roster; `run_gen_child`'s `perturb`
  parameter, which now has no caller, goes.
- **FR-004 The CLI test rolls nothing.** `generate` is patched for the test to a function that asserts the
  spec `main()` built is the reference spec, writes the `.json` and `.svg` artifacts from the shared roll's
  manifest, and returns the shared roll's Report; the test's assertions (artifacts written, the name reported)
  stand. Clitest leaves the roster.
- **FR-005 The perf tests run on stand-in stages.** `measure()` and `profile_stage()` are exercised with
  `driver.STAGES` monkeypatched to stand-in stages named so the profiled stage resolves, under a
  deterministic clock, exactly as the stage-profile tests do; both modules become `stub=True` exceptions in
  the roster and Inashiro 5, 6 and 7 leave it. The real seeds stay with `make perf-gate`.
- **FR-006 The roster and the record.** `tests/rolls.py` lists 12 rolls (the packing record's 11 plus seed
  43) and the four stated duplicates, all of the reference; the census verdict is green on a full run;
  `dev/loop.md`'s packing section and the 213 research point at the new count; research R2 records the
  census line and the gate's time.
- **FR-007 Every site adjudicated, none dropped.** No test is deleted and no assertion weakened: each of the
  ten sites keeps what it proves (R1's table says what that is), on a shared roll or stand-in stages.

## Success criteria

- **SC-001** A warm full gate's census reads 16 rolls of 12 specs, all four duplicates of the reference.
- **SC-002** `make done` green, 100% on both floors, no test removed.
- **SC-003** The cohort seed 42's three-attempt roll no longer appears in any gate.

## Decisions Recorded

- **D1 - the ratchet population is no longer "seeds nobody looked at".** The cohort test's docstring made
  that claim; of the new population only Inashiro was tuned by hand, and the polders and Kuwabata were chosen
  for their archetypes, not looked at as maps. The property pinned (seating, acreage, the gate) is the same.
- **D2 - seed 43 stays.** The GM's number is 11; this is 12, because the probe found no other carrier for
  the one open defect and hiding it is worse than one roll of 21 s. Raised with the GM at landing.
- **D3 - the immune subject is the reference, not the largest hamlet.** The 2026-08-16 choice of Kashikawa
  was for the mechanisms a large map exercises; the reference exercises the same mechanisms (position-seeded
  attributes, the farmstead, well and grove scopes) with five fewer households and a shrine. What is lost is
  variety, not a mechanism; what is gained is one distinct spec fewer and 25 s against 36-67 s.
- **D4 - the CLI's `generate` is patched.** The CLI test proved `main` and `generate` end to end; `generate`
  is proven by every roll in the suite, so the CLI test proves `main`'s wiring alone, for no roll.
