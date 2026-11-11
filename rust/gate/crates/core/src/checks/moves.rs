//! Which of a delta's changed files only moved: same bytes, new path (feature 329, from `scripts/reviews/moves.py`). A byte-identical blob at the base is exactly the claim "nothing in it changed".

use std::collections::BTreeSet;
use std::io::Write as _;
use std::path::Path;
use std::process::{Command, Stdio};

use super::git_text;

fn hash_objects(root: &Path, names: &[&String]) -> Option<Vec<String>> {
    let spawned = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["hash-object", "--stdin-paths"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn();
    let mut child = spawned.ok()?;
    let input: String = names.iter().flat_map(|n| [n.as_str(), "\n"]).collect();
    if let Some(mut pipe) = child.stdin.take() {
        let _ = pipe.write_all(input.as_bytes());
    }
    let out = child
        .wait_with_output()
        .map(|o| o.stdout)
        .unwrap_or_default();
    let ids = String::from_utf8_lossy(&out)
        .split_whitespace()
        .map(str::to_owned)
        .collect();
    Some(ids)
}

/// The subset of `names` whose working-tree content is a blob `base` already held; a missing file is never moved.
#[must_use]
pub fn moved_only(root: &Path, base: &str, names: &[String]) -> BTreeSet<String> {
    let mut present: Vec<&String> = names
        .iter()
        .filter(|n| !n.is_empty() && root.join(n).is_file())
        .collect();
    present.sort();
    present.dedup();
    let ids = if base.is_empty() || present.is_empty() {
        Vec::new()
    } else {
        hash_objects(root, &present).unwrap_or_default()
    };
    if ids.is_empty() || ids.len() != present.len() {
        return BTreeSet::new();
    }
    let listed = git_text(root, &["ls-tree", "-r", base]);
    let have: BTreeSet<&str> = listed
        .lines()
        .filter_map(|l| {
            l.split_whitespace()
                .collect::<Vec<_>>()
                .get(2)
                .copied()
                .filter(|_| l.split_whitespace().nth(1) == Some("blob"))
        })
        .collect();
    present
        .into_iter()
        .zip(ids)
        .filter(|(_, id)| have.contains(id.as_str()))
        .map(|(n, _)| n.clone())
        .collect()
}

#[cfg(test)]
mod tests;
