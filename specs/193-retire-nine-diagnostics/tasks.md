# Tasks - 193 Retire eight diagnostics

All `research: rendering` - make targets, tooling modules and the records that point at them. No
claim about how a place was built, farmed or lived in, so the three physical-research boxes do not
apply.

- [x] T01 `research: rendering` FR-001/002/003: eight targets, recipes, `.PHONY` entries, the root
      `FORWARD` list's `sun-audit`, eight `_invocation.OPERATIONS` rows, seven modules and seven test
      files. Verified: all eight `make <target>` report "No rule"; `why-placed`, `notes-census`,
      `pack-audit` and `hamlet-floor` all still resolve.
- [x] T02 `research: rendering` FR-009: `scatter_audit` split - 261 -> 118 lines. The residue was
      COMPUTED by AST reachability from the three kept roots, not listed. **The first attempt was
      wrong in the dangerous direction**: walking only the kept definitions reported `CROWN_FILLS`,
      `_NUM` and `re` as deletable, when the parser reaches all three through its module-level regex
      constants. Deleting a dependency breaks a gate rule; leaving an orphan only fails a check
      loudly. Verified: `parse_bases` imports, `adjudicate`/`main` gone, ruff clean.
- [x] T03 `research: rendering` FR-009: its test file 369 -> 245 lines, 18 adjudicator/CLI tests
      removed. Classified by AST, after a line-window classifier wrongly marked the POSITIONAL CROWN
      GUARD dead - it had spilled into the next test. Verified: 5 passed, 1 skipped.
- [x] T04 `research: rendering` SC-003: `tests/settlement/test_land.py` 43 passed, including
      `test_commons_keeps_scrub_off_every_recorded_marsh` - the cut took the adjudicator and left the
      parser the GM's own scrub-in-the-reeds rule depends on.
- [x] T05 `research: rendering` FR-004: `pyproject.toml` `project-includes` drops `tools/timings.py`
      only; `tools/pack_audit` and `tools/scatter_audit.py` stay, both being live and gate-tested.
- [x] T06 `research: rendering` FR-005/006: the untruncated sweep over every file outside `specs/`.
      Corrected: the skill `CLAUDE.md` (3 table rows + 2 doctrine lines), the skill Makefile,
      `tools/CLAUDE.md` (4 index rows), `waterfields/CLAUDE.md`, `dev/loop.md`, `dev/diagnostics.md`,
      `research/fields.md`, `research/vegetation.md`, `settlements/vegetation.md`,
      `future-work/farming-communities.md`, four engine comment pointers, two kept test comments,
      **and `.specify/memory/constitution.md` + `.specify/templates/tasks-template.md`**, which each
      cited `make sun-audit` as an EXAMPLE of a measuring tool. Records excluded per the ruling:
      `pool/**/*.notes.md`, `docs/review-ledger.md`, `specs/`.
- [x] T07 `research: rendering` FR-009: `.claude/agents/settlement-review.md`'s tooling section
      rewritten - the parser is still pointed at, the verdict is gone, and the GM's reasoning is
      recorded beside the agent's own admission that the verdict could not be trusted.
- [x] T08 `research: rendering` FR-007: `timings.md` kept and annotated as FROZEN, naming what a
      future measurement would have to rebuild.
- [x] T09 `research: rendering` FR-008: `docs/make-targets.html` regenerated - 63 -> 55 targets.
- [ ] T10 `research: rendering` SC-004: `make done` green, 100% coverage held, surface shrunk by the
      deleted modules rather than by an exclusion.
