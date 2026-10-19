# Implementation Plan: campaign costs I - inns, transport, cloth and sake (feature 396)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: four new money questions written from the four search passes in `passes/`. The work is one
write page session (four questions, the cap), one check-and-apply session, then the answer on EliAndrewC/diagram#3. No
code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s1-check.md"`. The passes are leads: each passage
  is read on its page before it is cited.
- **The wages.** Each figure sits beside the unskilled laborer's day wage of the same place and period where a source
  gives one. Where none does, the question says that wage is SILENT and names the nearest wage, with its place, its unit
  and its gap in years. A craftsman's wage is used only where no unskilled wage exists. Wages in hand:
  - Kyoto 1802-04, unskilled and craftsman (0250);
  - Osaka in the 1620s, unskilled (0257);
  - Edo in the 1850s, craftsman (0256);
  - Edo unskilled: only "broadly level with Kyoto" from 1818 (0256).
- **The units.** Most prices are in copper mon, and the wages are in silver monme. A mon price set beside a silver wage
  states both units. The copper-to-silver rate is not written here, so the issue's answer lists it as still open (the
  spec, User Story 2).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the four questions (FR-001, FR-002)

Each question is new and tagged `subject=money`, with no drawing page. Its level is `counts-and-measurements`.

| question | setting tag | what it covers |
|---|---|---|
| "What did a night at an inn cost?" | `countryside,city` | the hatago and kichin-yado rates, the horse charge, the Qing silence |
| "What did hiring a horse or a porter cost?" | `countryside` | the stage rates per ri, the negotiated rate, the return, the day hire, the Qing mule |
| "What did cloth and clothing cost?" | `countryside,city` | the tan, cotton, silk, the ratio, pongee, a kimono, the silences, Bassino and Ma beside the recorded cotton (0249) |
| "What did sake cost, by the shop and by the cup?" | `city,countryside` | the Edo shop, tavern and soba-shop prices, the Kazusa ceilings, the markups |

Each question answers its acceptance scenario: every attested figure, every silence, and each figure beside its wage. A
figure the project computes (a per-ri or per-day equivalent, a conversion) is labeled as the project's arithmetic.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds one line per question: "no code implements it - consumed by gm-assistant's money skill",
with the search.

## D3 - the answer (FR-004)

A comment on EliAndrewC/diagram#3 gives:
- each question's fragment FILE;
- the checked verdict for every figure;
- what is still open, with the copper-to-silver rate named wherever a mon price stands beside a silver wage. The
  exchange-rate lead posted on #3 (Kobe/Mitsui, Osaka 1787-1867) was never checked, and is named as such.

## T - the order

1. The page sessions.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
