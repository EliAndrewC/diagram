# The growth's seat funnel, and why its envelopes cannot be screened cheaply

Measured 2026-10-27, seed 25 at 40 households, nucleated (the reference spec).

## Where the time is: `make perf-share MODULE=l7r/diagram/settlement/rolling/bundle.py STAGES=homesteads PROFILES=dev/perf-raw/20261027T205423Z-seed25-homesteads.prof`

The envelope (`_bundle_envelope`, from `growth.household_reach`): 803 calls, 1.002 s cumulative of the stage's 4.47 s under
cProfile (22%) - the one large share in the stage; `bundle.py`'s own time is 0.204 s (4.6%).

## The funnel (the same profile's call counts, read with pstats)

| step | count |
|---|---|
| seats the growth asked the cheap ground test of (`seat_refused`) | 830 |
| seats settled (`settled_seat`) | 406 |
| full envelopes built (`household_reach`) | 803 |
| seats offered to the placer (`try_place`) | 272 |
| houses placed | 40 |

## Why the placer refused (spike 1, commit 1be58457a, reverted: counters on `_place_bundle_nucleated`'s refusals, `make perf-profile SEED=25 STAGE=homesteads HOUSEHOLDS=40`)

```
439-SPIKE {'why_union_clear': 98, 'why_placed': 40, 'why_refused': 132, 'why_reach': 3, 'why_landlocked': 100, 'why_parts': 72, 'why_blocked': 57, 'grow_offered': 272, 'grow_took': 40, 'grow_level': 0}
```

Of 272 offered: 40 placed; 100 refused as tight seats not landlocked (`passage.landlocked` over the four layouts); 72 by
their parts (`_parts_fit`); 57 with every garden side's box blocked; 3 with no layout's yard onto lane ground; none by the
cheap house-box test (`_house_box_refused`), which `settled_seat` already asks before each envelope.

## Reading

- 763 of the 803 envelopes (95%) are built for seats never placed.
- Every refusal the placer makes is read off the laid layouts themselves - which side's box is blocked, whether a layout has a
  corridor of its own, whether its parts fit - so no cheap test predicts it; the one cheap test there is, the house's box, is
  already asked first and refuses none.
- THE CEILING, MEASURED: unprofiled, the homesteads stage takes 2.28 s of a 6.93 s roll at seed 25 (`dev/perf-log/20261027T190722Z-435-end-diagram-backlog.json`,
  measured 2026-10-27 by `make perf LABEL=435-end SCALING=1`), so cProfile inflates it 1.96 times (4.47 / 2.28). The 763 wasted
  envelopes (0.95 s profiled) are then about 0.49 s (7% of the roll); the placer's work on the 232 refused seats (`try_place`
  0.571 s profiled over 272 seats) about 0.25 s more - a perfect screen's ceiling about 0.74 s, about 10.6%.
- WHERE THE WASTED ENVELOPES ARE LOST: about 397 are re-rolls inside `settled_seat`'s loop (803 envelopes for 406 settles - a
  seat whose reach grows is settled again); the rest are the settled seats never offered (134: near a house, or out of
  settles) and the 232 the placer refuses. Spike 2 (`research/spike2.md`) aimed at the re-rolls.
- No cheap test predicts the placer's 232 refusals (the house box, the one cheap test, is asked first and refuses none); the
  re-rolls were spiked instead (spike 2).
