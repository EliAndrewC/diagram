# Tasks: The Performance Audit Subagent

**Spec**: [spec.md](spec.md) (FAITHFUL) | **Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md)

Every refusal is TWO tasks (FIRES / STAYS QUIET, constitution XVIII). Paid tasks are marked 💵.

## Phase 1: Measurements the design rests on

- [x] T001 Identity: is a subagent's shell distinguishable? (research R1 - NO; recorded so it is never re-investigated)
- [x] T002 cProfile overhead on the REAL `make perf` workload (research R2 - +225%; always-on is out, tier 2 is triggered)
- [x] T003 What the existing stage timings cannot answer, in writing (research R3)
- [x] T004 (20260825T120024Z-129-start: total 269.0 s, median 76.3 s, worst 89.3 s - matches the spec's floor runs (267-269 s)) Bookend `make perf LABEL=129-start` on unmodified code
- [x] T005 (2026-08-25: three runs on one commit on xlarge - total spread 0.8%, worst seed 1.1% (research R4); not materially different from the laptop's 0.7%/1.7%, so no threshold question goes to the GM; ~$1.52) 💵 (~$1.20) CodeBuild noise floor: three `ci-check TARGET="perf LABEL=129-noise-{a,b,c}"` on one commit; spread in research.md + timings.md; report to the GM if materially different from 0.7%/1.7%

## Phase 2: The evaluator and the records

- [x] T006 (perf_snapshot.machine_identity records environment=local|codebuild; identity_of returns (environment, host, image); the refusal names both environments; the report row prints environment/host) `perf_snapshot.py`: explicit `environment` field (FR-013); `identity_of` returns it; the refusal names environments (FR-014)
- [x] T007 (l7r/diagram/tools/perf_bands.py) `perf_bands.py`: `evaluate()` - per-seed and total pct, stage delta, band 0-3, every line crossed, what is owed; refuses cross-environment
- [x] T008 (tests/tools/test_perf_bands.py - 10 cases incl. SC-002b and the refused cross-environment pair) `tests/tools/test_perf_bands.py`: the GM's matrix pinned (every threshold, both measurements); SC-002b (feature 128's pair: total -29.9%, seed 47 +30.7% -> band 3); band 1 on +0.5%; nothing owed on -1%; cross-environment REFUSED
- [x] T009 (l7r/diagram/tools/perf_review.py: explain/confirm/audit/signoff/check/show; binding = sha256(end commit, environment, measurements)) `perf_review.py`: ReviewRecord write/read, binding hash, `--check` for the active feature per environment; refusals name the command
- [x] T010 (tests/tools/test_perf_review.py - 12 cases: every refusal fires, the full ladder passes, environments independent, stale bindings named) `tests/tools/test_perf_review.py`: FIRES - missing confirmation, stale binding, inconsistent/not-justified/cannot-determine verdicts, audit with a missing criterion, band 3 without signoff; STAYS QUIET - the full ladder passes; no increase owes nothing
- [x] T011 (Makefile: the six targets; perf-report prints the bands via perf_bands.render and returns 0; the 10% cap exit is gone) Makefile: `perf-explain`, `perf-confirm`, `perf-audit`, `perf-signoff` (terminal required), `perf-review`, `perf-profile`; `perf-report` prints bands; `perf-gate` prints what is owed (FR-009b) and no longer exits on the superseded 10% cap; `.PHONY`, `help`
- [x] T012 (unit-tested (WHO IS ASKING prompt and decline without AS=perf-audit; signoff refused without a terminal via the --tty seam); make-level exercised at T020) **FIRES**: `perf-confirm` / `perf-audit` without `AS=perf-audit` decline with the GM's prompt; `perf-signoff` with no terminal is refused. **STAYS QUIET**: with the declaration each writes its record with `granted_by`
- [x] T013 (l7r/diagram/tools/perf_profile.py; proven 2026-08-25 on seed 4 stage `seat`: the derived table dev/perf-log/20260825T123324Z-profile-129-seed4-seat.txt is 3,951 bytes and tracked, the raw .prof sits under the gitignored dev/perf-raw/ (git check-ignore confirms), and with no PERF_ARCHIVE the archive step reports itself skipped and the table stands alone) `perf-profile SEED= STAGE=`: cProfile of one stage, derived top-25 table tracked (kilobytes), raw `.prof` under gitignored `dev/perf-raw/`; archive step degrades when no repository is configured (FR-011b); **FIRES/QUIET**: the table exists and is under 8 KB; the `.prof` is not tracked

## Phase 3: Enforcement at the push

- [x] T014 (sync-with-main.sh push runs `make perf-review` after review-gate.sh; CI_PERF_REVIEW seam) `sync-with-main.sh push`: `make perf-review` after `review-gate.sh`; a refusal stops the push naming the command; `CI_PERF_REVIEW` seam
- [x] T015 (test-sync-with-main.sh case 10 (24 checks green)) `scripts/test-sync-with-main.sh`: **FIRES** - `CI_PERF_REVIEW=false` stops a push; **STAYS QUIET** - a passing review pushes
- [x] T016 (2026-08-25, four guards deleted in turn - table below) T048-style proof: delete each new guard in a scratch copy, watch its companion go red; table below

## Phase 4: The subagent, the constitution, the docs

- [x] T017 (.claude/agents/perf-audit.md) `.claude/agents/perf-audit.md`: reads the artifact + the diff, confirms (band 1) or adjudicates the three criteria (band 2), runs the make command `AS=perf-audit`; may run `perf-profile`; returns cannot-determine when it cannot decide
- [x] T018 (container-scripts/append-system-prompt.md names perf-audit and its exclusive AS=perf-audit) `container-scripts/append-system-prompt.md`: `perf-audit` pre-authorized like the other review agents
- [x] T019 (constitution 2.1.0 (VI's clause replaced), CLAUDE.md enforcement row + version line, the skill CLAUDE.md command map and loop rule, dev/performance.md section) Constitution VI: the three-band matrix per environment replaces the two-band clause (v2.1.0); CLAUDE.md's always-on line; `dev/performance.md` section; memory
- [x] T020 (2026-08-25: 129-end 268.4 s vs 129-start 269.0 s - band 1 (seed 39 +1.0%, web +0.8 s; total -0.2%); `make perf-review` REFUSED until the explanation and confirmation existed; the session wrote the explanation, the perf-audit role (launched as general-purpose carrying the definition - the harness had no `perf-audit` type yet) verified the noise claim against the three identical-code runs and the diff (tools/ only) and recorded `consistent`; `make perf-review` now green. The subagent also found the trend loader crashing on review records - fixed with a regression test) This feature's own bookends: `-end` taken, bands evaluated, records produced through the real subagent (the first use), `make perf-review` green

## Closing

- [x] T021 (local `make done` green (this push's own gate), hooks-test green, pushed through the gated route naming this feature - the first production merge through feature 130) `make done` green; hooks-test green; `sync-with-main.sh done` through the gated route
- [x] T022 (the session's closing message of 2026-08-25) Report to the GM: the identity finding, the cProfile number, the CodeBuild floor, the archive repository they create

## Guard/test pairs (T016)

| guard | companion | deleted-guard test went red? |
|---|---|---|
| `perf_bands.evaluate` band 1 (any increase) | `tests/tools/test_perf_bands.py` | yes (3 red) |
| `perf_review` WHO-IS-ASKING decline without `AS=perf-audit` | `tests/tools/test_perf_review.py` | yes (2 red) |
| `perf_review.check` binding (a record counts only for the numbers it audited) | `tests/tools/test_perf_review.py::test_a_record_is_bound...` | yes (1 red - the test was strengthened first: the original passed for the wrong reason, a stale explanation) |
| `sync-with-main.sh` push refuses on a red `perf-review` | `scripts/test-sync-with-main.sh` case 10 | yes (2 red) |
