# Tasks - feature 290, the perceptual label order

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D5).

- [x] T01 The order and the fallback's sides, with unit tests (D1, D2; FR-001, FR-002, SC-001)
      research: rendering
      verify: DONE. standard.POSITIONS is PerceptPPO's eight in order (above, below, right, upper right, lower right, left, upper left, lower left); the fallback walks above, below, right, left; tests/labels/test_placer.py places a post on each chosen seat in turn and gets the next in the order; 64 label tests pass
- [x] T02 The record (D3; FR-003, SC-002)
      research: rendering
      verify: DONE. research/presentation 040 'Which side': the maps follow the readers' order, cited to bobak-cmolik-cadik-2024 (five notes, one new on the 'slightly' places); the deviation's notes removed; the Mapbox sentence made order-neutral after the style spec showed 'top' puts a label below its point; quote-check, record-format and source-applicability run, their edits applied; quote-verbatim VERBATIM on every note
- [ ] T03 The maps regenerated; make done; push (D4, D5; FR-004, SC-003)
      research: rendering
