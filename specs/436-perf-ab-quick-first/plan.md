# Implementation Plan: perf-ab quick first

**Branch**: `436-perf-ab-quick-first` (no branch; `main` in the clone) | **Date**: 2026-10-27 | **Spec**: `spec.md`

**Input**: `spec.md`, `request.md` (the GM's words and the proposal he approved).

## Summary

`make perf-ab` gains three forms decided by what is compared - quick (one seed at one size, the default seed 25 at 40
households, 6 runs a version), subset (more than one seed or size), full (`FULL=1`, today's sweep) - with the arms alternated
A B / B A, wall and CPU time each with its best and spread, an A/A noise floor per quick form, and a refusal of every
non-quick run that no quick run of the same two engines preceded (`PERF_AB_QUICK_OK="<reason>"` overrides, recorded).

## Technical Context

**Language/Version**: Python 3.14. **Testing**: pytest under `make quick` / `make test-file` (`tests/tools/test_perf_ab.py`).
**Project Type**: tooling (`l7r/diagram/tools/perf_ab.py`, `Makefile`, docs). **Single-artifact target**: the reference
hamlet at seed 25, 40 households (the quick form's default).

## Performance bookends

None: this feature changes no engine code a roll runs; it changes how two engines are timed.

## Constitution Check

- **I, II**: N/A - no UI. **III, IV, V, VII, VIII, IX, XI**: N/A - no pool content, no SOURCE blocks, no in-world writing.
- **VI. Verify Before Reporting Done**: PASS - `tests/tools/test_perf_ab.py` (the forms, the order, the refusal and its
  escape, the floor), `make quick`, `make cover-changed`, the landing's `make done`; a real quick A/B and an A/A run timed.
- **X. Python Discipline**: PASS - ruff, pyrefly, 100% coverage on `perf_ab.py`; functions under 100 statements.
- **XIII. No Known Regressions**: PASS - no map is rolled differently; the full form keeps today's sweep.
- **The guard doctrine** (`docs/guards.md`): the refusal names the compliant command and has an escape with a reason of two
  words or more, recorded in the guard log (`scripts/pages/escape_log.py`, the Python escape every refusal in Python uses).

## Decisions

**D1 - The form is the count compared (FR-001).** `--seeds` and `--households` are comma lists (defaults `25` and `40`);
one seed and one size is QUICK (`N` default 6), any more is SUBSET (`N` default 3), `--full` is FULL (`N` default 3, the
seeds and sizes `make perf SCALING=1` rolls). The Makefile passes `SEEDS=`, `HOUSEHOLDS=`, `FULL=`, `N=`, `AA=`.

**D2 - How quick and subset roll.** One worker process per version, started in that version's detached worktree
(`python3 -c` with the worktree as its working directory and first on `sys.path`), warmed by one untimed roll as `make perf`
warms its first, then asked for each run in turn over its stdin: it calls that version's own
`perf_snapshot.measure((seed,), households=size)` and answers with each leg's per-stage wall and CPU seconds (`stages`,
`cpu_stages`) or its refusal. After the timed runs, each worker counts calls once (`perf_snapshot.count_calls`). The code
that times is the version's own, so an older engine is timed as `make perf` timed it; both exist in every engine since
feature 435's start (d2ce4e79c). FULL keeps today's path: `make perf SCALING=1` in each worktree, a fresh process a run.

**D3 - The order (FR-003).** Run i takes the versions A, B when i is even and B, A when it is odd.

**D4 - Time (FR-003).** A leg's wall time is its stages' sum, its CPU time its `cpu_stages`' sum, each to the hundredth; per
seed and size each version's best and spread (worst less best) of both, the change between versions in each, and calls.

**D5 - The record of quick runs (FR-004).** A quick comparison writes
`<git common dir>/perf-ab/quick/<key>.json` (local to the clone, never committed), `<key>` the two engines' keys sorted
(so A against B and B against A are one pair), each key `pipeline.render_cache.engine_fingerprint(<worktree>)` - the
engine's Python by what runs, docstrings and comments stripped since feature 426 - holding the seed, size, N, the commits
and the table.

**D6 - The refusal (FR-005, FR-007).** Any run that is not quick looks up D5's record for its two keys after the worktrees
are made and before the first roll; with none, and no `PERF_AB_QUICK_OK`, it prints the refusal - what was asked, that no
quick comparison of these two engines is on record, and the command `make perf-ab A=<a> B=<b>` (the quick form at the
first seed and size asked) - and exits 2. `PERF_AB_QUICK_OK` goes through `escape_log.escape` (a reason of two words or
more, logged as guard `perf-ab-quick-first`; too short a reason refuses). A timing never refuses: the comparison itself
still exits 0.

**D7 - The noise floor (FR-006).** `AA=1` makes one worktree of A (default HEAD), starts two workers on it (D2), alternates
them as D3 does, and writes `<git common dir>/perf-ab/floor/<seed>-<households>-<n>.json` with each worker's best and
spread and the change between them, wall and CPU, and when it was taken. A quick comparison prints the floor of its seed,
size and N beside its table - "floor (A/A, taken <utc>): wall X%, CPU Y%" - or, where none is recorded, the `make perf-ab
AA=1 ...` command that takes it. AA=1 is itself a quick-form run and needs no record.

**D8 - Docs (FR-008).** `docs/performance-checklist.md` question 5 and its tools table: the quick form while iterating, a
subset or full run once before landing, the floor read beside a quick result. `docs/guards.md` gains the refusal's row with
its escape. The Makefile's help line names the forms.

## Task approaches

### T01 Approach (checklist part A)

1. **The goal, in the world.** A performance change is compared quickly while it is iterated on, and the slower comparisons
   come only after a quick one of the same engines.
2. **The constraints.** FR-001 to FR-008; D1-D8.
3. **Where each comes from.** G: the GM 2026-10-27 (`request.md`); O: feature 435's A/B runs, 8.2 min each, measured
   2026-10-27 (the file times of feature 435's T04 and T08 A/B logs).
4. **Do they describe the world here?** Yes: `perf_ab.py` as feature 435 landed it.
5. **The order.** One task.
6. **The exits.** Green: landed with its tests, a real quick A/B and an A/A run recorded in `research/t01-evidence.md`.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** A quick A/B of HEAD~ against HEAD at seed 25, 40 households, its wall time stated; the refusal seen
   on a subset run with no record.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the forms, order, refusal, floor | `tests/tools/test_perf_ab.py` |
| the quick form's wall time | a real `make perf-ab A=HEAD~1` |

**Performance work?** No - it times engines; it changes none.

## Project Structure

- `l7r/diagram/tools/perf_ab.py`; `tests/tools/test_perf_ab.py`; `Makefile` (`perf-ab`).
- `docs/performance-checklist.md`; `docs/guards.md`.

## Complexity Tracking

None.
