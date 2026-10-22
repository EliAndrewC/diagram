# Implementation Plan: how far goods traveled, and what distance did to their price (feature 411, diagram#12)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-22

## Summary

A research-record feature: four new money questions (A water against land; B how far goods went; C tea; D a named good far
from home), written from the four search passes (`passes/`), each passage read on its page before it is cited; two write
page sessions (A+B, then C+D, each under the ten-new-key cap) and one check-and-apply session, then the reply on
EliAndrewC/diagram#12. No code, map or canon change.

## Technical Context

- **The record.** `make page-session BRIEF="briefs/s1-write.md briefs/s2-write.md briefs/s3-check.md"`.
- **Bochum Jiangsu** transport and wage .xls: cells read with xlrd; a row dump goes to the checks.
- **PDFs** the reader cannot fetch (Cheng LSE WP 371, Kibe, Kato, Kobe City Archives): curl into an empty directory,
  pdftotext or rendered page images (`IMAGES=`).
- **The wages.** Each figure beside the craftsman's and laborer's day wage of the same place and period where a source
  gives them; otherwise SILENT with the nearest named (0250, 0255, 0260, 0275, 0278), its class, place, unit and gap.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the
  record tests stay green. XVI: built as the spec's FRs.

## D1 - questions A and B (FR-001, FR-002, FR-005, FR-006)

A "What did carrying goods cost by water, against by land?" and B "How far did goods travel before carriage priced them
out?", new, tagged as the money section's price questions are, China first, Japan beside it. A: Jiangsu's official boat
and porter rates with their wages; the Qing grain freight of 清史稿 卷122; the ratio as Cheng 2024 and Qiu Jun state it, and
as the official rates give it (this project's arithmetic, labeled); Japan's sake-ship freight standard and Hagi's freight
shares; 0260's land and Hunan rates named, not repeated. B: the Shiji proverb with Xu Tan's reading; Skinner's market
radius; the Ming surcharge by distance; Qiu Jun's Han and Tang extremes; the distance at which carriage equaled a grain
price SILENT in the sources, this project's arithmetic from Cheng's official rates beside it, labeled; firewood, charcoal
and salt hauls (0273 named). Each verdict one of the four; a nearest is SILENT, the nearest named under what is open.

## D2 - questions C and D (FR-001, FR-002, FR-005, FR-006)

C "How did tea travel, and what did it cost at the end of the road?": Rockhill's Ya-chou porters and price ladder; the
Ming tea-horse rates; Parkes's Kalgan-Kyakhta camels; the Uji tea-jar procession (its prices SILENT). D "What did a famous
good cost far from where it was made?": Ball's Wuyi Congou at origin, at Canton and in London with the region's wages;
Nada sake's Edo prices and freight (no brewery price the same year: ATTESTED ONLY FOR); 0279 and 0262 named.

## D3 - the implementation check (FR-003)

`implementation-check.md` holds each new question's line.

## D4 - the reply (FR-001, FR-004, FR-005)

A comment on #12: per figure the issue asks for, the fragment FILE, the verdict and what is still open; a combined figure
or ratio named with what it covers and labeled as this project's arithmetic where it is.

## T - the order

1. The page sessions (s1, s2 write; s3 check). 2. The implementation check. 3. The reply. 4. Report and land.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
<!-- plan-archive: T03 to T03 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
<!-- plan-archive: T04 to T04 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
<!-- plan-archive: T05 to T05 moved to plan-done.md, 2026-10-22 (feature 375 FR-044) -->
