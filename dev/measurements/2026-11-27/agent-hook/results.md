# 451 T388 - where an Agent call's hooks spend their time, read by read

Measured 2026-11-27, 06:33 to 06:52 local, by a measurement builder. No source file changed. Every figure is wall milliseconds of one
hook call, median / 90th centile over 20 counted runs after one warm-up round, the arms interleaved round-robin (`t388-time.py`), at
load1 4.0 to 12.6 on 22 cores with other builders running (each table row's range is in its TSV). T373's method
(`dev/measurements/2026-11-26/edit-hook/t373-results.md`), rebuilt for the Agent call.

## The answer in five lines

- T373's figure came back: a builder's dispatch (general-purpose) takes 152.8 / 169.4 ms on its PreToolUse and 122.3 / 359.7 on its
  PostToolUse, against T373's 153.8 and 134.9. But the dispatch's KIND matters: a plan review (spec-fidelity) takes 261.2 / 481.9 ms
  and a record check (record-format) 343.8 / 350.1.
- `pair-hooks`, 92 ms on every Agent call: 50 ms of it is `l7r-gate reviews checkpoint due` reading the feature's whole 50 MB event log
  to parse its first line, for a step-back that has been switched off since 2026-10-21 - the answer is always "not due". 17.5 ms more
  is the gate launcher's source walk. Filed: T491, T494.
- `checks-hooks`, 95 ms on every Agent PostToolUse: 91 ms of it is the load and save of the 3.0 MB `checks-open.json` - all T387's.
  The same state costs `check-bundle-hooks` 30 ms on a builder's dispatch and about 120 ms on a plan review's or a record check's
  (they save it too). With the file cut to its 12 unfinished dispatches (0.64 MB), the three are 18, 8 and 19 ms: that is what T387's
  pruning leaves, before any save it skips.
- Found beside them: a record check's dispatch runs a work-tree `git diff --numstat` for the cascade tripwire whether or not it can
  fire (40.6 ms in the sandbox, 78.6 in the real clone; T492), and a plan review's `review-round-hooks` parses the 4.7 MB
  `plan-review.json` for one round count (40 ms; T493).
- The day: about 103 s of Agent hook time over 2026-11-26's 296 dispatches (not T373's 220, which was a part-day count): pair-hooks 27 s,
  check-bundle-hooks 31 s (23 s of it the state, T387's), checks-hooks 27 s (T387's), review-round-hooks 8 s, event-log-hooks 8 s.

## How it was measured

THE SANDBOX (`t388-build.sh`), under the scratchpad's `t388/`, T373's shape built afresh tonight:
- `w/diagram`: a `git clone` of `/diagram` at `8963f871c4` (the mirror's HEAD when its kept binaries were built, 05:51); `w/diagram/.clones/diagram-backlog`:
  a `git clone` of the real clone at `23ca09d5d7`, the real clone's non-git state copied into its `.git` (the event logs, the 50.2 MB
  feature log among them, `checks-open.json` 2,994,673 bytes and 3,054 dispatches, `check-passes.jsonl`, the prompt store, the pool
  registry, the caches) and its untracked `.specify/feature.json`. No pool worktree: every case is the session's own dispatch (the day's
  109 dispatches by builders were not timed apart).
- The claim map's 2,869 files copied and the 131 naming the real clone re-aimed; the sandbox session `t388-sess-0001` added.
- A scratch home: `~/.claude/sessions` copied, the coordinating session's 297.6 MB transcript copied as the sandbox session's.
- The binaries live hooks run - the mirror's `l7r-guard.good` and `tool/l7r-gate`, built 05:51 - COPIED into the sandbox and stamped
  newer than its sources; every call is `env -i` plus `PATH`, `HOME` (the scratch one), `CLAUDE_PROJECT_DIR` and `CLONE_MAIN` (the
  sandbox mirror), `L7R_GUARD_TARGET`, `L7R_GATE_TARGET` (the gate launcher's target: T373 found it otherwise takes the account's real one),
  `L7R_GATE_CARGO=/bin/false` (no build can start), `GUARD_LOG_DIR`, `MEASURE_STATE_DIR`, `L7R_GUARD_TREE`, `cwd` the sandbox clone.
  The three guards timed are the same source in the mirror at `8963f871c4` and in this tree (`git diff --stat`: none of their files).
- THE RUNS ARE INDEPENDENT: an Agent hook writes the checks state (a dispatch row, a plan hold), the check-passes log and the prompt
  store `agent-prefix-hooks` compares against. All three are put back from a pristine copy before EVERY run, outside the clock; each
  run's payload is written fresh with its own `tool_use_id` and a nonce at its prompt's end; a PostToolUse is preceded, outside the
  clock, by its own PreToolUse, and carries a background launch's response (`{"status": "async_launched", "agentId": ...}`, the shape
  `checks::handle` `book_keep` reads). Every one of the 2,500-odd timed runs exited 0 (each row's exit-code column): no figure here
  mixes refused calls in, as T373's Agent row did.
- THE THREE CASES, the day's mix (`t388-mix.py` over copies of the 449 and 451 event logs, 2026-11-26T05:00Z to 2026-11-27T05:00Z,
  `t388-mix.txt`): 296 Agent PreToolUse and 288 PostToolUse calls; general-purpose 100, spec-fidelity 98, the record checks and
  impl-drift 65 (record-format 18, quote-check 16, source-reader 12, source-applicability 10, impl-drift 7, translation-check 2), the
  rest 33 (message-check 19, round-arbiter 8, escalation-check 5, research-pass 1), counted with general-purpose below.
  - `gp`: a builder's brief, general-purpose, the BUILDER-BRIEF block of this task's own brief and a stand-in task text (`t388-brief.txt`);
  - `sf`: a spec-fidelity MODE 4 plan review naming a copied plan bundle (a real one's words, from the prompt store);
  - `rf`: a record-format round-2 check naming a copied question bundle, its description naming a task whose plan is decided.
- WHERE TIME GOES was found under T373's `LD_PRELOAD` shim (`t373-shim.c`; `t388-probe.py`; `t388-probe-gp-pre.txt`,
  `t388-probes.txt`) and by ARMS that take one cause away: `+shortlog` (the feature event log cut to its first 2,000 lines), `+small`
  (`checks-open.json` with its 3,042 finished dispatches dropped: 635,286 bytes), `+none` (no checks state), `+fresh` (`L7R_GATE_FRESH`
  set: the gate launcher skips its source walk).
- ONE SANDBOX ARTIFACT, found and taken out: a fresh clone's index is racily clean (its files written in the second the index was), so
  a work-tree diff hashes every file - 212.1 ms against 40.6 after `git update-index --refresh`, and 78.6 in the real clone
  (`t388-git.txt`). The first `rf` rows (`t388-guards.tsv`: 534.5 ms, check-bundle 405.5) carry it; the corrected ones are the last
  rows of `t388-causes.tsv` (343.8, 231.9). No other case runs a work-tree git command.
- THE LEAK CHECK (`t388-leak-check.txt`): no `toolu_t388` id or `t388-sess` session in the real event logs, checks state, check passes,
  prompt store, claim map or guard log. The real binaries' 06:40 times are the mirror's own rebuild on its fast-forward at 06:40:04.

## (1) Which guard

Every guard that takes an Agent PreToolUse or PostToolUse (their `GUARD` constants), alone through `--only` (`t388-guards.tsv`; the
process start, `--version`, is 2.2 to 2.5 ms and inside each figure):

| | gp (a builder's brief) | sf (a plan review) | rf (a record check) |
|---|---|---|---|
| PreToolUse hook (launcher + binary) | 152.8 / 169.4 | 261.2 / 481.9 | 343.8 / 350.1 (534.5 with the racy index) |
| the binary, every guard | 135.0 / 155.3 | 255.5 / 440.2 | 523.8 / 618.9 (racy index) |
| `pair-hooks` | 92.0 / 104.1 | 91.9 / 114.0 | 91.5 / 96.7 |
| `check-bundle-hooks` | 33.9 / 42.9 | 102.9 / 252.2 | 231.9 / 240.5 (405.5 racy) |
| `review-round-hooks` | 2.6 | 76.6 / 147.5 | 2.6 |
| `event-log-hooks` | 14.3 / 17.9 | 12.6 / 17.2 | 12.8 / 14.4 |
| `builder-brief-hooks` | 7.2 / 8.3 | 2.9 | 2.3 |
| `agent-prefix-hooks` | 6.3 / 7.0 | 6.1 / 8.0 | 6.1 / 7.5 |
| the other five (agent-model, context-cap, escalation, research-switch) | 2.4 to 3.9 | 2.6 to 2.9 | 2.3 to 3.0 |
| PostToolUse hook | 122.3 / 359.7 | 121.5 / 271.1 | 110.7 / 191.0 |
| `checks-hooks` | 108.6 / 561.3 | 101.9 / 236.2 | 99.5 / 589.8 |
| `event-log-hooks` | 13.2 / 15.3 | 13.8 / 18.6 | 14.1 / 16.1 |

The hook less the binary is 15 to 18 ms (the launcher floor T439 and T456 worked on). The guards alone, each less one extra process
start, sum to within 10% of the binary's own on gp (148 against 135) and sf (281 against 256): nothing large is hidden between them.

## (2) What each is doing in that time

**`pair-hooks`, 92 ms on every Agent call** (`rust/guard/src/guards/pair_hooks.rs` `pretool`): for every Agent call (and every gate
invocation on Bash) it runs `bash scripts/gates/l7r-gate.sh reviews checkpoint due --root <clone> --tool Agent --agent <type>`.
- 50 ms: the gate binary's `first_event` (`rust/gate/crates/reviews/src/reviews/glyph.rs`) `read_to_string`s the feature's whole event
  log, 50,188,879 bytes, and parses its FIRST line. The shim: the log opened at +581.1 ms and the binary's next act at +633.2. The arm:
  91.8 / 114.0 ms against 41.6 / 83.2 with the log cut to 2,000 lines (`t388-causes.tsv`). It grows with the log, about 1 ms a MB.
- And it is wasted: `due` -> `state_in` (`checkpoint.rs`) reads `feature_start` BEFORE `suspended(root)`, and `due` is `!off && ...`.
  `dev/step-back.json` has said `off` since 2026-10-21 (the GM: "let's suspend but not remove the hourly step-back arbiter"), so every
  Agent call reads 50 MB, and runs `git log -1 -- specs/<feature>` (3.2 ms), to answer "not due". Lever: T491.
- 17.5 ms: the gate launcher's `stale()` walk, one `find` over 589 paths of `rust/gate` and `rust/guard` (13.3 ms under the shim):
  74.3 / 117.3 ms with `L7R_GATE_FRESH` set. Lever: T494.
- The rest, about 24 ms: the launcher's bash and `/etc/passwd` read, the gate binary's start and its three `git` calls (0.4 to 3.2 ms
  each), and the guard's own resolution of the session's clone (the claim map: one open).

**`checks-hooks`, 95 ms on every Agent PostToolUse** (`checks_hooks.rs` -> `checks::handle("launched")`): the lock, `passes::log_pass`
(a no-op for a dispatch, which carries no transcript), `load` of `checks-open.json`, `book_keep`, and `save` - the whole file
re-serialized, a temp file and a rename. The shim shows nothing else: one spawn (`flock`), the state's read, its temp file and rename.
The arms: 95.1 / 226.8 ms, 17.8 / 158.8 with the file cut to its 12 unfinished dispatches (0.64 MB), 4.1 / 7.4 with none. So 91 ms
is the state's load and save, about 30 ms a MB of it. ALL of this is T387's: it is the same load-and-save T387 is changing for
the plan hold. What its pruning leaves, if it keeps what the 0.64 MB copy keeps: 18 ms a PostToolUse; if a launch also saved only
what changed, less again (not measured: that is T387's design).

**`check-bundle-hooks`** (`check_bundle_hooks.rs` `judge` -> `checks::handle("dispatch")`), three costs:
- On EVERY dispatch the state is loaded under its lock: 34.7 ms for a builder's brief, 8.1 with the 0.64 MB copy, 4.6 with none. A
  builder's dispatch saves nothing (`dispatch_mode` returns before its counter: general-purpose is no check kind).
- A plan review SAVES it too (`planhold::hold` and `save`, `dispatch_mode`'s spec-fidelity branch): 126.2 / 349.5 ms, 19.0 with the
  small copy, 6.5 with none. Both shares are T387's state.
- A record check (a page check or impl-drift: `is_check_kind`) adds, before its counted dispatch is saved: `decide_first` (`git rev-parse`
  and `l7r-gate.sh plan decided`, the launcher's walk 17.4 ms and the binary 10.2 under the shim), `rounds::dispatch`'s git calls
  (`diff --name-only` 13.8 ms, two `merge-base`, a `show`), and `cascade_check` -> `rounds::changed_lines`: `git -c diff.autoRefreshIndex=false
  diff --numstat <merge-base>`, a work-tree diff - 221.2 ms under the shim with the racy index; 40.6 ms on a fresh index; 78.6 ms in the
  real clone (`t388-git.txt`, 20 runs, read-only). Its result decides a trip only where `dispatches - last >= CASCADE_MIN` (10,
  `arbiter.rs` `cascade`), which `cascade_check` asks only AFTER counting the lines. Lever: T492. The arms, after the index fix:
  231.9 ms, 116.3 with no state. The `+fresh` arm did not separate the gate's walk on this case (471.0 against 435.6, both racy, a
  noisy pair at 90th centiles of 887 and 983).

**`review-round-hooks`, 77 to 82 ms on a plan review only** (`review_round_hooks.rs`): `l7r-gate.sh plan door active-task` (the
script started by its shebang, `/usr/bin/env` then bash: 2.5 ms; the walk 19.2 ms; the binary 6.9), then `plan_rounds` reads and
parses `specs/<feature>/plan-review.json`, 4,713,274 bytes (block_reviews 2.7 MB, tasks 1.5 MB), for one task's round count - 40.5 ms
between its open and the guard's next act under the shim. The state's size does not move it (82.1, 82.5 small, 82.9 none);
`L7R_GATE_FRESH` takes 17.1 ms off (65.0). Levers: T493 (the parse), T494 (the walk and the shebang).

**`event-log-hooks`, 13 to 14 ms on each**: the line's write and the dispatch's record; not read further (under 8 s a day).

## (3) The day's cost - an ESTIMATE

From the mix above, the corrected medians, and `checks-hooks` on all 288 PostToolUse calls:

| | calls | ms a call | seconds |
|---|---|---|---|
| PreToolUse, a builder's brief or another non-check (gp) | 133 | 152.8 | 20.3 |
| PreToolUse, a plan review (sf) | 98 | 261.2 | 25.6 |
| PreToolUse, a record check (rf; the sandbox's fresh index, the real clone's diff 38 ms slower) | 65 | 343.8 | 22.3 |
| PostToolUse, every kind | 288 | 120 | 34.6 |
| **an Agent call's hooks, a day** | | | **103 s = 1.7 minutes** |

By guard: pair-hooks 296 x 92 = 27 s (15 s of it the event log read, 5 s the walk); check-bundle-hooks 133 x 34 + 98 x 103 + 65 x 232
= 30 s (23 s the state); checks-hooks 288 x 95 = 27 s (26 s the state); review-round-hooks 98 x 80 = 8 s; event-log-hooks 584 x 13.5 =
8 s. T373 estimated 63 s from 220 calls counted by 18:26 and one case's figure. The state's share, about 49 s, is T387's to take.

## (4) The levers, each priced. None built.

| lever | saves a call | a day | what it risks | filed |
|---|---|---|---|---|
| A. `checkpoint due` asks the switch before `feature_start`, and `first_event` reads line by line to its first event | 50 ms of pair-hooks' 92 on every Agent call (and every `make done`) | 296 x 0.050 = 15 s | none to a verdict while the switch is off (`due` is false either way); the line-by-line read must keep the find rule - the first line that is unparseable or not an ASIDE event | T491 |
| B. the cascade check counts changed lines only where `dispatches - last >= CASCADE_MIN` | 40 to 79 ms of a record check's dispatch | 65 x 0.08 = 5 s | none: the trip is decided by the same two numbers | T492 |
| C. review-round reads `block_reviews` alone, or keeps the count | about 35 of 40 ms on a plan review | 98 x 0.04 = 4 s, growing | the round count, its cap and the stub rule must not change | T493 |
| D. a guard runs the gate launcher by `bash`, and its walk is priced against the guard's own | 2.5 ms (the shebang) to 17.5 (the walk) a call | about 460 x 0.018 = 8 s | a stale gate binary must still be rebuilt before it answers: the walk is what finds it | T494 |
| E. the checks state's load and save (checks-hooks, check-bundle-hooks) | 91 ms a PostToolUse, 27 to 107 a PreToolUse, down to 18 / 8 / 19 at the pruned size | about 49 s | T387's | T387 (not filed again) |

Order by the day: E (T387, 49 s), A (15 s), D (8 s), B (5 s), C (4 s).

## Files

Scripts: `t388-build.sh` (the sandbox), `t388-time.py` (the timing, its arms and variants), `t388-probe.py` (one call under the
shim), `t388-runall.sh`, `t388-runall2.sh`, `t388-mix.py`, `t388-git.py`, `t388-leak-check.sh`; `t388-brief.txt` (the gp prompt).
Tables (columns: arm, runs, median, p90, min, max, children's CPU median, exit codes, load range, first refusal): `t388-guards.tsv`
(section 1), `t388-causes.tsv` (the arms; its last rows after the index fix). Outputs: `t388-mix.txt`, `t388-git.txt`,
`t388-probe-gp-pre.txt`, `t388-probes.txt`, `t388-leak-check.txt`. The sandbox itself (3.0 GB, scratchpad `t388/`) is not in the
record and was left in place.

## Not measured

- A builder's own dispatch from its pool tree (109 of the 296): the session's own case stands for it.
- The 33 dispatches of other kinds (message-check, round-arbiter, escalation-check, research-pass), counted at gp's figure.
- Lever E's figure after T387's real design (save only where changed): the pruned-size arm is a stand-in.
- The `+fresh` arm on the record check (noisy with the racy index, not rerun after the fix).
- Lever A on a Bash `make done` (counted by pair-hooks' code, not timed).
