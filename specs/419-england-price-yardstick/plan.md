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

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
