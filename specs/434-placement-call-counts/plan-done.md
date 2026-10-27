# 434-placement-call-counts - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-27 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** The page shows each stage's calls in its heading and ends with the expandable table (D4, D5).
2. **The constraints.** FR-003, FR-004, FR-005; SC-001, SC-004.
3. **Where each comes from.** `spec.md`, `request.md`.
4. **Do they describe the world here?** Yes: the page's stage headings (`<div class="hd">`) and its last section
   (`id="missing"`) as `placement_stages.build_page` writes them.
5. **The order.** After T01.
6. **The exits.** Green: on a page built from a test record, every heading's count and every table row's numbers match the
   record, the steps open and close, an unmeasured stage shows a dash, and no time appears.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the headings | a test on the page built from a test record |
| the table and its rows | the same test; the toggle checked in the generated page |

<!-- plan-archive: archived 2026-10-27 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** The reference hamlet at 40 households measured and the page regenerated with its counts; the
   other map types (row, dispersed, polder, dike-pond) measured too where a 40-household roll of them stands.
2. **The constraints.** SC-001 to SC-004.
3. **Where each comes from.** `spec.md`.
4. **Do they describe the world here?** Yes: `make perf-fanout` measures the reference spec at the same seed and size as
   `make phase-calls`' default (D6), the comparison SC-003 names.
5. **The order.** Last.
6. **The exits.** Green: the record committed, the page regenerated, each stage's count equal to the fanout's.
   Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Not yet measured.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

Each step measured alone:

| step | measured by |
|---|---|
| the record | `make phase-calls` |
| the agreement with the fanout | `make perf-fanout HOUSEHOLDS=40` on the same engine |
| the page | `make placement-stages`, read |

