//! THE BUILDER SPLIT (feature 451 T237, the GM 2026-11-25: "sounds good please do that ASAP"): a CODE BUILDER stops at its stop point
//! and does not run the claims round; the coordinating session runs it as its own dispatch. WHY: five 449 code builders and the 451
//! T218-T222 builder hit the context cap and handed off, the claims round (its agents, replies and re-bundles) the part that ran them
//! out. The brief's standing order is `scripts/container/builder-brief.md`; this is its backstop.
//!
//! A CODE BUILDER: a builder (D8: `agent_id`, no `.claude/agents/<agent_type>.md`) whose brief - the first row of its own transcript,
//! the prompt it was dispatched with - holds a line opening `STOP POINT` and does not itself open `Run the claims round` (the claims
//! round's own dispatch, which may quote the brief). Measured 2026-11-25 over this session's 579 builders: the 12 whose brief held
//! such a line (449 T431-T435, 451 T230-T240) dispatched no claims agent, so the rule would have refused none of their calls; the 6
//! claims-round dispatches ("Run the claims round for feature ...") and the 131 the main thread made carry no mark and pass. Any read
//! that fails passes: a guard that cannot see the brief does not guess it.
//!
//! WHAT IS REFUSED: its `Agent` call of `claims-triage` or `impl-drift`, or a `Workflow` naming either as an `agentType` (a wave of 4
//! or more runs through `check-wave`, whose units no Agent hook sees). Its escape: `SPLIT_OK="<reason>"` in the prompt (the Workflow's
//! input), recorded.

use std::fs::File;
use std::io::{BufRead as _, BufReader};
use std::path::Path;

use serde_json::Value;

use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::state::field;

/// The escape's token.
pub(super) const TOKEN: &str = "SPLIT_OK";

/// The claims round's agents, which a code builder does not dispatch.
const CLAIMS: [&str; 2] = ["claims-triage", "impl-drift"];

/// What the split says of one call of a code builder.
#[derive(Debug, PartialEq, Eq)]
pub(super) enum Split {
    /// A claims agent dispatched: refused, naming it.
    Refused(String),
    /// Escaped by `SPLIT_OK` and its reason.
    Escaped(String),
    /// `SPLIT_OK` with no reason: the escape's own refusal.
    NoReason(String),
}

/// The claims agent a call dispatches, and the text its escape is read from: an `Agent` call's `subagent_type` and prompt, a
/// `Workflow`'s first such `agentType` and its whole input. None for any other call, before anything is read.
pub(super) fn dispatch(input: &Value) -> Option<(String, String)> {
    let ti = input.get("tool_input")?;
    match field(input, "tool_name") {
        "Agent" | "Task" => {
            let kind = field(ti, "subagent_type");
            CLAIMS
                .contains(&kind)
                .then(|| (kind.to_owned(), field(ti, "prompt").to_owned()))
        }
        "Workflow" => typed(ti).map(|k| (k, ti.to_string())),
        _ => None,
    }
}

/// The first claims agent a Workflow's input names as an `agentType`: a key of its args (a check-wave's, or a unit's `then` step) or
/// a literal in its script (`agentType: "impl-drift"`).
fn typed(v: &Value) -> Option<String> {
    match v {
        Value::Object(o) => o.iter().find_map(|(k, x)| match x {
            Value::String(s) if k == "agentType" && CLAIMS.contains(&s.as_str()) => Some(s.clone()),
            _ => typed(x),
        }),
        Value::Array(a) => a.iter().find_map(typed),
        Value::String(s) => s.split("agentType").skip(1).find_map(|rest| {
            let word = rest
                .trim_start_matches(|c: char| {
                    c.is_whitespace() || matches!(c, ':' | '"' | '\'' | '`' | '\\')
                })
                .split(|c: char| !(c.is_ascii_alphanumeric() || c == '-'))
                .next()
                .unwrap_or_default();
            CLAIMS.contains(&word).then(|| word.to_owned())
        }),
        _ => None,
    }
}

/// Whether the builder whose own transcript is `own` is a code builder: its brief holds a line opening `STOP POINT`, and is no
/// claims round's. False where the transcript or its first row will not read.
pub(super) fn code_builder(own: &Path) -> bool {
    let Ok(file) = File::open(own) else {
        return false;
    };
    let mut first = String::new();
    let _ = BufReader::new(file).read_line(&mut first);
    let row: Value = serde_json::from_str(&first).unwrap_or(Value::Null);
    let content = &row["message"]["content"];
    let brief = content.as_str().map_or_else(
        || {
            content
                .as_array()
                .and_then(|bs| bs.iter().find_map(|b| b["text"].as_str()))
                .unwrap_or_default()
        },
        |t| t,
    );
    !brief.trim_start().starts_with("Run the claims round")
        && brief
            .lines()
            .any(|l| l.trim_start().starts_with("STOP POINT"))
}

/// The verdict on a code builder's dispatch of `kind`, its escape read from `text`.
pub(super) fn judge(kind: String, text: &str) -> Split {
    match escape_or_refuse(text, TOKEN) {
        Escape::Escaped(why) => Split::Escaped(why),
        Escape::Refused(_) => Split::NoReason(no_reason()),
        Escape::None => Split::Refused(kind),
    }
}

/// `SPLIT_OK` with no reason: its own text, not the shared escape's, which tells the reader to put the reason in a command where this
/// one goes in a prompt (message-check, 2026-11-25, also cut the shared text's rationale).
fn no_reason() -> String {
    format!(
        "\n\u{1b}[1mBLOCKED: {TOKEN} with no reason.\u{1b}[0m Put one in the prompt: {TOKEN}=\"<why this case is legitimate>\"\n\
(two words, eight characters, e.g. \"CI is down\").\n"
    )
}

/// The refusal: the agent, the stop point, what to report, the escape.
pub(super) fn refusal(kind: &str) -> String {
    format!(
        "\n\u{1b}[1mBLOCKED: a code builder does not dispatch {kind}; the claims round is the coordinating session's.\u{1b}[0m\n\n\
Your brief's STOP POINT: run `make claims-triage` (mechanical) and stop there. Report what you built and measured, the claim\n\
keys you touched, what `make claims-owed` lists and the exact paths to commit.\n\n\
Escape: {TOKEN}=\"<reason, two words or more>\" in the prompt, recorded in the guard log.\n"
    )
}

#[cfg(test)]
mod tests;
