//! `l7r-gate task-withdraw <feature> <task(s)>` - `make task-withdraw F= T= WHY=` (feature 451 T359): the way out for a filed task that
//! turned out a duplicate or no defect. Before it the only way to close a box was a landing, which asks a plan section and its review
//! of nothing: on 2026-11-26 `make land` refused T322, T323, T356 and T358 for their unfilled plan stubs.
//!
//! WHAT IT WRITES, and commits none of it:
//! - THE BOX TICKED, its line's text kept and ` Withdrawn YYYY-MM-DD: <why>` appended. A ticked box at column 0 is the form every
//!   reader of a closed task already takes - the state rule and `make speckit-todo` count it ticked, the feature report counts it of
//!   the total, the next tick archives its block to tasks-done.md - so no reader is taught a new mark; the word is a spec's own
//!   closing status (`speckit::CLOSING`). It gets no `verify: DONE.` line: nothing was verified.
//! - ITS UNFILLED PLAN STUB REMOVED from plan.md: the template `make task-add` wrote for the id, with or without the performance
//!   checklist, byte for byte. A section that has been filled in, or one `plan-review.json` holds a verdict for, is refused: that task
//!   was worked, and it closes by a landing.
//! - WHO AND WHY, one `TaskWithdrawn` line a task in the feature's event log, through the hooks' writer (the tree, the session).
//!
//! REFUSED, every task's reasons together and nothing written while one stands: a task started in any tree (a mark, `make
//! task-unstart` named), held by a builder's pool tree with no start made (the pool's registry, `make builder-tree-release` named:
//! 451 T366 - on 2026-11-26 `make task-withdraw F=451 T="T322 T359"` named no refusal for T359 while its builder held a tree), already ticked, not filed, with code carried in the clone (a commit since `origin/main` whose subject's head
//! names the feature's number and the task: `451 T359: ...`), with an open box under its line (a `research: physical` task's boxes: a
//! ticked task holding one is never archived), or the feature's last open boxes (the last tick runs the closing check; this does not).
//! The reserved id stays taken (`task-ids.txt`): a withdrawn id is never filed again. The filing lock (`task_add`'s) is held from the
//! read to the write, so a `make task-add` beside it loses nothing.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_gate_plan::plan::template::without_stub;
use l7r_shared::builder_pool;
use l7r_shared::escape::enough;
use l7r_shared::guards::event_log_hooks::append_row_with;
use l7r_shared::py_text::strip;
use l7r_shared::speckit::{marks, tasks as archive};
use serde_json::{json, Value};

use crate::tick::text::task_line;
use crate::tick::{repo_root, spec_dir, Env, Raise};
use crate::{common_text, git, now_secs, raised, read_strict, reply, utc_text, write_file, Reply};

const USAGE: &str = "usage: make task-withdraw F=<feature> T=<task(s)> WHY=\"<two words or more: the task it duplicates, or why it is no defect>\"\n";

/// What the refusals read, once for every task asked.
struct Read {
    name: String,
    number: String,
    tasks: String,
    done: String,
    plan: String,
    review: Value,
    marks: Vec<Value>,
    pool: Vec<builder_pool::Tree>,
    subjects: String,
}

/// Does a commit subject name the task as its own: its head, before the first colon, opening with the feature's number and holding
/// the task as a word (`451 T359: ...`, `451 T299 T282: ...`)? A subject that only mentions the id further on does not.
fn names(subject: &str, number: &str, task: &str) -> bool {
    let head = subject.split(':').next().unwrap_or_default();
    let mut words = head.split(|c: char| !c.is_ascii_alphanumeric());
    words.next() == Some(number) && words.any(|w| w == task)
}

/// Why `task` is not withdrawn, or none.
fn refusal(read: &Read, task: &str) -> Option<String> {
    let Read { name, number, .. } = read;
    let (open, ticked) = (task_line(" ", task), task_line("[xX]", task));
    let hit = |p: &fancy_regex::Regex, l: &str| p.is_match(l).unwrap_or(false);
    let lines: Vec<&str> = read.tasks.lines().collect();
    let Some(at) = lines.iter().position(|l| hit(&open, l)) else {
        if lines.iter().any(|l| hit(&ticked, l)) || archive::archived(&read.done, task) {
            return Some(format!("{task} is already ticked"));
        }
        return Some(format!("{task} is no open task of {name}/tasks.md"));
    };
    let boxed = lines[at + 1..]
        .iter()
        .take_while(|l| !l.starts_with("- [") && !l.starts_with('#'))
        .any(|l| l.contains("- [ ]"));
    if boxed {
        return Some(format!("{task} holds an open box under its line (a `research: physical` task's): a ticked task with one open is never archived - close it by hand"));
    }
    let started = read.marks.iter().find(|m| {
        m["feature"].as_str() == Some(name) && marks::tasks_of(m).iter().any(|t| t == task)
    });
    if let Some(mark) = started {
        let tree = mark["tree"].as_str().unwrap_or_default();
        let lead = mark["task"].as_str().unwrap_or(task);
        return Some(format!("{task} is started in {tree} (make task-start): unstart it there first - make -C {tree} task-unstart F={number} T={lead}"));
    }
    // a builder's pool tree held for it, whatever start was or was not made there (451 T366): the registry keys a feature by its
    // number, and a hold naming no feature is any feature's, as the pool itself reads one
    let pooled = read.pool.iter().find(|t| {
        t.tasks.iter().any(|held| held == task) && (t.feature.is_empty() || t.feature == *number)
    });
    if let Some(tree) = pooled {
        return Some(format!("{task} is held by a builder's pool tree ({}, held for {} since {}): its builder may be working it - free the tree first: make builder-tree-release T={task} F={number}", tree.tree.display(), tree.holder(), tree.since));
    }
    if let Some(subject) = read.subjects.lines().find(|s| names(s, number, task)) {
        return Some(format!("{task}'s code is carried in the clone (the commit \"{subject}\", since origin/main): a task with code closes by a landing - make land F={number} T={task}"));
    }
    if read.review["tasks"].get(task).is_some() {
        return Some(format!("{task}'s plan section carries a review verdict ({name}/plan-review.json): a reviewed task is no withdrawal but a landing - make land F={number} T={task}"));
    }
    if without_stub(&read.plan, task).is_err() {
        return Some(format!("{task}'s plan section has been filled in ({name}/plan.md): it is no withdrawal but a landing - make land F={number} T={task} - or empty the section back to its template first"));
    }
    None
}

/// The tasks' text with `task`'s open box ticked and the withdrawal appended to its line.
fn ticked(tasks: &str, task: &str, date: &str, why: &str) -> String {
    let open = task_line(" ", task);
    tasks
        .split_inclusive('\n')
        .map(|l| {
            if open.is_match(l).unwrap_or(false) {
                let text = l.trim_end_matches('\n');
                format!("- [x]{} Withdrawn {date}: {why}\n", &text["- [ ]".len()..])
            } else {
                l.to_owned()
            }
        })
        .collect()
}

/// Who and why, a line a task in the feature's event log (the hooks' writer gives it its time and the session's id): where it was
/// written, as the last line says it, "" where no log could be made.
fn record(root: &Path, name: &str, tasks: &[String], why: &str, env: Env) -> String {
    let top = crate::toplevel_or_dot(root);
    let mut log = None;
    for t in tasks {
        let row = json!({"ev": "TaskWithdrawn", "src": "task-withdraw", "task": t, "why": why, "tree": top.to_string_lossy()});
        let row = row.as_object().cloned().unwrap_or_default();
        log = append_row_with(root, Some(name), row, env).or(log);
    }
    log.map_or_else(String::new, |p| format!("; recorded in {}", p.display()))
}

/// The tasks withdrawn: what was printed, or the refusal.
fn withdraw(
    cwd: &Path,
    feature: &str,
    tasks: &[String],
    why: &str,
    env: Env,
) -> Raise<Result<String, Reply>> {
    let root = repo_root(cwd);
    let Some(d) = spec_dir(&root, feature).filter(|d| d.join("tasks.md").is_file()) else {
        return Ok(Err(reply(
            String::new(),
            format!(
                "task-withdraw: no single specs/{feature}* directory with a tasks.md under {}\n",
                root.display()
            ),
            2,
        )));
    };
    let _held = match crate::task_add::lock(&root, &d, env) {
        Ok(held) => held,
        Err(refused) => return Ok(Err(refused)),
    };
    let name = d
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let number = name.split('-').next().unwrap_or_default().to_owned();
    let (tasks_path, plan_path) = (d.join("tasks.md"), d.join("plan.md"));
    let plan = if plan_path.is_file() {
        read_strict(&plan_path)?
    } else {
        String::new()
    };
    let read = Read {
        tasks: read_strict(&tasks_path)?,
        done: archive::done_text(&d)?,
        review: std::fs::read_to_string(d.join("plan-review.json"))
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
            .unwrap_or(Value::Null),
        marks: marks::all(&PathBuf::from(common_text(&root))),
        pool: builder_pool::read(&PathBuf::from(common_text(&root))),
        subjects: String::from_utf8_lossy(
            &git(&root, &["log", "--format=%s", "origin/main..HEAD"]).1,
        )
        .into_owned(),
        plan,
        name,
        number,
    };
    let (name, number) = (&read.name, &read.number);
    let mut why_not: Vec<String> = tasks.iter().filter_map(|t| refusal(&read, t)).collect();
    let open = read
        .tasks
        .lines()
        .filter(|l| l.starts_with("- [ ] "))
        .count();
    if why_not.is_empty() && open <= tasks.len() {
        why_not.push(format!("{} would leave {name} no open box: the feature's last tick runs the closing check, which a withdrawal does not - close it with make tick F={number}", tasks.join(" ")));
    }
    if !why_not.is_empty() {
        return Ok(Err(reply(
            String::new(),
            format!(
                "task-withdraw: refused, nothing written (451 T359):\n  {}\n",
                why_not.join("\n  ")
            ),
            2,
        )));
    }
    let date = &utc_text(now_secs())[..10];
    let (mut text, mut plan) = (read.tasks.clone(), read.plan.clone());
    let mut out = String::new();
    let rel = |p: &Path| p.strip_prefix(&root).unwrap_or(p).display().to_string();
    for t in tasks {
        text = ticked(&text, t, date, why);
        let stub = without_stub(&plan, t).ok().flatten();
        let said = if stub.is_some() {
            format!(", its unfilled plan stub removed from {}", rel(&plan_path))
        } else {
            String::new()
        };
        plan = stub.unwrap_or(plan);
        let _ = writeln!(
            out,
            "task-withdraw: {name} {t} ticked `Withdrawn {date}: {why}` in {}{said}",
            rel(&tasks_path)
        );
    }
    write_file(&tasks_path, text.as_bytes())?;
    let mut changed = rel(&tasks_path);
    if plan != read.plan {
        write_file(&plan_path, plan.as_bytes())?;
        let _ = write!(changed, " {}", rel(&plan_path));
    }
    let recorded = record(&root, name, tasks, why, env);
    let _ = writeln!(
        out,
        "task-withdraw: changed {changed} - nothing staged or committed{recorded}"
    );
    Ok(Ok(out))
}

/// `l7r-gate task-withdraw <feature> <task(s)>` from `cwd`, `why` what `TASK_WHY` says.
#[must_use]
pub fn cli(args: &[String], cwd: &Path, why: &str) -> Reply {
    cli_with(args, cwd, why, &|k| std::env::var(k).ok())
}

/// [`cli`] with the environment's variables read through `env` (a closure in the tests).
pub(crate) fn cli_with(args: &[String], cwd: &Path, why: &str, env: Env) -> Reply {
    let why = strip(why);
    let tasks = args
        .get(1)
        .map(|t| crate::task_start::members(t))
        .unwrap_or_default();
    if args.len() != 2 || tasks.is_empty() {
        return reply(String::new(), USAGE.to_owned(), 2);
    }
    if !enough(why) {
        return reply(String::new(), format!("task-withdraw: WHY needs a REASON - two words and eight characters: the task it duplicates, or why it is no defect\n{USAGE}"), 2);
    }
    match withdraw(cwd, &args[0], &tasks, why, env) {
        Ok(Ok(out)) => reply(out, String::new(), 0),
        Ok(Err(refused)) => refused,
        Err(raise) => raised("task-withdraw", String::new(), "", &raise),
    }
}

#[cfg(test)]
mod tests;
