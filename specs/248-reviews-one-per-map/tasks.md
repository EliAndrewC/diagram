# Tasks - 248 Reviews one per map

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: procedure` - tooling, nothing on a
map.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: procedure
- [ ] T02 the per-map prompt files (FR-002): `_review_snapshot.py` writes `dispatch.md`; `make verify` and
      the pair guard's permit branch print N files and the one-per-map instruction
      research: procedure
- [ ] T03 the multi-map refusal and the dispatch record (FR-001, FR-004): `maps_named`, the refusal with no
      escape, the `dispatched` record, the parallel/serialized entry; suite sections
      research: procedure
- [ ] T04 the stop rule (FR-003): the missing set, refused once, cleared by a dispatch, a verdict or a
      waiver; suite sections
      research: procedure
- [ ] T05 the rendering waiver (FR-005): `rendering_only`, `active_features` (the DERIVED set - the pointer's
      feature plus every open-task feature the delta touches - waived only when all are rendering), the
      reason; `test_review_owed.py`;
      SC-003 measured on this clone against feature 247's and 230's task files
      research: procedure
- [ ] T06 the review gate on the verdict record (FR-006): the three passes and three refusals;
      `test-review-gate.sh`; SC-004 measured on feature 247's landed records
      research: procedure
- [ ] T07 the record (FR-007) and the proof (FR-008): the contract, CLAUDE.md, `dev/reviews.md`; the
      firing-log rows; `make hooks-test` and `make quick` green; land DIRECT
      research: procedure
