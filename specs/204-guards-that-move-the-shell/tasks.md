# Tasks: Guards That Move The Shell (feature 204)

Every task is `research: procedure`. Nothing here decides how a place was built, farmed or lived
in. The GM's words are in [`request.md`](request.md), the measurements in [`research.md`](research.md).

- [x] T01 spec review by `spec-fidelity` against `request.md` (constitution XVI), up to five rounds
      research: procedure
      verify: DONE. spec-fidelity: round 1 CHANGES (session name at firing time; subagent -> parent's clone), round 2 CHANGES (FR-009 must not read transcripts), round 3 FAITHFUL, 2026-09-07
- [x] T02 FR-011: `clone-sync-hooks.sh resolve` mode + a case in its suite
      research: procedure
      verify: DONE. clone-sync-hooks.sh resolve + 4 suite cases (map, transcript, SUBAGENT -> parent's clone, unresolvable) green in hooks-test 2026-09-07
- [x] T03 FR-001/002/003/004/005: `scripts/_hm_tree.py judge` - the effective-directory walk, the
      write targets, the verdict, the rewritten command
      research: procedure
      verify: DONE. _hm_tree.py judge: test-main-tree-hooks.sh 83/83 green 2026-09-07 - the incidents rewrite, named-main refuses, corpus 109/64/0
- [x] T04 FR-004/005/006/007: `main-tree-hooks.sh` becomes the wrapper - escape, derive main,
      resolve clone, call judge, emit rewrite/context or the refusal that names the cause
      research: procedure
      verify: DONE. main-tree-hooks.sh as the wrapper: rewrite emits updatedInput + additionalContext (suite section 1), refusals name the cause (section 2)
- [x] T05 FR-008: `guard_log` records session_id, cwd, tool, transcript, full command, context;
      the rebuild-loss comment corrected; `test_guard_firing_log.py` cases for main-tree
      research: procedure
      verify: DONE. guard_log fields: test_guard_firing_log.py 23 passed (session, session_name from the claim map, cwd, tool, full command, context); suite section 6
- [x] T06 FR-010: the corpus fixture + the replay section of `test-main-tree-hooks.sh`; the
      existing suite's incident cases re-expected as rewrites
      research: procedure
      verify: DONE. corpus fixture with per-row verdicts; replay through the hook: 173 -> 109 allowed / 64 rewrote / 0 refused, ~63 s; two replay traps recorded in FR-010
- [x] T07 FR-009: `make guard-log` listing (GUARD, SINCE, EVENT, FULL) with the name resolver
      research: procedure
      verify: DONE. make guard-log: test_guard_log_listing.py 4 passed; live run over the host log listed 40 main-tree firings for 2026-09-07
- [x] T08 FR-012: CLAUDE.md row + paragraph, docs/efficiency-tooling.md, the guard's header
      research: procedure
      verify: DONE. CLAUDE.md row + paragraph, docs/efficiency-tooling.md, the guard's header and _guardlog.sh's rebuild-loss comment
- [x] T09 `make hooks-test` green; `make test-file` on the changed pytest files; commit; push by
      `sync-with-main.sh done` (DIRECT route - no engine code)
      research: procedure
      verify: DONE. make hooks-test green 2026-09-07 (one pre-existing roster drift fixed on the way: page-check, soak); test-file green on test_guard_firing_log.py (23) and test_guard_log_listing.py (4); pushed by sync-with-main.sh done
