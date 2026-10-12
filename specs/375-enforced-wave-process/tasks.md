# Tasks - feature 375, an efficient process enforced and measured by the tooling

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.
`tasks.md` holds the current batch only (plan D18); the batches are listed in the plan.

## Occasions

- none: no map, sheet, glyph or placement changes

## Batch 1 - measurement and the two fixes

- [x] T01 The event log (plan D7, D9): `scripts/hooks/event-log-hooks.sh` + `scripts/measure/event_log.py` (the line, the category, the feature), wired in `.claude/settings.json` on PreToolUse, PostToolUse, SubagentStart, SubagentStop, UserPromptSubmit and Stop; its suite `tests/hooks/test-event-log-hooks.sh`; the per-call cost measured (`m:event-hook-cost`) (FR-008)
      research: rendering
      verify: DONE. DONE. event-log-hooks.sh + event_log.py, wired on six events in settings.json; test-event-log-hooks.sh 18/18; 59 ms a call (m:event-hook-cost), inside the existing guards' range; make targets read only in command position (a heredoc mention misread in 375's first report, fixed and tested)
- [x] T02 The transcript converter (plan D8): `event_log.py from-transcript` turns a Claude Code session transcript into the same events, Edit digests included; tested on a fixture transcript (FR-008, FR-009)
      research: rendering
      verify: DONE. DONE. from-transcript: tool_use/result, async launch, queue enqueue as SubagentStop with its verdict, typed prompts, end_turn; test_event_log.py fixture; 372's 170 MB transcript converts in ~3 s
- [x] T03 `make feature-report F=NNN [TRANSCRIPT=]` (plan D8): `scripts/measure/feature_report.py` writes `specs/NNN/report.md` from the events, `dev/run-log/`, the ledger, plan reviews and git; SC-005 on 372 (the spec's Why table reproduced, under ten seconds) and on a one-task feature (FR-009, SC-005)
      research: rendering
      verify: DONE. DONE. make feature-report (time split, other-tool by target, dispatches by verdict, rounds, gates, BLOCKs, reversals, cascade ratio over hand-written lines); SC-005: 372 in 2.3-3.3 s with its Why rows reproduced to within one round or count (m:sc005-372), 0.42 s on 182 (m:sc005-one-task)
- [x] T04 The claims triage (plan D5): the parser pinned to lines opening `TOUCHES `; the located defect fixed - a snapshot's page text kept as a blob so a withdrawn, never-committed block is shown rather than forcing every claim, and the named and forced counts reported apart (FR-005, part a)
      research: rendering
      verify: DONE. DONE. the parser was already anchored (pinned by a test); the located defect - a withdrawn never-committed block forcing every claim - fixed by keep_texts/kept_text (blob per snapshot); the test red with the fix removed, green with it; named and forced counts reported apart
- [x] T05 A plan verdict survives a typo (plan D6): `plan-review.json` keeps the reviewed text; `plan_gate.judge` admits a typo-scale diff and voids any other; tests for each side, the 372 typo among them (FR-005, part b)
      research: rendering
      verify: DONE. DONE. plan_text kept in plan-review.json; typo_only admits whitespace, case, punctuation and near spellings, voids numbers, number words, negations, quantifiers, added words; 8 cases + rules test; the verdict survived this plan's own re-wrap
- [x] T07 Staying open between batches (plan D18): a `[lands-open]` task mark exempt from the open-task refusal in `sync-with-main.sh` and read as open by `make speckit-todo`; `**Waits on**: NNN` refused by `make tick` while NNN is open; tests that an ordinary open box still refuses the push and that a waiting feature's tick refuses
      research: rendering
      verify: DONE. DONE. speckit-todo --holding (the trailing mark honored on the GM box with a row, or a CLEAR plan's Lands open line; a mention is no mark); the push names holding boxes; tick refuses Waits on an open feature and a hand-typed mark; sync suite incl. a hand-typed mark refused; test_lands_open.py incl. the fresh-interpreter load and the mention case (both found by this batch's own first tick)
- [x] T06 Batch 1 closes: `make done` green; `make hooks-test`; 375's report so far written from this session's transcript; landed
      research: rendering
      verify: DONE. DONE. make done green (476 s, run-log 20261010T170058); hooks-test inside it; 375's report written from this session's transcript (report.md); landed by the push that carries this tick
## Batch 2 - the owing logic

- [x] T08 The pop-up triage (plan D1): a modal unit owed only because a page its `Drawing:` or `Entry:` names moved owes a TRIAGE; `make modal-triage` shows each moved page's blocks new, changed or removed since the unit's last answer (the pages a bundle read kept as blobs) beside the kinds naming it; `make modal-triaged BUNDLE= REPLY=` answers the kinds a reply does not name and sends the named on; `make modal-bundle` refuses a unit owed only a triage (FR-001)
      research: rendering
      verify: DONE. DONE. modal_triage.py + make modal-triage/modal-triaged; bundles keep the pages they read (page: lines, blobs), answers store them; modal-bundle refuses a triage-only unit (REASON= to override); record-owed names the triage; tests red on the old owing (the depiction bundle test now refused) and green after
- [x] T09 Line-scoped procedure claims (plan D2): `tools/claims.py` fingerprints a section claim by its own line and keeps the section's own fingerprint and blocks; a section edit elsewhere owes a triage through `make claims-triage`, a table row being a block; `claims.py backfill-sections` migrates the index without owing anything; 100% coverage on `tools/claims.py` (FR-002)
      research: rendering
      verify: DONE. DONE. tools/claims.py: a section claim's code is its own line, section_blocks (table rows each a block), 100% on the new lines; claims_triage.py split out (claims.py 761 lines); section triage in claims-triage; backfill-sections re-keyed 281 real claims, nothing newly owed; tests red-first on the one-row edit
- [x] T10 File, don't fix (plan D15, its owing half): every check bundle's MANIFEST lists the blocks the delta changed (`changed-blocks:`), the page checks' contracts put a finding on any other block under `OUTSIDE THE CHANGE`, and `make record-checked REPLY=` files that section as open rows in `specs/NNN/found.jsonl` (FR-006)
      research: rendering
      verify: DONE. DONE. check bundles end with The change (changed-block/changed-note lines vs the merge base); five page-check contracts report OUTSIDE THE CHANGE apart; make record-checked REPLY= files them to specs/NNN/found.jsonl; test_outside_the_change.py
- [x] T11 SC-001 replay: 372's waves 106, 108 and 111 through the old and the new owing - modal-depiction units owed in full and impl-drift claims owed - recorded in `measurements.json` against two thirds and four fifths (SC-001)
      research: rendering
      verify: DONE. DONE. make replay-owing over 372's 24 commits: impl-drift in full 385 -> 19 (95%); depiction owed only by a page 13 -> 3 after the replayed triage (77%), every depiction unit 26 -> 16 (13 are the waves' own Depiction edits); m:sc001-replay
- [x] T12 Batch 2 closes: `make done` green; landed
      research: rendering
      verify: DONE. DONE. make done green (384 s); landed by the push carrying this tick
## Batch 3 - the guards and the arbiter

- [x] T13 Decide, then freeze - the check state (plan D4): `hm_checks.py` keeps every page or pop-up check in flight (dispatch, launch, return, answer); `record-edit-hooks.sh` refuses an Edit to a subject while a check on it runs and, once the round has returned, any edit but the round's own EDIT blocks (`make apply-edits` on a reply of the round admitted); `check-bundle-hooks.sh` refuses a check already in an open round while another runs; `make check-closed` for a silent one (FR-003 b, c)
      research: rendering
      verify: DONE. DONE. hm_checks.py (pending/running/returned/answered, versions, replies kept); record-edit-hooks freezes Edit/Write and apply-edits, admitting only the round's EDIT blocks; check-bundle-hooks refuses a re-dispatch into a running round; checks-hooks wired on PostToolUse(Agent) and SubagentStop; make check-closed; test-checks-hooks.sh 15/15, red with the freeze removed; test_hm_checks.py
- [x] T14 EDIT blocks for the three page checks that had none - intro-check, record-style, translation-check - so every proposal on a frozen subject is a block (plan D4)
      research: rendering
      verify: DONE. DONE. intro-check, record-style and translation-check contracts end findings with EDIT blocks; agent tier test green
- [x] T15 Decide first (plan D3, D19): `make task-start`, `make decide F= T=` (a plan review of the task's section), `make plan-verdict TASK=`; a check dispatch refused until the active task's decisions carry a CLEAR verdict (FR-003 a)
      research: rendering
      verify: DONE. DONE. plan_gate task sections + record_task, make task-start/decide/section-sha, plan-verdict TASK=; check-bundle-hooks and pair-hooks refuse a check before the active task's decisions carry a verdict (a current whole-plan verdict covers an unchanged section); DECIDE_OK logged; tests in test_plan_gate.py and test-checks-hooks.sh
- [x] T16 Tripwires (plan D10): the record checks' round cap (two per subject per feature); an Edit putting back an earlier Edit's old text; a second red gate in a row; the cascade ratio past its measured threshold; a heavy run the quick tier covers - each writing `arbiter-owed` and refusing the next dispatch or gate until a ruling (FR-010)
      research: rendering
      verify: DONE. DONE. hm_arbiter.py: round cap (record checks two per subject per feature; the review cap to the arbiter), reversal (Edit digests in the event log, and block returns across the versions each dispatch found), red gate (ci/state.py, gates only), cascade (1.0 a line, 10 dispatches, raised per ruling); a guard firing on correct work fixed on the way (make-only read a hook suite as a guard file)
- [x] T17 The round arbiter (plan D11): `.claude/agents/round-arbiter.md` (Opus, high, omitClaudeMd, its tier row); `make arbiter-bundle TRIGGER=`, `make arbiter-ruled`; one binding ruling per trigger in `specs/NNN/arbiter.jsonl`; the review checks' cap goes to the arbiter instead of `REVIEW_ROUNDS_OK` (FR-011)
      research: rendering
      verify: DONE. DONE. round-arbiter contract (opus high, omitClaudeMd, tier row, pre-authorized), make arbiter-bundle (rounds marked NEW/REPEATED/REVERSING, edits.diff, cascade.txt, oscillation, request/spec), make arbiter-ruled (binding once, gm-review row, process fault filed); test_hm_arbiter.py
- [x] T18 The escalation filter owed only for open findings (plan D16): disarmed when the ledger's row for the review shows every finding disposed (FR-007)
      research: rendering
      verify: DONE. DONE. ledger_lint.disposed (fixed/verified/accepted/filed or nothing-found vs left for the GM; binding from 2026-10-11); escalation-hooks disarms when the review's own rows are all disposed; test-escalation-hooks.sh 24/24
- [x] T19 SC-006 replay: 372's waves 106 and 108 through the tripwires - 0105's and 0100's third rounds and the bath bullet's A -> B -> A fire, and no round past the cap needs a GM waiver (SC-006)
      research: rendering
      verify: DONE. DONE. SC-006: 0100's and 0105's third rounds fire (12:23, 14:40 UTC), the bath bullet's return fires (tests/tooling/test_replays_375.py over its three versions - the D10 wire widened to the versions each dispatch found, as the spec's 'computed from the file's history' asks; an Edit-digest wire alone could not see a script and a git checkout), both GM-waived rounds go to the arbiter; m:sc006-replay, m:cascade-threshold
- [x] T20 Batch 3 closes: `make done` green; landed
      research: rendering
      verify: DONE. DONE. make done green (488 s) after two reds the gate found (the escape census: three new escapes unclassified and unlogged - fixed); landed by the push carrying this tick
## Batch 4 - the gates and the doctrine

- [x] T21 The closing check (plan D13): `scripts/gates/close_check.py` - no report or a carried key missing refuses the last `make tick`, `make gm-reviewed` and the push of a touched feature that reads closed; `closed-before-375.txt` written from what read closed at its landing; `make speckit-todo` shows each carry (FR-009, FR-014)
      research: rendering
      verify: DONE. DONE. close_check.py (report + carried keys) asked by the last make tick, make gm-reviewed and the push of a touched feature that reads closed (CLOSE_OK, logged); closed-before-375.txt (250 features, 372 among them - its report then written anyway); speckit-todo shows carries via close_check --carries; test_close_check.py 3, sync suite 116 with its closed fixtures given reports
- [x] T22 The GM's review after landing (plan D12): `make gm-review` (held and to-review rows by feature), `make accept`, `make gm-reviewed [OVERTURN= TO=]`; the GM-review box added by the tooling; `make speckit-todo` reads `Done - GM review pending` (FR-012)
      research: rendering
      verify: DONE. DONE. gm_review.py + make gm-review/accept/gm-reviewed (OVERTURN= TO=); the GM box added by the tooling on a row (accept, an arbiter ruling) and honored only with an open row; speckit-todo state Done - GM review pending; make gm-review lists 328's three held rows; test_gm_review.py 4
- [x] T23 The preflight inside the gate (plan D14): `make done` begins with the derived files, the research pointers, spec-lint and the quick tier with coverage on the changed engine files, stopping there on a failure; the gate refuses green when a tracked file changed while it ran, naming it; its cost measured (FR-004)
      research: rendering
      verify: DONE. DONE. preflight.py first in make done (ahead of the reuse): derived files, record + pointers, make quick, the changed engine lines (stop off the hamlet path and outside modules tests outside quick reach); tree check before green; PREFLIGHT_OK reasoned and logged; 36-62 s at load 5-7, the record build most of it (m:preflight-cost; amendment 2 ruled LEGITIMATE); test_preflight.py 4
- [x] T24 The doctrine (plan D17): the root CLAUDE.md's guard table and an FR-010 note the advisor reads; docs/guards.md rows; research/CLAUDE.md (modal-triage, record-checked REPLY=, check-closed); docs/spec-kit-and-reviews.md (feature-report, decide, the arbiter, the GM's review) (FR-013)
      research: rendering
      verify: DONE. DONE. CLAUDE.md (guard table rows, the workflow bullets naming feature-report, decide, the arbiter's bundle), docs/guards.md (six rows), research/CLAUDE.md (a check round), docs/spec-kit-and-reviews.md; FR-013 pinned by test_375_doctrine.py
- [x] T25 SC-002's audit: each FR with the test that fails on the old behavior, listed in `audit.md` (SC-002)
      research: rendering
      verify: DONE. DONE. audit.md: FR-001..FR-014 each with its test and how it was proved red (removed, by construction or changed); the event-log suite proved red here (14 of 18 with its write removed)
- [x] T26 375 closes: `make done` green; its report written; T99 ticked; landed through its own closing check
      research: rendering
      verify: DONE. DONE. make done green (preflight clean in 36 s, then the verified reuse - batch 4 is scripts and docs); the whole tooling tree 1491 passed and hooks-test green against these scripts; plan amendments 1 and 2 CLEAR; 375's report regenerated; landed through its own closing check
- [x] T99 The last batch (plan D18) [lands-open]
      research: rendering
      verify: DONE. DONE. batches 1-4 landed (plan D18): measurement and the fixes, the owing logic, the guards and the arbiter, the gates and the doctrine

## Amendment 1 (the GM 2026-10-10: "yes to each of those possible changes")

- [x] T27 The triage names the page (plan D20) and depiction owed by its own words (plan D21); the 343 replay fixture and tests red on today's code (SC-007)
      research: rendering
      verify: DONE. modal_triage names the page (TOUCHES uid @ page), owes only units reading it, an unknown page owes all; depiction owed and fingerprinted by what it reads; 343 replay clears exactly the 11 units (reply-paged.md names files, not the plan D20 wording); test_modal_triage + test_modal_checks 26 passed, red on old code
- [x] T28 The clones' view in `make speckit-todo` (plan D22); its fixture test (SC-008)
      research: rendering
      verify: DONE. speckit-todo shows an open or reopened feature as an active clone holds it, marked not landed, by git (unlanded work only); measured active 0.14 s vs all 0.9 s, same rows (m:375-a1-speckit-todo-clones); test_speckit_todo 50 passed
- [x] T29 375 closes again: tooling tests and `make hooks-test` green, the gate, the report, landed
      research: rendering
      verify: DONE. make done green (reuse: scripts only); tests/tooling 1608 passed after the ledger row fix; make hooks-test green; report written; landed by the push carrying this tick

## Amendment 2 (the GM 2026-10-11: one ruling for a batch at the round cap; the bundle defect)

- [x] T30 One bundle and one ruling for a batch (plan D23): `arbiter_bundle.batch`, `hm_arbiter.record_batch`, `make arbiter-bundle/arbiter-ruled BATCH=1`, the contract, the refusal; tests red on today's code (SC-009)
      research: rendering
      verify: DONE. arbiter_bundle.batch + hm_arbiter.batch_triggers/record_batch + make arbiter-bundle/arbiter-ruled BATCH=1 [TRIGGERS=]; refusal names the batch; a single ruling refused while its batch is owed; one fix held by one row; test_arbiter_fix batch tests (red on old code)
- [x] T31 A round bundle reads its unit from the trigger (plan D24); its test (SC-010)
      research: rendering
      verify: DONE. hm_arbiter.unit_of, used by the bundle and the ruling row; test_a_round_asked_ahead_of_the_guard_carries_its_rounds (red on old code)
- [x] T32 375 closes again: tooling tests and `make hooks-test` green, the gate, the report, landed
      research: rendering
      verify: DONE. make done green (reuse: scripts only); tests/tooling 1614 passed; make hooks-test green; report written; landed by the push carrying this tick

## Amendment 3 (the GM 2026-10-11: pop-up checks in order; the record tooling made fast; hooks-test by what changed)

- [x] T33 The pop-up checks in order, form, research, depiction, and a round's edits settling the checks before it (plan D25, D26); tests red on today's code (SC-011)
      research: rendering
      verify: DONE. modal_owed.ORDER + modal_bundle.order_hold (CHECK_ORDER_OK) + apply_edits settling earlier checks; tests/tooling/test_popup_order.py 8 passed, 5 red on the old code (SC-011)
- [x] T34 One parse per content and one git batch per revision (plan D27, D28); outputs unchanged, a changed file, a changed parser and a changed module it imports each miss (SC-013)
      research: rendering
      verify: DONE. record_cache.py: ParseCache by text + transitive code sha (code_sha_of), RevReader/cat_blobs; units() scoped by family and uid for each bundle; outputs identical old/new/cache-off (m:375-a3-record-tooling-after); test_record_cache 7 passed
- [x] T35 The claims kept by their sources (plan D29); a changed engine module, a changed reader and a changed module the reader imports each miss (SC-013)
      research: rendering
      verify: DONE. claims.units_of keyed by engine sources, PROCEDURES and the readers' transitive imports; gc.freeze at the command's exit; claims-owed 6.47 -> 0.48 s warm, cold 6.36 vs 6.62 (m:375-a3-record-tooling-after); miss tests in test_record_cache
- [x] T36 The script tests run by what they touch (plan D30); fixture tests (SC-014)
      research: rendering
      verify: DONE. hookdeps.pydeps/--pystale/--pystamp with the whole-tree fallback; Makefile pytest step per file; 27.2 of 55 per commit, 16 whole-tree (m:375-a3-hooks-test-after); test_hook_deps 15 passed
- [x] T37 The measurements (plan D31): SC-013's times and SC-014's count recorded; SC-012 carried to 374
      research: rendering
      verify: DONE. SC-013 medians all at most half warm, cold below today (m:375-a3-record-tooling-after); SC-014 counted (m:375-a3-hooks-test-after); SC-012 carried to 374 (Carried line in spec.md)
- [x] T38 375 closes again: tooling tests and `make hooks-test` green, the gate, the report, landed
      research: rendering
      verify: DONE. make done green (306 s); tests/tooling 1664 passed with the make-targets page regenerated; make hooks-test green (233 s); spec FAITHFUL round 4, plan CLEAR round 3; report written; landed by the push carrying this tick

## Amendment 4 (the GM 2026-10-11: "yes please add that as amendment 4")

- [x] T39 The sync suite's cases as functions in parallel parts (plan D32); today's 123 checks in every mode, a failed and an unreported case each fail it (SC-015)
      research: rendering
      verify: DONE. 26 cases as functions in 4 parts, helpers hoisted; today 150.2 s vs parts 60.5 s median, 123 checks on all 12 runs; an injected failure and an injected exit each fail it, named (m:375-a4-sync-suite-parts)
- [x] T40 375 closes again: SC-015 measured, `make hooks-test` green, the gate, the report, landed
      research: rendering
      verify: DONE. make hooks-test green in 81 s (the sync suite in parts); make done verified; tooling tests unchanged by a tests/hooks-only delta; spec FAITHFUL round 2, plan CLEAR; report written; landed by the push carrying this tick

## Amendment 5 (the GM 2026-10-11: performance recorded and flagged, never a gate)

- [x] T41 The flag, never a refusal (plan D33); the 5% line (D35); tests red on today's code (SC-016, SC-018)
      research: rendering
      verify: DONE. perf_review.check prints the band and the FLAG with both snapshots' machine state, exits 0; arbiter_signed removed; BAND1_PCT 5.0 in both environments; test_perf_review 27 and test_perf_bands 22 passed, 5/5.1 percent pinned (SC-016, SC-018)
- [x] T42 The machine's state, CPU time and the warm-up roll (D34); the scaling leg on request and the trend (D36); tests (SC-017, SC-019, SC-020)
      research: rendering
      verify: DONE. machine_state at both ends, CPU beside wall per stage after an untimed warm-up roll, metric_of CPU-else-wall; scaling only with SCALING=1; perf-report with CPU, load and free RAM per snapshot; test_perf_snapshot 27 and test_perf_scaling 14 passed; a real snapshot taken end to end (SC-017, SC-019, SC-020)
- [x] T43 The texts (D37); 375 closes again: tests, `make hooks-test`, the gate, the report, landed
      research: rendering
      verify: DONE. the texts (constitution 2.30.0, CLAUDE.md, l7r/diagram/CLAUDE.md, dev/performance.md, docs/guards.md, docs/efficiency-tooling.md, the system prompt, perf-audit and round-arbiter, the Makefile); tests/tooling 1665 and tests/tools 607 passed; hooks-test green; make done green (254 s); report written; landed by the push carrying this tick

## Amendment 6 (the GM 2026-10-12: About no longer owes modal-depiction; handed to the Diagram performance session)

- [x] T44 About drops out of what owes `modal-depiction` (FR-028): the depiction fingerprint and the re-owe rule, `modal-depiction`'s contract, the replay of the 44 About-only edits; tests red on today's code (SC-021)
      research: rendering
      verify: DONE. DONE. depiction_owed_by the one rule, fingerprint without About, amendment-1 answers kept, contract reports nothing from About; test_modal_triage 11 and test_record_owed 27 passed, the owing tests red on the old code (worktree at HEAD d7988deb9^); replay 43 About-only of 221, none owed now (m:375-a6-about-only-replay)
- [ ] T45 375 closes again: 343's rows 83 and 84 closed in `found.jsonl`, tests, `make hooks-test`, the gate, the report, landed
      research: rendering
      verify: spec-fidelity on amendment 6, plan reviewed; make done green; make feature-report F=375 WRITE=1

## Amendment 7 (the GM 2026-10-12: "two, three, six, and eight are a good place to start", 1 measured)

- [x] T46 The cohort through the roll cache and its per-seed record (plan D38, D39); tests red on today's code (SC-022)
      research: rendering
      verify: DONE. DONE. cohort through the roll cache (cohort:<spec>, Refusal stored by name via cohort_roll), store shared with a linked worktree, KEPT_VERSIONS=4 per subject, per-seed record dev/cohort-log/; test_cohort_audit 22 and test_rollcache 31 passed, the new ones red on the old code
- [x] T47 The census on request (D40); the gate's shortcut earns the hooks stamp (D42); the gate commits its own record (D43); tests (SC-023, SC-025, SC-026)
      research: rendering
      verify: DONE. DONE. make perf runs no census; done's shortcut runs hooks-test when the hooks stamp is stale; done commits its own run record at all six sites (commit-run-record.sh); test_gate_record_and_shortcut 5 passed
- [x] T48 The batching and pair suites in parallel processes, entry-gate serial with its reason (D41); the scan recorded (SC-024)
      research: rendering
      verify: DONE. DONE. batching and pair suites in parallel parts (pair with chains 06-08 and 12-13), entry-gate serial on its scan (chain 03-06, 22 s); scan recorded as m:375-a7-suites-scan
- [x] T49 The measurements (D44): the cohort two waves before and after, the suites, the turn time (SC-022, SC-024, SC-027)
      research: rendering
      verify: DONE. DONE. SC-022 m:375-a7-cohort-after (wave 2 both legs 323 s -> 19 s, 54 of 54 served, verdicts identical seed by seed); SC-024 m:375-a7-suites-parts (pair 70.6 -> 18.8 s, batching 71.7 -> 20.4 s, probes fail named); SC-027 m:375-a7-turn-time; SC-021 m:375-a6-about-only-replay
- [ ] T50 375 closes again: tests, `make hooks-test`, the gate, the report, landed
      research: rendering

