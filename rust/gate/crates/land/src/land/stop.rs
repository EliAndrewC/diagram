//! A STOPPED LANDING STOPS ITS RUNS (405 T79): a landing stopped by hand left its gate and the cohort beside it running as orphans
//! (batch 6). On TERM the landing ignores a second TERM, ends the process group of every gate and cohort it started ([`hold`]), then its
//! own group - `make done` and the other runs it waits on run there - and exits 143, as `land.py`'s `_stopped` did. `make land-stop`
//! ([`stop`]) sends that TERM to this tree's landing.
//!
//! The catch is the guard's one INT and TERM handler (`l7r_guard::shared::tempdir::before_exit`), which runs [`stopped`] first and then
//! removes the process's scratch directories and exits as the signal would: a handler of the land's own was replaced the moment an
//! in-process call made its first `TempDir` (the differential's stopped landing, 2026-11-12: exit 143 with its gate left running). An INT
//! (a Ctrl-C) stops nothing more than the guard's handler does: `land.py`'s `KeyboardInterrupt` ran no `_stopped` either.
//!
//! The crate's one use of `unsafe`: `signal(2)` and `kill(2)` from the C library std already links, there being no safe form of them in
//! std.

use std::path::Path;
use std::sync::Mutex;

/// The process groups this landing started and still runs: its gates and its cohort.
static RUNNING: Mutex<Vec<u32>> = Mutex::new(Vec::new());

const SIGTERM: i32 = 15;
/// `SIG_IGN`.
const IGNORE: usize = 1;

extern "C" {
    fn signal(signum: i32, handler: usize) -> usize;
    fn kill(pid: i32, sig: i32) -> i32;
}

/// The process group `pgid` (a child started in its own) sent TERM; false where none is left to signal.
pub(super) fn kill_group(pgid: u32) -> bool {
    let Ok(group) = i32::try_from(pgid) else {
        return false;
    };
    // SAFETY: kill(2) with a negative pid signals that process group, and only that
    unsafe { kill(-group, SIGTERM) == 0 }
}

/// A process group the landing started, stopped with it.
pub(super) fn hold(pgid: u32) {
    if let Ok(mut running) = RUNNING.lock() {
        running.push(pgid);
    }
}

/// A process group that has ended, or been stopped.
pub(super) fn release(pgid: u32) {
    if let Ok(mut running) = RUNNING.lock() {
        running.retain(|p| *p != pgid);
    }
}

/// TERM caught for the rest of the process.
pub(super) fn catch_term() {
    l7r_guard::shared::tempdir::before_exit(stopped);
}

/// `_stopped`, on TERM: TERM ignored from here, every held group stopped, then the landing's own group (the gate's `make` and every run
/// it waits on); the guard's handler then exits 143.
fn stopped(signum: i32) {
    if signum != SIGTERM {
        return;
    }
    // SAFETY: ignoring a signal installs no handler
    unsafe {
        signal(SIGTERM, IGNORE);
    }
    stop_groups();
}

/// Every held group, then this process's own, sent TERM.
fn stop_groups() {
    let held = RUNNING.lock().map(|r| r.clone()).unwrap_or_default();
    for pgid in held {
        kill_group(pgid);
    }
    // SAFETY: kill(2) with pid 0 signals the caller's own process group
    unsafe {
        kill(0, SIGTERM);
    }
}

/// This tree's running landings: the `l7r-gate land` processes whose working directory is `root`, never this one - nor the `sh -c`
/// recipe shell or `make` above it, whose command lines name the command too (405 T90: a SIGTERM aimed at the first process match hit
/// the recipe shell, so the landing's cleanup never ran and its gate ran on). `land.py` matched a python process running
/// `scripts/land.py`; the Rust land is the binary itself (`l7r-gate.sh` execs it), so it matches that (feature 449 T121).
pub(super) fn landing_pids(root: &Path, proc: &Path) -> Vec<i32> {
    let me = std::process::id();
    let root = root.canonicalize().unwrap_or(root.to_path_buf());
    let mut out: Vec<i32> = Vec::new();
    for entry in std::fs::read_dir(proc).into_iter().flatten().flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        let Ok(pid) = name.parse::<u32>() else {
            continue;
        };
        if pid == me || !name.chars().all(|c| c.is_ascii_digit()) {
            continue;
        }
        let Ok(cmdline) = std::fs::read(entry.path().join("cmdline")) else {
            continue;
        };
        let cwd = entry.path().join("cwd");
        let cwd = cwd.canonicalize().unwrap_or(cwd);
        let args: Vec<&[u8]> = cmdline.split(|b| *b == 0).collect();
        let program = String::from_utf8_lossy(args[0]);
        let is_gate = program.rsplit('/').next() == Some("l7r-gate");
        if is_gate && args.get(1) == Some(&&b"land"[..]) && cwd == root {
            out.extend(i32::try_from(pid));
        }
    }
    out.sort_unstable();
    out
}

/// `make land-stop`: TERM to this tree's landing, whose handler stops its gate and cohort ([`stopped`]).
///
/// # Errors
/// A landing that ended between the look and the signal, as `os.kill` raised `ProcessLookupError`.
pub(super) fn stop(root: &Path, proc: &Path, say: &mut dyn FnMut(&str)) -> Result<i32, String> {
    let pids = landing_pids(root, proc);
    for pid in &pids {
        // SAFETY: kill(2) on one process id
        if unsafe { kill(*pid, SIGTERM) } != 0 {
            return Err(format!(
                "ProcessLookupError: [Errno 3] No such process: {pid}"
            ));
        }
    }
    let shown: Vec<String> = pids.iter().map(ToString::to_string).collect();
    say(&if pids.is_empty() {
        format!("land-stop: no landing running in {}", root.display())
    } else {
        format!("land-stop: stopped {}", shown.join(", "))
    });
    Ok(0)
}

#[cfg(test)]
mod tests;
