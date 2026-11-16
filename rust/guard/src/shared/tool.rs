//! Asking a tool the guards consult (plan T006 decision (a)): a program run in a directory, its stdin given, its exit code and its
//! stdout and stderr kept - the shell's `$(...)`, which strips the trailing newlines, and its `$?`. A program that cannot start
//! answers -1 with nothing, as a guard's `2>/dev/null || true` did.

use std::fs::File;
use std::io::{Read, Write};
use std::os::unix::process::CommandExt;
use std::path::Path;
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

/// What a tool answered.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Said {
    pub code: i32,
    pub out: String,
    pub err: String,
}

impl Said {
    /// Its exit was 0.
    #[must_use]
    pub fn ok(&self) -> bool {
        self.code == 0
    }
}

/// Run `program args` in `dir`, `stdin` written to it.
#[must_use]
pub fn ask(dir: &Path, program: &str, args: &[&str], stdin: &str) -> Said {
    let Ok(mut child) = Command::new(program)
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
    else {
        return Said {
            code: -1,
            ..Said::default()
        };
    };
    if let Some(mut pipe) = child.stdin.take() {
        let _ = pipe.write_all(stdin.as_bytes());
    }
    let text = |b: &[u8]| String::from_utf8_lossy(b).trim_end_matches('\n').to_owned();
    child.wait_with_output().map_or(
        Said {
            code: -1,
            ..Said::default()
        },
        |done| Said {
            code: done.status.code().unwrap_or(-1),
            out: text(&done.stdout),
            err: text(&done.stderr),
        },
    )
}

/// Whether `program args`, run quiet in `dir`, exits 0 within `limit` - `timeout <limit> program args >/dev/null 2>&1`, its own
/// process group sent TERM at the limit as `timeout` sends it, without `timeout`'s own start (106 ms a call against 1 ms, measured
/// 2026-11-08 on `sh -c 'exit 1'`, five runs each; T013).
#[must_use]
pub fn within(dir: &Path, program: &str, args: &[&str], limit: Duration) -> bool {
    let Ok(mut child) = Command::new(program)
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .process_group(0)
        .spawn()
    else {
        return false;
    };
    let start = Instant::now();
    loop {
        if let Ok(Some(done)) = child.try_wait() {
            return done.success();
        }
        if start.elapsed() >= limit {
            let _ = ask(
                dir,
                "kill",
                &["-TERM", "--", &format!("-{}", child.id())],
                "",
            );
            let _ = child.wait();
            return false;
        }
        std::thread::sleep(Duration::from_millis(1));
    }
}

/// [`ask`] with no stdin and a limit, past which the program is killed and what it said so far is its answer, its code -1
/// (`subprocess.run(timeout=)`'s use here, without coreutils `timeout`'s 100 ms a call, measured in T013).
#[must_use]
pub fn ask_within(dir: &Path, program: &str, args: &[&str], limit: Duration) -> Said {
    let Ok(mut child) = Command::new(program)
        .args(args)
        .current_dir(dir)
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
    else {
        return Said {
            code: -1,
            ..Said::default()
        };
    };
    let out = collect(child.stdout.take());
    let err = collect(child.stderr.take());
    let start = Instant::now();
    let code = loop {
        if let Ok(Some(done)) = child.try_wait() {
            break done.code().unwrap_or(-1);
        }
        if start.elapsed() >= limit {
            let _ = child.kill();
            let _ = child.wait();
            break -1;
        }
        std::thread::sleep(Duration::from_millis(1));
    };
    Said {
        code,
        out: out.join().unwrap_or_default(),
        err: err.join().unwrap_or_default(),
    }
}

/// A pipe read to its end on a thread of its own, so that a full pipe cannot stall the wait on its writer.
fn collect<P: Read + Send + 'static>(pipe: Option<P>) -> std::thread::JoinHandle<String> {
    std::thread::spawn(move || {
        let mut out = Vec::new();
        if let Some(mut p) = pipe {
            let _ = p.read_to_end(&mut out);
        }
        String::from_utf8_lossy(&out)
            .trim_end_matches('\n')
            .to_owned()
    })
}

/// `flock <mode> 0` on an open file handed over as stdin: the lock belongs to that open file, which the caller holds, as a shell's
/// fd 9 did (`File::try_lock` is past this toolchain, T014 decision (b)).
#[must_use]
pub fn flock(lock: &File, mode: &str) -> bool {
    lock.try_clone().is_ok_and(|f| {
        Command::new("flock")
            .args([mode, "0"])
            .stdin(f)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .is_ok_and(|s| s.success())
    })
}

/// `flock` on the lock file at `path`, polled every 20 ms so a hung holder is a refusal rather than a hang: the open file holding it
/// (the lock lasts as long as it does), or none when `timeout` seconds passed first. Its directory is made, the file opened `0o644`, as
/// `claim-feature.py`'s, `reserve-prefix.py`'s and `sources.py`'s locks did; moved here from the gate's `core::record::repo` by feature
/// 449 T145, so the attempts log the blocked-fetch guard writes in process takes the same lock (one copy, FR-003).
///
/// # Errors
///
/// The directory cannot be made or the file opened: what the Python's `mkdir` or `os.open` raised.
pub fn flock_within(path: &Path, timeout: f64) -> std::io::Result<Option<File>> {
    use std::os::unix::fs::OpenOptionsExt as _;
    use std::time::Instant;
    std::fs::create_dir_all(path.parent().unwrap_or(Path::new(".")))?;
    let file = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .mode(0o644)
        .open(path)?;
    // `time.monotonic() + timeout`: a negative timeout a deadline already passed; NaN, or one past what an `Instant` holds (infinity), a
    // deadline the Python's comparison never reached
    let deadline = if timeout.is_nan() {
        None
    } else {
        Duration::try_from_secs_f64(timeout.max(0.0))
            .ok()
            .and_then(|d| Instant::now().checked_add(d))
    };
    while !flock(&file, "-n") {
        if deadline.is_some_and(|d| Instant::now() >= d) {
            return Ok(None);
        }
        std::thread::sleep(Duration::from_millis(20));
    }
    Ok(Some(file))
}

#[cfg(test)]
mod tests {
    use std::path::Path;
    use std::time::Duration;

    use super::{ask, ask_within, within};

    #[test]
    fn a_tool_asked_within_a_limit_answers_or_is_killed() {
        let limit = Duration::from_secs(5);
        let said = ask_within(
            Path::new("/"),
            "sh",
            &["-c", "echo out; echo err >&2; exit 3"],
            limit,
        );
        assert_eq!(
            (said.code, said.out.as_str(), said.err.as_str()),
            (3, "out", "err")
        );
        assert_eq!(
            ask_within(Path::new("/"), "/no/such/program", &[], limit).code,
            -1
        );
        assert_eq!(
            ask_within(Path::new("/"), "sleep", &["5"], Duration::from_millis(5)).code,
            -1
        );
    }

    #[test]
    fn a_quiet_tool_is_given_its_limit_and_no_more() {
        let limit = Duration::from_secs(5);
        assert!(within(Path::new("/"), "true", &[], limit));
        assert!(!within(Path::new("/"), "false", &[], limit));
        assert!(!within(Path::new("/"), "/no/such/program", &[], limit));
        assert!(!within(
            Path::new("/"),
            "sleep",
            &["5"],
            Duration::from_millis(20)
        ));
    }

    #[test]
    fn a_tool_answers_its_code_and_output_and_one_that_cannot_start_answers_nothing() {
        let said = ask(
            Path::new("/"),
            "sh",
            &["-c", "cat; echo err >&2; exit 3"],
            "in\n\n",
        );
        assert_eq!(
            (said.code, said.out.as_str(), said.err.as_str(), said.ok()),
            (3, "in", "err", false)
        );
        assert!(ask(Path::new("/"), "true", &[], "").ok());
        assert_eq!(ask(Path::new("/"), "/no/such/program", &[], "").code, -1);
    }
}
