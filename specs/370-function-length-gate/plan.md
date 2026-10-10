# Implementation Plan: a mechanical cap on function length, held at the gate

**Branch**: none (main, in the session clone) | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: `specs/370-function-length-gate/spec.md` (spec-fidelity round 2: FAITHFUL)

## Summary

Turn on ruff's statement rule (`PLR0915`) at 100 in `pyproject.toml` with the survey's reason beside it (research.md R1),
hold it over the three working trees the lint fence leaves out, refuse a bare or reasonless suppression, amend
constitution clause 12 to name the cap, and split the twelve functions over it today (research.md R2) without moving a map.

## Technical Context

**Language/Version**: Python 3.14 (`pyproject.toml` `target-version = "py314"`)

**Primary Dependencies**: ruff (already the gate's linter); no new dependency

**Testing**: pytest through `make test-file` / `make quick` / `make done`; the gate script's own `--selftest`

**Project Type**: the diagram engine and its tooling

**Single-artifact target**: no map changes by design. Proof is the opposite of a sweep: `make maps` over the whole pool on
the landing commit, every manifest compared with HEAD's (`git diff --stat HEAD -- pool/`) - empty (SC-003).

**Every step is two steps.** Each split is proven on its own first (`make test-file` on its module's tests, then
`make quick`), and the pool reroll at the end is its own task.

## Performance bookends (constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `370-start` | | | | on unmodified code, before the first engine edit |
| after | `370-end` | | | | before the push |

A split adds function calls and no work; any seed more than 5% slower is diagnosed here in writing.

## Constitution Check

- **I, II**: N/A - no UI in this repository.
- **III, IV, V, VII, VIII, IX**: N/A - no pool content, SOURCE block, in-world prose or setting detail is written.
- **VI. Verify before reporting done**: PASS - each split: its module's tests (`make test-file`), then `make quick`; at
  the end `make done`, the pool reroll diffed against HEAD (SC-003), the perf bookends. No review check is owed: no map
  changes (`tasks.md` `## Occasions`: none).
- **X. Python discipline**: PASS - this feature IS clause 12 made real. ruff, format, pyrefly and the 100% floor hold
  over every edit; the new gate behavior is test-first (the fixture tests fail before the setting lands). No file passes
  1,000 lines: each split stays in its own module unless that module would cross it, in which case the part moves to a
  sibling module named in the task.
- **XII. Historical grounding**: N/A for the world - no generator asserts anything new; every split carries its unit's
  `Research:` claims with the code they describe (FR-007), and the claims gate's `impl-drift` re-check is run on the
  units it owes.
- **XIII. No known regressions**: PASS - baseline is the pool's committed manifests at HEAD and a green `make done` on the
  unmodified clone (recorded 2026-10-10 by the earlier pushes' stamps); merge requires zero manifest changes and a green
  gate.
- **XVI. Do the literal thing**: PASS - splitting is the default for all twelve (FR-003); a function kept whole goes to a
  `spec-fidelity` exception check of its own first. None is planned to be kept whole.

## Decisions

- **D1 - the setting.** `[tool.ruff.lint] select` gains `"PLR0915"`; `[tool.ruff.lint.pylint] max-statements = 100`,
  with a comment giving the GM's reason (the second most common value on GitHub, 131 of 1,209 repositories, and the most
  common chosen over the default 50 - research.md R1). No other rule is added (plan review round 1: PGH004 was scope creep).
- **D2 - one check owns the cap, everywhere it is held.** `scripts/gates/check-function-cap.py` runs ruff's statement rule
  alone (`ruff check --select PLR0915`, the 100 from D1's config) over all five held trees - `l7r`, `tests`, `scripts`,
  `pool`, `tests/hooks` (ruff lints an explicitly named path even when `extend-exclude` lists it) - and on a finding prints
  each function with its count and BOTH ways out: split it into parts at module or class level, or put
  `# noqa: PLR0915 <why the body must remain one>` on its `def` line (constitution X clause 12) (FR-008). It runs FIRST in
  `make static`, so its message is what a session reads, and before every push in `sync-with-main.sh` beside
  `check-file-scale.py` - a push of `tests/` or `scripts/` alone takes the DIRECT route and runs no gate (plan review 3).
- **D3 - the suppression is one body, with its reason.** The same script refuses, in every held tree: a `# noqa` naming
  PLR0915 with fewer than three words after it; one anywhere but on a `def` line; a bare `# noqa` on a `def` line (it
  silences the cap with no rule named - measured by the plan review); a file-level `# ruff: noqa` that is bare or names
  PLR0915 (it would exempt every function in the file); and an `ignore` or `per-file-ignores` entry naming PLR0915 in
  `pyproject.toml` (FR-004). `--selftest` plants each case; the tests pin the messages.
- **D4 - the splits.** Each of the twelve (research.md R2) is cut along the phases its own comments already name, into
  module-level (or method-level, for a `Settlement` method) parts that take what they use as parameters - never a nested
  function (it counts in its parent: spec edge cases). The order of every call, every random draw and every registry
  write is unchanged, so no map moves. A part carries a `Research:` block with the claims for the code it took; a claim
  moves out of the parent only when none of the code it rests on stays behind, and is kept by the parent otherwise
  (FR-007: a split unit keeps its claims). The parent's `Steps:` list names the part where it has one.
- **D5 - map identity, measured.** After the last split: `make maps` (the whole pool), then `git diff --stat HEAD --
  pool/` must be empty. Per split, the module's tests are the quick proof; the reroll is the final one.
- **D6 - the claims re-check.** The split units' code fingerprints change, so `make claims-owed` will name them; one
  `make claims-bundle` per module and an `impl-drift` dispatch per bundle, run once after the last split, then
  `make claims-checked`. This is the feature's expected review cost (spec Assumptions).
- **D7 - the constitution.** Principle X clause 12 is amended to name the measure (ruff's statement count), the cap (100),
  the escape (`# noqa: PLR0915` with a reason saying why the body stays one), the survey (research.md R1) and where it is
  held; the deferred-TODO lines in the Sync Impact Report and the "carried" list close; the version goes 2.28.0 -> 2.29.0
  (a principle's requirement changes). The plan template's clause-12 paragraph is updated to match.
- **D8 - the docs.** Root `CLAUDE.md`'s "the gate" row gains the cap; `docs/guards.md` gains its record.

## Project Structure

```text
pyproject.toml                       D1
scripts/gates/check-function-cap.py  D2, D3
Makefile (static), sync-with-main.sh D2 (first in static; before every push)
tests/tooling/test_function_cap.py   SC-001, SC-004 (the cap fires at 101 with both ways out, passes at 100; every suppression case)
.specify/memory/constitution.md      D7
.specify/templates/plan-template.md  D7
CLAUDE.md, docs/guards.md            D8
the twelve functions (research.md R2) D4
```

## Complexity Tracking

None.

## Review history

- **Plan review round 1 (2026-10-10): CHANGES REQUIRED.** (1) FR-008's two ways out were printed nowhere ruff fires - D2 now
  runs the rule in one script that prints them. (2) PGH004 dropped as scope creep; the bare-noqa hole it closed is D3's,
  on `def` lines only. (3) The push now covers `tests/` (all five trees). (4) A file-level suppression and a pyproject
  ignore are refused (D3). D4 reworded: a split unit keeps a claim whose code stays. research.md R2's stale `claims.py`
  row updated.
