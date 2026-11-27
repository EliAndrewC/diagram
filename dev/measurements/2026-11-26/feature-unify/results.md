# 451 T325: one feature set a library in every test build - before and after

Measured 2026-11-26, 18:20-19:15 EST (23:20-00:15 UTC), in the pool tree `diagram-backlog-b1` at `24bf17c721`, its own target
directory, one run at a time, no load generator; another builder shared the machine (22 cores), so every wall figure carries its
load average. The method is T301 part 1's (`../cargo-hashes/gate-call.sh`: the gate's test build by hand,
`cargo test --no-run --message-format=json` with `-v` for `--quiet`, from the tree's root): `family.sh` runs it over the 28 gate
manifests in turn and counts rustc runs against distinct targets (crate, lib or test, its root source file); `rust-test.sh` times
the checks' own test step over the same 28; `featsets.sh` asks `cargo tree` what each crate's test build resolves, with no compile;
`phases.py` sums a window's `Phase` lines. Raw summaries: `family-runs.txt`, `rust-test-runs.txt`, `red-problems.txt`.

## The fix measured

Each crate's `[dev-dependencies]` names `testkit` on every crate of its build that has it, itself included (41 lines over 19
manifests, with `l7r_shared`'s `test-env` named by `l7r_shared` itself). No word of a test or coverage call changed; the lint gained a pass (below).

| what | before | after |
|---|---|---|
| crates resolved with more than one feature set over the 34 workspace crates' test builds (`featsets.sh`) | 6: `core`, `research`, `registry`, `owed`, `archive`, `l7r_shared` | 1: `l7r_shared`, apart on purpose (below) |
| root-and-crate pairs short of the fullest set (the pin test's red list, `red-problems.txt`) | 41: `research` 15, `registry` 12, `owed` 9, `archive` 3, `core` 1, `l7r_shared` 1 | 0 |
| after `touch rust/gate/crates/core/src/lib.rs`, the 28 test builds: rustc runs / targets / repeats (`family.sh`) | 75 / 58 / 17 (`owed` 4 times, `archive`, `bundle`, `registry` 3) | 58 / 58 / 0 |
| the same pass, wall | 42.6 s, load 12.8 to 10.0 | 40.0 s, load 12.8 to 7.8 |
| nothing touched, the 28 again | 0 rustc runs, 5.9 s | 0 rustc runs, 4.4 s |
| a constant appended to `core/src/lib.rs`, then the checks' test step over the 28 (`rust-test.sh`): wall | 171.1 s, load 50.5 to 26.4 | 51.6 s, load 23.1 to 17.6 |
| that run's `build` lines summed (`phases.py`) | 152.7 s in 27 lines, 53.4 s of it three waits for a build slot: 99.3 s compiling | 42.5 s in 28 lines, no slot wait |
| that run's tests | 1 crate ran (`checks`, 7.6 s), 27 kept by their binary | 1 crate ran (2.1 s), 27 kept |

READ THE WALL FIGURES WITH THEIR LOADS. The touch pass is the like-for-like one (load 13 both times) and moved 2.6 s: a touch
changes no content, so rustc's incremental cache answers a repeat in a fraction of a second - T301 part 1 called it a floor. The
appended-constant runs are ONE sample each under different load (50 against 23) and with slot waits only before; the 99.3 s
against 42.5 s of compile is not a clean 57% and is recorded as an upper bound. What is exact is the count: 17 of 75 compiles
(23%) were a library built again under another feature set, and none of 58 is.

The first run of the "before" touch pass was discarded: the tree's pre-warm (`l7r-rust prewarm`, started 18:41) was still
compiling beside it with the same words, and three manifests found their build already done (72 runs for 54 targets). It was
run again after the pre-warm ended at its ceiling; that run is the row above.

After the manifests changed, every testkit configuration was new to the tree: the 28 test builds took 200.1 s and 53 rustc runs
once (load 15.2 to 13.6), a one-time cost each tree pays at its first build after this lands.

## The coverage build

Not compiled and not timed (a builder runs no coverage). Shown the way T301 part 1 showed it, `cargo tree --offline -e normal,dev
-f '{p} [{f}]'` over `rust/Cargo.toml` with the `-p` sets it used: before, `-p l7r_gate_claims` resolved `owed []`, `research []`,
`registry []`, and adding `-p l7r_gate_bundle`, `-p l7r_gate_owed` or `-p l7r_gate_semantic` turned `testkit` on for one or more
of them (T301 part 1's section). After, `-p claims`, `-p claims -p bundle`, `-p claims -p owed`, `-p claims -p semantic`,
`-p core` alone and all 28 together each resolve `core`, `owed`, `registry`, `research` (and `archive` where it is built)
`[testkit]`: the set no longer depends on which crates owe coverage. The saving in the coverage directory is inferred from
that, as T301's 67 sibling hashes were.

## A production build compiles what it did

`cargo tree --offline -e features,no-dev --manifest-path rust/Cargo.toml -p <package>` for the seven packages the launchers
build (`l7r_gate` 463 lines, `l7r_gate_rustc` 187, `l7r_browser` 31, `l7r_embed` 550, `l7r_mode_a` 843, `l7r_phases`,
`l7r_guard` 172), captured before the first edit and again after the last: identical (`diff -r`), and no line of the seven
names `testkit` or `test-env`. A production build reads no `[dev-dependencies]` under resolver 2.

## The routes not taken, each asked of cargo 1.87.0

- A feature set named on the test call: `cargo ... --manifest-path rust/gate/crates/measure/Cargo.toml --features
  l7r_gate_owed/testkit` answers `error: the package 'l7r_gate_measure' does not contain this feature: l7r_gate_owed/testkit` -
  a call can name a DIRECT dependency's feature only (it works for `claims`, which names `owed`), and 20 of the 41 pairs are
  crates reached only through another.
- Workspace feature unification: `CARGO_RESOLVER_FEATURE_UNIFICATION=workspace` answers `warning: ignoring
  resolver.feature-unification without -Zfeature-unification`: not in the pinned stable cargo.
- The helpers always compiled (no feature): it would put the tests' seams into the tools - `owed`'s `entry_lines` reads a
  scratch record's `entry-lines.json` in place of the real report, `core`'s `env` reads a test thread's map - which the brief
  rules out.
- The whole family named in every call: every test build would then build all 28 crates' tests, where a builder's check asks
  for one.

## What changed for a test, and what only the gate can show

- `owed`'s `entry_lines` is the one place where `testkit` changes what code RUNS and not only what is public: eight crates
  (`gate`, `checks`, `ci`, `claims`, `land`, `measure`, `task`, `trials`) used to build `owed` without it and now get the seam.
  All 28 gate crates' tests ran after the change and passed (`rust-test.sh`'s settle run, 28 `test` lines, rc 0).
- `l7r_shared`'s `test-env` is NOT unified across the workspace: it makes `env` read a test thread's own map, and a gate
  crate's tests read the process's environment (`rust/guard/shared/Cargo.toml`). It is one set within the guard's family
  (`guard`, `guard/shared`), and the library is still built twice in a tree that tests both families.
- Lint: `cargo clippy --all-targets` reads `[dev-dependencies]`, so with a crate naming itself both of the lint's passes had
  its test-only feature on, and the lines compiled only with it off (`core/src/record/bundle.rs` 10 and 14, `core/src/build.rs`
  92, `owed/src/record/owed.rs` 254, `guard/shared/src/env.rs` 15, `guard/shared/src/checks/handle.rs` 82) were linted by
  nothing. Proven with a seed: `if name.len() == 0` (clippy's `len_zero`) in `core/src/build.rs`'s testkit-off `env`, and
  `l7r-gate.sh rust lint --crate rust/gate/crates/core` answered `lint clean on 1 crate(s)`. MENDED IN THIS TASK (the plan
  review's ruling): a third pass, `cargo clippy --quiet --lib`, for a crate whose `[dev-dependencies]` name itself. With it the
  same lint seeded as `name.len() < 1` fails the crate (exit 1); the seed was removed. Priced by `lint-pass.sh` over the six such
  crates (`lint-pass-runs.txt`): warm, the two passes 9.7 s and the third 10.0 s (6 check compiles, its configuration's first
  build); after a touch of `core` and `l7r_shared`, the two passes 14 check compiles and 23.9 s, the third 7 and 12.8 s, load 10
  to 14. All six lint clean through the three passes (`L7R_RUST_FRESH=1 l7r-gate.sh rust lint`, 27.4 s, load 16).
- `mode_a`'s manifest gained one line (`research` with `testkit`, which adds a public module and changes nothing that runs):
  `make rust-test CRATE=rust/mode_a` after the change, 362 passed, 67 s wall with its build (run after the plan section was
  written, which still lists it as the gate's to show).
- Not shown here, the landing's gate to show: the coverage run's verdicts on the 34 crates and lint over all of them (9 were
  linted here: `rustc`, `checks`, `core`, `owed`, `archive`, `research`, `registry`, `guard/shared`, `guard`).
