# M9 - three build levers measured (port talk agenda item 9), 2026-11-26

Tree: a detached worktree of origin/main at c58377b1cf (`/diagram/.clones/diagram-backlog-m9`), 22 cores. Nothing tracked was changed.
The two heaviest test builds: the GATE family (`rust/gate` + its 27 `rust/gate/crates/*`, 231,737 lines of Rust, 28 manifests in one
call) and the GUARD family (`rust/guard` + `rust/guard/shared`, 87,294 lines); `rust/mode_a` is 41,545 and `rust/phases` 20,254.

What a row is: wall seconds of `scripts/gates/l7r-gate.sh rust test --crate ...` (what `make rust-test CRATE=` runs), build AND test
run together, into its own `CARGO_TARGET_DIR`, with `L7R_RUST_FRESH=1` (the kept-result key is by content, so a `touch` alone
runs nothing). `cold` = empty target dir. `warm` = after `touch` of the family's root library (`rust/gate/crates/core/src/lib.rs`,
which the 27 other gate manifests name - the worst one-file case; `rust/guard/shared/src/lib.rs`). `keep` = rerun with no touch (the test run
alone, no compile): gate 24.5 s, guard 14.6 s. The gate tool's own build (`tool/`, 0.2 GB) is outside every figure.

## The table (quiet runs only: load average 5-15 at the start of the run)

| lever | family | cold s | warm s, median of 3 (spread) | target GB | vs baseline |
|---|---|---|---|---|---|
| BASELINE (main today: `debug = 0`, incremental on) | gate | 327 | 54.9 (54.8-55.6) | 2.86 | - |
| BASELINE | guard | 91.0, 90.8 | 23.8 (23.7-23.8) | 0.68 | - |
| A reversed: `line-tables-only` | gate | 367 | 68.6 (67.9-75.8) | 6.13 | cold +12%, warm +25%, disk +114% |
| A reversed: `line-tables-only` | guard | 103.8 | 24.0 (24.0-24.6) | 1.20 | cold +14%, warm +1%, disk +76% |
| A': `CARGO_INCREMENTAL=0` | gate | 299 | 363 (one run) | 0.54 | cold -9%, warm +561%, disk -81% |
| A': `CARGO_INCREMENTAL=0` | guard | 86.3 | 100.4 (99.9-106.6) | 0.13 | cold -5%, warm +322%, disk -81% |
| C: `RUSTC_WRAPPER=sccache`, primed, fresh target dir | guard | 112.0 (prime 109.9); 0 cache hits of 18 cacheable requests, 31 in all | 25.6 (two more at load 13-41: 53.8, 84.5) | 0.68 + cache | cold +23%, disk +0 |
| C: the same with `CARGO_INCREMENTAL=0` | guard | 0 hits of 21 cacheable, 31 in all (seconds void: load 28-54) | 94.1 (94.0-125.5), 9 hits in the 3 | 0.13 + cache | nothing saved |
| B: coverage build, fresh | gate | 512 (at load 48-83) | 123 (one run, load 65) | 2.65 | the price of a drop: about +390 s |
| B: coverage build, fresh | guard | 282 (at load 50) | - | 0.56 | the price of a drop |

NOISE. Quiet, the guard repeats within about 2 s: cold 91.0 / 90.8; warm 23.7 / 23.8 / 23.8, 24.3 and one 25.7 at load 8.8 (8%).
The gate's warm repeats within 1 s (54.8-55.6) but its cold has ONE quiet baseline, so the gate's cold +12% and -9% have no measured
noise to stand against (the guard's cold +14% and -5% do: its two baselines differ by 0.2 s). Under other sessions' builds nothing
holds: the same baseline gave gate cold 542 s (load 15 rising to 33) against 327 s, gate warm 133 / 84 / 56 s, guard warm 41.9 s,
and at load 40-57 a guard cold took 215-317 s against 91 s. The A and A' rows were each taken in a quiet window beside a baseline in
the same window; the two coverage rows were not (the machine never came back down), so they are upper bounds.

## Verdicts

- LEVER A (lighter debug info): ALREADY ADOPTED, and one step further than the lever asks - `rust/Cargo.toml` line 101,
  `[profile.dev] debug = 0` (451 T246, 2026-11-25; `[profile.test]` inherits it; T96 had set line tables before it). Measured in
  reverse: going back to `line-tables-only` costs +12-14% cold, +1-25% warm and 2.1x the gate's target (6.13 GB against 2.86). Nothing
  needs debug info: coverage is `-C instrument-coverage` through `cargo llvm-cov` (`rust/gate/crates/rustc/src/rustc/cover.rs`),
  which reads its own mapping, not DWARF; a panic's file and line come from `Location` (both T246's notes in `rust/Cargo.toml`, not
  re-measured); no `RUST_BACKTRACE` is set in `scripts/`, `rust/`, the Makefile or `.claude/settings.json` (grep); all 28 gate
  crates' and both guard crates' tests passed in every configuration. Nothing left to adopt.
- LEVER A' (not asked; measured as lever C's control): `CARGO_INCREMENTAL=0` - DECLINE. It saves 81% of a fresh target (incremental
  is 2.28 of the gate's 2.83 GB) and is 5-9% faster cold, but a one-file rebuild goes from 55 s to 363 s on the gate and from 24 s to
  100 s on the guard. Far beyond noise.
- LEVER B (drop a worktree's coverage build after its landing): ADOPT for a worktree that ENDS at its landing, DECLINE for a tree
  that lands again - and both are what the sweep already does (451 T245, landed 2026-11-25), so nothing new to set. A tree that is
  gone never asks for coverage again, so the drop costs no time; `sweep/evict.rs` already takes a removed worktree's build directory
  with no idle wait. A tree that builds coverage again (the main clone, the reused `-land` target) pays one cold coverage build a
  drop: gate 512 s cold against 123 s warm (both at load 48-86, so upper bounds), guard 282 s (load 50) - time lost beyond noise on
  every landing, which the GM's condition excludes; for those the existing rule stands (a whole `cover-*` profile goes only past
  `L7R_CACHE_BUDGET_GB`, 100, once idle `L7R_CACHE_IDLE_HOURS`, 12; `rust/guard/src/guards/scratch_sweep_hooks/sweep/evict.rs`).
  Disk held today: `diagram-backlog` cover-gate 43.97 GB, cover-mode_a 4.42, cover-guard 3.59, cover-embed 1.82, cover-browser 1.15,
  cover-phases 0.26 = 55.2 GB of that tree's 93.9 GB; `diagram-backlog-land` cover-gate 26.24 GB of its 39.1 GB. There is NO
  separate counting build directory: `rust test-counters` builds `--all-features` into the same `debug/`.
- WHERE THE DISK IS (under B, like for like): a FRESH gate coverage target is 2.65 GB; the accumulated `cover-gate/` is 43.97 GB
  (26.24 GB in `-land`). Of `cover-gate/target/debug/incremental`'s 21.4 GB in 428 directories, 20.1 GB is in the 398 that are not
  their crate's newest (`-land`: 11.6 of 13.0 GB); of `debug/incremental`'s 16.6 GB, 15.9 GB in 616 of 653 (`debug/` holds every
  family, so its 31.15 GB has no fresh figure here beyond the gate's 2.86 and the guard's 0.68). Not all of the not-newest are dead: a
  crate's lib, binary and test variants are live at once. The sweep keeps a crate's newest 16 variants a store (`sweep/cargo.rs`,
  `KEPT = 16`, raised from 4 by 451 T158 on a measured 13 live `l7r_mode_a` variants), and those only once idle 12 h. THE TRADE the GM
  could rule on, declined above under his own condition: dropping `cover-gate/` at each landing's end frees up to 41 GB (main clone)
  and 24 GB (`-land`) for one cold coverage build at the next landing (at most +390 s over a warm one).
- LEVER C (sccache): DECLINE as the project builds today; measured on the guard only, not the gate. `sccache` 0.13.0 is installed
  (`/usr/bin/sccache`) and nothing in the repository uses it. Primed by one full build, a second build into a FRESH target directory
  got 0 hits - in the same tree (0 of 18 cacheable) and in a second worktree (0 of 18), with incremental on and off (0 of 21) - and
  the project gives every tree its own target directory (`scripts/gates/l7r-gate.sh` line 14; `rustc.rs` `cargo_in`). Cost: cold
  109.9 and 112.0 s against 91 s (+21-23%, load 9-12), no target GB freed, its own cache added (0.15 GB after six builds). It hit
  only on a rebuild into the SAME target directory (9 hits in 3 warm runs). Its ceiling: 18 of the guard build's 31 rustc calls are
  cacheable with incremental on, 21 with it off. NOT MEASURED: a rebuild into the same directory after an eviction emptied it (the
  one case it could pay back), and why a fresh directory misses (the target path reaches rustc in `--out-dir`, `-L dependency=` and
  the inherited `CARGO_TARGET_DIR`). Where it would be set if ever: `RUSTC_WRAPPER` in `rustc.rs`'s `cargo_in` environment.

## Commands

Harness: `/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/m9-run.sh <label> <gate|guard> <test|cover>
<cold|warm|keep> [ENV=VAL ...]`; every row it wrote is in `m9-raw.tsv` beside it (label, family, command, mode, exit code, seconds,
`du -sb` of the target, load average at the start, the lever's environment), each run's output in `m9-log-<label>-*.txt`.

- baseline: `m9-run.sh baseg2 gate test cold`, `... keep`, `... warm` x3; `m9-run.sh base2 guard test cold|keep|warm`
- lever A reversed: the same with `CARGO_PROFILE_DEV_DEBUG=line-tables-only CARGO_PROFILE_TEST_DEBUG=line-tables-only` (labels `ltg`, `lt`)
- incremental off: the same with `CARGO_INCREMENTAL=0` (labels `inc0g`, `inc0`)
- lever B sizes: `du -sb ~/.cache/l7r-cargo-target/diagram-backlog/*` and `.../cover-gate/target/debug/*`; stale variants: `m9-stale.sh`
- lever B price: `m9-run.sh covg gate cover cold L7R_RUST_COVER_WORK=$HOME/.cache/l7r-cargo-target/diagram-backlog-m9-covg` (and `cov guard`)
- lever C: `m9-queue2.sh` - `SCCACHE_DIR=<scratch> sccache --start-server`, then `m9-run.sh sc1 guard test cold RUSTC_WRAPPER=sccache`
  (prime), `sc2` (fresh dir), `M9_TREE=/diagram/.clones/diagram-backlog-m9b m9-run.sh sc3 ...` (second worktree), `sc4`-`sc6` the same
  with `CARGO_INCREMENTAL=0`; `sccache --show-stats` after each, in `m9-queue2.out`
- what the harness runs: `cd <tree> && env <lever> CARGO_TARGET_DIR=$HOME/.cache/l7r-cargo-target/diagram-backlog-m9-<label>
  L7R_RUST_FRESH=1 scripts/gates/l7r-gate.sh rust test --crate rust/gate --crate rust/gate/crates/<each> ...`

## Caveats

- One cold run a lever on the gate (5-9 min each); the quiet repeats agree within 1 s, but a cold figure is one sample.
- The machine was shared throughout (load 5 to 83). The first gate baseline (542 s cold; warm 133 / 84 / 56 s) was taken under load
  and is replaced by `baseg2`; its two `keep` rows overlapped each other and are void. The sccache seconds (`sc3`-`sc6`) and both
  coverage figures were taken at load 20-57 and are not time evidence; the sccache hit counts are.
- `=0` for lever A was not run separately: it IS the baseline.
- The warm case touches the most depended-on file of each family; a leaf file's rebuild is cheaper in every configuration.
- `mode_a`, `browser`, `embed` and `phases` were not timed.
- Side effects: each run wrote its `Phase` rows (build, test, cover-build, cover-run) to the event log `make task-time` reads, under
  the worktree's name; a second worktree, `/diagram/.clones/diagram-backlog-m9b`, was made for the cross-tree cache test. Both
  worktrees, every `~/.cache/l7r-cargo-target/diagram-backlog-m9*` directory and the sccache server and cache are removed.
