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

