# Implementation Plan: the shrine builder's small lines (feature 408, diagram#10)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-21

## Summary

A research-record feature: five existing money questions gain the figures four search passes found (`passes/`), or name
in their absence notes the searches that found nothing. Two write page sessions (the four-question cap), one
check-and-apply session, then the reply on EliAndrewC/diagram#10. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-write.md briefs/s3-check.md"`. The passes are
  leads: each passage is read on its page before it is cited.
- **Morisada.** 類聚近世風俗志 上 (pid 991466) by feature 402's `measure/ft.sh` and `shot.py`; each quotation read on a
  viewer screenshot.
- **Bochum.** The Yunnan and Gansu chapter spreadsheets (xlrd) and their province pages; a cell of a public spreadsheet
  counts as a readable page (the GM, 407).
- **PDFs the reader cannot open** (Murata 1986, the Nakai paper, Yuasa 1986/1991): downloaded, read with pdftotext or as
  rendered page images, the images passed to source-reader with `IMAGES=`.
- **The wages.** Each new figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and
  period where a source gives them; otherwise the wage is SILENT, the nearest named with its class, place, unit and gap.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the questions, by write session (FR-001, FR-002, FR-005)

| session | questions | what changes |
|---|---|---|
| s1 | 0257, 0260 | group 1 (grounds: sweeping and earthwork, Kawachi 1704; Qing hedge and bridge norms; SILENTs named) into 0257; group 4 (Qing stone by cart and porters, Yunnan and Gansu 1769, the 會典則例 卷130 cart rate) into 0260; Japan's two lines (a cart hire near a road; porters into trailless forest) reported OPEN, the search in 0260's absence note, with 0257's 1620 hill stone and 0260's stage fares named as nearest figures, not answers; 0257's "carrying stone a ri" points to 0260 |
| s2 | 0258, 0268, 0271 | group 2 (carvers' and sawyers' day rates, Tanba and Tango; Morisada's signboards; the 1902 Yunnan stele; SILENTs) into 0258, sawing into 0268; group 3 (the Sannohe head mounds, the ground rite, unveilings, Doolittle's coffin money; SILENTs) into 0271, the ground rite into 0258; the mortuary hall and water pavilion reported OPEN - the pass searched 霊屋, 御霊屋, 位牌堂, 手水舎 and 水屋 and found no direct figure - with 0268's worship hall and roofs, 0255's Mitake covering house and 0271's 1803 hall named as nearest figures, not answers; 0268's absence note names that search |

Items an earlier fragment already ANSWERS are not rewritten (FR-005); a line whose page holds only a nearest figure is
reported OPEN with the nearest named, and its search goes into the question's absence note: the spec's "Already
answered" line in each group lists answered items only, and the reply names the fragment and the estimate it answers.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds one line per changed question.

## D3 - the reply (FR-001, FR-004, FR-005)

A comment on #10: per line of the issue, (S) lines first in each group, the fragment FILE, the verdict, and what is still
open; where a source prices several lines together, that combined figure and what it covers are given IN ADDITION to
each line's own verdict, never in place of it.

## T - the order

1. The page sessions (s1, s2 write; s3 check).
2. The implementation check.
3. The reply.
4. Report and land, by the direct route.
