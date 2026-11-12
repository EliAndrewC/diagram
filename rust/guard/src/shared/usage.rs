//! The tool-usage log, `<git common dir>/tool-usage.jsonl` (feature 406 T01, D160): one line a run of every tool that leaves no record
//! of its own, read by `make tool-yield`. Ported from `scripts/hooks/lib/usage_log.py` (feature 449 T129): its ONE writer, which the
//! guards, the gate's subcommands and `l7r-gate log usage` / `log goals` (the shell's and Python's door, run by command) all call, where
//! the gate's `stamp::record_for` and the guard's `passes::usage` had each written their own copy of the line.
//!
//! A record never fails its tool: every error is swallowed, as the Python's `except Exception: return` swallowed it.
//!
//! The line is written whole in one `write` on a file opened to append. The Python also took `fcntl.flock` around its write; the lock
//! is not taken here, because an appending write of one line this short is not interleaved with another on a local file system, and
//! the lock is past this toolchain without a process a record (`File::lock` is Rust 1.89; `shared::tool::flock` starts `flock(1)`),
//! which the Makefile's line on every `make` would pay (feature 449 T129, measured in its plan entry).

use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::json;

use super::log::civil;
use super::py_text;
use super::pyjson;

/// The log's file name in the git common directory.
pub const FILE: &str = "tool-usage.jsonl";

/// The git common directory of the repository `root` stands in (`usage_log._common`), or None outside one.
#[must_use]
pub fn common(root: &Path) -> Option<PathBuf> {
    let out = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["rev-parse", "--path-format=absolute", "--git-common-dir"])
        .output()
        .ok()?;
    let text = String::from_utf8_lossy(&out.stdout);
    let dir = py_text::strip(&text);
    (out.status.success() && !dir.is_empty()).then(|| PathBuf::from(dir))
}

/// One run of `tool` recorded in the repository `root` stands in (`usage_log.record`); nothing outside one.
pub fn record(root: &Path, tool: &str, kind: &str, outcome: &str) {
    if let Some(dir) = common(root) {
        append(&dir, tool, kind, outcome);
    }
}

/// A check's exit as its outcome (`usage_log.exited`): `passed` on 0, `refused` on anything else.
#[must_use]
pub fn exited(code: i32) -> &'static str {
    if code == 0 {
        "passed"
    } else {
        "refused"
    }
}

/// One line in `<common>/tool-usage.jsonl`, `json.dumps` of the row as the Python wrote it.
#[expect(clippy::many_single_char_names, reason = "the fields of a date")]
pub fn append(common: &Path, tool: &str, kind: &str, outcome: &str) {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, m, d, h, mi, s) = civil(secs);
    let session = std::env::var("CLAUDE_SESSION_ID").unwrap_or_default();
    let row = json!({"utc": format!("{y:04}-{m:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z"), "tool": tool, "kind": kind, "outcome": outcome, "session": session});
    let line = format!("{}\n", pyjson::dumps(&row, None, true));
    if let Ok(mut file) = std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(common.join(FILE))
    {
        let _ = file.write_all(line.as_bytes());
    }
}

#[cfg(test)]
mod tests {
    use std::path::Path;

    use super::{append, common, exited, record, FILE};
    use crate::shared::checks::testkit::{clone_at, dir};

    #[test]
    fn a_run_leaves_one_line_in_the_common_directory() {
        let root = clone_at("usage");
        std::fs::create_dir_all(root.join("sub")).unwrap();
        record(&root.join("sub"), "planhold-restore", "step", "changed");
        record(&root, "x\u{e9}", "check", exited(1));
        let text = std::fs::read_to_string(root.join(".git").join(FILE)).unwrap();
        let lines: Vec<&str> = text.lines().collect();
        assert_eq!(lines.len(), 2);
        assert!(lines[0].starts_with("{\"utc\": \"") && lines[0].contains("Z\", \"tool\": \"planhold-restore\", \"kind\": \"step\", \"outcome\": \"changed\", \"session\": "));
        assert!(lines[1]
            .contains("\"tool\": \"x\\u00e9\", \"kind\": \"check\", \"outcome\": \"refused\""));
        assert_eq!(exited(0), "passed");
    }

    #[test]
    fn outside_a_repository_or_unwritable_nothing_is_written_and_nothing_fails() {
        let d = dir("usage-none");
        assert!(common(&d).is_none() && common(Path::new("/nonexistent/x")).is_none());
        record(&d, "t", "step", "ran");
        append(&d.join("absent"), "t", "step", "ran");
        assert_eq!(std::fs::read_dir(&*d).unwrap().count(), 0);
    }
}
