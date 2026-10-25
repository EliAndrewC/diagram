# 417-all-seeds-pass - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
## T02 - the hold made (FR-010)

### T02 Approach (checklist part A)

1. **The goal, in the world.** No engine task of a held claims feature can be started while 417 is open.
2. **The constraints.** `make task-start` is the one place a task becomes active (`plan_gate.task_start`).
3. **Where each comes from.** O: FR-010 and D4.
4. **Do they describe the world here?** Yes: a landing needs the active task, and the active task comes only from task-start.
5. **The order.** Second, small, lands alone (`make land-tooling`).
6. **The exits.** `HOLD_OK` for a non-engine task only.
7. **The search smell.** None.
8. **The budget.** 45 min.
9. **Done, measured.** 405, 372 and 384 carry the ON HOLD status (all three marked 2026-10-24); a test starts a 405 engine
   task and is refused, naming 417; a `HOLD_OK` on it is refused; a non-engine
   task with `HOLD_OK` starts; each red without the guard.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D9** A held feature is one whose `**Status**` line holds `ON HOLD` and `until feature NNN`; NNN open by `speckit-todo`'s
  own open/closed rule. An engine task is one whose text names a path under `l7r/` or `pool/`, or whose `research:` line is
  `physical`, or that names a decision whose plan section names such a path; unsure counts as engine. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
## T01 - the baseline and the tally (FR-001)

### T01 Approach (checklist part A)

1. **The goal, in the world.** The GM can read how often a seed nobody has used fails, by form and by cause, at main.
2. **The constraints.** Seeds the gate has never used; the cohort's sizes, forms and pins; main's engine, no diff.
3. **Where each comes from.** O: the spec's FR-001 and D1; the tally's method is the spec's gap section.
4. **Do they describe the world here?** Yes: `make cohort ... FRESH=0` rolls exactly that and records per seed.
5. **The order.** First: every later task is measured against it.
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** The 1,000-seed roll (background) plus 30 min for the tally.
9. **Done, measured.** `research.md` R3 holds the 1,000-seed table by form and cause from `make fresh-tally`, and the tally's
   test is red without it.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D7** The baseline is seeds 3000101-3001100, rolled in a detached worktree at main (`make cohort N=1000 SEED=3000101
  FRESH=0 JOBS=5`; five workers, the containers' memory at the cap). Rendering: none.
- **D8** `make fresh-tally` takes `COMMIT=` (records at that engine commit) and `SINCE=` (records at or after a UTC stamp),
  and counts a seed as fresh when it is at or above its record's `fresh_first`, or, for a `FRESH=0` roll, when the record's
  first seed is above the fixed range and the pinned rows (`cohort_gate`'s fresh start); one seed counted once per commit.
  Rendering: none.

<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-24 (feature 375 FR-044) -->
<!-- plan-archive: archived 2026-10-25 -->
## T03 - the inventory (FR-002, FR-003)

### T03 Approach (checklist part A)

1. **The goal, in the world.** Every place the engine places-then-repairs, asks a rule too late, codes a rule twice or
   refuses where room is the remedy is listed, with where it is and the point it breaks.
2. **The constraints.** D3's method; found, not remembered.
3. **Where each comes from.** O: FR-002, D3.
4. **Do they describe the world here?** To be found.
5. **The order.** After T01 (its causes rank the entries).
6. **The exits.** An entry that breaks no point is kept with the predicate that makes it so.
7. **The search smell.** None.
8. **The budget.** 3 h.
9. **Done, measured.** `research.md` R2 complete; one task per breaking group in `tasks.md`, each with its Approach added by
   plan-delta when it starts; the principle's draft text in R4 for the GM.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D10** The reading is split by package (ways, homesteads and homestead_parts, waterfields, the overlap registry and the
  rest), each read by an `Explore` agent on `sonnet` given D3's whole method - its five searches and its five classes (the four
  points, and a rule coded twice) - and every entry it reports checked by the session against the code before it goes in R2
  (a fetched claim is not an entry). The three searches that cross packages are run by the session itself over the whole
  tree - every `cohort_audit` rule with its callers in `l7r/`; every caller of `law.violations`, `lane_violators`,
  `row_rules`, `grove_rules` and the overlap matrix inside the generator's run; every pair of functions judging one rule -
  and their hits reconciled against R2 before T03 is done. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
## T04 - one stream-crossing rule (R2 G7; FR-006)

### T04 Approach (checklist part A)

1. **The goal, in the world.** The cohort's "a farmstead part across the brook from its house" asks the same predicate the
   placers ask (`_geom/water_index.crosses_a_stream`), so the check and the placing cannot disagree.
2. **The constraints.** `crosses_a_stream(house, part, streams)` is the one predicate (its docstring: "all three now call
   this" - the audit's copy was missed); the audit's `parts_across_brook` keeps its part list and its count.
3. **Where each comes from.** O: FR-006 (a second implementation of a rule is deleted), R2 G7.
4. **Do they describe the world here?** Yes: the audit's `_cross` is a strict orientation test; `segments_cross` is the same
   test with one side non-strict, so they differ only for a part or house exactly on a stream's line.
5. **The order.** First of the engine tasks: it moves no map (the audit is not the generator).
6. **The exits.** n/a.
7. **The search smell.** None.
8. **The budget.** 30 min plus the landing.
9. **Done, measured.** `cohort_audit.parts_across_brook` calls `crosses_a_stream`; its test pins a part across a reach
   counted and one on the house's bank not; the landing cohort green (FR-008).
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D12** `parts_across_brook` counts the parts `r` (with `of`) for which `crosses_a_stream(r["of"], (r["x"], r["y"]),
  manifest["streams"])`; its local `_cross` is deleted. The streams with fewer than two points are skipped by the predicate
  itself. Rendering: none.
