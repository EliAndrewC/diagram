# 418-hoei-rates-and-canton-cash - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-25 -->
## T01 - Japan's market rates of 1705-1719 in 0287 (D1)

### T01 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can build `osaka-1712` and replace `osaka-1695`'s borrowed 1706-1711 rates from yearly market rates, each with the silver (and gold) it is quoted in.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or an absence note); the 20,000-byte question cap; `make record-owed` clean; the spec's acceptance 1-3.
3. **Where each comes from.** O: gm-assistant's two questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; Kusama is one Osaka merchant's compilation a century later, labeled ATTESTED ONLY FOR that; Edo's rates are jawiki's, their printed sources named as unread.
5. **The order.** Write (s1), check and apply (s2), the round-2 tail closed by the arbiter (ask:418-round3, accept).
6. **The exits.** 1715-1716 SILENT in Kusama rather than interpolated; no separate Yotsuho market rate (NOT ATTESTED) rather than one derived from the decrees.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0287 and 0277.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** As the section "D1 - Japan, 1705-1719" states. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
## T02 - Canton's cash in the 1830s in 0289 (D2)

### T02 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant knows whether `canton-1835`'s borrowed rural-Beijing cash rate can be replaced by Canton's own, and what the *Chinese Repository* gives.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or an absence note); the 20,000-byte question cap; `make record-owed` clean; the spec's acceptance 1-3.
3. **Where each comes from.** O: gm-assistant's two questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; a rate from elsewhere is ATTESTED ONLY FOR its place, and the per-tael figure from Canton's per-dollar one is labeled this project's arithmetic.
5. **The order.** Write (s1), check and apply (s2), the round-2 tail closed by the arbiter.
6. **The exits.** Canton's own cash per tael SILENT with the volumes searched and the leads not followed.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and its share of the check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for 0289.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D2** As the section "D2 - Canton's cash, the 1830s" states. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
## T03 - the implementation check (D3)

### T03 Approach (checklist part A)

1. **The goal, in the world.** The GM can see no code decides a coin rate, so no claim is owed.
2. **The constraints.** research/CLAUDE.md (feature 378): each touched question's line in `implementation-check.md`.
3. **Where each comes from.** G: research/CLAUDE.md.
4. **Do they describe the world here?** Yes.
5. **The order.** After the pages.
6. **The exits.** n/a.
7. **The search smell.** None: research, not a fit.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=418`: nothing missing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D3** As the section "D3 - the implementation check" states. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
## T04 - the reply on #13 (D4)

### T04 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can take each year's rates and the Canton findings from the reply alone.
2. **The constraints.** FR-002 (each rate with its fragment file, verdict and coinage, as acceptance 1 requires); SC-002 (what the *Chinese Repository* gives).
3. **Where each comes from.** O: the spec's FRs from the request.
4. **Do they describe the world here?** Yes.
5. **The order.** After the pages and the implementation check.
6. **The exits.** The two means left to gm-assistant: the per-year rows meet the request's either-or.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One reply.
9. **Done, measured.** The comment's URL.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T04 Decisions

- **D4** As the section "D4 - the reply" states. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
## T05 - close: report and land (D1-D4)

### T05 Approach (checklist part A)

1. **The goal, in the world.** The findings on main, the report written.
2. **The constraints.** `make land`'s refusals; `make feature-report F=418 WRITE=1`.
3. **Where each comes from.** G: CLAUDE.md, Development workflow.
4. **Do they describe the world here?** Yes.
5. **The order.** After the reply.
6. **The exits.** n/a.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One landing.
9. **Done, measured.** Landed.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T05 Decisions

- none beyond D1-D4. Rendering: none.
