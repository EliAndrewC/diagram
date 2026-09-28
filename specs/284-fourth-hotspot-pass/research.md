# Feature 284 - research

## R1 - The measurement (2026-09-28, main `5f15c65bd`: 281 and 282 landed; first taken at `f52ed6aa8`)

**Method.** `measure.py before`, in the detached worktree `/tmp/base284`: each pool hamlet rolled three times unprofiled
with every stage timed (the fastest kept), once writing its svg and page, once under cProfile (saved to
`/tmp/m284/before`), and once under `sys.monitoring` counting every call beneath each mechanism's entry functions
(281's buckets plus this pass's: `router`, `field`, `notice`, `bamboo`, `page`, `edge_scan`). The load is recorded at each
run's start and end. Every figure is in `measurements.json` as a `before-*` key.

**The roll.** The five pool hamlets take 32.168 s between them (m:before-pool-roll-s, load 3.1 -> 7.8), at `5f15c65bd`. At
`f52ed6aa8`, before main merged feature 282, they took 27.62 s at load 3.7 -> 3.2 (observed 2026-09-28, method: `measure.py
before` in that worktree) - the difference is the threshing yards' mats (R3). By stage, summed over the five: the
field is the largest, then the ways (`stage_web`), the hinterland, the homesteads, the windbreak and the notice board.
Sawada's field alone is 2.939 s (m:before-sawada-stage-field-s) and Kashikawa's ways 1.448 s
(m:before-kashikawa-stage-web-s).

**The profile, by lever** (profiled seconds summed over the five; profiling inflates Python about 2.4 times, so these
rank, they do not predict):

- **The router** (`_route`): Dijkstra's lazy cell tests and heap (`is_free`, `in_band`, the heap: about 5 s), the
  string-pull's link tests (`_clear_link` from `_route`: 2.5 s) and the fabric-index memo KEY rebuilt per link (`_key`,
  3,768 builds, 1 s) though every link of one route asks the same index. The bucket's calls: m:before-kashikawa-b-router-total,
  m:before-sawada-b-router-total. Dijkstra settles every cell nearer the start than the goal; a search toward the goal
  settles a fraction of them and returns a path of the same cost - where two routes cost the same, possibly the other one.
- **The field's size search** (`fit_field`): 13 carves over the four comb fields (Inashiro and Sawada 4 each,
  m:before-inashiro-b-field-carve-comb, m:before-sawada-b-field-carve-comb). A trace of every carve (observed 2026-09-28,
  method: a probe wrapping `carve_comb` and `_fit_at_aspect` on the four rolls) shows the shape: on Inashiro, Kashikawa and
  Sawada the first guess falls short, and the search then carves the LARGEST fan the aspect can draw (feature 145's
  saturation probe, the multiplier at the bracket's top - Inashiro's fall 2727 px against a first guess of 1240) before
  converging on a predicted size. That probe is the costliest carve of the search and lands nowhere near the target; it
  exists for a fan the envelope clamps (cohort seed 47), which the carve after it can detect by its acreage not growing.
  The seam closing (`close_seams`: 5.3 s over four) and the carve's own geometry are the rest.
- **The page writer** (`write_html`: 7.1 s): every classed record string is parsed by regex to cull its off-map ink
  (`drop_offmap`, 1.9 s), parsed again to merge its primitives (`wrap` -> `merge_primitives`, 3.1 s), again for the marks'
  hit regions (`marks_region`, 1.3 s) and again for the widened hit layer. The same text, the same elements, four parses.
- **The notice board** (`place_kosatsuba`): every candidate verge seat is fitted and its caption placed before the seats
  are compared - m:before-inashiro-b-notice-total, m:before-sawada-b-notice-total.
- **The bamboo seats** (`bamboo_seats`): the samples it tests per seat - m:before-kashikawa-b-bamboo-total,
  m:before-mizuguchi-b-bamboo-total.
- **Whole-ring `edge_dist`** (`_crosses_fabric`, `_trim_to_service`, `push_clear_of_fabric`): each walks every edge of every
  fabric polygon per point - m:before-kashikawa-b-edge-scan-total, m:before-kuwabata-b-edge-scan-total.
- **The brook toll**: after 281's 3 x 3 grid, still 590,253 cell lookups on Kashikawa (m:before-kashikawa-b-toll-dict-get).

- **Four more slow stages with no lever yet** (the GM's general instruction takes them in, FR-011), each bucket counted
  apart since buckets nest exclusively: the windbreak's fill and its draw (m:before-kashikawa-b-grove-total,
  m:before-kashikawa-b-grove-draw-total - the draw's crown test walks every nearby and every drawn crown per crown, 713,438
  comparisons over the pool in the profile), the seam closing (m:before-sawada-b-seams-total - shapely unions and buffers
  in `_absorb` and `_plant`, already batched by 276), the commons' scatter (m:before-kashikawa-b-commons-total) and the
  finish's blade flush (m:before-sawada-b-flush-total - every blade formatted to a path, which the page then re-parses).

**What the GM allowed** (request.md): a lane taking the other of two equally short routes, plot boundaries shifting within
the field's acreage tolerance (`fit_field`'s `tolerance`), a tied board seat resolving the other way, bamboo clumps sitting a little differently -
and in general any change of that nature that makes a map significantly faster. Not a change to what a settlement is,
and not a broken rule.

## R2 - Where the page's parsing goes, by class (2026-09-28)

**Method** (observed 2026-09-28, method: a probe timing the page's `wrap`, `drop_offmap` and `marks_region` per call and
attributing each to its string's feature class, over one full generate of Kashikawa and one of Sawada): 1.597 s of parsing
in all. The scrub and rough grazing took 41.4% (10,971 elements, 4.2 million characters), the marsh 18.5% - the two classes
whose ink is the deferred blade and mark buckets the finish flattens (`_blade_groups`, `_mark_groups`). The page's own
`marks_region` - the scrub's hit region, drawn from the scrub's marks (`HIT_FROM_MARKS` holds only the scrub) - took
another 23.2% (a probe attributing by string identity missed it, since that pass reads the marks by list; the review's
re-measurement placed it, observed 2026-09-28, method: a probe timing `marks_region` itself). No other class took more than 5.0%: the
bunds 5.0%, the paddies 3.0%, the windbreak 1.9%, the bund beans 1.3%, every other class under 1%, together about 17%. So the two
structured classes hold about 83% of the page's parsing in all (41.4 + 18.5 + 23.2), and carrying the structures the
engine already makes to the page reaches that, and what is left is spread
thin over every other producer - which one parse per string covers without rewriting each producer's drawing code.

## R3 - The threshing yards, after main merged feature 282 (2026-09-28)

Main merged feature 282 (the threshing yard's mats and racks) while this work was specified, and every pool manifest moved,
so the base was re-taken at `5f15c65bd`. The homesteads stage went from 0.357 s to 1.806 s on Inashiro (m:before-inashiro-stage-homesteads-s), 0.496 s to
2.313 s on Kashikawa (m:before-kashikawa-stage-homesteads-s) and 0.497 s to 1.859 s on Sawada
(m:before-sawada-stage-homesteads-s) - the first figure each from the `f52ed6aa8` run (observed 2026-09-28, method:
`measure.py before` in that worktree). Kashikawa's mats bucket counts 14288475 calls (m:before-kashikawa-b-mats-total). The profile names it: `mat_cells` took 15 profiled seconds over the 54 yards of three
maps, 10 million `hypot` calls - it tests every quarter-foot grid point of the yard against the floor's outline (point in
polygon, then the distance to each edge), and it counts, for every lattice at every offset, the seated mats one by one in
Python; `_lay_by_hand` then tests each mat's outline against every laid and every upcoming mat's (`_quad_gap`, 34,070 calls).
Both are static geometry asked per candidate: the grid's test can be decided in arrays (surely inside the inset floor,
surely outside it, the scalar test in the band between), the lattice counts are sums of shifted slices of one boolean
array, and two quads farther apart than the clearance need no `_quad_gap`. The mats come out the same.
