# Tasks - 196 Warm and cold ratchets

All `research: rendering` - guard mechanics and the run log. No claim about how a place was built.

- [x] T01 `research: rendering` FR-001: `_reference` writes the roll-cache class from the SAME call
      that prints the verdict. Two bugs found and fixed while implementing: a second `report()` call
      would always read HIT (the first fills the cache), and `@` mid-continuation is not a valid
      recipe-line start. Verified BOTH branches end to end - a normal roll writes `warm`,
      `GATE_NO_CACHE=1` writes `cold` (it reports `[BYPASS]`, the case round 4 caught).
- [x] T02 `research: rendering` D1: the gate clears the marker at `T0`, so a marker left by another
      target's `REF_FIRST` can never classify a later gate.
- [x] T03 `research: rendering` FR-002: `_gatecost.median_seconds` and `class_count` take a class,
      filtered BEFORE the `RECENT` slice; entries with no class are excluded, never defaulted.
      Classless callers unchanged (verified: the classless median still returns what it did).
- [x] T04 `research: rendering` FR-003: `baseline_cold=549` with its OWN written reason, additive to
      `baseline=400` which KEEPS ITS NAME - `check-run-plausible.py` derives the dry-run floor from it
      and treats a missing value as no floor.
- [x] T05 `research: rendering` FR-004: below sample the RUN is judged, never waved through; an
      unknown class takes the stricter warm ceiling; the rule binds at `reference` scope only, with
      the SCOPE carried to `_ratchet.py` as a fourth argument so the rule is not inert.
- [x] T06 `research: rendering` FR-006/SC-002/SC-003/SC-004: six new tests - cold vs warm ceilings,
      below-sample judging (over its ceiling FAILS), unknown class taking the warm bar, full scope
      staying unjudged, a per-CLASS written reason, the class-exclusion median, and the dry-run floor
      still reading `baseline`. 24 passed; `test_run_plausible.py` 6 passed.
- [ ] T07 `research: rendering` SC-006: `make done` green, 100% coverage, `make hooks-test` green -
      and feature 195 lands with it.
