# Implementation Plan: books, skilled wages, a smith's income, and entertainers (feature 423, diagram#19)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

A research-record feature answering the GM's four questions from search passes (`passes/q1-books.md`, `q2-skilled.md`,
`q3-smiths.md`, `q4-entertainers.md`). Two write sessions, each followed by a check-and-apply session, in two sibling clones side by
side: `/diagram/.clones/diagram-money-marks` (S1: Q1 books and Q3 a smith's accounts, two new questions) and
`/diagram/.clones/diagram-money-pages` (S2: Q2 skilled and trusted labor and Q4 entertainers). Then the reply on #19. No code, map or
canon change.

## Technical Context

- **The passes** are leads, not citations: each write session reads every passage on its page before citing it, and fixes any
  ledger outcome a pass recorded wrongly (the Q3 pass marked two pages it used `nothing-found`).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - books (Q1; FR-001)

A new money question, its title asking what a book cost to buy, to borrow and to have copied. Japan: kibyoshi by the volume (5
leaves; the two retail figures given as their sources give them, tertiary, unreconciled), the Tenpo gokan and yomihon trade prices
from Bakin's letters (wholesale or trade, said), lending fees per volume (the late-18th-century range and Nagatomo's scale); a
classic, primer or reference volume's price SILENT with the search (the 『増益書籍目録』 lead named); a copyist's rate SILENT, the one
lumped fair-copy fee given as what it is. China beside it: late-Ming prices per volume and per juan, a hand copy under 0.4 tael,
the Siku copyists' 1,000 characters a day (paid in rank, not cash). Against the canon: scribes among the heimen, no price.

## D2 - skilled and trusted labor (Q2; FR-001)

In 0275 (skilled against unskilled) or a sibling by size: a merchant house's live-in clerk by seniority, a scribe by the day; an
armed escort of goods or cash, and China's biaoju, per day or per trip; a household cook, a lord's cook, a lady's maid, each with
what came in kind. The ledger's Kanazawa lead (0.7-1 koku a year for servants, 3 for a young steward) confirmed, narrowed or
contradicted, its source traced and cited from the work, never the ledger. Against the canon: stipend = rank squared for samurai
clerks; servants and cooks hinin.

## D3 - a maker's income (Q3; FR-001)

A new money question beside 0276, its title asking what a smith earned. A tool's price against its iron (Qing Beijing 1736: the
sickle and wrought iron on one list, ATTESTED ONLY FOR a government purchase list; Japan: the 1822 Sakai hoe, the 1841 Echizen
repair charges, iron only in rice per kan - any ratio this project's arithmetic across sources, its caveats said; the two Japanese
figures left unreconciled where the sources do not reconcile them); who paid for charcoal in the itinerant model; output a year
(Takefu's sickles per household in aggregate; Sakai's tobacco knives a night); a smith's gross and net income SILENT; crew size
ATTESTED (a master with one or two helpers or grown sons; Qing shops one or two hands); payment in rice ATTESTED ONLY FOR
20th-century practice; the Edo carpenter's year as the second case, third-hand, said. Against the canon: smiths heimen craftsmen.

## D4 - entertainers (Q4; FR-001)

Beside 0266 (plays) or in it by size: a traveling troupe's takings per performance and per year and their sharing, a street
performer's day, a star actor's yearly pay, a traveling or rural troupe's size, the price of a costume (ordinary and fine), a
shamisen, a flute and a tsuzumi; Japan first (kabuki, rural troupes, Morisada), China beside it. Against the canon: the county
troupe of about 5-10 earning most on market day, with performances at the magistrate's manor; entertainers hinin.

## D5 - the implementation check and the reply (FR-003, FR-004)

`implementation-check.md` holds each touched question's line; the reply on #19 gives each figure with its fragment file and
verdict, and figures gm-assistant's estimates E0169-E0193 can be graded against; findings for the GM go through
`escalation-check` first.

## T01 - Q1 books and Q3 a smith's accounts (D1, D3)

### T01 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can price a book, a loan and a copy, and a smith's tools against their iron, and knows where the record is silent.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-3.
3. **Where each comes from.** O: the four questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; Japanese and Chinese figures each ATTESTED ONLY FOR their place, time and market level (retail, wholesale, a government list).
5. **The order.** S1 write, C1 check (marks clone).
6. **The exits.** A figure no source gives is SILENT with its search, never estimated; two sources that disagree are both given.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the two new questions.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1, D3** As the sections "D1" and "D3" state. Rendering: none.
## T02 - Q2 skilled and trusted labor and Q4 entertainers (D2, D4)

### T02 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can price a clerk, a guard, a cook and a maid, and an entertainer's income, troupe and gear.
2. **The constraints.** The record's citation rules (a verbatim passage on a readable page, or SILENT with its search); the 20,000-byte question cap; at most four questions and ten new keys a write; `make record-owed` clean; the spec's acceptance 1-3.
3. **Where each comes from.** O: the four questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes; each figure ATTESTED ONLY FOR its place, time and house.
5. **The order.** S2 write, C2 check (pages clone), after the Q2 and Q4 passes.
6. **The exits.** A figure no source gives is SILENT with its search; the Kanazawa lead is cited only from its own work.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the touched questions.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D2, D4** As the sections "D2" and "D4" state. Rendering: none.
## T03 - the implementation check and the reply (D5)

### T03 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify each answer, grade its estimates and close #19.
2. **The constraints.** `make impl-check F=423`; `escalation-check` on what is for the GM.
3. **Where each comes from.** O: the four questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01 and T02 land.
6. **The exits.** None.
7. **The search smell.** None: research, not a fit.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=423` nothing missing; the reply posted; `make feature-report F=423 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** As the section "D5" states. Rendering: none.
