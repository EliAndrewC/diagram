//! Is this edit an engine edit, and more than a docstring? (feature 449 T066, from `engine_edit.py`; the guard is
//! `engine_freeze_hooks.rs`, and it asks this only once a map review or a roll is live, so an ordinary edit starts nothing). The answers
//! belong to what this reads: `delta::is_engine`, the one list of engine paths, and the stamp's semantic identity of a Python file. The
//! GM, 2026-10-27: "We should change the rule to allow docstring edits during a run, since those don't affect things".

use std::io::Read;
use std::path::Path;

use serde_json::Value;

use crate::codeid;

/// The semantic id of these bytes as a Python file, or None when it cannot be taken. (Python reads the id from a file on disk.)
fn semantic(data: &[u8], root: &Path, python: &str) -> Option<String> {
    let dir = crate::checks::scratch("engine-edit");
    let file = dir.join("edit.py");
    let _ = std::fs::write(&file, data);
    let files = [(file, data.to_vec())];
    let ids = codeid::content_ids(
        &files,
        &mut codeid::Cache::at(root),
        python,
        &codeid::script(root),
    );
    let _ = std::fs::remove_dir_all(&dir);
    ids.ok()?.into_iter().next()
}

/// The file's text after the edit, or None when the edit cannot be applied.
fn edited(old: &[u8], tool: &str, input: &Value) -> Option<Vec<u8>> {
    let field = |k: &str| input.get(k).and_then(Value::as_str).unwrap_or("");
    if tool == "Write" {
        return Some(field("content").as_bytes().to_vec());
    }
    let current = String::from_utf8_lossy(old);
    let (from, to) = (field("old_string"), field("new_string"));
    if !current.contains(from) {
        return None;
    }
    let all = input
        .get("replace_all")
        .is_some_and(|v| v.as_bool().unwrap_or(false));
    Some(
        if all {
            current.replace(from, to)
        } else {
            current.replacen(from, to, 1)
        }
        .into_bytes(),
    )
}

/// Does the edit change only docstrings and comments of a `.py` file? Never in the byte-hashed areas (the interactive page's class
/// docstrings are the modal text a review reads), and never for a `NotebookEdit` or a file that cannot be read.
fn docstring_only(rel: &str, path: &str, input: &Value, tool: &str, python: &str) -> bool {
    if !crate::checks::has_ext(rel, "py") || !["Edit", "Write"].contains(&tool) {
        return false;
    }
    let Ok(old) = std::fs::read(path) else {
        return false;
    };
    let Some(new) = edited(&old, tool, input) else {
        return false;
    };
    let tree = path
        .strip_suffix(rel)
        .filter(|t| !t.is_empty())
        .unwrap_or(".");
    let root = Path::new(tree);
    if crate::stamp::in_raw_area(root, rel) {
        return false;
    }
    semantic(&old, root, python)
        .zip(semantic(&new, root, python))
        .is_some_and(|(a, b)| a == b)
}

fn is_engine(root: &str, rel: &str) -> bool {
    Path::new(root).join("scripts/gates/l7r-gate.sh").is_file() && crate::delta::is_engine(rel)
}

/// The path with its existing part resolved, the rest kept: a new file or package has no real path of its own.
fn real(path: &Path) -> std::path::PathBuf {
    for above in path.ancestors() {
        if let Ok(found) = std::fs::canonicalize(above) {
            return found.join(path.strip_prefix(above).unwrap_or(Path::new("")));
        }
    }
    path.to_owned()
}

fn relative(path: &str, root: &str) -> Option<String> {
    let (full, top) = (real(Path::new(path)), real(Path::new(root)));
    full.strip_prefix(top)
        .ok()
        .map(|p| p.to_string_lossy().into_owned())
}

/// `{"root", "path", "tool", "tool_input"}` on stdin: exit 0 for an engine edit that must wait, 1 otherwise.
pub(super) fn cli(stdin: &mut dyn Read, python: &str) -> crate::Reply {
    let mut text = String::new();
    let _ = stdin.read_to_string(&mut text);
    let question: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
    let word = |k: &str| question.get(k).and_then(Value::as_str).unwrap_or("");
    let (root, path) = (word("root"), word("path"));
    let wait = relative(path, root).is_some_and(|rel| {
        is_engine(root, &rel)
            && !docstring_only(&rel, path, &question["tool_input"], word("tool"), python)
    });
    crate::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: i32::from(!wait),
    }
}

#[cfg(test)]
mod tests;
