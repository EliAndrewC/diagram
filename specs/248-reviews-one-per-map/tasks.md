# Tasks - 248 Reviews one per map

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: procedure` - tooling, nothing on a
map.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: procedure
      verify: DONE. spec-fidelity: rounds 1 and 2 CHANGES REQUIRED (all taken), round 3 FAITHFUL; two amendments after acceptance each verified (rounds 4 and 6 FAITHFUL, round 5 two stale sentences fixed); plan MODE 4 CLEAR twice (16 decisions, none narrowing), plan-review.json on the current sha; rounds 3 onward and both plan reviews ran on this session's model after the Opus weekly limit, disclosed in the Status line
- [x] T02 the per-map prompt files (FR-002): `_review_snapshot.py` writes `dispatch.md`; `make verify` and
      the pair guard's permit branch print N files and the one-per-map instruction
      research: procedure
      verify: DONE. _review_snapshot.py writes <map>/dispatch.md per map (--key) and names it on the map's line; make verify prints N and 'ONE PER MAP, in this same message' with the files; the permit branch's snapshot carries the key; test_review_owed.py proves the file's contents
- [x] T03 the multi-map refusal and the dispatch record (FR-001, FR-004): `maps_named`, the refusal with no
      escape, the `dispatched` record, the parallel/serialized entry; suite sections
      research: procedure
      verify: DONE. pair-hooks.sh: maps_named (via _review_prereq.py named, against every pool map, snapshot dirs first) refuses two or more before the agent starts (rule review-multi-map, no escape, the prompt files named); a permitted one-map dispatch is recorded on both permitting paths (review-dispatched) and the last owed map's dispatch records reviews-parallel or reviews-serialized over PARALLEL_SPAN_S; test-pair-hooks.sh section 10: 93 passed
- [x] T04 the stop rule (FR-003): the missing set, refused once, cleared by a dispatch, a verdict or a
      waiver; suite sections
      research: procedure
      verify: DONE. pair-hooks.sh stop: the missing set (owed minus verdict-at-key, dispatch-at-key, running-review-naming-it) refused once per (key, set) after every waiver, naming the maps and prompt files (review-map-undispatched); the any-review-pending short-circuit retired; section 11: refused once, cleared by a dispatch, by a running review naming the map, quiet on a waived gate
- [x] T05 the rendering waiver (FR-005): `rendering_only`, `active_features` (the DERIVED set - the pointer's
      feature plus every feature directory with a `tasks.md` the delta touches, ticked or not - waived
      only when all are rendering), the
      reason; `test_review_owed.py`;
      SC-003 measured on this clone against feature 247's and 230's task files
      research: procedure
      verify: DONE. _review_owed.py: rendering_only, active_features (the pointer plus every touched feature directory with a tasks.md, ticked or not), pool_map_names, waiver, owed; --why prints the reason; test_review_owed.py 7 new cases including the derived pair both ways and the empty set; SC-003 on this clone: rendering_only(specs/247) = 5 tasks, rendering_only(specs/230) = None, the moved-manifest state proved by the fixture since 247 has landed
- [x] T06 the review gate on the verdict record (FR-006): the three passes and three refusals;
      `test-review-gate.sh`; SC-004 measured on feature 247's landed records
      research: procedure
      verify: DONE. review-gate.sh section 2: a PASS/NEEDS-WORK record at the pushed tree's engine key ships with no notes touch; the rendering waiver ships; no record at all still ships on the notes touch; NOT-REVIEWABLE, a stale-key record (notes touched or not) and no-record-no-notes refuse, each under its own rule; test-review-gate.sh 25 passed with six new cases; SC-004 on this clone: feature 247's four PASS records carry d9d78cdcd834, the worktree key
- [ ] T07 the record (FR-007) and the proof (FR-008): the contract, CLAUDE.md, `dev/reviews.md`; the
      firing-log rows; `make hooks-test` and `make quick` green; land DIRECT
      research: procedure
