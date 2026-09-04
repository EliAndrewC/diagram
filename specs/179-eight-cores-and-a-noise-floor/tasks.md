# Tasks - feature 179

Spec: [`spec.md`](spec.md) (FAITHFUL, spec-fidelity round 3). Request: [`request.md`](request.md).

## The compute type

- [ ] T01 FR-001/FR-003/FR-004: `config.py` constants and the test that pins them
      research: procedure
      verify: `COMPUTE_TYPE == "BUILD_GENERAL1_LARGE"`, `RATE_PER_MIN == 0.02`, the comment records
      the measurement that chose it, `PARK_TIMEOUT_S`'s cost is $0.04, `ESTIMATE_MINUTES["reference"]`
      is 10.0 from the cited run-log with `full`/`operation` labeled unmeasured placeholders, and
      `tests/tooling/ci/test_config.py` pins the new pair
- [ ] T02 FR-002: the `gm-assistant-ci-monthly-alert` Lambda's `RATE_PER_MIN` 0.08 -> 0.02
      research: procedure
      verify: read back from AWS. `MONTHLY_BUDGET` untouched - it is denominated in real dollars and
      is the GM's. If it cannot be done, REPORTED to the GM, never silently skipped
- [ ] T03 FR-005/FR-005a: forward-looking rate/type prose only
      research: procedure
      verify: `ci/CLAUDE.md:7` and `:94`, skill `Makefile:621` and `:1033`. `timings.md`, the run
      logs and specs 130/177/178 UNTOUCHED - a grep proves the records still say XLARGE at $0.08

## The band-1 noise floor

- [ ] T04 FR-007/FR-008/FR-009/FR-010: `BAND1_PCT` and `evaluate`
      research: procedure
      verify: the constant sits beside `BAND2_*`/`BAND3_*`; `local` 0.0, `codebuild` 2.0, unknown
      environment defaults to 0.0; `>` not `>=`; bands 2 and 3 provably untouched
- [ ] T05 FR-011: the `OWES[0]` string
      research: procedure
      verify: band 0 under a floor no longer claims there was no increase; no other disclosure
      machinery added (`render` already prints every seed and the total unconditionally)
- [ ] T06 FR-012/FR-013: the interaction and the matrix, at the point of change
      research: procedure
      verify: the docstring states the floor, the 5-of-6 noise measurement as its WHY, and the
      interaction AS MEASURED - the floor is live on the FIRST remote build because `perf-gate` takes
      both bookends in-build; what is retired is the 8 stored XLARGE snapshots as cross-feature
      baselines. It must NOT say the gate goes mute
- [ ] T07 FR-013a: the band-1 prose sweep
      research: procedure
      verify: `CLAUDE.md:272`, skill `CLAUDE.md:144`/`:160`, `dev/performance.md:187-188`,
      `.claude/agents/perf-audit.md:3`/`:32` (including its "1.7% per-seed noise floor" reasoning,
      which must match the rule it now applies). `specs/*` and the review records UNTOUCHED
- [ ] T08 FR-013b: the constitution, 2.15.0 -> 2.16.0 MINOR
      research: procedure
      verify: the live matrix at `:745` and Principle VI's prose, the footer at `:1987`, a Sync
      Impact Report entry quoting the GM verbatim and listing dependents. **`:123` UNTOUCHED** - it is
      inside the `PRIOR (2.0.0 -> 2.1.0)` block and is a record of what 2.1.0 did

## The defect (Principle XIV)

- [ ] T09 FR-017: the in-build bookend guard asks the SNAPSHOT, not the filename
      research: procedure
      verify: the guard matches on recorded machine identity; 0 of 44 filenames contain `codebuild`
      today, so the old test was unconditionally false. The no-baseline refusal downstream is
      untouched. The point-of-change note states the one behavioral change: a SECOND remote build of
      the same feature now reuses the earlier same-machine `-start` rather than re-taking against the
      current `origin/main`, which is the restored feature-130 intent

## Closing

- [ ] T10 tests for everything above, at the 100% floor
      research: procedure
      verify: the floor's four cases (local unchanged, codebuild under, codebuild over, unknown
      environment), bands 2/3 unmoved, the guard predicate, and the pinned constants
- [ ] T11 `make done` green, the records current, and the answer to the GM
      research: procedure
      verify: 100% coverage floor, all guard suites green, pushed to main
