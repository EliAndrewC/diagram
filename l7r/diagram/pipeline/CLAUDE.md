# `pipeline/` - how a pool map gets regenerated, cached, rendered and indexed

The BUILD side of the project. The other three sides are the drawing engines (`settlement/`,
`waterfields/`, `hamletgen/`, `compound.py`) and the by-hand
diagnostics ([`../tools/`](../tools/CLAUDE.md)). Drive it through `make` at the repository root:

    make map GEN=pool/hamlets/sawada/sawada.gen.py    # one map: regenerated, or CACHED when nothing it depends on changed
    make maps                                         # the pool, picking its own scope from how the last run went

| module | what it is | measured for coverage |
|---|---|---|
| `gencache` | the generation cache: the KEY, `store`/`load`, and `gate_obtain` (the gate rides this cache since feature 026) | no - a driver |
| `regen` | the ITERATION path: regenerate a map, or skip it when nothing it depends on changed | no - a driver |
| `rollcache` | the ROLL cache the gate tests ride (feature 135): `obtain` serves a keyed roll or produces and records it. **ONE ROLL PER SPEC** (feature 213, GM 2026-09-07): `hamlet()`, `report()` and `report_deps()` are three views of one `roll:<spec>` subject, produced in a child process (`_in_child("module:function", arg)` runs any module-level producer by name), shared across the run's workers behind a per-subject lock so the first wave waits instead of each rolling (`_share_lock`), and bounded to `L7R_ROLL_SLOTS` concurrent children (`_roll_slot`); the reference and Kuwabata are read from the POOL (`tests/gate/_pool.py`). A covered child starts coverage itself and switches to the requester's coverage context for the roll alone (`gencache.child_coverage`), because the incremental gate selects tests by those contexts and a roll under no context would select no roller. The roll census (`_census.py`, `ci/rollverdict.py`, the roster `tests/rolls.py`) proves at every gate that no spec rolls twice. `keyed_to(..., child=...)` is the same child for a patched roll | yes |
| `render_cache` | main's renders: a content-hash short-circuit so main regenerates its own renders from its own tip after the stop-work push | yes |
| `poolmaps` | the SINGLE source of truth for WHICH MAPS EXIST, in which tree, of which kind - `bundles()` for the walk, `classify()` for the kind | yes |
| `pool_index` | writes `pool/index.html`, the browsable index over the whole pool | yes |
| `record_build` | the record's site on the main checkout (feature 301): render-sync builds `research/site/` only when its STAMP - the record's files, the glossary's JSON and the engine modules the build imports - differs | yes |

## The two engine-tree walks must stay in step

`gencache.engine_files()` and `render_cache.engine_fingerprint()` are separate functions answering
the same question - "which .py files determine what a map comes out as?" - and they prune the same
way: `pool/`, `wip/`, `tests/`, `__pycache__`, dot-dirs and dot-files, plus any `test_*` directory
or `test_*.py` file. **If you change one, change the other**, and extend both ratchet tests
(`test_engine_files_prunes_the_tests_tree`, `test_engine_fingerprint_covers_and_skips`).

Two properties of that walk are load-bearing, and each was learned the expensive way:

- **It recurses.** A root-only listing silently stopped keying the cache on the main engine when
  `settlement/` became a package (feature 025), serving stale maps after engine edits. Nested
  packages count too - `settlement/fields/` (feature 112) is inside both walks, and a
  directory-shaped rule that dropped it would leave every map cached through an edit to the field
  engine, which is a quiet failure.
- **It prunes `tests/`.** Before the 2026-08-16 reorganization every test was a root-level
  `test_*.py`, so the name filter covered them all. Under `tests/` the helpers (`_builders.py`,
  `__init__.py`) match no name filter, and counting them as engine inputs would invalidate every
  map in the pool on any edit to a test helper. Same class of bug as the dot-file filter, which
  exists because the gate's own scratch drivers used to land in the project root and poison every
  concurrent key computation, so nothing ever hit.

Everything else here is still walked, including `tools/` and this package's own siblings. That is
deliberate conservatism: the cheap failure is regenerating a map that did not need it; the
expensive one is serving a stale map. `gencache` and `regen` exclude themselves (`_NOT_ENGINE`,
matched by basename) because the cache cannot be its own input, and `render_cache` excludes itself
for the same reason.

## Before you trust a cache change, audit it

`make cache-audit` (~10 min) perturbs a random numeric literal inside a `settlement/`
function, sweeps the pool with the cache and again with `--no-cache`, and demands byte-identical
artifacts. It never looks at the key, so it cannot share the key's blind spots. Since the gate
TRUSTS the cache (feature 026), this is the empirical backstop for the key itself - which makes
running it after a change here more important, not less.

What the key covers, the soundness argument and the concurrency cases are `gencache.py`'s own docstring; THE TRAP
(a miss rebuilds the entry against the tree as it is, so a trial of "does an edit to X invalidate?" needs the
baseline re-established - run until `CACHED` - before each trial) is [`dev/cache.md`](../../../dev/cache.md).

## `poolmaps.bundles()` - ask, do not glob (feature 161)

The pool is two trees, each `<tree>/<tier>/<map>/`: `pool/` for what is LIVE (scripted settlements
plus the Mode A compound plans that are hand-authored by design) and `legacy-hand-authored-pool/`
for the 19 FROZEN exhibits. **Everything that walks the pool calls `poolmaps.bundles()`**, saying
which tree(s) its job concerns.

No consumer globs, lists or greps the pool's shape itself (feature 161: ten hand-rolled walks drifted apart, and
`regen.py` regenerated a converted map `make maps` never rolled).

**The load-bearing argument is `trees`, not the file listing.** The two failure directions are not
symmetric: a consumer that collects too MUCH trips its own assertions, while one that collects too
LITTLE is simply green. So the default is both trees, narrowing is a deliberate act, and the
per-consumer answers are tabulated in `specs/161-pool-per-map-folders/contracts/pool-discovery.md`.
A consumer not in that table has not been considered; adding one means adding a row.

    bundles()                                                   # both trees, every kind
    bundles(trees=(poolmaps.LIVE_TREE,), kinds={"scripted"})    # the gate's regeneration sweep
    gens(...)                                                   # the same, as .gen.py paths

Each `MapBundle` carries `gen`, `stem`, `tier`, `tree`, `directory` and `kind`, and `path(ext)`
answers where a sibling file WOULD be whether or not it exists - which matters, because a live map's
renders are gitignored and a clean checkout has none of them.

**Two directory lists name a pool tree and must be corrected in OPPOSITE directions** when a tree is
added. `engine_fingerprint()` here and `gencache.engine_files()` PRUNE the trees, because a map
generator is not engine source; `ci/delta.py`'s `_ENGINE_DIRS` INCLUDES them, because that list
answers whether a delta owes the paid gate. Both are keyed on literal names, so both are invisible
to any test that builds its own fixture tree - see `dev/lessons.md`.
