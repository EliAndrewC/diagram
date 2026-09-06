# Tasks - 195 Targets that say what they do, and two removals

All `research: rendering` - make targets, their documentation, and the records that point at them.

- [x] T01 `research: rendering` FR-001: the argument-documentation mechanism (`##  NAME=<what>
      description` under a target; `make-docs.py` `argdocs` + `_args_cell`). Landed in the
      number-claim commit, which was out of order and is recorded as such in the spec.
- [x] T02 `research: rendering` FR-002: **27 of 27** argument-taking targets documented, one line per
      argument, each read off the RECIPE. A PARSER BUG was caught by verifying rather than trusting
      the script's own "documented 26": the value pattern was `(\S*)`, so `FILE=<test path>` failed
      and - because a miss BREAKS the loop - silently dropped every argument of four targets. Now
      non-greedy up to the two-space separator.
- [x] T03 `research: rendering` FR-003: `compound` says it composes a DRAFT the GM then refines, not
      that it draws the plan - the GM's question ("compounds are hand-drawn, so what is the target
      actually doing?") answered from the module's own docstring.
- [x] T04 `research: rendering` FR-004: `pack-audit` says HAND-DRAWN Mode A, and only that; the WHY
      is a Makefile comment, since `make-docs` publishes the `##` line verbatim.
- [x] T05 `research: rendering` FR-005: `make citybudget` gone - target, `.PHONY` entry, registry
      row, and the module's CLI (`main`, `guard()`, the `__main__` block) with its 8 CLI tests. The
      MODULE stays, on the GM's ratification; the planner is a library now and cannot be run.
- [x] T06 `research: rendering` FR-006: `make hamlet-floor` gone. The registry row is **RE-POINTED**
      to `("test-full", "cheap")`, not removed - the module keeps an `__main__` block the gate runs
      as a program, so a missing row fails `test_every_entry_point_has_a_registry_row` and deleting
      the block breaks the gate phase. The `cheap` cost carries a comment saying why it must not be
      "corrected" to `expensive`. Verified: registry tests 5 passed.
- [x] T07 `research: rendering` FR-007: the sweep over every file outside `specs/`, covering the
      routes in OTHER NOTATIONS a target-name sweep cannot see - `settlements/cities/sizing.md:85`
      (the removed `python3 citybudget.py --plan` audit), `hamlet_floor.py:4` (`--list`), the
      Makefile's two contradicting notes, the stale "20 entry points" count, and four index/doctrine
      rows. Records excluded: both pool trees' notes, `wip/*.notes.md`, `docs/review-ledger.md`.
- [x] T08 `research: rendering` FR-008: page regenerated - 55 -> **53** targets.
- [ ] T09 `research: rendering` SC-004: `make done` green, 100% coverage held.
