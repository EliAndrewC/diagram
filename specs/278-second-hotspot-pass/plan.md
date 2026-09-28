# Implementation Plan: the second hotspot pass

**Branch**: none (main, clone `diagram-inashiro`) | **Date**: 2026-09-28 | **Spec**: [spec.md](spec.md) (FAITHFUL, round 3)
**Input**: [spec.md](spec.md), [research.md](research.md), [request.md](request.md)

## Summary

Fifteen requirements in four kinds. (A) The exact removals - the router's lazy lattice, the doorstep hoist, the
footbridge segment index, the wells re-sort, the field's plot index and projected threads, the notice board's indexes,
the windbreak's one grid, the page's bucket index, the finish of the kept attempt only: each index PRUNES and the
existing exact test DECIDES (`dev/performance.md`), each proved by an equality test against the old form, and the pool
manifests they touch come out byte-identical. (B) The two moving changes - the envelope refusal (FR-005) and the
vectorized commons (FR-008) - held to feature 276's FR-006 condition in full. (C) The tooling. (D) The measurement.

## Technical Context

**Language/Version**: Python 3.14, shapely 2 and numpy (already dependencies).
**Primary Dependencies**: none new.
**Testing**: pytest through `make`; the harness `harness.py` (`make spec-harness`), before-figures from a detached
worktree of `ac01ffe2d` (`/tmp/base278`), after-figures from the clone, back to back.
**Constraints**: every gate rule on every live map; the 100% coverage floor; files under 1,000 lines.
**Single-artifact target**: each engine piece is proved on its unit tests and on the map it moves most (named per
piece), then across the pool through `make done`.

## Performance bookends (constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `278-start` | 27.8 s | 6.8 s | 7.6 s | taken 2026-09-28 in the base worktree (observed 2026-09-28, method: `make perf LABEL=278-start` in `/tmp/base278`, log copied into the clone) |
| after | `278-end` | | | | taken before the push |

## Constitution Check

- **VI (performance)**: bookends above; `make perf-report AGAINST=278-start` before the push.
- **X clause 15 (index once, ask per candidate)**: every piece of (A) is this clause, the index built before the loop.
- **XII (research)**: every task is `research: rendering` - no physical claim changes; FR-005 enforces the engine's
  existing reach rule at the placer, FR-008 changes where random marks land at the same density.
- **XIII (no regressions)**: the base worktree is the baseline; `make cohort N=24` before (21/24, the three residue
  seeds of feature 276) and after.
- **XIV (fix where found)**: FR-005 is a placer defect fixed at the placer; anything else found is fixed in this work.
- **XVI (the literal thing)**: every FR as written; no exceptions.

## Design

### A1. The router's lazy lattice (FR-001, `hamletgen/ways/route.py`)

`free` and `band` become dicts filled on first ask (`is_free`, `in_band`), asked by the same three conditions in the
same short-circuit order; the start and goal cells are pre-set free as before; `in_band` is asked only of cells the
condition has already found free, as the whole-box set was built from free cells. **Test**: a fixture of route requests
recorded from one Kashikawa roll on the base (inputs, and the base router's outputs) - the new router returns the
recorded paths exactly; plus the harness's cell-test counts.

### A2. The doorstep index hoisted (FR-002, `hamletgen/ways/serve.py`)

`fabric_index(hard, WEB_HARD_GAP, passable, FOOTPATH_FABRIC_GAP, water, 14.0)` is obtained once per house before the
target loop: `hard` and `water` are parameters never mutated in `_serve_stragglers`, `passable` is built once per
house, so the memo returned this same index for every ask. **Test**: a spy on `fabric_index` in one straggler pass -
one doorstep request per house served, not one per ring point.

### A3. The footbridge segment index (FR-003, `settlement/city/bridges.py`)

`channel_footbridges` builds a `PointGrid` of every other watercourse's segments (box, owner polyline, owner width)
once per pass; `_widen_for_confluence` asks it for the deck quad's box widened by the test's 3 px reach, skips its own
polyline by identity as before, and runs `quad_hits_seg` on the hits only. `under` is a max, so order is immaterial.
**Test**: random quads and watercourses - the indexed widening equals the scan.

### A4. The wells re-sort (FR-004, `hamletgen/homesteads/wells.py`)

The pool is re-sorted only when `placed` has grown since the last sort; `_neighborhood` and `_in_belt` are cached
per seat (neither reads `placed`). A pass that places nothing leaves the order the next pass reads - the popped head
removed, the rest still sorted. **Test**: the key-evaluation count on Kuwabata, and Kuwabata and Kashikawa's wells
byte-identical (the manifest comparison).

### A5. The field (FR-007, `waterfields/carve.py`, `waterfields/frame.py`)

The hem pass's `inside_any` asks a `PointGrid` of the plots' boxes, built at the start of `_hem_pass` and EXTENDED with
each hem plot the pass appends to `plots` inside its own loop (later drain samples must see those - a grid built once
would miss them and hem the same place twice), then `_pip` on the hits (any-of is order-free). `_at_f` reads the
polyline's fall values from a cache OWNED BY ONE `_carve` CALL - set up at its start, cleared at its end, each entry
holding its polyline object alive so no id can be reused while cached; the threads are not changed inside `_carve` (the
march and clip finish before it starts) - and keeps the same first-segment-in-order walk over those values, so a
non-monotone polyline answers as before. **Test**: equality of both against the scans over random plots and threads, a
hem pass whose appended plot covers a later sample included; the field's plots byte-identical on Sawada.

### A6. The notice board (FR-009, `settlement/structures/fixtures/siting.py`, `settlement/houses.py`, `settlement/_geom/overlap.py`)

`off_every_bed` asks a segment grid of the way beds (each segment's box widened by its half-width plus the board's
reach); `_hard_clear` asks a `PointGrid` of the hard polygons' boxes, rebuilt when `_hard_cache_key` changes, in list
order; `quad_hits_poly` tests only the polygon vertices inside the quad's box and the polygon edges whose box meets
it (a vertex outside the box cannot be inside the quad; an edge whose box misses cannot cross it). Its FIRST stage - a
quad corner inside the polygon - keeps the full point-in-polygon test over every edge, unchanged: containment is not
local to the quad's box. **Test**: equality of each against its scan (a quad wholly inside a large polygon included);
Inashiro's and Sawada's board seats byte-identical.

### A7. The windbreak's one grid (FR-010, `settlement/homestead_parts/grove_blocks.py`)

The grove's static keep-out families (`hard`, `local`, `lane`, `inside`'s complement is left as the ring test it is)
are filed into one `KeepoutGrid`, tagged per family, so a candidate reads one cell and loops once over what it holds;
each family's own predicate decides, as 218 did for the scatters. `too_near` (which changes as clumps land) keeps its
own grid. **Test**: for random points, the combined answers equal the separate families'; the grove's clumps
byte-identical on Kashikawa and Inashiro.

### A8. The page's bucket index (FR-011, `interactive/page.py`)

A bucket's `extents` and `skip` lists each carry a grid of their boxes (a disc filed by its box); `_refused` asks the
grid for the element's box and runs `_hits` on the hits; an unreadable extent (`None`) still marks the bucket blocked or
refuses as before. **Test**: equality of `_refused` against the scan over random extents; the pages byte-identical.

### A9. Only the kept attempt is finished (FR-006, `hamletgen/driver.py`)

`_roll` builds and self-reports (the unreached seats are read before any finish) but no longer finishes; the retry loop
chooses the kept attempt as now, and that one is finished once - to `out_base` or to scratch. **Test**: a stubbed build
that strands a house on attempt 1 - the finish runs once, on the kept attempt.

### B1. The unreachable-seat refusal (FR-005, `hamletgen/homesteads/boundary.py`)

**Mechanism**: the homestead ground test refuses a house whose CENTER stands more than `WEB_REACH_FT` inside the ground
no way may be drawn on - the union of what `stage_web` hands the router as hard (`hard = [plan.envelope, *crops,
toe, *wet]`, `ways/web.py`) inflated by `WEB_HARD_GAP`, the margin every web lane keeps off it (the track's
`PathChecker` keeps off the same crop). A way stands outside that union, so its nearest point to such a house is more
than `WEB_REACH_FT` away, and `unreached_houses` - a distance test at `WEB_REACH_FT` against the served lanes - must fail
it: the refused seat is one the reach rule is certain to fail, and no other. Built once per seat stage from the ground
known at seating (the envelope and crops; the toe band where `toe_band()` is already asked before it is drawn; a marsh
drawn later is simply not in it, which only refuses less), with the depth read from a prepared shapely geometry.

**Measured before choosing** (observed 2026-09-28, method: `build()` of all five pool hamlets, each house's center
tested against that union and its depth read): Sawada's stranded house stands 157.1 px deep; every other house on every
pool map stands outside the union entirely. So Sawada's first roll seats elsewhere, and no other pool map can move.

**The narrowing, recorded**: FR-005 is answered for seats that are unreachable BY CONSTRUCTION - deep in hard ground. A
seat the web cannot reach for any other reason (hemmed in by other steadings' fabric, say) is still caught only by the
roll's self-report after the build; `hamletgen/driver.py` records why reach is not tested at seating in general (a
hand-rolled reach measure was tried and was wrong on five of six seeds). **Class**: map drawing convention - no new
rule: a subset of the seats `farmhouses_reach_a_way` already fails is refused before the build instead of after it.
**Test**: a seat deep in the union is refused; one at the union's edge (within reach) and one outside it are not;
Sawada builds once and seats 19; Sawada's research entry gives its houses, paddies and ways before and after.

### B2. The vectorized commons (FR-008, `settlement/land/cover.py`)

The static keep-outs `_sparse` reads - the ring, the `KeepoutGrid`'s rings (with the crop pad), segments, rects and
circles, the crescent ponds, the pond - become one prepared shapely geometry per glyph family (the family's `lean` a
buffer), and a family's throws are drawn as a numpy batch from a generator seeded as the Python stream is now, tested
with `shapely.contains_xy` in one call, thinned by the feather and the soft ramps in numpy. The loop keeps its per-
family target counts. **Test**: a compliance test - every mark the new scatter keeps passes the old `_sparse`'s
deterministic keep-out conditions - and a density test - each family's mark count within `5%` of the old scatter's on
the pool maps. The marks move (the Decisions row in the spec).

### C. Tooling (FR-012 to FR-014)

- **FR-012**: `make map GEN=<the reference>` stops rolling the map twice - the render roll files its entry in the roll
  cache with the render, so the gate's reference check that follows reads it as a HIT (the implementation reads the
  `map` and `_reference` recipes first and takes whichever of the two orderings the cache allows). **Proof**: the
  build count of one `make map` on the reference (the census or a counter), one before `REGENERATED`, and the reference
  line reading `[HIT ...]`.
- **FR-013**: the page records a hash of the class registry it was plated from; `sync-with-main.sh sync-in` re-plates it
  (`make placement-stages`) when that hash differs from the clone's registry after a merge. The test is unchanged - it
  still reads the page a reader opens - so a class genuinely missing still turns it red (a planted test).
- **FR-014**: the equality test's oracle runs the whole-text pattern over each LINE holding `.md` - a token contains no
  newline and the pattern's lookbehind and `\b` read a newline as they read any non-token character, so the lines
  yield exactly the whole text's tokens - over every tracked text. A planted token test keeps the proof that it finds.

### D. Measure, sweep, record (FR-015, SC-001, SC-013, SC-014)

`measure.py` writes the after-keys from `make spec-harness` into `measurements.json` with its command; the pool's
manifests are compared against the base's (a byte comparison for the exact pieces, the houses/paddies/ways counts for
the moved maps); SC-013's scenarios beyond the pool - the rescue-rounds scenario and the 10- and 20-household toys
(`tests/hamletgen/test_homesteads.py`) - seat at least as many houses as on the base, measured on both; `make cohort
N=24`; `make perf LABEL=278-end` and `perf-report`. `dev/performance.md` gains the after-profile's residue with its
levers priced - per stage, the finishing's external-renderer wait (4.7 s profiled over three finishes, R2) and the
rest of the durations list among them.

## Verification per piece

| piece | proves it | then |
|---|---|---|
| A1-A9 | its equality test; the map it touches most regenerated byte-identical | `make done` |
| B1 | the refusal test; Sawada rolled once; Sawada's research entry (houses, paddies, ways before and after) | `make done`, cohort, the rescue scenario and the toys |
| B2 | compliance and density tests; each map regenerated and read | `make done`, cohort, research entries before/after, the rescue scenario and the toys |
| C | each planted test | `make quick` |
| D | the harness back to back; SC-001 to SC-014 | the push |

## Complexity Tracking

None: every piece is an index, a hoist or a vectorization of an existing loop; no new rule.
