# Tasks - feature 179

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 3). Request: [`request.md`](request.md).

## The compute type

- [x] T01 FR-001/FR-003/FR-004: `config.py` constants and the test that pins them
      research: procedure
      verify: DONE. `BUILD_GENERAL1_LARGE` / 0.02, with the measured three-row table recorded as the
      reason and the 4-vCPU rejection kept with its evidence. Park cost $0.04. `reference` 10.0 from
      the cited run-log; `full`/`operation` left alone and labeled unmeasured placeholders - and the
      visible artifact of that DISCLOSED rather than papered over: `full` (8.0) now reads LOWER than
      the measured `reference` (10.0), which cannot be true, and is not corrected because correcting
      it means inventing a number for a scope no run on this box has measured
- [x] T02 FR-002: the `gm-assistant-ci-monthly-alert` Lambda's `RATE_PER_MIN` 0.08 -> 0.02
      research: procedure
      verify: DONE, by READ-BACK from AWS: rate 0.02, `MONTHLY_BUDGET` and every other variable
      byte-identical. Left at 0.08 the 20%-steps email would have overstated every bill 4x and
      tripped the $75 budget at about $19 of real spend. The docstring's claim that the mirror exists
      was CHECKED against the account rather than trusted - feature 178 was burned by a comment
- [x] T03 FR-005/FR-005a: forward-looking rate/type prose only
      research: procedure
      verify: DONE. `ci/CLAUDE.md:7` and `:94`, `Makefile:621` and `:1033`, the last two with
      GUARD_EDIT_OK and a reason. The RECORDS are untouched and it is proved rather than asserted:
      `timings.md` still carries 3 XLARGE mentions and 38 run-log files still name XLARGE at $0.08

## The band-1 noise floor

- [x] T04 FR-007/FR-008/FR-009/FR-010: `BAND1_PCT` and `evaluate`
      research: procedure
      verify: DONE. `{local: 0.0, codebuild: 2.0}` beside `BAND2_*`/`BAND3_*`, `BAND1_DEFAULT_PCT`
      0.0, compared with `>` to match BAND2's own boundary. Nine tests: exactly-the-floor, the
      seed-only path with a negative total, the unknown environment defaulting to strict, and bands
      2 and 3 proved unmoved
- [x] T05 FR-011: the `OWES[0]` string
      research: procedure
      verify: DONE - now "nothing - no increase above this environment's band-1 line", which stays
      true when a floor muted one. No disclosure machinery added: `render` already prints every seed
      and the total unconditionally, and a test pins that a muted +1.0% is still on the page
- [x] T06 FR-012/FR-013: the interaction and the matrix, at the point of change
      research: procedure
      verify: DONE, and stated AS MEASURED: the floor is LIVE on the first remote build, because
      `perf-gate` takes both bookends in-build; what the compute move retires is the eight stored
      XLARGE snapshots as CROSS-FEATURE baselines. An earlier draft asserted the opposite - that the
      gate would go mute and self-heal after two runs - which was never measured and is false
- [x] T07 FR-013a: the band-1 prose sweep
      research: procedure
      verify: DONE. `CLAUDE.md:272`, skill `CLAUDE.md:144`/`:160`, `dev/performance.md`, and
      `.claude/agents/perf-audit.md:3`/`:32` - the agent that ADJUDICATES band 1, so its own
      instructions now match the rule it applies. A repo-wide grep leaves "any increase" alive only
      in `specs/` and the constitution's historical PRIOR block, both records
- [x] T08 FR-013b: the constitution, 2.15.0 -> 2.16.0 MINOR
      research: procedure
      verify: DONE. The live matrix at `:745`, a new Principle VI clause carrying the 5-of-6
      measurement AND the labeled guess, the footer, and a Sync Impact Report entry quoting the GM
      verbatim and listing dependents. **`:123` UNTOUCHED**, proved by diff: zero removals of the
      historical line. Precedent that this is the project's own mechanism and not a session widening
      its remit: v2.1.0 is the amendment that WROTE this matrix in, by the session implementing 129

## The defect (Principle XIV)

- [x] T09 FR-017: the in-build bookend guard asks the SNAPSHOT, not the filename
      research: procedure
      verify: DONE. `perf_review.has_start_for_this_machine` compares recorded `(host, image)`;
      `make -n perf-gate` shows the guard calling `has-start`. Eight tests, including the one that
      would have caught the original defect: it writes the exact file the old glob looked for and
      shows the glob still finds nothing, while asking the snapshot finds it. Exercised on real data
      too - True for a same-machine start, False for a start taken on another box

## Closing

- [x] T10 tests for everything above, at the 100% floor
      research: procedure
      verify: DONE. 20 in `test_perf_bands.py`, 26 in `test_perf_review.py`, all green. One
      PRE-EXISTING test broke and was ADAPTED rather than deleted:
      `test_environments_are_checked_independently` proved independence with a +0.8% codebuild
      increase, which is now correctly under the floor - raised to +3%, and a new test asserts the
      new property directly, that the same +0.8% owes an explanation locally and nothing remotely
- [ ] T11 `make done` green, the pairing recorded, and the answer to the GM
      research: procedure
      verify: the 100% coverage floor, all guard suites green, `PAIR_OK` recorded on the confirming
      run (this feature rolls no map, so a settlement-review has nothing to read), pushed to main
