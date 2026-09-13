# Feature 240 - tasks

Spec ACCEPTED 2026-09-13 at `spec-fidelity` round 4. Every task is classified `research: rendering` or
`research: physical`; NOTHING here is physical - this is tooling about review rounds, not how a place was
built, farmed or lived in. The figures it rests on are in `research.md` R1 and R2 and `measurements.json`.

## Phase 1 - the decisions, importable

- [x] T01 `gencache.is_current(gen)`: the key comparison without `load()`'s copy, and `load()` calls it
      (FR-005). Unit test on a stub entry: current, moved, absent.
      research: rendering
      verify: DONE. gencache.is_current: the key comparison load() makes, and nothing else; load() asks it first so there is one body. Test proves it answers current / moved / absent while a standing PNG load() would delete stays put and a JSON load() would restore stays absent. 0.18 s from the repo root
- [x] T02 `scripts/_review_prereq.py`: `unverified_findings` (FR-003: a verdict's findings with no
      `verifies` record and no `accepted` disposition), `stale_maps` (FR-005: key moved or snapshot missing
      a file), `fix_review_without_green_gate` (FR-004), `unresolved_figures` (FR-006: `_FIGURE` imported
      from `spec-lint.py`, backtick spans skipped, a record's value or a dated one-shot label resolves it),
      and a `check` CLI printing the refusal. `tests/tooling/test_review_prereq.py`, each decision both ways.
      research: rendering
      verify: DONE. scripts/_review_prereq.py: unverified_findings, has_findings, stale_maps, unresolved_figures (spec-lint's _FIGURE imported, backticks skipped, m: key or 239's dated one-shot label resolves), check and a CLI. tests/tooling/test_review_prereq.py 7/7, including SC-002 - feature 230's pass-13 dispatch with every figure removed is refused naming the finding. PROVEN TO FIRE: with the finding check deleted, 2 of 7 go red

## Phase 2 - the records

- [x] T03 The verdict record shape and `make review-accept MAP= FINDING= REASON=` writing an `accepted`
      disposition and its bypass-log entry (FR-001, FR-003); `make audit` lists the dispositions.
      research: rendering
      verify: DONE. the verdict record shape (FR-001) lives in _review_prereq's readers and the agent file (T06); make review-accept MAP= FINDING= REASON= writes the accepted disposition AND the bypass-log entry make audit lists, never one without the other (&&). Exercised end to end: a reasoned acceptance wrote both; a one-word reason refused and wrote neither. The acceptance must name a finding the verdict actually raised; re-accepting replaces. 8/8 module tests

## Phase 3 - the hooks

- [ ] T04 `pair-hooks.sh` Agent branch: `REVIEW_PREREQ_OK` escape, the module's refusals, and no
      `review_key` at dispatch; `review_recorded()` reads verdict records (FR-002 to FR-006).
      `scripts/test-pair-hooks.sh` cases for each refusal, the escape, and a NOT-REVIEWABLE verdict leaving
      the pair open - each proven to fire by deleting its branch once.
      research: rendering
- [ ] T05 `review-gate.sh`: refuse a changed map whose latest verdict is NOT-REVIEWABLE (FR-002); its suite.
      research: rendering

## Phase 4 - the agents

- [ ] T06 `settlement-review.md`: the FIRST STAGE (findings, records, sources, the paired gate before the
      first map, between maps and before the verdict) and the VERDICT RECORD as the last act; the canopy case
      as the worked example; the right to measure kept (FR-007, FR-008). A static test finds each.
      research: rendering
- [ ] T07 `perf_review.py explain --control / --unverified` and the Makefile's `CONTROL=` / `UNVERIFIED=`;
      `perf-audit.md` first stage (NOT-REVIEWABLE on a control naming no record; on UNVERIFIED, run the
      counterfactual itself first) (FR-010). Tests, feature 230's first explanation as the negative fixture.
      research: rendering

## Phase 5 - proof and landing

- [ ] T08 SC-002's fixture: feature 230's pass-13 dispatch with every figure removed is refused naming the
      pass-12 finding ids; SC-009 `make done` green and `make hooks-test` green; land.
      research: rendering
