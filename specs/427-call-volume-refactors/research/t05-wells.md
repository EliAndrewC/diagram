# T05's measurements: the wells without the cubic term (US3)

**Load this file when:** you check what T05 removed, or re-measure it.

Observed 2026-10-26. Counts from `make perf-fanout STAGES=lane_wells` (seed 39 at 20 and 40 households unless named); times
from `make perf LABEL=427-T05c SCALING=1` (`dev/perf-log/20261026T192756Z-427-T05c-diagram-backlog.json`) against the
`427-start` bookend (`dev/perf-log/20261026T184511Z-427-start-diagram-backlog.json`), the same machine, minutes apart.

## What changed, in the order it was measured

| step | what | lane_wells @40 (seed 39) |
|---|---|---|
| before | the T01 survey | 22,620,000 (exponent 2.24) |
| D5 | `PoolScore`: the sort key for the whole pool in array operations; `_in_belt` once a seat | 16,408,424 |
| a | `SeatSweep.walls`: the wall gap once a seat, as arrays, dwelling by dwelling within reach | 9,465,555 |
| b | a seat `well_at` refused is not asked again (refusals only grow while wells are added) | - |
| c | `stage_lane_wells` keeps the belt, the seat sweeps, the verge test and the refusals for its eight `seat_wells` calls | 2,580,249 (exponent 1.40) |

At 20 households: 4,790,000 -> 978,547. Seed 25 at 40 households, the slowest: 19,544,940 after D5 and a, 3,706,312 after c.

## US3's two tests

- **The ranking chain** (`most_served_after`, `worst_after` and the per-seat key under the sort, 2.19M inner calls): gone - no
  chain of 50,000 or more under the sort remains; the `wells.py:151 <lambda>` and `most_served_after` chains are absent from
  every report after D5. **Met.**
- **The slowest seed's lane_wells time** (bound 0.5 s, a GUESS): seed 25 at 40 households 6.67 s -> 0.72 s; seed 39 3.15 ->
  0.49 s; seed 47 0.37 -> 0.13 s. **Not met on seed 25** (0.72 s against 0.5 s). Under cProfile seed 25's stage is now
  `seats` 0.44 s, `well_at` 0.37 s (1,705 calls, from 21,093), the pool's sort 0.16 s. **Waived** by the round arbiter
  (`ask:427-T05-wells-time`, accept, 2026-10-26): the 0.5 s is a GUESS, timings gate nothing (the GM 2026-10-26, T03), and
  SC-003's one second at 40 households is met; the verge test's vectorization and a `well_at` prefilter are an optional
  `found.jsonl` row, taken up only if the 427-end bookend shows lane_wells at 1 s or more or the call-count watch flags it.

## The maps

`make maps` after c: no pool manifest moved against HEAD (Mizuguchi and Sawada regenerated, both identical). The homesteads
tests' oracle (`test_the_sweep_keeps_the_seats_the_loop_kept`) holds the vectorized wall gap to `well_gap_to_dwellings` on 30
random hamlets.
