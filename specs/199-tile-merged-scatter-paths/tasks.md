# Tasks - 199 Tile the merged scatter paths

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - how a browser
paints a page, nothing about how a place was built.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
- [ ] T02 `merge_primitives` tiles a bucket of `TILE_MIN`+ members into one path per `TILE` cell
      (FR-001, FR-002, FR-005); `_cell` at module level; the why at the point of change
      research: rendering
- [ ] T03 unit tests for the tiling (FR-006); the structural guard on the real reference page (FR-007)
      research: rendering
- [ ] T04 the browser test: a Kuwabata fixture, the pointer sweep at the opening view capped at 40 ms
      on the median; the reference sweep recorded (FR-008); both guards shown to FAIL with the tiling
      reverted (SC-005)
      research: rendering
- [ ] T05 measurement on the implementation: the R2 move-cost table and the R4 pixel comparison over
      the pool pages, written to `research.md` R6 (FR-004, SC-001..003)
      research: rendering
- [ ] T06 documents: `interactive/CLAUDE.md` row; `.specify` pointer; memory note (FR-009)
      research: rendering
- [ ] T07 `make done` green, `make page-check` green, the Kuwabata page opened and hovered at the
      opening view (SC-004); land on the GATED route
      research: rendering
