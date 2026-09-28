# Feature 276 - research (Phase 0)

Every figure below comes from `harness.py` (`harness-before.json`) or a probe recorded in `measurements.json`
under the key named beside it. This is a performance feature: no element changes what a map asserts about the
world (constitution XII's opening bookend has nothing to ground - see R8).

## R1. The baseline (harness.py, unmodified code)

- Four AST-scanning tests alone: 1.23 s to 1.87 s each (m:before-ast-tests-min, m:before-ast-tests-max).
- Five named record tests alone: 17.22 s summed, the slowest 4.47 s (m:before-record-tests-sum, m:before-record-tests-max).
- Rescue-rounds homestead stage: 2.718 s, 46781 full fit tests, 10 houses seated of 20 asked
  (m:before-rescue-s, m:before-rescue-fits).
- The placement primitive at constant density: 0.0308 s per seated house at 60 seeds, 0.0586 s at 240
  (m:before-dense-60-per-house, m:before-dense-240-per-house) - per-house cost nearly doubles while the fit
  tests per house stay flat, so each fit test is getting slower as houses accumulate: the scans in R2.
- `close_seams` inside one comb build: 0.842 s to 1.018 s (m:before-close-seams-min, m:before-close-seams-max),
  most of each build.
- Track stage on Inashiro seed 4: 1.308 s, of which the path checks 0.966 s (m:before-track-stage-s,
  m:before-track-checks-s).
- Performance bookend `276-start`: 31.3 s over the reference seeds, median 7.7 s (m:perf-start-total,
  m:perf-start-median).
- Pool hamlets before (`pool-before.json`, read from the committed manifests): Inashiro 15 houses, Kashikawa 20,
  Kuwabata 16, Mizuguchi 12, Sawada 19 - each seats every household it asks for; all nucleated, all plain houses.

## R2. Why homestead placement is slow - two costs, both measured

**Which path (added by amendment 1).** `_toy_hamlet` never set the placer's own switch, so every figure first taken for
this section ran the DISPERSED spiral; fixed, both paths re-measured on the unmodified engine
(`harness-before-homesteads-both-paths.json`). The NUCLEATED path - every pool hamlet's - is cheap at hamlet scale: the
rescue scenario takes 0.16 s and seats 15 houses (m:before-rescue-nucleated-s, m:before-rescue-nucleated-houses), 240
seeds 0.395 s (m:before-dense-240-nucleated-s) - but its cost per house still grows from 0.0009 s to 0.0017 s between 60
and 240 seeds (m:before-dense-60-nucleated-per-house, m:before-dense-240-nucleated-per-house): the placed-house scans
below, which are the city's problem. The dispersed spiral - staged for the form `_SETTLEMENT_FORMS_WHEN_GROVES_WORK`
rolls - is the generate-and-test search the rest of this section measures.

**Decision** (revised after the plan reviews): a FREE-GROUND index - the static ground's surely-taken cells and the
placed boxes, updated as each house lands - asked for every seat's candidates before any is tested; behind it, on the
dispersed path only, a pre-screen by the fit test's cheapest exact conjuncts; and indexes for every scan of the placed
houses and of the static ground.

**What the probe found** (rescue scenario):
- Almost every question is new: 45368 distinct (house rect, placed count) keys among the 46781 fit tests
  (m:rescue-distinct-fits), so a cache of verdicts would answer almost nothing. Rejected: memoizing `_bundle_fits`.
- Almost every answer is NO: 46686 of 46781 are rejections (m:rescue-rejected). The first failing rule: the
  house on forbidden ground 33710 (m:rescue-reject-house-ground), the eave gap 3887 (m:rescue-reject-eave-gap),
  the side half - bbox, garden ground, placed-box overlap - 2536 (m:rescue-reject-side), the grove's ground 2270
  (m:rescue-reject-grove-ground), a sun rule 3276 (m:rescue-reject-sun), the yard's ground or the wall rule 1007
  (m:rescue-reject-yard-wall).
- `_bundle_fits` is a conjunction whose own docstring says it is order-independent, so testing its cheapest
  rejecting rules FIRST, and skipping the rest on a NO, returns the verdict the whole test returns - exactly.

**The linear scans** (read in `settlement/rolling/fit.py`, `hamletgen/homesteads/boundary.py`): per candidate,
`_sun_corridor_ok` walks every house record twice, `_gardens_sun_ok`, `_yard_sun_conflict` and
`_house_too_near_a_neighbor` once each, `_bundle_side_fits` and `_envelope_blocked` every placed box; and the
site boundary's `SiteCorridors.hit_points` checks every VERTEX of each nearby outline ring and every HOLE of the
outline for every one of the nine points. The first group grows with the houses placed (the density curve in
R1); the second is static geometry re-scanned per candidate - the shape `dev/performance.md` names.

**Alternatives priced**: a free-space raster that DECIDES seats ("the nearest cell that fits") was rejected: the fit
test's rules (sun corridors, the wall rule against the bund, the eave gap by rotated corners, the tread by the drawn
rake) are not a property of a cell. So the index PRUNES - it drops only candidates the exact test would refuse at a point
it holds as taken - and proposes the survivors in the spiral's own order, so a seat is still the nearest acceptable one.
Caching verdicts was rejected on the probe's evidence (almost every question is new).

## R3. Why seam closing is slow

**Decision**: compute once, batch per-piece work into shapely 2 array calls, and visit only the cells a pocket
touches.

**What the profile found** (cProfile of `test_comb_topology` seed 11 and `test_seams`): the cost is spread over
every step - `_visible_parts`, `_absorb`, `_unjog`, `_repair_crossing_rings`, `_plant`, the tint loop - each a
Python loop of small shapely calls on single polygons, so the per-call wrapper overhead is paid hundreds to
thousands of times per field. Concrete duplicates: `_plant` computes `k.buffer(-half)` twice for every kept
piece (two list comprehensions over the same pieces); the tint pass builds `Polygon(p["poly"]).buffer(0)` for
every plot twice (the median-area list and the loop). A normal comb plants about 20 pockets into 120 to 151
cells (a scratch probe, observed 2026-09-28, method: `_despike` and `_plant` wrapped in a probe test over
`build_comb` seeds 5 and 11), so the grid is not the normal cost - but one test's map cuts four pockets into
5544 cells, and a diagonal sliver would do the same on a big field, which FR-004's touched-cells rule closes.

**Alternatives priced**: rewriting the seam pass as a raster (paint and trace) was rejected - it would change
every bund's geometry class, not just its cost. Caching the whole `close_seams` result per field is what the roll
cache already does across runs; it does nothing for a cold build.

## R4. Why the track stage's path checks are slow

**Decision**: a `PathChecker` built once per `stage_track` from the geometry `path_violations` reads (the avoid
polygons, the pond, the brook and water segments), with every segment and ring in a `PointGrid`; the function
itself stays as the ORACLE for the equality test (FR-005).

**What the profile found**: 176 `path_violations` calls take 0.966 s of the stage (m:before-track-checks-s); each
walks every brook segment, every avoid polygon (`crosses_poly`) and every water segment (twice: the shallow
crossing and the crop-landing test) for every segment of the candidate path.

## R5. Why the four AST tests and the five record tests are slow

**Decision**: one shared, content-keyed parse per engine module per process, with a per-test text prefilter
where the property a test looks for cannot occur without a literal (`STAGES`, `del `, `import`); one scan of the
record per process for ids, words and `.md` tokens.

The profiles: each AST test walks 1.0 to 1.5 million nodes, re-parsing ~264 modules the other three also parse;
`test_every_link_in_a_record_page_resolves` re-reads and re-scans the TARGET page for ids once per link (544
regex scans for one page); the glossary test searches the whole joined corpus once per term variant; the two
`.md`-token scans run a complex regex over every tracked file, most of which contain no `.md` at all.

## R6. What "the settlement stays what it was" means here (FR-006)

The before counts are `pool-before.json`. After the engine changes, every pool hamlet must seat the same number
of houses as it asks for (all five do today), keep nucleated form and plain houses, and its paddy, flooded,
dry-plot and lane counts are reported beside the before counts; a paddy count moving more than a few percent is a
finding to diagnose, not a report.

**The result** (`pool-after.json`, written by `pool_counts.py` from the manifests the green gate of 2026-09-28 left):
every hamlet seats the households it asks for - Inashiro 15, Kashikawa 20, Kuwabata 16, Mizuguchi 12, Sawada 19 - all
nucleated, all plain houses, as before. Kuwabata is unchanged in every count. Paddy plots: Kashikawa 774 -> 786 (+1.6%),
Sawada 810 -> 804 (-0.7%), the rest equal; dry plots Kashikawa 22 -> 27, Sawada 28 -> 25; flooded plots equal on every
map. Lane records: Inashiro 11 -> 13, Kashikawa 14 -> 13, Mizuguchi 9 -> 10, Sawada 11 -> 14. The lanes move because
`seg_intersect` now bounds both segments: before, a candidate track crossing the infinite extension of a water or crop
edge was refused on a crossing that was not there, so the stage settled for another route - Inashiro's connector left
north and now leaves east through the cluster, with the web re-laid around it; read by eye, the same hamlet. The
Kashikawa weld that shipped a 0.88 deg hairline spur (the seam pass's reordered geometry produced it) was fixed at the
placer - `_weld_apex` reads the ring as recorded as well as deduped - not waived.

## R7. The regression baseline (constitution XIII)

`make cohort N=24` on the unmodified code in a detached worktree (`scratchpad/base276`), started 2026-09-28; its
result: 21 of 24 seeds pass the whole gate (m:cohort-before-passed); the three that fail - Audit-02, Audit-08, Audit-23 - fail
`scatter_frame_breach` only, the cohort's standing residue. The after-cohort must pass these same 21 or more, every
newly failing seed diagnosed.

## R8. Historical grounding

Nothing this feature changes asserts anything about the world: the same rules seat the same kinds of houses on the
same ground and close the same paddies. Where a seat, a seam or a track lands differently it is a different legal
answer to the same rules - the spec's Decisions Recorded classes both as map drawing conventions. The closing
bookend is the GM's own look at the regenerated pool (the GM, 2026-08-29: they read the maps themselves).
