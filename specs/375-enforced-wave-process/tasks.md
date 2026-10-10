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

- [ ] T13 Decide, then freeze - the check state (plan D4): `hm_checks.py` keeps every page or pop-up check in flight (dispatch, launch, return, answer); `record-edit-hooks.sh` refuses an Edit to a subject while a check on it runs and, once the round has returned, any edit but the round's own EDIT blocks (`make apply-edits` on a reply of the round admitted); `check-bundle-hooks.sh` refuses a check already in an open round while another runs; `make check-closed` for a silent one (FR-003 b, c)
      research: rendering
      verify: the hook suites drive each state; proved red with each refusal removed
- [ ] T14 EDIT blocks for the three page checks that had none - intro-check, record-style, translation-check - so every proposal on a frozen subject is a block (plan D4)
      research: rendering
      verify: each contract's reply form carries the block; the agent-model tier test still green
- [ ] T15 Decide first (plan D3, D19): `make task-start`, `make decide F= T=` (a plan review of the task's section), `make plan-verdict TASK=`; a check dispatch refused until the active task's decisions carry a CLEAR verdict (FR-003 a)
      research: rendering
      verify: suites red on a dispatch before the verdict, green after; a plan with no task sections uses the plan verdict
- [ ] T16 Tripwires (plan D10): the record checks' round cap (two per subject per feature); an Edit putting back an earlier Edit's old text; a second red gate in a row; the cascade ratio past its measured threshold; a heavy run the quick tier covers - each writing `arbiter-owed` and refusing the next dispatch or gate until a ruling (FR-010)
      research: rendering
      verify: each wire fires in its suite on the recorded shape; the threshold from the replay (m:cascade-threshold)
- [ ] T17 The round arbiter (plan D11): `.claude/agents/round-arbiter.md` (Opus, high, omitClaudeMd, its tier row); `make arbiter-bundle TRIGGER=`, `make arbiter-ruled`; one binding ruling per trigger in `specs/NNN/arbiter.jsonl`; the review checks' cap goes to the arbiter instead of `REVIEW_ROUNDS_OK` (FR-011)
      research: rendering
      verify: tests over the bundle, the ruling's three outcomes and a second dispatch refused
- [ ] T18 The escalation filter owed only for open findings (plan D16): disarmed when the ledger's row for the review shows every finding disposed (FR-007)
      research: rendering
      verify: test-escalation-hooks.sh cases for a disposed and an open row
- [ ] T19 SC-006 replay: 372's waves 106 and 108 through the tripwires - 0105's and 0100's third rounds and the bath bullet's A -> B -> A fire, and no round past the cap needs a GM waiver (SC-006)
      research: rendering
      verify: the replay's firings recorded in measurements.json
- [ ] T20 Batch 3 closes: `make done` green; landed
      research: rendering
      verify: the gate's run-log line
- [ ] T99 Batch 4 (plan D18) [lands-open]
      research: rendering
      verify: ticked by the last batch
