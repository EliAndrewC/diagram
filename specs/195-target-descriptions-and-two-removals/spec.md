# 195 - Targets that say what they do, and two removals

**Status**: draft, round 2
**Request**: [request.md](request.md) (the GM's words, verbatim, with two readings recorded)

## Why

The generated target reference (feature 191/193) is now the thing the GM reads to decide what the
tooling is for - and reading it produced four complaints, each of which is a defect in the RECORD
rather than in the tooling:

1. **An argument's existence is not its meaning.** `make durations FULL MARK` told the GM that two
   arguments exist and nothing about what either does: *"does not tell me what the difference is
   between `make duration` and `make duration FULL=1` and `make duration MARK=1` (if that is even
   what I am meant to pass to `MARK` - I'm not sure)."* They are right to be unsure - `MARK` takes a
   pytest `-m` EXPRESSION, not `1` - and a third argument, `N`, was not listed at all.
2. **`make compound`'s description is actively misleading.** *"Compounds like magistracies are
   hand-drawn, so what is the make target actually doing?"* It reads "draw a Mode A compound plan",
   which sounds like it produces the finished artifact. It does not: per its own docstring it
   arranges a feet-based PROGRAM perimeter-first into *"a composed draft SVG the GM then refines"*.
3. **`make pack-audit` does not say it is for hand-drawn maps**, which is the whole reason it exists
   when the scripted tier's rules are placer tests instead.
4. **Two targets are not wanted**: `citybudget` and `hamlet-floor`.

## Requirements

- **FR-001 - the MECHANISM, and it is ALREADY LANDED.** Stated as fact rather than intent because
  it shipped in commit `0bfc26c0`, before this review: a `##  NAME=<what>  description` line beneath
  a target documents one argument, `make-docs.py` parses it (`argdocs`, `_args_cell`), and an
  argument with no doc line still appears by name so the page never hides one it cannot describe.
  Make reads the lines as ordinary comments; `make -n durations` resolves unchanged with them in
  place. **Two process notes, recorded rather than hidden**: implementing before the Principle XVI
  review was out of order, and the number-claim commit was supposed to carry `specs/` alone.
- **FR-002 - the REMAINING WORK: 24 targets.** 26 targets declare an argument in their help line;
  `durations` is done and two are being removed here, leaving **24** to document, one line per
  argument, each description read off the RECIPE rather than guessed.
- **FR-003** `compound`'s description says it composes a DRAFT that is then refined by hand, not that
  it draws the plan.
- **FR-004** `pack-audit`'s description says it is for HAND-DRAWN Mode A maps. **Only that** - the
  GM asked it *"note it is specifically used for hand-drawn maps"* and nothing more. The WHY (that
  tier keeps automated checks because its maps are not scripted, GM 2026-08-30) goes in a Makefile
  COMMENT above the target, not in the `##` line, which `make-docs.py` publishes verbatim - the same
  rule that moved a marker off a help line earlier today.
- **FR-005** `make citybudget` is removed: target, `.PHONY` entry, `_invocation.OPERATIONS` row, and
  the module's CLI (`main`, the `guard()` call and the `if __name__ == "__main__":` block, which
  `tests/test_operations_registry.py::_entry_points()` matches BY REGEX - removing the row while the
  block stands fails the gate, as feature 193 learned). The CLI's own tests go with it.
  **The MODULE STAYS**, per the reading in request.md: three frozen city exhibits and 1,732 lines of
  in-progress capital work import it.
- **FR-006** `make hamlet-floor` is removed: the target and its recipe. **The module stays** -
  `test-full` invokes it directly (`Makefile:1303`), which is the GM's own stated reason.
  Two corrections that make the naive version of this requirement IMPOSSIBLE:
  - **the registry row is RE-POINTED, not removed.** `hamlet_floor.py:182` carries
    `if __name__ == "__main__":`, so `test_operations_registry._entry_points()` counts it; deleting
    the row fails `test_every_entry_point_has_a_registry_row`, and deleting the block instead breaks
    the gate phase that runs the module as a program. The row becomes
    `("test-full", "cheap")` - the target that actually runs it, so a bare `python3 -m` refusal still
    names a command that exists. Same mechanism feature 193 met; met again here.
  - **there is no `.PHONY` entry to remove.** `hamlet-floor` appears on no `.PHONY` line (measured);
    `citybudget` does. Naming one would send the implementation to "fix" something adjacent.
- **FR-007** Every pointer to either removed target **or to `citybudget`'s removed CLI** is
  corrected, over the search space feature 193 established: **every file outside `specs/`**. Excluded
  as dated records: `pool/**/*.notes.md`, `legacy-hand-authored-pool/**/*.notes.md`,
  `wip/*.notes.md` and `docs/review-ledger.md`. Three site classes a target-name sweep cannot see:
  - **live doctrine naming the CLI**: `settlements/cities/sizing.md:85` says *"Audit it with
    `python3 citybudget.py --plan --population 3000 --river`"*, in a file whose header says to read
    it BEFORE picking any wall dimension. After FR-005 that capability exists in NO form, so the
    sentence must say the audit route is gone rather than quietly disappear.
  - **the Makefile's own contradicting notes**: `:11-14` ("restoring `citybudget`") and `:436`
    ("`citybudget` RETIRED ... 0 live consumers", which was never true).
  - **DERIVED COUNTS, which are not pointers**: `_invocation.py:189` says *"The 20 entry points"*
    (measured 19, becoming 18), and `test_operations_registry._entry_points()`'s docstring asserts
    that `citybudget` IS an entry point.

## Decisions Recorded

- **D1 - the argument convention is a comment line, not a new file or a schema.** Priced
  alternatives: a YAML sidecar (a second place to forget), and extending the single `##` line (it is
  already the widest line in the file and cannot hold three arguments' prose). A comment directly
  under the target keeps the documentation three characters from the thing it documents - the same
  argument that put the `[category]` tag there in feature 191.
- **D2 - `citybudget`'s module is kept and the GM was told.** Their instruction names the target and
  their reasoning is that the city tier is future work; `wip/shiro_daika/` is the start of that work
  and imports the module. Deleting it would break the thing the instruction anticipates resuming.
  Recoverable either way - this is recorded so the choice is visible, not to avoid the question.
- **D3 - `hamlet-floor`'s module is kept for a different reason**: it is not future work, it is a
  LIVE gate phase. Removing the module would break `test-full`.

## Out of scope

- `cache-audit` and `cohort`, which the GM asked about and did not ask to remove. The answers given:
  `cache-audit` is the only empirical backstop on a generation cache the gate TRUSTS (a wrong key
  ships stale maps with every check green); `cohort` is how the generator's per-seed success RATE is
  measured, which is a primary quality number for a generator project.
- `pack-audit`'s existence (kept; only its description changes).

## Success Criteria

- **SC-001** `make citybudget` and `make hamlet-floor` fail; `python3 -m l7r.diagram.citybudget` is
  no longer a runnable entry point; `test-full` still runs the hamlet floor and the gate is green.
- **SC-002** Every target in the generated page that takes an argument shows, per argument, what it
  takes and what it does. `make durations` in particular shows `FULL`, `MARK` AND `N`.
- **SC-003** An untruncated sweep finds no reference to either removed target outside `specs/` and
  the two record classes.
- **SC-004** `make done` green, 100% coverage held.

## Review history

- **Round 1 (`spec-fidelity`): CHANGES REQUIRED**, seven items, all accepted. The decisive one:
  **FR-006 was impossible as written** - `hamlet_floor.py:182` carries an `__main__` block that
  `_entry_points()` matches, so removing its registry row fails the gate and removing the block
  breaks the gate phase; the row is RE-POINTED at `test-full` instead. That is the same mechanism
  feature 193 hit, met a second time. It also found: no `.PHONY` entry for `hamlet-floor` to remove;
  FR-007 blind to `citybudget`'s CLI, to two contradicting Makefile notes, and to two DERIVED COUNTS
  that are not pointers; the record-exclusion naming the wrong pool tree; FR-004 requiring prose the
  GM did not ask for in text the page publishes; and FR-001/002 written as prospective when the
  mechanism had already shipped in the number-claim commit. It verified both narrowings as
  legitimate, and corrected the evidence for one: `wip/shiro_daika/frame.py` is **156 lines** (1,732
  is the whole 7-file package, and only `frame.py` imports `citybudget`), last substantively touched
  2026-08-31.
- **Round 2**: pending.
