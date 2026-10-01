# Rubric - task I: the storehouse annex goes to the larger houses first

Frozen before the task's first run (spec FR-008, SC-002; re-frozen when the GM replaced the task, 2026-09-30). Each criterion is
scored 0-4 on its anchors, for A and for B separately; the total is the weighted sum (maximum 4 x 11 = 44). **Pass line: a total of
26 or more AND at least 3 on criterion 1 AND at least 2 on criterion 2.**

| # | criterion | weight |
|---|---|---|
| 1 | The acceptance criteria met | 3 |
| 2 | Regression and gate results | 2 |
| 3 | The moved maps as a reader sees them | 2 |
| 4 | The size and shape of the change | 2 |
| 5 | Decisions recorded in the four classes | 2 |

## 1. The acceptance criteria met (weight 3)

- **4** - On every scripted hamlet the houses that carry the storehouse annex are the largest (by footprint) among those eligible,
  the share of houses carrying one is the record's, a tie is broken by a stated rule, a test asserts it over the pool's hamlets (not
  one map), and no other tier's map and no hand-drawn map was changed.
- **3** - All of the above except a test that covers only the reference hamlet, or one hamlet left with the reason recorded.
- **2** - Mostly ranked by size, but the share moved without a reason, or the ranking is not the footprint.
- **1** - Only the reference hamlet is ranked.
- **0** - Still by position, or the change touches another tier's map or a hand-drawn map.

## 2. Regression and gate results (weight 2)

From `make-done.txt` and the diff.

- **4** - A green `make done` at the end; the baseline taken in a detached worktree; no test that passed before fails after; the
  performance bookends taken and any band's records written; coverage kept at 100%.
- **3** - Green, with one of the bookkeeping items (bookends, baseline record) missing.
- **2** - Green, but a regression explained away rather than fixed, or coverage kept by a test that asserts nothing.
- **1** - Not green, with the failures named.
- **0** - Not green and not said.

## 3. The moved maps as a reader sees them (weight 2)

From the moved maps' pictures and notes, and the review findings the output records.

- **4** - The storehouse annexes now sit on the big houses; nothing else on the maps moved that should not have (a re-pack the change
  caused is explained); the settlement-reviews found nothing left unfixed.
- **3** - Reads well; one small review finding left and recorded.
- **2** - The annexes moved, but something else moved with them unexplained on one map.
- **1** - Unexplained moves on several maps, or review findings left unrecorded.
- **0** - The maps are worse than before.

## 4. The size and shape of the change (weight 2)

From `changes.diff`.

- **4** - The ranking reuses the engine's existing way of ordering houses for a fixture (as the sketch names), sits where the annex is
  decided, adds no special case, and is small for what it does; tests read like the code around them.
- **3** - Sound, with one piece that could have reused existing machinery.
- **2** - Works, but by a second mechanism beside the existing one, or with a special case.
- **1** - Works only through patches after the fact.
- **0** - Fragile or unreadable.

## 5. Decisions recorded in the four classes (weight 2)

- **4** - Every rendering decision (the ranking, the tie rule, the share, anything else) is recorded in the four classes with its
  reason, in the research record, the operative doc and a pointer at the point of change, and in the handoff table; the record's
  grounding ("the larger houses first", homesteads/720) is cited, not restated from memory.
- **3** - All recorded, one place of the four missing.
- **2** - Recorded in the handoff only.
- **1** - Some decisions unrecorded.
- **0** - None recorded, or a guess left unlabeled.
