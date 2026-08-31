# Feature 175 - research

Every number here was measured on 2026-08-31 in `.clones/diagram-testing`, not estimated. Where a
figure is indicative rather than comparable, it says so.

## R1 - The remote build starts cold, and nothing has ever tried to stop it

- `.gencache/` is ignored by `.claude/skills/diagram/.gitignore` line 1 and has **0 tracked files**
  (`git ls-files .claude/skills/diagram/.gencache | wc -l`).
- **No `cache:` block exists in any buildspec.** `grep -rn cache buildspec/` returns nothing across
  `check.yml`, `merge.yml`, `image.yml`, `run.sh`.
- `buildspec/check.yml` does `git clone -q --filter=blob:none` into a fresh container per build.

So every `gencache.gate_obtain` that HITs locally MISSES remotely, and the map regenerates for real
in a `coverage run --parallel-mode` subprocess. **The remote gate does strictly more work than the
local gate for the same commit** - which is the GM's point: the slowness is our configuration.

**Indicative timings** (recorded runs; the remote figures predate this month's efficiency work and
one of them FAILED, so they bound nothing):

| run | where | wall | cost |
|---|---|---|---|
| `full` 2026-08-25 | CodeBuild | 18.0 min | $1.44 (FAILED) |
| `reference` 2026-08-25 | CodeBuild | 8.0 min | $0.64 |
| `make test-full` 2026-08-31 | this laptop | ~4:10 | - |

## R2 - What the 221 MB actually is

    54M  .gencache/rolls        the ROLL cache (rollcache.py)
    41M  .gencache/kashikawa    \
    40M  .gencache/sawada        |
    33M  .gencache/kuwabata      |  the five live pool maps' gate entries = 168 MB
    29M  .gencache/inashiro      |
    25M  .gencache/mizuguchi    /
    1.4M .gencache/ast          the AST memo (compute_key's parsed-source cache)

And inside one entry (kashikawa, 41 MB):

    22M   kashikawa.svg     the vector render
    13M   kashikawa.html    the interactive map (feature 134)
    6.0M  kashikawa.png     the raster
    184K  kashikawa.json    THE MANIFEST - what the gate judges
    96K   coverage.data     the generation coverage, replayed into the run on a HIT
    76K   meta.json         the key and the dep list `load()` re-checks
    4.0K  coverage.key

**~99% of every entry is render artifacts; ~360 KB is what a HIT is keyed on.**

## R3 - What a HIT actually needs, per the code rather than per intuition

`gate_obtain` HITs only when all of: `coverage.data` exists and is non-empty,
`_coverage_stamp_matches`, `_coverage_is_current`, and `load(gen)` returns True. `load()` re-checks
`compute_key(gen, meta["deps"]) == meta["key"]` and then copies each of `_outputs(gen)` out of the
entry.

Which of the outputs a test then READS:

| artifact | needed? | evidence |
|---|---|---|
| `.json` manifest | **yes** | `_regen_and_gate` asserts it exists; every gate test reads it |
| `.svg` | **yes** | `_channels_under_plots(svg)` - the z-order audit in `full/test_villages.py` |
| `.png` | **no, and caching it is WRONG** | see below |
| `.html` | **not established** - no test found reading a POOL map's `.html`; the readers found are `test_core_classes.py` (a tmp file it wrote itself), `test_pool_index.py` (`index.html`) and `test_render_cache.py` (files it writes) |

**The PNG must not be cached.** A gate-built entry is stored with rendering skipped, so it HAS no
PNG - `gate_obtain` sets `DIAGRAM_SKIP_RENDER=1` in the child, and `finish.py` skips the raster on
it. `load()` deliberately DELETES a standing output the entry lacks, and the comment records why:
keeping it "shipped four maps whose .png was the PREVIOUS roll while their .json and .svg were the
current one... Nothing looked wrong - all three files carried the same mtime - and two review rounds
judged the wrong image." The 6 MB PNGs in the local cache are residue of local iteration runs, which
DO render. Uploading them would seed a remote container with rasters no remote roll produces.

`tests/test_villages.py:379` already guards this shape - it skips its PNG/SVG dimension check when
no PNG is present, and line 353 states the rule: "a gate-driven roll writes a new `.json` and `.svg`
and no `.png`".

## R4 - `rolls/` (54 MB, 24% of the payload) is worthless to a remote FULL

`rollcache.bypassed()` is true under `L7R_TESTS_FULL=1`, which `test-full` sets - the full run
produces every roll for real and serves none from the cache. So 54 MB of `rolls/` would be uploaded,
downloaded and never read by a FULL build.

It is NOT worthless to a `reference`-scope build: `make reference` calls `rollcache.report(...)`,
and a reference-scope remote run is the common case (`ci-merge`'s gated route). **So the answer to
"what needs to go there" is MODE-DEPENDENT**, which is the part of the GM's question that has a
non-obvious answer.

## R5 - Nothing must accumulate forever (the GM's explicit failure case)

CodeBuild's `cache: type: S3` writes an object per cache key and **never expires it**; expiry is the
bucket's job. So the feature owes an S3 **lifecycle rule**, and a cache key that does not grow
without bound. A key containing the commit SHA would leave one object per commit for ever - the
exact failure the GM named ("uploading many megabytes... on every run and then never cleaning it
up").

## R6 - Open questions this research does NOT settle

1. Whether the `.html` is read by any remote-run test. Not proven absent, only not found - it must
   be established before excluding it, because `load()` deleting a missing output makes an omission
   destructive rather than merely lossy.
2. Whether S3 restore of ~110 MB is faster than regenerating five maps. A cache that costs more to
   fetch than it saves is worse than none, and this has to be MEASURED on the build, not modeled -
   this session has had four predictions about performance overturned by measurement in one day.
3. Whether `ast/` (1.4 MB) helps enough to bother. Cheap either way.
