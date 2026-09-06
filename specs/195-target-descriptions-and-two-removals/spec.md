# 195 - Targets that say what they do, and two removals

**Status**: draft
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

- **FR-001 - an argument is documented where it is declared.** A `##  NAME=<what>  description` line
  beneath a target documents one argument; `make-docs.py` renders each on its own row with what it
  DOES and its default. Make reads these as ordinary comments, so no recipe changes. Verified before
  adopting: `make -n durations` resolves unchanged with the lines in place.
- **FR-002** Every target that takes an argument gets one line per argument, including arguments that
  were never listed (`durations`' `N`). An argument with no doc line still appears by name - the page
  must not hide one it cannot describe.
- **FR-003** `compound`'s description says it composes a DRAFT that is then refined by hand, not that
  it draws the plan.
- **FR-004** `pack-audit`'s description says it is for HAND-DRAWN Mode A maps, and why that tier has
  automated checks when the scripted tier does not (GM 2026-08-30).
- **FR-005** `make citybudget` is removed: target, `.PHONY` entry, `_invocation.OPERATIONS` row, and
  the module's CLI (`main`, the `guard()` call and the `if __name__ == "__main__":` block, which
  `tests/test_operations_registry.py::_entry_points()` matches BY REGEX - removing the row while the
  block stands fails the gate, as feature 193 learned). The CLI's own tests go with it.
  **The MODULE STAYS**, per the reading in request.md: three frozen city exhibits and 1,732 lines of
  in-progress capital work import it.
- **FR-006** `make hamlet-floor` is removed: target, `.PHONY` entry, registry row. **The module
  stays** - `test-full` invokes it directly as a gate phase, which is the GM's own stated reason.
  Its `--list` flag becomes unreachable from make; that is the whole of what is lost.
- **FR-007** Every pointer to either removed target is corrected, over the same search space feature
  193 established: **every file outside `specs/`**, with `pool/**/*.notes.md` and
  `docs/review-ledger.md` excluded as dated records.

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

(pending `spec-fidelity`)
