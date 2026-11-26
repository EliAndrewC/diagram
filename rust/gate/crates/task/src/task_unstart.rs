//! `l7r-gate task-unstart <feature> <task>` - `make task-unstart F= T=` (feature 451 T359, the second half of T343's line): the undo
//! of `make task-start`. On 2026-11-26 a task started by mistake in a tree held every landing that carried its edits, and the only
//! way out was moving its mark file by hand.
//!
//! It removes THIS TREE'S mark of the task (`task-marks/<feature>/<task>.json`, or the main worktree's one-mark file of before 451
//! T254 where that names it) and appends one `unstart` row a task the mark names to `task-starts.jsonl` -
//! `{"unstart": {"feature", "task"}, "tree", "utc"}` - which every reader of that file reads, with every earlier start of that task
//! in that tree, as no start (`l7r_shared::speckit::marks::live_starts`, the one filter: a task started twice here and unstarted
//! once has no mark, and reads as not started). The row names its feature and task under `unstart`, never at its top:
//! a reader that has not met the filter then reads it as no task's row, not as a second start.
//!
//! REFUSED: a mark another tree wrote (run there: the command is printed), a task with no mark, and a bundle's member that is not
//! its first task - the bundle's one mark is its first task's (451 T141), and unstarting that unstarts every member. A phase task's
//! hold on its stage's old code (`phase-sources.json`) goes with its start. `.specify/feature.json` stays: it names the tree's
//! feature, which the next start writes again.

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::pyjson::dumps;
use l7r_shared::speckit::{marks, py_path};
use serde_json::{json, Value};

use crate::tick::Raise;
use crate::{common_text, now_secs, raised, reply, utc_text, Reply};

const USAGE: &str = "usage: make task-unstart F=<feature> T=<task>\n";

/// The start undone: what was printed, or the refusal.
fn unstart(cwd: &Path, feature: &str, task: &str) -> Raise<Result<String, String>> {
    let root = crate::toplevel_or_dot(cwd);
    let Some(d) = l7r_gate_plan::plan::resolve_feature(feature, &root) else {
        return Ok(Err(format!(
            "task-unstart: no single specs/{feature}* directory\n"
        )));
    };
    let d = py_path(&d.to_string_lossy());
    let name = d
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let number = name.split('-').next().unwrap_or(&name);
    let common = PathBuf::from(common_text(cwd));
    let all = marks::all(&common);
    let ours = |m: &&Value| m["feature"].as_str() == Some(name.as_str());
    let Some(mark) = all
        .iter()
        .filter(ours)
        .find(|m| m["task"].as_str() == Some(task))
    else {
        let bundle = all
            .iter()
            .filter(ours)
            .find(|m| marks::tasks_of(m).iter().any(|t| t == task));
        return Ok(Err(match bundle {
            Some(b) => {
                let lead = b["task"].as_str().unwrap_or_default();
                format!("task-unstart: refused - {task} is a member of the bundle started under {lead}, whose one mark is {lead}'s (451 T141): make task-unstart F={number} T={lead} unstarts the bundle\n")
            }
            None => format!("task-unstart: refused - {name} {task} has no start mark in any tree: nothing to unstart (make speckit-todo lists what is started)\n"),
        }));
    };
    let tree = mark["tree"].as_str().unwrap_or_default();
    if !marks::same_tree(Path::new(tree), &root) {
        return Ok(Err(format!("task-unstart: refused - {name} {task} was started in {tree}, not in this tree ({}): its mark is that tree's to remove - make -C {tree} task-unstart F={number} T={task}\n", root.display())));
    }
    // the task's own mark, else the one-mark file of before T254, which `marks::all` reads as the main worktree's
    let own = common
        .join(marks::DIR)
        .join(&name)
        .join(format!("{task}.json"));
    let file = if own.is_file() {
        own
    } else {
        common.join(marks::LEGACY)
    };
    std::fs::remove_file(&file).map_err(|e| format!("{}: {e}", file.display()))?;
    let utc = utc_text(now_secs());
    let members = marks::tasks_of(mark);
    let mut rows = String::new();
    for t in &members {
        let row = json!({"unstart": {"feature": name, "task": t}, "tree": tree, "utc": utc});
        let _ = writeln!(rows, "{}", dumps(&row, None, true));
    }
    let starts = common.join(marks::STARTS);
    std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(&starts)
        .and_then(|mut f| f.write_all(rows.as_bytes()))
        .map_err(|e| format!("{}: {e}", starts.display()))?;
    // a phase task's hold on its stage's old code goes with its start
    let state = crate::phase_sources::state_path(&root);
    let held: Value = std::fs::read_to_string(&state)
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or(Value::Null);
    let lifted =
        held["feature"].as_str() == Some(name.as_str()) && held["task"].as_str() == Some(task);
    let said = if lifted {
        let _ = std::fs::remove_file(&state);
        "; its hold on its stage's old code is lifted"
    } else {
        ""
    };
    Ok(Ok(format!("task-unstart: {name} {} is no longer started in {tree} - its mark removed ({}), an unstart row in {}{said}\n", members.join(", "), file.display(), starts.display())))
}

/// `l7r-gate task-unstart <feature> <task>` from `cwd`.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    let [feature, task] = args else {
        return reply(String::new(), USAGE.to_owned(), 2);
    };
    match unstart(cwd, feature, task) {
        Ok(Ok(out)) => reply(out, String::new(), 0),
        Ok(Err(refused)) => reply(String::new(), refused, 2),
        Err(raise) => raised("task-unstart", String::new(), "", &raise),
    }
}

#[cfg(test)]
mod tests;
