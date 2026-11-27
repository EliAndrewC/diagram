# 451 T392 - the reversal tripwire's read of the whole event log, priced and made cheap

Measured 2026-11-27, 00:15 to 01:05 local, by T392's builder. Two kinds of figure: the PRICING of the options (a temporary test
inside `rust/guard/shared`, its source kept as `t392-pricing.rs`, its output `t392-pricing.tsv`), which ran beside the crate's other
541 tests and is good for RANKING only, and the HOOK-LEVEL before and after (`t392-time.py`, T383's timer reused, in T373's
throwaway world), the figures of record.

## The options, priced (`t392-pricing.tsv`; median / 90th centile in ms, 20 runs after one warm-up, the test profile at opt-level 2)

On a copy of the real clone's 451 log, 44.4 MB and 169,220 lines, for two paths: the most edited (`specs/451-.../plan.md`, 1,092
PreToolUse Edit lines) and a pool worktree's `docs/usage.md` (43). Three runs were made; the third is the file, load1 24.7 (LOADED);
the first two (load1 21.9 and 23.4) ranked the same.

| option | plan.md | docs/usage.md | what it costs the WRITER, and refile |
|---|---|---|---|
| NOW: `read_to_string` of the whole log, the line screen, the parse | 206.5 / 258.9 (90 and 174 in runs 1-2) | 99.5 / 109.0 (70, 69) | nothing |
| the whole log's read alone, `read_to_string` | 48.0 / 87.4 | 37.5 / 39.1 | - |
| the whole log's read alone, `fs::read` (no UTF-8 check) | 59.5 / 121.8 | 33.4 / 34.2 | - |
| BYTES: `fs::read` of the whole log, `memmem` of the needle, only hit lines decoded | 144.6 / 164.9 (64, 53) | 77.8 / 82.6 (43, 44) | nothing |
| CHUNKED: the log read 64 / 256 / 1,024 KiB at a time, alone | 10.7 / 11.8 / 11.9 | 17.2 / 16.8 / 13.7 | - |
| CHUNKED 256 KiB, `memmem` of the needle over each chunk's whole lines, hit lines decoded and parsed (BUILT) | 27.4 / 28.1 | 40.0 / 70.6 (21.6, 22.4) | nothing |
| CHUNKED 256 KiB, std only: each chunk's whole lines decoded, the line screen | 51.1 / 52.9 | 103.3 / 109.3 | nothing |
| SIDE FILE: a 1.6 MB file of the log's PreToolUse Edit lines alone, `memmem` | 4.4 / 4.6 | 1.4 / 1.5 | one more open and append on every Edit's line, 0.00 to 0.01 ms; and every other writer kept in step (below) |
| KEPT OFFSET: the tail since a kept offset (64 KiB read by seek) | 0.01 | 0.01 | the tail holds no earlier Edit, so this needs a kept index of every earlier Edit line beside it: its price is the side file's read (1.4 to 4.4 ms) plus the index's write on the hook path |

What the figures show, against the task line's hypothesis: the cost is the ONE LARGE BUFFER (a 44 MB allocation filled and
page-faulted, about 33 ms), not the UTF-8 check (a few ms: `read_to_string` and `fs::read` are within each other's noise). The
same bytes read a chunk at a time take about 12 ms. `memchr`'s `memmem` over each chunk halves std's line-by-line `contains`.

What a side file or a kept index would have to keep in step, each a place a line can go missing and a reversal be missed:
`write_line` (the hooks' writer, `event_log_hooks.rs`), the `append_row*` family (the gate's in-process lines; none writes an Edit
today, so each would need a test that it never does), `make events-refile`'s append of a moved line to its target log and its
temporary-file-and-rename of the source (`--from` too; `rust/gate/crates/measure/src/measure/event_log/refile.rs`), its retask
(`refile/retask.rs`, a line rewritten in place), and a backfill of the 34 logs that exist. The precedent, `dispatches.rs`'s side
file `<events dir>-dispatches/<sid>.jsonl`, is a different case: it holds an Agent call's halves until its agent's first start, a
line missing there costs one booking, and refile neither reads nor writes it. A kept INDEX derived by the reader (rebuilt by a full
scan when the log's inode or length disagrees) needs none of the writers: that is the follow-up filed, a new mechanism and two
builders by the sizing rule.

## The proof on the real logs (`t392-differential.tsv`, `t392-differential.rs`)

A temporary test inside the crate, over a copy of every log of the real clone's `.git/l7r-events/` (34 logs, 479,705 lines). The
oracle is the FULL PARSE of every line (`parse_all`, every line JSON-parsed and kept where `ev`, `tool` and `path` match), not
T383's screen. For each log, every distinct path of a PreToolUse Edit line: the new read (`replaced` on the file, 256 KiB chunks)
against the oracle's list, in order.

- 8,958 PreToolUse Edit lines the full parse uses: 0 dropped.
- 1,878 paths: 0 lists differing (order included).
- The 451 log: 169,220 lines, 5,019 Edit lines over 786 paths, 0 dropped, 0 differing.

Every log is valid UTF-8 (observed 2026-11-27, method: `iconv -f utf-8 -t utf-8` over each copy, 0 failing), so the one outcome that
changes - a line that is not UTF-8 costs only itself, where the whole-string read returned no line at all - is the fixture's.

## Before and after, at the hook (`t392-timing.tsv`)

T373's sandbox reused as it stood (its 451 log 42.0 MB, 160,231 lines); `t383-time.py` unchanged as `t392-time.py`; BEFORE the
binary of this tree before any edit of `reversal.rs` (the launcher's `L7R_GUARD_PRINT_FRESH=1` build of `0327c6aa67` plus an
unused dependency line and test code), AFTER the same launcher's build with the change; eight arms interleaved, 20 counted runs
after a warm-up round. Load1 10.1 to 12.6 on 22 cores (not LOADED).

| an Edit of a doc, PreToolUse | before | after | saved at the median |
|---|---|---|---|
| a builder in a pool WORKTREE, the hook (launcher + binary) | 100.5 / 390.3 | 50.1 / 139.5 | 50.4 |
| ... the binary, every guard | 88.4 / 227.5 | 33.7 / 81.0 | 54.7 |
| ... `event-log-hooks` alone | 83.9 / 225.4 | 29.4 / 75.5 | 54.5 |
| ... `clone-sync-hooks` alone | 3.0 / 10.2 | 2.7 / 12.3 | 0.3 |
| the session in its CLONE (dirty), the hook | 172.3 / 188.1 | 129.1 / 148.4 | 43.2 |
| ... the binary, every guard | 157.5 / 169.0 | 116.5 / 131.0 | 41.0 |
| ... `event-log-hooks` alone | 72.0 / 85.1 | 28.3 / 32.1 | 43.7 |
| ... `clone-sync-hooks` alone | 91.5 / 100.0 | 88.2 / 108.9 | 3.3 |

Every call exited 0 with no output; the sandbox log gained 252 lines (3 log-writing arms x 2 binaries x 21 rounds x 2 sessions).
What is left in the clone's hook is `clone-sync-hooks`' `git status` (T383: 97 ms).

## The leak check (`t392-leak-check.txt`)

T373's method after the run: no line of a `t373-*` session in the real clone's or the mirror's event logs, no `t373-*`/`t392-*`
claim-map entry, nothing in the real `checks-open.json` or `arbiter-owed.json`; the one guard-log file naming the sandbox predates
this run (T373's own session's command). The sandbox clone was left clean.
