//! The checks the gate runs over text (feature 449 T065, from `scripts/gates/check-*.py`; `ask:449-T065-scope` says which of the twelve are here). `l7r-gate check <name> ...`; each is one module and records its run.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicUsize, Ordering};

mod file_scale;
mod house_style_delta;
mod moves;
mod question_size;
mod research_pointers;
mod rust_tooling;
mod stale_dirs;

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

/// `git <args>`'s text; empty where it fails, as the Python's unchecked calls read it.
fn git_text(root: &Path, args: &[&str]) -> String {
    let done = Command::new("git").arg("-C").arg(root).args(args).output();
    done.ok()
        .filter(|o| o.status.success())
        .map_or_else(String::new, |o| {
            String::from_utf8_lossy(&o.stdout).into_owned()
        })
}

/// A scratch directory of this process.
fn scratch(tag: &str) -> PathBuf {
    static SEQ: AtomicUsize = AtomicUsize::new(0);
    let dir = std::env::temp_dir().join(format!(
        "l7r-gate-check-{tag}-{}-{}",
        std::process::id(),
        SEQ.fetch_add(1, Ordering::Relaxed)
    ));
    let _ = std::fs::remove_dir_all(&dir);
    let _ = std::fs::create_dir_all(&dir);
    dir
}

/// Python's `str.splitlines`: a form feed and the Unicode line separators end a line too, so a reported line number agrees.
fn py_lines(text: &str) -> impl Iterator<Item = &str> {
    text.split_inclusive([
        '\n', '\r', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\u{85}', '\u{2028}', '\u{2029}',
    ])
    .scan(false, |after_cr, piece| {
        let empty_lf = *after_cr && piece == "\n";
        *after_cr = piece.ends_with('\r');
        Some((empty_lf, piece))
    })
    .filter(|(skip, _)| !skip)
    .map(|(_, piece)| {
        piece.trim_end_matches([
            '\n', '\r', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\u{85}', '\u{2028}', '\u{2029}',
        ])
    })
}

/// Does this path carry the extension?
pub(crate) fn has_ext(path: &str, ext: &str) -> bool {
    Path::new(path).extension().is_some_and(|e| e == ext)
}

/// Does this change hold a file the Python-source checks read? (`ask:449-T065-scope`: those that stay Python never start on a change that holds none of what they read, so a one-line Rust edit starts none.) A `.py`
/// file or `pyproject.toml` for `python`; those or anything under `research/` for `research`. Exit 0 to run them.
fn needs(what: &str, root: &Path) -> Outcome {
    let base = git_text(root, &["merge-base", "HEAD", "origin/main"]);
    if base.trim().is_empty() {
        return Outcome::out(String::new()); // no base to compare with: cannot tell, so it runs
    }
    let against = base.trim();
    let mut names = git_text(root, &["diff", "--name-only", against]);
    names += &git_text(root, &["ls-files", "--others", "--exclude-standard"]);
    let hit = |p: &str| {
        has_ext(p, "py")
            || p == "pyproject.toml"
            || (what == "research" && p.starts_with("research/"))
    };
    Outcome {
        stdout: String::new(),
        stderr: String::new(),
        code: i32::from(!names.lines().any(hit)),
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
        Some("needs") => {
            let o = needs(rest.first().map_or("python", String::as_str), root);
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
