# Tasks - feature 293, the effort-level experiment (a pilot)

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md), [`research.md`](research.md) (R1-R8, D1-D6), [`data-model.md`](data-model.md),
[`contracts/cli.md`](contracts/cli.md), [`quickstart.md`](quickstart.md).

Written by the spec session (2026-09-29); every task below is the IMPLEMENTING session's. The order is strict: tooling (Phase 1) lands before
the freeze (Phase 3), the freeze before the first run, the runs one at a time.

## Phase 1 - tooling (lands on the DIRECT route; no engine code)

- [ ] T01 [US2] `scripts/page-session.sh`, `_page_session_runner.py`, the Makefile's `page-session`: `EFFORT=` and `AGENTS=` passed through as `--effort` and `--agents` on every session; unset, the command line unchanged (contracts/cli.md; FR-003, FR-005)
      research: rendering
      verify: `make test-file` on `test_page_session.py` - new cases for both flags and for the unchanged default, red before the change
- [ ] T02 [US2] `scripts/_effort_run.py` + `make effort-run`: the refusals (a live run, memory over the headroom threshold or a fresh memwatch warning (R5 D7), rubrics changed since the freeze, prompt hash differs, `--agents` hash differs), the fresh clone at `COMMIT`, the per-run sources copy (`L7R_SOURCES_HOME`, R6 D4), `CLAUDE_CODE_EFFORT_LEVEL` removed (R1 D1), the detached start for R (via the runner) and I (one full session), the claims release after an R run (R6 D5), the run record with `shared_state` (R6 D6) (FR-001, FR-003, FR-004, FR-005)
      research: rendering
      verify: `make test-file` on `test_effort_run.py` against a throwaway repository and a fake `claude` on `PATH` that records its argv; every refusal and every argv field asserted
- [ ] T03 [US1] `scripts/_effort_measure.py` + `make effort-measure`: tokens folded per message id by `_agent_census`'s fold (R3), main vs subagents, the `result.json` cross-check, wall-clock minus pauses, tool calls, dispatches, the ad-hoc dispatch list and count (R1 D3), every rework signal of R4 with its matched lines, the void rule (R5) (FR-006, FR-007)
      research: rendering
      verify: `make test-file` on `test_effort_measure.py` over saved fixture transcripts (a multi-block message, a subagent, an ad-hoc opus dispatch, a guard firing, a failed `make quick`, a fix commit, an exit 137)
- [ ] T04 [US3] `scripts/_effort_blind.py` + `make effort-blind`: the export per task, the stripping (run id, clone path, session names, trailers, arm names), A/B from the seed, the bundle and `MANIFEST.md` outside the repository, the key under `.git/effort-keys/` (FR-009)
      research: rendering
      verify: `make test-file` on `test_effort_blind.py` - a planted arm name, run id and clone path in each export are gone; the key is not in the bundle
- [ ] T05 [US3] `.claude/agents/effort-grader.md` (opus, `effort: high`, `omitClaudeMd: true`, Read and Grep) with the contract of contracts/cli.md; its row in `test_agent_models.py` (FR-010)
      research: rendering
      verify: `make test-file` on `test_agent_models.py`, red before the row
- [ ] T06 Gate and land the tooling: `make done`, then `scripts/sync-with-main.sh done`
      research: rendering
      verify: `make done` green; the push's route DIRECT

## Phase 2 - pre-flight (P0)

- [ ] T07 [US2] The R1 measurements in a scratch clone: (a) a `--agents` agent with `effort` dispatched from `claude -p` - dispatchable, and what its transcript and `meta.json` record; (b) whether any transcript records effort; (c) whether the Agent tool takes an `effort` input (recorded, not used). If (a) fails, land D2a's agent file (and its tier-table row) before `START`. Results into research.md R1
      research: rendering
      verify: the transcripts' lines quoted in R1; D2 or D2a stated as the one in force
- [ ] T08 [US2] The R6 D5 check: does the page-session rules' reading of the claims file treat the release line as the end of a claim; if not, the per-run copy by env override, tested
      research: rendering
      verify: a scratch page session given a claimed-then-released question proceeds; or the override's test
- [ ] T09 [US2] Record `START`; confirm both future-work entries open at `START` and no burial-ground way on main (R8); snapshot the sources ledger and cache and record its hash; draw `SEED` and derive the order (task 1's arms from the seed, task 2's the other way round); the first lines of `interventions.md`
      research: rendering
      verify: `interventions.md` carries START, the snapshot hash, SEED and the four runs' order

## Phase 3 - the freeze (before the first run)

- [ ] T10 [US3] `rubrics/research.md` and `rubrics/implementation.md` with the criteria FR-008 names, 0-4 anchored scales, weights, pass lines; committed, the commit recorded as the freeze
      research: rendering
      verify: both files committed before any `runs/*.json` exists (`git log` order)
- [ ] T11 [US2] `prompts/R-write.md`, `prompts/R-check.md` (one question, the servants' quarters, in the project's brief shape; stop at the record, the Ubame sheet untouched), `prompts/I.md` (the burial-ground footpath, hamlets only, Inashiro the reference, baseline in a detached worktree, bookends, stop at a green `make done` without pushing); each naming no effort; the `adhoc-judge` routing sentence in all three; committed with the rubrics
      research: rendering
      verify: `grep -i -E 'medium|xhigh|effort'` over `prompts/` finds nothing; the hashes recorded

## Phase 4 - the runs (one at a time, each measured before the next)

- [ ] T12 [US2] Run 1 (`e1`): `make effort-run` in the drawn order, under the headroom check (R5 D7); nothing else of the experiment while it is live; on its completion notification `make effort-measure RUN=e1`
      research: rendering
      verify: `runs/e1.json` complete, `measurements/e1.json` written, status valid (or void and re-run as the next id, logged)
- [ ] T13 [US2] Run 2 (`e2`), as T12
      research: rendering
      verify: as T12; no overlap with e1
- [ ] T14 [US2] Run 3 (`e3`), as T12
      research: rendering
      verify: as T12
- [ ] T15 [US2] Run 4 (`e4`), as T12
      research: rendering
      verify: as T12; SC-006 (no overlaps, no counted void, every launch under the threshold, nothing of the experiment beside a live run)

## Phase 5 - grading and the report

- [ ] T16 [US3] Blind and grade task R: `make effort-blind TASK=R`; `effort-grader` on the bundle; the GM's grade on the same bundle; both recorded, THEN the key opened and committed
      research: rendering
      verify: `grades/R-effort-grader.json` and `grades/R-gm.json` committed before `keys/R.json`
- [ ] T17 [US3] Blind and grade task I, as T16, after T16's grading has ended (one grading at a time)
      research: rendering
      verify: as T16
- [ ] T18 [US1] `report.md`: the per-task table, the differences, the tiers that ran and any control unmet, the interventions, the FR-011 outcome per task type with its arithmetic, whether to expand, the caveats; the recommended `.claude/settings.local.json` setting if a default changes; through `escalation-check` before it reaches the GM
      research: rendering
      verify: every number in the table traced to a `measurements/` or `grades/` file; the escalation-check verdict applied

## Phase 6 - landing the winners (spec US4)

- [ ] T19 [US4] Land task R's winner if it meets its pass line: its fragment, notes, sources and glossary files onto main; its ledger lines appended to the real ledger; the Ubame sheet untouched; the future-work item closed (or left open with both runs' findings if neither passed)
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
      verify: the run's own check verdicts re-read for the landed entry; `make record` clean; `entry-drift` on any modal the entry feeds
- [ ] T20 [US4] Land task I's winner if it meets its pass line: merged onto current main (287's changes included), `make done` and the moved maps' `settlement-review`s there, the merge work recorded apart, defects found added to the report's later-defects section; the future-work item closed
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
      verify: `make done` green post-merge; each moved map's review a row in `docs/review-ledger.md`
- [ ] T21 Delete the losing (and void) run clones unmerged; retire D2a's agent file if it landed; the report's final lines updated
      research: rendering
      verify: `ls /diagram/.clones | grep diagram-exp-` empty; report final
