//! Claude Code's hook protocol as the repository's guards speak it (`specs/449-rust-codebase/contracts/guard-protocol.md`, research
//! R3): the event read once, each guard's answers, and their merge into one reply - every refusal together, the rewrites in order,
//! the notices joined.

use serde_json::{json, Value};

use crate::shared::session::Session;

/// A hook event: its name (`PreToolUse`, `Stop`, ...) and the input Claude Code handed it, rewritten in place as guards rewrite it.
pub struct Event {
    pub name: String,
    pub input: Value,
}

impl Event {
    /// The tool the event is about, or "" for an event without one.
    #[must_use]
    pub fn tool(&self) -> &str {
        self.input
            .get("tool_name")
            .and_then(Value::as_str)
            .unwrap_or("")
    }
}

/// One guard's answer (data-model.md, "The answer").
#[derive(Debug, Clone, PartialEq)]
pub enum Answer {
    /// The call is refused: exit 2, the reason on stderr.
    Refuse(String),
    /// The tool's input is replaced (`updatedInput`): the guards after this one see it.
    Rewrite(Value),
    /// A line added to the session's context (`additionalContext`).
    Notice(String),
    /// A `Stop` or `SubagentStop` held: `decision: "block"` with the reason.
    StopBlock(String),
    /// Plain text for a person, printed as it is: a hand-run mode's answer (`gate-hooks status`), never a hook event's.
    Print(String),
}

/// A guard: its name as the guard log names it, the events it decides, the tools it takes (a settings matcher: `*`, or names joined
/// by `|`), and its decider - a function of the event returning its answers, none for an allow.
pub struct Guard {
    pub name: &'static str,
    pub events: &'static [&'static str],
    pub matcher: &'static str,
    pub decide: fn(&Event, &Session) -> Vec<Answer>,
}

impl Guard {
    /// Does this guard decide `event`?
    #[must_use]
    pub fn takes(&self, event: &Event) -> bool {
        // an event that carries no tool (Stop, UserPromptSubmit) is matched by its name alone, as Claude Code matches it
        self.events.contains(&event.name.as_str())
            && (event.tool().is_empty()
                || self.matcher == "*"
                || self.matcher.split('|').any(|m| m == event.tool()))
    }
}

/// The reply to Claude Code: what goes to stdout and stderr, and the exit code.
#[derive(Debug, PartialEq, Eq)]
pub struct Reply {
    pub stdout: String,
    pub stderr: String,
    pub code: i32,
}

/// Run `guards`, in their order, on `event`, merging their answers by the contract: a refusal wins and every refusal is reported;
/// a rewrite replaces the tool's input before the next guard decides; notices are joined; a stop-block's reasons are joined.
pub fn run(event: &mut Event, guards: &[Guard]) -> Reply {
    let (mut refusals, mut notices, mut held, mut printed) =
        (Vec::new(), Vec::new(), Vec::new(), Vec::new());
    let mut rewritten = false;
    // which guards decide is fixed by the event's name and tool, which no rewrite changes: chosen before any guard runs
    let takers: Vec<&Guard> = guards.iter().filter(|g| g.takes(event)).collect();
    // the session's facts, read once for every guard (D6)
    let session = Session::from_input(&event.input);
    for guard in takers {
        let answers = (guard.decide)(event, &session);
        for answer in answers {
            match answer {
                Answer::Refuse(why) => refusals.push(why),
                Answer::Rewrite(input) => {
                    event.input["tool_input"] = input;
                    rewritten = true;
                }
                Answer::Notice(line) => notices.push(line),
                Answer::StopBlock(why) => held.push(why),
                Answer::Print(text) => printed.push(text),
            }
        }
    }
    if !refusals.is_empty() {
        return Reply {
            stdout: String::new(),
            stderr: refusals.join("\n\n"),
            code: 2,
        };
    }
    if !printed.is_empty() {
        return Reply {
            stdout: printed.join("\n"),
            stderr: String::new(),
            code: 0,
        };
    }
    if !held.is_empty() {
        return Reply {
            stdout: json!({"decision": "block", "reason": held.join("\n\n")}).to_string(),
            stderr: String::new(),
            code: 0,
        };
    }
    let mut out = serde_json::Map::new();
    if rewritten {
        out.insert("updatedInput".to_owned(), event.input["tool_input"].clone());
    }
    if !notices.is_empty() {
        out.insert(
            "additionalContext".to_owned(),
            Value::String(notices.join("\n\n")),
        );
    }
    if out.is_empty() {
        return Reply {
            stdout: String::new(),
            stderr: String::new(),
            code: 0,
        };
    }
    out.insert(
        "hookEventName".to_owned(),
        Value::String(event.name.clone()),
    );
    Reply {
        stdout: json!({"hookSpecificOutput": out}).to_string(),
        stderr: String::new(),
        code: 0,
    }
}

#[cfg(test)]
mod tests;
