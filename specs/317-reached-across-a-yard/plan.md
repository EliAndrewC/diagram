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
  side - within `TIGHT_BEARING_DEG` (90) of the bearing to its yard, the side its yard lies on, as the drawing page places it - a
  search breadth MEASURED (research R7): with every bearing offered, behind its house a walk to the yard was found once in 194
  tries on 13 settlements, and 15 of the 16 passages came within 90 degrees of the yard. (It was 112.5, past the perpendicular,
  until the impl-drift check held it to the page - research R9.) A household behind its neighbor is still seated, by the ordinary seats and
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
- A WAY OF ITS OWN, WITHOUT THE ROUTED SEARCH (amended 2026-10-03 on the GM's ruling, `request.md`: *"we don'y need to be
  rigorous because people cut through their neighbors yards all the time"*; *"even if there IS a lane you might do it anyway if
  it was faster or more direct"*). The corridor a tight seat asks for is a straight one or one round the gable
  (`access.access_corridor`, `routed` False): no path bending round the homesteads is searched for, so a household such a path
  alone would reach may be seated across its neighbor's yard. Proving that none reached the tree was the passage's cost at 40
  households (the band-3 cell, research R9); measured after, research R10. CANON (the GM's ruling), recorded on the drawing page.
- THE ORDER AT A TIGHT SEAT: the corridors asked first, now the cheaper (`landlocked`), then the walks; at each layout the walk and
  the corridor again as the one predicate - the same verdict (both must hold). And once a seat: a household that has a way of its
  own from one garden layout at the seat is not on land the custom covers, so its other layouts there are refused unasked
  (research R7: the corridor found at 93 of 106 searches after a walk; the tight seats' work 4.0 -> 2.15 s).
- THE LAND, NOT ONE LAYOUT (`passage.landlocked`): the seat is taken only where some garden layout at it has a walk to the
  neighbor's yard and none has a straight or round-the-gable corridor of its own, asked once a seat before any layout is judged -
  a household lays its beds where its way can run. Judged a layout at a time, 10 of 13 passages at 15 households and 6 of 20 at
  40 were households another layout would have given a way of its own (research R8).
- ON THE FINISHED SEATING (`passage.recheck_passages`): once every household is seated, each household reached across a yard is
  asked again - its own homestead set aside, as when it was first asked - whether it has a straight or round-the-gable corridor
  of its own now; one that has
  is seated by it as any other household and loses its passage (`meta.passage_revoked`). A later household's corridor reserved
  past its beds had given Inashiro's one such household a drawn lane a few feet off (the farmhouse glyph check, research R9).
  By its WHOLE HOLDING, as at the seat (the plan review's ruling): the layout drawn is asked first; then every other layout
  built at its seat (kept for this, `_tight_of["layouts"]`), and one with a corridor that fits the finished seating - judged as
  the placer judges a layout, the household's own record, homestead, walk and wood reservations set aside - re-seats it
  (`passage.relay`). A layout with a way that no longer fits is not a way the holding has (`meta.passage_unfit`); measured 0
  on the reference at 15 and 40 households (research R9).

Every other rule of the placer is asked as before; only the corridor's question is answered by the passage.

**D3 - The chain (FR-002, the spec's edge case).** The neighbor must itself reach the tree - by its own corridor, or by a passage
whose chain to a corridor is at most `PASSAGE_CHAIN` households: 2, a GUESS citing Wigmore's Echigo entry, where C passes over
both B's plot and A's to the highway - the longest chain the record reads.

**D4 - The share (FR-002).** `PASSAGE_SHARE_BAND = (0.0, 0.25)`: each nucleated settlement rolls its share of households that may
be reached by passage from the map's seed, a GUESS - the record attests the custom, not how common it was, and a clustered
village whose rear households all walked through their neighbors' yards is not what the entries describe (alleys to the rear
houses, Morse; blind alleys to the houses, the Manchu survey). A household beyond the share is seated only with a corridor, as now. THE SHARE IS A CEILING (the perf-audit, 2026-10-03; research R10): a margin
that leaves a household without a house after seating some across a yard is seated once more with the passage withheld before
the ladder takes the next margin (`stages.seat_the_margin`, `meta.passage_withheld`) - seed 47 at 40 households had seated on its
third margin after two seatings thrown away; withheld, its chosen margin seats all 40. And a seating that has spent passages stops before the
growth's widest level (`growth.grow_the_margin`, `passage.passages_spent`): no seating that seats everyone reached it with
passages on the bookend's seeds, and seed 47 spent 5.7 s there on the seating thrown away (the perf-audit's second audit).

**D5 - The reach (FR-003).** The household's record carries `reached_across` (the neighbor's position) and no corridor; the
ways' one predicate of reach (`checks.unreached_houses`, which the web's settle, its last resort, the tree's judge and the gate
read) counts it reached when its chain ends at a reached household. The pool and gate tests that ask reach read the same
predicate. And the household it is reached across keeps its way drawn: its corridor is owed and never pruned, however near the
lanes its center stands (`tree.passage_anchors`; the village lane's glyph-check on Inashiro, F1 - the anchor 90 ft from a lane,
its corridor not owed, the two farmsteads left with no way). And the ways owe the reached household no lane of its own (research
R9, the impl-drift check): where a pass keeps an arm or a fragment as a house's only way, carries a lane's end to a dooryard, or
spaces the web's cuts to cover the houses, it asks one rule of who a lane serves - every farmhouse but those reached across a
neighbor's yard (`geom.lane_houses`) - while an end that merely reaches a house still counts every house. Nothing else of the
ways changes.

**D6 - The corridor judged as drawn (FR-004).** Feature 314 R12's refused web, reproduced (the route's own parts switched on, seed
13 at 20 households): three access lanes close a sliver because the web begins one at the house's door - (2939, 2606) - where the
seating's record and its judge (`tree.admits`, through `tree_records` and `lanes_of`) begin it where it leaves the yard - (2929,
2596). The fix as found (research R2): the web's settle carries a free lane end that stops short of a way onto it
(`settle.settle_joins`, reading `law.near_misses`), and that join, not the door leg, closed the sliver - so `admits` asks the needle
of the tree again with its ends joined as the settle will join them (`tree.as_joined`), with an exact box prefilter in
`law.near_misses` and `law.free_end` (the same answers) that keeps its cost below the host's noise. Verified on the reproduction
(the seed rolls), then the route's own parts re-measured: if the seating now admits only drawable corridors,
feature 314 R12's withdrawn lever is retried by `abab.sh` and kept only if it pays (FR-006). Retried and WITHDRAWN (research R4,
R8): searched per garden layout round the household's own parts, it paid before feature 315 merged (seats lost to the path alone
77 -> 21 and 90 -> 22, the stage -6% and -10% in CPU seconds), and after it cost the homesteads stage 3-43% more than main's search
round the house alone (calls, passage off, on the bookend's flagged seeds) - so the corridor's route keeps off the house alone,
shared by a seat's layouts, as on main. Its regression on the cohort (seed 18: squaring a water crossing straightened a routed
path across the household's own privy) showed a defect of the judge that stays closed: the seating judge asks the household's own
house, beds and fixtures of the path as the web will lay it (`tree.laid_run`, `own_clear`). Found and closed against main
(research R8): a joint's pull is never taken into a kink the two lanes did not have (`joints._one_joint`, seed 47 at 20
households).

**D7 - The known bugs (FR-007).** research.md lists each: the D6 defect (this feature); cohort seeds 14, 15, 906 and 22, 23 (the
Diagram (Inashiro) session, feature 315). At close, each is fixed with its run or in progress with its owner's last word. Found
at the gate and closed (research R8): feature 315's persimmon reseat asked a neighbor's sun only of the first seat its search chose,
on the household's rolled side alone, and gave the tree up where a later seat or the other side shaded no one - Inashiro, moved by
the tight seats, drew 11 persimmons of 12 rolled (B10). It now asks the neighbor's sun of every seat it tries, on the rolled side
and then the other (`persimmon_reseat.persimmon_for`). Found by the impl-drift check and closed (research R9): a grove farm's
test that no part of it stands on a corridor (`fit._on_the_access`) left out its kura and its byre. Found by the village lane's
glyph check, round 3 (F5: lane 14 on Inashiro bulged 27 ft round bare scrub), and closed (research R10): feature 310 holds the copse
out of the afternoon lane west of every yard and bed, and the seating's reservation of each household's wood floor
(`wood_share.copse_keepouts`) did not keep that lane, so seats were reserved where the copse never plants - 18, 16 and 34 of them
on main's Inashiro, Kuwabata and Sawada - and a neighbor's path was routed round two of them. The reservation now keeps the lane
by the copse's own figure, and a gate test holds every reserved seat planted (`tests/gate/test_wood_shares_planted.py`).

**D8 - The route search shared (the GM, 2026-10-03: *"Yes, definitely do this"*), AMENDED ON THE MEASUREMENT (research R10).**
The perf audit's lever was one map of what is reachable, shared across the route searches. Measured before building, it would
have answered none of seed 47's 509 failed searches at 40 households: none began inside a region an earlier failure had found
closed. 348 of them had no branch of the tree within reach and explored their whole box first; an exact check before each
search (`route.tree_in_reach`) takes those out with the same verdict, maps byte-identical. Built in its place, inside this
feature; the shared map is not built.

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
