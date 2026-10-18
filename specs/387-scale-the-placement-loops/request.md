# Request - feature 387, verbatim

## The GM's question, 2026-10-18

> How long does it take to generate a hamlet these days?

> Okay, can you profile that for me?  Like, generate a hamlet and break down where the time is spent?  Because I remain
> convinced that there are massive inefficiencies we can fix.  It shouldn't take over a minute to render a map with 40
> households.  40 is simply not a very big number, so we must be doing some very inefficient things, which will be a
> problem for us when we get to larger and larger settlements.

## The session's measurement (as given to the GM)

Measured on main `eae693d92` (2026-10-18), the reference spec (Inashiro: 15 households, nucleated, pond) at the scaling
sizes, seeds 4, 25, 39 and 47 (`make perf SCALING=1`, `dev/perf-log/20261018T095027Z-adhoc-diagram-unit-tests.json`, taken
under another session's load of ~4.5): the stages total 3.3 s at 10 households, 7.1 s at 20 and 16.4 s at 40 (seeds 20.4,
15.5, 14.8, 14.9 s) - 10 -> 40 grows ~5x. Per stage at 40 households: homesteads 5.3 s (6.0x), field 2.9 s (5.7x), hinterland
2.8 s (3.8x), web 2.35 s (5.2x), windbreak 1.8 s (6.6x). cProfile of each at 40 households, seed 4 (`make perf-profile
SEED=4 STAGE=<stage> HOUSEHOLDS=40`):

| stage | what dominates |
|---|---|
| homesteads | laying each household's way (42%): every candidate way re-judges the whole way tree (88 full judgements); growing the cluster (35%): the bundle geometry rebuilt 4,346 times for 771 reach checks; the commons byres (12%): 7,636 clearance checks |
| field | merging small paddy cells (52%): each merge re-runs every ring rule, 8k intersections and 12.7k buffers |
| hinterland | bamboo strips (32%): each of 1,102 candidate spots is checked against every building, house and lane segment in a straight loop, 447k segment tests, no spatial index; open-ground patches (28%): 17k candidate checks |
| web | the settling loop (77%): 36 passes, each re-checking the whole lane network |
| windbreak | drawing the grove (52%): the sun keep-outs are rebuilt for every one of 908 groves, plus 12k spatial-index inserts |

> **What this means for bigger settlements**
>
> You're right that it won't hold up. Each check is cheap; the cost is in the shape:
>
> - **Re-checking everything after each addition.** The way tree, the web's settling passes and the cell merges each redo
>   the whole check every time something is added. Those are the quadratic parts, and they would dominate in a village or
>   town.
> - **Rebuilding things that don't change.** The house layout geometry and the sun keep-outs are recomputed per call when
>   they could be built once and reused.
> - **One straight scan with no index.** The bamboo strip check is the exact pattern `dev/performance.md` warns about.
>
> Making those incremental, cached or indexed should cut the 40-household time by well over half, and turn the growth from
> roughly quadratic into roughly linear in those parts.

## The GM's approval, 2026-10-18

> No thanks, I was just curious.  I don't want to contradict the research, I just wanted to understand the limitation.
>
> I think we should do all of this:
>
> - Re-checking everything after each addition. The way tree, the web's settling passes and the cell merges each redo the
>   whole check every time something is added. Those are the quadratic parts, and they would dominate in a village or town.
> - Rebuilding things that don't change. The house layout geometry and the sun keep-outs are recomputed per call when they
>   could be built once and reused.
> - One straight scan with no index. The bamboo strip check is the exact pattern dev/performance.md warns about.
>
> I don't think we need to re-check everything after each addition, and you've already proposed fixes for the others, so
> please file a feature for this and then make it happen.

("No thanks" declines rendering the 40-household scaling legs; "the limitation" is the hamlet band of 10-20 households.)
