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
- [x] T05 Close: the tooling tests and `make hooks-test` green, the gate, `make feature-report F=379 WRITE=1`, landed
      research: rendering
      verify: DONE. make done green (gate log done379.log), hooks-test green, tooling tests 34 passed, feature-report written; landed by the push carrying this tick

## Amendment 1 (the GM 2026-10-10: a tooling fix lands alone, mid-feature)

- [x] T06 `scripts/land-tooling.sh` and `make land-tooling FILES=` (plan D8, D9); its suite `tests/hooks/test-land-tooling.sh` over real git repos (SC-003)
      research: rendering
      verify: DONE. scripts/land-tooling.sh + make land-tooling; tests/hooks/test-land-tooling.sh 17/17 over real git repos (SC-003: alone, no engine work, clean merge, non-tooling/conflict/failed check/unlanded-work test refused); in make hooks-test
- [x] T07 Done means landed (plan D10): `settle_fix` compares the TEST's blob on origin/main; tests (SC-004)
      research: rendering
      verify: DONE. settle_fix refuses until the TEST blob on origin/main equals HEAD's (on_main, fetches first); test_arbiter_fix SC-004 refused then passes after update-ref; 14 passed
- [x] T08 Close: the text (CLAUDE.md's session-clones bullet and guard table, `docs/session-clones.md`), tooling tests and `make hooks-test` green, the gate, the report, landed
      research: rendering
      verify: DONE. CLAUDE.md session-clones bullet + docs/session-clones.md; make done green (short-circuit: no engine change), tests/tooling 1582 passed, make hooks-test green incl. land-tooling 17/17 and feature-approval 48/48; report written; landed by the push carrying this tick

## Amendment 2 (the GM 2026-10-10: the arbiter before the GM)

- [x] T09 The spec review's round cap (plan D11, D12): the trip and refusal in `hm_review_round.py`, an `accept` or `process-fault` ruling read by `review-gate.sh` (a `continue` not); tests red on today's code (SC-005)
      research: rendering
      verify: DONE. hm_review_round spec_cap_refusal per pass (round:spec-fidelity|<f>#<pass>@N), a closed pass starts a new one; review-gate takes accept/process-fault via hm_arbiter spec-ruled on the spec's hash; test-review-round-hooks 77/77, test-review-gate 38/38, test_arbiter_fix 9 - red on old code
- [x] T10 `make arbiter-ask` and the contract and bundle for spec rounds and asks (plan D13); tests (SC-006)
      research: rendering
      verify: DONE. make arbiter-ask records ask:<subject> and builds its bundle in one command; the contract and bundle cover spec rounds and asks; test_arbiter_fix asks/bundle tests; exercised end to end in a scratch repo
- [x] T11 The text (plan D14) and the retired waiver (plan D15): CLAUDE.md, the constitution, both fidelity agents, `escalation-check.md`, `wakeup-hooks.sh`, `docs/spec-kit-and-reviews.md`, `docs/reviews.md`, `pair-hooks.sh`; tooling tests and `make hooks-test` green, the gate, the report, landed
      research: rendering
      verify: DONE. the text (CLAUDE.md, constitution XIII/XVI, both fidelity agents, escalation-check, wakeup-hooks, spec-kit-and-reviews, reviews, guards) and the retired waiver; make done green (419 s), tooling tests 1591 passed, hooks-test green; report written; landed by the push carrying this tick

## Amendment 3 (the GM 2026-10-10: "yes it covers the band-3 perf signoff too")

- [ ] T12 Band 3 to the arbiter (plan D16): `perf_review.py` (`arbiter_subject`, `arbiter_signed`, `check`, the refusal), `make perf-arbiter`, the arbiter's contract, the texts; tests red on today's code (SC-007); the gate, the report, landed
      research: rendering
