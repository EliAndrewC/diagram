# Implementation Plan: the Hoei and Shotoku market rates (1706-1718) and Canton's own cash rate in the 1830s (feature 418, diagram#13)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

A research-record feature: extend 0287 (coin by coin) with the market rates of 1705-1719, gold and copper against silver, each
named by the silver it was quoted in, and say which silver chiefly passed; extend 0289 (tael, string of cash, dollar) with what the
*Chinese Repository* and the other readable sources give for Canton's cash in the 1830s. Written from the search pass
(`passes/rates.md`), each passage read on its page before it is cited; one write session and one check-and-apply session in the
sibling clone `/diagram/.clones/diagram-money-marks`; then the reply on #13. No code, map or canon change.

## Technical Context

- **The record.** `make page-session` in `/diagram/.clones/diagram-money-marks`, briefs `briefs/s1-write.md` and `s2-check.md`.
- **Page images.** Kusama's 『三貨図彙』 (NDL pid 1279564, internet-public; its machine text refused) as read by the pass: viewer
  frames 409-419 (printed pp. 803-823), kept at `/diagram/.clones/diagram-money-pages/.git/418-pass/418img/` for the sessions'
  `IMAGES=`; the *Chinese Repository* volume texts beside them (`418cr`, `418cr3`).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - Japan, 1705-1719 (FR-001, FR-002; acceptance 1-2)

In 0287, a section on the market rates of the recoinage years: per year, Kusama's gold rate (monme a ryo, the gold named as he
names it - Genroku, Keicho or Genroku, Kenji, new) and copper rate (monme a kanmon of copper; mon a monme is this project's
arithmetic, 1,000 divided by it), each with the silver he quotes it in (Genroku to 1706, Hoei Futatsuho from 1706-1707 to 1713,
"current silver" - Eiji, Mitsuho and Yotsuho together - in 1714-1717, new silver from the eleventh month of 1718); 1715-1716 SILENT
in Kusama. Which silver chiefly passed: Kusama's own passages (p. 804, 1706; p. 816, 1714; p. 820, 1717), ATTESTED; a separate
market rate for Eiji, Mitsuho or Yotsuho NOT ATTESTED (the market quoted them as one); the decrees' legal ratios of 1714 and 1718
(pp. 816-817, 821-822) as the law's split, not the market's. Kusama's city: ATTESTED only as far as a source on Kusama himself
says (an Osaka money-changer, if a readable biography says so); otherwise "one merchant's compilation", unplaced. Edo's rates of
1714 and 1717-1718 from Japanese Wikipedia, ATTESTED ONLY FOR what jawiki states, its printed sources named as unread. The
coin-walk table named as the derivative it is (its rice from Kusama, its silver column from elsewhere). 0277 gets a pointer for
the new copper rates, not a copy. The page's "1706-1721 mixed coins, not converted" is revised to what is now known.

## D2 - Canton's cash, the 1830s (FR-001, FR-002; acceptance 3)

In 0289: the *Chinese Repository* searched by name and its findings given - Canton 1837, about 1,000 cash a dollar (vol. 6,
a letter-writer's conversion: ATTESTED ONLY FOR cash per dollar); the 1835-1836 review saying Canton's "1,000 cash = 1 tael" was a
nominal figure (no market number); Xu Naiji's memorial of 1836 (1,200-1,300 cash a tael, empire-wide); the other places as
ATTESTED ONLY FOR their place (Tianjin 1832, Nan'ao 1832, Fujian 1835, Taiwan 1838). Canton's own cash per tael: SILENT with the
search (the volumes read, the leads not followed). A cash-per-tael figure from 1,000 a dollar at 0289's 0.71-0.72 tael a dollar is
this project's arithmetic, labeled so.

## D3 - the implementation check (FR-003)

`implementation-check.md` holds each touched question's line (no code implements a rate).

## D4 - the reply (FR-002)

A comment on #13: per year the rates with their silver (and gold), which silver passed, the two means only if gm-assistant asks
for them (the per-year rows let it take its own); Canton's figures and its SILENT, and what the *Chinese Repository* gives.

## T - the order

1. The write session (s1). 2. The check session (s2). 3. The implementation check. 4. The reply and the landing.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
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
