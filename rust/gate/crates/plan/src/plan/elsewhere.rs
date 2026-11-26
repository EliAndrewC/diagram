//! The tree that holds a reviewed text (feature 451 T257): in the parallel trials (2026-11-25) spec-fidelity ran `make plan-verdict`
//! from the session clone, where a worktree task's section was still the template, and was refused on a digest mismatch five times
//! with no word of where the text it read was. A refusal now looks in the clone's other trees (`git worktree list` names the clone
//! and every worktree made from it) and names the one whose plan holds the reviewed text, with the command to record it there.
//! It runs only on a refusal, so a recording that matches costs nothing more.

use std::path::{Path, PathBuf};
use std::process::Command;

/// Every tree `git worktree list` names from `root`, `root` itself left out.
pub(super) fn trees(root: &Path) -> Vec<PathBuf> {
    let here = std::fs::canonicalize(root).ok();
    let listed = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["worktree", "list", "--porcelain"])
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default();
    listed
        .lines()
        .filter_map(|l| l.strip_prefix("worktree "))
        .map(PathBuf::from)
        .filter(|t| std::fs::canonicalize(t).ok() != here)
        .collect()
}

/// The first of `trees` whose `specs/<feature>/plan.md` answers `holds`.
pub(super) fn holding(
    trees: &[PathBuf],
    feature: &str,
    holds: &dyn Fn(&str) -> bool,
) -> Option<PathBuf> {
    trees.iter().find_map(|t| {
        std::fs::read_to_string(t.join("specs").join(feature).join("plan.md"))
            .ok()
            .filter(|p| holds(p))
            .map(|_| t.clone())
    })
}

/// What a digest refusal adds: the tree that holds the reviewed text and the command to record there (`form`: `TASK=T07`,
/// `BLOCKS=1`), or nothing where no other tree holds it.
pub(super) fn hint(spec_dir: &Path, form: &str, holds: &dyn Fn(&str) -> bool) -> String {
    let feature = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let root = spec_dir
        .parent()
        .and_then(Path::parent)
        .unwrap_or(Path::new("."));
    let n = feature.split('-').next().unwrap_or("");
    holding(&trees(root), &feature, holds).map_or_else(String::new, |t| {
        format!(
            "; the text reviewed is in {} - record it there: make -C {} plan-verdict F={n} {form} FILE=<the same file> AS=spec-fidelity (451 T257)",
            t.display(),
            t.display()
        )
    })
}

#[cfg(test)]
mod tests;
