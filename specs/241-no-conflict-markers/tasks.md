# Feature 241 - tasks

Spec AMENDED after implementation measured the design (the fence exemption removed, the pathspec
enumeration replaced by asking git, the backstop added at the push) - so the review counter resets to zero
and the amended spec is re-reviewed (the GM 2026-09-12 on the five-round cap). Every task is
classified `research: rendering` or `research: physical`. **NOTHING here is physical**: this feature is
about what a commit may contain, not about how a place was built. Its measurements are the two incidents
in `research.md` R1, both from this session's own record.

- [x] T01 `scripts/_hm_conflict.py` - the ONE detector, shared by the hook and the backstop the way
      `_hm_make.recipe_comment_hazards` is: the triple in order at COLUMN 0, with the
      markers BUILT so the file does not trip itself, and what a command would stage asked of git rather
      than enumerated (FR-001, FR-002, FR-004).
      research: rendering
      verify: DONE. Runs over the whole tree: 3,045 tracked files, none flagged - including this feature's own spec, research and suite, all of which carry markers as examples. `--selftest` proves the detector fires: 9 content cases (the triple, a fenced triple, the lone underline, the indented example, out-of-order, the file marker with and without a reason, and past the head) and 4 command shapes.
- [x] T02 `scripts/conflict-marker-hooks.sh` - refuses a `git add` / `git commit` that would stage a
      conflicted file, judging what each form would actually stage, naming the files, recording per rule
      and escaping through `_hookmatch.py` (FR-002, FR-003, FR-005).
      research: rendering
      verify: DONE. Measured on a real git tree: `git add -A` with one tracked and one untracked conflict is blocked naming both; `git commit -am` blocked; `git add clean.md` passes; and the recorded incident's own shape `CL=$T; git -C $CL add -A` is blocked (rc=2) where the first implementation permitted it - R4.
- [x] T03 The backstop in BOTH places its two siblings run - the skill Makefile's `static` phase and
      `sync-with-main.sh` at push time, `--selftest` first in each - because a hook cannot see a conflict
      that is already COMMITTED, and the delta that lands one is a merge that often runs no gate (FR-006,
      R5).
      research: rendering
      verify: DONE. Prints "conflict-markers: none in 3045 tracked file(s)"; the suite proves it FAILS on a committed conflict and names the file, and passes on this repository, whose spec, research and suite all discuss markers.
- [x] T04 `scripts/test-conflict-marker-hooks.sh`, run by `make hooks-test` (FR-007).
      research: rendering
      verify: DONE. 28 cases, 0 failures: the two cases a state-based rule gets wrong (a RESOLVED merge's own `add -A` with MERGE_HEAD present, and `git add .` in a clean subdirectory while a marker sits elsewhere), the Markdown underline, the indented and inline examples, a FENCED triple flagged and then exempted by the file-level marker with a reason, the incident's own `CL=...; git -C $CL add -A`, a `cd` into the tree, `-u`, a clean directory pathspec, a commit message that names a file, the bare escape refused, and the grep that is not an escape.
- [x] T05 The row in `CLAUDE.md`'s enforcement table, carrying both incidents and why the rule is on
      content rather than on merge state (FR-008).
      research: rendering
      verify: DONE. In the table after feature 236's spec-lint row, carrying the departure from the approved state-based proposal (spec D1, Principle XVI) and what the content rule cannot see (D5).
- [ ] T06 `spec-fidelity` on the AMENDED spec, then `make hooks-test` and `make done` green, then land
      - and the report to the GM states the departure from the proposal they approved (Principle XVI).
      research: rendering
