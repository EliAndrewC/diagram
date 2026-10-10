# Tasks - feature 375, an efficient process enforced and measured by the tooling

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.
`tasks.md` holds the current batch only (plan D18); the batches are listed in the plan.

## Occasions

- none: no map, sheet, glyph or placement changes

## Batch 1 - measurement and the two fixes

- [ ] T01 The event log (plan D7, D9): `scripts/hooks/event-log-hooks.sh` + `scripts/measure/event_log.py` (the line, the category, the feature), wired in `.claude/settings.json` on PreToolUse, PostToolUse, SubagentStart, SubagentStop, UserPromptSubmit and Stop; its suite `tests/hooks/test-event-log-hooks.sh`; the per-call cost measured (`m:event-hook-cost`) (FR-008)
      research: rendering
      verify: the suite green; proved red with the hook's append removed; the cost recorded
- [ ] T02 The transcript converter (plan D8): `event_log.py from-transcript` turns a Claude Code session transcript into the same events, Edit digests included; tested on a fixture transcript (FR-008, FR-009)
      research: rendering
      verify: the fixture's events equal the expected lines; 372's transcript converts
- [ ] T03 `make feature-report F=NNN [TRANSCRIPT=]` (plan D8): `scripts/measure/feature_report.py` writes `specs/NNN/report.md` from the events, `dev/run-log/`, the ledger, plan reviews and git; SC-005 on 372 (the spec's Why table reproduced, under ten seconds) and on a one-task feature (FR-009, SC-005)
      research: rendering
      verify: tests over fixture sources; SC-005's two runs timed and recorded (`m:sc005-372`, `m:sc005-one-task`)
- [ ] T04 The claims triage (plan D5): the parser pinned to lines opening `TOUCHES `; the located defect fixed - a snapshot's page text kept as a blob so a withdrawn, never-committed block is shown rather than forcing every claim, and the named and forced counts reported apart (FR-005, part a)
      research: rendering
      verify: a test red on today's code for the withdrawn-block case, green after; the parser cases pinned
- [ ] T05 A plan verdict survives a typo (plan D6): `plan-review.json` keeps the reviewed text; `plan_gate.judge` admits a typo-scale diff and voids any other; tests for each side, the 372 typo among them (FR-005, part b)
      research: rendering
      verify: tests red on today's gate for the typo case, green after; a new decision still voids
- [ ] T07 Staying open between batches (plan D18): a `[lands-open]` task mark exempt from the open-task refusal in `sync-with-main.sh` and read as open by `make speckit-todo`; `**Waits on**: NNN` refused by `make tick` while NNN is open; tests that an ordinary open box still refuses the push and that a waiting feature's tick refuses
      research: rendering
      verify: test-sync-with-main.sh and tooling tests green; proved red with the exemption removed
- [ ] T06 Batch 1 closes: `make done` green; `make hooks-test`; 375's report so far written from this session's transcript; landed
      research: rendering
      verify: the gate's run-log line; the report file
- [ ] T99 Batches 2-4 (plan D18) [lands-open]
      research: rendering
      verify: ticked by the last batch
