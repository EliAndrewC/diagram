# Implementation Plan: miso and soy sauce in the basket, and what the opening changed (feature 422, diagram#18)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

A research-record feature answering gm-assistant's four questions from search passes already run (`passes/q1-*.md`,
`q2-eras.md`, `q3-modern.md`, `q4-opening.md`). Two write sessions, each followed by a check-and-apply session, in two sibling
clones side by side: `/diagram/.clones/diagram-money-marks` (S1: Q1 and Q2, miso and soy sauce) and
`/diagram/.clones/diagram-money-pages` (S2: Q4, the opening, and Q3 in 0299). Then the reply on #18. No code, map or canon change.

## Technical Context

- **The passes** are leads, not citations: each write session reads every passage on its page before citing it.
- **The silver rate.** The Mitsui cells are monme; grams are given at the era's coin rate (`money-conversions.json`
  `units.monme.silver_g`, from 0287) and, beside it, at Bassino and Ma's 3.11 g where 0249 already uses it, each labeled; gm-assistant
  confirmed on #18 that it takes the monme cells at its era rates (issuecomment-6402725625).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - miso and soy sauce: how much, and from how many soybeans (Q1; FR-001; acceptance 1, 5)

A new money question beside 0249, its title asking how much miso and soy sauce a household used and what they cost era by era.
Its first part: kg of miso and liters of soy sauce per adult-year, each with its source and verdict (a household or ration figure
divided per adult is this project's arithmetic, labeled); failing that, the soybean in a kg of miso and a liter of soy sauce in
Edo-period practice, and the share of a household's soybeans going to miso, soy sauce, tofu and natto; the source of Bassino and
Ma's 52 kg; and the remainder of the 52 kg left for tofu and natto, or its SILENT (spec review: owed in either branch). No
quantity is estimated. The addendum's modern yields (kg of miso per kg of dry soybeans, rice-koji miso; liters of soy sauce per kg
of soybeans, equal parts wheat), preferably from a Japanese industry or food-science source, any sourced yield given with its
source named, its proportions stated beside the Edo
prescriptions', labeled modern (`passes/q1-yields.md`). 0249 gets a pointer.

## D2 - miso and soy sauce era by era (Q2; FR-001; acceptance 2)

In the same question: a table of the Mitsui miso and soy sauce means per era held in the record's eras (kyoto-1745, -1790,
-1800; edo-1818, -1830, -1850, -1860; osaka-1712 and osaka-1706 with what city each row is), in monme and in grams at the era's
coin rate, each cell's n and range; edo-1860's rise within the era said; Kimura's osaka-1620 "Soya" only as what the sheet heads it
(soy sauce a reading); tokyo-1882 SILENT within its years, the 1887 "Soy" as nearest; the Chinese eras SILENT for soy sauce and
醬, with the searches. 0301 and 0302 get a pointer.

## D3 - the modern miso and soy sauce (Q3; FR-001; acceptance 3)

In 0299 (comparative): the cheapest household miso (Shirakiku red and white, 2.2 lb, Amazon) with Walmart's small tub beside it;
Walmart's own naturally brewed soy sauce (15 fl oz) with Kikkoman's 40 oz and gallon; the hydrolyzed store brand named as such;
USDA and BLS SILENT. Each dated, linked and archived.

## D4 - what the opening changed (Q4; FR-001; acceptance 4, 5)

A new money question, its title asking which goods' prices the opening of the ports changed. Edo 1860-67, per good: rice NOT
ATTESTED as a trade effect (the treaties' export ban; its rise late and tied to money by Shinbo); lamp oil and 雑穀 ATTESTED ONLY
FOR 1859-60, from an encyclopedia; soybeans SILENT on a trade tie; cooking oil named with its own verdict (the basket's edible oil is the same rapeseed oil
as its lamp oil, 0249; the 水油 the edict names and Shinbo's 種油 and 白油 are what the sources price, so cooking oil takes lamp
oil's evidence, said by name, or SILENT where the sources do not reach it); salt, firewood and wheat NOT ATTESTED; barley SILENT; Shinbo's
prices Kansai's, and his period ratios unable to separate trade from money (said). Beijing 1900-19: rice and millet SILENT. Tokyo
1882's soybeans: the low ratio holds 1879-95, starts at Kumon's 1879 source switch to LTES, deepens in the Matsukata deflation; a
series or grade difference possible, the start of Manchurian imports SILENT. No good is called changed from timing alone.

## D5 - the implementation check and the reply (FR-003, FR-004)

`implementation-check.md` holds each touched question's line; the reply on #18 gives each figure with its fragment file and
verdict; findings for the GM go through `escalation-check` first.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
## T03 - the implementation check and the reply (D5)

### T03 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify each answer and close #18.
2. **The constraints.** `make impl-check F=422`; `escalation-check` on what is for the GM.
3. **Where each comes from.** O: the four questions (`request.md`); G: research/CLAUDE.md, research/money-requests.md.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01 and T02 land.
6. **The exits.** None.
7. **The search smell.** None: research, not a fit.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=422` nothing missing; the reply posted; `make feature-report F=422 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** As the section "D5" states. Rendering: none.
