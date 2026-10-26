# Hotspots: cheap wins (cache keys, point-at-a-time access, record reads, one mislabel)

**Load this file when:** you want the smallest, most contained changes first: caches whose key costs a scan, a
point-at-a-time read beside an existing batch version, and the cost of reading manifest records.

Counts are seed 39, 20 households -> 40 (`fanout-2026-10-26.txt`). Paths are under `l7r/diagram/`.

## C1. `clearance.ring_index`: the cache key walks the whole ring

`hamletgen/clearance.py:85 ring_index` caches a `RingIndex` per ring, keyed by
`tuple((float(p[0]), float(p[1])) for p in pts)`. The key is rebuilt on every call (genexpr `:87`), so even a hit walks
the ring.

| | @20 | @40 |
|---|---|---|
| calls (mostly from `ways/geom.py:209 ring_within`) | 27.8k | 70.6k |
| key steps | 144k | 361k |

`ring_within` also copies the ring first (`list(poly)`).

**Direction:** key the cache on the ring's identity or a version the owner carries (the manifest record's id and the field
version). Alternatively, let callers hold the `RingIndex` they were handed.

## C2. `ways/keeper.py` `pts_key`: the same pattern in the lane-law cache

`ways/keeper.py:25 pts_key` hashes a run's points into a tuple on every `keyed` call (`:39`, the `kept` decorator over
`lru_cache`).

| | @20 | @40 |
|---|---|---|
| keys | 12.8k | 41k |
| steps | 91.5k | 229k |

Mostly from `law.py:438 doubled_tails` -> `tails.tail_doubled`.

**Direction:** key lanes by an id and an edit counter maintained by the web, not by their coordinates.

## C3. `Region.taken`: one PIL pixel per call beside `taken_many`

`settlement/_geom/region.py:131 Region.taken` reads `self._im.getpixel((i, j))`. That costs a PIL `load()` per call:
26.5k -> 36k calls in `close_belt_gaps` via `grove_blocks.static_clear` -> `taken_by`. `taken_many` (just below it) takes
numpy arrays.

**Direction:** batch the callers, or hold the raster as a numpy array (`Region.array()`) and index it.

## C4. Scalar primitives beside their vectorized version

`settlement/_geom/primitives.py:59 seg_dists` vectorizes `seg_dist` over points x segments. About 2.2M scalar `seg_dist`
calls remain at 40 households, inside the chains in `hotspots-pairwise.md` and `hotspots-recompute.md` (wells legality
965k, lane pairs 955k, yards 174k, admission 108k). This is not separate work; it is the tool for those chains.

## C5. `CanopyArea`: area bookkeeping on a 2 ft raster (not an index)

`settlement/_geom/indexes.py:321 CanopyArea.add` marks every 2 ft cell under a crown in a Python set.

| | @20 | @40 |
|---|---|---|
| crowns added (windbreak) | 6,103 | 11,071 |
| `set.add` calls (windbreak) | 618k | 1.05M |

That is about a third of the windbreak stage. Users: `homestead_parts/stands.py:302`, `wood_goal.py:72`,
`hinterland/stages.py:506`. The estimate agents called this a "too-fine index"; it is the area counter that fills a copse
to an area goal (269 B26).

**Direction:**
- a numpy boolean raster with each crown's disc written by slicing;
- or count the area at a coarser cell sized to the crowns, if the area goal's tolerance allows it (check the research claim
  on 269 B26 first).

## C6. Reading manifest records

Records are dicts read as `float(h["x"])` at every use, inside the loops above. Seen as builtin volume, not as any one site:

| builtin | stage | @20 | @40 |
|---|---|---|---|
| `dict.get` | windbreak | 283k | 906k |
| `isinstance` | windbreak | 98k | 284k |
| `len` | lane_wells | 355k | 1.8M |

**Direction:** not a refactor of its own. When a family is batched, pull the coordinates it needs into an array once at the
top of the stage. Not traced to sites; the survey's builtin rows are in `fanout-2026-10-26.txt`.
