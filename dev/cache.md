# The generation cache - what it covers, what it cannot see, and its traps

**Load this file when:** The cache is behaving oddly, you changed how generation is driven, or you are about to test whether an edit
invalidates an entry.

The short always-on version of each rule is in the engine index, [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md).

## The cache is Rust, and `make map` is its one driver (feature 449 T221)

`make map MAP=<folder|spec>` draws any live pool map - a hamlet, a generated compound or a hand sheet - through one Rust driver
(`rust/gate/crates/pool/src/map.rs`) over the generation cache (`rust/gate/crates/pool/src/cache.rs`), both rebuilt from
`specs/449-rust-codebase/derivations/T219-pipeline.md` and never from the Python they replaced (`pipeline/regen.py`, `rollcache.py`,
the six `.gen.py` wrappers and `interactive/sheet.py`, deleted; `pipeline/gencache.py` and `_census.py` stay only because
`render_cache.py` imports them, and leave with it in T222). The walk's kind names the engine and the spec: a hamlet's `.spec.json`
(the `hamlet` binary of `rust/phases`), a compound's `.compound.json` and a hand sheet's `.svg` (`l7r-mode-a compound` and
`hand-sheet`). `MAP=--all` does every live map in one run; the review gate asks `l7r_gate_pool::is_current` in process, read-only.

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
