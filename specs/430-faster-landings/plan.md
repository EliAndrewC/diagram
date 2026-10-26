# Implementation Plan: Faster landings - the gate, the push and the review rounds

**Branch**: `430-faster-landings` (no branch; `main` in the clone) | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/430-faster-landings/spec.md` (reviewed FAITHFUL, round 5; amendment 1)

## Summary

Seven tooling changes, one task each, each landed through `make land` (every one touches the gate's machinery, `scripts/gates/`
or `l7r/diagram/ci/`, so `land.py`'s `GATE_MACHINERY` sends it through a gate):

1. The gate's planner stays incremental when only pool manifests changed, adding the tests that read them (D1).
2. A doc file under `tests/` adds nothing; another non-module file selects its own directory's tests and the tests that name it;
   one directly under `tests/` plans full (D2).
3. `cover_changed.py` asks every line of each changed module, with the tests the gate's floor counts for it (D3).
4. The push's claims, entry and cohort gates exit at once on a delta holding nothing they judge, cache a pass on the delta's
   content, and run side by side (D4).
5. The plan-lint runs before every plan review bundle is written, with three new checks, and an approach block that decides
   nothing owes no review (D5).
6. A known drift lands without an arbiter round, recorded and listed in `make gm-review`; a triage bundle of 3 or fewer claims
   goes straight to impl-drift (D6).
7. `make decide` and `make plan-delta` name an owed claims triage so it is dispatched beside the review; a guard test pins that
   decide-first lets it through (D7).

## Technical Context

**Language/Version**: Python 3.14 (the container's), bash for the gates and make recipes

**Primary Dependencies**: the standard library; the project's `l7r/diagram/ci/incremental.py`, `scripts/gates/cover_changed.py`,
`scripts/gates/plan_lint.py`, `scripts/gates/plan_gate.py`, `scripts/record/claims.py`, `scripts/record/claims_carry.py`,
`scripts/sync-with-main.sh`, the three `*-gate.sh` push gates, `scripts/land.py`

**Storage**: the gate baseline (`<git dir>/gate-baseline/`, read only); a new push-gate pass cache under `<git dir>/push-gates/`
(untracked); the feature's `gm-review.jsonl` (tracked) for admitted known drifts; `dev/review-ledger.md` for a skipped triage

**Testing**: pytest through `make test-file`; the tooling suites in `tests/tooling/`; the guard suites through `make hooks-test`

**Target Platform**: the dev container (Linux)

**Project Type**: build and test tooling

**Performance Goals**: SC-001 (12 of today's 19 full-planned deltas plan incremental), SC-002 (the coverage check names its
reds' lines in less time than the gate), SC-003 (a records-only push's three gates exit before reading what they judge)

**Constraints**: FR-009 - every shortcut is replayed against today's runs; a narrowing is stated and priced, never silent

**Scale/Scope**: 7 changes; ~10 files

**Single-artifact target**: not a generator change; no map moves.

## Performance bookends

Not a generator change. The measurements that matter are each task's replay against today's records (FR-009), in `research.md`.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content, no SOURCE blocks, no in-world writing.
- **VI. Verify Before Reporting Done**: PASS - each task's tests are red without its change (FR-008) and its replay is recorded.
- **X. Python Discipline**: PASS - ruff, ruff format, pyrefly, 100% coverage on the touched engine modules (`ci/incremental.py`
  and its new reader module); functions under 100 statements; no file past 1,000 lines (`incremental.py` is 580 lines, measured 2026-10-26 (`wc -l`),
  `claims_carry.py` and `plan_lint.py` small).
- **XII**: N/A - changes nothing a generator asserts about the world.
- **XIII. No Known Regressions**: PASS - FR-009's replays are the baseline: today's run records and pushes, judged the old way
  and the new.
- **XVI. Do the literal thing**: D3's placement beside the gate (not before it) and D2's superset are stated where they stand.
- **XIX**: N/A - places nothing.

## Decisions

**D1 - pool manifests keep the gate incremental (FR-001).** In `incremental.plan()`, the non-Python engine files split in two:
a MANIFEST (`pool/<tier>/<map>/<map>.json`) and anything else. Anything else plans full as today. Manifests alone add their
READERS to the selection, as changed test modules are added: the test modules under the gate's own trees (`tests/` and its
`gate/`, `full/`, `tooling/`; not `soak/` or `tier_*`) whose source names the pool as a path part, pool-readers' pattern. The
pattern and the reader search move into one engine module, `l7r/diagram/ci/pool_readers.py`, which `scripts/gates/pool-readers.py`
imports for `make quick`'s narrower trees (one copy of the rule). The plan's reason names the manifests and the reader count; a
manifest no reader names keeps the plan incremental and says so (the spec's edge case). The replay (FR-009): each of today's 11
runs that planned full for `inashiro.json` is re-planned at its commit, and every test that run reported failing must be in the
new selection.

**D2 - the test tree's non-module files (FR-002).** `changed()` sorts `other_tests` three ways: a doc (`*.md`) adds nothing; a
file directly under `tests/` plans full, as today; any other selects (a) every test module under the file's own directory, and
(b) for a file that is not a `conftest.py`, every test module under the gate's trees whose source names the file's name or its
directory as a path part. (b) is wider than FR-002's "that directory", on purpose: fixture data under `tests/fixtures/` (56
files, no test module of its own) is read by tests in eight other directories (observed 2026-10-26, method: research R3), and the directory alone would
select nothing - an unpriced narrowing, which FR-009 forbids. A guard suite under `tests/hooks/` selects only the pytest modules there, which is
right: `make hooks-test`, not the gate, runs the suites. The replay: SC-001's 12 re-plan incremental, the 4 top-level `conftest.py`
runs re-plan full, and the 3 that also changed the gate's configuration re-plan full by that rule.

**D3 - the coverage check asks every line of each changed module, with the floor's tests (FR-003, FR-003a).**
`cover_changed.py`:
- the modules: every engine `.py` file the merge base's diff changes (any hunk, not only additions);
- the tests: those whose contexts in the gate baseline touch those modules (`incremental.contexts_touching`), the changed test
  modules, and the mirrored directory - less the map-rolling ones (`-m "not rolls_map"`), so it stays seconds; run with coverage
  on the changed modules only;
- the marker expression is the gate's own: the `(tooling or not tooling)` override goes, so a test the floor would not count is
  not counted here (today's sixth red, `9a157cc4b`);
- a line the run leaves unrun is NAMED unless the baseline shows it reached by a context this run did not run (a roll, or a
  tooling test the gate reuses) and the line's text is unchanged since the merge base (the two versions matched by `difflib`):
  that is the floor's own carried coverage, read the way the floor reads it;
- with no baseline it falls back to the mirrored directory, every line asked.
The narrowing, stated and priced (FR-009): a roll-reached line that the change stops a roll reaching is not named here; the gate
names it, as today. The task measures how many of today's in-scope reds that would have missed (expected none: R1 names deleted
tests and moved code, no roll).
Placement: `make land` already starts it FIRST, with the gate beside it, and stops the gate the moment it refuses
(`land.start_cover`, feature 415 T03 D6: run before the gate it had cost T26's landing 48 s, measured 2026-10-24 (feature 415
T03, `land.py`'s docstring)). That is kept: a refusal arrives at the check's time, not the gate's, which is what "before the 4-5 minute gate" buys,
and a green check costs the landing nothing. SC-002's "less time than the gate" is therefore timed with the check running beside
the gate on this shared container, as a landing runs it, never alone. The escape stays `COVER_OK`.

**D4 - the push gates (FR-004).** A new `scripts/gates/push_gates.py` holds, per gate, what it judges:
- `claims`: `claims.BASE_PATHS`, `claims.INDEX`, `claims.DEFERRED`, `claims.STORE`, `specs/*/tasks.md` (a known drift reads
  its open task row) and `specs/*/gm-review.jsonl` (D6: a known drift is admitted once recorded there);
- `entry`: the paths `record_owed.py` reads (`research/`, `l7r/diagram/interactive/`, and the record's answer files - the list
  read off its constants in the task, each pinned by a test that fails when a constant names a path the list lacks);
- `cohort`: the engine paths (`ci/delta.is_engine`).
Each gate script asks it first: `push_gates.py nothing <gate>` exits 0 and prints "`<gate>`: nothing to judge (the delta holds
no <what>)" when the merge base's diff to HEAD, working tree included, touches none of its paths; then `push_gates.py cached
<gate>` exits 0 when a PASS is stored for the key - the gate's name, the code id of the gate's own scripts, the merge base, and
the blob ids of the delta's paths it judges - under `<git dir>/push-gates/`. A pass is stored after the gate passes; a refusal
is never cached. `sync-with-main.sh` decides the route first (it already does, cheaply), then runs the gates the route owes -
entry and claims always, cohort on a gated route - side by side, each to its own log, waits for all, prints every log, and exits
1 when any refused, naming each. The replay: every push of 2026-10-26 judged old and new gives the same verdict.

**D5 - the plan-lint before every plan review (FR-005, SC-004).** `plan_lint.refusal` gains three checks:
- a figure with a unit anywhere in the section (not only Approach item 4) whose sentence carries no label (`measured <date>
  (<method>)`, `observed <date>, method: ...`, or `m:<key>`), using the spec-lint's unit list (`spec_figures.UNITS`);
- an Approach block whose item 6 lacks `make arbiter-ask` (the red exit, D35's wording);
- in a plan whose tasks owe approach blocks - one that opts in (`**Approach checklist**:`) or already holds a `### Txx Approach`
  block, as this plan does - an open task of `tasks.md` with no `### Txx Approach` block. A plan with neither predates the
  checklist (feature 385) and owes none (`approach_gate.py` D8), so it is not asked.
`plan_gate.py delta` (`make plan-delta`) runs the lint on every block it would bundle, as `make decide` already does, and writes
no bundle while one refuses, naming each: no review is dispatched on a block the lint refuses, because no bundle exists to
dispatch it on.
An approach block owes no review only when it MATCHES THE TEMPLATE AND DECIDES NOTHING, labeled or not, asked of every one of its
eleven answers with no free text left unasked: each answer, once the ids it names are set aside (`D<n>`, `FR-<n>`, `SC-<n>`,
`R<n>`, `T<n>`, a feature number, a date - each `D<n>` and `R<n>` defined elsewhere in the plan, `plan-done.md` or the spec), is
empty, "n/a", "None", "Yes", "One landing", or `task-add`'s own template wording for that item (item 6's red exit, item 9's "Its
tests red without D<n>."); and the block holds no number of any kind outside those ids, unit or not ("9 of the 11", "4 or fewer"
are tuned numbers). Any answer in the block's own words - a goal, a source, an order, a finish line - is where a rule or a number
can stand, so it owes the review. A missing `D<n>` alone is never enough. `plan_sections.decides_nothing` takes the approach form beside the part B form.

**D6 - known departures and small triages (FR-006, SC-005).** `claims_carry.known_drifts` drops the condition that the claim's
code be the merge base's: a DRIFTED claim whose own text's last named task is an open row of that feature's `tasks.md` naming the
claim's unit is known, the landing's change to its code or not. The gate admits it and asks it to be RECORDED, as a carry is
filed: an unrecorded known drift refuses with `make claims-known F=<n>`, which appends a row per claim to that feature's
`gm-review.jsonl` (`kind: known-drift`, the claim, its task, the time), and `make land` runs it itself. `make gm-review` lists
those rows as it lists every TO REVIEW row. A claims-triage bundle that would hold `TRIAGE_SKIP_MAX` = 3 claims or fewer (a
knob, labeled CONVENTION: the spec's "a few") is not written: `make claims-triage` writes the impl-drift bundle for those claims
instead, prints its MANIFEST, and appends a ledger row (`claims-triage`, `SKIPPED (3 or fewer claims)`, no cost).

**D7 - the claims triage beside the plan review (FR-007).** Research R2: no guard holds a claims triage today; the triage ran
after the plan review because the session began the claims round at landing. So: `make decide` and `make plan-delta` end, when
the clone owes claims a triage (`claims.py triage` would write a bundle), with the line "claims owed a triage: `make
claims-triage` - dispatch it beside this review (impl-drift waits for the verdict)". `tests/hooks/test-check-bundle-hooks.sh`
gains the case: with a task undecided, a `claims-triage` dispatch passes decide-first and an `impl-drift` one is refused.

## Task approaches

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T06 to T06 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
<!-- plan-archive: T07 to T07 moved to plan-done.md, 2026-10-26 (feature 375 FR-044) -->
## Project Structure

### Documentation (this feature)

```text
specs/430-faster-landings/
├── request.md         # the GM's words, verbatim
├── spec.md            # reviewed FAITHFUL
├── plan.md            # this file
├── research.md        # R1 the coverage replay, R2 the triage guard, R3 the test tree's files; each task's replay
├── measurements.json  # m:coverage-reds-replay, m:full-plan-reasons
└── tasks.md           # /speckit-tasks
```

### Source Code (repository root)

```text
l7r/diagram/ci/incremental.py      # manifests (D1), the test tree's files (D2)
l7r/diagram/ci/pool_readers.py     # new: the readers pattern and search (D1)
scripts/gates/pool-readers.py      # imports it (D1)
scripts/gates/cover_changed.py     # every line, the floor's tests (D3)
scripts/gates/push_gates.py        # new: nothing to judge, the pass cache (D4)
scripts/gates/{claims,entry,cohort}-gate.sh, scripts/sync-with-main.sh   # ask it; side by side (D4)
scripts/gates/plan_lint.py, scripts/gates/plan_sections.py, scripts/gates/plan_gate.py   # D5, D7
scripts/record/claims_carry.py, scripts/record/claims.py, scripts/land.py, Makefile   # D6
tests/tooling/ci/test_incremental.py, tests/tooling/test_plan_blocks.py, tests/tooling/test_plan_gate.py,
tests/tooling/test_known_drift.py (existing); tests/tooling/test_cover_changed.py, tests/tooling/test_push_gates.py (new);
tests/hooks/test-check-bundle-hooks.sh and the three push gates' suites
```

## Complexity Tracking

None.
