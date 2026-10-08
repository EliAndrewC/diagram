# hamletgen/ - the scripted hamlet generator as a package

Split from the 2,913-line `hamletgen.py` monolith by feature 111 (constitution Principle X
clause 13: files stay at human scale - the cost being managed is context-window tokens), following
the `waterfields/` exemplar. **Load only the file the task calls for**; this
index is the map. `import hamletgen` still exposes the whole consumed surface via `__init__.py`
(star-import re-exports, clause 14), and the CLI is `make hamlet ARGS="..."`.

Read the package docstring in `__init__.py` first if you have not worked on this engine before: it
carries the doctrine paragraphs (WHAT THIS IS, THE ORDER IS THE DESIGN, DERIVE NEVER PIN) that
explain why the generator is shaped the way it is.

**Tiers share a library, and the rule is MOVE, never copy**: tier-agnostic machinery lives in
[`../sitegen/`](../sitegen/CLAUDE.md), which states the rule.

Three invariants the split does NOT touch:

- **`STAGES` in `driver.py` IS the pipeline contract.** The order is a design decision, shared with
  the DRAW ORDER map in [`dev/placement.md`](../../../dev/placement.md) - not something to be derived by introspection, and not
  something to reorder casually. The comment above the tuple says so at the point of change.
- **DERIVE, NEVER PIN.** Every position in this package is computed from geometry already on the
  map. A hard-coded coordinate silently becomes false when the thing it referenced moves; that is
  the project's standing rule and it is also what lets one script run at any size, seed or fall
  direction.
- **A ROLL DOES NOT REPORT ON ITSELF** (features 166, 287). Every rule about a map is proven at the
  placer that makes it, or is a recorded drop; that every house is reached is guaranteed by
  construction - the seating reserves a corridor from every door, the web draws it, and a settle that
  leaves a house unreached is refused (`ways/last_resort.py`).

## Look here when

| file | look here when |
|---|---|
| `__init__.py` | you need the package docstring, the `sys.path` bootstrap, or the re-export mechanism - star imports carry every submodule's public names, an aliased block carries the four consumed underscore names (guard: `tests/hamletgen/test_surface.py`); never add logic here |
| `__main__.py` | the CLI entry point (`make hamlet`) needs changing (it is a shim; `main` itself lives in `driver.py` because consumers reach `hamletgen.main`) |
| `consts.py` | a researched number needs reading or changing: `GROSS_ACRES_PER_HOUSEHOLD`, `POLDER_FABRIC` / `POND_LAYOUTS` / `DIKEPOND_CONVERSION` / `MANURE_FORMS` / `DIKE_CROPS` / `LEFTOVER_FORMS` (the dike-pond archetype and its knobs, feature 150), `LANE_CLEARANCE`, `SPUR_SETBACK`, `SUN_CORRIDOR_FT`, `CROP_MARGIN`, the archetype/bearing/wind tables (`FIELD_ARCHETYPES`, `ROLLED_ARCHETYPES`, `FALL_BEARINGS`, `WIND_VECTORS`, `CLUSTER_SHAPES`, `LANE_SKELETONS`, `PLOT_SIZES`), and the `Pt`/`Poly` aliases (which now LIVE in [`../sitegen/types.py`](../sitegen/CLAUDE.md) and are re-exported here, so `from .consts import Poly, Pt` still works). **Every constant carries the reasoning that fixed it** - keep it that way (the project's record-the-why rule). The bearing and wind tables are the standing candidates to move down into `sitegen` when the village tier makes them a second consumer |
| `consts_water.py` | the water constants, re-exported by name from `consts.py` (feature 316, the 1,000-line bar): the brook (`BROOK_*`), the intake and weir (`INTAKE_FORMS`, `WEIR_*`, `OFFTAKE_DEG`, `HEAD_RACE_LEAD`), the fords (`FORD_*`), `OFFTAKE_LADDER`, `SINKS` and `POND_SETBACK_LIMIT` - import them from `consts` |
| `plan.py` | the caller-facing spec or the derived plan: `HamletSpec` (what a pool `.gen.py` writes), `SitePlan` (everything derived from it), `plan_site`, `canvas_for`, `offtakes_for` (the wind is `DEFAULT_WINDWARD` unless the spec declares one - feature 261) |
| `clearance.py` | the fabric index (feature 138): clearance tests that measure only what is near, so the lane router asks an index rather than walking every lane per lattice cell. Geometry predicates and measures live in the shared [`../sitegen/geom.py`](../sitegen/CLAUDE.md) |
| [`water/`](water/CLAUDE.md) | STAGES 1-2 - the irrigation skeleton, the brook that feeds it, and the field it shapes (`stage_water_frame`, `stage_field`, `stage_polder`, `stage_waterward`, `fit_field`, `fit_polder`, `feed_brook`). Read its index, then load one file |
| `sink.py` | STAGE 3 - where the runoff goes: `stage_sink`, the tameike derived from the drain outfall, `drain_outfall`, `drain_heading` (which measures over `GATE_FLOW_SPAN`, the gate's own 40 px chord - read its docstring before touching the offmap route search, it is where a 76 deg disagreement with `drainage_junction_smooth` came from), `edge_run`, `pond_clear_of_crop`, `pond_setback` |
| `cluster.py` | STAGE 4a - where the settlement sits: `seat_cluster` (the 背山面水 margin band), `below_drain`, `back_fouled`, and the spur helpers `_fork_spur`, `_arm_hit`, `_arm_crossing_accidental` |
| [`ways/`](ways/CLAUDE.md) | STAGES 4b and 5b - the lanes, the track and what makes a path legal, as LAYERS bottom-up so every reference points backwards. **The two stages and the order between them are the whole design**; `web.py` and `track.py` hold them. Read its index, then load one file |
| [`homesteads/`](homesteads/CLAUDE.md) | STAGES 5-6 - the houses and what stands among them: the seating, the bamboo strip, the farmstead fixtures (`FIXTURE_BANDS`, and `HamletSpec.fixtures_min` - at least N of a kind, feature 133 T61), the wells, `stage_homesteads` and `stage_appurtenances`. Read its index, then load one file |
| [`hinterland/`](hinterland/CLAUDE.md) | STAGE 7 - the ground between everything: the content box and title pocket, open-ground parcels, bamboo seats, the shelter belt, the four stage entry points |
| `burial.py` | STAGE 6c (feature 273) - `stage_burial`: where the hamlet's dead lie - `hamlet_burial` keeps its one attested value, the village's ground, off the map (feature 280 M68: a hamlet's own ground is attested only in modern records); nothing is drawn |
| `pondstock.py` | STAGE 6b (feature 150 A3/A4) - `stage_pond_stock`: a dike-pond hamlet's pig sties on the ponds nearest the houses (`STY_SHARE` is a GUESS band; the duck pen retired by 269 B32, a modern form; the glyphs live in `settlement/farm_fixtures.py` `PondStockMixin`) |
| `frame.py` | THE CLOSING STAGES - `stage_crossings`, `stage_frame` (crop-to-content and the title), `stage_notice` (the kosatsuba, the last map FEATURE - feature 154), and `stage_labels` (the LABEL PHASE, the last stage of all - feature 157: every caption is seated here, against the finished map, because *"how we place labels will always depend on what else is on the map"*) |
| `driver.py` | the pipeline and everything that drives it: the `STAGES` tuple, `Report`, `build`, `generate` (builds ONCE, finishes, and reports what it seated), `cohort_specs` / `cohort` (fanned out across processes - `generate` IS the worker; `jobs=1` forces serial) and `main`. There is no re-roll (feature 287): the seating reserves every door's corridor, so a map is built once. `default_jobs` lives in [`../sitegen/jobs.py`](../sitegen/CLAUDE.md) and is imported back, so `hamletgen.default_jobs` still resolves |

## Adding a stage

Write the `stage_<name>(s, plan)` function in whichever submodule covers its theme (or a new one,
if it is genuinely a new concern), then add it to `STAGES` in `driver.py` **at the position the
draw order requires** - not at the end.

**Before/after the houses is a real decision, not a detail.** Feature 123 is the worked example: a
stage that RESERVES ground (a no-build corridor the houses pack around) belongs before
`stage_homesteads`; a stage that FILLS ground left over belongs after it. Getting that backwards
does not fail loudly - it just makes the settlement bigger and looser, and no check measures that.

Update the DRAW ORDER map in [`dev/placement.md`](../../../dev/placement.md) in the same change, and add the stage's
row to the table above.

Sub-stage helpers extracted from a long stage are named for what they do (`_seat_*`, `_fit_*`,
`_route_*`) and keep the extraction mechanical: same code order, same RNG draw order, same
float-operation order. The generator is seeded and deterministic, so any reordering shifts every
downstream coordinate.

## Reproduce a failure with the entry point that produced it

**`build()` is not `generate()`, and "nearest lane" is not "nearest lane IN THE NETWORK".** Rules are judged on the
FINISHED manifest, and several measure against the connected component containing the connector; a hand-rolled
diagnostic that stops at `build()` and measures to any drawn polyline answers a different question (one of feature
123's failing seeds was reported with zero unserved houses where the sweep said nine). So reproduce with the same entry
point: a cohort member is `make cohort N=1 SEED=<n>` (it rolls `Audit-<n>` and prints its spec on the header line), and
`make hamlet ARGS="--name Audit-<n> --seed <n> --households <h> --out <path> --no-render"` gives the same map with a
manifest to read.

## Verifying a change

The oracle is the rules, not byte-identity (maps may change - `l7r/diagram/CLAUDE.md`, "Performance"). For a change
that alters output, roll a cohort (`make cohort`) and read its verdicts, regenerate the pool hamlets (`make maps`), and
run the review checks the change's occasions owe (`docs/reviews.md`).
