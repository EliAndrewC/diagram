//! `workflow-hooks` (feature 383 amendment 7, FR-045; ported from the shell of the same name and `lib/hm_workflow.py`, feature 449 T040): A WORKFLOW CALL IS
//! HELD TO THE GUARDS ITS AGENTS WOULD MEET AS AGENT CALLS, because no Agent hook fires for an agent a workflow spawns (research R20). An untyped `agent(` is
//! refused (`GP_OK` with a reason, and a model, is the escape); a defined agent of this project runs through the saved `check-wave` workflow; and each unit of
//! `check-wave` is put through every `PreToolUse` hook an Agent call meets, the first refusal refusing the whole run.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::sha256;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "workflow-hooks",
    events: &["PreToolUse"],
    matcher: "Workflow",
    decide,
};

/// The jobs the appended system prompt authorizes a workflow for (`tests/test_agent_models.py` holds the two equal). Not spec-fidelity: its round hook rewrites the
/// prompt, which a workflow cannot carry. The GM, 2026-10-26: "I also do pre-authorize the translation check as a wave job".
pub(crate) const WAVE_JOBS: [&str; 16] = [
    "source-applicability",
    "quote-check",
    "settlement-review",
    "entry-drift",
    "modal-depiction",
    "record-format",
    "impl-drift",
    "modal-research",
    "building-review",
    "source-reader",
    "glyph-check",
    "modal-form",
    "round-arbiter",
    "claims-triage",
    "modal-triage",
    "translation-check",
];
const WAVE: &str = "check-wave";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static GP_ESCAPE: LazyLock<Regex> = LazyLock::new(|| re(r#"GP_OK\s*[=:]\s*["']?\S+\s+\S+"#));
static AGENT_TYPE: LazyLock<Regex> =
    LazyLock::new(|| re(r#"\bagentType\s*:\s*(?:(['"`])([\w-]+)\1|(\S))"#));
static NAMES_WAVE: LazyLock<Regex> = LazyLock::new(|| re(r#"['"`]check-wave['"`]"#));
static MODEL: LazyLock<Regex> = LazyLock::new(|| re(r"\bmodel\s*:"));

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// The end of a call opened before `from`, its parentheses balanced (quotes and template strings skipped).
fn call_end(script: &[u8], from: usize) -> usize {
    let (mut depth, mut i, mut quote) = (1_usize, from, 0_u8);
    while i < script.len() && depth > 0 {
        let c = script[i];
        if quote != 0 {
            if c == b'\\' {
                i += 1;
            } else if c == quote {
                quote = 0;
            }
        } else if matches!(c, b'\'' | b'"' | b'`') {
            quote = c;
        } else if matches!(c, b'(' | b'[' | b'{') {
            depth += 1;
        } else if matches!(c, b')' | b']' | b'}') {
            depth -= 1;
        }
        i += 1;
    }
    i.min(script.len())
}

/// The text of each `name(...)` call in a script.
fn calls(script: &str, name: &str) -> Vec<String> {
    let opening = re(&format!(r"(?<![\w.$]){name}\s*\("));
    let bytes = script.as_bytes();
    opening
        .find_iter(script)
        .flatten()
        .map(|m| String::from_utf8_lossy(&bytes[m.start()..call_end(bytes, m.end())]).into_owned())
        .collect()
}

/// A call's `agentType`: its literal, `?` when it is an expression, None when the call names none.
fn agent_type(call: &str) -> Option<String> {
    let m = AGENT_TYPE.captures(call).ok().flatten()?;
    Some(m.get(2).map_or("?", |g| g.as_str()).to_owned())
}

fn defined(root: &Path) -> Vec<String> {
    std::fs::read_dir(root.join(".claude/agents"))
        .into_iter()
        .flatten()
        .filter_map(Result::ok)
        .filter_map(|e| Some(e.file_name().to_str()?.strip_suffix(".md")?.to_owned()))
        .collect()
}

fn short(call: &str) -> String {
    call.chars()
        .take(120)
        .collect::<String>()
        .replace('\n', " ")
}

/// Why an inline or file script is refused, or "".
fn script_verdict(script: &str, root: &Path) -> String {
    if calls(script, "workflow")
        .iter()
        .any(|c| found(&NAMES_WAVE, c))
    {
        return "SCRIPT check-wave is run by name from the Workflow tool, its args written out, never from inside a script".to_owned();
    }
    let gp = found(&GP_ESCAPE, script);
    let mut used = false;
    let ours = defined(root);
    for call in calls(script, "agent") {
        let kind = agent_type(&call);
        if kind.is_none() && !gp {
            return format!("UNTYPED {}", short(&call));
        }
        used = used || kind.is_none();
        if let Some(k) = kind.filter(|k| k == "?" || ours.contains(k)) {
            return format!("GUARDED {k}");
        }
        if !found(&MODEL, &call) {
            return format!("MODEL {}", short(&call));
        }
    }
    if used {
        "ESCAPED".to_owned()
    } else {
        String::new()
    }
}

/// The `PreToolUse` hook commands an Agent call meets, in order; an entry with no matcher takes every tool, Agent among them.
fn agent_hooks(settings: &Path) -> Vec<String> {
    let text = std::fs::read_to_string(settings).unwrap_or_default();
    let data: Value = serde_json::from_str(&text).unwrap_or_default();
    let mut out = Vec::new();
    let entries = data.pointer("/hooks/PreToolUse").and_then(Value::as_array);
    for m in entries.into_iter().flatten() {
        let matcher = field(m, "matcher");
        if matcher.is_empty() || found(&re(&format!("^(?:{matcher})$")), "Agent") {
            let hooks = m.get("hooks").and_then(Value::as_array);
            out.extend(
                hooks
                    .into_iter()
                    .flatten()
                    .filter(|h| !matches!(field(h, "type"), t if !t.is_empty() && t != "command"))
                    .map(|h| field(h, "command").to_owned()),
            );
        }
    }
    out
}

fn run_id(event: &Event) -> String {
    let given = field(&event.input, "tool_use_id");
    if !given.is_empty() {
        return given.to_owned();
    }
    let input = event
        .input
        .get("tool_input")
        .map(Value::to_string)
        .unwrap_or_default();
    sha256::hex(input.as_bytes())[..12].to_owned()
}

/// What this guard needs from outside the call.
pub(crate) struct Ctx {
    pub(crate) root: PathBuf,
    pub(crate) settings: PathBuf,
}

/// One prompt the run can launch.
struct Launch {
    tag: String,
    kind: String,
    prompt: String,
    label: String,
}

/// Every prompt a run can launch - each unit, and each verify step it declares - or why the args are refused.
fn launches(args: &Value, kind: &str) -> Result<Vec<Launch>, String> {
    let mut out = Vec::new();
    for (n, u) in args
        .get("units")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .enumerate()
    {
        let (label, prompt) = (field(u, "label"), u.get("prompt").and_then(Value::as_str));
        let Some(prompt) = prompt.filter(|_| u.is_object() && !label.is_empty()) else {
            return Err(format!("ARGS unit {n} needs a label and a prompt"));
        };
        out.push(Launch {
            tag: n.to_string(),
            kind: kind.to_owned(),
            prompt: prompt.to_owned(),
            label: label.to_owned(),
        });
        let then = u.get("then").filter(|t| !t.is_null());
        let steps = match then.map(Value::as_array) {
            None => &[][..],
            Some(Some(s)) => s,
            Some(None) => {
                return Err(format!(
                    "ARGS unit {label}: then is a list of {{agentType, prompt}}"
                ))
            }
        };
        for (k, step) in steps.iter().enumerate() {
            let typ = field(step, "agentType");
            let Some(asked) = step
                .get("prompt")
                .and_then(Value::as_str)
                .filter(|_| WAVE_JOBS.contains(&typ))
            else {
                return Err(format!("ARGS unit {label}: verify step {k} needs a prompt and an agentType among the wave jobs"));
            };
            out.push(Launch {
                tag: format!("{n}.{k}"),
                kind: typ.to_owned(),
                prompt: asked.to_owned(),
                label: format!("{label} / {typ}"),
            });
        }
    }
    Ok(out)
}

/// A refused run launches nothing: its dispatches the check tracking recorded go. `hm_checks` by path until T048 ports it, on a refused wave alone.
fn drop_run(event: &Event, prefix: &str, _ctx: &Ctx) {
    crate::shared::checks::rounds::drop_run(field(&event.input, "cwd"), prefix);
}

/// Why a `check-wave` run is refused, or "": its args' form, then each unit through the Agent hooks.
fn wave_verdict(event: &Event, ctx: &Ctx) -> String {
    let null = Value::Null;
    let args = event.input.pointer("/tool_input/args").unwrap_or(&null);
    if args.is_string() {
        return "ARGS args is a JSON string - pass the object itself: args: {agentType: ..., units: [...]}".to_owned();
    }
    if args
        .get("units")
        .and_then(Value::as_array)
        .is_none_or(Vec::is_empty)
    {
        return "ARGS check-wave needs args {agentType: \"<job>\", units: [{label, prompt}, ...]}"
            .to_owned();
    }
    let kind = field(args, "agentType");
    if !WAVE_JOBS.contains(&kind) {
        return format!(
            "JOB `{kind}` is not an authorized wave job ({})",
            WAVE_JOBS.join(", ")
        );
    }
    let hooks = agent_hooks(&ctx.settings);
    let run = run_id(event);
    let all = match launches(args, kind) {
        Ok(all) => all,
        Err(why) => return why,
    };
    let cwd = field(&event.input, "cwd");
    let dir = if cwd.is_empty() {
        Path::new(".")
    } else {
        Path::new(cwd)
    };
    for launch in all {
        let unit = json!({
            "session_id": event.input.get("session_id"),
            "transcript_path": event.input.get("transcript_path"),
            "cwd": event.input.get("cwd"),
            "hook_event_name": "PreToolUse",
            "tool_name": "Agent",
            "tool_use_id": format!("wave:{run}:{}", launch.tag),
            "tool_input": {"subagent_type": launch.kind, "prompt": launch.prompt, "description": launch.label, "run_in_background": true},
        })
        .to_string();
        for cmd in &hooks {
            let said = ask(dir, "env", &["L7R_WAVE_UNIT=1", "bash", "-c", cmd], &unit);
            if said.code == 2 {
                drop_run(event, &format!("wave:{run}:"), ctx);
                return format!("UNIT {}\n{}", launch.label, said.err.trim());
            }
        }
    }
    String::new()
}

/// What the decider says: "", `WAVE-PASSED`, `ESCAPED` or the refusal's kind and words.
pub(crate) fn verdict(event: &Event, ctx: &Ctx) -> String {
    let null = Value::Null;
    let ti = event.input.get("tool_input").unwrap_or(&null);
    let (name, path) = (field(ti, "name"), field(ti, "scriptPath"));
    let wave_file = realpath(
        &ctx.root
            .join(".claude/workflows")
            .join(format!("{WAVE}.js")),
    );
    if name == WAVE || (!path.is_empty() && realpath(Path::new(path)) == wave_file) {
        let why = wave_verdict(event, ctx);
        return if why.is_empty() {
            "WAVE-PASSED".to_owned()
        } else {
            why
        };
    }
    let script = if !path.is_empty() {
        let Ok(text) = std::fs::read_to_string(path) else {
            return String::new();
        };
        text
    } else if !name.is_empty() {
        std::fs::read_to_string(
            ctx.root
                .join(".claude/workflows")
                .join(format!("{name}.js")),
        )
        .unwrap_or_default()
    } else {
        field(ti, "script").to_owned()
    };
    script_verdict(&script, &ctx.root)
}

const TRAILER: &str = "(rust/guard/src/guards/workflow_hooks.rs; feature 383 amendment 7)";
const PASSED: &str = "check-wave: every unit passed the Agent guards. When this run finishes, `make wave-report` measures it - each agent's first-request cache read and write, and the main session's wakes - against the last hand-launched wave (feature 383 FR-046).";

fn bold(line: &str) -> String {
    format!("\n\u{1b}[1mBLOCKED: {line}\u{1b}[0m\n")
}

fn refusal(got: &str) -> String {
    let (kind, rest) = got.split_once(' ').unwrap_or((got, ""));
    let body = match kind {
        "UNTYPED" => format!("{}A workflow's default subagent loads every CLAUDE.md and every tool - ~35k tokens written at its first request,\nagainst ~4k for a typed agent whose file omits them (feature 383 research R20). Pass agentType: \"<its .claude/agents/ name>\"\non every agent() call. A deliberate general-purpose stage: GP_OK: <reason> in the script, and name its model.\n", bold(&format!("an agent() call with no agentType: {rest}"))),
        "MODEL" => format!("{}As an ad-hoc Agent call must (agent_model_hooks.rs): model: \"sonnet\" to read, fetch, translate or extract, \"opus\" for\nanything that judges.\n", bold(&format!("an ad-hoc agent() call names no model: {rest}"))),
        "GUARDED" => format!("{}No Agent hook fires inside a workflow, so a defined check is held to its guards (bundle, owed, freeze, round caps,\ndecide-first) only when its units are known before the run - as check-wave's args are:\n  Workflow({{name: \"check-wave\", args: {{agentType: \"<job>\", units: [{{label: \"<unit>\", prompt: \"<its prompt>\"}}, ...]}}}})\nAn agentType computed at run time is refused the same way: name it literally.\n", bold(&format!("`{rest}` runs through the check-wave workflow, not a script of its own."))),
        "UNIT" => {
            let (label, why) = rest.split_once('\n').unwrap_or((rest, ""));
            format!("{}{why}\nThe whole wave is refused: fix or drop that unit, and run check-wave again.\n", bold(&format!("check-wave unit {label} - a guard of its type refused it:")))
        }
        _ => bold(rest),
    };
    format!("{body}{TRAILER}")
}

pub(crate) fn judge(event: &Event, session: &Session, ctx: &Ctx) -> Vec<Answer> {
    if event.tool() != "Workflow" || !ctx.settings.is_file() {
        return Vec::new();
    }
    let got = verdict(event, ctx);
    match got.as_str() {
        "" => Vec::new(),
        "WAVE-PASSED" => vec![Answer::Notice(PASSED.to_owned())],
        "ESCAPED" => {
            log::fire(
                "workflow",
                "escaped",
                "an untyped agent() stage, with a reason",
                "escape",
                &event.input,
                session,
            );
            Vec::new()
        }
        _ => {
            let kind = got.split(' ').next().unwrap_or("");
            let first = got.split('\n').next().unwrap_or("");
            log::fire(
                "workflow",
                "blocked",
                first,
                &kind.to_lowercase(),
                &event.input,
                session,
            );
            vec![Answer::Refuse(refusal(&got))]
        }
    }
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cwd = Some(field(&event.input, "cwd"))
        .filter(|c| !c.is_empty())
        .unwrap_or(".");
    let said = ask(
        Path::new("."),
        "git",
        &["-C", cwd, "rev-parse", "--show-toplevel"],
        "",
    );
    if !said.ok() {
        return Vec::new();
    }
    let root = PathBuf::from(said.out.trim());
    let settings = std::env::var("WORKFLOW_SETTINGS")
        .map_or_else(|_| root.join(".claude/settings.json"), PathBuf::from);
    judge(event, session, &Ctx { root, settings })
}

#[cfg(test)]
mod tests;
