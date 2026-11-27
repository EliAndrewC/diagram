# Who reads 451's large records whole, and how often: the BEFORE figure for the split (451 T536)

Task 451 T536 (462 FR-004, SC-002; the GM's seventeenth and eighteenth process-reviewer messages, `specs/449-rust-codebase/port-talk-gm-goal.md`).
Read-only, on COPIES, observed 2026-11-27. T537 splits the records; the AFTER figure is read with the same scripts (every path is
matched by its DIRECTORY prefix - the feature directory, the events directory - so a record split into parts is still counted).

## The snapshot (`t536-snapshot.txt`)

Taken 2026-11-27T20:03:07Z at HEAD c9f365a65b, copied to the scratchpad (`t536-copy/`): plan-review.json 5,026,023 bytes (64,589 lines),
plan-done.md 3,637,994 (22,086), tasks-done.md 600,807 (1,479), the event log `451-time-retro-and-efficiency.jsonl` 54,329,227
(204,679 lines); beside them plan.md 280,580 and tasks.md 36,254. Every figure below is of these copies.

## Method

1. **The readers, by code** (`t536-readers.py` -> `t536-readers.txt`): every non-test Rust line naming a record by name or by the
   constant or helper that stands for it (`tasks::DONE`, `RECORD`, `log_path`, `edit_lines`, `text_if_file`, `landings`), 285 lines;
   each hot one read by hand for whether it reads the file whole and on what trigger.
2. **The bytes a call, observed** (`t536-readers-run.py` -> `t536-readers-run.txt`): the real binaries (the pool tree's built
   `l7r-guard` and `l7r-gate`, copied) run against a `git clone --shared` of the tree carrying the record copies, under an
   LD_PRELOAD shim (`t536-readcount.c`) that sums each process's read() bytes per file - strace is refused in this container (ptrace
   not permitted). The shim counts read/pread/readv, not mmap or sendfile (Rust's `fs::read` uses read). Hooks are fed synthetic
   payloads; each case once under the shim, then 5 runs without it for the median wall time.
3. **The in-process cost of a whole read** (`t536-bench-main.rs`, `t536-bench-Cargo.toml` -> `t536-bench.txt`): a release Rust
   bench, warm page cache, the readers' own forms (fs::read; read_to_string + lines; a whole serde_json parse; `edit_lines`' filter
   and parse; `landings`' filter and parse). The machine: 22 cores, load average about 6 during the runs.
4. **How often** (`t536-counts.py` -> `t536-counts.txt`): the 2026-11-27 lines (UTC, 00:00 to the snapshot's 20:03:07Z) of the 451
   log copy, and apart the 461, 462 and `_unassigned` logs (a reader runs whatever feature a call is filed to).
5. **The builders' own reads** (`t536-builder-reads.py`, adapted from `../plan-reads/plan-reads.py` -> `t536-builder-reads.txt`,
   `-from-0200.txt`): the Read, Grep and Bash results naming a path under the feature directory or `l7r-events/451`, in the
   2026-11-27 builder transcripts. The seventeenth message's own script was not saved; this one is.

## A whole read, in process (`t536-bench.txt`, warm cache, median of 5 to 9)

| record | fs::read | read + lines | the reader's own work |
|---|---|---|---|
| plan-review.json, 5.0 MB | 1.1 ms | - | whole serde_json parse 15.9 ms (the plan crate's readers; the review-round guard's slim parse skips most fields) |
| plan-done.md, 3.6 MB | 0.5 ms | 2.1 ms | - |
| tasks-done.md, 0.6 MB | 0.1 ms | 0.2 ms | - |
| event log, 54.3 MB | 43.9 ms | 57.4 ms | `edit_lines` 162.7 ms (16,687 lines kept); `landings` 68.8 ms (277 rows) |

## The readers on the hot paths: bytes a call, observed on the copy (`t536-readers-run.txt`, `t536-readers-run2.txt`)

"Whole" means a call's bytes of the record are a multiple of its size. A row marked BY CODE could not be run on the copy; its
reader is named and its cost is the bench's.

| trigger (2026-11-27 count) | plan-review.json | plan-done.md | tasks-done.md | event log | wall median |
|---|---|---|---|---|---|
| every hook call: PreToolUse/PostToolUse Bash, PostToolUse Edit, SubagentStart, Stop (30,206 hook rows over 451, 461, 462) | none | none | none | opened to append, 0 bytes read | 3-28 ms |
| SessionStart (not logged) | none | none | none | none | 6 ms |
| PreToolUse Edit or Write of a file: `source_block_hooks` reads the edited file whole (plan.md 280,580 bytes here; 214 Edit/Write of plan.md, 0 of plan-done.md or tasks-done.md) | - | whole, only on an edit of it | whole, only on an edit of it | - | 6 ms |
| PreToolUse Agent, a spec-fidelity plan review (`review_round_hooks`; 197 spec-fidelity and 8 spec-fidelity-verify dispatches, plan and spec reviews together) | **whole once, 5,026,023** | none | none | none | 70 ms (10 ms without it) |
| `make decide` (420), a section that passes (`t536-readers-run3.txt`; refused at the stub it read only tasks-done.md x5, 209 ms) | **whole once, 5,026,023** | **whole x2, 7,275,988** | **whole x5, 3,004,035** | none | 1,436 ms (n=3) |
| `make plan-delta` (142) | **whole x2, 10,052,046** | **whole x11, 40,017,934** | whole x5, 3,004,035 | none | **2,619 ms** |
| `make plan-verdict` (217): `plan/record.rs` | BY CODE: read whole, parsed whole (15.9 ms), written whole | BY CODE: read whole (record.rs:589) | - | - | - |
| `make task-add` (146) | none | whole once, 3,637,994 | whole x5, 3,004,035 | 0 bytes | 2,822 ms (runs make quick) |
| `make queue`, `make builder-next` (7), and the pool-idle Stop guard where a tree is free (`builder_queue::facts`, the same reader) | none | none | whole once, 600,807 | none | 27-31 ms |
| `make plan-section` (65): an open task's section (T536) | none | none | none | none | 9 ms |
| `make plan-section` of a done task's section (T499, `t536-readers-run4.txt`) | none | **whole once, 3,637,994** | none | none | 33 ms |
| `make land` (39 calls; 85 land `end` rows, 34 of them landed): the ready ruling (`land/ready.rs` -> `shared::speckit::touch::edit_lines`) | - | - | - | BY CODE: **whole**, every `451*.jsonl`, where the mark holds the landing and the delta has a file not sectioned: 162.7 ms | - |
| the push's hold (`sync-with-main.sh` -> `speckit-todo --holding`, the same `touch` reader) | none | none | none | 0 on the copy (no other tree's task started); BY CODE whole where one is | 12 ms |
| `make land`'s tick (`task/tick.rs`) and carry (`land/carry.rs`) | carry: BY CODE, its three merge stages whole, only on a conflict | tick: BY CODE, read and rewritten whole at each archive | tick: likewise | - | - |
| SessionStart's and `make task-start`'s wait rule (`set_down_hooks::landings`) | - | - | - | BY CODE: whole where an open task waits on a landing; 0 on the copy | 68.8 ms |
| `make task-time` (32) | none | none | none | **whole once, 54,341,485** | **260,066 ms** (n=2) |
| `make claims-triage` (131) | none | none | none | none | 666 ms |
| `make where-time F=451` (0 on the day; `t536-readers-run5.txt`) | none | none | none | **whole x3, 163,024,455** | 283,941 ms (n=1) |
| `make feature-report F=451` (0 on the day; owed once at the feature's end) | none | none | whole once, 600,807 | **whole x5, 271,707,425** | 292,187 ms (n=1) |

`house_style_hooks` opens no file: it judges the tool's input text alone (an Edit's new string, a Write's content), observed on the
copy (the Edit case reads only the file `source_block_hooks` reads) and in its code (no `fs::` read).

## The builders' own reads (`t536-builder-reads.txt`)

146 builders started 2026-11-27 (UTC; 133 from 02:00Z, the seventeenth message's window): 6,191,894 bytes of their 29,738,619
tool-result bytes (20.8%) named a 451 record, in 1,385 calls - 42,410 bytes a builder, about 10,600 tokens (an ESTIMATE at 4 bytes a
token). By record: plan.md 829 calls 3,122,102 bytes; tasks.md 344 calls 2,451,011; plan-done.md 63 calls 508,363; request.md 44
calls 166,579; the event log 71 calls 154,735; plan-review.json 105 calls 81,352; tasks-done.md 8 calls 19,426. The four large
records together: 247 calls, 763,876 bytes, about 1,300 tokens a builder (ESTIMATE). Builders read the large records in slices;
the whole reads are the tools'.

## Every other agent's and session's own reads (`t536-agent-reads.txt`, `ALL=1`)

The plan review of T536 (round 1) asked for every agent, not builders alone: the same script with `ALL=1` (observed 2026-11-27,
method: every transcript under `/home/agent/.claude/projects/-diagram*/` with a tool result on the day, each subagent grouped by
its `meta.json` agentType, a top-level transcript as `session`). Bytes returned naming one of the four large records, by kind:
builder 730,661 in 254 calls (153 transcripts; largest call 28,207 bytes, a `sed` range of plan-done.md); general-purpose 55,884 in
18 (10; largest 11,539); session 22,312 in 32 (1; largest 3,522); spec-fidelity-verify 15,159 in 3 (7; largest 9,791, a `git diff`
naming the records); round-arbiter 0 (11), spec-fidelity 0 (219), message-check 0 (23), escalation-check 0 (5). No agent's own
call returned any of the four records whole: the largest single call was 28,207 bytes of the 3,637,994-byte plan-done.md, and the
reviewers read bundles under `/tmp/l7r-check/`, not the records. (The builder count differs from the section above: there a
transcript is dated by its first timestamp, here by each result's.)

## Reading

- **No hook reads a large record whole on every call.** Every tool call's hooks only append to the event log (0 bytes read). The
  per-call whole reads are narrower: a plan review's dispatch reads plan-review.json whole (5.0 MB; 70 ms against 4-28 ms for the other hook calls), and
  an Edit of a record reads that record whole (none of the three today).
- **The largest repeated reads are the gate's, not the hooks':** `make plan-delta` reads plan-done.md eleven times and
  plan-review.json twice a call - 50 MB, 2.6 s on the copy, 9.2 s median over the day's 142 real calls (an upper bound, about 22 minutes on the day); filed as 462 T543. `make decide` and
  `make task-add` read tasks-done.md five times a call (3.0 MB), and a `make decide` that passes reads plan-done.md twice and
  plan-review.json once (12.3 MB, 1.4 s on the copy, 420 calls).
- **`make where-time` and `make feature-report` read the event log whole three and five times** (163 MB and 272 MB, about
  5 minutes each on the copy); neither ran on 2026-11-27, but 451's closing owes one feature report.
- **The event log is read whole by three more readers:** the landing's ready ruling and the push's hold (`touch::edit_lines`, 162.7 ms),
  the wait rule (`landings`, 68.8 ms) and `make task-time` (one read of the whole log). `make task-time` took 61 s median over
  the day's 31 real calls and 260 s a call on the copy, reading about 5.0 GB by 87 s there, nearly all of it outside 451's records;
  filed as 462 T544.
- **No agent reads a large record whole by its own calls** (every kind, above); the reviewers' whole reads are the tools' they run
  (a plan review's dispatch, `make plan-delta`, `make decide`).
- **The builders' direct reads of the four large records are small** (about 1,300 tokens a builder, ESTIMATE); plan.md and tasks.md,
  which T537 does not split, carry 90% of the bytes builders read of 451's records.

## The copy's wall times against the day's real calls

The copy's figures are of one state (the copy's `make plan-delta` saw 19 changed blocks; the clone's at this task's end saw 4). The
day's real calls (the median of each target's PostToolUse `ms` in the 451 and 461 logs to the snapshot - the whole Bash call's
time, so an upper bound on the target alone) were: `make plan-delta` 9,180 ms (142 calls), `make decide` 1,202 ms (419),
`make task-add` 15,372 ms (145), `make task-time` 60,866 ms (31), `make plan-section` 3,084 ms (65), `make claims-triage` 809 ms
(131), `make plan-verdict` 282 ms (217), `make queue` 49,338 ms (4), `make builder-next` 5,580 ms (3). So the copy understates
`plan-delta` and `task-add` (the live machine was loaded and ran their checks over real deltas) and overstates `task-time` (260 s on
the copy against 61 s live: the copy's git directory lacks whatever the clone's holds for it - not traced here). The bytes a call
are the copy's; the times to compare after T537 are both, each against its own kind.

## For T537's after figure

Run the same five scripts on the split records' copies: `t536-readers-run.py` (the shim, by directory prefix), `t536-bench`
(each part a reader now opens), `t536-counts.py` and `t536-builder-reads.py`. SC-002 holds when no row above marked whole reads
a split record whole.

## Side effects of this measurement, outside the copy

- The synthetic UserPromptSubmit set off the once-a-day `scratch-sweep` under the session name `t536-copy-session`: it removed 869
  idle entries (5,960.6 MB) by its own three-day rule, which the next real prompt of the day would have removed: 445 under
  `~/.cache/l7r-cargo-target/diagram-backlog/cover-mode_a`, 191 under `.../cover-gate`, 91 under `.../debug`; 73 old task-output
  files under `/tmp/claude-1000/-diagram/a2348fda-.../tasks/` and 8 old scratchpad files of session `714e7303-...`; 52 loose
  `/tmp/*` entries; and 9 whole session directories under `/tmp/claude-1000/` (two `-diagram--clones-diagram-research`, three
  `-diagram--clones-diagram-backlog`, three of the `m14-*-sonnet-tree` scratch trees, and `pv453/`). Nothing under this task's own
  scratchpad or a live builder's tree was removed: each entry was idle three days by the sweep's own test. A later coverage run in
  the diagram-backlog clone may rebuild what it removed.
- 886 guard-log records (`~/.claude/guard-log/`) carry the session name `t536-copy-session`: the sweep's 870, and 16 firings of
  `agent-model`, `agent-prefix`, `review-round` and `finished-run` on the synthetic payloads. They were left in place.
- `make plan-delta` on the copy rewrote the bundle `/tmp/l7r-check/plan-451-time-retro-and-efficiency-blocks-T532-<hash>/`, the
  same bundle the clone's HEAD builds.
- To repeat this without those effects: `t536-readers-run.py` now leaves UserPromptSubmit out unless `T536_PROMPT=1`, and drops the
  stub plan-verdict and tick cases (both refused before any read); the other hook cases still write a few guard-log rows.
