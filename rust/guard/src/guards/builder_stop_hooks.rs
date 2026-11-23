//! `builder-stop-hooks` (feature 451 T84): A BUILDER STOPS READY TO LAND. WHY: over the night of 2026-11-20/21 (29 tasks, 43 builders)
//! about 16 builder reports asked the session to file a task and every MODE 4 plan review was left to it, each BLOCK answered by a fresh
//! builder re-reading a handoff; a builder can dispatch its own review (measured 2026-11-21, the session's subagent transcripts: 27 of 205
//! builders did, 35 calls, every one launched, none refused by a guard), so nothing but the briefs stood in the way.
//!
//! WHO IS HELD: a `SubagentStop` of a builder - `agent_id` present, its `agent_type` no `.claude/agents/<type>.md` of the clone, as
//! `context_cap_hooks` reads one (D8) - dispatched by the session itself (its meta file's `spawnDepth` 1: a builder's own helper is not
//! held), whose brief names a feature and a task (its meta `description` opening `<feature> T<n>`, or a bundle's, its first member - 449 T268), that task started
//! (`<git common dir>/task-starts.jsonl`) and open in the feature's tasks.md. Every other stop passes before any file but the meta is read.
//!
//! WHAT HOLDS IT: the gate's own reading of the verdict store `make plan-verdict` writes, asked per task (`l7r-gate plan decided <root>
//! <feature> <task>`, `task::task_refusal`): the task's plan section carries no current CLEAR verdict (a wording-only section, its task
//! verdict typo aside, or every block CLEAR), or a found-and-left deferral in it names no filed open task. The stop is answered with
//! `decision: block` and that reason, so the builder keeps working: the refusal names `make decide F= T=` and the review to dispatch.
//!
//! THE EXITS, in order: `STOP_OK="<reason>"` in the builder's final message (`last_assistant_message`), recorded; a builder past
//! `CONTEXT_CAP_TOKENS`, whose every call but its handoff is refused, passes, recorded; a spec-fidelity review the builder launched and
//! whose notification has not come passes, recorded - its notification wakes the builder, whose next stop is judged again (measured
//! 2026-11-21: T71's builder stopped at 12:20:50Z, its review's notification woke it at 12:21:24Z, it stopped again at 12:21:28Z); a
//! gate that cannot answer within [`ASK_LIMIT`] passes, recorded.

use std::path::{Path, PathBuf};
use std::time::Duration;

use serde_json::Value;

use crate::guards::context_cap_hooks::CONTEXT_CAP_TOKENS;
use crate::guards::event_log_hooks::common_git_dir;
use crate::guards::set_down_hooks::builder_brief;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::context::{context, own_transcript};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log::fire;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask_within;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "builder-stop-hooks",
    events: &["SubagentStop"],
    matcher: "*",
    decide,
};

const TOKEN: &str = "STOP_OK";

/// How long the gate is given to answer: GUESS, 40 s - under the hook's 60 s, above the gate wrapper's rebuild of a changed plan crate.
pub const ASK_LIMIT: Duration = Duration::from_secs(40);

/// What the guard says of one stop.
#[derive(Debug, PartialEq, Eq)]
pub(crate) enum Said {
    /// Not held, nothing recorded.
    Quiet,
    /// Not held, recorded: (rule, detail).
    Passed(&'static str, String),
    /// Held: (the reason the builder reads, the detail recorded).
    Held(String, String),
    /// `STOP_OK` with no reason: held, its refusal the escape's.
    NoReason(String),
}

/// The gate's answer: (exit code, its stdout), asked from `root` with `args`.
pub(crate) type Ask<'a> = &'a dyn Fn(&Path, &[&str]) -> (i32, String);

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let clone = session.clone_dir().map(Path::to_path_buf);
    let ask = |root: &Path, args: &[&str]| {
        let script = root.join("scripts/gates/l7r-gate.sh");
        let mut all = vec![script.to_str().unwrap_or("")];
        all.extend_from_slice(args);
        let said = ask_within(root, "bash", &all, ASK_LIMIT);
        (said.code, said.out)
    };
    let said = judge(&event.input, &here, clone, &ask);
    let log = |kind: &str, detail: &str, rule: &str| {
        fire("builder-stop", kind, detail, rule, &event.input, session);
    };
    match said {
        Said::Quiet => Vec::new(),
        Said::Passed(rule, detail) => {
            log(
                if rule == "stop-ok" {
                    "escaped"
                } else {
                    "passed"
                },
                &detail,
                rule,
            );
            Vec::new()
        }
        Said::Held(reason, detail) => {
            log("blocked", &detail, "not-ready");
            vec![Answer::StopBlock(reason)]
        }
        Said::NoReason(text) => {
            log("blocked", "STOP_OK with no reason", "STOP_OK-no-reason");
            vec![Answer::StopBlock(text)]
        }
    }
}

/// An id no path can take is no agent's.
fn plain(name: &str) -> bool {
    !name.is_empty()
        && name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
}

fn tree_of(cwd: &Path) -> Option<PathBuf> {
    cwd.ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
}

/// The verdict on one stop. `clone` is the session's clone (451 T60: a builder's shell may stand in the mirror); `ask` the gate.
pub(crate) fn judge(input: &Value, here: &Path, clone: Option<PathBuf>, ask: Ask<'_>) -> Said {
    let agent = field(input, "agent_id");
    if !plain(agent) {
        return Said::Quiet;
    }
    let cwd = match field(input, "cwd") {
        "" => here.to_path_buf(),
        c => PathBuf::from(c),
    };
    let Some(tree) = clone
        .filter(|c| c.join(".git").exists())
        .or_else(|| tree_of(&cwd))
    else {
        return Said::Quiet;
    };
    let kind = field(input, "agent_type");
    if plain(kind)
        && tree
            .join(".claude/agents")
            .join(format!("{kind}.md"))
            .is_file()
    {
        return Said::Quiet;
    }
    let own = match field(input, "agent_transcript_path") {
        "" => own_transcript(field(input, "transcript_path"), agent),
        p => Some(PathBuf::from(p)),
    };
    let Some(own) = own else {
        return Said::Quiet;
    };
    let Some((feature, task)) = brief_of(&own) else {
        return Said::Quiet;
    };
    match escape_or_refuse(field(input, "last_assistant_message"), TOKEN) {
        Escape::Escaped(why) => return Said::Passed("stop-ok", format!("{feature} {task}: {why}")),
        Escape::Refused(text) => return Said::NoReason(text),
        Escape::None => {}
    }
    if let Some(tokens) = context(&own).filter(|t| *t > CONTEXT_CAP_TOKENS) {
        return Said::Passed("past-cap", format!("{feature} {task}: {tokens} tokens"));
    }
    let Some(dir) = spec_dir(&tree, &feature) else {
        return Said::Quiet;
    };
    if !started_and_open(&tree, &dir, &task) {
        return Said::Quiet;
    }
    if let Some(id) = review_in_flight(&own) {
        return Said::Passed("review-in-flight", format!("{feature} {task}: {id}"));
    }
    let root = tree.to_string_lossy();
    let (code, out) = ask(&tree, &["plan", "decided", &root, &feature, &task]);
    match code {
        0 => Said::Quiet,
        1 => Said::Held(
            refusal(out.trim(), &feature, &task),
            format!("{feature} {task}: {}", out.trim()),
        ),
        _ => Said::Passed("gate-unanswered", format!("{feature} {task}: exit {code}")),
    }
}

/// (feature, task) the builder's brief names, read from its meta file - only a builder the session dispatched (`spawnDepth` 1) - by the
/// Stop hook's own reader (`set_down_hooks::builder_brief`, 449 T268): a bundle's builder is held on its first member, whose section
/// is every member's (451 T141). WHY: this guard's `<feature> T<n>` brief matched no bundle description (`449 bundle T258, T268, T269:
/// ...`, `449 record bundle: ...`, both live on 2026-11-22), so a bundle's builder stopped unheld (found by 449 T268, fixed here).
fn brief_of(own: &Path) -> Option<(String, String)> {
    let id = own
        .file_stem()?
        .to_string_lossy()
        .strip_prefix("agent-")?
        .to_owned();
    let (feature, tasks) = builder_brief(own.parent()?, &id)?;
    Some((feature, tasks.into_iter().next()?))
}

/// The one `specs/<feature>-*` directory with a tasks.md.
fn spec_dir(tree: &Path, feature: &str) -> Option<PathBuf> {
    let mut found = std::fs::read_dir(tree.join("specs"))
        .ok()?
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .and_then(|n| n.to_str())
                .is_some_and(|n| n.starts_with(&format!("{feature}-")))
                && p.join("tasks.md").is_file()
        });
    let one = found.next()?;
    found.next().is_none().then_some(one)
}

/// The task has a start in the clone's `task-starts.jsonl` and an open box in its tasks.md.
fn started_and_open(tree: &Path, dir: &Path, task: &str) -> bool {
    let name = dir.file_name().and_then(|n| n.to_str()).unwrap_or("");
    let starts =
        std::fs::read_to_string(common_git_dir(tree).join("task-starts.jsonl")).unwrap_or_default();
    let started = starts
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
        .any(|v| {
            v.get("feature").and_then(Value::as_str) == Some(name)
                && v.get("task").and_then(Value::as_str) == Some(task)
        });
    let open = format!("- [ ] {task} ");
    started
        && std::fs::read_to_string(dir.join("tasks.md"))
            .unwrap_or_default()
            .lines()
            .any(|l| format!("{} ", l.trim_start()).starts_with(&open))
}

/// The id of a spec-fidelity review the builder launched whose notification has not come: its Agent call's result names the launched
/// agent (`agentId: <id>`), its completion a `<task-id><id></task-id>` notification later in the transcript.
fn review_in_flight(own: &Path) -> Option<String> {
    let text = std::fs::read_to_string(own).ok()?;
    let mut calls: Vec<String> = Vec::new();
    let mut launched: Vec<String> = Vec::new();
    for row in text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l).ok())
    {
        let content = row.pointer("/message/content").and_then(Value::as_array);
        for b in content.into_iter().flatten() {
            let kind = b.get("type").and_then(Value::as_str);
            if kind == Some("tool_use")
                && b.pointer("/input/subagent_type").and_then(Value::as_str)
                    == Some("spec-fidelity")
            {
                calls.push(b.get("id").and_then(Value::as_str).unwrap_or("").to_owned());
            }
            if kind == Some("tool_result")
                && calls
                    .iter()
                    .any(|c| Some(c.as_str()) == b.get("tool_use_id").and_then(Value::as_str))
            {
                let said = b.get("content").map(Value::to_string).unwrap_or_default();
                if let Some(id) = said
                    .split("agentId: ")
                    .nth(1)
                    .and_then(|r| r.split(|c: char| !c.is_ascii_alphanumeric()).next())
                {
                    launched.push(id.to_owned());
                }
            }
        }
    }
    launched
        .into_iter()
        .rev()
        .find(|id| !text.contains(&format!("<task-id>{id}</task-id>")))
}

/// The tail of the gate's no-CLEAR why (`task::task_refusal`): the review to dispatch and the fix, which the block says once, with
/// the review's type, its wake and the deferrals.
const NO_CLEAR_TAIL: &str =
    " and dispatch the MODE 4 review it prints yourself, then fix what it finds";

/// The block: the gate's why, which names the decide, the review to dispatch and the fix, then what it does not. 451 T177
/// (message-check): the block had said the decide and the review twice; "A builder ends ready to land (feature 451 T84)" and
/// "(recorded)" were cut - the feature is this module's, the record the guard log's. Its second round (the round arbiter's
/// ask:guard-wordings-third-round) put "its notification wakes you" back, since without it a builder may poll or end its turn, and
/// merged the why's review into one sentence; a why without that tail (a deferral alone, which names its own `make task-add`) owes
/// no review, so it is said as the gate gave it.
fn refusal(why: &str, feature: &str, _task: &str) -> String {
    let review = format!(", then dispatch the MODE 4 review it prints (subagent_type spec-fidelity, in the background; its notification wakes you), fix its findings, and file each deferral with `make task-add F={feature} TITLE=\"...\"`");
    let said = why.replacen(NO_CLEAR_TAIL, &review, 1);
    format!(
        "builder-stop: {said}\nA builder that cannot finish ends its final message with {TOKEN}=\"<reason>\"; past the context cap it needs none - write the handoff and stop.\n"
    )
}

#[cfg(test)]
mod tests;
