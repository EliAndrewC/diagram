# Implementation Plan: kitchen knives, and the copper-to-silver rate (feature 401)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: two new money questions written from the three search passes in `passes/`. The work is one
write page session (two questions), one check-and-apply session, then the answer on EliAndrewC/diagram#8. No code, map or
canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s1-check.md"`. The passes are leads: each passage
  is read on its page before it is cited. NDL scans (the 1851 Edo price-cut list, the Tsuyama tariff, 『日本経済史』 9, 『堺市史』 3)
  are read on the page images; their images go to source-reader with `IMAGES=`.
- **The rate series (FR-003).** The Kobe RIEB Excel file is archived first (`make archive-inbox`). A script under
  `research/assets/` (or the feature's own directory, named in the notes) computes the decade means from the archived
  file, and the notes name it and its method: the days used, each day's value (its midpoint where a minimum and maximum are
  given), the years missing, and 1844-49 shown as the administered floor.
- **The wages.** Each knife price sits beside the craftsman's and the unskilled laborer's day wage of the same place and
  period where a source gives them; where none does, the question says that wage is SILENT and names the nearest, with its
  class, its place, its unit and its gap in years. The rate question gives rates, not converted prices.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the two questions (FR-001, FR-002, FR-003)

Each is new and tagged `subject=money`, with no drawing page. Its level is `counts-and-measurements`.

| question | setting tag | what it covers |
|---|---|---|
| "What did a kitchen knife cost?" | `city,countryside` | the 1851 Edo wholesale list per ten by kind and grade; Tsuyama 1665; the four makers SILENT; Sakai's 1761 output rule; the trade split; the Qing and Ming cleaver; the wages beside them |
| "What was copper coin worth in silver?" | `city` | the official 60 monme = 4,000 mon and 1842's 6,500; the Osaka series by decade in mon per monme and mon per ryo, beside the source's units; the 1844-49 floor; Edo's printed figures or SILENT; before 1787; the anchor years 1802-04 and 1842 |

## D2 - the implementation check (FR-004)

`implementation-check.md` holds one line per question: "no code implements it - consumed by gm-assistant's money skill",
with the search.

## D3 - the answer (FR-005)

A comment on EliAndrewC/diagram#8 gives each question's fragment FILE, the checked verdict for every figure, what is still
open, and whether the checked rate supports the Kazusa 1842 laborer-day conversion (132 mon, 0262), without adopting it.

## T - the order

1. The page sessions.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
