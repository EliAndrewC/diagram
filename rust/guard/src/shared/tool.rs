//! Asking a tool the guards consult (plan T006 decision (a)): a program run in a directory, its stdin given, its exit code and its
//! stdout and stderr kept - the shell's `$(...)`, which strips the trailing newlines, and its `$?`. A program that cannot start
//! answers -1 with nothing, as a guard's `2>/dev/null || true` did.

use std::io::Write;
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

#[cfg(test)]
mod tests {
    use std::path::Path;
    use std::time::Duration;

    use super::{ask, within};

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
