# Tasks - 231 Review only when the layout moved

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. Round 1 CHANGES REQUIRED (FR-002 read as loosening feature 151's neither-half-alone rule; rewritten to preserve it) and its aside taken (FR-005: the snapshot on every gate shape); round 2 FAITHFUL
- [x] T02 `scripts/review-owed.py` + `tests/tooling/test_review_owed.py` (FR-001)
      research: rendering
      verify: DONE. scripts/_review_owed.py (the merge base with origin/main, both pool trees, committed + staged + unstaged + untracked); tests/tooling/test_review_owed.py, 18 cases on real git fixtures - a manifest moved two commits back (the case the old HEAD~1 diff missed), a render or notes file alone owing nothing, feature 228's own shape (engine code, no manifest) owing nothing, no origin/main, a repository with no commits
- [x] T03 `pair-hooks.sh`: the clone resolved, the check at each decision point, the escaped review
      recorded; the suite's new cases (FR-002/003/004/008)
      research: rendering
      verify: DONE. pair-hooks.sh resolves the session's clone through clone-sync-hooks.sh resolve (cwd only as fallback), asks the script at the gate branch and again at stop, records the automatic waiver with its reason, and an escaped review now records review_key; test-pair-hooks.sh 42 passed (sections 6-8 are the new behaviors: the gate untouched and the context valid JSON, the stop branch quiet with the waiver recorded, a MOVED manifest owing the review again, the mirror-standing payload recording the clone's state and never the mirror's, the escaped review closing the pairing)
- [x] T04 `scripts/review-snapshot.py` and `make verify` (FR-005), with its unit test
      research: rendering
      verify: DONE. scripts/_review_snapshot.py + the verify recipe + the pair guard's permit path; the snapshot lands in <clone>/.git/review-snapshot/<map>/{clone,main}/ with a missing render NAMED (`make map` in the line); covered by test_review_owed.py's snapshot half (both sides, the missing render, a map in neither tree, the previous snapshot cleared, the mirror derived from the clone path)
- [x] T05 `tools/page_lit.py`, `tools/picture_diff.py`, their targets, index rows and tests (FR-006)
      research: rendering
      verify: DONE. tools/page_lit.py + tools/picture_diff.py, `make page-lit` / `make picture-diff`, rows in tools/CLAUDE.md; 310 passed across tests/tools plus 3 browser cases on the synthetic page. Two defects the real page found and the tests now hold: a fixed wall-clock wait is not a paint (the same instrument read 100% and 0% on one page - two animation frames instead), the pointer starts ON the map so the before-shot arrived with a class already lit, and the id map is the VIEWBOX rather than the map (feature 200 crops it; every sample landed outside and every class read zero). picture_diff attributes through the PAGE's own id map - a map's .svg carries no class groups at all, which the first Kuwabata run reported as 100% off-class
- [x] T06 the doctrine: the agent file, reviews.md, CLAUDE.md, efficiency-tooling.md (FR-007)
      research: rendering
      verify: DONE. the settlement-review agent file (WHEN it is dispatched at all, the snapshot in its inputs, the two tools in place of a scratch script), dev/reviews.md (FIRST: is one owed), the root CLAUDE.md pair row and docs/efficiency-tooling.md; the derived make-targets page regenerated (61 targets, 0 undocumented). Also corrected in passing (Principle XIV): tools/CLAUDE.md still said the measured coverage surface was a module-by-module roster and that a new tool should not owe the floor - the GM reversed that on 2026-09-02 and feature 174 removed the roster
- [x] T07 SC-001..SC-004 replayed on feature 228's delta and recorded; `make hooks-test` and the gate
      green; land GATED
      research: rendering
      verify: DONE. SC-001: feature 228's shape replayed in the guard suite - with no manifest moved the gate runs as typed, is not rewritten, carries the NO SETTLEMENT-REVIEW OWED context and the stop branch is quiet with the waiver recorded (42 passed). SC-002: a moved manifest owes the review again, in the same suite. SC-003: a payload standing in the mirror records the clone's pairing state and never the mirror's. SC-004 measured on the real Kuwabata: `make page-lit CLASS="mulberry dike"` reports the dike 99.7% lit, the fish pond 3.1%, the fry pond 5.3%, the vegetable ground, lanes, windbreak and scrub 0.0%; `make picture-diff` of the pre-228 geometry against the shipped one reports 0.088% of pixels differing, max delta 10/255, and 100% of it on the fish pond, the mulberry dike, the pond sluice and the fry pond - nothing off those classes. SC-005: `make hooks-test` green (3 suites, 18 unchanged) and `make done` green (the first two runs failed on the operations registry and on page_lit's two driving branches - both fixed and committed). Landing GATED (LOCAL-GATED).
