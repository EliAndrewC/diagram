# The first-principles estimate exercise

**Load this file when:** you want the reasoning behind the feature's target, i.e. why roughly 1-2 s at 20 households and
2-4 s at 40 is believed attainable in this stack.

## Method

Six opus agents (general-purpose, no repository access) in two arms of three:

- **arm A:** shown only finished maps, as renders of Sawada (19 households) and Kashikawa (20);
- **arm B:** shown only the placement write-up, `dev/placement-stages/hamlet-placement.html` as plain text.

Each was asked for a per-stage operation count and a time on the stated stack. Then each agent, in its own context, was
given:

1. the other input (map then write-up, write-up then map);
2. the measured per-stage times, and asked to diagnose;
3. the cProfile call counts, and asked to score its hypotheses.

The brief and inputs lived in the session's scratchpad and are not kept. This file is the record of the results.

## Estimates against measurement

| arm | 20 households | 40 households |
|---|---|---|
| map only | 0.4-0.55 s | 0.9-1.25 s |
| write-up only | 1.2-1.35 s | 2.5-2.8 s |
| map, then write-up | 1.1-2.2 s | 2.1-4.6 s |
| write-up, then map | 1.2-1.8 s | 2.4-3.3 s |
| **measured** | **6.8 s** | **14.7 s** |

The rules (searches, repair loops, scans over the canvas) raised the estimates about 2.5x. The map's content barely moved
them (0-40%). The remaining 5x at 20 households and 7x at 40 is implementation.

## What they diagnosed from the timings alone (round 3, before any profile)

All six independently said:

- lane_wells grows about n^3.7 and switches on at a threshold;
- the web grows about n^2.1;
- the other stages are linear with a 3-15x constant;
- the notice board, the one placer already backed by an index, matched their estimates exactly (the control).

All six also predicted the constant factor would show up as hundreds of thousands to millions of SHAPELY calls. That was wrong.

## What the counts showed that none predicted (round 4)

- A hand-written pure-Python geometry kernel and pure-Python grid indexes are the hot path; GEOS and numpy sit mostly unused.
- Homesteads has **no hotspot**: its top function is 0.38 s of 11.2 s under the profiler, and about ten modules cost 0.3-0.8 s
  each. This is why past one-function tuning sessions kept finding small gains.
- Recomputation once per object (`free_components` per house) and expensive area bookkeeping (`CanopyArea`; the agents
  mislabeled it an index).

## Their consensus causes (seconds lost, 20 / 40 households)

| cause | 20 hh | 40 hh |
|---|---|---|
| pointwise pure-Python geometry where batched shapely 2 / numpy applies | 2-3.5 s | 4-7 s |
| recompute after every change instead of keeping state (wells, lane pairs, free components) | 0.6-0.9 s | 5-6 s |
| index and raster upkeep | ~0.5 s | ~1 s |

## Their first pick, corrected

All six named the wells first and predicted 14.7 s -> ~10 s at 40 households. **That arithmetic was wrong.** It subtracted
seed 39's lane_wells median (4.58 s) from seed 47's total median (14.7 s). Seed by seed (lane_wells 10.04 / 4.58 / 0.59 s),
the fix cuts the slow tail (worst seed 23.8 s -> about 14 s) and removes the cubic term. The median barely moves, and it
is about 5% at 15-20 households. Batching the geometry is the everyday win.
