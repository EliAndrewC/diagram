//! `l7r-gate measure event-log phase`: the shell's door to the ONE Phase writer (feature 451 T153; the GM 2026-11-22: "we want everything
//! measured so we know where our time goes, especially for compiling, running tests, and generating maps"). Only the checks' wrapper
//! (T05) and `make land` (T06) wrote `Phase` lines, so a hook suite, `make record`, `make quick`, `make preflight` and `make cohort`
//! were invisible to `make where-time`. A recipe or `hookrun.sh` times its own step and hands the spans here, one call for many (a
//! `hooks-test` run's 57 suites are one process after the fan-out, not 57: one call a suite cost 6.9 s on a loaded host, measured
//! 2026-11-20 for `hookrun.sh --jobs`), each written through `phase_row` and `append_row_with`. It feeds the task time breakdown
//! (`make task-time`, 451 T243).
//!
//! ```text
//! l7r-gate measure event-log phase --root <tree> --src <tool> [--make <target>] [--feature <F>] [--task <T>] <step>:<t0>:<t1>:<code>[:<name>[:<log>]]...
//! ```
//!
//! `t0` and `t1` are UTC seconds since the epoch (`date +%s.%N`, bash's `$EPOCHREALTIME`); `--make` defaults to the outermost make above
//! this process (`shared::make::outermost_goal`), as the landing's lines read theirs. `--task` files the lines under that task, where
//! the writer's own chain would read the tree's marks (451 T286: `closing-checks.sh`'s launch line carries its caller's `T=`, as the
//! call's `PreToolUse` line does: of 464 `make closing-checks` calls in 451's log, the Phase lines their session wrote before its next
//! such call named only other tasks after 198, measured 2026-11-27 - in a pool tree the chain read the tree's previous task).

use std::path::Path;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use l7r_shared::env::Reader;
use l7r_shared::guards::event_log_hooks::{append_row_with, phase_row};
use serde_json::Value;

use super::super::reply;
use crate::Reply;

/// The usage.
pub const USAGE: &str = "usage: l7r-gate measure event-log phase --root <tree> --src <tool> [--make <target>] [--feature <F>] [--task <T>] <step>:<t0>:<t1>:<code>[:<name>[:<log>]]...\n";

/// A span read: its step, start, end, exit code, name and kept log.
type Span = (String, SystemTime, SystemTime, i32, String, String);

/// One span's `<step>:<t0>:<t1>:<code>[:<name>[:<log>]]`, the log the rest after the fifth colon: a failed hook suite's kept log,
/// relative to the common git directory (451 T414), which `hookrun.sh` names without a colon or a space.
fn span(word: &str) -> Option<Span> {
    let mut parts = word.splitn(6, ':');
    let step = parts.next().filter(|s| !s.is_empty())?.to_owned();
    let at = |t: Option<&str>| {
        let s: f64 = t?.parse().ok()?;
        (s.is_finite() && s >= 0.0).then(|| UNIX_EPOCH + Duration::from_secs_f64(s))
    };
    let (t0, t1) = (at(parts.next())?, at(parts.next())?);
    let code = parts.next()?.parse().ok()?;
    let mut rest = || parts.next().unwrap_or("").to_owned();
    let (name, log) = (rest(), rest());
    Some((step, t0, t1, code, name, log))
}

/// The command: each span a line, exit 0; a span it cannot read, or no `--root` or `--src`, the usage and exit 2, nothing written.
pub fn cli(args: &[String], env: &Reader) -> Reply {
    let (mut root, mut src, mut make, mut feature, mut task, mut spans) =
        (None, None, None, None, None, Vec::new());
    let mut it = args.iter();
    while let Some(a) = it.next() {
        let slot = match a.as_str() {
            "--root" => &mut root,
            "--src" => &mut src,
            "--make" => &mut make,
            "--feature" => &mut feature,
            "--task" => &mut task,
            word => {
                let Some(s) = span(word) else {
                    return reply(
                        String::new(),
                        format!("phase: cannot read {word:?}\n{USAGE}"),
                        2,
                    );
                };
                spans.push(s);
                continue;
            }
        };
        *slot = it.next().cloned();
    }
    let (Some(root), Some(src)) = (root, src) else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let make = make.unwrap_or_else(|| {
        l7r_shared::make::outermost_goal(Path::new("/proc"), std::process::id()).unwrap_or_default()
    });
    let root = Path::new(&root);
    for (step, t0, t1, code, name, log) in spans {
        let mut row = phase_row(&src, &step, (t0, t1), code, &make, root);
        for (key, value) in [
            ("name", name),
            ("log", log),
            ("task", task.clone().unwrap_or_default()),
        ] {
            if !value.is_empty() {
                row.insert(key.into(), Value::from(value));
            }
        }
        let _ = append_row_with(root, feature.as_deref(), row, env);
    }
    reply(String::new(), String::new(), 0)
}

#[cfg(test)]
mod tests;
