# Tasks - feature 286, a hand-drawn sheet's labels placed by the one placer

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D9).

- [x] T01 The before measurement: every hand-sheet caption's cost at its hand seat, and the scripted maps' captions (D9; SC-002)
      research: rendering
      verify: DONE. before286: 4 sheets, 184 captions, hand-seat costs recorded (Hayakawa 28,000 with 6 hand seats kept, Ochiba 15,250, Ubame 36,750 with 2, the shrine 6,000); the five scripted hamlets regenerated with the new placer and their SVGs byte-identical - no generated caption moved; both in measurements.json
- [x] T02 The placer: lines at their own sizes, the extended fallback search, each block of a stepped subject; unit tests (D3, D4; FR-003)
      research: rendering
      verify: DONE. placer.py: sized_half (each line at its own size), _extended_cands (an area sampled over its whole extent, a point's sides slid along), the nudge, extended=; tests/labels/test_placer.py (22 pass) and the stepped subject in hand_sheet.subjects, each block largest first (tests/labels/test_hand_sheet.py)
- [x] T03 Declarations: subject by group or `data-names`, inside-or-beside by the placer, no position read; the migration run on the sheets (D1, D2; FR-002)
      research: rendering
      verify: DONE. the four sheets declared by tools/caption_decl.py (the old reading kept there only, tested in tests/tools/test_caption_decl.py) and by hand where it found nothing or named one piece of a thing (river landing, the alcove notes, the Fox border with the east wall, the tubs, Ubame's OUTER COURT - each in its map's notes); no caption carries a position; tests/labels/test_hand_sheet.py proves placement independent of any coordinates left on a caption (SC-001)
- [x] T04 The render pipeline places every hand sheet's captions; `make sheet-render` (D5; FR-001, FR-005)
      research: rendering
      verify: DONE. labels/hand_sheet.py placed() in each of the four gens (png and page from the placed text, write_sheet_page svg=); make sheet-render; the four regenerate in 4-16 s (make map)
- [x] T05 The placement checks removed; readers by tags (D6, D7; FR-004, FR-005)
      research: rendering
      verify: DONE. removed: the caption gate test and ledger, make seat-label, overlapping_labels, dark_on_dark_labels, orphan_group_labels, the label halves of occluded_foreground and trees_overlap, building-review's caption-seat step; the pack audit pairs by data-kind; make quick ALL=1 3,865 passed
- [x] T06 The docs and contracts (D8; FR-006)
      research: rendering
      verify: DONE. buildings.md, SKILL.md, research presentation 040 (make record), labels/tools/engine CLAUDE indexes, pack_audit CLAUDE, the building-review and size-audit contracts, future-work/compounds.md, make docs
- [x] T07 The after measurement, make done, push (D9; SC-001 to SC-004)
      research: rendering
      verify: DONE. SC-002 met in full context (sc002_ctx.py, the round-4 reviewer's): 0 captions worse on the four sheets, m:sc002-placed-worse; placed seats covering any ink 6/0/10/5 against the hand's 17/11/22/5 (sc002.json); scripted maps byte-identical; plan review round 5 CLEAR (28 decisions); make done green 2026-09-29 (109 s)
