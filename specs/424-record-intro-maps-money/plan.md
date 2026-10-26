# Implementation Plan: the record's opening (feature 424)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

`research/contents.json` gains an `opening` (HTML); `contents.load_opening` reads it; `site._home` writes it under the title,
before the whole-record link. A record test pins the order and both links; a contents test pins the reader.

## Technical Context

- `l7r/diagram/interactive/record/contents.py` (`load_opening`), `record/site.py` (`_home`), `research/contents.json`;
  `tests/interactive/test_record_site.py`, `tests/interactive/test_record_questions.py`.
- A GATED landing (an engine path): `make land` runs `make done`.

## Performance bookends

N/A: one string at the record's build; no generator change.

## Constitution Check

- XIII: the record tests and `make done` green. XVI: built as FR-001 and FR-002. The record's house style (no "people" for
  commoners; American spelling; hyphens) holds in the opening's words.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
