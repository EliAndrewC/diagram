//! A REBUILT FILE (feature 449 T152, `ask:449-T152-rebuilt-claims`): a `.py` file a phase task deleted after rebuilding its job in Rust
//! from a derivation judged SOUND, blind to the old code (the GM 2026-10-30 and 2026-11-19, engine-plan.md: "An algorithm is rebuilt,
//! never ported"). A rebuild has no port by design - no Rust unit inherits the old claim text, the new code carrying its own `Research:`
//! lines, each owed a fresh check - and its rules were not overruled by research, so neither `ports` nor `retired` fits; holding the new
//! code to the old claims' wording would carry the Python's mistakes into it. So the map's `rebuilt` names the FILE (not each unit),
//! with the phase task that rebuilt it (`by`), the Rust module or directory doing its job now (`as`, a path or a list of paths in the
//! tree, each covering the claims of the files at or under it) and that task's derivation (`derivation`).
//!
//! THE TIE TO ITS TASK (the ruling's condition 1, read at [`load`](super::load)): the file is named, literally or by a glob, on the
//! `by` task's `old-code:` line in its feature's `tasks.md` or `tasks-done.md`; `derivation` is that block's `derivation:` line as
//! written; the derivation and every `as` path are in the tree. A unit with its own `ports` or `retired` entry is handled there, and
//! `rebuilt` covers only the file's other units (condition 2).
//!
//! THE PUSH ([`refusals`], condition 3) refuses a rebuilt file still in the tree, and lets a merge-base claim on a gone unit of a
//! rebuilt file go only once nothing under its `as` paths is owed (`make claims-owed`) - the rebuilt code's own claims all checked - and
//! its row is dropped. `claims rekey` drops the rows and the deferred entries of those units and prints their count and derivation
//! (condition 4). Nothing here matches an old claim to the new code: the research pages and docs hold the findings, and the derivation
//! was written from them.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use serde_json::Value;

use super::PORTS;
use crate::claims::index::field;
use crate::record::repo::Fail;

/// One `rebuilt` entry: the phase task that rebuilt the file, what does its job now, and the task's derivation.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Rebuilt {
    pub by: String,
    /// The Rust module(s) or directory(ies) doing the file's job now (`as`), each a path in the tree.
    pub to: Vec<String>,
    pub derivation: String,
    /// Is the file still in the tree (the push refuses it)?
    pub present: bool,
}

/// `.py` file -> its rebuild.
pub type Rebuilds = BTreeMap<String, Rebuilt>;

/// The rebuild covering `uid`'s file, where it has one.
#[must_use]
pub fn of<'a>(rebuilt: &'a Rebuilds, uid: &str) -> Option<&'a Rebuilt> {
    rebuilt.get(uid.split_once("::").map_or(uid, |p| p.0))
}

/// Is `key`'s path at or under one of `paths` (a directory's trailing `/` optional)?
#[must_use]
pub fn under(key: &str, paths: &[String]) -> bool {
    let path = key.split_once("::").map_or(key, |p| p.0);
    paths.iter().any(|a| {
        let a = a.trim_end_matches('/');
        path == a || path.strip_prefix(a).is_some_and(|r| r.starts_with('/'))
    })
}

/// The form a `rebuilt` entry must take, for the refusal.
const FORM: &str = "\"<path>.py\": {\"by\": \"<feature> <task>\", \"as\": \"<the Rust module or directory doing the file's job now>\" (or a list of them), \"derivation\": \"<the task's derivation file>\"}";

/// The map's `rebuilt` entries, each held to its form and tied to its phase task at `root` (condition 1).
pub(super) fn load_rebuilt(root: &Path, doc: &Value) -> Result<Rebuilds, Fail> {
    let mut out = Rebuilds::new();
    let empty = serde_json::Map::new();
    for (file, v) in doc
        .get("rebuilt")
        .and_then(Value::as_object)
        .unwrap_or(&empty)
    {
        let (by, derivation) = (field(v, "by"), field(v, "derivation"));
        let to: Vec<String> = match v.get("as") {
            Some(Value::String(s)) => vec![s.clone()],
            Some(Value::Array(a)) => a
                .iter()
                .map(|x| x.as_str().unwrap_or_default().to_owned())
                .collect(),
            _ => Vec::new(),
        };
        let pathlike = |p: &str| !p.trim().is_empty() && !p.contains("..") && !p.starts_with('/');
        if Path::new(file).extension().is_none_or(|e| e != "py")
            || file.contains("::")
            || by.split_whitespace().count() != 2
            || to.is_empty()
            || !to.iter().all(|p| pathlike(p))
            || !pathlike(derivation)
        {
            return Err(format!(
                "{PORTS}: the rebuilt entry `{file}` is not of the form {FORM}"
            ));
        }
        if let Some(gone) = to.iter().find(|p| !root.join(p).exists()) {
            return Err(format!("{PORTS}: the rebuilt entry `{file}` names `as` {gone}, which is no file or directory in the tree: name the Rust module that does the file's job now"));
        }
        if !root.join(derivation).is_file() {
            return Err(format!("{PORTS}: the rebuilt entry `{file}` names the derivation {derivation}, which is no file in the tree: name the derivation {by} was rebuilt from"));
        }
        tied(root, file, by, derivation)?;
        out.insert(
            file.clone(),
            Rebuilt {
                by: by.to_owned(),
                to,
                derivation: derivation.to_owned(),
                present: root.join(file).exists(),
            },
        );
    }
    Ok(out)
}

/// Is the entry tied to its phase task: `file` on `by`'s `old-code:` line, `derivation` its `derivation:` line?
fn tied(root: &Path, file: &str, by: &str, derivation: &str) -> Result<(), Fail> {
    let block = task_block(root, by).ok_or_else(|| format!("{PORTS}: the rebuilt entry `{file}` is rebuilt by {by}, which is no task of its feature's tasks.md or tasks-done.md: name the phase task (`<feature> <task>`) whose `old-code:` line names the file"))?;
    let words = |name: &str| -> Vec<String> {
        block
            .lines()
            .filter_map(|l| l.trim_start().strip_prefix(name))
            .flat_map(|rest| {
                rest.split_whitespace()
                    .map(str::to_owned)
                    .collect::<Vec<_>>()
            })
            .collect()
    };
    if !words("old-code:").iter().any(|w| glob_match(w, file)) {
        return Err(format!("{PORTS}: the rebuilt entry `{file}` is not on {by}'s `old-code:` line, literally or by a glob: a file is rebuilt only by the phase task whose old code it is - name that task under `by`, or add the file to its `old-code:` line"));
    }
    let line = words("derivation:");
    if line.first().map(String::as_str) != Some(derivation) {
        let read = line.first().map_or_else(
            || "has no `derivation:` line".to_owned(),
            |d| format!("reads {d}"),
        );
        return Err(format!("{PORTS}: the rebuilt entry `{file}` names the derivation {derivation}, but {by}'s block {read}: name the derivation the task was rebuilt from, as its `derivation:` line writes it (give the block that line where it has none)"));
    }
    Ok(())
}

/// The block of the task `by` (`<feature> <task>`) in `specs/<feature>-*/`'s tasks.md or tasks-done.md: its box line and the lines
/// under it, to the next column-0 `- [` or `## `.
fn task_block(root: &Path, by: &str) -> Option<String> {
    let (feature, task) = by.split_once(' ')?;
    let mut dirs: Vec<_> = std::fs::read_dir(root.join("specs"))
        .ok()?
        .filter_map(Result::ok)
        .filter(|e| {
            e.file_name()
                .to_string_lossy()
                .starts_with(&format!("{feature}-"))
        })
        .map(|e| e.path())
        .collect();
    dirs.sort();
    let text = l7r_shared::speckit::tasks::all_text(dirs.first()?).ok()?;
    let mut out: Option<String> = None;
    for line in text.lines() {
        let boxed = line.starts_with("- [");
        if let Some(block) = out.as_mut() {
            if boxed || line.starts_with("## ") {
                break;
            }
            block.push_str(line);
            block.push('\n');
        } else if boxed && line.get(6..).is_some_and(|r| is_task(r, task)) {
            out = Some(format!("{line}\n"));
        }
    }
    out
}

/// Does `rest` (a box line after `- [x] `) open with the task id `task`, a word boundary after it?
fn is_task(rest: &str, task: &str) -> bool {
    rest.strip_prefix(task)
        .is_some_and(|r| !r.starts_with(|c: char| c.is_alphanumeric() || c == '_'))
}

/// Does the glob `pat` match the path `path`, as `Path.glob` would match the file were it there: `*` and `?` within one segment, `**`
/// any number of segments (the file is deleted, so the tree cannot be globbed)?
#[must_use]
pub fn glob_match(pat: &str, path: &str) -> bool {
    let p: Vec<&str> = pat.split('/').collect();
    let s: Vec<&str> = path.split('/').collect();
    segments(&p, &s)
}

fn segments(p: &[&str], s: &[&str]) -> bool {
    match (p.first(), s.first()) {
        (None, None) => true,
        (Some(&"**"), _) => segments(&p[1..], s) || (!s.is_empty() && segments(p, &s[1..])),
        (Some(a), Some(b)) => segment(a.as_bytes(), b.as_bytes()) && segments(&p[1..], &s[1..]),
        _ => false,
    }
}

fn segment(p: &[u8], s: &[u8]) -> bool {
    match (p.first(), s.first()) {
        (None, None) => true,
        (Some(b'*'), _) => segment(&p[1..], s) || (!s.is_empty() && segment(p, &s[1..])),
        (Some(b'?'), Some(_)) => segment(&p[1..], &s[1..]),
        (Some(a), Some(b)) => a == b && segment(&p[1..], &s[1..]),
        _ => false,
    }
}

/// The push's refusals of the rebuilt files: each still in the tree; and, for each whose merge-base claims on gone units (`stranded`,
/// file -> keys) wait to go, any claim still owed under its `as` paths (`owed`, the tree's owed keys) or a row of them the tree's index
/// (`held`) still holds.
pub fn refusals(
    rebuilt: &Rebuilds,
    stranded: &BTreeMap<String, Vec<String>>,
    owed: &[String],
    held: &dyn Fn(&str) -> bool,
) -> Vec<String> {
    let mut out = Vec::new();
    for (file, rb) in rebuilt.iter().filter(|(_, rb)| rb.present) {
        out.push(format!("unported: {file} - rebuilt ({}) but still present: {PORTS}'s `rebuilt` names a file deleted once {} rebuilt its job as {}; delete the file, or take it out of `rebuilt`", rb.by, rb.by, rb.to.join(", ")));
    }
    for (file, keys) in stranded {
        let Some(rb) = rebuilt.get(file).filter(|rb| !rb.present) else {
            continue;
        };
        let due: BTreeSet<&str> = owed
            .iter()
            .map(String::as_str)
            .filter(|k| under(k, &rb.to))
            .collect();
        if let Some(first) = due.first() {
            out.push(format!("unported: {} claim(s) of {file}, rebuilt by {} as {} - {} claim(s) of the rebuilt code still owed (first {first}): its old claims go only once the code doing its job now is checked - `make claims-owed`, then the claims round (ask:449-T152-rebuilt-claims)", keys.len(), rb.by, rb.to.join(", "), due.len()));
            continue;
        }
        let rows = keys.iter().filter(|k| held(k)).count();
        if rows > 0 {
            out.push(format!("unported: {rows} claim row(s) of {file}, rebuilt by {} ({}), not yet dropped: `make claims-rekey` (make land runs it)", rb.by, rb.derivation));
        }
    }
    out
}

#[cfg(test)]
mod tests;
