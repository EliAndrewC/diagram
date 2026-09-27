# Tasks - feature 266, labels placed by the cartographic standard

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (P1-P6). Research: [`research.md`](research.md) (R1-R4).

**No task here is `research: physical`.** Label placement is a map drawing convention: nothing is asserted about the
world, and the sources are cartographic practice (research.md R1).

- [ ] T01 `l7r/diagram/labels/`: standard, geom, layout, obstacles, placer - point, line and area subjects, the ranked
      positions, nearest-first rings, free-first cost, leaders, layouts (FR-002 to FR-009)
      research: rendering
- [ ] T02 Unit tests of the placer on synthetic sheets: every SC-003 case, the four subject kinds, the upright rule,
      the frame, the index built once (SC-002, SC-003)
      research: rendering
- [ ] T03 Settlement adaptor: `seat_caption`, `label_obstacles`, the leader, `label(lines=, angle=)`; the board, `place_caption`,
      the road caption and the field names through it; the town and city cover rule with its civic exception; the old
      searches deleted (FR-001, FR-014)
      research: rendering
- [ ] T04 `compound.py`: every caption through the placer, with its leader where it has one; the two composed sheets
      regenerated (FR-001, FR-005, FR-011)
      research: rendering
- [ ] T05 The static path test: `self.label` only at D8's call sites, raw `<text` in `settlement/` only in `label()` and
      the placer-fed field-name markup, `compound.py` text only in its placer-fed caption drawer and title, note and
      scale bar; shown red on a planted call and a planted raw `<text` (FR-012, SC-002)
      research: rendering
- [ ] T06 `make seat-label` (`tools/seat_label.py`): read a hand-drawn sheet with every shape classified by its tag,
      check and write captions and their leaders; the three magistracy sheets' board captions re-seated (FR-005, FR-013,
      SC-006)
      research: rendering
- [ ] T07 The caption ledger and its gate test, leaders included; shown red on a changed sheet, on a new off-seat
      caption, on a missing leader and on an untagged caption in a changed sheet (FR-013, SC-006)
      research: rendering
- [ ] T08 Doctrine: `buildings.md`, `.claude/agents/building-review.md`, `future-work/cities.md` (D8), `dev/placement.md`
      and the captions index (FR-013)
      research: rendering
- [ ] T09 The five pool hamlets and the two composed magistracy sheets regenerated; every board caption measured as in
      R2, before and after (FR-011, SC-001)
      research: rendering
- [ ] T10 The record: questions 040 and 050 on the standard with every calibration labeled (D2, D3, D4, D4a), eight
      registry entries; `quote-check`, `record-format`, `source-applicability` pass; the unreadable works on the download
      list (FR-010, SC-004)
      research: rendering
- [ ] T11 Existing tests updated for the removed parameters and searches (the board's `label_above` and `label_xy`,
      `place_caption`'s hint and slides, the pull)
      research: rendering
- [ ] T12 `make done` green with 100% coverage, then land, and report D7, D8, D9 and P1 to the GM (SC-005)
      research: rendering
- [ ] T13 The review-round hook: a NOT-REVIEWABLE pass does not count as a round, so the next dispatch is a first
      reading (constitution XIV, found this feature)
      research: rendering
