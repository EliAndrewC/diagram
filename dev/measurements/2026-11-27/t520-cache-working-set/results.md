# 451 T520: the build cache's per-tree working set, priced - measured 2026-11-27

Load this file when: you are weighing a way to shrink `~/.cache/l7r-cargo-target` beyond T515's prune (a pool tree's coverage
profiles, a free tree past `L7R_BUILDERS`, a shared cache for third-party crates, the landing tree), or asking where the
container's disk goes. Folds 451 T518 (the pool trees' idle coverage profiles).

Nothing was deleted from the real cache. Every figure reads it by `du` or stat, or reads file contents with O_NOATIME (the
sweep judges atimes, 451 T515). The cold builds ran into scratch target directories, which were removed afterwards. Units:
`du -h` and `df` figures are GiB, and the scripts' figures are GB (10^9). Each is labeled where it appears.

## The disk now (2026-11-27 about 16:45Z, BEFORE T515's prune: it has not run yet)

`df -B1G /`: 461 GiB, 358 used, 80 free (82%). `/`, `/diagram` and `/home/agent/.claude` are all the host's one partition
(`/dev/nvme0n1p3`). `du -xsh` (GiB, `disk-before.out`, and `du -xsh /*`):

| where | GiB | of which |
|---|---|---|
| `/home` | 235 | the build cache 230; `~/.claude` 16 (`projects/` 15, transcripts); `~/.local` 2.1; `~/.rustup` 0.8; `~/.cargo` 0.3 |
| `/tmp` | 26 | this session's scratchpad 21 (measurement leftovers: `t373` 3.6, `t388` 3.1, `m14` 2.4, `t386-bench` 1.1, ...); `/tmp/l7r-check` 1.1 |
| `/diagram` | 23 | the clones about 7 (each pool worktree 0.3), `diagram-research` 1.1, the rest the mirror and its git |
| `/usr`, `/host-l7r-repo` | 7.4 | |
| visible in all | about 291 | the other about 67 GiB of the 358 used are outside the container's view (the host's own files on the same partition) |

The build cache by tree (`du -sh`, GiB): the clone 104, the landing tree 39, t269 23, t270 23, t271 21, b1 16, the mirror 6.5,
`diagram-research` 0.01, `tree/` 12 KB. `make cache-clean DRY=1` now (`cache-clean-dry.out`, `cache-clean-dry-by-tree.out`):
87.1 GB (81 GiB) would go: the clone 54.9 GB, the landing tree 28.5, the mirror 3.3, and every pool tree 0. It stopped early with
"a build runs", so the budget's eviction was not priced.

## (a) A pool tree's coverage profiles (folds T518)

- **Size** (GB, `c-third-party.out`, every `cover-*` profile summed): t269 7.8, t270 7.6, t271 5.9, b1 1.9. That is **23.2 GB
  (21.6 GiB)**. T515's prune takes 0 of it, because the profiles are under two days old.
- **What still builds them.** `make builder-checks` has no cover step (Makefile, the FIRST TIER), and the pre-warm builds no
  coverage (`rustc/prewarm.rs` header: "A coverage build and the counting build are not warmed"). A COVERAGE-REPAIR builder does
  build them, which is the brief's one exception (`scripts/container/builder-brief.md`, TWO TIERS). The census
  (`a-cover-runs.py`, `a-cover-runs.out`) counts every `cover-build` phase in a pool tree since 2026-11-25, cut at the reversal
  recorded at 23:38Z on 11-26 (`docs/process-decisions.md`, commit 9b5e948896):
  - before the reversal: 116 builds.
  - after it: 9. Two are T271 at 23:39Z, briefed before the cut. One is T139 in b1 at 01:45Z, `crate-checks`, before the brief
    block changed at 03:34Z (3012655340). One is T512's coverage repair in t269 (16:19Z, 79 s; pool log: the `fix` brief at
    16:15Z). Five are T521 in t270 (16:36-16:42Z, 13-70 s each), a builder running now.
  - So the profiles are read by about one repair builder every few hours, and only for the crate family it repairs.
- **Rebuild cost when a profile is gone.** See the table below (`a-cover-cold-warm.sh`, `.tsv`): one gate crate's coverage,
  cold (empty target: the tool binary and the whole `cover-gate` family's dependencies) against warm. The real cold first coverage
  builds of each pool tree, 2026-11-26 13:57-14:23Z, three trees at once (`a-cover-runs.out`): browser 47-123 s, embed 50-153 s,
  the gate family 424-589 s, guard and shared 104-200 s, mode_a 113-285 s, phases 10-47 s. That is 15-20 minutes a tree for every
  family, and about 7-10 minutes for the gate family alone, which is the one the repairs touched (measure).

| `l7r-gate.sh rust cover --crate rust/gate/crates/measure`, `L7R_RUST_FRESH=1` | seconds | load at start |
|---|---|---|
| warm (t269's own `cover-gate`, last built by T512's repair) | 8.2 | 12.1 |
| warm, `src/lib.rs` touched | 4.2 | 11.9 |
| cold (empty target): 70.3 s of it the cover build, the rest the tool binary | 99.0 (1.04 GB written) | 11.0 |

So a repair of one small gate crate pays about **1.5 minutes** cold against under 10 s warm. A repair across the gate family pays
up to the 7-10 minutes above.

- **Verdict**: a candidate for the GM, NOT built here. Dropping a pool tree's `cover-*` at release frees about 23 GB. The cost
  falls only on a coverage repair in that tree, a cold cover build once per family. His rule of 2026-11-26 ("we definitely want
  those extra 6 minutes more than we want the 65G", `docs/process-decisions.md`, "reopens only on his word") was given for the
  clone and landing tree. A repair builder is on the critical path of a red batch gate, so the same trade applies here.
  A cheaper middle course is to evict a pool tree's `cover-*` only once idle past a knob (T518's ask): t269's `cover-browser`,
  `-embed`, `-mode_a` and `-phases` last built 11-26 14-15Z (`newest=` per profile, below), with 1.4 GB idle 26 h.

Newest file per profile (stat, UTC): t269 `cover-gate` 11-27 16:20; `cover-guard` 11-26 22:04; `cover-browser`, `cover-embed`
11-26 15:12; `cover-mode_a` 11-26 15:14; `cover-phases` 11-26 14:22. t270 `cover-gate` 11-26 23:08 (then T521 at 16:36 today).
t271 `cover-gate` 11-26 23:39. b1 `cover-gate` 11-27 01:46.

## (b) b1, the free tree past L7R_BUILDERS, held cold

- **Size**: 16 GiB (`du -sh`), 16.7 GB (`c-third-party.out`): debug 11.5, tool 3.3, coverage 1.9.
- **When it is taken.** A handout takes "the first free tree" (`task/src/builder_tree.rs` header), so b1 is taken only when the
  other three are held. It had 19 of 142 handouts since 11-26 12Z, and the last was at 10:04Z today (T384). From the pool log,
  the peak number of trees held per hour was 4 through 10Z and 3 from 11Z on. At `L7R_BUILDERS=3`, b1 is not taken.
- **Cold against warm, its next handout's first build** (`b-cold-warm.sh`, `.tsv`; `L7R_RUST_FRESH=1`, because a kept green result
  lives in the clone's git directory, not the target, and otherwise answers with no build. The first try, in `void-kept/`, timed
  only the tool binary's cold build: 94-98 s, 1.02 GB):

| crate | warm, nothing changed | warm, one file touched | cold (empty target) | cold, again |
|---|---|---|---|---|
| `rust/guard` (builder-checks: test, lint, format) | 5.9 s | 14.3 s | 165.9 s (1.59 GB written) | 4.9 s |
| `rust/gate/crates/measure` | 3.1 s | 10.6 s | 197.8 s (2.00 GB) | 3.5 s |

  Load was 4-12 on 22 cores. b1's own real cold first handout, 2026-11-26 20:44Z (`b-b1-builds.out`), took 85.4 s to build
  measure, 21.8 s for task, and 39.0 + 9.3 s for their lint. The handout also built the guard binary first.
- **Verdict**: holding b1 cold frees about 15 GiB (its 1.8 of coverage is counted under (a)) and costs nothing while 3 builders run.
  If the GM raises the count to 4 again, it costs about 2.5-3.5 minutes on each crate family a builder in b1 first touches, once,
  and every later handout is warm. A knob for him (drop a tree past `L7R_BUILDERS` idle over N hours, through
  `make builder-tree-drop`). Not built here.

Filed from this record: 451 T523 (the model trial's shared `tree` target, the cache root's loose files) and T525 (the `-land`
worktree removed with land-alone's retirement). The scratchpad's 21 GiB is T517's, filed by T515.

## (c) One shared compile cache for third-party crates

- **How much is third-party** (`c-third-party.py`, `.out`): a file under `deps/`, `build/` or `.fingerprint/` whose crate name is
  no workspace crate's. 18.0 GB across all seven trees, of 230 GiB. The pool trees hold t269 2.3, t270 2.7, t271 2.3 and b1 1.4 GB.
  Units held by 2 or more trees come to 14.3 GB, and **one copy of each would free at most 10.6 GB**.
- **Are they identical?** A sample of 120 multi-tree files (60 at random, the 30 largest artifacts, and 30 artifacts at random),
  hashed in every tree: 107 identical, 13 not. By bytes, 1.62 GB identical and 0.19 GB differing. The differing ones are the
  `.d` and `root-output` files, which name the tree's own target path, and some same-size `.rlib`/`.rmeta` a few bytes apart
  (`libgeo` rmeta: 48 bytes, a different hash in each of six trees; `libtokenizers`, `libserde_json`). So rustc's output is not
  byte-reproducible across trees, and a hard link from one tree into another would hand dependants an artifact they were not
  built against.
- **sccache**: 0.13.0 IS installed (`/usr/bin/sccache`, Ubuntu's package, installed for 451 T155 on 2026-11-22), so nothing
  needs the GM to install it. Nothing in the repository sets `RUSTC_WRAPPER`. It frees no disk: it keeps its own copy, and each
  target directory still holds its own. It was measured twice at 0 hits across target directories (T155, 2026-11-22, in
  `plan-done.md`; 2026-11-26, `dev/measurements/2026-11-26/build-levers/m9-results.md`, lever C: 0 of 18, cold +23%).
- **One target directory for all trees**: cargo locks the whole build directory per invocation, so the three builders and the
  clone would take turns on one lock. Cargo 1.87 has no stable way to keep the third-party units in a directory apart from the
  workspace's.
- **Verdict**: decline. The ceiling is 10.6 GB. sccache saves 0 GB, a shared target serializes every build, and a hard-link
  dedupe is a new mechanism over files that are not reproducible. It would reopen if a cargo with a split build directory
  reached the container.

## (d) The landing tree's cache once land-alone retires

- **Size**: 39 GiB now: `cover-gate` 26, debug 8.6, tool 4.0. T515's prune takes 28.5 GB of it, which leaves **about 10 GB**.
  That 10 GB, not 38, is this option's own saving.
- **What builds there**: only `scripts/land-alone.sh` (`LAND_ALONE_TREE`, default `<clone>-land`). Its builds over two days
  (`b-build-phases.py land`, `d-land-builds.out`) are 11-26 19Z and 11-27 03:57-04:03Z (T256 both times), and nothing since
  04:03Z. In the event logs, the land-alone lines since 11-26 are edits of the script, not runs.
- **Rebuild cost once retired**: 0. Before then, a land-alone landing after a drop pays a cold gate-family coverage build (the
  pool trees' 424-589 s above) plus a cold lint.
- **How it goes**: when 461's T302 part 4 removes the `-land` worktree, the sweep's dead-tree rule takes the directory without
  further help. On 2026-11-16 it removed `tree/`, 621 MB, as "a build directory of no live tree" (guard log
  `20261116T013815...json`). The removal needs to be a step of T302 part 4. Filed as 451 T525.

## Totals: what would remain

| step | frees (GiB) | cache after (GiB) | disk used after (GiB, of 461) | rebuild cost |
|---|---|---|---|---|
| now | - | 230 | 358 (78% used, `df` 82% with reserved blocks) | - |
| T515's prune (landed, not yet run) | 81 | 149 | 277 | 0 measured (T515's warm copy) |
| (a) pool trees' `cover-*` | 21.6 | 128 | 256 | one cold cover build per family, per repair in that tree |
| (b) b1 cold (less its coverage) | 14.8 | 113 | 241 | 0 at 3 builders; 2.5-3.5 min a family at 4 |
| (d) the landing tree after retirement | about 10 | about 103 | about 231 | 0 once land-alone is gone |
| (c) third-party dedupe | at most 9.9 | about 93 | about 221 | declined: no safe mechanism |
| the scratchpad's leftovers (not the cache; 451 T517's) | about 21 | - | about 210 | 0 |

Against the 100 GB budget (`L7R_CACHE_BUDGET_GB`), the prune together with (a), (b) and (d) brings the cache to about 103 GiB
(110 GB). That is one full build per tree for the clone (about 49 GiB after the prune), three warm pool trees (about 15 GiB each
without coverage) and the mirror (3).

## The stray files at the cache's root

- **`fixture-*.profraw` (28), `fixture-profraw-list`, `fixture.profdata`**, 4.1 MB, all dated 2026-10-30 18:10 local. They come
  from the Python era: `cargo llvm-cov` names its outputs after the package (`fixture`) in the target directory it was given, and
  444 T17 ("proven on the fixture", commits 2385129d1a and babe232cf5) ran `scripts/gates/rust_checks.py` and
  `tests/tooling/test_rust_tooling.py` that evening with the cache root as the target. Both were deleted with the Python tests
  (`rust_checks.py` removed in b4f5afd072, 2026-11-09). No live code writes them. The live gap is that nothing sweeps a loose
  FILE at the cache's root: the sweep judges build directories only.
- **`tree/`**: a build directory, not a test's. The model trial (`rust/gate/crates/trials/src/measure/model_trial/`, `case.rs`
  and `runs.rs` running each arm in `<out>/tree`) gives every arm's checkout the basename `tree`. The gate launcher names the
  target directory after the tree's basename and reads the account's home from `/etc/passwd`, not `HOME`
  (`scripts/gates/l7r-gate.sh` line 14; `rust/guard/shared/src/tool.rs` `gate_binary`). So every arm of the m14 trial (eight
  trees under the scratchpad's `m14/A/*/tree`, made 11-26 17:39-17:40Z) built into the one `~/.cache/l7r-cargo-target/tree`:
  `CACHEDIR.TAG` was written at 17:51:50Z and `.rustc_info.json` at 17:56:32Z. Concurrent arms share one cargo lock and one
  tool binary. The sweep evicted `tree/tool` (0.99 GB, "an idle tree's profile, least recently built", by low-disk) at
  2026-11-27 12:45:02Z (guard log `20261127T124502...json`), which moved the directory's mtime. It left the 12 KB shell.
  Filed as 451 T523.

## Commands

- `a-cover-runs.py`: `grep -h '"step":"cover-build"' <clone>/.git/l7r-events/*.jsonl | python3 -I a-cover-runs.py`
- `b-build-phases.py TREE [SINCE]` over the `"src":"rust"` lines of the same logs (`b-b1-builds.out`, `d-land-builds.out`);
  `b-prewarm-handouts.out` is the pre-warm's seconds per handout, from the same lines.
- `b-cold-warm.sh <scratch target> <out.tsv>` and `a-cover-cold-warm.sh <scratch target> <out.tsv>`, run from the T520 tree.
- `c-third-party.py ~/.cache/l7r-cargo-target c-workspace-crates.txt 60`
- `make cache-clean DRY=1` (`cache-clean-dry.out`); `du -xsh` as in `disk-before.out`.
