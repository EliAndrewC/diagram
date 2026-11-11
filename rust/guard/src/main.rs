//! `l7r-guard`: the guards' one process (feature 449 phase 1) - `lib::cli` decides; this prints its reply and exits with its code.

use std::io::Read;

use l7r_guard::shared::tempdir::TempDir;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut stdin = String::new();
    if !matches!(
        args.first().map(String::as_str),
        Some(
            "--version"
                | "--self-check"
                | "--idle-tests"
                | "--agent-stall"
                | "--escalation"
                | "--review-round"
                | "--stall-watchdog"
                | "--scratch-sweep"
                | "--finished-run"
                | "permit"
                | "dropped"
                | "deps"
                | "trace"
                | "bench"
        )
    ) {
        let _ = std::io::stdin().read_to_string(&mut stdin);
    }
    let sandbox = (args.first().map(String::as_str) == Some("--self-check")).then(sandbox);
    let reply = l7r_guard::cli(&args, &stdin, &l7r_guard::guards());
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    // `exit` runs no destructor: the self-check's directory goes first (feature 449 T101)
    drop(sandbox);
    std::process::exit(reply.code);
}

/// THE SELF-CHECK TOUCHES NOTHING (T012, 2026-11-08): it runs every guard on a fixed input, and the event log wrote six real lines
/// into the log of the tree the rebuild stood in - so it runs from a fresh empty directory, every guard's log and state there.
fn sandbox() -> TempDir {
    let dir = TempDir::new("guard-self-check");
    let _ = std::env::set_current_dir(&dir);
    for k in [
        "GUARD_LOG_DIR",
        "L7R_EVENTS_DIR",
        "GATE_STATE_DIR",
        "MEASURE_STATE_DIR",
    ] {
        std::env::set_var(k, dir.path());
    }
    std::env::set_var("HOME", dir.path());
    std::env::set_var("L7R_SELF_CHECK", "1"); // no guard starts a daemon from here (T016 decision (c))
    dir
}
