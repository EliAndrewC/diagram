# Implementation Plan: what an empty charcoal bale cost (feature 453, diagram#23)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-11-24

## Summary

A research-record feature answering the issue's one question from one search pass (`passes/a-bales.md`). One write session (and its continuations under the key cap) and one
check-and-apply session in this clone (`/diagram/.clones/diagram-research`), then the reply on #23. No code, map or canon change.

## Technical Context

- **The pass is leads, not citations**: the write session reads every passage on its page before citing it, through `make archive-find` and
  `make source-pages`.
- **Machine-read manuscripts**: the Edo ward records (NDL 2548494, 2587102, 2547651, 2587455, 2547702, 2548603) were read through the NDL's
  machine reading; two frames were checked against the scans. A passage is cited only once read on its page image, and given to the checks
  with `IMAGES=`.
- **The write cap**: one new question and a pointer; at most ten new registry keys a write session; the eleventh sends the rest to a
  continuation write session (`make reserve`), and no finding is dropped for the cap.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question task is `research: physical` with its five boxes. XIII: `make record CHECK=1` stays green. XVI: built as the
  spec's FRs.

## D1 - the empty bale (FR-001, FR-002, FR-005, FR-006, FR-007)

A new money question, its title asking what an empty charcoal bale cost and who wove it. Japan first: the price (SILENT for the charcoal
bale, the Edo empty bales of unstated kind beside their day wages as the nearest); who made them and of what; how long one took; whether
they were traded empty; the share of a full bale; the neighbors (mats, matting, rope, earth bags; empty rice bales, whose 1859 order names no price, and sandals SILENT, named with what is
still open), each with its wage where found. Then
China: the Beijing baskets of 1736 and the Ming's silence. 0279, 0199, 0197, 0312, 0332 and 0283 named by file where they bear; a one-line pointer to
the new question from 0279 where it speaks of bales.

## D2 - the implementation check, the reply and the report (FR-001, FR-003, FR-004)

`implementation-check.md` holds the new question's line (`no code implements it`, with the search). The reply on #23 gives, part by part
and figure by figure, the fragment file and the verdict, and what is still open. Anything for the GM goes through `escalation-check` first.
