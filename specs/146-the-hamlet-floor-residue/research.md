# Research: feature 146 - the hamlet floor's residue

`research: rendering` throughout unless a task says otherwise - nothing here decides how a place was
built; it decides what is tested.

## R1 - the residue, counted (the baseline this feature closes)

Measured on feature 145's landing state (`make test-full`, the hamlet-floor phase; 89 modules, 97.68%).
The three classes the GM named are EXHAUSTIVE of the floor's red state - 56 + 176 + 141 = 373, with
nothing outside them. That is the answer to the GM's question: closing the classes IS turning the floor
green, and SC-001 says so.

| class | lines | where the weight is |
|---|---|---|
| 1 - the dike-pond check, behind `meta.field_archetype == "mulberry_dike_fishpond"` | 56 | all of it in `check_village/segments_11a_taxfree_terraces_and_dikeponds.py` (`dikepond_is_ponds_in_a_block`) |
| 2 - check FAILURE branches no map trips | 176 | `segments_04c_groves_and_shading` 24, `common_02_overlap_policy` 23, `segments_03a_overlaps_and_ward_fences` 18, `segments_06c_decks_yards_and_moat_clearances` 14, `segments_01a_city_ring_and_frame` 13, `segments_03c_clusters_and_labels` 12, `common_03_capacity` 11, and a tail |
| 3 - placer refusals and never-needed fallbacks | 141 | `hamletgen/ways.py` 37, `settlement/city/bridges.py` 17, `settlement/water_ways.py` 14, `settlement/homestead_parts.py` 11, `hamletgen/homesteads.py` 9, and a tail of ones and twos |

The full table as it stood is `floor-at-145.txt` beside this file.

## R2 - what each class needs (the method, before the work)

- **Class 2 is not a coverage errand.** A check whose failure branch nothing reaches is a check nobody
  has proved fires - which is exactly what feature 141 said a kept check owes
  (`tests/gate/test_scripted_fixtures.py`: a cached roll plus one deliberate, targeted break). So the
  work is the fixture, and the coverage follows. Where a check cannot be tripped by any legal break, that
  is a finding about the check, reported by name (FR-003).
- **Class 3** is one unit test per refusal reason - the shape feature 145 used for sixteen of them.
- **Class 1** turns on whether a scripted map rolls the archetype by the time the task is reached.

## R3 - the numbers at the end

(filled in at the closing task)
