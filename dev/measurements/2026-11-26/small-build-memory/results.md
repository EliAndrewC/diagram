# 451 T347: what a small test build needs of memory, and how the tool can tell one before it starts

2026-11-26, added by the task's closing half: the knob as built is `L7R_BUILD_SLOTS_SMALL` (`rust/gate/crates/rustc/src/rustc/slot.rs`); this record, written before the build, names it `L7R_BUILD_SMALL_SLOTS`, and is left as it was written.

Measured 2026-11-26, 21:20-21:50 UTC, in the pool tree `diagram-backlog-t269`, one build at a time, beside other builders' work
(load 9.6 to 32.3 on 22 cores; the container's anonymous memory 0.7 to 1.8 GiB where a run began). Scripts beside this file:
`mem-sample.py` (the sampler), `windows.py` (its samples by `Phase` span), `small-run.sh` (one test run after a body edit),
`big-run.sh` (a build of the slot's own kind, run while HOLDING a slot). The raw rows: `small-runs.txt`, `whole-crate-runs.txt`, `big-cold.txt`.

## Method and its limits

A scratch cgroup is refused here (`mkdir /sys/fs/cgroup/t347-probe`: read-only file system), and `/usr/bin/time -v` reports the
largest ONE process, not the tree. So: the command is started in a session of its own and `/proc` is read every 20 ms (the
largest gap between two reads inside a build span was 100 ms, under load); every process of the session - make, the gate, cargo,
each rustc, the linker `cc` and the `rust-lld` it runs - is summed. `anon` is the sum of `RssAnon`, the anonymous memory the
container's limit counts (`docs/process-decisions.md`, "Two code builders at once"); `rss` the sum of `VmRSS`, file pages with it.
A spike shorter than the gap is missed. The sum of each process's last `VmHWM` over a span is NOT a usable bound here: it adds
peaks that were minutes apart and, in a test span, hundreds of test processes; it is in the raw rows and not below.

Each crate: T315's body edit (a statement with a new value at the head of the first function body of one file), then
`L7R_BUILD_SLOTS=0 make rust-test CRATE=<crate>`, three times. Run `w` is the first of a crate: more compiled in it than in runs 1
and 2 - a dependency's file put back by the run before (`git checkout` gives it a new time, and cargo judges a path crate by its
files' times, so `land` recompiled `reviews` at its committed content: 4 rustc), or the crate's own incremental cache stale
(`reviews`, run first with nothing edited before it, and the guard, whose one workspace dependency was untouched). Runs 1 and 2
are the body edit in a warm tree, the crate alone, its incremental cache warm.

## The test build after a body edit in a warm tree (the `build` Phase span: `cargo test --no-run` of one manifest)

| crate | run | load | build s | anon MiB | rss MiB | rustc at once |
|---|---|---|---|---|---|---|
| rust/gate/crates/land | 1 | 13.7 | 1.86 | 188 | 414 | 2 |
| rust/gate/crates/land | 2 | 14.7 | 1.30 | 190 | 408 | 2 |
| rust/gate/crates/task | 1 | 26.4 | 1.49 | 226 | 425 | 2 |
| rust/gate/crates/task | 2 | 24.8 | 1.53 | 229 | 426 | 2 |
| rust/gate/crates/plan | 1 | 23.8 | 3.23 | 301 | 514 | 2 |
| rust/gate/crates/plan | 2 | 23.8 | 2.91 | 306 | 527 | 2 |
| rust/guard/shared | 1 | 32.3 | 6.39 | 535 | 792 | 2 |
| rust/guard/shared | 2 | 30.3 | 4.27 | 512 | 766 | 2 |
| rust/guard | 1 | 27.2 | 3.68 | 541 | 810 | 2 |
| rust/guard | 2 | 25.5 | 4.36 | 544 | 799 | 2 |
| rust/gate/crates/reviews | 1 | 9.6 | 6.15 | 580 | 777 | 2 |
| rust/gate/crates/reviews | 2 | 13.4 | 5.50 | 568 | 763 | 2 |
| rust/gate/crates/measure | 1 | 22.3 | 6.41 | 635 | 847 | 2 |
| rust/gate/crates/measure | 2 | 19.5 | 9.45 | 630 | 844 | 2 |

Two rustc at once in every one (the library and its test build), the linker after them (`cc`, `ld.lld`: three linker processes
alive, one link). **One body edit: 0.19 to 0.64 GiB anonymous, 1.3 to 9.5 s.** That is the usual case and NOT the ceiling of "the crate alone":

## The crate alone, all of it (every non-test source body-edited at once, dependencies untouched, after a discarded warm-up)

| crate | files edited | load | build s | anon MiB | rss MiB | rustc at once |
|---|---|---|---|---|---|---|
| rust/guard (46,021 lines) | 85 | 8.7 | 18.88 | 1093 | 1380 | 2 |
| rust/gate/crates/measure (29,315, the largest gate crate) | 52 | 7.7 | 18.97 | 1107 | 1367 | 2 |
| rust/mode_a (41,575) | 100 | 9.9 | 26.61 | 1417 | 1780 | 2 |

(`rust/mode_a` after one body edit: 6.23 s, 403 MiB, 1 rustc at once.) **The ceiling of a build that compiles one crate alone:
1.42 GiB, 27 s** - as much as a cold build of a small crate's whole dependency closure (below). What a build of this class
never does is run many rustc: two at most.

## The first run of each crate (run `w`: a dependency recompiled, or the crate's stale incremental cache)

| crate | load | build s | anon MiB | rss MiB | rustc at once |
|---|---|---|---|---|---|
| rust/gate/crates/task | 24.7 | 9.95 | 330 | 665 | 3 |
| rust/gate/crates/plan | 23.0 | 10.24 | 478 | 734 | 2 |
| rust/gate/crates/land | 14.2 | 11.35 | 620 | 1016 | 4 |
| rust/gate/crates/reviews | 9.6 | 9.67 | 649 | 846 | 2 |
| rust/guard/shared | 24.5 | 30.73 | 736 | 1001 | 2 |
| rust/guard | 25.7 | 25.83 | 918 | 1200 | 2 |
| rust/gate/crates/measure | 17.1 | 28.43 | 1083 | 1327 | 2 |

Up to 1.08 GiB and 31 s, inside the ceiling above.

## The builds the slot was made for

Kept, not re-measured (`dev/measurements/2026-11-26/builder-count/`, the container's `anon` every 10 s): three trees in a
coverage build at once 6.4 GiB (6,539 MiB the highest sample, baseline 0.54), so about 2.0 GiB a tree; the later rounds' logs
3.3 to 3.9 GiB at their highest (`mem-samples-round1-three-warm.log` 3,939 MiB, `-round2-two-tier.log` 3,260,
`-round2-under-load-tests.log` 3,802; `mem-samples-two-builders.log` has another format and was not read). What they lack is one build's own tree,
measured here once each, holding a slot:

| build | load | s | anon MiB | rss MiB | rustc at once |
|---|---|---|---|---|---|
| cold test build: `cargo test --no-run` of `rust/gate/crates/land` into an empty target directory (every dependency) | 17.5 | 69.95 | 1171 | 1967 | 12 |
| coverage pass of `rust/gate/crates/measure` in the tree's coverage directory as it stood, one file body-edited (how much of it was stale is not known; its coverage build 40.0 s of 55.05; the pass ended red on five lines of `task_time/progress.rs` no test reached, twice running - filed) | 23.7 | 55.05 | 1103 | 1648 | 7 |

So one large build alone is 1.1 to 1.2 GiB by the tree's own processes, and the kept 2.0 GiB a tree at three at once is the
figure to budget with (it is the container's, with the sessions' own growth in it).

## Which calls of a builder's test run take a slot

`make rust-test` after an edit: the binary key's build (`kept.rs`, `binary_key`: `cargo test --no-run --message-format=json`) is
the compiling cargo call of a GREEN build; the test binaries then run directly (`side.rs`), no slot; a crate with doctests adds
a `cargo test --doc` (slotted, compiles the doctests only). A build that FAILS is asked again (`rustc.rs`, `stepped`:
`cargo test --no-run`, so the failure reads as cargo's own words), a second slotted call - a compile error, where a builder
iterates most, waits twice. `make builder-checks` adds the lint (clippy, slotted) - not measured here, filed.

## The rule the numbers support

Budget, in GiB anonymous: the sessions and their tools 1.4 (0.7 to 1.8 seen at these runs' starts, other trees' work in it) +
two slot holders at 2.0 each = 5.4. **Margin: 7 GiB of the 10 (GUESS, a knob; proposed by `builder-count/m1-results.md`, never
certified).** The room is 1.6 GiB: ONE build of a crate alone at its ceiling (1.42), or two after one body edit (2 x 0.64 = 1.3)
but not two at the ceiling (2.8). One tree runs one compiling call at a time (the run lock), so the builds of this class at once
are as many as the trees at work, which is not capped at two.

So: **a lane of its own, ONE wide** (a knob, `L7R_BUILD_SMALL_SLOTS`, GUESS: 1), not no slot at all, and not two. A build of one
crate alone waits only behind another of its kind (1.3 to 9.5 s after a body edit, 27 s at the worst measured), never behind a
coverage build; the 57.3 s wait T315 measured becomes at most that. The lane also bounds a WRONG telling as no slot would not:
at the worst three large builds at once, 3 x 2.0 + 1.4 = 7.4 GiB, under the limit by 2.6, where an unbounded skip has no ceiling.
What would widen it to two: the wide slots' holders measured at less than 2.0 GiB each with the slot on (alone they were 1.1 to
1.2 here), or a lane wait showing in `make task-time`.

## How the tool tells such a build before it starts

**By its inputs AND their times: nothing the build compiles but the crate's own sources has moved, or been rewritten, since this
same call last built here.** The check already holds every input's content id (`Kept::ids`) and the crates the manifest builds
from by path (`depended`). Two tests, both needed:

1. THE KEY: the content ids of every file of the crates it builds from, the workspace's manifests, lockfile and
   `.cargo/config.toml`, the crate's own `Cargo.toml`, the compiler, the call's feature words and the `RUSTFLAGS` it inherits.
   Kept in the TARGET directory the call builds into (a wiped or new one holds no key, so a cold build is never told small),
   written when the build passes.
2. THE TIMES: none of those files is newer than the key's file, whose time is the START of the build that wrote it (written
   before the build, moved into place when it passes). Content alone is not enough: cargo judges a path crate by its files'
   times, and `land`'s run `w` above recompiled `reviews` (4 rustc) at its committed content after a `git checkout` put the file
   back - a content key would have called that build small.

Where both hold, cargo finds every dependency's unit fresh and compiles the crate's library and tests alone: two rustc at most
and the ceiling above. Anything else (a dependency's edit or rewrite, a commit pulled into one, a manifest, the first build in
a tree, the counting build's first) takes a wide slot, as now. The same test must stand at BOTH calls a red build makes
(`binary_key`'s and `stepped`'s second asking). Cost: a filter over ids the run has read and one `stat` a dependency's file
(some hundreds to low thousands) - no process started; NOT yet timed (job 2's first step: it must cost well under the 2 s a wait
costs at the least).

NOT measured here, owed by whoever builds it: the telling's cost in the built tool; one real-tree negative (a body edit in
`rust/guard/shared` or `core`, then `land`'s test run, takes the WIDE slot - `depended` reads manifest text, so a fixture does
not prove the real graph); the waits before and after.

Weighed, not taken:
- cargo's unit graph (`--unit-graph`) and build plan: `-Z unstable-options`, which a stable toolchain refuses (cargo 1.87.0 is pinned;
  cargo's documentation, not run here: a bare cargo is refused by the make guard).
- no `--dry-run` exists for `cargo build`/`cargo test`.
- reading cargo's own fingerprints under `target/debug/.fingerprint/`: an internal format, a hash a unit and profile.
- "the kept result's key says only the crate moved": the verdict key is one hash, and holds what the tests READ at run time
  (`reads = ["."]` moves it with any file); the key above is that idea with the inputs that compile, kept apart.
