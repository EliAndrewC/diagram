# Tasks - feature 379, an arbiter's tooling fix is made, not lost

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The field and the record (plan D1, D2): `record_ruling` keeps `tooling_fix` with `"fix": "open"` on the ruling's row and on its GM-review row, refuses a `process-fault` without one, writes no `found.jsonl` row; `hm_arbiter.open_fixes(feature dir)`
      research: rendering
      verify: DONE. built and verified: tests/tooling/test_arbiter_fix.py 6 cases + test_hm_arbiter/gm_review/close_check/tick_task green (34 passed); hooks-test green; quick 499 passed
- [x] T02 The holds and the two commands (plan D3-D5): `scripts/tick-task.py` refuses any tick while a fix is open; `close_check.reasons` refuses too; `make arbiter-fix-done ID= NOTE= TEST=` and `make arbiter-fix-declined ID= REASON=`, each a closing row and a GM-review row
      research: rendering
      verify: DONE. built and verified: tests/tooling/test_arbiter_fix.py 6 cases + test_hm_arbiter/gm_review/close_check/tick_task green (34 passed); hooks-test green; quick 499 passed
- [x] T03 The contract (plan D1): `.claude/agents/round-arbiter.md` - the `tooling_fix` field and when to give one; a `process-fault`'s fault is its `tooling_fix`; no ruling tells anyone to file a tooling row
      research: rendering
      verify: DONE. built and verified: tests/tooling/test_arbiter_fix.py 6 cases + test_hm_arbiter/gm_review/close_check/tick_task green (34 passed); hooks-test green; quick 499 passed
- [x] T04 Tests red on today's code (SC-002) and the replay (SC-001, plan D6); CLAUDE.md's guard row and the targets' `##` lines (plan D7)
      research: rendering
      verify: DONE. built and verified: tests/tooling/test_arbiter_fix.py 6 cases + test_hm_arbiter/gm_review/close_check/tick_task green (34 passed); hooks-test green; quick 499 passed
- [ ] T05 Close: the tooling tests and `make hooks-test` green, the gate, `make feature-report F=379 WRITE=1`, landed
      research: rendering
