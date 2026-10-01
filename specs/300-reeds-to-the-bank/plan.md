# Plan - feature 300, reeds to the bank

**Spec**: [spec.md](spec.md) - **Research**: [research.md](research.md)

## Design

- **A.** `marsh()` (`land/wet.py`): the reeds' bare ground files the watercourses (keep-out slot 3) at their drawn width alone -
  the query's extra for slot 3 is 0 where it was `2 + pad`. The pond's slots (4-5) are unchanged, so its embankment stays bare.
- **B.** `flush_covers` (`settlement/finish.py`): when any marsh is drawn, the union of every watercourse (`_watercourse_segs(0.0)`)
  buffered by its half-width plus `BANK_FT` is the bank ground; each marsh shape's part in it is cut out and drawn with the
  `reed-bank` tile (`land/tiles.py`: reed tufts at three times the marsh's density, a darker green, the base repeat) in the
  marsh's own slot and class. The scrub is untouched.
- **C.** The outline (FR-003) is judged by eye on Inashiro after B and recorded in research R1: not added.
- **D.** Record: vegetation 125's drawing paragraph gains the bank; `record-format` on it. Tests: the unit test of SC-001
  (`tests/settlement/test_outline_299.py`), the existing marsh tests unchanged in what they assert.

## Decisions (for the plan review)

| id | decision | class |
|---|---|---|
| D1 | Slot 3 at drawn width; the pond's slots kept | FR-001, FR-004 |
| D2 | The bank band 6 ft, three times the density, darker green, in the marsh's slot | FR-002, calibration in R1 |
| D3 | No outline added (the stream reads clearly) | FR-003, judged in R1 |
