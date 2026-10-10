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
- [ ] T99 Batches 3-4 (plan D18) [lands-open]
      research: rendering
      verify: ticked by the last batch
