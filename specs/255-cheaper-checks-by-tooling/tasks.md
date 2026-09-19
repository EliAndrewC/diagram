# Tasks - 255 cheaper checks by tooling

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing physical.

- [x] T01 `make source-entries` and `source-applicability`'s step 0; two seeded cases scored; ADOPTED or NOT (FR-002)
      research: rendering
      verify: DONE. NOT ADOPTED - three candidate runs (0.70-0.80) each missed a recorded limit the same-setting control (2.78) hit; contract as it was, script removed; research R1
- [x] T02 scoped text for `record-format` (`--text`) and `quote-check`; two seeded cases each scored (FR-003)
      research: rendering
      verify: DONE. NOT ADOPTED for either agent - record-format missed 3 of 6 and 3 of 3, quote-check under-called fn-95 and cost 3.30 against 2.98; research R2
- [x] T03 the batching line, tested on the twin's two recorded rounds; adopted for the seven contracts or not (FR-004)
      research: rendering
      verify: DONE. ADOPTED in the seven contracts - both rounds hit, 13 turns and 1.27 against the control's 19 and 1.66; research R3
- [x] T04 `make source-pages` and `source-reader`'s grep-then-read contract; three cases scored on both axes (FR-006)
      research: rendering
      verify: DONE. misses nothing (one recorded false CONTRADICTED corrected, the width passage found) and costs 2.81 against 2.21 - the agent left as it was, the decision is the GM's; research R4
- [x] T05 the fixed-context probes recorded; the memory index and unused tools trimmed and re-probed (FR-007)
      research: rendering
      verify: DONE. ten probes recorded; the memory index trimmed (209 tokens on a re-probe), no tool trim because removing Grep beside Bash saves 0; research R5
- [x] T06 `make review-facts` and the shorter `settlement-review` contract; two seeded runs scored; the ledger row (FR-005)
      research: rendering
      verify: DONE. NOT ADOPTED - one of four recorded errors hit over two seeded reviews, 81 turns both ways, weight 8.64 to 9.31; contract restored, script removed, ledger row written; research R6
- [x] T07 the record: docs, make-targets page, NOT ADOPTED candidates written up (FR-008)
      research: rendering
      verify: DONE. docs/efficiency-tooling.md row, docs/make-targets.html regenerated (source-pages), the ledger row, every NOT ADOPTED candidate written up in research.md
- [x] T08 `make hooks-test` and `make quick` green; land DIRECT
      research: rendering
      verify: DONE. make quick and make hooks-test green 2026-09-19; nothing under l7r/ or pool/ changed
