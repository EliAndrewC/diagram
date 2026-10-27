# The search and its ceiling - and the four others'

Measured 2026-10-27, seed 25 at 40 households (nucleated, the reference spec).

## The lattice search (`hamletgen/ways/route.py`, `lattice_search`): `make perf-share MODULE=l7r/diagram/hamletgen/ways/route.py STAGES=web PROFILES=dev/perf-raw/20261027T205431Z-seed25-web.prof`, and the profile's call tree

The web's router, Dijkstra over its 10 px lattice, three routes (`_route` from `_lay_skeleton`): 0.428 s cumulative of the
web's 1.90 s under cProfile (22%) - its own loop 0.171 s, the memo dictionaries' `get` 0.107 s (1.13 million calls), the
cell tests `is_free` 0.086 s (37,740) and `in_band` 0.048 s (35,696), the heap 0.016 s; 35,094 cells expanded, about 11,700 a
route.

Its batched form - every cell's verdict asked at once - is the design feature 278 withdrew: the box was judged whole before
the search began, 358,398 and 174,118 tests on Kashikawa, "most of them for cells Dijkstra never reaches"
(`route.py`, the comment above `is_free`); asked of the box as an array it would want an array form of the fabric index's
`fouled`, which does not exist. A* toward the goal was tried and withdrawn too (feature 284, research R6: not faster beyond the
noise, and it moved maps).

## Each named search's ceiling, unprofiled

The stage's cProfile inflation is its profiled total over its unprofiled time - homesteads 4.47 s / 2.20 s, web 1.90 s / 0.83
s (the unprofiled times: `make perf-ab A=HEAD~1`'s stage rows, A's best, measured 2026-10-27 on the engine these profiles were
taken of) - and a search's ceiling is its cumulative time over that, against the 7.01 s roll: what the roll would save were the
search free.

| search | stage | calls | cumulative, profiled | inflation | ceiling, unprofiled | of the roll |
|---|---|---|---|---|---|---|
| `lattice_search` | web | 3 | 0.428 s | 2.29x | 0.187 s | 2.7% |
| `_first` (the fixture seats) | homesteads | 8,030 | 0.392 s | 2.03x | 0.193 s | 2.8% |
| `_samples` (the site boundary) | homesteads | 8,078 | 0.232 s | 2.03x | 0.114 s | 1.6% |
| `flood` (the gaps' ways) | homesteads | 1 | 0.177 s | 2.03x | 0.087 s | 1.2% |
| `within_reach_of` (the privy's reach) | homesteads | 159,645 | 0.143 s | 2.03x | 0.070 s | 1.0% |

Each is under the quick form's floor (4%, `make perf-ab AA=1`, measured 2026-10-27): no change to any one of them - even its
deletion - can be told from the run's own noise in the quick A/B. Together they are about 9% (and `_first` runs inside the
envelope probes trial 439 measured, so they overlap).
