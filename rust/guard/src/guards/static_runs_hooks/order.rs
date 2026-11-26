//! THE CLOSING STEP'S ORDER (feature 451 T55): the closing checks start in the background the moment the code is done, and the plan
//! section and `make decide` are written while they run. WHY: over 39 builders' transcripts, after a builder's last code edit its closing
//! checks ran one after another - 63 min in the foreground and 101 min idle on its own background runs - beside 158 min of model time
//! writing the plan section, running `make decide` and writing the report, none of which needs a check's result (measured 2026-11-21).
//!
//! Two rules:
//! - a `make decide` whose caller's last code edit has no `make closing-checks` started after it is TOLD the order (a NOTICE: an
//!   `additionalContext` line, recorded `noticed` in the guard log). The caller is the builder by its `agent_id` (the log's `by`), else
//!   the main session by its `session_id` with no `by`: a builder sharing the clone is another caller, so a neighbor's edits never fire
//!   it. A start is a `PreToolUse` line naming `closing-checks` that ran (a `PostToolUse` carries its `id`: a backgrounded call's comes
//!   at once, with `bg`). A LANDED edit is no code edit here (T64): one a landing of its own task went out after - a landing's `end`
//!   line later in the log whose `landed` is true and whose `tasks` names the edit line's `task`, `static_runs_hooks`' landed rule
//!   ([`landings`]) - so the notice reads back past it to the caller's last edit not landed. A landing line is the main session's,
//!   so it lands a builder's edits of its tasks too; an edit with no `task` (the log's first hours, 2026-11-20) no landing names.
//!   WHY THE EDIT'S TASK, NOT THE DECIDE'S: the main session was told at every `make decide` of its Makefile edit of
//!   2026-11-20T15:48:51Z, filed under T12, which landed at 15:55:22Z; its decides were filed under the task it was deciding, not
//!   yet landed. Replayed over 451's log to 2026-11-21T08:09Z (211 decides; measured 2026-11-21, `/tmp/claude-T64/replay.py`), the
//!   rule fires on 127, keyed on the decide's task still 127, keyed on the edit's task 105: the 22 it drops are all the main session's
//!   on edits landed, and the main session's 3 left are within 4 min of their edit, before its landing.
//!   A BUILDER (a caller with an `agent_id`) is told both tiers' runs, the first tier's `make builder-checks` first, and a
//!   `builder-checks` it started since its last code edit is a start as `closing-checks` is (451 T308); the main session, which
//!   builds under no tier, is told the closing run alone.
//! - a foreground `make static`, `make hooks-test` or `make closing-checks` (no `run_in_background`) is REFUSED, naming
//!   `run_in_background` and `make closing-checks`, recorded `blocked`; [`TOKEN`] with a reason escapes, recorded. It reads no log.
//!
//! Both name the closing run as the caller starts it, `make closing-checks T=<task> F=<feature>` ([`closing_run`], 451 T86): the task
//! and feature the call's own event-log line is filed under (`event_log_hooks::filed_at`), asked only when something is said.
//!   It is judged FIRST, on every command of the chain: a `make decide` chained with a foreground closing check, either order, is
//!   refused, never covered by the decide notice (T55's open hole, closed red first).
//!   `STATIC_OK` does not stand it aside: that escape is the run count's, and a builder past its count would get a foreground run with it.
//!
//! WHY THE DECIDE RULE IS A NOTICE: replayed over 451's log, the decide rule fired on 75 of 170 `make decide` calls, 45 after the
//! caller's last code edit (the order the finding prices) and 30 with code edited after them - a decide in mid-build, where a refusal
//! would force a check run on unfinished code or an escape: 40% wrong (measured 2026-11-21, the decide rule replayed by hand over
//! `.git/l7r-events/451-time-retro-and-efficiency.jsonl`; T55's plan section). A Bash write (`sed -i`, a heredoc) leaves no Edit line, so
//! it is no code edit here - the notice can miss, never wrongly refuse.
//!
//! WHY THE FOREGROUND RULE REFUSES (T55's plan review, 2026-11-21, ruled a notice there NOT LEGITIMATE): the caller has already chosen
//! to run the check, so a refusal changes only how it is launched - D12's form. Replayed by hand over the same log (measured 2026-11-21:
//! each foreground `make static` or `make hooks-test` call that ran, against what its caller did after it before its next code edit),
//! 55 such calls (51.6 min): none the main session's, none chained with a landing, and 5 (5.5 min) whose result the caller needed at
//! once - mid-build, the check followed only by itself again, a crate-scoped check or a fixer, then a code edit, nothing to run beside
//! it. Those 5 are the refusal's cost and the escape's case; the other 50 were followed by work that needs no check result (T55's plan
//! section). `make closing-checks` has no foreground call in the log: its refusal rests on the review's ruling.

use std::collections::HashMap;

use serde_json::Value;

use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::make::invoked;
use crate::shared::state::field;

/// The foreground rule's escape: its own token, not the run count's `STATIC_OK`.
pub(super) const TOKEN: &str = "FOREGROUND_OK";

/// What the guard says of a call.
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Told {
    /// A `make decide` with no closing checks started since the caller's last code edit: a notice.
    Decide(String),
    /// A closing check run in the foreground: refused.
    Foreground(String),
    /// A closing check run in the foreground, escaped by [`TOKEN`] and its reason.
    Escaped(String),
    /// [`TOKEN`] with no reason: the escape's own refusal.
    NoReason(String),
}

/// The checks a closing run runs together, and the target that runs them.
const CLOSING: [&str; 3] = ["static", "hooks-test", "closing-checks"];
/// The first tier's check run, a builder's in its own tree (451 T308, the two-tier trial of 2026-11-26): tests, lint and format of the
/// crates it changed, the full gate run once at the landing. WHY IT COUNTS AS THE START: a first-tier builder's brief forbids
/// `make closing-checks`, so the notice told it at every `make decide` to start a run it may not start.
const FIRST_TIER: &str = "builder-checks";

/// Is `path` code a closing check checks: inside the clone `root`, and not its plan or tasks (`specs/`), a Markdown document or
/// anything under `.git/` (a handoff file)?
pub(super) fn code_path(path: &str, root: &str) -> bool {
    let Some(rel) = path.strip_prefix(root).and_then(|r| r.strip_prefix('/')) else {
        return false;
    };
    let markdown = std::path::Path::new(rel)
        .extension()
        .is_some_and(|e| e.eq_ignore_ascii_case("md"));
    !(rel.starts_with("specs/") || rel.starts_with(".git/") || markdown)
}

fn text<'a>(line: &'a Value, k: &str) -> &'a str {
    line.get(k).and_then(Value::as_str).unwrap_or("")
}

fn names(line: &Value, target: &str) -> bool {
    text(line, "make") == target
        || line
            .get("makes")
            .and_then(Value::as_array)
            .is_some_and(|ms| ms.iter().any(|m| m == target))
}

/// What the guard says of one call, if anything; `root` (the clone) and `lines` (the event log) are asked only for a `make decide`,
/// `caller` (the feature and task the call's own line is filed under) only for what is said.
pub(super) fn told(
    input: &Value,
    root: &dyn Fn() -> String,
    lines: &dyn Fn() -> Vec<Value>,
    caller: &dyn Fn() -> (String, Option<String>),
) -> Option<Told> {
    let tool = input.get("tool_input")?;
    let cmd = field(tool, "command");
    if !(cmd.contains("decide") || CLOSING.iter().any(|c| cmd.contains(c))) {
        return None;
    }
    let targets = invoked(cmd);
    let background = tool.get("run_in_background") == Some(&Value::Bool(true));
    // the foreground refusal before the decide branch: a decide in the chain must not cover a closing check run beside it
    let closing = targets.iter().find(|t| CLOSING.contains(&t.as_str()));
    if let Some(ran) = closing.filter(|_| !background) {
        return Some(match escape_or_refuse(cmd, TOKEN) {
            Escape::Escaped(why) => Told::Escaped(why),
            Escape::Refused(text) => Told::NoReason(text),
            Escape::None => Told::Foreground(foreground(ran, &run_of(caller))),
        });
    }
    if targets.iter().any(|t| t == "decide") {
        return decide(input, &root(), &lines(), &|| run_of(caller));
    }
    None
}

fn decide(input: &Value, root: &str, lines: &[Value], run: &dyn Fn() -> String) -> Option<Told> {
    let by = field(input, "agent_id");
    let sid = field(input, "session_id");
    let mine = |l: &Value| {
        if by.is_empty() {
            text(l, "by").is_empty() && text(l, "sid") == sid
        } else {
            text(l, "by") == by
        }
    };
    let landed = landings(lines);
    let (at, edit) = lines.iter().enumerate().rev().find(|(at, l)| {
        text(l, "ev") == "PostToolUse"
            && ["Edit", "Write", "NotebookEdit"].contains(&text(l, "tool"))
            && mine(l)
            && code_path(text(l, "path"), root)
            && landed.get(text(l, "task")).is_none_or(|went| went < at)
    })?;
    let after = &lines[at + 1..];
    // a builder's check run is the first tier's too (451 T308); the main session builds under no tier
    let builder = !by.is_empty();
    let started = after.iter().any(|l| {
        text(l, "ev") == "PreToolUse"
            && mine(l)
            && (names(l, "closing-checks") || (builder && names(l, FIRST_TIER)))
            && after
                .iter()
                .any(|p| text(p, "ev") == "PostToolUse" && text(p, "id") == text(l, "id"))
    });
    (!started).then(|| {
        let path = text(edit, "path");
        let rel = path.strip_prefix(root).unwrap_or(path).trim_start_matches('/');
        let (at, run) = (text(edit, "t"), run());
        Told::Decide(if builder {
            format!(
                "T55 order: your last code edit not landed ({rel}, {at}) has no check run started after it. Neither needs the other's \
                 result: start one now with run_in_background: true - under FIRST TIER (your brief says so) `make {FIRST_TIER} \
                 CRATE=\"<the crates you changed>\"`, otherwise `{run}` - and write the plan section and run `make decide` while it runs."
            )
        } else {
            format!(
                "T55 order (feature 451): your last code edit not landed ({rel}, {at}) has no `make closing-checks` started after it. \
                 Neither needs the other's result: start `{run}` now with run_in_background: true (it runs make static, make hooks-test \
                 and make quick at once), and write the plan section and run `make decide` while it runs. When it ends, if you edited \
                 the section after it started, `make quick` (seconds) covers the section."
            )
        })
    })
}

/// Each task's last landing that went out, by its line's place in the log: `static_runs_hooks`' landed rule (`runs`) - a `Phase` `end`
/// line whose `landed` is true and whose `tasks` names the task, whatever its exit code; a refused landing is none.
fn landings(lines: &[Value]) -> HashMap<&str, usize> {
    let mut last = HashMap::new();
    for (at, l) in lines.iter().enumerate() {
        if text(l, "ev") == "Phase"
            && text(l, "step") == "end"
            && l.get("landed") == Some(&Value::Bool(true))
        {
            let tasks = l
                .get("tasks")
                .and_then(Value::as_array)
                .into_iter()
                .flatten();
            for task in tasks.filter_map(Value::as_str) {
                last.insert(task, at);
            }
        }
    }
    last
}

/// The closing run a caller is told to start: `make closing-checks` for the task and feature its own call is filed under.
fn run_of(caller: &dyn Fn() -> (String, Option<String>)) -> String {
    let (feature, task) = caller();
    closing_run(&feature, task.as_deref())
}

/// `make closing-checks` as the caller starts it (451 T86): `T=` its task and `F=` its feature's number, so the run judges the files
/// and crates that task changed, another task's red apart. WHY NAMED: with no `T=` the run judges the whole clone, another builder's
/// half-done crate counted - the verdict T86 exists to fix. A call filed under no task, or outside any clone, gets the placeholders.
pub(super) fn closing_run(feature: &str, task: Option<&str>) -> String {
    let number = feature.split('-').next().unwrap_or(feature);
    let feature = if !number.is_empty() && number.bytes().all(|b| b.is_ascii_digit()) {
        number
    } else if feature.is_empty() {
        "<feature>"
    } else {
        feature
    };
    format!(
        "make closing-checks T={} F={feature}",
        task.unwrap_or("<your task>")
    )
}

fn foreground(target: &str, run: &str) -> String {
    format!(
        "\n\u{1b}[1mBLOCKED (static-runs, the closing step's order - feature 451 T55): `make {target}` in the foreground.\u{1b}[0m\n\n\
It blocks you on a check while the work beside it waits: after builders' last code edits, 63 min of closing checks ran in the\n\
foreground beside 158 min of writing that needs no check's result.\n\n\
Do this instead: the same call with run_in_background: true; its completion notice wakes you. Once the code is done,\n\
`{run}` runs make static, make hooks-test and make quick at once with one combined result: start it with\n\
run_in_background: true, then write the plan section and run `make decide` while it runs.\n\n\
Escape: {TOKEN}=\"<reason>\" in the command, recorded in the guard log - for a run whose result your very next step needs, with\n\
nothing to do beside it. (STATIC_OK is the run count's escape, not this one's.)\n"
    )
}

#[cfg(test)]
mod tests;
