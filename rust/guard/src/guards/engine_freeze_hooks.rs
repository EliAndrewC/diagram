//! `engine-freeze-hooks` (feature 429; ported from the shell of the same name and `lib/hm_engine_freeze.py`, feature 449 T018): NO
//! ENGINE EDIT WHILE A MAP REVIEW THIS SESSION LAUNCHED IS STILL RUNNING. A review's verdict is recorded against the engine it reviewed;
//! engine code edited under running reviews made each record NOT-REVIEWABLE, a whole extra round each time (features 261 and 317). No
//! escape: the compliant routes are to wait, or to stop the review (`TaskStop`) and ack it. A roll in the clone freezes the engine too
//! (feature 444, 2026-11-05: a crate edit rebuilt the extension under the rolls still to come).
//!
//! FINISHED, read from the agent's own files: its `meta.json` says `"finished": true`, its transcript's last record ended its turn
//! (`stop_reason: end_turn`), or the session acked it. Anything else is live, stalled or not, however old (a slow review looks exactly
//! like a dead one, and `TaskStop` then ack is the route).
//!
//! Plan T018's decisions: (a) the reviews, the rolls and the words in-process; (b) `l7r-gate plan engine-edit` answers "is this an
//! engine edit, and more than a docstring", asked only once something is live; (c) `REVIEW_AGENTS` read directly.

use std::path::{Path, PathBuf};
use std::time::SystemTime;

use serde_json::{json, Value};

use crate::guards::agent_stall_hooks::last_record;
use crate::guards::finished_run_hooks::runs::{owner, realpath, Procs};
use crate::guards::pair_hooks::REVIEW_AGENTS;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "engine-freeze-hooks",
    events: &["PreToolUse"],
    matcher: "Edit|Write|NotebookEdit",
    decide,
};

/// The rolls an engine edit may not land under: each builds the Rust extension once and rolls on it.
const ROLLS: [&str; 3] = [
    "l7r.diagram.tools.rust_gate",
    "l7r.diagram.tools.cohort",
    "l7r.diagram.tools.work_budget",
];

/// What one decision reads.
pub(crate) struct Ctx {
    pub procs: Procs,
    pub stale: u64,
    pub tree: PathBuf,
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(
        event,
        session,
        &Ctx {
            procs: Procs {
                root: PathBuf::from("/proc"),
                mine: std::process::id(),
            },
            stale: std::env::var("AGENT_STALE_S")
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(300),
            tree: std::env::var("L7R_GUARD_TREE")
                .map_or_else(|_| PathBuf::from("/diagram"), PathBuf::from),
        },
    )
}

/// The gate, cohort and work-budget rolls whose working directory is the clone.
pub(crate) fn live_rolls(procs: &Procs, root: &Path) -> Vec<String> {
    let real = realpath(root);
    procs
        .pids()
        .into_iter()
        .filter_map(|p| {
            let cmd = procs.read(p, "cmdline").replace('\0', " ");
            let name = ROLLS.iter().find(|r| cmd.contains(**r))?;
            let dir = procs.link(p, "cwd")?;
            (realpath(&dir) == real)
                .then(|| format!("{p} {} rolling", name.rsplit('.').next().unwrap_or(name)))
        })
        .collect()
}

/// One line for every unfinished map-review agent of this session: `<id> <type> live|stalled <age>s`.
pub(crate) fn live_reviews(subagents: &Path, stale: u64) -> Vec<String> {
    let mut names: Vec<String> = std::fs::read_dir(subagents)
        .map(|d| {
            d.filter_map(Result::ok)
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        })
        .unwrap_or_default();
    names.sort();
    let now = SystemTime::now();
    names
        .iter()
        .filter_map(|name| {
            let id = name.strip_prefix("agent-")?.strip_suffix(".jsonl")?;
            let meta: Value = serde_json::from_str(
                &std::fs::read_to_string(subagents.join(format!("agent-{id}.meta.json"))).ok()?,
            )
            .ok()?;
            let kind = meta
                .get("agentType")
                .and_then(Value::as_str)
                .filter(|t| REVIEW_AGENTS.contains(t))?;
            if meta.get("finished") == Some(&Value::Bool(true))
                || subagents.join("../stall-ack").join(id).exists()
            {
                return None;
            }
            let path = subagents.join(name);
            let age = std::fs::metadata(&path)
                .ok()?
                .modified()
                .ok()
                .and_then(|at| now.duration_since(at).ok())
                .map_or(0, |d| d.as_secs());
            let last = last_record(&path).unwrap_or(Value::Null);
            let record = field(&last, "type");
            if record == "assistant"
                && last
                    .get("message")
                    .is_some_and(|m| field(m, "stop_reason") == "end_turn")
            {
                return None;
            }
            Some(format!(
                "{id} {kind} {} {age}s",
                if age >= stale && record == "user" {
                    "stalled"
                } else {
                    "live"
                }
            ))
        })
        .collect()
}

/// The refusal's words.
fn refusal(live: &[String], subagents: &str) -> String {
    let all = live.join("\n");
    let mut lines = vec![if all.contains("rolling") {
        "BLOCKED: an engine edit while a Rust gate, cohort or work-budget roll runs in this clone - the extension would be rebuilt under the rolls still to come.".to_owned()
    } else {
        "BLOCKED: an engine edit while a map review is still running - its verdict would come back NOT-REVIEWABLE.".to_owned()
    }];
    lines.extend(live.iter().map(|l| format!("  running: {l}")));
    lines.push("Draft the fix outside the clone (the scratchpad) and make it once every review and roll has returned.".to_owned());
    if all.contains("stalled") {
        lines.push(
            "A stalled review is still running until stopped: TaskStop it, then run exactly:"
                .to_owned(),
        );
        lines.extend(
            live.iter()
                .filter(|l| l.split(' ').nth(2) == Some("stalled"))
                .map(|l| {
                    format!(
                        "  scripts/hooks/agent-stall-hooks.sh ack {subagents} {}",
                        l.split(' ').next().unwrap_or("")
                    )
                }),
        );
    }
    lines.join("\n")
}

pub(crate) fn judge(event: &Event, session: &Session, c: &Ctx) -> Vec<Answer> {
    let tool = event.tool();
    let empty = json!({});
    let input = event.input.get("tool_input").unwrap_or(&empty);
    let path = Some(field(input, "file_path"))
        .filter(|p| !p.is_empty())
        .unwrap_or(field(input, "notebook_path"));
    if !path.starts_with('/') || event.input.get("transcript_path").is_none() {
        return Vec::new();
    }
    let existing = Path::new(path)
        .ancestors()
        .skip(1)
        .find(|d| d.is_dir())
        .unwrap_or(Path::new("/"));
    let Some(root) = owner(existing) else {
        return Vec::new();
    };
    let transcript = field(&event.input, "transcript_path");
    let subagents = format!(
        "{}/subagents",
        transcript.strip_suffix(".jsonl").unwrap_or(transcript)
    );
    let mut live = live_rolls(&c.procs, &root);
    if Path::new(transcript)
        .extension()
        .is_some_and(|x| x == "jsonl")
    {
        live.extend(live_reviews(Path::new(&subagents), c.stale));
    }
    if live.is_empty() {
        return Vec::new();
    }
    let question =
        json!({"root": root.to_string_lossy(), "path": path, "tool": tool, "tool_input": input})
            .to_string();
    let answerer = c.tree.join("scripts/gates/l7r-gate.sh");
    if !ask(
        Path::new("/"),
        "bash",
        &[&answerer.to_string_lossy(), "plan", "engine-edit"],
        &question,
    )
    .ok()
    {
        return Vec::new();
    }
    let detail: String = path.chars().take(200).collect();
    log::fire(
        "engine-freeze",
        "blocked",
        &detail,
        "review-running",
        &event.input,
        session,
    );
    vec![Answer::Refuse(refusal(&live, &subagents))]
}

#[cfg(test)]
mod tests;
