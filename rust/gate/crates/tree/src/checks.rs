//! Which retained check a change starts (`ask:449-T065-scope`, from `checks.rs`, split out by T92 so the cohort asks it without the
//! checks): those that stay Python never start on a change that holds none of what they read, so a one-line Rust edit starts none.

use std::path::Path;

pub use l7r_gate_core::checks::*;

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
                "rust/gate/crates/downloads/src/record/downloads",
            ]) || (path.starts_with("research/questions/") && path.ends_with(".notes.html"))
                || [
                    "research/partial-confirmations.jsonl",
                    "research/source-access.json",
                    "research/to-download.md",
                    "rust/gate/crates/checks/src/checks/partial_citations.rs",
                    "rust/gate/crates/downloads/src/record/access_tags.rs",
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

/// Does the change hold a file this retained Python check reads?
#[must_use]
pub fn needs_run(check: &str, root: &Path) -> bool {
    needs(check, root) == 0
}

/// Does this change hold a file `check` reads? Exit 0 to run it, and when there is no base to compare with.
#[must_use]
pub fn needs(check: &str, root: &Path) -> i32 {
    let base = git_text(root, &["merge-base", "HEAD", "origin/main"]);
    if base.trim().is_empty() {
        return 0; // no base to compare with: cannot tell, so it runs
    }
    let mut names = git_text(root, &["diff", "--name-only", base.trim()]);
    names += &git_text(root, &["ls-files", "--others", "--exclude-standard"]);
    i32::from(!names.lines().any(|p| reads(check, p)))
}

#[cfg(test)]
mod tests;
