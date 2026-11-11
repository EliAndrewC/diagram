//! The checks the gate runs over text (feature 449 T065, from `scripts/gates/check-*.py`; `ask:449-T065-scope` says which of the twelve are here). `l7r-gate check <name> ...`; each is one module and records its run.

use std::path::Path;
use std::process::Command;

pub use l7r_gate_tree::checks::*;

mod conflict;
mod file_scale;
mod house_style_delta;
mod partial_citations;
mod question_size;
mod research_pointers;
mod run_plausible;
mod rust_tooling;
mod spec_figures;
mod spec_lint;
mod stale_dirs;
mod tool_signals;

/// What a check answered.
#[derive(Debug, PartialEq, Eq)]
pub(crate) struct Outcome {
    stdout: String,
    stderr: String,
    code: i32,
}

impl Outcome {
    /// A self-test's verdict.
    fn selftest(passed: bool, ok: &str, failed: String) -> Self {
        if passed {
            Self::out(ok.to_owned())
        } else {
            Self::refuse(failed)
        }
    }

    fn out(stdout: String) -> Self {
        Self {
            stdout,
            stderr: String::new(),
            code: 0,
        }
    }

    fn usage(stderr: &str) -> Self {
        Self {
            stdout: String::new(),
            stderr: stderr.to_owned(),
            code: 2,
        }
    }

    fn refuse(stderr: String) -> Self {
        Self {
            stdout: String::new(),
            stderr,
            code: 1,
        }
    }
}

/// `git <args>`'s NUL-separated output, or None where git cannot answer (not a repository).
fn git_z(root: &Path, args: &[&str]) -> Option<Vec<String>> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .ok()
        .filter(|o| o.status.success())?;
    Some(
        String::from_utf8_lossy(&done.stdout)
            .split('\0')
            .filter(|p| !p.is_empty())
            .map(str::to_owned)
            .collect(),
    )
}

/// `text` with each match of `pattern` overwritten by as many spaces as it has characters.
fn blank_matches(pattern: &fancy_regex::Regex, text: &str) -> String {
    pattern
        .replace_all(text, |c: &fancy_regex::Captures<'_>| {
            " ".repeat(c[0].chars().count())
        })
        .into_owned()
}

/// `l7r-gate check <name> [args]`.
pub(crate) fn cli(args: &[String], root: &Path) -> crate::Reply {
    let rest = args.get(1..).unwrap_or(&[]);
    let (tool, outcome) = match args.first().map(String::as_str) {
        Some("file-scale") => (file_scale::USAGE_LOG_TOOL, file_scale::cli(rest)),
        Some("stale-dirs") => (stale_dirs::USAGE_LOG_TOOL, stale_dirs::cli(rest)),
        Some("question-size") => (question_size::USAGE_LOG_TOOL, question_size::cli(rest, root)),
        Some("rust-tooling") => (rust_tooling::USAGE_LOG_TOOL, rust_tooling::cli(rest, root)),
        Some("research-pointers") => (research_pointers::USAGE_LOG_TOOL, research_pointers::cli(rest)),
        Some("house-style-delta") => (house_style_delta::USAGE_LOG_TOOL, house_style_delta::cli(rest)),
        Some("conflict") => (conflict::USAGE_LOG_TOOL, conflict::cli(rest)),
        Some("spec-lint") => (spec_lint::USAGE_LOG_TOOL, spec_lint::cli(rest)),
        Some("run-plausible") => (run_plausible::USAGE_LOG_TOOL, run_plausible::cli(rest, root, &std::env::var("MAKEFLAGS").unwrap_or_default())),
        Some("tool-signals") => (tool_signals::USAGE_LOG_TOOL, tool_signals::cli(rest, root)),
        Some("partial-citations") => (partial_citations::USAGE_LOG_TOOL, partial_citations::cli(rest)),
        Some("needs") => {
            let code = needs(rest.first().map_or("", String::as_str), root);
            return crate::Reply { stdout: String::new(), stderr: String::new(), code };
        }
        _ => return crate::Reply { stdout: String::new(), stderr: "usage: l7r-gate check file-scale | stale-dirs | question-size | rust-tooling | research-pointers | house-style-delta [args]\n".to_owned(), code: 2 },
    };
    crate::stamp::record_for(
        root,
        tool,
        if outcome.code == 0 {
            "passed"
        } else {
            "refused"
        },
    );
    crate::Reply {
        stdout: outcome.stdout,
        stderr: outcome.stderr,
        code: outcome.code,
    }
}

#[cfg(test)]
mod tests;
