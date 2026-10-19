# Implementation Plan: the rest of the shrine builder's options (feature 398)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: four new money questions written from the four search passes in `passes/`. Their findings
were posted on EliAndrewC/diagram#7 as interim. The work is one write page session (four questions, the cap), one
check-and-apply session, then the answer on the issue. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s1-check.md"`. The passes are leads: each passage
  is read on its page before it is cited. The Kawakami AIJ No. 435 paper is a scanned PDF already archived; its notes
  31-36 are read on the page images (the passes rendered them), which go into source-reader bundles with `IMAGES=`.
- **What #6 already covers.** Where 0255-0258 give an item (relief panels, the cover-shed inside the Mitake repair, the
  worship hall, the copper roof, the great stone torii, the enshrinement cost share), the question points at the page
  and states its limit rather than repeating it (request.md).
- **The wages.** Each figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and period
  where a source gives them. Where none does, the question says that wage is SILENT and names the nearest wage, with its
  class (unskilled or craftsman), its place, its unit and its gap in years. A craftsman's wage is never shown as the
  unskilled wage. Wages in hand:
  - Kumehara 1830 carpenter (0255);
  - Tama 1749 (0255);
  - the Edo carpenter 1804-60 (0256);
  - Kyoto 1802-04 unskilled (0250);
  - the Jiangsu 1769 construction norms (`allen-2009-china-wages`).

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
| "What did a shrine's other sanctuaries, halls and finishes cost?" | `countryside` | kasuga and shinmei forms, the hokora, the cover-shed, the pavilion and offering hall, timber, thatch and shingle, paint and lacquer, relief panels, beam-end carving, transoms |
| "What did a shrine's stonework cost?" | `countryside` | the small torii, lanterns, the mason's day, the stairway and plinth, komainu and foxes, the basin, the stele, the gorinto, the coffer |
| "What did a shrine's metal furnishings cost?" | `countryside,city` | the mirror, the gong, hanging lanterns, the reliquary, the offering chest and lock, the lacquered chest, the copper floor, Qing copper ware |
| "What did rites for the dead and a shrine's dedication cost?" | `countryside,city` | the night enshrinement, the goryo festival, eitai kuyo, a portion to a mountain temple, washing bones, a calligrapher's plaque fee |

Each question answers its acceptance scenario: every figure, every silence, each "covered by" with its limit, and each
figure beside its wages. A figure the project computes is labeled as the project's arithmetic.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds one line per question: "no code implements it - consumed by gm-assistant's money skill",
with the search.

## D3 - the answer (FR-004)

A comment on EliAndrewC/diagram#7 gives:
- each question's fragment FILE;
- the checked verdict for every figure, or the page that covers it;
- what is still open.

It supersedes the interim comment.

## T - the order

1. The page sessions.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
