//! WHICH STARTED TASKS' FILES A DELTA TOUCHES (feature 451 T101's rule, moved here by T254 so the push's hold and `make land`'s
//! ready ruling ask one reader): a delta file - but the feature's sectioned files ([`SECTIONED`]) and the review ledger, which every
//! task writes - holds a task's edit when the feature's event log names a task-tagged write of it made after the file last landed
//! and before the delta's last commit of it. An edit line names its tree's absolute path; it is read against EVERY tree of the
//! clone ([`prefixes`]: the worktrees git lists, the trees the marks and starts name, the clone itself), not the clone's alone -
//! T101's one prefix passed over every edit a worktree's builder made (T254, the parallel trials of 2026-11-25).

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use serde_json::Value;

/// The feature's files a landing commits by section (`scoped.rs`): each holds every open task's section, line or verdict.
pub const SECTIONED: [&str; 3] = ["plan.md", "tasks.md", "plan-review.json"];
/// The review ledger, which every task's passes write a row of.
pub const LEDGER: &str = "dev/review-ledger.md";
/// How far back a file's last landed change is read; an edit older than this, or than its file's last landed change, is landed.
pub const LANDED_SINCE: &str = "--since=7.days";

/// A delta as the rule reads it: the files judged, each file's last landed change and its delta's last commit (epoch seconds).
#[derive(Debug, Default)]
pub struct Delta {
    pub judged: BTreeSet<String>,
    pub landed: BTreeMap<String, u32>,
    pub committed: BTreeMap<String, u32>,
}

/// The delta's files `names` but the feature's sectioned ones (the feature at `rel`) and the ledger.
#[must_use]
pub fn judged(names: Vec<String>, rel: &str) -> BTreeSet<String> {
    names
        .into_iter()
        .filter(|n| n != LEDGER && !SECTIONED.iter().any(|f| *n == format!("{rel}/{f}")))
        .collect()
}

/// `git log --format=@%ct --name-only`: each file's newest commit time (its first appearance, the log newest first).
#[must_use]
pub fn last_changes(log: &str) -> BTreeMap<String, u32> {
    let mut at = 0;
    let mut out = BTreeMap::new();
    for line in log.lines() {
        if let Some(t) = line.strip_prefix('@') {
            at = t.trim().parse().unwrap_or(0);
        } else if !line.is_empty() {
            out.entry(line.to_owned()).or_insert(at);
        }
    }
    out
}

/// The oldest landed time read ([`LANDED_SINCE`]): an edit before it is taken as landed. A file changed in the window has its own.
fn landed_floor() -> f64 {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64());
    now - 7.0 * 86_400.0
}

/// `git <args>` in `dir`: its output, or None where it failed.
fn git(dir: &Path, args: &[&str]) -> Option<String> {
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .ok()?;
    out.status
        .success()
        .then(|| String::from_utf8_lossy(&out.stdout).into_owned())
}

/// The delta of the tree holding `d` (`origin/main...HEAD`), the feature at `rel`; none where git cannot say (no `origin/main`).
#[must_use]
pub fn delta_of(d: &Path, rel: &str) -> Option<Delta> {
    let names = git(d, &["diff", "--name-only", "origin/main...HEAD"])?;
    let judged = judged(names.lines().map(str::to_owned).collect(), rel);
    if judged.is_empty() {
        return Some(Delta::default());
    }
    let base = git(d, &["merge-base", "origin/main", "HEAD"])?;
    let base = base.trim();
    let landed = last_changes(&git(d, &["log", "--format=@%ct", "--name-only", LANDED_SINCE, base])?);
    let committed = last_changes(&git(d, &["log", "--format=@%ct", "--name-only", &format!("{base}..HEAD")])?);
    Some(Delta {
        judged,
        landed,
        committed,
    })
}

/// Each tree an edit line may name, as a `<top>/` prefix: the worktrees `git worktree list` names from `d`, the trees `marks`
/// and `starts` name (a worktree removed after its builder's work was carried over), and the clone, `common`'s parent; the longest
/// first.
#[must_use]
pub fn prefixes(d: &Path, common: &Path, named: &[Value]) -> Vec<String> {
    let listed = git(d, &["worktree", "list", "--porcelain"]).unwrap_or_default();
    let mut trees: Vec<PathBuf> = listed
        .lines()
        .filter_map(|l| l.strip_prefix("worktree "))
        .map(PathBuf::from)
        .collect();
    trees.extend(
        named
            .iter()
            .filter_map(|v| v["tree"].as_str())
            .map(PathBuf::from),
    );
    trees.push(super::marks::main_top(common));
    let mut out: Vec<String> = Vec::new();
    for t in trees {
        let p = format!("{}/", t.to_string_lossy().trim_end_matches('/'));
        if !out.contains(&p) {
            out.push(p);
        }
    }
    // the longest first: a worktree inside another tree is read as its own, not as a directory of the outer one
    out.sort_by_key(|p| std::cmp::Reverse(p.len()));
    out
}

/// Each delta file that holds an edit of a task `wanted` takes: `{file: (task, its time as written)}`, the first such task's.
#[must_use]
pub fn touched(
    events: &Path,
    feature: &str,
    prefixes: &[String],
    delta: &Delta,
    wanted: &dyn Fn(&str) -> bool,
) -> BTreeMap<String, (String, String)> {
    let mut found = BTreeMap::new();
    if delta.judged.is_empty() {
        return found;
    }
    for (task, at, path) in edit_lines(events, feature) {
        let Some(file) = prefixes.iter().find_map(|p| path.strip_prefix(p.as_str())) else {
            continue;
        };
        if !wanted(&task) || !delta.judged.contains(file) {
            continue;
        }
        let after = delta
            .landed
            .get(file)
            .copied()
            .map_or_else(landed_floor, f64::from);
        let before = delta
            .committed
            .get(file)
            .copied()
            .map_or(f64::MIN, |c| f64::from(c) + 1.0);
        if after < at.0 && at.0 < before {
            found.entry(file.to_owned()).or_insert((task, at.1));
        }
    }
    found
}

/// Every task-tagged write the feature's event logs name: (task, (epoch seconds, its time as written), the path) - an Edit or Write's
/// `path`, a Bash call's `writes` (451 T93); a fallback line's task is a guess and is passed over, as the landing alone passes it.
#[must_use]
pub fn edit_lines(events: &Path, feature: &str) -> Vec<(String, (f64, String), String)> {
    let mut logs: Vec<PathBuf> = std::fs::read_dir(events)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            let stem = p.file_stem().unwrap_or_default().to_string_lossy();
            p.extension().is_some_and(|x| x == "jsonl")
                && (stem == feature || stem.starts_with(&format!("{feature}-")))
        })
        .collect();
    logs.sort();
    let mut out = Vec::new();
    for log in logs {
        let text = String::from_utf8_lossy(&std::fs::read(&log).unwrap_or_default()).into_owned();
        for line in text.lines() {
            if !line.contains("\"PostToolUse\"")
                || !(line.contains("\"cat\":\"edit\"") || line.contains("\"writes\""))
            {
                continue;
            }
            let Ok(v) = serde_json::from_str::<Value>(line) else {
                continue;
            };
            let task = v["task"].as_str().unwrap_or_default().to_owned();
            let when = v["t"].as_str().unwrap_or_default().to_owned();
            let Some(secs) = crate::iso::parse(&when.replace('Z', "+00:00")) else {
                continue;
            };
            if task.is_empty() || v["fallback"].as_bool() == Some(true) {
                continue;
            }
            let mut paths: Vec<String> = v["writes"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(|w| w.as_str().map(str::to_owned))
                .collect();
            if v["cat"].as_str() == Some("edit") {
                paths.extend(v["path"].as_str().map(str::to_owned));
            }
            for path in paths {
                out.push((task.clone(), (secs, when.clone()), path));
            }
        }
    }
    out
}
