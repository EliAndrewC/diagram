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
- [ ] T99 Batches 2-4 (plan D18) [lands-open]
      research: rendering
      verify: ticked by the last batch
