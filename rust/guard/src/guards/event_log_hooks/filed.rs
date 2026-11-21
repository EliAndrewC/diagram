//! WHERE A LINE IS FILED (feature 451 T26): the feature of the task the line carries, never the clone's `.specify/feature.json` alone.
//! WHY: `make task-start` rewrites feature.json to the feature whose task started last, so with two features worked in one clone (449
//! and 451 on 2026-11-20) every line landed in that one feature's log - a 451 builder's `T26` was booked in 449's log as 449's T26, 45
//! lines of it and 5 of 451's T03 (observed 2026-11-20, method: the 449 log's lines whose `task` is no 449 task, matched to the clone's
//! `task-starts.jsonl`), and `make where-time` read both features wrong.
//!
//! THE CHAIN (first that says wins, each read cheap - no `tasks.md` is read on a hook):
//! - the FEATURE: a make command's `F=` (read outside its heredocs, 451 T53) where the command carries its own `T=` or no brief names a
//!   feature; else the dispatch's brief - the Agent call's own `description`, or a subagent's meta file's, or for a first start, whose meta
//!   file is not written yet, its dispatch's (`dispatches.rs`, 451 T53) - the feature it names ([`brief_feature`]); else the feature whose
//!   task-start names the line's task, a start older than [`STALE_START_S`] naming none (451 T53); else the
//!   FALLBACK, `feature_of` (the session's environment, then feature.json), and the line is marked `"fallback": true` unless the session's environment declared that feature;
//! - the TASK: a `tick`, `task-start`, `decide` or `land` command's `T=` (`line`); else the `T<n>` the brief names; else, for an Agent call, its prompt's first line's (451 T07); else the task-start
//!   in force for the line's feature (D2's last entry, now of the line's own feature, not of feature.json's).
//!
//! A fallback line's task is a guess when two features are worked at once (the coordinator's own calls), so it says so: a reader of the
//! task field (T07, T08, T14) can keep that time apart rather than book it to the task feature.json happened to name. The session's
//! environment (`L7R_FEATURE_DIRECTORY`, `SPECIFY_FEATURE` in the hook's own process) is the fallback's, not first: the hook's
//! environment is the whole Claude Code session's, shared by the main session and every builder it dispatches, so it cannot tell two
//! builders apart; a line's own word can.

use std::cell::OnceCell;
use std::collections::HashMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::{
    common_git_dir, dispatches, feature_of, first_group, log_path_in, make_target, re, text_of,
    TASK_NAMED,
};
use crate::shared::shape::strip_heredocs;

/// How old a task start may be and still name a brief's bare task's feature (451 T53). WHY: `T47 plan review`, from a 451 T47 builder
/// in a clone that never started 451's T47, was filed by 385's T47 start of 2026-10-18 - 23 lines, three spec-fidelity rounds, in
/// 385's log on 2026-11-21 (observed 2026-11-21, method: `make events-refile DRY=1`'s lines left, joined to their meta files). GUESS knob:
/// 72 h. Of 571 task-only briefs in the clone's logs, the start their log's feature made of that task was p50 0.3 h, p90 1.8 h old,
/// 14 past 24 h, the longest of them 34.1 h (444's T16), and then 313, 618 and 799 h (7 agents), measured 2026-11-21 (each such
/// subagent's first line against the clone's `task-starts.jsonl`); the bound keeps the 34 h one and drops the three weeks-old ones.
pub(super) const STALE_START_S: f64 = 72.0 * 3600.0;

pattern!(FEATURE_ARG, r#"(?:^|\s)F=["']?([A-Za-z0-9][\w.-]*)"#);
// a brief's feature: the number before its task (`451 T26: ...`, `spec-fidelity on 451 T03's section`) ...
pattern!(FEATURE_BEFORE_TASK, r"\b(\d+)\s+T\d+[a-z]?\b");
// ... else a number standing alone - never one inside a hyphenated word (`FR-008`, `qingshigao-122`, `375-a1`)
pattern!(BARE_NUMBER, r"(?<![\w-])(\d+)(?![\w-])");

/// The feature a dispatch's brief names (451 T26): the number before a task id, naming one feature directory; else a number standing
/// alone that names one feature directory this clone has started a task of. WHY the second is held to started features: a brief's
/// numbers are mostly counts and source ids - "Triage T09's 108 moved claims", "source-reader Qingshigao 122", "impl-drift on 154 owed
/// claims" - and every one of those named an old feature's directory (observed 2026-11-20, method: the numbers of every subagent
/// meta file's `description` under `~/.claude/projects` matched to `specs/<n>-*`; `make events-refile DRY=1` moved 545 lines to 008
/// on "FR-008" before this rule).
pub fn brief_feature(
    brief: &str,
    named: &dyn Fn(&str) -> Option<String>,
    worked: &dyn Fn(&str) -> bool,
) -> Option<String> {
    let numbers = |p: &Regex| -> Vec<String> {
        p.captures_iter(brief)
            .map_while(Result::ok)
            .filter_map(|c| c.get(1).map(|m| m.as_str().to_owned()))
            .collect()
    };
    numbers(&FEATURE_BEFORE_TASK)
        .iter()
        .find_map(|n| named(n))
        .or_else(|| {
            numbers(&BARE_NUMBER)
                .iter()
                .find_map(|n| named(n).filter(|f| worked(f)))
        })
}

/// Where a line goes: its feature (the log), its task, and whether the feature was only the fallback's.
pub(super) struct Filed {
    pub feature: String,
    pub task: Option<String>,
    pub fallback: bool,
}

/// The `specs/` directory names, read at most once a line, and only when a word asks.
struct Specs<'a> {
    root: &'a Path,
    names: OnceCell<Vec<String>>,
}

impl Specs<'_> {
    /// The one feature directory `word` names: `specs/<word>` itself, else the single `specs/<word>-*`; None for none or several.
    fn named(&self, word: &str) -> Option<String> {
        let specs = self.root.join("specs");
        if specs.join(word).is_dir() {
            return Some(word.to_owned());
        }
        let names = self.names.get_or_init(|| {
            std::fs::read_dir(&specs)
                .into_iter()
                .flatten()
                .filter_map(Result::ok)
                .filter(|e| e.path().is_dir())
                .map(|e| e.file_name().to_string_lossy().into_owned())
                .collect()
        });
        let prefix = format!("{word}-");
        let mut hits = names.iter().filter(|n| n.starts_with(&prefix));
        match (hits.next(), hits.next()) {
            (Some(one), None) => Some(one.clone()),
            _ => None,
        }
    }
}

/// The dispatch's briefs: an Agent call's own `description`; else, for a subagent's line, its meta file's `description`
/// (`<transcript_path without .jsonl>/subagents/agent-<agent_id>.meta.json`, research R2; one read a line); else, for a first start,
/// whose meta file is not written yet, the dispatches it may have come from (`dispatches.rs`, 451 T53). None where nothing is readable;
/// several only for a start, which the caller takes where they agree.
fn briefs(payload: &Value, events: &Path, now: &str) -> Vec<String> {
    if text_of(payload.get("tool_name")) == "Agent" {
        let own = text_of(payload.get("tool_input").and_then(|t| t.get("description")));
        if !own.is_empty() {
            return vec![own];
        }
    }
    let aid = text_of(payload.get("agent_id"));
    let transcript = text_of(payload.get("transcript_path"));
    if aid.is_empty() || transcript.is_empty() {
        return Vec::new();
    }
    let session = transcript.strip_suffix(".jsonl").unwrap_or(&transcript);
    if let Some(own) =
        std::fs::read_to_string(Path::new(session).join(format!("subagents/agent-{aid}.meta.json")))
            .ok()
            .and_then(|t| serde_json::from_str::<Value>(&t).ok())
            .map(|m| text_of(m.get("description")))
    {
        return vec![own];
    }
    if text_of(payload.get("hook_event_name")) == "SubagentStart" {
        return dispatches::briefs_at_start(events, payload, now);
    }
    Vec::new()
}

/// The one value every brief gives, None for none or a disagreement.
fn agreed(each: impl Iterator<Item = Option<String>>) -> Option<String> {
    let mut each = each.peekable();
    let first = each.peek()?.clone();
    each.all(|v| v == first).then_some(first).flatten()
}

/// An Agent call's prompt's first line, "" for any other call (a later line quotes other tasks).
fn prompt_head(payload: &Value) -> &str {
    if payload.get("tool_name").and_then(Value::as_str) != Some("Agent") {
        return "";
    }
    payload
        .get("tool_input")
        .and_then(|t| t.get("prompt"))
        .and_then(Value::as_str)
        .and_then(|p| p.lines().next())
        .unwrap_or_default()
}

/// One task start: its feature, its task, its epoch seconds where its `utc` parses.
type Start = (String, String, Option<f64>);

/// The clone's task starts in file order; a line that does not parse is skipped, a missing file is none.
fn starts(root: &Path) -> Vec<Start> {
    std::fs::read_to_string(common_git_dir(root).join("task-starts.jsonl"))
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
        .map(|e| {
            let at = crate::shared::iso::parse(&text_of(e.get("utc")));
            (text_of(e.get("feature")), text_of(e.get("task")), at)
        })
        .filter(|(f, t, _)| !f.is_empty() && !t.is_empty())
        .collect()
}

/// The task in force for `feature`: its last start.
fn in_force(starts: &[Start], feature: &str) -> Option<String> {
    starts
        .iter()
        .rev()
        .find(|(f, _, _)| f == feature)
        .map(|(_, t, _)| t.clone())
}

/// The feature a task belongs to by the starts: the latest feature whose task in force it is, else the latest that started it at all -
/// a start more than [`STALE_START_S`] before `now` counting for neither (a start or a `now` with no time is never stale).
fn started(starts: &[Start], task: &str, now: Option<f64>) -> Option<String> {
    let mut last: HashMap<&str, &str> = HashMap::new();
    for (f, t, _) in starts {
        last.insert(f, t);
    }
    let fresh = |at: &Option<f64>| match (at, now) {
        (Some(at), Some(now)) => now - at <= STALE_START_S,
        _ => true,
    };
    starts
        .iter()
        .rev()
        .find(|(f, t, at)| t == task && fresh(at) && last.get(f.as_str()) == Some(&task))
        .or_else(|| {
            starts
                .iter()
                .rev()
                .find(|(_, t, at)| t == task && fresh(at))
        })
        .map(|(f, _, _)| f.clone())
}

/// Does the hook's environment name the session's feature (`feature_of`'s first two sources)?
fn declared(root: &Path, env: &dyn Fn(&str) -> Option<String>) -> bool {
    let own = env("L7R_FEATURE_DIRECTORY").unwrap_or_default();
    let named = env("SPECIFY_FEATURE").unwrap_or_default();
    let named = named.trim().trim_matches('/');
    !own.trim().trim_end_matches('/').is_empty()
        || (!named.is_empty() && root.join("specs").join(named).is_dir())
}

/// Where the payload's line is filed at `now` (the line's `t`); `carried` is the task its own command names (`T=`), `named` the feature
/// a gate tool names for its own line (451 T06: a landing's `F=`), read first, as a make command's `F=` is.
pub(super) fn filed(
    payload: &Value,
    carried: Option<&str>,
    named: Option<&str>,
    root: &Path,
    now: &str,
    env: &dyn Fn(&str) -> Option<String>,
) -> Filed {
    let specs = Specs {
        root,
        names: OnceCell::new(),
    };
    // a heredoc's body is text written to a file, never the command's own words: `F=` quoted in a test file filed a 451 builder's
    // `make rust-test` in 385's and 449's logs (451 T53; observed 2026-11-21, method: the dry run's moved lines' commands read from the
    // subagents' transcripts)
    let command = if text_of(payload.get("tool_name")) == "Bash" {
        strip_heredocs(&text_of(
            payload.get("tool_input").and_then(|t| t.get("command")),
        ))
    } else {
        String::new()
    };
    // a blank word names no feature (`specs/` itself is a directory)
    let said = named
        .filter(|w| !w.trim().is_empty())
        .and_then(|w| specs.named(w))
        .or_else(|| {
            if make_target(&command).is_empty() {
                None
            } else {
                first_group(&FEATURE_ARG, &command).and_then(|w| specs.named(&w))
            }
        });
    let events = log_path_in(root, "", env);
    let briefs = briefs(payload, events.parent().unwrap_or(root), now);
    let starts = starts(root);
    let briefed = agreed(briefs.iter().map(|b| {
        brief_feature(b, &|n| specs.named(n), &|f| {
            starts.iter().any(|(s, _, _)| s == f)
        })
    }));
    // an Agent call whose description names no task: its prompt's first line's (451 T07, plan D6) - the task only, the feature
    // still the description's, since a prompt's line is free text a bare number in it could misfile
    let task = carried
        .map(str::to_owned)
        .or_else(|| agreed(briefs.iter().map(|b| first_group(&TASK_NAMED, b))))
        .or_else(|| first_group(&TASK_NAMED, prompt_head(payload)));
    // a builder's `make task-add F=449` is the builder's own time: its `F=` names where the call writes, not whose task it serves, and
    // filed by it the line took 449 from the `F=` and T36 from 451's brief (451 T53). The brief wins unless the command carries its own
    // `T=` - the re-file's rule (`make events-refile`, BY BRIEF), so the writer and the re-file agree
    let feature = if carried.is_some() {
        said.or(briefed)
    } else {
        briefed.or(said)
    }
    .or_else(|| {
        task.as_deref()
            .and_then(|t| started(&starts, t, crate::shared::iso::parse(now)))
    });
    let (feature, fallback) = match feature {
        Some(f) => (f, false),
        // a session that declares its feature (a page session's `L7R_FEATURE_DIRECTORY`, a `SPECIFY_FEATURE` naming a feature) is
        // that feature's whole: not marked, the mark is for feature.json's guess
        None => (feature_of(root, env), !declared(root, env)),
    };
    let task = task.or_else(|| {
        if feature.is_empty() {
            None
        } else {
            in_force(&starts, &feature)
        }
    });
    Filed {
        feature,
        task,
        fallback,
    }
}
