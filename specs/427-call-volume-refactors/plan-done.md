# 427-call-volume-refactors - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-26 -->
### T01 Approach (checklist part A)

1. **The goal, in the world.** A session asks which functions run millions of times and from which loop, and one command
   answers.
2. **The constraints.** D1; FR-001, FR-002, SC-001.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 2 and 5; `tooling-perf-fanout.md`.
4. **Do they describe the world here?** Yes: the reference walk produced `research/fanout-2026-10-26.txt`.
5. **The order.** First: every engine task is scoped against its output (FR-002).
6. **The exits.** Green: its tests red without D1, and `make perf-fanout` on the current engine compared with
   `research/fanout-2026-10-26.txt` (FR-001, SC-001). Red: a red test, or a seed that passes on HEAD failing after (FR-007),
   which a tool that changes no stage cannot cause, recorded and the task set down; a claim that it cannot be done is ruled
   through `make arbiter-ask`. A seed already failing on HEAD is no exit (`request.md` 4 and 5).
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D1; `make perf-fanout` on the current engine lists the chains, compared with
   `research/fanout-2026-10-26.txt`.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** Every snapshot says how many Python calls each stage made, on each seed.
2. **The constraints.** D2; FR-006.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 4; `call-count-flag.md`.
4. **Do they describe the world here?** Yes: counts are deterministic per seed and size.
5. **The order.** After T01; before T03, which compares what it records.
6. **The exits.** Green: its tests red without D2, and a `make perf` snapshot carrying counts. Red: what failed recorded and the
   task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D2; the counting pass's overhead on the reference seeds recorded beside the code.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

<!-- plan-archive: archived 2026-10-26 -->
### T03 Approach (checklist part A)

1. **The goal, in the world.** A landing that makes the engine do more Python work says so, and lands only on the arbiter's
   accept; a slower machine says nothing.
2. **The constraints.** D3; FR-006, SC-005.
3. **Where each comes from.** The GM 2026-10-26, `request.md` 4; `call-count-flag.md`.
4. **Do they describe the world here?** Yes: the counts T02 records.
5. **The order.** After T02.
6. **The exits.** Green: its tests red without D3; a deliberate extra loop refuses the push and an accept clears it (US5's
   test). Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** Its tests red without D3; US5's independent test run on a scratch change.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

