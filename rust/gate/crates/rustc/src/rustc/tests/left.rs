//! A crate's test run that leaves a process behind fails by name, and the process is ended (feature 451 T363, `left.rs`).

use super::*;

/// Is process `pid` still running (not gone, not a zombie)?
fn running(pid: &str) -> bool {
    std::fs::read_to_string(format!("/proc/{pid}/stat")).is_ok_and(|s| {
        s.rsplit_once(") ")
            .is_some_and(|(_, r)| !r.starts_with('Z'))
    })
}

/// Has process `pid` ended within about 10 s (a SIGKILL lands at once, but the kernel's exit and the reap are not instant on a loaded
/// machine)? Polled, never a fixed sleep: a test's own GUESS cap.
fn ends(pid: &str) -> bool {
    (0..200u64).any(|i| {
        std::thread::sleep(std::time::Duration::from_millis(50 * i.min(1)));
        !running(pid)
    })
}

/// A test run whose stand-in starts a `sleep` that holds none of its output and does not wait on it: the crate is red, the line names
/// the process, and the process has been ended when the run returns.
#[test]
fn a_test_run_that_leaves_a_process_behind_fails_by_name_and_the_process_is_ended() {
    let (root, _, _) = two_crates();
    let body = "case \"$*\" in \"test --quiet\"*) sleep 46.7 </dev/null >/dev/null 2>&1 & echo $! >> \"$(dirname \"$0\")/left\";; esac\necho 'test result: ok. 1 passed'";
    let world = world_with(&root, body);
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    let left = std::fs::read_to_string(world.target.join("left")).unwrap();
    let pid = left.trim().to_owned();
    // this test's own process is running: the reader's every line taken, whatever the kill's timing
    assert!(running(&std::process::id().to_string()));
    let ended = ends(&pid);
    let quiet = std::process::Stdio::null();
    let _ = Command::new("kill").arg(&pid).stderr(quiet).status();
    assert_eq!(done.code, 1);
    assert!(ended, "pid {pid} was left running");
    let named = format!("pid {pid} (sleep 46.7)");
    let (said, line) = (
        &done.stderr,
        "rust-checks: the tests left 1 process running",
    );
    assert!(said.contains(line) && said.contains(&named), "{said}");
}

/// A run that ends everything it started leaves nothing to name.
#[test]
fn a_test_run_that_waits_on_its_child_is_green() {
    let (root, _, _) = two_crates();
    let body = "case \"$*\" in \"test --quiet\"*) sleep 0.01 & wait $!;; esac\necho 'test result: ok. 1 passed'";
    let world = world_with(&root, body);
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    assert_eq!(done.code, 0, "{}", done.stderr);
}

/// `marked` over a fake `/proc`: a process holding the run's `TMPDIR` is named; a zombie, one gone mid-read, one whose `TMPDIR` only
/// starts with the run's, this process, and an entry that is no pid are not.
#[test]
fn the_left_processes_are_read_from_proc_by_the_run_s_tmpdir() {
    use super::super::left::marked;
    let dir = scratch("left-proc");
    let proc = dir.join("proc");
    let fake = |pid: &str, state: &str, tmp: &str| {
        let at = proc.join(pid);
        std::fs::create_dir_all(&at).unwrap();
        let stat = format!("{pid} (s h) {state} 1 {}0\n", "0 ".repeat(18));
        std::fs::write(at.join("stat"), stat).unwrap();
        std::fs::write(at.join("environ"), format!("A=1\0TMPDIR={tmp}\0")).unwrap();
        std::fs::write(at.join("cmdline"), "sleep\x005\0").unwrap();
    };
    fake("30", "S", "/t/run");
    fake("31", "Z", "/t/run");
    fake("32", "S", "/t/run-other");
    fake("33", "S", "/t/run");
    std::fs::remove_file(proc.join("33/stat")).unwrap();
    fake("34", "S", "/t/run");
    std::fs::create_dir_all(proc.join("self")).unwrap();
    let found = marked(&proc, Path::new("/t/run"), 34);
    assert_eq!(found, [(30, "pid 30 (sleep 5)".to_owned())]);
}
