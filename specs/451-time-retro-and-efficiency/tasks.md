# Tasks - feature 451, where the time goes, and the six cheap fixes

Ticked tasks are archived in `tasks-done.md` (feature 449 T142): `make tick` moves each ticked task there with its lines; this file holds the open ones.

**Input**: `plan.md` (D1-D17 and each task's section), `research.md` (R1-R12), `data-model.md`, `contracts/refusals.md`, `spec.md`.

Every task is tooling, so every task is `research: rendering`. Each builder task is one guard or one reader, so no builder's context
grows large (the feature's own lesson, User Story 2). A task whose files include a HELD file (research R11: `rust/guard/src/**` but its
tests, `scripts/hooks/*.sh`, the root `Makefile`) says so; its builder runs `make guard-edit FILE=<file> WHY="<reason>"` for each
before the first edit. Every task writes prose or code: American spellings, hyphens only. Each refusal's test is written first and
seen red, then the check deleted and the test seen red again (FR-012).

## Occasions

- none: tooling only - no map feature, sheet, glyph, placement rule or research page changes.

## Dependencies

- T01 before any tick (the plan gate).
- T02 first of the data: every later task reads its detector. T03 next: T07, T08 and T14 read its table and `task` field. T04 before
  T05, T06 (`append_row`) and T09 (`BgEnd`).
- T08 after T02-T07; T09 after T08; T10 after T09; T11 after T10.
- T12 before T13 (one guard). T13 and T14 after T03 (the line's `task`) and T06 (the landing's `end` line naming its tasks, D5), T14
  after T02. T15 before T16 (one file). T17, T18, T19 independent of each other.
- T20 before T21 (the shard form). T22 last.

The order, the GM 2026-11-20 (request.md: "let's prioritize those remaining improvement fixes"): the refusals and the split (T12-T21) before the rest of the data and the readers (T07-T11), since they make the work after them faster; T06, in flight, lands first (T13 and T14 read its `end` line). Lanes: T18 then T14; T15, T16, then T12, T13; then T17, T19, T20, T21; then T07-T11; then T22. Parallel lanes, where two builders are run at once: T05 beside T06
(different crates); T17, T18 and T19 beside each other; T21's two suites beside each other. Two builders never edit one held file at
once.

## Implementation strategy

The refusals and the split first (T12-T21, with T28 after T18), the GM 2026-11-20: performance work before other work, since it
makes the work after it faster. Then the rest of the data and the readers (T07-T11: the retrospective as one command), each refusal
landing on its own, each small; T22 last.

## Tasks

### The plan review

### The event-log data (FR-001 to FR-004)

### The readers (FR-005)

- [ ] T09 [perf] `make where-time`'s background-run column: a launch paired with its end - the log's `BgEnd`, else the subagent transcript's `queued_command` row holding its `<tool-use-id>`, else open to the window's end - and a between-turns wait booked to the runs its `Stop` line names `inflight`, in `rust/gate/crates/measure/src/measure/where_time/columns.rs` (D3, D7; FR-002, FR-005, SC-001); its waits start from the Stop line that opened them, and those lines can sit in another feature's log (T08's finding, folded into T10) - T09 reads the session's turn lines across every feature's log, or lands after T10 does (T08's plan review, 2026-11-21)
      research: rendering
      verify: red first - User Story 1's acceptance scenario 2 as a fixture (a background `make land`, its `BgEnd`, the wait it caused booked to land), a subagent's run ended by its transcript's attachment, a run with no end booked open from its start; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T10 [perf] `make where-time`'s critical path apart from the summed agent-minutes, each agent's minutes and tokens under its task, and the rework (refused landings from the landing's `end` lines whose `landed` is false, plan re-rounds from a task's later `spec-fidelity` dispatches), in `rust/gate/crates/measure/src/measure/where_time/columns.rs` (D5, D6, D7; FR-005, SC-002); and a session's turn ends read from every feature's log, so time between turns is booked as waiting, not model - T08 found the main session's Stop lines filed in the log of whichever feature was active (449's), leaving 451's walk to book 235.4 of 342 model minutes that the transcript shows between turns, measured 2026-11-21 (the 451 log's in-turn stretches against the main transcript's turn ends, /tmp/t08/real6.md) (T08's found-and-left, folded into T10); T09 built the shared turn reader (events::turn_lines, with_turns), which moved 253 model minutes, so T10 reconciles that with the 235.4 cited above; (another feature's turns are booked apart by T09 itself, its plan review 2026-11-21)
      research: rendering
      verify: red first - two agents overlapping a main-session wait book the wait once on the critical path and both agents under their tasks with their tokens, a landing `end` of code 1 and a second `spec-fidelity` dispatch count as rework; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`
- [ ] T11 [perf] `make feature-report` reads the same columns through `where_time/columns.rs`, in `rust/gate/crates/measure/src/measure/feature_report.rs` and `feature_report/tables.rs` (D7; FR-005)
      research: rendering
      verify: red first - T08's fixture through `feature-report` gives `where-time`'s sums; `make feature-report F=451` shows the columns; `make rust-test CRATE=rust/gate/crates/measure`; `make quick`

### The refusals (FR-006 to FR-009, FR-011), each red first (FR-012)

### The hook-suite split (FR-010)

### The close

- [ ] T22 [perf] The close: on the first full day of work after T02-T21 land, SC-001 (`make where-time F= SINCE= UNTIL=`, unexplained waiting under a tenth), SC-002 (the day's per-task table from the log against a hand join of the transcripts, each bucket within a tenth), SC-005 (static runs per task, builders' largest contexts, every escape listed), `docs/guards.md`'s knob table complete (D14), then `make feature-report F=451 WRITE=1` (SC-001, SC-002, SC-003, SC-005); and CONTEXT_CAP_TOKENS retuned on the day's per-call speed by context: on 2026-11-20 builders reached their first edit at a median 162k of context (90th percentile 254k, 5 of 99 past 300k) and peaked at a median 498k (99 of 114 past 300k), measured 2026-11-20 (the session's subagent transcripts, the last usage before each builder's first Edit or Write, and its largest) - so at 300k most tasks hand off once; the first real firing stopped T13's builder before any edit; and the plan template's `Performance work?` placeholder (rust/gate/crates/plan/src/plan/template.rs) names FR-013's measurement clause beside its speed clause (T08's blocks review, 2026-11-21)
      research: rendering
      verify: `report.md` holds the three measurements against their bars; a missed bar names its number and the knob it retunes; `make quick`
- [ ] T48 The bundle reads ids inside a clause naming another feature as the reviewed feature's (the round arbiter on ask:451-T46-fourth-round, accept, 2026-11-20): '<ids> in N's' / '<ids> of feature N' fall to the reviewed feature's bare reading; measured first - how often such a clause names a feature other than the reviewed one across specs/*/plan.md and plan-done.md - and fixed (read as N's, carried or named NOT FOUND, red first) only if a real one hands a reviewer the wrong text
      research: rendering
- [ ] T49 gate_write_hooks lets through a write into the tree made through a function of the program's own (found by T33's after8 gate replay, 2026-11-20): window#170's `replace_note("citations/urban-features.html", ...)`, whose function writes `R / path` with `R = Path("research")`, and window#172's `sub(<the urban-features record page>, ...)`, writing `Path(f)`, run unread under a running gate, as at HEAD - place such a literal by reading the function's body (which parameter reaches the write, onto what base; a base the program computes fails open, so window#72 stays let through), red first on #170 and #172's shapes, the replay's moves accounted
      research: rendering
- [ ] T50 shared::tree's git_write reads 12 writing git subcommands as reads (found by T33, 2026-11-20): worktree, clone, init, switch, bisect, sparse-checkout, submodule, config, fetch, notes, update-ref, symbolic-ref - T33 added them and the replay of 1,134 commands caught no real write with them (only 2 false refusals, fixed) while a review found four misreadings (fetch -n is --no-tags; one value-option list for all twelve; config --global writes outside the repository), so T33 dropped them; measured first on a corpus that runs them in the mirror or a clone, each subcommand's options read from its own -h, added only where a move is a correction, red first; git stash list and show are reads since T33 (fixed there)
      research: rendering
- [ ] T51 A program run from a script file (python3 $S/x.py) is not read by make-only's guard-write or the gate's shell-write check (found by T33, 2026-11-20): of the replay's 1,134 rows, 41 scratch scripts whose source a heredoc in the corpora wrote, run through make-only's reader as -c programs, give 5 refusals - window#215's desc195.py rewriting a clone's Makefile, a real guard-file write the guard let through, and 4 false (window#302, #305, #306, #309 read or run house-style-hooks.sh) - and 7 rewrite a clone's research page, test or Makefile the gate would see; measured first - read the script file's text at the call, replayed over the corpora with the 4 false shapes as the let-through baseline - and fixed red first where a move is a correction
      research: rendering
- [ ] T52 The make-call readers that skip shared::make (the 451 T02 class, counted by 451 T36): 10 readers of command text keep their own reading of a make call, measured 2026-11-20 (a grep of rust/, scripts/ and the Makefile, and of rust/ at HEAD for make literals outside tests, process-table, log-field and prose readers and batching_hooks NOT_RECON set apart) - shared/checks/rounds.rs APPLY (make apply-edits FROM=), ledger_hooks appended (make append), claims_file_hooks VERB (make lines or append), make_only_hooks LANDING (land-tooling FILES, arbiter-fix-done LAND) and LABEL_TARGET, measure stepback_bundle/words.rs MAKES and measure_hooks has(make done), each reading a mention such as echo make append as a call; phase_source_hooks search.rs (make phase-read), shared/tree.rs (a segment headed by make) and gate_write_hooks head_of (a make segment left to the shared::make check), each past its own wrapper list, which skips timeout or flock - measured first, each reader against shared::make::invoked on the T02 red shapes and the T33 replay corpus, and moved onto shared::make only where a real command gets a wrong verdict, red first on that shape; lands before T22
      research: rendering
- [ ] T53 [perf] Three T26 leftovers (found by 451 T36): make events-refile DRY=1 still moves 19 lines, 17 from the 449 log and 2 from the 385 log, measured 2026-11-20 (make events-refile DRY=1 in this clone); the 17 were written 09:36Z to 13:21Z, after the T26 writer landed, 15 of them SubagentStart lines whose brief names 451, while the one builder checked, T05's (a9442ba44c1f1f44e), had its tool lines reach the 451 log, measured 2026-11-20 (the 449 log joined by hand to the subagents meta files; that one builder's id looked up in the 451 log) - so the writer may file a SubagentStart line by feature.json: measured first (whether the meta file is readable when SubagentStart fires), a wrong filing fixed red first on that shape, then make events-refile run once more; and the indexes name the files T26 and T04 added - rust/guard/CLAUDE.md (the event_log_hooks row: filed.rs, fields.rs) and rust/gate/CLAUDE.md (the measure row: event_log/refile.rs, make events-refile); lands before T22
      research: rendering
- [ ] T54 [perf] The stale-terms guard refuses a review on a common word (found 2026-11-20): an FR-013 amendment's spec review was refused with 66 candidates, every one the word 'end' in history (plan-done.md) and other tasks' sections the amendment did not touch - a refusal on correct work, which costs an escape each time; measured first (the candidates of recent refusals, how many named text the change made untrue), then the subject read from what the change moved, not a bare common word, red first on this case
      research: rendering
- [ ] T55 [perf] A builder's closing checks run one after another and block its writing (measured 2026-11-21 over 39 builders' transcripts: after the last code edit, 63 min of tests in the foreground and 101 min idle on its own background runs, beside 158 min of model time writing the plan section, decide and the report, which need no check's result) - make closing-checks runs make static, make hooks-test and make quick at once with one combined result, and the builder's step order starts it in the background the moment the code is done, writing its section and running decide while it runs; measured before and after on the next tasks' transcripts (the closing tail's idle minutes), and whether a check that decide ran while the closing checks ran is worth its cost read from the event log once T09 lands (the GM 2026-11-21, request.md: "yes please file that as a performance task")
      research: rendering
- [ ] T56 [perf] make events-refile leaves 23 lines in 385's log (found by T53, 2026-11-21): a 451 T47 builder's review agents, briefed with a task id and no feature, matched 385's T47 start of 2026-10-18 and were filed in 385's log; T53's writer now gives a start over 72 hours old no feature, but the refile (rust/gate/crates/measure event_log/refile.rs) still reads the old rule, so they stay - the refile shares the writer's rule (one reader, not a copy), a dry run shows the 23 moving, red first; then the real refile run once T53 and this land
      research: rendering
- [ ] T57 [perf] make static compiles and runs each crate's tests twice (measured 2026-11-21 over the event log's Phase lines since 2026-11-20T12:35Z: build 82 min and test 44 min beside cover-build 73 min and cover-run 44 min) - a plain test binary built and run, then a coverage-instrumented one built and run over the same tests; measured first what the plain run catches the covered run does not (a test that differs under instrumentation, a cfg, a feature), then static's plain build and test dropped where the covered run answers for them, make rust-test's fast uninstrumented loop unchanged, red first on a failing test caught by the covered run alone
      research: rendering
- [ ] T58 [perf] rust/guard is the root of 27 gate crates, so any guard edit rebuilds them all (measured 2026-11-21 over the event log's Phase lines: 128 real guard rebuilds at a median 18 s, and the whole-workspace coverage rebuild of 27-28 crates 18 times, about 15 min) - the gate crates use the guard's shared readers, not its hooks; measured first how many guard edits touch src/shared/ against a single hook, then, if hooks dominate, the shared modules split into their own crate the gate crates build on, so a hook edit rebuilds the guard alone; red first on the rebuild count of a hook edit
      research: rendering
