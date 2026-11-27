//! A TEST RUN LEAVES NO PROCESS BEHIND (feature 451 T363, found by T340): rust/guard's stand-in sessions left nine `sleep 5`
//! processes a run, alive as long as each stand-in was, and nothing said so; T364 (`drain.rs`) names only a process that holds the
//! run's output pipe. The leak pin (`leak_checked`) runs a crate's tests with a `TMPDIR` of the run's own, and every process the tests
//! start inherits it, wherever it is reparented once its parent exits. So once the run is over, every process still alive whose
//! environment holds exactly that `TMPDIR` is one the tests left: named, ended (SIGKILL), and the crate failed, as a file left in the
//! directory fails it. WHY the environment, not a process group: `land`'s stop sends TERM to the process groups it holds
//! (`land/stop.rs`), and a test run in a group of its own would escape that; a test process that clears its environment escapes this
//! one, and none does. A zombie is ended already and is not named; the environment is read from `/proc/<pid>/environ` as it was at
//! the process's exec.

use std::path::Path;
use std::time::Duration;

use super::alive::stat;

/// How long a process found left gets to end on its own before it is named, read once more after: a GUESS knob. Slack for a child a
/// test has signalled and not yet seen end on a loaded machine. WHY 1 s: a falsely red batch gate costs about ten minutes and an
/// arbiter round, and the machine's load reached 37 on 2026-11-27, where 100 ms is thin; it is waited only where something was found,
/// never on a clean run, so a real leak pays it and a clean run does not (451 T363, the coordinating session's call, 2026-11-27).
const GRACE: Duration = Duration::from_secs(1);

/// SIGKILL: a process a test left is ended outright, since nothing of it is wanted.
const SIGKILL: i32 = 9;

extern "C" {
    fn kill(pid: i32, sig: i32) -> i32;
}

/// Each process of `proc` but `me`, alive and not a zombie, whose environment holds `TMPDIR=<tmp>` exactly, as its pid and
/// `pid N (its command line)`, in pid order.
pub(super) fn marked(proc: &Path, tmp: &Path, me: u32) -> Vec<(u32, String)> {
    let want = format!("TMPDIR={}", tmp.display());
    let mut found = Vec::new();
    for entry in std::fs::read_dir(proc).into_iter().flatten().flatten() {
        let Ok(pid) = entry.file_name().to_string_lossy().parse::<u32>() else {
            continue;
        };
        let at = entry.path();
        let environ = std::fs::read(at.join("environ")).unwrap_or_default();
        let holds = pid != me && environ.split(|b| *b == 0).any(|w| w == want.as_bytes());
        let state = std::fs::read_to_string(at.join("stat"))
            .ok()
            .and_then(|s| stat(&s))
            .map(|s| s.0);
        if holds && state.is_some_and(|s| s != "Z") {
            let line = std::fs::read(at.join("cmdline")).unwrap_or_default();
            let words: Vec<String> = line
                .split(|b| *b == 0)
                .filter(|w| !w.is_empty())
                .map(|w| String::from_utf8_lossy(w).into_owned())
                .collect();
            found.push((pid, format!("pid {pid} ({})", words.join(" "))));
        }
    }
    found.sort();
    found
}

/// The processes the run with `TMPDIR` `tmp` left, named and ended: those found, and found again after `GRACE`.
pub(super) fn ended(tmp: &Path) -> Vec<String> {
    let proc = Path::new("/proc");
    let me = std::process::id();
    let first = marked(proc, tmp, me);
    if first.is_empty() {
        return Vec::new();
    }
    std::thread::sleep(GRACE);
    let left: Vec<(u32, String)> = marked(proc, tmp, me)
        .into_iter()
        .filter(|p| first.contains(p))
        .collect();
    for (pid, _) in &left {
        if let Ok(pid) = i32::try_from(*pid) {
            // SAFETY: kill(2) with a positive pid signals that one process, one the run's own tests started
            let _ = unsafe { kill(pid, SIGKILL) };
        }
    }
    left.into_iter().map(|p| p.1).collect()
}
