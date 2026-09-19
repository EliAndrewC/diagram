# Tasks - 253 the old value is looked for before a later review round is spent on it

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling.

- [x] T01 `scripts/_stale_terms.py` and `tests/tooling/test_stale_terms.py`, the real feature-251 case included (FR-001, FR-004)
      research: rendering
      verify: DONE. scripts/_stale_terms.py + tests/tooling/test_stale_terms.py (6 passed): plain inputs, the task-line/verify-note split, an unnamed file kind searched by default, and the real feature-251 case (FR-007's Sonnet and FR-008's medium named, 3 candidates, all in spec.md)
- [x] T02 the guard branch in `_hm_review_round.py` and suite section 10 (FR-002)
      research: rendering
      verify: DONE. the guard branch in _hm_review_round.py refuses before any snapshot or round state moves; suite section 10 green in test-review-round-hooks.sh (59 passed): refusal names file:line, subject and old value; a bare STALE_TERMS_OK refused; with a reason the round is rewritten, routed and recorded
- [x] T03 `make stale-terms`; `research.md` R2's count; the docs rows and the make-targets page (FR-003, FR-004)
      research: rendering
      verify: DONE. make stale-terms F= [AGAINST=]; research.md R2 lists all thirteen amendment-round findings of feature 251 - 2 CAUGHT, 11 NOT, no round saved; root CLAUDE.md row, docs/guards.md, docs/spec-kit-and-reviews.md and docs/make-targets.html updated; the escape census classifies STALE_TERMS_OK
- [x] T04 `make hooks-test` and `make quick` green; land DIRECT
      research: rendering
      verify: DONE. make hooks-test green (3 suites run) and make quick clean on 2026-09-19; nothing under l7r/ or pool/ changed
