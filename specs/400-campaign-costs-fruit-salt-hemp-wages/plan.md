# Implementation Plan: campaign costs III - fruit, salt, hemp cloth and amulets, skilled day wages (feature 400)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: four new money questions written from the four search passes in `passes/`. The work is one
write page session (four questions, the cap), one check-and-apply session, then the answer on EliAndrewC/diagram#5. No
code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s1-check.md"`. The passes are leads: each passage
  is read on its page before it is cited. Scanned or image-only pages (the Handa museum slide, the Tokugawa forestry
  booklet) are rendered and read on the image; their page images go to source-reader with `IMAGES=`.
- **What the record already holds.** Where 0250 (Kyoto and Saito wages), 0255 and 0256 (craftsmen's wages), 0261 (cotton
  by the tan; Beijing 1736 cloth), 0262 (Kazusa 1842 laborer) or 0263 (the Ming forge smiths; fletchers) give a figure,
  the question points at it and states its limit rather than repeating it (spec FR-001).
- **The wages.** Each price sits beside the craftsman's and the unskilled laborer's day wage of the same place and period
  where a source gives them; where none does, the question says that wage is SILENT and names the nearest, with its class,
  its place, its unit and its gap in years. A craftsman's wage is never shown as the unskilled wage. No price is converted
  between coins unless its source converts it (Gao's 800 cash to the tael, 1737, is Gao's).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the four questions (FR-001, FR-002)

Each is new and tagged `subject=money`, with no drawing page. Its level is `counts-and-measurements`.

| question | setting tag | what it covers |
|---|---|---|
| "What did fruit cost?" | `countryside,city` | the Kanto persimmon; Edo and castle-town silences; the Qing court's fruit prices, the Shengjing valuations, the Ming stolen-goods valuation |
| "What did salt cost?" | `countryside,city` | Kashimo 1763-74 beside its laborer; Otsukawa 1842; the hearsay inland ladder; the Qing field, official and retail prices and the stated markups |
| "What did hemp cloth and a shrine's amulets cost?" | `countryside,city` | the Etchu hemp lot; Beijing 1736 and 1615 hemp and ramie beside cotton; the Ise oshi's 1813 takings; the silences |
| "What did a skilled craftsman earn against a laborer?" | `city,countryside` | Osaka building trades; the Edo silence and the one-sided figures gathered; Saito's village pair; Zhili 1769 and the 1813 norm; tailors, smiths, fletchers |

Each question answers its acceptance scenario: every attested figure, every silence, each figure beside its wages. A figure
the project computes is labeled as the project's arithmetic.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds one line per question: "no code implements it - consumed by gm-assistant's money skill",
with the search.

## D3 - the answer (FR-004)

A comment on EliAndrewC/diagram#5 gives each question's fragment FILE, the checked verdict for every figure (or the page
that covers it), and what is still open.

## T - the order

1. The page sessions.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
