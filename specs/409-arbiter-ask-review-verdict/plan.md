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
an accept stands as the <r> review's verdict)"; the output says the same. With no review, a SUBJECT matching
`^\d+-(spec|plan)-` prints a hint to pass `REVIEW=` and records nothing. `make arbiter-ask` passes `$(REVIEW)`; its `##` line
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
accept on the unchanged spec and not after an edit. Each proved to fail with its change removed.

## T - the order

1. D1-D3 in one change, the tests run. 2. Report and land (`make land`, the direct route).
