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

## Re-opened by the GM, 2026-08-28 - the floor goes GREEN

T40 closed at 99.13% and reported that. The GM read the report and re-opened the remainder in their own
words: *"anything that is a real test that you think is actually testing a real case, then please add the
test coverage for it ... as always, you can refactor things in order to make things more testable. For
example, if something is only available as an inner function in a closure, then you can move it out into
its own function to make it more unit testable ... please proceed until we are actually back up to
everything passing and full coverage. at one hundred percent in the place that you currently report as
99.13%"*. So SC-001 is live again, and the method is named: EXTRACT, then test.

- [x] T50 the paradigm written into the project guidelines - the GM asked *"Is that not something you were already doing? If not, then we might want to update the project guidelines"*, and the honest answer was no: this repository's own commits say *"dropped (nested closure)"*. Root `CLAUDE.md`, above the human-scale clause - `research: rendering`
- [x] T51 the first three extractions, as the worked examples the guideline cites: `hamletgen/ways.py` `web_pieces` and `web_rejoinable`, `settlement/water_ways.py` `fan_rival`, each with a unit test taking plain dicts and tuples - `research: rendering`
- [x] T52 the rest of the extractions and their tests, module by module. Thirteen closures lifted (`web_pieces`, `web_rejoinable`, `commit_lane`, `bowtie_cut`, `push_clear_of_fabric`, `fan_rival`, `pick_caption_seat`, `anchor_holds`, `hem_on_water`, `s_on_side`, `bamboo_blocked`, plus the two dead ones removed); ~70 tests added. **Four dead-code removals with their proofs**: `facing_chains`' two unreachable guards, the `wells_troughs_rails_clear_of_each_other` and `paddy_fan_gapless` derivations that feature 141 left running on every gate, `pull_caption_toward`'s centroid guard, and `_fit_at_aspect`'s second saturation break. **One real defect fixed where it was found** (constitution XIV): `_miter_normals` built an empty list and indexed it when a hem is one boundary wide - an `IndexError` from a `build_comb` call with legal arguments - `research: rendering`
- [x] T52a `make cov-file FILE=... MOD=...` added, because the loop this task ran in was "write a test, wait 10 minutes for `make test-full` to say you covered the guard ABOVE the one you aimed at". It answers in seconds and it found exactly that mistake twice (the byre and garden seats, both refused by `_in_blocked` one line earlier) - `research: rendering`
- [x] T53 `make test-full`: the hamlet-path floor is **100%** (`TOTAL 14661 0 100%`; `make hamlet-floor-check` names nothing short). Every test passes. The remaining red on that target is the PRE-EXISTING global-floor ledger - 29 lines in `ci/`, `switches.py` and three `tools/` modules, none of them touched by this feature and all of them red before it started (T41 recorded the same set). Constitution XIII: a pre-existing failure stays ledgered and is not fixed under another feature's number. `settlement/` is 95% against its 94% ratchet - `research: rendering`
- [x] T54 the reference hamlet is CLEAN and served from the roll cache - nothing the roll executes changed, which is the evidence a lift or a deletion moved no map. `make done` green (2,386 tests, 52 s). Landed on main - `research: rendering`
