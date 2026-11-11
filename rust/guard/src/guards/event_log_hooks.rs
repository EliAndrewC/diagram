//! `event-log-hooks` (feature 375 FR-008; ported from `scripts/hooks/event-log-hooks.sh` and the hook half of
//! `scripts/measure/event_log.py`, feature 449 T012): ONE LINE A HOOK EVENT into the feature's event log, so where a feature's time
//! went is counted, not remembered (`make feature-report` reads it). It never refuses and never prints. The line's fields, their
//! order and their reasons are `event_log.py`'s docstring, kept until phase 3 ports its other half.
//!
//! Plan T012's decisions: (a) the line, the log's path and the append are in-process; (b) the reversal test runs here, and the
//! trigger it owes is recorded by `hm_arbiter.py`, asked by path; (c) the event is the payload's; (d) the digests are SHA-1's.

use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::checks;
use crate::shared::log::civil;
use crate::shared::session::Session;
use crate::shared::sha1;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "event-log-hooks",
    events: &[
        "PreToolUse",
        "PostToolUse",
        "SubagentStart",
        "SubagentStop",
        "UserPromptSubmit",
        "Stop",
        "PostToolUseFailure",
        "",
    ],
    matcher: "*",
    decide,
};

const RECORD_CHECKS: [&str; 11] = [
    "quote-check",
    "record-format",
    "source-applicability",
    "source-reader",
    "entry-drift",
    "record-style",
    "translation-check",
    "intro-check",
    "modal-form",
    "modal-research",
    "modal-depiction",
];
const REVIEW_CHECKS: [&str; 5] = [
    "glyph-check",
    "settlement-review",
    "fix-check",
    "building-review",
    "size-audit",
];
const EDIT_TOOLS: [&str; 4] = ["Edit", "Write", "NotebookEdit", "MultiEdit"];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

macro_rules! pattern {
    ($name:ident, $p:expr) => {
        static $name: LazyLock<Regex> = LazyLock::new(|| re($p));
    };
}

pattern!(
    MAKE,
    r"(?m)(?:^|[;&|(]\s*|\b(?:then|do|else|time)\s+)(?:[A-Z_][A-Z0-9_]*=\S*\s+)*make\s+(?:-[CfIjo]\s+\S+\s+|-{1,2}[\w-]+(?:=\S+)?\s+|[A-Z_]+=\S*\s+)*([a-z][\w-]*)"
);
pattern!(MANIFEST, r#"(/[^\s`"'<>)]*MANIFEST\.md)"#);
pattern!(
    FINDING_COUNT,
    r"\b[1-9]\d*\s+(?:findings?|unfootnoted|EDITs?|DOES-NOT-SUPPORT|DRIFTED|MISLABELED|FIX|VOCABULARY|SESSION NOTE|HISTORY)\b"
);
pattern!(CLEAN_SAID, r"(?i)\b(?:nothing to act on|no findings)\b");
pattern!(
    UNIT_SUMMARY,
    r"(?m)^[a-z-]+: \S+ - [A-Z]+ \d+ findings?;.*$"
);
pattern!(
    EMPTY_SAID,
    r"(?i)\blists no (?:changed pages|claims|units)\b|\bbundle (?:was|is) (?:built )?empty\b"
);
pattern!(
    VERDICT,
    r"\b(NOT-REVIEWABLE|NOT FAITHFUL|CHANGES REQUIRED|BLOCKED|FAITHFUL|CLEAR|NEEDS-WORK|PASS|FAIL)\b"
);
pattern!(
    RECORDED,
    r"(?mi)\brecorded (PASS|NEEDS-WORK|NOT-REVIEWABLE) for\b|^\s*VERDICT:\s*(pass|needs-work|not-reviewable)\b"
);
pattern!(NUMBER, r"\b\d+\b");
pattern!(TASK, r"\bT=(T\d+[a-z]?)\b");
pattern!(UNIT, r"\bUNIT:\s*(\S+)");
pattern!(GITDIR, r"gitdir:\s*(.+)");

fn found(p: &Regex, text: &str) -> bool {
    p.is_match(text).unwrap_or(false)
}

fn first_group(p: &Regex, text: &str) -> Option<String> {
    p.captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
}

/// The first `n` characters of `text` (Python's `text[:n]`).
fn head(text: &str, n: usize) -> &str {
    text.char_indices().nth(n).map_or(text, |(i, _)| &text[..i])
}

fn numbers(text: &str) -> Vec<String> {
    NUMBER
        .find_iter(text)
        .filter_map(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// The verdict a returned agent's reply leads with, or `clean`/`findings` from its counts, or "" (`verdict_of`).
#[must_use]
pub fn verdict_of(text: &str) -> String {
    if let Ok(Some(c)) = RECORDED.captures(text) {
        return c
            .get(1)
            .or_else(|| c.get(2))
            .map_or(String::new(), |m| m.as_str().to_uppercase());
    }
    let lead = head(text, 600);
    if let Some(v) = first_group(&VERDICT, lead) {
        return v;
    }
    let first = text
        .trim()
        .lines()
        .find(|l| !l.trim().is_empty())
        .unwrap_or("");
    if found(&FINDING_COUNT, first) {
        return "findings".to_owned();
    }
    if found(&CLEAN_SAID, lead) {
        return "clean".to_owned();
    }
    let nums = numbers(first);
    if !nums.is_empty() {
        return if nums.iter().all(|n| n == "0") {
            "clean"
        } else {
            "findings"
        }
        .to_owned();
    }
    let units: Vec<String> = UNIT_SUMMARY
        .find_iter(text)
        .filter_map(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect();
    if !units.is_empty() {
        let any = units.iter().any(|u| {
            u.split_once(" - ")
                .is_some_and(|(_, rest)| numbers(rest).iter().any(|n| n != "0"))
        });
        return if any { "findings" } else { "clean" }.to_owned();
    }
    if found(&EMPTY_SAID, lead) {
        return "empty bundle".to_owned();
    }
    String::new()
}

/// The first make target a Bash command runs, or "" (`make_target`).
#[must_use]
pub fn make_target(command: &str) -> String {
    let text = command
        .split_once("<<")
        .map_or(command, |(before, _)| before);
    first_group(&MAKE, text).unwrap_or_default()
}

/// What kind of subagent this is (`agent_category`).
#[must_use]
pub fn agent_category(agent_type: &str, prompt: &str) -> &'static str {
    if agent_type == "impl-drift" || prompt.contains("claims-triage") {
        "claims check"
    } else if RECORD_CHECKS.contains(&agent_type) || prompt.contains("modal-triage") {
        "record check"
    } else if REVIEW_CHECKS.contains(&agent_type) {
        "review check"
    } else if agent_type == "spec-fidelity" || agent_type == "spec-fidelity-verify" {
        "spec review"
    } else if agent_type == "round-arbiter" {
        "round arbiter"
    } else {
        "other subagent"
    }
}

fn text_of(v: Option<&Value>) -> String {
    match v {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Null | Value::Bool(false)) | None => String::new(),
        Some(other) if truthy(other) => other.to_string(),
        _ => String::new(),
    }
}

/// Python's truthiness of a JSON value.
fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

/// The value, or "" where it is not truthy (`payload.get(k) or ""`).
fn or_empty(v: Option<&Value>) -> Value {
    v.filter(|x| truthy(x))
        .cloned()
        .unwrap_or_else(|| Value::String(String::new()))
}

/// The category of one tool call (`category`).
#[must_use]
pub fn category(tool: &str, ti: &Map<String, Value>) -> &'static str {
    if EDIT_TOOLS.contains(&tool) {
        return "edit";
    }
    match tool {
        "Bash" => match make_target(&text_of(ti.get("command"))).as_str() {
            "quick" => "quick test",
            "test-file" => "test file",
            "done" => "gate",
            "tick" | "claim" | "plan-verdict" => "spec-kit step",
            _ => "other tool",
        },
        "Agent" => agent_category(
            &text_of(ti.get("subagent_type")),
            &text_of(ti.get("prompt")),
        ),
        "Skill" if text_of(ti.get("skill")).starts_with("speckit-") => "spec-kit step",
        _ => "other tool",
    }
}

fn digest(text: &str) -> String {
    sha1::hex(text.as_bytes())[..12].to_owned()
}

/// One Markdown heading line and nothing else (`heading_only`).
fn heading_only(text: &str) -> bool {
    let lines: Vec<&str> = text.lines().filter(|l| !l.trim().is_empty()).collect();
    lines.len() == 1 && lines[0].trim_start().starts_with('#')
}

/// Whether a user message is a prompt the GM typed (`_typed_prompt`).
fn typed_prompt(content: &Value) -> bool {
    let text = match content {
        Value::Array(blocks) => {
            let texts: Vec<String> = blocks
                .iter()
                .filter(|b| b.get("type") == Some(&Value::from("text")))
                .map(|b| text_of(b.get("text")))
                .collect();
            if texts.is_empty()
                || blocks
                    .iter()
                    .any(|b| b.get("type") == Some(&Value::from("tool_result")))
            {
                return false;
            }
            texts.join("\n")
        }
        Value::String(s) => s.clone(),
        other => other.to_string(),
    };
    let text = text.trim_start();
    !text.is_empty()
        && ![
            "<task-notification>",
            "<system-reminder>",
            "<local-command",
            "Caveat:",
        ]
        .iter()
        .any(|p| text.starts_with(p))
}

/// Now as the log writes it: UTC to the millisecond, `Z`.
#[must_use]
pub fn now_stamp(at: SystemTime) -> String {
    let d = at.duration_since(UNIX_EPOCH).unwrap_or_default();
    let (y, mo, day, h, mi, s) = civil(d.as_secs());
    format!(
        "{y:04}-{mo:02}-{day:02}T{h:02}:{mi:02}:{s:02}.{:03}Z",
        d.subsec_millis()
    )
}

/// The log line for one hook payload (`line`).
#[must_use]
pub fn line(payload: &Value, t: &str) -> Map<String, Value> {
    let ev = text_of(payload.get("hook_event_name"));
    let mut out = Map::new();
    out.insert("t".into(), Value::from(t));
    out.insert("sid".into(), or_empty(payload.get("session_id")));
    out.insert("ev".into(), Value::from(ev.clone()));
    let tool = payload.get("tool_name").filter(|v| truthy(v));
    if let Some(tool) = tool {
        let empty = Map::new();
        let ti = payload
            .get("tool_input")
            .and_then(Value::as_object)
            .unwrap_or(&empty);
        let name = text_of(Some(tool));
        out.insert("tool".into(), tool.clone());
        out.insert("id".into(), or_empty(payload.get("tool_use_id")));
        out.insert("cat".into(), Value::from(category(&name, ti)));
        if let Some(by) = payload.get("agent_id").filter(|v| truthy(v)) {
            out.insert("by".into(), by.clone());
        }
        tool_fields(&mut out, &name, ti, payload);
        if payload.get("duration_ms").is_some_and(Value::is_number) {
            out.insert("ms".into(), payload["duration_ms"].clone());
        }
    } else if ev == "UserPromptSubmit" && payload.get("prompt").is_some() {
        out.insert("gm".into(), Value::Bool(typed_prompt(&payload["prompt"])));
    } else if ev == "SubagentStart" || ev == "SubagentStop" {
        let agent = or_empty(payload.get("agent_type"));
        out.insert("agent".into(), agent.clone());
        out.insert("aid".into(), or_empty(payload.get("agent_id")));
        out.insert(
            "cat".into(),
            Value::from(agent_category(&text_of(Some(&agent)), "")),
        );
        let verdict = verdict_of(&text_of(payload.get("last_assistant_message")));
        if !verdict.is_empty() {
            out.insert("verdict".into(), Value::from(verdict));
        }
    }
    out
}

/// The fields a tool's own call adds to its line.
fn tool_fields(out: &mut Map<String, Value>, tool: &str, ti: &Map<String, Value>, payload: &Value) {
    if tool == "Bash" {
        let command = text_of(ti.get("command"));
        let target = make_target(&command);
        if !target.is_empty() {
            if ["tick", "task-start", "decide"].contains(&target.as_str()) {
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

/// The working tree holding `cwd`, walked up to its `.git` (`clone_root`).
fn clone_root(cwd: &Path) -> Option<PathBuf> {
    let p = std::fs::canonicalize(cwd).unwrap_or_else(|_| cwd.to_path_buf());
    p.ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
}

/// The git dir a worktree shares with its clone (`common_git_dir`).
fn common_git_dir(root: &Path) -> PathBuf {
    let g = root.join(".git");
    let Some(dir) = std::fs::read_to_string(&g)
        .ok()
        .and_then(|t| first_group(&GITDIR, t.trim()))
    else {
        return g;
    };
    let dir =
        std::fs::canonicalize(root.join(dir.trim())).unwrap_or_else(|_| root.join(dir.trim()));
    match std::fs::read_to_string(dir.join("commondir")) {
        Ok(c) => std::fs::canonicalize(dir.join(c.trim())).unwrap_or_else(|_| dir.join(c.trim())),
        Err(_) => dir,
    }
}

/// The active feature's directory name, or "" (`feature_of`).
fn feature_of(root: &Path, env: &dyn Fn(&str) -> Option<String>) -> String {
    let own = env("L7R_FEATURE_DIRECTORY").unwrap_or_default();
    let own = own.trim().trim_end_matches('/');
    if let Some(name) = Path::new(own).file_name().filter(|_| !own.is_empty()) {
        return name.to_string_lossy().into_owned();
    }
    let named = env("SPECIFY_FEATURE").unwrap_or_default();
    let named = named.trim().trim_matches('/');
    if !named.is_empty() && root.join("specs").join(named).is_dir() {
        return named.to_owned();
    }
    std::fs::read_to_string(root.join(".specify/feature.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .map(|d| text_of(d.get("feature_directory")))
        .and_then(|d| {
            Path::new(&d)
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
        })
        .unwrap_or_default()
}

/// Whether an Edit of `path` puts back text an earlier Edit of that file replaced (`hm_arbiter.reversal`).
fn reversal(log: &Path, path: &Value, old: &Value, new: &Value) -> bool {
    let text = std::fs::read_to_string(log).unwrap_or_default();
    let replaced: Vec<Value> = text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
        .filter(|e| {
            e.get("ev") == Some(&Value::from("PreToolUse"))
                && e.get("tool") == Some(&Value::from("Edit"))
                && e.get("path") == Some(path)
        })
        .map(|e| e.get("old").cloned().unwrap_or(Value::Null))
        .collect();
    truthy(new) && replaced.contains(new) && new != old
}

/// A feature's event log (`event_log.log_path`): under `L7R_EVENTS_DIR`, else the clone's common git dir; `_unassigned` for no feature.
#[must_use]
pub fn log_path(root: &Path, feature: &str) -> PathBuf {
    log_path_in(root, feature, &|k| std::env::var(k).ok())
}

fn log_path_in(root: &Path, feature: &str, env: &dyn Fn(&str) -> Option<String>) -> PathBuf {
    let base = env("L7R_EVENTS_DIR")
        .filter(|d| !d.is_empty())
        .map_or_else(|| common_git_dir(root).join("l7r-events"), PathBuf::from);
    base.join(format!(
        "{}.jsonl",
        if feature.is_empty() {
            "_unassigned"
        } else {
            feature
        }
    ))
}

/// Append the payload's line to its feature's log; None outside any clone (`append`).
pub(crate) fn append(
    payload: &Value,
    t: &str,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
) -> Option<PathBuf> {
    let cwd = payload
        .get("cwd")
        .and_then(Value::as_str)
        .filter(|c| !c.is_empty())
        .map_or_else(|| here.to_path_buf(), PathBuf::from);
    let root = clone_root(&cwd)?;
    let path = log_path_in(&root, &feature_of(&root, env), env);
    let base = path.parent().map_or_else(PathBuf::new, Path::to_path_buf);
    std::fs::create_dir_all(&base).ok()?;
    let row = line(payload, t);
    let edit = row.get("ev") == Some(&Value::from("PreToolUse"))
        && row.get("tool") == Some(&Value::from("Edit"));
    let null = Value::Null;
    let field = |k: &str| row.get(k).unwrap_or(&null);
    if edit
        && path.is_file()
        && row.get("heading").is_none()
        && reversal(&path, field("path"), field("old"), field("new"))
    {
        let p = text_of(Some(field("path")));
        let _ = checks::arbiter::trip(
            &root,
            &format!("reversal:{p}"),
            "reversal",
            &p,
            &format!("an Edit put back text an earlier Edit of {p} replaced (A -> B -> A)"),
            &Value::Null,
            "",
        );
    }
    let mut text = Value::Object(row).to_string();
    text.push('\n');
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .ok()?
        .write_all(text.as_bytes())
        .ok()?;
    Some(path)
}

fn decide(event: &Event, _session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let _ = append(&event.input, &now_stamp(SystemTime::now()), &here, &|k| {
        std::env::var(k).ok()
    });
    Vec::new()
}

#[cfg(test)]
mod tests;
