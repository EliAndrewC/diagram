# Implementation Plan: The research backfill

**Feature**: `269-research-backfill` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

Forty-six owed items ([`inventory.md`](inventory.md), B01-B46) in twenty groups, researched by the process feature
250 landed, on feature 267's pattern: each group is a WRITE session and then CHECK sessions, each one a fresh headless
session from a written brief (`make page-session`). The state between them is carried in the group's handoff file.
This session orchestrates. It writes the briefs, queues the sessions, keeps the queue and the peers alive through
usage-limit resets, and once a group is checked, rewrites the kinds and the generator its outcomes bear on.

## Decisions

- **D1 - The research runs in page sessions, not here** (FR-005), as 267 D1. Briefs come from `briefs/gen.py`
  (`write <G>` from the inventory; `checks <G>` from the handoff, two questions a session, the new keys with the last),
  and the check briefs are queued as `then:<g>-checks.sh` steps.
- **D2 - One queue, serial, in this clone** (the runner's rule: do not edit the clone while it runs). The order is the
  inventory's "Queue order". `then:sync.sh` between groups merges main in (a conflict is aborted and the queue goes
  on), and `then:wait265.sh` before the first group that edits existing fragments waits, for up to 10 hours, until
  265 has landed (its close carries `scripts/reserve-prefix.py` to main).
- **D3 - Surviving the usage limit** (FR-007): the runner carries diagram-buildings' 4d13ad4f byte-identical. A
  failed session waits until the reset its message names, else 15, 30, then 60 minutes, and RESUMES by `--resume`,
  up to 14 times. This session holds an hourly `CronCreate` heartbeat (at :17). It fires only while this session is
  idle, so after a limit ends one of this session's turns, the next firing after the reset resumes it. The heartbeat
  restarts a queue whose runner process has died with work left, and checks the peers (D4). The heartbeat lives as
  long as this Claude process does, and expires after 7 days.
- **D4 - Peers** (FR-008, spec US3): the claims live in `/diagram/.clones/RESEARCH-CLAIMS.md`. On each heartbeat,
  `ListAgents` is read, and a peer research session that is idle while its claimed work is unfinished is messaged to
  resume. The next wake confirms it resumed (busy, or new commits or run-log lines since), and a peer still idle is
  messaged again. A busy peer is never messaged. Each check is a line in `/diagram/.clones/RESEARCH-PEER-CHECKS.log`
  (FR-008). Each write brief re-reads the claims file first and marks its group in 269's line (FR-011). Headless queues (the peers'
  runners) resume by themselves once they run 4d13ad4f.
- **D5 - Prefixes** (FR-005): new registry and glossary files are reserved through
  `/diagram/.clones/.tools/reserve-prefix.py`, a byte copy of 265's, under the same lock and ledger. It is kept
  outside the repository so the file lands only with 265.
- **D6 - An item's outcome is one of four**, recorded in its handoff line `B<nn> <OUTCOME> - ... - ...` and gathered
  into `outcomes.md` (FR-001).
- **D7 - The kinds and the generator follow, in this session, per group, after its checks** (FR-003, FR-004): the
  `Entry:`, label and prose of each kind follow the outcome, with `entry-drift` on a bundle. A map-changing outcome
  becomes an engine change (a KNOB rolled from the seed), the motivating map is regenerated, and `make done` must be
  green. A change past one feature's size goes into `future-work/` with measurement, mechanism and sketch.
- **D8 - Corrections owed to another feature's section** are sent to that session by `SendMessage`, and are listed in
  `outcomes.md`.
- **D9 - The GM's items go through `escalation-check`** (FR-010).
- **D10 - future-work is closed out at the end** (FR-009): each answered item is moved to `closed.md` or rewritten to
  what remains.

## Constitution check

- XII: every finding is read (`source-reader`) before it is written. It is quoted and checked (quote-check,
  record-format, source-applicability), and labeled one of four classes. A silent record is labeled a guess, with its
  search.
- XIII: an engine change is measured against a detached-worktree baseline, and the gate runs before the landing.
- XIV: a defect found in passing is fixed in the same work, or recorded where it was found.
- XVI: every inventory item is researched. The GM's two decisions (B33, B34) get research, and the rulings stay the
  GM's.
