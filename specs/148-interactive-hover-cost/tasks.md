# Tasks: feature 148 - the interactive map's element count

Every task is `research: rendering` - this changes how a page is serialized, and nothing about how a
hamlet was built. No acceptance task: the GM reads the map by eye.

- [x] T01 the GM's request verbatim; the hover spec; `spec-fidelity` round 1 (3 changes) and round 2
      (FAITHFUL); the number claimed and pushed
- [x] T02 BEFORE, measured - AND IT REFUTED THE HOVER AIM (research R1). Kuwabata is the CHEAPER page at
      hit-testing (277 us/probe against 453) because inashiro carries 749 fat hit copies and a polder map
      carries none. Reported to the GM, who re-aimed the feature at element count
- [x] T03 the spec re-aimed at element count; `spec-fidelity` round 1 on the new aim: FAITHFUL, with
      three asides - the plan and tasks still described the dead aim (this rewrite), SC-001's headroom
      numbers were not in the record (T04), and the load half must be handed back if it does not move (T10)
- [x] T04 research R2: the counting method behind SC-001, with the numbers - drawn now, the
      order-preserving floor, and the order-free bound, per page. SC-001 rests on these and this feature
      exists because an unrecorded premise turned out false
- [x] T05 `<ellipse>` joins `<line>` and `<circle>` in the merge (FR-003)
- [x] T06 the merge gathers same-styled primitives that are SEPARATED by others (FR-001), with the
      skipped-extent test that keeps the picture (FR-002): an element joins an earlier bucket only where
      nothing it must pass overlaps it
- [x] T07 the unit tests: a separated same-styled pair merges; a pair separated by something it OVERLAPS
      does not; the emitted `d` draws what the elements drew; ellipses merge
- [x] T08 the picture is proved unchanged (US2, SC-003) - AND IT WAS ALREADY CHANGED, before this feature:
      the old merge had no overlap test, so translucent shapes it joined painted lighter, and every page
      sat 12-18% of its pixels away from its own SVG. Now 0.03%, which is antialiasing (research R3)
- [x] T09 AFTER, the same five measurements on both pages (FR-005); SC-001 wants kuwabata down 40% and
      inashiro down 20%
- [x] T10 the report to the GM: element count, load, scroll, zoom, highlight - and if LOAD has not moved,
      the open question handed back rather than closed over. The GM reported it and never withdrew it
- [x] T11 the pool maps regenerated and gated, `make done` green, the why at the point of change and in
      `interactive/CLAUDE.md`
