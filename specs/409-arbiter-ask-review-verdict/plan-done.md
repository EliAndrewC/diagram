# 409-arbiter-ask-review-verdict - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-22 -->
### T01 Approach

1. Goal: an `ask:` the session names as a spec or plan review (REVIEW=) is that review's verdict on the arbiter's accept.
2. Constraints: FR-001 to FR-005; the round-trigger paths unchanged; a ruling covers the spec or plan as it reads at the ruling.
3. Sources: the request G (the GM, 2026-10-22); the round-trigger behavior to copy G (features 379 a2, 385 T16); REVIEW= explicit G (spec-fidelity round 1).
4. Holds as written.
5. Order: hm_arbiter (ask, trip, record_ruling, spec_ruled, ruled), plan_gate.arbiter_accept, the Makefile, the docs, the tests, each new test red with the change removed.
6. Exits: (e) conform.
7. No search loop.
8. Budget: an hour.
9. Done: the two test files green (42), the four new tests red without the change.
10. n/a.
11. n/a.

<!-- plan-archive: archived 2026-10-22 -->
### T02 Approach

1. Goal: the feature lands on main with its report.
2. Constraints: the review gate, the ledger, hooks-test before the push.
3. Sources: all G (CLAUDE.md's stop-work procedure).
4. Holds as written.
5. Order: report, land.
6. Exits: (e) conform.
7. No search loop.
8. Budget: 15 minutes.
9. Done: the push lands; origin/main carries 409.
10. n/a.
11. n/a.
