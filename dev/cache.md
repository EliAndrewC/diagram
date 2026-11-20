# The generation cache - what it covers, what it cannot see, and its traps

**Load this file when:** The cache is behaving oddly, you changed how generation is driven, or you are about to test whether an edit
invalidates an entry.

The short always-on version of each rule is in the engine index, [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md).

## The cache is Rust, and `make map` is its one driver (feature 449 T221)

`make map MAP=<folder|spec>` draws any live pool map - a hamlet, a generated compound or a hand sheet - through one Rust driver
(`rust/gate/crates/pool/src/map.rs`) over the generation cache (`rust/gate/crates/pool/src/cache.rs`), both rebuilt from
`specs/449-rust-codebase/derivations/T219-pipeline.md` and never from the Python they replaced (`pipeline/regen.py`, `rollcache.py`,
the six `.gen.py` wrappers and `interactive/sheet.py`, deleted with T221; the rest of `l7r/diagram/pipeline/` - `gencache.py`,
`render_cache.py`, `poolmaps.py`, `pool_index.py`, `record_build.py`, `codeid.py`, with `_census.py` and `_invocation.py` - deleted with
T222, and this file holds what that directory's index did). The walk's kind names the engine and the spec: a hamlet's `.spec.json`
(the `hamlet` binary of `rust/phases`), a compound's `.compound.json` and a hand sheet's `.svg` (`l7r-mode-a compound` and
`hand-sheet`). `MAP=--all` does every live map in one run; the review gate asks `l7r_gate_pool::is_current` in process, read-only.

    make map MAP=pool/hamlets/sawada        # one map: CACHED, REGENERATED (with why) or FROZEN
    make map MAP=--all                      # every live map (render-sync's first step runs the same driver)
    make rust-test CRATE=rust/mode_a        # the pool sweep: every pool sheet through its tier's checks

## The pool walk - ask it, never glob (feature 161; Rust since 449 T220)

`l7r_gate_pool::walk` (`rust/gate/crates/pool/src/walk.rs`) lists each pool directory once and classifies each map folder once - a
hamlet, a generated compound, a hand sheet, a frozen exhibit, or reported - keeping its entry names so a consumer asks `Map::has` of
the listing; the shell asks it as `l7r-gate pool find <map> [<suffix>]`, and `l7r-gate pool list` lists every map. No consumer globs,
lists or greps the pool's shape itself: feature 161 found ten hand-rolled walks drifted apart. The two failure directions are not
symmetric - a consumer that collects too MUCH trips its own assertions, one that collects too LITTLE is simply green (the probe's pool
section, filtering hamlets on a `.gen.py` no map had after T221, printed nothing for every hamlet until T222; the probe itself was removed by T230) - so a consumer names the
trees and kinds it means. `pool/index.html` is written from the walk (`index.rs`), every map of both trees; a hamlet's row links only
what the Rust driver writes, never the deleted Python engine's `.png`, `.html` or `.svg` left beside it (T222).

## Main's renders: `make render-sync` (feature 449 T222)

`scripts/sync-with-main.sh render-sync` (and its background runner after every landing, logging to `.clones/.render-sync.log` and
`.clones/.render-sync.status`) runs `make render-sync` in main under the sync lock with `DIAGRAM_ALLOW_MAIN=1`, the one sanctioned run in
main's tree (the Makefile's `guard` refuses it there otherwise). It does the three things the Python render cache did, its log's three
lines, with no Python: every live map through the driver (`pool map --all`), the pool index (`pool index`), and the record's site
built when its stamp - the record's files, the glossary and the gate binary - differs (`record site-stale --root`, printing `fresh` or
`rebuilt`). **A map that fails stops neither the index nor the site**: the driver draws every other map first and the two later steps
read no map's drawing, so the recipe runs all three and exits 1 at the end, the runner's status then reading FAILED (decided and
measured by T222). It renders the tree it runs in, taking the Python's `ARGS=--skill-dir/--main-repo` only where they name that tree. What the Python did and
nothing does now: the frozen tree's count and its warning on an exhibit with no render (the index lists each exhibit with the links its
folder holds, and an exhibit's render can never be regenerated), and the `.<map>.render-cache` stamp beside a hand sheet, left on disk
in main and still ignored by `.gitignore`.

## What re-keys a map

- **its spec** - held by its record in the entry's meta (size, mtime ns, ctime, inode, digest);
- **every file its engine reported reading, and every file it looked for and did not find** - a miss is a read (T219's assumption 3:
  before T221 the page writer reported only files that existed, so a modal text or a map's notes created later left the sheet cached
  and stale). The Mode A engine prints them in its reply's `reads` (`rust/mode_a/src/reads.rs`); the hamlet driver reads its spec alone;
- **its engine's binary** - identified by its GNU build id, read once a run from the binary `scripts/gates/l7r-gate.sh <mode-a|hamlet>`
  names fresh (`L7R_GATE_PRINT_FRESH=1`, which builds a stale one); a binary with no note is hashed whole;
- **the font set** (a Mode A sheet) - every directory and font file under fontconfig's roots, held by its stat;
- **the picture switch** - an entry drawn under `DIAGRAM_SKIP_RENDER=1` serves only a run that sets it too.

## How it never serves a stale map

- **One read table a clone** (`.gencache/rust/reads.tsv`): one row a distinct path with its stat, the filesystem's time it was hashed
  at, its digest and the maps that read it - held once a run however many maps read it. A row whose stat matches and whose file
  settled before its hashing is held with no read of the file; anything else re-hashes it (the racy-file rule), and a digest that
  moved removes, durably and first, the entry of every map the row names - only then does the row take the new digest.
- **A read first reported on a miss** is hashed after the engine ran, so it is held against the engine's START, a file's time taken on
  the filesystem's clock just before the engine was started: a read (the spec among them) whose mtime or ctime is not older than that, or
  an absent read whose nearest standing directory moved since, may have changed while the engine read it - the map is drawn into its
  folder but NOT published, and the next run draws it again. No entry carries a digest of content it was not built from.
- **Published atomically, meta last**: the engine draws into a staging folder; each artifact is renamed into the entry
  (`.gencache/rust/entries/<tier>/<name>/`) and hard-linked into the map's folder; the table is written, THEN each meta renamed. A table
  that is gone or does not read throws every entry away.
- **One run at a time**: a run holds `.gencache/rust/lock` throughout; a second waits.

The clock is the filesystem's own: every reference time is a file's mtime (`stat.rs`'s `fs_clock`), because a file's timestamps come
from the kernel's coarse clock, which can stand a tick behind `SystemTime::now`.

## What it cannot see

- A file restored with its old size, mtime, ctime and inode - which no ordinary tool does.
- A shared library the engines load at run time other than the fonts (the build id covers what is linked in).
- A file an engine reads without reporting it. The Mode A engine reports what its reads pass through `reads::note`; a new read in the
  engine that skips it is invisible to the cache - `strace -f -e trace=openat,newfstatat` on one `l7r-mode-a hand-sheet` run, compared
  with its reply's `reads`, is the audit.

## THE TRAP, which cost three wrong conclusions in one session

A miss REBUILDS the entry against whatever the sources say at that moment. So if you edit a file, regenerate (correctly a miss), then
`git checkout` the edit away, the next run is a *legitimate* miss - the stored entry was built against content that no longer exists.
Testing "does an edit to X invalidate?" therefore needs the baseline re-established (run until you see `CACHED`) before each trial, or
the previous trial's cleanup produces the miss and you conclude the cache is broken when it is working perfectly.

## Its counted work

The all-hit run's counted operations are the `pipeline` stage of the work budget (`dev/work-budget.json`), counted by `l7r-pool counts
<tree>` (the counting build) on the second of two runs back to back, and held at the push by `make work-budget-review`.
