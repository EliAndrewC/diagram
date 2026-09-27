# Tasks - feature 266, labels placed by the cartographic standard

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (P1-P6). Research: [`research.md`](research.md) (R1-R4).

**No task here is `research: physical`.** Label placement is a map drawing convention: nothing is asserted about the
world, and the sources are cartographic practice (research.md R1).

- [x] T01 `l7r/diagram/labels/`: standard, geom, layout, obstacles, placer - point, line and area subjects, the ranked
      positions, nearest-first rings, free-first cost, leaders, layouts (FR-002 to FR-009)
      research: rendering
      verify: DONE. labels/ package: standard, geom, layout, obstacles, placer, svg; 100% covered; make done green
- [x] T02 Unit tests of the placer on synthetic sheets: every SC-003 case, the four subject kinds, the upright rule,
      the frame, the index built once (SC-002, SC-003)
      research: rendering
      verify: DONE. tests/labels/test_placer.py (18) + test_svg.py: every SC-003 case, four subject kinds, upright, frame, the index
- [x] T03 Settlement adaptor: `seat_caption`, `label_obstacles`, the leader, `label(lines=, angle=)`; the board, `place_caption`,
      the road caption and the field names through it; the town and city cover rule with its civic exception; the old
      searches deleted (FR-001, FR-014)
      research: rendering
      verify: DONE. captions.py adaptor (_draw_seated_caption, label_obstacles, leaders); board, place_caption, road, field names through it; old ladder, annulus, pull deleted; civic rule FR-014 tested
- [x] T04 `compound.py`: every caption through the placer, with its leader where it has one; the two composed sheets
      regenerated (FR-001, FR-005, FR-011)
      research: rendering
      verify: DONE. compound.py captions through the placer with leaders; both composed sheets regenerated, boards at 4.2 and 3.6 px, no leader (R5)
- [x] T05 The static path test: `self.label` only at D8's call sites, raw `<text` in `settlement/` only in `label()` and
      the placer-fed field-name markup, `compound.py` text only in its placer-fed caption drawer and title, note and
      scale bar; shown red on a planted call and a planted raw `<text` (FR-012, SC-002)
      research: rendering
      verify: DONE. tests/labels/test_caption_paths.py: 33 D8 functions pinned, raw text allow-list, red on a planted call and a planted raw text
- [x] T06 `make seat-label` (`tools/seat_label.py`): read a hand-drawn sheet with every shape classified by its tag,
      check and write captions and their leaders; the three magistracy sheets' board captions re-seated (FR-005, FR-013,
      SC-006)
      research: rendering
      verify: DONE. tools/seat_label.py + make seat-label; tag classification; three magistracy boards re-seated and checking clean
- [x] T07 The caption ledger and its gate test, leaders included; shown red on a changed sheet, on a new off-seat
      caption, on a missing leader and on an untagged caption in a changed sheet (FR-013, SC-006)
      research: rendering
      verify: DONE. tests/fixtures/caption_ledger.json + tests/gate/test_hand_sheet_captions.py; red on a changed sheet, a new off-seat caption, a missing leader, an untagged caption (tests/tools/test_seat_label.py)
- [x] T08 Doctrine: `buildings.md`, `.claude/agents/building-review.md`, `future-work/cities.md` (D8), `dev/placement.md`
      and the captions index (FR-013)
      research: rendering
      verify: DONE. buildings.md, building-review.md, future-work/cities.md (D8), dev/placement.md, the engine and tools indexes
- [x] T09 The five pool hamlets and the two composed magistracy sheets regenerated; every board caption measured as in
      R2, before and after (FR-011, SC-001)
      research: rendering
      verify: DONE. five hamlets and two composed sheets regenerated; R5: every board caption at the preferred offset (3.9-4.1 ft), no leader
- [x] T10 The record: questions 040 and 050 on the standard with every calibration labeled (D2, D3, D4, D4a), eight
      registry entries; `quote-check`, `record-format`, `source-applicability` pass; the unreadable works on the download
      list (FR-010, SC-004)
      research: rendering
      verify: DONE. 040/050 rewritten and footnoted; 8 registry entries; quote-check, record-format and source-applicability run and every finding applied; Imhof, Yoeli, Krygier-Wood on the download list
- [x] T11 Existing tests updated for the removed parameters and searches (the board's `label_above` and `label_xy`,
      `place_caption`'s hint and slides, the pull)
      research: rendering
      verify: DONE. 22 tests of the removed machinery retired, 4 rewritten on the new standard; make done green
- [x] T12 `make done` green with 100% coverage, then land, and report D7, D8, D9 and P1 to the GM (SC-005)
      research: rendering
      verify: DONE. make done green (113 s, 100% coverage); landing report raises D7, D8, D9 and P1
- [x] T13 The review-round hook: a NOT-REVIEWABLE pass does not count as a round, so the next dispatch is a first
      reading (constitution XIV, found this feature)
      research: rendering
      verify: DONE. _hm_review_round.py: a NOT-REVIEWABLE first reading passes through; test-review-round-hooks.sh 64/64, red with the rule off
