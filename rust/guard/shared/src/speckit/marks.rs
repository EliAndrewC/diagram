//! A STARTED-TASK MARK PER TASK (feature 451 T254; the parallel trials of 2026-11-25, `specs/449-rust-codebase/port-talk-agenda.md`
//! item 1: `make task-start` wrote ONE `active-task` in the git common directory, so a second worktree's builder's start overwrote
//! the first's, and a push of one task was refused while the other was started - worked around by moving the mark by hand for every
//! landing). Each start writes its own mark, `<git common dir>/task-marks/<feature>/<task>/<tree key>.json` - `{"feature", "task",
//! "tasks" (a bundle's members, 451 T141), "tree" (the worktree's top that started it), "utc"}` - and no start moves another's.
//! ONE MARK A TASK A TREE (451 T369): a task started in two trees - a builder's pool tree, then the clone that carries its work -
//! keeps both marks, so one tree's `make task-unstart` leaves the other's mark beside its live start row, as the start log
//! ([`live_starts`], filtered per tree) already read it; with one file a task, the second start overwrote the first tree's mark and
//! the unstart left the first tree's row live with no mark behind it. A mark in the layout of before T369 (`<task>.json`) is read
//! as written and replaced by its own tree's next start.
//!
//! - A TREE'S TASK ([`of_tree`]), the one task a reader asks "what is this session working" of (decide, the review-round guard, the
//!   reviews' declared placement): the newest mark the tree itself wrote. The main worktree also reads the one-mark file of before
//!   (`active-task`, [`LEGACY`]) as its oldest mark, so a start made before this change still counts; its next start removes it.
//! - EVERY STARTED TASK ([`all`]): each mark, the legacy one as the main worktree's - what the push's hold asks
//!   (`speckit::holding_with`: this tree's started tasks, and another tree's whose files the delta touches) and the stall check reads.
//! - A mark goes when its task lands ([`remove`], `make land`'s sweep) or its feature is set down in its tree ([`clear`]). A mark
//!   of a ticked task left behind holds nothing: every reader asks for an open box.

use std::path::{Path, PathBuf};

use serde_json::Value;

/// The directory of the marks, in the git common directory.
pub const DIR: &str = "task-marks";
/// The one mark of before T254, read as the main worktree's oldest.
pub const LEGACY: &str = "active-task";

/// The log of every start, in the git common directory: a row a start (`{"feature", "task", "utc", "tree"}`) and a row an undo
/// (`make task-unstart`'s, `{"unstart": {"feature", "task"}, "tree", "utc"}`).
pub const STARTS: &str = "task-starts.jsonl";

/// The start log's text as every reader takes it: each `unstart` row gone, and with it EVERY start row before it of its feature and
/// task in its tree (a start row from before rows named their tree is any tree's). So a start and its undo read as no start
/// (feature 451 T359: `make task-unstart`), and every other line stays as written, a line that is no JSON among them, for the
/// reader's own rule on it. WHY EVERY EARLIER START, not the latest alone: a tree holds one mark a task, which a second start
/// overwrites and the unstart removes, so a task started twice and unstarted once has no mark - and the log, read by the landing's
/// "was it started" (`land/ready.rs`) and the closing order, must say what the mark says. Its cost: the time breakdown loses the
/// earlier start of a task worked, unstarted and never started again; a start made after the undo is kept and dates it.
/// ONE READER TAKES THE RAW LOG INSTEAD, on purpose (T359-D9b): `static_runs_hooks`' count of a task's `make static` runs since its
/// last landing, which no unstart resets - read through this filter, an unstart and a new start would restart it unrecorded.
#[must_use]
pub fn live_starts(text: &str) -> String {
    if !text.contains("\"unstart\"") {
        return text.to_owned();
    }
    let lines: Vec<&str> = text.split_inclusive('\n').collect();
    let rows: Vec<Value> = lines
        .iter()
        .map(|l| serde_json::from_str(l.trim()).unwrap_or(Value::Null))
        .collect();
    let mut keep = vec![true; lines.len()];
    for (i, row) in rows.iter().enumerate() {
        let undone = &row["unstart"];
        if !undone.is_object() {
            continue;
        }
        keep[i] = false;
        for (j, s) in rows.iter().enumerate().take(i) {
            let answered = s["task"].is_string()
                && s["task"] == undone["task"]
                && s["feature"] == undone["feature"]
                && (s["tree"].is_null() || s["tree"] == row["tree"]);
            keep[j] = keep[j] && !answered;
        }
    }
    let kept = lines.iter().zip(keep).filter(|(_, k)| *k);
    kept.map(|(l, _)| *l).collect()
}

/// [`live_starts`] of the log under `common`, "" where there is none or it cannot be read.
#[must_use]
pub fn starts_text(common: &Path) -> String {
    live_starts(&std::fs::read_to_string(common.join(STARTS)).unwrap_or_default())
}

/// The git common directory and the top of the tree holding `dir`, as git names them; none outside a repository.
#[must_use]
pub fn places(dir: &Path) -> Option<(PathBuf, PathBuf)> {
    let out = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args([
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
            "--show-toplevel",
        ])
        .output()
        .ok()?;
    let text = String::from_utf8_lossy(&out.stdout).into_owned();
    let mut lines = text.lines();
    let common = PathBuf::from(lines.next()?.trim());
    let top = PathBuf::from(lines.next()?.trim());
    out.status.success().then_some((common, top))
}

/// Two paths naming one tree: equal as written, or once each is resolved.
#[must_use]
pub fn same_tree(a: &Path, b: &Path) -> bool {
    a == b
        || matches!((std::fs::canonicalize(a), std::fs::canonicalize(b)), (Ok(x), Ok(y)) if x == y)
}

/// The main worktree's top: the common directory's parent (`<clone>/.git`).
#[must_use]
pub fn main_top(common: &Path) -> PathBuf {
    common.parent().unwrap_or(common).to_path_buf()
}

/// The tree a mark names (`""` for none).
fn tree_of(mark: &Value) -> &Path {
    Path::new(mark["tree"].as_str().unwrap_or(""))
}

/// The file name of `tree`'s mark in a task's directory: the tree's path, resolved where it can be, each character but a letter, a
/// digit, `.`, `-` and `_` written `_` - one name a tree, and no hash a later build could spell otherwise. No reader derives it: a
/// tree's mark is found by the `tree` it names ([`own_file`]).
fn tree_key(tree: &Path) -> String {
    let resolved = std::fs::canonicalize(tree).unwrap_or_else(|_| tree.to_path_buf());
    let keep = |c: char| c.is_ascii_alphanumeric() || matches!(c, '.' | '-' | '_');
    let key: String = resolved
        .to_string_lossy()
        .chars()
        .map(|c| if keep(c) { c } else { '_' })
        .collect();
    format!("{key}.json")
}

/// The file of `tree`'s own mark of `task` of `feature`: in the task's directory, else the layout of before 451 T369
/// (`<feature>/<task>.json`) where that file names `tree`; none where `tree` holds no mark of it in either.
#[must_use]
pub fn own_file(common: &Path, feature: &str, task: &str, tree: &Path) -> Option<PathBuf> {
    let dir = common.join(DIR).join(feature);
    let mine = |p: &PathBuf| matches!(read(p), Ok(Some(v)) if same_tree(tree_of(&v), tree));
    let nested = std::fs::read_dir(dir.join(task))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path());
    nested
        .chain(std::iter::once(dir.join(format!("{task}.json"))))
        .find(mine)
}

/// `make task-start`'s mark of `value` (`feature`, `task`, perhaps `tasks`), started in `tree` at `utc`: THIS TREE'S file of the task
/// (`task-marks/<feature>/<task>/<tree key>.json`, 451 T369), which replaces the tree's earlier mark of it - in the layout of before
/// T369 too - and moves no other tree's; the main worktree's legacy mark removed, as this start replaces it.
///
/// # Errors
/// The tree's earlier mark cannot be removed, the directory made or the file written.
pub fn write(common: &Path, tree: &Path, mut value: Value, utc: &str) -> Result<(), String> {
    let feature = value["feature"].as_str().unwrap_or_default().to_owned();
    let task = value["task"].as_str().unwrap_or_default().to_owned();
    value["tree"] = Value::from(tree.to_string_lossy().into_owned());
    value["utc"] = Value::from(utc);
    while let Some(earlier) = own_file(common, &feature, &task, tree) {
        std::fs::remove_file(&earlier).map_err(|e| format!("{}: {e}", earlier.display()))?;
    }
    let dir = common.join(DIR).join(&feature).join(&task);
    std::fs::create_dir_all(&dir).map_err(|e| format!("{}: {e}", dir.display()))?;
    let path = dir.join(tree_key(tree));
    std::fs::write(
        &path,
        format!("{}\n", crate::pyjson::dumps(&value, None, true)),
    )
    .map_err(|e| format!("{}: {e}", path.display()))?;
    if same_tree(tree, &main_top(common)) {
        let _ = std::fs::remove_file(common.join(LEGACY));
    }
    Ok(())
}

/// One mark read: `Ok(None)` for a file that is not JSON, `Err` for one that cannot be read (the legacy reader's two cases).
fn read(path: &Path) -> Result<Option<Value>, String> {
    let bytes = std::fs::read(path).map_err(|_| format!("{}: unreadable", path.display()))?;
    Ok(String::from_utf8(bytes)
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok()))
}

/// Every mark under `common`, oldest first (by `utc`, then path); the legacy mark first, as the main worktree's, where it is an
/// object. A file that cannot be read, or is not an object, is skipped.
#[must_use]
pub fn all(common: &Path) -> Vec<Value> {
    let mut out = Vec::new();
    if let Ok(Some(mut v)) = read(&common.join(LEGACY)) {
        if v.is_object() {
            v["tree"] = Value::from(main_top(common).to_string_lossy().into_owned());
            out.push(v);
        }
    }
    out.extend(files(common).into_iter().map(|(_, m)| m));
    out
}

/// Every mark file under `common` and its mark, oldest first (by `utc`, then path): a task's directory's files, one a tree (451
/// T369), and a feature's own `<task>.json` files of before T369 alike. A file that cannot be read, or is not an object, is skipped.
fn files(common: &Path) -> Vec<(PathBuf, Value)> {
    let listed = |d: &Path| -> Vec<PathBuf> {
        let entries = std::fs::read_dir(d).into_iter().flatten().flatten();
        entries.map(|e| e.path()).collect()
    };
    let mut paths: Vec<PathBuf> = listed(&common.join(DIR))
        .iter()
        .flat_map(|f| listed(f))
        .flat_map(|p| if p.is_dir() { listed(&p) } else { vec![p] })
        .collect();
    paths.sort();
    let mut marks: Vec<(PathBuf, Value)> = paths
        .into_iter()
        .filter_map(|p| read(&p).ok().flatten().map(|v| (p, v)))
        .filter(|(_, v)| v.is_object())
        .collect();
    marks.sort_by(|(_, a), (_, b)| a["utc"].as_str().cmp(&b["utc"].as_str()));
    marks
}

/// Every task a mark names: its `task` and a bundle's `tasks`, each once.
#[must_use]
pub fn tasks_of(mark: &Value) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    let named =
        std::iter::once(&mark["task"]).chain(mark["tasks"].as_array().into_iter().flatten());
    for t in named.filter_map(Value::as_str).filter(|t| !t.is_empty()) {
        if !out.iter().any(|o| o == t) {
            out.push(t.to_owned());
        }
    }
    out
}

/// The mark of the tree holding `dir`: its newest own mark, else (the main worktree) the legacy one as written - `Value::Null`
/// where there is none, and the legacy value as it reads where it is not an object (its readers' refusal).
///
/// # Errors
/// The legacy mark there but unreadable.
pub fn of_tree(dir: &Path) -> Result<Value, String> {
    let Some((common, top)) = places(dir) else {
        return Ok(Value::Null);
    };
    let own = all(&common)
        .into_iter()
        .rev()
        .find(|m| m["utc"].is_string() && same_tree(tree_of(m), &top));
    if let Some(m) = own {
        return Ok(m);
    }
    let legacy = common.join(LEGACY);
    if !same_tree(&top, &main_top(&common)) || !legacy.exists() {
        return Ok(Value::Null);
    }
    Ok(read(&legacy)?.unwrap_or(Value::Null))
}

/// `make set-down`'s clear (451 T29): the marks of `feature` that tree `top` wrote removed, and the legacy one where it names
/// `feature` and `top` is the main worktree; the last task removed, or none. Another tree's marks stay: a set-down in one tree
/// moves no other builder's.
#[must_use]
pub fn clear(common: &Path, top: &Path, feature: &str) -> Option<String> {
    let mut named = None;
    let legacy = common.join(LEGACY);
    if same_tree(top, &main_top(common)) {
        if let Ok(Some(v)) = read(&legacy) {
            if v["feature"].as_str() == Some(feature) && std::fs::remove_file(&legacy).is_ok() {
                named = Some(
                    v["task"]
                        .as_str()
                        .map_or_else(|| "None".to_owned(), str::to_owned),
                );
            }
        }
    }
    let own = files(common).into_iter().filter(|(_, m)| {
        m["utc"].is_string() && m["feature"].as_str() == Some(feature) && same_tree(tree_of(m), top)
    });
    for (path, m) in own {
        if std::fs::remove_file(path).is_ok() {
            named = Some(m["task"].as_str().unwrap_or_default().to_owned());
        }
    }
    named
}

/// The marks of `tasks` of `feature` - its directory name, or its number as `make land`'s `F=` gives it - removed once they land
/// (`make land`'s sweep): every tree's (451 T369); a mark that is not there is no error.
pub fn remove(common: &Path, feature: &str, tasks: &[String]) {
    let dirs = std::fs::read_dir(common.join(DIR))
        .into_iter()
        .flatten()
        .flatten();
    for dir in dirs.map(|e| e.path()) {
        let name = dir
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        if name != feature && !name.starts_with(&format!("{feature}-")) {
            continue;
        }
        // an empty id would name the feature's own directory
        for t in tasks.iter().filter(|t| !t.is_empty()) {
            let _ = std::fs::remove_file(dir.join(format!("{t}.json")));
            let _ = std::fs::remove_dir_all(dir.join(t));
        }
    }
}

#[cfg(test)]
mod tests;
