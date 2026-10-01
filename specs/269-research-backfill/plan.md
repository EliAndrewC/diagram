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
  on), and `then:wait265.sh` before EVERY group that edits an existing fragment - A1 and R1 among them, since A1
  edits 0018 and 170-173 and R1 0235 - waits until the CLONE has 265's landing (its
  close, 1c2797c99, an ancestor of HEAD; main carrying it is not enough, because `sync.sh` merges nothing while the tree
  is dirty), with no time limit: the spec's Edge Cases hold such a group back until then, so a long wait is a stalled
  queue for the hourly heartbeat to flag, never a reason to go on.
  **As run, this was not held** (found by the plan review's round 2, 2026-09-28): the queue ran A1 (12:40) and R1
  (13:22) as new-question groups before the wait, and the clone first had 265's close at the H3 sync-in merge
  110004e58 (16:50), where 0023 conflicted and A1's version was kept. Checked at the landing: every fragment
  both sides edited in that merge (0023 and four registry entries - satoyama-jawiki, ohmi-yoshi,
  nippon-com-gokaido, tonami-yashikirin-haichi) keeps main's edits - the four entries' translated titles are all
  present, and 265's one change to 170, the fry line's "attested and drawn, as a share of the ponds", is superseded by
  A1's fuller line saying the same; R1's fragments did not conflict. Nothing main had landed was dropped.
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
