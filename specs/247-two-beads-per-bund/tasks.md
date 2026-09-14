# Tasks - 247 Two beads per bund

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - a glyph convention,
nothing physical behind it (the GM's own words in `request.md`).

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
      verify: DONE. spec-fidelity: round 1 NOT FAITHFUL (three changes taken), round 2 FAITHFUL, round 3 FAITHFUL on the FR-005 amendment; plan MODE 4 CLEAR at round 1 (11 decisions, none narrowing), plan-review.json recorded by the subagent
- [x] T02 `_bund_beans` lays runs of two or more (FR-001, FR-002, FR-003, FR-006): the thirds rule on a
      short edge, the split-and-judge `_bead_runs`, runs returned; the unit tests in `tests/settlement/test_core.py`
      research: rendering
      verify: DONE. carve.py: bead_runs (MIN_BEADS_PER_RUN = 2, the GM's words and R2/R3 beside it) splits a line at every drop and keeps parts of two; _bund_beans lays two beads at the thirds of a two-to-three-spacing edge (nd == 2 -> 3), returns runs; test_core.py: bead_runs over plain lists (a middle drop splits, a single goes), the thirds on a 24 px square and the spacing on a 38 px one, the random state equal to the old laying's on the same input; 60 passed
- [x] T03 the draw site splits and judges its runs and the record keeps its shape (FR-001, FR-005, FR-006):
      `_comb_drop_drowned_beads` over `bund_bean_runs` in the net, the flat list re-flattened; the unit
      tests in `tests/settlement/test_fields.py`; the gate test in `tests/gate/test_bunds_and_dikes.py`
      research: rendering
      verify: DONE. waterfields/comb.py carries bund_bean_runs in the net with bund_beans flattened (hill/polder empty); settlement/fields/comb.py _comb_drop_drowned_beads applies one dry-predicate per run through bead_runs and re-flattens, record shape unchanged; test_fields.py: a drowned head keeps the part of two, a drowned middle drops two singles; test_bunds_and_dikes.py: _bead_segments derivation proved to see a single, and every shipped hamlet's segments hold two or more through _pool.obtain (Kuwabata skipped); 347 passed
- [x] T04 the record (FR-004): the research convention paragraph and the modal Note; `make page-check`
      green with no entry-drift pair open
      research: rendering
      verify: DONE. research/fields.html convention paragraph and the BundBeans Note each say a stretch of bund that carries beads shows at least two, because one does not read as a row; make page-check green (778 passed, no modal's research section moved against origin/main); make glossary CHECK=1 and make citations CHECK=1 report nothing stale
- [ ] T05 the maps: `make map` on Inashiro, `make maps` over the pool, R1's script counting zero
      single-bead runs (SC-001), `make verify` green with the settlement-review beside it; land GATED
      research: rendering
