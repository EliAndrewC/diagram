# Tasks - 247 Two beads per bund

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - a glyph convention,
nothing physical behind it (the GM's own words in `request.md`).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
      verify: DONE. spec-fidelity: round 1 NOT FAITHFUL (three changes taken), round 2 FAITHFUL, round 3 FAITHFUL on the FR-005 amendment; plan MODE 4 CLEAR at round 1 (11 decisions, none narrowing), plan-review.json recorded by the subagent
- [ ] T02 `_bund_beans` lays runs of two or more (FR-001, FR-002, FR-003, FR-006): the thirds rule on a
      short edge, the split-and-judge `_bead_runs`, runs returned; the unit tests in `tests/settlement/test_core.py`
      research: rendering
- [ ] T03 the draw site splits and judges its runs and the record keeps its shape (FR-001, FR-005, FR-006):
      `_comb_drop_drowned_beads` over `bund_bean_runs` in the net, the flat list re-flattened; the unit
      tests in `tests/settlement/test_fields.py`; the gate test in `tests/gate/test_bunds_and_dikes.py`
      research: rendering
- [ ] T04 the record (FR-004): the research convention paragraph and the modal Note; `make page-check`
      green with no entry-drift pair open
      research: rendering
- [ ] T05 the maps: `make map` on Inashiro, `make maps` over the pool, R1's script counting zero
      single-bead runs (SC-001), `make verify` green with the settlement-review beside it; land GATED
      research: rendering
