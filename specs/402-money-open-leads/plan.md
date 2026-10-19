# Implementation Plan: the money answers' open leads, written in (feature 402)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-19

## Summary

A research-record feature: four existing money questions (0273, 0275, 0276, 0277) gain the figures four search passes found
(`passes/`), in place of verdicts that said SILENT. One write page session, one check-and-apply session, then a note to
the asker. No code, map or canon change.

## Technical Context

- **Morisada.** 類聚近世風俗志: full-text search for 上 (pid 991466) and the 1934 edition (pid 1444386); 下 (pid 991467)
  page by page in NDL's viewer, or through 1444386 once shown whole; "unread lead" if 下 cannot be searched. Its IIIF and
  lab routes refuse all three pids.
- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s1-check.md"`. The passes are leads: each passage is
  read on its page before it is cited. The NDL scans (諸問屋再興調 十之二, pid 2548694; 類聚近世風俗志 上, pid 991466; 読史備要,
  pid 1915733) are read on their page images, which go to source-reader with `IMAGES=`. Oishi's table (glim-re repository
  PDF) has a garbled text layer: its rows are read on the rendered page images.
- **The wages.** Each new figure sits beside the craftsman's and the unskilled laborer's day wage of the same place and
  period where a source gives them; where none does, the question says that wage is SILENT and names the nearest, with its
  class, its place, its unit and its gap in years.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs.

## D1 - the four questions (FR-001, FR-002)

| question | what changes |
|---|---|
| 0276 "What did a kitchen knife cost?" | the wage beside Mimasaka 1665: Kyoto carpenter 1653 (Hirai 2007), the 1656 bath account (arithmetic), Osaka laborers 1620s (Kitano); Mimasaka SILENT after 藩法集 岡山藩 is read or named; Inui named not readable; the sharpener: Morisada's 磨師 entry (the trade, no fee) and Uwajima 1662 (swords only) |
| 0275 "What did a skilled craftsman earn against a laborer?" | an Edo pair from 類聚近世風俗志 (searched in NDL's viewer and full-text search), or SILENT naming the search |
| 0277 "What was copper coin worth in silver?" | the Edo rate: Oishi's yearly table 1781-1842 (low and high mon per ryo), decade summaries as arithmetic, Edo-ness the record's reading; 1842-52 blank; the 1850s SILENT; the restricted 両替年代記 books and 新保 1978 named; 読史備要's scattered 1780s rows if read |
| 0273 "What did salt cost?" | Edo, Ako salt: the brokers' 1791 price, 9-9.5 bales per ryo, the bale's measure as the page reads; per sho arithmetic; Edo retail and 1800-1850s from the Morisada search or SILENT naming it; the wholesalers' commission if read on the image |

The anchor rows of 0277 and the wage sections of 0273 and 0276 that the new figures touch are revised to match; nothing
else in the three pages changes.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds one line per changed question: "no code implements it - consumed by gm-assistant's money
skill", with the search.

## D3 - the note to the asker (FR-004)

A new issue on EliAndrewC/diagram (gm-assistant reads the repository's issues), or a comment on #8, naming the changed
fragment FILES, each verdict that changed from the #5 and #8 answers, the leads closed as not readable, and what is still
open (with the other answers' leads that feature 403 is to take).

## T - the order

1. The page sessions.
2. The implementation check.
3. The note.
4. Report and land, by the direct route.
