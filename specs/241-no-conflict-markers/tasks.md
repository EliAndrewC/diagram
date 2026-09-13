# Feature 241 - tasks

Spec DRAFT; `spec-fidelity` round 1 dispatched before implementation (constitution XVI). Every task is
classified `research: rendering` or `research: physical`. **NOTHING here is physical**: this feature is
about what a commit may contain, not about how a place was built. Its measurements are the two incidents
in `research.md` R1, both from this session's own record.

- [x] T01 `scripts/_hm_conflict.py` - the ONE detector, shared by the hook and the backstop the way
      `_hm_make.recipe_comment_hazards` is: the triple in order on lines that are not prose, with the
      markers BUILT so the file does not trip itself (FR-001, FR-004).
      research: rendering
      verify: DONE. Runs over the whole tree: 3,037 tracked files, none flagged - including this feature's own spec, research and suite, all of which carry markers as examples.
- [x] T02 `scripts/conflict-marker-hooks.sh` - refuses a `git add` / `git commit` that would stage a
      conflicted file, judging what each form would actually stage, naming the files, recording per rule
      and escaping through `_hookmatch.py` (FR-002, FR-003, FR-005).
      research: rendering
      verify: DONE. Measured on a real git tree: `git add -A` with one tracked and one untracked conflict is blocked naming both; `git commit -am` blocked; `git add clean.md` passes.
- [x] T03 The gate-phase backstop, in the skill Makefile's `static` beside `check-file-scale.py` and
      `spec-lint.py` - because a hook cannot see a conflict that is already COMMITTED (FR-006).
      research: rendering
      verify: DONE. `make static` prints "conflict-markers: none in 3037 tracked file(s)" and the suite proves it FAILS on a committed conflict and names the file.
- [x] T04 `scripts/test-conflict-marker-hooks.sh`, run by `make hooks-test` (FR-007).
      research: rendering
      verify: DONE. 18 cases, 0 failures, including the case a state-based rule gets wrong - a RESOLVED merge's own `add -A` with MERGE_HEAD present, which passes - plus the Markdown underline, the fenced/indented/inline examples, the bare escape refused and the grep that is not an escape.
- [x] T05 The row in `CLAUDE.md`'s enforcement table, carrying both incidents and why the rule is on
      content rather than on merge state (FR-008).
      research: rendering
      verify: DONE. In the table after feature 236's spec-lint row.
- [ ] T06 `make hooks-test` and `make done` green, then land.
      research: rendering
