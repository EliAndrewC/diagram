# Implementation Plan: reached across a yard (feature 317)

**Spec**: [spec.md](spec.md) | **Date**: 2026-10-02

## Summary

The record answers the GM's question from what was read (R1, a page session); the grown cluster may then seat a nucleated household
against a neighbor's land, with no corridor of its own, reached by passage across the neighbor's yard to the neighbor's way
(Wigmore's custom of passage for land with no road access), up to a share rolled per settlement; the seating judges a corridor in the form the web will draw it
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

**D2 - The passage, offered only where no corridor is (FR-002; amended 2026-10-03 on a MODE 1 ruling).** Wigmore's custom is for
land that "cannot reach the highway without passing over" another's, so a household asks for a corridor first, as now; only where
`access_corridor` finds none may it be reached by passage. The first build (a leg from the door to a neighbor's yard within 40 ft)
seated no household: the growth parts every two footprints by a path's whole strip (`grow_gap`, 16 ft at 1 ft a pixel), so the
custom's condition - land behind a neighbor's - never arose (research R3). The MODE 1 check ruled not building the passage NOT
LEGITIMATE: the spacing that kept the condition from arising was built for a lane to every house. So:

- TIGHT SEATS. While the settlement's share has room (D4), each standing house of the grown cluster also offers seats at the
  distance where the two footprints part plus the 2 px parting (`grow_gap` without the path's strip): a household seated there
  stands against its neighbor's land. A tight seat is taken only by passage: a household that finds a corridor of its own there
  is not land the custom covers and is refused the seat (the growth's ordinary seats keep a path's room). They are offered only
  round a house a passage may cross to (reached within the chain, D3, with a yard: `passage.crossable`) and only on its yard's
  side - within `TIGHT_BEARING_DEG` (112.5) of the bearing to its yard, its front and flanks - a search breadth MEASURED (research
  R7): with every bearing offered, behind its house a walk to the yard was found once in 194 tries on 13 settlements, and 15 of
  the 16 passages came within 90 degrees of the yard. A household behind its neighbor is still seated, by the ordinary seats and
  a way of its own. Nor is a tight seat offered within `TIGHT_TREE_FT` (80 ft) of the access tree, where a household has a way of
  its own and the custom's condition fails - measured (research R8): no passage came from nearer than 87 ft, and of the 135 of 343
  tight tries nearer than 80 every one whose walk was found had a corridor of its own.
- THE CUSTOM'S CONDITION AS THE REACH: the household's own ground adjoins the neighbor's - its land (the reach the growth parted
  its seat by, over every garden layout, carried with its house) within the parting and `PASSAGE_ADJOIN_FT` of the neighbor's
  footprint, a GUESS (the 2 px the parting leaves and a foot of tolerance) - never a walking distance across open ground (a long
  walk across open ground is a path, not the custom). Measured (research R6): one layout's box, or the reach rolled at the final
  seat alone, stands 3-36 px back from the parting, and refused all but one household.
- THE WALK: from one of its dooryard doors (`doors_of`) to the neighbor's threshing yard, every point of it on the two households'
  land (within their two lands, the parting between them included), clear of both households' houses, beds, sheds, byres, well
  pockets and fixtures, of every other placed homestead, of the refused-ground grid and of the reserved wood seats - ROUTED round
  them on the map's own router (`route.search`, `route.taut`), as a household's path is: a straight leg ran through one of the two
  households' own house, beds or fixtures on 95 of the 109 tight-seat layouts with no corridor at 15 households, seeds 1-16, and
  found 3 passages (research R6). Kept clear of every later homestead as a corridor is; not drawn as a lane - a dooryard and a
  yard are open trodden ground, the walk across them is the custom, not a way (this record's reading, a GUESS).
- THE ORDER AT A TIGHT SEAT: the walk asked first, then the corridor - the same verdict (both must hold), since the walk is
  searched on the two households' land and the corridor over the whole tree (research R6). And once a seat: a household that has
  a way of its own from one garden layout at the seat is not on land the custom covers, so its other layouts there are refused
  unasked (research R7: the corridor found at 93 of 106 searches after a walk; the tight seats' work 4.0 -> 2.15 s).
- THE LAND, NOT ONE LAYOUT (`passage.landlocked`): the seat is taken only where some garden layout at it has a walk to the
  neighbor's yard and none has a corridor of its own, asked once a seat before any layout is judged - a household lays its beds
  where its way can run. Judged a layout at a time, 10 of 13 passages at 15 households and 6 of 20 at 40 were households another
  layout would have given a way of its own (research R8).

Every other rule of the placer is asked as before; only the corridor's question is answered by the passage.

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
2596). The fix as found (research R2): the web's settle carries a free lane end that stops short of a way onto it
(`settle.settle_joins`, reading `law.near_misses`), and that join, not the door leg, closed the sliver - so `admits` asks the needle
of the tree again with its ends joined as the settle will join them (`tree.as_joined`), with an exact box prefilter in
`law.near_misses` and `law.free_end` (the same answers) that keeps its cost below the host's noise. Verified on the reproduction
(the seed rolls), then the route's own parts re-measured: if the seating now admits only drawable corridors,
feature 314 R12's withdrawn lever is retried by `abab.sh` and kept only if it pays (FR-006). Done (research R2, R4): the route is
searched per garden layout round the household's own parts (feature 314's searched once per house and yard, so every layout took
the route laid round the first one's beds), and it pays - the seats lost to the path alone 77 -> 21 and 90 -> 22, the stage -6%
and -10% in CPU seconds. Its one regression on the cohort (seed 18: squaring a water crossing straightened a routed path across
the household's own privy) is closed the same way as R12: the seating judge asks the household's own house, beds and fixtures of
the path as the web will lay it (`tree.laid_run`, `own_clear`). Found and closed against main (research R8): a joint's pull is
never taken into a kink the two lanes did not have (`joints._one_joint`, seed 47 at 20 households); a door the search round its
house alone cannot take to the tree is searched once for a seat's four layouts (`route.house_reaches`, exact); and the route's
search leaves the persimmon - held by the door since feature 315 - to the taut pull's leg tests (seed 39 at 40 households,
1,084 -> 295 seats tried).

**D7 - The known bugs (FR-007).** research.md lists each: the D6 defect (this feature); cohort seeds 14, 15, 906 and 22, 23 (the
Diagram (Inashiro) session, feature 315). At close, each is fixed with its run or in progress with its owner's last word.

## Verification

- Unit tests: the tight seats (offered only while the share has room, at the parting without the path's strip), the passage
  (taken only without a corridor, the adjoining ground, the walk on the two households' land and its clearances, the chain
  limit, the share), the reach predicate with passages; the reproduction as a test where it can be built small.
- SC-002: at 15 households, seeds 1-16, households reached by passage where the share is above zero, never more than it allows
  (`meta.passage_share`, `meta.passage_reached`).
- `refusals.py`/`abab.sh` at 15 and 40 households against main; the cohort (`make cohort N=24 JOBS=4`) against main; `make done`
  with five workers; the bookends back to back.

## Constitution Check

- XII: D2-D4 are recorded with their classes (accurate: the custom; GUESS: the dooryard, the reach, the chain, the share).
- XIII: the cohort and the pool against main (FR-005).
- XVI: the passage is the GM's "go with" the research - no exception taken; D2's corridor-first order is the record's (land with
  no road access), not a limit added.
