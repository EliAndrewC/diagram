# Implementation Plan: relax the coverage floor for the engine code the Rust port replaces

**Branch**: `448-engine-coverage-relax` (no branch; `main` in the clone) | **Date**: 2026-11-02 | **Spec**: `spec.md`

**Input**: `spec.md`, `request.md` (the GM, 2026-11-02).

## Summary

One record, `dev/coverage-exempt.json`, names the Python files the Rust port replaces: (a) the own files of each 444 stage not yet
landed in Rust, each entry with the stages it serves, and (b) the engine modules the port leaves unreached (the program's
whole-engine replacement), which name no stage. One reader, `l7r/diagram/ci/coverage_exempt.py`, gives every coverage floor
the same set: the gate's `coverage report --fail-under=100` omits it, the derived hamlet floor drops it from its module set, and
`make cover-changed` (and so `make land`) reports its unrun lines without refusing. The slated files' unrun lines are printed as
information; everything else keeps the floor.

## Technical Context

**Language/Version**: Python 3.14, bash (the Makefile recipe). **Testing**: `tests/tooling/ci/test_coverage_exempt.py` (new),
`tests/tooling/test_coverage_floor.py`, `tests/tooling/test_docs_match_the_mechanism.py`, `tests/tooling/test_cover_changed.py`,
the hamlet floor's tests (`tests/tooling/test_hamlet_floor*.py`). **Project Type**: tooling - the gate's coverage floors; no map,
no roll changes.

## Performance bookends

None: no code a roll runs changes. The floor step gains one reader call (a JSON read) and one information line per slated module
with unrun lines.

## Constitution Check

- **I-V, VII-IX, XI, XII, XIX**: N/A - no map, no setting prose, no placement.
- **VI**: PASS - the tests above, `make quick`, the landing's `make done`.
- **X, clause 5** (full line coverage on everything, no opt-in, GM 2026-09-02): AMENDED by the GM's 2026-11-02 ruling for the slated files only;
  D5 writes the amendment into the constitution with his words. The new module and every changed tool owe the full floor as before.
- **XIII**: PASS - the floor tightens nowhere and loosens only on the record; SC-002 is measured at the landing's gate.
- **Guard doctrine**: the stale-entry refusal (D4) names the command that cures it, has its test, and is proven to fire.

## Decisions

**D1 - What is slated** (FR-001: "the 444 phase that replaces it, or the program's whole-engine replacement"), two parts:
- **(a) the phases' own code**: the Python files of `work_budget_bundle.stage_files(root, stage)` - the module defining
  `stage_<stage>`, with its subpackage's siblings - for every stage of `STAGES` not `accepted` in `dev/work-budget.json`; 444's own
  definition of a stage's old code (`scripts/gates/phase_sources.py`), the code a phase task rebuilds and deletes. Measured
  2026-11-02 (`stage_files` over `STAGES`, the Python half, the accepted stages left out): 76 files, all under
  `l7r/diagram/hamletgen/`.
- **(b) the whole-engine replacement**: every engine module the port leaves dead - not reached by imports from any root that stays
  Python once (a) is removed. The roots are what 444 FR-010 keeps Python (the driver, `STAGES`, the manifest, rendering, the pool's
  `.gen.py` scripts, the tools and the pytest suite) and the trees FR-003 keeps: every module of `tools/`, `ci/`, `pipeline/`,
  `interactive/`, `labels/` and `overlap/`, every module run as a program, and every importer under `pool/` and `scripts/`.
  Measured 2026-11-02 (`specs/448-engine-coverage-relax/closure.py`: an AST import graph over `l7r/`, a name re-exported by a
  package resolved to the module defining it, reachability from those roots with (a) removed): 14 files - `hamletgen/ways/law/`
  (5), `hamletgen/ways/settle/` (5), `settlement/fields/landuse.py`, `settlement/fields/outfall.py`,
  `settlement/rolling/gap_ways.py`, `waterfields/twins.py`. Everything else the closure reaches - the driver, `plan.py`, the
  `consts*` modules, `clearance.py`, `cluster.py`, `hinterland/parcels/`, the two landed stages' thin doors (`field_stage.py`; the
  water frame's), the rest of `settlement/` and `waterfields/` - stays Python after the port and keeps the floor.
Rejected: the union of `phase_sources.sources()` over every stage (146 files, measured 2026-11-02 (the same `stage_files` script
with `counted_files`)) - its `counted_files` half takes in exactly the kept trees FR-003 names. A later phase whose contract slates
more adds its entries in its own task (FR-004: the default is the floor).

**D2 - The record** (FR-001, FR-004): `dev/coverage-exempt.json`: a `ruling` key (the GM's words, dated) and an `entries` list, each
entry its `path`, its `stages` and its `why`; written once at this landing by `seeded` - D1(a) from `stage_files`, D1(b) the paths `closure.py` measured - and edited
by hand after. A path not in it is held to the full floor.

**D3 - The one reader** (FR-002, User Story 3): `l7r/diagram/ci/coverage_exempt.py`:
- `entries(root)` / `exempt(root)` - the live entries' paths (a stale entry, D4, is not exempt: its floor returns at once).
- `omit` (CLI) - prints `--omit=<p1>,<p2>,...` for the live paths, nothing when there are none.
- `report` (CLI) - from the gate's coverage data, one line per live path with unrun lines: `coverage (information, feature 448 - slated
  for the Rust port): <path> - unrun lines: ...`; then D4's stale check, exit 1 on a stale entry.
- Readers: the Makefile's floor line becomes `python3 -m coverage report -m --fail-under=100 $$(python3 -m
  l7r.diagram.ci.coverage_exempt omit)` followed by `python3 -m l7r.diagram.ci.coverage_exempt report || cov_ec=1`;
  `tools/hamlet_floor.py`'s `check` drops the exempt paths from its set and names how many it dropped; `scripts/gates/
  cover_changed.py` splits its result - an exempt module's unrun lines print as `cover-changed: information (slated, feature 448):
  ...` and do not refuse. `make land` runs `cover_changed.py` and inherits it. `scripts/gates/preflight.py`'s coverage step (`make
  preflight`; FR-002's search found it) moves an exempt file's off-path lines out of its refusal and prints them as information.
- Unchanged: `[tool.coverage.run] source = ["l7r"]` - every file is still measured, only the floor moves; `uncovered_marks.py`
  and `uncovered-in-diff.py` stay information.

**D4 - Stale entries** (FR-005): an entry is stale when its path no longer exists, or - for a (a) entry - when every stage it names
is `accepted` in `dev/work-budget.json` (the Rust has landed; what remains of the file is the stage's thin door, which keeps the
floor). A (b) entry names no stage and is stale when its path is gone or when the reader's own reachability measure (`unreached`, the
same rule as D1(b)'s `closure.py`, moved into the reader) finds it reached from the kept roots - a module kept code begins to
import is no longer going away, and its floor returns. `report`
names each stale entry and the cure, `make coverage-exempt PRUNE=1` (a new target: lists the record; `PRUNE=1` drops the stale
entries and writes the file). `make land`'s cheap refusals ask the same check first, so a Rust landing meets it in seconds rather
than at the gate's end.

**D5 - The docs** (FR-006): every operative statement of the one floor FR-006's search finds says the exemption, points to the
record and carries the GM's 2026-11-02 words: the root `CLAUDE.md` (the Python line), `l7r/diagram/CLAUDE.md` (the loop),
`settlement/CLAUDE.md`'s Coverage, `tools/CLAUDE.md`'s hamlet-floor row, `tests/CLAUDE.md`'s tree table, `tests/soak/CLAUDE.md`'s gate row and membership rule, `docs/efficiency-tooling.md`,
`docs/guards.md`'s coverage row, `docs/migration-plan.md`, `ci/incremental.py`'s docstring, `pyproject.toml`'s coverage note (its
paragraph on the derived surface kept, the 2026-11-02 ruling written beside it), `.specify/templates/plan-template.md`'s Principle X gate
and the constitution's Principle X clause 5 (a dated amendment, 2.34.0); and the phase checklist's rebuild box, which a phase reads
as it deletes its old Python. `tests/tooling/test_coverage_floor.py` and `test_docs_match_the_mechanism.py` assert "no `--omit` on
the floored report": each now asserts the only omission is the record's, generated by the reader, with the GM's 2026-11-02 words
beside the 2026-09-02 ones.

## Task approaches

- **T01** (D1-D4, the code): red first - `test_coverage_exempt.py` asserts SC-001 on a fixture (a coverage data file with one
  unrun line in a slated and in a kept module: `report` exits 0 naming the slated line, the floored report with `omit` fails on the
  kept one), the stale check (a missing path, an all-accepted entry), and that the record's entries are exactly D1's rule at
  landing; hamlet floor and cover-changed tests for the split. Then the module, the record seeded, the Makefile (`make guard-edit`),
  the two readers, `make coverage-exempt`, land's cheap refusal.
- **T02** (D5, the docs and the floor tests), then the landing: `make land F=448 T=T01,T02` - the gate's floor is the
  measurement of SC-002.

### T01 Approach (checklist part A)

1. **The goal, in the world.** A session changing the engine code the Rust port replaces is not held to the full floor on it; every other
   file still is.
2. **The constraints.** FR-001 to FR-005; D1-D4.
3. **Where each comes from.** G: the GM's ruling, 2026-11-02 (`request.md`); 444 FR-010 for what stays Python.
4. **Do they describe the world here?** The record's 90 entries, 0 stale, measured 2026-11-02 (`make coverage-exempt`, the
   reader's own reachability over `stage_files` and `closure.py`'s entries).
5. **The order.** First.
6. **The exits.** Green: `tests/tooling/ci/test_coverage_exempt.py`, the hamlet floor's, cover-changed's and land's tests green,
   and the landing's gate floor green. Red: what failed recorded, a claim it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** The landing's `make done` floor green with the record's omission, every kept file at the full floor (SC-002).
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

### T02 Approach (checklist part A)

1. **The goal, in the world.** Every doc that states the one floor says the exemption, with the GM's words.
2. **The constraints.** FR-006, SC-003; D5.
3. **Where each comes from.** G: the GM's ruling, 2026-11-02 (`request.md`).
4. **Do they describe the world here?** The floor tests read the Makefile the gate runs.
5. **The order.** After T01 (the docs name its record and reader).
6. **The exits.** Green: `test_coverage_floor.py` and `test_docs_match_the_mechanism.py` green. Red: recorded, ruled through
   `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** The same landing as T01.
9. **Done, measured.** Every doc D5 lists - `l7r/diagram/CLAUDE.md` among them - names `dev/coverage-exempt.json` and carries the
   GM's 2026-11-02 words, checked by `git grep -l coverage-exempt` and `git grep -l "going away"` over that list.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - docs.
