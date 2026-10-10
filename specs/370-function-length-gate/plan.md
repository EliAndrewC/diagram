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

- **D1 - the setting.** `[tool.ruff.lint] select` gains `"PLR0915"` and `"PGH004"`; `[tool.ruff.lint.pylint]
  max-statements = 100`, with a comment giving the GM's reason (the second most common value on GitHub, 131 of 1,209
  repositories, and the most common chosen over the default 50 - research.md R1). `PGH004` (blanket `# noqa`) is on
  because a bare `# noqa` would silence `PLR0915` with no code and no reason - the bypass FR-004 closes; it fires on
  nothing today (measured 2026-10-10: 0 in every tree).
- **D2 - the trees outside the fence.** `make static` gains one line: `python3 -m ruff check --select PLR0915,PGH004
  scripts pool tests/hooks` - ruff lints an explicitly named path even when `extend-exclude` lists it (`force-exclude` is
  off), so the fence's formatting reasons stand and only these two rules reach those trees (FR-002). The same line runs at
  the push beside `check-file-scale.py`, because a scripts-only push takes the DIRECT route and runs no gate.
- **D3 - the reason check.** `scripts/gates/check-file-scale.py` - which already scans the same trees with the same
  exclusions (`SKIP_PARTS`: the legacy pool, `specs/`) and already refuses a bare file-size marker - also refuses a
  `# noqa` naming `PLR0915` with fewer than three words after it, printing the line and "say why the body must remain one
  (constitution X clause 12), or split it". Its `--selftest` gains the two cases (bare fires, reasoned passes).
- **D4 - the splits.** Each of the twelve (research.md R2) is cut along the phases its own comments already name, into
  module-level (or method-level, for a `Settlement` method) parts that take what they use as parameters - never a nested
  function (it counts in its parent: spec edge cases). The order of every call, every random draw and every registry
  write is unchanged, so no map moves. A part that lands in a hamlet-rolled module carries a `Research:` block holding
  the claims for the code it took (moved from the parent's, not copied), and the parent's `Steps:` list names it where it
  has one.
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
Makefile (static)                    D2
scripts/sync-with-main.sh            D2 (the push)
scripts/gates/check-file-scale.py    D3
tests/tooling/test_function_cap.py   SC-001, SC-004 (the cap fires at 101, passes at 100; the reason check)
.specify/memory/constitution.md      D7
.specify/templates/plan-template.md  D7
CLAUDE.md, docs/guards.md            D8
the twelve functions (research.md R2) D4
```

## Complexity Tracking

None.
