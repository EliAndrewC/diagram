# Tasks - 247 Two beads per bund

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - a glyph convention,
nothing physical behind it (the GM's own words in `request.md`).

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
- [ ] T02 `_bund_beans` lays runs of two or more (FR-001, FR-002, FR-003, FR-006): the candidate filter
      after the shuffle, runs returned, `_bead_runs_kept`; the unit tests in `tests/settlement/test_core.py`
      research: rendering
- [ ] T03 the draw site drops a run whole and the record carries the run lengths (FR-001, FR-005, FR-006):
      `_comb_drop_drowned_beads` over runs, `bund_bean_runs` in the net and the field record; the unit
      tests in `tests/settlement/test_fields.py`; the gate test in `tests/gate/test_bunds_and_dikes.py`
      research: rendering
- [ ] T04 the record (FR-004): the research convention paragraph and the modal Note; `make page-check`
      green with no entry-drift pair open
      research: rendering
- [ ] T05 the maps: `make map` on Inashiro, `make maps` over the pool, R1's script counting zero
      single-bead runs (SC-001), `make verify` green with the settlement-review beside it; land GATED
      research: rendering
