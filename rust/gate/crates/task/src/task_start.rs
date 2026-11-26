//! `l7r-gate task-start <feature> <task>` - `make task-start` (feature 375; `scripts/task_start.py`, ported by feature 449 T131 with what
//! it read, `ask:449-T066-scope`'s phase-3 placement): the task's own mark (`task-marks/<feature>/<task>.json`, 451 T254, beside
//! `task-starts.jsonl`, in the git common directory), its feature named in `.specify/feature.json`, its start logged - unless its feature is held (feature 417, [`plan_hold`]) -
//! and a phase task's old code held from reading (feature 444, [`phase_sources`]). The usage text names `task_start.py` byte for byte.
//!
//! [`plan_hold`]: crate::plan_hold
//! [`phase_sources`]: crate::phase_sources

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::escape::enough;
use l7r_shared::guards::set_down_hooks::{next_performance, performance};
use l7r_shared::log::Entry;
use l7r_shared::plan_text::task_sections;
use l7r_shared::py_text::strip;
use l7r_shared::speckit::py_path;
use serde_json::{json, Value};

use crate::tick::text::re;
use crate::tick::Raise;
use crate::{common_text, now_secs, raised, read_strict, reply, utc_text, Reply};

const USAGE: &str = "usage: task_start.py <feature> <task>";

fn write(path: &Path, text: &str) -> Raise<()> {
    crate::write_file(path, text.as_bytes())
}

/// The task's block in tasks.md: its line and what follows, up to the next box.
fn task_block(tasks: &str, task: &str) -> String {
    let pattern = re(&format!(
        r"(?ms)^- \[[ x]\] {}\b.*?(?=^- \[|\z)",
        fancy_regex::escape(task)
    ));
    pattern
        .find(tasks)
        .ok()
        .flatten()
        .map_or(String::new(), |m| m.as_str().to_owned())
}

/// One guard-log entry of the performance-first refusal, as `$(LOGESCAPE)` and the guards write theirs (`make guard-log
/// GUARD=perf-first`, `make audit`); never fails.
fn record(event: &str, detail: &str, rule: &str) {
    record_as("perf-first", event, detail, rule);
}

/// One guard-log entry under `guard` (`perf-first`, or `parked-stage`, 449 T244); never fails.
fn record_as(guard: &str, event: &str, detail: &str, rule: &str) {
    let detail: String = detail.chars().take(400).collect();
    let _ = l7r_shared::log::write(&Entry {
        guard,
        event,
        detail: &detail,
        rule,
        context: None,
        input: &Value::Null,
        session_name: "",
    });
}

/// PERFORMANCE WORK FIRST (feature 451 FR-013, the GM 2026-11-20: "can we in general priotitize performance improvements going
/// forward?"): a task that is not performance work is refused while an active feature holds an open one, naming it and its start - the
/// set-down guard's own active test and picker ([`next_performance`]), the feature being started counted active. The escape,
/// `PERF_LATER_OK="<reason>"` (a performance task waiting on another task's landing), is read first and recorded either way.
fn perf_first(
    root: &Path,
    common: &Path,
    d: &Path,
    name: &str,
    task: &str,
    perf_later: &str,
) -> Raise<Option<String>> {
    let why = strip(perf_later);
    if !why.is_empty() {
        if !enough(why) {
            record("blocked", why, "PERF_LATER_OK-no-reason");
            return Ok(Some("task-start: PERF_LATER_OK needs a REASON, not just a value - two words and eight characters; say why this task goes before the open performance work\n".to_owned()));
        }
        record("escaped", &format!("{name} {task}: {why}"), "perf-later-ok");
        return Ok(None);
    }
    let read = |f: &str| -> Raise<String> {
        let p = d.join(f);
        if p.is_file() {
            read_strict(&p)
        } else {
            Ok(String::new())
        }
    };
    let (tasks, plan) = (read("tasks.md")?, read("plan.md")?);
    let line = re(&format!(
        r"(?m)^- \[[ xX]\] {} (.*)$",
        fancy_regex::escape(task)
    ));
    let title = line
        .captures(&tasks)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map_or("", |m| m.as_str());
    if performance(task, title, &plan) {
        return Ok(None);
    }
    let Some(next) = next_performance(root, common, name)? else {
        return Ok(None);
    };
    let number = next.feature.split('-').next().unwrap_or(&next.feature);
    let short: String = next.title.chars().take(80).collect();
    record(
        "blocked",
        &format!("{name} {task} before {} {}", next.feature, next.id),
        "not-performance-first",
    );
    Ok(Some(format!(
        "task-start: refused - {name} {task} is not performance work, and {} {} is ({} {short}): performance work goes first (feature 451 FR-013, the GM 2026-11-20). Start it first: make task-start F={number} T={} - or, where it waits on another task's landing, PERF_LATER_OK=\"<reason>\" make task-start F={} T={task}\n",
        next.feature,
        next.id,
        next.id,
        next.id,
        name.split('-').next().unwrap_or(name)
    )))
}

/// THE PARKED STAGES WAIT FOR THE GM (feature 449 T244; the GM 2026-11-21, `docs/gm-rulings.md`, "Stop before homesteads, and talk
/// first"): a task whose line or block names a parked stage (`phase: homesteads`, [`l7r_shared::parked`]) that no row has resumed is
/// refused, naming the ruling, before the performance-first check, so the session is told to stop rather than to escape `PERF_LATER_OK`.
/// The escape, `GM_RESUMED="<the GM's words resuming it>"` (the guard's `phase_source_hooks` holds the words to a message the GM wrote
/// this session), is recorded in the guard log and in `parked-resumed.jsonl`, after which the stage is held no longer.
fn parked_stage(
    root: &Path,
    common: &Path,
    name: &str,
    task: &str,
    block: &str,
    gm_resumed: &str,
) -> Raise<Option<String>> {
    let Some(stage) = l7r_shared::parked::held_task(root, common, block) else {
        return Ok(None);
    };
    let what = format!("make task-start of {name} {task} ({stage})");
    let words = strip(gm_resumed);
    if words.is_empty() {
        record_as("parked-stage", "blocked", &what, "no-gm-resumed");
        return Ok(Some(l7r_shared::parked::refusal(&what)));
    }
    if !enough(words) {
        record_as(
            "parked-stage",
            "blocked",
            &format!("{what}: {words}"),
            "GM_RESUMED-no-words",
        );
        return Ok(Some("task-start: GM_RESUMED needs the GM's words resuming the stage, verbatim from his message - two words or more; a bare value resumes nothing\n".to_owned()));
    }
    record_as(
        "parked-stage",
        "escaped",
        &format!("{what}: {words}"),
        "gm-resumed",
    );
    let row = json!({"stage": stage, "feature": name, "task": task, "words": words, "utc": utc_text(now_secs())});
    let resumed = common.join(l7r_shared::parked::RESUMED);
    l7r_shared::parked::record(common, &row).map_err(|e| format!("{}: {e}", resumed.display()))?;
    Ok(None)
}

/// The task started, its stdout so far kept when a later step raises.
fn start(
    cwd: &Path,
    tree: &Path,
    feature: &str,
    task: &str,
    holds: (&str, &str, &str),
    out: &mut String,
) -> Raise<Option<String>> {
    let (hold_ok, perf_later, gm_resumed) = holds;
    let root = crate::toplevel_or_dot(cwd);
    let Some(d) = l7r_gate_plan::plan::resolve_feature(feature, &root) else {
        return Ok(Some(format!(
            "task-start: no single specs/{feature}* directory\n"
        )));
    };
    let d = py_path(&d.to_string_lossy());
    // ...NOT A HELD FEATURE'S TASK (feature 417 T02, plan D4/D9): the hold is asked where a task becomes active
    let plan = d.join("plan.md");
    let section = if plan.is_file() {
        task_sections(&read_strict(&plan)?).remove(task)
    } else {
        None
    };
    let why = crate::plan_hold::refusal(tree, &d, task, section.as_deref(), hold_ok)?;
    if !why.is_empty() {
        return Ok(Some(format!("{why}\n")));
    }
    let name = d
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let common = PathBuf::from(common_text(cwd));
    let tasks = d.join("tasks.md");
    let text = if tasks.is_file() {
        read_strict(&tasks)?
    } else {
        String::new()
    };
    let block = task_block(&text, task);
    if let Some(why) = parked_stage(&root, &common, &name, task, &block, gm_resumed)? {
        return Ok(Some(why));
    }
    // the specs read where `resolve_feature` found this one, never the gate's own tree: a fixture clone holds its own
    if let Some(why) = perf_first(&root, &common, &d, &name, task, perf_later)? {
        return Ok(Some(why));
    }
    let top = bundle::mark(&common, &d, &name, &[task])?;
    let _ = writeln!(out, "task-start: {name} {task} is the active task - its checks need its decisions ruled first (make decide)");
    // ...AND A PHASE TASK'S OLD CODE HELD (feature 444, the GM 2026-10-30): its stage is rebuilt from its derivation, never read from
    // today's Python; any other task clears the hold
    let line = crate::phase_sources::record(&top, &name, task, &block)?;
    if !line.is_empty() {
        let _ = writeln!(out, "{line}");
    }
    Ok(None)
}

/// `l7r-gate task-start <feature> <task>` from `cwd`; `HOLD_OK` from the environment. Records no run, as the Python recorded none.
#[must_use]
pub fn cli(args: &[String], cwd: &Path) -> Reply {
    cli_with(args, cwd, &|k| std::env::var(k).ok())
}

pub(crate) fn cli_with(args: &[String], cwd: &Path, env: crate::tick::Env) -> Reply {
    if args.len() != 2 {
        return reply(String::new(), format!("{USAGE}\n"), 2);
    }
    // the engine's modules are read in the gate's own tree, where `plan_hold.py` stood
    let tree = env("L7R_GATE_TREE").map_or_else(|| crate::toplevel_or_dot(cwd), PathBuf::from);
    let hold_ok = env("HOLD_OK").unwrap_or_default();
    let perf_later = env("PERF_LATER_OK").unwrap_or_default();
    let gm_resumed = env(l7r_shared::parked::ESCAPE).unwrap_or_default();
    let mut out = String::new();
    let holds = (hold_ok.as_str(), perf_later.as_str(), gm_resumed.as_str());
    // a bundle, `T=a,b,c` (451 T141): its own start; one task's start as it always was
    let tasks = bundle::members(&args[1]);
    let started = if tasks.len() > 1 {
        bundle::start(cwd, &tree, &args[0], &tasks, holds, &mut out)
    } else {
        start(cwd, &tree, &args[0], &args[1], holds, &mut out)
    };
    match started {
        Ok(None) => reply(out, String::new(), 0),
        Ok(Some(refused)) => reply(out, refused, 2),
        Err(why) => raised("task-start", out, "", &why),
    }
}

mod bundle;

/// The tasks a `T=` names ([`bundle::members`]), for the commands beside this one.
pub(crate) fn members(words: &str) -> Vec<String> {
    bundle::members(words)
}

#[cfg(test)]
mod tests;
