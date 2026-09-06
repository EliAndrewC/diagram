# 193 - Retire the diagnostics nobody runs

**Status**: draft
**Request**: [request.md](request.md) (the GM's words, verbatim)

## Why

The Diagnostics category holds twelve targets. The GM: *"I don't understand what most of the
diagnostics are doing for us ... `make why-placed` makes sense as an option, but the other
diagnostics mostly do not."* The audit that followed agreed, on evidence:

- **Their apparent consumers are circular.** Every diagnostic has a coverage test (the 100% floor
  obliges one) and a row in `_invocation.OPERATIONS` (the module has a CLI, so the guard needs a
  route). Neither is evidence anybody wants the tool.
- **Zero recorded runs.** The guard firing log and the bypass log carry the command text of every
  blocked, rewritten or escaped invocation. No diagnostic appears in either.
- **`sun-audit` measures against a standard that no longer exists.** Its docstring cites three rules
  as its authority - `yards_unshaded_by_neighbors`, `gardens_unshaded_by_neighbors`,
  `village_trees_unshade_from_west`. Those names now appear in exactly three places in the tree: two
  COMMENTS and sun-audit's own docstring. They were check-battery segments and feature 166 deleted
  the battery.
- **The cost is mostly TESTS, and they run in every gate**: 2,761 lines of tool against 5,735 lines
  of test, all owing 100% coverage in perpetuity.

## What goes, and the ONE that does not

**EIGHT are removed outright** - target, recipe, `.PHONY` entry, registry row, module and tests:
`pack-audit`, `timings`, `crop`, `overlap-audit`, `jogs`, `polder-probe`, `sun-audit`,
`family-census`.

**`scatter-audit` loses its TARGET but KEEPS its module**, and this is a finding rather than a
hedge. `tests/settlement/test_land.py:566` imports `parse_bases` from it - a settlement gate test
encoding the GM's 2026-08-26 ruling (feature 133 T12, *"scrub scattered straight through the
reeds"*) - and `tests/tools/test_scatter_audit.py` uses it for the POSITIONAL crown guard. That
parser resolves a grove clump's `<g transform="translate(...)">`, and its own docstring records why
it matters: a count-based guard passed at `1,446 >= 1,446` while ~78% of the crown family was being
adjudicated in the wrong place. Deleting it would delete a guard that has caught a real defect.
So the diagnostic ENTRY POINT goes (target, `.PHONY`, registry row, `main`/CLI) and the module
becomes what it already is in practice: test support.

**`why-placed` and `notes-census` stay**, as the GM directed. `notes-census` earns it independently:
`tests/test_notes_census.py:52` is a gate test whose failure message says *"run `make
notes-census`"* - the only diagnostic with a consumer that is not itself.

## Requirements

- **FR-001** The eight targets, their recipes, their `.PHONY` entries, their `_invocation.OPERATIONS`
  rows, their modules and their test files are removed.
- **FR-002** `scatter-audit`'s target, `.PHONY` entry, registry row and CLI entry point are removed;
  `parse_bases` and what the two guard tests need survive. No gate test loses coverage of a rule.
- **FR-003** `pyproject.toml`'s `project-includes` list (line 69) drops `tools/pack_audit`,
  `tools/scatter_audit.py` and `tools/timings.py`. **This is the removal's real hazard**: a path list
  outside every walk, which no test builds a fixture for, and which fails only when the type checker
  runs. It is named here because a census by grep for `make <target>` cannot see it.
- **FR-004** The two engine COMMENT pointers that would go stale are corrected at the point of
  change: `settlement/_geom/base.py:66` (cites `tools/scatter_audit.py` for CROWN_FILLS) and
  `compound.py:35` (cites `pack_audit.structures_on_walls`).
- **FR-005** Every operative doc naming a removed target is corrected - `tools/CLAUDE.md`'s index
  (12 lines), the skill `CLAUDE.md` cost table, `dev/*.md`, `migration-plan.md`. A doc that sends a
  reader to a target that no longer resolves is the defect feature 191 existed to fix.
- **FR-006** `timings.md` is KEPT and annotated. It is a 31 KB measured record cited as authoritative
  by four documents; this feature removes its PRODUCER, so the file must say that it is now frozen
  and how a future measurement would be taken.
- **FR-007** `docs/make-targets.html` regenerates; the Diagnostics category is left with
  `why-placed`, `notes-census`, `crop`... - see D3 - and `hamlet-floor` moves out of Diagnostics
  entirely, since `test-full` invokes `hamlet_floor` directly as a gate phase and the target is only
  the `--list` view of what the gate enforces.

## Decisions Recorded

- **D1 - `scatter_audit.py` is kept as test support rather than deleted.** Priced alternatives:
  lifting `parse_bases` into a test helper (a 100+ line SVG parser with a documented bug history
  moving into `tests/`, where the file-scale rule and the coverage floor both still apply, for no
  gain), or deleting the guard tests with it (deleting a guard that caught a real 78% misplacement,
  which is the one thing this feature must not do).
- **D2 - `timings` goes even though it produces a cited record.** The GM was told this before
  authorizing (*"removing it means that record has no producer"*) and said *"I want all of the ones
  we don't need"*. FR-006 keeps the record and states its status; a future measurement is a new
  tool, and 2,246 lines is a high price for a capability last exercised in a spec that records no
  use of it.
- **D3 - `crop` is in the eight, and this is the one worth a second look.** It has 3 operative-doc
  mentions and 940 lines of test against 112 of tool. It is a UTILITY (crop a rendered map in
  manifest coordinates), not a check, so it fails the "what workflow uses it" test the same way; but
  unlike the audits it could plausibly be wanted by a human preparing an image. Removed per the GM's
  "all of the ones we don't need", and flagged here so the decision is visible rather than buried.

## Out of scope

- `why-placed`, `notes-census` (the GM kept both), and `hamlet-floor`, which is recategorized rather
  than removed.
- The Tests/Maps/Performance categories. The GM's question was about Diagnostics.

## Success Criteria

- **SC-001** `make <removed>` fails for all nine; `make why-placed` and `make notes-census` resolve.
- **SC-002** No message printed by the engine, and no operative doc, names a removed target -
  the same untruncated sweep feature 191 owed.
- **SC-003** `tests/settlement/test_land.py::test_commons_keeps_scrub_off_every_recorded_marsh` and
  the positional crown guard both still pass, proving FR-002 lost no rule.
- **SC-004** `make done` green, 100% coverage held, and the coverage SURFACE shrinks by the removed
  modules rather than by an exclusion.

## Review history

(pending `spec-fidelity`)
