# Implementation Plan: the money tooltip's goods range (feature 421, diagram#17)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-25

## Summary

`money.box()` writes the goods text from `goods_dollars` to `goods_dollars_high` times the amount, through the existing
`_dollars` range formatter; the docstring says so; the record money tests pin the worked example and an amount range, and their
fixtures gain `goods_dollars_high`.

## Technical Context

- `l7r/diagram/interactive/record/money.py` (`box`, the module docstring); `tests/interactive/test_record_money.py`.
- A GATED landing (an engine path): `make land` runs `make done`.

## Performance bookends

N/A: a string at the record's build; no generator change.

## Constitution Check

- XIII: the record money tests and `make done` green. XVI: built as FR-001 and FR-002. Research: the module's claim stays
  `NONE: presentation of gm-assistant's conversion table`.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
<!-- plan-archive: T02 to T02 moved to plan-done.md, 2026-10-25 (feature 375 FR-044) -->
