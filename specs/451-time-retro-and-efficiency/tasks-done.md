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
- [x] T15 [perf] A run the harness cannot track: `no_poll_hooks` refuses a make or cargo job detached by a lone `&` unless a `wait` at a command position covers it (in the job's own list and shell, unconditional, not backgrounded; bare, `wait $!` with no `&` between, or `wait %N` naming it), or started under `nohup` or `setsid` at a command position, or followed by a `disown` in any form (bare, `%N`, `-h`, `-a`) whatever `wait` follows, naming `run_in_background`; `DETACH_OK` (D12; FR-008, FR-012, SC-003)
      research: rendering
      held: rust/guard/src/guards/no_poll_hooks.rs
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
- [x] T18 [perf] `make land T="T1,T2"` read as `T="T1 T2"`, in `rust/gate/crates/land/src/land.rs` and `make land`'s help (D16; FR-011); lands before T08, so a land line naming two tasks is booked to both (T03's plan review, 2026-11-20)
      research: rendering
      held: Makefile (the help line only)
      verify: DONE. landed in batch T18+T24+T28+T29+T15+T30: performance work first, and four of the improvements
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
