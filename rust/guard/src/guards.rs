//! The guards, one module each, in the fixed order `lib::guards` runs them (plan D2): each ported from its shell guard by its own
//! task (feature 449 T006-T049), its suite replayed against `l7r-guard --only <guard>` before its shell is deleted (D3, D4).

pub mod agent_model_hooks;
pub mod agent_prefix_hooks;
pub mod agent_stall_hooks;
pub mod archive_first_hooks;
pub mod batching_hooks;
pub mod blocked_fetch_hooks;
pub mod budget_change_hooks;
pub mod check_bundle_hooks;
pub mod checks_hooks;
/// Write an executable a test will run, the file written by a child process.
///
/// A thread that forks in another test copies every open descriptor until its child execs, so a
/// script this process has just written can still be open for writing in that child and running
/// it fails with "Text file busy". `install` holds the only descriptor that writes the file, and
/// it has exited by the time this returns.
#[cfg(test)]
pub(crate) fn write_executable(path: &std::path::Path, text: &str) {
    let draft = path.with_extension("draft");
    std::fs::write(&draft, text).unwrap();
    let done = std::process::Command::new("install")
        .args(["-m", "755"])
        .arg(&draft)
        .arg(path)
        .status();
    assert!(done.unwrap().success());
    std::fs::remove_file(&draft).unwrap();
}

#[cfg(test)]
mod case_tables;
pub mod claims_file_hooks;
pub mod clone_sync_hooks;
pub mod conflict_marker_hooks;
pub mod discard_hooks;
pub mod download_copy_hooks;
pub mod engine_freeze_hooks;
pub mod escalation_hooks;
pub mod event_log_hooks;
pub mod feature_approval_hooks;
pub mod finished_run_hooks;
pub mod gate_hooks;
pub mod gate_write_hooks;
pub mod gm_tree_hooks;
pub mod guard_file_hooks;
pub mod house_style_hooks;
pub mod idle_tests_hooks;
pub mod ledger_hooks;
pub mod main_tree_hooks;
pub mod make_only_hooks;
pub mod measure_hooks;
pub mod new_file_hooks;
pub mod no_branch_hooks;
pub mod no_poll_hooks;
pub mod pair_hooks;
pub mod phase_source_hooks;
pub mod readme_hooks;
pub mod record_edit_gate;
pub mod record_edit_hooks;
pub mod repo_safety_hooks;
pub mod review_round_hooks;
pub mod set_down_hooks;
pub mod shell_check_hooks;
pub mod source_block_hooks;
pub mod stall_watchdog_hooks;
pub mod wakeup_hooks;
pub mod workflow_hooks;
