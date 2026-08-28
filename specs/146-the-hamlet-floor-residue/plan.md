# Implementation Plan: the hamlet floor's residue

**Feature**: 146 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 2) | **Date**: 2026-08-28

## Constitution Check

- VI: `make done` and `make done FULL=1` at the end; a moved map gets a `settlement-review` before it ships.
  No map is expected to move - this feature writes tests, it does not change what is drawn - so a moved map
  is a FINDING, and the review is the proof rather than a formality.
- X: the feature EXISTS to satisfy the 100% rule on the hamlet path; nothing is exempted to get there
  (FR-001), and the anti-cheat list is the spec's.
- XII: every task is `research: rendering` unless a check's rule turns out to rest on a physical question,
  which would make that task `physical` with its three boxes.
- XIII: the baseline is 145's landing (373 lines, `floor-at-145.txt`); the pre-existing global-floor misses
  stay ledgered and are NOT fixed here.
- XVI: the spec was reviewed against the GM's words, two rounds, before any code.

## Technical approach

1. **Class 2 (176 lines), the largest and the one with real content.** For each hamlet-entered check with an
   uncovered failure branch: name the smallest legal break of a scripted roll that trips it, add the case to
   `tests/gate/test_scripted_fixtures.py` (`_fires(spec, check, mutate)`), confirm the branch is covered.
   Work it file by file, biggest first (`segments_04c` 24, `common_02` 23, `segments_03a` 18, `segments_06c` 14,
   `segments_01a` 13, `segments_03c` 12, `common_03` 11, then the tail), so each commit is one theme.
2. **Class 3 (141 lines).** One unit test per refusal reason, in the mirrored test file, the shape 145 used.
   `hamletgen/ways.py` (37) is the hard part: several are fallbacks inside long stage functions
   (`_thread_the_fabric`, `_smooth_web`), where the test has to build the geometry that forces the fallback -
   and where "this is unreachable" is a real possible answer, disposed of under FR-001 with its reason.
3. **Class 1 (56 lines).** Check the state of the peer's feature 139 (Kuwabata as `mulberry_dike_fishpond`)
   when the task is reached. If a scripted map rolls the archetype, the check is exercised by that roll and
   the task is the fixture; if not, the fallback is a scripted roll pinned to the archetype in the test itself.
   **The spec reviewer flagged this as the one place the feature could quietly grow** - so the task records
   the decision and its cost before the work, and the fallback is the test-side pin, never a new pool map.
4. **Close**: re-measure, `make done`, `make done FULL=1`, research R3, land without an acceptance task.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| a check's failure branch is proved by a SCRIPTED break, never a frozen hand-built manifest | rendering (feature 141's ruling, applied) | spec FR-002, `tests/gate/test_scripted_fixtures.py` |
| an untrippable check is disposed of inside this feature, not escalated | rendering (the GM removed the acceptance gate) | spec FR-003 |
| the global floor's pre-existing misses stay ledgered | rendering (constitution XIII) | spec FR-006, 145 research R3d |
