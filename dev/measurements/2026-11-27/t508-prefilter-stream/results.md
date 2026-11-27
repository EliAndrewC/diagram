# 451 T508 - the Bash hooks' prefilters stream the check state

**The finding.** Of T507's three routes, the stream through one small buffer saves the most. Outside a plan hold, as built, it saves
3.52 to 3.97 ms of a Bash call's record-edit-hooks `PreToolUse` and 2.30 to 2.47 ms of its checks-hooks `PostToolUse`. Under a hold it
saves 2.71 to 3.34 and 1.22 to 2.11. It is built in `rust/guard/shared/src/checks/scan.rs`, and every verdict is unchanged on copies
of the clone's state.

## Method

- **The binaries.** `t508-build.sh` builds four guards in a scratch directory, never the tree:
  - `clean`: the tree's HEAD (900332c7ec);
  - `A`: HEAD with `holds_text`'s `split_once` made `memchr::memmem::find` over the whole string (the read unchanged);
  - `C`: `A`, and under a hold the prefilter's string handed to `Part::read` in place of its read. This is a scratch static, and it
    leaves out the check that the file is unchanged under the lock, so C is priced at its best;
  - `B`: the tree's working files, the stream (`checks::scan`).
- **The timing.** `t508-time.py`, over T507's fixtures (`t507-fixture.py`):
  - the state: a COPY of the clone's state, 2,618,222 bytes, copied 2026-11-27 09:06, never the real file;
  - the trees: one per build and arm, since a call under a hold may write its state;
  - the call: a Bash `true`, through record-edit-hooks' `PreToolUse` and checks-hooks' `PostToolUse`;
  - the arms: under a running hold (its snapshot taken by a first call), and with `plan_holds` empty;
  - the runs: 2 warm-up rounds and 20 counted, every build once a round, INTERLEAVED; CPU from `RUSAGE_CHILDREN`, the median.
- **The verdicts.** Every call's exit code and stdout were compared across the four builds. There was one distinct output in each
  case, on every run.

## The routes on the same arms (CPU median ms; saved against `clean` in brackets)

B as built, which checks UTF-8 (below): run 3 (`t508-time-run3.txt`, load 10.9), then run 4 (`t508-time-run4.txt`, load 10.2 to 9.6).

| case | clean | A: memmem | B: the stream | C: memmem, string handed on |
|---|---|---|---|---|
| bash-pre, no hold | 7.29 / 6.98 | 5.34 / 5.84 (+1.95 / +1.14) | **3.32 / 3.46 (+3.97 / +3.52)** | 5.38 / 5.60 (+1.92 / +1.38) |
| bash-pre, a hold | 17.37 / 18.67 | 16.36 / 17.02 (+1.02 / +1.65) | 14.67 / 15.33 (+2.71 / +3.34) | **13.84 / 14.88 (+3.54 / +3.79)** |
| bash-post, no hold | 5.72 / 5.90 | 5.33 / 5.47 (+0.39 / +0.44) | **3.42 / 3.43 (+2.30 / +2.47)** | 5.17 / 5.56 (+0.55 / +0.35) |
| bash-post, a hold | 14.89 / 15.65 | 14.74 / 14.91 (+0.15 / +0.74) | **13.67 / 13.54 (+1.22 / +2.11)** | 15.73 / 15.75 (-0.84 / -0.10) |

Runs 1 and 2 (`t508-time-run1.txt`, `t508-time-run2.txt`, load 4.9 to 6.8) used the first B, which skipped the UTF-8 check and
stopped at the key on a yes too. They gave B +3.96 / +4.19 on bash-pre with no hold and +2.16 / +1.94 on bash-post, with the same
ranking.

- **Why B.**
  - C beats B only on bash-pre under a hold, by 0.45 to 0.83 ms (runs 3 and 4).
  - Outside a hold, B beats C by 2.05 and 2.14 ms on bash-pre.
  - Taking bash-pre alone, C would win only if more than 71% (run 3) or 83% (run 4) of Bash calls ran under a hold.
  - With bash-post counted, B wins in every case: A and C leave its `contains` as it was.
- **The daily figure.** Outside a hold, B saves about 6 ms a Bash call: 3.5 to 4.0 on the pre call plus 2.3 to 2.5 on the post call.
  At 2026-11-26's 6,141 Bash calls (T507's count), that is about 37 s of CPU a day.
- **C's saving is left, and filed.** Under a hold, B as built already reads the whole file, to check its UTF-8. So handing its bytes
  on to `handle` (C's saving) could now be had beside B. That is a new mechanism: `handle`'s read seam, plus the file's identity
  checked under the lock. It is filed as T509.

## UTF-8, as the whole-string read had it (`t508-nonutf8.py`, `t508-nonutf8.txt`)

- **The old behavior.** `read_to_string` failed on a file with one bad byte anywhere, and both prefilters then said no.
- **The first B broke this.** It checked no UTF-8. On a copy of the state under a hold, with one bad byte in `dispatches`, checks-hooks'
  `PostToolUse` then ran `handle`, which wrote its empty reading over the file ("file CHANGED"). HEAD left the file unchanged.
- **B as built.** It checks every byte as it reads, keeping the bytes of a character cut by a chunk's edge for the next chunk. It
  stops early only on a no: a yes reads on to the end to check the rest.
- **The result.** On the same fixture, HEAD and B now agree for both hooks: exit 0, no output, and the file unchanged.

## Where the key sits, and why no prefix read

- **The writer sorts the top-level keys** (`checks::save`, `pyjson::sorted`).
- **The positions.** In the copy, `dispatches` is the first key and 1,926,871 bytes of the file. `plan_holds` is at byte 1,999,829
  of 2,618,222, and `plan_snaps`, when present, comes after it.
- **So a prefix read cannot find either key**, and the size of every key before them moves them. The stream searches the WHOLE file.

## The differential (`t508-differential.rs`, run by `t508-differential.sh` in build B's scratch source)

- **The oracle.** The old `holds_text` (`split_once`) and `contains("\"plan_snaps\"")`.
- **The files.** Five copies:
  - the state copy itself;
  - a hold's fixture after its snapshot;
  - a no-hold fixture;
  - that hold with `plan_holds` emptied and its snapshot left (`hold-ended`);
  - the copy with no `plan_holds` key.
- **The chunk sizes.** 1 to 64, 4,096, `CHUNK` - 1, `CHUNK`, `CHUNK` + 1, 1 MiB, the file's length and one past it. Also every
  size that cuts either key at each of its bytes. Each file is also read through `holds` and `snaps` themselves.
- **The result.** 0 differing (`t508-differential.tsv`), for B as built.
- **The fixture cases.** The crate's own test holds the stream to the oracle on 27 cases, at every chunk size:
  - 6 that are not UTF-8: a bad byte before the key, after the key, inside its object and after the decision, and a character cut
    by the file's end;
  - one with characters of two, three and four bytes before the key.

## Red first (`t508-red-first.txt`)

Run with `make rust-test CRATE=rust/guard/shared ONLY="checks::scan"`, or `CRATE=rust/guard ONLY="guards::checks_hooks"` for the last
mutant. Each mutant was restored from its copy afterwards.

- **The old whole-file read behind the new seam:** `the_read_holds_one_chunk_and_stops_early_only_on_a_no` went red (4 passed,
  1 failed).
- **No carry of the key's first bytes across a chunk's edge:** `the_stream_answers_as_the_whole_string_did_at_every_chunk_size` went
  red (4 passed, 1 failed).
- **No UTF-8 check:** `the_stream_answers_as_the_whole_string_did_at_every_chunk_size` went red (4 passed, 1 failed), and so did the
  guard's own `a_state_that_is_not_utf8_is_left_as_it_is` (5 passed, 1 failed).

## Other readers of the state

The search: a grep of the guards for `checks-open.json`, `state_path` and calls into `checks::` (`load`, `handle`, `planhold`,
`rounds`, `arbiter`, ...), with each caller's matcher read.

- **Same way as these two:** none. No other hot guard reads the whole state to find one key.
- **record-edit-hooks' Edit of a `plan.md`.** It asks the same `holding`, so it is streamed too.
- **`event_log_hooks`** (matcher `*`) and **pair-hooks' review** (Bash). They reach `checks::arbiter`, which reads `arbiter-owed.json`
  and `arbiter.jsonl`, not this state. They do so only on a reversal Edit, or on a gate's third round.
- **`escalation_hooks`.** Its `state_path` is `escalation-state.json`, a different file, and it runs on Agent calls only.
- **`check_bundle_hooks` (dispatch) and `checks_hooks` (launched, returned).** They call `handle`, which needs the state's contents
  and reads them through T490's partial parse. They run on Agent calls and SubagentStops, not on every Bash call.
- **`rounds::drop_run`.** It runs from workflow-hooks, on a refused `check-wave` run alone.
- **`rounds::record_answer` and `handle::close`.** They run from the gate's commands (`make check-closed`, the owed checks' answers).
