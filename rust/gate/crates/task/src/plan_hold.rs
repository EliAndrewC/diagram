//! A held feature's tasks refused at `make task-start` - feature 417 T02 (plan D4, D9; FR-010); `gates/plan_hold.py`, ported by feature
//! 449 T131.
//!
//! WHY. The GM, 2026-10-24: "we might want to put our claims work on hold and then open a new feature whose goal is 'all seeds passing'" -
//! and 417's FR-010: no task of a claims feature that changes the engine starts until 417 closes. A hold written only in a status line is
//! remembered, not made; `make task-start` is the one place a task becomes active, so the hold is asked there.
//!
//! A feature is HELD when its spec's `**Status**:` paragraph says `ON HOLD` and `until feature NNN`, while NNN is open by `make
//! speckit-todo`'s own rule. A held feature's ENGINE task has no escape; any other starts with `HOLD_OK="<reason>"`. A task is NOT an
//! engine task only when it is sure: it names a path outside the engine and no engine path or module, and is not `research: physical`;
//! anything else - a task not found, a task that names nothing - is unsure, and unsure counts as engine (plan D9).

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use l7r_guard::shared::speckit::{read_text, splitlines};

use crate::tick::refusal::state;
use crate::tick::text::{lstrip, re};
use crate::tick::Raise;

static HOLD: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)ON HOLD\b.*?\buntil feature (\d{3,})"));
/// The status PARAGRAPH, not its first line: 384's wraps, and its hold is on the second.
static STATUS: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?ms)^\*\*Status\*\*:[{SPACE_CLASS}]*(.*?)(?:\n[{SPACE_CLASS}]*\n|\z)"
    ))
});
/// `rust/`: the rebuilt phases' crates (feature 444 T17).
static ENGINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\w/.-])(?:l7r|pool|rust)/"));
static OUTSIDE: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?<![\w/.-])(?:scripts|tests|research|docs|specs|dev|\.claude)/|\bMakefile\b")
});
static WORD: LazyLock<Regex> = LazyLock::new(|| re(r"[A-Za-z_][A-Za-z0-9_]*"));
static PHYSICAL: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"research:[{SPACE_CLASS}]*physical")));

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// Every path under `dir` as `rglob("*")` walks it: symlinked directories not entered.
fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for e in entries.flatten() {
        let path = e.path();
        let real_dir = e.file_type().is_ok_and(|t| t.is_dir());
        out.push(path.clone());
        if real_dir {
            walk(&path, out);
        }
    }
}

/// Every engine module's name, longer than three characters: `l7r/**/*.py` and `pool/**/*.py` stems (`fixture_seats`, a `.gen` suffix
/// dropped), packages included, `__init__` not; and the Rust phases' `rust/**/*.rs` stems, `lib`, `mod` and `main` not (feature 444
/// T17), read under the gate's own tree, where the Python file stood.
fn engine_modules(tree: &Path) -> BTreeSet<String> {
    let mut names = BTreeSet::new();
    let stem = |p: &Path| {
        p.file_stem()
            .map(|s| s.to_string_lossy().into_owned())
            .unwrap_or_default()
    };
    let ends = |p: &Path, ext: &str| {
        p.file_name().is_some_and(|n| {
            let n = n.to_string_lossy();
            n.ends_with(ext) && n.len() > ext.len()
        })
    };
    for top in ["l7r", "pool"] {
        let mut all = Vec::new();
        walk(&tree.join(top), &mut all);
        for p in all.iter().filter(|p| ends(p, ".py")) {
            let s = stem(p);
            if s != "__init__" {
                names.insert(s.strip_suffix(".gen").unwrap_or(&s).to_owned());
            }
        }
        if top == "l7r" {
            names.extend(
                all.iter()
                    .filter(|p| p.is_dir() && p.join("__init__.py").is_file())
                    .map(|p| {
                        p.file_name()
                            .unwrap_or_default()
                            .to_string_lossy()
                            .into_owned()
                    }),
            );
        }
    }
    let mut rust = Vec::new();
    walk(&tree.join("rust"), &mut rust);
    names.extend(
        rust.iter()
            .filter(|p| ends(p, ".rs"))
            .map(|p| stem(p))
            .filter(|s| !matches!(s.as_str(), "lib" | "mod" | "main")),
    );
    names.retain(|n| n.chars().count() > 3);
    names
}

/// The open feature that `d` waits on, or None.
fn holder(d: &Path) -> Raise<Option<PathBuf>> {
    let spec = d.join("spec.md");
    if !spec.is_file() {
        return Ok(None);
    }
    let text = read_text(&spec)?;
    let caps = STATUS.captures(&text).ok().flatten();
    let Some(n) = caps
        .and_then(|c| c.get(1))
        .and_then(|s| HOLD.captures(s.as_str()).ok().flatten())
        .and_then(|m| m.get(1).map(|g| g.as_str().to_owned()))
    else {
        return Ok(None);
    };
    let parent = l7r_guard::shared::speckit::py_parent(d);
    let prefix = format!("{n}-");
    let mut hits: Vec<PathBuf> = std::fs::read_dir(&parent)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix))
        .map(|e| e.path())
        .collect();
    hits.sort();
    if hits.len() != 1 {
        return Ok(None);
    }
    let by = hits.remove(0);
    Ok((state(&by)? != "closed").then_some(by))
}

/// The task's line in `tasks.md` and the indented lines under it ('' when the task is not there).
fn task_lines(d: &Path, task: &str) -> Raise<String> {
    let tasks = d.join("tasks.md");
    let text = if tasks.is_file() {
        read_text(&tasks)?
    } else {
        String::new()
    };
    let head = re(&format!(
        r"^[{SPACE_CLASS}]*- \[[ xX]\] {}\b",
        fancy_regex::escape(task)
    ));
    let mut out: Vec<&str> = Vec::new();
    for line in splitlines(&text) {
        if found(&head, line) {
            out = vec![line];
        } else if !out.is_empty()
            && (line.starts_with(' ') || line.starts_with('\t'))
            && !lstrip(line).starts_with("- [")
        {
            out.push(line);
        } else if !out.is_empty() {
            break;
        }
    }
    Ok(out.join("\n"))
}

fn is_engine_task(tree: &Path, d: &Path, task: &str, section: Option<&str>) -> Raise<bool> {
    let lines = task_lines(d, task)?;
    if lines.is_empty() {
        return Ok(true); // unsure counts as engine (plan D9)
    }
    let text = format!("{lines}\n{}", section.unwrap_or_default());
    let names = engine_modules(tree);
    if found(&ENGINE, &text)
        || found(&PHYSICAL, &lines)
        || WORD
            .find_iter(&text)
            .flatten()
            .any(|w| names.contains(w.as_str()))
    {
        return Ok(true);
    }
    Ok(!found(&OUTSIDE, &text)) // sure only when it names somewhere outside the engine
}

/// '' when the task may start, else why not and what to do; `tree` is where the engine's modules are read.
pub(crate) fn refusal(
    tree: &Path,
    d: &Path,
    task: &str,
    section: Option<&str>,
    hold_ok: &str,
) -> Raise<String> {
    let Some(by) = holder(d)? else {
        return Ok(String::new());
    };
    let name = d.file_name().unwrap_or_default().to_string_lossy();
    let by = by
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    if is_engine_task(tree, d, task, section)? {
        return Ok(format!("task-start: REFUSED - {name} is ON HOLD until {by} closes, and {task} changes the engine (its task or plan section names an engine path or module, or names nothing outside the engine, or it is research: physical). An engine task of a held feature has no escape (feature 417 FR-010): work {by} first."));
    }
    if strip(hold_ok).is_empty() {
        let number = name.split('-').next().unwrap_or_default();
        return Ok(format!("task-start: REFUSED - {name} is ON HOLD until {by} closes. {task} does not change the engine, so it may start with a reason: make task-start F={number} T={task} HOLD_OK=\"<why it cannot wait>\""));
    }
    Ok(String::new())
}

#[cfg(test)]
mod tests;
