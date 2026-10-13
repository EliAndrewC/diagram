# Tasks - feature 383, tooling caches, one-process push checks, and the hourly step-back

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

### Phase 1 - the caches and the cheap fixes

- [ ] T01 The cache layers (plan D1): `content_ids`, `FileFacts`, `ResultMemo` in `scripts/record/record_cache.py`; tests (a changed file and a changed extractor miss; `L7R_CACHE_OFF=1` bypasses)
      research: rendering
- [ ] T02 The record and glossary build checks (plan D2): `scripts/gates/memo_check.py` and the Makefile's CHECK branches; the splitter's comment test by bisection; tests (SC-002: same answer on and off, a changed input re-runs, a failing run not kept)
      research: rendering
- [ ] T03 The four whole-tree checks on per-file facts (plan D3): research pointers, duplicate defs, function cap, conflict markers; tests (SC-002 per check)
      research: rendering
- [ ] T04 The ledger check costs a pass once (plan D4); tests (SC-003: same answers, no transcript read when all are costed)
      research: rendering
- [ ] T05 The review lookup (plan D5): one batched read of the base; out of the gate start and the turn's end; the snapshot at dispatch; `test-pair-hooks.sh` (SC-004)
      research: rendering
- [ ] T06 check-bundle (plan D6): the base cached by revision, the helpers in-process; tests (SC-005)
      research: rendering
- [ ] T07 The old-layout check retired (plan D7)
      research: rendering
- [ ] T08 Phase 1 measured (`push_check_times.py` into `measurements.json`), the tooling tests and `make hooks-test` green, landed with `make land-tooling`
      research: rendering

### Phase 2 - the push checks in one process

- [ ] T09 The runner (plan D8) and the self-test stamp (plan D9): `scripts/gates/push_checks.py`, `sync-with-main.sh` calling it once; tests (SC-006: alone and in the runner, passing and seeded to fail)
      research: rendering
- [ ] T10 Phase 2 measured, `test-sync-with-main.sh` and `make hooks-test` green, landed with `make land-tooling`
      research: rendering

### Phase 3 - the hourly step-back

- [ ] T11 The checkpoint (plan D10) and the hold (plan D13): `review_owed.checkpoint`, `owed(checkpoint=True)`, `tick-task.py`'s refusal, `CHECKPOINT_OK`; tests (SC-007)
      research: rendering
- [ ] T12 The step-back (plan D11, D12): `make step-back`, `scripts/reviews/stepback_bundle.py`, the `hour` trigger in `hm_arbiter.py` and its rulings, the round arbiter's contract; tests (SC-007)
      research: rendering
- [ ] T13 The replays (SC-008): the step-back on 374's batch 13 hour and on a quiet hour of the same session, recorded in `research.md`
      research: rendering
- [ ] T14 The text: `CLAUDE.md` (the pair guard's row, the checkpoint), `docs/reviews.md`, `docs/guards.md`, `docs/efficiency-tooling.md`
      research: rendering
- [ ] T15 Close: SC-001 measured, the gate, `make feature-report F=383 WRITE=1`, landed; this session's hourly cron deleted (plan D14)
      research: rendering
