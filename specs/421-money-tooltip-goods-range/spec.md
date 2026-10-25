# Feature 421: the money tooltip shows goods dollars as a range, central to high (diagram#17)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-25

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-24, "anything that gets filed, go ahead and work it"

The GM asked for what gm-assistant files here to be worked (his words, quoted above); gm-assistant relays that "the GM approved
goods dollars as a range (central to high)" (`request.md`), and a request it makes for him is approved by his asking (GM
2026-10-18: "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in
the future").

**Input**: `request.md` (gm-assistant's ask, verbatim).

## Why

gm-assistant's feature 223 made `goods_dollars` the central reading (the spending-weighted geometric mean) and added
`goods_dollars_high` (the arithmetic mean). Its toolkit page never shows one goods figure without the other; the record's hover
box (feature 413, `l7r/diagram/interactive/record/money.py`) shows only the central one.

## User Scenarios & Testing

1. A reader hovers a marked amount in the record and reads the goods value as a range from `goods_dollars` to
   `goods_dollars_high`: for 20 mon at kyoto-1745, "about $1.54-$3.32 in goods, $37.92 in wages, 3.8 sen in Rokugan".
2. An amount that is itself a range (two ends) reads its goods from the low end at `goods_dollars` to the high end at
   `goods_dollars_high`, one range, both ends at one precision as today.
3. An era row without `goods_dollars_high` (an older table) reads as today, one goods figure.

**Acceptance**:
1. The worked example above reads exactly so from the vendored table.
2. Wages and sen are unchanged.

## Requirements

- **FR-001**: The hover box's goods text is `goods_dollars` to `goods_dollars_high` times the amount, formatted as the existing
  dollar ranges are (one precision for both ends, joined by "-"); without `goods_dollars_high` it is one figure.
- **FR-002**: The module's own description of the hover box (`money.py`'s docstring, the one place that states what the box
  shows) says the goods figure is a range from the central to the high reading.

## Success Criteria

- **SC-001** (FR-001): the record money tests pin the worked example, an amount range and the no-high fallback; `make done`
  is green at the landing.
- **SC-002** (FR-002): `make record CHECK=1` is clean and the docstring names the range.
