//! A task whose change is wording alone owes no plan review; the tick checks that it was (feature 385 T118, D137/D138; `gates/wording.py`,
//! ported by feature 449 T131).
//!
//! WHY (the GM 2026-10-19, amendment 10: "I would also like to implement all 3 of your suggestions" - the third, "skip the plan review for
//! wording-only tasks that decide nothing new"). A task's Decisions block holding `**Wording only.** <what is reworded>` and no
//! `**D<n> - ` line declares it (the plan gate's `wording_only`); `make tick` refuses it when a commit since its `make task-start` changed
//! anything but the feature's records, a glossary entry, or a `.py` file outside what runs.
//!
//! "Changed in what runs" for a `.py` file is `codeid.py`'s `semantic_bytes`, which only `CPython`'s `ast` can say (feature 449 T062), so
//! every pair of versions the check needs is put to ONE `codeid.py --ids` (equal ids, equal semantic bytes), where the Python loaded
//! `codeid.py` once and asked it per pair.

use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::speckit::splitlines;
use serde_json::Value;

use crate::tick::text::re;
use crate::tick::Raise;
use crate::{common_text, git, read_strict};

const WORDING: &str = "**Wording only.**";

/// What a wording-only task may change beside `.py` comments, docstrings and claims: its feature's records, the run records, and a
/// glossary entry (a word's definition, which the page check reads).
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

/// One `codeid.py --ids` over each pair's two versions, written under a scratch directory with a `.py` name (the suffix is what
/// `semantic_bytes` reads); for each pair, are they the same in what runs?
fn same_pairs(tree: &Path, pairs: &[(Vec<u8>, Vec<u8>)]) -> Raise<Vec<bool>> {
    if pairs.is_empty() {
        return Ok(Vec::new());
    }
    let dir = l7r_guard::shared::tempdir::TempDir::new("task-wording");
    let mut names = Vec::with_capacity(pairs.len() * 2);
    for (i, (a, b)) in pairs.iter().enumerate() {
        for (side, data) in [("a", a), ("b", b)] {
            let path = dir.path().join(format!("{i}-{side}.py"));
            crate::write_file(&path, data)?;
            names.push(path);
        }
    }
    let script = tree.join("scripts/gates/codeid.py");
    // a python3 that cannot start reads as one that answered nothing: either way the check cannot say
    let done = Command::new("python3")
        .arg(&script)
        .arg("--ids")
        .args(&names)
        .output()
        .ok();
    let (ok, out, err) = done.map_or((false, Vec::new(), Vec::new()), |d| {
        (d.status.success(), d.stdout, d.stderr)
    });
    let out = String::from_utf8_lossy(&out).into_owned();
    let ids: Vec<&str> = out.split_whitespace().collect();
    if !ok || ids.len() != names.len() {
        return Err(format!(
            "{} could not say: {}",
            script.display(),
            String::from_utf8_lossy(&err).trim()
        ));
    }
    Ok(ids.chunks(2).map(|p| p[0] == p[1]).collect())
}

/// Every file a commit since `since` (merges skipped: main's work is not the task's) changed beyond wording (D138).
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `endswith(\".py\")`, which is case-sensitive"
)]
fn changed_in_what_runs(root: &Path, tree: &Path, since: &str) -> Raise<Vec<String>> {
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
    for c in l7r_guard::shared::py_text::split(&revs) {
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
    // the pairs to ask, every `.py` both of whose versions git shows
    let mut pairs: Vec<(Vec<u8>, Vec<u8>)> = Vec::new();
    let mut at: Vec<(String, String)> = Vec::new();
    for (c, files) in &changes {
        for f in files
            .iter()
            .filter(|f| f.ends_with(".py") && !FREE.is_match(f).unwrap_or(false))
        {
            let (b_rc, before) = git(root, &["show", &format!("{c}^:{f}")]);
            let (a_rc, after) = git(root, &["show", &format!("{c}:{f}")]);
            if b_rc == Some(0) && a_rc == Some(0) {
                pairs.push((before, after));
                at.push((c.clone(), f.clone()));
            }
        }
    }
    let same = same_pairs(tree, &pairs)?;
    let mut out: Vec<String> = Vec::new();
    for (c, files) in &changes {
        for f in files {
            if f.is_empty() || out.contains(f) || FREE.is_match(f).unwrap_or(false) {
                continue;
            }
            let k = at.iter().position(|(ac, af)| ac == c && af == f);
            if k.is_some_and(|k| same[k]) {
                continue;
            }
            out.push(f.clone());
        }
    }
    Ok(out)
}

/// Why a wording-only task may not tick: a commit since its start changed a file beyond wording; "" otherwise (D138).
///
/// # Errors
/// What the Python raised: an unreadable start log, a row that is not an object, `codeid.py` failing.
/// `tree` is the gate's own, whose `scripts/gates/codeid.py` says what runs, as `wording.py` loaded the one beside it.
pub(crate) fn refusal(
    root: &Path,
    tree: &Path,
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
    let since = l7r_guard::shared::pyjson::py_str(&since);
    let off = changed_in_what_runs(root, tree, &since)?;
    Ok(off.first().map_or(String::new(), |f| {
        format!("{task}'s section says wording only, but {f} changed in what runs - write its decision (`**D<n> - `) in place of the `{WORDING}` line and `make decide`")
    }))
}

#[cfg(test)]
mod tests;
