# Tasks - feature 273, hamlet graveyards

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D6).

- [x] T01 The record: 540 (where a hamlet's dead lie), the GM's ruling in 210 and 530, 210's hamlet cell and rule; checks applied (FR-001, FR-002, FR-004)
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. religion-and-death 540 (a knob: own ground or the village's), the GM's ruling in 210 and 530, 210's hamlet cell and rule; source-reader READ (4, 2 narrowed), quote-check twice and record-format twice applied, source-applicability on the five new keys applied; glossary Wakasa, Kikaijima, temple registration (Kyushu and Huizhou defined by the other clones)
- [x] T02 The hamlet generator's burial stage and its knob (D1-D3; FR-003): `hamletgen/burial.py`, wired into STAGES before the web, red-first tests of the seat, the size and the class; `dev/placement.md`
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. hamletgen/burial.py stage_burial and its knob hamlet_burial; the shared edge seat (settlement/civic_grounds/edge_seat.py: nearest first, outside the houses' hull, 60 ft, 180's water bands); the box sized for the drawn blob (BLOB_FILL 0.58, measured); crowns kept off the ground to its markers; the BurialGround class; tests red-first in tests/hamletgen/test_burial.py; dev/placement.md and the package index
- [x] T03 The village's cremation ground in `_roll_civic` with 530's whole rule (D4, D4b; FR-003) and a roll test that no hamlet from either generator draws a cremation ground, a shrine or a headman's house
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE. _roll_cremation in the roller's village tier: 530's cremation_seat knob, the edge seat (120 ft, 30 px water, off the approach, within ~650 ft), six jizo (cremation_ground(jizo=True)); roll tests incl. no hamlet from either generator draws a cremation ground, shrine or headman's house
- [x] T04 The five pool hamlets re-rolled; a settlement-review per moved map; ledger rows (D6; FR-005)
      research: rendering
      verify: DONE. DONE. settlement-review: rounds 1-3 on inashiro, kashikawa, kuwabata (round 3 PASS), rounds 1-2 on sawada, mizuguchi (PASS); every finding verified in specs/273-hamlet-graveyards/measurements.json or accepted; ledger rows
- [ ] T05 `make done`; `scripts/sync-with-main.sh done`; relink 271's `RELINK 273` comment in 400 if it is on main
      research: rendering

- [x] T06 The village's burial ground (D5): built here if 269's 270 and 280 are on main when T01-T05 are done, or ticked by claiming the follow-up feature that carries the design
      research: physical
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited  - [x] quote-check confirmed  - [x] source-applicability confirmed
      verify: DONE. DONE by the plan's second branch: 269's 270 and 280 are not on main, so the village's burial ground is claimed as feature 275 (specs/275-village-burial-ground/request.md carries the design; RESEARCH-CLAIMS.md names it). Boxes: the research is 269's R1 (270, 280, 160), checked in its queue
