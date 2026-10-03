# Implementation Plan: reached across a yard (feature 317)

**Spec**: [spec.md](spec.md) | **Date**: 2026-10-02

## Summary

The record answers the GM's question from what was read (R1, a page session); the seating may then admit a nucleated household
whose own corridor the tree cannot take by passage across a neighbor's dooryard to the neighbor's way (Wigmore's custom of passage
for land with no road access), up to a share rolled per settlement; the seating judges a corridor in the form the web will draw it
(the defect feature 314 R12 found); and every known bug is listed with its owner.

## Performance bookends (constitution VI)

| | label | notes |
|---|---|---|
| before | `317-start` | taken back to back with `317-end`, in a worktree at origin/main (feature 314's lesson: this host is loaded) |
| after | `317-end` | `make perf-report AGAINST=317-start` |

## Decisions

**D1 - The record first (FR-001).** Brief `briefs/r1-write.md` (a page session, write then check): the entry's "Was every house in
a clustered village reached by a lane?" rewritten from what was read - no page states it as a rule; passage over a neighbor's land
for land with no road access in seven provinces (three towns), and a chain of it (Echigo) - each passage quoted from the scan,
its limits stated. A second brief (R2) brings the drawing page's rule once D2-D4 land, each value in its class.

**D2 - The passage, offered only where no corridor is (FR-002).** Wigmore's custom is for land that "cannot reach the highway
without passing over" another's, so the seating asks for a corridor first, as now; only where `access_corridor` finds none does
it ask for a passage: a straight leg from the household's dooryard door to the nearest point of a standing neighbor's threshing
yard within `PASSAGE_REACH_FT`, clear of every house, garden bed, shed, byre, well pocket and fixture (its own and every
other's), of every other placed homestead, of the refused-ground grid and of the reserved wood seats - so it crosses only open
ground and the neighbor's yard. `PASSAGE_REACH_FT` is a GUESS (a neighbor's yard across the path's room the growth leaves,
`grow_gap`, and a dooryard's depth - about 40 ft); the leg is not drawn as a lane - a yard and a dooryard are open trodden ground,
the walk across them is the custom, not a way (this record's reading, a GUESS). Every rule of the placer is asked as before;
only the corridor's question is answered by the passage.

**D3 - The chain (FR-002, the spec's edge case).** The neighbor must itself reach the tree - by its own corridor, or by a passage
whose chain to a corridor is at most `PASSAGE_CHAIN` households: 2, a GUESS citing Wigmore's Echigo entry, where C passes over
both B's plot and A's to the highway - the longest chain the record reads.

**D4 - The share (FR-002).** `PASSAGE_SHARE_BAND = (0.0, 0.25)`: each nucleated settlement rolls its share of households that may
be reached by passage from the map's seed, a GUESS - the record attests the custom, not how common it was, and a clustered
village whose rear households all walked through their neighbors' yards is not what the entries describe (alleys to the rear
houses, Morse; blind alleys to the houses, the Manchu survey). A household beyond the share is seated only with a corridor, as now.

**D5 - The reach (FR-003).** The household's record carries `reached_across` (the neighbor's position) and no corridor; the
ways' one predicate of reach (`checks.unreached_houses`, which the web's settle, its last resort, the tree's judge and the gate
read) counts it reached when its chain ends at a reached household. The pool and gate tests that ask reach read the same
predicate. Nothing else of the ways changes.

**D6 - The corridor judged as drawn (FR-004).** Feature 314 R12's refused web, reproduced (the route's own parts switched on, seed
13 at 20 households): three access lanes close a sliver because the web begins one at the house's door - (2939, 2606) - where the
seating's record and its judge (`tree.admits`, through `tree_records` and `lanes_of`) begin it where it leaves the yard - (2929,
2596). The fix: find the web pass that lays that door leg, and have `lanes_of` lay it the same way for the seating, so `admits`
asks the needle and every pair rule of the drawn lane. Verified on the reproduction (it must refuse the corridor at seating, or
the web must draw it lawfully), then the route's own parts re-measured: if the seating now admits only drawable corridors,
feature 314 R12's withdrawn lever is retried by `abab.sh` and kept only if it pays (FR-006).

**D7 - The known bugs (FR-007).** research.md lists each: the D6 defect (this feature); cohort seeds 14, 15, 906 and 22, 23 (the
Diagram (Inashiro) session, feature 315). At close, each is fixed with its run or in progress with its owner's last word.

## Verification

- Unit tests: the passage (offered only without a corridor, its leg's clearances, the chain limit, the share), the reach
  predicate with passages, `lanes_of`'s door leg; the reproduction as a test where it can be built small.
- `refusals.py`/`abab.sh` at 15 and 40 households against main; the cohort (`make cohort N=24 JOBS=4`) against main; `make done`
  with five workers; the bookends back to back.

## Constitution Check

- XII: D2-D4 are recorded with their classes (accurate: the custom; GUESS: the dooryard, the reach, the chain, the share).
- XIII: the cohort and the pool against main (FR-005).
- XVI: the passage is the GM's "go with" the research - no exception taken; D2's corridor-first order is the record's (land with
  no road access), not a limit added.
