# Implementation Plan: an arbiter's ruling on an asked review stands as that review's verdict (feature 409)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-22

## Summary

An `ask:` trigger gains the review it is about (spec or plan), named by `REVIEW=`. Its ruling row carries that review (and, for a spec, the spec digest), so `spec_ruled`
honors it as it honors a spec round's ruling, and a plan ruling runs `plan_gate.arbiter_accept` as a plan round's does.
Tooling only; no engine code.

## Technical Context

- `scripts/hooks/lib/hm_arbiter.py`: `trip` (the owed entry), the `ask` command, `record_ruling` (the row), the `ruled`
  command (runs `arbiter_accept` for a plan round), `spec_ruled`.
- `scripts/gates/plan_gate.py`: `arbiter_accept` refuses any trigger but `round:spec-fidelity|plan:`.
- `Makefile` `arbiter-ask`: passes SUBJECT and WHY.
- Tests: `tests/hooks/test_hm_arbiter.py`, `tests/tooling/test_plan_arbiter_accept.py`.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the task is `research: rendering` (tooling). XIII: the two test files and `make hooks-test` stay green.
  XVI: built as the spec's FRs.

## D1 - the ask names its review (FR-001)

`hm_arbiter.py ask <subject> <why> [spec|plan]`; a third value is refused. The review is stored as `review` on the owed entry
(`trip` takes it as an optional keyword) and the ask's detail - the question the arbiter's bundle shows - ends "(REVIEW=<r>:
an accept stands as the <r> review's verdict)"; the output says the same. An ask with no review is recorded as
today, with no review; where its SUBJECT matches `^\d+-(spec|plan)-` the output adds a hint to pass `REVIEW=`. `make arbiter-ask` passes `$(REVIEW)`; its `##` line
names `[REVIEW=spec|plan]`.

## D2 - the ruling carries it (FR-002, FR-003, FR-004)

`record_ruling`: `review = trig.get("review")` on an `ask:` trigger goes on the row; for `spec`, `spec_sha` as for a spec
round. `spec_ruled` honors a row whose trigger starts `round:spec-fidelity|<feature>#` OR whose `review` is `spec`, with
the ruling and digest tests unchanged. The `ruled` command runs `arbiter_accept` when the trigger is a plan round OR the
row's `review` is `plan`; `arbiter_accept` takes a trigger whose `arbiter.jsonl` row has `review: plan` (its accept test
unchanged), and refuses any other non-plan trigger as today.

## D3 - tests (FR-005)

In `test_plan_arbiter_accept.py`: an asked plan review ruled `accept` through `ha.main(["ask", ...])` then
`ha.main(["ruled", ...])` leaves `pg.owed(d)` None; a `continue` leaves it owed; an ask with no review records none, even named `408-plan-round3`. In
`test_hm_arbiter.py`: a bad REVIEW is refused; `spec_ruled` honors an asked spec
accept on the unchanged spec and not after an edit. The ask's output and its stored detail name the review (and the hint shows only on a review-like SUBJECT with none);
`make -n arbiter-ask ... REVIEW=plan` passes `plan` to the `ask` command. Each proved to fail with its change removed.

## T - the order

1. D1-D3 in one change, the tests run. 2. Report and land (`make land`, the direct route).

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
