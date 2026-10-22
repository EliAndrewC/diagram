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

### T01 Approach

1. Goal: issue #12's questions 1 and 2 written into 0280 (freight by water against by land) and 0281 (how far goods traveled), each figure with its verdict and file.
2. Constraints: FR-005 (a nearest figure is not an answer); FR-006 (each figure beside its place's craftsman and laborer day wage, or a named nearest); the four verdicts of money-requests.md; the ten-key write cap; the 20,000-byte cap; the record checks.
3. Sources: the request G (#12, the GM 2026-10-22); the passes' leads O, each read on its page before citing; the record rules G (constitution XII).
4. Holds: as written; the ten-key cap sent the Edo five-ri rule to a continuation session, which wrote it into 0281.
5. Order: write session s1 (and its continuation), then the check session s3.
6. Exits: (e) conform.
7. No search loop: the passes ran once; leads not followed are named in the handoff and the absence notes.
8. Budget: one write session and its continuation, one check session of at most two rounds a check (three for record-format on 0282).
9. Done: handoff written; make record-owed 0 unanswered.
10. n/a.
11. n/a.

### T02 Approach

1. Goal: issue #12's questions 3 and 4 written into 0282 (how tea traveled) and 0283 (a famous good far from home), each figure with its verdict and file.
2. Constraints: as T01.
3. Sources: as T01.
4. Holds: as written; Shizuoka tea and Tosa charcoal searched (spec Assumptions), Shizuoka SILENT, Tosa ATTESTED ONLY FOR Chikuzen 1836.
5. Order: write session s2, then the check session s3.
6. Exits: (e) conform.
7. No search loop, as T01.
8. Budget: one write session, the shared check session.
9. Done: handoff written; make record-owed 0 unanswered.
10. n/a.
11. n/a.

### T03 Approach

1. Goal: 0280-0283 closed with their no-code lines.
2. Constraints: make impl-check F=411.
3. Sources: G (CLAUDE.md, features 389 and 378).
4. Holds as written.
5. Order: after the checks.
6. Exits: (e) conform.
7. n/a.
8. One run.
9. Done: make impl-check F=411 reports nothing missing.
10. n/a.
11. n/a.

### T04 Approach

1. Goal: the reply on #12, per figure the file, the verdict and what is open, arithmetic labeled, every mode and good the issue names given a verdict.
2. Constraints: FR-001, FR-004, FR-005.
3. Sources: the handoff and s3-checks.md O; the pages as checked O.
4. Holds: ratios, day counts and parity distances are this record's arithmetic, labeled in the reply.
5. Order: after the checks and impl-check.
6. Exits: (e) conform.
7. n/a.
8. One comment.
9. Done: the reply posted (issuecomment-6341257028).
10. n/a.
11. n/a.

### T05 Approach

1. Goal: the feature lands on main with its report.
2. Constraints: the review gate, the ledger, the record tests before the push.
3. Sources: all G (CLAUDE.md's stop-work procedure).
4. Holds as written.
5. Order: report, land, then watch #12 until gm-assistant closes it.
6. Exits: (e) conform.
7. n/a.
8. One landing.
9. Done: origin/main carries 411.
10. n/a.
11. n/a.
