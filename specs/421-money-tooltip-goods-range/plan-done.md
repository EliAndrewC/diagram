# 421-money-tooltip-goods-range - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-25 -->
## T01 - the goods range in the hover box (FR-001, FR-002)

### T01 Approach (checklist part A)

1. **The goal, in the world.** A reader hovering a marked amount sees goods as a range, central to high, as the toolkit shows.
2. **The constraints.** The worked example exactly (Acceptance 1); wages and sen unchanged (Acceptance 2); no single-figure
   path (FR-001).
3. **Where each comes from.** O: `request.md`; the spec's FR-001.
4. **Do they describe the world here?** Yes; the table is gm-assistant's and carries the field on every unit.
5. **The order.** Code and tests together, then the record build, then the gated landing.
6. **The exits.** None: a missing `goods_dollars_high` fails the build as any missing key does.
7. **The search smell.** None.
8. **The budget.** Minutes of code; one `make done`.
9. **Done, measured.** `make test-file FILE=tests/interactive/test_record_money.py` green; `make record CHECK=1` clean; `make
   done` green at the landing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** The goods ends are (first amount end x `goods_dollars`, last amount end x `goods_dollars_high`), formatted by
  `_dollars` (one precision from the larger end, joined by "-"). Rendering: none.
- **D2** The docstring's "goods dollars (what it bought)" becomes the range from the central (geometric) to the high
  (arithmetic) reading. Rendering: none.

<!-- plan-archive: archived 2026-10-25 -->
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
