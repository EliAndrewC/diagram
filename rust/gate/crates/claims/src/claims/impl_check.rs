//! A research feature ends with its findings checked against the code (feature 378) - `make impl-check F=NNN`, and the closing check's
//! question of every feature it is asked to close. Ported from `scripts/record/impl_check.py` by feature 449 T132
//! (`ask:449-phase3-remainder` Q2 task B): whole, no door, `scripts/claims_door.py` deleted with it, its last caller.
//!
//! WHY (the GM, 2026-10-10, specs/378-research-findings-checked-against-code/request.md): every `research record` feature has *"a task
//! in which we look up whether or not our implementation conforms"* - the link added where the code should cite the new page, a
//! mismatch *"properly annotated so that a `make claims-report` will show this item"* - without fixing the code unless the feature
//! asked; and the task is *"a tracked must be there"*. The claims machinery already holds the answer (feature 316): a `Research:` claim
//! cites a question, `impl-drift` checks it, the index keeps the verdict, and `make claims-report` lists every finding. This asks the
//! one question that was never asked: did the feature connect its findings to it?
//!
//! WHAT IS OWED by a feature tagged `research record`, for each question whose FINDINGS page (`research/questions/NNNN-<id>.html`, not
//! its `.notes`, `.drawing` or `.originals`) the feature's commits changed or created - its commits being those whose subject opens
//! with its number (`Feature NNN` or `NNN:`): (a) at least one `Research:` claim citing the question's findings page, none of them
//! owed; or (b), only for a question NO code decides, a line in the feature's `implementation-check.md`:
//! `- NNNN: no code implements it - <why>; searched: <the units and the grep that found none>`. A DRIFTED claim satisfies (a).
//!
//! WHERE (feature 449 T132): here in `claims`, which it reads in process (`current`, the index, the page store, what is owed) where the
//! Python asked them through `claims-door`. The closing check (`reviews::closing`, below `claims` in the crates) asks [`missing_each`]
//! in process through the function its callers hand it, where it ran `impl_check.py --missing-json` by path (T127's seam).

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::pyjson::dumps;
use l7r_guard::shared::speckit::splitlines;
use serde_json::Value;

use super::index::{current, load_map, owed, INDEX, QUESTIONS, STORE};
use super::scope::Reader;
use crate::record::repo::{tree_of, universal};
use crate::reviews::gm_review::name;
use crate::Reply;

const TAG: &str = "research record";
const RECORD: &str = "implementation-check.md";
/// The usage line the Python printed with no argument (its docstring's, byte for byte, `ask:449-usage-text`).
const USAGE: &str = "impl_check.py <feature dir>           what is owed and what is missing; exit 1 if anything is missing";

fn re(p: &str) -> Regex {
    Regex::new(p).unwrap_or_else(|_| unreachable!("a pattern of the code's own"))
}

/// A findings page, under the project's old place too (before feature 329 moved it to the root a commit named its pages under it; the
/// prefix split so the old-layout check, retired by feature 383, did not read it as a stale pointer).
static FINDINGS_PAGE: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"^(?:{})?research/questions/(\d{{4}})-[a-z0-9-]+\.html$",
        fancy_regex::escape(&[".claude/skills/", "diagram/"].concat())
    ))
});
/// A claim cites a question by its FINDINGS page only: a claim on the drawing page alone is fingerprinted on that page, so a rewritten
/// finding never re-owes it and it would pass on a verdict reached before the change (plan review of 378).
static CITED: LazyLock<Regex> =
    LazyLock::new(|| re(r"research/questions/(\d{4})-[a-z0-9-]+\.html$"));
static NONE_LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^-\s*(\d{4}):\s*no code implements it\s*-\s*(\S.*)$"));
/// Case (b) says what was searched, or it is a reason without a search (spec FR-001, review round 1).
static SEARCHED: LazyLock<Regex> = LazyLock::new(|| re(r";\s*searched:\s*\S"));
static AFFECTS: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\*\*Affects\*\*:?\s*(.+)$"));

/// Python's name of a JSON value's type, as an error names it.
fn py_type(v: &Value) -> &'static str {
    match v {
        Value::Null => "'NoneType'",
        Value::Bool(_) => "'bool'",
        Value::Number(n) if n.is_f64() => "'float'",
        Value::Number(_) => "'int'",
        Value::String(_) => "'str'",
        Value::Array(_) => "'list'",
        Value::Object(_) => "'dict'",
    }
}

fn matched(rx: &Regex, text: &str) -> bool {
    rx.is_match(text).unwrap_or(false)
}

/// A file as `read_text(errors="replace")` reads it: undecodable bytes replaced, newlines universal; `None` where it cannot be read.
fn read_replace(path: &Path) -> Option<String> {
    std::fs::read(path)
        .ok()
        .map(|b| universal(&String::from_utf8_lossy(&b)))
}

/// `git -C root args...`'s stdout, whatever its exit, as the Python's `check=False` run read it.
fn git(root: &Path, args: &[&str]) -> String {
    std::process::Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default()
}

fn is_research_feature(d: &Path) -> bool {
    let Some(text) = read_replace(&d.join("spec.md")) else {
        return false;
    };
    let Ok(Some(c)) = AFFECTS.captures(&text) else {
        return false;
    };
    c[1].split(',').any(|t| strip(t).to_lowercase() == TAG)
}

/// `int(s)` as Python reads a feature's number: whitespace stripped, a sign, ASCII digits with single underscores between them.
fn py_int(s: &str) -> Result<i128, String> {
    let body = strip(s);
    let digits = body.strip_prefix(['-', '+']).unwrap_or(body);
    let ok = !digits.is_empty()
        && !digits.starts_with('_')
        && !digits.ends_with('_')
        && !digits.contains("__")
        && digits.chars().all(|c| c.is_ascii_digit() || c == '_');
    let bad = || {
        format!(
            "ValueError: invalid literal for int() with base 10: {}",
            l7r_guard::shared::py_text::repr(s)
        )
    };
    if !ok {
        return Err(bad());
    }
    body.replace('_', "").parse().map_err(|_| bad())
}

/// Every question whose findings page a commit of feature `number` changed or created: the commits whose SUBJECT opens with the number
/// (git's `--grep` would also match a later line); a merge is no feature's.
fn changed_questions(root: &Path, number: i128) -> Vec<String> {
    let rx = re(&format!(r"^(Feature )?0*{number}([: ]|$)"));
    let log = git(root, &["log", "--no-merges", "--format=%H %s"]);
    let mut found: Vec<String> = Vec::new();
    for line in splitlines(&log) {
        let subject = line.split_once(' ').map_or(line, |(_, s)| s);
        if !matched(&rx, subject) {
            continue;
        }
        let sha = line.split(' ').next().unwrap_or_default();
        let tree = git(
            root,
            &[
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "--root",
                sha,
            ],
        );
        for name in tree.split_whitespace() {
            if let Ok(Some(c)) = FINDINGS_PAGE.captures(name) {
                found.push(c[1].to_owned());
            }
        }
    }
    found.sort();
    found.dedup();
    found
}

fn recorded_none(d: &Path) -> BTreeMap<String, String> {
    let text = read_replace(&d.join(RECORD)).unwrap_or_default();
    NONE_LINE
        .captures_iter(&text)
        .flatten()
        .map(|c| (c[1].to_owned(), c[2].to_owned()))
        .collect()
}

/// What a feature's report reads of the claims: (question -> the claim keys citing it, the keys owed their check, key -> its index
/// verdict as Python's `verdict.get(k) or '-'` printed it).
pub struct Cites {
    by_q: BTreeMap<String, Vec<String>>,
    due: Vec<String>,
    verdict: BTreeMap<String, Value>,
}

/// A verdict as `f"{v or '-':<14}"` prints it: a falsy value is `-`, `True` formats as the number 1; a list or an object cannot take
/// the width and raises, as `format()` raised.
fn shown(v: &Value) -> Result<String, String> {
    Ok(match v {
        Value::String(s) if !s.is_empty() => s.clone(),
        Value::Null | Value::Bool(false) | Value::String(_) => "-".to_owned(),
        Value::Number(n) if n.as_f64() == Some(0.0) => "-".to_owned(),
        Value::Bool(true) => "1".to_owned(),
        Value::Number(_) => l7r_guard::shared::pyjson::py_str(v),
        Value::Array(a) if a.is_empty() => "-".to_owned(),
        Value::Object(o) if o.is_empty() => "-".to_owned(),
        _ => {
            return Err(format!(
                "TypeError: unsupported format string passed to {}.__format__",
                if v.is_array() { "list" } else { "dict" }
            ))
        }
    })
}

/// The claims at `root`, read in process where the Python asked the door: `current`, then the index, the page store, what is owed.
///
/// # Errors
///
/// What the claims reading raised: an unreadable or broken index or store, a unit that cannot be read.
pub fn citing(root: &Path) -> Result<Cites, String> {
    let mut reader = Reader::new(&tree_of(root), root);
    let cur = current(&mut reader, root, &root.join(QUESTIONS))?;
    drop(reader);
    let index = load_map(&root.join(INDEX))?;
    let store = load_map(&root.join(STORE))?;
    let due = owed(&cur, &index, Some(&root.join(QUESTIONS)), Some(&store))?
        .into_iter()
        .map(|(k, _)| k)
        .collect();
    let mut by_q: BTreeMap<String, Vec<String>> = BTreeMap::new();
    for row in cur.iter() {
        for p in &row.claim.pointers {
            if let Ok(Some(c)) = CITED.captures(p) {
                by_q.entry(c[1].to_owned())
                    .or_default()
                    .push(row.key.clone());
            }
        }
    }
    // `{k: v.get("verdict", "")}`: a row that is no object has no `get`, and the Python raised
    let mut verdict = BTreeMap::new();
    for (k, v) in &index {
        let row = v.as_object().ok_or_else(|| {
            format!(
                "AttributeError: {} object has no attribute 'get'",
                py_type(v)
            )
        })?;
        let said = row.get("verdict").cloned();
        verdict.insert(k.clone(), said.unwrap_or_else(|| Value::from("")));
    }
    Ok(Cites { by_q, due, verdict })
}

/// (lines to print, what is missing) for feature directory `d` of `root`, the claims read by `cites` only when a question is owed.
///
/// # Errors
///
/// What the Python raised: a research feature's number that is no number, the claims reading failing.
pub fn report(
    root: &Path,
    d: &Path,
    cites: &mut dyn FnMut(&Path) -> Result<std::rc::Rc<Cites>, String>,
) -> Result<(Vec<String>, Vec<String>), String> {
    let n = name(d);
    if !is_research_feature(d) {
        return Ok((
            vec![format!(
                "impl-check: {n} is not tagged `{TAG}` - nothing is owed"
            )],
            Vec::new(),
        ));
    }
    let number = py_int(n.split('-').next().unwrap_or_default())?;
    let qs = changed_questions(root, number);
    if qs.is_empty() {
        return Ok((
            vec![format!(
                "impl-check: {n}'s commits changed no question's findings - nothing is owed"
            )],
            Vec::new(),
        ));
    }
    let c = cites(root)?;
    let nones = recorded_none(d);
    let mut lines = vec![format!(
        "impl-check: {n} changed {} question(s): {}",
        qs.len(),
        qs.join(" ")
    )];
    let mut missing = Vec::new();
    for q in &qs {
        let mut keys = c.by_q.get(q).cloned().unwrap_or_default();
        keys.sort();
        if !keys.is_empty() {
            let is_due = |k: &String| c.due.contains(k);
            let owed_n = keys.iter().filter(|k| is_due(k)).count();
            let tail = if owed_n > 0 {
                format!(", {owed_n} owed the check")
            } else {
                String::new()
            };
            lines.push(format!("  {q}: {} claim(s) cite it{tail}", keys.len()));
            for k in &keys {
                let v = shown(c.verdict.get(k).unwrap_or(&Value::Null))?;
                let mark = if is_due(k) { "  (owed)" } else { "" };
                lines.push(format!("      {v:<14} {k}{mark}"));
            }
            if owed_n > 0 {
                missing.push(format!("{q}: {owed_n} claim(s) citing it are owed their impl-drift check - `make claims-owed` names them"));
            }
        } else if let Some(why) = nones.get(q) {
            if matched(&SEARCHED, why) {
                lines.push(format!("  {q}: no code implements it - {why}"));
            } else {
                lines.push(format!(
                    "  {q}: no code implements it - {why}  (says nothing of what was searched)"
                ));
                missing.push(format!("{q}: its line in {RECORD} must say what was searched - `; searched: <the units and the grep that found none>`"));
            }
        } else {
            lines.push(format!(
                "  {q}: no claim cites it, and {RECORD} has no line for it"
            ));
            missing.push(format!("{q}: cite it in the `Research:` claim of the code that decides it (then its impl-drift check), or, only if NO code decides it, add `- {q}: no code implements it - <why>; searched: <what>` to {n}/{RECORD}"));
        }
    }
    lines.push(if missing.is_empty() {
        "impl-check: nothing missing".to_owned()
    } else {
        format!("impl-check: {} missing", missing.len())
    });
    Ok((lines, missing))
}

/// The claims of each root read once a run: the reading is the expensive part, and nothing a report does writes what it reads.
#[derive(Default)]
struct Memo(BTreeMap<PathBuf, std::rc::Rc<Cites>>);

impl Memo {
    fn get(&mut self, root: &Path) -> Result<std::rc::Rc<Cites>, String> {
        if let Some(c) = self.0.get(root) {
            return Ok(c.clone());
        }
        let c = std::rc::Rc::new(citing(root)?);
        self.0.insert(root.to_path_buf(), c.clone());
        Ok(c)
    }
}

/// `missing(d, d.resolve().parents[1])` for each of `dirs`, in order: what the closing check refuses on, each item prefixed with its
/// feature. The closing check's question (`reviews::closing::ImplCheck`), asked in process since feature 449 T132.
///
/// # Errors
///
/// What the Python raised, at the first directory that raised: a resolved path with no grandparent, a research feature's number that
/// is no number, the claims reading failing.
pub fn missing_each(dirs: &[&Path]) -> Result<Vec<Vec<String>>, String> {
    let mut memo = Memo::default();
    let mut out = Vec::with_capacity(dirs.len());
    for d in dirs {
        let real = super::flight::resolved(d);
        let root = real
            .parent()
            .and_then(Path::parent)
            .ok_or_else(|| "IndexError: 1".to_owned())?;
        let (_, miss) = report(root, d, &mut |r| memo.get(r))?;
        let n = name(d);
        out.push(
            miss.iter()
                .map(|m| format!("{n} owes its implementation check (feature 378): {m}"))
                .collect(),
        );
    }
    Ok(out)
}

fn raised(why: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("Traceback (most recent call last):\n  l7r-gate impl-check\n{why}\n"),
        code: 1,
    }
}

/// The feature directory a word names: itself when it is a directory, else the first `specs/NNN-*` under `root` in the directory's own
/// order (`next(glob)`, unsorted), else the word as a path.
fn feature_dir(word: &str, root: &Path) -> Result<PathBuf, String> {
    // `Path("")` is `.`
    let d = PathBuf::from(if word.is_empty() { "." } else { word });
    if d.is_dir() {
        return Ok(d);
    }
    let n = py_int(word)?;
    let prefix = if n < 0 {
        format!("-{:02}-", -n)
    } else {
        format!("{n:03}-")
    };
    let found = std::fs::read_dir(root.join("specs"))
        .into_iter()
        .flatten()
        .flatten()
        .find(|e| e.file_name().to_string_lossy().starts_with(&prefix))
        .map(|e| e.path());
    Ok(found.unwrap_or(d))
}

/// `l7r-gate impl-check <F | feature dir>` (`make impl-check F=`), `root` the repository whose features and claims it reads, as the
/// Python read its own (`ROOT`); `--missing-json DIR...` is the closing check's question in command form, kept so no form vanishes
/// (feature 449 T119's rule), one JSON list a directory.
#[must_use]
pub fn cli(args: &[String], root: &Path) -> Reply {
    if args.first().map(String::as_str) == Some("--missing-json") {
        let dirs: Vec<&Path> = args[1..].iter().map(Path::new).collect();
        return match missing_each(&dirs) {
            Ok(each) => Reply {
                stdout: dumps(&Value::from(each), None, true) + "\n",
                stderr: String::new(),
                code: 0,
            },
            Err(why) => raised(&why),
        };
    }
    let Some(word) = args.first() else {
        return Reply {
            stdout: String::new(),
            stderr: format!("{USAGE}\n"),
            code: 2,
        };
    };
    let run = || -> Result<(Vec<String>, Vec<String>), String> {
        let d = feature_dir(word, root)?;
        let mut memo = Memo::default();
        report(root, &d, &mut |r| memo.get(r))
    };
    match run() {
        Ok((lines, miss)) => Reply {
            stdout: lines.join("\n") + "\n",
            stderr: String::new(),
            code: i32::from(!miss.is_empty()),
        },
        Err(why) => raised(&why),
    }
}

#[cfg(test)]
mod tests;
