# 451 T507 - where a hot hook's 5 to 8 ms over the arm with no `dispatches` goes

**The finding.** Most of the gap, 54%, is not the partial read. It is the guard's PREFILTER. Before `handle` runs, record-edit-hooks'
`record_edit_gate::holding` reads the whole state a first time to find `"plan_holds":`. It uses `split_once`, whose search costs 1.9 to
2.0 ms over the 2.0 MB ahead of that key. The same prefilter runs on EVERY Bash call, with or without a hold: 4.8 ms of a 7.1 ms call.

## Method

- **The binaries.** `t507-build.sh` builds two guards from the tree's HEAD (1e6c9ba0e7) in a scratch directory. It never touches the
  tree. `clean` is HEAD as it stands. `stamps` is HEAD plus `t507-stamps.patch`, which takes in-process stamps and appends them to
  `$T507_STAMPS` at the end of main. Each stamp records three things:
  - the wall time (`Instant`);
  - the process CPU (`clock_gettime(CLOCK_PROCESS_CPUTIME_ID)`, exact at the call; `/proc/self/schedstat` moves only at ticks);
  - the minor and major faults (`/proc/self/stat`).
- **Where the stamps sit:**
  - the prefilter's read, scan and drop (`record_edit_gate::holding`; `checks_hooks::state_holds_snaps` for bash-post);
  - the lock;
  - `Part::read`'s `read_to_string`, and the partial parse;
  - the hook's own work, the drop of the state, and the exit.
- **The tools.** perf, gdb and strace are refused here (ptrace is not permitted).
- **The timing.** `t507-time.py` runs the arms on fixtures built by `t507-fixture.py`. Each fixture is its own tree with a COPY of the
  clone's state: 2,618,222 bytes, copied 2026-11-27 08:49, never the real file. It holds one running plan hold, and its snapshot is
  taken by a first call.
  - Runs: 2 warm-up and 20 counted, every arm once a round, INTERLEAVED.
  - Totals: CPU from `RUSAGE_CHILDREN`.
  - Each interval: the median over the 20 runs of that interval's CPU.
  - Raw stamps of each arm's first counted run: `t507-raw-<case>-<arm>.tsv`. No label pair repeats in a run, and no `whole` parse
    happens on this path.
- **The arms:**
  - `full`: the copy.
  - `full-reread`: the stamps build reads the file a second time into the buffer the first read faulted in. That is the copy
    without its faults.
  - `padded`: `dispatches` replaced by one string. The file is the same byte count, so the read and the faults are the same and
    there is little to scan.
  - `nodisp`: `dispatches` dropped (T490's 10.9 ms arm).
  - `floor`: `dispatches`, `versions` and `seen` dropped.
  - `nohold` and `nohold-nodisp`: full and nodisp with `plan_holds` empty, which is any Bash call outside a hold.
- **The stamps' own cost.** The `clean` and `stamps` totals agree within 0.8 ms: full 18.21 against 17.81, nodisp 9.50 against 10.27.

## bash-pre under a hold (record-edit-hooks PreToolUse, a Bash `true`): two runs

The output is in `t507-time-pre-run1.txt` (load 18.5 to 17.4) and `t507-time-pre-run2.txt` (load 17.4 to 16.2).

| total, CPU median ms | run 1 | run 2 |
|---|---|---|
| clean: full / nodisp / gap | 18.21 / 9.50 / 8.71 | 17.35 / 8.87 / 8.48 |
| stamps: full / nodisp / gap | 17.81 / 10.27 / 7.54 | 17.58 / 10.20 / 7.38 |

The gap is split below by interval, as full - nodisp in ms of CPU, run 1 then run 2. The full arm's own figure follows in brackets
(run 1, with its minor faults).

| part | gap run 1 | gap run 2 | share of the gap | full's own (run 1) |
|---|---|---|---|---|
| **the prefilter's read** (`holding`, `read_to_string` of the whole file) | +1.98 | +2.01 | 26-27% | 2.75 ms, 641 faults (nodisp 156) |
| **the prefilter's scan** (`holds_text`, `split_once("\"plan_holds\":")`) | +1.98 | +1.85 | 25-26% | 2.02 ms |
| the prefilter's drop of its 2.6 MB text | +0.13 | +0.16 | 2% | 0.20 ms |
| **the prefilter, all told** | **+4.09** | **+4.02** | **54%** | 4.97 ms |
| `Part::read`'s read | +1.64 | +1.69 | 22-23% | 2.23 ms, 639 faults |
| the partial parse (`Top`, `Skip` over `dispatches`, `versions`, `seen`) | +2.26 | +2.24 | 30% | 3.47 ms |
| the hook's own work (snapshot compare, feature, freeze) | -0.61 | -0.50 | -7 to -8% | 3.11 ms |
| the state's drop, the lock, the exit and its reaping | +0.21 | -0.01 | 0-3% | |
| before main (exec, the loader) | -0.05 | -0.09 | 0% | 1.73 ms |

- **The faults against the copy.** In `full-reread`, the second read into the faulted buffer took 0.53 and 0.54 ms with 1 fault. The
  first read took 1.97 and 1.92 ms with 639 faults. So about 1.4 ms of each 2.6 MB read is its page faults, and about 0.5 ms is the
  copy.
- **The scan, and why `split_once` is slow.** The `padded` scan is 0.30 and 0.41 ms against `split_once`'s 2.02 and 1.89 on the
  same byte count, so the cost is the real text's content (150,040 `"` in the file, `grep -o`), not its length. bash-post's
  `contains("\"plan_snaps\"")` searches the same 2.0 MB to a key 273 bytes past `plan_holds` (byte offsets 1,999,828 and 2,000,101,
  observed with `grep -bo` on the fixture), and takes 0.27 ms (below). The likely cause, not measured apart: std's `str::contains`
  has a SIMD path on x86_64, and `find` and `split_once` take the scalar Two-Way search.
- **The other keys' values** (what the task line asked about) cost about 0.2 ms. That is `floor`'s whole partial parse (0.21 ms),
  with every kept key made a value.
- **The skip of `dispatches`' structure** costs 2.0 ms. That is `full`'s 3.47 against `padded`'s 1.50 and 1.45. T506's `IgnoredAny`
  priced its exactness at about 1 ms of that.

## bash-post under a hold (checks-hooks PostToolUse): one run

The output is in `t507-time-post-run1.txt` (load 17.4).

- The clean totals are 14.56 for full and 8.14 for nodisp, a gap of 6.42. The stamps gap is 6.15.
- The prefilter (`state_holds_snaps`): read +1.73, scan +0.25, drop +0.13, so +2.11 (34%).
- `Part::read`'s read: +1.47 (24%). The partial parse: +2.31 (38%).
- No part is most of it here. The prefilter's `contains` is already cheap. Its read, and `handle`'s second read of the same file, are
  what is left.

## Any Bash call outside a hold: no `handle` at all

The output is in `t507-time-nohold-pre.txt` and `t507-time-nohold-post.txt` (load 12.7).

| case, CPU median ms | clean, the copy | clean, no `dispatches` | the prefilter's read + scan + drop (stamps) |
|---|---|---|---|
| bash-pre (record-edit-hooks) | 6.54 | 2.63 | 2.69 + 1.92 + 0.22 = 4.83 of 7.11 |
| bash-post (checks-hooks) | 4.45 | 2.43 | 2.29 + 0.25 + 0.21 = 2.75 of 4.72 |

- **The count.** On 2026-11-26 the diagram sessions made 6,141 Bash calls, observed 2026-11-27. Method: tool_use blocks named `Bash`
  with that date's timestamp, counted with Python's `json` over `~/.claude/projects/-diagram*/**/*.jsonl`.
- **The daily cost.** Every one of those calls pays both prefilters on today's state: 4.83 + 2.75 = 7.6 ms. That is about
  6,141 x 7.6 ms = 47 s of CPU a day. Under a hold, `handle` then reads the same file a second time.

## The lever (filed; nothing built)

The prefilter is most of the gap: 4.0 to 4.1 ms of 7.4 to 7.5 (54%), on both runs. It is also the whole of the state's cost on
every Bash call outside a hold. Three routes were measured above; none was built:

- **Search without `split_once`.** `memchr::memmem`, or `contains` plus the position, would take the scan from 1.9 to about 0.3 ms
  (bash-post's `contains` on the same bytes).
- **Do not fault in a 2.6 MB buffer to find one key.** Read through a small reused buffer, searching as it goes. That avoids about
  1.4 ms of faults a read (the reread arm) and the 0.2 ms drop.
- **Under a hold, read the file once.** `handle` would take the prefilter's text where the file is unchanged under the lock. That
  saves `Part::read`'s 2.2 ms.

The parts left after the prefilter, `Part::read`'s faults (about 1.4 ms) and the skip of `dispatches` (about 2.0 ms), are each under
a third of the gap. They are not filed on their own.
