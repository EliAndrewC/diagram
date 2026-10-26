# Implementation Plan: the single-page record's opening (feature 425)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-26

## Summary

`site._single` writes `contents.load_opening(self.record_dir)` under its title; its pointer sentence becomes "Every question,
every note and every source on one page. The same record, a page per question: the contents." A record test pins it.

## Technical Context

- `l7r/diagram/interactive/record/site.py` (`_single`); `tests/interactive/test_record_site.py`.
- A GATED landing (an engine path): `make land` runs `make done`.

## Performance bookends

N/A: one string at the record's build; no generator change.

## Constitution Check

- XIII: the record tests and `make done` green. XVI: built as FR-001 and FR-002.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
