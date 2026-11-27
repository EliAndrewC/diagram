# 451 T439: where a hook call's time outside the guard binary goes, 2026-11-27

T373 found every hook call spending 15 to 17 ms outside the guard binary (`dev/measurements/2026-11-26/edit-hook/t373-results.md`,
"The floor"). This record takes the chain apart hop by hop and prices each lever.

METHOD. Each row is run round-robin with the others (`t439-hops.py`, `t439-inplace.py`), wall time by `perf_counter` and the child's
CPU by `getrusage`, median, 90th centile and minimum. The binary the wrapper execs is a STUB (`/bin/true` copied to a scratch
`L7R_GUARD_TARGET` as `l7r-guard.good`, touched newer than every source), so nothing is built and no live log, permit store or
target is touched; `CLONE_MAIN` names no mirror, so `l7r-hook` runs the tree's own `l7r-guard.sh`. The in-place variants
(`t439-inplace.py`) are copies of the wrapper in a scratch tree whose `rust/` and `.cargo/` are links to the real tree's, so each
walks the real 449 paths. The machine was shared with other builders the whole time; each table carries its load (22 cores).
The total of the chain with a stub binary, 14.0 ms (12.1 minimum), reproduces T373's 15 to 17 ms floor.

## Each hop (`t439-hops.txt`, 40 runs, load 19.2)

| hop | wall median | wall p90 | wall min | CPU median |
|---|---|---|---|---|
| `dash -c :` (the launcher's shell) | 1.00 | 1.17 | 0.82 | 0.82 |
| `/usr/bin/env bash -c :` (the wrapper's shebang) | 4.80 | 5.57 | 4.24 | 4.63 |
| `bash -c :` | 1.75 | 2.02 | 1.54 | 1.55 |
| an exec of a binary (`/bin/true`) | 0.77 | 0.89 | 0.67 | 0.64 |
| `l7r-guard.sh`, the walk skipped (`L7R_GUARD_FRESH`) | 6.15 | 6.58 | 5.33 | 5.99 |
| `l7r-guard.sh` as it was (one walk) | 12.95 | 14.17 | 11.85 | 12.77 |
| `l7r-hook` -> `l7r-guard.sh` -> stub, as it was | 14.04 | 15.26 | 12.08 | 13.86 |
| bash: the globstar expansion of `rust/guard/**` alone | 4.05 | 4.45 | 3.08 | 3.80 |
| bash: the walk as `newer()` ran it | 8.75 | 10.13 | 7.80 | 8.54 |
| `find SOURCES -newer GOOD -print -quit` | 3.66 | 3.96 | 2.90 | 3.45 |

An earlier run at load 21 to 25 (LOADED) gave the same order at two to six times the figures; it is not used.

- **Sourcing**: the hot path sources nothing. `lib/lld-path.sh` is sourced only inside a build, `lib/guardlog.sh` only where no binary
  was ever built; `BASH_ENV` names `/etc/sandbox-persistent.sh`, an empty file, in this shell (whether the harness's hook processes
  inherit it was not checked).
- **The walk**: 449 paths (318 tracked files, 131 directories), no dotfile and no symlink under `rust/guard`. Its two parts are the
  globstar expansion (about 4 ms) and an `-nt` per path, each statting both files (about 4.7 ms).
- **`env bash`**: `/usr/bin/env` is uutils coreutils' multicall binary (`-> ../lib/cargo/bin/coreutils/env`), whose start alone is
  about 3 ms (`env /bin/true`, 3.45 median against 0.77 for `/bin/true`, 40 runs, load 16): about 3 ms of every call, on the
  wrapper's shebang.

## Each lever, in place (`t439-inplace.txt`, 40 runs, load 22.9)

| wrapper variant | wall median | wall p90 | wall min | CPU median |
|---|---|---|---|---|
| A as it was (bash walk, `[ -nt ]`), by its shebang | 14.85 | 16.45 | 13.62 | 14.51 |
| B the walk skipped: the floor with no walk at all | 6.06 | 6.79 | 5.29 | 5.89 |
| C a walk with no fork (`[[ -nt ]]`) | 12.48 | 14.21 | 10.71 | 12.28 |
| D one `find -newer -print -quit` | 10.77 | 12.75 | 9.82 | 10.67 |
| E as it was, by `bash` (no `env` hop) | 11.78 | 13.37 | 10.34 | 11.39 |
| F `find`, by `bash` (both levers) | 8.00 | 8.95 | 6.94 | 7.74 |

The 20-run table beside it (load 22.9 to 24.7) agrees within 0.4 ms. As built (`t439-inplace-built.txt`, 40 runs, load 12.7 to
13.0, a noisier run): A 16.24, G (the built `find` with its fallback) 13.44, D 13.64 -> 12.64, F 9.76.

- **The walk costs 8.8 ms of the call (A - B)**. A kept stamp could save at most that, less its own read.
- **A stamp is not safe.** An edit moves only its own file's time; a directory's time moves only when an entry is added or removed,
  so a stamp on directory times misses every edit of an existing file. A stamp kept fresh by a signal - the Edit hook marking the
  tree dirty, git's index - misses an edit made through Bash (`sed -i`, `cargo fmt`), a fast-forward of the mirror by sync-in or
  render-sync, and another session's edits of a shared tree: each would run a STALE guard. Any stamp that is safe still has to look
  at every file's time, which is the walk. Not built.
- **`find` pays 4.1 ms (A - D)**, 2.8 in the noisier as-built run: built (`scripts/hooks/l7r-guard.sh`, `newer`). The no-fork `[[ ]]`
  walk pays 2.4 ms: not built, `find` pays more and fails toward the walk.
- **The `env` hop pays 3.1 ms (A - E)**, a second lever in another guard file (`l7r-hook` execing `bash "$h"`, or the shebang):
  filed, not built here (the brief's one job).

Daily: about 10,400 PreToolUse and PostToolUse calls on 2026-11-26 (T373) x 4.1 ms = 43 s; the `env` hop 32 s more.
