# Tasks - feature 388, retire roll_village

Every task deletes code no shipping map runs, or repoints prose to what does: nothing physical is decided, so each is
`research: rendering`.

## Occasions

- none: no element of a shipping map is new, re-glyphed or re-placed - the deletion removes only code no live pool map runs
  (FR-006, proven by `make maps` byte-identical)

## Tasks

- [x] T01 The deletion (plan T01; FR-001, FR-002): `roll.py` and the closure's names per the plan's table, their tests, the closure re-run to a fixpoint, the coverage floor's leftovers through the same table
      research: rendering
      verify: DONE. DONE. roll.py, water_source.py, edge_seat.py, cut_undeckable_lanes + cut_at/_sub_run, BUNDLE_PITCH_FT and their tests deleted; build_comb, crop_to_content, cremation_ground, headman kept (frozen exhibits call them, D1b); 5 unit tests for branches only the roller reached; make dead-closure against ab8471ab6: nothing newly dead, roll_village still called only by its 3 exhibits; make done green
- [x] T02 The prose (plan T02; FR-003, FR-004): the docstrings, comments and indexes repointed; the claims index rebuilt; 380's carry removed and its cremation-ground and burial-ground items reworded to name the code as deleted (FR-004)
      research: rendering
      verify: DONE. DONE. roll_village prose repointed in hamletgen/__init__, cluster, water/fit, burial, houses, _geom/village, bridges, siting, rolling/__init__ and the five indexes; 380's carry removed, its cremation/burial items name the deleted seat at ab8471ab6; claims: 9 IN-STEP, none owed
- [x] T03 Measure and land (plan T03; FR-006, SC-001 - SC-004): `make maps` byte-identical, `make soak`, `make done`, the end bookend, `make cohort-landing`, the claims gate, the feature report, the gated push
      research: rendering
      verify: DONE. DONE. make maps clean (all CACHED, pool unchanged); make soak 9 passed; make done green; bookends 18.9 -> 18.8 s; cohort-landing 54/54 (fresh 9 of 48, a rate); claims-owed none; four red-gate tripwires accepted, their tooling fixes landed
- [ ] T04 (amendment 1) The four helpers and their tests (plan T04; FR-001, FR-002): `build_comb`, `crop_to_content`, `cremation_ground`, `headman` deleted; comb and frame tests through `lay_comb` / `crop`; the censuses stop scanning the legacy pool; `make dead-closure` before the gate
      research: rendering
      verify:
- [ ] T05 (amendment 1) The prose (plan T05; FR-003): the four repointed in docstrings, comments and indexes; the moved claims re-checked
      research: rendering
      verify:
- [ ] T06 (amendment 1) Measure and land (plan T06; FR-006, SC-002, SC-003, SC-006): `make maps`, `make done`, `make cohort-landing`, the end bookend, the report, the push
      research: rendering
      verify:
- [ ] GM review (make gm-reviewed F=388) [lands-open]
      research: rendering
      verify: the GM reviewed every row (make gm-review lists them)
