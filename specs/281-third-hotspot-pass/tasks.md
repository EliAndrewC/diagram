# Tasks - feature 281, the third hotspot pass

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A1-A8, B1-B2, C). Research: [`research.md`](research.md).
Order: the exact pieces first, each proved on its equality test; the pool regenerated and compared byte for byte against
`c13a6ebe6` with all of them landed; then the two moving pieces under 276's FR-006 condition; then the measurement and
the record.

## Setup

- [ ] T01 The base: `measure.py before` in the clone at `c13a6ebe6` (`measurements.json` before-keys), the `281-start` bookend in `/tmp/base281`, the harness's entry-bucket instrument (plan C), and the committed pool confirmed to regenerate byte-identically in the base worktree
      research: rendering

## US2 - the ways, the board and the captions ask indexes (P1)

- [ ] T02 [US2] The clip through the fabric index in `hamletgen/ways/clearance.py`, with its equality test (A1)
      research: rendering
- [ ] T03 [P] [US2] The toll's grid sized to the band in `hamletgen/ways/route.py`, with its equality test (A3)
      research: rendering
- [ ] T04 [P] [US2] The notice board's indexes - `outermost_join` and `RouteReach` - in `settlement/structures/fixtures/_helpers.py`, `siting.py` and `hamletgen/frame.py`, with their equality tests (A4)
      research: rendering
- [ ] T05 [P] [US2] The watercourse indexes in `hamletgen/ways/sweeps.py` (`_link_home_bank`) and `settlement/rolling/fit.py` (`_rect_on_stream`), with their equality tests (A5)
      research: rendering
- [ ] T06 [P] [US2] The caption probe's lane index in `settlement/structures/captions.py` and its two many-seat callers, with its equality test (A6)
      research: rendering

## US3 - what was computed once is not computed again (P1)

- [ ] T07 [US3] Ring indexes shared by content in `hamletgen/clearance.py`, with the build-once and mutated-ring tests (A2)
      research: rendering
- [ ] T08 [P] [US3] The carve's vertex memo in `waterfields/carve.py`, with its equality test (A7)
      research: rendering

## US4 - the windbreak stops re-asking (P2)

- [ ] T09 [US4] The windbreak gap fill's memory in `settlement/homestead_parts/stands.py` and `grove_blocks.py`, with its equality test (A8)
      research: rendering
- [ ] T10 [US1] The pool regenerated with A1-A8 landed and B not yet: every live pool manifest byte-identical against `c13a6ebe6` (SC-011, first half)
      research: rendering

## US3 / US4 - the moving pieces

- [ ] T11 [US3] The shared plot edge walked once in `waterfields/carve.py`, with its symmetry and verdict tests and the Decisions note at the point of change (B1)
      research: rendering
- [ ] T12 [US4] The vectorized marsh in `settlement/land/wet.py`, with its compliance and density tests and the Decisions note at the point of change (B2)
      research: rendering
- [ ] T13 [US1] The pool regenerated under 276's FR-006 condition: `make done` green, the rescue-rounds scenario and the toys, forms and kinds, the moved maps' research entries, `make cohort N=24` against the base's (SC-011, second half)
      research: rendering

## Polish

- [ ] T14 `measure.py after` back to back; SC-001 to SC-010 checked on the entry buckets (plan C), base-rerun over after, each bucket's total beside its named count; `make perf LABEL=281-end` and `make perf-report AGAINST=281-start`
      research: rendering
- [ ] T15 `dev/performance.md`: the third pass's section and its residue table, levers priced (FR-011, SC-012)
      research: rendering
