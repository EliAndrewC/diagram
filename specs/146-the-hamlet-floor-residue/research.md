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

## R2b - what the residue turned out to BE (the finding that reshaped this feature)

Class 2 was specified as "check failure branches no map trips". Most of it was not that at all: it was
**dead code feature 141's cut left behind**. 141 retired ~385 check names by replacing each `check(...)`
call with a `pass  # ... retired ...` stub, and left every segment body that computed the retired check's
inputs in place, on the comment "the segment stays for the check it keeps or the value it writes". For a
third of the battery neither was true.

| removed | count | lines |
|---|---|---|
| segments whose chain reaches NO live check | 201 | 3,457 |
| segments keeping a retired stub and no live check (a second pass - see the caveat) | 9 | 1,041 |
| helpers with no production caller, to fixpoint (each round orphans the next) | 6 + 9 + 14 | ~700 |
| **total** | | **~5,200** |

All 153 live checks survive; the reference and the pool are unchanged; frozen registry rows 595 -> 385.

**The caveat, recorded because it cost a round**: the first reachability pass used "does any later segment
NEED a name this segment WRITES", and segment locals are single letters (`q`, `k`, `b`, `s`), so almost
everything reached a live check spuriously and the pass was far too conservative. The second pass keyed on
"keeps a retired stub AND keeps no live check", which is the honest test.

**And a mistake worth recording**: sweeping the TEST tree for references to removed helpers with a regex
matched module names (`py`, `_builders`) and deleted ~300 unrelated tests. It was caught immediately and
reverted whole (the suite was back to 1,737 passing in one command), and the removal was redone by naming
each test through the AST. No broad automated test deletion; name every victim.

## R2c - the floor's path down

373 (145's landing) -> 347 (dead segments) -> 297 (orphaned helpers) -> 260 (nine more segments) -> 301
(a REGRESSION: the 39 tests deleted with those helpers were also giving incidental gate coverage) -> 227
(the fixpoint helper removal). Every step is a FULL run; the regression is recorded rather than smoothed
over, because it is the argument for replacing incidental coverage with purposeful fixtures.

Scripted negative fixtures: 4 at the start, **26** now - each a cached roll plus one deliberate break.

## R3 - the numbers at the end

(filled in at the closing task)
