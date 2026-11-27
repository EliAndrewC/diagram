# Where `l7r-rust` spends its start after a guard edit (451 T341)

Load this file when: weighing the checks' start-up cost, or the code-views cache's stamp (`rust/gate/crates/rustc/src/rustc/kept.rs`, `this_binary`).

## Method

Temporary step lines (`step-lines.diff`, taken against HEAD, so it also carries T364's `run_in` hunks; every line it adds is marked
`T341STEP`; all were removed once the measurement was taken). `T341_STEPS=1` printed seconds since `cli` started at each step of `Kept::read` and at
the binary key's build. Each run: a new `pub const` appended to `rust/guard/src/lib.rs` (a code edit, so the guard's key moves), then
`make rust-test CRATE=rust/guard`, in the pool tree diagram-backlog-t269. Three runs before the fix and three after. The load average is
on each run's first line in `before-steps.txt` and `after-steps.txt`.

## Found

| step (s since `cli`) | before, runs 1-3 (load 44.6 / 45.4 / 44.8) | after, runs 11-13 (load 10.5 / 9.9 / 9.3) |
|---|---|---|
| `git ls-files` + `hash-object` (content ids) | 0.95 / 0.96 / 0.42 | 0.18 / 0.16 / 0.17 |
| code views (`code_ids_kept`) | **5.78 / 6.48 / 6.30** | 0.05 / 0.04 / 0.05 |
| first cargo build starts | 7.50 / 7.66 / 6.95 | **0.33 / 0.30 / 0.30** |

The time goes to the code views, and the code views are recomputed for every Rust file: all 1,504 files, not just the one that was
edited. The cause is that the cache's stamp named the binary by size and modification time. `scripts/gates/l7r-gate.sh` runs a cargo build
whenever any file under `rust/guard` is newer than `l7r-rust`, and then `touch`es the binary (line 166), even though `l7r-rust` does not
build from `rust/guard`'s own sources. So the stamp moved, the whole cache was thrown away, and every file was read and hashed again.
The binary itself was unchanged (same size, same content). An unchanged run kept its stamp and spent 0.06 s on the views. Measured
right after a real rebuild at load about 12, a full recompute took 1.93 s. That is the 2.0 s T341 found, which at load 45 became 6 s.

Not the cause: the content ids (0.2 s at load 10), the comment-lint scan (0.04 to 0.4 s), the compiler version (0.03 to 0.07 s), the
verdict key and the telling (`slot-tell`, 0.02 to 0.2 s at load 45).

## Fix

The stamp is now `l7r-rust views <size> <time> <content id>`. If the size and time match, the cache is this binary's without reading
anything. If the time moved, the cache is still this binary's when the content id matches. A run whose stamp moved reads the 5.2 MB
binary once (about 0.05 s with `sha256sum`) and writes the new time back, so the next run reads nothing.
Test: `a_touched_binary_keeps_its_views_and_a_rebuilt_one_does_not` (`rustc/tests/kept.rs`). With the content check turned off it failed
(129 passed, 1 failed). With the fix it passes (130 passed).

## Left

When `l7r-rust` really is rebuilt (an edit of `rust/guard/shared`, `core`, `tree` or `rustc`), its content changes and all of the views
are still recomputed (1.9 s at load 12). This is on top of the 2.0 s rebuild. Keying the views on the code that reads them, rather than
on the binary, would remove that cost. It is filed separately rather than built here.
