# Implementation Plan: England's premodern prices as a comparative yardstick (feature 419, diagram#15)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

A research-record feature: one new question in the "Comparative money: other societies" section on how steady English prices
were under commodity money, from the Bank of England's millennium dataset (the price level, 1209-2016) and Clark's English
prices and wages (single goods and wages, 1209-1869), each figure this project's arithmetic from `measure/england.py`
(`measure/england.out.md`). 0291 points to it. One write session and one check-and-apply session in the sibling clone
`/diagram/.clones/diagram-money-marks`; then the reply on #15. No code, map or canon change.

## Technical Context

- **The data.** The two files measured, fetched 2026-10-25 and byte-identical to 414's fetch of 2026-10-24 (`cmp`, observed
  2026-10-25); archived by the write session with the source keys it reserves, so the record's links resolve.
- **The record.** `make page-session` in `/diagram/.clones/diagram-money-marks`, briefs `briefs/s1-write.md` and `s2-check.md`.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question task is `research: physical` with its five boxes. XIII: `make record CHECK=1` and the record
  tests stay green. XVI: built as the spec's FRs.

## D1 - the question (FR-001; acceptance 1, 3, 4)

A new question, its title asking how steady English prices were before paper money, tagged `subject=comparative,money`, filed in
the section `comparative-money`. Its sections: the drift (the price level by period and by century, from the Bank of
England's column, with its source note and the pre-1661 years shown to be Clark's index rescaled, this project's check); the
swing (the price level's SD by period and the years moving more than 10%; the goods and wages from Clark, each with its year
pairs); beside Edo, the Qing and today (0290's and 0291's figures in the same measure, pointed to, not restated beyond a line
each). The two sources registered with the kind `comparative`. Clark's stated limit is the file's own caveat ("subject to
revision"); his blank years are dropped from the year pairs, which each figure counts; Lindert's interpolated silver price of
the pound is not used, so it is not carried; the flat year pairs the script counts are given as this project's observation,
never as interpolation, since the file does not say. The page's own words say these are a yardstick for players and never the basis of a Rokugani price.

## D2 - the figures (FR-002; acceptance 2)

Every figure from `measure/england.out.md`, labeled this project's arithmetic, naming the series, England, the measure, the
years and the year pairs. Nothing is computed in the page session itself.

## D3 - 0291 (FR-001)

0291's "Beside the premodern figures" gains a pointer to the new question, and its source comment drops "wait on the GM's
approval and are not written here".

## D4 - the implementation check (FR-003)

`implementation-check.md` holds the touched questions' lines (no code implements a comparative price).

## D5 - the reply (FR-002)

A comment on #15: the drift and the swing, the fragment file, and how to verify the landing.

## T01 - England's prices under commodity money, the new question and 0291's pointer (D1, D2, D3)

### T01 Approach (checklist part A)

1. **The goal, in the world.** A player or gm-assistant reads how steady English prices were under commodity money - little
   drift, a big swing from year to year - beside Edo, the Qing and today, as a yardstick and never a Rokugani price.
2. **The constraints.** The record's citation rules and the comparative rules (research/CLAUDE.md); the 20,000-byte question
   cap; `make record-owed` clean; the spec's acceptance 1-4.
3. **Where each comes from.** O: the GM's answer (`request.md`); G: research/CLAUDE.md, research/money-requests.md; the figures
   from `measure/england.out.md`.
4. **Do they describe the world here?** They describe England; the comparative kind and the section confine them to money
   questions, and `source-applicability` judges them on England's own terms.
5. **The order.** Write (s1), check and apply (s2).
6. **The exits.** A figure the script does not give is not written; a limit neither file states is not claimed.
7. **The search smell.** None: research, not a fit.
8. **The budget.** One write session and one check session.
9. **Done, measured.** `make record-owed` names nothing unanswered for the new question, 0291 and the two sources.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1-D3** As the sections "D1 - the question", "D2 - the figures" and "D3 - 0291" state. Rendering: none.

## T02 - the implementation check (D4)

### T02 Approach (checklist part A)

1. **The goal, in the world.** The feature closes with its findings checked against the code: none implements them.
2. **The constraints.** `make impl-check F=419`.
3. **Where each comes from.** G: root CLAUDE.md, "A research record feature closes only with its findings checked".
4. **Do they describe the world here?** Yes.
5. **The order.** After T01.
6. **The exits.** None.
7. **The search smell.** None.
8. **The budget.** Minutes.
9. **Done, measured.** `make impl-check F=419` reports nothing missing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D4** As the section "D4 - the implementation check" states. Rendering: none.

## T03 - the reply and the landing (D5)

### T03 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify the landing and close #15.
2. **The constraints.** The reply names the fragment file and the verify commands.
3. **Where each comes from.** O: `request.md` ("Please post here when it lands").
4. **Do they describe the world here?** Yes.
5. **The order.** After T01 and T02 land.
6. **The exits.** None.
7. **The search smell.** None.
8. **The budget.** Minutes.
9. **Done, measured.** The comment is posted; `make feature-report F=419 WRITE=1` written.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T03 Decisions

- **D5** As the section "D5 - the reply" states. Rendering: none.
