# 451-time-retro-and-efficiency - the ticked tasks, archived by `make tick` (feature 449 T142; the open ones are in tasks.md)

- [x] T01 `spec-fidelity` PLAN REVIEW of plan.md, recorded with `make plan-verdict F=451 FILE=<json> AS=spec-fidelity` (the subagent runs it); the plan's narrow readings named for it - D4 (phases per family, not per crate), D8 (the builder), D11 (the main session's runs counted), D12 (`&` then a `wait` covering the job passes), D14 (`make tunables`) (feature 243)
      research: rendering
      verify: DONE. landed: the plan reviewed CLEAR (round 4)
- [x] T02 One make detector: `shared::make::invoked` (the targets in command order, at a command position past `(`, `{`, `flock <file>`, `nice`, `time`, `timeout N`, `env` and `VAR=`), `targets()` its set, and the event-log writer's own `MAKE` pattern deleted for it; `scripts/gates/l7r-gate.sh rust <cmd>` read as `rust-<cmd>` (D1; FR-001); the XIII baseline taken first in a detached worktree
      research: rendering
      held: rust/guard/src/shared/make.rs, rust/guard/src/guards/event_log_hooks.rs
      verify: DONE. landed: one shared make-target detector
