# Derivation - the homesteads seat funnel, as it works today (a work-budget fixture, feature 443 FR-009)

This fixture is TODAY's homesteads algorithm written as if it were a derivation, so that the `work-budget` agent can be shown to
bite: the design the GM approved (2026-10-28) requires it to be ruled LOOSE or OVER. Its factors are the funnel trial 439 measured
on seed 25 at 40 households, nucleated (`specs/439-fewer-envelope-probes/research/funnel.md`, measured 2026-10-27), each with the
reason the algorithm has for it.

## Contract

- Reads: the settlement's seat (where the cluster sits), the field and its water lines, the ground the earlier stages reserved.
- Writes: one farmhouse per household, each with its yard, its garden side, its storehouse, sheds and fixtures (its parts), and
  a corridor from its door that the lanes later draw.
- Keeps: every house reachable from its door; no part on the crop, the water or another household's ground.

## The algorithm

    for each household (one at a time, in growth order):
        repeat until the house is placed or the seats run out:
            pick the next candidate seat the growth offers near the houses already placed
            ask the cheap ground test of it; skip it on a refusal
            settle the seat: build the household's full reach envelope from it;
                if the reach grew while settling, build the envelope again from the settled seat
            offer the settled seat to the placer, unless it is near a house already placed
            the placer lays the four layouts of the homestead on the seat and refuses the seat when
                a tight seat is not landlocked, or the parts do not fit, or every garden side's box is blocked,
                or no layout's yard opens onto lane ground

## The count, factor by factor

| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 20 at 20, 40 at 40, 80 at 80 | one per household | the reference spec at each size |
| seats asked the cheap ground test | per item | about 21 (830 for 40) | the growth offers seats until one is placed; no bound but the seats in the growth's ring | no bound: until the ring's seats run out |
| envelopes built | per item | about 20 (803 for 40) | each settle builds one, and builds it again when the reach grows (about 397 rebuilds) | every settle rebuilt |
| seats offered to the placer | per item | about 7 (272 for 40) | the settled seats not near a house already placed | every settled seat offered |
| layouts laid per offered seat | per item | 4 | the homestead's four layouts, each laid before the placer can say whether the seat is refused | every offered seat refused after laying |
| slack | per item | 1 | none added to the measured funnel | as measured |

So per house: about 21 ground tests, about 20 full envelopes (95% of them for seats never placed) and about 7 x 4 = 28 laid
layouts, of which about 24 are refused. The later web stage then tests each lane end against every other lane end and every
household box (all pairs), a pass over a growing set inside a loop over a growing set.


## Totals

- at 20: 20 x (21 + 20 + 7 x 4) x 1 = 1,380
- at 40: 40 x (21 + 20 + 7 x 4) x 1 = 2,760
- at 80: 80 x (21 + 20 + 7 x 4) x 1 = 5,520

## Cheaper algorithms considered

- sweep: not used - the growth offers seats in its own order
- grid or spatial index: not used for the near-a-house test, which is asked of every house placed
- priority queue: used - the growth's ring is taken in order of its seats
- incremental update: not used - the reach envelope is rebuilt when the reach grows
- memoizing what a scan does not change: not used - each settle builds its own envelope
