# Implementation Plan: Faster iteration - no wasted waits, no re-rolled seeds

**Branch**: `426-faster-iteration` (no branch; `main` in the clone) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/426-faster-iteration/spec.md` (reviewed FAITHFUL, round 2)

## Summary

Five tooling changes, each with its own task and landing (`make land-tooling` for the scripts; the cache key is engine-adjacent
code under `l7r/diagram/pipeline/` and lands through `make land`):

1. `make land` fails fast when the claims gate refuses for a reason waiting cannot cure (D1).
2. Code is hashed docstring- and comment-blind at every staleness key that should be, by one shared function, after an audit of
   every code-hashing site (D2, D3, the audit table).
3. `make cohort` gains `FAILED_FIRST=1`, `LAST_FAILED=1`, `EXITFIRST=1`, and reports how many seeds it served and rolled (D4).
4. `make probe` compares a worktree's cohort, fresh block and pool against HEAD's stored verdicts (D5).
5. `make task-add` writes the D35 red exit and the alone-off table into every new plan section (D6).

## Technical Context

**Language/Version**: Python 3.14 (the container's), bash for the make recipes

**Primary Dependencies**: the standard library (`ast`, `hashlib`, `concurrent.futures`); the project's own `rollcache`,
`gencache`, `cohort_audit`, `scripts/land.py`, `scripts/task-add.py`

**Storage**: the roll store (`.gencache/rolls`, shared by a clone's linked worktrees), `dev/cohort-log/*.json` (the cohort's
per-run records), a new probe-baseline store under the clone's common git dir (`.git/probe-baselines/`, untracked)

**Testing**: pytest through `make test-file` / `make quick`; the tooling suites in `tests/tooling/`; `make cache-audit` for the
key change; `make hooks-test` where a guard's message changes

**Target Platform**: the dev container (Linux)

**Project Type**: build and test tooling

**Performance Goals**: SC-001 (a docs-only edit re-rolls no seed), SC-002 (no claims wait when nothing can arrive), SC-003
(EXITFIRST stops at the first failing seed), SC-004 (HEAD's block rolled at most once per engine key)

**Constraints**: a cache must stay exact - an executable edit always re-rolls (FR-003, SC-006); no map changes

**Scale/Scope**: ~10 code-hashing sites audited; 5 commands touched

**Single-artifact target**: not a generator change. The one artifact the key change is proven on first is the reference roll
(Inashiro, seed 4): rolled, a docstring added to a function it executes, rolled again - served.

## Performance bookends

Not a generator change: maps are byte-identical by construction (the key changes what is served, never what is rolled). The
measurement that matters is the cohort's own count of seeds rolled and served (D4's summary line), taken before and after the
key change on the same docs-only edit (SC-001), recorded in `research.md`.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content, no SOURCE blocks, no in-world writing.
- **VI. Verify Before Reporting Done**: PASS - each task lists its verification (tasks.md): its tests red without the change and
  green with it, `make quick`, the landing's `make done`; the key change adds `make cache-audit` and the cohort before/after count.
- **X. Python Discipline**: PASS - ruff, ruff format, pyrefly, 100% coverage on the touched modules (`gencache`, `rollcache`,
  `cohort_audit`, the new `codeid` module); red-green per FR; functions under 100 statements (`cohort_audit.main` grows: the
  ordering and early stop go in their own functions, D4); no file past 1,000 lines (`cohort_audit.py` is ~430, `land.py` ~600).
- **XII**: N/A - changes nothing a generator asserts about the world.
- **XIII. No Known Regressions**: PASS - baseline: `make cohort-landing` at HEAD before the key change (54 of 54 on main at
  2026-10-26) and the pool manifests as committed; after it the same, byte-identical manifests, and `make cache-audit` green.
- **XIX**: N/A - places nothing.

## Decisions

**D1 - the claims wait ends when nothing can arrive (FR-001, FR-002).** `land.py`'s `wait_for_claims` already reads the claims
gate's refusal each poll. It returns at once, naming every refusal with its cure, when ANY part of the refusal is one no
in-flight check can cure: an INTRODUCED finding, a known drift awaiting an arbiter's accept, or anything else only an edit or a
ruling cures (the next `make land` reads it); the owed claims, if any, are listed beside it. It also returns at once on an owed
claim when no claims check is IN FLIGHT. In flight is seen, not inferred: `make claims-bundle` and `make claims-triage` write a
marker (`.git/claims-in-flight/<bundle>`, the bundle's path and the time) and `make claims-checked` / `make claims-triaged`
remove it; a marker older than `CLAIMS_WAIT_S` is stale and ignored. Only while a live marker exists does the landing wait, as
today. A carry is filed as today. Each message names its cure (`make claims-bundle OWED=1` and dispatch impl-drift for an owed
claim; `make arbiter-ask ... REVIEW=claims:<key>` for an introduced known drift; fix the code or the claim otherwise), per FR-011.

**D2 - one docstring-blind code id (FR-003, FR-004).** A new `l7r/diagram/pipeline/codeid.py` holds the normalization
`gate-stamp.py`'s `content_id` already does: parse, drop every docstring (module, class, function, and the bare string after an
assignment that carries a constant's claim), dump the AST without attributes (so comments, blank lines and formatting do not
count), hash. `gate-stamp.py` calls it instead of its own copy (one copy of the rule). A file that does not parse is hashed by its
bytes, as today.

**D3 - the roll and render keys use it, content areas excepted (FR-003, FR-005).** `gencache._split_sources` keys each function
on `codeid` of its node and the module's top level on `codeid` of the module with function bodies taken out, replacing the raw
line text. `render_cache.engine_fingerprint` uses `codeid` for `.py`. Both keep hashing by BYTES the files whose docstrings are
an artifact's content: `l7r/diagram/interactive/**` (the class registry's docstrings are the modal text, `_base.py`
`cls.__doc__`; the page writer's own text), the same area `gate-stamp`'s `RAW_AREAS` holds raw. The rule and its reason sit at the
point of change in each, naming the other.

**The audit (FR-004)** - every site that hashes code to decide whether work is stale, read 2026-10-26:

| site | what it keys | today | ruling |
|---|---|---|---|
| `pipeline/gencache.py` `_split_sources` | every roll (cohort, gate) and every pool map | raw source lines | **change** to `codeid` (D3); `interactive/` raw |
| `pipeline/render_cache.py` `engine_fingerprint` | every pool render | raw bytes | **change** to `codeid` for `.py` (D3); `interactive/` and the page assets raw |
| `scripts/gates/gate-stamp.py` `content_id` | `make done`'s stamp | docstring-blind | keep; its normalization moves to `codeid` (D2); `RAW_AREAS` stay raw |
| `ci/delta.py` `engine_key` | the paid gate's delta | docstring-blind | keep |
| `scripts/measure/cohort_known.py` `engine_key` | which cohort records are the same engine | docstring-blind | keep |
| `ci/state.py` `tooling_hash` | reuse of the tooling tests | raw bytes, "deliberately: a Makefile comment IS a Makefile change worth one run" (its docstring) | **change** `.py` files to `codeid` except each file's MODULE docstring (scripts print it as usage: `regen.py`, `building_programs.py`, and a tooling test may assert on it); function and class docstrings are not read by any tooling test (grep for `__doc__`/`getdoc` under `scripts/` and `tests/tooling/`, research R3), so dropping them reuses no stale pass; non-`.py` (the Makefile, whose comments and `##` lines build `docs/make-targets.html`) stays raw - the reason written at the point of change |
| `ci/gate_config.py` `config_hash` | how the gate's tests run | raw bytes | **change** `.py` (conftest and the machinery) to `codeid`; lockfiles and config files raw |
| `scripts/record/record_cache.py` `code_sha` | a parse cache's extractor code | raw bytes | **change** to `codeid` for `.py`: an extractor's docstring does not change what it extracts |
| `pipeline/record_build.py` `fingerprint` | the record's built site | raw bytes | keep - the build reads the engine's research claims, which live in docstrings |
| `tools/claims.py`, `scripts/record/claims*.py` fingerprints | which claims owe a check | claim text and code separately | keep - the claim text IS what is checked; out of FR-003 per the spec's edge case |
| `scripts/gates/plan_*.py`, `scripts/hooks/lib/hm_*.py`, `scripts/record/*` other hashes | plan blocks, transcripts, record pages | text, not code | not code-staleness keys; no change |

**D4 - the cohort's iteration modes (FR-007, FR-008, FR-012).** `cohort_audit` gains `--failed-first`, `--last-failed` and
`--exitfirst` (`make cohort FAILED_FIRST=1 LAST_FAILED=1 EXITFIRST=1`):
- "last run": the newest `dev/cohort-log/` record of this clone with the same seed block (count, first seed, households, fresh
  block); its failing seeds. None: say so and roll all (the edge case).
- ordering and selection in one function (`ordered_specs`); the early stop in another (`roll_until_failure`), which submits in
  order to the pool, and on the first failing result cancels what has not started, waits for what has, and reports the count
  left unrolled; exit 1.
- a run under `--last-failed` or `--exitfirst` writes its record marked `partial`, which `cohort_gate.landing_shaped` refuses, so
  it can never stand as a landing (FR-008); `cohort-landing` passes none of the three.
- every run prints `rolled N, served M` from `rollcache.obtain`'s `how`, the measurement for SC-001 and FR-012. FR-012 is pinned
  through the landing path itself: a test runs a full `make cohort N=48 FRESH=0`, then `make cohort-landing` (its own recipe, its
  seed block, `cohort_gate.py check`) at the same code, the roll stubbed to count, and asserts the landing rolled zero; and the
  same with the first run in a linked worktree of the clone.
- a record from a run that rolled only some seeds (`--last-failed`, or `--exitfirst` stopping early) CARRIES FORWARD the earlier
  failures it did not roll, as pytest's last-failed list keeps tests not run until they pass: its `failed` list is the seeds it
  saw fail plus the previous record's failures it never rolled.

**D5 - `make probe` (FR-009).** `scripts/measure/probe.py`, `make probe [WT=<worktree>] [EXITFIRST=1]`:
- in `WT` (default: the current tree) it runs the landing cohort, the fresh block and `make map` for each live hamlet;
- the fresh block is HEAD's (`fresh-from` derived from HEAD's engine key, as `make cohort` derives it), so HEAD and the probe roll
  the same seeds;
- HEAD's verdicts per block are read from `.git/probe-baselines/<engine key>-<block>.json`; absent, HEAD is rolled once in a
  detached worktree at HEAD and stored (SC-004);
- it prints EVERY seed's verdict beside HEAD's, a difference marked (new failure, fixed, changed failure, same failure, same
  pass), so the seed being worked on shows whether or not it moved; and per pool manifest, each changed field path, lanes
  compared as drawn (rounded points);
- `EXITFIRST=1` passes `--exitfirst-against <baseline>` to the cohort: stop at the first seed worse than HEAD's.

**D6 - the plan section template (FR-010).** `task-add.py` writes, when no `SECTION=` is given, a section `### {T} (...)` with an
Approach bullet, a `| step | alone off: fixed/pinned | fresh block vs HEAD | pool manifests moved | last resort |` table header,
and the checklist part A whose item 6 reads: "FR-008 green: landed with its fresh rate. Red: the failing seeds recorded and the
task set down, a claim that it cannot be placed correctly ruled through `make arbiter-ask` (D11, D35)." Given a `SECTION=` whose
item 6 lacks `make arbiter-ask`, it prints that wording as a warning and files the section anyway.

## Task approaches

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** A code edit that runs nothing changes no key.
2. **The constraints.** D2; FR-003, FR-004.
3. **Where each comes from.** the GM 2026-10-26 ("omitting docstrings when hashing code"); feature 133 T11's rule.
4. **Do they describe the world here?** Measured by: `gate-stamp.py`'s `semantic_bytes` already held the rule; moved, not rewritten.
5. **The order.** before T03 and T04, which use it.
6. **The exits.** green: landed with T01, T03, T04; red: the failing tests recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
### T09 Approach (checklist part A)

1. **The goal, in the world.** The feature closed with its numbers shown to the GM.
2. **The constraints.** the close.
3. **Where each comes from.** the constitution's close.
4. **Do they describe the world here?** Measured by: the feature report.
5. **The order.** last.
6. **The exits.** green: the report written; red: the missing items named and the close set down.
7. **The search smell.** None: one change, its tests first.
8. **The budget.** One landing.
9. **Done, measured.** Its verify line in tasks.md passes.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 part B (2026-10-26T12:15Z)

The trigger: red-gate@2026-10-26T12:13:24Z, the second red gate in a row on 426 T01-T04's landing.

1. **What exactly is refusing?** Gate 1 (11:53): seven hook and content-cache tests - their fixture repos copy `scripts/` but the
   code id sat under `l7r/`, so `gate-stamp.py` could not load it there. Gate 2 (12:13): the 100% floor, six lines of
   `gencache._split_sources`' raw (`interactive/`) branch no unit test ran.
2. **A3 again.** O: the gate's fixtures (they copy the scripts tree whole); the coverage floor over the whole engine.
3. **A4 again.** It describes the change: the module's home decided which fixtures carried it; `cover-changed` measured
   `tests/pipeline` only, the full floor the rest.
4. **Moving something placed earlier to suit something later?** The module moved to `scripts/gates/` beside `gate-stamp.py`,
   where the rule always lived, an engine shim at `l7r/diagram/pipeline/codeid.py`; no behavior changed.
5. **Tuning or changing?** Neither: two distinct defects, each fixed once (the move; one unit test).
6. **The one-sentence test.** "The code id lives where every fixture carries it, and its raw branch is tested" - no question.
7. **The next step is a measurement.** `make land` again: hook suites, the shim and `gencache` at 100% under the full floor.
8. **Routes measured?** One route each: the move (hook suites green), the test (coverage of the branch).
9. **After a ruling.** The round arbiter ruled continue (red-gate@2026-10-26T12:13:24Z); a third distinct red goes back to it.

## Project Structure

### Documentation (this feature)

```text
specs/426-faster-iteration/
├── request.md     # the GM's words, verbatim
├── spec.md        # reviewed FAITHFUL
├── plan.md        # this file
├── research.md    # the audit's readings and the before/after counts
├── quickstart.md  # how to verify each part
└── tasks.md       # /speckit-tasks
```

### Source Code (repository root)

```text
l7r/diagram/pipeline/codeid.py        # new: the docstring-blind code id (D2)
l7r/diagram/pipeline/gencache.py      # _split_sources on codeid, interactive/ raw (D3)
l7r/diagram/pipeline/render_cache.py  # engine_fingerprint on codeid (D3)
l7r/diagram/ci/state.py               # tooling_hash (audit)
l7r/diagram/ci/gate_config.py         # config_hash (audit)
l7r/diagram/tools/cohort_audit.py     # the three modes and the rolled/served count (D4)
scripts/gates/gate-stamp.py           # content_id calls codeid (D2)
scripts/gates/cohort_gate.py          # a partial record is not landing-shaped (D4)
scripts/record/record_cache.py        # code_sha on codeid (audit)
scripts/land.py                       # the claims wait ends when nothing can arrive (D1)
scripts/measure/probe.py              # new: make probe (D5)
scripts/task-add.py                   # the section template (D6)
Makefile                              # cohort's three variables, probe
tests/pipeline/test_codeid.py, tests/pipeline/test_gencache*.py, tests/tooling/test_land*.py, tests/tools/test_cohort_audit*.py,
tests/tooling/test_probe.py, tests/tooling/test_task_add*.py
```

## Complexity Tracking

None.
