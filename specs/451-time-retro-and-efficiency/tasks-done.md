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
- [x] T23 Two builders' cargo runs in one clone corrupt each other's coverage (found by T02, 2026-11-20): T02's make static ran beside T234's cargo in the same target directory and failed on corrupt or missing coverage profiles in seven crates, a collision, not a result - the Rust checks take one lock a target directory for the length of a run, the second waiting (named, with how long) rather than racing, red first with two concurrent runs
      research: rendering
      verify: DONE. landed: one lock a target directory for the Rust checks
- [x] T25 make decide's figure lint stops at its first finding (found writing T23's section, 2026-11-20): an unlabeled figure is reported one a run, so a section with four took four runs and four turns to clear - it reports every finding of the section together, each with its line, as make done reports every failure together, red first with a fixture section holding three
      research: rendering
      verify: DONE. landed in batch T25+T27: make decide reports every finding together; T27 folded in
- [x] T26 The event log files a line under the clone's .specify/feature.json, not the line's own feature (found by T03, 2026-11-20): with two features worked in one clone (449 and 451 on 2026-11-20), every line lands in the log feature.json names, so a 451 builder's T03 is booked in 449's log as 449's T03 and where-time reports both features wrong - a line is filed under the feature of the task it carries (the dispatch's brief, the task-start in force for that feature, the make target's F=), feature.json only where nothing else says, red first with two features' builders in one clone; lands before T07, T08 and T14 (the readers of the task field), and re-files the lines written before it: a line whose task names no task of its log's feature but one of another feature's moves to that feature's log (T03's plan review, 2026-11-20); and its plan says how a line with no task, or whose task came from D2's fallback (the task-start of the feature feature.json names), is filed, since the re-file rule by task id cannot reach it (T03's plan review, round 3)
      research: rendering
      verify: DONE. landed: each event line filed under its own feature
- [x] T27 Withdrawn: folded into T25 (T25's plan review, 2026-11-20, BLOCKED its deferral). make decide checks item 4 of a section's first Approach block only (found by T25, 2026-11-20): the item-4 rule reads only the section's first '4. **' item, so an unlabeled figure in a re-answered Approach block's item 4 reaches the plan review - every Approach block's item 4 read, red first with a section holding two; lands before T17
      research: rendering
      verify: DONE. landed in batch T25+T27: make decide reports every finding together; T27 folded in
