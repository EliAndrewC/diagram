//! `static-runs-hooks` (feature 451 T14, FR-007, plan D11; research R6): A TASK'S THIRD `make static` SINCE ITS LAST LANDING IS REFUSED.
//! WHY: `make static` - every crate's lint, format, coverage and dead-code checks and the repository's static checks - was the edit
//! loop: 30.8 of a window's tool-minutes (research R1), where the approved route is "a crate-scoped check while iterating, with make
//! static once at the end". The refusal names the crate-scoped checks for the crates the task's delta changes.
//!
//! THE COUNT (D11), read through the event log's one reader (`event_log_hooks::read`) from the log the call's own line goes to, under
//! the task that line carries ([`filed_at`], the writer's own chain - so the main session and its builders share one count by task,
//! a `fallback` line too: the call being judged is filed by the same chain):
//! - a RUN is a `PreToolUse` line whose `make` is `static`, or whose `makes` holds it (a `make rust-test CRATE=x && make static`), and
//!   whose call ran: a `PostToolUse` or `PostToolUseFailure` line carries its `id`. A call another guard refused (`make static &`
//!   refused by `no_poll_hooks`) leaves a `PreToolUse` line and no other, and ran nothing: 1 of 33 such lines in 451's log and 8 of
//!   340 in 449's (observed 2026-11-20, method: the logs' `make: static` `PreToolUse` lines with no line of their `id` after). The call
//!   being judged is never one: in the whole chain `event_log_hooks` has written its `PreToolUse` line before this guard reads, and its
//!   `id` is set aside;
//! - SINCE the task's last landing that succeeded - a landing's `end` line (feature 451 T06) whose `landed` is true and whose `tasks`
//!   names it, whatever its exit code (3 with its ticks standing is a landing; a refused landing is not) - else since its FIRST
//!   `task-starts.jsonl` entry for the feature (a later `make task-start` resets nothing: 48 of the clone's 498 started tasks have more
//!   than one entry, R6), else every line of it;
//! - the knob [`STATIC_RUNS_A_TASK`] such runs pass; the next is refused. `STATIC_OK="<reason>"` escapes, recorded.
//!
//! A call whose line carries no task is passed, the pass recorded as `no-task` (plan D10's precedent): there is nothing to count by.

use std::collections::{BTreeSet, HashSet};
use std::path::Path;

use serde_json::Value;

use crate::guards::event_log_hooks::read::read_jsonl;
use crate::guards::event_log_hooks::{common_git_dir, filed_at};
use crate::protocol::{Answer, Event, Guard};
use crate::shared::checks::git_stdout;
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::make::invoked;
use crate::shared::session::Session;
use crate::shared::state::field;

mod order;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "static-runs-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// The runs of `make static` a task makes between landings before the next is refused: GUESS, 2 (plan D11) - one to see the static
/// checks' findings, one to confirm them fixed before the landing. Retuned from SC-005's count of runs per task (T22).
pub const STATIC_RUNS_A_TASK: usize = 2;

const TOKEN: &str = "STATIC_OK";

/// What the guard says of a `make static` call it does not simply pass.
#[derive(Debug, PartialEq, Eq)]
enum Said {
    /// The call's line carries no task: passed, the pass recorded.
    NoTask,
    /// Past the knob: refused, naming the task, its runs and the crates its delta changes.
    Refused {
        feature: String,
        task: String,
        runs: usize,
        crates: Vec<String>,
    },
    /// Past the knob, escaped by `STATIC_OK` and its reason.
    Escaped(String),
    /// Past the knob, `STATIC_OK` with no reason: the escape's own refusal.
    NoReason(String),
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    answer(event, session, &here, &|k| std::env::var(k).ok())
}

/// The answers to one call, its environment read through `env`, and each firing recorded.
fn answer(
    event: &Event,
    session: &Session,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
) -> Vec<Answer> {
    let said = judge(&event.input, here, env, &delta_crates);
    let log = |kind: &str, detail: &str, rule: &str| {
        fire("static-runs", kind, detail, rule, &event.input, session);
    };
    // both rules' answers together: a call that breaks both hears both at once
    let mut out = refusals(said, &log);
    out.extend(order_answer(&event.input, here, env, &log));
    out
}

/// The closing step's order (T55, `order.rs`): a decide told it, a foreground closing check refused, each firing recorded.
fn order_answer(
    input: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
    log: &dyn Fn(&str, &str, &str),
) -> Option<Answer> {
    let filed = std::cell::OnceCell::new();
    let at = || filed.get_or_init(|| filed_at(input, here, env)).clone();
    let read = || {
        at().and_then(|(_, _, log, _)| read_jsonl(&log).ok())
            .unwrap_or_default()
    };
    let root = || {
        at().map(|(root, ..)| root.to_string_lossy().into_owned())
            .unwrap_or_default()
    };
    // the feature and task the call's own line is filed under: the closing run its notice and refusal name (451 T86)
    let caller = || {
        at().map(|(_, feature, _, task)| (feature, task))
            .unwrap_or_default()
    };
    match order::told(input, &root, &read, &caller)? {
        order::Told::Decide(text) => {
            log(
                "noticed",
                "decide-before-closing-checks",
                "decide-before-closing-checks",
            );
            Some(Answer::Notice(text))
        }
        order::Told::Foreground(text) => {
            log(
                "blocked",
                "a closing check in the foreground",
                "closing-check-foreground",
            );
            Some(Answer::Refuse(text))
        }
        order::Told::Escaped(why) => {
            log("escaped", &why, "foreground-ok");
            None
        }
        order::Told::NoReason(text) => {
            let rule = format!("{}-no-reason", order::TOKEN);
            log(
                "blocked",
                &format!("{} with no reason", order::TOKEN),
                &rule,
            );
            Some(Answer::Refuse(text))
        }
    }
}

/// A verdict's answers, each firing recorded.
fn refusals(said: Option<Said>, log: &dyn Fn(&str, &str, &str)) -> Vec<Answer> {
    match said {
        None => Vec::new(),
        Some(Said::NoTask) => {
            log("passed", "make static, no task", "no-task");
            Vec::new()
        }
        Some(Said::Escaped(why)) => {
            log("escaped", &why, "static-ok");
            Vec::new()
        }
        Some(Said::NoReason(text)) => {
            log("blocked", "STATIC_OK with no reason", "STATIC_OK-no-reason");
            vec![Answer::Refuse(text)]
        }
        Some(Said::Refused {
            feature,
            task,
            runs,
            crates,
        }) => {
            log(
                "blocked",
                &format!("{feature} {task}: {runs} runs"),
                "third-static",
            );
            vec![Answer::Refuse(refusal(&feature, &task, runs, &crates))]
        }
    }
}

/// The verdict on one hook input: None to pass it silently. `crates` lists the crates a clone's delta changes, asked only to refuse.
fn judge(
    input: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
    crates: &dyn Fn(&Path) -> Vec<String>,
) -> Option<Said> {
    let cmd = input.get("tool_input").map_or("", |t| field(t, "command"));
    // NO `static` (nor `closing-checks`, which runs it - T55), NO READ: every other Bash call ends here
    if !(cmd.contains("static") || cmd.contains("closing-checks"))
        || !invoked(cmd).iter().any(|t| is_run(t))
    {
        return None;
    }
    let (root, feature, log, task) = filed_at(input, here, env)?;
    let Some(task) = task else {
        return Some(Said::NoTask);
    };
    let lines = read_jsonl(&log).unwrap_or_default();
    let starts = std::fs::read_to_string(common_git_dir(&root).join("task-starts.jsonl"))
        .unwrap_or_default();
    let runs = runs(
        &lines,
        &starts,
        &feature,
        &task,
        field(input, "tool_use_id"),
    );
    if runs < STATIC_RUNS_A_TASK {
        return None;
    }
    Some(match escape_or_refuse(cmd, TOKEN) {
        Escape::Escaped(why) => Said::Escaped(why),
        Escape::Refused(text) => Said::NoReason(text),
        Escape::None => Said::Refused {
            feature,
            task,
            runs,
            crates: crates(&root),
        },
    })
}

/// A target that is a run of `make static`: itself, or `make closing-checks`, which runs it beside `make hooks-test` and `make quick`
/// (feature 451 T55) - one run of it, as its one call is one line of the log.
fn is_run(target: &str) -> bool {
    target == "static" || target == "closing-checks"
}

fn text<'a>(line: &'a Value, k: &str) -> &'a str {
    line.get(k).and_then(Value::as_str).unwrap_or("")
}

/// A time as one form compares: `task-starts.jsonl`'s `utc` is to the second (`...:26Z`) and a log line's `t` to the millisecond
/// (`...:26.500Z`), and as strings `.` sorts before `Z`, so a second's stamp is written `.000Z`.
fn stamp(t: &str) -> String {
    match t.strip_suffix('Z') {
        Some(head) if !head.contains('.') => format!("{head}.000Z"),
        _ => t.to_owned(),
    }
}

/// The task's `make static` runs the log records since its last landing, else its first start for `feature`, else ever; `own` is the
/// call being judged, never counted.
fn runs(lines: &[Value], starts: &str, feature: &str, task: &str, own: &str) -> usize {
    let landed = lines
        .iter()
        .filter(|l| {
            text(l, "ev") == "Phase"
                && text(l, "step") == "end"
                && l.get("landed") == Some(&Value::Bool(true))
                && l.get("tasks")
                    .and_then(Value::as_array)
                    .is_some_and(|ts| ts.iter().any(|t| t == task))
        })
        .map(|l| stamp(text(l, "t")))
        .max();
    // after a landing, strictly; from a start, the start's own second on
    let since = landed.map(|t| (t, false)).or_else(|| {
        starts
            .lines()
            .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
            .find(|e| text(e, "feature") == feature && text(e, "task") == task)
            .map(|e| (stamp(text(&e, "utc")), true))
    });
    let ran: HashSet<&str> = lines
        .iter()
        .filter(|l| ["PostToolUse", "PostToolUseFailure"].contains(&text(l, "ev")))
        .map(|l| text(l, "id"))
        .collect();
    lines
        .iter()
        .filter(|l| {
            let id = text(l, "id");
            let t = stamp(text(l, "t"));
            text(l, "ev") == "PreToolUse"
                && text(l, "task") == task
                && (is_run(text(l, "make"))
                    || l.get("makes")
                        .and_then(Value::as_array)
                        .is_some_and(|ms| ms.iter().any(|m| m.as_str().is_some_and(is_run))))
                && id != own
                && ran.contains(id)
                && since
                    .as_ref()
                    .is_none_or(|(s, from)| t > *s || (*from && t == *s))
        })
        .count()
}

/// The crates the clone's delta changes: the files `git diff --name-only` of `origin/main`'s merge base names, and the untracked ones,
/// each under `rust/` mapped to the nearest directory above it whose `Cargo.toml` is a package's.
fn delta_crates(root: &Path) -> Vec<String> {
    let base = git_stdout(root, &["merge-base", "HEAD", "origin/main"]);
    let mut paths = String::new();
    if !base.is_empty() {
        paths = git_stdout(root, &["diff", "--name-only", &base]);
    }
    paths.push('\n');
    paths.push_str(&git_stdout(
        root,
        &["ls-files", "--others", "--exclude-standard"],
    ));
    crates_of(root, paths.lines())
}

pub(crate) fn crates_of<'a>(root: &Path, paths: impl Iterator<Item = &'a str>) -> Vec<String> {
    let mut out = BTreeSet::new();
    for p in paths.filter(|p| p.starts_with("rust/")) {
        let found = Path::new(p).ancestors().skip(1).find(|a| {
            std::fs::read_to_string(root.join(a).join("Cargo.toml"))
                .is_ok_and(|t| t.contains("[package]"))
        });
        if let Some(c) = found {
            out.insert(c.to_string_lossy().into_owned());
        }
    }
    out.into_iter().collect()
}

/// The refusal: the count, the crate-scoped checks for the crates as ONE command, its list said once (`make crate-checks`, 451 T170:
/// four lines a crate reached builders at up to 7,909 characters over 25 crates, 4,054 on average, measured 2026-11-23; held at its
/// worst case, every crate of the workspace, by `suite_tools/messages/worst.rs`), `make static` once before the landing, the escape.
pub(crate) fn refusal(feature: &str, task: &str, runs: usize, crates: &[String]) -> String {
    let checks = if crates.is_empty() {
        "  This task's delta changes no Rust crate (against origin/main's merge base): `make quick` is its edit loop.\n".to_owned()
    } else {
        format!("  make crate-checks CRATE=\"{}\"\n", crates.join(" "))
    };
    let run = order::closing_run(feature, Some(task));
    format!(
        "\n\u{1b}[1mBLOCKED: {task} of {feature} has run `make static` {runs} times since its last landing (feature 451 FR-007).\u{1b}[0m\n\n\
`make static` is the check before a landing, not the edit loop: it runs every crate's checks. While iterating, run the\n\
test, lint, format and cover checks of the crates this task changes:\n\n{checks}\n\
then `make static` once, before `make land` (or `{run}` in the background: it runs make static, make hooks-test\n\
and make quick at once, and is one run of `make static`) - a landing of {task} that goes out starts the count again; a later\n\
`make task-start` does not.\n\n\
Escape: {TOKEN}=\"<reason>\" in the command, recorded in the guard log.\n"
    )
}

#[cfg(test)]
mod tests;
