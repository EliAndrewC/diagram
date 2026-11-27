# 451 T387 - the plan hold's writes of the check state, before and after

Method: `t387-time.py <before> <after> 20` - two guard binaries (`l7r-guard.good` built from HEAD 2fbd648105 and from the T387 tree),
each on its own fixture tree holding a copy of the clone's `checks-open.json` (2,994,673 bytes, 3,054 dispatches, read from the
clone's common git dir 2026-11-27 06:15) with one running hold on a plan section; per case 2 warm-up and 20 counted rounds, the two
binaries INTERLEAVED round by round; `--only <guard> <event>`; wall from `perf_counter`, CPU from `RUSAGE_CHILDREN`; a write is the
state file's inode moving (`save` renames a temporary). Load 14 to 16 (`t387-results.txt`).

| case | before: CPU median (wall median / min) | after | writes before / after |
|---|---|---|---|
| Bash `true` PreToolUse, record-edit-hooks, under a hold | 98.8 ms (104.5 / 93.0) | 42.6 ms (43.3 / 34.1) | 22/22 / 0/22 |
| the same call's PostToolUse, checks-hooks | 92.6 ms (93.8 / 83.1) | 38.2 ms (38.9 / 29.5) | 22/22 / 1/22 (the warm-up's feature switch) |
| a non-check Agent's PostToolUse, checks-hooks | 108.1 ms (109.3 / 95.1) | 52.6 ms (53.2 / 44.0) | 22/22 / 0/22 |

A Bash call under a hold paid both hooks: 191 ms of CPU before, 81 after. What is left is the parse of the 3.0 MB state, which every
hook that reads it pays (filed as T490). A first cut of the Agent case compared a clone of the whole state before and after its
bookkeeping: 95.5 ms, the clone and compare 55 ms of it, so it was replaced by a test of whether the event names any dispatch or
hold (`handle::concerns`).

Pruning (`t387-pruned.txt`, the after binary, load 11 to 12): `counted` and `quote_notes` dropped from the 2,447 rounded dispatches,
2,994,673 to 2,703,627 bytes (9.7%): 36.0 / 33.4 / 48.4 ms of CPU against 42.6 / 38.2 / 52.6 - about 4 to 6 ms a call, at a lower
load, so an upper bound.

The readers of the kept dispatches, found by grep over `rust/` for `"dispatches"`, each field name, and every `state_path` / `load`
of the state (2026-11-27), with what each reads:

| reader | reads |
|---|---|
| `checks/rounds.rs` `running`, `open_round`, `pair_wave`, the batch sibling test, `flying` | live rows: `state`, `t`, `subjects`, `check`, `aid`, `wave`, `wave_len`, `reply`, `manifest`, `notes` |
| `checks/rounds.rs` `returned` | `aid`, `reply`, `rounded`, `counted`, `check`, `subjects`, and `quote_notes` through `fixloop::returned` - `counted` and `quote_notes` only while `rounded` is false |
| `checks/rounds.rs` `launched` / `apply_marks` | `marks`, at launch only (a wave row never: filed as T488) |
| `checks/rounds/freeze.rs` `dispatches_since`, `close_dispatches`; `answered_count` | `t`, `prewrite`, `state`, `aid`, `subjects`, `check` |
| gate `record/apply_edits/settled.rs` | every row's `reply` and `check`, all time |
| gate `bundle/record/bundle/earlier.rs`, `keys.rs`, `modal.rs` | `check`, `subjects`, `t`, `state`, `reply`, `notes`, since the feature's start or all |
| gate `arbiter/bundle.rs`, `sections.rs` | a unit's rows: `check`, `subjects`, `t`, `owed`, `manifest`, `reply`; `rounds`, `rebased` |
| gate `trials/measure/popup_rounds.rs` | `check`, `subjects`, `t` |

So `counted` and `quote_notes` of a rounded row are the only fields no reader needs: pruned at a return (`rounds::returned`), which
prunes the rows already rounded too. `owed` (465 KB) and `manifest` (212 KB) are read by the arbiter's bundle; `marks` (222 KB)
stays while T488 is open; whole rows are held by `settled.rs` (T490).
