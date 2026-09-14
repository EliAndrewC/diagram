# Plan - 248 reviews one per map

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I / XVI**: spec-fidelity before code; this plan reviewed (MODE 4) before any tick. No map changes,
  so no settlement-review is owed and `_review_owed.py` will say so (no manifest moves).
- **VI**: `make hooks-test` (every guard suite in parallel) and `make quick` for the tooling tests; the
  gate is not re-keyed (no engine code); DIRECT route.
- **X**: `pair-hooks.sh` is at 503 lines and `test-pair-hooks.sh` at 335; the new branches are added as
  functions and both stay under 1,000. `_review_owed.py` gains one lifted function (the classification
  read) tested over plain text.
- **XVIII**: each guard change has its test companion, and `_hookdeps.py` derives the suite set; a new
  rule slug is driven by `tests/tooling/test_guard_firing_log.py` with a real payload.
- **XIII**: baseline is the last green `make hooks-test` in the run log; the guard corpus replay must
  stay at zero refusals.

## Design

- `scripts/_review_snapshot.py`: for each map, after copying, write `dispatch.md` in the map's snapshot
  directory from one template (the map, both directories, the missing files, the engine key passed in
  with `--key`, the standing instructions); print the file's path on the map's line. `make verify` and
  the pair guard's permit branch print "N agents, one per map, in this same message" with the N paths.
- `scripts/pair-hooks.sh`, Agent branch: `maps_named(prompt, all_pool_maps)` (a lifted function in
  `_review_prereq.py`, R5's rule, the names from `_review_owed.pool_map_names(root)` - every map folder
  of both trees) before the prerequisite check; two or more
  -> refuse, `guard_log pair blocked <atype> review-multi-map`, exit 2, no escape. One -> after the
  existing rules permit, `write_pairing` a `dispatched` map: `{map: {key, at}}`, `guard_log pair
  permitted <atype> review-dispatched`; when every owed map now has a dispatch at this key, compute the
  span and `guard_log pair permitted <atype> reviews-parallel|reviews-serialized`.
- `scripts/pair-hooks.sh`, stop branch: after `review_recorded` and before the half-open refusal, compute
  the missing set (owed minus recorded-at-key minus dispatched-at-key minus pending-agent-naming-it,
  the last by grepping the pending agent transcripts for the map); if `review_pending` holds and the
  missing set is empty -> quiet; if the missing set is non-empty -> refuse once per (key, sorted set)
  with `stop_missing_told`, rule `review-map-undispatched`, naming the maps and their `dispatch.md`.
- `scripts/_review_owed.py`: `rendering_only(tasks_text) -> int | None` (the task count when every task
  is `research: rendering`, else None; the task regex from `tests/test_task_research_boxes.py`, copied
  with a pointer - a test module cannot be imported by a guard); `active_features(root, base)` - the
  pointer's directory plus every `specs/*/` directory the delta against the base touches that has a
  `tasks.md`, ticked or not (the in-progress rule's derivation widened: at push no box is open); an empty
  set OWES; `pool_map_names(root)`; `changed_maps` returns no names with the reason
  `rendering-only feature(s) <dirs>: <n> task(s) all research: rendering, no settlement-review owed (feature 248)`
  when every derived feature is rendering-only. `--why` prints it; the `--maps` callers change nothing.
- `scripts/review-gate.sh`, section 2: per changed manifest, read its verdict record; PASS/NEEDS-WORK at
  the pushed tree's engine key (`make -s engine-key REF=worktree` from the skill, computed once) ->
  pass; else if `_review_owed.py --why` reports the rendering waiver -> pass (recorded `escaped`-class
  as `review-waived-rendering`); else if no record at all and the notes file is touched -> pass; else
  refuse naming which (stale key / NOT-REVIEWABLE / no record and no notes touch), rules
  `map-stale-verdict`, `map-not-reviewable`, `map-no-review`.
- Tests: `scripts/test-pair-hooks.sh` sections 10 to 12 (multi-map refused, one-map permitted and
  recorded, stop missing-map refused once and cleared, parallel/serialized entries via an injected
  clock `PAIR_NOW`, fixture-only); `tests/tooling/test_review_owed.py` cases for `rendering_only` and the
  pointer forms; `scripts/test-review-gate.sh` the three passes and three refusals with a stub engine
  key; `tests/tooling/test_guard_firing_log.py` rows for the new rules; `_hookdeps` unchanged (the
  suites already carry these scripts).
- Docs: `.claude/agents/settlement-review.md` "WHEN YOU ARE DISPATCHED AT ALL" gains the one-map rule and
  the prompt files; CLAUDE.md's pair row gains the four rules and the waiver; `dev/reviews.md` the
  doctrine; `docs/review-ledger.md` unchanged.
