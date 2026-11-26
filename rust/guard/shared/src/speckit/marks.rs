//! A STARTED-TASK MARK PER TASK (feature 451 T254; the parallel trials of 2026-11-25, `specs/449-rust-codebase/port-talk-agenda.md`
//! item 1: `make task-start` wrote ONE `active-task` in the git common directory, so a second worktree's builder's start overwrote
//! the first's, and a push of one task was refused while the other was started - worked around by moving the mark by hand for every
//! landing). Each start writes its own mark, `<git common dir>/task-marks/<feature>/<task>.json` - `{"feature", "task", "tasks"
//! (a bundle's members, 451 T141), "tree" (the worktree's top that started it), "utc"}` - and no start moves another's.
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

/// `make task-start`'s mark of `value` (`feature`, `task`, perhaps `tasks`), started in `tree` at `utc`; the main worktree's
/// legacy mark removed, as this start replaces it.
///
/// # Errors
/// The directory cannot be made or the file written.
pub fn write(common: &Path, tree: &Path, mut value: Value, utc: &str) -> Result<(), String> {
    let feature = value["feature"].as_str().unwrap_or_default().to_owned();
    let task = value["task"].as_str().unwrap_or_default().to_owned();
    value["tree"] = Value::from(tree.to_string_lossy().into_owned());
    value["utc"] = Value::from(utc);
    let dir = common.join(DIR).join(&feature);
    std::fs::create_dir_all(&dir).map_err(|e| format!("{}: {e}", dir.display()))?;
    let path = dir.join(format!("{task}.json"));
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
    let mut files: Vec<PathBuf> = std::fs::read_dir(common.join(DIR))
        .into_iter()
        .flatten()
        .flatten()
        .flat_map(|f| std::fs::read_dir(f.path()).into_iter().flatten().flatten())
        .map(|e| e.path())
        .collect();
    files.sort();
    let mut marks: Vec<Value> = files
        .iter()
        .filter_map(|p| read(p).ok().flatten())
        .filter(Value::is_object)
        .collect();
    marks.sort_by(|a, b| a["utc"].as_str().cmp(&b["utc"].as_str()));
    out.extend(marks);
    out
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
    let own = all(common).into_iter().filter(|m| {
        m["utc"].is_string() && m["feature"].as_str() == Some(feature) && same_tree(tree_of(m), top)
    });
    for m in own {
        let task = m["task"].as_str().unwrap_or_default().to_owned();
        if std::fs::remove_file(common.join(DIR).join(feature).join(format!("{task}.json"))).is_ok()
        {
            named = Some(task);
        }
    }
    named
}

/// The marks of `tasks` of `feature` - its directory name, or its number as `make land`'s `F=` gives it - removed once they land
/// (`make land`'s sweep); a mark that is not there is no error.
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
        for t in tasks {
            let _ = std::fs::remove_file(dir.join(format!("{t}.json")));
        }
    }
}

#[cfg(test)]
mod tests;
