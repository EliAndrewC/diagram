# Implementation Plan: charcoal, ordinary and fine white (feature 410, diagram#11)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-22

## Summary

A research-record feature: one new money question, 0279 "What did charcoal cost?", written from the two search passes
(`passes/`), each passage read on its page before it is cited; one write page session and one check-and-apply session,
then the reply on EliAndrewC/diagram#11. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-check.md"`.
- **Ōishi 1966** (key oishi-1966-tenpo13-bukka-kakiage, live host 406): read on rendered page images (pp. 86-87),
  passed to source-reader with `IMAGES=`.
- **Bochum Zhili** chapter .xls: cells read with xlrd; a row dump goes to the checks (a cell is a readable page, the GM).
- **The wages.** Each figure beside the craftsman's and laborer's day wage of the same place and period where a source
  gives them; otherwise SILENT with the nearest named (0250, 0255, 0257, 0275), its class, place, unit and gap.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question task is `research: physical` with its five boxes. XIII: `make record CHECK=1` and the
  record tests stay green. XVI: built as the spec's FRs.

## D1 - the question (FR-001, FR-002, FR-005)

0279, tagged as the money section's price questions are, in the order: Japan (black by the bale retail, the bale's
weight naming 0197, white and the Kumano/Hachiōji contrast, wholesale and carriage OPEN or SILENT, kiln output), then the
Qing comparison (Beijing 1615/1736, Zhili 1769, 武編). A figure the record holds only a nearest for is OPEN with the
nearest named and the search in the absence note. Under the 20,000-byte cap; a question that would pass it splits.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds 0279's line.

## D3 - the reply (FR-001, FR-004, FR-005)

A comment on #11: per figure the issue asks for, the fragment FILE, the verdict and what is still open; a combined price
named with what it covers.

## T - the order

1. The page sessions (s1 write; s2 check). 2. The implementation check. 3. The reply. 4. Report and land.
