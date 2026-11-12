//! Every reason `make tick` refuses a task, asked before anything is written (`tick-task.py`'s `refusal` and what it called, feature 449
//! T131): the plan's review (feature 243), an open research box, a spec that waits on an open feature (feature 375 D18), an open arbiter
//! tooling fix (379), the hourly checkpoint (383), the approach blocks (385 D8, D9), a wording-only task's commits (385 D138) and a
//! "landed" note over work that is not on main (385 T79, T113, T139). Each asked in process where the Python ran its command or door.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::plan_text::task_sections;
use l7r_guard::shared::py_text::{split, strip};
use l7r_guard::shared::pyjson::py_str;
use serde_json::Value;

use super::text::{boxes_refusal, re};
use super::{spec_dir, Raise};
use crate::{git, read_strict, wording};

static WAITS: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\*\*Waits on\*\*:\s*(\d+)"));
static LANDED: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\blanded\b"));

/// What lands beside every run and moves on its own (append-only rows), so it is never compared with main.
const RIDERS: [&str; 1] = ["dev/review-ledger.md"];

/// One tick asked about: the repository, the feature's directory, the task and its note; and what the process hands it, read once
/// where the command starts so the tests hand their own: `PLAN_REVIEW_OK`, and the tree whose tools the closing check runs (the
/// wrapper's `L7R_GATE_TREE`, else the working directory, as `close-check` took it).
pub struct Ask<'a> {
    pub root: &'a Path,
    pub dir: &'a Path,
    pub task: &'a str,
    pub note: &'a str,
    pub escaped: Option<String>,
    pub tree: PathBuf,
}

impl<'a> Ask<'a> {
    /// The ask with what `env` says of the process.
    pub fn with_env(root: &'a Path, dir: &'a Path, task: &'a str, note: &'a str, env: Env) -> Self {
        let tree = env("L7R_GATE_TREE").map_or_else(
            || std::env::current_dir().unwrap_or_default(),
            PathBuf::from,
        );
        Self {
            root,
            dir,
            task,
            note,
            escaped: env("PLAN_REVIEW_OK"),
            tree,
        }
    }
}

/// What the process's environment says of a name.
pub type Env<'e> = &'e dyn Fn(&str) -> Option<String>;

/// The feature directory's state, by `make speckit-todo`'s one rule, in process (the Python ran `speckit-todo --each-state`, which
/// raised on a nonzero exit).
pub(crate) fn state(d: &Path) -> Result<String, String> {
    l7r_guard::shared::speckit::state(d)
        .map_err(|why| format!("speckit-todo: {}: {why}", d.display()))
}

/// Why `make tick` may not tick in `d`, or "": its spec waits on a feature still open (`**Waits on**: NNN`, feature 375 D18).
fn waits(root: &Path, d: &Path) -> Raise<String> {
    let spec = d.join("spec.md");
    if !spec.is_file() {
        return Ok(String::new());
    }
    let text = read_strict(&spec)?;
    let Some(n) = WAITS
        .captures(&text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
    else {
        return Ok(String::new());
    };
    let Some(other) = spec_dir(root, &n) else {
        return Ok(String::new());
    };
    if state(&other)? == "closed" {
        return Ok(String::new());
    }
    let name = |p: &Path| {
        p.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned()
    };
    Ok(format!(
        "{} waits on feature {n} ({}), which is still open - its spec says `**Waits on**: {n}`; take its tasks once that one has closed",
        name(d),
        name(&other)
    ))
}

/// A JSON value's truth, as Python's `bool()` reads it.
fn truthy(v: Option<&Value>) -> bool {
    match v {
        None | Some(Value::Null) => false,
        Some(Value::Bool(b)) => *b,
        Some(Value::Number(n)) => n.as_f64().is_some_and(|f| f != 0.0),
        Some(Value::String(s)) => !s.is_empty(),
        Some(Value::Array(a)) => !a.is_empty(),
        Some(Value::Object(o)) => !o.is_empty(),
    }
}

/// `r.get(key)` of a row, which must be an object as the Python's `.get` required (`AttributeError` otherwise).
fn field<'v>(row: &'v Value, key: &str) -> Raise<Option<&'v Value>> {
    match row {
        Value::Object(map) => Ok(map.get(key)),
        other => Err(format!(
            "AttributeError: '{}' object has no attribute 'get'",
            match other {
                Value::Array(_) => "list",
                Value::String(_) => "str",
                Value::Bool(_) => "bool",
                Value::Null => "NoneType",
                _ => "number",
            }
        )),
    }
}

/// `r.get("files") or []` as the names Python iterated: a list's items, a string's characters.
fn files_of(row: &Value) -> Raise<Vec<String>> {
    let Some(v) = field(row, "files")?.filter(|v| truthy(Some(v))) else {
        return Ok(Vec::new());
    };
    Ok(match v {
        Value::Array(items) => items.iter().map(py_str).collect(),
        Value::String(s) => s.chars().map(String::from).collect(),
        Value::Object(o) => o.keys().cloned().collect(),
        other => {
            return Err(format!(
                "TypeError: '{}' object is not iterable",
                py_str(other)
            ))
        }
    })
}

/// Does `f` differ from origin/main (`git diff --quiet origin/main -- f` exits nonzero)?
fn off_main(root: &Path, f: &str) -> bool {
    git(root, &["diff", "--quiet", "origin/main", "--", f]).0 != Some(0)
}

/// A NOTE saying "landed" (any case) while the task's last `make land-tooling` failed, or a file it named differs from origin/main
/// (feature 385 T79, plan D98: T72 was ticked "landed" over a failed landing). A task with no run is not refused, unless something of
/// it outside the feature's records stands off main (T113, D130); files that reached main another way pass (T139, D150).
fn landed_refusal(root: &Path, feature: &str, task: &str, note: &str) -> Raise<String> {
    if !LANDED.is_match(note).unwrap_or(false) {
        return Ok(String::new());
    }
    let gd = crate::common_text(root);
    let log = (!gd.is_empty()).then(|| PathBuf::from(&gd).join("land-tooling.jsonl"));
    let mut every: Vec<Value> = Vec::new();
    if let Some(log) = log.filter(|l| l.is_file()) {
        for line in l7r_guard::shared::speckit::splitlines(&read_strict(&log)?) {
            if let Ok(v) = serde_json::from_str::<Value>(line) {
                every.push(v);
            }
        }
    }
    let mut mine = Vec::new();
    for (i, r) in every.iter().enumerate() {
        if field(r, "feature")? == Some(&Value::from(feature))
            && field(r, "task")? == Some(&Value::from(task))
        {
            mine.push(i);
        }
    }
    let Some(&at) = mine.last() else {
        let _ = git(root, &["fetch", "-q", "origin"]);
        let (_, out) = git(
            root,
            &["log", "--name-only", "--format=", "origin/main..HEAD"],
        );
        let ahead = String::from_utf8_lossy(&out).into_owned();
        // ...compared by CONTENT, as T79 compares: `make land-tooling` lands a file as a new commit on main, so a commit ahead of
        // origin/main may hold a file main already has
        let mut off: Vec<&str> = split(&ahead)
            .into_iter()
            .filter(|f| !f.starts_with("specs/") && !f.starts_with("dev/") && off_main(root, f))
            .collect();
        off.sort_unstable();
        off.dedup();
        return Ok(off.first().map_or(String::new(), |f| format!("the NOTE says landed, but {f} is committed here and not on origin/main - land it (scripts/sync-with-main.sh done, or make land F= T=<task> NOTE=, which lands and ticks it), then tick")));
    };
    let mut last = &every[at];
    // a later run of the same files lands them, whichever task was active when it ran (T79's own reland was booked to T81)
    let files = files_of(last)?;
    for r in &every[at + 1..] {
        let theirs = files_of(r)?;
        if files.iter().all(|f| theirs.contains(f)) {
            last = r;
        }
    }
    let _ = git(root, &["fetch", "-q", "origin"]);
    let files = files_of(last)?;
    let off: Vec<&String> = files
        .iter()
        .filter(|f| !RIDERS.contains(&f.as_str()) && off_main(root, f))
        .collect();
    let outcome = field(last, "outcome")?;
    if outcome != Some(&Value::from("landed"))
        && (!off.is_empty() || !truthy(field(last, "files")?))
    {
        let said = |v: Option<&Value>| v.map_or_else(|| "None".to_owned(), py_str);
        return Ok(format!(
            "the NOTE says landed, but {task}'s last make land-tooling ended '{}' ({}) - land it, then tick",
            said(outcome),
            said(field(last, "log")?)
        ));
    }
    Ok(off.first().map_or(String::new(), |f| {
        format!("the NOTE says landed, but {f} differs from origin/main - land it (make land-tooling FILES=...), then tick")
    }))
}

/// `(refusal, message)`: every reason `make tick` refuses the task, together (feature 444 T20, D2: an `or`-chain showed a landing only
/// the first, and T19 took four landing rounds), and what the plan gate says to print. `landed` false leaves out the landed check, which
/// `make land` asks of each task before it lands them (feature 385 T117, D135; feature 405 T33). A PLAN'S DECISIONS ARE REVIEWED BEFORE
/// ITS TASKS ARE TICKED (feature 243), asked before the task is even looked up, so a refused tick writes nothing.
///
/// # Errors
/// What the Python raised: a file that cannot be read, a feature state that cannot be read, a wording check that cannot say.
pub fn refusal(ask: &Ask, landed: bool, boxes: bool) -> Raise<(String, String)> {
    let Ask {
        root,
        dir,
        task,
        note,
        ..
    } = *ask;
    let (permitted, message) = l7r_gate_plan::plan::tick_gate(dir, root, ask.escaped.as_deref());
    let plan = dir.join("plan.md");
    let section = if plan.is_file() {
        task_sections(&read_strict(&plan)?).remove(task)
    } else {
        None
    };
    let mut whys: Vec<String> = if permitted {
        Vec::new()
    } else {
        vec![strip(&message).to_owned()]
    };
    let tasks = dir.join("tasks.md");
    let text = if tasks.is_file() {
        read_strict(&tasks)?
    } else {
        String::new()
    };
    let asked = [
        boxes_refusal(&text, task, boxes),
        waits(root, dir)?,
        // 379: an open tooling fix; 383: the hour
        l7r_gate_reviews::reviews::closing::fix_hold(dir),
        l7r_gate_reviews::reviews::checkpoint::hold(root, None),
        l7r_gate_plan::plan::approach_refusal(dir, root, task).unwrap_or_default(),
        wording::refusal(root, &ask.tree, dir, task, section.as_deref())?,
    ];
    whys.extend(asked.into_iter().filter(|w| !w.is_empty()));
    if whys.is_empty() && landed {
        let name = dir.file_name().unwrap_or_default().to_string_lossy();
        whys.extend(Some(landed_refusal(root, &name, task, note)?).filter(|w| !w.is_empty()));
    }
    if whys.is_empty() {
        return Ok((String::new(), message));
    }
    let why = if whys.len() == 1 {
        whys.remove(0)
    } else {
        whys.iter()
            .enumerate()
            .fold(String::new(), |mut all, (i, w)| {
                let _ = write!(all, "\n  ({}) {w}", i + 1);
                all
            })
    };
    Ok((
        format!("tick: refused - {why}"),
        if permitted { message } else { String::new() },
    ))
}

#[cfg(test)]
mod tests;
