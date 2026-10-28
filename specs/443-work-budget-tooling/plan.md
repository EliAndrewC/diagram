# Implementation Plan: the work-budget tooling

**Branch**: `443-work-budget-tooling` (no branch; `main` in the clone) | **Date**: 2026-10-28 | **Spec**: `spec.md`

**Input**: `spec.md` (the round arbiter's accept at the round cap, ask:443-spec-round-3), `request.md`.

## Summary

Counters of basic operations in the geometry layer, the placement registry and every stage's candidate loops, attributed per
stage and per function and dropped under
`python -O`; `make work-budget` and its standing record; the inertness check; the budget table, `make budget-change` and the
ratchet at the push; the `work-budget` agent, its rubric, bundles and two proving fixtures; the phase checklist and its
landing check; the Rust-tooling inventory and its check.

## Technical Context

**Language/Version**: Python 3.14, bash. **Testing**: pytest (`tests/settlement/_geom/`, `tests/overlap/`,
`tests/hamletgen/test_driver.py`, `tests/tools/test_work_budget.py`, `tests/tooling/`), `tests/hooks/test-*.sh` through
`make hooks-test`. **Project Type**: engine instrumentation and tooling.

**Single-artifact target**: the reference hamlet, seed 25 (`perf_snapshot.REFERENCE`), at 40 households.

## Performance bookends

`make perf LABEL=443-start` before the first counter lands and `LABEL=443-end` before the last push (a record, FR-012 of
feature 435: nothing refuses on a time). The counters must add no Python call (SC-001): the push's call-count review
(`make perf-review`, feature 427 T03) judges the pair as for any engine change.

## Constitution Check

- **I-V, VII-IX, XI**: N/A - no map content, no setting prose.
- **VI**: PASS - each task's tests, `make quick`, `make hooks-test`, the landing's `make done` and `make cohort-landing`.
- **X**: PASS - 100% coverage on every new or changed module; no function past 100 statements; `l7r/diagram/settlement/_geom/
  indexes.py` (887 lines) gains at most about 30 lines and stays under 1,000 (D2).
- **XII**: N/A - no rendering decision; the counters change no map (FR-004 proves it).
- **XIII**: PASS - the counters change no manifest; `make counters-inert` and the landing cohort hold it.
- **XIX**: N/A - nothing placed, moved or removed.
- **The guard doctrine**: every new refusal (D5, D6, D7, D10, D12, D13) has a test companion run by `make hooks-test`, names
  the command that gets past it (D12: `make tick` of the box's line, or the checklist copied from the template; D13: the row
  to add to `dev/rust-tooling.md`), is proven to fire by deleting it, and is listed in `docs/guards.md` (FR-012).

## Decisions

**D1 - The counters** (FR-001): a leaf module `l7r/diagram/work_counts.py` holding `OPS: dict[str, int]` (a
`collections.defaultdict(int)`) and the kind names: `pt_test`, `seg_test`, `dist`, `index_query`, `index_examined`,
`candidate`, `placed`, `dropped`, `moved`. A counting site is one line, `if __debug__: OPS["<kind>@<function>"] += <n>`,
the key a string literal naming its kind and the function it sits in (so the counts are read by kind and by function): a dict
subscript and an add are C operations, not Python calls, so `sys.monitoring`'s PY_START count (the push's call guard) does
not move; `<n>` is 1, or the element count of a vectorized call (`len(pts)`). The module has no imports of the engine.

**D2 - Where they count** (FR-001):
- `settlement/_geom/primitives.py`: `point_in_poly` and `points_in_poly` (`pt_test`), `segments_cross`, `seg_intersect`,
  `ring_touches`, `ring_meets_ellipse` (`seg_test`), `seg_dist`, `seg_dists`, `poly_seg_dist`, `edge_dist` (`dist`), the
  chain tests (`seg_test`, per chord examined).
- `settlement/_geom/indexes.py`: `PointGrid.near`, `RingIndex`'s and `KeepoutGrid`'s queries - `index_query` per call,
  `index_examined` per entry returned.
- `overlap/registry.py` (the placement registry, through which every footprint is admitted): `Standing.admits` and
  `conflicts` (`candidate`, and `index_examined` per extent compared), `_add` (`placed`), `forget` (`dropped`), `rerecord`
  (`moved`).
- Every stage's candidate loops, found by walking each stage's code (the stage function and every module it reaches, from
  `STAGES`) for every loop that tries a site - submits it to `Standing.admits` or `conflicts`, or tests it against the `_geom`
  layer - and recorded in `research/candidate-loops.md` with that search space, the search command and its date; each gets a
  `candidate@<function>` increment per candidate tried. `make perf-fanout`'s anchors at 40 households (feature 427 T01) are
  then a cross-check that the walk missed no hot loop. A stage the walk finds no candidate loop in is recorded as such.
- Inline arithmetic outside these sites is not counted; the standing record prints each stage's Python calls beside its
  counts (D4), so a stage whose calls are large against its counts shows it. A rebuilt phase counts every inner loop (444's
  checklist box 5), and MODE AUDIT rules UNCOUNTED on any it leaves out (S5).

**D3 - Attributed per stage** (FR-002): `driver._run_stages` takes, under `if __debug__:`, a copy of `OPS` before each stage
and stores the difference, by kind and by function, in `work_counts.BY_STAGE[<stage name>]`; `work_counts.reset()` clears both at the start of a roll.
Nothing enters the manifest.

**D4 - `make work-budget`** (FR-003): `l7r/diagram/tools/work_budget.py`. Seeds: 25 and the cohort's pinned seeds by default
(`cohort_audit`'s pinned rows), `SEED=` one seed; sizes 10, 20, 40 and 80 (`beyond_the_band()` past the band). Per roll it
records each stage's `BY_STAGE` counts, its things placed (`perf_profile.placed_counts` across the stage), its Python calls
(`perf_snapshot.count_calls`' monitor) and its seconds. It prints, per stage, the counts in total and per thing placed (a
stage that places nothing: its whole-stage figure, Edge Cases), the exponent from 20 to 80 households (a log-log fit; a size a
seed refused is named and left out), the budget and the ratio, then the whole roll. It writes the run to
`dev/work-budget/<stamp>-<engine code id>.json` (the docstring-blind code id, `scripts/gates/codeid.py`), the engine commit
recorded inside it, and regenerates
`dev/work-budget.md` from the newest run and `dev/work-budget.json`.

**D5 - `make counters-inert`** (FR-004): rolls seed 25 at 20 households in two subprocesses, `python3` and `python3 -O`, each
writing its manifest to a temporary file, and refuses unless the two are byte-identical, naming the first key that
differs. `make done` runs it as a step. The test (SC-002) gives it a stub counter that writes to the manifest and sees it
refuse.

**D6 - The budget table** (FR-005): `dev/work-budget.json` - `{"program": {"ops_at_40": null, "exponent": null}, "stages":
{"<stage>": {"status": "unbudgeted"}}}` for every stage of `STAGES` at landing; a budgeted stage holds `per_thing`,
`exponent`, `derivation` (a path) and `verdict` (the ledger row's subject of its MODE BUDGET), an accepted one adds
`accepted` (its counted operations at 40 and 80 households). `scripts/budget_change.py` (`make budget-change PHASE= TO=
[EXPONENT=] WORDS=`, `make budget-set PHASE= PER_THING= EXPONENT= DERIVATION= VERDICT=` and `make budget-program`) is the one
writer:
- `budget-set` refuses unless the stage is `unbudgeted` (its message names `make budget-change` for a budgeted one) and the
  verdict file it names reads SOUND;
- `budget-change` refuses without WORDS, and logs each change to `dev/work-budget-changes.jsonl` with the words;
- the words are checked by a hook, `scripts/hooks/budget-change-hooks.sh` (PreToolUse on Bash), which matches an invocation
  of `make budget-change` or `make budget-program` and refuses it unless WORDS passes `hm_approval.problem` against `hm_approval.gm_messages` of the
  session's transcript - the check the approval line meets (a make target cannot read the transcript; a hook can).
- `make budget-program OPS_AT_40= EXPONENT= WORDS=` sets the program's whole-roll budget (444 FR-002: the GM approves the
  target), under the same WORDS hook and log;
- `dev/work-budget.json` joins the guard files (`guard-file-hooks.sh`): an edit other than through these targets needs
  `GUARD_EDIT_OK`.

**D7 - The ratchet** (FR-006): `make work-budget-review` (`work_budget.review`), run by `sync-with-main.sh` beside `make
perf-review`, with a test seam `CI_WORK_BUDGET_REVIEW` read only in a fixture as the others are. It does nothing while no
stage is accepted. Otherwise, on a push carrying engine code, it requires a `dev/work-budget/` run at the pushed engine's code
id, and refuses when an accepted stage's counted operations at 40 or 80 households exceed its `accepted` figure or its budget,
naming the stage, the figures, `make work-budget` and `make budget-change`. No arbiter accept clears it.

**D8 - In view** (FR-007): `scripts/land.py` prints `dev/work-budget.md`'s whole-roll line, every stage's status and the
stages that moved since the previous run, when the landing carries engine code; `scripts/speckit-todo.py` prints the same
summary under feature 444's row.

**D9 - The agent and its rubric** (FR-008): `.claude/agents/work-budget.md` (model `opus`, effort high, `omitClaudeMd: true`,
tools Read, Grep): the two modes, their questions and verdicts as FR-008 states them, each verdict a first line the ledger
reads. `docs/work-budget-rubric.md` holds S1-S7 and the homestead reference worked out factor by factor (S7: candidates per
house from the seat spacing within reach, neighbors per candidate from the index cell, parts per house from the homestead
program, slack at most 2). The agent joins `scripts/container/append-system-prompt.md`'s list, the wave-job list there,
`tests/test_agent_models.py`'s tier table and `docs/reviews.md`'s occasions (MODE BUDGET at a budget's setting, MODE AUDIT at a
phase landing).

**D10 - The bundles** (FR-008): `scripts/reviews/work_budget_bundle.py` (`make work-budget-bundle MODE=budget|audit
PHASE=<stage> [DERIVATION=<file>]`) copies to `/tmp/l7r-check/work-budget-<mode>-<stage>/` with a MANIFEST. A budget bundle
holds the derivation, the stage's contract (its manifest keys read and written, from the derivation) and the rubric; it refuses
when the derivation contains a fenced block of Python, a path under `l7r/` or a figure tagged as a current count (`calls`,
`ops` beside a number). An audit bundle holds the stage's modules, the newest run's counts for the stage at each size by kind and
by function, the stage's `make perf-fanout` chains (the callers above each counted function) and its budget. 444 FR-007 adds `MODE=table`.

**D11 - The two fixtures** (FR-009): `tests/fixtures/work-budget/funnel/` (the homesteads seat funnel as it is: the
derivation written from trial 439's measured funnel, `specs/439-fewer-envelope-probes/research/funnel.md`) and
`tests/fixtures/work-budget/grid-placer/` (a textbook grid-indexed placer: a derivation and a 40-line placer). Each is bundled
and dispatched once; the agent's first line goes to `verdict.txt` beside it and its row to the ledger. `tests/tools/
test_work_budget_fixtures.py` holds the funnel's verdict to LOOSE or OVER and the placer's to SOUND or WITHIN.

**D12 - The phase checklist** (FR-010): `.specify/templates/phase-checklist.md`, the eight boxes. `scripts/land.py`'s cheap
refusals add one: a feature-444 task whose text carries `phase: <stage>` lands only when `specs/444-*/phases/<stage>.md`
exists, holds the eight box lines of the template and has each ticked; the refusal names the file and the first missing or
unticked box.

**D13 - The inventory** (FR-011): `dev/rust-tooling.md`, one row per check from the design's section 7, each with its key
(the script's path or the make target's name). `scripts/gates/check-rust-tooling.py` (`make rust-tooling`, and a step of `make
hooks-test`) reads every tracked file (`git ls-files`) outside `specs/`, `research/`, `dev/` records and `pool/` and lists
each that imports `ast`, `tokenize`, `inspect` or `symtable`, calls `compile(`, or reads `.py` files (`"*.py"`, `.py"`,
`suffix == ".py"`, `-name '*.py'`) - the engine's own readers (`gencache.engine_files()`, the placement-stages page, the claims
reader) included - and every Makefile recipe whose text runs ruff, pyrefly, pytest, coverage, testmon or vulture or matches
the same `.py` patterns; it fails on any whose key has no row, naming the row to add. Its test runs it on the real tree
(finding `scripts/gates/check-file-scale.py`, the arbiter's note) and on scratch readers of each kind with no row.

## Task approaches

The tasks, in landing order: T01 the shared counters and their attribution (D1, D3, D2's shared sites); T09-T12 the stages'
candidate loops by family (D2) - the families are the whole of `STAGES`, every stage in exactly one: the 23 stages listed on
2026-10-28 by `grep -n "STAGES = (" -A60 l7r/diagram/hamletgen/driver.py`, T09 six (water_frame, field, sink, waterward,
pond_stock, pond_bank), T10 seven (seat, homesteads, appurtenances, burial, lane_wells, sties, washing), T11 three (track, web,
crossings), T12 seven (hinterland, woodland, windbreak, bamboo, frame, notice, labels); a stage added to `STAGES` later joins a
family before its counters land; T02 `make work-budget`, the standing record with
today's figures, and `make counters-inert` (D4, D5); T03 the budget table, `budget-set`, `budget-change` and its hook (D6);
T04 the ratchet and the record in view (D7, D8); T05 the agent, its rubric, bundles and fixtures (D9-D11); T06 the phase
checklist and its landing check (D12); T07 the Rust-tooling inventory and its check (D13); T08 the docs and the closing report.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T09 to T09 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T10 to T10 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T11 to T11 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T12 to T12 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
<!-- plan-archive: T08 to T08 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
## Project Structure

- Engine: `l7r/diagram/work_counts.py` (new), `l7r/diagram/settlement/_geom/primitives.py`, `l7r/diagram/settlement/_geom/
  indexes.py`, `l7r/diagram/overlap/registry.py`, `l7r/diagram/hamletgen/driver.py`.
- Tools: `l7r/diagram/tools/work_budget.py` (new); `scripts/budget_change.py`, `scripts/reviews/work_budget_bundle.py`,
  `scripts/gates/check-rust-tooling.py`, `scripts/hooks/budget-change-hooks.sh` (new); `scripts/land.py`,
  `scripts/speckit-todo.py`, `scripts/sync-with-main.sh`, `Makefile`, `.claude/settings.json`.
- Records: `dev/work-budget.json`, `dev/work-budget.md`, `dev/work-budget/`, `dev/work-budget-changes.jsonl`,
  `dev/rust-tooling.md`.
- Agent and docs: `.claude/agents/work-budget.md`, `docs/work-budget-rubric.md`, `.specify/templates/phase-checklist.md`,
  `docs/guards.md`, `docs/reviews.md`, `scripts/container/append-system-prompt.md`, the root `CLAUDE.md`'s performance line.

## Complexity Tracking

None.

<!-- plan-archive: T13 to T13 moved to plan-done.md, 2026-10-28 (feature 375 FR-044) -->
