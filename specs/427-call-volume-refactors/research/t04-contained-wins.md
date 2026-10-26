# T04's measurements: the contained wins (US2)

**Load this file when:** you check what T04 removed, or re-measure it.

Each count is seed 39 at 40 households, before from `dev/perf-log/20261026T164639Z-fanout-427-T01.txt` and after from
`dev/perf-log/*-fanout-427-T04a.txt` / `-T04b.txt` (observed 2026-10-26, method: `make perf-fanout HOUSEHOLDS=40 STAGES=...`; a
builtin's count read from the stage's `.prof` with `pstats`, since the survey starts no chain from a builtin).

| item | the chain's leaf | before | after |
|---|---|---|---|
| C5 | `set.add` in the windbreak stage (`CanopyArea.add`) | 1,052,833 | 0 |
| R6 | `_Frame.to_uf` under `grid_lines` -> `_falls` | 513,948 (all `to_uf`) | 83,038 (all `to_uf`, every one from `_f_at_u` under `drain_f`; none from `_falls`) |
| C1 | the `ring_index` key generator (`clearance.py:87`) | 361,036 | under 50,000 (gone) |
| C2 | the `pts_key` generator (`keeper.py:27`) | 228,843 | under 50,000 (gone) |
| R2 | the crop's shelter generator (`_knobs.py:827`) | 121,845 | under 50,000 (gone) |
| R3 | `_near_a_house` and its generator | 55,820 / 60,648 | under 50,000 (gone) |
| R5 | the union-find's `find` (`region.py:319`) | 108,709 | under 50,000 (gone) |
| C3 | `Region.taken` -> `getpixel` | 36,391 | under 50,000 (gone) |

Stage totals at 40 households: windbreak 3,925,050 -> 2,796,372; field 4,501,155 -> 4,176,895; web 11,052,045 -> 10,462,166;
hinterland 5,962,328 -> 5,595,875; homesteads 10,660,802 -> 10,119,232.

**The maps**: `make maps` then `make maps-moved` after each batch - "no pool manifest moved against HEAD", both times: every
change computed the same values, R3's `np.hypot` and R5's labeling included.
