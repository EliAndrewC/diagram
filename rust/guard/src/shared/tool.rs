//! Asking a tool the guards consult (plan T006 decision (a)): a program run in a directory, its stdin given, its exit code and its
//! stdout and stderr kept - the shell's `$(...)`, which strips the trailing newlines, and its `$?`. A program that cannot start
//! answers -1 with nothing, as a guard's `2>/dev/null || true` did.

use std::io::Write;
use std::path::Path;
use std::process::{Command, Stdio};

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

#[cfg(test)]
mod tests {
    use std::path::Path;

    use super::ask;

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
