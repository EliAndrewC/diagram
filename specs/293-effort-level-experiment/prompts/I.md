# Task I - feature 293: the storehouse annex goes to the larger houses first

You are a session started to do ONE task, headless: no one will answer a question while you work. Where you would ask the GM,
decide as the project's rules direct (research first, a knob where the record supports two forms, a labeled GUESS where it is
silent), record the question and what you did in `handoffs/293/I-handoff.md`, and carry on. Work in the clone you were started in
(`git rev-parse --show-toplevel`); every project rule in the CLAUDE.md files applies.

**Ad-hoc agents.** Dispatch any ad-hoc work that checks or judges (a verdict, a review, a comparison) that no defined agent
covers to the `adhoc-judge` agent. Dispatch ad-hoc reading, fetching, translating or extracting as you normally would.

## The task

`.claude/skills/diagram/future-work/farming-communities.md`, under "Found by feature 280's settlement-reviews": "The storehouse
against the farmhouse is rolled per house by position, not by size (`houses.py`, `KURA_SHARE`): Sawada's one went to its
18th-largest of 19 houses, where the record gives it to 'the larger houses first' (homesteads/720). Sketch: rank by footprint as
`fixture_order_key` does for the wood shed." Make the scripted HAMLET generator give the storehouse annex to the larger houses
first, as the record says, keeping the share the record supports, so that on every scripted hamlet the houses that carry the annex
are the largest ones. Scripted hamlets only: no other tier's map is regenerated (the legacy maps are frozen), and no hand-drawn map
is changed.

This is a task under feature 293, which is already claimed: do not claim a feature number and do not write a spec. Record every
rendering decision you make (how the houses are ranked, what happens at a tie, the share, anything else) in the four classes -
historically accurate, deliberate deviation, map drawing convention, guess - where the project records them (the research record,
the operative doc, a pointer at the point of change) AND as a table in the handoff file above.

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
