//! `record-edit-hooks` (feature 258, FR-028; feature 449 T011, T86): an edit aimed at an ASSEMBLED record page goes to its fragment, and a page or pop-up is frozen while its checks run (feature 375 FR-003(b)).
//! The freeze runs first, for an Edit, a Write and a Bash `make apply-edits`; a Write of an assembled page, which cannot be routed, is refused, every refusal naming the command that fixes it. `record_edit_gate::mode_for`
//! answers without a process for a call that cannot concern it, so a plain call starts nothing.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::record_edit_gate::mode_for;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::checks::handle;
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "record-edit-hooks",
    events: &["PreToolUse"],
    matcher: "Edit|Write|Bash",
    decide,
};

const NAME: &str = "record-edit";

fn fire(event: &Event, kind: &str, detail: &str, rule: &str, context: &str, session: &Session) {
    let _ = log::write(&log::Entry {
        guard: NAME,
        event: kind,
        detail,
        rule,
        context: Some(json!(context)),
        input: &event.input,
        session_name: &session.name(),
    });
}

/// The route's verdict, for a verdict the shell guard acted on: a rewrite's answers or a refusal, recorded.
fn routed(verdict: &Value, event: &Event, session: &Session) -> Vec<Answer> {
    let shown = verdict.to_string();
    match field(verdict, "verdict") {
        "rewrite" => {
            fire(
                event,
                "rewrote",
                "edit",
                "edit-moved-to-fragment",
                &shown,
                session,
            );
            let hook = verdict.get("hook").unwrap_or(&Value::Null);
            let said = hook.get("hookSpecificOutput").unwrap_or(hook);
            let rewrite = said.get("updatedInput").map(|v| Answer::Rewrite(v.clone()));
            let notice = said
                .get("additionalContext")
                .and_then(Value::as_str)
                .map(|t| Answer::Notice(t.to_owned()));
            rewrite.into_iter().chain(notice).collect()
        }
        "refuse" => {
            let rule = match field(verdict, "rule") {
                "" => "record-edit",
                r => r,
            };
            fire(event, "blocked", "edit", rule, &shown, session);
            vec![Answer::Refuse(format!(
                "BLOCKED: {}\n(scripts/hooks/record-edit-hooks.sh; feature 258, spec FR-028)",
                field(verdict, "message")
            ))]
        }
        _ => Vec::new(),
    }
}

pub(crate) fn judge(event: &Event, session: &Session, here: &Path, tree: &Path) -> Vec<Answer> {
    let given = field(&event.input, "cwd");
    let from = if given.is_empty() {
        here
    } else {
        Path::new(given)
    };
    let Some(mode) = mode_for(event, from) else {
        return Vec::new();
    };
    let held = handle::handle("edit", &event.input, None);
    if !held.is_empty() {
        let text = handle::blocked_text(&held);
        fire(
            event,
            "blocked",
            "edit",
            "frozen-while-checked",
            &text,
            session,
        );
        return vec![Answer::Refuse(text)];
    }
    if mode == "pretool-bash" {
        return Vec::new();
    }
    let gate = tree.join("scripts/gates/l7r-gate.sh");
    let said = ask(
        here,
        &gate.to_string_lossy(),
        &["record", "edit-route"],
        &event.input.to_string(),
    );
    if !said.ok() {
        return Vec::new();
    }
    serde_json::from_str::<Value>(&said.out)
        .map_or_else(|_| Vec::new(), |v| routed(&v, event, session))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(event, session, &here, &tree)
}

#[cfg(test)]
mod tests;
