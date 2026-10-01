# Tasks - feature 293, the effort-level experiment (a pilot)

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md), [`research.md`](research.md) (R1-R8, D1-D6), [`data-model.md`](data-model.md),
[`contracts/cli.md`](contracts/cli.md), [`quickstart.md`](quickstart.md).

Written by the spec session (2026-09-29); every task below is the IMPLEMENTING session's. The order is strict: tooling (Phase 1) lands before
the freeze (Phase 3), the freeze before the first run, the runs one at a time.

## Phase 1 - tooling (lands on the DIRECT route; no engine code)

- [x] T01 [US2] `scripts/page-session.sh`, `_page_session_runner.py`, the Makefile's `page-session`: `EFFORT=` and `AGENTS=` passed through as `--effort` and `--agents` on every session; unset, the command line unchanged (contracts/cli.md; FR-003, FR-005)
      research: rendering
      verify: DONE. page-session.sh EFFORT and AGENTS: test_page_session.py 18 passing, the two new cases red before
- [x] T02 [US2] `scripts/_effort_run.py` + `make effort-run`: the refusals (a live run, memory over the headroom threshold or a fresh memwatch warning (R5 D7), rubrics changed since the freeze, prompt hash differs, `--agents` hash differs), the fresh clone at `COMMIT`, the per-run sources copy (`L7R_SOURCES_HOME`, R6 D4), `CLAUDE_CODE_EFFORT_LEVEL` removed (R1 D1), the detached start for R (via the runner) and I (one full session), the claims release after an R run (R6 D5), the run record with `shared_state` (R6 D6) (FR-001, FR-003, FR-004, FR-005)
      research: rendering
      verify: DONE. _effort_run.py + effort-init/effort-run: test_effort_run.py 12 passing - every refusal, --effort only, the pinned --agents, neutral brief path, the shared-cgroup gate
- [x] T03 [US1] `scripts/_effort_measure.py` + `make effort-measure`: tokens folded per message id by `_agent_census`'s fold (R3), main vs subagents, the `result.json` cross-check, wall-clock minus pauses, tool calls, dispatches, the ad-hoc dispatch list and count (R1 D3), every rework signal of R4 with its matched lines, the void rule (R5) (FR-006, FR-007)
      research: rendering
      verify: DONE. _effort_measure.py + effort-measure: test_effort_measure.py 6 passing on fixtures - four token fields agreeing with the census fold, per-message effort, every R4 signal, void and claim release
- [x] T04 [US3] `scripts/_effort_blind.py` + `make effort-blind`: the export per task, the stripping (run id, clone path, session names, trailers, arm names), A/B from the seed, the bundle and `MANIFEST.md` outside the repository, the key under `.git/effort-keys/` (FR-009)
      research: rendering
      verify: DONE. _effort_blind.py + effort-blind: test_effort_blind.py 5 passing - planted run id, clone path, session id, trailer and five effort-setting forms gone; the key outside the bundle
- [x] T05 [US3] `.claude/agents/effort-grader.md` (opus, `effort: high`, `omitClaudeMd: true`, Read and Grep) with the contract of contracts/cli.md; its row in `test_agent_models.py` (FR-010)
      research: rendering
      verify: DONE. .claude/agents/effort-grader.md opus/high omitClaudeMd; test_agent_models.py red before its TIERS row, 8 passing after
- [x] T06 Gate and land the tooling: `make done`, then `scripts/sync-with-main.sh done`
      research: rendering
      verify: DONE. make done green (205 s, 2026-09-29) on the tooling; the push waits for the feature's end (a feature with open tasks lands only its claim), so the runs clone from this clone

## Phase 2 - pre-flight (P0)

- [x] T07 [US2] The R1 measurements in a scratch clone: (a) a `--agents` agent with `effort` dispatched from `claude -p` - dispatchable, and what its transcript and `meta.json` record; (b) whether any transcript records effort; (c) whether the Agent tool takes an `effort` input (recorded, not used). If (a) fails, land D2a's agent file (and its tier-table row) before `START`. Results into research.md R1
      research: rendering
      verify: DONE. P0 measured: --agents pins adhoc-judge at high under medium and xhigh sessions; transcripts carry effort per message (now measured); no per-dispatch effort - research R1 P0 (a)-(d)
- [x] T08 [US2] The R6 D5 check: does the page-session rules' reading of the claims file treat the release line as the end of a claim; if not, the per-run copy by env override, tested
      research: rendering
      verify: DONE. the claims question settled in R-write.md (lines for 293 not written by the run are not claims on its work); research R6 D5
- [x] T09 [US2] Record `START`; confirm both future-work entries open at `START` and no burial-ground way on main (R8); read the shared cgroup's working set through host-diag (R5 D7 revised - the gate's primary figure); re-measure the working-set-to-memwatch offset at a memwatch warning for the fallback (the event's figure beside a working-set reading in its minute; the larger of it and the recorded 0.9 GB is used), and record the working set on a quiet host (R5 D7: a quiet reading plus the offset above the threshold goes to the GM before any run); snapshot the sources ledger and cache and record its hash; draw `SEED` and derive the order (task 1's arms from the seed, task 2's the other way round); the first lines of `interventions.md`
      research: rendering
      verify: DONE. experiment.json: START 1044b0372, SEED 853050, order R xhigh/medium, I medium/xhigh; snapshot ledger sha 8b2c60bb; fallback offset 1.9 GB; shared working set 5.87 GB (gate can open); both entries open, 287 T46 open - interventions.md

## Phase 3 - the freeze (before the first run)

- [x] T10 [US3] `rubrics/research.md` and `rubrics/implementation.md` with the criteria FR-008 names, 0-4 anchored scales, weights, pass lines; committed, the commit recorded as the freeze
      research: rendering
      verify: DONE. rubrics committed in 1044b0372 (START), before any runs/*.json; hashes in experiment.json, the launcher refuses a changed file
- [x] T11 [US2] `prompts/R-write.md`, `prompts/R-check.md` (one question, the servants' quarters, in the project's brief shape; stop at the record, the Ubame sheet untouched), `prompts/I.md` (the burial-ground footpath, hamlets only, Inashiro the reference, baseline in a detached worktree, bookends, stop at a green `make done` without pushing); each naming no effort; the `adhoc-judge` routing sentence in all three; committed with the rubrics
      research: rendering
      verify: DONE. prompts committed in 1044b0372; no word of effort, medium or xhigh in any (plan review CLEAR); hashes in experiment.json

## Phase 4 - the runs (one at a time, each measured before the next)

Run ids as made (interventions.md): e1 void (the launcher leaked make's variables); T12 = e2 (R, xhigh), T13 = e3 (R, medium); e4 ran
task I's first pick, found its premise gone (280 M68) and is set aside; the GM replaced task I (2026-09-30), so T14 = e5 (I, medium) and
T15 = e6 (I, xhigh), both from the one start commit with task I's re-frozen prompt and rubric.

- [x] T12 [US2] Run 1 (`e1`): `make effort-run` in the drawn order, under the headroom check (R5 D7); nothing else of the experiment while it is live; on its completion notification `make effort-measure RUN=e1`
      research: rendering
      verify: DONE. run e2 (task R, xhigh; e1 void - the launcher leaked make's variables): runs/e2.json complete, measurements/e2.json, valid
- [x] T13 [US2] Run 2 (`e2`), as T12
      research: rendering
      verify: DONE. run e3 (task R, medium): runs/e3.json complete, measurements/e3.json, valid; no overlap with e2
- [x] T14 [US2] Run 3 (`e3`), as T12
      research: rendering
      verify: DONE. run e5 (task I, medium; e4 ran the replaced task, set aside): measurements/e5.json, valid; 3 stalls resumed, the waits pauses
- [x] T15 [US2] Run 4 (`e4`), as T12
      research: rendering
      verify: DONE. run e7 (task I, xhigh; e6 void - failed at launch): measurements/e7.json, valid; 5 stalls resumed; SC-006: no overlaps, every launch under the threshold, nothing beside a live run

## Phase 5 - grading and the report

- [x] T16 [US3] Blind and grade task R (amendment of 2026-09-30): `make effort-blind TASK=R`; two `effort-grader` runs on the bundle, each answering the GM's two questions (deficient? strongly better?); the GM's non-blind reading recorded (request.md); both runs recorded, THEN the key opened and committed
      research: rendering
      verify: DONE. two effort-grader runs (headless, the agent's contract and tier; the agent file lands with the feature): grades/R-effort-grader-1.json and -2.json committed before keys/R.json (A = e2)
- [x] T17 [US3] Task I's quality (amendment of 2026-09-30): no blind grading - the GM's ruling after reading both outputs is recorded (request.md) and carried into the report
      research: rendering
      verify: DONE. the GM's ruling after reading both implementation outputs, verbatim in request.md; report.md's implementation row gives it
- [x] T18 [US1] `report.md`: the per-task table, the differences, the tiers that ran and any control unmet, the interventions, the FR-011 outcome per task type with its arithmetic, whether to expand, the caveats; the recommended `.claude/settings.local.json` setting if a default changes; through `escalation-check` before it reaches the GM
      research: rendering
      verify: DONE. report.md: the per-task table (all four cost kinds, main vs subagents, API time, wall-clock with its caveat), the blind review with the graders' agreement and disagreement, the FR-011 outcome per task type with its arithmetic, the GM's rulings, the tiers measured, the controls, the caveats; filtered by escalation-check (4 kept, 5 cut, 4 merged); the setting: none to change (medium is the default)

## Phase 6 - landing the winners (spec US4)

- [x] T19 [US4] Land task R's winner if it meets its pass line: its fragment, notes, sources and glossary files onto main; its ledger lines appended to the real ledger; the Ubame sheet untouched; the future-work item closed (or left open with both runs' findings if neither passed)
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. e2's buildings/910 landed with its 4 sources and 3 glossary terms (its write and check sessions' research pass, source-reader, quote-check, record-format, source-applicability); the graders' two flaws fixed and re-checked clean; make record clean, 258 record tests green; ledger lines appended; the future-work item closed into closed.md, a narrower sheet check left open
- [ ] T20 [US4] Land `xhigh`'s implementation (e7, the GM's choice), ported onto current main: `make done` and the moved maps' `settlement-review`s there, the merge work recorded apart, defects found added to the report's later-defects section; the future-work item closed
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
