# Task I - feature 293: a footpath to the hamlet's own burial ground

You are a session started to do ONE task, headless: no one will answer a question while you work. Where you would ask the GM,
decide as the project's rules direct (research first, a knob where the record supports two forms, a labeled GUESS where it is
silent), record the question and what you did in `handoffs/293/I-handoff.md`, and carry on. Work in
the clone you were started in (`git rev-parse --show-toplevel`); every project rule in the CLAUDE.md files applies.

**Ad-hoc agents.** Dispatch any ad-hoc work that checks or judges (a verdict, a review, a comparison) that no defined agent
covers to the `adhoc-judge` agent. Dispatch ad-hoc reading, fetching, translating or extracting as you normally would.

## The task

`.claude/skills/diagram/future-work/farming-communities.md`, "OPEN 2026-09-28, OWED: no way reaches a burial ground, at any size
of settlement": no lane or path reaches a hamlet's own burial ground on any scripted map (Inashiro, Kashikawa, Kuwabata were named
by review), though the record says a path was there (religion-and-death 140: at the festival of the dead "the graves and the
paths to the graves are cleaned"). Make the scripted HAMLET generator draw a footpath from the settlement's way web to the edge of
every burial ground the hamlet rolls as its own, so that on every scripted hamlet with its own burial ground a path reaches it.
Hamlets only: no other tier, and no hand-drawn map.

This is a task under feature 293, which is already claimed: do not claim a feature number and do not write a spec. Record every
rendering decision you make (the path's width, where it meets the ground's edge, what the page calls it, anything else) in the
four classes - historically accurate, deliberate deviation, map drawing convention, guess - where the project records them (the
research record, the operative doc, a pointer at the point of change) AND as a table in the handoff file above.

## How to work

- Read `.claude/skills/diagram/l7r/diagram/CLAUDE.md` and the `dev/` doc your step is in (`dev/placement.md` for the draw order and
  the keep-clear contract, `dev/pool.md` before touching the pool).
- Take the regression baseline FIRST, in a detached worktree (`git worktree add --detach <dir> HEAD`), never a stash, and the
  performance bookends (`make perf LABEL=293I-start` before the first edit, `make perf LABEL=293I-end` at the end, then
  `make perf-report AGAINST=293I-start`, with what a band owes).
- Inashiro is the reference hamlet: make the change work there first, then across the pool.
- Tests with the change, 100% coverage, the whole affected test file before the gate, then `make done` once, backgrounded, acted on
  at its notification.
- Every map whose layout moved gets its `settlement-review` (one map per agent); fix what they find, and send anything for the GM
  through `escalation-check` into the handoff.

## Where you stop

Commit in this clone with messages beginning `293 I:`. The last state is a green `make done` with the moved maps regenerated,
reviewed and fixed, and the handoff written. Do NOT push, and do NOT run `scripts/sync-with-main.sh`. Your last message is one
paragraph saying what you did.
