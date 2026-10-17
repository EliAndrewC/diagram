# Tasks - feature 383, tooling caches, one-process push checks, and the hourly step-back

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

### Phase 1 - the caches and the cheap fixes

- [x] T01 The cache layers (plan D1): `content_ids`, `FileFacts`, `ResultMemo` in `scripts/record/record_cache.py`; tests (a changed file and a changed extractor miss; `L7R_CACHE_OFF=1` bypasses)
      research: rendering
      verify: DONE. DONE. content_ids/FileFacts/ResultMemo in record_cache.py; tests/tooling/test_content_cache.py 13 passed (changed file and changed extractor miss, cache off bypasses, failure never kept); tooling tree 1776 passed
- [x] T02 The record and glossary build checks (plan D2): `scripts/gates/memo_check.py` and the Makefile's CHECK branches; the splitter's comment test by bisection; tests (SC-002: same answer on and off, a changed input re-runs, a failing run not kept)
      research: rendering
      verify: DONE. DONE. memo_check.py presets record/glossary (inputs measured, R1), store.MEMO per-file memo (notes, cited URLs, registry items), page_html tables once per build, split.headings by bisection (test_record_assembly); record CHECK replay 0.15 s, rebuild after an edit 4.85 s vs 5.46 s cold (R4); test_content_cache memo tests
- [x] T03 The four whole-tree checks on per-file facts (plan D3): research pointers, duplicate defs, function cap, conflict markers; the rest measured (research R3), the Affects check reading its features once; tests (SC-002 per check)
      research: rendering
      verify: DONE. DONE. research pointers, duplicate defs, function cap, conflict markers on FileFacts; partial citations measured no win and reverted, speckit-todo reads features once (R3); test_content_cache: each check same with cache on/off and finds a fault put in after a cached run, and pointers/conflicts over this repository
- [x] T04 The ledger check costs a pass once (plan D4); tests (SC-003: same answers, no transcript read when all are costed)
      research: rendering
      verify: DONE. DONE. ledger_owed keeps costed passes (path, size, mtime) and lists transcripts once; test_content_cache: no transcript read once costed, a grown transcript re-costed, same answers with no cache; 0.89 s -> 0.10 s
- [x] T05 The review lookup (plan D5): one batched read of the base; out of the gate start and the turn's end; the snapshot at dispatch; `test-pair-hooks.sh` (SC-004)
      research: rendering
      verify: DONE. DONE. review_owed reads the base by one RevReader and each tasks.md once; pair-hooks gate branch runs as typed, stop retired (no-op), dead helpers removed; test-pair-hooks 85 passed incl. the trace that no review lookup runs at gate start or stop; review lookup 0.6 -> 0.37 s
- [x] T06 check-bundle (plan D6): the base cached by revision, the helpers in-process; tests (SC-005)
      research: rendering
      verify: DONE. DONE. check-bundle helpers in-process (source_pages too), the base revision's record files kept by commit (rev-files); bundle compared with HEAD's: identical but its own out path; 2.2 -> 1.5 s; test_content_cache rev-files test
- [x] T07 The old-layout check retired (plan D7)
      research: rendering
      verify: DONE. DONE. check-old-layout.py removed with its calls in static and sync-with-main and its mentions; split-path comments marked as history; sync-with-main suite 124 passed
- [x] T08 Phase 1 measured (`push_check_times.py` into `measurements.json`), the tooling tests and `make hooks-test` green, landed with `make land-tooling`
      research: rendering

### Phase 2 - the push checks in one process
      verify: DONE. DONE. phase 1 measured (R6: the same checks as separate processes 19.87 -> 3.43 s), tooling tree 1776 passed, hooks-test green; landed with make land-tooling (0906d798a, with phase 2 and 3's tooling)

- [x] T09 The runner (plan D8) and the self-test stamp (plan D9): `scripts/gates/push_checks.py`, `sync-with-main.sh` calling it once; tests (SC-006: alone and in the runner, passing and seeded to fail; a changed imported module re-runs a kept self-test)
      research: rendering
      verify: DONE. DONE. scripts/gates/push_checks.py runs every Python push check in one process (gate-stamp and the closing check rows, escapes pass --skip), self-tests stamped by code sha incl. imports; sync-with-main calls it once; tests/tooling/test_push_checks.py 16 passed (alone vs in-process on this tree and seeded to fail, first refusal stops, a changed import re-runs a kept self-test); test-sync-with-main 124 passed
- [x] T10 Phase 2 measured, `test-sync-with-main.sh` and `make hooks-test` green, landed with `make land-tooling`
      research: rendering

### Phase 3 - the hourly step-back
      verify: DONE. DONE. phase 2 measured (R6: the runner 1.92 s against 19.87 s), test-sync-with-main 124 and hooks-test green; landed in 0906d798a

- [x] T11 The checkpoint (plan D10) and the hold (plan D13): `review_owed.checkpoint`, `owed(checkpoint=True)`, `tick-task.py`'s refusal, no escape; tests (SC-007)
      research: rendering
      verify: DONE. DONE. scripts/reviews/checkpoint.py (state, open, close, hold) on the glyph clock; tick-task.py asks checkpoint_hold, no escape; tests/tooling/test_checkpoint.py 7 passed (under an hour nothing held; on the hour held until ruled; owed units held until dispatched)
- [x] T12 The step-back (plan D11, D12): `make step-back`, `scripts/reviews/stepback_bundle.py`, the `hour` trigger in `hm_arbiter.py` and its rulings, the round arbiter's contract; tests (SC-007)
      research: rendering
      verify: DONE. DONE. make step-back, scripts/reviews/stepback_bundle.py (time, dispatches, refusals, tasks, words, MANIFEST), hm_arbiter hour rulings continue/change-route with for_gm, a quiet continue adds no GM row, the clock closes on ruling; round-arbiter.md An hour trigger; test_checkpoint covers each
- [x] T13 The replays (SC-008): the step-back on 374's batch 13 hour and on a quiet hour of the same session, recorded in `research.md`
      research: rendering
      verify: DONE. DONE. replays recorded in research R5: batch 13 hour -> change-route naming PART_GAP_FT, the offset ladder, the reach and the seat margin, room first; the quiet hour -> continue
- [x] T14 The text: `CLAUDE.md` (the pair guard's row, the checkpoint), `docs/reviews.md`, `docs/guards.md`, `docs/efficiency-tooling.md`
      research: rendering
      verify: DONE. DONE. CLAUDE.md (pair guard row: the checkpoint; the push row: push_checks.py), docs/reviews.md (the checkpoint; the stop branch retired), docs/guards.md, docs/efficiency-tooling.md; make docs regenerated
- [x] T15 Close: SC-001 measured, the gate, `make feature-report F=383 WRITE=1`, landed; this session's hourly cron deleted (plan D14)
      research: rendering
      verify: DONE. DONE. SC-001 measured (R6: 19.87 s -> 1.92 s in one process), the gate green on this content, make feature-report F=383 WRITE=1 written, the tooling landed in 0906d798a, the hourly cron ddf30448 deleted (CronList: no scheduled jobs); the rest lands by the push carrying this tick
## Amendment 1 (the GM 2026-10-13: skip what the clone already passed; quote-verbatim's cache)

- [x] T16 The reads recorded and reused (plan D15, D16): `tests/tooling/_test_deps.py`, `_deps_site/sitecustomize.py`, `make test-file`, `land-tooling.sh`; tests (SC-010); measured
      research: rendering
      verify: DONE. DONE. tests/tooling/_test_deps.py + _deps_site/sitecustomize.py record each tooling test file's reads (in-process and in Python children) on a whole pass, in make test-file, the gate's tooling run and land-tooling's reuse run; land-tooling reuses with L7R_TEST_DEPS=reuse; test_reuse_and_quotes 4 passed; 88 of 126 files reusable, 36.21 -> 27.58 s (m:land-tooling-tests-reuse, scripts/measure/tooling_reuse_time.py)
- [x] T17 quote-verbatim's verdicts kept (plan D17); tests and the byte-for-byte comparison (SC-011)
      research: rendering
      verify: DONE. DONE. quote_verbatim.verdict kept in a ParseCache by passage and page sha256 under the module's code sha; report byte-identical with L7R_CACHE_OFF=1 (0049); second run 6.25 -> 1.29 s; test_reuse_and_quotes: a changed passage or page judged afresh, kept on disk
- [x] T18 Close: the tooling tests, `make hooks-test`, the gate, the report, landed
      research: rendering
      verify: DONE. DONE. tooling tests 1796 passed, make hooks-test green, make done green, the report written; landed by the push carrying this tick

- [x] GM review (make gm-reviewed F=383) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)

## Amendment 2 (the GM 2026-10-13: the savings measured, then the rest of a landing)

- [x] T19 Each step of a landing timed (plan D21); the suite's case; landed alone, then a landing measured as the before (SC-013)
      research: rendering
      verify: DONE. DONE. land-tooling times prepare, worktree, patch, guard-suites, tooling-tests, checks and push into its log and land-tooling-steps.jsonl; the suite green (28); landed alone first, the before landing measured 113.98 s (m:land-tooling-landing-before)
- [x] T20 Git questions kept and asked again; Python children adopted; relative os.open ignored (plan D18, D19); tests (SC-012)
      research: rendering
      verify: DONE. DONE. tests/tooling/_deps_site/l7r_dep_rules.py: read-only git questions kept with their answers and asked again (STORE_VERSION 2), Python children given a fresh environment adopted, an os.open by name under a directory handle ignored; test_reuse_and_quotes 5 passed with a fixture repository; always run 38 of 126 -> 18 of 127 (tooling_reuse_time.py)
- [x] T21 The ignored reads made known and every other cause looked at (plan D20); research R9 (SC-014)
      research: rendering
      verify: DONE. DONE. CACHE_READS gains the semantic-id cache and the translation pairs; one fixed SPECIFY_FEATURE; test_makefile_recipe_comments reads the tracked Makefiles; 0 kept files blocked by an ignored read; the 18 remaining files recorded in research R9 with their 41.4 test-seconds and why each stays
- [x] T22 One run per test file and the checks side by side in a landing (plan D22); tests (SC-013)
      research: rendering
      verify: DONE. DONE. make hooks-test HOOKS_PYTEST_SKIP=tests/tooling/ and the plugin in its pytest phase; land-tooling runs the guard suites and the tooling tests side by side; the suite green (28, the overlap and a named failing job); the after landing: guard-suites 17.92 s beside tooling-tests 25.07 s, checks 25.11 s wall
- [x] T23 Close: measured after (SC-012, SC-013), the remaining steps looked at (plan D23), the gate, the report, landed
      research: rendering
      verify: DONE. DONE. measured after: tooling reuse 27.58 -> 19.35 s (m:land-tooling-tests-reuse-a2), a landing 113.98 -> 37.05 s at load 3.4-3.5 (m:land-tooling-landing-before/-after), the claims gate 8.53 -> 1.65 s (m:claims-gate-push); research R9; the gate green; the report written; landed by the push carrying this tick

## Amendment 3 (the GM 2026-10-17: the always-run files, tests not imported, the guard suites, Sonnet 5.5 trials first)

- [x] T24 The trial tool and the cases (plan D24): `scripts/measure/model_trial.py`; two cases per check chosen and prepared
      research: rendering
      verify: DONE. DONE. scripts/measure/model_trial.py (catalog --replayable, prepare as a separate clone at the recording clone's HEAD, bundles frozen, snapshots rebuilt, run-all queued, usage); tests/tooling/test_model_trial.py 4 passed; the 14 cases in research R10, one with fixed findings and one clean per check
- [x] T25 The 42 Sonnet 5.5 runs, scored; tiers, tier table, docs and the CLAUDE.md pointer (plan D24; SC-018)
      research: rendering
      verify: DONE. DONE. 42 Sonnet 5.5 runs scored (research R10): every check missed a known finding in all or most runs, none moves; Sonnet found two real modal errors Opus missed; tier table notes, docs/spec-kit-and-reviews.md Models tried, CLAUDE.md pointer; test_agent_models 8 passed
- [x] T26 Not importing what will not run (plan D25): the plugin's ignore_collect, quick's collection measured and cut (SC-016)
      research: rendering
      verify: DONE. DONE. the tooling plugin ignores reused files at collection (12.9 -> 10.7 s in the clone, 296 tests); quick measured with make collect-cost: testmon already imports 5 of 283 test modules per worker, the 2.5 s worker start not cut (research R10); targeted runs collect only what they name; the gate's full collection recorded
- [x] T27 The always-run files traced (plan D26); strace's overhead measured (SC-015)
      research: rendering
      verify: DONE. DONE. the preloaded C-library recorder (D26), checked each run against Python's (one gap found, Python's, fixed); always run 18 of 127 -> 0 of 128; a fresh worktree reuse run 18.39 s / 61 tests at load 8.1 (research R10)
- [x] T28 The guard suites by what their cases read (plan D27) (SC-017)
      research: rendering
      verify: DONE. DONE. 44 landings replayed: sync-with-main and gate-stamp re-ran on 42 (whole-tree inputs); suites now traced by what they read (38 of 44), sync-with-main 36.2 -> 17.9 s (case_11 split, 8 parts), hooks-test idle 16.1 -> 2.6 s; tests/tooling/test_file_log.py 4 passed (research R10)
- [x] T29 Close: a landing measured before and after, the gate, the report, landed
      research: rendering
      verify: DONE. DONE. a landing 37.05 -> 30.04 s (m:land-tooling-landing-a3; 113.98 s before amendment 2), 121 of 128 tooling files reused, guard suites 2.76 s; the gate green; the report written; landed by the push carrying this tick

## Amendment 4 (the GM 2026-10-17: the serial guard suites, and the tooling tests a landing still runs)

- [x] T30 The slow guard suites in parts or without idle waits (plan D28); timed whole before and after (SC-019)
      research: rendering
      verify: DONE. DONE. main-tree 57.7 -> 18.9 s, no-poll 48.4 -> 12.2, finished-run 39.1 -> 11.3, pair 23.5 -> 12.8-17.4, review-gate 21.8 -> 8.9, check counts unchanged; parts capped by the cores per running suite; make parts-sweep the same at 1/2/3/8 parts (research R11)
- [x] T31 The whole-repository tooling tests (plan D29) (SC-020)
      research: rendering
      verify: DONE. DONE. test_content_cache's whole-repository test one per check, side by side (9.4 -> 6.0 and 3.6 s); the pointer check's 5.1 s uncached run is the floor, three faster filters measured slower and reverted; open_questions measured and kept (research R11)
- [x] T32 The tooling run's start-up (plan D30) (SC-020)
      research: rendering
      verify: DONE. DONE. the start measured part by part (workers, a controller-side decision, byte-code first): none gained, each reverted and recorded (research R11)
- [x] T33 Close: a landing measured before and after, the gate, the report, landed
      research: rendering
      verify: DONE. DONE. a landing 30.04 -> 27.28 s (m:land-tooling-landing-a4); research R11; the gate green; the report written; landed by the push carrying this tick

## Amendment 5 (the GM 2026-10-17: the gate's tooling run reuses, and reuse per test)

- [x] T34 The gate's tooling run reuses; the tooling hash reads scripts/ whole (plan D31) (SC-021)
      research: rendering
      verify: DONE. SC-021 met (research R12; m:gate-tooling-makefile-a5). After a Makefile-only edit, the gate's full run reused 1,739 of 1,824 tooling tests with their coverage carried; the 85 that ran are the tests that read the Makefile; all floors at 100%; 132 s against 167 s. Two gates green; hash test red on the old glob.
- [x] T35 A pass kept per test (plan D32) (SC-022)
      research: rendering
      verify: DONE. SC-022 met (R12; m:source-page-edit-a5, m:tooling-reuse-a5). One source-page edit re-runs 15 tests, against 219 per file. An unchanged tree reuses 1,825 of 1,827 in 6.5 s. Store 10.8 MB. D32b fixed a soundness defect: a delta.py edit now re-runs 178 tests, not 36.
- [x] T36 Tests of code moved off the real repository, case by case (plan D33) (SC-022)
      research: rendering
      verify: DONE. R12 table. 12 tests of code are on copies of the pages they name, or on records of their own; data reads went from 475-4,656 files to 155 or fewer, assertions unchanged. The tests whose subject is the record's data are kept, with reasons.
- [x] T37 Close: the gate, the report, landed
      research: rendering
      verify: DONE. Two gates, the second green (221 s). Feature report written. The arbiter's step-back ruling was continue; its tooling fix is settled and landed. Tooling landed mid-feature three times: the reads fix, the new-file guard, the make-only refusal.
