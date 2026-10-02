# Tasks - feature 304, homesteads at scale

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). Research: [`research.md`](research.md).
Order: P1 (the scaling leg, tooling) and its base snapshot before any engine edit; P2 (the indexed scans, output-identical);
P3 (no dead seats) measured as scratch toggles first and built only for the form the choice rule keeps (plan D10).

## Occasions

None declared. P1 is tooling; P2 changes no output (plan D8 proves it byte-identical); P3 changes which seats the exhaustive pass
OFFERS, never where a house may stand or any placement rule (spec Decisions Recorded). If the chosen form moves a pool map's
houses, that map is re-examined here before landing and an occasion is added if the move reaches a rule.

## Baseline (constitution XIII)

- [x] T01 The `304-start` bookend on unmodified code, and the cohort baseline in the detached worktree `/tmp/base304`
      (`make cohort N=24`)
      research: rendering
      verify: DONE. 304-start 12.3 s total (dev/perf-log/20261002T031740Z-304-start-diagram-performance.json); cohort base 28/30 in /tmp/base304, research R6
- [ ] T02 The pre-existing cohort failure Audit-11 (`WebRefused`, linear, 10 households; research R6) diagnosed and fixed
      (constitution XIV)
      research: rendering
      verify: `make cohort N=1 SEED=11` passes; the cause and the fix in research.md; the rest of the cohort not worse
- [ ] T03 The pre-existing cohort failure Audit-905 (`UndeckableCrossing`, dispersed, 20 households; research R6) diagnosed and
      fixed (constitution XIV)
      research: rendering
      verify: the seed passes; the cause and the fix in research.md; the rest of the cohort not worse

## P1 - the scaling leg (US1; FR-001 - FR-003)

- [x] T10 [US1] Red: tests for `beyond_the_band()` (40 households refused outside, admitted inside; no `pool/` file names it),
      for `measure(households=)` rows and a refused row, and for `evaluate_scaling` (per-size verdicts, "no baseline" on an old
      base, the quadratic seeded fault of D4 reaching band 2+ on the 40 leg with the reference at band 0)
      research: rendering
      verify: DONE. test_perf_scaling.py: 11 of 13 failed red on missing code (beyond_the_band, SCALING_SIZES, Verdict.legs)
- [x] T11 [US1] Green: D2 in `hamletgen/plan.py`; D1 in `perf_snapshot.py` (`SCALING_SIZES`, `scaling` rows, `placer_calls`,
      `refused`); D3 in `perf_bands.py`, `perf_snapshot.report` and `perf_review` / `perf-gate` (the band owed is the maximum)
      research: rendering
      verify: DONE. D1-D3 built; 85 perf tool tests pass; make quick green
- [ ] T12 [US1] The `304-scale-base` snapshot with the new tool on the UNMODIFIED engine; its four seeds x three sizes in
      research.md beside R1
      research: rendering
      verify: the snapshot has 12 scaling rows (or a recorded refusal per missing one); `make perf-report` prints the legs

## P2 - the indexed scans (US2; FR-004, FR-005; SC-005)

- [ ] T20 [US2] Red: equivalence tests with the old bodies as oracles - D5 (random trees and doors, ties, a tree under
      `TARGETS_TRIED` points, a door far outside the tree) and D6 (random outlines and candidates, a candidate inside an outline,
      one within `bh` of an edge only)
      research: rendering
      verify: the tests fail against a stub index that drops a far candidate (proving they can fire)
- [ ] T21 [US2] Green: D5 in `settlement/rolling/access.py` (`AccessTree` ring query); D6 in `settlement/shrines_wells/byres.py`
      research: rendering
      verify: `make quick` green; T20 passes
- [ ] T22 [US2] The one-roll spy (D8b) on the reference at 40 households: every 97th indexed answer equals the oracle's
      research: rendering
      verify: the spy's count of compared calls and zero mismatches, in research.md
- [ ] T23 [US2] Inashiro regenerated (`make map GEN="--no-cache pool/hamlets/inashiro/inashiro.gen.py"`): SVG and manifest
      byte-identical
      research: rendering
      verify: `git status` over `pool/hamlets/inashiro/` shows no change
- [ ] T24 [US2] The pool (`make maps SCOPE=all`) and the cohort (`make cohort N=24`): every pool hamlet byte-identical; the
      cohort's per-seed houses and results equal to T01's
      research: rendering
      verify: `git status` over `pool/hamlets/` empty; the cohort compared seed by seed in research.md
- [ ] T25 [US2] What P2 bought: the scaling legs on the clone against `304-scale-base`, back to back (base worktree, then clone)
      research: rendering
      verify: per-size homesteads seconds before/after in research.md

## P3 - no dead seats (US3; FR-006; SC-006)

- [ ] T30 [US3] Scratch toggles for forms A, A' and B (plan D9) on top of P2; each timed at 15/20/40 households on the four seeds
      (best of three) and counted (placer calls, houses seated), and on the pool and cohort seeds 1-24 (houses seated, rules)
      research: rendering
      verify: the table of D9's measurements in research.md, base and each form back to back
- [ ] T31 [US3] The choice by D10's rule, recorded with every form's numbers; on "none faster", P3 is withdrawn here (T32-T34
      dropped, the record says why)
      research: rendering
      verify: the decision and the withdrawn forms in research.md and `dev/performance.md`
- [ ] T32 [US3] Red: D11's tests for the chosen form (no seat offered that the current state refuses / that has no clear strip)
      research: rendering
      verify: the tests fail on P2's engine
- [ ] T33 [US3] Green: the chosen form in `hamletgen/homesteads/capacity.py` / `region.py`
      research: rendering
      verify: `make quick` green; T32 passes
- [ ] T34 [US3] Inashiro regenerated and gated, then the pool and the cohort: every map's rules pass; households seated per
      cohort seed and pool map at least T01's (SC-006)
      research: rendering
      verify: `make maps SCOPE=all` green; the cohort compared seed by seed in research.md

## Closing

- [ ] T40 The `304-end` bookend; `make perf-report AGAINST=304-start` and against `304-scale-base`; any band diagnosed in writing
      research: rendering
      verify: the bands printed; SC-002/SC-003/SC-004 judged in research.md (a miss recorded and raised with the GM)
- [ ] T41 `dev/performance.md` section "Homesteads at scale (feature 304)" (D12); the memory note updated (D13)
      research: rendering
      verify: the section names each lever's wall-clock gain and every withdrawn form
- [ ] T42 `make done` green; push
      research: rendering
      verify: the gate's verdict; `sync-with-main.sh done` lands
