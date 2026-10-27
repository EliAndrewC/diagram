# Implementation Plan: Call counts on the placement-stages page

**Branch**: `434-placement-call-counts` (no branch; `main` in the clone) | **Date**: 2026-10-27 | **Spec**: `spec.md`

**Input**: `spec.md`, `request.md` (the GM's three messages, verbatim).

## Summary

A make target measures one 40-household hamlet stage by stage, each stage under cProfile as `make perf-fanout` does, and each
step the page lists under a stage under its own profiler while it is the innermost listed step running; it records the
counts, newest per map type, in a committed file. `make placement-stages` reads that file and breaks down the reference hamlet's
roll: each stage's heading carries the reference's calls and share (another recorded type beside it, named, where it spent
more), and a last section - after "Features this map does not have" - tables every stage, each row expanding on a click to
its steps with their calls, share of the stage and share of the reference's whole roll. Calls only, never time.

## Technical Context

**Language/Version**: Python 3.14 (the engine's interpreter).

**Primary Dependencies**: the standard library's `cProfile` and `pstats` (the fanout's own measure); the page is plain HTML
with a few lines of inline script for the expanding rows.

**Storage**: `dev/phase-calls.json`, committed (the page regenerates the same counts on any clone).

**Testing**: pytest under `make quick` / `make test-file`; the tool's tests in `tests/tools/test_phase_calls.py`, the page's
in `tests/tools/test_placement_stages.py`.

**Project Type**: tooling - `l7r/diagram/tools/` (read-only diagnostics; nothing a generator imports).

**Constraints**: the measuring roll runs on demand, never in the gate (it rolls a 40-household hamlet under profiling).

**Single-artifact target**: the reference hamlet's spec at 40 households, seed 39 (feature 417's T57 roll).

## Performance bookends

Not a generator change: the engine is untouched and no map moves. The measure this feature adds is checked against the
fanout's for the same roll (SC-003), not bookended.

## Constitution Check

- **I, II**: N/A - the page is a developer document generated in `dev/`, not a UI of this repository's maps.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content, no SOURCE blocks, no in-world writing.
- **VI. Verify Before Reporting Done**: PASS - each task's tests red without the change and green with it, `make quick`,
  `make cover-changed`, the landing's `make done`; T03 checks SC-001 to SC-004 on the generated page and the fanout.
- **X. Python Discipline**: PASS - ruff, ruff format, pyrefly, 100% coverage on the new module and the changed lines of
  `placement_stages.py`; no function past 100 statements; `placement_stages.py` is ~910 lines, so the page's new section goes
  in its own module (`tools/placement_calls.py`) rather than past the 1,000-line bar.
- **XII**: N/A - asserts nothing about the world.
- **XIII. No Known Regressions**: PASS - no engine file changes; `make placement-stages` regenerates the page with its plates
  as before, the counts added.
- **XIX**: N/A - places nothing.

## Decisions

**D1 - The step tally switches cProfile profilers.** Each stage runs under a stage profiler; each listed step's every binding
(`placement_stages._bind_points`, the page's own) is wrapped so that, while the step runs, the profiler that was running is
disabled and the step's own is enabled, and the reverse on its return. A call is counted by exactly one profiler: the
innermost listed step's, or the stage's (its own work). The wrappers' own frames and the profilers' `enable`/`disable` calls
are removed from the counts, so a stage's total is cProfile's count of the stage alone - the fanout's (SC-003). A step that
calls itself, or a step nested in another, nests on the same stack.

**D2 - Each stage in a fresh process, as the fanout measures it.** AMENDED 2026-10-27: one sequential roll measuring every
stage was 3,317 calls short of the fanout on seed 39's 40-household homesteads, measured 2026-10-27 (make phase-calls
against make perf-fanout) - the process a stage meets is not the one a plain roll of the stages before it leaves. So each
stage is measured as the fanout measures it: a fresh worker runs the stages before it plainly, then it under the tally
(`phase_calls.stage_job`, `--jobs` workers, each job a fresh process). What remains apart from the fanout is a few hundred
calls in four stages - two the fanout's own run variation (two consecutive fanouts gave sink 77,448 then 77,396), two a
small residue - measured 2026-10-27 (make phase-calls against make perf-fanout); the round arbiter accepted SC-003 so
(ask:434-SC-003-exact).

**D3 - The record.** `dev/phase-calls.json`: one entry per map type, keyed by the spec's knobs that decide which stages do
work (settlement form, field archetype, water sink), each with its date, seed, households, engine commit, total, and per
stage `calls`, `own` and `steps` (a step's dotted name -> calls). A new measurement of a type replaces its entry.

**D4 - What the page shows for a stage.** The page breaks down the reference hamlet's roll: each stage shows the
reference's count and its share of the reference's total, or a dash where the reference's record lacks the stage. Every roll
runs every stage (one that does not apply returns after a handful of calls), so another recorded type is shown beside a
stage - named, with its count and its share of its own total, never in the reference's place - where it spent more calls in
the stage than the reference did, or holds a stage the reference's record lacks (the reference's dash then shown with it) -
the polder's `waterward`, which the reference runs in 2 calls, measured 2026-10-27 (make perf-fanout LABEL=417-T57).

**D5 - The end section and its rows.** A section after `id="missing"`, `id="calls"`: a table of the 23 stages (number, title,
calls, share), the reference's total below them, and beside a stage any other type D4 shows. Each stage row
toggles the hidden rows of its steps (inline script, a dozen lines, no library): each step's short name (as the page names
it), calls, share of the stage, share of the reference's total; and a row for the stage's own work; above the table, one
sentence says a step's calls are those made while it is the innermost listed step. A stage no recorded type holds shows only
dashes and has no steps to open; one only another type holds shows the reference's dash with that type beside it.

**D6 - The make target.** `make phase-calls [SEED=39] [HOUSEHOLDS=40] [FORM=] [ARCHETYPE=] [SINK=]` - the reference spec by
default, each knob overriding it; it writes the record and prints the stage table. `make placement-stages` reads the record
and needs no measurement to run.

## Task approaches

### T01 Approach (checklist part A)

1. **The goal, in the world.** One command measures a 40-household hamlet's calls by stage and by step (D1, D2) and records
   them (D3, D6).
2. **The constraints.** FR-001, FR-002, FR-005, FR-006; SC-002, SC-003.
3. **Where each comes from.** `spec.md`; the fanout's measure (`tools/perf_profile.profile_stage`).
4. **Do they describe the world here?** Yes: the page's steps are its stages' `Steps:` lists (`placement_stages.stage_doc`).
5. **The order.** First: the page reads what it records.
6. **The exits.** Green: a stage's recorded total equals `profile_stage`'s for the same stage, and its steps plus its own
   work equal it, on a test roll.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None: a measurement.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the stage total equals the fanout's | a test against `profile_stage` on a stand-in stage |
| steps plus own work equal the stage | a test on a stand-in stage with nested steps |

### T02 Approach (checklist part A)

1. **The goal, in the world.** The page shows each stage's calls in its heading and ends with the expandable table (D4, D5).
2. **The constraints.** FR-003, FR-004, FR-005; SC-001, SC-004.
3. **Where each comes from.** `spec.md`, `request.md`.
4. **Do they describe the world here?** Yes: the page's stage headings (`<div class="hd">`) and its last section
   (`id="missing"`) as `placement_stages.build_page` writes them.
5. **The order.** After T01.
6. **The exits.** Green: on a page built from a test record, every heading's count and every table row's numbers match the
   record, the steps open and close, an unmeasured stage shows a dash, and no time appears.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the headings | a test on the page built from a test record |
| the table and its rows | the same test; the toggle checked in the generated page |

### T03 Approach (checklist part A)

1. **The goal, in the world.** The reference hamlet at 40 households measured and the page regenerated with its counts; the
   other map types (row, dispersed, polder, dike-pond) measured too where a 40-household roll of them stands.
2. **The constraints.** SC-001 to SC-004.
3. **Where each comes from.** `spec.md`.
4. **Do they describe the world here?** Yes: `make perf-fanout` measures the reference spec at the same seed and size as
   `make phase-calls`' default (D6), the comparison SC-003 names.
5. **The order.** Last.
6. **The exits.** Green: the record committed, the page regenerated, each stage's count equal to the fanout's.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the record | `make phase-calls` |
| the agreement with the fanout | `make perf-fanout HOUSEHOLDS=40` on the same engine |
| the page | `make placement-stages`, read |

## Project Structure

- `l7r/diagram/tools/phase_calls.py` (new) - the measurement and the record.
- `l7r/diagram/tools/placement_calls.py` (new) - the page's counts: the heading text and the end section.
- `l7r/diagram/tools/placement_stages.py` - calls the two above.
- `dev/phase-calls.json` (new) - the record.
- `Makefile` - `phase-calls`.
- `tests/tools/test_phase_calls.py`, `tests/tools/test_placement_calls.py` (new).

## Complexity Tracking

None.
