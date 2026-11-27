//! `l7r-gate closing-split <root> <events dir> <git common dir> <F=> <T=> <run dir> <SPECIFY_FEATURE>` - the caller's files and another
//! task's, for `make closing-checks T=<task>` (451 T86, T93, T141, T303; ported from the Python block `scripts/gates/closing-checks.sh`
//! carried, 451 T311: the repository holds no Python since feature 449). The rules are the script's header's; this is their one copy.
//!
//! It writes `<run dir>/caller-files` (a path a line) and `<run dir>/others` (`<path>\t<task>@<feature> ...`), then, unless refused,
//! `feature` and `judged`; it prints the split, or a refusal, on stdout, which the script keeps as `split.txt`. Exit 0: split; 3: REFUSED
//! (no feature for the task, or none of the uncommitted files is one the task's own edits name); 1: git could not be read, and the
//! script judges every file as the caller's.
//!
//! Where the Python did otherwise, on cases no run met (observed 2026-11-27, the fixture suite `tests/hooks/test-closing-checks.sh`
//! green on both): an edit line whose time does not parse claims nothing, where the Python stopped with a traceback and the run fell
//! back to judging every file as the caller's; a task named by a non-string value claims nothing; the start marks are read through
//! `marks::all`, which also reads the main worktree's one-mark file of before 451 T254.

use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::builder_pool::{self, Tree};
use l7r_shared::speckit::marks;
use serde_json::Value;

use crate::{git, reply, Reply};

const USAGE: &str =
    "usage: l7r-gate closing-split <root> <events dir> <common dir> <feature> <task> <run dir> <exported feature>\n";
/// How far back a file's last commit is looked for: an edit line older than it claims nothing (a GUESS window, 7 days).
const WINDOW: f64 = 7.0 * 86_400.0;

/// A landing's commit subject: `<feature>: T.. T.. ticked (make land)`.
static LANDED: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(r"^(\S+): ((?:T\d+ )+)ticked \(make land\)")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// What the split reads: the arguments, and the clone's state as read from git, the pool, the marks and the event logs.
pub struct World<'a> {
    /// the clone's top, as `git rev-parse --show-toplevel` prints it
    pub root: &'a str,
    pub common: &'a Path,
    /// `F=` and `SPECIFY_FEATURE`
    pub feature: &'a str,
    pub exported: &'a str,
    pub task: &'a str,
    pub pool: Vec<Tree>,
    pub marks: Vec<Value>,
    /// the clone's uncommitted files
    pub dirty: BTreeSet<String>,
    /// `git log --since=7.days --format='@%ct %s' --name-only`
    pub log: &'a str,
    /// each event log's file stem and text, in their files' order
    pub events: Vec<(String, String)>,
    pub now: f64,
}

/// The split's answer: what it prints, its exit, and each file written into the run's directory.
#[derive(Debug, PartialEq, Eq)]
pub struct Split {
    pub stdout: String,
    pub code: i32,
    pub files: Vec<(&'static str, String)>,
}

/// One claim on a file: the feature (an event log's stem) and the task.
type Claim = (String, String);

/// The task's feature and where it came from (451 T303): `F=`, `SPECIFY_FEATURE`, the pool registry's holder of this tree, this tree's
/// newest start mark naming one of the tasks; none of them, `("", "")`.
fn feature_of(w: &World, tasks: &BTreeSet<String>) -> (String, &'static str) {
    let root = Path::new(w.root);
    let here = |p: &str| !p.is_empty() && marks::same_tree(Path::new(p), root);
    let held = w
        .pool
        .iter()
        .find(|t| {
            here(&t.tree.to_string_lossy())
                && !t.feature.is_empty()
                && t.tasks.iter().any(|k| tasks.contains(k))
        })
        .map(|t| t.feature.clone())
        .unwrap_or_default();
    // the newest by `utc`, the first of a tie, as Python's max kept
    let mut marked: Option<&Value> = None;
    for m in &w.marks {
        let feature = m["feature"].as_str().unwrap_or_default();
        let ours = here(m["tree"].as_str().unwrap_or_default())
            && !feature.is_empty()
            && marks::tasks_of(m).iter().any(|k| tasks.contains(k));
        let utc = |v: &Value| v["utc"].as_str().unwrap_or_default().to_owned();
        if ours && marked.is_none_or(|b| utc(m) > utc(b)) {
            marked = Some(m);
        }
    }
    let marked = marked
        .and_then(|m| m["feature"].as_str())
        .unwrap_or_default();
    let found = [
        (w.feature, "F="),
        (w.exported, "SPECIFY_FEATURE"),
        (held.as_str(), "the pool registry's holder of this tree"),
        (marked, "this tree's start mark"),
    ]
    .into_iter()
    .find(|(f, _)| !f.is_empty())
    .map_or((String::new(), ""), |(f, s)| (f.to_owned(), s));
    found
}

/// Each file's last commit in the window, and each landed task's newest landing (`(feature, task)`), from the log's text.
fn commits(log: &str) -> (BTreeMap<String, f64>, BTreeMap<Claim, f64>) {
    let (mut last, mut landed, mut at) = (BTreeMap::new(), BTreeMap::new(), 0.0);
    for l in log.lines() {
        if let Some(head) = l.strip_prefix('@') {
            let (secs, subject) = head.split_once(' ').unwrap_or((head, ""));
            at = secs.parse().unwrap_or(0.0);
            if let Ok(Some(c)) = LANDED.captures(subject) {
                for t in c[2].split_whitespace() {
                    landed.entry((c[1].to_owned(), t.to_owned())).or_insert(at);
                }
            }
        } else if !l.is_empty() {
            last.entry(l.to_owned()).or_insert(at);
        }
    }
    (last, landed)
}

/// Python's truth of a JSON value.
fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

/// Every uncommitted file some task's edit line names since that file's last commit and that task's last landing, with its claims.
fn claims(w: &World) -> BTreeMap<String, BTreeSet<Claim>> {
    let (last, landed) = commits(w.log);
    let since = w.now - WINDOW;
    let pre = format!("{}/", w.root.trim_end_matches('/'));
    let mut out: BTreeMap<String, BTreeSet<Claim>> = BTreeMap::new();
    for (stem, text) in &w.events {
        for l in text.lines() {
            // an edit tool's end names its path; a Bash call's end its `writes`, the files the tree walk says it wrote (451 T93)
            let edit = l.contains("\"PostToolUse\"") && l.contains("\"cat\":\"edit\"");
            if !edit && !l.contains("\"writes\":") {
                continue;
            }
            let Ok(d) = serde_json::from_str::<Value>(l) else {
                continue;
            };
            let Some(task) = d["task"].as_str().filter(|t| !t.is_empty()) else {
                continue;
            };
            let ev = d["ev"].as_str().unwrap_or_default();
            if truthy(&d["fallback"]) || !ev.starts_with("PostToolUse") {
                continue;
            }
            let named = edit.then(|| &d["path"]).into_iter();
            let writes = d["writes"].as_array().into_iter().flatten();
            // an exact path, never a prefix: a write the walk places where the shell stands is a directory, and claims no file in it
            let rels: BTreeSet<&str> = named
                .chain(writes)
                .filter_map(Value::as_str)
                .filter_map(|p| p.strip_prefix(&pre))
                .filter(|r| w.dirty.contains(*r))
                .collect();
            let Some(at) = d["t"]
                .as_str()
                .map(|t| t.replace('Z', "+00:00"))
                .and_then(|t| l7r_shared::iso::parse(&t))
            else {
                continue;
            };
            let claim = (stem.clone(), task.to_owned());
            if at < landed.get(&claim).copied().unwrap_or(0.0) {
                continue;
            }
            for rel in rels {
                if at >= last.get(rel).copied().unwrap_or(since) {
                    out.entry(rel.to_owned()).or_default().insert(claim.clone());
                }
            }
        }
    }
    out
}

/// `\n  <key>: <up to six paths>[ ...]` a key, in the keys' order.
fn listed(by: &BTreeMap<String, Vec<String>>) -> String {
    let mut out = String::new();
    for (t, rs) in by {
        let more = if rs.len() > 6 { " ..." } else { "" };
        let shown: Vec<&str> = rs.iter().take(6).map(String::as_str).collect();
        let _ = write!(out, "\n  {t}: {}{more}", shown.join(", "));
    }
    out
}

/// The split of `w`'s uncommitted files between the caller's task and another's.
#[must_use]
pub fn split(w: &World) -> Split {
    let task = w.task;
    // a bundle, T=a,b,c (451 T141): its tasks' files judged together, as one task's
    let tasks: BTreeSet<String> = task
        .split(|c: char| c == ',' || c.is_whitespace())
        .filter(|t| !t.is_empty())
        .map(str::to_owned)
        .collect();
    let (feature, source) = feature_of(w, &tasks);
    if feature.is_empty() {
        let pool = w.common.join(builder_pool::FILE);
        let stdout = format!("closing-checks: REFUSED - T={task} names no feature, and a task number alone is several features': no F=, no SPECIFY_FEATURE exported, {} holds this tree for no such task, and this tree has no start mark of it. Run:\n  make closing-checks T={task} F=<feature>\n", pool.display());
        return Split {
            stdout,
            code: 3,
            files: Vec::new(),
        };
    }
    let prefix = format!("{feature}-");
    let mine_f = w
        .events
        .iter()
        .map(|(s, _)| s)
        .find(|s| **s == feature || s.starts_with(&prefix))
        .cloned()
        .unwrap_or_else(|| feature.clone());
    let mine = |c: &Claim| c.0 == mine_f && tasks.contains(&c.1);
    let claims = claims(w);
    let others: BTreeMap<&String, &BTreeSet<Claim>> =
        claims.iter().filter(|(_, c)| !c.iter().any(mine)).collect();
    let caller: Vec<&String> = w.dirty.iter().filter(|r| !others.contains_key(r)).collect();
    let mut listing = String::new();
    for r in &caller {
        let _ = writeln!(listing, "{r}");
    }
    let mut theirs = String::new();
    for (r, c) in &others {
        let named: Vec<String> = c.iter().map(|(f, t)| format!("{t}@{f}")).collect();
        let _ = writeln!(theirs, "{r}\t{}", named.join(" "));
    }
    let mut files = vec![("caller-files", listing), ("others", theirs)];
    let by = |key: &dyn Fn(&Claim) -> String| {
        let mut by: BTreeMap<String, Vec<String>> = BTreeMap::new();
        for (r, c) in &others {
            for claim in *c {
                by.entry(key(claim)).or_default().push((*r).clone());
            }
        }
        by
    };
    let named = caller.iter().filter(|r| claims.contains_key(**r)).count();
    let (n, o, d) = (caller.len(), others.len(), w.dirty.len());
    if !others.is_empty() && named == 0 {
        // each with its feature here: the same number under another feature is the likely cause; nothing of the task's own would be
        // judged (451 T303), so refused before a check runs, never a GREEN over none of its files
        let apart = listed(&by(&|(f, t)| format!("{t}@{f}")));
        let stdout = format!("closing-checks: REFUSED - no uncommitted file here is one {task}'s own edits name under feature {mine_f} (from {source}), while {o} of the clone's {d} are set apart as another task's:{apart}\na run that judges none of the task's own files says nothing of it. If those are {task}'s under another feature, run:\n  make closing-checks T={task} F=<feature>\nor judge every file here as yours:\n  make closing-checks\n");
        return Split {
            stdout,
            code: 3,
            files,
        };
    }
    let apart = listed(&by(&|(_, t)| t.clone()));
    files.push(("feature", format!("{feature}\n")));
    files.push(("judged", format!("{n} files judged as {task}'s of {mine_f}, {named} of them its own edits name; {o} set apart as another task's\n")));
    let stdout = format!("closing-checks: judged as {task}'s: {n} of the clone's {d} uncommitted files ({named} its own edits name, {} no task's edit); another task's, its red reported apart: {o}; the task's feature: {mine_f} (from {source}){apart}\n", n - named);
    Split {
        stdout,
        code: 0,
        files,
    }
}

/// The clone's uncommitted files from `git status --porcelain=v1 -z -uall`: a rename's or copy's old path, which follows it, skipped.
fn dirty_of(status: &str) -> BTreeSet<String> {
    let (mut out, mut recs) = (BTreeSet::new(), status.split('\0'));
    while let Some(r) = recs.next() {
        if r.len() > 3 {
            out.insert(r[3..].to_owned());
            if r.starts_with(['R', 'C']) {
                recs.next();
            }
        }
    }
    out
}

/// `git <args>` in `root` as text, or the failure the script reports.
fn git_text(root: &Path, args: &[&str]) -> Result<String, String> {
    match git(root, args) {
        (Some(0), out) => Ok(String::from_utf8_lossy(&out).into_owned()),
        _ => Err(format!(
            "closing-checks: git {} failed in {}\n",
            args.join(" "),
            root.display()
        )),
    }
}

/// `l7r-gate closing-split ...` (the module's head): the clone read, the split made and its files written into the run's directory.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let [root, events, common, feature, task, out, exported] = args else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    let top = Path::new(root);
    let read = || -> Result<(String, String), String> {
        Ok((
            git_text(top, &["status", "--porcelain=v1", "-z", "-uall"])?,
            git_text(
                top,
                &["log", "--since=7.days", "--format=@%ct %s", "--name-only"],
            )?,
        ))
    };
    let (status, log) = match read() {
        Ok(read) => read,
        Err(e) => return reply(e, String::new(), 1),
    };
    let mut logs: Vec<PathBuf> = std::fs::read_dir(events)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        // as Python's glob `*.jsonl` lists them: a dot file is not one
        .filter(|p| p.extension().is_some_and(|x| x == "jsonl"))
        .filter(|p| {
            !p.file_name()
                .is_some_and(|n| n.to_string_lossy().starts_with('.'))
        })
        .collect();
    logs.sort();
    let events = logs
        .iter()
        .map(|p| {
            let stem = p
                .file_stem()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned();
            let bytes = std::fs::read(p).unwrap_or_default();
            (stem, String::from_utf8_lossy(&bytes).into_owned())
        })
        .collect();
    let common = Path::new(common);
    let world = World {
        root,
        common,
        feature,
        exported,
        task,
        pool: builder_pool::read(common),
        marks: marks::all(common),
        dirty: dirty_of(&status),
        log: &log,
        events,
        now: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_or(0.0, |t| t.as_secs_f64()),
    };
    let s = split(&world);
    for (name, text) in &s.files {
        if let Err(e) = crate::write_file(&Path::new(out).join(name), text.as_bytes()) {
            return reply(format!("closing-checks: {e}\n"), String::new(), 1);
        }
    }
    reply(s.stdout, String::new(), s.code)
}

#[cfg(test)]
mod tests;
