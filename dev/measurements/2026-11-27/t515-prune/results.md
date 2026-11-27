# 451 T515: pruning inside a live build directory - measured 2026-11-27

Load this file when: you are changing `rust/guard/src/guards/scratch_sweep_hooks/sweep/prune.rs`, its knob
`L7R_CACHE_STALE_HOURS`, or asking why the build cache still sits over its budget.

All figures read the REAL cache (`~/.cache/l7r-cargo-target`) by stat alone (`find -printf`, `t515-measure.sh`
here): no file's contents read, so no atime moved; nothing in it was removed. The warm build ran on COPIES only.

## Before

- `make disk-audit`, 10:40 local: the build cache 246.9 GB against its 100 GB budget (the clone's 111.4 GB, the
  landing tree's 41.7, the pool trees t270 24.5 and t269 23.3); the disk at 82% (`df -h /`). Its last line:
  "evict: a build runs (3419470 cargo); nothing of the build cache removed" - the second audit of the day so held.
  A two-minute sample (60 `pgrep` calls, 2 s apart, 11:10) found no build running: the hold comes and goes.
- The clone's `debug/`: `incremental/` 21.9 GB in 915 crate directories (53 of them `l7r_mode_a`), one rustc
  session each; `deps/` 14.7 GB in 4,231 files; `.fingerprint/` 1,799 units.
- Processes run from inside the cache: `diagram/l7r-guard.good`, `diagram-backlog/tool/l7r-gate`,
  `diagram-backlog-t269/tool/l7r-gate` (`/proc/*/exe`). They hold their PROFILE (or, for the guard binary, a
  build directory's root, which is no profile), not the whole build directory.

## The signal: how "not read" is told

A unit's hash matches across `deps/`, `.fingerprint/` and `build/` (`libserde-3b2e85d1ed891f7c.rmeta`,
`.fingerprint/serde-3b2e85d1ed891f7c/`); `incremental/` names carry another id (base 36), so it is judged alone.
The mount is `relatime` (`/proc/mounts`): an atime moves at most once a day unless older than the mtime.

What the rule would take (`MODE=rel KEY=kind STALE=48`), by signal:

| last use read from | would take |
|---|---|
| mtime alone | 86.9 GB |
| mtime, and the atime of every file | 69.6 GB |
| mtime, and the atime of every file but a `.json` (CHOSEN) | 85.0 GB |

- mtime alone takes 1.9 GB more: units a no-op build still reads (their fingerprint's atime recent, their
  artifacts built days ago), e.g. `.fingerprint/serde-77d85448652f4a6d/lib-serde` built 11-20, read 11-24.
- Every fingerprint `.json` in the clone's `debug/`, live hash or dead, shows the same atime, 2026-11-26 14:31:21:
  one scan read them all. Counting `.json` atimes masks 15.4 GB. Cargo reads the `.json` only to explain a
  rebuild; the hash file and `dep-*` are what a freshness check reads.
- The profile root's dep-info `.d` names source files only, never a dependency's hash: it cannot tell a hash stale.
- A directory's atime is never read (a listing, the sweep's own, moves it).

## Knob and reference

| rule | would take |
|---|---|
| 30 h before the profile's last use | 111.6 GB |
| 48 h (CHOSEN, `STALE_HOURS`) | 85.0 GB |
| 72 h | 76.5 GB |
| 48 h before NOW (not the profile's last use) | 92.2 GB |

Keying the newest kept by crate alone instead of crate and fingerprint kind: 3.1 GB more taken, under the all-atime
signal (72.7 against 69.6 GB). Per tree at the chosen rule (`sig-nojson.txt`): the clone 53.1 GB, the landing
tree 28.5, the mirror 3.4, the pool trees t269, t270, t271, b1 0.0 each (their profiles under two days old).

## A warm build stays warm

`t515-warm.sh`: the mirror's `tool` profile (6.3 GB, the guard's and the gate's tool builds) copied with
`tar --atime-preserve=system` (O_NOATIME), every package it serves built with `cargo build --profile tool --locked
-v` from the mirror's source, (A) unpruned, (B) with the rule's 760 entries removed from the copy (6,304 MB to
3,123 MB), (B again) a second time:

| build | l7r_gate | l7r_guard | l7r_mode_a | hamlet | compiled |
|---|---|---|---|---|---|
| A unpruned | 0.4 s, 47 fresh | 0.1 s, 20 | 0.5 s, 127 | 0.2 s, 1 | 0 |
| B pruned | 0.2 s, 47 fresh | 0.6 s, 20 | 0.1 s, 127 | 0.1 s, 1 | 0 |
| B again | 0.1 s, 47 fresh | 0.1 s, 20 | 0.1 s, 127 | 0.1 s, 1 | 0 |

Not measured: an EDIT's rebuild of a variant whose incremental directory went (the newest per crate is kept;
the cost is that variant's crate compiled from scratch once).

## The built rule, dry, on the real cache

`make cache-clean DRY=1` from the T515 tree (its own guard build), 2026-11-27 about 11:35, no build running at
that moment: 8,401 entries, 88.0 GB, in 19.9 s - the prune 83.3 GB (the clone 53.7, the landing tree 26.3, the
mirror 3.3, every pool tree 0.0) and the budget's eviction 4.4 GB (the landing tree's `tool` profile). The
prototype's 85.0 GB is within 2%: the built rule skips held profiles the prototype did not. The mirror's 3.3 GB
against the prototype's 3.4 shows the O_NOATIME copy left its atimes alone.

## After

The rule frees about 85 GB of 246.9; the cache stays about 162 GB against its 100 GB budget (filed: 451 T518).
