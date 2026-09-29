# Rubric - task I: a footpath to the hamlet's own burial ground

Frozen before the first run (spec FR-008, SC-002). Each criterion is scored 0-4 on its anchors, for A and for B separately;
the total is the weighted sum (maximum 4 x 11 = 44). **Pass line: a total of 26 or more AND at least 3 on criterion 1 AND at
least 2 on criterion 2.**

| # | criterion | weight |
|---|---|---|
| 1 | The acceptance criteria met | 3 |
| 2 | Regression and gate results | 2 |
| 3 | The moved maps as a reader sees them | 2 |
| 4 | The size and shape of the change | 2 |
| 5 | Decisions recorded in the four classes | 2 |

## 1. The acceptance criteria met (weight 3)

- **4** - On every scripted hamlet that rolls its own burial ground, a path is drawn from the way web to the ground's edge; the path
  is a footpath (its width the project's footpath width, not a lane's); a test asserts both over the pool's hamlets (not one map); no
  other tier and no hand-drawn map was changed.
- **3** - All of the above except a test that covers only the reference hamlet, or one hamlet unreached with the reason recorded.
- **2** - Most hamlets reached; the width or the test is off.
- **1** - Only the reference hamlet works.
- **0** - No path reaches a burial ground, or the change touches another tier or a hand-drawn map.

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

- **4** - The path reads as a path to the graves: it meets the burial ground at an edge that faces the settlement, does not cross a
  house, yard, paddy or water it should not, and the settlement-reviews found nothing left unfixed.
- **3** - Reads well; one small review finding left and recorded.
- **2** - The path is there but reads oddly (a detour, a crossing of a field, a stub that stops short) on one map.
- **1** - Odd on several maps, or review findings left unrecorded.
- **0** - The maps are worse than before.

## 4. The size and shape of the change (weight 2)

From `changes.diff`.

- **4** - The change is where the draw order says it belongs (the way-target registered where the ground is seated, before the web),
  reuses the web's own machinery, adds no special case to the router, and is small for what it does; tests read like the code around
  them.
- **3** - Sound, with one piece that could have reused existing machinery.
- **2** - Works, but by a second mechanism beside the existing one, or with a special case.
- **1** - Works only through patches after the fact.
- **0** - Fragile or unreadable.

## 5. Decisions recorded in the four classes (weight 2)

- **4** - Every rendering decision (width, where the path meets the ground, what it is called, anything else) is recorded in the four
  classes with its reason, in the research record, the operative doc and a pointer at the point of change, and in the handoff table;
  the record's grounding (the path attested at the festival of the dead) is cited, not restated from memory.
- **3** - All recorded, one place of the four missing.
- **2** - Recorded in the handoff only.
- **1** - Some decisions unrecorded.
- **0** - None recorded, or a guess left unlabeled.
