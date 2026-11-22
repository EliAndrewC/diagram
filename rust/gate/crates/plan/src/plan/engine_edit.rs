//! Is this edit an engine edit? (feature 449 T066, from `engine_edit.py`; the guard is `engine_freeze_hooks.rs`, and it asks this only
//! once a map review or a roll is live, so an ordinary edit starts nothing). The answer belongs to `delta::is_engine`, the one list of
//! engine paths. A `.py` file's docstring-only edit passed (the GM, 2026-10-27: "We should change the rule to allow docstring edits during
//! a run, since those don't affect things"), its semantic id asked of `codeid.py`, until feature 449 T247 deleted that script with the last
//! `.py` file outside `specs/` (`ask:449-T158-codeid`): no `.py` engine file is left to edit, and a Rust file's comment edit waited before
//! and waits now.

use std::io::Read;
use std::path::Path;

use serde_json::Value;

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
pub(super) fn cli(stdin: &mut dyn Read) -> crate::Reply {
    let mut text = String::new();
    let _ = stdin.read_to_string(&mut text);
    let question: Value = serde_json::from_str(&text).unwrap_or(Value::Null);
    let word = |k: &str| question.get(k).and_then(Value::as_str).unwrap_or("");
    let (root, path) = (word("root"), word("path"));
    let wait = relative(path, root).is_some_and(|rel| is_engine(root, &rel));
    crate::Reply {
        stdout: String::new(),
        stderr: String::new(),
        code: i32::from(!wait),
    }
}

#[cfg(test)]
mod tests;
