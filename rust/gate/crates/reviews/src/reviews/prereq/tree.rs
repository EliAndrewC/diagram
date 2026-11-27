//! A REVIEW'S GATE IS ITS SNAPSHOT'S (feature 451 T164). With three builders in one clone on 2026-11-22, the 449 T312 bundle's paired
//! gate (`make verify`, then `make done`) went red or "tree moved" four times on other builders' half-done edits, and seven of its ten
//! finished verdicts were rewritten NOT-REVIEWABLE because a page session and a test-file edit wrote into the clone while the reviews
//! ran: the gate's state was the clone's one green stamp, keyed on the clone's working tree, which every builder's edit moves.
//!
//! So `make verify T=<tasks>` builds the review tree (`scripts/gates/review-tree.sh`): a worktree at a commit of the bundle's own files
//! on HEAD, the landing worktree's way, where the gate runs and the snapshot is taken. Each unit's snapshot carries `tree.json` - the
//! commit, the review tree's engine key and the tree - and the gate's run its record, `.git/review-trees/<commit>.json`, which the
//! review tree's runner writes `running`, then `green` or `red` with the key it judged. A unit with a snapshot is judged by that record
//! alone: another builder's edit to the clone neither voids nor colors it, and its verdict is keyed to the snapshot's engine key and
//! content key, which a landing of the same files carries. A unit with none (`make verify` in the clone before T164, a fixture) is
//! judged by the clone's stamp, as before.
//!
//! Research: plumbing - NONE: reads the review tree's records, deciding nothing about a map

use std::path::{Path, PathBuf};

use l7r_shared::guards::event_log_hooks::common_git_dir;
use serde_json::Value;

/// A unit's snapshot: the review tree's commit, engine key and directory, and the snapshot's own copy of the sheet.
#[derive(Debug, PartialEq, Eq)]
pub struct Snap {
    pub commit: String,
    pub key: String,
    pub tree: PathBuf,
    /// the map or sheet the unit is judged on
    pub on: String,
    /// `.git/review-snapshot/<unit>/clone`, the sheet's files as the review tree drew them
    pub copy: PathBuf,
}

fn read(p: &Path) -> Option<Value> {
    serde_json::from_str(&std::fs::read_to_string(p).ok()?).ok()
}

fn text(v: &Value, k: &str) -> String {
    v.get(k)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned()
}

/// The unit's snapshot record, where the review tree took it: None for a unit with no snapshot, or one taken in the clone.
#[must_use]
pub fn of_unit(clone: &Path, unit: &str) -> Option<Snap> {
    if unit.is_empty() {
        return None;
    }
    let dir = common_git_dir(clone).join("review-snapshot").join(unit);
    let rec = read(&dir.join("tree.json"))?;
    let (commit, key) = (text(&rec, "commit"), text(&rec, "key"));
    (!commit.is_empty() && !key.is_empty()).then(|| Snap {
        commit,
        key,
        tree: PathBuf::from(text(&rec, "tree")),
        on: text(&rec, "on"),
        copy: dir.join("clone"),
    })
}

/// What a unit's snapshot lacks of the artifacts a reviewer reads (a sheet has no manifest), or None when whole or not snapshotted.
#[must_use]
pub fn lacking(clone: &Path, unit: &str) -> Option<String> {
    let snap = of_unit(clone, unit)?;
    let file = |ext: &str| snap.copy.join(format!("{}{ext}", snap.on));
    let sheet = !file(".json").is_file() && file(".svg").is_file();
    let gone: Vec<&str> = super::ARTIFACTS
        .iter()
        .copied()
        .filter(|ext| !(file(ext).is_file() || (sheet && *ext == ".json")))
        .collect();
    (!gone.is_empty()).then(|| {
        format!(
            "{unit}: its review snapshot lacks {} - `make verify T=<task(s)>` draws it in the review tree and takes it again",
            gone.join(" ")
        )
    })
}

/// The gate's record of the review tree at `commit`.
#[must_use]
pub fn gate_file(clone: &Path, commit: &str) -> PathBuf {
    common_git_dir(clone)
        .join("review-trees")
        .join(format!("{commit}.json"))
}

/// Whether process `pid` is alive (`/proc/<pid>` stands).
fn alive(pid: i64) -> bool {
    pid > 0 && Path::new(&format!("/proc/{pid}")).exists()
}

/// The snapshot's gate: `green` (it went green on the snapshot's key), `running` (its runner is alive), else `red` - a red run, a
/// runner gone with no result, a green on another key, or no record at all.
#[must_use]
pub fn gate(clone: &Path, snap: &Snap) -> &'static str {
    let Some(rec) = read(&gate_file(clone, &snap.commit)) else {
        return "red";
    };
    match text(&rec, "state").as_str() {
        "green" if text(&rec, "key") == snap.key => "green",
        "running" if rec.get("pid").and_then(Value::as_i64).is_some_and(alive) => "running",
        _ => "red",
    }
}

#[cfg(test)]
mod tests;
