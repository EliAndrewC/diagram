# 195 - Targets that say what they do, and two removals

**Status**: FAITHFUL at review round 3; implementing
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
- **FR-002 - the REMAINING WORK: 25 targets.** Counted with `make-docs.py`'s own `parse()` - the
  parser that renders the page - **27** targets declare an argument; `durations` is documented and
  `citybudget` is removed here, leaving **25**. The off-by-one worth naming: removing `hamlet-floor`
  subtracts nothing, because it declares no argument at all. One line per argument, each description
  read off the RECIPE rather than guessed.
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
  **The MODULE STAYS**, per the reading in request.md and the GM's ratification of it: three frozen
  city exhibits import it, and so does `wip/shiro_daika/frame.py` (156 lines, part of a 1,732-line
  in-progress capital package - only `frame.py` imports it). `pyproject.toml:69` type-checks it and
  live tests price the tango/nagahara programs through it, which is the load-bearing half; the
  frozen-gen half is weaker, since `dev/pool.md:102` says legacy gens are never re-run.
- **FR-006** `make hamlet-floor` is removed: the target and its recipe. **The module stays** -
  `test-full` (`Makefile:1208`) runs it through `make test COV_FLOORS=1`, and the phase itself is
  `Makefile:1303` inside the `test:` recipe. (The first draft called 1303 "test-full invoking it
  directly"; it is in a different target, and a precise-but-wrong pointer is worse than a vague one -
  this repository's own recorded lesson.) No other route sets `COV_FLOORS=1`, so the GM's reason
  holds. **What is LOST, stated rather than dropped**: `--list` was reachable only through this
  target, so the module set can no longer be asked for without running the gate.
  Two corrections that make the naive version of this requirement IMPOSSIBLE:
  - **the registry row is RE-POINTED, not removed.** `hamlet_floor.py:182` carries
    `if __name__ == "__main__":`, so `test_operations_registry._entry_points()` counts it; deleting
    the row fails `test_every_entry_point_has_a_registry_row`, and deleting the block instead breaks
    the gate phase that runs the module as a program. The row becomes
    `("test-full", "cheap")` - the target that actually runs it, so a bare `python3 -m` refusal still
    names a command that exists. Same mechanism feature 193 met; met again here.
    **The cost stays `cheap`, and that needs a half-line comment at the row**: it prices the MODULE's
    operation, and flipping it to `expensive` would make `test-full` remotely dispatchable and give it
    its own S3 cache location (`ci/__main__.py:105`, `dispatch.py:74`). A later reader must not
    "correct" it.
  - **there is no `.PHONY` entry to remove.** `hamlet-floor` appears on no `.PHONY` line (measured);
    `citybudget` does. Naming one would send the implementation to "fix" something adjacent.
- **FR-007** Every pointer to either removed target, **to its route in ANY OTHER NOTATION**, or to
  `citybudget`'s removed CLI is corrected, over the search space feature 193 established: **every file outside `specs/`**. Excluded
  as dated records: `pool/**/*.notes.md`, `legacy-hand-authored-pool/**/*.notes.md`,
  `wip/*.notes.md` and `docs/review-ledger.md`. Four site classes a target-name sweep cannot see:
  - **live doctrine naming the CLI**: `settlements/cities/sizing.md:85` says *"Audit it with
    `python3 citybudget.py --plan --population 3000 --river`"*, in a file whose header says to read
    it BEFORE picking any wall dimension. After FR-005 that capability exists in NO form, so the
    sentence must say the audit route is gone rather than quietly disappear.
  - **the Makefile's own contradicting notes**: `:11-14` ("restoring `citybudget`") and `:436`
    ("`citybudget` RETIRED ... 0 live consumers", which was never true).
  - **DERIVED COUNTS, which are not pointers**: `_invocation.py:189` says *"The 20 entry points"*
    (measured 19, becoming 18), and `test_operations_registry._entry_points()`'s docstring asserts
    that `citybudget` IS an entry point.
  - **A ROUTE IN ANOTHER NOTATION**: `hamlet_floor.py:4`'s own docstring advertises
    `python3 -m l7r.diagram.tools.hamlet_floor --list`, which no sweep for `hamlet-floor` finds - and
    after the re-point, the refusal a bare invocation earns sends the reader to `make test-full`,
    which offers no `--list`. Same blind spot on this side that round 1 closed on the other.

## Decisions Recorded

- **D1 - the argument convention is a comment line, not a new file or a schema.** Priced
  alternatives: a YAML sidecar (a second place to forget), and extending the single `##` line (it is
  already the widest line in the file and cannot hold three arguments' prose). A comment directly
  under the target keeps the documentation three characters from the thing it documents - the same
  argument that put the `[category]` tag there in feature 191.
- **D2 - `citybudget`'s module is kept, and this is now the GM's own decision rather than a session
  narrowing.** Told that `wip/shiro_daika/frame.py` imports it, they ruled: *"Leaving the module is
  fine as long as the make target for citybudget is gone."* **Stated consequence**: with the CLI gone
  the planner cannot be RUN at all - it survives as a library other code imports. That is what the
  instruction asks for, and FR-007 makes `sizing.md` say so rather than lose the sentence.
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
- **SC-003** An untruncated sweep finds no reference to either removed target, **to its route in any
  other notation**, or to `citybudget`'s CLI, outside `specs/` and the four record classes FR-007
  names. The other-notation clause is what lets this criterion fail on `hamlet_floor.py:4`.
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
- **Round 2 (`spec-fidelity`): CHANGES REQUIRED**, three items, all applied. It VERIFIED the
  re-pointed row end to end - `test-full` matches the registry regex, both directions of the registry
  test pass, and it priced the row's three other consumers (a `cheap` target is refused for a paid
  run before a Context is built, and the cache-location test enumerates only `expensive` rows), so
  nothing breaks. The three items: FR-002's count was 24 and is 25 (`hamlet-floor` declares no
  argument, so removing it subtracts nothing); FR-006 cited `Makefile:1303` as `test-full` invoking
  the module "directly" when 1303 is inside the `test:` recipe behind `COV_FLOORS`; and FR-007 had
  the same other-notation blind spot on the hamlet-floor side that round 1 closed on the citybudget
  side - `hamlet_floor.py:4` advertises `--list` in a form no sweep for the target name finds. The
  round-1 sentence recording what `--list` costs had been dropped in the rewrite and is restored.
- **Round 3 (`spec-fidelity`): FAITHFUL.** *"Implement it."* It re-measured each corrected fact -
  the 25 against `parse()`, `Makefile:1209` as the only `COV_FLOORS=1` assignment in the tree, and
  `hamlet_floor.py:4` as the only non-target-notation route to `--list` - and ran a last completeness
  check nobody had: no reference to either target exists in `scripts/`, `l7r/diagram/ci/` or any
  buildspec, so the removals cannot reach the remote build. Three editorial slips fixed in the same
  edit: a stale "Three site classes" above four bullets, an SC-003 that had not picked up FR-007's
  widening, and the status line.
