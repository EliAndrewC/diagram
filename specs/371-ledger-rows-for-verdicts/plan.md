# Implementation Plan: a ledger row for every pass of every check

**Branch**: none (main, in the session clone) | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 3)

## Summary

Log each check's pass where feature 375's hooks already see it return, with its cost cells computed from the agent's
transcript exactly as `make review-cost` computes them; a pass is answered by a measured-table row carrying its check and those
cells; a script lists the unanswered passes with the row to add, reports at every commit and refuses at the push.

## Technical Context

**Language**: Python 3.14 and bash (the hooks). **Dependencies**: none new - `scripts/reviews/review_cost.py` (`cost`, `cells`)
and `scripts/reviews/ledger_lint.py` (`CHECKS`, `measured_rows`). **Testing**: pytest (`tests/tooling/`) and the hook suites
(`tests/hooks/`, `make hooks-test`). **No generator change**, so no map moves, no perf bookends, no review occasions.

## Constitution Check

- I-V, VII-IX: N/A - tooling only; no UI, pool content, SOURCE block or setting detail.
- VI: PASS - each task names its test; `make hooks-test` and `make done` before landing.
- X: PASS - test-first; the new script under the 100-statement cap and 100% where coverage reaches (`scripts/` is outside the
  engine floor; its tests are its proof).
- XII: N/A - nothing the world sees changes. XIII: PASS - the hook suites and the gate green before and after.
- XVI: PASS - every check the ledger names, every pass, no carve-out (spec rounds 1-3).

## Decisions

- **D1 - the log.** `<git common dir>/check-passes.jsonl`, one JSON line per RETURN: `date`, `check`, `subject`, `agent`,
  `wall`, `tokens`. `hm_checks.py` writes it in its own branch, apart from the page-check state (which a switch of feature
  resets, plan review 1): at SubagentStop - whose payload carries `agent_type`, `agent_id` and `agent_transcript_path`
  (feature 375's `subagent-stop-probe`) - an agent whose type is in `CHECKS` gets a line, its cells computed from the
  transcript with `review_cost.cost` / `cells`; at PostToolUse a FOREGROUND (`completed`) check gets one too, its transcript
  found by `review_cost.transcript`. Nothing is held pending between the two events. The subject is the first line of the
  dispatch's prompt (the transcript's first user message), cut to 100 characters, with `|` and newlines made spaces so the
  printed row passes the lint. Append-only: opened in append mode, never rewritten.
- **D1b - a resumed agent, and a pass logged twice.** One agent id may log several lines: a check resumed after it returned
  stops again (measured by plan review 1: 2 agents, 3 of 78 stops), and a foreground check may be seen by both events. The
  PASS is the agent; its cells are its LATEST line's, computed over its whole transcript - which is what `make review-cost`
  prints once it has finished, so the row the session copies answers it (SC-004).
- **D2 - CHECKS.** `ledger_lint.CHECKS` gains `modal-depiction`, `modal-form`, `modal-research` and `source-filter` (spec
  FR-001), so their rows pass the lint.
- **D3 - the answer.** `scripts/reviews/ledger_owed.py` reads the log as one pass per agent id (its latest line, D1b); a pass is answered when some measured row has the same `check`, and
  its `wall` and `tokens` cells equal the pass's (whitespace-normalized). It prints each unanswered pass as the row to add -
  date, check, subject and cost filled, the five judgment cells `?`.
- **D4 - where it runs.** At every commit `ledger-hooks.sh` adds the list as context and never refuses for it (FR-004); at the
  push `sync-with-main.sh` runs `ledger_owed.py --refuse` beside `ledger_lint.py`, refusing while a pass logged in that clone
  is unanswered, escape `LEDGER_ROWS_OK="<reason>"`, recorded in the bypass log. `make ledger-owed` lists them by hand.
- **D5 - tests.** `tests/tooling/test_ledger_owed.py`: a fixture log and ledger - fires with no row, quiet with it, two
  same-day rounds told apart by their cells, the printed row's cells; `tests/tooling/test_hm_checks.py`: a check's return appends one line with the
  transcript's cells, a non-check agent appends none, a foreground check is logged at PostToolUse, a resumed agent's second
  stop appends a second line; the push suite
  (`tests/hooks/test-sync-with-main.sh`) refuses an unanswered pass and passes once answered; `test-ledger-hooks.sh` reports
  without refusing.
- **D6 - the record.** Root `CLAUDE.md`'s enforced table (the `ledger-hooks.sh` row), `docs/guards.md`, and `docs/reviews.md`'s
  ledger paragraph say a pass is logged and its row owed at the push.

## Project Structure

```text
scripts/hooks/lib/hm_checks.py       D1
scripts/reviews/ledger_lint.py       D2
scripts/reviews/ledger_owed.py       D3 (new)
scripts/hooks/ledger-hooks.sh        D4 (report at commit)
scripts/sync-with-main.sh            D4 (refuse at the push)
Makefile                             D4 (make ledger-owed)
tests/tooling/test_ledger_owed.py, tests/tooling/test_hm_checks.py, tests/hooks/test-sync-with-main.sh, tests/hooks/test-ledger-hooks.sh   D5
CLAUDE.md, docs/guards.md, docs/reviews.md   D6
```

## Review history

- **Plan review round 1 (2026-10-10): CHANGES REQUIRED.** A resumed check's first cells went stale and a feature switch could
  drop a pending pass: now a line per return written at that event with nothing pending (D1), the pass is the agent and its
  latest line's cells count (D1b). The subject is sanitized and the printed row asserted lint-clean (D1, D5).
