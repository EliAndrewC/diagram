# 451-time-retro-and-efficiency - the ticked tasks, archived by `make tick` (feature 449 T142; the open ones are in tasks.md)

- [x] T01 `spec-fidelity` PLAN REVIEW of plan.md, recorded with `make plan-verdict F=451 FILE=<json> AS=spec-fidelity` (the subagent runs it); the plan's narrow readings named for it - D4 (phases per family, not per crate), D8 (the builder), D11 (the main session's runs counted), D12 (`&` then a `wait` covering the job passes), D14 (`make tunables`) (feature 243)
      research: rendering
      verify: DONE. landed: the plan reviewed CLEAR (round 4)
- [x] T02 One make detector: `shared::make::invoked` (the targets in command order, at a command position past `(`, `{`, `flock <file>`, `nice`, `time`, `timeout N`, `env` and `VAR=`), `targets()` its set, and the event-log writer's own `MAKE` pattern deleted for it; `scripts/gates/l7r-gate.sh rust <cmd>` read as `rust-<cmd>` (D1; FR-001); the XIII baseline taken first in a detached worktree
      research: rendering
      held: rust/guard/src/shared/make.rs, rust/guard/src/guards/event_log_hooks.rs
      verify: DONE. landed: one shared make-target detector
- [x] T03 The category table and the line's task: the shared `bucket_of` table (`data-model.md`'s rows, with `format`, `render-sync` and `map` placed) in `rust/guard/src/guards/event_log_hooks.rs`, `category()` booking a Bash call by it, and `task` on every line where known - a command's `T=` (`tick`, `task-start`, `decide`, `land`), a subagent's meta `description`, else the clone's active task (D2; FR-001, SC-002)
      research: rendering
      held: rust/guard/src/guards/event_log_hooks.rs
      verify: DONE. landed: the shared category table and the task on every line
- [x] T04 A background run's end: `bg` on a backgrounded Bash call's PostToolUse, a `BgEnd` line from a `<task-notification>` prompt with a `<tool-use-id>`, `inflight` on Stop and SubagentStop from `background_tasks`, and `append_row` public for the gate's tools, in `rust/guard/src/guards/event_log_hooks.rs` (its tool fields moved to `event_log_hooks/fields.rs` if the file would pass the file cap); and the one reader, `rust/gate/crates/measure/src/measure/events.rs::load_events`, setting the new kinds (`BgEnd`, `Phase`) aside from the time-gap stream until T08 and T09 read them (D3, D4; FR-002)
      research: rendering
      held: rust/guard/src/guards/event_log_hooks.rs (and event_log_hooks/fields.rs if made)
      verify: DONE. landed: a background run's end is logged
- [x] T05 The Rust checks' phase lines: `build`, `test`, `cover-build` (per family), `cover-run`, `lint` and `format` per crate, each with its wall-clock span, through `append_row`, in `rust/gate/crates/rustc/src/rustc.rs`, `rustc/cover.rs`, `rustc/side.rs`, `rustc/kept.rs` (D4; FR-003); and every reader outside measure's load_events filters the event log by kind before it reads a line's time - reviews/glyph.rs takes the log's first event as the feature's start, which a Phase line would become (T04, 2026-11-20), red first
      research: rendering
      verify: DONE. landed: the Rust checks' phase lines
- [x] T06 The landing's phase lines: `cheap`, `gate`, `cohort`, `claims`, `push` and an `end` with the exit code and `tasks` (the ids it was asked to land), in `rust/gate/crates/land/src/land.rs` and `land/long_runs.rs`, each line filed in the landed feature's log by `append_row_for` (D5; FR-003)
      research: rendering
      held: rust/guard/src/guards/event_log_hooks.rs (and event_log_hooks/filed.rs)
      verify: DONE. landed: the landing's phase lines
- [x] T12 [perf] The context cap: a new guard `context_cap_hooks` refusing a builder's tool call past `CONTEXT_CAP_TOKENS` (GUESS, 300k) but the Write of its handoff file, naming the file and the next step; its first step one real subagent PreToolUse payload captured and pinned as the fixture (D8, D9; FR-006, FR-012, SC-003, SC-005)
      research: rendering
      held: rust/guard/src/guards/context_cap_hooks.rs (new), rust/guard/src/guards.rs, rust/guard/src/lib.rs, Makefile (`make context-ok`)
      verify: DONE. landed in batch T12+T17: the builder context cap; unordered deferrals refused
- [x] T13 [perf] A builder resumed: `context_cap_hooks` refuses a SendMessage to a builder past the cap, or to one whose task (D2's chain: its meta `description`'s `T<n>`, else its first line's `task`, else the `task-starts.jsonl` entry in force at its dispatch) has landed since its dispatch (D5's `end` line naming it, read by its `landed`, true) or is ticked or archived, naming a fresh dispatch with the handoff file; with no task found the landing check passes with a `no task` guard-log record, and the cap check still applies (D10; FR-006, FR-012, SC-003); and D9's per-agent permit `make context-ok AID= WHY=` (a root Makefile target and guard_file_hooks' grantable widened to a `context-cap:<agent id>` key), so a builder resumed past the cap under D10's escape gets through context_cap_hooks on its next call (T12's found-and-left, the session's ruling 2026-11-20), red first
      research: rendering
      held: rust/guard/src/guards/context_cap_hooks.rs
      verify: DONE. landed in batch T13+T19: resume past the cap refused; task-add lints its line
- [x] T14 [perf] The third `make static`: a new guard `static_runs_hooks` refusing a task's third run since its last landing that succeeded, or since its first start if it has never landed (a later `task-start` resets nothing), naming the crate-scoped checks for the crates its delta changes; `STATIC_RUNS_A_TASK` (GUESS, 2) (D11; FR-007, FR-012, SC-003, SC-005)
      research: rendering
      held: rust/guard/src/guards/static_runs_hooks.rs (new), rust/guard/src/guards.rs, rust/guard/src/lib.rs
      verify: DONE. landed in batch T14+T16: a third make static refused; the slow poll refused
- [x] T15 [perf] A run the harness cannot track: `no_poll_hooks` refuses a make or cargo job detached by a lone `&` unless a `wait` at a command position covers it (in the job's own list and shell, unconditional, not backgrounded; bare, `wait $!` with no `&` between, or `wait %N` naming it), or started under `nohup` or `setsid` at a command position, or followed by a `disown` in any form (bare, `%N`, `-h`, `-a`) whatever `wait` follows, naming `run_in_background`; `DETACH_OK` (D12; FR-008, FR-012, SC-003)
      research: rendering
      held: rust/guard/src/guards/no_poll_hooks.rs
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T16 [perf] A main-session wait slower than its check: `no_poll_hooks` refuses, on the POLL_OK and the file-watching paths, a loop whose longest `sleep` is over `POLL_CHECK_S` (GUESS, 60 s) from a payload with no `agent_id`, naming the 60 s form; `SLOW_POLL_OK` (D13; FR-008, FR-012, SC-003)
      research: rendering
      held: rust/guard/src/guards/no_poll_hooks.rs
      verify: DONE. landed in batch T14+T16: a third make static refused; the slow poll refused
- [x] T17 [perf] The deferral's form: `make decide` refuses a found-and-left deferral without its reason, task id and order, or whose task id or "lands before" id names no OPEN task (an unticked box of the feature's `tasks.md`) when `make decide` judges it, or whose order names its own id, and a class fix without its labeled line on how every instance was found, in `rust/gate/crates/plan/src/plan/lint.rs` (the timeless parts, which `make plan-delta` runs too) and `plan.rs::decide` (the open test alone); the template's placeholder states the form (`plan/template.rs`); `DEFER_FORM_OK` on `make decide`, honored by `make plan-delta` for a section decided under it and taken by `make plan-delta` too (D15; FR-009, FR-012, SC-003)
      research: rendering
      held: Makefile
      verify: DONE. landed in batch T12+T17: the builder context cap; unordered deferrals refused
- [x] T18 [perf] `make land T="T1,T2"` read as `T="T1 T2"`, in `rust/gate/crates/land/src/land.rs` and `make land`'s help (D16; FR-011); lands before T08, so a land line naming two tasks is booked to both (T03's plan review, 2026-11-20)
      research: rendering
      held: Makefile (the help line only)
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T19 [perf] `make task-add` runs each of `make quick`'s checks to its own end over what it wrote and, on a red, again with the line withdrawn; where the with-line run has any failure (a check's finding, line numbers masked) the other lacks, the line stays withdrawn and it refuses naming those failures; the line is restored only when the failures are the same; `QUICK_OK` on `make task-add`, in `rust/gate/crates/task/src/task_add.rs` (D16; FR-011, FR-012, SC-003)
      research: rendering
      held: Makefile
      verify: DONE. landed in batch T13+T19: resume past the cap refused; task-add lints its line
- [x] T20 [perf] The shard form - `tests/hooks/test-<name>.<k>.sh`, each shard a job under the suite's stamp key, the suite stamped green only when every shard is, the companion check accepting shards - in the `hooks-test` recipe and `tests/hooks/hookrun.sh`, proved on `tests/hooks/test-parts.sh` split in two; the entry-gate split moved to T21 with the other two (the session, 2026-11-20) (D17; FR-010, SC-004)
      research: rendering
      held: Makefile
      verify: DONE. landed in batch T20+T32: the shard form; the guard's tests read their own environment
- [x] T21 [perf] The three slowest suites split into shards where it speeds the run (measured 2026-11-20: `tests/hooks/test-l7r-gate.sh` split in three, about 6 s off an incremental run; `test-sync-with-main.sh` and `test-entry-gate.sh` kept whole, their splits saving nothing; the full run's wall set by entry-gate's case-4 chain) (D17; FR-010, SC-004)
      research: rendering
      verify: DONE. landed in batch T21+T35: the l7r-gate split; the run lock's test on a stepped clock
- [x] T23 Two builders' cargo runs in one clone corrupt each other's coverage (found by T02, 2026-11-20): T02's make static ran beside T234's cargo in the same target directory and failed on corrupt or missing coverage profiles in seven crates, a collision, not a result - the Rust checks take one lock a target directory for the length of a run, the second waiting (named, with how long) rather than racing, red first with two concurrent runs
      research: rendering
      verify: DONE. landed: one lock a target directory for the Rust checks
- [x] T24 A gate test reads the real environment (found by T02, 2026-11-20): rust/gate/crates/bundle/src/record/helpers/tests.rs (about line 377) means to reach helpers.rs:537's error path by writing [1] into feature.json, but l7r_guard compiled without cfg(test) reads SPECIFY_FEATURE from the real environment, so with it exported the path is skipped, the test still passes (it accepts 0 or 1) and make static's coverage goes red - the test given its own environment, asserting the one outcome it means, red first with SPECIFY_FEATURE exported; lands before T08 (T03's plan review, 2026-11-20)
      research: rendering
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T25 make decide's figure lint stops at its first finding (found writing T23's section, 2026-11-20): an unlabeled figure is reported one a run, so a section with four took four runs and four turns to clear - it reports every finding of the section together, each with its line, as make done reports every failure together, red first with a fixture section holding three
      research: rendering
      verify: DONE. landed in batch T25+T27: make decide reports every finding together; T27 folded in
- [x] T26 The event log files a line under the clone's .specify/feature.json, not the line's own feature (found by T03, 2026-11-20): with two features worked in one clone (449 and 451 on 2026-11-20), every line lands in the log feature.json names, so a 451 builder's T03 is booked in 449's log as 449's T03 and where-time reports both features wrong - a line is filed under the feature of the task it carries (the dispatch's brief, the task-start in force for that feature, the make target's F=), feature.json only where nothing else says, red first with two features' builders in one clone; lands before T07, T08 and T14 (the readers of the task field), and re-files the lines written before it: a line whose task names no task of its log's feature but one of another feature's moves to that feature's log (T03's plan review, 2026-11-20); and its plan says how a line with no task, or whose task came from D2's fallback (the task-start of the feature feature.json names), is filed, since the re-file rule by task id cannot reach it (T03's plan review, round 3)
      research: rendering
      verify: DONE. landed: each event line filed under its own feature
- [x] T27 Withdrawn: folded into T25 (T25's plan review, 2026-11-20, BLOCKED its deferral). make decide checks item 4 of a section's first Approach block only (found by T25, 2026-11-20): the item-4 rule reads only the section's first '4. **' item, so an unlabeled figure in a re-answered Approach block's item 4 reaches the plan review - every Approach block's item 4 read, red first with a section holding two; lands before T17
      research: rendering
      verify: DONE. landed in batch T25+T27: make decide reports every finding together; T27 folded in
- [x] T28 [perf] Performance work goes first (FR-013, the GM 2026-11-20): a [perf] tag or PERF=1 marks a task; make task-start refuses a task that is not performance work while an open performance task exists in any active feature, naming it and its task-start, escape PERF_LATER_OK="<reason>" recorded; the Stop hook's start-the-next names an open performance task first; 451's T12-T21 and every open task across features that speeds the work tagged [perf] (a list measured, each named); red first; lands right after T18; and a [perf] task's plan section answers "Performance work?" yes (T12-T19's sections say no today, in the checklist's engine-timing sense - square the two meanings in the plan, PERF=1 meaning the checklist); an in-flight lane refused by it uses the escape with its reason
      research: rendering
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T29 [perf] make set-down leaves the feature's started-task mark (found landing T06, 2026-11-20): 449 was set down with T241 parked, but .git/active-task still named 449 T241, so sync-with-main's speckit-todo --holding held every push touching 449's specs (T06's landing refused, its ticks reverted); set-down clears the clone's active-task mark when it names the set-down feature (and a later task-start of that feature restores it), red first
      research: rendering
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T30 [perf] Withdrawn: folded into T15 (T15's plan review, 2026-11-20, ruled leaving the shared readers' defects NOT LEGITIMATE). The shared shell readers miss forms (found by T15, 2026-11-20): shared::shape::strip_heredocs misses `cat <<'EOF' > f` (words after the delimiter), strip_quotes keeps a string after `-c ` (`grep -c "make x &"`) and blanks one after `bash -lc`, and shared::make::invoked misses `setsid make`, `bash -lc "make x"` and a goal-less make - every guard and the event log's make detector share them (T15 works around them in no_poll_hooks; the event log booked a landing launched after a python3 -c string as other tool, T08's note); fixed in the shared code, T15's work-arounds retired onto it, red first on each form
      research: rendering
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T31 [perf] main-tree refuses a read as a write (found by T15's corpus replay, 2026-11-20): `python3 -c "data = open('$SP/x.html','rb').read() ..."` is refused with no escape as a write where the shell stands, the same before and after T15's shared-reader fix - measure it on the corpora (the main-tree refusals whose command only reads), and fix a refusal of correct work in the guard, red first
      research: rendering
      verify: DONE. landed in batch T31+T40: python3 -c reads let through; entry-gate's suite faster
- [x] T32 [perf] Guard tests read the real environment (found by T14, 2026-11-20): with L7R_FEATURE_DIRECTORY exported (page sessions export it) 17-20 tests of checks_hooks, check_bundle_hooks, pair_hooks, review_round_hooks, shared::checks::arbiter and no_poll_hooks fail - T24's defect in the guard's own tests; each test given its own environment (no process-env mutation), asserting the one outcome it means, red first with the variable exported, and every other variable the guard reads swept the same way
      research: rendering
      verify: DONE. landed in batch T20+T32: the shard form; the guard's tests read their own environment
- [x] T34 [perf] No make target formats one file (found by T14, 2026-11-20): make format reformats every crate, so a builder beside another's in-progress files formats with bare rustfmt outside make - make format FILE=<path> (or CRATE=) formats only what it names, red first
      research: rendering
      verify: DONE. landed: make format FILE= and CRATE=
- [x] T35 [perf] Two timing tests fail under load (found by T12, 2026-11-20): rustc's another_runs_holder_is_waited_for_named_and_past_the_ceiling_refused expects two waiting lines inside a 60 ms ceiling at a 10 ms poll and saw one under make static's load, and test-land-tooling.sh case 2b fails under the full hooks-test run and passes alone - a red gate on correct work; each test's timing taken from what it measures (an event, a count, or a ceiling scaled by a calibration loop), never a bare wall-clock bound, red first under induced load; its land-tooling half (case 2b) folded into T20 by T20's plan review (2026-11-20), so T35 holds the rustc test alone
      research: rendering
      verify: DONE. landed in batch T21+T35: the l7r-gate split; the run lock's test on a stepped clock
- [x] T37 [perf] The plan-review bundle cuts a decision at its list (found by T19's plan review, 2026-11-20): spec-cited.md stops D16 at 'Two things make the comparison real:' and drops the bullets, as it stopped D15 at a colon for T17's review - a reviewer judges a decision without its text, and asks a round for it; every cited decision carried whole, its lists included, red first on D15 and D16
      research: rendering
      verify: DONE. landed in batch T37+T39: whole decisions in the bundle; FRESH not a replay
- [x] T39 [perf] A FRESH=1 test run may replay another run's result (found by T32, 2026-11-20): two make rust-test CRATE=rust/guard FRESH=1 runs queued behind one target-directory lock both reported 'finished in 4.21s', where alone it takes 2.82-3.20 s - if a run waiting on the lock takes the holder's kept result, a fresh run reports green without running; measured first (two FRESH runs started together, each one's test binary execution counted), fixed red first if so
      research: rendering
      verify: DONE. landed in batch T37+T39: whole decisions in the bundle; FRESH not a replay
- [x] T40 [perf] entry-gate's case-4 chain sets hooks-test's full-run wall (found by T21, 2026-11-20): in every full run the wall was entry-gate's seconds plus 2-3 s, about 10 s ahead of the next suite, its case 4 a chain of record gates on one clone's state (9.4 s alone, 31-46 s in a full run); splitting it or more job slots did not shorten it - measure where the chain's time goes (alone and under the full run's load) and cut it, held to the suite still checking what it checks
      research: rendering
      verify: DONE. landed in batch T31+T40: python3 -c reads let through; entry-gate's suite faster
