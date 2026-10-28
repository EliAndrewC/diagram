# 446-counter-only-landings - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-28 -->
### T01 - the counter-only delta and the cohort skip (D1, D2)

`codeid`'s counter-block functions (written with their tests), `cohort_known.counter_only` and `same_key`'s third test,
`cohort_gate.py counter-only`, `land.py` skipping both cohorts on a counter-only delta.

### T01 Approach (checklist part A)

1. **The goal, in the world.** A landing that only adds counters rolls no cohort; any other rolls both.
2. **The constraints.** FR-001, FR-002, FR-004; D1, D2.
3. **Where each comes from.** G: the GM's words, 2026-10-28 (`request.md`).
4. **Do they describe the world here?** 133 of 136 `if __debug__:` blocks under `l7r/` are counter blocks, measured 2026-10-28 (an
   AST walk of every one through `is_counter_block`).
5. **The order.** First.
6. **The exits.** Green: `tests/pipeline/test_codeid.py`, a `same_key` test (counter-only successor the same engine, an added file
   not), and a `land.py` test (cohorts skipped on a counter-only delta, run on another, the full suite on both), each skip red with
   its condition deleted.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** none
8. **The budget.** One landing.
9. **Done, measured.** A counter-only landing prints the skip and the push's cohort gate passes it.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

**Performance work?** no - tooling.

