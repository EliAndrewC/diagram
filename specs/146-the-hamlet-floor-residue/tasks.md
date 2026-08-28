# Tasks: feature 146 - the hamlet floor's residue

Every task is `research: rendering` unless it says otherwise. No acceptance task, by the GM's instruction
(*"take it to completion and then merge it in as well without needing any acceptance from me"*).

- [x] T01 the GM's request verbatim; spec; `spec-fidelity` round 1 (2 changes) and round 2 (FAITHFUL); plan
- [x] T02 the residue counted by class - 56 + 176 + 141 = 373, exhaustive (research R1, `floor-at-145.txt`)
- [ ] T10 class 2, `segments_04c_groves_and_shading` (24): a scripted break per uncovered failure branch
- [ ] T11 class 2, `common_02_overlap_policy` (23) and `common_03_capacity` (11)
- [ ] T12 class 2, `segments_03a_overlaps_and_ward_fences` (18) and `segments_06c_decks_yards_and_moat_clearances` (14)
- [ ] T13 class 2, `segments_01a_city_ring_and_frame` (13) and `segments_03c_clusters_and_labels` (12)
- [ ] T14 class 2, the tail (`segments_04a/04b/05a/05b/06a/06b/07b/07c/08b/11b`, `driver`, `registry_analysis`)
- [ ] T16 RESTORE `labels_clear_of_other_buildings` (found by the Kashikawa settlement-review under 145): feature 141's cut retired it, so the `_LABEL_GROUP` / `_LABEL_EXEMPT` registry - live doctrine, maintained in comments to this day - has no consumer at all, and a caption drawn through a byre passes green. Re-derive the check from the registry, prove it fires with a scripted break, and settle what the reference and pool maps then owe (Kashikawa's board caption clips a byre roof by 15.4 x 4.8 ft, accepted under 145 with its alternatives priced in the map's notes) - `research: rendering`
- [ ] T17 two checks found passing VACUOUSLY by the 145 reviews (the shape this project has written down twice - "a check that never RUNS looks exactly like a check that passes"): the three `woodland_commons_*` checks on the two scripted hamlets that roll zero woodland parcels, and `village_windbreak_is_continuous`, which counts the RECORD rather than the ink by design and so cannot see a belt drawn 57 px short (Sawada, deferred under 145 with its mechanism). Decide per check whether the vacuous pass is legitimate or wants a companion "the declaration was attempted" check - `research: rendering`
- [ ] T15 class 2 census: every hamlet-entered check with a reachable failure branch has a scripted fixture; any that cannot be tripped is named with its reason and disposed of under FR-001
- [ ] T20 class 3, `hamletgen/ways.py` (37) - the fallbacks; each either forced by a test or removed with its reason at the point of change
- [ ] T21 class 3, `settlement/city/bridges.py` (17) and `settlement/water_ways.py` (14)
- [ ] T22 class 3, `settlement/homestead_parts.py` (11), `hamletgen/homesteads.py` (9), `hamletgen/hinterland.py`, `settlement/houses.py`, `rolling/fit.py`, `shrines_wells/*`, `structures/*`, `fields/comb.py`
- [ ] T23 class 3, `waterfields/` (carve, comb, seams, polder) and `settlement/_geom/*`
- [ ] T30 class 1: the state of feature 139 read and the route chosen (a scripted map rolling `mulberry_dike_fishpond`, else a test-side archetype pin - never a new pool map); the decision and its cost recorded BEFORE the work
- [ ] T31 class 1: `dikepond_is_ponds_in_a_block` (56) exercised
- [ ] T40 re-measure: `make hamlet-floor-check` GREEN on the FULL run's data; the before/after counts in research R3
- [ ] T41 `make done` green; `make done FULL=1` red on nothing but the ledgered global-floor misses; the pool clean; any map that moved settlement-reviewed
- [ ] T42 land on main (no acceptance task); report to the GM what closed, what was removed as unreachable, and the global-floor ledger that remains
