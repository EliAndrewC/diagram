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
- **The wages.** Each question sets its figures beside the day wage of the same district and period where a source gives
  one (Tama 1749; Kumehara 1818 and 1830; Osaka 1620s; Edo 1853-56; Kyoto 1802-4 from 0250), and says so where none
  matches.

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
- "What did a shrine roof cost, in copper, bark or shingle?" (`setting=countryside`)
- "What did a torii, stonework and earthwork cost?" (`setting=countryside,city`)
- "What did a shrine's rites and furnishings cost?" (`setting=countryside,city`)

Each answers its acceptance scenario: every attested figure, every silence, and each figure beside its wage. Where a pass
computed a figure (per-day equivalents, the 600-1,100 craftsman-day reading of the 30-ryō contract), it is labeled as
the project's arithmetic.

## D2 - the implementation check (FR-003)

`implementation-check.md`, one line per question: "no code implements it - consumed by gm-assistant's money skill"
with the search.

## D3 - the answer (FR-004)

A comment on EliAndrewC/diagram#6 with the fragment files, the verdicts, and what is still open. The interim findings
stand; the answer says only what changed in checking.

## T - the order

1. The page sessions.
2. The implementation check.
3. The answer.
4. Report and land, by the direct route.
