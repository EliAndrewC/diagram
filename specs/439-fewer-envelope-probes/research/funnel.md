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
- THE CEILING: a perfect screen that skipped all 763 wasted envelopes would save about 0.95 s profiled - about 0.3 s of a 7 s
  roll unprofiled (cProfile's inflation, a GUESS from feature 435's profiles), about 4%, at the quick form's floor. Even
  perfect, restructuring this search cannot approach an order of magnitude; a real screen would catch only part of it.
- By the brief's rule the screen is not built: the trial is set down at the measurement.
