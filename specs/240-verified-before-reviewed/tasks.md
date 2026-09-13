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

- [x] T04 `pair-hooks.sh` Agent branch: `REVIEW_PREREQ_OK` escape, the module's refusals, and no
      `review_key` at dispatch; `review_recorded()` reads verdict records (FR-002 to FR-006).
      `scripts/test-pair-hooks.sh` cases for each refusal, the escape, and a NOT-REVIEWABLE verdict leaving
      the pair open - each proven to fire by deleting its branch once.
      research: rendering
      verify: DONE. DONE. pair-hooks.sh Agent branch: settlement-review asks _review_prereq.py check (gate green from gate-stamp.py --fresh diagram, prompt text from the payload), REVIEW_PREREQ_OK="<why>" escape refused bare and logged with a reason, review_dispatch_key written at dispatch instead of review_key, review_recorded() reads verdict records via _review_prereq.py recorded. test-pair-hooks.sh 70/70 (section 8 updated: an escaped review counts once its verdict is written; 8b new: FR-003 naming the finding, verified by a record, accepted; FR-004; FR-005 key moved and artifact missing; FR-006 and 239's one-shot label; the escape; NOT-REVIEWABLE and a PASS for other content leave the pair open, a PASS for this content closes it). Each proven to fire by mutation in a scratch copy: refusal deleted 5 red, recorded-always 17, reason unchecked 1, FR-003/004/005/006 deleted 1/1/2/1, NOT-REVIEWABLE counted 1.
- [x] T05 `review-gate.sh`: refuse a changed map whose latest verdict is NOT-REVIEWABLE (FR-002); its suite.
      research: rendering
      verify: DONE. DONE. review-gate.sh reads <git-dir>/review-verdicts/<map>.json for each changed manifest whose notes were touched, and refuses one whose latest verdict is NOT-REVIEWABLE; no record keeps the notes rule. test-review-gate.sh 19/19, the new pair of cases (NOT-REVIEWABLE blocked with notes updated, PASS ok) proven to fire: with the verdict comparison broken the blocked case goes red.

## Phase 4 - the agents

- [x] T06 `settlement-review.md`: the FIRST STAGE (findings, records, sources, the paired gate before the
      first map, between maps and before the verdict) and the VERDICT RECORD as the last act; the canopy case
      as the worked example; the right to measure kept (FR-007, FR-008). A static test finds each.
      research: rendering
      verify: DONE. DONE. settlement-review.md: FIRST STAGE before Inputs (make review-paired-gate before the first map, before each further map and immediately before the verdict; red is NOT-REVIEWABLE; last findings against measurements.json verifies/subject and review-dispositions; the record's source judged, canopy clumps vs tree_crowns as the worked example; the right to measure independently kept) and the VERDICT RECORD as the last act (make review-verdict, which copies review_dispatch_key and re-reads the gate itself, so red records NOT-REVIEWABLE whatever the agent passes). tests/test_settlement_review_contract.py finds each; with two phrases removed it went 2 red. Module: gate_state, write_verdict, 3 new tests (14 total).
- [x] T07 `perf_review.py explain --control / --unverified` and the Makefile's `CONTROL=` / `UNVERIFIED=`;
      `perf-audit.md` first stage (NOT-REVIEWABLE on a control naming no record; on UNVERIFIED, run the
      counterfactual itself first) (FR-010). Tests, feature 230's first explanation as the negative fixture.
      research: rendering
      verify: DONE. DONE. perf_review explain takes --control <key> (must name a specs/*/measurements.json record, carried on the explanation as control_record) or --unverified <reason> (two words, eight chars), exactly one; the Makefile passes CONTROL= / UNVERIFIED= and logs UNVERIFIED to dev/bypass-log only after a recorded explanation. perf-audit.md FIRST STAGE: NOT-REVIEWABLE on a control naming no record; on unverified, run the counterfactual itself first. Feature 230's first explanation is the negative fixture. test_perf_review 29/29 (3 new, proven to fire: with both refusals removed all 3 red); agent contract test finds the first stage.

## Phase 5 - proof and landing

- [ ] T08 SC-002's fixture: feature 230's pass-13 dispatch with every figure removed is refused naming the
      pass-12 finding ids; SC-009 `make done` green and `make hooks-test` green; land.
      research: rendering
