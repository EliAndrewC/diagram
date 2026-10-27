# Spike 2 - each settle starts from the widest reach seen (fewer envelope re-rolls)

Measured 2026-10-27, seed 25 at 40 households. Commit acf08eb45, reverted (the rule: set down - time rose beyond the floor).

**The change**: `grow_the_margin` passed each settle the reach of the last seat that settled (`start = union(guess, last)`);
the spike passed it the widest reach seen so far (`start = union(start, last)`), so a seat settles on its first envelope
instead of growing and re-rolling. It aims at the ~397 envelopes built inside `settled_seat`'s loop (803 envelopes for 406
settles, `research/funnel.md`).

## The target moved as aimed

`make perf-profile SEED=25 STAGE=homesteads HOUSEHOLDS=40` + `make perf-share MODULE=l7r/diagram/settlement/rolling/bundle.py`:
envelopes 803 -> 394 (`household_reach` calls), their cumulative time 1.002 s -> 0.589 s, the stage 4.47 s -> 3.97 s under
cProfile (-11%); settles 406 -> 387, seats offered 272 -> 220.

## The roll did not: `make perf-ab A=HEAD~1` (the quick form, one run a version)

```
 households, seed   A wall    +-  B wall    +-  wall    A cpu    +-   B cpu    +-   cpu      A calls     B calls  calls
         (40, 25)     6.64  0.00    7.75  0.00  +17%     6.63  0.00    7.75  0.00  +17%    7,564,885   9,088,283   +20%
best of each version's runs, alternated A B / B A; +- its worst less its best - read a change against it, never as a pass
floor (one engine against itself, taken 2026-10-27T20:32:13Z): wall -4%, CPU -4% - a change inside it is not a change
```

## Where it went: `make perf-fanout STAGES=homesteads,web,hinterland,field,windbreak`, before (HEAD~1, a detached worktree) and after

| stage | calls @40 before | after | change | growth exponent before -> after |
|---|---|---|---|---|
| homesteads | 7,718,035 | 7,189,320 | -7% | 1.08 -> 0.92 |
| web | 4,933,316 | 11,554,521 | +134% | 0.86 -> 2.29 |
| hinterland | 4,353,877 | 4,408,301 | +1% | 0.92 -> 1.24 |
| field | 3,695,274 | 3,695,269 | 0% | 0.74 -> 0.74 |
| windbreak | 1,561,346 | 1,564,642 | 0% | 0.96 -> 1.08 |

## Reading

Settling every seat at the widest reach spaces the homesteads wider, and the web - the lanes laid between them - then does
more than twice the work, its growth with size turning from under linear to over quadratic. The homesteads stage saved about
a tenth of its time; the roll lost 17%. A change to how one search tries its candidates changed what every later stage
works on: the search cannot be judged by its own stage alone, and its saving was bought with the settlement's shape.
