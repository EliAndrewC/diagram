//! A BUNDLE OF SMALL TASKS STARTED AS ONE (feature 451 T141; the GM 2026-11-22, request.md "on bundling small tasks": "what set of tasks
//! is currently open? All of which are very tiny, such that they could all be worked basically at the same time?"). `make task-start
//! T=a,b,c` (commas or spaces, as `make land` takes them, 451 T18) marks the bundle: every member's refusal is asked before anything is
//! written, then the mark names the bundle's first task as `task` - the one task every reader of the mark already reads, so the event
//! log files the bundle's lines under it, the static-runs guard counts its runs once and the plan-round tripwire its rounds once - and
//! every member as `tasks`. Each member's start is logged, the first task's last, so it is the task in force (`filed::in_force`) and every
//! member counts as started for a landing beside the mark (451 T101).
//!
//! A phase task is never a bundle's member: its stage's old code is held for it alone ([`crate::phase_sources`]), and nothing in the
//! record says how one hold would serve several stages - so it is refused, named, and started by itself (the easier route, said here).

use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::guards::set_down_hooks::{next_performance, performance};
use l7r_shared::plan_text::task_sections;
use l7r_shared::pyjson::dumps;
use l7r_shared::speckit::{py_parent, py_path};
use serde_json::json;

use super::{perf_first, task_block, write};
use crate::tick::text::re;
use crate::tick::Raise;
use crate::{common_text, now_secs, read_strict, utc_text};

/// The tasks `T=` names: split at commas and spaces, each once, in their order.
pub(super) fn members(words: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for t in words.split([',', ' ', '\t']).filter(|t| !t.is_empty()) {
        if !out.iter().any(|o| o == t) {
            out.push(t.to_owned());
        }
    }
    out
}

/// The mark, the feature named and each start logged, for one task or a bundle (`tasks[0]` its first); the tree's top, where the
/// phase hold is written. A single task's mark is written as it always was, with no `tasks`.
pub(super) fn mark(common: &Path, d: &Path, name: &str, tasks: &[&str]) -> Raise<PathBuf> {
    let lead = tasks.first().copied().unwrap_or_default();
    let value = if tasks.len() > 1 {
        json!({"feature": name, "task": lead, "tasks": tasks})
    } else {
        json!({"feature": name, "task": lead})
    };
    // THE TASK'S OWN MARK, in the tree that started it (451 T254): no start moves another task's or another worktree's
    let top = py_parent(&py_parent(d));
    let utc = utc_text(now_secs());
    l7r_shared::speckit::marks::write(common, &top, value, &utc)?;
    // ...AND THE FEATURE NAMED where `active_task` reads it (405 T106): a mark naming another feature than `.specify/feature.json` is
    // ignored, so a session that started 405's task with 415 still named there had the cohort and `claims-carry` charge 405's work to 415
    let specify = top.join(".specify");
    if !specify.is_dir() {
        std::fs::create_dir(&specify).map_err(|e| format!("{}: {e}", specify.display()))?;
    }
    write(
        &specify.join("feature.json"),
        &format!(
            "{}\n",
            dumps(
                &json!({"feature_directory": format!("specs/{name}")}),
                Some(2),
                true
            )
        ),
    )?;
    // ...AND WHEN, for the report's per-task split (feature 385 T02, plan D10): a bundle's other members first, its first task last
    // ...each row naming its tree, so a reader asking for this tree's task in force reads only its own (451 T254)
    let starts = common.join("task-starts.jsonl");
    let mut rows = String::new();
    let tree = top.to_string_lossy();
    for t in tasks.iter().skip(1).chain(tasks.first()) {
        let row = dumps(
            &json!({"feature": name, "task": t, "utc": utc, "tree": tree}),
            None,
            true,
        );
        let _ = writeln!(rows, "{row}");
    }
    std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(&starts)
        .and_then(|mut f| f.write_all(rows.as_bytes()))
        .map_err(|e| format!("{}: {e}", starts.display()))?;
    Ok(top)
}

/// The bundle started, or why it was not: every member's refusal together, nothing written while any stands.
pub(super) fn start(
    cwd: &Path,
    tree: &Path,
    feature: &str,
    tasks: &[String],
    holds: (&str, &str, &str),
    out: &mut String,
) -> Raise<Option<String>> {
    // a parked stage (449 T244) is named by its task's `phase:` line, so its task is a phase task, refused below with the rest
    let (hold_ok, perf_later, _) = holds;
    let root = crate::toplevel_or_dot(cwd);
    let Some(d) = l7r_gate_plan::plan::resolve_feature(feature, &root) else {
        return Ok(Some(format!(
            "task-start: no single specs/{feature}* directory\n"
        )));
    };
    let d = py_path(&d.to_string_lossy());
    let read = |f: &str| -> Raise<String> {
        let p = d.join(f);
        if p.is_file() {
            read_strict(&p)
        } else {
            Ok(String::new())
        }
    };
    let (text, plan) = (read("tasks.md")?, read("plan.md")?);
    let sections = task_sections(&plan);
    let name = d
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let number = name.split('-').next().unwrap_or(&name).to_owned();
    let common = PathBuf::from(common_text(cwd));
    let mut why: Vec<String> = Vec::new();
    for t in tasks {
        let open = re(&format!(r"(?m)^- \[ \] {}\b", fancy_regex::escape(t)));
        if !open.is_match(&text).unwrap_or(false) {
            why.push(format!("{t} is not an open task of {name}/tasks.md"));
            continue;
        }
        let block = task_block(&text, t);
        let (phase, _) = crate::phase_sources::phase_of(&block);
        if !phase.is_empty() {
            why.push(format!("{t} is a phase task (phase: {phase}): its stage's old code is held for it alone - start it by itself, make task-start F={number} T={t}"));
            continue;
        }
        let held =
            crate::plan_hold::refusal(tree, &d, t, sections.get(t).map(String::as_str), hold_ok)?;
        if !held.is_empty() && !why.contains(&held) {
            why.push(held);
        }
    }
    let list = tasks.join(",");
    if !why.is_empty() {
        return Ok(Some(format!(
            "task-start: refused - the bundle T={list} was not started, nothing written (451 T141):\n  {}\n",
            why.join("\n  ")
        )));
    }
    // ...PERFORMANCE WORK FIRST (451 FR-013), asked of EACH member as a single start asks it: a member that is not performance work
    // waits while an open performance task does - unless that task is a member, which starts with it (the review's round-2 note)
    let title = |t: &str| -> String {
        let line = re(&format!(
            r"(?m)^- \[[ xX]\] {} (.*)$",
            fancy_regex::escape(t)
        ));
        line.captures(&text)
            .ok()
            .flatten()
            .and_then(|c| c.get(1))
            .map_or(String::new(), |m| m.as_str().to_owned())
    };
    let next = next_performance(&root, &common, &name)?;
    let waiting_in = next
        .as_ref()
        .is_some_and(|n| n.feature == name && tasks.contains(&n.id));
    if !waiting_in {
        for t in tasks.iter().filter(|t| !performance(t, &title(t), &plan)) {
            if let Some(refused) = perf_first(&root, &common, &d, &name, t, perf_later)? {
                return Ok(Some(refused));
            }
        }
    }
    let refs: Vec<&str> = tasks.iter().map(String::as_str).collect();
    let top = mark(&common, &d, &name, &refs)?;
    let shown = refs.join(", ");
    let _ = writeln!(out, "task-start: {name} {shown} is the active bundle (451 T141) - one plan section, `### {shown} (bundle)` and `### {shown} Approach (checklist part A)`, each item answered per task where they differ; decide it once (make decide F={number} T={list}), close it once (make closing-checks T={list} F={number}), land it once (make land F={number} T={list})");
    // no member is a phase task: the hold any earlier task left is cleared, as any other task's start clears it
    crate::phase_sources::record(&top, &name, &tasks[0], "")?;
    Ok(None)
}

#[cfg(test)]
mod tests;
