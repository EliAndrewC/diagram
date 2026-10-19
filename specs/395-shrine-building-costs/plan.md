# Implementation Plan: what a small forest shrine cost to build (feature 395)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: four new money questions written from the four search passes in `passes/`. Their findings were
posted on EliAndrewC/diagram#6 as interim on 2026-10-18. One write page session (four questions, the cap), one
check-and-apply session, then the answer on the issue. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s1-check.md"`. The passes are leads; each passage is
  read on its page before it is cited. A scanned PDF with no text layer (the two AIJ papers) is read by OCR, its quotes
  checked against the page image. The AIJ No. 420 paper's Kasuga figures serve two questions (sanctuary and roof): one
  question holds them, and the other points at it rather than repeating them.
- **The wages.** Each figure is set beside the craftsman's AND the unskilled laborer's day wage of the same place and period,
  where a source gives each, and for each one that no source matches the question says it is SILENT and names the nearest
  with its place and gap in years. Sources in hand: Tama 1749 (craftsman); Kumehara 1818 and 1830 (craftsman, sawyer,
  carter); Osaka 1620s (unskilled); Edo 1853-56 (craftsman); Kyoto 1802-4 (unskilled and craftsman, from 0250).

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the four questions (FR-001, FR-002)

Each is new, tagged `subject=money`, with no drawing page, and its level is `counts-and-measurements`.
- "What did a small shrine sanctuary cost to build?" (`setting=countryside`)
- "What did a shrine roof and its finish cost?" (`setting=countryside`): copper, cypress bark, shingle, and the
  persimmon-tannin finish
- "What did a torii, stonework and earthwork cost?" (`setting=countryside,city`)
- "What did a shrine's rites and furnishings cost?" (`setting=countryside,city`)

Each answers its acceptance scenario: every attested figure, every silence, and each figure beside its wage. Where a pass
computed a figure (per-day equivalents, the 600-1,100 craftsman-day reading of the 30-ryō contract), it is labeled as
the project's arithmetic.

## D2 - the implementation check (FR-003)

`implementation-check.md`, one line per question: "no code implements it - consumed by gm-assistant's money skill"
with the search.

## D3 - the answer (FR-004)

A comment on EliAndrewC/diagram#6: per question its fragment FILE, the checked verdict for every figure, and what is still
open (the interim comments were posted unchecked; this answer supersedes them; changed verdicts may be marked). A question
that points at another for shared figures (the Kasuga accounts) still gives its own verdict for each figure it relies on.

## T - the order

1. The page sessions.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
