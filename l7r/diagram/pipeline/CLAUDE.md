# `pipeline/` - how a pool map gets regenerated, cached, rendered and indexed

The BUILD side of the project. The other three sides are the drawing engines (`settlement/`,
`waterfields/`, `hamletgen/`, the Rust compound generator `rust/mode_a/src/compound/`) and the by-hand
diagnostics ([`../tools/`](../tools/CLAUDE.md)). Drive it through `make` at the repository root:

    make map MAP=pool/hamlets/sawada                  # one map: regenerated, or CACHED when nothing it depends on changed
    make rust-test CRATE=rust/mode_a                  # the pool sweep: every pool sheet through its tier's checks (`make maps` left with the Python engine)

| module | what it is | measured for coverage |
|---|---|---|
| (Rust) `rust/gate/crates/pool/src/cache.rs`, `map.rs` | THE GENERATION CACHE and `make map`'s one driver (feature 449 T221, rebuilt from `specs/449-rust-codebase/derivations/T219-pipeline.md`; `regen.py`, `rollcache.py`, the six `.gen.py` and `interactive/sheet.py` deleted with it): the read table, the entries, the engines' build ids; [`dev/cache.md`](../../../dev/cache.md) | the crate's own tests |
| `gencache` | the Python generation cache, no longer what `make map` runs: kept only because `render_cache` imports it (with `_census.py`), and deleted with it (T222) | no - a driver |
| `render_cache` | main's renders: a content-hash short-circuit so main regenerates its own renders from its own tip after the stop-work push | yes |
| `poolmaps` | the Python pool listing, kept for the Python left in this package until T221 and T222 delete it; every Rust consumer asks the one pool walk, `rust/gate/crates/pool` (feature 449 T220) | yes |
| `pool_index` | the Python index writer, no longer what `make pool-index` runs: the Rust pool walk (`rust/gate/crates/pool`, feature 449 T220) writes `pool/index.html` now, every map of both trees; kept only because `render_cache` imports it, and deleted with it (T222) | yes |
| `record_build` | the record's site on the main checkout (feature 301): render-sync builds `research/site/` only when its STAMP - the record's files, the glossary's JSON and the building program - differs; a forwarder to `l7r-gate record site-stale` since feature 449 T148, kept for `render_cache` until S12 | no - a forwarder |

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

## Before you trust a cache change

Nothing audits the cache now: `make cache-audit` (a perturbed engine literal, the pool swept cached and fresh, identical
artifacts demanded) was deleted with the Python hamlet engine (feature 444 T39, ea5638968); `dev/cache.md` says what that
leaves, until feature 449 T221 rebuilds the cache in Rust.

What the key covers, the soundness argument and the concurrency cases are `gencache.py`'s own docstring; THE TRAP
(a miss rebuilds the entry against the tree as it is, so a trial of "does an edit to X invalidate?" needs the
baseline re-established - run until `CACHED` - before each trial) is [`dev/cache.md`](../../../dev/cache.md).

## `poolmaps.bundles()` - ask, do not glob (feature 161)

**In Rust the one walk is `l7r_gate_pool::walk`** (`rust/gate/crates/pool`, feature 449 T220, rebuilt from
`specs/449-rust-codebase/derivations/T219-pipeline.md`): each pool directory listed once, each map folder classified once (a hamlet,
a generated compound, a hand sheet, a frozen exhibit, or reported), its entry names kept so a consumer asks `Map::has` of the listing;
the shell asks it as `l7r-gate pool find <map> [<suffix>]`. What follows is the Python's rule, for the Python left here.

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
