# 451 T355: what the lint of one crate needs of memory, pass by pass, and whether the small lane's telling can vouch for it

Measured 2026-11-27, 01:40-02:25 UTC, in the pool tree `diagram-backlog-t270`, one lint at a time, no load generator, beside other
builders' work (load 2.3 to 26.2 on 22 cores; the container's anonymous memory 0.6 to 2.4 GiB where a run began). Written before
any code of the task. Scripts beside this file: `lint-sample.py` (the sampler), `lint-run.sh` (one lint after a body edit); the
raw rows: `lint-runs.txt`.

## Method and its limits

451 T347's (`dev/measurements/2026-11-26/small-build-memory/results.md`): the command in a session of its own, `/proc` read every
20 ms, `RssAnon` summed over every process of the session (`anon`), `VmRSS` beside it (`rss`); a spike shorter than the gap between
two reads is missed (the largest gap inside a pass was 102 ms, under load). The edit is T347's: a statement with a new value at the
head of the first function body of one file; then `L7R_BUILD_SLOTS=0 scripts/gates/l7r-gate.sh rust lint --crate <crate>` (no
slot, so no pass waits and its memory is its own). Three things differ from a test build, and the sampler is a copy for them:

- **The compiler is `clippy-driver`.** Under `cargo clippy` every crate of the workspace is compiled by `clippy-driver`, which
  T347's sampler (it counts `rustc`) reads as none. Both are counted, as `compilers`, each with its `--crate-name` and target.
- **A pass is read from cargo's own words.** The checks write ONE `lint` `Phase` line a crate for all of its clippy calls, so a
  pass is the span in which the live `cargo clippy` process holds that pass's words: `targets` (`clippy --all-targets`),
  `features` (`clippy --all-targets --all-features`), `lib` (`clippy --lib`, the third pass of a crate that names itself in its
  dev-dependencies, 451 T325).
- **The probe must lint clean**, or the first pass is red and no later pass runs: its number is written with digit separators
  (`clippy::unreadable_literal`; the first run of all, of `land`, was red on it and is not in the rows).

Each crate: the edit and the lint three times. Run `w` is the first of a crate and is not the warm case: the checks' last lint of it
in this tree was older than commits the handout brought, or a dependency's file had been put back by the run before (`git checkout`
gives it a new time). Runs 1 and 2 are the body edit in a warm tree.

`no pass` in the raw rows is a compile seen while no `cargo clippy` lived: the launcher rebuilding the checks' own tool
(`l7r-rust`), where the edited file is in a crate that tool builds from (`core`, `guard/shared`). It is `rustc` with a link, it is
not the lint's, and it takes no slot today (`dev/audits/build-slot.md`, `cost:`); it is why a run's wall can be far more than its
passes (`guard/shared`: 15.1 s of wall, 10.2 s of passes).

## The lint after a body edit in a warm tree, by pass

| crate | run | load | pass | s | anon MiB | rss MiB | compilers at once | what compiled |
|---|---|---|---|---|---|---|---|---|
| rust/gate/crates/land | 1 | 11.3 | targets | 1.20 | 123 | 399 | 2 | its lib, its tests |
| rust/gate/crates/land | 2 | 11.3 | targets | 1.16 | 123 | 398 | 2 | the same |
| rust/gate/crates/task | 1 | 10.2 | targets | 1.35 | 137 | 428 | 2 | its lib, its tests |
| rust/gate/crates/task | 2 | 10.2 | targets | 1.36 | 136 | 425 | 2 | the same |
| rust/gate/crates/plan | 1 | 9.5 | targets | 1.57 | 151 | 423 | 2 | its lib, its tests |
| rust/gate/crates/plan | 2 | 8.9 | targets | 1.60 | 150 | 423 | 2 | the same |
| rust/gate/crates/reviews | 1 | 8.5 | targets | 2.62 | 210 | 503 | 2 | its lib, its tests |
| rust/gate/crates/reviews | 2 | 8.5 | targets | 2.50 | 210 | 505 | 2 | the same |
| rust/gate/crates/measure | 1 | 6.8 | targets | 4.20 | 289 | 590 | 2 | its lib, its tests |
| rust/gate/crates/measure | 2 | 6.3 | targets | 4.21 | 288 | 587 | 2 | the same |
| rust/guard/shared (names itself) | 1 | 4.5 | targets | 8.21 | 251 | 429 | 1 | its lib, its tests |
| | | | lib | 2.38 | 158 | 329 | 1 | its lib (the feature off) |
| rust/guard/shared | 2 | 3.9 | targets | 7.78 | 251 | 428 | 1 | its lib, its tests |
| | | | lib | 2.33 | 157 | 328 | 1 | its lib |
| rust/guard | 1 | 3.8 | targets | 5.23 | 344 | 644 | 3 | its lib, its binary, its tests |
| rust/guard | 2 | 3.5 | targets | 5.31 | 346 | 642 | 3 | the same |

In every row above the `features` pass ran 0.08 to 0.15 s at 31 to 34 MiB and compiled NOTHING: none of the seven crates has a
feature that its `--all-targets` build does not already have on, so the second clippy call finds every unit fresh. **One body
edit: 0.12 to 0.35 GiB anonymous a pass, 1.2 to 8.2 s, one to three `clippy-driver` at once, no linker** (a check build writes
metadata and links nothing).

Two more crates, for the passes the seven do not show:

| crate | run | load | pass | s | anon MiB | rss MiB | compilers at once | what compiled |
|---|---|---|---|---|---|---|---|---|
| rust/gate/crates/owed (names itself; builds from `core`, `research`, `registry`) | 2 | 17.0 | targets | 5.76 | 103 | 272 | 1 | its lib, its tests |
| | | | lib | 1.54 | 85 | 252 | 1 | its lib |
| rust/gate/crates/owed | 3 | 18.2 | targets | 4.35 | 102 | 273 | 1 | its lib, its tests |
| | | | lib | 0.93 | 85 | 253 | 1 | its lib |
| rust/gate/crates/owed, a TEST-ONLY file edited (`src/item_relabel.rs`, a `#[cfg(test)]` module) | 1 | 2.4 | targets | 1.28 | 102 | 271 | 1 | its tests alone |
| | | | lib | 0.11 | 32 | 74 | 0 | nothing |
| rust/mode_a (a `counters` feature of its own) | 1 | 24.2 | targets | 7.42 | 377 | 753 | 3 | its lib, its binary, its tests |
| | | | features | 8.19 | 377 | 753 | 3 | the same three again, the feature on |

So each pass is accounted for: `targets` always compiles the crate; `features` compiles it a second time only where the crate has a
feature its default test build leaves off (`counters`: `rust/mode_a`, `rust/phases`, `rust/gate/crates/pool`), and is a 0.1 s
no-op elsewhere; `lib` compiles the library once more with no dev-dependency read. The passes run one after another, never at once.

## The crate alone, all of it (every non-test source body-edited at once, dependencies untouched, after a warm-up)

| crate | files edited | load | pass | s | anon MiB | rss MiB | compilers at once |
|---|---|---|---|---|---|---|---|
| rust/gate/crates/measure (the largest gate crate) | 54 | 22.9 | targets | 4.75 | 310 | 626 | 2 |
| rust/guard | 85 | 13.2 | targets | 10.91 | 529 | 838 | 3 |
| rust/guard/shared | 81 | 12.7 | targets | 19.14 | 263 | 446 | 1 |
| | | | lib | 3.88 | 172 | 350 | 1 |
| rust/mode_a (the largest crate) | 94 | 20.4 | targets | 9.86 | 665 | 1048 | 3 |
| | | | features | 16.80 | 674 | 1079 | 3 |

(One file of `rust/guard` and two of `rust/mode_a` were left out: the probe before a `const` item or in a `const fn` does not lint
clean. Their first runs, red at the first pass, are in the raw rows: 556 and 633 MiB.) **The ceiling of a lint pass that compiles
one crate alone: 0.66 GiB anonymous, 19 s.**

## Is the lint of the test build's class?

Yes, and under it at every point measured:

| | the test build (T347) | a lint pass (here) |
|---|---|---|
| after one body edit | 0.19 to 0.64 GiB, 1.3 to 9.5 s | 0.08 to 0.37 GiB, 0.9 to 8.2 s |
| the crate's whole rebuild | 1.42 GiB at the most, 27 s | 0.66 GiB at the most, 19 s |
| compilers at once | 2 `rustc`, then a link | 1 to 3 `clippy-driver` (the library, then its tests and its binary), no link |

A check build generates no code and links nothing. The lane's budget is T347's and is not moved: sessions 1.4 GiB + two wide
holders at 2.0 = 5.4 against a 7 GiB margin (GUESS), leaving 1.6; the lane is one wide, so a lint pass in it REPLACES a test build
there and is never beside one, and its ceiling of 0.66 GiB is under the 1.42 GiB the lane was sized for. One thing the audit's
falsifier must be reworded for: it reopens the lane on "a slot-small build seen with more than two rustc", and a lint of a crate
with a binary runs three `clippy-driver` at 0.34 to 0.66 GiB all told - the bound that matters is the memory and "nothing but
this crate compiles", so the count for a lint is the crate's targets (three at the most in this workspace: no crate has an
integration test, an example or a bench; seven have a library and a binary, counted 2026-11-27 from the manifests and `src/`).

## Does the SAME telling vouch for it? No: the lint needs a key of its own, one a pass

Two measurements:

1. **The test build's key does not vouch for the lint.** A body edit of `rust/gate/crates/core/src/difflib.rs`, then `make
   rust-test CRATE=rust/gate/crates/reviews` with the lane on (green, a wide build: it kept its key,
   `l7r-alone/rust_gate_crates_reviews-test`, timed 20:40:51.1 local against the file's 20:40:47.5, so the test build's telling
   stands from then on), then the lint of `reviews`: its `targets` pass compiled `l7r_gate_core`'s library as well as `reviews`
   (row `dep-edit-after-test`: 3.55 s, 241 MiB, 2 at once). Clippy's check units have fingerprints of their own, which a test build
   does not freshen; a lint told by the test build's key would have been called alone there, wrongly.
2. **One pass does not vouch for another.** A body edit of the same file of `core`, then the lint of `owed` (row `dep-edit`): the
   `targets` pass compiled `core`, `research`, `registry` and `owed` (4.37 s, 121 MiB), and the `lib` pass, straight after it,
   compiled `core`, `research`, `registry` and `owed` AGAIN (2.96 s, 122 MiB) - the same crates with the test-only feature off,
   other units. So a pass is known to compile its crate alone only by what THAT pass last built: a key a pass, each holding its own
   words.

What the key needs is what T347's holds, with the pass's words in the place of the build's: the content ids of the crates it
builds from by path (a crate's dev-dependencies are read by `depended` too, which `--all-targets` compiles), what those compile
in, the workspace's files - `clippy.toml` is among them already (`kept.rs`, `WORKSPACE`) - the crate's own manifest (its
`[lints]`), the compiler, the pass's words with `-D warnings`, the inherited flags; and the times, for the reason T347 measured:
the lint after a dependency's file was put back at its committed content compiled the dependency again (rows `dep-put-back`:
`owed` 4.23 and 2.94 s for its two passes, `reviews` 6.31 s).

A dependency's edit is not the lane's class by rule, though it was small here too (`core`'s edit under `owed`: 121 MiB, 1 at once;
the first lint of `rust/mode_a` after the handout, eight crates: 624 MiB, 3 at once, 28.9 s). It stays wide: how much a
dependency's edit recompiles is not bounded by one crate.

## What this supports (job 2)

The lint of a crate takes the small lane at each pass whose own key stands with no keyed file newer, and a wide slot otherwise -
the first lint of a crate in a target directory, the lint after a dependency's edit or put-back, a pass after any red wide pass.
The lane's width, budget and knob are not changed.

NOT measured here, owed by the build: the wait before and after in the built tool (`make builder-checks` of `reviews` with both
wide slots held); the telling's cost a pass; the real-tree negative in the built tool (a dependency's body edit told wide).
Not measured at all: a lint in the lane beside two compiling wide holders (the audit's memory falsifier reads it).

What of 451 T367 (the pre-warm and the lint keep no key, so a builder's first build of each crate after a handout is wide) a key
for the lint settles: the lint's half of "keeps no key" - a green lint pass keeps its key, so the SECOND lint of a crate in a tree
is in the lane. It does not settle the first: the pre-warm runs no lint, so nothing warms clippy's units or keeps a lint key
before a builder's first `make builder-checks`, and that lint is wide once for each crate (measured above as run `w`: 2.5 to 28.9 s
of compiling, its wait whatever the wide slots hold).

## The built tool: the lint's wait before and after (added once job 2 was built, 2026-11-27, 02:35-03:05 UTC)

The script is `lint-wait.sh` beside this file (451 T347's `lane-wait.sh` with the builder's whole first tier in its test run's
place): a body edit of `rust/gate/crates/reviews/src/reviews/census.rs`, both wide slots of a SCRATCH slot directory
(`L7R_BUILD_SLOT_DIR`) held by `flock <slot file> sleep 60`, nothing compiling, then `make builder-checks
CRATE=rust/gate/crates/reviews`, its `Phase` lines read from the event log; one run at a time, load 3.2 to 18.8. The raw rows:
`lint-wait-rows.txt`. The test build was in the lane in every held row but `knob-off` (451 T347), so the wait is the lint's.

| run | tool | holders | the lint's tellings (`slot-tell`, a pass) | the lint's wide wait (`slot-wait`) | the lint's lane (`slot-small`, a pass) | `lint` span s | make wall s |
|---|---|---|---|---|---|---|---|
| before1 | before the change | 2 x 60 s | - | 55.50 s | - | 60.16 | 65.8 |
| before2 | before the change | 2 x 60 s | - | 49.95 s | - | 52.97 | 63.9 |
| after-establish1 (the first lint by the built tool: no key yet) | built | none | NOT alone, 10 and 9 ms | none (slots free) | - | 2.77 | 7.9 |
| after-establish2 | built | none | alone, 6 and 9 ms | none | 1 and 2 ms | 2.71 | 7.7 |
| after1 | built | 2 x 60 s | alone, 6 and 9 ms | none | 2 and 1 ms | 3.37 | 8.9 |
| after2 | built | 2 x 60 s | alone, 6 and 5 ms | none | 1 and 1 ms | 2.68 | 7.7 |
| after3 | built | 2 x 60 s | alone, 6 and 8 ms | none | 1 and 1 ms | 2.77 | 7.9 |
| negative (body edits of `rust/gate/crates/core/src/difflib.rs` AND of `census.rs`) | built | 2 x 60 s | NOT alone, 5 and 5 ms | none: the test build before it, told wide too, had waited 56.41 s, and the holders were gone | - | 3.23 | 69.9 |
| after-negative-1 (both files put back: `difflib.rs`'s time moved) | built | none | NOT alone, 6 and 7 ms | none (slots free) | - | 3.21 | 13.4 |
| after-negative-2 | built | none | alone, 6 and 5 ms | none | 2 and 2 ms | 2.64 | 7.6 |
| knob-off | built, `L7R_BUILD_SLOTS_SMALL=0` | 2 x 60 s | none asked | none: the test build, wide with no lane, had waited 60.03 s | - | 2.67 | 67.7 |

**The lint's wait: 55.5 and 49.9 s before, none after (1 to 2 ms for the lane, three runs); the builder's `make builder-checks`
65.8 and 63.9 s before, 8.9, 7.7 and 7.9 s after.** The before rows' waits are under 60 s by the test build and tests that ran
first (4 to 9 s). **The telling costs 5 to 10 ms a pass** (the eighteen `slot-tell` lines of the lint above; `reviews` builds from
three crates), two passes a crate, three for one that names itself.

Limits of these rows. The negative shows the TELLING (a dependency's body edit: both passes told wide, and wide again after the
file is put back, alone on the run after that), not a wide wait of the lint's own: one `make builder-checks` runs its test build
first, which waited out the 60 s holders. A dependency's body edit alone does not re-lint its dependent at all (the lint's kept
result reads a dependency's interface, 449 T113), which is why the negative edits both files. `knob-off` shows that with no lane
nothing is told for the lint either. Three passes in the lane are pinned by the suite's fixture
(`all_three_passes_of_a_crate_that_names_itself_take_the_lane_each_by_its_own_key`), not measured on a real self-naming crate here.
