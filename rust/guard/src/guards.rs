//! The guards, one module each, in the fixed order `lib::guards` runs them (plan D2): each ported from its shell guard by its own
//! task (feature 449 T006-T049), its suite replayed against `l7r-guard --only <guard>` before its shell is deleted (D3, D4).

pub mod agent_stall_hooks;
pub mod archive_first_hooks;
pub mod batching_hooks;
pub mod budget_change_hooks;
pub mod clone_sync_hooks;
pub mod conflict_marker_hooks;
pub mod discard_hooks;
pub mod engine_freeze_hooks;
pub mod event_log_hooks;
pub mod feature_approval_hooks;
pub mod finished_run_hooks;
pub mod gate_hooks;
pub mod gate_write_hooks;
pub mod gm_tree_hooks;
pub mod idle_tests_hooks;
pub mod ledger_hooks;
pub mod main_tree_hooks;
pub mod measure_hooks;
pub mod no_branch_hooks;
pub mod no_poll_hooks;
pub mod pair_hooks;
pub mod stall_watchdog_hooks;
