//! The checks the gate runs over text (feature 449 T065, from `scripts/gates/check-*.py`; `ask:449-T065-scope` says which of the twelve are here). `l7r-gate check <name> ...`; each is one module and records its run.

use std::path::Path;
use std::process::Command;

pub use l7r_gate_core::checks::*;

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

/// Does `check`, one of the four gated on their delta (three still Python, `partial-citations` in Rust since T80), read this path? Each set is that check's own, from its source and what it
/// imports. An unknown name reads everything: it runs.
fn reads(check: &str, path: &str) -> bool {
    let python = has_ext(path, "py");
    let under = |trees: &[&str]| trees.iter().any(|t| path.starts_with(t));
    let own = |name: &str| path == format!("scripts/gates/check-{name}.py");
    match check {
        "duplicate-defs" => {
            own(check)
                || (python && under(&["l7r/", "tests/", "pool/", "legacy-hand-authored-pool/"]))
        }
        "function-cap" => {
            own(check)
                || path == "pyproject.toml"
                || (python && under(&["l7r/", "tests/", "scripts/", "pool/"]))
        }
        "partial-citations" => {
            under(&[
                "research/sources/010-works-cited/",
                "research/archive/",
                "rust/gate/src/record/downloads",
            ]) || (path.starts_with("research/questions/") && path.ends_with(".notes.html"))
                || [
                    "research/partial-confirmations.jsonl",
                    "research/source-access.json",
                    "research/to-download.md",
                    "rust/gate/src/checks/partial_citations.rs",
                    "rust/gate/src/record/access_tags.rs",
                ]
                .contains(&path)
        }
        // a class's `Entry:` is parsed from its modal text
        "entry-headings" => {
            own(check)
                || under(&[
                    "research/questions/",
                    "l7r/diagram/interactive/assets/modals/",
                ])
                || (python && path.starts_with("l7r/diagram/interactive/"))
        }
        _ => true,
    }
}

/// Does this change hold a file `check` reads (`ask:449-T065-scope`: those that stay Python never start on a change that holds
/// none of what they read, so a one-line Rust edit starts none)? Exit 0 to run it, and when there is no base to compare with.
/// Does the change hold a file this retained Python check reads?
pub(crate) fn needs_run(check: &str, root: &Path) -> bool {
    needs(check, root).code == 0
}

fn needs(check: &str, root: &Path) -> Outcome {
    let base = git_text(root, &["merge-base", "HEAD", "origin/main"]);
    if base.trim().is_empty() {
        return Outcome::out(String::new()); // no base to compare with: cannot tell, so it runs
    }
    let mut names = git_text(root, &["diff", "--name-only", base.trim()]);
    names += &git_text(root, &["ls-files", "--others", "--exclude-standard"]);
    Outcome {
        stdout: String::new(),
        stderr: String::new(),
        code: i32::from(!names.lines().any(|p| reads(check, p))),
    }
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
            let o = needs(rest.first().map_or("", String::as_str), root);
            return crate::Reply { stdout: o.stdout, stderr: o.stderr, code: o.code };
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
