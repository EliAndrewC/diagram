//! The batches and the carries read from the logs, for the booking's second tier (feature 451 T298; the rule is `book/tier.rs`'s doc).
//!
//! A BATCH is found from the landing's own `Phase` lines, never from its run's label: each `src: land`, `step: end` line carries its
//! `tasks` and whether it `landed`, its `gate` step the gate's seconds. Attempts over the same tasks of one feature join one batch
//! until one lands. A `make land` run with no end line (in flight at the window's end, or killed) is an open attempt, its tasks
//! read from its command's `T=`, else the task its line names.
//!
//! A CARRY's task is not on its line (the mark names whatever the session last started: on 2026-11-26 T309's and T289's carries were
//! both logged under T305). It is read from the command's `FROM=<tree>` and the builder pool's log (`builder-pool.log` in the clone's
//! git directory, `make builder-tree`'s record): the task holding that tree when the carry's run BEGAN. Read at the run's end it was
//! the next task's wherever a landing's release and the next handout retook the tree in the run's last second: on 2026-11-26 the carry
//! from diagram-backlog-t271 that ended 19:40:54Z was booked to T308, which took the tree at 19:40:54Z, where T301 had held it until
//! then (451 T346).

use std::collections::HashMap;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::guards::event_log_hooks::common_git_dir;
use serde_json::Value;

use super::super::events::{get, is, or_s, re, t_of, ts, Event, Raised};
use super::super::where_time::columns::Runs;
use super::book::{ran, Attempt, Batch};

static FROM: LazyLock<Regex> = LazyLock::new(|| re(r#"\bFROM=["']?([^\s"']+)"#));
static TASKS: LazyLock<Regex> =
    LazyLock::new(|| re(r#"\bland\b[^\n;&|]*?\sT=(?:"([^"]*)"|'([^']*)'|(\S+))"#));

/// One tree handed to a task: (when, the tree's directory name, `<feature number> <task> ...`).
pub type Take = (f64, String, String);

/// A path's last part: a tree's directory name.
pub(super) fn dir_name(path: &str) -> String {
    path.trim_end_matches('/')
        .rsplit('/')
        .next()
        .unwrap_or("")
        .to_owned()
}

/// Every `take` of every tree's pool log, in time order.
#[must_use]
pub fn takes(bases: &[std::path::PathBuf]) -> Vec<Take> {
    let mut out: Vec<Take> = Vec::new();
    for base in bases {
        let text = std::fs::read_to_string(common_git_dir(base).join("builder-pool.log"))
            .unwrap_or_default();
        for v in text
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        {
            let field = |k: &str| v.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
            let take = (
                ts(&field("utc")).unwrap_or(0.0),
                dir_name(&field("tree")),
                field("detail"),
            );
            if field("event") == "take" && !out.contains(&take) {
                out.push(take);
            }
        }
    }
    out.sort_by(|a, b| a.0.total_cmp(&b.0));
    out
}

/// A carry found: its run's id, when it ended, and the pool's detail of what it carried (`451 T309`).
pub type Carry = (String, f64, String);

/// Each main session's `make carry` whose tree the pool's log names a holder for, the holder when the run began (the module's doc).
#[must_use]
#[expect(clippy::implicit_hasher, reason = "the map `read_subagents` makes")]
pub fn carries(runs: &Runs, commands: &HashMap<String, String>, takes: &[Take]) -> Vec<Carry> {
    let mut out = Vec::new();
    for r in runs
        .runs
        .iter()
        .filter(|r| r.by.is_empty() && ran(r, commands).iter().any(|m| m == "carry"))
    {
        let tree = commands
            .get(&r.id)
            .and_then(|c| FROM.captures(c).ok().flatten().map(|m| dir_name(&m[1])));
        let held = tree.and_then(|tree| {
            takes
                .iter()
                .rfind(|(at, name, _)| *name == tree && *at <= r.t0)
        });
        if let Some((_, _, detail)) = held {
            out.push((r.id.clone(), r.t1, detail.clone()));
        }
    }
    out
}

/// The tasks a landing's command names (`make land ... T="A B"` or `T=A,B`).
fn named(command: &str) -> Vec<String> {
    let Ok(Some(c)) = TASKS.captures(command) else {
        return Vec::new();
    };
    let text = c
        .get(1)
        .or(c.get(2))
        .or(c.get(3))
        .map_or("", |m| m.as_str());
    text.split([' ', ','])
        .filter(|t| !t.is_empty())
        .map(str::to_owned)
        .collect()
}

/// The batches of the lines read (the module's doc): `aside` the set-aside lines, `stream` the calls' (a run's feature is its call's).
///
/// # Errors
///
/// A line's time the reader cannot read.
#[expect(clippy::implicit_hasher, reason = "the map `read_subagents` makes")]
pub fn batches(
    (stream, aside): (&[Event], &[Event]),
    runs: &Runs,
    commands: &HashMap<String, String>,
    carried: &[Carry],
) -> Result<Vec<Batch>, Raised> {
    let land = |step: &'static str| {
        aside
            .iter()
            .filter(move |e| is(e, "ev", "Phase") && is(e, "src", "land") && is(e, "step", step))
    };
    let span = |e: &Event, k: &str| ts(&or_s(e, k));
    let mut gates: Vec<(String, f64, f64)> = Vec::new();
    for e in land("gate") {
        gates.push((or_s(e, "feature"), span(e, "t0")?, span(e, "t1")?));
    }
    let gate_in = |feature: &str, t0: f64, t1: f64| -> f64 {
        gates
            .iter()
            .filter(|(f, a, b)| f == feature && t0 <= *a && *b <= t1)
            .map(|(_, a, b)| b - a)
            .sum()
    };
    let mut found: Vec<(String, Vec<String>, Attempt)> = Vec::new();
    for e in land("end") {
        let (feature, t1) = (or_s(e, "feature"), t_of(e)?);
        let t0 = span(e, "t0").unwrap_or(t1);
        let tasks: Vec<String> = get(e, "tasks")
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
            .map(str::to_owned)
            .collect();
        let attempt = Attempt {
            t0,
            t1,
            landed: get(e, "landed").as_bool() == Some(true),
            gate: gate_in(&feature, t0, t1),
            open: false,
        };
        found.push((feature, tasks, attempt));
    }
    // a landing's run that wrote no end line: in flight at the window's end, or killed
    let feature_of: HashMap<String, String> = stream
        .iter()
        .filter(|e| is(e, "ev", "PreToolUse"))
        .map(|e| (or_s(e, "id"), or_s(e, "feature")))
        .collect();
    for r in runs
        .runs
        .iter()
        .filter(|r| r.by.is_empty() && ran(r, commands).iter().any(|m| m == "land"))
    {
        let feature = feature_of.get(&r.id).cloned().unwrap_or_default();
        if found
            .iter()
            .any(|(f, _, a)| *f == feature && r.t0 - 1.0 <= a.t0 && a.t0 <= r.t1)
        {
            continue;
        }
        let mut tasks = commands.get(&r.id).map_or_else(Vec::new, |c| named(c));
        if tasks.is_empty() {
            tasks.push(r.task.clone());
        }
        let attempt = Attempt {
            t0: r.t0,
            t1: r.t1,
            landed: false,
            gate: gate_in(&feature, r.t0, r.t1),
            open: true,
        };
        found.push((feature, tasks, attempt));
    }
    found.sort_by(|a, b| a.2.t0.total_cmp(&b.2.t0));
    let mut out: Vec<Batch> = Vec::new();
    for (feature, tasks, attempt) in found {
        match out
            .iter_mut()
            .rfind(|b| b.feature == feature && b.tasks == tasks && b.landed().is_none())
        {
            Some(b) => b.attempts.push(attempt),
            None => out.push(Batch {
                feature,
                tasks,
                attempts: vec![attempt],
                carried: Vec::new(),
            }),
        }
    }
    for b in &mut out {
        let end = b.attempts.last().map_or(0.0, |a| a.t1);
        for task in &b.tasks {
            // the task's FIRST carry before the landing: a second (a repair's) is the batch's own
            let first = carried.iter().find(|(_, at, detail)| {
                let mut words = detail.split_whitespace();
                let f = words.next().unwrap_or("");
                *at <= end
                    && (b.feature == f || b.feature.starts_with(&format!("{f}-")))
                    && words.any(|w| w == task)
            });
            if let Some((_, at, _)) = first {
                b.carried.push((task.clone(), *at));
            }
        }
    }
    Ok(out)
}
