# 451 T490 - the check state read in part on the hot hooks, before and after

Method: `t490-time.py <before> <after> 20` (T387's `t387-time.py`, with two more cases and a `T490_STRIP_<label>` arm that drops
top-level keys from one fixture's copy). Two guard binaries, `l7r-guard.good` of this tree before the change (HEAD 72fba93ac9) and
after it, each on its own fixture tree holding a copy of the clone's `checks-open.json` (2,619,265 bytes, 3,054 dispatches, copied
from the clone's common git dir 2026-11-27 07:47) with one running hold on a plan section. Per case 2 warm-up and 20 counted
rounds, the two binaries INTERLEAVED round by round; `--only <guard> <event>`; CPU from `RUSAGE_CHILDREN`, wall from
`perf_counter`.

## Pricing the routes (the before binary against itself, one copy stripped)

CPU medians, ms, full state -> stripped copy (`t490-pricing.txt`, `t490-pricing2.txt`):

| case | `dispatches versions seen` dropped (load 16 to 20) | `dispatches` dropped (load 10 to 11) | `versions` dropped (load 11 to 12) |
|---|---|---|---|
| Bash `true` PreToolUse under a hold (record-edit-hooks) | 81.8 -> 19.1 | 34.2 -> 10.9 | 37.4 -> 32.9 |
| its PostToolUse (checks-hooks) | 88.7 -> 17.5 | 31.5 -> 8.7 | 33.7 -> 32.8 |
| a non-check Agent's PostToolUse (checks-hooks) | 75.8 -> 37.4 | 44.2 -> 25.2 | 47.4 -> 45.0 |
| that Agent's PreToolUse (check-bundle-hooks) | - | 28.0 -> 7.2 | 27.4 -> 27.0 |

The `dispatches` arm is route (a)'s ceiling (no row in the hot file), and the `versions` arm is route (c)'s ceiling (no version
kept). Route (b), a partial read, is measured below.

## Before and after (route b)

CPU median ms (wall median), before -> after, two runs, load 3.2 to 4.8 and 4.5 to 4.7 (`t490-time-run1.txt`, `t490-time-run2.txt`):

| case | run 1 | run 2 | writes |
|---|---|---|---|
| bash-pre | 37.1 (37.9) -> 18.4 (19.0) | 38.3 (38.9) -> 19.5 (20.2) | 0/22 both |
| bash-post | 32.7 (33.7) -> 15.0 (15.6) | 31.9 (32.6) -> 15.7 (16.1) | 1/22 both (the warm-up's feature switch) |
| agent-post | 45.9 (46.5) -> 29.6 (30.5) | 46.2 (46.9) -> 29.1 (29.7) | 0/22 both |
| agent-pre | 28.7 (29.7) -> 10.2 (10.8) | 29.4 (29.8) -> 10.1 (10.6) | 0/22 both |
| agent-stop (SubagentStop) | 93.7 -> 92.0 | 95.1 -> 92.2 | 22/22 both: 14 wave rows wait (filed as T505) |

## Every answer unchanged

`t490-diff.py <before> <after> <state>` (`t490-diff.txt`) runs 15 calls on each binary's own copy and compares the exit code,
stdout, stderr and the state file's bytes after every call. The tree's path is written `<root>`, and a time the call itself stamped
is written `<now>`. The calls: a hold's first Bash call (its save) and end, a steady one and its end, an Edit of a frozen page, an
Edit of the held plan, an `apply-edits`, an Explore's dispatch, launch and return, a pending dispatch launched, a running check's
return, the hold's review's return, a TaskStop, and a quote-check's dispatch. Result: 15 of 15 the same on the clone's state, and
15 of 15 on a state that is not JSON. Because the state's bytes are the same after every call, every cold reader of the file reads
what it read: the gate's `settled.rs`, the bundles, the arbiter's, `popup_rounds`, and the guard's own close and record answers,
which still use `load`.
