//! THE CHECK'S OWN TASK (feature 449 T258). WHY: decide-first asked `l7r-gate plan decided <root>`, whose answer is the clone's one
//! `active-task` mark's task - whichever task started last - or, the mark naming none open, the feature's first open task; with three
//! builders in one clone every record check was judged on another builder's section (449 T248's, T250's for each of T197 G1's checks), and
//! 113 dispatches carried `DECIDE_OK` on 2026-11-22 while 32 were refused (measured 2026-11-22, `make guard-log GUARD=check-bundle
//! SINCE=2026-11-22`). A check is judged on the task it serves, first that says:
//! - its OWN WORDS: the first task id of the Agent call's `description`, else of its prompt's first line - the feature the number before
//!   it (`449 T265's claims re-check`), else the feature whose task start names it, else `.specify/feature.json`'s;
//! - its BUILDER: the agent that dispatched it, read from its meta file as the Stop hook reads a builder
//!   (`set_down_hooks::builder_brief`, a bundle's builder every member);
//! - its PAGE SESSION's brief (`L7R_PAGE_SESSION`, the `make page-session` runner's id, looked up in the clone's
//!   `page-sessions/index.txt`): the feature its `specs/<feature>/` path names, the task its first line names (`# Brief - feature 449
//!   task T197, ...`), else its file name's (`t197-g2-checks.md`).
//!
//! NONE OF THEM: the check serves no task anything names, and passes, recorded (`decide-no-task`) - a CONVENTION, the plain reading of
//! T258's line ("a record check that names a task, or none, should be judged on its own task's verdict, not the mark's"): the mark is
//! exactly the guess this replaces, and a guess that refuses is what sent 113 dispatches to the escape.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::guards::event_log_hooks::{started, starts};
use crate::guards::set_down_hooks::{builder_brief, page_session_brief};
use crate::shared::state::field;

/// The task a check serves: its feature (a number or a `specs/` directory name, as `plan decided` resolves either) and its tasks (a
/// bundle's builder names each member; they share one section).
#[derive(Debug, PartialEq, Eq)]
pub(super) struct Own {
    pub feature: String,
    pub tasks: Vec<String>,
}

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

/// A task id, and the feature number before it where one stands there.
static NAMED: LazyLock<Regex> = LazyLock::new(|| re(r"(?:\b(\d{3})\s+)?\b(T\d+[a-z]?)\b"));

/// The task the dispatch in `input` serves, in the clone at `root`; None where nothing names one.
pub(super) fn own_task(input: &Value, root: &Path) -> Option<Own> {
    let ti = input.get("tool_input").unwrap_or(&Value::Null);
    let head = field(ti, "prompt").lines().next().unwrap_or_default();
    [field(ti, "description"), head]
        .iter()
        .find_map(|text| named(text, root))
        .or_else(|| builder(input))
        .or_else(|| page_session(root))
}

/// The first task `text` names, its feature the number before it or the one that started it.
fn named(text: &str, root: &Path) -> Option<Own> {
    let c = NAMED.captures(text).ok().flatten()?;
    let task = c[2].to_owned();
    let feature = c
        .get(1)
        .map(|n| n.as_str().to_owned())
        .or_else(|| started(&starts(root), &task, None).or_else(|| feature_json(root)))?;
    Some(Own {
        feature,
        tasks: vec![task],
    })
}

/// `.specify/feature.json`'s feature directory's name.
fn feature_json(root: &Path) -> Option<String> {
    let text = std::fs::read_to_string(root.join(".specify/feature.json")).ok()?;
    let parsed: Value = serde_json::from_str(&text).ok()?;
    let dir = parsed["feature_directory"].as_str()?.trim_end_matches('/');
    let name = dir.rsplit('/').next().unwrap_or_default();
    (!name.is_empty()).then(|| name.to_owned())
}

/// The dispatching builder's (feature, tasks): the payload's `agent_id`, read in the session's `subagents` directory.
fn builder(input: &Value) -> Option<Own> {
    let aid = field(input, "agent_id");
    let transcript = field(input, "transcript_path");
    if aid.is_empty() || transcript.is_empty() {
        return None;
    }
    let dir =
        PathBuf::from(transcript.strip_suffix(".jsonl").unwrap_or(transcript)).join("subagents");
    let (feature, tasks) = builder_brief(&dir, aid)?;
    Some(Own { feature, tasks })
}

/// The page session's brief's (feature, task), where the hook runs in one (`set_down_hooks::page_session_brief`, the one reader).
fn page_session(root: &Path) -> Option<Own> {
    let sid = crate::shared::env::var("L7R_PAGE_SESSION");
    if sid.is_empty() {
        return None;
    }
    let (feature, task) = page_session_brief(root, &sid)?;
    Some(Own {
        feature,
        tasks: vec![task],
    })
}

#[cfg(test)]
mod tests;
