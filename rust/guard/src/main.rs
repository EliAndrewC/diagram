//! `l7r-guard`: the guards' one process (feature 449 phase 1) - `lib::cli` decides; this prints its reply and exits with its code.

use std::io::Read;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut stdin = String::new();
    if !matches!(
        args.first().map(String::as_str),
        Some("--version" | "--self-check" | "--idle-tests")
    ) {
        let _ = std::io::stdin().read_to_string(&mut stdin);
    }
    if args.first().map(String::as_str) == Some("--self-check") {
        sandbox();
    }
    let reply = l7r_guard::cli(&args, &stdin, &l7r_guard::guards());
    print!("{}", reply.stdout);
    eprint!("{}", reply.stderr);
    std::process::exit(reply.code);
}

/// THE SELF-CHECK TOUCHES NOTHING (T012, 2026-11-08): it runs every guard on a fixed input, and the event log wrote six real lines
/// into the log of the tree the rebuild stood in - so it runs from a fresh empty directory, every guard's log and state there.
fn sandbox() {
    let dir = std::env::temp_dir().join(format!("l7r-guard-self-check-{}", std::process::id()));
    let _ = std::fs::create_dir_all(&dir);
    let _ = std::env::set_current_dir(&dir);
    for k in [
        "GUARD_LOG_DIR",
        "L7R_EVENTS_DIR",
        "GATE_STATE_DIR",
        "MEASURE_STATE_DIR",
    ] {
        std::env::set_var(k, &dir);
    }
    std::env::set_var("HOME", &dir);
}
