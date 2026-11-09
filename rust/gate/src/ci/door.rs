//! The build-side door for the full sweep (FR-025, research R11, from `ci/door.py`): the prompt's answer travels in the tree, as a `permitted` entry in `dev/bypass-log/` committed with the work. It never reads an environment
//! variable, and forging an entry is an edit to a tracked file, visible in a diff.

use std::path::Path;
use std::process::Command;

use serde_json::Value;

use super::runlog;

fn is_ancestor(root: &Path, commit: &str, reference: &str) -> bool {
    Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["merge-base", "--is-ancestor", commit, reference])
        .output()
        .is_ok_and(|o| o.status.success())
}

/// (may the full scope run, why).
pub(crate) fn check(root: &Path, base_ref: &str) -> (bool, String) {
    let mut seen = 0;
    for path in runlog::log_files(root, runlog::BYPASS_LOG).iter().rev() {
        let Ok(entry) =
            serde_json::from_str::<Value>(&std::fs::read_to_string(path).unwrap_or_default())
        else {
            continue;
        };
        if !entry["target"]
            .as_str()
            .unwrap_or_default()
            .contains("FULL")
        {
            continue;
        }
        seen += 1;
        let commit = entry["commit"].as_str().unwrap_or_default();
        if entry["outcome"] != "permitted"
            || commit.is_empty()
            || !is_ancestor(root, commit, "HEAD")
            || is_ancestor(root, commit, base_ref)
        {
            continue;
        }
        let name = path
            .file_name()
            .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
        let why: String = entry["why"]
            .as_str()
            .unwrap_or_default()
            .chars()
            .take(80)
            .collect();
        return (
            true,
            format!("permitted entry {name} (commit {commit}) authorizes FULL: {why}"),
        );
    }
    if seen > 0 {
        return (false, "no committed `permitted` FULL entry authored by THIS work (entries seen were cancelled, refused, or inherited from main) - answer the local prompt: make done FULL=1".to_owned());
    }
    (false, "no FULL entry in dev/bypass-log/ at all - the prompt was never answered for this work (run the merge action with FULL=1 in a terminal)".to_owned())
}

#[cfg(test)]
mod tests;
