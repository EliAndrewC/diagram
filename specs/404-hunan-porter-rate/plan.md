# Implementation Plan: the Hunan edition's porter and boat rates (feature 404)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: 0260 gains the Hunan edition's porter and boat rates and, if its scan gives them, the same
districts' wages; the Zhili rows stay out with their reason. One write page session, one check-and-apply session, a note
on EliAndrewC/diagram#9. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-check.md"`.
- **The scan.** Wikimedia Commons, `File:SSID-11354707_欽定物料價值則例_第1卷.pdf` (no text layer): downloaded and its pages
  rendered (`pdftoppm`), each row read on the image; the images go to source-reader with `IMAGES=`. The wage rows, if any,
  are found by rendering the volume's 長沙/善化 pages around pp. 38-39.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question task is `research: physical` with its five boxes. XIII: `make record CHECK=1` and the
  record tests stay green. XVI: built as the spec's FRs.

## D1 - 0260 (FR-001, FR-002)

The Hunan porter (80 jin, per li, 0.003 tael) and boat (100 jin, per 10 li, 0.002 tael) rows of 長沙/善化, quoted with
their note, ATTESTED ONLY FOR official building-work reimbursement in Hunan, dated as the edition states; the same
volume's craftsman's and laborer's day wages for those districts beside them if the scan gives them, otherwise SILENT
with the nearest named; a porter's 100 li in days as the project's arithmetic. The Zhili rows stay out: the absence note says no public scan
of the original was found (and where it was searched), quotes the Bochum ch.13 rows its claim rests on (青縣 28b against
29a), says the Hunan original writes its unit row by row, and chooses no unit for Zhili. The pack animal stays without an
official rate (Hunan's rows are two items; Zhili's left out). Moll-Murata, Song and Vogel 2005 and the HathiTrust search
are retried, or named with the failure and both dates; the Jiangsu edition and Hunan 卷2-8 are named as open.

## D2 - the implementation check (FR-003)

One "no code implements it" line for 0260.

## D3 - the note (FR-004)

A comment on EliAndrewC/diagram#9.

## T - the order

1. The page sessions. 2. The implementation check. 3. The note. 4. Report and land.
