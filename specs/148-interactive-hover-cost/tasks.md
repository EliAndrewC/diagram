# Tasks: feature 148 - the interactive map's hover cost

Every task is `research: rendering` - this feature changes how a page answers the pointer, and nothing
about how a hamlet was built. No acceptance task: the GM asked for the fix and reviews the map by eye.

- [x] T01 the GM's request verbatim; spec; `spec-fidelity` round 1 (3 changes) and round 2 (FAITHFUL, 2
      asides taken); the number claimed and pushed; plan
- [ ] T02 BEFORE, measured on both pages (FR-005): hit-testable path geometry by class, and load to first
      interaction. Inashiro is this clone's; kuwabata is read from the peer clone, never written
- [ ] T03 the coverage test (FR-002): for scrub and marsh, assert every drawn mark of the class falls
      inside the region that will answer for it. This is the whole of the safety for MARSH, whose region
      is the manifest footprint rather than a marks-built one - see the spec
- [ ] T04 the change (FR-001): `pointer-events: none` on the scrub and marsh ink where T03's coverage
      holds; the ink keeps its hit-testing where it does not
- [ ] T05 the unit tests: the attribute is emitted for those two classes and no others, and is withheld
      when coverage fails
- [ ] T06 the browser assertion (FR-006): hover a point ON the disabled ink for each affected class and
      assert the class still lights - the existing assertions pass even if a mark goes dead
- [ ] T07 AFTER, the same two measurements; SC-001 wants the hit-testable geometry down at least 90%
- [ ] T08 the pool maps regenerated and gated, `make done` green, the why recorded at the point of change
      and in `interactive/CLAUDE.md`
- [ ] T09 the load half reported to the GM: what it measured before and after, and - if the fix did not
      move it - the open question handed back rather than answered
