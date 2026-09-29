# Tasks - feature 289, adjacent before diagonal

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5).

- [x] T01 The order and the fallback's sides, with unit tests (D1, D2, D5; FR-001, FR-002, SC-001)
      research: rendering
      verify: DONE. standard.POSITIONS: above, below, left, right, then upper right, upper left, lower right, lower left, above slightly right, below slightly left; the fallback walks above, below, left, right; tests/labels/test_placer.py blocks the four adjacent seats in turn (SC-001) and the placer's other tests pass with only position names changed; 64 label tests pass
- [x] T02 The deviation in the record (D3; FR-003)
      research: rendering
      verify: DONE. research/presentation 040 'Which side': the deviation (grounds note), the textbooks' order, an absence note for small drawn objects, the other orders cited (spektrum-schriftplatzierung, bobak-cmolik-cadik-2024 x4, mapbox-variable-label-placement); quote-verbatim 9/9 VERBATIM; quote-check, record-format and source-applicability run and their edits applied
- [ ] T03 The maps regenerated and measured; make done; push (D4, D5; FR-004, SC-002, SC-003)
      research: rendering
