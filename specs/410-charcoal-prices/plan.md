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

0279, tagged as the money section's price questions are, in the order: Japan - charcoal by the bale (the 1842 ordered
price by grade, retail/wholesale and black/white left open unless the page says so), the bale's weight (naming 0197 and
0199's Iburi weights; the record has no Edo-period one), retail by small measure, white and the Kumano/Hachiōji contrast,
wholesale, carriage, kiln output, burner-days and yield - then the Qing comparison (Beijing 1615/1736, Zhili 1769, 武編).
Each verdict is one of the four of `research/money-requests.md`; a figure the record holds only a nearest for is SILENT,
the nearest named under what is still open and the search in the absence note. Under the 20,000-byte cap; a question that
would pass it splits.

## D2 - the implementation check (FR-003)

`implementation-check.md` holds 0279's line.

## D3 - the reply (FR-001, FR-004, FR-005)

A comment on #11: per figure the issue asks for, the fragment FILE, the verdict and what is still open; a combined price
named with what it covers.

## T - the order

1. The page sessions (s1 write; s2 check). 2. The implementation check. 3. The reply. 4. Report and land.

### T01 Approach

1. Goal: issue #11's figures written into a new question, 0279 What did charcoal cost?, each with its verdict and file.
2. Constraints: FR-005 (a nearest figure is not an answer); each figure beside its place's craftsman and laborer day wage or a named nearest; the four verdicts of money-requests.md; the 20,000-byte cap; the record checks.
3. Sources: the request G (#11, the GM 2026-10-22); the passes' leads O, each read on its page before citing; the record rules G (constitution XII).
4. Holds: as written; a third check round on 0279 (session 2's leftovers) went to the round arbiter first (ask:410-0279-round3).
5. Order: write session (brief s1), then the check session (s2), then the leftovers' round.
6. Exits: (e) conform.
7. No search loop: the passes ran once; leads not followed are named in the handoff and the absence note.
8. Budget: one write session, one check session, one capped leftovers round.
9. Done: handoff written; make record-owed 0 unanswered.
10. n/a.
11. n/a.

### T02 Approach

1. Goal: 0279 closed with its no-code line.
2. Constraints: make impl-check F=410.
3. Sources: G (CLAUDE.md, features 389 and 285).
4. Holds as written.
5. Order: after the checks.
6. Exits: (e) conform.
7. n/a.
8. One run.
9. Done: make impl-check F=410 reports nothing missing.
10. n/a.
11. n/a.

### T03 Approach

1. Goal: the reply on #11, per figure the file, the verdict and what is open, combined prices named with what they cover.
2. Constraints: FR-001, FR-004, FR-005.
3. Sources: the handoff and s2-checks.md O; the page as checked O.
4. Holds: day counts and ratios are this record's arithmetic, labeled in the reply.
5. Order: after the checks and impl-check.
6. Exits: (e) conform.
7. n/a.
8. One comment.
9. Done: the reply posted.
10. n/a.
11. n/a.

### T04 Approach

1. Goal: the feature lands on main with its report.
2. Constraints: the review gate, the ledger, the record tests before the push.
3. Sources: all G (CLAUDE.md's stop-work procedure).
4. Holds as written.
5. Order: report, land, then watch #11 until gm-assistant closes it.
6. Exits: (e) conform.
7. n/a.
8. One landing.
9. Done: origin/main carries 410.
10. n/a.
11. n/a.
