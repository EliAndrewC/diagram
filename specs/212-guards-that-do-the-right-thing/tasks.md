# Tasks: Guards That Do The Right Thing (feature 212)

Every task is `research: procedure`. Nothing here decides how a place was built, farmed or lived
in. The GM's words are in [`request.md`](request.md), the census in [`research.md`](research.md).

- [x] T01 spec review by `spec-fidelity` against `request.md` (constitution XVI), up to five rounds
      research: procedure
      verify: DONE. round 1 CHANGES (FR-002 context; FR-003 kept the verify rewrite + D7; FR-008 per branch), round 2 CHANGES (FR-004 normalization stated in full, substitution on raw), round 3 FAITHFUL, 2026-09-07
- [x] T02 FR-001: `_hm_make.py` targeted-pytest rewrite (paths, dirs, node ids, K=, output flags,
      pipeline tail, heredoc-aware match) + `why_not_make_target`; the Makefile's `K=`;
      `gate-hooks` subset accounting for `K=`/`::`; `make-only-hooks.sh` names the stopping token
      research: procedure
      verify: DONE. test-make-only-hooks.sh 66/66 (section 4: 8 rewrites incl. pipeline tail, -k -> K=, node id, dir, two files, env prefix, a pytest after a heredoc; 6 refusals name their token); Makefile K=; test-gate-hooks.sh 42/42 (K= and :: arm the subset, a whole test-file clears it); corpus: 11 of 18 bare-pytest rows rewrite
- [x] T03 FR-002: `_hm_make.py` Makefile-derived entry-point rewrite + `why_not_wrapped_target`;
      `make-only-hooks.sh` entry-point branch rewrites and lists what is wrapped
      research: procedure
      verify: DONE. test-make-only-hooks.sh section 5: ci engine-key/status/--route, a `$(ARGS)` recipe, switches show rewrite; scatter_audit, ci state, hamletgen refuse and the refusal lists the wrapped modules; corpus: 3 of 29 entry-point rows rewrite
- [x] T04 FR-003: `pair-hooks.sh` records-and-permits every gate shape `verify` cannot take, with
      the DISPATCH NOW context (detached vs foreground); the plain `make done` rewrite kept
      research: procedure
      verify: DONE. test-pair-hooks.sh 27/27: plain make done still -> make verify; FULL=1, make maps | tail, setsid nohup make done &, run_in_background gate permitted with DISPATCH NOW, gate_key recorded, detached vs FOREGROUND told; stop still refuses a half-open pairing
- [x] T05 FR-004: `_hm_shape.py` `file_watching_loop` (the five normalization steps) +
      `file-wait-loop` mode; `no-poll-hooks.sh` backgrounds the foreground form
      research: procedure
      verify: DONE. test-no-poll-hooks.sh 54/54: the 7 corpus shapes permitted backgrounded (| in the regex, a `$S/` path, 2>/dev/null, [ -s f ] && grep), quoted substitution / && curl / backtick refused, the foreground form backgrounded with run_in_background and told; corpus test 44 rows
- [x] T06 FR-005: `clone-sync-hooks.sh` runs `sync-in` on a clean stale clone under a 25 s bound and
      lets the edit proceed, else the refusal stands
      research: procedure
      verify: DONE. test-clone-sync-hooks.sh all green: a clean clone behind main is synced by the hook (fixture stub sync-in, tracked) and the edit allowed with the merged-in notice; a diverged clone still refused
- [x] T07 FR-006/FR-007: the guard suites (make-only, gate, no-poll, pair, clone-sync) carry the new
      cases; `test_guard_firing_log.py` gains the five (event, rule) rows; the corpus fixture
      labeled and replayed by `tests/tooling/test_guard_corpus.py`
      research: procedure
      verify: DONE. test_guard_firing_log.py 27 passed (targeted-pytest, entry-point, backgrounded-file-wait, recipe-comment-substitution rows); guard-refusals-2026-09.json labeled (183 rows) and test_guard_corpus.py 142 passed; make hooks-test green 2026-09-08T00:11Z
- [x] T08 FR-008/FR-009: research R1-R2 final numbers; CLAUDE.md rows and the rewrite paragraph;
      `docs/efficiency-tooling.md`; each guard's header
      research: procedure
      verify: DONE. research R1 per branch + R4; CLAUDE.md rows (make-only, guard-file + recipe comment, no-poll, pair, clone-sync) and the second-pass paragraph; docs/efficiency-tooling.md rows; make-only and pair headers
- [x] T10 FR-010 (the GM's request relayed 2026-09-07): `_hm_make.py recipe_comment_hazards`;
      `guard-file-hooks.sh` refuses a recipe comment that would run, on any Makefile, before the
      escape; suite section 5; `tests/tooling/test_makefile_recipe_comments.py` as the gate backstop;
      the guard-file escape judged after the file (the mention false positive found on the way)
      research: procedure
      verify: DONE. test-guard-file-hooks.sh 30/30 (section 5: the 207 shape refused with the marker, escaped forms and single quotes pass, any Makefile by Write); test_makefile_recipe_comments.py 2 passed (the tree's Makefiles carry no hazard; the detector fires on 4 forms, passes 7); the marker escape judged after the file
- [x] T09 `make hooks-test` green; `make test-file` on the changed pytest files; a green
      `make page-check` is not owed (no asset changed); commit; push by `sync-with-main.sh done`
      (DIRECT route: no engine code - the Makefile and `scripts/` route DIRECT behind a green
      hooks-test stamp); D7 raised with the GM in the landing report
      research: procedure
      verify: DONE. make hooks-test green 2026-09-08T00:20Z (4 suites re-run after the header edits, 17 unchanged); make quick green (2,952 passed then 11 selected after make docs regenerated docs/make-targets.html for the test-file help line); no asset changed so no page-check owed; committed and pushed by sync-with-main.sh done, DIRECT route; D7 raised with the GM in the landing report
