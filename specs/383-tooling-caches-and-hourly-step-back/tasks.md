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
- [ ] GM review (make gm-reviewed F=383) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
