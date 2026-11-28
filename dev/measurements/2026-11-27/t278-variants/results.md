# 462 T278: a smaller keep and an earlier idle cutoff for the variants rule, measured on coverage builds (2026-11-27)

The question: the cargo-variant sweep (`rust/guard/src/guards/scratch_sweep_hooks/sweep/cargo.rs`, `KEPT = 16`, idle cutoff
`L7R_CACHE_IDLE_HOURS` = 12) keeps 16 variants of a crate in each store. Would a smaller keep, or an earlier cutoff, free disk in the
`cover-<family>` build directories without costing a later build any time? The GM's rule (2026-11-26, 462 T301's restatement)
applies: time saved outranks disk, so nothing a later run would reuse may be evicted. Measured after T325 (one feature set per family,
landed 2026-11-26 19:42 -0500) and after T515's prune (`L7R_CACHE_STALE_HOURS`, 48 h), with the machine at load 14 to 56 on 22 cores
while other builders ran.

## Scripts

All the scripts are in this directory. Every read of a live cache was by `lstat` alone, and every build ran against a copy in the
session scratchpad.

- `t278-count.py`: counts the variants in each `cover-*` directory (groups, entries, the largest group, entries built since T325, and
  bytes). It prints what the rule would take at keep 16, 8, 4, 2 and 1, each at idle cutoffs of 12, 6, 1 and 0 h. Output:
  `t278-count.tsv`.
- `t278-net.py`: the same take, net of what T515's prune takes anyway. It is an approximation of T515 that leaves out T515's "newest
  of kind" keep, so the net is an upper bound. Output: `t278-net.tsv`.
- `t278-live.py`: lists the groups that hold more than N entries built since T325.
- `t278-prune.py`: applies the rule at a given KEEP and HOURS to a copy. With `--live`, it first names any entry the control build
  used (the hashes in its compiler-artifact filenames and build-script out_dirs) that the rule would take. It refuses to run on a live
  cache.
- `t278-build.sh`: the gate's coverage build of the gate family (`cover.rs`: `cover_env`, `workspace_only`, `build`), run by hand.
  - It runs from the tree's root with `cargo llvm-cov show-env`'s environment.
  - The coverage flags go into the live directory's own `instrument.sh`, which has the same text the gate writes.
  - The command is `cargo test --no-run --lib --quiet --message-format=json-render-diagnostics` with `-p` for all 29 gate crates that
    have a library, into `CARGO_TARGET_DIR=<copy>/target`.
  - It prints the wall seconds and the units compiled (compiler-artifact messages with `fresh=false`, the count `phase::compiled`
    makes).
- `t278-arms.sh`: runs each arm on a fresh `cp -a` of the warmed base:
  1. the rule is applied at KEEP;
  2. the whole family is built warm;
  3. `-p l7r_gate_claims` alone is built warm;
  4. the whole family is built after a one-line edit of `rust/gate/crates/registry/src/lib.rs` (a constant appended). The file and
     its mtime are restored with `cp -p` afterwards and checked with `git diff --quiet`.

  Output: `t278-runs.tsv`.

## Thing 1: today's variants per crate in the cover-<family> trees (after T325 and T515)

Observed 2026-11-27 19:47 -0500 (method: `t278-count.py`, `t278-count.tsv`). Each pool tree's figures are much the same as its
neighbors', so only the gate family is shown for them.

| directory | GB | groups | entries | largest group | groups over 4 / over 2 | entries since T325 |
|---|---|---|---|---|---|---|
| clone `diagram-backlog/cover-gate` | 17.27 | 259 | 1,349 | 17 | 128 / 179 | 537 |
| landing `diagram-backlog-land/cover-gate` | 6.10 | 247 | 599 | 6 | 10 / 94 | 180 |
| pool `t269` / `t270` / `t271` / `b1` `cover-gate` | 5.53 / 6.15 / 4.51 / 2.20 | 247 / 247 / 247 / 159 | 619 / 689 / 541 / 291 | 7 / 7 / 5 / 4 | 30 / 43 / 6 / 0 over 4 | 79 / 93 / 79 / 165 |
| clone `cover-guard` / `cover-mode_a` / `cover-embed` / `cover-browser` | 2.33 / 2.83 / 1.75 / 0.99 | 86 / 506 / 407 / 90 | 162 / 750 / 975 / 206 | 7 / 7 / 7 / 5 | 4 / 4 / 22 / 1 over 4 | |
| all 27 `cover-*` directories | 58.3 | | | | | |

**The rule as it stands (keep 16, 12 h)** takes 0.02 GB today, in the clone's `cover-gate`, and 0.00 GB everywhere else. Only 3 of the
clone's groups hold more than 16 entries. T515's prune already did the work: the clone's `cover-gate` was 44 GB before it and is
17.3 GB now.

**Why a group still holds 4 to 17 entries.** Each gate crate has 2 live units, its library and its library test. On top of those it
gains a new pair of hashes whenever a dependency's hash moves.

- For example, the clone's `l7r_gate_core` and `l7r_gate_measure` each hold 4 fingerprints built since T325. Two are current (0.3 h
  and 2.1 h old). The other two are 18.3 h old and differ only in their dependency hashes: `l7r_shared` gained `memchr`, so the hashes
  of `serde_json` and `fancy_regex` under it moved (observed 2026-11-27, method: each fingerprint's JSON read).
- So "built since T325" does not mean "live". Variants accumulate because every manifest or lockfile change makes a new generation of
  hashes.
- The warm-up below showed this directly: bringing `t270`'s copy up to HEAD compiled 58 units as new hashes, and the copy grew from
  6.15 to 8.16 GB.

## Things 2 and 3: the rebuild time of a coverage build at keep 16, 4 and 2 (gate family)

The source was a `tar --atime-preserve=system` copy of `diagram-backlog-t270/cover-gate` (6.15 GB; its counts matched the original's
row for row). It was then warmed up to HEAD: 58 units compiled in 362.9 s at load 15 to 37. The control build that followed compiled
0 units with 80 fresh, in 0.5 s, which validates the hand replica of the gate's call. All measured 2026-11-27 (method:
`t278-arms.sh`, arms run in the order k16, k4, k2, k16; `t278-runs.tsv`).

| keep (12 h cutoff) | taken from the copy | live entries taken (`--live` check) | warm, whole family | warm, `-p claims` alone | after the one-line `registry` edit |
|---|---|---|---|---|---|
| 16 (today), first run | 0 entries, 0.00 GB | 0 | 0 compiled, 0.3 s | 0 compiled, 0.1 s | 27 compiled, 134.9 s, load 31 to 43 |
| 4 | 162 entries, 1.93 GB | 0 | 0 compiled, 0.1 s | 0 compiled, 0.1 s | 27 compiled (the same 27), 124.1 s, load 14 to 36 |
| 2 | 423 entries, 4.55 GB | 5 (fingerprints of `serde`, `serde_core`, `serde_json` ×2, `zmij`: build-script compile and run units, which share a group with the library) | **62 compiled, 297.9 s**, load 25 to 54: the two build scripts were rerun and the whole workspace cascaded | **14 compiled, 41.9 s** (`serde`, `serde_core`, `serde_json`, `zmij`, `l7r_shared` and 9 gate crates) | 51 compiled, 83.3 s |
| 16, second run | 0 entries, 0.00 GB | 0 | 0 compiled, 0.9 s | 0 compiled, 0.7 s | 27 compiled, 202.1 s, load 20 to 57 |

Units compiled is the figure to go by. Wall time moved from 124 to 202 s across arms that compiled the same 27 units, so it tracks the
machine's load rather than the lever.

- **Keep 4 loses no time in either the build store or the incremental store.** Its edit run compiled the same 27 units as keep 16. An
  evicted live incremental directory would have shown up as a slower compile of those 27, and nothing did beyond the load band.
- **The margin under keep 4 is zero.** Keep 3 already takes one live entry, `.fingerprint/serde_json-864f8b427ec4b3cb`, a build-script
  run unit (method: `t278-prune.py ... 3 12 --live`). The cause is that `variant_of` groups a crate's library, its build-script compile
  and its build-script run under one name. A crate with a build script therefore has 3 live entries in `.fingerprint`. Two `-p`
  selections that resolve an outside crate differently add one more: `-p claims` alone rebuilt `serde` and `serde_json` once keep 2 had
  taken the variant it uses.
- **Keep 2 loses time:** 297.9 s and 62 units on the first warm build, about the cost of a cold workspace build (the warm-up's 58 units
  took 362.9 s), and 41.9 s more on the next selection.

## Thing 4: an earlier idle cutoff (`L7R_CACHE_IDLE_HOURS`)

Priced without building. At every keep, the take at a 12, 6, 1 or 0 h cutoff is the same to the hundredth of a GB in every
directory (method: `t278-count.tsv`'s `take_k*_h*` columns). At keep 16 an earlier cutoff frees 0.00 GB (0.02 GB in the clone): the
entries past rank 16 are all older than 12 h. **There is no lever here.** The cutoff never decides what goes, so it can neither free
disk nor cost time.

## Each lever priced, net of T515

The net figures come from `t278-net.py` (`t278-net.tsv`). The take is today's; the net is the part T515's 48 h prune would NOT take
anyway.

| lever | GB taken today, all 27 `cover-*` directories | net of T515 | of which the clone's `cover-gate` | seconds lost |
|---|---|---|---|---|
| keep 16 → 8 | 3.11 | 0.78 | 0.78 | 0 (no live entry within 4 of the cut) |
| keep 16 → 4 | 11.52 | 5.69 | 3.78 | 0 measured (above), but with no margin: keep 3 takes a live entry |
| keep 16 → 2 | 26.40 | 16.68 | 6.48 | 297.9 s and 62 units on the next warm build, plus 41.9 s on a second selection |
| idle 12 h → 0 h (at keep 16) | 0.02 | 0.02 | 0.02 | 0 |

No live process or live cache was touched. The scratch copies were deleted after the arms ran, and the tree's `registry/src/lib.rs`
was restored byte for byte with its mtime.
