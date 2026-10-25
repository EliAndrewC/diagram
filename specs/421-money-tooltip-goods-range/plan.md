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
## T02 - the reply and the report

### T02 Approach (checklist part A)

1. **The goal, in the world.** gm-assistant can verify the tooltip.
2. **The constraints.** The reply names the commit and what to look at.
3. **Where each comes from.** O: `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** After T01 lands.
6. **The exits.** None.
7. **The search smell.** None.
8. **The budget.** Minutes.
9. **Done, measured.** The comment posted; `make feature-report F=421 WRITE=1`.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T02 Decisions

- **D3** One comment on #17. Rendering: none.
