# Implementation Plan: the landing cohort - 48 seeds when engine work lands, and a fresh-seed rate (feature 386)

**Spec**: `spec.md` | **Request**: `request.md` | **Builds on**: `make cohort` and its per-seed record
(`l7r/diagram/tools/cohort_audit.py`, feature 375 amendment 7), `scripts/measure/cohort_known.py` (baselines and standing,
feature 385 T03/T04), `scripts/measure/cohort_seeds.py` (FR-038), the gated route of `scripts/sync-with-main.sh`.

## Summary

`make cohort` rolls a fresh block beside its ten fixed seeds, in the same pool and record (`cohort_audit --fresh`); `make
cohort-landing` rolls main's baseline first when it is missing, then 48 fixed seeds, the pinned rows and a 48-seed fresh block; one
push gate holds the gated route to that record; the seed report gains the fresh rate. One engine-tree file changes,
`l7r/diagram/tools/cohort_audit.py` (D1), so the feature lands on the GATED route and goes through its own landing cohort (SC-004).

## Constitution Check

- I-V, VII-IX, XI: N/A - no UI, no pool content, no SOURCE block, no setting prose, no kanji.
- VI: each task's verification is listed in it; the gate is proved red on a fixture and by removing its call (SC-001, SC-002).
- X: ruff, ruff format, pyrefly; 100% coverage of `cohort_audit.py` held by `tests/tools/test_cohort_audit.py`; each new
  behavior has a test red without it; `audit()` stays under the 100-statement cap (the block's specs and its rate line are helpers).
- XII: tooling; no research question. Every task is `research: rendering`.
- XIII: the gate IS the cohort half of XIII at the push; nothing is loosened.
- XIV: the six failing fresh seeds are defects found; their kinds belong to feature 385's lane-law and web-settle work and feature
  384's rows, and go to the GM (spec, Out of scope). `cohort_seeds` counting any seed of 901 or more as pinned is fixed (D7).
  `cohort_known --stamp` treating a docs-only edit under `l7r/` as an engine diff was reported here, then fixed after the landing
  at the GM's ask (2026-10-18): `cohort_known` and `cohort_gate` now compare `l7r/diagram/ci/delta.py`'s `engine_key`, blind to
  docs, comments, docstrings and formatting, as the push route and `make done` are.
- XVI: built as the three bullets and "That would change the cohort default and the landing route" say (spec, "read literally").

## T01 - the fresh block, the landing cohort, its gate and the rate (FR-001 to FR-010)

### T01 Decisions

**D1 - the fresh block lives in `cohort_audit`, the rest in the Makefile and `scripts/`.** FR-002 puts the block in the same run and
record as the fixed seeds, so `cohort_audit` takes `--fresh <k> --fresh-from <seed>`: the block's specs follow the pinned rows in the
one process pool, each seed marked `"fresh": true` in the record (with `fresh_first`, `fresh_count`), the report prints the block's
rate after the pass count, and neither the pass count, the residue table, the knob coverage lines nor the exit code read a fresh seed.
A `--households` or `--only` run rolls no block, as it rolls no pinned row. Why not a second `cohort_audit` call from the Makefile
(no engine edit): a second call is a second reference check and a second pool wave on the per-fix loop, against bullet 1's "at 48 s
it's the right inner loop" (D3 measures the in-pool cost). The engine edit re-keys every cached roll once (`gencache.engine_files()`
counts `tools/`); that is a one-time cold cohort and gate, accepted for the inner loop's speed. The gate logic is
`scripts/gates/cohort_gate.py`, the push's refusal and escape `scripts/gates/cohort-gate.sh` (as `claims-gate.sh`).

**D2 - which record counts.** A record is *on the landed engine* when its `commit` resolves, `git diff --quiet <commit> HEAD -- l7r
pool` holds, and it carries no `engine_diff` (feature 385 T04). The **landing record** is the newest such record with `first_seed` 1,
`households` null, 48 fixed seeds or more (not pinned, not fresh) and 48 fresh seeds or more. The pinned rows are seeds 901-906.

**D3 - the fresh block's start and size.** First seed `10000 + int(sha256(<l7r tree id> <pool tree id> <git diff HEAD -- l7r
pool>)[:12], 16) % 990000` (`cohort_gate.py fresh-seed`, printed in the rate line): one engine, one block (a re-run is served from the
roll cache); a changed engine, another block; never a seed below 10000. Size: 48 on the landing cohort (comparable with the 12%
measured on 400-447); on the per-fix run `COHORT_FRESH`, set from the measurement below so the ten-seed loop's wall time does not
move: the per-fix run is 16 maps on `cpus - 2` workers (20 here), so the spare workers roll the block in the same wave.
`COHORT_FRESH = 4`, from the measurement under `### T01 measurements` (m:fresh-block-cost): 20 maps cold took a median 56.7 s against
57.2 s for the 16 of the per-fix run. THE BAND: within 5% of the FRESH=0 median (the perf bands' band 1), 60.1 s here - and the
run-to-run spread is wider still (16 maps ran from 45.6 to 69.8 s). Past the spare workers the cost shows: 24 maps ran 78.3 and
61.4 s (observed 2026-10-18; method: two cold runs on seeds 7240 and 10240, not part of the recorded value), so the block stops at 4.

**D4 - the regression reading is cohort_known's.** `cohort_gate` calls `cohort_known.baselines(landing, records, same_engine)` and
`standing(...)`; `standing` skips a seed marked fresh (it has no baseline by construction). A NEWLY FAILING, WORSENED or NO BASELINE
line refuses, verbatim; FIXED and PRE-EXISTING lines print and pass (XIII).

**D5 - the push.** `cohort-gate.sh` runs where `push_cmd` takes the `GATED` or `GATED-LOCAL` route, before `make ci-merge`; a DIRECT
push never meets it. Its refusals: no landing record on this engine; a regression line (D4). Each names `make cohort-landing`. It
prints the landing record's fresh rate and never refuses on it. A tree whose Makefile has no `cohort-landing` target (the guard
suites' fixtures) is silent - keyed on the target, because a fixture holding `l7r/diagram` wakes every push check that imports the
engine. `COHORT_OK="<reason>"` discharges, checked by `hm_escape.py reason-ok`, logged by `guard_log`, written to `dev/bypass-log/`.
Freshness against a moved main is the gated route's own (`make done` green on the merged engine content, which the landing record
must match).

**D6 - `make cohort-landing`.** First, when `cohort_gate.py needs-baseline` finds no 48-seed record on main's engine, it rolls main's
(`git worktree add --detach <tmp> origin/main`, `make -C <tmp> cohort N=48 FRESH=0`, the worktree removed; the record lands in the
clone, `commit-run-record.sh` providing). FIRST because `cohort_known.baselines` reads only records older than the one it judges
(spec-fidelity, round 1). Then `make cohort N=48 FRESH=48`, its failure carried on; then `cohort_gate.py check`, whose exit is the
target's. Once every gated landing leaves a landing record, main's engine always has one, and this step is skipped.

**D7 - the report.** `cohort_seeds.summary` leaves fresh seeds (a record's marked seeds, and every unpinned seed of a record marked
fresh or starting at 10000 or above - the two probe records of 2026-10-18 are marked `"fresh": true`) out of its failures and its
fewest-first-seeds count, counts a seed pinned only if it is one of the six pinned rows, and lists each record's fresh rate and the
pooled rate.

**D8 - docs.** `l7r/diagram/CLAUDE.md` ("The loop"), `l7r/diagram/tools/CLAUDE.md` (the tools table), `docs/guards.md` (a row for
`cohort-gate.sh` with its escape), the `cohort` target's `FRESH=` help line, `make docs`.

**D9 - tests.** `tests/tools/test_cohort_audit.py`: the block rolled after the pinned rows, marked in the record, printed as a rate,
outside the pass count and the exit code, absent on a scaling roll. `tests/tooling/test_cohort_gate.py`: the landing record's
selection, the fresh seed, the refusal lines, `needs-baseline`. `tests/hooks/test-cohort-gate.sh`: silent without the target; a
refusal names `make cohort-landing`; `COHORT_OK` with and without a reason; a failing fresh seed never refuses.
`tests/hooks/test-sync-with-main.sh` case 27: a real-shaped gated push with no landing record is refused before ci-merge, and
`COHORT_OK` lands it - red when the gate's call is removed (shown 2026-10-18). `tests/tooling/test_measure_reports.py`: the fresh
rate, and 907 not read as pinned.

### T01 verification

`make quick`; `make hooks-test`; the three tooling test files; `make cohort` prints its fresh rate and keeps its exit code;
`make cohort-landing` on this clone, then the push (SC-001, SC-004); `make cohort-seeds` (SC-003); `make done` once at the end.

### T01 measurements

m:fresh-block-cost (`specs/386-landing-cohort/fresh_cost.sh`, recorded in `measurements.json`): the per-fix cohort cold, median wall
time - 16 maps (FRESH=0) 57.2 s, 18 maps 58.1 s, 20 maps (a 4-seed block) 56.7 s; load 3.2-10.8 with other sessions running.
