//! A run ends at its program's exit, not at the end of its output pipe (feature 451 T364, `drain.rs`).

use super::*;

/// A program that leaves a `sleep 5` holding its stdout: the run returns near the program's exit with every byte it wrote, and names
/// the process that still holds the pipe; the 5 s the pipe stays open is not waited (measured 2026-11-26: binary exit 2.0 s, pipe end
/// 5.2 s).
#[test]
fn a_run_ends_at_the_exit_though_a_process_it_left_holds_the_pipe() {
    let began = std::time::Instant::now();
    let ran = run(
        "sh",
        &own(&["-c", "sleep 5 & echo \"left $!\"; echo said >&2"]),
        &BTreeMap::new(),
    );
    let took = began.elapsed();
    let pid = ran.stdout.trim().trim_start_matches("left ").to_owned();
    let _ = Command::new("kill").arg(&pid).status();
    assert!(took < std::time::Duration::from_secs(2), "{took:?}");
    assert!(ran.code == 0 && ran.stdout.starts_with("left ") && ran.stderr.starts_with("said\n"));
    let held = format!("pid {pid} (sleep 5)");
    assert!(ran.stderr.contains(super::super::drain::HELD) && ran.stderr.contains(&held));
}

/// What a program writes past a pipe's buffer, and its exit code, all come back, and a run whose pipes end names nothing.
#[test]
fn a_run_reads_past_the_pipe_s_buffer_and_keeps_the_exit_code() {
    let ran = run(
        "sh",
        &own(&[
            "-c",
            "head -c 300000 /dev/zero | tr '\\0' x; echo e >&2; exit 3",
        ]),
        &BTreeMap::new(),
    );
    assert!(ran.code == 3 && ran.stdout.len() == 300_000 && ran.stderr == "e\n");
}

/// A run killed by a signal has no exit code, and is a failure.
#[test]
fn a_run_killed_by_a_signal_fails() {
    let ran = run("sh", &own(&["-c", "kill -9 $$"]), &BTreeMap::new());
    assert_eq!(ran.code, 1);
}

/// A pipe still open past `DRAIN` that no other process holds is a late reader, never a leak: the run waits for its end, every byte
/// read, and names nothing.
#[test]
fn a_late_reader_with_no_holder_is_waited_for_not_cut() {
    let (out, err) = (
        super::super::drain::late_pipe(std::time::Duration::from_millis(400), "late\n"),
        super::super::drain::late_pipe(std::time::Duration::ZERO, ""),
    );
    let (stdout, stderr) = super::super::drain::ended("x", &out, &err);
    assert!(stdout == "late\n" && stderr.is_empty());
}

/// A child another thread of this process has forked and not yet exec'd holds a copy of every descriptor this process has, the late
/// pipe's ends among them, close-on-exec or not: it is no holder of the pipe, and the late reader is still waited for, not cut (451
/// T535; the batch gate of 2026-11-27 19:10Z failed the test above once so). The child here parks in that window past `DRAIN`, and
/// says when it is there.
#[test]
fn a_late_reader_is_not_cut_for_a_child_of_this_process_between_its_fork_and_its_exec() {
    use std::io::{Read as _, Write as _};
    use std::os::unix::process::CommandExt as _;
    let (out, err) = (
        super::super::drain::late_pipe(std::time::Duration::from_millis(400), "late\n"),
        super::super::drain::late_pipe(std::time::Duration::ZERO, ""),
    );
    let (mut there, told) = std::io::pipe().unwrap();
    let forking = std::thread::spawn(move || {
        let (mut child, park) = (Command::new("true"), std::time::Duration::from_secs(1));
        // SAFETY: the closure runs in the forked child before its exec and only writes a byte and sleeps, write(2) and nanosleep(2);
        // on one line, since what runs only in the child is never counted by coverage
        unsafe {
            child.pre_exec(move || (&told).write_all(b"x").map(|()| std::thread::sleep(park)))
        };
        child.status()
    });
    let mut byte = [0u8; 1];
    there.read_exact(&mut byte).unwrap();
    let (stdout, stderr) = super::super::drain::ended("x", &out, &err);
    assert!(forking.join().unwrap().unwrap().success());
    assert!(stdout == "late\n" && stderr.is_empty(), "{stderr}");
}

/// A crate whose test run left a process on its output says so, is red for it (451 T363, `left.rs`), and the run does not wait for it.
#[test]
fn a_crate_whose_run_left_a_holder_names_it_and_is_red() {
    let (root, _, _) = two_crates();
    // the holder left by the test call alone, and alive well past the bound: the run waits for none of it
    let body = "case \"$*\" in \"test --quiet\"*) sleep 30 & echo $! >> \"$(dirname \"$0\")/left\";; esac\necho 'test result: ok. 1 passed'";
    let world = world_with(&root, body);
    let began = std::time::Instant::now();
    let done = answer(&world, "test", &["rust/a".to_owned()], false);
    let took = began.elapsed();
    let left = std::fs::read_to_string(world.target.join("left")).unwrap();
    let _ = Command::new("kill").args(left.split_whitespace()).status();
    // the bound is the holder's 30 s, not a speed: a coverage build on a loaded host took past 2 s here (2026-11-27)
    assert_eq!(done.code, 1);
    assert!(took < std::time::Duration::from_secs(15), "{took:?}");
    assert!(done.stderr.contains("rust-checks: HELD: ") && done.stderr.contains("(sleep 30)"));
}
