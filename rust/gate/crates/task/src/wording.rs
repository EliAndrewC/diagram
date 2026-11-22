//! A task whose change is wording alone owes no plan review; the tick checks that it was (feature 385 T118, D137/D138; `gates/wording.py`,
//! ported by feature 449 T131).
//!
//! WHY (the GM 2026-10-19, amendment 10: "I would also like to implement all 3 of your suggestions" - the third, "skip the plan review for
//! wording-only tasks that decide nothing new"). A task's Decisions block holding `**Wording only.** <what is reworded>` and no
//! `**D<n> - ` line declares it (the plan gate's `wording_only`); `make tick` refuses it when a commit since its `make task-start` changed
//! anything but the feature's records or a glossary entry.
//!
//! A `.py` file changed only outside what runs (its comments, docstrings and claims) passed too, its `semantic_bytes` asked of `codeid.py`
//! (feature 449 T062), until feature 449 T247 deleted that script with the last `.py` file outside `specs/` (`ask:449-T158-codeid`): every
//! file a commit changed is a change in what runs now, but those three kinds.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::speckit::splitlines;
use serde_json::Value;

use crate::tick::text::re;
use crate::tick::Raise;
use crate::{common_text, git, read_strict};

const WORDING: &str = "**Wording only.**";

/// What a wording-only task may change: its feature's records, the run records, and a glossary entry (a word's definition, which the page check reads).
static FREE: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(specs/|dev/|l7r/diagram/interactive/assets/glossary/[^/]+\.json$)"));

/// The UTC of the task's last `make task-start`, from `task-starts.jsonl`; "" when it has none (a row's `utc` as Python's `str` gives it).
fn started(root: &Path, feature: &str, task: &str) -> Raise<Value> {
    let common = common_text(root);
    let mut last = Value::from("");
    if common.is_empty() {
        return Ok(last);
    }
    let log = PathBuf::from(common).join("task-starts.jsonl");
    if !log.is_file() {
        return Ok(last);
    }
    for line in splitlines(&read_strict(&log)?) {
        let Ok(row) = serde_json::from_str::<Value>(line) else {
            continue;
        };
        let Value::Object(map) = &row else {
            return Err("AttributeError: the row has no attribute 'get'".to_owned());
        };
        if map.get("feature") == Some(&Value::from(feature))
            && map.get("task") == Some(&Value::from(task))
        {
            last = map.get("utc").cloned().unwrap_or_else(|| Value::from(""));
        }
    }
    Ok(last)
}

/// git's output as text: its names are quoted (`core.quotepath`), so it is ASCII, which the Python's `decode()` never failed on.
fn text_of(out: &[u8]) -> String {
    String::from_utf8_lossy(out).into_owned()
}

/// Every file a commit since `since` (merges skipped: main's work is not the task's) changed beyond wording (D138).
fn changed_in_what_runs(root: &Path, since: &str) -> Vec<String> {
    let (_, revs) = git(
        root,
        &[
            "rev-list",
            "--no-merges",
            &format!("--since={since}"),
            "HEAD",
        ],
    );
    let revs = text_of(&revs);
    let mut changes: Vec<(String, Vec<String>)> = Vec::new();
    for c in l7r_shared::py_text::split(&revs) {
        let (_, names) = git(
            root,
            &[
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--root",
                c,
            ],
        );
        let names = text_of(&names);
        changes.push((
            c.to_owned(),
            splitlines(&names).into_iter().map(str::to_owned).collect(),
        ));
    }
    let mut out: Vec<String> = Vec::new();
    for (_, files) in &changes {
        for f in files {
            if f.is_empty() || out.contains(f) || FREE.is_match(f).unwrap_or(false) {
                continue;
            }
            out.push(f.clone());
        }
    }
    out
}

/// Why a wording-only task may not tick: a commit since its start changed a file beyond wording; "" otherwise (D138).
///
/// # Errors
/// What the Python raised: an unreadable start log, a row that is not an object.
pub(crate) fn refusal(
    root: &Path,
    spec_dir: &Path,
    task: &str,
    section: Option<&str>,
) -> Raise<String> {
    if !section.is_some_and(l7r_gate_plan::plan::section_wording_only) {
        return Ok(String::new());
    }
    let name = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    let since = started(root, &name, task)?;
    let falsy = match &since {
        Value::Null => true,
        Value::String(s) => s.is_empty(),
        Value::Bool(b) => !b,
        Value::Number(n) => n.as_f64() == Some(0.0),
        Value::Array(a) => a.is_empty(),
        Value::Object(o) => o.is_empty(),
    };
    if falsy {
        return Ok(format!("{task}'s section says wording only, but it has no `make task-start` to read its commits from - start it, then tick"));
    }
    let since = l7r_shared::pyjson::py_str(&since);
    let off = changed_in_what_runs(root, &since);
    Ok(off.first().map_or(String::new(), |f| {
        format!("{task}'s section says wording only, but {f} changed in what runs - write its decision (`**D<n> - `) in place of the `{WORDING}` line and `make decide`")
    }))
}

#[cfg(test)]
mod tests;
