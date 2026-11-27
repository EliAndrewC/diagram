# 451 T373 - which guard makes a hook on an Edit take ten times a hook on a Bash call

Measured 2026-11-26, 18:26 to 19:25 local, by a measurement builder. No source file changed. Every figure is wall milliseconds of
one hook call unless it says otherwise, written median / 90th centile over 20 counted runs after one warm-up round, the arms of a
run interleaved round-robin (`t373-time.py`). The machine was shared with other builders the whole time: load1 ran from 4.4 to 53
(22 cores), each table row carries its own range, and a row taken above load 20 is marked LOADED where it is used.

## The answer in four lines

- TWO guards, not one. `event-log-hooks` spends 333 / 360 ms on EVERY Edit (not a Write): its reversal tripwire reads the feature's
  whole event log (41.0 MB, 156,753 lines) and JSON-parses every line. This is all of T365's 342 ms.
- `clone-sync-hooks` spends another 480 / 508 ms on an Edit or Write of a file in the session's CLONE ITSELF (not in a pool
  worktree): it reads the session's whole transcript (274 MB) to find the session's name, before it knows it needs the name, then
  runs `git status --porcelain`. T365 did not see it: its event carried no transcript and its file was in a worktree.
- So an Edit by the session in its own clone costs 824 / 1146 ms today, an Edit by a builder in a pool worktree 372 to 402 ms, and
  both grow: 8.1 ms for each MB of the feature's event log (it grew 5.6 MB that day), 1.4 ms for each MB of transcript.
- FOUND BESIDE IT, and larger by the day: a Bash call takes 150 ms where it takes 35 ms, whenever a plan review holds text - the
  hold makes `record-edit-hooks` parse and REWRITE the 3.0 MB `checks-open.json` on every Bash call. 28% of the day's Bash calls.

## How it was measured, and what it could not touch

T365 timed the hook with a made-up session id against the real tree, and left 130 lines in the clone's event log and a file in
the mirror's claim map (`/diagram/.clones/.session-clones/t365-measure-0000.name-notice`, still there). This run made a THROWAWAY
WORLD under the scratchpad (`<scratchpad>/t373/`) and fired only PreToolUse and PostToolUse, so no reminder was consumed:

- `w/diagram`: a `git clone` of `/diagram` (the mirror stand-in); `w/diagram/.clones/diagram-backlog`: a `git clone` of the real
  clone at `0a0acdfc4f`, with the real clone's non-git state copied into its `.git` (the event logs, `checks-open.json`,
  `task-starts.jsonl`, the caches) and its untracked `.specify/feature.json`; `w/diagram/.clones/diagram-backlog-t270`: a worktree
  of that sandbox clone, standing in for a builder's pool tree (its `.git` is a file).
- The mirror's 2,872 claim-map files copied to `w/diagram/.clones/.session-clones/`, the 131 that named the real clone re-aimed at
  the sandbox clone, the live session's own entry replaced by the sandbox session's.
- The binary: the mirror's kept one (`~/.cache/l7r-cargo-target/diagram/l7r-guard.good`, built 17:53 from `e6be62339a`), COPIED to
  `target/` and reached through `L7R_GUARD_TARGET`, so the launcher's staleness walk could never start a build in the real target.
- The environment of every call, `env -i` plus exactly: `PATH`, `HOME` (a scratch home holding copies of `~/.claude/sessions`, 143
  files, the session's 274 MB transcript, and one builder's `agent-*.meta.json`), `CLAUDE_PROJECT_DIR` and `CLONE_MAIN` (the sandbox
  mirror), `L7R_GUARD_TARGET`, `GUARD_LOG_DIR`, `MEASURE_STATE_DIR`, and for a direct binary call `L7R_GUARD_TREE`. `SPECIFY_FEATURE`
  and `L7R_FEATURE_DIRECTORY` unset, as in a hook's own process.
- Each payload is a real one's shape (`t373-payloads.py`): the Edit's `old_string` is a line of the file, the Write's target does
  not exist, the PostToolUse carries a `tool_response`. Sessions: `sess` (resolved by the claim map, the 274 MB transcript), `sub`
  (the same with a builder's `agent_id`), `wt` (that builder, its cwd and files in the sandbox worktree), `half` and `tenth` (the
  transcript's first 137 MB and 27 MB), `none` (T365's form: an id nothing resolves, no transcript). States: `dirty` (one tracked
  file of the clone changed) and `clean`.

WHERE A HOOK CALL WRITES, found under an `LD_PRELOAD` shim that logs every process, open, mkdir and rename (`t373-shim.c`,
`t373-probe.py`, `t373-probes.txt`), and where each went here:

| what | where it writes by default | sent to |
|---|---|---|
| the event log line | `<the clone's common git dir>/l7r-events/<feature>.jsonl` | the sandbox clone's (3,386 lines; `L7R_EVENTS_DIR` is its knob, not needed) |
| clone-sync's claim | `<mirror>/.clones/.session-clones/<session id>`, rewritten on every Edit of a clone file | the sandbox mirror's (`CLONE_MAIN`) |
| the guard log, on a block or permit | `~/.claude/guard-log/` | `GUARD_LOG_DIR` (166 entries) |
| the measure guard's state | `/tmp/claude-measure` | `MEASURE_STATE_DIR` |
| the plan hold's state, while a review holds | `<common git dir>/checks-open.json` and `.lock`, REWRITTEN on every Bash and Edit | the sandbox clone's |
| an Agent dispatch's state | the common git dir | the sandbox clone's |

COULD NOT REDIRECT, and what came of it:
- The first probe ran before `MEASURE_STATE_DIR` was set: one `mkdir /tmp/claude-measure` of a directory that already existed. No
  file in it was opened.
- `scripts/gates/l7r-gate.sh` (called by `record-edit-hooks` on a plan.md Edit under a hold) takes its target from the ACCOUNT'S
  home, not `HOME`, and the tree's name: the sandbox mirror is named `diagram`, so it ran the real `/diagram` gate binary
  (`~/.cache/l7r-cargo-target/diagram/tool/l7r-gate record edit-route`, read-only). It did not build: the real binary was newer
  than the sandbox's sources, and its `.d` file names only `/diagram` paths (its 18:31 rebuild was the mirror's own, on its
  fast-forward to `4e132bb8fc`). A sandbox whose sources were NEWER than that binary would have rebuilt the real one:
  `L7R_GATE_TARGET` is the knob to set next time.
- The copied hold named the real `/diagram/.clones/diagram-backlog-t271/specs/...` as its root, which the guard READ.
- THE LEAK CHECK (`t373-leak-check.txt`): the real event logs hold no line of a `t373-*` session, the real claim map no `t373-*`
  entry, the real guard log no entry naming the sandbox, the real `checks-open.json` no `toolu_t373*` id. (The one real log line
  that names `t373-sess-0001` is the harness's own record of this builder's Bash call.)

FIDELITY, proved before any attribution: T365's figure came back. In the sandbox worktree (T365's case: a tree whose `.git` is a
file) the Edit's hook is 372.3 / 413.1 ms (load 22 to 30, LOADED) and 402.0 / 640.3 (load 13 to 53, LOADED), minimum 344.6,
against T365's 342.2 / 362.0. Two things the first attempts got wrong, both visible in the record: without `.specify/feature.json`
the line went to a small `_unassigned.jsonl` and the Edit took 130 ms; with the sandbox clone named `t373-sess` the guard refused
the edit as misrouted (`t373-try1-misnamed-clone.tsv`), because the transcript's `/rename` names `diagram-backlog`.

`l7r-guard --only <guard> <event>` exists (`rust/guard/src/lib.rs`, `cli`) and forces the guard's matcher to `*`, so it was run
only for the guards whose own events and matcher take the tool (`t373-time.py`, `GUARDS`, read off each `GUARD` constant). The
process start (`--version`) is 2.0 to 2.5 ms and is inside every `--only` figure. The guards' figures taken alone, less the extra
process starts, sum to within 2% of the binary's own (`t373-top3.txt`, last column: 809 against 802, 946 against 936, 494 against
492), so nothing is shared or hidden between them.

## (1) Which guard

The session itself (`sess`), its clone dirty, load 5.4 to 16.9 (`t373-guards.tsv`):

| event | the hook (launcher + binary) | the binary, every guard | 1st guard | 2nd | 3rd |
|---|---|---|---|---|---|
| PreToolUse, Edit of `docs/usage.md` | 823.6 / 1146.0 | 802.1 / 836.2 | clone-sync 480.1 / 508.0 | event-log 333.0 / 359.7 | engine-freeze 3.3 / 3.8 |
| PreToolUse, Edit of `rust/gate/src/main.rs` | 819.3 / 842.9 | 813.5 / 1179.4 | clone-sync 485.4 / 538.1 | event-log 337.6 / 408.2 | guard-file 3.1 / 3.4 |
| PreToolUse, Edit of the spec's `plan.md` (a plan review holding) | 935.8 / 1037.4 | 935.8 / 1035.9 | clone-sync 480.9 / 528.9 | event-log 334.3 / 352.6 | record-edit 131.6 / 212.3 |
| PreToolUse, Write of a new file | 500.0 / 581.4 | 491.7 / 510.5 | clone-sync 488.2 / 517.7 | event-log 5.6 / 6.8 | engine-freeze 3.1 / 4.3 |
| PostToolUse, Edit (doc, Rust, plan.md) | 23.8 / 25.1, 24.0 / 28.5, 22.9 / 30.0 | 8.7 / 10.0 | checks 6.0 / 6.8 | event-log 5.9 / 7.1 | (two guards take it) |
| PostToolUse, Write | 24.2 / 30.9 | 8.3 / 10.6 | event-log 5.6 / 6.5 | checks 5.4 / 6.3 | (two guards take it) |

The other rows (`t373-top3.txt` has every one):

| case | Edit of a doc, PreToolUse hook | clone-sync | event-log |
|---|---|---|---|
| the session, clone CLEAN (the first edit after a commit), load 4.4 to 16.9 | 949.9 / 1397.1 | 627.3 / 1219.2 | 336.3 / 538.9 |
| a builder (`agent_id`) editing the clone, dirty | 846.0 / 1202.3 | 487.3 / 504.8 | 337.4 / 361.7 |
| a builder editing its POOL WORKTREE, LOADED (13 to 53) | 402.0 / 640.3 | no opinion, under 3.6 | 364.8 / 502.0 |
| the same, Write of a new file, LOADED | 31.2 / 60.1 | no opinion | 8.1 / 12.4 |
| the same, Edit of plan.md under a hold, LOADED | 656.6 / 1229.7 | no opinion | 409.3 / 635.2 (record-edit 188.6 / 934.3) |

The FILE'S KIND does not matter (doc 823.6, Rust 819.3); three things do: Edit or Write, clone or worktree, and - for plan.md -
whether a plan review holds text. Every third-place guard except record-edit is within 1.5 ms of the bare process start: nothing
else in the Edit's fifteen guards is worth a lever. The PostToolUse is 23 to 29 ms, of which the binary is 9: the other 15 are the
launcher (see "the floor" below).

### What each is doing in that time

**`event-log-hooks`, 333 ms on an Edit** (`rust/guard/shared/src/guards/event_log_hooks.rs`, `reversal`, line 614, called at line
753 for a PreToolUse Edit whose feature log exists): `std::fs::read_to_string` of the feature's whole log, then
`serde_json::from_str` on EVERY line, keeping the earlier Edits of the same path, to ask whether this Edit puts back text an
earlier one replaced. No child process (shim: 0 spawns, 11 opens). The log was 40,969,607 bytes and 156,753 lines; 4,691 of them
(1.5 MB) are PreToolUse Edit lines of real sessions, over the whole feature, not the day. A Write, a Bash call and every PostToolUse skip it: 5.6 to 8 ms. Read alone, with no parse, the
log is 46.6 ms; read and screened for the path's text, 67.6 ms (`t373-levers.txt`, at load 18, LOADED). So about 265 to 290 ms of
the 333 is the JSON parse of lines that cannot match. It grows with the log: 333 / 41.0 = 8.1 ms a MB, and the log grew from
35.4 MB to 41.0 MB between 00:00 and 18:26 local that day.

**`clone-sync-hooks`, 480 ms on an Edit or Write in the clone** (`rust/guard/src/guards/clone_sync_hooks.rs`, `pretool`, line 327):
- `let canon = cx.session.canonical();` (line 357) runs BEFORE `dirty(&clone)` (line 364), and `canonical` is
  `shared/src/session.rs` `titled` (line 217): the session's whole transcript read a line at a time for its last `custom-title`
  record. 274 MB, 129,589 lines, 4,880 of them holding `custom-title`. No process; one open.
- then ONE child process, `git -C <clone> status --porcelain`: 83 ms in the sandbox clone under the shim (418 opens; 60 ms in the
  real clone, 30,490 tracked files, `GIT_OPTIONAL_LOCKS=0`, load 6.8).
- A DIRTY clone ends there: `canon` was never used. It is read only by `misrouted`, which runs only on a clean clone.
- The size sweep (`t373-sizes2.tsv`, clone-sync alone, dirty, load 10 to 13): no transcript 96.6 / 107.7; 27 MB 148.2 / 164.6;
  137 MB 297.7 / 315.1; 274 MB 480.1 / 508.0 (the calmer first pass; 572.5 / 913.3 in this one). 1.4 to 1.5 ms a MB of transcript:
  383 ms of the 480 is the transcript, about 85 the `git status`, 10 the rest.
- A CLEAN clone adds 147 ms (627.3 against 480.1): 2,871 opens of the claim map (1,581 of its files are empty) to find other
  sessions claiming the same clone, and for each of the 131 that do, `sid_is_live` -> `pid_of` lists and parses the sessions
  directory again (9,546 opens of `~/.claude/sessions`, 143 files, 131 times over); then `git rev-parse HEAD` in the mirror and
  `git merge-base --is-ancestor` in the clone (0.7 and 2.6 ms).
- A pool worktree pays none of this: `clone.join(".git").is_dir()` is false there (line 354) and the guard has no opinion.
- Real `HOME` against the scratch one, the same call: 872.5 / 1662.8 against 892.5 / 2003.2 (LOADED, load 15 to 30): no difference.

**`record-edit-hooks`, 132 ms on a plan.md Edit - only while a plan review holds text** (`rust/guard/src/guards/record_edit_hooks.rs`
`judge`, `record_edit_gate.rs` `mode_for`): `checks::handle("edit")` (`shared/src/checks/handle.rs` line 204) loads the 3.0 MB
`checks-open.json` (2,994,933 bytes, 3,054 dispatches kept in it), snapshots the held text, and SAVES the whole file back (sorted,
re-serialized, a temp file and a rename, under `flock`); then `scripts/gates/l7r-gate.sh record edit-route` (bash, a `find` over the
gate's sources for staleness, 22 ms, the gate binary 2.4 ms). With no hold: 9.6 / 10.7 ms (`t373-nohold.tsv`).

## (2) The day's cost - an ESTIMATE

The count is from a COPY of the clone's event log made at 18:26 local (`t373-events.py`, `t373-events.txt`): PreToolUse lines with
`t` from 2026-11-26T05:00Z (the local day), the measurement sessions' lines left out (t365-measure-0000 130, t304-probe 9). The day
was not over. 306 Edit and Write calls (T365's 470 is 353 Edit + 117 Write in its own day file, `t365-events-counts.txt`, its own 43 probe edits among them; why the rest differs was NOT determined): 214 Edit, 92 Write; 266
by sub-agents, 40 by the session.

| where the file is | Edit | Write |
|---|---|---|
| a pool worktree (`.git` a file: clone-sync has no opinion) | 184 | 46 |
| the clone itself | 29 | 19 |
| outside any clone (scratch, `/tmp`) | 1 | 27 |

By kind (it does not change the time): Rust source 121 Edit and 39 Write; tooling 35 and 1; docs 18 and 19; "other in a clone" 23
and 4; plan.md 8; tasks.md 7; `dev/measurements` 1 and 2.

| | calls | ms a call (median used) | seconds |
|---|---|---|---|
| Edit, worktree or outside | 185 | 390 (372 and 402, both LOADED) | 72.2 |
| Edit, in the clone | 29 | 850 (824 dirty, 950 clean; the split is not in the log) | 24.7 |
| Write, worktree or outside | 73 | 31 (outside a clone ASSUMED as a worktree: not timed) | 2.3 |
| Write, in the clone | 19 | 550 (500 dirty, 644 clean) | 10.5 |
| PostToolUse of both | 297 | 26 | 7.7 |
| **Edit and Write, a day** | | | **117 s = 2.0 minutes** |

Of it: event-log's reversal scan 214 x 0.335 = 72 s; clone-sync 48 x about 0.5 = 24 s. The transcript was 244 MB at the day's
start and 274 MB at its end, the log 35.4 to 41.0 MB, so the clone rows are at most 5% and the reversal rows at most 7% high for
the day's early calls. It is every edit's wait more than it is minutes: 0.4 s for a builder's, 0.8 to 1.1 s for the session's own.

THE OTHER TOOLS, timed once each as asked, then by guard where slow (`t373-tools-first-pass.tsv`, `t373-tools2.tsv`,
`t373-nohold.tsv`; the session, clone dirty):

| tool | PreToolUse hook | PostToolUse hook | calls that day (Pre, Post) | seconds a day |
|---|---|---|---|---|
| Read | 26.4 / 51.4 | 24.9 / 43.9 | 386, 382 | 20 |
| Grep | 24.3 / 34.1 | 23.2 / 47.8 | 70, 68 | 3.5 |
| Bash `true`, NO plan review holding | 34.7 / 44.6 (LOADED, load 30; T365: 31.6) | 27.4 / 31.9 | 3,026 of 4,202; 4,075 | 106 + 118 |
| Bash `true`, a plan review HOLDING | 150.4 / 251.1 (minimum 119.1) | 30.2 / 38.4 | 1,176 of 4,202 | 176 |
| Agent | 153.8 / 200.9 | 134.9 / 325.6 | 220, 212 | 63 |

- **Bash is slow too, on a condition.** While any plan review holds text (`plan_holds` not empty in `checks-open.json`),
  `record-edit-hooks` takes 97 to 118 ms of CPU on EVERY Bash call (`--only record-edit-hooks`: minimum 97.4 ms, child CPU 117.9;
  8.0 / 9.2 with no hold): the same load-snapshot-SAVE of the 3.0 MB state as on a plan.md Edit (shim: `checks-open.lock`, a temp
  file, a rename, on a Bash `true`). HOW MUCH OF THE DAY, estimated (`t373-holds.py`, `t373-holds.txt`): a hold taken to run from a
  `spec-fidelity` agent's SubagentStart to its SubagentStop; 63 runs, 52 merged intervals, 186.7 minutes of the 18.4 hours the log
  spans; 1,176 of the 4,202 Bash PreToolUse calls (28%) fall inside one, 35 of 214 Edits, 23 of 92 Writes. Its extra is
  1,176 x 0.115 = 135 s = 2.3 minutes a day - more than everything the Edit hook costs. AN UPPER BOUND: every `spec-fidelity` run was
  counted as a hold, and only a plan review (a `/plan-` manifest) takes one; the share with such a manifest was NOT counted.
- **Agent**: `pair-hooks` 87.8 / 140.9, `check-bundle-hooks` 34.5 / 97.0 on the PreToolUse; `checks-hooks` 98.1 / 127.5 on the
  PostToolUse, hold or no hold (by reading `handle_locked`, the same 3.0 MB state loaded and saved; NOT confirmed under the shim). Not read further here: 220 calls a day, about a minute.
  The sandbox's Agent PreToolUse was refused in part of its runs (exit 2: `agent-prefix` saw the same prompt again), so its figure
  is of a call that is sometimes refused.
- **The floor.** The hook less the binary is 15 to 17 ms on every call (34.7 against 17.5 for Bash, 23.8 against 8.7 for an
  Edit's PostToolUse): `sh`, `env bash`, and the launcher's `-nt` walk of `rust/guard/**` (`scripts/hooks/l7r-guard.sh`, `newer`).
  About 10,400 PreToolUse and PostToolUse calls that day x 16 ms = 166 s = 2.8 minutes. Not a lever priced here.
- All hooks of these five tools: about 117 + 400 + 20 + 3.5 + 63 = 604 s, 10 minutes of the day.

## (3) The levers, each priced against (1). None built.

| lever | saves a call | saves a day (the counts above) | what it risks | filed |
|---|---|---|---|---|
| A. `reversal` screens each line for `"tool":"Edit"` and the path's own JSON text BEFORE parsing it, as `launch_line` (line 834) already does for an id | 265 to 290 ms of 333 (leaves the 47 ms read and a parse of the file's own lines; 67.6 ms measured at load 18) | 214 x 0.28 = 60 s | the screen must be the writer's own serialization of the path (a path with a quote, a backslash or non-ASCII), or a reversal is MISSED - the tripwire is the arbiter's and must not miss; a differential over the log's 4,691 Edit lines proves it | T383 |
| A2. the alternative: the Edit lines kept in a side file beside the log (1.5 MB of 41), read instead | about 330 ms | 214 x 0.33 = 70 s | two files to keep in step: `make events-refile` moves lines between features, and a line missing from the index is a missed reversal | in T383, as the option not taken first |
| B. clone-sync asks for the session's name only where it reads it (`canonical` after `dirty`, lazily) | 383 ms of 480 on a dirty clone's Edit or Write (1.4 ms a MB of transcript) | at most 48 x 0.38 = 18 s (the dirty share is not in the log) | none to a verdict: `canon` reaches only `misrouted`, which runs only on a clean clone | T384 |
| C. `titled` reads the transcript from its END, block by block, to the last whole `custom-title` record | 383 ms, on the clean path too, and for every other caller of the session's name (17 files name `canonical`, `clone_dir`, `name` or the transcript's text; the Stop and prompt events were not timed here); the backward read is 0.0 ms and one 64 KiB block against 755 ms forward (LOADED, `t373-levers.txt`) - the record recurs every 56 KB on average | 18 s on Edit and Write; more on the events not timed | parity at the edge: today a line that holds `custom-title` and is not a JSON object ENDS the lookup with no name; read backward, one before the last good record is never seen. The last record must still win | T385 |
| D. clone-sync's clean path reads the sessions directory ONCE (a map of session id to pid) and skips an empty claim file by its size | about 130 of the 147 ms a clean clone adds | at most 48 x 0.13 = 6 s (clean edits are the first after a commit: fewer) | the live-claim refusal must still find a live session claiming the clone; the 1,581 empty and the long-dead claim files could also be pruned, which is a deletion and needs its own rule | T386 |
| E. the plan hold stops rewriting `checks-open.json` on every Bash call: save only where the snapshot changed, and prune the 3,054 dispatches the file keeps (3.0 MB) | 100 to 115 ms of 150 on a Bash call under a hold; 98 ms on every Agent PostToolUse | 1,176 x 0.115 = 135 s, and 212 x 0.098 = 21 s | the hold exists to put back held text a command overwrote: a snapshot skipped where the text DID change loses the restore; what the dispatch records are read for must be known before any is dropped | T387 |
| F. the cheaper dirty test (`git diff-index --quiet HEAD` first: 52.1 ms against 110.9 for `status --porcelain`, a dirty clone, LOADED) | about 40 to 60 ms | at most 48 x 0.05 = 2 s | untracked files alone must still read as dirty (a second call on a clean answer) | not filed: under 3 s a day; noted in T384 |
| G. Agent hooks: pair-hooks 88 ms, check-bundle-hooks 35 ms, checks-hooks 98 ms | not priced: the cause was not read | about 60 s | - | T388, a measurement |

Order by the day: E (156 s), A (60 s), then B and C together (18 s, but the session's own every-edit wait: 824 ms to about 440),
then D. A and B are each one function's change; C changes what every guard that names the session reads.

## Files

Scripts: `t373-shim.c` (the tracing preload), `t373-payloads.py`, `t373-time.py`, `t373-probe.py`, `t373-runall.sh`,
`t373-runall2.sh`, `t373-top3.py`, `t373-events.py`, `t373-holds.py`, `t373-git.py`, `t373-levers.rs` (std only, `rustc -O`),
`t373-snapshot.sh`. Tables (columns in `t373-head.tsv`): `t373-guards.tsv` (the first table), `t373-worktree.tsv`,
`t373-sizes2.tsv`, `t373-tools-first-pass.tsv`, `t373-tools2.tsv`, `t373-nohold.tsv`, `t373-sizes-first-pass-loaded.tsv` (load 8 to
31, kept and not used), `t373-try1-misnamed-clone.tsv` (the refused first attempt, kept and not used). Outputs: `t373-top3.txt`,
`t373-events.txt`, `t373-holds.txt`, `t373-levers.txt`, `t373-git.txt`, `t373-probes.txt`, `t373-leak-check.txt`.

The sandbox itself (3.6 GB under the scratchpad's `t373/`) is not in the record and was left in place.

## Not measured

- The share of clean against dirty clones among the 48 edits in the clone itself; a Write outside any clone (taken as a worktree's).
- Whether each `spec-fidelity` run of the day was a plan review: the 28% hold share, the 135 s and lever E's day figure are upper bounds.
- Lever E's saving a call (100 to 115 ms) is the whole extra under a hold: the state's load and save were not separated from the snapshot's read of the plan.
- The Agent PostToolUse's 98 ms in `checks-hooks`: attributed by reading, not probed. Its 21 s is counted in lever E and again inside lever G's 60 s; T388 is the measurement that settles which.
- The Stop, UserPromptSubmit and SessionStart events (never fired here), so lever C's saving outside Edit and Write.
- The worktree Edit row (230 of the 306 calls) exists only at load 13 to 53; its minimum, 344.6 ms, and event-log alone at 333.0 ms (load 5 to 17) bracket it.
- The launcher's 16 ms floor was observed, not priced as a lever, and is not filed.
