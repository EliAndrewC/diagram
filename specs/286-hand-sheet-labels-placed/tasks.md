# Tasks - feature 286, a hand-drawn sheet's labels placed by the one placer

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D9).

- [x] T01 The before measurement: every hand-sheet caption's cost at its hand seat, and the scripted maps' captions (D9; SC-002)
      research: rendering
      verify: DONE. before286: 4 sheets, 184 captions, hand-seat costs recorded (Hayakawa 28,000 with 6 hand seats kept, Ochiba 15,250, Ubame 36,750 with 2, the shrine 6,000); the five scripted hamlets regenerated with the new placer and their SVGs byte-identical - no generated caption moved; both in measurements.json
- [x] T02 The placer: lines at their own sizes, the extended fallback search, each block of a stepped subject; unit tests (D3, D4; FR-003)
      research: rendering
      verify: DONE. placer.py: sized_half (each line at its own size), _extended_cands (an area sampled over its whole extent, a point's sides slid along), the nudge, extended=; tests/labels/test_placer.py (22 pass) and the stepped subject in hand_sheet.subjects, each block largest first (tests/labels/test_hand_sheet.py)
- [ ] T03 Declarations: subject by group or `data-names`, inside-or-beside by the placer, no position read; the migration run on the sheets (D1, D2; FR-002)
      research: rendering
- [ ] T04 The render pipeline places every hand sheet's captions; `make sheet-render` (D5; FR-001, FR-005)
      research: rendering
- [ ] T05 The placement checks removed; readers by tags (D6, D7; FR-004, FR-005)
      research: rendering
- [ ] T06 The docs and contracts (D8; FR-006)
      research: rendering
- [ ] T07 The after measurement, make done, push (D9; SC-001 to SC-004)
      research: rendering
