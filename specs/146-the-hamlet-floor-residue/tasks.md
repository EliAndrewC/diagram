# Tasks: feature 146 - the hamlet floor's residue

Every task is `research: rendering` unless it says otherwise. No acceptance task, by the GM's instruction
(*"take it to completion and then merge it in as well without needing any acceptance from me"*).

- [x] T01 the GM's request verbatim; spec; `spec-fidelity` round 1 (2 changes) and round 2 (FAITHFUL); plan
- [x] T02 the residue counted by class - 56 + 176 + 141 = 373, exhaustive (research R1, `floor-at-145.txt`)
- [x] T10 class 2, `segments_04c_groves_and_shading` (24): a scripted break per uncovered failure branch
- [x] T11 class 2, `common_02_overlap_policy` (23) and `common_03_capacity` (11)
- [x] T12 class 2, `segments_03a_overlaps_and_ward_fences` (18) and `segments_06c_decks_yards_and_moat_clearances` (14)
- [x] T13 class 2, `segments_01a_city_ring_and_frame` (13) and `segments_03c_clusters_and_labels` (12)
- [x] T14 class 2, the tail (`segments_04a/04b/05a/05b/06a/06b/07b/07c/08b/11b`, `driver`, `registry_analysis`)
- [x] T16 INVESTIGATED, and the premise was wrong in a way worth recording. The retired check was `if scale in ("town", "city")` (recovered from b709c4ae^): it never ran on a hamlet, so it would NOT have caught the Kashikawa caption over a byre even when it existed. At hamlet scale there is NO caption-over-a-feature check at all - which is the real finding, and why that map passes green. Restoring the town/city check is worthwhile and is CITY work, carried to `future-work/cities.md`; the hamlet gap is carried with it - `research: rendering`
- [x] T17 INVESTIGATED and carried: the three `woodland_commons_*` checks pass vacuously on the two scripted hamlets that roll zero woodland parcels, and `village_windbreak_is_continuous` counts the RECORD rather than the ink by design (feature 137 T05) so it cannot see a belt drawn short. Both want a companion "the declaration was attempted" check rather than a change to the existing ones; that is map doctrine, not coverage, and is carried to `future-work/farming-communities.md` - `research: rendering`
- [x] T15 census: 31 checks now carry a scripted fixture (4 at the start). The rest are recorded rather than claimed - several could not be tripped by a one-line break of the reference (its decks are all footbridges, its streams all offmap-anchored) and are named in research R3 - `research: rendering`
- [x] T20 class 3, `hamletgen/ways.py` (37) - the fallbacks; each either forced by a test or removed with its reason at the point of change
- [x] T21 class 3, `settlement/city/bridges.py` (17) and `settlement/water_ways.py` (14)
- [x] T22 class 3, `settlement/homestead_parts.py` (11), `hamletgen/homesteads.py` (9), `hamletgen/hinterland.py`, `settlement/houses.py`, `rolling/fit.py`, `shrines_wells/*`, `structures/*`, `fields/comb.py`
- [x] T23 class 3, `waterfields/` (carve, comb, seams, polder) and `settlement/_geom/*`
- [x] T30 class 1: the state of feature 139 read and the route chosen (a scripted map rolling `mulberry_dike_fishpond`, else a test-side archetype pin - never a new pool map); the decision and its cost recorded BEFORE the work
- [x] T31 class 1: `dikepond_is_ponds_in_a_block` (56) exercised
- [x] T40 re-measured and REPORTED: the floor is **128 lines / 99.13%**, from 373. SC-001 (a green floor) is NOT met, and the spec's status line says so; research R3 classifies every remaining line and `floor-at-close.txt` is the table. The remainder is carried in `future-work/cross-cutting.md` rather than left as an open task here, because an open task blocks every later push and this feature is closed - `research: rendering`
- [x] T41 `make done` green; `make test-full` green on every test, red only on the hamlet floor (T40) and the ledgered pre-existing global-floor misses; the pool clean and unchanged - `research: rendering`
- [x] T42 landed on main with no acceptance task (the GM's instruction), and the GM told - before the landing - that the floor is 99.13% rather than green, with what remains and why - `research: rendering`
