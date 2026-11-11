//! The active task, a check's wait for its decisions, the plan's archive and the push (feature 449 T066, from `plan_gate.py`).

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::Value;

use super::history::History;
use super::sections::{ordered_sections, re, task_sections, wording_only, TASK_ID};
use super::status::{judge, owed, section_clear, task_current, RECORD};
use super::today;
use crate::codeid::common_git_dir;

fn read(path: &Path) -> String {
    std::fs::read_to_string(path).unwrap_or_default()
}

fn review_of(dir: &Path) -> Value {
    serde_json::from_str(&read(&dir.join(RECORD))).unwrap_or(serde_json::json!({}))
}

/// (the active feature's directory, its active task): `.git/active-task` when it names this feature and its box is open, else the
/// first open task of `.specify/feature.json`'s feature.
pub(super) fn active_task(root: &Path) -> (Option<PathBuf>, String) {
    let parsed: Value =
        serde_json::from_str(&read(&root.join(".specify/feature.json"))).unwrap_or(Value::Null);
    let named = parsed["feature_directory"]
        .as_str()
        .unwrap_or("")
        .trim_end_matches('/');
    let dir = root.join(named);
    if named.is_empty() || !dir.join("tasks.md").is_file() {
        return (None, String::new());
    }
    let mark: Value = common_git_dir(root).map_or(Value::Null, |c| {
        serde_json::from_str(&read(&c.join("active-task"))).unwrap_or(Value::Null)
    });
    let tasks = read(&dir.join("tasks.md"));
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    if let Some(task) = mark["task"]
        .as_str()
        .filter(|t| !t.is_empty() && mark["feature"] == *name)
    {
        if re(&format!(r"(?m)^- \[ \] {}\b", fancy_regex::escape(task)))
            .is_match(&tasks)
            .unwrap_or(false)
        {
            let task = task.to_owned();
            return (Some(dir), task);
        }
    }
    let first = re(r"(?m)^- \[ \] (T\d+[a-z]?)\b")
        .captures(&tasks)
        .ok()
        .flatten()
        .map_or(String::new(), |c| c[1].to_owned());
    (Some(dir), first)
}

/// Why a check may not be dispatched yet (feature 375 FR-003(a)): the active task's decisions carry no current CLEAR verdict.
pub(super) fn decision_refusal(root: &Path) -> String {
    let (dir, task) = active_task(root);
    let Some(dir) = dir.filter(|_| !task.is_empty()) else {
        return String::new();
    };
    let plan = dir.join("plan.md");
    let text = read(&plan);
    let review = review_of(&dir);
    let name = dir.file_name().unwrap_or_default().to_string_lossy();
    let history = History::new(&plan, "HEAD");
    if let Some(section) = task_sections(&text).get(&task) {
        if wording_only(section)
            || task_current(&review, &text, &task, Some(&history))
            || (owed(&dir).is_none() && section_clear(&review, section, Some(&history)))
        {
            return String::new();
        }
        let number = name.split('-').next().unwrap_or("");
        return format!("{name} {task}: its plan section carries no current CLEAR decision verdict - decide first, then check (feature 375 FR-003a): `make decide F={number} T={task}` names the review to dispatch");
    }
    owed(&dir).map_or(String::new(), |(rule, reason)| format!("{name} {task}: the plan has no section for this task and its plan-stage review is not current and CLEAR ({rule}) - decide first (feature 375 FR-003a): {reason}"))
}

/// The task sections `make plan-archive` may move (D62): every task their heading names ticked, and their verdict CLEAR.
fn archivable(dir: &Path) -> Vec<String> {
    let plan = dir.join("plan.md");
    let text = read(&plan);
    let tasks = read(&dir.join("tasks.md"));
    let done: BTreeSet<String> = re(r"(?m)^- \[[xX]\] (T\d+[a-z]?)\b")
        .captures_iter(&tasks)
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    let review = review_of(dir);
    let history = History::new(&plan, "HEAD");
    let mut sections: Vec<String> = Vec::new();
    for (_, sec) in ordered_sections(&text) {
        if !sections.contains(&sec) {
            sections.push(sec);
        }
    }
    let mut out = Vec::new();
    let mut taken: Vec<(usize, usize)> = Vec::new();
    for sec in sections {
        let at = text.find(&sec);
        let heading = sec.lines().next().unwrap_or("");
        let ids: Vec<&str> = TASK_ID
            .find_iter(heading)
            .flatten()
            .map(|m| m.as_str())
            .collect();
        if ids.is_empty()
            || ids.iter().any(|i| !done.contains(*i))
            || at.is_some_and(|a| taken.iter().any(|(lo, hi)| *lo <= a && a < *hi))
        {
            continue;
        }
        if ids.iter().any(|i| task_current(&review, &text, i, None))
            || section_clear(&review, &sec, Some(&history))
        {
            if let Some(a) = at {
                taken.push((a, a + sec.len()));
            }
            out.push(sec);
        }
    }
    out
}

const MARKER: &str = "\0archived\0";

/// Move the archivable sections out of plan.md into plan-done.md (D62), byte for byte, leaving one generated line where each run of
/// them stood; the task ids moved. Piece by piece, and only what moved; and again until nothing is left (features 449, 444 T20).
pub(super) fn archive(dir: &Path, when: Option<&str>) -> Vec<String> {
    let plan = dir.join("plan.md");
    let mut text = read(&plan);
    let sections = archivable(dir);
    let day = when.map_or_else(today, str::to_owned);
    let split = re(r"(?m)^(?=#{2,4} )");
    let mut moved: Vec<(String, Vec<String>)> = Vec::new();
    for sec in &sections {
        let ids: Vec<String> = TASK_ID
            .find_iter(sec.lines().next().unwrap_or(""))
            .flatten()
            .map(|m| m.as_str().to_owned())
            .collect();
        let pieces: Vec<String> = if text.contains(sec.as_str()) {
            vec![sec.clone()]
        } else {
            pieces_of(&split, sec)
        };
        for piece in pieces {
            if text.contains(&piece) {
                text = text.replacen(&piece, MARKER, 1);
                moved.push((piece, ids.clone()));
            }
        }
    }
    if moved.is_empty() {
        return Vec::new();
    }
    let mut pos = 0;
    let mut out = String::new();
    let mut rest = text.as_str();
    while let Some(at) = rest.find(MARKER) {
        out.push_str(&rest[..at]);
        let after = &rest[at..];
        let count = after
            .len()
            .saturating_sub(after.trim_start_matches(MARKER).len())
            / MARKER.len();
        let ids: Vec<&String> = moved[pos..pos + count]
            .iter()
            .flat_map(|(_, i)| i)
            .collect();
        pos += count;
        let _ = writeln!(
            out,
            "<!-- plan-archive: {} to {} moved to plan-done.md, {day} (feature 375 FR-044) -->",
            ids[0],
            ids[ids.len() - 1]
        );
        rest = &rest[at + count * MARKER.len()..];
    }
    out.push_str(rest);
    let _ = std::fs::write(&plan, out);
    let done = dir.join("plan-done.md");
    let head = if done.is_file() {
        String::new()
    } else {
        format!("# {} - the plan's finished sections (feature 375 FR-044; no review reads this file)\n\n", dir.file_name().unwrap_or_default().to_string_lossy())
    };
    let appended = format!(
        "{head}<!-- plan-archive: archived {day} -->\n{}",
        moved.iter().map(|(p, _)| p.as_str()).collect::<String>()
    );
    let _ = std::fs::write(&done, read(&done) + &appended);
    let mut ids: Vec<String> = Vec::new();
    for id in moved.into_iter().flat_map(|(_, i)| i) {
        if !ids.contains(&id) {
            ids.push(id);
        }
    }
    ids.extend(archive(dir, when));
    ids
}

fn pieces_of(split: &fancy_regex::Regex, sec: &str) -> Vec<String> {
    let mut starts: Vec<usize> = split.find_iter(sec).flatten().map(|m| m.start()).collect();
    starts.push(sec.len());
    let mut out = Vec::new();
    let mut last = 0;
    for at in starts {
        if !sec[last..at].trim().is_empty() {
            out.push(sec[last..at].to_owned());
        }
        last = at;
    }
    out
}

fn show(root: &Path, reference: &str, path: &str) -> Option<Vec<u8>> {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["show", &format!("{reference}:{path}")])
        .output()
        .ok()?;
    done.status.success().then_some(done.stdout)
}

/// Every `specs/NNN-*` directory the range touches.
pub(super) fn touched_features(root: &Path, range: &str) -> Vec<String> {
    let names = super::git_line(root, &["diff", "--name-only", range]);
    let mut out: BTreeSet<String> = BTreeSet::new();
    for name in names.lines() {
        let mut parts = name.split('/');
        if let (Some("specs"), Some(dir), Some(_)) = (parts.next(), parts.next(), parts.next()) {
            out.insert(format!("specs/{dir}"));
        }
    }
    out.into_iter().collect()
}

/// A ticked task is a column-zero line, in either case: an indented research box is part of its task.
fn has_ticked(tasks: &str) -> bool {
    tasks
        .lines()
        .any(|l| l.starts_with("- [x] ") || l.starts_with("- [X] "))
}

/// (feature dir, rule, reason) for each touched feature with a ticked task and no current CLEAR review, at `reference`.
pub(super) fn push_owed(
    root: &Path,
    range: &str,
    reference: &str,
) -> Vec<(String, &'static str, String)> {
    let mut out = Vec::new();
    for feature in touched_features(root, range) {
        let Some(tasks) = show(root, reference, &format!("{feature}/tasks.md")) else {
            continue;
        };
        if !has_ticked(&String::from_utf8_lossy(&tasks)) {
            continue;
        }
        let review = show(root, reference, &format!("{feature}/{RECORD}"))
            .map(|r| String::from_utf8_lossy(&r).into_owned());
        let plan = show(root, reference, &format!("{feature}/plan.md"));
        let done = show(root, reference, &format!("{feature}/plan-done.md")).unwrap_or_default();
        let history = History::new(&root.join(&feature).join("plan.md"), reference);
        if let Some((rule, reason)) = judge(
            plan.as_deref(),
            review.as_deref(),
            Some(&history),
            &String::from_utf8_lossy(&done),
        ) {
            out.push((feature, rule, reason));
        }
    }
    out
}

/// A spec directory from a path, a number (`243`) or a directory name; None when not exactly one.
pub(super) fn resolve(feature: &str, root: &Path) -> Option<PathBuf> {
    let given = Path::new(feature);
    if given.is_dir() {
        return Some(given.to_owned());
    }
    if feature.contains('/') {
        return None;
    }
    let specs = root.join("specs");
    if specs.join(feature).is_dir() {
        return Some(specs.join(feature));
    }
    let prefix = format!("{feature}-");
    let hits: Vec<PathBuf> = std::fs::read_dir(&specs)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix) && e.path().is_dir())
        .map(|e| e.path())
        .collect();
    if hits.len() == 1 {
        hits.into_iter().next()
    } else {
        None
    }
}

#[cfg(test)]
mod tests;
