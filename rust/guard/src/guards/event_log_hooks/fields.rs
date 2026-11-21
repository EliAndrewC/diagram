//! A line's fields beyond its base: a tool call's own (moved here from `event_log_hooks.rs` by feature 451 T04, which would have passed
//! the 1,000-line file cap), and a background run's (451 T04, FR-002, plan D3, research R2) - `bg` on a backgrounded call's
//! `PostToolUse`, `inflight` on every `Stop` and `SubagentStop`, and what a completion notice gives its `BgEnd` line.

use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{Map, Value};

use super::{
    digest, first_group, heading_only, make_target, or_empty, re, text_of, truthy, EDIT_TOOLS,
    MANIFEST, TASK, UNIT,
};

pattern!(TOOL_USE, r"<tool-use-id>([^<]+)</tool-use-id>");
pattern!(TASK_ID, r"<task-id>([^<]+)</task-id>");
pattern!(STATUS, r"<status>([^<]+)</status>");
pattern!(SUMMARY, r"<summary>([^<]*)</summary>");
pattern!(EXIT_CODE, r"exit code (-?\d+)");

/// The fields a tool's own call adds to its line.
pub(super) fn tool_fields(
    out: &mut Map<String, Value>,
    tool: &str,
    ti: &Map<String, Value>,
    payload: &Value,
) {
    if tool == "Bash" {
        let command = text_of(ti.get("command"));
        // EVERY TARGET, where the call runs more than one (feature 451 T14): `make` is the first alone, so `make rust-test CRATE=x &&
        // make static` logged no `static` and `static_runs_hooks` would not have counted it; `makes` lists them all, first included
        let mut all: Vec<String> = Vec::new();
        for t in crate::shared::make::invoked(&command) {
            if !all.contains(&t) {
                all.push(t);
            }
        }
        let target = all.first().cloned().unwrap_or_default();
        if all.len() > 1 {
            out.insert("makes".into(), Value::from(all));
        }
        if !target.is_empty() {
            if ["tick", "task-start", "decide", "land"].contains(&target.as_str()) {
                if let Some(task) = first_group(&TASK, &command) {
                    out.insert("make".into(), Value::from(target.clone()));
                    out.insert("task".into(), Value::from(task));
                    return;
                }
            }
            out.insert("make".into(), Value::from(target));
        }
    } else if EDIT_TOOLS.contains(&tool) {
        let path = ti
            .get("file_path")
            .filter(|v| truthy(v))
            .or_else(|| ti.get("notebook_path").filter(|v| truthy(v)));
        out.insert("path".into(), or_empty(path));
        if tool == "Edit" {
            out.insert(
                "old".into(),
                Value::from(digest(&text_of(ti.get("old_string")))),
            );
            let new = text_of(ti.get("new_string"));
            out.insert("new".into(), Value::from(digest(&new)));
            if heading_only(&new) {
                out.insert("heading".into(), Value::Bool(true));
            }
        } else if tool == "Write" {
            out.insert(
                "new".into(),
                Value::from(digest(&text_of(ti.get("content")))),
            );
        }
    } else if tool == "Agent" {
        out.insert(
            "agent".into(),
            ti.get("subagent_type")
                .filter(|v| truthy(v))
                .cloned()
                .unwrap_or_else(|| Value::from("general-purpose")),
        );
        let prompt = text_of(ti.get("prompt"));
        if let Some(m) = first_group(&MANIFEST, &prompt) {
            out.insert("manifest".into(), Value::from(m));
        }
        if let Some(u) = first_group(&UNIT, &prompt) {
            out.insert(
                "unit".into(),
                Value::from(u.trim_end_matches([',', ';', '.'])),
            );
        }
        if prompt.contains("REVIEW_ROUNDS_OK=") {
            out.insert("waiver".into(), Value::from(1));
        }
        if let Some(aid) = payload
            .get("tool_response")
            .and_then(|r| r.get("agentId"))
            .filter(|v| truthy(v))
        {
            out.insert("aid".into(), aid.clone());
        }
    }
}

/// A background run's fields on its event's line (D3): a backgrounded call's `PostToolUse` carries `bg`, the `backgroundTaskId` its
/// `tool_response` names (the id the run's notice and a stop's `background_tasks` name it by); a `Stop` or `SubagentStop` carries
/// `inflight`, each run of its `background_tasks` as `{id, type}` and a shell's make target, so a wait after the stop is booked to the
/// runs it waited on (T09). An empty list is written - nothing in flight is a fact the reader books by - and a payload with no list
/// (a harness before the field) writes none.
pub(super) fn run_fields(out: &mut Map<String, Value>, ev: &str, payload: &Value) {
    if ev == "PostToolUse" {
        if let Some(bg) = payload
            .get("tool_response")
            .and_then(|r| r.get("backgroundTaskId"))
            .filter(|v| truthy(v))
        {
            out.insert("bg".into(), bg.clone());
        }
    } else if ev == "Stop" || ev == "SubagentStop" {
        if let Some(tasks) = payload.get("background_tasks").and_then(Value::as_array) {
            let runs = tasks
                .iter()
                .map(|r| {
                    let mut run = Map::new();
                    run.insert("id".into(), or_empty(r.get("id")));
                    run.insert("type".into(), or_empty(r.get("type")));
                    let target = make_target(&text_of(r.get("command")));
                    if !target.is_empty() {
                        run.insert("make".into(), Value::from(target));
                    }
                    Value::Object(run)
                })
                .collect();
            out.insert("inflight".into(), Value::Array(runs));
        }
    }
}

/// An agent's cost on its `SubagentStop` line (feature 451 T07, plan D6, research R2): `tok`, its transcript's `in`, `cached`, `created`
/// and `out` tokens, each model call once - one call's streamed reply is several `assistant` rows of one `message.id`, the last holding
/// the whole output, so the last row of an id stands for it (a sum over rows read the T202 builder's output 1,317,955 tokens against its
/// 481,878, 723 rows of 305 ids, measured 2026-11-20 (a Python scan of its 50 MB transcript)); `ctx`, its last call's context. Both are
/// read by `context_cap_hooks`' row reader, the whole file for `tok` (a stop is cumulative: a resumed agent's file holds every leg, and
/// the reader keeps the last line per `aid`). The transcript is the payload's `agent_transcript_path`, else the one beside the session's;
/// none readable, or no call in it, writes neither field: the hook never refuses.
pub(super) fn agent_cost(out: &mut Map<String, Value>, payload: &Value) {
    use crate::guards::context_cap_hooks::{call_of, context, own_transcript, Call};
    use std::io::BufRead as _;
    let own = text_of(payload.get("agent_transcript_path"));
    let path = if own.is_empty() {
        own_transcript(
            &text_of(payload.get("transcript_path")),
            &text_of(payload.get("agent_id")),
        )
    } else {
        Some(own.into())
    };
    let Some(file) = path.as_ref().and_then(|p| std::fs::File::open(p).ok()) else {
        return;
    };
    let mut calls: Vec<Call> = Vec::new();
    let mut at: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
    for row in std::io::BufReader::new(file)
        .split(b'\n')
        .map_while(Result::ok)
    {
        let Some(c) = call_of(&row) else { continue };
        // a row naming no id is a call of its own
        if let Some(&i) = at.get(&c.id).filter(|_| !c.id.is_empty()) {
            calls[i] = c;
        } else {
            at.insert(c.id.clone(), calls.len());
            calls.push(c);
        }
    }
    let n = |f: fn(&Call) -> u64| calls.iter().map(f).sum::<u64>();
    if n(|c| c.input + c.cached + c.created + c.out) == 0 {
        return;
    }
    out.insert(
        "tok".into(),
        serde_json::json!({"in": n(|c| c.input), "cached": n(|c| c.cached), "created": n(|c| c.created), "out": n(|c| c.out)}),
    );
    if let Some(ctx) = path.as_deref().and_then(context) {
        out.insert("ctx".into(), Value::from(ctx));
    }
}

/// What a completion notice gives its `BgEnd` line (D3): `id` (the launching call's `<tool-use-id>`), `bg` (its `<task-id>`),
/// `status` and `exit` - the LAST `exit code N` of its summary, the quoted description before it being free text; none where the run
/// was stopped or its session ended. None for a prompt that is no notice (one the GM typed, quoting one, is his), a notice naming no
/// launching call (a Monitor's event), and an AGENT's notice, whose `SubagentStop` is its end: an agent's notice names its launching
/// call's tool-use id too, 3,801 of the 3,986 agent notices beside all 1,992 shells' (measured 2026-11-20 (the `-diagram` and clone
/// transcripts' enqueued notices, tallied by summary and by a `<tool-use-id>` before any `<result>`)), so the id does not tell them apart -
/// the summary's `Agent "` does, and the writer also drops a notice whose launch line is an Agent call. Every other notice with an id
/// ends a background run the session can wait on and writes its end: a shell's, a workflow's (46 in the same count), a Monitor's stream
/// ended or stopped (128). Only the tags before a `<result>` are read: an agent's result is free text and can quote another notice.
pub(super) fn notice_end(prompt: &str) -> Option<Map<String, Value>> {
    let body = prompt.trim_start().strip_prefix("<task-notification>")?;
    let head = body.split("<result>").next().unwrap_or(body);
    let head = head.split("</task-notification>").next().unwrap_or(head);
    let id = first_group(&TOOL_USE, head)?;
    let summary = first_group(&SUMMARY, head).unwrap_or_default();
    if summary.starts_with("Agent \"") {
        return None;
    }
    let mut out = Map::new();
    out.insert("id".into(), Value::from(id));
    for (key, p) in [("bg", &TASK_ID), ("status", &STATUS)] {
        if let Some(v) = first_group(p, head) {
            out.insert(key.into(), Value::from(v));
        }
    }
    let code = EXIT_CODE
        .captures_iter(&summary)
        .map_while(Result::ok)
        .last()
        .and_then(|c| c.get(1).and_then(|m| m.as_str().parse::<i64>().ok()));
    if let Some(code) = code {
        out.insert("exit".into(), Value::from(code));
    }
    Some(out)
}
